// v18 — اصلاحات وتحسينات
const CACHE_NAME = 'saif-seha-musaed-v18';

// Only truly static binary assets worth caching
const STATIC_ASSETS = [
  'manifest.webmanifest',
  'favicon.svg',
  'maskable-icon.svg',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) =>
      cache.addAll(
        STATIC_ASSETS.map(
          (a) => new URL(a, self.registration.scope).toString()
        )
      )
    )
  );
  // Take control immediately — don't wait for old SW clients to close
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  // Delete ALL old caches (v11 / v12 / v13 / anything else)
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
      )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // ── HTML navigation: ALWAYS network — never serve stale HTML from cache ──
  if (
    event.request.mode === 'navigate' ||
    event.request.headers.get('accept')?.includes('text/html')
  ) {
    event.respondWith(
      fetch(event.request).catch(() =>
        // Offline fallback: serve the root SPA shell
        caches.match(new URL('', self.registration.scope).toString())
      )
    );
    return;
  }

  // ── JS / CSS: let the browser's HTTP cache decide (files are content-hashed) ──
  const ext = url.pathname.slice(url.pathname.lastIndexOf('.'));
  if (ext === '.js' || ext === '.css') return;

  // ── Static binary assets: cache-first ──
  event.respondWith(
    caches.match(event.request).then(
      (cached) =>
        cached ??
        fetch(event.request).then((res) => {
          if (res.ok) {
            const copy = res.clone();
            caches.open(CACHE_NAME).then((c) => c.put(event.request, copy));
          }
          return res;
        })
    )
  );
});
