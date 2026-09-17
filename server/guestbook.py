#!/usr/bin/env python3
"""Serves the site and keeps the guest book.

    python3 server/guestbook.py                 # http://localhost:8000
    PORT=8080 GUESTBOOK_TOKEN=secret python3 server/guestbook.py

Notes go to PostgreSQL when DATABASE_URL is set and psycopg is installed
(requirements.txt has it), and to a SQLite file otherwise — next to this script,
or wherever GUESTBOOK_DB points. Nothing else is needed either way.

No note appears on the site until it has been read and approved, so the page
cannot be used to publish something in Max Darkosadze's name without him seeing
it first.

Public:
    GET  /api/guestbook          the approved notes, newest first
    POST /api/guestbook          {name, place, message} -> stored as pending

Moderation from a browser:
    /admin                       enter the token once, then keep or delete each note

Moderation over HTTP (needs the token, either ?token=… or an X-Token header):
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

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
psycopg = None
if DATABASE_URL:
    try:
        import psycopg                      # the Railway Postgres service
    except ImportError:
        psycopg = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def _db_path():
    """Somewhere writable: the configured path, next to this file, or /tmp —
    a read-only project directory should not stop the server from starting."""
    candidates = [os.environ.get("GUESTBOOK_DB")] if os.environ.get("GUESTBOOK_DB") else []
    candidates.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "guestbook.db"))
    candidates.append(os.path.join("/tmp", "guestbook.db"))
    for candidate in candidates:
        directory = os.path.dirname(candidate) or "."
        try:
            os.makedirs(directory, exist_ok=True)
            probe = os.path.join(directory, ".write-probe")
            with open(probe, "w") as fh:
                fh.write("")
            os.remove(probe)
            return candidate
        except OSError:
            continue
    return candidates[-1]


DB_PATH = _db_path()
TOKEN = os.environ.get("GUESTBOOK_TOKEN", "")
PORT = int(os.environ.get("PORT", "8000"))

MAX_NAME, MAX_PLACE, MAX_MESSAGE = 40, 80, 700
COOLDOWN_SECONDS = 60            # one note per address per minute
MAX_PER_DAY = 10
LINK_RE = re.compile(r"https?://|www\.", re.I)


ADMIN_PAGE = """<!DOCTYPE html>
<html lang="ka">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>სტუმრების წიგნი — მოდერაცია</title>
<style>
  :root { color-scheme: dark; }
  body { margin:0; padding:1.4rem; background:#0b1219; color:#e7edf3;
         font:16px/1.6 system-ui, -apple-system, "Noto Sans Georgian", sans-serif; }
  .wrap { max-width:46rem; margin-inline:auto; }
  h1 { font-size:1.3rem; margin:0 0 1.2rem; }
  h1 span { color:#d8ae3f; }
  input, button { font:inherit; border-radius:10px; }
  input { width:100%; padding:.7rem .9rem; background:#121c26; color:inherit;
          border:1px solid #22303d; }
  button { cursor:pointer; padding:.5rem 1rem; border:1px solid #22303d;
           background:#121c26; color:inherit; }
  button.keep { border-color:#d8ae3f; color:#d8ae3f; }
  button.drop { border-color:#7a3b34; color:#e08b80; }
  .note { border:1px solid #22303d; border-top:3px solid #d8ae3f; border-radius:12px;
          padding:1rem 1.1rem; margin-bottom:1rem; background:#121c26; }
  .who { color:#d8ae3f; font-weight:600; }
  .where, .when { color:#9aa8b6; font-size:.85rem; }
  .actions { display:flex; gap:.6rem; margin-top:.9rem; }
  .msg { white-space:pre-line; margin:.6rem 0 0; }
  .empty, .hint { color:#9aa8b6; }
</style>
</head>
<body>
<div class="wrap">
  <h1>სტუმრების წიგნი — <span>მოდერაცია</span></h1>
  <p id="gate">
    <label>ტოკენი (GUESTBOOK_TOKEN)<br><input id="token" type="password" autocomplete="off"></label>
    <button id="go" style="margin-top:.7rem">შესვლა</button>
  </p>
  <p class="hint" id="hint" hidden>ჩანაწერი გამოქვეყნდება მხოლოდ „დატოვება“-ზე დაჭერის შემდეგ.</p>
  <div id="list"></div>
</div>
<script>
(function () {
  var list = document.getElementById("list");
  var gate = document.getElementById("gate");
  var hint = document.getElementById("hint");
  var token = "";
  try { token = sessionStorage.getItem("gb-token") || ""; } catch (e) {}

  function call(path, method) {
    return fetch(path, { method: method || "GET", headers: { "X-Token": token } });
  }

  function load() {
    call("/api/guestbook/pending").then(function (r) {
      if (r.status === 401) { alert("ტოკენი არ ემთხვევა."); gate.hidden = false; return null; }
      return r.json();
    }).then(function (data) {
      if (!data) return;
      gate.hidden = true;
      hint.hidden = false;
      try { sessionStorage.setItem("gb-token", token); } catch (e) {}
      list.textContent = "";
      if (!data.notes.length) {
        var empty = document.createElement("p");
        empty.className = "empty";
        empty.textContent = "ახალი ჩანაწერი არ არის.";
        list.appendChild(empty);
        return;
      }
      data.notes.forEach(function (note) {
        var box = document.createElement("div");
        box.className = "note";
        var who = document.createElement("p");
        var name = document.createElement("span");
        name.className = "who";
        name.textContent = note.name;
        var place = document.createElement("span");
        place.className = "where";
        place.textContent = note.place ? " · " + note.place : "";
        who.appendChild(name);
        who.appendChild(place);
        var msg = document.createElement("p");
        msg.className = "msg";
        msg.textContent = note.message;
        var when = document.createElement("p");
        when.className = "when";
        when.textContent = new Date(note.created * 1000).toLocaleString();
        var actions = document.createElement("p");
        actions.className = "actions";
        var keep = document.createElement("button");
        keep.className = "keep";
        keep.textContent = "დატოვება";
        keep.onclick = function () {
          call("/api/guestbook/" + note.id + "/approve", "POST").then(load);
        };
        var drop = document.createElement("button");
        drop.className = "drop";
        drop.textContent = "წაშლა";
        drop.onclick = function () {
          if (confirm("წავშალოთ?")) call("/api/guestbook/" + note.id, "DELETE").then(load);
        };
        actions.appendChild(keep);
        actions.appendChild(drop);
        box.appendChild(who);
        box.appendChild(msg);
        box.appendChild(when);
        box.appendChild(actions);
        list.appendChild(box);
      });
    });
  }

  document.getElementById("go").onclick = function () {
    token = document.getElementById("token").value.trim();
    load();
  };
  if (token) load();
})();
</script>
</body>
</html>
"""


DB_READY = True
USING_POSTGRES = bool(DATABASE_URL and psycopg)

SQLITE_SCHEMA = """
    CREATE TABLE IF NOT EXISTS notes (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        name      TEXT NOT NULL,
        place     TEXT NOT NULL DEFAULT '',
        message   TEXT NOT NULL,
        lang      TEXT NOT NULL DEFAULT '',
        source_ip TEXT NOT NULL DEFAULT '',
        created   BIGINT NOT NULL,
        approved  INTEGER NOT NULL DEFAULT 0
    )"""

POSTGRES_SCHEMA = """
    CREATE TABLE IF NOT EXISTS notes (
        id        SERIAL PRIMARY KEY,
        name      TEXT NOT NULL,
        place     TEXT NOT NULL DEFAULT '',
        message   TEXT NOT NULL,
        lang      TEXT NOT NULL DEFAULT '',
        source_ip TEXT NOT NULL DEFAULT '',
        created   BIGINT NOT NULL,
        approved  INTEGER NOT NULL DEFAULT 0
    )"""


class Store:
    """One tiny interface over both databases. Queries are written with ?
    placeholders and translated for Postgres, so there is a single set of SQL."""

    def __init__(self):
        self.postgres = USING_POSTGRES

    def connect(self):
        if self.postgres:
            return psycopg.connect(DATABASE_URL, autocommit=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.isolation_level = None
        return conn

    def setup(self):
        with self.connect() as conn:
            self._execute(conn, POSTGRES_SCHEMA if self.postgres else SQLITE_SCHEMA, ())

    def _execute(self, conn, sql, params):
        if self.postgres:
            sql = sql.replace("?", "%s")
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor

    def rows(self, sql, params=()):
        with self.connect() as conn:
            cursor = self._execute(conn, sql, params)
            columns = [c[0] for c in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def run(self, sql, params=()):
        with self.connect() as conn:
            self._execute(conn, sql, params)


STORE = Store()


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
        if path in ("/admin", "/admin/"):
            body = ADMIN_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Robots-Tag", "noindex")
            self.end_headers()
            self.wfile.write(body)
            return
        if path in ("/healthz", "/api/health"):
            return self.send_json({"ok": True, "guestbook": DB_READY,
                                   "store": "postgres" if USING_POSTGRES else "sqlite"})
        if path == "/api/guestbook":
            if not DB_READY:
                return self.send_json({"error": "unavailable"}, 503)
            rows = STORE.rows("SELECT id, name, place, message, created FROM notes "
                              "WHERE approved = 1 ORDER BY id DESC LIMIT 200")
            return self.send_json({"notes": rows})
        if path == "/api/guestbook/pending":
            if not self.authorised():
                return self.send_json({"error": "unauthorised"}, 401)
            rows = STORE.rows("SELECT id, name, place, message, lang, created "
                              "FROM notes WHERE approved = 0 ORDER BY id")
            return self.send_json({"notes": rows})
        return super().do_GET()

    # ---------------------------------------------------------------- POST
    def do_POST(self):
        path = self.path.split("?")[0]

        if path == "/api/guestbook":
            if not DB_READY:
                return self.send_json({"error": "unavailable"}, 503)
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
            recent = STORE.rows(
                "SELECT created FROM notes WHERE source_ip = ? ORDER BY id DESC LIMIT 1", (ip,))
            if recent and now - recent[0]["created"] < COOLDOWN_SECONDS:
                return self.send_json({"error": "too soon"}, 429)
            today = STORE.rows(
                "SELECT COUNT(*) AS n FROM notes WHERE source_ip = ? AND created > ?",
                (ip, now - 86400))[0]["n"]
            if today >= MAX_PER_DAY:
                return self.send_json({"error": "too many"}, 429)
            STORE.run(
                "INSERT INTO notes (name, place, message, lang, source_ip, created, approved)"
                " VALUES (?, ?, ?, ?, ?, ?, 0)",
                (name, place, message, clean(payload.get("lang"), 5), ip, now))
            return self.send_json({"ok": True, "pending": True})

        match = re.match(r"^/api/guestbook/(\d+)/approve$", path)
        if match:
            if not self.authorised():
                return self.send_json({"error": "unauthorised"}, 401)
            STORE.run("UPDATE notes SET approved = 1 WHERE id = ?", (int(match.group(1)),))
            return self.send_json({"ok": True})

        return self.send_json({"error": "not found"}, 404)

    # -------------------------------------------------------------- DELETE
    def do_DELETE(self):
        match = re.match(r"^/api/guestbook/(\d+)$", self.path.split("?")[0])
        if not match:
            return self.send_json({"error": "not found"}, 404)
        if not self.authorised():
            return self.send_json({"error": "unauthorised"}, 401)
        STORE.run("DELETE FROM notes WHERE id = ?", (int(match.group(1)),))
        return self.send_json({"ok": True})

    def list_directory(self, path):         # no directory listings
        self.send_error(404, "Not found")
        return None

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, fmt, *args):      # quieter logs
        if "/api/" in (self.path or ""):
            super().log_message(fmt, *args)


def main():
    global DB_READY
    try:
        STORE.setup()
    except Exception as error:              # noqa: BLE001 - never refuse to serve
        DB_READY = False
        print("! the guest book is unavailable (%s) — the site is still served" % error)
    if not TOKEN:
        print("! GUESTBOOK_TOKEN is not set — moderation endpoints are disabled.")
    if DATABASE_URL and not psycopg:
        print("! DATABASE_URL is set but psycopg is not installed — using SQLite instead")
    print("guest book storage: %s" % ("PostgreSQL" if USING_POSTGRES else "SQLite at %s" % DB_PATH))
    print("serving %s on http://0.0.0.0:%d" % (ROOT, PORT))
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
