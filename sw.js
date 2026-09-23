/* Built by build.py — do not edit by hand. */
var VERSION = "2026-09-23-1790176499";
var SHELL = [
  "/ka/index.html",
  "/en/index.html",
  "/404.html",
  "/assets/css/style.css",
  "/assets/js/main.js",
  "/assets/fonts/noto-serif-georgian.woff2",
  "/assets/fonts/noto-sans-georgian.woff2",
  "/assets/icons/icon-192.png"
];

self.addEventListener("install", function (event) {
  self.skipWaiting();
  event.waitUntil(caches.open(VERSION).then(function (cache) {
    /* one missing file must not sink the whole install */
    return Promise.all(SHELL.map(function (url) {
      return cache.add(new Request(url, { cache: "reload" })).catch(function () {});
    }));
  }));
});

self.addEventListener("activate", function (event) {
  event.waitUntil(caches.keys().then(function (names) {
    return Promise.all(names.map(function (name) {
      return name === VERSION ? null : caches.delete(name);
    }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener("message", function (event) {
  /* an escape hatch: postMessage("unregister") and the worker steps aside */
  if (event.data === "unregister") {
    self.registration.unregister().then(function () {
      return caches.keys().then(function (names) {
        return Promise.all(names.map(function (n) { return caches.delete(n); }));
      });
    });
  }
});

self.addEventListener("fetch", function (event) {
  var request = event.request;
  if (request.method !== "GET") return;
  var url = new URL(request.url);
  if (url.origin !== location.origin) return;
  if (url.pathname.indexOf("/api/") === 0 || url.pathname === "/admin") return;

  var wantsPage = request.mode === "navigate" ||
    (request.headers.get("accept") || "").indexOf("text/html") > -1;

  if (wantsPage) {
    event.respondWith(
      fetch(request).then(function (response) {
        var copy = response.clone();
        caches.open(VERSION).then(function (cache) { cache.put(request, copy); });
        return response;
      }).catch(function () {
        return caches.match(request).then(function (hit) {
          return hit || caches.match("/ka/index.html") || caches.match("/404.html");
        });
      })
    );
    return;
  }

  /* the stylesheet and the script describe the markup of one deploy: serving an
     old one with a new page looks broken, so they follow the network first,
     exactly like a page, and fall back to the cache only when there is none. */
  if (/\.(?:css|js|json)$/.test(url.pathname)) {
    event.respondWith(
      fetch(request).then(function (response) {
        if (response && response.status === 200) {
          var fresh = response.clone();
          caches.open(VERSION).then(function (cache) { cache.put(request, fresh); });
        }
        return response;
      }).catch(function () { return caches.match(request); })
    );
    return;
  }

  if (/\.(?:woff2|jpg|jpeg|png|svg|webp|avif|mp4|webm|ico)$/.test(url.pathname)) {
    event.respondWith(
      caches.match(request).then(function (hit) {
        var live = fetch(request).then(function (response) {
          if (response && response.status === 200) {
            var copy = response.clone();
            caches.open(VERSION).then(function (cache) { cache.put(request, copy); });
          }
          return response;
        }).catch(function () { return hit; });
        return hit || live;
      })
    );
  }
});
