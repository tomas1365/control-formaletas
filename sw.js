const VERSION="unispan-v21-1";
const CORE=["./","./index.html","./manifest.webmanifest","./icons/icon-192.png","./icons/icon-512.png","./icons/apple-touch-icon.png"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(VERSION).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()));});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==VERSION).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener("fetch",e=>{
  const req=e.request, url=new URL(req.url);
  if(req.method!=="GET") return;                       // subidas/anotaciones: siempre red
  if(url.origin!==location.origin){
    // Solo librerías estáticas de CDN se cachean; APIs (Roboflow, Anthropic, etc.) van directo a red
    if(url.hostname==="cdnjs.cloudflare.com"||url.hostname==="cdn.jsdelivr.net"||url.hostname==="fonts.googleapis.com"||url.hostname==="fonts.gstatic.com"){
      e.respondWith(caches.match(req).then(h=>h||fetch(req).then(r=>{const c=r.clone();caches.open(VERSION).then(ca=>ca.put(req,c));return r;})));
    }
    return;
  }
  if(req.mode==="navigate"){                           // HTML: red primero, caché si no hay conexión
    e.respondWith(fetch(req).then(r=>{const c=r.clone();caches.open(VERSION).then(ca=>ca.put("./index.html",c));return r;}).catch(()=>caches.match("./index.html")));
    return;
  }
  e.respondWith(caches.match(req).then(h=>{const n=fetch(req).then(r=>{const c=r.clone();caches.open(VERSION).then(ca=>ca.put(req,c));return r;}).catch(()=>h);return h||n;}));
});
