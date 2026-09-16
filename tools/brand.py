#!/usr/bin/env python3
"""Draw the brand kit: wordmark, business card, QR code, e-mail signature and
Instagram highlight covers — all from the site's own colours and fonts.

    python3 tools/brand.py

Everything lands in assets/brand/. Run it again after buying a domain: the QR
code and the card take their address from baseUrl in content/site.json.
"""

import json
import os

import qrcode
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "tools", "fonts")
OUT = os.path.join(ROOT, "assets", "brand")

INK = "#0d1b2a"
INK_SOFT = "#16283c"
GOLD = "#c9a227"
GOLD_DEEP = "#b8860b"
PAPER = "#fbf9f5"


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


def site():
    with open(os.path.join(ROOT, "content", "site.json"), encoding="utf-8") as fh:
        return json.load(fh)


def content(lang):
    with open(os.path.join(ROOT, "content", "%s.json" % lang), encoding="utf-8") as fh:
        return json.load(fh)


def pretty_url(url):
    return url.replace("https://", "").replace("http://", "").rstrip("/")


# ---------------------------------------------------------------- wordmark --

def wordmark(path, fg="#0d1b2a", gold=GOLD, name="MAX DARKOSADZE", tag="BATONI MAKSI"):
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 140" width="640" height="140" role="img" aria-label="%s">
  <rect x="2" y="24" width="92" height="92" rx="20" fill="none" stroke="%s" stroke-width="3"/>
  <text x="48" y="80" font-family="Georgia, 'Times New Roman', serif" font-size="40" font-weight="700"
        fill="%s" text-anchor="middle" dominant-baseline="middle">MD</text>
  <text x="124" y="66" font-family="Georgia, 'Times New Roman', serif" font-size="42" font-weight="700"
        letter-spacing="2.5" fill="%s">%s</text>
  <line x1="126" y1="84" x2="176" y2="84" stroke="%s" stroke-width="3"/>
  <text x="190" y="93" font-family="Helvetica, Arial, sans-serif" font-size="19"
        letter-spacing="4" fill="%s">%s</text>
</svg>
""" % (name, gold, gold, fg, name, gold, gold, tag)
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
    d.rounded_rectangle((int(3.4 * MM), int(4.2 * MM), int(10.6 * MM), int(11.4 * MM)),
                        radius=int(1.8 * MM), outline=GOLD, width=4)
    d.text((int(7 * MM), int(8 * MM)), "MD", font=font("NotoSerifGeorgian.ttf", int(3.4 * MM), 700),
           fill=GOLD, anchor="mm")

    x = int(20 * MM)
    d.text((x, int(16 * MM)), "MAX DARKOSADZE",
           font=font("NotoSerifGeorgian.ttf", int(4.4 * MM), 700), fill=INK, anchor="ls")
    d.text((x, int(21 * MM)), "მაქსი დარკოსაძე",
           font=font("NotoSerifGeorgian.ttf", int(3.4 * MM), 500), fill=INK_SOFT, anchor="ls")
    d.line((x, int(24 * MM), x + int(12 * MM), int(24 * MM)), fill=GOLD_DEEP, width=3)
    d.text((x, int(30 * MM)), "ქირურგი · ავიაინსტრუქტორი · ლექტორი",
           font=font("NotoSansGeorgian.ttf", int(2.5 * MM), 400), fill=INK_SOFT, anchor="ls")
    d.text((x, int(34 * MM)), "მწერალი · ფილოსოფოსი · კინორეჟისორი",
           font=font("NotoSansGeorgian.ttf", int(2.5 * MM), 400), fill=INK_SOFT, anchor="ls")
    url_font = fit_font(d, pretty_url(url), "NotoSansGeorgian.ttf", 2.8 * MM, 600,
                        w - x - int(6 * MM))
    d.text((x, int(44 * MM)), pretty_url(url), font=url_font, fill=GOLD_DEEP, anchor="ls")
    d.text((x, int(48.5 * MM)), "@maxdarkosadze",
           font=font("NotoSansGeorgian.ttf", int(2.6 * MM), 400), fill=INK_SOFT, anchor="ls")
    return img


def card_back(url):
    w, h = CARD
    img = Image.new("RGB", (w, h), INK)
    d = ImageDraw.Draw(img)
    d.text((w // 2, int(19 * MM)), "დისციპლინა",
           font=font("NotoSerifGeorgian.ttf", int(5.0 * MM), 700), fill="#ffffff", anchor="mm")
    d.text((w // 2, int(26 * MM)), "ქმნის თავისუფლებას",
           font=font("NotoSerifGeorgian.ttf", int(5.0 * MM), 700), fill="#ffffff", anchor="mm")
    d.line((w // 2 - int(6 * MM), int(31 * MM), w // 2 + int(6 * MM), int(31 * MM)),
           fill=GOLD, width=4)
    d.text((w // 2, int(36 * MM)), "DISCIPLINE CREATES FREEDOM",
           font=font("NotoSansGeorgian.ttf", int(2.4 * MM), 500), fill=GOLD, anchor="mm")

    code = qr(os.path.join(OUT, "qr.png"), url)
    size = int(17 * MM)
    code = code.resize((size, size), Image.NEAREST)
    img.paste(code, (w - size - int(5 * MM), h - size - int(5 * MM)))
    back_font = fit_font(d, pretty_url(url), "NotoSansGeorgian.ttf", 2.5 * MM, 500,
                         w - size - int(13 * MM))
    d.text((int(6 * MM), h - int(7 * MM)), pretty_url(url),
           font=back_font, fill="#9aa8b6", anchor="ls")
    return img


# ------------------------------------------------- instagram highlight covers

COVERS = [
    ("surgery", "ქირურგია", "✚"),
    ("aviation", "ავიაცია", "✈"),
    ("lectures", "ლექციები", "✎"),
    ("books", "წიგნები", "❦"),
    ("film", "კინო", "▣"),
    ("foundation", "ფონდი", "✦"),
]


def covers():
    made = []
    for slug, label, glyph in COVERS:
        size = 1080
        img = Image.new("RGB", (size, size), INK)
        d = ImageDraw.Draw(img)
        d.ellipse((size * 0.08, size * 0.08, size * 0.92, size * 0.92),
                  outline=GOLD, width=6)
        d.text((size / 2, size * 0.44), glyph,
               font=font("NotoSansGeorgian.ttf", 210, 400), fill=GOLD, anchor="mm")
        d.text((size / 2, size * 0.64), label,
               font=font("NotoSerifGeorgian.ttf", 82, 600), fill="#ffffff", anchor="mm")
        path = os.path.join(OUT, "instagram-%s.jpg" % slug)
        img.save(path, "JPEG", quality=90, optimize=True)
        made.append(path)
    return made


# --------------------------------------------------------- e-mail signature --

def signature(url):
    html = """<!-- Paste into Gmail: Settings → General → Signature.
     Or into Outlook: File → Options → Mail → Signatures. -->
