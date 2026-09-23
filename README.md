# Max Darkosadze — maxdarkosadze / მაქსი დარკოსაძე

A bilingual (English + Georgian) website about **Max Darkosadze / მაქსი დარკოსაძე**,
known to many simply as **Mr. Max / ბატონი მაქსი** — writer, director and
contemporary philosopher; also a lecturer, a surgeon and an aviation instructor.

ორენოვანი (ქართული და ინგლისური) საიტი **მაქს დარკოსაძეზე**, რომელიც ბევრისთვის
უბრალოდ **„ბატონი მაქსია“** — მწერალი, რეჟისორი და თანამედროვე ფილოსოფოსი;
ასევე ლექტორი, ქირურგი და ავიაინსტრუქტორი.

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
5. **The Philosophy of Mr. Max / ბატონი მაქსის ფილოსოფია** — `articles/philosopher.html`
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

## The address / მისამართი

The site lives at **https://maxdarkosadze.com**. `baseUrl` in
`content/site.json` is the single place that address is written; canonical
links, hreflang, the sitemap, the share cards, the QR code, the business card
and the closing card of the film all follow it. If it ever changes:

```bash
# 1. put the new address in content/site.json ("baseUrl")
python3 tools/brand.py       # QR, card, signature, quotation cards
python3 tools/og_images.py   # the pictures shown when a link is shared
python3 tools/video.py       # the closing card of the film
python3 build.py             # canonical links, hreflang, sitemap, robots.txt
```

**The old Railway address redirects here.** `server/guestbook.py` answers any
other host — the `*.up.railway.app` one, or a `www.` spelling — with a
permanent redirect to the address in `baseUrl`, so links and search results
gather in one place instead of being split between two identical sites. The
guest book API, `/admin` and `/healthz` are answered wherever they are asked, so
nothing in flight breaks. Set `CANONICAL_HOST` to override the host it redirects
to.

**`www.` needs its own entry.** In Railway → Settings → Networking, add
`www.maxdarkosadze.com` as a second custom domain and point the DNS at what it
shows; visitors who type `www.` are then redirected to the bare address.

## Being found / ძებნაში პოვნა

What the site already does for itself: both spellings of the name in every
title, a `Person` record with the Instagram and IMDb links as `sameAs`, a
`WebSite` record with the site's own search, `FAQPage` answers, an `Article`
record per article, a sitemap that carries the photographs and the film as well
as the pages, `robots.txt` pointing at it, and
`max-image-preview:large` so a picture can appear beside the result.

What has to be done once, by hand:

