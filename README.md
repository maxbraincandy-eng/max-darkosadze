# Max Darkosadze — maxdarkosadze / მაქსი დარკოსაძე

A bilingual (English + Georgian) website about **Max Darkosadze / მაქსი დარკოსაძე**,
known to many simply as **Batoni Maksi / ბატონი მაქსი** — surgeon, aviation
instructor, lecturer, writer, modern philosopher and public figure.

ორენოვანი (ქართული და ინგლისური) საიტი **მაქს დარკოსაძეზე**, რომელიც ბევრისთვის
უბრალოდ **„ბატონი მაქსია“** — ქირურგი, ავიაინსტრუქტორი, ლექტორი, მწერალი,
თანამედროვე ფილოსოფოსი და საზოგადო მოღვაწე.

---

## ⚠️ Before publishing / გამოქვეყნებამდე

The articles are written, but every **fact** — dates, names of hospitals and
universities, numbers, awards, contact details — is a marked placeholder that
looks like <code>[[this]]</code> and is highlighted in yellow on the page.
Nothing factual was invented. Replace each one with verified information before
the site goes public.

სტატიები დაწერილია, მაგრამ ყველა **ფაქტობრივი დეტალი** — თარიღები, კლინიკებისა და
უნივერსიტეტების სახელები, ციფრები, ჯილდოები, საკონტაქტო ინფორმაცია — დროებით
ადგილშემნახველად არის მონიშნული <code>[[ასე]]</code> და გვერდზე ყვითლად არის გამოყოფილი.
არც ერთი ფაქტი გამოგონილი არ არის. გამოქვეყნებამდე თითოეული ჩაანაცვლეთ
დადასტურებული ინფორმაციით.

Find them all / ყველას პოვნა:

```bash
grep -rn '\[\[' content/
```

When a page no longer has placeholders, the yellow highlight and the draft note
disappear on their own — that already happened for most pages.

### What is verified, and what is still open

