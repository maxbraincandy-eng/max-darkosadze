#!/usr/bin/env python3
"""Static site generator for maxdarkosadze.com.

Content lives in content/en.json and content/ka.json (and content/site.json).
Running `python3 build.py` regenerates every HTML page in en/ and ka/.

Nothing here needs a package manager, a framework or an internet connection.
"""

import html
import json
import os
import re
import shutil
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(ROOT, "content")
LANGS = ["en", "ka"]
PAGE_KEYS = ["home", "about", "articles", "news", "foundation", "gallery", "legend", "guestbook", "booking", "faq", "search", "contact", "press"]


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def load(name):
    with open(os.path.join(CONTENT_DIR, name), encoding="utf-8") as fh:
        return json.load(fh)


IMAGES = {}


def load_manifest():
    """Pixel sizes written by tools/images.py; absent is fine."""
    path = os.path.join(ROOT, "assets", "img", "manifest.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def img_tag(src, alt, depth, *, eager=False, extra=""):
    """An <img> that reserves its own space and offers a phone-sized file."""
    attrs = [
        'src="%s"' % asset(src, depth),
        'alt="%s"' % esc(alt or ""),
    ]
    size = IMAGES.get(src)
    if size:
        attrs.append('width="%d" height="%d"' % (size[0], size[1]))
    small = src.rsplit(".", 1)[0] + "-800.jpg"
    if small in IMAGES and size and size[0] > IMAGES[small][0]:
        attrs.append('srcset="%s %dw, %s %dw"' % (
            asset(small, depth), IMAGES[small][0], asset(src, depth), size[0]))
        attrs.append('sizes="(max-width: 700px) 100vw, %dpx"' % min(size[0], 1140))
    attrs.append('loading="%s"' % ("eager" if eager else "lazy"))
    attrs.append('decoding="async"')
    attrs.append("data-slot")
    if extra:
        attrs.append(extra)
    return "<img %s>" % " ".join(attrs)


def esc(text):
    return html.escape(str(text), quote=True)


PLACEHOLDER_RE = re.compile(r"\[\[([^\[\]]*)\]\]")


LINK_RE = re.compile(r"\[([^\[\]]+)\]\((https?://[^)\s]+)\)")


def inline(text):
    """Escape, then render [text](url) links, **bold**, *italic* and [[placeholders]]."""
    out = esc(text)
    out = LINK_RE.sub(
        r'<a href="\2" target="_blank" rel="noopener me">\1</a>', out
    )
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", out)
    while True:
        new = PLACEHOLDER_RE.sub(r'<span class="ph">\1</span>', out)
        if new == out:
            return new
        out = new


def plain(text):
    """Strip the [[ ]] placeholder markers — for meta tags and structured data."""
    out = str(text)
    while True:
        new = PLACEHOLDER_RE.sub(r"\1", out)
        if new == out:
            return new
        out = new


def prefix(depth):
    return "../" * depth


def asset(path, depth):
    return prefix(depth) + path


def page_path(lang, key, slug=None):
    if key == "article":
        return "%s/articles/%s.html" % (lang, slug)
    if key == "home":
        return "%s/index.html" % lang
    return "%s/%s.html" % (lang, key)


def link(lang, key, depth, slug=None):
    return prefix(depth) + page_path(lang, key, slug)


def word_count(article):
    words = 0
    for block in article["blocks"]:
        if "text" in block:
            words += len(str(block["text"]).split())
        for item in block.get("items", []):
            words += len(str(item).split())
    return words


def reading_time(article):
    return max(1, round(word_count(article) / 180))


# --------------------------------------------------------------------------
# components
# --------------------------------------------------------------------------

def figure(src, alt, caption, depth, classes="fig"):
    size = IMAGES.get(src)
    if size and size[1] > size[0] and "fig-portrait" not in classes:
        classes += " fig-tall"      # taller than it is wide: do not let it run away
    caption_html = (
        '<figcaption>%s</figcaption>' % inline(caption) if caption else ""
    )
    return (
        '<figure class="%s">'
        '<div class="img-slot" data-path="%s">%s</div>%s</figure>'
    ) % (classes, esc(src), img_tag(src, alt, depth), caption_html)


def editor_note(data, *parts):
    """Show the draft note only while the page still contains placeholders."""
    if not any("[[" in json.dumps(p, ensure_ascii=False) for p in parts):
        return ""
    return '<p class="editor-note">%s</p>' % esc(data["ui"]["editorNote"])


def blocks_html(blocks, depth):
    out = []
    for block in blocks:
        kind = block.get("type", "p")
        if kind == "p":
            out.append("<p>%s</p>" % inline(block["text"]))
        elif kind == "lead":
            out.append('<p class="lead">%s</p>' % inline(block["text"]))
        elif kind == "h2":
            out.append("<h2>%s</h2>" % inline(block["text"]))
        elif kind == "h3":
            out.append("<h3>%s</h3>" % inline(block["text"]))
        elif kind == "quote":
            cite = (
                "<cite>%s</cite>" % inline(block["cite"]) if block.get("cite") else ""
            )
            out.append(
                '<blockquote><p>%s</p>%s</blockquote>'
                % (inline(block["text"]), cite)
            )
        elif kind == "list":
            items = "".join("<li>%s</li>" % inline(i) for i in block["items"])
            out.append('<ul class="rich-list">%s</ul>' % items)
        elif kind == "note":
            out.append('<p class="note">%s</p>' % inline(block["text"]))
        elif kind == "image":
            out.append(
                figure(block["src"], block.get("alt", ""), block.get("caption"), depth)
            )
    return "\n".join(out)


def article_card(data, article, depth):
    ui = data["ui"]
    href = link(data["lang"], "article", depth, article["slug"])
    return """
      <a class="card" href="%s">
        <div class="card-media img-slot" data-path="%s">%s</div>
        <div class="card-body">
          <span class="tag">%s</span>
          <h3>%s</h3>
          <p>%s</p>
          <span class="card-more">%s <span aria-hidden="true">&rarr;</span></span>
        </div>
      </a>""" % (
        href,
        esc(article["image"]),
        img_tag(article["image"], article.get("imageAlt", article["title"]), depth),
        esc(article["category"]),
        inline(article["title"]),
        inline(article["summary"]),
        esc(ui["readMore"]),
    )


def head(data, title, description, depth, key, slug=None):
    site = SITE
    base = site["baseUrl"].rstrip("/")
    lang = data["lang"]
    other = data["other"]
    canonical = "%s/%s" % (base, page_path(lang, key, slug)) if base else ""
    alt_self = "%s/%s" % (base, page_path(lang, key, slug)) if base else ""
    alt_other = "%s/%s" % (base, page_path(other, key, slug)) if base else ""
    # each page has its own share card when tools/og_images.py has drawn one
    card = "assets/og/%s-article-%s.jpg" % (lang, slug) if key == "article" \
        else "assets/og/%s-%s.jpg" % (lang, key)
    if not os.path.exists(os.path.join(ROOT, card)):
        card = "assets/img/og.jpg"
    og_image = "%s/%s" % (base, card) if base else asset(card, depth)

    tags = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % esc(title),
        '<meta name="description" content="%s">' % esc(description),
        '<meta name="author" content="%s">' % esc(data["meta"]["siteName"]),
        '<meta name="theme-color" content="#0d1b2a">',
    ]
    if SITE.get("googleVerification", "").strip():
        tags.append('<meta name="google-site-verification" content="%s">'
                    % esc(SITE["googleVerification"].strip()))
    if canonical:
        tags += [
            '<link rel="canonical" href="%s">' % esc(canonical),
            '<link rel="alternate" hreflang="%s" href="%s">' % (lang, esc(alt_self)),
            '<link rel="alternate" hreflang="%s" href="%s">' % (other, esc(alt_other)),
            '<link rel="alternate" hreflang="x-default" href="%s/ka/">' % esc(base),
        ]
    tags += [
        '<meta property="og:type" content="%s">' % ("article" if key == "article" else "website"),
        '<meta property="og:site_name" content="%s">' % esc(data["meta"]["siteName"]),
        '<meta property="og:title" content="%s">' % esc(title),
        '<meta property="og:description" content="%s">' % esc(description),
        '<meta property="og:locale" content="%s">' % ("ka_GE" if lang == "ka" else "en_GB"),
        '<meta property="og:image" content="%s">' % esc(og_image),
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta property="og:image:alt" content="%s">' % esc(title),
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:image" content="%s">' % esc(og_image),
        '<link rel="icon" href="%s">' % asset("assets/img/favicon.svg", depth),
        '<link rel="me" href="%s">' % esc(data["meta"]["links"]["instagram"]),
        '<link rel="me" href="%s">' % esc(data["meta"]["links"]["imdb"]),
        '<link rel="preload" as="font" type="font/woff2" crossorigin href="%s">'
        % asset("assets/fonts/noto-serif-georgian.woff2", depth),
        '<link rel="preload" as="font" type="font/woff2" crossorigin href="%s">'
        % asset("assets/fonts/noto-sans-georgian.woff2", depth),
        '<link rel="stylesheet" href="%s">' % asset("assets/css/style.css", depth),
        THEME_BOOT,
    ]
    if SITE.get("analytics", {}).get("goatcounter"):
        tags.append(
            '<script data-goatcounter="https://%s.goatcounter.com/count" '
            'async src="//gc.zgo.at/count.js"></script>'
            % esc(SITE["analytics"]["goatcounter"])
        )
    if SITE.get("analytics", {}).get("plausible"):
        tags.append(
            '<script defer data-domain="%s" src="https://plausible.io/js/script.js"></script>'
            % esc(SITE["analytics"]["plausible"])
        )
    return "\n  ".join(tags)


