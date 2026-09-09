/* EcoFinwize service worker */
const CACHE_NAME = "ecofinwize-shell-v1";
const PRECACHE_URLS = [
  "/",
  "/index.html",
  "/offline.html",
  "/manifest.webmanifest",
  "/favicon.png",
  "/icons/icon-192.png",
  "/icons/icon-512.png",
  "/icons/icon-maskable-512.png",
  "/icons/apple-touch-icon.png",
];

// Public, non-user-specific GET endpoints that are safe to serve stale-offline.
// Anything with an Authorization header or containing user data is NEVER cached.
const PUBLIC_API_PATHS = [
  "/articles",
  "/news",
  "/blog",
  "/markets",
  "/fundamentals",
  "/health",
];

const PUBLIC_API_CACHE = "ecofinwize-public-api-v1";
const PUBLIC_API_TTL = 5 * 60 * 1000; // 5 minutes

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .catch(() => {})
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys
            .filter((k) => k !== CACHE_NAME && k !== PUBLIC_API_CACHE)
            .map((k) => caches.delete(k))
        )
      )
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET" && request.method !== "HEAD") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  // Never intercept authenticated / private requests.
  if (request.headers.has("authorization")) return;

  // API: only safe public GET endpoints, with a short TTL.
  if (url.pathname.startsWith("/api/")) {
    if (PUBLIC_API_PATHS.some((p) => url.pathname.startsWith(`/api/v1${p}`))) {
      event.respondWith(networkFirstWithPublicCache(request, PUBLIC_API_CACHE, PUBLIC_API_TTL));
    } else {
      event.respondWith(networkFirst(request, null));
    }
    return;
  }

  // Vite emits content-hashed assets -> cache-first is safe.
  if (
    request.destination === "script" ||
    request.destination === "style" ||
    request.destination === "font" ||
    request.destination === "image"
  ) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // Navigations: network-first, fall back to the cached shell or offline page.
  if (request.mode === "navigate") {
    event.respondWith(networkFirstNavigate(request));
    return;
  }

  event.respondWith(cacheFirst(request));
});

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return cached;
  }
}

async function networkFirst(request, cacheName) {
  try {
    const response = await fetch(request);
    return response;
  } catch {
    if (cacheName) {
      const cached = await caches.match(request);
      if (cached) return cached;
    }
    return offlineResponse();
  }
}

async function networkFirstWithPublicCache(request, cacheName, ttlMs) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      const headers = new Headers(response.headers);
      headers.set("x-ecofinwize-cache", Date.now().toString());
      cache.put(
        request,
        new Response(await response.clone().blob(), { status: response.status, statusText: response.statusText, headers })
      );
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    if (cached) {
      const ts = Number(cached.headers.get("x-ecofinwize-cache") || 0);
      const stale = Date.now() - ts > ttlMs;
      return new Response(cached.body, {
        status: stale ? 504 : cached.status,
        statusText: stale ? "Gateway Timeout" : cached.statusText,
        headers: { "Content-Type": "application/json", "X-EcoFinwize-Offline": "true" },
      });
    }
    return offlineResponse();
  }
}

async function networkFirstNavigate(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put("/index.html", response.clone());
    }
    return response;
  } catch (e) {
    const shell = await caches.match("/index.html");
    if (shell) return shell;
    const offline = await caches.match("/offline.html");
    if (offline) return offline;
    return offlineResponse();
  }
}

function offlineResponse() {
  return new Response(
    JSON.stringify({ error: "offline", message: "You are offline. Connect to the internet and try again." }),
    {
      status: 503,
      headers: { "Content-Type": "application/json", "X-EcoFinwize-Offline": "true" },
    }
  );
}