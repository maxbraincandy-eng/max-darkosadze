#!/usr/bin/env python3
"""Prepare the photographs for the web.

Writes assets/img/manifest.json (every image's real pixel size, so the pages can
reserve the right space and never jump while loading) and, for each large
photograph, a smaller -800 variant that phones download instead of the full one.

    python3 tools/images.py

Needs Pillow (pip install Pillow). build.py itself needs nothing — it just reads
the manifest if it is there.
"""

import json
import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required: pip install Pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "img")
SMALL_WIDTH = 800
VARIANT = "-800"


def is_source(name):
    return (name.lower().endswith((".jpg", ".jpeg"))
            and VARIANT not in name)


def main():
    manifest = {}
    made = 0
    for dirpath, _dirs, files in os.walk(IMG):
        for name in sorted(files):
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
            if name.lower().endswith(".svg"):
                continue
            if not name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                continue
            with Image.open(path) as im:
                manifest[rel] = list(im.size)
                if is_source(name) and im.width > SMALL_WIDTH * 1.25:
                    small_rel = rel.rsplit(".", 1)[0] + VARIANT + ".jpg"
                    small_path = os.path.join(ROOT, small_rel)
                    if not os.path.exists(small_path) or \
                            os.path.getmtime(small_path) < os.path.getmtime(path):
                        copy = im.convert("RGB")
                        copy.thumbnail((SMALL_WIDTH, SMALL_WIDTH * 4), Image.LANCZOS)
                        copy.save(small_path, "JPEG", quality=80,
                                  optimize=True, progressive=True)
                        made += 1
                    with Image.open(small_path) as small:
                        manifest[small_rel] = list(small.size)

                # WebP beside each JPEG: the same picture, roughly half the
                # bytes, with the JPEG left in place for anything that cannot
                # read it.
                if is_source(name) or VARIANT in name:
                    webp_rel = rel.rsplit(".", 1)[0] + ".webp"
                    webp_path = os.path.join(ROOT, webp_rel)
                    if not os.path.exists(webp_path) or \
                            os.path.getmtime(webp_path) < os.path.getmtime(path):
                        im.convert("RGB").save(webp_path, "WEBP", quality=76, method=5)
                        made += 1
                    with Image.open(webp_path) as w:
                        manifest[webp_rel] = list(w.size)

    out = os.path.join(IMG, "manifest.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1, sort_keys=True)
    print("%d images measured, %d small variants written" % (len(manifest), made))
    print("manifest: " + os.path.relpath(out, ROOT))


if __name__ == "__main__":
    main()