THEME_BOOT = (
    "<script>"
    "try{var t=localStorage.getItem('md-theme');"
    "if(t){document.documentElement.setAttribute('data-theme',t);}}catch(e){}"
    "</script>"
)


def film_section(data, depth, alt=False):
    """The short film, if it has been rendered. The page never shows a player
    with nothing behind it: no file, no section."""
    f = data.get("film")
    lang = data["lang"]
    name = "assets/video/showreel-%s.mp4" % lang
    if not f or not os.path.exists(os.path.join(ROOT, name)):
        return ""
    up = "../" * depth
    poster = "assets/video/showreel-poster.jpg"
    poster_tag = (' poster="%s%s"' % (up, poster)) if os.path.exists(os.path.join(ROOT, poster)) else ""
    webm = name.replace(".mp4", ".webm")
    webm_source = ('\n        <source src="%s%s" type="video/webm">' % (up, webm)
                   if os.path.exists(os.path.join(ROOT, webm)) else "")
    return """
<section class="section film%s" id="film">
  <div class="wrap">
    <header class="section-head">
      <p class="eyebrow">%s</p>
      <h2>%s</h2>
      <p>%s</p>
    </header>
    <figure class="film-frame">
      <video class="film-video" controls playsinline preload="none"
             width="1280" height="720"%s>
        <source src="%s%s" type="video/mp4">%s
      </video>
      <figcaption>%s</figcaption>
    </figure>
  </div>
</section>
""" % (" section-alt" if alt else "", esc(f["eyebrow"]), inline(f["title"]), inline(f["lead"]),
       poster_tag, up, name, webm_source, inline(f["caption"]))


def film_jsonld(data):
    """Tells Google there is a film here, and what it shows."""
    f = data.get("film")
    name = "assets/video/showreel-%s.mp4" % data["lang"]
    base = SITE["baseUrl"].rstrip("/")
    full = os.path.join(ROOT, name)
    if not f or not base or not os.path.exists(full):
        return ""
    payload = {
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": plain(f["title"]),
        "description": plain(f["lead"]),
        "thumbnailUrl": "%s/assets/video/showreel-poster.jpg" % base,
        "contentUrl": "%s/%s" % (base, name),
        "uploadDate": date.fromtimestamp(os.path.getmtime(full)).isoformat(),
        "inLanguage": data["lang"],
    }
    return '<script type="application/ld+json">%s</script>' % json.dumps(payload, ensure_ascii=False)


def person_jsonld(data):
    meta = data["meta"]
    payload = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": meta["siteName"],
        "alternateName": [
            "Max Darkosadze" if data["lang"] == "ka" else "მაქსი დარკოსაძე",
            meta["nickname"],
        ],
        "description": meta["description"],
        "jobTitle": meta["tagline"].replace(" · ", ", "),
        "nationality": "Georgian",
        "sameAs": [meta["links"]["instagram"], meta["links"]["imdb"]],
        "knowsLanguage": ["ka", "en"],
    }
    if SITE["baseUrl"]:
        payload["url"] = SITE["baseUrl"]
        payload["image"] = SITE["baseUrl"].rstrip("/") + "/assets/img/portrait.jpg"
    website = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": meta["siteName"],
        "alternateName": [meta["nickname"], "Max Darkosadze", "მაქსი დარკოსაძე"],
        "inLanguage": data["lang"],
    }
    if SITE["baseUrl"]:
        website["url"] = SITE["baseUrl"]
    return "".join(
        '<script type="application/ld+json">%s</script>' % json.dumps(p, ensure_ascii=False)
        for p in (payload, website)
    )


def header(data, depth, active, key="home", slug=None):
    nav_items = []
    for item in data["nav"]:
        cls = ' class="is-active"' if item["key"] == active else ""
        nav_items.append(
            '<li><a%s href="%s">%s</a></li>'
            % (cls, link(data["lang"], item["key"], depth), esc(item["label"]))
        )
    return """
<a class="skip-link" href="#main">%s</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="%s">
      <span class="brand-mark" aria-hidden="true">MD</span>
      <span class="brand-text">
        <strong>%s</strong>
        <small>%s</small>
      </span>
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="%s">
      <span></span><span></span><span></span>
    </button>
    <nav id="site-nav" class="site-nav" aria-label="%s">
      <ul>%s</ul>
      <div class="nav-tools">
        <a class="lang-switch" href="%s" hreflang="%s" lang="%s" title="%s">%s</a>
        <button class="theme-toggle" type="button" aria-label="%s" title="%s">
          <svg class="icon-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5Z"/></svg>
          <svg class="icon-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.2M12 19.3v2.2M4.2 4.2l1.6 1.6M18.2 18.2l1.6 1.6M2.5 12h2.2M19.3 12h2.2M4.2 19.8l1.6-1.6M18.2 5.8l1.6-1.6"/></svg>
        </button>
      </div>
    </nav>
  </div>
</header>""" % (
        esc(data["ui"]["skip"]),
        link(data["lang"], "home", depth),
        esc(data["meta"]["siteName"]),
        esc(data["meta"]["nickname"]),
        esc(data["ui"]["menu"]),
        esc(data["ui"]["menu"]),
        "".join(nav_items),
        link(data["other"], key, depth, slug),
        data["other"],
        data["other"],
        esc(data["otherAria"]),
        esc(data["otherLabel"]),
        esc(data["ui"]["theme"]),
        esc(data["ui"]["theme"]),
    )


