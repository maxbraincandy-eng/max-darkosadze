#!/usr/bin/env python3
"""Draw a share image for every page and every article, in both languages.

These are the pictures that appear when a link is posted to Facebook, WhatsApp,
Telegram, X or LinkedIn. Each one carries the page's own title rather than one
generic photograph.

    python3 tools/og_images.py        # writes assets/og/<lang>-<name>.jpg

Needs Pillow. Run it again after changing a title.
"""

import json
import os
import re

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "tools", "fonts")
OUT = os.path.join(ROOT, "assets", "og")

W, H = 1200, 630
INK = (8, 9, 11)                  # the site's own ground
INK_SOFT = (17, 19, 24)
VIOLET = (124, 92, 255)
VIOLET_SOFT = (154, 130, 255)
PAPER = (242, 242, 240)
MUTED = (154, 157, 165)
PAD = 68

GEORGIAN = re.compile(r"[\u10A0-\u10FF\u1C90-\u1CBF]")


def display(text, size):
    """The site sets Latin in Newsreader and Georgian in Noto Serif Georgian.
    One file cannot draw both, so the text itself chooses."""
    if GEORGIAN.search(text):
        return font("NotoSerifGeorgian.ttf", size, 600)
    return ImageFont.truetype(os.path.join(FONTS, "Newsreader-SemiBold.ttf"), size)


def spaced(draw, xy, text, fnt, fill, tracking, anchor_mid=False):
    """Pillow has no letter-spacing, and the small capitals on this site live by
    it. Drawn letter by letter, returning the width it used."""
    width = sum(draw.textlength(ch, font=fnt) + tracking for ch in text) - tracking
    x, y = xy
    if anchor_mid:
        y -= fnt.size / 2
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return width


def font(name, size, weight=None):
    path = os.path.join(FONTS, name)
    f = ImageFont.truetype(path, size)
    if weight is not None:
        try:
            f.set_variation_by_axes([weight, 100])   # axis order is Weight, Width
        except Exception:
            pass
    return f


def clean(text):
    """Strip the editing markers so they never reach a share card."""
    out = str(text)
    for a, b in (("[[", ""), ("]]", ""), ("**", ""), ("*", "")):
        out = out.replace(a, b)
    return out.strip()


def wrap(draw, text, fnt, width, max_lines):
    words, lines, line = text.split(), [], ""
    for word in words:
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
            if len(lines) == max_lines:
                break
    if line and len(lines) < max_lines:
        lines.append(line)
    if len(lines) == max_lines and len(" ".join(lines)) < len(text):
        while lines[-1] and draw.textlength(lines[-1] + "…", font=fnt) > width:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "…"
    return lines


def fit(draw, text, fnt, width):
    """Trim a line to the space it has, with an ellipsis if it had to be cut."""
    if draw.textlength(text, font=fnt) <= width:
        return text
    while text and draw.textlength(text + "…", font=fnt) > width:
        text = text[:-1]
    return text.rstrip(" ·-—") + "…"


SPLIT = 744                       # where the ink panel ends and the photograph starts


def background(photo_path):
    """Two panels, the way the site itself sets a page: the words on the ink
    ground, the photograph in its own frame beside them at full colour. Nothing
    fades across the face, and nothing is greyed out."""
    base = Image.new("RGB", (W, H), INK)
    grad = Image.new("L", (W, 1))
    for x in range(W):
        grad.putpixel((x, 0), int(255 * (x / SPLIT) ** 1.5) if x < SPLIT else 255)
    base = Image.composite(Image.new("RGB", (W, H), INK_SOFT), base, grad.resize((W, H)))

    # the violet the site uses for emphasis, low and behind the words
    glow = Image.new("RGB", (W, H), (40, 28, 96))
    gmask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(gmask).ellipse((-460, 120, 520, 900), fill=120)
    base = Image.composite(glow, base, gmask.filter(ImageFilter.GaussianBlur(150)))

    if photo_path and os.path.exists(photo_path):
        frame_w = W - SPLIT
        with Image.open(photo_path) as im:
            photo = im.convert("RGB")
        ratio = max(frame_w / photo.width, H / photo.height)
        photo = photo.resize((max(frame_w, int(photo.width * ratio)),
                              max(H, int(photo.height * ratio))), Image.LANCZOS)
        left = (photo.width - frame_w) // 2
        top = int((photo.height - H) * 0.32)        # faces sit above the middle
        base.paste(photo.crop((left, top, left + frame_w, top + H)), (SPLIT, 0))

        # a hairline where the two panels meet, and the ink reaching a little
        # way into the picture so the join is a seam and not a cut
        veil = Image.new("RGB", (W, H), INK)
        vmask = Image.new("L", (W, 1), 0)
        for x in range(W):
            if SPLIT <= x < SPLIT + 90:
                vmask.putpixel((x, 0), int(190 * (1 - (x - SPLIT) / 90) ** 1.4))
        base = Image.composite(veil, base, vmask.resize((W, H)))
        ImageDraw.Draw(base).rectangle((SPLIT, 0, SPLIT + 2, H), fill=VIOLET)
    return base


