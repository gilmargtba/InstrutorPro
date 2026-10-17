// Cache only the public, versioned Angular assets and a generic offline page.
// Never cache navigations, API responses, uploaded media, identity documents or sessions.
const CACHE_NAME = 'instrutorpro-public-v1';
const OFFLINE_PAGE = '/offline.html';
const PUBLIC_FILES = new Set(['/logo-cnh.svg', '/app-icon-192.png', '/app-icon-1024.png', '/manifest.webmanifest', OFFLINE_PAGE]);
const HASHED_ASSET = /^\/(?:main|polyfills|styles|chunk)-[A-Za-z0-9]+\.(?:js|css)$/;
const PRIVATE_PATH = /^\/(?:api|admin|downloads|media|documents|uploads|private|private_documents|quarantine|professional-documents)(?:\/|$)/;

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.add(OFFLINE_PAGE)));
});

self.addEventListener('activate', (event) => {
  event.waitUntil(Promise.all([
    caches.keys().then((keys) => Promise.all(keys.filter((key) => key.startsWith('instrutorpro-public-') && key !== CACHE_NAME).map((key) => caches.delete(key)))),
    self.clients.claim(),
  ]));
});

self.addEventListener('message', (event) => {
  if (event.data?.type === 'SKIP_WAITING') self.skipWaiting();
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET' || request.headers.has('Authorization')) return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  if (url.search) return;
  if (PRIVATE_PATH.test(url.pathname)) return;

  if (request.mode === 'navigate') {
    event.respondWith(fetch(request).catch(() => caches.match(OFFLINE_PAGE)));
    return;
  }

  if (!PUBLIC_FILES.has(url.pathname) && !HASHED_ASSET.test(url.pathname)) return;
  event.respondWith(caches.match(request).then((cached) => cached || fetch(request).then((response) => {
    const policy = response.headers.get('Cache-Control') || '';
    const type = response.headers.get('Content-Type') || '';
    const allowedType = /(?:javascript|css|image\/png|image\/svg\+xml|application\/manifest\+json|text\/html)/i.test(type);
    if (response.ok && response.type === 'basic' && allowedType && !/(?:private|no-store)/i.test(policy)) {
      const copy = response.clone();
      event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.put(request, copy)));
    }
    return response;
  })));
});