def footer(data, depth):
    nav_links = "".join(
        '<li><a href="%s">%s</a></li>'
        % (link(data["lang"], item["key"], depth), esc(item["label"]))
        for item in data["nav"]
    ) + "".join(
        '<li><a href="%s">%s</a></li>' % (link(data["lang"], key, depth), esc(label))
        for key, label in (("legend", data["pages"]["legend"]["masthead"]),
                           ("booking", data["pages"]["booking"]["heading"]),
                           ("faq", data["pages"]["faq"]["heading"]),
                           ("search", data["pages"]["search"]["heading"]),
                           ("press", data["pages"]["press"]["heading"]))
    )
    return """
<footer class="site-footer">
  <div class="wrap footer-inner">
    <div class="footer-brand">
      <span class="brand-mark" aria-hidden="true">MD</span>
      <p><strong>%s</strong><br><em class="footer-nick">%s</em><br><span>%s</span></p>
      <p class="muted">%s</p>
    </div>
    <nav class="footer-nav" aria-label="%s">
      <ul>%s</ul>
    </nav>
    <div class="footer-lang">
      <p class="muted">%s</p>
      <ul class="footer-social">%s</ul>
      <ul>
        <li><a href="%s" hreflang="en" lang="en">English</a></li>
        <li><a href="%s" hreflang="ka" lang="ka">ქართული</a></li>
      </ul>
    </div>
  </div>
  <div class="wrap footer-bottom">
    <p>&copy; %s %s. %s</p>
    <a class="to-top" href="#top">%s &uarr;</a>
  </div>
</footer>""" % (
        esc(data["meta"]["siteName"]),
        esc(data["meta"]["nickname"]),
        esc(data["meta"]["tagline"]),
        esc(data["ui"]["footerNote"]),
        esc(data["ui"]["menu"]),
        nav_links,
        esc(data["ui"]["langLabel"]),
        "".join(
            '<li><a href="%s" rel="me noopener" target="_blank">%s</a></li>' % (esc(url), esc(label))
            for label, url in (("Instagram", data["meta"]["links"]["instagram"]),
                               ("IMDb", data["meta"]["links"]["imdb"]))
        ),
        link("en", "home", depth),
        link("ka", "home", depth),
        date.today().year,
        esc(data["meta"]["siteName"]),
        esc(data["ui"]["rights"]),
        esc(data["ui"]["toTop"]),
    )


def document(data, *, title, description, key, body, depth, active, slug=None, extra_head=""):
    return """<!DOCTYPE html>
<html lang="%s" id="top">
<head>
  %s
  %s
</head>
<body class="lang-%s page-%s">
%s
<main id="main">
%s
</main>
%s
<script src="%s" defer></script>
</body>
</html>
""" % (
        data["htmlLang"],
        head(data, title, description, depth, key, slug),
        extra_head,
        data["lang"],
        active,
        header(data, depth, active, key, slug),
        body,
        footer(data, depth),
        asset("assets/js/main.js", depth),
    )


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------

def quote_wall(data, depth, limit=6):
    """Every quotation on the site, gathered from the articles themselves."""
    found = []
    for article in data["articles"]:
        for block in article["blocks"]:
            if block.get("type") == "quote":
                found.append((block["text"], article))
                break
    cards = []
    for text, article in found[:limit]:
        cards.append(
            '<a class="quote-card" href="%s"><p>%s</p><span>%s</span></a>'
            % (link(data["lang"], "article", depth, article["slug"]),
               inline(text), esc(article["title"]))
        )
    return "".join(cards)


def render_home(data):
    depth = 1
    p = data["pages"]["home"]
    ui = data["ui"]
    pillars = "".join(
        """
        <a class="pillar" href="%s">
          <span class="pillar-index" aria-hidden="true">%02d</span>
          <h3>%s</h3>
          <p>%s</p>
        </a>"""
        % (link(data["lang"], "article", depth, item["slug"]), i + 1, esc(item["label"]), inline(item["text"]))
        for i, item in enumerate(p["pillars"])
    )
    cards = "".join(article_card(data, a, depth) for a in data["articles"])
    body = """
<section class="hero">
  <div class="hero-media img-slot" data-path="assets/img/hero.jpg">%s</div>
  <div class="wrap hero-inner">
    <figure class="hero-portrait img-slot" data-path="assets/img/portrait.jpg">%s</figure>
    <div class="hero-text">
    <p class="eyebrow">%s</p>
    <h1>%s</h1>
    <p class="nickname"><span>%s</span> <strong>%s</strong></p>
    <p class="hero-subtitle">%s</p>
    <p class="hero-lead">%s</p>
    <p class="hero-actions">
      <a class="btn btn-primary" href="%s">%s</a>
      <a class="btn btn-ghost" href="%s">%s</a>
    </p>
    <p class="hero-roles">%s</p>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <header class="section-head">
      <h2>%s</h2>
      <p>%s</p>
    </header>
    <div class="pillars">%s</div>
  </div>
</section>

<section class="motto">
  <div class="wrap motto-inner">
    <p>%s</p>
    <p class="motto-alt">%s</p>
    <hr class="motto-rule">
  </div>
</section>

<section class="section section-alt">
  <div class="wrap">
    <header class="section-head">
      <h2>%s</h2>
      <p>%s</p>
    </header>
    <div class="cards">%s</div>
  </div>
</section>

<section class="section quote-section">
  <div class="wrap">
    <blockquote class="big-quote">
      <p>%s</p>
      <cite>%s</cite>
    </blockquote>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <header class="section-head"><h2>%s</h2></header>
    <div class="quote-wall">%s</div>
  </div>
</section>

<section class="section">
  <div class="wrap split">
    <div class="split-media img-slot" data-path="assets/img/foundation.jpg">%s</div>
    <div class="split-body">
      <h2>%s</h2>
      <p>%s</p>
      <p><a class="btn btn-primary" href="%s">%s</a></p>
    </div>
  </div>
</section>

<section class="legend-band">
  <div class="wrap">
    <p class="legend-band-eyebrow">%s</p>
    <p class="legend-band-title">%s</p>
    <p class="legend-band-text">%s</p>
    <p><a class="btn btn-ghost" href="%s">%s</a></p>
  </div>
</section>

<section class="section section-alt">
  <div class="wrap split split-reverse">
    <div class="split-media img-slot" data-path="assets/img/gallery/01.jpg">%s</div>
    <div class="split-body">
      <h2>%s</h2>
      <p>%s</p>
      <p><a class="btn btn-ghost" href="%s">%s</a></p>
    </div>
  </div>
</section>
""" % (
        img_tag("assets/img/hero.jpg", "", depth, eager=True),
        img_tag("assets/img/portrait.jpg", data["meta"]["siteName"], depth, eager=True),
        esc(p["heroEyebrow"]),
        esc(p["heroTitle"]),
        esc(data["meta"]["nicknameLabel"]),
        esc(data["meta"]["nickname"]),
        inline(p["heroSubtitle"]),
        inline(p["heroLead"]),
        link(data["lang"], "articles", depth),
        esc(p["ctaPrimary"]),
        link(data["lang"], "about", depth),
        esc(p["ctaSecondary"]),
        esc(data["meta"]["tagline"]),
        esc(p["pillarsTitle"]),
        inline(p["pillarsLead"]),
        pillars,
        inline(p["motto"]["main"]),
        esc(p["motto"]["alt"]),
        esc(ui["featured"]),
        inline(p["featuredLead"]),
        cards,
        inline(p["quote"]),
        esc(p["quoteCite"]),
        esc(data["ui"]["quotesTitle"]),
        quote_wall(data, depth),
        img_tag("assets/img/foundation.jpg", p["foundationTitle"], depth),
        esc(p["foundationTitle"]),
        inline(p["foundationText"]),
        link(data["lang"], "foundation", depth),
        esc(p["foundationCta"]),
        esc(data["pages"]["legend"]["eyebrow"]),
        esc(data["pages"]["legend"]["heading"]),
        inline(data["pages"]["legend"]["quote"]),
        link(data["lang"], "legend", depth),
        esc(data["ui"]["legendCta"]),
        img_tag("assets/img/gallery/01.jpg", p["galleryTeaserTitle"], depth),
        esc(p["galleryTeaserTitle"]),
        inline(p["galleryTeaserText"]),
        link(data["lang"], "gallery", depth),
        esc(p["galleryCta"]),
    )
    body = body.replace('<section class="motto">',
                        film_section(data, depth) + '<section class="motto">', 1)
    return document(
        data,
        title=p["title"],
        description=data["meta"]["description"],
        key="home",
        body=body,
        depth=depth,
        active="home",
        extra_head=person_jsonld(data) + film_jsonld(data),
    )