Verified from public sources and written in as fact — born in Tbilisi on
26 August 1995, working between Tbilisi and New York, credited as director,
writer and actor, *Cowards* (2016), *Star Wars Zero*
([IMDb](https://www.imdb.com/name/nm8752510/)).

დადასტურებული საჯარო წყაროებიდან და ტექსტში ფაქტად ჩაწერილი — დაბადებული
თბილისში, 1995 წლის 26 აგვისტოს; მუშაობს თბილისსა და ნიუ-იორკს შორის;
კრედიტირებულია როგორც რეჟისორი, სცენარისტი და მსახიობი.

Still open, and only you can supply them / ჯერ შესავსები, და მხოლოდ თქვენ იცით:

| What | Where |
|---|---|
| Award names, years and awarding bodies | `about → honours`, article `honours` |
| Book titles and years | article `writer` |
| Years for: medical qualification, pilot's licence, instructor rating, first book, foundation | `about → timeline` |
| Three e-mail addresses (press, lectures, foundation) | `contact → cards` |

Send them over and they go straight in. Nothing else is marked.

---

## Language / ენა

**Georgian is the default.** Opening the site sends a visitor to `/ka/`; the
header switch moves to English, and that choice is remembered for next time.

**ქართული ნაგულისხმევი ენაა.** საიტზე შესვლისას ვიზიტორი ხვდება `/ka/`-ზე;
ჰედერის გადამრთველი გადადის ინგლისურზე და ეს არჩევანი მახსოვრდება.

## Links / ბმულები

The site links to the real profiles, in the footer of every page and on the
contact page: [Instagram](https://www.instagram.com/maxdarkosadze/) and
[IMDb](https://www.imdb.com/name/nm8752510/). To add more, edit `social` in
`content/en.json` and `content/ka.json`.

## What is in the site / რა არის საიტზე

| Page | English | ქართული |
|---|---|---|
| Home / მთავარი | `en/index.html` | `ka/index.html` |
| Biography, timeline, honours / ბიოგრაფია, ქრონოლოგია, ჯილდოები | `en/about.html` | `ka/about.html` |
| Articles index / სტატიების სია | `en/articles.html` | `ka/articles.html` |
| Foundation / ფონდი | `en/foundation.html` | `ka/foundation.html` |
| Gallery / გალერეა | `en/gallery.html` | `ka/gallery.html` |
| News / სიახლეები | `en/news.html` | `ka/news.html` |
| Contact / კონტაქტი | `en/contact.html` | `ka/contact.html` |
| Press kit / პრეს-პაკეტი | `en/press.html` | `ka/press.html` |

Ten long-form articles, each published in both languages / ათი ვრცელი სტატია, ორივე ენაზე:

1. **The Surgeon's Hands / ქირურგის ხელები** — `articles/surgeon.html`
2. **Wings and Discipline / ფრთები და დისციპლინა** — `articles/aviation-instructor.html`
3. **The Lecture Hall / აუდიტორია** — `articles/lecturer.html`
4. **The Written Word / დაწერილი სიტყვა** — `articles/writer.html`
5. **The Philosophy of Batoni Maksi / ბატონი მაქსის ფილოსოფია** — `articles/philosopher.html`
6. **Faces in Stone / სახეები ქვაში** — `articles/sculptor.html`
7. **A Life in Public Service / ცხოვრება საზოგადოების სამსახურში** — `articles/public-figure.html`
8. **Two Ordinary Afternoons / ორი ჩვეულებრივი შუადღე** — `articles/two-afternoons.html`
9. **Honours and Recognition / ჯილდოები და აღიარება** — `articles/honours.html`
10. **The Filmmaker / კინორეჟისორი** — `articles/filmmaker.html` (written from the public IMDb record)

The language switch in the header always moves to the *same* page in the other
language. `index.html` at the root sends a visitor to Georgian or English
according to their browser, and offers both if they prefer to choose.

---

## Adding your photographs / ფოტოების დამატება

Copy the files into `assets/img/` using the exact names listed in
[`assets/img/README.md`](assets/img/README.md). Until a file exists, the page shows
a monogram block instead — hover over it to see the file name it is waiting for.
No rebuild needed.

Every topic now carries its own photograph — home page and biography, surgery,
aviation, writing, philosophy, film, public service and honours — plus thirteen
pictures in the gallery. Still open: `lecture.jpg` and `foundation.jpg`.

ჩააგდეთ ფაილები `assets/img/`-ში ზუსტად იმ სახელებით, რომლებიც აღწერილია
[`assets/img/README.md`](assets/img/README.md)-ში. სანამ ფაილი არ არსებობს, გვერდზე
მონოგრამის ბლოკი ჩანს — კურსორის მიტანისას გამოჩნდება, რომელ ფაილს ელოდება.
თავიდან აგება საჭირო არ არის.

---

## Editing the text / ტექსტის რედაქტირება

All text lives in two files — there is no text inside the HTML:

* `content/en.json` — English
* `content/ka.json` — ქართული
* `content/site.json` — the site address used for canonical links and the sitemap

After editing, rebuild / რედაქტირების შემდეგ თავიდან ააგეთ:

```bash
python3 build.py
```

That regenerates every page in `en/` and `ka/`. Python 3 is the only requirement —
no npm, no framework, no internet connection.

### Adding a new article / ახალი სტატიის დამატება

Add one object to the `articles` list in **both** `content/en.json` and
`content/ka.json`, using the **same `slug`** in each, then run `python3 build.py`.
The article page, the article index, the cards on the home page, the
previous/next links and the sitemap all update themselves.

Block types available in `blocks`: `lead`, `p`, `h2`, `h3`, `quote` (with `cite`),
`list` (with `items`), `note`, `image` (with `src`, `alt`, `caption`).

An article with a tall photograph can set `"imagePortrait"` to a second file:
the article page then shows that photograph whole and large instead of cropping
it into the wide frame, while `"image"` stays the wide version used on the cards.

Inside any text you can write `[link text](https://example.com)` for a link,
`*italics*`, `**bold**`, and `[[something]]` for anything still to be filled in.

---

## Posting news / სიახლის დამატება

Add an entry to the top of `entries` in the `news` section of both content files
and rebuild:

```json
{ "date": "1 October 2026", "title": "…", "text": "…",
  "link": "https://…", "linkLabel": "Watch the trailer" }
```

`link` and `linkLabel` are optional. With no entries at all the page says so
politely.

## Turning on the contact form / საკონტაქტო ფორმის ჩართვა

The form is written and styled but hidden until it has somewhere to send to, so
no visitor ever meets a form that goes nowhere. Create a free form at
[formspree.io](https://formspree.io), paste its endpoint into `formEndpoint` in
`content/site.json`, run `python3 build.py`, and the form appears on the contact
page in both languages.

## Visitor statistics / სტატისტიკა

Off by default. For free, privacy-friendly counting register a name at
[goatcounter.com](https://www.goatcounter.com) and put it in
`analytics.goatcounter` in `content/site.json` (the name only, not the URL); or
put your domain in `analytics.plausible`. Rebuild and the script is added to
every page. Leave both empty and no tracking code is emitted at all.

## Preparing photographs / ფოტოების მომზადება

After adding or replacing anything in `assets/img/`:

```bash
python3 tools/images.py      # measures every image, writes phone-sized copies
python3 tools/press_kit.py   # rebuilds the press archive
python3 build.py
```

`tools/images.py` needs Pillow (`pip install Pillow`); everything else is the
standard library. It writes `assets/img/manifest.json`, which lets each page
reserve the right space for a picture (no jumping while it loads) and offer a
smaller file to phones.

## Previewing locally / ლოკალური გაშვება

```bash
python3 -m http.server 8000
# then open http://localhost:8000/
```

---

## Publishing / გამოქვეყნება

The site is plain static HTML, so it can be hosted anywhere.

**GitHub Pages:** repository *Settings → Pages → Source: Deploy from a branch*,
choose this branch and the `/` (root) folder. `.nojekyll` is already included.

**Your own domain:** set `baseUrl` in `content/site.json` to the real address
(for example `https://maxdarkosadze.ge`), run `python3 build.py`, and add a
`CNAME` file if you use GitHub Pages.

---

## Structure / სტრუქტურა

```
build.py             the generator — rebuilds every page from content/
content/             all text, in JSON, one file per language
assets/css/style.css a single stylesheet (light and dark themes)
assets/js/main.js    mobile menu and photo-slot hints; no dependencies
assets/img/          your photographs go here
en/  ka/             the generated pages (committed, so hosting is instant)
index.html           language chooser and automatic redirect
sitemap.xml robots.txt 404.html
```

Interface details: the header condenses on scroll and carries a light/dark
switch (it follows the system until a reader chooses, then remembers), sections
fade in as they are reached, article pages show a reading-progress bar, and
gallery photographs open in a lightbox. All of it is optional enhancement — the site works with
JavaScript disabled, and motion is switched off for readers who ask for reduced
motion.

Accessibility and SEO are built in: skip links, keyboard-operable menu, alt text,
`hreflang` pairs between the two languages, Open Graph tags, and schema.org
`Person`/`Article` data.
