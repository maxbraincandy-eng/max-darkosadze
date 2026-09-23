#!/usr/bin/env python3
"""Build the short film — a moving collage made from the photographs already on
the site: a slow drift across each picture, a soft dissolve between them, one
word on screen for each life, a title card at the front and the address at the
end. Silent on purpose, so it can play by itself on a page without ambushing
anyone with sound.

    python3 tools/video.py              # both languages, about half a minute each
    python3 tools/video.py --fast       # quarter size, for checking the cut

Writes assets/video/showreel-ka.mp4 (and .webm), the same for English, and a
poster frame. Add or reorder the photographs in SHOTS below and run it again.

Needs Pillow and an ffmpeg binary. If ffmpeg is not on the PATH, install the
one that comes with imageio-ffmpeg:  pip install imageio-ffmpeg
"""

import json
import os
import shutil
import subprocess
import sys

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    sys.exit("This needs Pillow:  pip install Pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "img")
OUT = os.path.join(ROOT, "assets", "video")
FONTS = os.path.join(ROOT, "tools", "fonts")

WIDTH, HEIGHT, FPS = 1280, 720, 30
HOLD = 2.9                      # seconds a photograph is on screen
DISSOLVE = 0.7                  # seconds of overlap between two photographs
CARD = 3.2                      # seconds for the title and the closing card

INK = (13, 27, 42)              # the site's own dark blue
GOLD = (216, 174, 63)
PAPER = (231, 237, 243)

# photograph, the word on screen (Georgian, English), and which way the eye moves
SHOTS = [
    ("portrait.jpg",    ("", ""),                                    "in"),
    ("surgery.jpg",     ("ქირურგი", "Surgeon"),                      "left"),
    ("aviation.jpg",    ("ავიაინსტრუქტორი", "Aviation instructor"),  "out"),
    ("lecture.jpg",     ("ლექტორი", "Lecturer"),                     "right"),
    ("writing.jpg",     ("მწერალი", "Writer"),                       "in"),
    ("philosophy.jpg",  ("ფილოსოფოსი", "Philosopher"),               "left"),
    ("sculpture.jpg",   ("მოქანდაკე", "Sculptor"),                   "out"),
    ("film.jpg",        ("კინორეჟისორი", "Filmmaker"),               "right"),
    ("public.jpg",      ("საზოგადო მოღვაწე", "Public figure"),        "in"),
    ("honours.jpg",     ("აღიარება", "Recognition"),                 "out"),
    ("gallery/16.jpg",  ("", ""),                                    "left"),
    ("gallery/19.jpg",  ("", ""),                                    "in"),
]

TITLE = {
    "ka": ("მაქსი დარკოსაძე", "ბატონი მაქსი", "ერთი ადამიანი, რამდენიმე ცხოვრება"),
    "en": ("Max Darkosadze", "Mr. Max", "One man, several lives"),
}
CLOSING = {
    "ka": ("მაქსი დარკოსაძე", "ბატონი მაქსი"),
    "en": ("Max Darkosadze", "Mr. Max"),
}


def ffmpeg_binary():
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        sys.exit("No ffmpeg found. Install one:  pip install imageio-ffmpeg")


def font(name, size, weight=400):
    path = os.path.join(FONTS, name)
    face = ImageFont.truetype(path, size)
    try:                                   # the Noto Georgian files are variable
        face.set_variation_by_axes([weight, 100])   # axes are [Weight, Width]
    except Exception:
        pass
    return face


def site_url():
    try:
        with open(os.path.join(ROOT, "content", "site.json"), encoding="utf-8") as fh:
            base = json.load(fh).get("baseUrl", "")
    except OSError:
        base = ""
    return base.replace("https://", "").replace("http://", "").rstrip("/")


def ease(t):
    """Slow at both ends: nothing on screen should start or stop abruptly."""
    return t * t * (3 - 2 * t)


def prepared(path, scale):
    """The photograph, large enough for the widest crop and no larger."""
    image = Image.open(path).convert("RGB")
    target = int(WIDTH * scale * 1.35)
    if image.width < target:
        target = image.width
    ratio = target / image.width
    return image.resize((target, max(1, int(image.height * ratio))), Image.LANCZOS)


def drift(image, move, t, scale):
    """One frame of the slow travel across a photograph."""
    zoom_from, zoom_to = (1.16, 1.02) if move in ("in", "left") else (1.02, 1.16)
    zoom = zoom_from + (zoom_to - zoom_from) * ease(t)
    if image.width / image.height < 0.72:     # only the narrow, phone-shaped ones are
        return standing(image, zoom, scale)   # letterboxed; the rest fill the screen
    view_w = min(image.width, int(image.width / zoom))
    view_h = int(view_w * HEIGHT / WIDTH)
    if view_h > image.height:
        view_h = image.height
        view_w = int(view_h * WIDTH / HEIGHT)

    slack_x, slack_y = image.width - view_w, image.height - view_h
    if move == "left":
        x = slack_x * (1 - ease(t))
    elif move == "right":
        x = slack_x * ease(t)
    else:
        x = slack_x / 2
    y = slack_y * 0.42                      # faces sit above the middle
    box = (int(x), int(y), int(x) + view_w, int(y) + view_h)
    return image.crop(box).resize((int(WIDTH * scale), int(HEIGHT * scale)), Image.LANCZOS)


def standing(image, zoom, scale):
    """A photograph taller than the screen is kept whole and set over a blurred,
    darkened copy of itself — the same thing the pages do, so nothing is cut."""
    out_w, out_h = int(WIDTH * scale), int(HEIGHT * scale)

    fill = max(out_w / image.width, out_h / image.height) * 1.08
    back = image.resize((max(1, int(image.width * fill)), max(1, int(image.height * fill))),
                        Image.LANCZOS)
    left = (back.width - out_w) // 2
    top = int((back.height - out_h) * 0.35)
    back = back.crop((left, top, left + out_w, top + out_h))
    back = back.filter(ImageFilter.GaussianBlur(radius=max(6, int(26 * scale))))
    back = Image.blend(back, Image.new("RGB", back.size, INK), 0.55)

    tall_h = int(out_h * (1.0 + (zoom - 1.0) * 0.35))     # a much gentler move
    tall_w = max(1, int(image.width * tall_h / image.height))
    front = image.resize((tall_w, tall_h), Image.LANCZOS)
    cut = (front.height - out_h) // 2
    front = front.crop((0, cut, front.width, cut + out_h))
    back.paste(front, ((out_w - front.width) // 2, 0))
    return back


def shade(frame, scale):
    """A gentle darkening at the foot of the picture, so a word can be read."""
    height = int(260 * scale)
    band = Image.new("L", (1, height))
    for row in range(height):
        band.putpixel((0, row), int(150 * (row / height) ** 1.7))
    mask = band.resize(frame.size if False else (frame.width, height))
    dark = Image.new("RGB", (frame.width, height), (0, 0, 0))
    frame.paste(dark, (0, frame.height - height), mask)
    return frame


def caption(frame, text, alpha, scale):
    if not text or alpha <= 0.01:
        return frame
    layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    face = font("NotoSerifGeorgian.ttf", int(46 * scale), 600)
    x, y = int(72 * scale), frame.height - int(118 * scale)
    draw.line([(x, y - int(26 * scale)), (x + int(54 * scale), y - int(26 * scale))],
              fill=GOLD + (int(255 * alpha),), width=max(1, int(3 * scale)))
    draw.text((x, y), text, font=face, fill=PAPER + (int(255 * alpha),))
    return Image.alpha_composite(frame.convert("RGBA"), layer).convert("RGB")


def title_card(lang, t, scale, closing=False):
    """The opening and closing cards: the name, drawn on the site's own blue."""
    frame = Image.new("RGB", (int(WIDTH * scale), int(HEIGHT * scale)), INK)
    layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    alpha = min(1.0, ease(min(t, 0.25) / 0.25)) * min(1.0, ease(min(1 - t, 0.25) / 0.25))
    ink = int(255 * alpha)

    lines = CLOSING[lang] if closing else TITLE[lang][:2]
    name = font("NotoSerifGeorgian.ttf", int(74 * scale), 700)
    small = font("NotoSansGeorgian.ttf", int(30 * scale), 400)
    middle = frame.height // 2

    w = draw.textlength(lines[0], font=name)
    draw.text(((frame.width - w) / 2, middle - int(78 * scale)), lines[0], font=name,
              fill=PAPER + (ink,))
    draw.line([(frame.width / 2 - int(40 * scale), middle + int(16 * scale)),
               (frame.width / 2 + int(40 * scale), middle + int(16 * scale))],
              fill=GOLD + (ink,), width=max(1, int(3 * scale)))
    second = lines[1]
    w = draw.textlength(second, font=small)
    draw.text(((frame.width - w) / 2, middle + int(38 * scale)), second, font=small,
              fill=GOLD + (ink,))

    tail = site_url() if closing else TITLE[lang][2]
    if tail:
        w = draw.textlength(tail, font=small)
        draw.text(((frame.width - w) / 2, middle + int(96 * scale)), tail, font=small,
                  fill=PAPER + (int(ink * 0.72),))
    return Image.alpha_composite(frame.convert("RGBA"), layer).convert("RGB")


def build(lang, scale, ffmpeg):
    shots = []
    for name, words, move in SHOTS:
        path = os.path.join(IMG, name)
        if not os.path.exists(path):
            print("  (skipping %s — not in assets/img)" % name)
            continue
        shots.append((prepared(path, scale), words[0] if lang == "ka" else words[1], move))
    if not shots:
        sys.exit("No photographs found in assets/img.")

    step = HOLD - DISSOLVE
    starts = [CARD - DISSOLVE + i * step for i in range(len(shots))]
    total = starts[-1] + HOLD + CARD - DISSOLVE
    frames = int(total * FPS)
    size = (int(WIDTH * scale), int(HEIGHT * scale))

    target = os.path.join(OUT, "showreel-%s.mp4" % lang)
    webm = os.path.join(OUT, "showreel-%s.webm" % lang)
    os.makedirs(OUT, exist_ok=True)
    # one pass over the frames, two files out: H.264 for everything that plays
    # video at all, VP9 for the browsers built without the patented codecs
    pipe = subprocess.Popen([
        ffmpeg, "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", "%dx%d" % size, "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "24",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", target,
        "-an", "-c:v", "libvpx-vp9", "-crf", "34", "-b:v", "0",
        "-row-mt", "1", "-deadline", "good", "-cpu-used", "3",
        "-pix_fmt", "yuv420p", webm,
    ], stdin=subprocess.PIPE)

    poster_at = int((CARD + HOLD * 0.5) * FPS)
    for number in range(frames):
        now = number / FPS
        layers = []                                   # (image, weight)

        if now < CARD:
            layers.append((title_card(lang, min(1.0, now / CARD), scale), 1.0))
        if now > total - CARD:
            t = (now - (total - CARD)) / CARD
            layers.append((title_card(lang, min(1.0, t), scale, closing=True), min(1.0, t / 0.4)))

        for (image, word, move), start in zip(shots, starts):
            if start <= now < start + HOLD:
                t = (now - start) / HOLD
                frame = shade(drift(image, move, t, scale), scale)
                fade_in = min(1.0, (now - start) / DISSOLVE)
                fade_out = min(1.0, (start + HOLD - now) / DISSOLVE)
                text_alpha = min(1.0, (t - 0.12) / 0.18) * min(1.0, (0.92 - t) / 0.18)
                frame = caption(frame, word, max(0.0, min(1.0, text_alpha)), scale)
                layers.append((frame, min(fade_in, fade_out)))

        picture = Image.new("RGB", size, INK)
        for image, weight in layers:
            picture = Image.blend(picture, image, max(0.0, min(1.0, weight)))

        if number == poster_at:
            picture.resize((WIDTH, HEIGHT), Image.LANCZOS).save(
                os.path.join(OUT, "showreel-poster.jpg"), quality=84, optimize=True)
        pipe.stdin.write(picture.tobytes())
        if number % (FPS * 5) == 0:
            print("    %4.1fs / %.1fs" % (now, total))

    pipe.stdin.close()
    if pipe.wait() != 0:
        sys.exit("ffmpeg refused the frames")
    for made in (target, webm):
        print("  %s  (%.1f s, %.1f MB)" % (os.path.relpath(made, ROOT), total,
                                           os.path.getsize(made) / 1e6))


def main():
    fast = "--fast" in sys.argv
    scale = 0.5 if fast else 1.0
    ffmpeg = ffmpeg_binary()
    for lang in ("ka", "en"):
        print("%s:" % lang)
        build(lang, scale, ffmpeg)
    print("\nThe pages pick these up by name — nothing else to change.")


if __name__ == "__main__":
    main()