def render_about(data):
    depth = 1
    p = data["pages"]["about"]
    timeline = "".join(
        '<li><span class="t-year">%s</span><span class="t-text">%s</span></li>'
        % (inline(row["year"]), inline(row["text"]))
        for row in p["timeline"]
    )
    honours = "".join(
        """
        <li class="honour">
          <span class="honour-year">%s</span>
          <div>
            <h3>%s</h3>
            <p>%s</p>
          </div>
        </li>"""
        % (inline(h["year"]), inline(h["title"]), inline(h["text"]))
        for h in p["honours"]
    )
    body = """
<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h1>%s</h1>
    <p class="page-lead">%s</p>
  </div>
</section>

<section class="section">
  <div class="wrap prose">
    %s
    %s
  </div>
</section>

<section class="section section-alt">
  <div class="wrap">
    <header class="section-head">
      <h2>%s</h2>
      <p>%s</p>
    </header>
    <ol class="timeline">%s</ol>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <header class="section-head">
      <h2>%s</h2>
      <p>%s</p>
    </header>
    <ul class="honours">%s</ul>
  </div>
</section>
""" % (
        esc(p["eyebrow"]),
        inline(p["heading"]),
        inline(p["lead"]),
        editor_note(data, p["blocks"]),
        blocks_html(p["blocks"], depth),
        esc(p["timelineTitle"]),
        inline(p["timelineNote"]),
        timeline,
        esc(p["honoursTitle"]),
        inline(p["honoursLead"]),
        honours,
    )
    return document(
        data,
        title=p["title"],
        description=data["meta"]["description"],
        key="about",
        body=body,
        depth=depth,
        active="about",
        extra_head=person_jsonld(data),
    )


def render_articles_index(data):
    depth = 1
    p = data["pages"]["articles"]
    cards = "".join(article_card(data, a, depth) for a in data["articles"])
    body = """
<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h1>%s</h1>
    <p class="page-lead">%s</p>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="cards">%s</div>
  </div>
</section>
""" % (
        esc(p["eyebrow"]),
        inline(p["heading"]),
        inline(p["lead"]),
        cards,
    )
    return document(
        data,
        title=p["title"],
        description=plain(p["lead"]),
        key="articles",
        body=body,
        depth=depth,
        active="articles",
    )


def render_article(data, index):
    depth = 2
    ui = data["ui"]
    article = data["articles"][index]
    articles = data["articles"]
    prev_a = articles[index - 1] if index > 0 else None
    next_a = articles[index + 1] if index < len(articles) - 1 else None

    pager = []
    if prev_a:
        pager.append(
            '<a class="pager-item pager-prev" href="%s"><span>%s</span><strong>%s</strong></a>'
            % (
                link(data["lang"], "article", depth, prev_a["slug"]),
                esc(ui["prevArticle"]),
                inline(prev_a["title"]),
            )
        )
    if next_a:
        pager.append(
            '<a class="pager-item pager-next" href="%s"><span>%s</span><strong>%s</strong></a>'
            % (
                link(data["lang"], "article", depth, next_a["slug"]),
                esc(ui["nextArticle"]),
                inline(next_a["title"]),
            )
        )

    others = [a for a in articles if a["slug"] != article["slug"]][:3]
    related = "".join(article_card(data, a, depth) for a in others)

    body = """
<article class="article">
  <header class="article-head">
    <div class="wrap">
      <p class="eyebrow"><a href="%s">%s</a> <span aria-hidden="true">/</span> %s</p>
      <h1>%s</h1>
      <p class="article-subtitle">%s</p>
      <p class="article-meta">%s<span>%s %s</span></p>
    </div>
  </header>

  <div class="wrap">
    %s
  </div>

  <div class="wrap prose">
    %s
    %s
  </div>

  <div class="wrap article-foot">
    <a class="btn btn-ghost" href="%s">&larr; %s</a>
  </div>

  <nav class="wrap pager" aria-label="%s">%s</nav>
</article>

<section class="section section-alt">
  <div class="wrap">
    <header class="section-head"><h2>%s</h2></header>
    <div class="cards">%s</div>
  </div>
</section>
""" % (
        link(data["lang"], "articles", depth),
        esc(data["pages"]["articles"]["heading"]),
        esc(article["category"]),
        inline(article["title"]),
        inline(article["subtitle"]),
        ("<span>%s</span>" % inline(article["date"])) if article.get("date") else "",
        reading_time(article),
        esc(ui["readingTime"]),
        figure(
            article.get("imagePortrait") or article["image"],
            article.get("imageAlt", article["title"]),
            article.get("imageCaption"),
            depth,
            classes="fig fig-portrait" if article.get("imagePortrait") else "fig fig-hero",
        ),
        editor_note(data, article["blocks"], article.get("subtitle"), article.get("summary")),
        blocks_html(article["blocks"], depth),
        link(data["lang"], "articles", depth),
        esc(ui["backToArticles"]),
        esc(ui["allArticles"]),
        "".join(pager),
        esc(ui["relatedReading"]),
        related,
    )

    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": []}
    if SITE["baseUrl"]:
        base = SITE["baseUrl"].rstrip("/")
        for i, (name, path) in enumerate((
                (data["meta"]["siteName"], page_path(data["lang"], "home")),
                (data["pages"]["articles"]["heading"], page_path(data["lang"], "articles")),
                (plain(article["title"]), page_path(data["lang"], "article", article["slug"])))):
            crumbs["itemListElement"].append(
                {"@type": "ListItem", "position": i + 1, "name": name,
                 "item": "%s/%s" % (base, path)})

    jsonld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": plain(article["title"]),
            "description": plain(article["summary"]),
            "inLanguage": data["lang"],
            "about": data["meta"]["siteName"],
            "author": {"@type": "Person", "name": data["meta"]["siteName"]},
        },
        ensure_ascii=False,
    )

    return document(
        data,
        title="%s — %s" % (article["title"], data["meta"]["siteName"]),
        description=plain(article["summary"]),
        key="article",
        slug=article["slug"],
        body=body,
        depth=depth,
        active="articles",
        extra_head='<script type="application/ld+json">%s</script>' % jsonld
        + ('<script type="application/ld+json">%s</script>' % json.dumps(crumbs, ensure_ascii=False)
           if crumbs["itemListElement"] else ""),
    )


