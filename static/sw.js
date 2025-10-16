const CACHE_NAME = 'citizen-service-v1';
const urlsToCache = [
  '/',
  '/static/css/bootstrap.rtl.min.css',
  '/static/js/bootstrap.bundle.min.js',
  '/static/images/صورة اللوجو الخاص بالنيف بار.jpg',
  '/chat/',
  '/requests/',
  '/achievements/',
  '/about/'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});

