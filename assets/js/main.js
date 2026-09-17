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
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });

    nav.addEventListener("click", function (event) {
      if (event.target.closest("a")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && nav.classList.contains("is-open")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
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
      header.classList.toggle("is-scrolled", window.scrollY > 24);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---- reveal sections as they come into view ------------------------
     A plain position check rather than IntersectionObserver: a fast flick
     scroll can move an element past the observer between two computations,
     which would leave that section invisible for good.                     */
  var revealTargets = Array.prototype.slice.call(document.querySelectorAll(
    ".section-head, .pillar, .card, .programme, .honour, .gal-item, .stats li, .timeline li, .split-body, .split-media, .contact-card, .big-quote"
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

  /* ---- the hero photograph drifts slightly behind the words ---------- */
  var heroMedia = document.querySelector(".hero .hero-media");
  if (heroMedia && !reduced) {
    var parallaxQueued = false;
    var moveHero = function () {
      parallaxQueued = false;
      var y = window.scrollY;
      if (y > window.innerHeight * 1.2) return;
      heroMedia.style.transform = "translate3d(0, " + (y * 0.18).toFixed(1) + "px, 0)";
    };
    window.addEventListener("scroll", function () {
      if (!parallaxQueued) { parallaxQueued = true; window.requestAnimationFrame(moveHero); }
    }, { passive: true });
    moveHero();
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
      form.replaceWith(note);
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
          if (!r.ok) throw new Error("rejected");
          form.reset();
          if (counter) counter.textContent = "700";
          tell(say("thanks"), "ok");
        }).catch(function () {
          tell(say("error"), "error");
        }).then(function () {
          button.disabled = false;
        });
      });
    }
  }

  /* ---- light / dark switch ------------------------------------------ */
  var themeButton = document.querySelector(".theme-toggle");
  if (themeButton) {
    var systemDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)");
    var currentTheme = function () {
      return docEl.getAttribute("data-theme") ||
        (systemDark && systemDark.matches ? "dark" : "light");
    };
    themeButton.addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      docEl.setAttribute("data-theme", next);
      try { localStorage.setItem("md-theme", next); } catch (e) { /* private mode */ }
    });
  }

  /* ---- remember the reader's language choice ------------------------ */
  try {
    var lang = document.documentElement.lang;
    if (lang) localStorage.setItem("md-lang", lang);
  } catch (e) { /* private mode — nothing to do */ }
})();