def render_news(data):
    depth = 1
    p = data["pages"]["news"]
    entries = p.get("entries", [])
    if entries:
        items = "".join(
            """
        <li class="news-item">
          <p class="news-date">%s</p>
          <h2>%s</h2>
          <p>%s</p>%s
        </li>""" % (
                inline(e["date"]),
                inline(e["title"]),
                inline(e["text"]),
                ('<p><a class="news-link" href="%s" target="_blank" rel="noopener">%s <span aria-hidden="true">&rarr;</span></a></p>'
                 % (esc(e["link"]), esc(e.get("linkLabel") or e["link"]))) if e.get("link") else "",
            )
            for e in entries
        )
        body_inner = '<ol class="news">%s</ol>' % items
    else:
        body_inner = '<p class="note">%s</p>' % esc(p["empty"])

    body = """
<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h1>%s</h1>
    <p class="page-lead">%s</p>
  </div>
</section>

<section class="section">
  <div class="wrap prose">%s</div>
</section>
""" % (esc(p["eyebrow"]), inline(p["heading"]), inline(p["lead"]), body_inner)
    return document(data, title=p["title"], description=plain(p["lead"]), key="news",
                    body=body, depth=depth, active="news")


def render_booking(data):
    """Invitations to lecture. Uses the same server as the guest book, and shows
    the form only when something is there to receive it."""
    depth = 1
    p = data["pages"]["booking"]
    f = p["form"]
    api = SITE.get("guestbookApi", "").strip()
    post_to = ("/api/booking" if api else SITE.get("bookingForm", "").strip())

    if post_to:
        form = """
    <form class="guest-form booking-form" data-booking="%s" novalidate>
      <label>%s<input type="text" name="name" maxlength="80" required autocomplete="name"></label>
      <label>%s<input type="text" name="contact" maxlength="120" required></label>
      <label>%s<input type="text" name="org" maxlength="120" autocomplete="organization"></label>
      <label>%s<input type="text" name="wanted" maxlength="60" placeholder="2026-11-14"></label>
      <label>%s<input type="text" name="audience" maxlength="120"></label>
      <label>%s<input type="text" name="topic" maxlength="160"></label>
      <label class="form-wide">%s<textarea name="message" rows="5" maxlength="900"></textarea></label>
      <p class="form-hp" aria-hidden="true"><label>Leave this field empty<input type="text" name="website" tabindex="-1" autocomplete="off"></label></p>
      <p class="form-actions">
        <button class="btn btn-primary" type="submit">%s</button>
        <span class="muted" data-form-note>%s</span>
      </p>
      <p class="form-status" role="status" aria-live="polite" hidden></p>
    </form>""" % (esc(post_to), esc(f["name"]), esc(f["contact"]), esc(f["org"]), esc(f["wanted"]),
                  esc(f["audience"]), esc(f["topic"]), esc(f["message"]), esc(f["send"]),
                  esc(f["note"]))
    else:
        form = ('<p>%s</p><p><a class="btn btn-primary" href="%s" target="_blank" rel="noopener">%s</a></p>'
                % (inline(p["disabledNote"]), esc(data["meta"]["links"]["instagram"]),
                   esc(p["disabledCta"])))

    topics = "".join("<li>%s</li>" % inline(item) for item in p["aside"])
    body = """
<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h1>%s</h1>
    <p class="page-lead">%s</p>
  </div>
</section>

<section class="section">
  <div class="wrap booking-grid"
       data-msg-sending="%s" data-msg-thanks="%s" data-msg-error="%s"
       data-offline-url="%s" data-offline-cta="%s" data-msg-offline="%s">
    <div class="booking-main">
      <h2>%s</h2>
      %s
    </div>
    <aside class="booking-aside">
      <h2>%s</h2>
      <ul class="rich-list">%s</ul>
      <div class="booking-portrait img-slot" data-path="assets/img/lecture.jpg">%s</div>
    </aside>
  </div>
</section>
""" % (
        esc(p["eyebrow"]), inline(p["heading"]), inline(p["lead"]),
        esc(f["sending"]), esc(f["thanks"]), esc(f["error"]),
        esc(data["meta"]["links"]["instagram"]), esc(p["disabledCta"]), esc(p["disabledNote"]),
        esc(p["formTitle"]), form,
        esc(p["asideTitle"]), topics,
        img_tag("assets/img/lecture.jpg", p["heading"], depth),
    )
    return document(data, title=p["title"], description=plain(p["lead"]), key="booking",
                    body=body, depth=depth, active="booking")


