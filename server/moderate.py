#!/usr/bin/env python3
"""Read the notes waiting in the guest book, and keep or delete them.

    GUESTBOOK_TOKEN=secret python3 server/moderate.py            # list them
    GUESTBOOK_TOKEN=secret python3 server/moderate.py keep 4
    GUESTBOOK_TOKEN=secret python3 server/moderate.py delete 5

Point it elsewhere with GUESTBOOK_URL (default http://localhost:8000).
"""

import json
import os
import sys
import urllib.request

BASE = os.environ.get("GUESTBOOK_URL", "http://localhost:8000").rstrip("/")
TOKEN = os.environ.get("GUESTBOOK_TOKEN", "")


def call(path, method="GET"):
    request = urllib.request.Request(BASE + path, method=method)
    request.add_header("X-Token", TOKEN)
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def main():
    if not TOKEN:
        sys.exit("Set GUESTBOOK_TOKEN first.")
    args = sys.argv[1:]
    if not args:
        notes = call("/api/guestbook/pending")["notes"]
        if not notes:
            print("nothing waiting.")
            return
        for note in notes:
            print("#%-4d %s%s\n      %s\n" % (
                note["id"], note["name"],
                (" · " + note["place"]) if note["place"] else "", note["message"]))
        print("keep one with:  python3 server/moderate.py keep <id>")
        return
    action, note_id = args[0], args[1]
    if action == "keep":
        call("/api/guestbook/%s/approve" % note_id, "POST")
        print("kept #%s" % note_id)
    elif action == "delete":
        call("/api/guestbook/%s" % note_id, "DELETE")
        print("deleted #%s" % note_id)
    else:
        sys.exit("use: keep <id> | delete <id>")


if __name__ == "__main__":
    main()
