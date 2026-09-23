#!/usr/bin/env python3
"""Draw the brand kit: wordmark, business card, QR code, e-mail signature and
Instagram highlight covers — all from the site's own colours and fonts.

    python3 tools/brand.py

Everything lands in assets/brand/. Run it again after buying a domain: the QR
code and the card take their address from baseUrl in content/site.json.
"""

import json
import os
import re

import qrcode
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "tools", "fonts")
OUT = os.path.join(ROOT, "assets", "brand")

INK = "#08090b"                 # the site's own ground
INK_SOFT = "#15171c"
VIOLET = "#7c5cff"              # the accent, on dark
VIOLET_DEEP = "#5b3fd4"         # the same accent, readable on paper
PAPER = "#f4f3f0"
MUTED = "#9a9da5"

GEORGIAN = re.compile(r"[\u10A0-\u10FF\u1C90-\u1CBF]")


def display(text, size, weight=600):
    """Latin is set in Newsreader here, as it is on the site; Georgian in Noto
    Serif Georgian. One file cannot draw both, so the words choose the face."""
    if GEORGIAN.search(text):
        return font("NotoSerifGeorgian.ttf", int(size), weight)
    return ImageFont.truetype(os.path.join(FONTS, "Newsreader-SemiBold.ttf"), int(size))


def mark_image(size):
    """The mark that tools/logo.py draws, so every surface shows one thing."""
    path = os.path.join(ROOT, "assets", "icons", "icon-512.png")
    with Image.open(path) as im:
        return im.convert("RGB").resize((int(size), int(size)), Image.LANCZOS)


def font(name, size, weight=400):
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    try:
        f.set_variation_by_axes([weight, 100])
    except Exception:
        pass
    return f


def fit_font(draw, text, name, size, weight, max_width):
    """Shrink a line until it fits the space the card gives it."""
    while size > 6:
        f = font(name, int(size), weight)
        if draw.textlength(text, font=f) <= max_width:
            return f
        size -= 0.5
    return font(name, 6, weight)


def mark_letters(text, target_width):
    """Outlines for a word, from the same font and the same code the mark uses."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "logo", os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.py"))
    logo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(logo)
    return logo.letter_paths(text, target_width)


def site():
    with open(os.path.join(ROOT, "content", "site.json"), encoding="utf-8") as fh:
        return json.load(fh)


def content(lang):
    with open(os.path.join(ROOT, "content", "%s.json" % lang), encoding="utf-8") as fh:
        return json.load(fh)


def pretty_url(url):
    return url.replace("https://", "").replace("http://", "").rstrip("/")


# ---------------------------------------------------------------- wordmark --

def wordmark(path, fg="#08090b", accent=VIOLET_DEEP, name="MAX DARKOSADZE", tag="MR. MAX"):
    """The name beside the mark, drawn as outlines so it looks the same on a
    slide, in a programme and on a poster, with or without the font installed."""
    letters, width, height = mark_letters("MD", 44)
    title, t_width, t_height = mark_letters(name, 430)
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 140" width="640" height="140" role="img" aria-label="%s">
  <rect x="2" y="22" width="96" height="96" rx="20" fill="none" stroke="%s" stroke-width="2.4"/>
  <g transform="translate(%.1f %.1f)"><path d="%s" fill="%s"/></g>
  <rect x="%.1f" y="92" width="26" height="3" fill="%s"/>
  <g transform="translate(124 %.1f)"><path d="%s" fill="%s"/></g>
  <rect x="124" y="104" width="46" height="3" fill="%s"/>
  <text x="184" y="112" font-family="Helvetica, Arial, sans-serif" font-size="17"
        letter-spacing="4" fill="%s">%s</text>
</svg>
""" % (name, accent,
       50 - width / 2, 58 - height / 2, letters, fg,
       50 - 13, accent,
       74 - t_height / 2, title, fg,
       accent, accent, tag)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(svg)
    return path


# --------------------------------------------------------------- QR code ----

