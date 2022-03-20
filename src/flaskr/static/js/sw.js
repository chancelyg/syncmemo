self.addEventListener("install", (e) => {
    e.waitUntil(
      caches
        .open("chancel-store")
        .then((cache) =>
          cache.addAll([
            "/static/css/mdui.min.css",
            "/static/js/mdui.min.js",
            "/static/js/wangEditor.min.js",
            "/static/js/vue.min.js",
            "/static/fonts/roboto/Roboto-Medium.woff2",
            "/static/fonts/roboto/Roboto-Regular.woff2"
          ])
        )
    );
  });
  
  self.addEventListener("fetch", (e) => {
    e.respondWith(
      caches.match(e.request).then((response) => response || fetch(e.request))
    );
  });
  