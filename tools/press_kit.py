#!/usr/bin/env python3
"""Rebuild the press-kit archive from the photographs in assets/img.

    python3 tools/press_kit.py

Run it after adding or replacing photographs. Uses only the standard library.
"""

import glob
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "press", "max-darkosadze-photos.zip")
NOTE = (
    "Photographs of Max Darkosadze (Mr. Max) for editorial use.\n"
    "მაქს დარკოსაძის ფოტოები რედაქციული გამოყენებისთვის.\n\n"
    "Please credit the photographer where known.\n"
    "გთხოვთ, მიუთითოთ ფოტოს ავტორი, სადაც ცნობილია.\n"
)


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sources = sorted(
        glob.glob(os.path.join(ROOT, "assets", "img", "*.jpg"))
        + glob.glob(os.path.join(ROOT, "assets", "img", "gallery", "*.jpg"))
    )
    sources = [f for f in sources if "-800" not in os.path.basename(f)]

    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sources:
            folder = "gallery/" if os.sep + "gallery" + os.sep in path else ""
            archive.write(path, "max-darkosadze-photos/%s%s" % (folder, os.path.basename(path)))
        archive.writestr("max-darkosadze-photos/README.txt", NOTE)

    print("%s — %d photographs, %d KB" % (
        os.path.relpath(OUT, ROOT), len(sources), os.path.getsize(OUT) // 1024))


if __name__ == "__main__":
    main()
