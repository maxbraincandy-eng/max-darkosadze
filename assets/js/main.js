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

  /* ---- gallery lightbox ---------------------------------------------- */
  var gallery = document.querySelector(".gallery");
  if (gallery) {
    var box = null;

    var close = function () {
      if (!box) return;
      box.classList.remove("is-open");
      var node = box;
      box = null;
      window.setTimeout(function () { node.remove(); }, 250);
    };

    gallery.addEventListener("click", function (event) {
      var img = event.target.closest(".gal-item .img-slot:not(.is-missing) img");
      if (!img) return;
      var caption = img.closest("figure").querySelector("figcaption");
      box = document.createElement("div");
      box.className = "lightbox";
      box.setAttribute("role", "dialog");
      box.setAttribute("aria-modal", "true");

      var big = document.createElement("img");
      big.src = img.currentSrc || img.src;
      big.alt = img.alt;
      box.appendChild(big);

      if (caption) {
        var cap = document.createElement("figcaption");
        cap.textContent = caption.textContent;
        box.appendChild(cap);
      }

      var button = document.createElement("button");
      button.className = "lightbox-close";
      button.type = "button";
      button.setAttribute("aria-label", docEl.lang === "ka" ? "დახურვა" : "Close");
      button.innerHTML = "&times;";
      box.appendChild(button);

      box.addEventListener("click", function (e) {
        if (e.target === box || e.target === button) close();
      });
      document.body.appendChild(box);
      window.requestAnimationFrame(function () { box.classList.add("is-open"); });
      button.focus();
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") close();
    });
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
