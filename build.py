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
PAGE_KEYS = ["home", "about", "articles", "news", "foundation", "gallery", "contact", "press"]


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
    og_image = "%s/%s" % (base, "assets/img/og.jpg") if base else asset("assets/img/og.jpg", depth)

    tags = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % esc(title),
        '<meta name="description" content="%s">' % esc(description),
        '<meta name="author" content="%s">' % esc(data["meta"]["siteName"]),
        '<meta name="theme-color" content="#0d1b2a">',
    ]
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
        '<meta name="twitter:card" content="summary_large_image">',
        '<link rel="icon" href="%s">' % asset("assets/img/favicon.svg", depth),
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
        "family=Noto+Serif+Georgian:wght@400;600;700&"
        'family=Noto+Sans+Georgian:wght@300;400;500;600&display=swap">',
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
    }
    if SITE["baseUrl"]:
        payload["url"] = SITE["baseUrl"]
    return '<script type="application/ld+json">%s</script>' % json.dumps(
        payload, ensure_ascii=False
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
    ) + '<li><a href="%s">%s</a></li>' % (
        link(data["lang"], "press", depth), esc(data["pages"]["press"]["heading"])
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
  <div class="wrap split">
    <div class="split-media img-slot" data-path="assets/img/foundation.jpg">%s</div>
    <div class="split-body">
      <h2>%s</h2>
      <p>%s</p>
      <p><a class="btn btn-primary" href="%s">%s</a></p>
    </div>
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
        img_tag("assets/img/foundation.jpg", p["foundationTitle"], depth),
        esc(p["foundationTitle"]),
        inline(p["foundationText"]),
        link(data["lang"], "foundation", depth),
        esc(p["foundationCta"]),
        img_tag("assets/img/gallery/01.jpg", p["galleryTeaserTitle"], depth),
        esc(p["galleryTeaserTitle"]),
        inline(p["galleryTeaserText"]),
        link(data["lang"], "gallery", depth),
        esc(p["galleryCta"]),
    )
    return document(
        data,
        title=p["title"],
        description=data["meta"]["description"],
        key="home",
        body=body,
        depth=depth,
        active="home",
        extra_head=person_jsonld(data),
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
        extra_head='<script type="application/ld+json">%s</script>' % jsonld,
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
    items = "".join(
        figure(item["src"], p["heading"], item.get("caption"), depth, classes="gal-item")
        for item in p["items"]
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
    <div class="gallery">%s</div>
  </div>
</section>
""" % (
        esc(p["eyebrow"]),
        inline(p["heading"]),
        inline(p["lead"]),
        items,
    )
    return document(
        data,
        title=p["title"],
        description=plain(p["lead"]),
        key="gallery",
        body=body,
        depth=depth,
        active="gallery",
    )


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
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page not found — Max Darkosadze</title>
<link rel="icon" href="/assets/img/favicon.svg">
<link rel="stylesheet" href="/assets/css/style.css">
</head>
<body class="choose-lang">
  <main>
    <div class="choose-inner">
      <span class="brand-mark" aria-hidden="true">MD</span>
      <h1>404</h1>
      <p>This page does not exist.</p>
      <p lang="ka">ასეთი გვერდი არ არსებობს.</p>
      <p class="choose-actions">
        <a class="btn btn-primary" href="/ka/" lang="ka">ქართული</a>
        <a class="btn btn-ghost" href="/en/">English</a>
      </p>
    </div>
  </main>
</body>
</html>
"""


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
        write(page_path(lang, "press"), render_press(data))
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