def render_guestbook(data):
    """Notes left by visitors. Entries that have been read and kept live in the
    content file; if a guest-book API is configured the page also loads the
    live ones and can post new notes to it."""
    depth = 1
    p = data["pages"]["guestbook"]
    f = p["form"]
    api = SITE.get("guestbookApi", "").strip()
    post_to = api or SITE.get("guestbookForm", "").strip()   # own server, or a form service

    kept = "".join(
        """
        <li class="note-card">
          <p class="note-text">%s</p>
          <p class="note-by"><span class="note-name">%s</span>%s</p>
        </li>""" % (
            inline(e["message"]), esc(e["name"]),
            ('<span class="note-place">%s</span>' % esc(e["place"])) if e.get("place") else "",
        )
        for e in p.get("entries", [])
    )

    form = """
    <form class="guest-form" novalidate>
      <label>%s<input type="text" name="name" maxlength="40" required autocomplete="nickname"></label>
      <label>%s<input type="text" name="place" maxlength="80"></label>
      <label class="form-wide">%s<textarea name="message" rows="5" maxlength="700" required></textarea>
        <span class="form-counter"><span data-counter>700</span> %s</span></label>
      <p class="form-hp" aria-hidden="true"><label>Leave this field empty<input type="text" name="website" tabindex="-1" autocomplete="off"></label></p>
      <p class="form-actions">
        <button class="btn btn-primary" type="submit">%s</button>
        <span class="muted" data-form-note>%s</span>
      </p>
      <p class="form-status" role="status" aria-live="polite" hidden></p>
    </form>""" % (esc(f["name"]), esc(f["place"]), esc(f["message"]), esc(f["counter"]),
                  esc(f["send"]), esc(f["note"])) if post_to else (
        """
    <p>%s</p>
    <p><a class="btn btn-primary" href="%s" target="_blank" rel="noopener">%s</a></p>""" % (
            inline(p["disabledNote"]), esc(data["meta"]["links"]["instagram"]),
            esc(p["disabledCta"])))

    body = """
<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h1>%s</h1>
    <p class="page-lead">%s</p>
  </div>
</section>

<section class="section">
  <div class="wrap guest-grid"
       data-guestbook="%s" data-guestbook-post="%s" data-guestbook-mode="%s"
       data-msg-sending="%s" data-msg-thanks="%s" data-msg-published="%s" data-msg-error="%s" data-msg-long="%s"
       data-msg-empty="%s" data-msg-loading="%s" data-msg-offline="%s" data-msg-instant="%s"
       data-msg-soon="%s" data-msg-many="%s" data-msg-links="%s"
       data-offline-url="%s" data-offline-cta="%s">
    <div class="guest-form-wrap">
      <figure class="guest-portrait img-slot" data-path="assets/img/portrait.jpg">
        %s
        <figcaption>%s</figcaption>
      </figure>
      <h2>%s</h2>
      %s
    </div>
    <div class="guest-entries">
      <h2>%s</h2>
      <ul class="notes" data-notes>%s</ul>
      <p class="note guest-empty"%s>%s</p>
    </div>
  </div>
</section>
""" % (
        esc(p["eyebrow"]), inline(p["heading"]), inline(p["lead"]),
        esc(api),
        esc(post_to),
        "api" if api else ("form" if post_to else "off"),
        esc(f["sending"]), esc(f["thanks"]), esc(f.get("published", f["thanks"])),
        esc(f["error"]), esc(f["tooLong"]),
        esc(p["empty"]), esc(p["loading"]), esc(p["disabledNote"]),
        esc(f.get("noteInstant", "")),
        esc(f.get("tooSoon", "")), esc(f.get("tooMany", "")), esc(f.get("noLinks", "")),
        esc(data["meta"]["links"]["instagram"]), esc(p["disabledCta"]),
        img_tag("assets/img/portrait.jpg", data["meta"]["siteName"], depth),
        inline(p["portraitCaption"]),
        esc(p["formTitle"]), form,
        esc(p["entriesTitle"]), kept,
        "" if not p.get("entries") else " hidden", esc(p["empty"]),
    )
    return document(data, title=p["title"], description=plain(p["lead"]), key="guestbook",
                    body=body, depth=depth, active="guestbook")


def render_legend(data):
    """A magazine-style spread of tall tales — plainly labelled as such."""
    depth = 1
    p = data["pages"]["legend"]

    entries = "".join(
        """
        <article class="tale">
          <p class="tale-tag">%s</p>
          <h2>%s</h2>
          <p>%s</p>
        </article>""" % (esc(e["tag"]), inline(e["title"]), inline(e["text"]))
        for e in p["entries"]
    )
    records = "".join(
        '<li><span class="rec-name">%s</span><span class="rec-value">%s</span></li>'
        % (inline(r["name"]), inline(r["value"]))
        for r in p["records"]
    )

    body = """
<section class="legend-head">
  <div class="wrap">
    <p class="legend-eyebrow">%s</p>
    <p class="legend-masthead">%s</p>
    <h1>%s</h1>
    <p class="legend-strap">%s</p>
  </div>
</section>

<section class="section">
  <div class="wrap legend-grid">
    <div class="legend-main">
      <p class="legend-lead">%s</p>
      <blockquote class="legend-quote"><p>%s</p><cite>%s</cite></blockquote>
      <h2 class="legend-section">%s</h2>
      <div class="tales">%s</div>
      <p class="legend-closing">%s</p>
    </div>
    <aside class="legend-side">
      <h2>%s</h2>
      <p class="muted">%s</p>
      <ul class="records">%s</ul>
      <div class="legend-portrait img-slot" data-path="assets/img/gallery/07.jpg">%s</div>
    </aside>
  </div>
</section>
""" % (
        esc(p["eyebrow"]), esc(p["masthead"]), inline(p["heading"]), inline(p["strapline"]),
        inline(p["lead"]), inline(p["quote"]), esc(p["quoteCite"]),
        esc(p["entriesTitle"]), entries, inline(p["closing"]),
        esc(p["recordsTitle"]), inline(p["recordsNote"]), records,
        img_tag("assets/img/gallery/07.jpg", p["heading"], depth),
    )
    return document(data, title=p["title"], description=plain(p["lead"]), key="legend",
                    body=body, depth=depth, active="legend")


def render_press(data):
    depth = 1
    p = data["pages"]["press"]
    facts = "".join("<li>%s</li>" % inline(f) for f in p["facts"])
    archive = "assets/press/max-darkosadze-photos.zip"
    body = """
<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h1>%s</h1>
    <p class="page-lead">%s</p>
  </div>
</section>

<section class="section">
  <div class="wrap prose">
    <h2>%s</h2>
    <p class="copyable">%s</p>
    <h2>%s</h2>
    <p class="copyable">%s</p>
    <h2>%s</h2>
    <ul class="rich-list">%s</ul>
    <h2>%s</h2>
    <p>%s</p>
    <h2>%s</h2>
    <p>%s</p>
    <p><a class="btn btn-primary" href="%s" download>%s</a></p>
    <h2>%s</h2>
    <p>%s</p>
    <ul class="rich-list">%s</ul>
    <h2>%s</h2>
    <p>%s</p>
  </div>
</section>
""" % (
        esc(p["eyebrow"]), inline(p["heading"]), inline(p["lead"]),
        esc(p["shortTitle"]), inline(p["short"]),
        esc(p["longTitle"]), inline(p["long"]),
        esc(p["factsTitle"]), facts,
        esc(p["namesTitle"]), inline(p["names"]),
        esc(p["downloadsTitle"]), inline(p["downloadsText"]),
        asset(archive, depth), esc(p["downloadLabel"]),
        esc(p["brandTitle"]), inline(p["brandText"]),
        "".join('<li><a href="%s" download>%s</a></li>' % (asset(href, depth), esc(label))
                for label, href in p["brandItems"]),
        esc(p["contactTitle"]), inline(p["contactText"]),
    )
    return document(data, title=p["title"], description=plain(p["short"]), key="press",
                    body=body, depth=depth, active="press")


def render_foundation(data):
    depth = 1
    p = data["pages"]["foundation"]
    programmes = "".join(
        '<li class="programme"><h3>%s</h3><p>%s</p></li>'
        % (inline(item["title"]), inline(item["text"]))
        for item in p["programmes"]
    )
    body = """
<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h1>%s</h1>
    <p class="page-lead">%s</p>
  </div>
</section>

<section class="section">
  <div class="wrap prose">
    %s
    %s
  </div>
</section>

<section class="section section-alt">
  <div class="wrap">
    <header class="section-head"><h2>%s</h2></header>
    <ul class="programmes">%s</ul>
  </div>
</section>

""" % (
        esc(p["eyebrow"]),
        inline(p["heading"]),
        inline(p["lead"]),
        editor_note(data, p["blocks"]),
        blocks_html(p["blocks"], depth),
        esc(p["programmesTitle"]),
        programmes,
    )
    return document(
        data,
        title=p["title"],
        description=plain(p["lead"]),
        key="foundation",
        body=body,
        depth=depth,
        active="foundation",
    )


