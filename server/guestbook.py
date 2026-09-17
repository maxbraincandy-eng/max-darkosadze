#!/usr/bin/env python3
"""Serves the site and keeps the guest book.

    python3 server/guestbook.py                 # http://localhost:8000
    PORT=8080 GUESTBOOK_TOKEN=secret python3 server/guestbook.py

Standard library only — no packages to install. Notes are stored in a SQLite
file next to this script (override with GUESTBOOK_DB) and none of them appear on
the site until they have been read and approved, so the page cannot be used to
publish something in Max Darkosadze's name without him seeing it first.

Public:
    GET  /api/guestbook          the approved notes, newest first
    POST /api/guestbook          {name, place, message} -> stored as pending

Moderation (needs the token, either ?token=… or an X-Token header):
    GET    /api/guestbook/pending
    POST   /api/guestbook/<id>/approve
    DELETE /api/guestbook/<id>

Set GUESTBOOK_TOKEN before deploying. Without it the moderation endpoints are
refused outright rather than left open.
"""

import json
import os
import re
import sqlite3
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.environ.get("GUESTBOOK_DB", os.path.join(os.path.dirname(os.path.abspath(__file__)), "guestbook.db"))
TOKEN = os.environ.get("GUESTBOOK_TOKEN", "")
PORT = int(os.environ.get("PORT", "8000"))

MAX_NAME, MAX_PLACE, MAX_MESSAGE = 40, 80, 700
COOLDOWN_SECONDS = 60            # one note per address per minute
MAX_PER_DAY = 10
LINK_RE = re.compile(r"https?://|www\.", re.I)


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT NOT NULL,
            place     TEXT NOT NULL DEFAULT '',
            message   TEXT NOT NULL,
            lang      TEXT NOT NULL DEFAULT '',
            source_ip TEXT NOT NULL DEFAULT '',
            created   INTEGER NOT NULL,
            approved  INTEGER NOT NULL DEFAULT 0
        )""")
    return conn


def clean(value, limit):
    text = re.sub(r"[\x00-\x1f\x7f]", " ", str(value or "")).strip()
    text = re.sub(r"\s{3,}", "  ", text)
    return text[:limit]


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    # ------------------------------------------------------------- helpers
    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def client_ip(self):
        forwarded = self.headers.get("X-Forwarded-For", "")
        return (forwarded.split(",")[0].strip() or self.client_address[0])[:60]

    def authorised(self):
        if not TOKEN:
            return False
        supplied = self.headers.get("X-Token", "")
        if "token=" in (self.path or ""):
            supplied = supplied or self.path.split("token=", 1)[1].split("&")[0]
        return supplied == TOKEN

    def read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > 8000:
            return None
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None

    # ----------------------------------------------------------------- GET
    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/guestbook":
            with db() as conn:
                rows = conn.execute(
                    "SELECT id, name, place, message, created FROM notes "
                    "WHERE approved = 1 ORDER BY id DESC LIMIT 200").fetchall()
            return self.send_json({"notes": [dict(r) for r in rows]})
        if path == "/api/guestbook/pending":
            if not self.authorised():
                return self.send_json({"error": "unauthorised"}, 401)
            with db() as conn:
                rows = conn.execute(
                    "SELECT * FROM notes WHERE approved = 0 ORDER BY id").fetchall()
            return self.send_json({"notes": [dict(r) for r in rows]})
        return super().do_GET()

    # ---------------------------------------------------------------- POST
    def do_POST(self):
        path = self.path.split("?")[0]

        if path == "/api/guestbook":
            payload = self.read_json()
            if payload is None:
                return self.send_json({"error": "bad request"}, 400)
            if clean(payload.get("website"), 10):        # honeypot
                return self.send_json({"ok": True})      # quietly drop it

            name = clean(payload.get("name"), MAX_NAME)
            place = clean(payload.get("place"), MAX_PLACE)
            message = clean(payload.get("message"), MAX_MESSAGE)
            if not name or len(message) < 2:
                return self.send_json({"error": "name and message are required"}, 400)
            if LINK_RE.search(message) or LINK_RE.search(name):
                return self.send_json({"error": "links are not accepted"}, 400)

            now = int(time.time())
            ip = self.client_ip()
            with db() as conn:
                recent = conn.execute(
                    "SELECT created FROM notes WHERE source_ip = ? ORDER BY id DESC LIMIT 1",
                    (ip,)).fetchone()
                if recent and now - recent["created"] < COOLDOWN_SECONDS:
                    return self.send_json({"error": "too soon"}, 429)
                today = conn.execute(
                    "SELECT COUNT(*) AS n FROM notes WHERE source_ip = ? AND created > ?",
                    (ip, now - 86400)).fetchone()["n"]
                if today >= MAX_PER_DAY:
                    return self.send_json({"error": "too many"}, 429)
                conn.execute(
                    "INSERT INTO notes (name, place, message, lang, source_ip, created, approved)"
                    " VALUES (?, ?, ?, ?, ?, ?, 0)",
                    (name, place, message, clean(payload.get("lang"), 5), ip, now))
            return self.send_json({"ok": True, "pending": True})

        match = re.match(r"^/api/guestbook/(\d+)/approve$", path)
        if match:
            if not self.authorised():
                return self.send_json({"error": "unauthorised"}, 401)
            with db() as conn:
                conn.execute("UPDATE notes SET approved = 1 WHERE id = ?", (int(match.group(1)),))
            return self.send_json({"ok": True})

        return self.send_json({"error": "not found"}, 404)

    # -------------------------------------------------------------- DELETE
    def do_DELETE(self):
        match = re.match(r"^/api/guestbook/(\d+)$", self.path.split("?")[0])
        if not match:
            return self.send_json({"error": "not found"}, 404)
        if not self.authorised():
            return self.send_json({"error": "unauthorised"}, 401)
        with db() as conn:
            conn.execute("DELETE FROM notes WHERE id = ?", (int(match.group(1)),))
        return self.send_json({"ok": True})

    def list_directory(self, path):         # no directory listings
        self.send_error(404, "Not found")
        return None

    def log_message(self, fmt, *args):      # quieter logs
        if "/api/" in (self.path or ""):
            super().log_message(fmt, *args)


def main():
    db().close()
    if not TOKEN:
        print("! GUESTBOOK_TOKEN is not set — moderation endpoints are disabled.")
    print("guest book database: %s" % DB_PATH)
    print("serving %s on http://0.0.0.0:%d" % (ROOT, PORT))
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
