#!/usr/bin/env python3
"""Draw the mark: the MD monogram that stands for the site everywhere it is
small — the browser tab, the search result, the phone's home screen, the
bookmark bar.

    python3 tools/logo.py

Writes, all from one drawing so nothing drifts apart:

    favicon.ico                     16, 32, 48 — what Google reads first
    assets/img/favicon.svg          the sharp one, for browsers that take SVG
    assets/icons/icon-48…512.png    the sizes a search result and a phone use
    assets/icons/maskable-512.png   for Android, which crops the corners
    assets/icons/apple-touch-icon.png
    assets/brand/logo-dark.png      the mark on the site's own ground, for slides
    assets/brand/logo-light.png     the same mark for a white page

Google wants a square icon, a multiple of 48 px, reachable and unchanged for a
while; it picks it up on its own schedule after the next crawl.

Needs Pillow.
"""

import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("This needs Pillow:  pip install Pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "tools", "fonts", "Newsreader-SemiBold.ttf")

INK = (8, 9, 11)
PAPER = (242, 242, 240)
VIOLET = (124, 92, 255)
BLUE = (126, 167, 255)

SIZES = (48, 96, 144, 192, 512)


def face(size):
    return ImageFont.truetype(FONT, size)


def mark(size, *, text="MD", ground=INK, letters=PAPER, accent=VIOLET,
         width=.58, rule_weight=.026, ring=True):
    """The monogram on a square: two letters, a rule beneath them, a hairline
    round the edge. Everything is proportional, so it holds at 16 px and at 512.

    `width` is how much of the square the letters take. Small favicons are read
    at a glance, so the letters stay large and the air around them stays even."""
    scale = 8 if size < 128 else 1           # draw large, shrink once: cleaner edges
    s = size * scale
    img = Image.new("RGBA", (s, s), ground + (255,))
    d = ImageDraw.Draw(img)

    if ring:
        inset = s * 0.065
        d.rounded_rectangle((inset, inset, s - inset, s - inset),
                            radius=s * 0.20, outline=accent + (215,),
                            width=max(1, int(round(s * 0.022))))

    # the letters, fitted to the width they are allowed
    box = s * width
    point = int(s * 0.60)
    while point > 6:
        f = face(point)
        left, top, right, bottom = d.textbbox((0, 0), text, font=f)
        if right - left <= box:
            break
        point -= 1
    f = face(point)
    left, top, right, bottom = d.textbbox((0, 0), text, font=f)
    letter_w, letter_h = right - left, bottom - top

    # the letters and the rule beneath them are centred together, as one block
    gap = s * 0.085
    rule_h = max(1, int(round(s * rule_weight)))
    block = letter_h + gap + rule_h
    top_y = (s - block) / 2

    x = (s - letter_w) / 2 - left
    d.text((x, top_y - top), text, font=f, fill=letters + (255,))

    rule_w = letter_w * (0.62 if len(text) > 1 else 0.95)
    rule_y = top_y + letter_h + gap
    d.rectangle(((s - rule_w) / 2, rule_y, (s + rule_w) / 2, rule_y + rule_h),
                fill=accent + (255,))

    if scale > 1:
        img = img.resize((size, size), Image.LANCZOS)
    return img


def letter_paths(text, target_width):
    """The word as outlines rather than as text: a favicon is drawn before any
    web font arrives, so the SVG cannot ask for Newsreader by name. Returns the
    path data with its top-left corner at the origin, and the size it occupies."""
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.boundsPen import BoundsPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.misc.transform import Transform

    font = TTFont(FONT)
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()

    run, advance = [], 0
    for ch in text:
        name = cmap[ord(ch)]
        run.append((name, advance))
        advance += glyphs[name].width

    bounds = BoundsPen(glyphs)
    for name, shift in run:
        glyphs[name].draw(TransformPen(bounds, Transform().translate(shift, 0)))
    x0, y0, x1, y1 = bounds.bounds

    scale = target_width / (x1 - x0)
    # y flips: font units run up, SVG runs down
    place = Transform().translate(-x0 * scale, y1 * scale).scale(scale, -scale)

    out = []
    for name, shift in run:
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(TransformPen(pen, place.translate(shift, 0)))
        out.append(pen.getCommands())
    font.close()
    return " ".join(out), target_width, (y1 - y0) * scale


def svg():
    """The same drawing in vector, drawn to the same proportions as the PNGs."""
    board = 64.0
    d, w, h = letter_paths("MD", board * 0.58)
    gap, rule_h = board * 0.085, board * 0.026
    top = (board - (h + gap + rule_h)) / 2
    rule_w = w * 0.62
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="MD">
  <rect width="64" height="64" fill="#08090b"/>
  <rect x="4.16" y="4.16" width="55.68" height="55.68" rx="12.8" fill="none"
        stroke="#7c5cff" stroke-opacity=".84" stroke-width="1.4"/>
  <g transform="translate(%.2f %.2f)"><path d="%s" fill="#f2f2f0"/></g>
  <rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="#7c5cff"/>
</svg>
""" % ((board - w) / 2, top, d,
       (board - rule_w) / 2, top + h + gap, rule_w, rule_h)


def main():
    icons = os.path.join(ROOT, "assets", "icons")
    brand = os.path.join(ROOT, "assets", "brand")
    os.makedirs(icons, exist_ok=True)
    os.makedirs(brand, exist_ok=True)
    written = []

    for size in SIZES:
        path = os.path.join(icons, "icon-%d.png" % size)
        mark(size).convert("RGB").save(path, "PNG", optimize=True)
        written.append(path)

    # Android crops a circle out of the middle: keep the letters well inside
    path = os.path.join(icons, "maskable-512.png")
    mark(512, width=.44, ring=False).convert("RGB").save(path, "PNG", optimize=True)
    written.append(path)

    path = os.path.join(icons, "apple-touch-icon.png")
    mark(180).convert("RGB").save(path, "PNG", optimize=True)
    written.append(path)

    # the file every browser and crawler tries first, at the three classic sizes.
    # Sixteen pixels cannot hold two serif letters and a frame — they close up
    # into a smudge — so that size keeps only the M and the rule beneath it.
    path = os.path.join(ROOT, "favicon.ico")
    base = mark(48).convert("RGB")           # Pillow drops sizes above the source
    base.save(path, "ICO", sizes=[(16, 16), (32, 32), (48, 48)],
              append_images=[mark(16, text="M", width=.58, rule_weight=.055, ring=False).convert("RGB"),
                             mark(32).convert("RGB")])
    written.append(path)

    path = os.path.join(ROOT, "assets", "img", "favicon.svg")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(svg())
    written.append(path)

    # a large mark for slides and profiles, on both grounds
    mark(1024).convert("RGB").save(os.path.join(brand, "logo-dark.png"), "PNG", optimize=True)
    mark(1024, ground=PAPER, letters=INK, accent=VIOLET).convert("RGB").save(
        os.path.join(brand, "logo-light.png"), "PNG", optimize=True)
    written += [os.path.join(brand, "logo-dark.png"), os.path.join(brand, "logo-light.png")]

    print("the mark, in %d files:" % len(written))
    for path in written:
        print("  %-42s %5.1f KB" % (os.path.relpath(path, ROOT), os.path.getsize(path) / 1024))
    print("\nGoogle picks a favicon up on its own schedule after the next crawl;")
    print("keep it in place and unchanged and it will appear beside the result.")


if __name__ == "__main__":
    main()
