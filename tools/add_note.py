#!/usr/bin/env python3
"""Add a note to the guest book by hand, in both languages, and rebuild.

Use it for notes that arrive by e-mail or Instagram rather than through a live
guest book.

    python3 tools/add_note.py --name "ნინო" --place "თბილისი" \
        --message "ბატონმა მაქსმა დედაჩემი მოარჩინა. მადლობა."

The note is written into content/ka.json and content/en.json exactly as given —
the same words appear on both versions of the page, since that is what the
person wrote. Add --only ka (or en) to put it on one of them only.
"""

import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser(description="Add a guest-book note.")
    parser.add_argument("--name", required=True, help="the name or nickname they chose")
    parser.add_argument("--message", required=True, help="what they wrote")
    parser.add_argument("--place", default="", help="where they met him (optional)")
    parser.add_argument("--only", choices=["ka", "en"], help="put it on one language only")
    parser.add_argument("--no-build", action="store_true", help="do not run build.py afterwards")
    args = parser.parse_args()

    note = {"name": args.name.strip(), "message": args.message.strip()}
    if args.place.strip():
        note["place"] = args.place.strip()
    if not note["name"] or len(note["message"]) < 2:
        sys.exit("A name and a message are both needed.")

    for lang in (["ka", "en"] if not args.only else [args.only]):
        path = os.path.join(ROOT, "content", "%s.json" % lang)
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        entries = data["pages"]["guestbook"].setdefault("entries", [])
        entries.insert(0, dict(note))          # newest first
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        print("added to %s (%d notes)" % (lang, len(entries)))

    if not args.no_build:
        subprocess.run([sys.executable, os.path.join(ROOT, "build.py")], check=True,
                       stdout=subprocess.DEVNULL)
        print("pages rebuilt — commit and push to publish")


if __name__ == "__main__":
    main()
