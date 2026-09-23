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
import threading
import time
import urllib.parse
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
try:
    import psycopg                          # the Railway Postgres service
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

# Notes normally wait to be read before they appear. Set GUESTBOOK_AUTO_APPROVE=1
# and they are published the moment they are written — the length limits, the
# refusal of links and the one-note-per-minute rule still apply.
def _switch(name):
    """A variable typed by hand in a dashboard: quotes and stray spaces happen,
    and anything that is not plainly 'off' is meant as 'on'."""
    value = os.environ.get(name, "").strip().strip("\"'").strip().lower()
    return value not in ("", "0", "false", "no", "off")


AUTO_APPROVE = _switch("GUESTBOOK_AUTO_APPROVE")


def _canonical_host():
    """The one address the site should answer on, taken from content/site.json.
    Everything else — the old deployment address, a www. spelling — is sent
    there with a permanent redirect, so searches and links pile up in one
    place instead of being split between two identical sites."""
    try:
        with open(os.path.join(ROOT, "content", "site.json"), encoding="utf-8") as fh:
            base = json.load(fh).get("baseUrl", "")
    except (OSError, ValueError):
        return ""
    return base.split("://")[-1].strip("/").lower()


CANONICAL_HOST = os.environ.get("CANONICAL_HOST", "").strip().lower() or _canonical_host()

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
<title>მაქსი დარკოსაძე — მართვა</title>
<style>
  :root { color-scheme: dark; }
  body { margin:0; padding:1.4rem; background:#0b1219; color:#e7edf3;
         font:16px/1.6 system-ui, -apple-system, "Noto Sans Georgian", sans-serif; }
  .wrap { max-width:50rem; margin-inline:auto; }
  h1 { font-size:1.25rem; margin:0 0 1.1rem; }
  h1 span { color:#d8ae3f; }
  input, button { font:inherit; border-radius:10px; }
  input { width:100%; padding:.7rem .9rem; background:#121c26; color:inherit; border:1px solid #22303d; }
  button { cursor:pointer; padding:.5rem 1rem; border:1px solid #22303d; background:#121c26; color:inherit; }
  button.keep { border-color:#d8ae3f; color:#d8ae3f; }
  button.drop { border-color:#7a3b34; color:#e08b80; }
  .tabs { display:flex; gap:.5rem; margin-bottom:1.2rem; flex-wrap:wrap; }
  .tabs button.on { border-color:#d8ae3f; color:#d8ae3f; }
  .badge { background:rgba(216,174,63,.18); color:#d8ae3f; border-radius:999px;
           padding:.05rem .5rem; font-size:.78rem; margin-inline-start:.4rem; }
  .card { border:1px solid #22303d; border-top:3px solid #d8ae3f; border-radius:12px;
          padding:1rem 1.1rem; margin-bottom:1rem; background:#121c26; }
  .card.done { border-top-color:#3c4b59; opacity:.65; }
  .who { color:#d8ae3f; font-weight:600; }
  .meta { color:#9aa8b6; font-size:.85rem; }
  .actions { display:flex; gap:.6rem; margin-top:.9rem; flex-wrap:wrap; }
  .msg { white-space:pre-line; margin:.6rem 0 0; }
  .empty, .hint { color:#9aa8b6; }
  table { width:100%; border-collapse:collapse; font-size:.92rem; }
  td, th { text-align:start; padding:.4rem .2rem; border-bottom:1px solid #1b2733; }
  th { color:#9aa8b6; font-weight:500; }
  .bar { background:#d8ae3f; height:8px; border-radius:4px; display:block; min-width:2px; }
  .tiles { display:flex; gap:.8rem; flex-wrap:wrap; margin-bottom:1.2rem; }
  .tile { flex:1 1 8rem; border:1px solid #22303d; border-radius:12px; padding:.9rem 1rem; background:#121c26; }
  .tile b { display:block; font-size:1.6rem; color:#d8ae3f; line-height:1.2; }
  .tile span { color:#9aa8b6; font-size:.82rem; }
</style>
</head>
<body>
<div class="wrap">
  <h1>მაქსი დარკოსაძე — <span>მართვა</span></h1>
  <p id="gate">
    <label>ტოკენი (GUESTBOOK_TOKEN)<br><input id="token" type="password" autocomplete="off"></label>
    <button id="go" style="margin-top:.7rem">შესვლა</button>
  </p>
  <div id="app" hidden>
    <div class="tabs">
      <button data-tab="notes" class="on">ჩანაწერები<span class="badge" id="b-notes">0</span></button>
      <button data-tab="bookings">მოწვევები<span class="badge" id="b-bookings">0</span></button>
      <button data-tab="stats">სტატისტიკა</button>
    </div>
    <p class="hint" id="mode"></p>
    <div id="view"></div>
  </div>
</div>
<script>
(function () {
  var token = "";
  try { token = sessionStorage.getItem("gb-token") || ""; } catch (e) {}
  var view = document.getElementById("view");
  var app = document.getElementById("app");
  var gate = document.getElementById("gate");
  var tab = "notes";
  var auto = false;

  function call(path, method) {
    return fetch(path, { method: method || "GET", headers: { "X-Token": token } });
  }
  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function when(seconds) { return new Date(seconds * 1000).toLocaleString(); }

  function counts() {
    return call("/api/stats").then(function (r) { return r.ok ? r.json() : null; }).then(function (s) {
      if (!s) return;
      document.getElementById("b-notes").textContent = s.notesWaiting;
      document.getElementById("b-bookings").textContent = s.bookingsOpen;
      auto = !!s.autoApprove;
      var flag = document.getElementById("mode");
      flag.textContent = auto
        ? "რეჟიმი: ჩანაწერები ქვეყნდება მაშინვე."
        : "რეჟიმი: ჩანაწერი ელოდება თქვენს დადასტურებას.";
    });
  }

  function notes() {
    call("/api/guestbook/pending").then(function (r) {
      if (r.status === 401) { alert("ტოკენი არ ემთხვევა."); gate.hidden = false; app.hidden = true; return null; }
      return r.json();
    }).then(function (data) {
      if (!data) return;
      gate.hidden = true; app.hidden = false;
      try { sessionStorage.setItem("gb-token", token); } catch (e) {}
      view.textContent = "";
      if (!auto) {
        view.appendChild(el("h2", "", "ელოდება"));
        view.appendChild(el("p", "hint", "ჩანაწერი გამოქვეყნდება მხოლოდ „დატოვება“-ზე დაჭერის შემდეგ."));
      }
      if (!data.notes.length) { view.appendChild(el("p", "empty", "ახალი ჩანაწერი არ არის.")); }
      data.notes.forEach(function (note) {
        var box = el("div", "card");
        var head = el("p");
        head.appendChild(el("span", "who", note.name));
        head.appendChild(el("span", "meta", note.place ? " · " + note.place : ""));
        box.appendChild(head);
        box.appendChild(el("p", "msg", note.message));
        box.appendChild(el("p", "meta", when(note.created)));
        var actions = el("p", "actions");
        var keep = el("button", "keep", "დატოვება");
        keep.onclick = function () { call("/api/guestbook/" + note.id + "/approve", "POST").then(render); };
        var drop = el("button", "drop", "წაშლა");
        drop.onclick = function () { if (confirm("წავშალოთ?")) call("/api/guestbook/" + note.id, "DELETE").then(render); };
        actions.appendChild(keep); actions.appendChild(drop);
        box.appendChild(actions);
        view.appendChild(box);
      });
      published();
    });
  }

  function published() {
    /* what the visitors see right now — so it can be taken down from here too */
    call("/api/guestbook").then(function (r) { return r.ok ? r.json() : null; }).then(function (data) {
      if (!data) return;
      view.appendChild(el("h2", "", "გამოქვეყნებული"));
      if (!data.notes.length) { view.appendChild(el("p", "empty", "ჯერ არც ერთი.")); return; }
      data.notes.forEach(function (note) {
        var box = el("div", "card done");
        var head = el("p");
        head.appendChild(el("span", "who", note.name));
        head.appendChild(el("span", "meta", note.place ? " · " + note.place : ""));
        box.appendChild(head);
        box.appendChild(el("p", "msg", note.message));
        box.appendChild(el("p", "meta", when(note.created)));
        var actions = el("p", "actions");
        var drop = el("button", "drop", "წაშლა");
        drop.onclick = function () { if (confirm("წავშალოთ?")) call("/api/guestbook/" + note.id, "DELETE").then(render); };
        actions.appendChild(drop);
        box.appendChild(actions);
        view.appendChild(box);
      });
    });
  }

  function bookings() {
    call("/api/bookings").then(function (r) { return r.ok ? r.json() : null; }).then(function (data) {
      if (!data) return;
      view.textContent = "";
      if (!data.bookings.length) { view.appendChild(el("p", "empty", "მოწვევები ჯერ არ არის.")); return; }
      data.bookings.forEach(function (row) {
        var box = el("div", "card" + (row.done ? " done" : ""));
        var head = el("p");
        head.appendChild(el("span", "who", row.name));
        head.appendChild(el("span", "meta", row.org ? " · " + row.org : ""));
        box.appendChild(head);
        box.appendChild(el("p", "meta", row.contact));
        if (row.topic) box.appendChild(el("p", "", row.topic));
        var bits = [];
        if (row.wanted) bits.push("თარიღი: " + row.wanted);
        if (row.audience) bits.push("აუდიტორია: " + row.audience);
        if (bits.length) box.appendChild(el("p", "meta", bits.join(" · ")));
        if (row.message) box.appendChild(el("p", "msg", row.message));
        box.appendChild(el("p", "meta", when(row.created)));
        var actions = el("p", "actions");
        if (!row.done) {
          var done = el("button", "keep", "დამუშავებულია");
          done.onclick = function () { call("/api/bookings/" + row.id + "/done", "POST").then(render); };
          actions.appendChild(done);
        }
        var drop = el("button", "drop", "წაშლა");
        drop.onclick = function () { if (confirm("წავშალოთ?")) call("/api/bookings/" + row.id, "DELETE").then(render); };
        actions.appendChild(drop);
        box.appendChild(actions);
        view.appendChild(box);
      });
    });
  }

  function stats() {
    call("/api/stats").then(function (r) { return r.ok ? r.json() : null; }).then(function (s) {
      if (!s) return;
      view.textContent = "";
      var tiles = el("div", "tiles");
      [[s.total, "ნახვა სულ"], [s.notesWaiting, "ჩანაწერი ელოდება"], [s.bookingsOpen, "ღია მოწვევა"]]
        .forEach(function (pair) {
          var tile = el("div", "tile");
          tile.appendChild(el("b", "", String(pair[0])));
          tile.appendChild(el("span", "", pair[1]));
          tiles.appendChild(tile);
        });
      view.appendChild(tiles);

      function table(title, rows, key) {
        if (!rows.length) return;
        view.appendChild(el("h2", "", title));
        var max = rows.reduce(function (m, r) { return Math.max(m, Number(r.n)); }, 1);
        var t = el("table");
        rows.forEach(function (row) {
          var tr = el("tr");
          tr.appendChild(el("td", "", row[key]));
          var td = el("td");
          var bar = el("span", "bar");
          bar.style.width = Math.max(2, Math.round(Number(row.n) / max * 100)) + "%";
          td.appendChild(bar);
          tr.appendChild(td);
          tr.appendChild(el("td", "meta", String(row.n)));
          t.appendChild(tr);
        });
        view.appendChild(t);
      }
      table("ბოლო 14 დღე", s.days, "day");
      table("გვერდები", s.pages, "path");
      table("საიდან მოდიან", s.referrers, "domain");
      if (!s.total) view.appendChild(el("p", "empty", "ნახვები ჯერ არ დაფიქსირებულა."));
    });
  }

  function render() {
    /* the counts also tell us which mode the guest book is in, so they come first */
    return counts().then(function () {
      if (tab === "notes") return notes();
      if (tab === "bookings") return bookings();
      return stats();
    });
  }

  Array.prototype.forEach.call(document.querySelectorAll(".tabs button"), function (button) {
    button.onclick = function () {
      Array.prototype.forEach.call(document.querySelectorAll(".tabs button"), function (b) {
        b.classList.remove("on");
      });
      button.classList.add("on");
      tab = button.getAttribute("data-tab");
      render();
    };
  });

  var enter = function () {
    token = document.getElementById("token").value.trim();
    render();
  };
  document.getElementById("go").onclick = enter;
  document.getElementById("token").addEventListener("keydown", function (event) {
    if (event.key === "Enter") { event.preventDefault(); enter(); }
  });
  if (token) render();
})();
</script>
</body>
</html>
"""


DB_READY = True
USING_POSTGRES = bool(DATABASE_URL and psycopg)

SQLITE_EXTRA = [
    """CREATE TABLE IF NOT EXISTS views (
        day   TEXT NOT NULL,
        path  TEXT NOT NULL,
        lang  TEXT NOT NULL DEFAULT '',
        hits  INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (day, path, lang))""",
    """CREATE TABLE IF NOT EXISTS referrers (
        day    TEXT NOT NULL,
        domain TEXT NOT NULL,
        hits   INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (day, domain))""",
    """CREATE TABLE IF NOT EXISTS bookings (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        name     TEXT NOT NULL,
        contact  TEXT NOT NULL,
        org      TEXT NOT NULL DEFAULT '',
        wanted   TEXT NOT NULL DEFAULT '',
        audience TEXT NOT NULL DEFAULT '',
        topic    TEXT NOT NULL DEFAULT '',
        message  TEXT NOT NULL DEFAULT '',
        lang     TEXT NOT NULL DEFAULT '',
        created  BIGINT NOT NULL,
        done     INTEGER NOT NULL DEFAULT 0)""",
]

POSTGRES_EXTRA = [
    """CREATE TABLE IF NOT EXISTS views (
        day   TEXT NOT NULL,
        path  TEXT NOT NULL,
        lang  TEXT NOT NULL DEFAULT '',
        hits  INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (day, path, lang))""",
    """CREATE TABLE IF NOT EXISTS referrers (
        day    TEXT NOT NULL,
        domain TEXT NOT NULL,
        hits   INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (day, domain))""",
    """CREATE TABLE IF NOT EXISTS bookings (
        id       SERIAL PRIMARY KEY,
        name     TEXT NOT NULL,
        contact  TEXT NOT NULL,
        org      TEXT NOT NULL DEFAULT '',
        wanted   TEXT NOT NULL DEFAULT '',
        audience TEXT NOT NULL DEFAULT '',
        topic    TEXT NOT NULL DEFAULT '',
        message  TEXT NOT NULL DEFAULT '',
        lang     TEXT NOT NULL DEFAULT '',
        created  BIGINT NOT NULL,
        done     INTEGER NOT NULL DEFAULT 0)""",
]

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
            for statement in (POSTGRES_EXTRA if self.postgres else SQLITE_EXTRA):
                self._execute(conn, statement, ())

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


NOTIFY_WEBHOOK = os.environ.get("NOTIFY_WEBHOOK", "").strip()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT = os.environ.get("TELEGRAM_CHAT_ID", "").strip()


def notify(title, body):
    """Tell him something arrived. Never blocks or breaks the request."""
    def send():
        text = "%s\n%s" % (title, body)
        try:
            if TELEGRAM_TOKEN and TELEGRAM_CHAT:
                payload = json.dumps({"chat_id": TELEGRAM_CHAT, "text": text,
                                      "disable_web_page_preview": True}).encode("utf-8")
                request = urllib.request.Request(
                    "https://api.telegram.org/bot%s/sendMessage" % TELEGRAM_TOKEN,
                    data=payload, headers={"Content-Type": "application/json"})
                urllib.request.urlopen(request, timeout=8).close()
            if NOTIFY_WEBHOOK:
                payload = json.dumps({"title": title, "text": body,
                                      "content": text}).encode("utf-8")
                request = urllib.request.Request(
                    NOTIFY_WEBHOOK, data=payload,
                    headers={"Content-Type": "application/json"})
                urllib.request.urlopen(request, timeout=8).close()
        except Exception:                   # noqa: BLE001 - a failed ping is not an error
            pass

    if TELEGRAM_TOKEN or NOTIFY_WEBHOOK:
        threading.Thread(target=send, daemon=True).start()


def today():
    return time.strftime("%Y-%m-%d", time.gmtime())


def referrer_domain(value):
    value = str(value or "").strip()[:200]
    if not value:
        return ""
    try:
        host = urllib.parse.urlparse(value).netloc.lower()
    except ValueError:
        return ""
    if host.startswith("www."):
        host = host[4:]
    return host[:80]


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

    def redirected(self):
        """True when the request came in on some other host and has been sent
        to the canonical one. Health checks are answered where they are asked."""
        if not CANONICAL_HOST:
            return False
        host = (self.headers.get("Host") or "").split(":")[0].lower()
        if not host or host == CANONICAL_HOST or host in ("localhost", "127.0.0.1"):
            return False
        path = self.path.split("?")[0]
        if path.startswith("/api/") or path in ("/healthz", "/admin"):
            return False          # a client mid-request is not an audience to move
        self.send_response(301)
        self.send_header("Location", "https://%s%s" % (CANONICAL_HOST, self.path))
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Length", "0")
        self.end_headers()
        return True

    # ----------------------------------------------------------------- GET
    def do_GET(self):
        if self.redirected():
            return
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
            # booleans only: enough to see what is set up, nothing to give away
            return self.send_json({"ok": True, "guestbook": DB_READY,
                                   "store": "postgres" if USING_POSTGRES else "sqlite",
                                   "databaseUrl": bool(DATABASE_URL),
                                   "psycopg": bool(psycopg),
                                   "autoApprove": AUTO_APPROVE,
                                   "token": bool(TOKEN)})
        if path == "/api/guestbook":
            if not DB_READY:
                return self.send_json({"error": "unavailable"}, 503)
            rows = STORE.rows("SELECT id, name, place, message, created FROM notes "
                              "WHERE approved = 1 ORDER BY id DESC LIMIT 200")
            return self.send_json({"notes": rows, "moderated": not AUTO_APPROVE})
        if path == "/api/stats":
            if not self.authorised():
                return self.send_json({"error": "unauthorised"}, 401)
            if not DB_READY:
                return self.send_json({"error": "unavailable"}, 503)
            since = time.strftime("%Y-%m-%d", time.gmtime(time.time() - 14 * 86400))
            return self.send_json({
                "total": STORE.rows("SELECT COALESCE(SUM(hits), 0) AS n FROM views")[0]["n"],
                "days": STORE.rows(
                    "SELECT day, SUM(hits) AS n FROM views WHERE day >= ? "
                    "GROUP BY day ORDER BY day", (since,)),
                "pages": STORE.rows(
                    "SELECT path, SUM(hits) AS n FROM views WHERE day >= ? "
                    "GROUP BY path ORDER BY n DESC LIMIT 12", (since,)),
                "referrers": STORE.rows(
                    "SELECT domain, SUM(hits) AS n FROM referrers WHERE day >= ? "
                    "GROUP BY domain ORDER BY n DESC LIMIT 10", (since,)),
                "notesWaiting": STORE.rows(
                    "SELECT COUNT(*) AS n FROM notes WHERE approved = 0")[0]["n"],
                "bookingsOpen": STORE.rows(
                    "SELECT COUNT(*) AS n FROM bookings WHERE done = 0")[0]["n"],
                "autoApprove": AUTO_APPROVE,
            })

        if path == "/api/bookings":
            if not self.authorised():
                return self.send_json({"error": "unauthorised"}, 401)
            if not DB_READY:
                return self.send_json({"error": "unavailable"}, 503)
            return self.send_json({"bookings": STORE.rows(
                "SELECT id, name, contact, org, wanted, audience, topic, message, created, done "
                "FROM bookings ORDER BY done, id DESC LIMIT 200")})

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
            posted_today = STORE.rows(
                "SELECT COUNT(*) AS n FROM notes WHERE source_ip = ? AND created > ?",
                (ip, now - 86400))[0]["n"]
            if posted_today >= MAX_PER_DAY:
                return self.send_json({"error": "too many"}, 429)
            STORE.run(
                "INSERT INTO notes (name, place, message, lang, source_ip, created, approved)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (name, place, message, clean(payload.get("lang"), 5), ip, now,
                 1 if AUTO_APPROVE else 0))
            notify("ახალი ჩანაწერი / New note", "%s%s\n%s" % (
                name, (" · " + place) if place else "", message[:300]))
            if AUTO_APPROVE:
                # hand the note straight back so the page can show it at once
                return self.send_json({"ok": True, "pending": False,
                                       "note": {"name": name, "place": place,
                                                "message": message}})
            return self.send_json({"ok": True, "pending": True})

        if path == "/api/hit":
            # one anonymous count per page view: no address, no fingerprint
            if not DB_READY:
                return self.send_json({"ok": False})
            payload = self.read_json() or {}
            page = clean(payload.get("path"), 120)
            if not page.startswith("/"):
                return self.send_json({"ok": False})
            lang = clean(payload.get("lang"), 5)
            day = today()
            if STORE.postgres:
                STORE.run("INSERT INTO views (day, path, lang, hits) VALUES (?, ?, ?, 1) "
                          "ON CONFLICT (day, path, lang) DO UPDATE SET hits = views.hits + 1",
                          (day, page, lang))
            else:
                STORE.run("INSERT INTO views (day, path, lang, hits) VALUES (?, ?, ?, 1) "
                          "ON CONFLICT (day, path, lang) DO UPDATE SET hits = hits + 1",
                          (day, page, lang))
            domain = referrer_domain(payload.get("ref"))
            if domain:
                if STORE.postgres:
                    STORE.run("INSERT INTO referrers (day, domain, hits) VALUES (?, ?, 1) "
                              "ON CONFLICT (day, domain) DO UPDATE SET hits = referrers.hits + 1",
                              (day, domain))
                else:
                    STORE.run("INSERT INTO referrers (day, domain, hits) VALUES (?, ?, 1) "
                              "ON CONFLICT (day, domain) DO UPDATE SET hits = hits + 1",
                              (day, domain))
            return self.send_json({"ok": True})

        if path == "/api/booking":
            if not DB_READY:
                return self.send_json({"error": "unavailable"}, 503)
            payload = self.read_json()
            if payload is None:
                return self.send_json({"error": "bad request"}, 400)
            if clean(payload.get("website"), 10):            # honeypot
                return self.send_json({"ok": True})
            name = clean(payload.get("name"), 80)
            contact = clean(payload.get("contact"), 120)
            message = clean(payload.get("message"), 900)
            if not name or not contact:
                return self.send_json({"error": "name and contact are required"}, 400)

            now = int(time.time())
            ip = self.client_ip()
            recent = STORE.rows(
                "SELECT created FROM bookings WHERE contact = ? ORDER BY id DESC LIMIT 1",
                (contact,))
            if recent and now - recent[0]["created"] < COOLDOWN_SECONDS:
                return self.send_json({"error": "too soon"}, 429)

            STORE.run(
                "INSERT INTO bookings (name, contact, org, wanted, audience, topic, message,"
                " lang, created, done) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)",
                (name, contact, clean(payload.get("org"), 120), clean(payload.get("wanted"), 60),
                 clean(payload.get("audience"), 120), clean(payload.get("topic"), 160),
                 message, clean(payload.get("lang"), 5), now))
            notify("ახალი მოწვევა / New request", "%s (%s)\n%s\n%s" % (
                name, contact, clean(payload.get("topic"), 160), message[:300]))
            return self.send_json({"ok": True})

        match = re.match(r"^/api/bookings/(\d+)/done$", path)
        if match:
            if not self.authorised():
                return self.send_json({"error": "unauthorised"}, 401)
            STORE.run("UPDATE bookings SET done = 1 WHERE id = ?", (int(match.group(1)),))
            return self.send_json({"ok": True})

        match = re.match(r"^/api/guestbook/(\d+)/approve$", path)
        if match:
            if not self.authorised():
                return self.send_json({"error": "unauthorised"}, 401)
            STORE.run("UPDATE notes SET approved = 1 WHERE id = ?", (int(match.group(1)),))
            return self.send_json({"ok": True})

        return self.send_json({"error": "not found"}, 404)

    # -------------------------------------------------------------- DELETE
    def do_DELETE(self):
        path = self.path.split("?")[0]
        if not self.authorised():
            return self.send_json({"error": "unauthorised"}, 401)
        match = re.match(r"^/api/guestbook/(\d+)$", path)
        if match:
            STORE.run("DELETE FROM notes WHERE id = ?", (int(match.group(1)),))
            return self.send_json({"ok": True})
        match = re.match(r"^/api/bookings/(\d+)$", path)
        if match:
            STORE.run("DELETE FROM bookings WHERE id = ?", (int(match.group(1)),))
            return self.send_json({"ok": True})
        return self.send_json({"error": "not found"}, 404)

    def list_directory(self, path):         # no directory listings
        self.send_error(404, "Not found")
        return None

    # Nothing here is fingerprinted, so a browser must not be left holding a page
    # from before the last deploy: pages and scripts are revalidated every time
    # (a 304 costs nothing), while photographs and fonts may be kept.
    LONG_LIVED = (".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif", ".ico",
                  ".woff", ".woff2", ".ttf")

    # a few types older Pythons do not know by heart
    extensions_map = dict(SimpleHTTPRequestHandler.extensions_map)
    extensions_map.update({
        ".webp": "image/webp", ".avif": "image/avif", ".woff2": "font/woff2",
        ".webmanifest": "application/manifest+json", ".mp4": "video/mp4",
        ".webm": "video/webm", ".svg": "image/svg+xml",
    })

    def send_header(self, keyword, value):
        if keyword.lower() == "cache-control":
            self._cache_told = True
        super().send_header(keyword, value)

    def end_headers(self):
        if not getattr(self, "_cache_told", False):
            ext = os.path.splitext(self.path.split("?")[0])[1].lower()
            self.send_header("Cache-Control",
                             "public, max-age=604800" if ext in self.LONG_LIVED else "no-cache")
        super().end_headers()

    def handle_one_request(self):
        self._cache_told = False
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
    print("notes: %s" % ("published at once (GUESTBOOK_AUTO_APPROVE)"
                         if AUTO_APPROVE else "held until approved at /admin"))
    if TELEGRAM_TOKEN and TELEGRAM_CHAT:
        print("notifications: Telegram")
    elif NOTIFY_WEBHOOK:
        print("notifications: webhook")
    if DATABASE_URL and not psycopg:
        print("! DATABASE_URL is set but psycopg is not installed — using SQLite instead")
    if not DATABASE_URL:
        print("! DATABASE_URL is not set — notes are kept in SQLite inside the container "
              "and are LOST on the next deploy. On Railway add the variable as "
              "${{Postgres.DATABASE_URL}}.")
    print("guest book storage: %s" % ("PostgreSQL" if USING_POSTGRES else "SQLite at %s" % DB_PATH))
    print("serving %s on http://0.0.0.0:%d" % (ROOT, PORT))
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
