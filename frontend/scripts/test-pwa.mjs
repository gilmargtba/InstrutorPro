import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import vm from 'node:vm';

const source = readFileSync(new URL('../public/sw.js', import.meta.url), 'utf8');
const manifest = JSON.parse(readFileSync(new URL('../public/manifest.webmanifest', import.meta.url), 'utf8'));

function worker(fetchResult) {
  const listeners = new Map();
  const stored = new Map();
  const cache = {
    match: async (request) => stored.get(typeof request === 'string' ? request : request.url),
    put: async (request, response) => stored.set(request.url, response),
    add: async (path) => stored.set(path, { offline: true }),
  };
  const context = {
    self: {
      location: { origin: 'https://instrutorprocnh.com.br' },
      clients: { claim: async () => {} },
      addEventListener: (name, callback) => listeners.set(name, callback),
      skipWaiting: () => {},
    },
    caches: {
      open: async () => cache,
      match: cache.match,
      keys: async () => [],
      delete: async () => true,
    },
    fetch: fetchResult,
    URL,
    Set,
    Promise,
  };
  vm.runInNewContext(source, context);
  return { listeners, stored };
}

function dispatchFetch(listeners, path, options = {}) {
  let handled;
  const request = {
    url: `https://instrutorprocnh.com.br${path}`,
    method: options.method || 'GET',
    mode: options.mode || 'same-origin',
    headers: new Headers(options.headers),
  };
  listeners.get('fetch')({ request, respondWith: (response) => { handled = response; }, waitUntil: () => {} });
  return handled;
}

test('manifest provides a standalone app with the existing brand icon', () => {
  assert.equal(manifest.display, 'standalone');
  assert.equal(manifest.scope, '/');
  assert.deepEqual(manifest.icons.map((icon) => icon.sizes), ['192x192', '1024x1024']);
});

test('service worker never handles private requests, APIs or authenticated responses', () => {
  const { listeners } = worker(async () => { throw Error('unexpected fetch'); });
  for (const path of ['/api/v1/session/me/', '/admin/', '/private/cnh.pdf', '/documents/cnh.png', '/app-icon-1024.png?token=secret']) {
    assert.equal(dispatchFetch(listeners, path), undefined, path);
  }
  assert.equal(dispatchFetch(listeners, '/admin/', { mode: 'navigate' }), undefined);
  assert.equal(dispatchFetch(listeners, '/downloads/InstrutorProCNH-android.apk', { mode: 'navigate' }), undefined);
  assert.equal(dispatchFetch(listeners, '/app-icon-1024.png', { headers: { Authorization: 'Bearer secret' } }), undefined);
  assert.equal(dispatchFetch(listeners, '/app-icon-1024.png', { method: 'POST' }), undefined);
});

test('service worker caches only a public static asset and honors no-store', async () => {
  const publicResponse = {
    ok: true, type: 'basic',
    headers: new Headers({ 'Content-Type': 'image/png' }),
    clone() { return this; },
  };
  const { listeners, stored } = worker(async () => publicResponse);
  await dispatchFetch(listeners, '/app-icon-1024.png');
  assert.ok(stored.has('https://instrutorprocnh.com.br/app-icon-1024.png'));

  const blocked = worker(async () => ({
    ...publicResponse,
    headers: new Headers({ 'Content-Type': 'image/png', 'Cache-Control': 'private, no-store' }),
  }));
  await dispatchFetch(blocked.listeners, '/app-icon-1024.png');
  assert.equal(blocked.stored.size, 0);
});

test('navigation always tries the network, then shows only a generic offline page', async () => {
  const { listeners, stored } = worker(async () => { throw Error('offline'); });
  stored.set('/offline.html', { offline: true });
  assert.deepEqual(await dispatchFetch(listeners, '/aluno/painel', { mode: 'navigate' }), { offline: true });
  assert.equal(stored.has('https://instrutorprocnh.com.br/aluno/painel'), false);
});