def render_gallery(data):
    depth = 1
    p = data["pages"]["gallery"]
    lb = p["lightbox"]

    counts = {}
    for item in p["items"]:
        counts[item.get("category", "life")] = counts.get(item.get("category", "life"), 0) + 1

    chips = []
    for i, cat in enumerate(p["categories"]):
        total = len(p["items"]) if cat["key"] == "all" else counts.get(cat["key"], 0)
        if not total:
            continue
        chips.append(
            '<button class="chip%s" type="button" data-filter="%s" aria-pressed="%s">'
            '%s<span class="chip-count">%d</span></button>'
            % (" is-on" if i == 0 else "", esc(cat["key"]), "true" if i == 0 else "false",
               esc(cat["label"]), total)
        )

    tiles = []
    for i, item in enumerate(p["items"]):
        cat = item.get("category", "life")
        label = next((c["label"] for c in p["categories"] if c["key"] == cat), cat)
        caption = item.get("caption") or ""
        tiles.append(
            """
        <figure class="gal-item" data-category="%s" data-index="%d">
          <button class="gal-open" type="button">
            <span class="img-slot" data-path="%s">%s</span>
            <span class="gal-tag">%s</span>
          </button>
          <figcaption>%s</figcaption>
        </figure>""" % (
                esc(cat), i, esc(item["src"]),
                img_tag(item["src"], caption or p["heading"], depth),
                esc(label), inline(caption),
            )
        )

    body = """
<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h1>%s</h1>
    <p class="page-lead">%s</p>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="chips" role="group" aria-label="%s">%s</div>
    <p class="gal-count"><span data-gallery-count>%d</span> %s</p>
    <div class="gallery" data-lightbox
         data-label-close="%s" data-label-prev="%s" data-label-next="%s">%s</div>
    <p class="note gal-empty" hidden>%s</p>
  </div>
</section>
""" % (
        esc(p["eyebrow"]), inline(p["heading"]), inline(p["lead"]),
        esc(p["heading"]), "".join(chips),
        len(p["items"]), esc(p["countLabel"]),
        esc(lb["close"]), esc(lb["prev"]), esc(lb["next"]),
        "".join(tiles),
        esc(p["emptyLabel"]),
    )
    body += film_section(data, depth, alt=True)
    return document(data, title=p["title"], description=plain(p["lead"]), key="gallery",
                    body=body, depth=depth, active="gallery")


def contact_form(data, depth):
    """Rendered only when content/site.json carries a form endpoint, so a
    visitor never meets a form that goes nowhere."""
    endpoint = SITE.get("formEndpoint", "").strip()
    if not endpoint:
        return ""
    p = data["pages"]["contact"]
    f = p["form"]
    return """
<section class="section">
  <div class="wrap form-wrap">
    <h2>%s</h2>
    <form class="contact-form" action="%s" method="POST">
      <label>%s<input type="text" name="name" autocomplete="name" required></label>
      <label>%s<input type="email" name="email" autocomplete="email" required></label>
      <label class="form-wide">%s<input type="text" name="subject"></label>
      <label class="form-wide">%s<textarea name="message" rows="6" required></textarea></label>
      <p class="form-actions"><button class="btn btn-primary" type="submit">%s</button>
      <span class="muted">%s</span></p>
    </form>
  </div>
</section>
""" % (esc(p["formTitle"]), esc(endpoint), esc(f["name"]), esc(f["email"]),
       esc(f["subject"]), esc(f["message"]), esc(f["send"]), esc(f["note"]))


def render_contact(data):
    depth = 1
    p = data["pages"]["contact"]
    cards = "".join(
        '<li class="contact-card"><h3>%s</h3>%s</li>'
        % (inline(c["title"]), "".join("<p>%s</p>" % inline(l) for l in c["lines"]))
        for c in p["cards"]
    )
    social = "".join(
        '<li><a href="%s" rel="me noopener" target="_blank">%s</a></li>'
        % (esc(s["url"]), esc(s["label"]))
        for s in p["social"]
        if not s["url"].startswith("[[")
    )
    body = """
<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h1>%s</h1>
    <p class="page-lead">%s</p>
  </div>
</section>

<section class="section">
  <div class="wrap">
    %s
    <ul class="contact-grid">%s</ul>
  </div>
</section>

%s

<section class="section section-alt">
  <div class="wrap split">
    <div class="split-body">
      <h2>%s</h2>
      <ul class="social">%s</ul>
    </div>
    <div class="split-body">
      <h2>%s</h2>
      <p>%s</p>
    </div>
  </div>
</section>
""" % (
        esc(p["eyebrow"]),
        inline(p["heading"]),
        inline(p["lead"]),
        editor_note(data, p["cards"]),
        cards,
        contact_form(data, depth),
        esc(p["socialTitle"]),
        social,
        esc(p["pressTitle"]),
        inline(p["pressText"]),
    )
    return document(
        data,
        title=p["title"],
        description=plain(p["lead"]),
        key="contact",
        body=body,
        depth=depth,
        active="contact",
    )


# --------------------------------------------------------------------------
# root files
# --------------------------------------------------------------------------

def render_root_index():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>მაქსი დარკოსაძე / Max Darkosadze</title>
<meta name="description" content="Max Darkosadze — surgeon, aviation instructor, lecturer, writer and public figure. Official site in English and Georgian.">
<link rel="icon" href="assets/img/favicon.svg">
<link rel="alternate" hreflang="ka" href="ka/index.html">
<link rel="alternate" hreflang="en" href="en/index.html">
<link rel="alternate" hreflang="x-default" href="ka/index.html">
<link rel="stylesheet" href="assets/css/style.css">
<script>
  /* Georgian is the default language of this site. A reader who chose English
     before is sent back to English; everyone else lands on the Georgian pages. */
  (function () {
    var target = "ka/";
    try {
      if (localStorage.getItem("md-lang") === "en") target = "en/";
    } catch (e) { /* private mode - stay with the default */ }
    location.replace(target);
  })();
</script>
</head>
<body class="choose-lang">
  <main>
    <div class="choose-inner">
      <span class="brand-mark" aria-hidden="true">MD</span>
      <h1><span lang="ka">მაქსი დარკოსაძე</span><br>Max Darkosadze</h1>
      <p>Surgeon · Aviation instructor · Lecturer · Writer · Public figure</p>
      <p lang="ka">ქირურგი · ავიაინსტრუქტორი · ლექტორი · მწერალი · საზოგადო მოღვაწე</p>
      <p class="choose-actions">
        <a class="btn btn-primary" href="ka/" lang="ka">ქართული</a>
        <a class="btn btn-ghost" href="en/">English</a>
      </p>
    </div>
  </main>
</body>
</html>
"""


def render_404():
    return """<!DOCTYPE html>
<html lang="ka">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>404 — მაქსი დარკოსაძე</title>
<meta name="robots" content="noindex">
<link rel="icon" href="/assets/img/favicon.svg">
<link rel="stylesheet" href="/assets/css/style.css">
</head>
<body class="choose-lang">
  <main>
    <div class="choose-inner">
      <span class="brand-mark" aria-hidden="true">MD</span>
      <h1>404</h1>
      <p lang="ka">ეს გვერდი არ არსებობს.<br>
         მისამართი შეამოწმეთ — ჩეკლისტები სწორედ ამისთვისაა.</p>
      <p>This page does not exist.<br>
         Check the address — this is exactly what checklists are for.</p>
      <p class="choose-actions">
        <a class="btn btn-primary" href="/ka/" lang="ka">მთავარი გვერდი</a>
        <a class="btn btn-ghost" href="/en/">Home</a>
      </p>
    </div>
  </main>
