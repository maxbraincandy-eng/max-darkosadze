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
| The Legend / ლეგენდები | `en/legend.html` | `ka/legend.html` |
| Guest book / სტუმრების წიგნი | `en/guestbook.html` | `ka/guestbook.html` |
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

Every topic carries its own photograph — home page and biography, surgery,
aviation, lectures, writing, philosophy, sculpture, film, public service and
honours — plus sixteen pictures in the gallery. Still open: `foundation.jpg`.

### The gallery / გალერეა

Each gallery picture carries a `category`, and the categories themselves are
listed in the `categories` block of the same page. The filter chips, their
counts and the photograph count are all worked out at build time, so adding a
picture means adding one line:

```json
{ "src": "assets/img/gallery/16.jpg", "category": "aviation", "caption": "…" }
```

The pictures are laid out in columns that keep each photograph's own
proportions, and any of them opens full size with arrows, arrow keys, swipe and
Escape.

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

## The guest book / სტუმრების წიგნი

Visitors choose any name they like, say where they met him if they want to, and
leave a note. **Nothing appears on the site until it has been read and kept** —
the page cannot be used to publish something in his name behind his back, and it
cannot be filled with spam.

ვიზიტორი ირჩევს სახელს, წერს ჩანაწერს — და ის საიტზე მხოლოდ მას შემდეგ ჩნდება,
რაც წაიკითხავთ და დაამტკიცებთ.

Run it (serves the site and the guest book from one process):

```bash
GUESTBOOK_TOKEN=pick-a-long-secret python3 server/guestbook.py
```

**Moderating from a browser — `/admin`.** Open
`https://your-site/admin`, type the token once (it is remembered for the tab),
and every waiting note appears with **დატოვება** and **წაშლა** buttons. It works
on a phone, so notes can be approved from anywhere. The page is `noindex` and
every action is refused without the token.

**Why a note does not appear at once.** That is the default and it is on
purpose: the note is saved, but it waits for you. Open `/admin`, press
**დატოვება**, and it is on the page. `/admin` *is* the account — there is no
other login: the "password" is the `GUESTBOOK_TOKEN` you set in Railway →
Variables. The same page also lists everything already published, so a note can
be taken down later.

რატომ არ ჩნდება ჩანაწერი მაშინვე: ის შენახულია, მაგრამ ელოდება თქვენს
დადასტურებას. გახსენით `/admin`, შეიყვანეთ `GUESTBOOK_TOKEN` (ეს არის თქვენი
„ექაუნთი“ — სხვა შესასვლელი არ არის) და დააჭირეთ **დატოვება**.

**Or publish every note the moment it is written.** Railway → Variables → add
`GUESTBOOK_AUTO_APPROVE=1`. Notes then go up instantly — the page even shows the
new note without a reload — and the wording under the form changes by itself to
say so. Everything else still guards it: links refused, one note per address per
minute and ten a day, the honeypot, the length caps, and text-only rendering.
`/admin` keeps working, now as the place to delete anything unwanted.

თუ გინდათ, რომ ჩანაწერი მაშინვე გამოქვეყნდეს — Railway → Variables →
`GUESTBOOK_AUTO_APPROVE=1`.

