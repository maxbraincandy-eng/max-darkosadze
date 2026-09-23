/* Max Darkosadze — small progressive enhancements. No dependencies. */
(function () {
  "use strict";

  var docEl = document.documentElement;
  docEl.classList.add("js");
  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- mobile navigation ------------------------------------------- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");

  if (toggle && nav) {
    var setMenu = function (open) {
      document.body.classList.toggle("nav-open", open);
      nav.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      if (open) {
        var first = nav.querySelector("a");
        if (first) window.setTimeout(function () { first.focus(); }, 180);
      }
    };

    toggle.addEventListener("click", function () {
      setMenu(!document.body.classList.contains("nav-open"));
    });

    nav.addEventListener("click", function (event) {
      if (event.target.closest("a")) setMenu(false);
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && document.body.classList.contains("nav-open")) {
        setMenu(false);
        toggle.focus();
      }
    });
  }

  /* ---- photo slots --------------------------------------------------
     Every image on the site points at a fixed file name. Until that file
     exists, show the path so the photograph can simply be dropped in.    */
  var hintLabel = docEl.lang === "ka"
    ? "ფოტოს ადგილი — ჩააგდეთ სურათი მისამართზე: "
    : "Photo slot — place your image at: ";

  function markMissing(img) {
    var slot = img.closest(".img-slot");
    if (!slot || slot.classList.contains("is-missing")) return;
    slot.classList.add("is-missing");
    var path = slot.getAttribute("data-path") || "";
    slot.setAttribute("title", hintLabel + path);
    var mark = document.createElement("span");
    mark.className = "slot-hint";
    mark.setAttribute("aria-hidden", "true");
    mark.textContent = "MD";
    slot.appendChild(mark);
  }

  Array.prototype.forEach.call(document.querySelectorAll("img[data-slot]"), function (img) {
    if (img.complete) {
      if (!img.naturalWidth) markMissing(img);
    } else {
      img.addEventListener("error", function () { markMissing(img); });
    }
  });

  /* ---- header condenses once the page is scrolled -------------------- */
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-stuck", window.scrollY > 24);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---- reveal sections as they come into view ------------------------
     A plain position check rather than IntersectionObserver: a fast flick
     scroll can move an element past the observer between two computations,
     which would leave that section invisible for good.                     */
  var revealTargets = Array.prototype.slice.call(document.querySelectorAll(
    "[data-reveal], .section-head, .pillar, .card, .programme, .honour, .gal-item, " +
    ".timeline li, .split-body, .split-media, .contact-card, .big-quote, .world, .entry, .project"
  ));

  if (!reduced && revealTargets.length) {
    revealTargets.forEach(function (el, i) {
      el.setAttribute("data-reveal", "");
      el.style.setProperty("--reveal-delay", Math.min(i % 6, 5) * 60 + "ms");
    });

    var pending = revealTargets.slice();
    var queued = false;

    var revealAll = function () {
      pending.forEach(function (el) { el.classList.add("is-visible"); });
      pending = [];
    };

    var check = function () {
      queued = false;
      var limit = window.innerHeight * 0.92;
      pending = pending.filter(function (el) {
        if (el.getBoundingClientRect().top < limit) {
          el.classList.add("is-visible");
          return false;
        }
        return true;
      });
      if (!pending.length) {
        window.removeEventListener("scroll", queue);
        window.removeEventListener("resize", check);
      }
    };

    var queue = function () {
      if (!queued) { queued = true; window.requestAnimationFrame(check); }
    };

    window.addEventListener("scroll", queue, { passive: true });
    window.addEventListener("resize", check);
    window.addEventListener("load", check);
    window.addEventListener("beforeprint", revealAll);
    check();
  }

  /* ---- reading progress on article pages ----------------------------- */
  var article = document.querySelector(".article");
  if (article) {
    var bar = document.createElement("div");
    bar.className = "progress";
    document.body.appendChild(bar);
    var ticking = false;
    var update = function () {
      // full when the end of the article reaches the bottom of the viewport
      var rect = article.getBoundingClientRect();
      var ratio = rect.height > 0 ? (window.innerHeight - rect.top) / rect.height : 1;
      bar.style.transform = "scaleX(" + Math.min(1, Math.max(0, ratio)) + ")";
      ticking = false;
    };
    update();
    window.addEventListener("scroll", function () {
      if (!ticking) { ticking = true; window.requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener("resize", update);
  }

  /* ---- gallery: filters and a lightbox you can walk through ---------- */
  var gallery = document.querySelector(".gallery[data-lightbox]");
  if (gallery) {
    var tiles = Array.prototype.slice.call(gallery.querySelectorAll(".gal-item"));
    var labels = {
      close: gallery.getAttribute("data-label-close") || "Close",
      prev: gallery.getAttribute("data-label-prev") || "Previous",
      next: gallery.getAttribute("data-label-next") || "Next"
    };

    /* --- filter chips --- */
    var chips = Array.prototype.slice.call(document.querySelectorAll(".chip[data-filter]"));
    var counter = document.querySelector("[data-gallery-count]");
    var empty = document.querySelector(".gal-empty");
    var visible = tiles.slice();

    var applyFilter = function (key) {
      visible = [];
      tiles.forEach(function (tile) {
        var show = key === "all" || tile.getAttribute("data-category") === key;
        tile.hidden = !show;
        if (show) visible.push(tile);
      });
      chips.forEach(function (chip) {
        var on = chip.getAttribute("data-filter") === key;
        chip.classList.toggle("is-on", on);
        chip.setAttribute("aria-pressed", on ? "true" : "false");
      });
      if (counter) counter.textContent = visible.length;
      if (empty) empty.hidden = visible.length > 0;
    };

    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        applyFilter(chip.getAttribute("data-filter"));
      });
    });

    /* --- lightbox --- */
    var box = null, current = 0;

    var show = function (index) {
      if (!visible.length) return;
      current = (index + visible.length) % visible.length;
      var tile = visible[current];
      var img = tile.querySelector("img");
      var caption = tile.querySelector("figcaption");
      box.querySelector(".lightbox-figure img").src = img.currentSrc || img.src;
      box.querySelector(".lightbox-figure img").alt = img.alt || "";
      box.querySelector(".lightbox-figure figcaption").textContent =
        caption ? caption.textContent.trim() : "";
      box.querySelector(".lightbox-counter").textContent =
        (current + 1) + " / " + visible.length;
      var solo = visible.length < 2;
      box.querySelector(".lightbox-prev").hidden = solo;
      box.querySelector(".lightbox-next").hidden = solo;
    };

    var close = function () {
      if (!box) return;
      var node = box;
      box = null;
      node.classList.remove("is-open");
      document.body.style.removeProperty("overflow");
      window.setTimeout(function () { node.remove(); }, 250);
    };

    var button = function (cls, label, glyph) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = cls;
      b.setAttribute("aria-label", label);
      b.innerHTML = glyph;
      return b;
    };

    var open = function (tile) {
      box = document.createElement("div");
      box.className = "lightbox";
      box.setAttribute("role", "dialog");
      box.setAttribute("aria-modal", "true");
      box.innerHTML =
        '<figure class="lightbox-figure"><img alt=""><figcaption></figcaption></figure>' +
        '<p class="lightbox-counter"></p>';
      var closeButton = button("lightbox-close", labels.close, "&times;");
      box.appendChild(closeButton);
      box.appendChild(button("lightbox-prev", labels.prev, "&#8249;"));
      box.appendChild(button("lightbox-next", labels.next, "&#8250;"));

      box.addEventListener("click", function (event) {
        var hit = event.target.closest("button");
        if (hit && hit.classList.contains("lightbox-prev")) return show(current - 1);
        if (hit && hit.classList.contains("lightbox-next")) return show(current + 1);
        if (hit && hit.classList.contains("lightbox-close")) return close();
        if (event.target === box) close();
      });

      document.body.appendChild(box);
      document.body.style.overflow = "hidden";
      show(visible.indexOf(tile));
      window.requestAnimationFrame(function () { box.classList.add("is-open"); });
      closeButton.focus();
    };

    gallery.addEventListener("click", function (event) {
      var opener = event.target.closest(".gal-open");
      if (!opener) return;
      var tile = opener.closest(".gal-item");
      if (tile.querySelector(".img-slot.is-missing")) return;
      open(tile);
    });

    document.addEventListener("keydown", function (event) {
      if (!box) return;
      if (event.key === "Escape") close();
      if (event.key === "ArrowRight") show(current + 1);
      if (event.key === "ArrowLeft") show(current - 1);
    });

    /* --- swipe on a phone --- */
    var touchX = null;
    document.addEventListener("touchstart", function (e) {
      if (box) touchX = e.changedTouches[0].clientX;
    }, { passive: true });
    document.addEventListener("touchend", function (e) {
      if (!box || touchX === null) return;
      var dx = e.changedTouches[0].clientX - touchX;
      if (Math.abs(dx) > 50) show(current + (dx < 0 ? 1 : -1));
      touchX = null;
    }, { passive: true });
  }

  /* ---- guest book ---------------------------------------------------- */
  var guest = document.querySelector("[data-guestbook]");
  if (guest) {
    var api = guest.getAttribute("data-guestbook");
    var postTo = guest.getAttribute("data-guestbook-post") || api;
    var mode = guest.getAttribute("data-guestbook-mode") || "off";
    var list = guest.querySelector("[data-notes]");
    var emptyNote = guest.querySelector(".guest-empty");
    var form = guest.querySelector(".guest-form");
    var say = function (key) { return guest.getAttribute("data-msg-" + key) || ""; };

    var noteElement = function (note) {
      var li = document.createElement("li");
      li.className = "note-card";
      var text = document.createElement("p");
      text.className = "note-text";
      text.textContent = note.message;              // text, never markup
      var by = document.createElement("p");
      by.className = "note-by";
      var name = document.createElement("span");
      name.className = "note-name";
      name.textContent = note.name;
      by.appendChild(name);
      if (note.place) {
        var place = document.createElement("span");
        place.className = "note-place";
        place.textContent = note.place;
        by.appendChild(place);
      }
      li.appendChild(text);
      li.appendChild(by);
      return li;
    };

    var offline = function () {
      /* no guest-book service answering: keep whatever notes are already on the
         page and take the form away rather than leave one that cannot send. */
      var wrap = guest.querySelector(".guest-form-wrap");
      if (!wrap) return;
      var form = wrap.querySelector(".guest-form");
      if (!form) return;
      var note = document.createElement("p");
      note.className = "note";
      note.textContent = guest.getAttribute("data-msg-offline") || "";
      var url = guest.getAttribute("data-offline-url");
      var cta = guest.getAttribute("data-offline-cta");
      form.replaceWith(note);
      if (url && cta) {
        var link = document.createElement("a");
        link.className = "btn btn-primary";
        link.href = url;
        link.target = "_blank";
        link.rel = "noopener";
        link.textContent = cta;
        var holder = document.createElement("p");
        holder.appendChild(link);
        note.after(holder);
      }
    };

    if (api) {
      fetch(api, { headers: { "Accept": "application/json" } })
        .then(function (r) {
          if (!r.ok) throw new Error("no guest book");
          return r.json();
        })
        .then(function (data) {
          if (!data || !data.notes) return;
          data.notes.forEach(function (note) { list.appendChild(noteElement(note)); });
          if (emptyNote) emptyNote.hidden = list.children.length > 0;
          if (data.moderated === false) {
            /* notes go up at once: do not promise a wait that will not happen */
            var hint = guest.querySelector("[data-form-note]");
            if (hint && say("instant")) hint.textContent = say("instant");
          }
        })
        .catch(offline);
    }

    if (form) {
      var field = form.querySelector("textarea[name=message]");
      var counter = form.querySelector("[data-counter]");
      var status = form.querySelector(".form-status");
      var button = form.querySelector("button[type=submit]");

      if (field && counter) {
        var count = function () {
          counter.textContent = Math.max(0, 700 - field.value.length);
        };
        field.addEventListener("input", count);
        count();
      }

      var tell = function (message, kind) {
        status.textContent = message;
        status.hidden = !message;
        status.className = "form-status" + (kind ? " is-" + kind : "");
      };

      form.addEventListener("submit", function (event) {
        event.preventDefault();
        var payload = {
          name: form.name.value.trim(),
          place: form.place.value.trim(),
          message: form.message.value.trim(),
          website: form.website.value,
          lang: docEl.lang
        };
        if (!payload.name || payload.message.length < 2) return;
        if (payload.message.length > 700) return tell(say("long"), "error");

        button.disabled = true;
        tell(say("sending"));
        fetch(postTo, {
          method: "POST",
          headers: { "Content-Type": "application/json", "Accept": "application/json" },
          body: JSON.stringify(payload)
        }).then(function (r) {
          if (!r.ok) {
            /* say which rule stopped it, not just "it failed" */
            return r.json().catch(function () { return {}; }).then(function (body) {
              var reason = (body && body.error) || "";
              var key = reason === "too soon" ? "soon"
                      : reason === "too many" ? "many"
                      : reason === "links are not accepted" ? "links" : "";
              var message = key && say(key);
              throw new Error(message || "rejected");
            });
          }
          return r.json().catch(function () { return {}; });
        }).then(function (data) {
          form.reset();
          if (counter) counter.textContent = "700";
          if (data && data.pending === false) {
            /* the server published it straight away: put it on the page now */
            if (data.note && list) {
              list.insertBefore(noteElement(data.note), list.firstChild);
              if (emptyNote) emptyNote.hidden = true;
            }
            tell(say("published") || say("thanks"), "ok");
          } else {
            tell(say("thanks"), "ok");
          }
        }).catch(function (problem) {
          var message = problem && problem.message;
          tell(message && message !== "rejected" ? message : say("error"), "error");
        }).then(function () {
          button.disabled = false;
        });
      });
    }
  }

  /* ---- invitation form ----------------------------------------------- */
  var booking = document.querySelector("[data-booking]");
  if (booking) {
    var target = booking.getAttribute("data-booking");
    var scope = booking.closest("[data-msg-sending]") || booking;
    var speak = function (key) { return scope.getAttribute("data-msg-" + key) || ""; };
    var state = booking.querySelector(".form-status");
    var sendButton = booking.querySelector("button[type=submit]");

    var report = function (message, kind) {
      state.textContent = message;
      state.hidden = !message;
      state.className = "form-status" + (kind ? " is-" + kind : "");
    };

    booking.addEventListener("submit", function (event) {
      event.preventDefault();
      var payload = {
        name: booking.name.value.trim(),
        contact: booking.contact.value.trim(),
        org: booking.org.value.trim(),
        wanted: booking.wanted.value.trim(),
        audience: booking.audience.value.trim(),
        topic: booking.topic.value.trim(),
        message: booking.message.value.trim(),
        website: booking.website.value,
        lang: docEl.lang
      };
      if (!payload.name || !payload.contact) return;
      sendButton.disabled = true;
      report(speak("sending"));
      fetch(target, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify(payload)
      }).then(function (r) {
        if (!r.ok) throw new Error("rejected");
        booking.reset();
        report(speak("thanks"), "ok");
      }).catch(function () {
        report(speak("error"), "error");
      }).then(function () {
        sendButton.disabled = false;
      });
    });

    /* nothing listening: offer Instagram rather than a form that cannot send */
    fetch(target.replace("/api/booking", "/api/guestbook"), { method: "GET" })
      .then(function (r) { if (!r.ok) throw new Error("no server"); })
      .catch(function () {
        var note = document.createElement("p");
        note.className = "note";
        note.textContent = scope.getAttribute("data-msg-offline") || "";
        var url = scope.getAttribute("data-offline-url");
        var cta = scope.getAttribute("data-offline-cta");
        booking.replaceWith(note);
        if (url && cta) {
          var link = document.createElement("a");
          link.className = "btn btn-primary";
          link.href = url;
          link.target = "_blank";
          link.rel = "noopener";
          link.textContent = cta;
          var holder = document.createElement("p");
          holder.appendChild(link);
          note.after(holder);
        }
      });
  }

  /* ---- one anonymous count per page view ------------------------------
     No address, no cookie, no fingerprint: the page tells the site's own
     server which page was opened, and nothing else. Quietly does nothing
     when there is no server, or when the reader asks not to be tracked.  */
  try {
    var doNotTrack = navigator.doNotTrack === "1" || window.doNotTrack === "1";
    if (!doNotTrack && location.protocol.indexOf("http") === 0) {
      var sameSiteReferrer = document.referrer &&
        document.referrer.indexOf(location.origin) === 0;
      fetch("/api/hit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          path: location.pathname,
          lang: docEl.lang,
          ref: sameSiteReferrer ? "" : document.referrer
        }),
        keepalive: true
      }).catch(function () { /* no counter running */ });
    }
  } catch (e) { /* never let counting break a page */ }

  /* ---- the film, running quietly behind the title -------------------- */
  var filmSlot = document.querySelector(".hero .hero-media[data-hero-film]");
  if (filmSlot) {
    var wideEnough = window.matchMedia && window.matchMedia("(min-width: 60rem)").matches;
    var calmPlease = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var link = navigator.connection || {};
    var sparing = link.saveData === true || /2g/.test(link.effectiveType || "");

    /* a phone pays for every megabyte, and a visitor who asked for less
       motion means it: both keep the photograph and nothing else */
    if (wideEnough && !calmPlease && !sparing) {
      var film = document.createElement("video");
      film.className = "hero-film";
      film.muted = true;
      film.defaultMuted = true;
      film.loop = true;
      film.autoplay = true;
      film.playsInline = true;
      film.setAttribute("muted", "");
      film.setAttribute("playsinline", "");
      film.setAttribute("aria-hidden", "true");
      film.setAttribute("tabindex", "-1");
      var webm = filmSlot.getAttribute("data-hero-film-webm");
      if (webm) {
        var vp9 = document.createElement("source");
        vp9.src = webm;
        vp9.type = "video/webm";
        film.appendChild(vp9);
      }
      var h264 = document.createElement("source");
      h264.src = filmSlot.getAttribute("data-hero-film");
      h264.type = "video/mp4";
      film.appendChild(h264);

      var button = document.createElement("button");
      button.type = "button";
      button.className = "hero-film-toggle";
      var pauseLabel = filmSlot.getAttribute("data-film-pause") || "Pause";
      var playLabel = filmSlot.getAttribute("data-film-play") || "Play";
      var mark = function () {
        var paused = film.paused;
        button.setAttribute("aria-label", paused ? playLabel : pauseLabel);
        button.title = paused ? playLabel : pauseLabel;
        button.textContent = paused ? "▶" : "❚❚";
      };
      button.addEventListener("click", function () {
        if (film.paused) { film.play().catch(function () {}); } else { film.pause(); }
        mark();
      });

      film.addEventListener("playing", function () {
        filmSlot.classList.add("has-film");
        mark();
      });
      film.addEventListener("pause", mark);
      film.addEventListener("error", function () {
        filmSlot.classList.remove("has-film");
        if (button.parentNode) button.parentNode.removeChild(button);
      });

      filmSlot.appendChild(film);
      var hero = document.querySelector(".hero");
      if (hero) hero.appendChild(button);
      mark();
      film.play().catch(function () {
        /* the browser refused to start it on its own: keep the photograph */
        filmSlot.classList.remove("has-film");
        if (button.parentNode) button.parentNode.removeChild(button);
      });
    }
  }

  /* ---- searching the site -------------------------------------------- */
  var search = document.querySelector("[data-search]");
  if (search) {
    var indexUrl = search.getAttribute("data-search");
    var upToRoot = indexUrl.replace(/assets\/[^/]*$/, "");
    var field = search.querySelector("input[type=search]");
    var results = search.querySelector("[data-results]");
    var counter = search.querySelector(".search-count");
    var word = function (key) { return search.getAttribute("data-msg-" + key) || ""; };
    var index = null;

    var snippet = function (entry, term) {
      var at = term ? entry.x.indexOf(term) : -1;
      if (at < 0) return entry.s;
      var from = Math.max(0, at - 60);
      return (from ? "…" : "") + entry.x.slice(from, from + 170).trim() + "…";
    };

    var show = function (matches, first) {
      results.textContent = "";
      matches.slice(0, 40).forEach(function (entry) {
        var li = document.createElement("li");
        var a = document.createElement("a");
        a.href = upToRoot + entry.u;
        var title = document.createElement("strong");
        title.textContent = entry.t;
        var line = document.createElement("span");
        line.textContent = snippet(entry, first);      /* text, never markup */
        a.appendChild(title);
        a.appendChild(line);
        li.appendChild(a);
        results.appendChild(li);
      });
    };

    var run = function () {
      var query = field.value.trim().toLowerCase();
      if (!index) return;
      if (!query) {
        results.textContent = "";
        counter.textContent = word("start");
        return;
      }
      var terms = query.split(/\s+/).filter(Boolean);
      var matches = index.filter(function (entry) {
        var hay = (entry.t + " " + entry.s + " " + entry.x).toLowerCase();
        return terms.every(function (term) { return hay.indexOf(term) > -1; });
      });
      counter.textContent = matches.length === 0 ? word("empty")
        : matches.length === 1 ? word("one")
        : word("many").replace("%d", matches.length);
      show(matches, terms[0]);
    };

    fetch(indexUrl, { headers: { "Accept": "application/json" } })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        index = data;
        var asked = new URLSearchParams(location.search).get("q");
        if (asked) field.value = asked;
        run();
      })
      .catch(function () { counter.textContent = word("empty"); });

    var typing;
    field.addEventListener("input", function () {
      clearTimeout(typing);
      typing = setTimeout(function () {
        run();
        try {                                   /* a searched page stays linkable */
          var url = field.value.trim()
            ? location.pathname + "?q=" + encodeURIComponent(field.value.trim())
            : location.pathname;
          history.replaceState(null, "", url);
        } catch (e) { /* older browsers simply keep the address */ }
      }, 120);
    });
    search.querySelector("form").addEventListener("submit", function (event) {
      event.preventDefault();
      run();
    });
  }

  /* ---- the cursor ----------------------------------------------------
     A dot that follows exactly and a ring that lags behind it, naming what
     a link would do. Pointer devices only, and never when less motion is
     asked for.                                                            */
  var finePointer = window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (finePointer && !reduced) {
    var dot = document.createElement("div");
    dot.className = "cursor-dot";
    dot.setAttribute("aria-hidden", "true");
    var ring = document.createElement("div");
    ring.className = "cursor-ring";
    ring.setAttribute("aria-hidden", "true");
    document.body.appendChild(dot);
    document.body.appendChild(ring);

    var mouseX = 0, mouseY = 0, ringX = 0, ringY = 0, running = false;
    var words = {
      view: docEl.lang === "ka" ? "ნახვა" : "View",
      open: docEl.lang === "ka" ? "გახსნა" : "Open"
    };

    var frame = function () {
      ringX += (mouseX - ringX) * 0.18;
      ringY += (mouseY - ringY) * 0.18;
      dot.style.transform = "translate(" + mouseX + "px," + mouseY + "px)";
      ring.style.transform = "translate(" + ringX + "px," + ringY + "px)";
      if (Math.abs(mouseX - ringX) > 0.3 || Math.abs(mouseY - ringY) > 0.3) {
        window.requestAnimationFrame(frame);
      } else {
        running = false;
      }
    };

    document.addEventListener("mousemove", function (event) {
      mouseX = event.clientX;
      mouseY = event.clientY;
      document.body.classList.add("has-cursor");
      if (!running) { running = true; window.requestAnimationFrame(frame); }
    }, { passive: true });

    document.addEventListener("mouseleave", function () {
      document.body.classList.remove("has-cursor");
    });

    document.addEventListener("mouseover", function (event) {
      var target = event.target.closest("a, button, summary, .gal-open, input, textarea");
      if (!target) {
        document.body.classList.remove("cursor-active");
        ring.textContent = "";
        return;
      }
      document.body.classList.add("cursor-active");
      ring.textContent = target.closest(".gal-open, .strip-item")
        ? words.view
        : (target.tagName === "A" ? words.open : "");
    });
  }

  /* ---- buttons that lean towards the cursor -------------------------- */
  if (finePointer && !reduced) {
    Array.prototype.forEach.call(document.querySelectorAll(".btn, .link-arrow, .brand-mark"),
      function (el) {
        el.addEventListener("mousemove", function (event) {
          var box = el.getBoundingClientRect();
          var x = (event.clientX - box.left - box.width / 2) * 0.18;
          var y = (event.clientY - box.top - box.height / 2) * 0.22;
          el.style.transform = "translate(" + x.toFixed(2) + "px," + y.toFixed(2) + "px)";
        });
        el.addEventListener("mouseleave", function () { el.style.transform = ""; });
      });
  }

  /* ---- the portrait drifts with the cursor, the words do not ---------- */
  var parallax = document.querySelector("[data-parallax]");
  if (parallax && finePointer && !reduced) {
    var target = parallax.querySelector(".hero-media") || parallax;
    var glow = parallax.querySelector(".hero-glow");
    var ticking = false, px = 0, py = 0;
    window.addEventListener("mousemove", function (event) {
      px = (event.clientX / window.innerWidth - 0.5);
      py = (event.clientY / window.innerHeight - 0.5);
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        ticking = false;
        target.style.transform = "translate3d(" + (px * -14).toFixed(2) + "px," +
          (py * -12).toFixed(2) + "px,0)";
        if (glow) {
          glow.style.transform = "translate3d(" + (px * 26).toFixed(2) + "px," +
            (py * 22).toFixed(2) + "px,0)";
        }
      });
    }, { passive: true });
  }

  /* ---- leaving a page ------------------------------------------------
     A black panel rises, a thin violet line crosses it, the next page
     opens. Half a second, and only between pages of this site.           */
  if (!reduced) {
    var veil = document.createElement("div");
    veil.className = "veil";
    veil.setAttribute("aria-hidden", "true");
    document.body.appendChild(veil);
    window.requestAnimationFrame(function () { veil.classList.add("is-in"); });

    document.addEventListener("click", function (event) {
      var link = event.target.closest("a");
      if (!link || event.metaKey || event.ctrlKey || event.shiftKey || event.button !== 0) return;
      var href = link.getAttribute("href") || "";
      if (!href || href.charAt(0) === "#" || link.target === "_blank" ||
          href.indexOf("mailto:") === 0 || href.indexOf("tel:") === 0) return;
      if (link.origin && link.origin !== location.origin) return;
      if (link.pathname === location.pathname && link.search === location.search) return;
      event.preventDefault();
      veil.classList.remove("is-in");
      veil.classList.add("is-out");
      window.setTimeout(function () { location.href = link.href; }, 380);
    });

    window.addEventListener("pageshow", function (event) {
      if (event.persisted) {
        veil.classList.remove("is-out");
        veil.classList.add("is-in");
      }
    });
  }

  /* ---- remember the reader's language choice ------------------------ */
  try {
    var lang = document.documentElement.lang;
    if (lang) localStorage.setItem("md-lang", lang);
  } catch (e) { /* private mode — nothing to do */ }
})();