<table cellpadding="0" cellspacing="0" style="font-family:Georgia,'Times New Roman',serif;color:#1b232e">
  <tr>
    <td style="padding-right:18px;border-right:2px solid #c9a227">
      <div style="width:64px;height:64px;border:2px solid #c9a227;border-radius:14px;
                  text-align:center;line-height:64px;font-size:24px;font-weight:700;color:#b8860b">MD</div>
    </td>
    <td style="padding-left:18px">
      <div style="font-size:18px;font-weight:700;color:#0d1b2a">Max Darkosadze &middot; მაქსი დარკოსაძე</div>
      <div style="font-size:13px;color:#b8860b;padding-top:2px">Batoni Maksi &middot; ბატონი მაქსი</div>
      <div style="font-size:12px;color:#5d6874;padding-top:6px;font-family:Helvetica,Arial,sans-serif">
        Surgeon &middot; Aviation instructor &middot; Lecturer &middot; Writer &middot; Philosopher &middot; Filmmaker
      </div>
      <div style="font-size:12px;padding-top:8px;font-family:Helvetica,Arial,sans-serif">
        <a href="%s" style="color:#b8860b;text-decoration:none">%s</a>
        &nbsp;&middot;&nbsp;
        <a href="https://www.instagram.com/maxdarkosadze/" style="color:#5d6874;text-decoration:none">Instagram</a>
        &nbsp;&middot;&nbsp;
        <a href="https://www.imdb.com/name/nm8752510/" style="color:#5d6874;text-decoration:none">IMDb</a>
      </div>
    </td>
  </tr>
</table>
""" % (url, pretty_url(url))
    path = os.path.join(OUT, "email-signature.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return path


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

    print("brand kit written to assets/brand/ for %s" % pretty_url(url))
    print("  wordmark.svg, wordmark-light.svg")
    print("  business-card-front.png, business-card-back.png (85×55mm at 300dpi)")
    print("  qr.png, email-signature.html, instagram-*.jpg")
    print("After buying the domain: update baseUrl in content/site.json and run this again.")


if __name__ == "__main__":
    main()