**Being told when a note arrives.** Set either of these and a message is sent
the moment a note or an invitation comes in (it never delays or breaks the
visitor's request):

* `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` — from @BotFather; write to the
  bot once and read the chat id from
  `https://api.telegram.org/bot<TOKEN>/getUpdates`
* `NOTIFY_WEBHOOK` — any address that accepts a JSON `{"title", "text"}` POST

Or from a terminal:

```bash
GUESTBOOK_TOKEN=pick-a-long-secret python3 server/moderate.py            # list
GUESTBOOK_TOKEN=pick-a-long-secret python3 server/moderate.py keep 3
GUESTBOOK_TOKEN=pick-a-long-secret python3 server/moderate.py delete 4
```

The page is already pointed at `/api/guestbook`, so **the moment that server is
the web process the form appears by itself** — no rebuild, no further edit.
While nothing answers there, the page shows his photograph, says the form is not
switched on yet, and offers Instagram instead.

**On Railway, do not add a `Procfile` for this.** One was tried and it took the
whole site down: the file changes how the service is built, not just what it
runs, and the deploy failed. Change it in the dashboard instead, where it can be
undone in a click:

1. Settings → Deploy → **Custom Start Command**:
   `python3 server/guestbook.py || python3 -m http.server $PORT`
   The second half is a safety net: if the guest-book server cannot start at
   all, the site is still served as plain files.
2. Variables → add `GUESTBOOK_TOKEN` (a long secret of your choosing)
3. Variables → add `DATABASE_URL` as a reference to the Postgres service —
   in Railway type `${{Postgres.DATABASE_URL}}`. With it the notes live in
   Postgres and survive every redeploy. Without it the server falls back to
   SQLite, which needs a volume to survive one.
4. `guestbookApi` is already `/api/guestbook`, so there is nothing to rebuild —
   the form appears as soon as the server answers.

If the deploy goes wrong, clearing the custom start command puts the site back
exactly as it is now. Standard library only — nothing to install.

The server is built not to take the site down with it: if the database cannot be
opened it says so on startup, serves every page as normal, answers only the
guest-book endpoints with 503, and reports `guestbook: false` at `/healthz` —
tested by forcing the database to fail, with pages still returning 200.

The page keeps working without any of this: if no guest book answers, the notes
already in the content files still show and the form quietly disappears instead
of failing when someone presses send. To collect notes by e-mail instead, leave
`guestbookApi` empty and add approved notes to the `entries` list in the content
files by hand.

What it does about abuse: notes are held for approval, one note per address per
minute and ten a day, links refused, a hidden honeypot field, lengths capped,
and every note is rendered as text — a note containing HTML shows the HTML as
characters rather than running it.

### Checking the setup / შემოწმება

Open `https://your-site/healthz`. It answers with booleans only — nothing
secret — and they say exactly how the running server is set up:

```json
{"ok": true, "guestbook": true, "store": "postgres",
 "databaseUrl": true, "psycopg": true, "autoApprove": false, "token": true}
```

* `"store": "sqlite"` with `"databaseUrl": false` — **the notes are inside the
  container and the next deploy erases them.** Add `DATABASE_URL` as
  `${{Postgres.DATABASE_URL}}` to the *web* service (not to the Postgres one).
* `"databaseUrl": true` but `"psycopg": false` — the variable is there but the
  library is not installed; `requirements.txt` must be picked up by the build.
* `"autoApprove": false` — notes wait for you at `/admin`; `true` — they are
  published the moment they are written.
* `"token": false` — `GUESTBOOK_TOKEN` is not set, so `/admin` cannot be used.

`/healthz` გახსენით და ნახავთ, როგორ არის რეალურად აწყობილი სერვერი: სად ინახება
ჩანაწერები, ჩართულია თუ არა მაშინვე გამოქვეყნება და დაყენებულია თუ არა ტოკენი.

## Invitations / მოწვევები

`/ka/booking.html` and `/en/booking.html` are the page for anyone who wants to
invite him — a lecture, a class, a talk, a conference. The form asks who is
asking, how to reach them, the organisation, the wanted date, the audience and
the subject, and it goes to the same server as the guest book (`POST
/api/booking`). Requests are never public: they sit in `/admin` →
**მოწვევები**, each with **დამუშავებულია** and **წაშლა**, and, if
notifications are on, a message arrives the moment one comes in. With no server
answering, the page offers Instagram instead — it never shows a form that
cannot send.

მოწვევის გვერდი: ვინც ლექციაზე ან შეხვედრაზე ეპატიჟება, აქ წერს. განაცხადები
საჯარო არასდროსაა — ისინი ჩანს მხოლოდ `/admin`-ში.

## The Legend page / „ლეგენდების“ გვერდი

A magazine-style spread of tall tales, written in his own voice and labelled as
such: the lead says nothing on the page is confirmed, and the last line says
plainly that everything else on the site is meant seriously and this page is
not. It is comedy published under his own name — not invented coverage
attributed to outlets, journals or experts that do not exist.

ხუმრობის გვერდი, ჟურნალის მაკეტით. შესავალშივე წერია, რომ არც ერთი ამბავი არ
არის დადასტურებული, ბოლო ხაზში კი — რომ საიტის დანარჩენი ნაწილი სერიოზულია.

Entries and the "records" list live in the `legend` block of both content
files; add or remove either and rebuild.

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

**Built in, if the guest-book server is the web process.** Every page quietly
counts itself: `POST /api/hit` stores the day, the page and the language — no
address, no cookie, no fingerprint — and Do Not Track is honoured. Open `/admin`
→ **სტატისტიკა** for the total, the last fourteen days, the most-read pages and
where the visitors came from. Nothing is sent to anyone else.

**Or an outside counter.** Off by default. For free, privacy-friendly counting register a name at
[goatcounter.com](https://www.goatcounter.com) and put it in
`analytics.goatcounter` in `content/site.json` (the name only, not the URL); or
put your domain in `analytics.plausible`. Rebuild and the script is added to
every page. Leave both empty and no tracking code is emitted at all.

## Buying the domain later / დომენის შემდეგ შეძენა

Everything works today on the GitHub Pages address. When the domain is bought,
three steps and it is done — nothing else in the project needs editing:

```bash
# 1. put the new address in content/site.json  ("baseUrl": "https://maxdarkosadze.ge")
python3 tools/brand.py     # 2. redraws the QR code, the card and the signature
python3 build.py           # 3. rewrites canonical links, hreflang, sitemap, share cards
```

Then point the domain at the host. On Railway: Settings → Networking → **Custom
Domain**, type the domain, and copy the `CNAME` target it shows into your
registrar's DNS (for a bare `maxdarkosadze.ge` use the registrar's ALIAS/ANAME
record, or `www` plus a redirect). The certificate is issued automatically; give
DNS an hour.

**Google Search Console** — this is what makes searches for the name find the
site:

1. [search.google.com/search-console](https://search.google.com/search-console)
   → Add property → **URL prefix** → the full address.
2. Choose **HTML tag**. It gives a tag like
   `<meta name="google-site-verification" content="AbC123…">`.
3. Put **only the code** — `AbC123…` — into `googleVerification` in
   `content/site.json`, run `python3 build.py`, push, wait for the deploy, then
   press **Verify**. The tag is written into every page and survives every
   rebuild.
4. In Search Console → Sitemaps, submit `sitemap.xml`. It already lists every
   page in both languages, and `robots.txt` points at it.
5. Ask for the two front pages to be read at once: paste the address into the
   search bar at the top → **Request indexing**, for `/ka/` and `/en/`.

Google-ის ძიებაში გამოსაჩენად: Search Console → HTML tag → კოდი ჩასვით
`content/site.json`-ში (`googleVerification`), გაუშვით `python3 build.py`,
ატვირთეთ და დააჭირეთ Verify. შემდეგ Sitemaps → `sitemap.xml`.

დომენის ყიდვის შემდეგ: შეცვალეთ `baseUrl` ფაილში `content/site.json`, გაუშვით ეს
ორი ბრძანება და მორჩა — QR-კოდი, ვიზიტკა, ბმულები და sitemap თავისით განახლდება.

## The short film / მოკლე ფილმი

A half-minute film is built from the photographs already in `assets/img`: a slow
drift across each picture, a dissolve between them, one word on screen for each
life, the name at the front and the address at the end. It is silent on purpose,
so it can sit on a page without ambushing anyone with sound.

```bash
pip install Pillow imageio-ffmpeg     # once
python3 tools/video.py                # both languages, ~1 min per language
python3 tools/video.py --fast         # quarter size, for checking the cut
python3 build.py
```

It writes `assets/video/showreel-ka.mp4` and `.webm` (and the English pair) plus
`showreel-poster.jpg`, and the home page and the gallery pick them up by name —
if the files are not there, the section simply does not appear. To change which
photographs are used, or the word shown over each, edit the `SHOTS` list at the
top of `tools/video.py`. The closing card reads the address from
`content/site.json`, so it follows the domain by itself.

ფილმი იქმნება იმ ფოტოებისგან, რომლებიც უკვე საიტზეა: ნელი მოძრაობა თითოეულ
კადრზე, რბილი გადასვლები, ერთი სიტყვა ეკრანზე. ხმა განზრახ არ აქვს. კადრების
თანმიმდევრობა და წარწერები იცვლება `tools/video.py`-ის `SHOTS` სიაში.

**Adding music.** A film on a personal site is better with a track you have the
right to use — buy one, or use a piece licensed for the purpose — then:

```bash
ffmpeg -i assets/video/showreel-ka.mp4 -i track.mp3 -shortest \
       -c:v copy -c:a aac -b:a 160k showreel-ka-music.mp4
```

Do not take a track off YouTube or a film: the site carries his name, and a
copyright claim against it is the one kind of attention it does not need.

## Share images / გაზიარების სურათები

Every page and every article has its own picture for when the link is posted to
Facebook, WhatsApp, Telegram or LinkedIn — the page's own title over its own
photograph, drawn by:

```bash
python3 tools/og_images.py      # writes assets/og/<lang>-<page>.jpg
```

Run it again after changing a title. `build.py` picks the file up automatically
and falls back to `assets/img/og.jpg` if one is missing.

## Brand kit / ბრენდის მასალები

```bash
python3 tools/brand.py
```

writes into `assets/brand/`: the wordmark (SVG, light and dark), a business card
front and back at 85×55 mm / 300 dpi ready for a printer, a QR code pointing at
the site, an e-mail signature to paste into Gmail or Outlook, and six Instagram
highlight covers. They are all linked from the press-kit page as well.

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
