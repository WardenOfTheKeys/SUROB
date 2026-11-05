// Offline copy of the SUROB MSI calculator (Version 3).
// Same-origin files only. Esri map pictures and the live NWS forecast always go to the
// network; without them the app uses its packaged NOAA data.
// Bump CACHE when the list of files changes.
const CACHE = 'surob-v3-1';
const FILES = ['./', 'index.html', 'conditions-data.js', 'manifest.webmanifest', 'icon.svg', 'icon-192.png', 'icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith('surob-v3-') && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

// Network first, with a short wait: a connected device gets the newest app and NOAA data
// (and the copy is updated), a disconnected or very slow one opens the saved copy.
self.addEventListener('fetch', e => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== self.location.origin) return;
  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const net = fetch(req).then(res => { if (res.ok) cache.put(req, res.clone()); return res; });
    net.catch(() => {});  // a late network failure after the cache answered is expected offline
    try {
      return await Promise.race([net, new Promise((_, no) => setTimeout(() => no(new Error('slow')), 4000))]);
    } catch (err) {
      const hit = await cache.match(req, { ignoreSearch: true }) || (req.mode === 'navigate' && await cache.match('index.html'));
      if (hit) return hit;
      return net.catch(() => Response.error());
    }
  })());
});