def qr(path, url, dark=INK):
    code = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_Q,
                         box_size=16, border=2)
    code.add_data(url)
    code.make(fit=True)
    img = code.make_image(fill_color=dark, back_color="white").convert("RGB")
    img.save(path)
    return img


# ---------------------------------------------------------- business card ---

MM = 300 / 25.4          # 300 dpi
CARD = (int(85 * MM), int(55 * MM))
BLEED = int(3 * MM)


def card_front(url):
    w, h = CARD
    img = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, int(14 * MM), h), fill=INK)
    size = int(7.4 * MM)
    img.paste(mark_image(size), (int(3.3 * MM), int(4.2 * MM)))

    x = int(20 * MM)
    d.text((x, int(16 * MM)), "MAX DARKOSADZE",
           font=display("MAX DARKOSADZE", 4.4 * MM), fill=INK, anchor="ls")
    d.text((x, int(21 * MM)), "მაქსი დარკოსაძე",
           font=font("NotoSerifGeorgian.ttf", int(3.4 * MM), 500), fill=INK_SOFT, anchor="ls")
    d.line((x, int(24 * MM), x + int(12 * MM), int(24 * MM)), fill=VIOLET_DEEP, width=3)
    d.text((x, int(30 * MM)), "მწერალი · რეჟისორი · ფილოსოფოსი",
           font=font("NotoSansGeorgian.ttf", int(2.5 * MM), 400), fill=INK_SOFT, anchor="ls")
    d.text((x, int(34 * MM)), "ლექტორი · ქირურგი · ავიაინსტრუქტორი",
           font=font("NotoSansGeorgian.ttf", int(2.5 * MM), 400), fill=INK_SOFT, anchor="ls")
    url_font = fit_font(d, pretty_url(url), "NotoSansGeorgian.ttf", 2.8 * MM, 600,
                        w - x - int(6 * MM))
    d.text((x, int(44 * MM)), pretty_url(url), font=url_font, fill=VIOLET_DEEP, anchor="ls")
    d.text((x, int(48.5 * MM)), "@maxdarkosadze",
           font=font("NotoSansGeorgian.ttf", int(2.6 * MM), 400), fill=INK_SOFT, anchor="ls")
    return img


