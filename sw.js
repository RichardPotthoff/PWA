const version = 'v1.0f';
const cacheName = 'my-pwa-cache-' + version;


self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(cacheName).then(function(cache) {
            return cache.addAll([
			    './', // Your start URL
			    './index.html',
			    './manifest.json',
			    './icon-16x16.png',
			    './icon-32x32.png',
			    './icon-152x152.png', // Add this line
			    './icon-180x180.png', // Add this line
			    './icon-192x192.png',
			    './icon-512x512.png',
			    // Other assets
			]);
        })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request).then(function(response) {
            return response || fetch(event.request).then(function(response) {
                // Cache the new response for future offline use
                return caches.open(cacheName).then(function(cache) {
                    cache.put(event.request, response.clone());
                    return response;
                });
            });
        }).catch(function() {
            // If both fail, you might want to return a fallback offline page
            return caches.match('./index.html'); // Assuming you have an offline fallback page
        })
    );
});

self.addEventListener('activate', function(event) {
    let cacheWhitelist = [cacheName];
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(name) {
                    if (cacheWhitelist.indexOf(name) === -1) {
                        return caches.delete(name);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Optional: Add message event listener for manual update checks
self.addEventListener('message', function(event) {
    if (event.data.type === 'CHECK_FOR_UPDATE') {
        self.skipWaiting(); // This starts the new service worker if one is waiting
    }
});