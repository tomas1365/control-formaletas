// Jornada Ext Laboral · Unispan — permite instalar la app y abrirla al instante.
// La pantalla de la app se abre desde la copia guardada en el equipo (no espera al servidor) y se actualiza
// en segundo plano; los datos (/api/) siempre van al servidor.
const CACHE = "hx-v3";
const BASE = ["/", "/logo.jpg", "/icono-192.png", "/icono-512.png", "/manifest.json"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(BASE)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin || u.pathname.startsWith("/api/") || u.pathname === "/salud") return;
  const clave = e.request.mode === "navigate" ? "/" : e.request;
  const red = fetch(e.request).then(r => {
    if (r.ok && r.type === "basic") { const copia = r.clone(); caches.open(CACHE).then(c => c.put(clave, copia)); }
    return r;
  });
  // Copia guardada primero (abre al instante aunque el servidor esté despertando); si no hay copia, la red.
  e.respondWith(caches.match(clave).then(c => c || red).catch(() => red));
  e.waitUntil(red.catch(() => {}));
});