</body>
</html>
"""


def render_faq(data):
    """The questions people actually ask, answered plainly — and handed to
    Google in the form it reads."""
    depth = 1
    p = data["pages"]["faq"]

    blocks = []
    for item in p["items"]:
        more = ""
        if item.get("link"):
            key = item["link"]
            label = data["ui"]["faqMore"]
            more = '<p class="faq-more"><a href="%s">%s &rarr;</a></p>' % (
                link(data["lang"], key, depth), esc(label))
        blocks.append("""
      <details class="faq-item">
        <summary><span>%s</span></summary>
        <div class="faq-answer"><p>%s</p>%s</div>
      </details>""" % (inline(item["q"]), inline(item["a"]), more))

    body = """
<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h1>%s</h1>
    <p class="page-lead">%s</p>
  </div>
</section>

<section class="section">
  <div class="wrap faq-wrap">%s
  </div>
</section>
""" % (esc(p["eyebrow"]), inline(p["heading"]), inline(p["lead"]), "".join(blocks))

    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": plain(item["q"]),
             "acceptedAnswer": {"@type": "Answer", "text": plain(item["a"])}}
            for item in p["items"]
        ],
    }
    return document(data, title=p["title"], description=plain(p["lead"]), key="faq",
                    body=body, depth=depth, active="faq",
                    extra_head='<script type="application/ld+json">%s</script>'
                               % json.dumps(schema, ensure_ascii=False))


def search_index(data):
    """What the search box looks through: every page and every article, as
    plain text. Written once at build time, read once in the browser."""
    entries = []

    def add(key, title, lead, text, slug=None):
        words = " ".join(text.split())
        entries.append({
            "t": plain(title),
            "u": page_path(data["lang"], key, slug),
            "s": plain(lead)[:180],
            "x": plain(words).lower()[:2400],
        })

    pages = data["pages"]
    for key in ("home", "about", "articles", "news", "foundation", "gallery",
                "legend", "guestbook", "booking", "faq", "contact", "press"):
        p = pages.get(key)
        if not p:
            continue
        title = p.get("heading") or p.get("heroTitle") or p.get("title", "")
        lead = p.get("lead") or p.get("heroLead") or p.get("description", "")
        bag = [title, lead]
        for value in p.values():
            if isinstance(value, str):
                bag.append(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        bag.append(item)
                    elif isinstance(item, dict):
                        bag.extend(v for v in item.values() if isinstance(v, str))
        add(key, title, lead, " ".join(bag))

    for article in data["articles"]:
        bits = [article["title"], article.get("subtitle", ""), article.get("summary", "")]
        for block in article.get("blocks", []):
            if not isinstance(block, dict):
                continue
            for value in block.values():
                if isinstance(value, str) and value not in ("p", "h2", "lead", "quote", "list"):
                    bits.append(value)
                elif isinstance(value, list):
                    bits.extend(v for v in value if isinstance(v, str))
        add("article", article["title"], article.get("summary", ""),
            " ".join(bits), article["slug"])

    return json.dumps(entries, ensure_ascii=False, separators=(",", ":"))


def render_search(data):
    """A search box with no server behind it: the index is a file, the work
    happens in the visitor's own browser."""
    depth = 1
    p = data["pages"]["search"]
    body = """
<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">%s</p>
    <h1>%s</h1>
    <p class="page-lead">%s</p>
  </div>
</section>

<section class="section">
  <div class="wrap search-wrap" data-search="%s"
       data-msg-empty="%s" data-msg-start="%s"
       data-msg-one="%s" data-msg-many="%s">
    <form class="search-form" role="search" novalidate>
      <label class="sr-only" for="q">%s</label>
      <input id="q" type="search" name="q" autocomplete="off" placeholder="%s" autofocus>
    </form>
    <p class="search-count" role="status" aria-live="polite">%s</p>
    <ul class="search-results" data-results></ul>
    <noscript><p class="note">%s</p></noscript>
  </div>
</section>
""" % (esc(p["eyebrow"]), inline(p["heading"]), inline(p["lead"]),
       esc(asset("assets/search-%s.json" % data["lang"], depth)),
       esc(p["empty"]), esc(p["start"]), esc(p["countOne"]), esc(p["countMany"]),
       esc(p["label"]), esc(p["placeholder"]), esc(p["start"]), esc(p["start"]))
    return document(data, title=p["title"], description=plain(p["lead"]), key="search",
                    body=body, depth=depth, active="search")


def render_sitemap(datasets):
    base = SITE["baseUrl"].rstrip("/")
    urls = []
    for data in datasets.values():
        for key in PAGE_KEYS:
            urls.append(page_path(data["lang"], key))
        for article in data["articles"]:
            urls.append(page_path(data["lang"], "article", article["slug"]))
    today = date.today().isoformat()
    entries = "".join(
        "\n  <url><loc>%s/%s</loc><lastmod>%s</lastmod></url>" % (base, u, today)
        for u in urls
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s\n</urlset>\n'
        % entries
    )


def render_favicon():
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#0d1b2a"/>
  <text x="32" y="42" font-family="Georgia, 'Times New Roman', serif" font-size="28"
        font-weight="700" fill="#c9a227" text-anchor="middle">MD</text>
</svg>
"""


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

SITE = {}


def main():
    global SITE
    SITE = load("site.json")
    global IMAGES
    IMAGES = load_manifest()
    datasets = {lang: load("%s.json" % lang) for lang in LANGS}

    written = []

    def write(rel, content):
        path = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        written.append(rel)

    for lang, data in datasets.items():
        # a stale article page (renamed slug) should not survive a rebuild
        art_dir = os.path.join(ROOT, lang, "articles")
        if os.path.isdir(art_dir):
            shutil.rmtree(art_dir)

        write(page_path(lang, "home"), render_home(data))
        write(page_path(lang, "about"), render_about(data))
        write(page_path(lang, "articles"), render_articles_index(data))
        write(page_path(lang, "news"), render_news(data))
        write(page_path(lang, "legend"), render_legend(data))
        write(page_path(lang, "guestbook"), render_guestbook(data))
        write(page_path(lang, "booking"), render_booking(data))
        write(page_path(lang, "press"), render_press(data))
        write(page_path(lang, "faq"), render_faq(data))
        write(page_path(lang, "search"), render_search(data))
        write("assets/search-%s.json" % lang, search_index(data))
        write(page_path(lang, "foundation"), render_foundation(data))
        write(page_path(lang, "gallery"), render_gallery(data))
        write(page_path(lang, "contact"), render_contact(data))
        for i, article in enumerate(data["articles"]):
            write(page_path(lang, "article", article["slug"]), render_article(data, i))

    write("index.html", render_root_index())
    write("404.html", render_404())
    write("assets/img/favicon.svg", render_favicon())
    if SITE["baseUrl"]:
        write("sitemap.xml", render_sitemap(datasets))
        write("robots.txt", "User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % SITE["baseUrl"].rstrip("/"))
    write(".nojekyll", "")

    print("Built %d files:" % len(written))
    for rel in written:
        print("  " + rel)


if __name__ == "__main__":
    main()
