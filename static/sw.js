// Service Worker for خدمة المواطنين
const CACHE_NAME = 'citizen-service-v1';
const urlsToCache = [
    '/',
    '/static/css/about-page.css',
    '/static/js/gallery.js',
    '/static/css/all.min.css',
    '/static/images/صورة واتساب بتاريخ 1447-05-16 في 21.18.45_7574d868.jpg',
    '/static/images/133535127_4804186402985532_4702410038579466158_n.jpg',
    '/static/images/489820290_28999004809743687_1206268839315847125_n.jpg',
    '/static/images/صورة واتساب بتاريخ 1447-05-16 في 21.18.45_7574d868.jpg',
    '/static/images/513855479_30109175582059932_767779498495140005_n.jpg',
    '/static/images/535711159_30846120211698795_5392745618849719853_n.jpg',
    '/static/images/صورة واتساب بتار1447-05-16 في 21.51.05_b5877a5f.jpg',
    '/static/images/صورة واتساب بتاريخ 1447-05-02 في 17.01.35_1309e0af.jpg'
];

// Install event
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch event
self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // Cache hit - return response
                if (response) {
                    return response;
                }
                return fetch(event.request);
            }
        )
    );
});

// Activate event
self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});