/* Max Darkosadze — small progressive enhancements. No dependencies. */
(function () {
  "use strict";

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
  var hint = document.documentElement.getAttribute("data-img-missing") ||
    (document.documentElement.lang === "ka"
      ? "ფოტოს ადგილი — ჩააგდეთ სურათი მისამართზე:"
      : "Photo slot — place your image at:");

  function markMissing(img) {
    var slot = img.closest(".img-slot");
    if (!slot || slot.classList.contains("is-missing")) return;
    slot.classList.add("is-missing");
    var note = document.createElement("span");
    note.className = "slot-hint";
    note.appendChild(document.createTextNode(hint));
    var code = document.createElement("code");
    code.textContent = slot.getAttribute("data-path") || "";
    note.appendChild(code);
    slot.appendChild(note);
  }

  Array.prototype.forEach.call(document.querySelectorAll("img[data-slot]"), function (img) {
    if (img.complete) {
      if (!img.naturalWidth) markMissing(img);
    } else {
      img.addEventListener("error", function () { markMissing(img); });
    }
  });

  /* ---- remember the reader's language choice ------------------------ */
  try {
    var lang = document.documentElement.lang;
    if (lang) localStorage.setItem("md-lang", lang);
  } catch (e) { /* private mode — nothing to do */ }
})();