def monogram(img, x, y, size=78):
    """The mark itself, so the card and the browser tab show one thing."""
    path = os.path.join(ROOT, "assets", "icons", "icon-192.png")
    if not os.path.exists(path):
        return
    with Image.open(path) as im:
        mark = im.convert("RGB").resize((size, size), Image.LANCZOS)
    img.paste(mark, (x, y))


def card(title, eyebrow, footer, photo, out_path, lang):
    sans = "NotoSansGeorgian.ttf"
    img = background(photo)
    d = ImageDraw.Draw(img)

    monogram(img, PAD, PAD)
    d = ImageDraw.Draw(img)

    if eyebrow:
        f_eye = font(sans, 23, 600)
        label = clean(eyebrow)
        if lang == "en":
            label = label.upper()
        spaced(d, (PAD + 100, PAD + 39 - f_eye.size * 0.05), fit(d, label, f_eye, SPLIT - PAD * 2 - 100),
               f_eye, MUTED, 2.6 if lang == "en" else 1.0, anchor_mid=True)

    column = SPLIT - PAD * 2
    size = 66 if len(title) < 40 else (56 if len(title) < 72 else 46)
    f_title = display(clean(title), size)
    lines = wrap(d, clean(title), f_title, column, 3)
    line_height = int(size * 1.2)
    top = H - PAD - 118 - line_height * len(lines)
    for i, line in enumerate(lines):
        d.text((PAD, top + i * line_height), line, font=f_title, fill=PAPER)

    # the short violet rule the site puts under everything it means
    d.rectangle((PAD, H - PAD - 86, PAD + 88, H - PAD - 82), fill=VIOLET)
    f_foot = font(sans, 25, 500)
    d.text((PAD, H - PAD - 56), fit(d, clean(footer), f_foot, SPLIT - PAD * 2),
           font=f_foot, fill=MUTED)

    img.save(out_path, "JPEG", quality=88, optimize=True, progressive=True)
    return out_path


def main():
    os.makedirs(OUT, exist_ok=True)
    made = 0
    for lang in ("en", "ka"):
        with open(os.path.join(ROOT, "content", "%s.json" % lang), encoding="utf-8") as fh:
            data = json.load(fh)
        site_name = data["meta"]["siteName"]
        nickname = data["meta"]["nickname"]
        footer = "%s · %s" % (site_name, nickname)

        pages = data["pages"]
        home_photo = os.path.join(ROOT, "assets", "img", "portrait.jpg")
        card(pages["home"]["heroTitle"], pages["home"]["heroEyebrow"],
             clean(data["meta"]["tagline"]), home_photo,
             os.path.join(OUT, "%s-home.jpg" % lang), lang)
        made += 1

        for key in ("about", "articles", "news", "foundation", "gallery", "legend", "guestbook", "contact", "press"):
            page = pages.get(key)
            if not page:
                continue
            photo = {"about": "portrait.jpg", "foundation": "foundation.jpg",
                     "gallery": "gallery/01.jpg", "legend": "honours.jpg", "guestbook": "gallery/16.jpg"}.get(key, "portrait.jpg")
            card(page["heading"], page["eyebrow"], footer,
                 os.path.join(ROOT, "assets", "img", photo),
                 os.path.join(OUT, "%s-%s.jpg" % (lang, key)), lang)
            made += 1

        for article in data["articles"]:
            photo = article.get("imagePortrait") or article["image"]
            card(article["title"], article["category"], footer,
                 os.path.join(ROOT, photo),
                 os.path.join(OUT, "%s-article-%s.jpg" % (lang, article["slug"])), lang)
            made += 1

    print("%d share images written to assets/og/" % made)


if __name__ == "__main__":
    main()
