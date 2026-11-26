// Jornada Ext Laboral · Unispan — permite instalar la app y abrirla rápido.
// La pantalla se pide primero al servidor; si en 5 segundos no responde (por ejemplo, porque está despertando),
// se abre la copia guardada en el equipo. Los datos (/api/) siempre van al servidor.
const CACHE = "hx-v25";
const BASE = ["/", "/logo.jpg", "/icono-192.png", "/icono-512.png", "/manifest.json"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(BASE)).catch(() => {}).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin || u.pathname.startsWith("/api/") || u.pathname === "/salud") return;
  const clave = e.request.mode === "navigate" ? "/" : e.request;
  const red = fetch(e.request).then(r => {
    if (r.ok && r.type === "basic" && (r.headers.get("content-type") || "").match(/html|image|json|javascript/)) {
      const copia = r.clone(); caches.open(CACHE).then(c => c.put(clave, copia));
    }
    return r;
  });
  const espera = new Promise(res => setTimeout(res, 5000)).then(() => caches.match(clave));
  e.respondWith(Promise.race([red.catch(() => caches.match(clave)), espera.then(c => c || red)]).then(r => r || red));
  e.waitUntil(red.catch(() => {}));
});
