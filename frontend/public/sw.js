const CACHE_NAME = "finwize-v1";
const STATIC_ASSETS = [
  "/",
  "/index.html",
  "/assets/index.css",
  "/assets/index.js",
];

const API_CACHE = "finwize-api-v1";
const API_CACHE_TTL = 5 * 60 * 1000;

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((k) => k !== CACHE_NAME && k !== API_CACHE).map((k) => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  if (url.pathname.startsWith("/api/")) {
    event.respondWith(networkFirstWithCache(request, API_CACHE, API_CACHE_TTL));
    return;
  }

  if (
    request.destination === "style" ||
    request.destination === "script" ||
    request.destination === "font" ||
    request.destination === "image"
  ) {
    event.respondWith(cacheFirst(request));
    return;
  }

  if (request.mode === "navigate") {
    event.respondWith(networkFirstWithCache(request, CACHE_NAME));
    return;
  }
});

async function cacheFirst(request) {
  const cached = await caches.match(request);
  return cached || fetch(request);
}

async function networkFirstWithCache(request, cacheName, ttl) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      const clone = response.clone();
      const headers = new Headers(clone.headers);
      headers.set("x-cache-timestamp", Date.now().toString());
      cache.put(request, new Response(await clone.blob(), { headers }));
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    if (cached) {
      const timestamp = parseInt(cached.headers.get("x-cache-timestamp") || "0", 10);
      if (ttl && Date.now() - timestamp > ttl) {
        return cached;
      }
      return cached;
    }
    return new Response(JSON.stringify({ error: "offline", message: "You are offline" }), {
      status: 503,
      headers: { "Content-Type": "application/json" },
    });
  }
}
