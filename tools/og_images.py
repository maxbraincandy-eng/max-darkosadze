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

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "tools", "fonts")
OUT = os.path.join(ROOT, "assets", "og")

W, H = 1200, 630
INK = (13, 27, 42)
INK_SOFT = (22, 40, 60)
GOLD = (201, 162, 39)
GOLD_LIGHT = (230, 193, 90)
WHITE = (255, 255, 255)
MUTED = (168, 182, 196)
PAD = 68


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


def background(photo_path):
    """Ink gradient, with the page's own photograph fading in from the right."""
    base = Image.new("RGB", (W, H), INK)
    grad = Image.new("L", (W, 1))
    for x in range(W):
        grad.putpixel((x, 0), int(255 * (x / W) ** 1.4))
    grad = grad.resize((W, H))
    base = Image.composite(Image.new("RGB", (W, H), INK_SOFT), base, grad)

    if photo_path and os.path.exists(photo_path):
        with Image.open(photo_path) as im:
            photo = im.convert("RGB")
        ratio = max(W / photo.width, H / photo.height)
        photo = photo.resize((int(photo.width * ratio), int(photo.height * ratio)), Image.LANCZOS)
        left = (photo.width - W) // 2
        photo = photo.crop((left, 0, left + W, H))
        photo = ImageEnhance.Color(photo).enhance(0.75)
        mask = Image.new("L", (W, 1))
        for x in range(W):
            t = max(0.0, (x - W * 0.42) / (W * 0.58))
            mask.putpixel((x, 0), int(235 * (t ** 1.6)))
        base = Image.composite(photo, base, mask.resize((W, H)))

    glow = Image.new("RGB", (W, H), (60, 48, 12))
    gmask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(gmask).ellipse((-360, -460, 620, 300), fill=95)
    base = Image.composite(glow, base, gmask.filter(ImageFilter.GaussianBlur(120)))
    return base


def card(title, eyebrow, footer, photo, out_path, lang):
    serif = "NotoSerifGeorgian.ttf"
    sans = "NotoSansGeorgian.ttf"
    img = background(photo)
    d = ImageDraw.Draw(img)

    # monogram
    d.rounded_rectangle((PAD, PAD, PAD + 78, PAD + 78), radius=18, outline=GOLD, width=3)
    mono = font(serif, 34, 700)
    d.text((PAD + 39, PAD + 41), "MD", font=mono, fill=GOLD_LIGHT, anchor="mm")

    if eyebrow:
        f_eye = font(sans, 25, 600)
        label = clean(eyebrow).upper() if lang == "en" else clean(eyebrow)
        d.text((PAD + 100, PAD + 40), fit(d, label, f_eye, W - PAD * 2 - 100),
               font=f_eye, fill=GOLD_LIGHT, anchor="lm")

    size = 70 if len(title) < 46 else (58 if len(title) < 78 else 48)
    f_title = font(serif, size, 700)
    text_width = int(W * 0.74)
    lines = wrap(d, clean(title), f_title, text_width, 3)
    line_height = int(size * 1.22)
    top = H - PAD - 104 - line_height * len(lines)
    for i, line in enumerate(lines):
        d.text((PAD, top + i * line_height), line, font=f_title, fill=WHITE)

    d.line((PAD, H - PAD - 74, PAD + 92, H - PAD - 74), fill=GOLD, width=4)
    f_foot = font(sans, 26, 500)
    d.text((PAD, H - PAD - 42), fit(d, clean(footer), f_foot, int(W * 0.8)),
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

        for key in ("about", "articles", "news", "foundation", "gallery", "contact", "press"):
            page = pages.get(key)
            if not page:
                continue
            photo = {"about": "portrait.jpg", "foundation": "foundation.jpg",
                     "gallery": "gallery/01.jpg"}.get(key, "portrait.jpg")
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
