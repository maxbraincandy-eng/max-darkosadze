#!/usr/bin/env python3
"""Put the two Georgian typefaces on this site's own server.

The pages used to fetch them from Google's servers: two extra connections
before a single letter could be drawn, and every visitor announced to a third
party. The same fonts (Noto Serif Georgian and Noto Sans Georgian, both under
the SIL Open Font License, so this is allowed) are cut down here to the letters
the site actually uses and written as .woff2 into assets/fonts.

    python3 tools/webfonts.py

The width axis is pinned — nothing on the site uses it — and the weight axis is
kept, so one file covers every weight from thin to black. Run it again if the
text ever needs a character these keep out.

Needs fonttools and brotli:  pip install fonttools brotli
"""

import json
import os
import sys

try:
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont
    from fontTools.subset import Subsetter, Options
except ImportError:
    sys.exit("This needs fonttools and brotli:  pip install fonttools brotli")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "tools", "fonts")
TARGET = os.path.join(ROOT, "assets", "fonts")

FACES = [
    ("NotoSerifGeorgian.ttf", "noto-serif-georgian.woff2"),
    ("NotoSansGeorgian.ttf", "noto-sans-georgian.woff2"),
]

# Georgian, Latin, the punctuation the pages use, and a little room to spare
ALWAYS = (
    "".join(chr(c) for c in range(0x10A0, 0x1100))          # Georgian, all three cases
    + "".join(chr(c) for c in range(0x20, 0x7F))            # Latin, digits, punctuation
    + "".join(chr(c) for c in range(0x1C90, 0x1CC0))        # Mtavruli, for uppercase
    + "«»„“”‘’—–…·•№°±×÷©®™€₾$£  ​"
    + "ÀÁÂÄÇÈÉÊËÍÎÏÑÓÔÖÙÚÛÜßàáâäçèéêëíîïñóôöùúûüÿŠšŽžŒœ"
)


def text_on_the_site():
    """Every character the content files contain, so nothing goes missing."""
    seen = set(ALWAYS)
    content = os.path.join(ROOT, "content")
    for name in sorted(os.listdir(content)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(content, name), encoding="utf-8") as fh:
            seen.update(fh.read())
    return "".join(sorted(seen))


def cut(source, target, text):
    # lazy=False: the subsetter trips over lazily loaded variation data
    font = TTFont(os.path.join(SOURCE, source), lazy=False)

    options = Options()
    options.flavor = "woff2"
    options.desubroutinize = False
    options.layout_features = ["*"]         # keep the Georgian shaping rules intact
    options.name_IDs = ["*"]
    options.notdef_outline = True
    options.recalc_bounds = True
    subsetter = Subsetter(options=options)
    subsetter.populate(text=text)
    subsetter.subset(font)

    # the width axis is pinned after the cut — nothing on the site varies width,
    # and one axis fewer is a smaller file
    axes = {a.axisTag for a in font["fvar"].axes} if "fvar" in font else set()
    if "wdth" in axes:
        instantiateVariableFont(font, {"wdth": 100}, inplace=True, updateFontNames=False)

    os.makedirs(TARGET, exist_ok=True)
    out = os.path.join(TARGET, target)
    font.flavor = "woff2"
    font.save(out)
    font.close()
    before = os.path.getsize(os.path.join(SOURCE, source))
    print("  %-28s %6.1f KB  (from %.0f KB)"
          % (target, os.path.getsize(out) / 1024, before / 1024))


def main():
    text = text_on_the_site()
    print("%d characters kept" % len(text))
    for source, target in FACES:
        cut(source, target, text)
    print("\nThe stylesheet already points at assets/fonts — nothing else to do.")


if __name__ == "__main__":
    main()