1. **Google Search Console** — [search.google.com/search-console](https://search.google.com/search-console)
   → Add property → **URL prefix** → `https://maxdarkosadze.com` → **HTML tag**.
   Paste only the code (the `content="…"` part) into `googleVerification` in
   `content/site.json`, run `python3 build.py`, push, wait for the deploy, then
   press Verify.
2. **Sitemaps** → submit `sitemap.xml`. Then paste `https://maxdarkosadze.com/ka/`
   and `/en/` into the bar at the top and press **Request indexing** for each.
3. **Bing Webmaster Tools** ([bing.com/webmasters](https://www.bing.com/webmasters))
   — same again into `bingVerification`. It feeds DuckDuckGo too.
4. **Links from places Google already trusts** — this is what actually decides
   whether the site comes first. Put the address in the Instagram bio, in the
   IMDb profile, in an e-mail signature, and anywhere else his name already
   appears. A handful of real links outrank any amount of markup.

Give it a week or two: a new domain is not ranked the day it is verified.

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

### The film behind the title / ფილმი მთავარ გვერდზე

On a wide screen the home page runs the same film quietly behind the name —
muted, looping, no sound, with a small button in the corner to stop it. It is
never loaded on a phone, never when the browser says the visitor prefers less
motion, and never when the connection asks to save data: those visitors keep the
photograph, which is what was there before. If the film cannot start, the
photograph stays. Nothing to switch on — the page uses whatever
`python3 tools/video.py` last produced.

ფართო ეკრანზე მთავარ გვერდზე ფილმი ჩუმად მიდის სახელის უკან; კუთხეში ღილაკია
გასაჩერებლად. ტელეფონზე და ნელ ინტერნეტზე ფილმი საერთოდ არ იტვირთება.

## The mark / ლოგო

`python3 tools/logo.py` draws the monogram once and exports every shape a
browser, a phone or Google asks for, so none of them can drift apart:

| file | where it is seen |
| --- | --- |
| `favicon.ico` (16, 32, 48) | the browser tab, and the first thing Google reads |
| `assets/img/favicon.svg` | browsers that prefer vector — also the mark in the site header |
| `assets/icons/icon-48…512.png` | search results, Android, the manifest |
| `assets/icons/maskable-512.png` | Android, which crops the corners off |
| `assets/icons/apple-touch-icon.png` | iPhone home screen |
| `assets/brand/logo-dark.png`, `logo-light.png` | slides, profiles, print |

It is the site's own alphabet: MD in Newsreader on the ink ground, a violet
hairline frame, a violet rule beneath the letters. Sixteen pixels cannot hold
two serif letters and a frame, so that one size keeps only the **M** and the
rule — the same reason a road sign is not a paragraph.

The letters in the SVG are outlines, not text: a favicon is drawn before any
web font arrives. The drawing needs `tools/fonts/Newsreader-SemiBold.ttf`, which
is the self-hosted web font instanced at weight 600, and Pillow.

Google shows the icon beside the result only after it crawls the site again,
and only if it stays square, a multiple of 48 px, reachable at the same
address and unchanged for a while. Nothing to press — it appears on its own.

ლოგო ერთხელ იხატება და ყველა ზომაში ერთნაირია: ჩანართში, Google-ის შედეგთან,
ტელეფონის ეკრანზე. Google-ს თავისი გრაფიკი აქვს — ხელახალი ინდექსაციის შემდეგ
გამოჩნდება.

## On a phone's home screen / ტელეფონის ეკრანზე

The site can be kept on a phone like an app: **Share → Add to Home Screen** on
iPhone, **⋮ → Install app** on Android. It then opens without the browser bars,
with its own icon, and the pages already visited open even with no signal.

`build.py` writes `manifest.webmanifest` (name, icon, colours, and shortcuts
straight to the gallery, the guest book and the invitation page) and `sw.js`.
The icons come from `python3 tools/logo.py` — see **The mark** below.

The worker is deliberately timid, because a careless one can serve yesterday's
site for days: **every page is fetched from the network first** and the cached
copy is used only when the network fails; pictures, fonts, the stylesheet and
the script are served from the cache and refreshed behind the visitor; the guest
book (`/api/…`) and `/admin` are never touched. Each build stamps a new version,
and the old cache is deleted the moment the new worker takes over.

To switch it off entirely: delete `sw.js`, remove the registration at the foot
of `assets/js/main.js`, and rebuild. A browser that already has it can be
cleared from the console with
`navigator.serviceWorker.getRegistration().then(r => r.active.postMessage("unregister"))`.

საიტი ტელეფონის ეკრანზე აპლიკაციასავით დაყენდება: iPhone-ზე Share → „Add to Home
Screen“, Android-ზე ⋮ → „Install app“. უკვე ნანახი გვერდები ინტერნეტის გარეშეც
იხსნება.

## The filmography / ფილმოგრაფია

`/ka/films.html` and `/en/films.html` list every public screen credit: the
title, the year, the format, the genre, the country, the language, the jobs he
did on it and a link to the entry on IMDb. Each film is also handed to search
engines as a `Movie` record (director, writer, producer, actor, `sameAs` the
IMDb title), which is what lets a search result show the work rather than only
the name.

The list is written in `content/<lang>.json` under `pages.films`, taken from the
public credits on IMDb (`nm8752510`) — nothing is listed that cannot be checked
there. It does not update itself: when a new credit appears on IMDb, add the
same entry here (`title`, `year`, `kind`, `roles`, `genre`, `genreSchema`,
`country`, `language`, `imdb`, `id`, `text`) and rebuild.

ფილმოგრაფია `pages.films`-შია ორივე ენაზე. ახალი კრედიტი ჯერ IMDb-ზე ჩნდება,
შემდეგ აქ იწერება ხელით.

## Void Mafia / თამაში

`/ka/void-mafia.html` and `/en/void-mafia.html` are the site's page about the
game he built — a cyberpunk social-deduction game that plays in the browser in
Georgian and English, at **voidmafia.one**. The page says what it is, what is
inside it and why he recommends it, and sends the reader to the game's own
address; the game itself is a separate site and is not served from here.

It is also the first entry in the projects list on the home page, it has a band
of its own there, it sits in the menu as "Game", and `voidmafia.one` is listed
in the `sameAs` of his Person record, so a search engine can connect the person
and the game. The page carries a `VideoGame` record with him as its author.

The mark shown on the page is the game's own icon, kept at
`assets/img/voidmafia.png`; its violet happens to be the site's own accent.

ეს გვერდი მხოლოდ ამბობს, რომ თამაში მისია, და მიუთითებს voidmafia.one-ზე.

## Share images / გაზიარების სურათები

Every page and every article has its own picture for when the link is posted to
Facebook, WhatsApp, Telegram or LinkedIn — the page's own title over its own
photograph, drawn by:

```bash
python3 tools/og_images.py      # writes assets/og/<lang>-<page>.jpg
```

Each card is the site in miniature: the ink panel carries the title (Newsreader
for Latin, Noto Serif Georgian for Georgian) over the violet glow, the
photograph keeps its own frame at full colour on the right, and a violet seam
runs between them. Nothing is faded across a face, and the mark is the same one
the browser tab shows.

Run it again after changing a title. `build.py` picks the file up automatically
and falls back to `assets/img/og.jpg` if one is missing.

## The design — THE ARCHIVE / დიზაინი

The site is a dark editorial archive rather than a portfolio: near-black ground,
hairline borders, one violet and one cold blue used sparingly, and typography
doing most of the work. Everything is driven by the tokens at the top of
`assets/css/style.css`:

```css
--ink: #08090b;  --ink-2: #111318;  --surface: #15171c;
--text: #f2f2f0; --muted: #9a9da5;  --line: rgba(255,255,255,.10);
--violet: #7c5cff; --blue: #7ea7ff;
--display: "Cormorant Garamond", "Noto Serif Georgian", …;
--sans: "Inter", "Noto Sans Georgian", …;
```

Change a token and the whole site follows. There is no light theme and no theme
switch: the archive is dark by design.

**The homepage is one narrative**, built by `render_home()` in `build.py` from
the `archive` block of `content/ka.json` and `content/en.json`:

> hero → the statement → the five worlds → about → surgery → aviation →
> philosophy → writing → the book → the film → projects → the Library of the
> Void → the visual archive → the journey → notes → contact

Each part reads its text from `archive.<name>`; nothing in the layout is
hard-coded prose. The five disciplines share one renderer
(`discipline_block()`), so a new one is a content change, not a template change.

**Motion** lives in `assets/js/main.js` and is all optional: sections reveal as
they approach, a two-part cursor names what a link would do, buttons lean
towards the pointer, the portrait drifts with it, and a black veil with a thin
violet line covers a page change. Every one of these is switched off by
`prefers-reduced-motion`, and the pointer effects only run on a device with a
fine pointer — a phone gets none of them and pays for none of them.

**Unverified facts are visible, not invented.** Anything written as
`[[…]]` in the content files renders as marked text on the page: the
professional background in surgery and aviation, the book's chapters, excerpt
and status, one project, and every row of the journey. Replace the text between
the brackets and the mark disappears.

დიზაინი: მუქი, სარედაქციო არქივი. ფერები და შრიფტები ერთ ადგილას წერია
(`assets/css/style.css`-ის თავში), მთავარი გვერდის თექვსმეტივე ნაწილი კი
`content/*.json`-ის `archive` ბლოკიდან იკითხება. `[[…]]`-ში ჩასმული ტექსტი
გვერდზე გამოკვეთილად ჩანს — ეს ის ადგილებია, სადაც დადასტურებული ინფორმაცია
უნდა ჩაიწეროს.

## Typefaces / შრიფტები

Four faces are served from this site, never fetched from Google: **Cormorant
Garamond** and **Inter** for Latin, **Noto Serif Georgian** and **Noto Sans
Georgian** for Georgian, with the Georgian pair carrying anything the Latin
faces do not. Each page preloads only the two its own language sets text in.

The Georgian pair is cut to size here:
fewer round trips before the first letter is drawn, and no visitor announced to
a third party. `tools/webfonts.py` cuts Noto Serif Georgian and Noto Sans
Georgian (both under the SIL Open Font License) down to the characters the
content actually uses and writes them to `assets/fonts` as `.woff2` — 79 KB and
53 KB, one file per family covering every weight.

```bash
pip install fonttools brotli     # once
python3 tools/webfonts.py        # after adding text in a new alphabet
```

The stylesheet declares them and every page preloads them; there is nothing to
change in the HTML. Verified with a browser: zero requests leave the site.

## Questions / ხშირი კითხვები

`/ka/faq.html` and `/en/faq.html` answer what people actually ask — who he is,
where the name Mr. Max comes from, how to invite him, whether the Legend
page is true. Each answer can point at the page that says more: add `"link"`
with a page key (`booking`, `press`, `gallery`…) to an item in
`pages.faq.items` and the link appears by itself.

The page also carries a `FAQPage` record, which is the form Google reads when
it shows questions and answers directly in the search results.

## Search / ძებნა

`/ka/search.html` searches the whole site with no server behind it. `build.py`
writes `assets/search-ka.json` and `assets/search-en.json` — every page and
every article as plain text — and the page filters them in the visitor's own
browser as they type. A search is linkable (`search.html?q=ავიაცია`), and the
index is rebuilt with the site, so it can never fall behind the text.

## Brand kit / ბრენდის მასალები

```bash
python3 tools/brand.py
```

writes into `assets/brand/`: the wordmark (SVG, light and dark), a business card
front and back at 85×55 mm / 300 dpi ready for a printer, a QR code pointing at
the site, an e-mail signature to paste into Gmail or Outlook, and seven
Instagram highlight covers. They are all linked from the press-kit page as well.
Everything is drawn in the site's own colours — ink, paper and violet — and the
wordmark carries the mark's own letters as outlines, so it looks the same on a
slide where Newsreader is not installed.

### Quotation cards for Instagram / ციტატების ბარათები

`python3 tools/brand.py` also writes `assets/brand/quotes/` — every quotation
already on the site as a card in the site's own colours: `*-post.jpg` at
1080×1080 for the feed and `*-story.jpg` at 1080×1920 for stories, in both
languages, each carrying the name and the address. Write a new quotation into an
article (a block of `"type": "quote"`) and the next run makes its cards too.

ციტატების ბარათები Instagram-ისთვის: `assets/brand/quotes/` — კვადრატული
ფიდისთვის, ვერტიკალური სთორისთვის, ქართულად და ინგლისურად.

## Image formats / სურათების ფორმატები

`python3 tools/images.py` writes three things beside every photograph: a
phone-sized `-800.jpg`, a `.webp`, and a `-800.webp`. The pages serve WebP to
everything that accepts it and keep the JPEG for anything that does not — the
homepage went from 1.65 MB to 0.80 MB on that change alone, with no visible
difference. Drop a new photograph in and run the tool again; nothing else needs
touching.

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