def card_back(url):
    w, h = CARD
    img = Image.new("RGB", (w, h), INK)
    d = ImageDraw.Draw(img)
    d.text((w // 2, int(19 * MM)), "დისციპლინა",
           font=font("NotoSerifGeorgian.ttf", int(5.0 * MM), 700), fill=PAPER, anchor="mm")
    d.text((w // 2, int(26 * MM)), "ქმნის თავისუფლებას",
           font=font("NotoSerifGeorgian.ttf", int(5.0 * MM), 700), fill=PAPER, anchor="mm")
    d.line((w // 2 - int(6 * MM), int(31 * MM), w // 2 + int(6 * MM), int(31 * MM)),
           fill=VIOLET, width=4)
    d.text((w // 2, int(36 * MM)), "DISCIPLINE CREATES FREEDOM",
           font=font("NotoSansGeorgian.ttf", int(2.4 * MM), 500), fill=VIOLET, anchor="mm")

    code = qr(os.path.join(OUT, "qr.png"), url)
    size = int(15 * MM)
    code = code.resize((size, size), Image.NEAREST)
    img.paste(code, (w - size - int(6 * MM), h - size - int(6 * MM)))
    back_font = fit_font(d, pretty_url(url), "NotoSansGeorgian.ttf", 2.5 * MM, 500,
                         w - size - int(13 * MM))
    d.text((int(6 * MM), h - int(7 * MM)), pretty_url(url),
           font=back_font, fill=MUTED, anchor="ls")
    return img


# ------------------------------------------------- instagram highlight covers

COVERS = [
    ("books", "წიგნები"),
    ("film", "კინო"),
    ("philosophy", "ფილოსოფია"),
    ("lectures", "ლექციები"),
    ("surgery", "ქირურგია"),
    ("aviation", "ავიაცია"),
    ("foundation", "ფონდი"),
]


def covers():
    """The round buttons at the top of an Instagram profile. Instagram crops a
    circle out of the middle, so nothing important goes near a corner: the mark,
    the word, and the rule the site puts under everything it means."""
    made = []
    for slug, label in COVERS:
        size = 1080
        img = Image.new("RGB", (size, size), INK)
        d = ImageDraw.Draw(img)
        d.ellipse((size * 0.055, size * 0.055, size * 0.945, size * 0.945),
                  outline=VIOLET, width=4)

        mark = int(size * 0.17)
        img.paste(mark_image(mark), (int((size - mark) / 2), int(size * 0.30)))
        d = ImageDraw.Draw(img)

        face = font("NotoSerifGeorgian.ttf", 86, 600)
        while d.textlength(label, font=face) > size * 0.62 and face.size > 40:
            face = font("NotoSerifGeorgian.ttf", face.size - 4, 600)
        d.text((size / 2, size * 0.60), label, font=face, fill=PAPER, anchor="mm")
        d.rectangle((size / 2 - 52, size * 0.685, size / 2 + 52, size * 0.695), fill=VIOLET)

        path = os.path.join(OUT, "instagram-%s.jpg" % slug)
        img.save(path, "JPEG", quality=90, optimize=True)
        made.append(path)
    return made


# --------------------------------------------------------- e-mail signature --

def signature(url):
    html = """<!-- Paste into Gmail: Settings → General → Signature.
     Or into Outlook: File → Options → Mail → Signatures. -->
<table cellpadding="0" cellspacing="0" style="font-family:Georgia,'Times New Roman',serif;color:#15171c">
  <tr>
    <td style="padding-right:18px;border-right:2px solid #7c5cff">
      <div style="width:64px;height:64px;background:#08090b;border:1px solid #7c5cff;border-radius:14px;
                  text-align:center;line-height:64px;font-size:24px;font-weight:700;color:#f2f2f0">MD</div>
    </td>
    <td style="padding-left:18px">
      <div style="font-size:18px;font-weight:700;color:#08090b">Max Darkosadze &middot; მაქსი დარკოსაძე</div>
      <div style="font-size:13px;color:#5b3fd4;padding-top:2px">Mr. Max &middot; ბატონი მაქსი</div>
      <div style="font-size:12px;color:#6b6f78;padding-top:6px;font-family:Helvetica,Arial,sans-serif">
        Writer &middot; Director &middot; Philosopher &middot; Lecturer &middot; Surgeon &middot; Aviation instructor
      </div>
      <div style="font-size:12px;padding-top:8px;font-family:Helvetica,Arial,sans-serif">
        <a href="%s" style="color:#5b3fd4;text-decoration:none">%s</a>
        &nbsp;&middot;&nbsp;
        <a href="https://www.instagram.com/maxdarkosadze/" style="color:#6b6f78;text-decoration:none">Instagram</a>
        &nbsp;&middot;&nbsp;
        <a href="https://www.imdb.com/name/nm8752510/" style="color:#6b6f78;text-decoration:none">IMDb</a>
      </div>
    </td>
  </tr>
</table>
""" % (url, pretty_url(url))
    path = os.path.join(OUT, "email-signature.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return path


# --------------------------------------------------------------- quote cards --

def wrap(draw, text, face, max_width):
    """Break a line of Georgian or English so that it fits the card."""
    words, lines, line = text.split(), [], ""
    for word in words:
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=face) <= max_width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def quotes_from(data, limit=8):
    """The quotations the site already carries: the one on the home page, then
    one from each article that has one."""
    found = [(data["pages"]["home"]["quote"], data["pages"]["home"]["quoteCite"])]
    for article in data["articles"]:
        for para in article["blocks"]:
            if para.get("type") == "quote":
                found.append((para["text"], article["title"]))
                break
    cleaned = []
    for text, cite in found:
        text = text.replace("[[", "").replace("]]", "").strip()
        if text and text not in [t for t, _ in cleaned]:
            cleaned.append((text, cite.replace("[[", "").replace("]]", "").strip()))
    return cleaned[:limit]


def quote_card(text, cite, name, url, size, tall=False):
    """One card for Instagram: the words, the name, the address. Nothing else."""
    width, height = size
    img = Image.new("RGB", (width, height), INK)
    d = ImageDraw.Draw(img)

    margin = int(width * 0.11)
    d.rectangle((0, 0, width, int(height * 0.012)), fill=VIOLET)
    img.paste(mark_image(width * 0.085), (margin, margin))

    body = int(width * (0.088 if tall else 0.072))   # stories carry bigger type
    for attempt in range(14):                      # shrink until the words fit
        face = font("NotoSerifGeorgian.ttf", body, 500)
        lines = wrap(d, "„%s“" % text, face, width - margin * 2)
        step = int(body * 1.42)
        block_height = len(lines) * step
        room = height * (0.52 if tall else 0.46)
        if block_height <= room:
            break
        body = int(body * 0.9)

    top = (height - block_height) / 2 + (height * 0.02 if tall else 0)
    for i, line in enumerate(lines):
        d.text((margin, top + i * step), line, font=face, fill=PAPER)

    rule = top + block_height + int(height * 0.045)
    d.line([(margin, rule), (margin + int(width * 0.09), rule)], fill=VIOLET, width=4)
    d.text((margin, rule + int(height * 0.022)), cite,
           font=font("NotoSansGeorgian.ttf", int(width * 0.032), 500), fill=VIOLET)
    d.text((margin, height - margin - int(width * 0.03)), name,
           font=display(name, width * 0.036), fill=PAPER)
    d.text((margin, height - margin + int(width * 0.015)), url,
           font=font("NotoSansGeorgian.ttf", int(width * 0.026), 400), fill=MUTED)
    return img


def quote_cards(url):
    """A square for the feed and a tall one for stories, per quotation, in both
    languages."""
    made = []
    folder = os.path.join(OUT, "quotes")
    os.makedirs(folder, exist_ok=True)
    for lang in ("ka", "en"):
        data = content(lang)
        name = data["meta"]["siteName"]
        for i, (text, cite) in enumerate(quotes_from(data), start=1):
            for shape, size, tall in (("post", (1080, 1080), False),
                                      ("story", (1080, 1920), True)):
                card = quote_card(text, cite, name, pretty_url(url), size, tall)
                path = os.path.join(folder, "%s-%02d-%s.jpg" % (lang, i, shape))
                card.save(path, "JPEG", quality=90, optimize=True)
                made.append(path)
    return made


def main():
    os.makedirs(OUT, exist_ok=True)
    url = site()["baseUrl"].rstrip("/") or "https://example.com"

    wordmark(os.path.join(OUT, "wordmark.svg"))
    wordmark(os.path.join(OUT, "wordmark-light.svg"), fg="#ffffff")

    front, back = card_front(url), card_back(url)
    front.save(os.path.join(OUT, "business-card-front.png"), "PNG")
    back.save(os.path.join(OUT, "business-card-back.png"), "PNG")

    signature(url)
    covers()
    cards = quote_cards(url)

    print("brand kit written to assets/brand/ for %s" % pretty_url(url))
    print("  wordmark.svg, wordmark-light.svg")
    print("  business-card-front.png, business-card-back.png (85×55mm at 300dpi)")
    print("  qr.png, email-signature.html, instagram-*.jpg")
    print("  quotes/ — %d quotation cards (1080×1080 for the feed, 1080×1920 for stories)"
          % len(cards))
    print("  the app icons and the favicon are drawn by tools/logo.py, not here")
    print("After buying the domain: update baseUrl in content/site.json and run this again.")


if __name__ == "__main__":
    main()
