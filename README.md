<!DOCTYPE html>
<html lang="es"><head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html-to-image/1.11.13/html-to-image.min.js" integrity="sha512-iZ2ORl595Wx6miw+GuadDet4WQbdSWS3JLMoNfY8cRGoEFy6oT3G9IbcrBeL6AfkgpA51ETt/faX6yLV+/gFJg==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
  
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<meta name="theme-color" content="#0a1628">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<title>UNISPAN — Dataset v16</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;touch-action:manipulation;}
:root{--bg:#0a1628;--surface:#102a43;--surface2:#1a3a5c;--border:rgba(99,125,152,0.25);--amber:#f59e0b;--steel:#627d98;--text:#e2e8f0;--text2:#94a3b8;--ok:#22c55e;--danger:#ef4444;--radius:14px;}
body{background:var(--bg);color:var(--text);font-family:-apple-system,'Inter',sans-serif;min-height:100dvh;display:flex;flex-direction:column;}
header{background:rgba(10,22,40,.95);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);padding:14px 16px;display:flex;align-items:center;gap:12px;position:sticky;top:0;z-index:100;}
.logo{width:36px;height:36px;background:var(--amber);border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:16px;color:#0a1628;flex-shrink:0;}
header h1{font-size:15px;font-weight:700;}
header p{font-size:11px;color:var(--steel);}
.tabs{display:flex;border-bottom:1px solid var(--border);background:var(--bg);position:sticky;top:64px;z-index:99;}
.tab{flex:1;padding:12px 8px;font-size:12px;font-weight:600;text-align:center;color:var(--steel);border-bottom:2px solid transparent;cursor:pointer;transition:all .15s;}
.tab.active{color:var(--amber);border-bottom-color:var(--amber);}
main{flex:1;padding:14px;display:flex;flex-direction:column;gap:12px;}
.page{display:none;flex-direction:column;gap:12px;}
.page.active{display:flex;}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:14px;}
.card-title{font-size:11px;font-weight:700;color:var(--steel);text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px;}
label{font-size:13px;color:var(--text2);display:block;margin-bottom:4px;}
input,select{width:100%;background:var(--bg);border:1px solid var(--border);border-radius:10px;padding:10px 12px;color:var(--text);font-size:14px;margin-bottom:10px;outline:none;-webkit-appearance:none;}
input:focus,select:focus{border-color:var(--amber);}
input[type="file"]{display:none;}
input[type="password"]{letter-spacing:2px;}
.tool-bar{display:flex;gap:8px;margin-bottom:10px;}
.tool-btn{flex:1;padding:10px 8px;border-radius:10px;border:1.5px solid var(--border);background:var(--bg);color:var(--text2);font-size:12px;font-weight:600;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:4px;transition:all .15s;}
.tool-btn.active{border-color:var(--amber);background:rgba(245,158,11,.1);color:var(--amber);}
.tool-icon{font-size:20px;}
.tool-hint{font-size:10px;color:var(--steel);text-align:center;margin-bottom:6px;padding:6px 10px;background:rgba(245,158,11,.06);border-radius:8px;}
.zoom-viewport{position:relative;overflow:hidden;border-radius:12px;background:#000;touch-action:none;user-select:none;}
.bbox-wrap{position:relative;transform-origin:0 0;transition:transform .05s linear;touch-action:none;user-select:none;}
.bbox-img{width:100%;display:block;user-select:none;-webkit-user-drag:none;pointer-events:none;}
#bbox-canvas{position:absolute;inset:0;width:100%;height:100%;touch-action:none;}
.capture-zone{border:2px dashed var(--border);border-radius:var(--radius);min-height:160px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;cursor:pointer;transition:border-color .2s;}
.capture-zone.has-img{display:none;}
.zoom-bar{display:flex;gap:6px;margin-top:8px;align-items:center;flex-wrap:wrap;}
.zoom-btn{background:var(--bg);border:1.5px solid var(--border);color:var(--text);border-radius:8px;padding:7px 11px;font-size:14px;font-weight:700;cursor:pointer;min-width:38px;}
.zoom-btn:active{background:var(--surface2);}
.zoom-lbl{font-size:11px;color:var(--steel);font-family:monospace;}
.zoom-hint{font-size:10px;color:var(--steel);flex:1;text-align:right;}
.blur-warn{background:rgba(239,68,68,.12);border:1.5px solid rgba(239,68,68,.4);color:#fca5a5;padding:9px 11px;border-radius:10px;font-size:12px;margin-top:8px;display:flex;align-items:center;gap:8px;}
.blur-warn.ok{background:rgba(34,197,94,.1);border-color:rgba(34,197,94,.3);color:#86efac;}
.blur-warn .x{margin-left:auto;cursor:pointer;font-size:16px;}
.blur-warn-discard{cursor:pointer;text-decoration:underline;font-weight:700;white-space:nowrap;}
.stat-row{display:flex;justify-content:space-between;align-items:center;padding:7px 10px;background:var(--bg);border-radius:8px;font-size:12px;margin-bottom:4px;}
.stat-code{font-family:monospace;font-weight:700;color:var(--text);}
.stat-count{font-family:monospace;font-weight:700;color:var(--amber);}
.stat-count.low{color:#fca5a5;}
.stat-count.ok{color:var(--ok);}
.stat-bar{height:4px;background:var(--bg);border-radius:99px;overflow:hidden;margin-top:3px;}
.stat-bar-fill{height:100%;background:var(--amber);border-radius:99px;}
.poly-toolbar{display:flex;gap:6px;margin-top:8px;}
.anno-list{display:flex;flex-direction:column;gap:6px;margin-top:10px;}
.anno-item{display:flex;align-items:center;gap:8px;padding:8px 10px;border-radius:10px;border:1.5px solid var(--border);background:var(--bg);font-size:12px;flex-wrap:wrap;}
.anno-color{width:14px;height:14px;border-radius:4px;flex-shrink:0;}
.anno-label{flex:1;font-family:monospace;font-weight:700;min-width:0;}
.anno-type{font-size:10px;color:var(--steel);background:var(--surface);border-radius:5px;padding:2px 6px;}
.anno-check{font-size:18px;cursor:pointer;}
.anno-del{cursor:pointer;font-size:16px;color:var(--steel);}
.quick-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:5px;margin-bottom:6px;}
.quick-btn{background:var(--bg);border:1.5px solid var(--border);border-radius:8px;padding:7px 4px;color:var(--text2);font-size:10px;font-weight:600;text-align:center;cursor:pointer;transition:all .15s;}
.quick-btn.active{background:rgba(245,158,11,.15);border-color:var(--amber);color:var(--amber);}
.prog-wrap{background:var(--bg);border-radius:99px;height:5px;overflow:hidden;display:none;margin-top:10px;}
.prog-wrap.show{display:block;}
.prog-bar{height:100%;background:var(--amber);border-radius:99px;transition:width .4s;width:0%;}
.btn-row{display:flex;gap:8px;}
.btn{flex:1;padding:13px;border-radius:12px;font-size:13px;font-weight:700;cursor:pointer;border:none;display:flex;align-items:center;justify-content:center;gap:6px;transition:opacity .15s,transform .1s;-webkit-tap-highlight-color:transparent;}
.btn:active{transform:scale(.97);}
.btn:disabled{opacity:.4;cursor:not-allowed;}
.btn-cam{background:var(--surface);color:var(--text);border:1.5px solid var(--border);}
.btn-up{background:var(--amber);color:#0a1628;}
.btn-up.loading{background:#b45309;}
.btn-sm{padding:8px 12px;font-size:12px;border-radius:9px;flex:none;}
.btn-danger{background:rgba(239,68,68,.15);color:var(--danger);border:1.5px solid rgba(239,68,68,.3);}
.btn-ok{background:rgba(34,197,94,.15);color:var(--ok);border:1.5px solid rgba(34,197,94,.3);}
.btn-ghost{background:var(--surface);color:var(--text2);border:1.5px solid var(--border);}
.btn-amber{background:rgba(245,158,11,.15);color:var(--amber);border:1.5px solid rgba(245,158,11,.3);}
.counter{display:flex;gap:8px;}
.counter-item{flex:1;background:var(--bg);border-radius:10px;padding:10px;text-align:center;}
.counter-num{font-size:22px;font-weight:800;color:var(--amber);}
.counter-lbl{font-size:10px;color:var(--steel);margin-top:1px;}
.log-list{display:flex;flex-direction:column;gap:6px;}
.log-item{background:var(--bg);border-radius:10px;padding:10px;border:1.5px solid transparent;}
.log-item.error{border-color:rgba(239,68,68,.3);}
.log-header{display:flex;align-items:center;gap:10px;}
.log-thumb{width:48px;height:48px;border-radius:8px;object-fit:cover;flex-shrink:0;}
.log-info{flex:1;min-width:0;}
.log-name{font-weight:700;color:var(--text);font-family:monospace;font-size:13px;}
.log-meta{color:var(--steel);margin-top:2px;font-size:11px;}
.log-annos{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px;}
.log-anno-tag{padding:3px 8px;border-radius:6px;font-size:10px;font-weight:700;font-family:monospace;}
.log-actions{display:flex;flex-direction:column;align-items:center;gap:4px;flex-shrink:0;}
.cat-search{position:relative;margin-bottom:8px;}
.cat-search input{margin-bottom:0;padding-left:36px;}
.cat-search .ico{position:absolute;left:12px;top:50%;transform:translateY(-50%);font-size:14px;}
.cat-families{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px;}
.fam-btn{padding:5px 12px;border-radius:99px;font-size:11px;font-weight:700;border:1.5px solid var(--border);color:var(--steel);cursor:pointer;transition:all .15s;}
.fam-btn.active{background:rgba(245,158,11,.15);border-color:var(--amber);color:var(--amber);}
.cat-list{max-height:220px;overflow-y:auto;display:flex;flex-direction:column;gap:4px;}
.cat-item{display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:var(--bg);border-radius:10px;cursor:pointer;border:1.5px solid transparent;}
.cat-item .ci-code{font-weight:700;font-size:13px;font-family:monospace;color:var(--amber);}
.cat-item .ci-spec{font-size:11px;color:var(--steel);margin-top:2px;}
.ref-grid{display:flex;flex-direction:column;gap:6px;}
.ref-card{background:var(--bg);border-radius:10px;padding:12px;display:flex;align-items:center;gap:10px;}
.ref-fam{width:36px;height:36px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:11px;flex-shrink:0;}
.ref-fam.PM{background:rgba(59,130,246,.15);color:#60a5fa;}
.ref-fam.PB{background:rgba(168,85,247,.15);color:#c084fc;}
.ref-fam.EI{background:rgba(245,158,11,.15);color:var(--amber);}
.ref-fam.EE{background:rgba(34,197,94,.15);color:var(--ok);}
.ref-info{flex:1;min-width:0;}
.ref-code{font-family:monospace;font-weight:700;font-size:13px;}
.ref-spec{font-size:11px;color:var(--steel);margin-top:2px;}
.ref-copy{font-size:20px;cursor:pointer;padding:4px;}
.modal-bg{display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:200;align-items:flex-end;}
.modal-bg.show{display:flex;}
.modal{background:var(--surface);border-radius:20px 20px 0 0;padding:20px 16px 32px;width:100%;max-height:85vh;overflow-y:auto;}
.modal-title{font-size:15px;font-weight:700;margin-bottom:14px;display:flex;justify-content:space-between;align-items:center;}
.modal-close{font-size:22px;cursor:pointer;color:var(--steel);}
.review-img-wrap{position:relative;border-radius:12px;overflow:hidden;background:#000;margin-bottom:12px;}
.review-img{width:100%;display:block;}
#review-canvas{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;}
.review-annos{display:flex;flex-direction:column;gap:6px;margin-bottom:14px;}
.review-anno{display:flex;align-items:center;gap:10px;padding:10px 12px;background:var(--bg);border-radius:10px;border:1.5px solid transparent;}
.review-anno.approved{border-color:var(--ok);}
.review-anno.rejected{border-color:var(--danger);opacity:.5;}
.review-check{font-size:22px;cursor:pointer;flex-shrink:0;}
.toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%) translateY(80px);background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:11px 18px;font-size:13px;font-weight:600;transition:transform .3s;z-index:500;white-space:nowrap;box-shadow:0 8px 32px rgba(0,0,0,.4);}
.toast.show{transform:translateX(-50%) translateY(0);}
.toast.ok{border-color:var(--ok);color:var(--ok);}
.toast.err{border-color:var(--danger);color:var(--danger);}
.float-panel{position:fixed;top:80px;right:10px;z-index:350;background:var(--surface);border:1.5px solid var(--amber);border-radius:12px;padding:0;width:260px;max-width:92vw;box-shadow:0 8px 32px rgba(0,0,0,.5);user-select:none;}
.float-panel .fp-head{display:flex;align-items:center;gap:6px;padding:8px 10px;background:rgba(245,158,11,.15);border-radius:12px 12px 0 0;cursor:grab;font-size:12px;font-weight:700;color:var(--amber);}
.float-panel .fp-head:active{cursor:grabbing;}
.float-panel .fp-body{padding:10px 12px 12px;}
.float-panel.min .fp-body{display:none;}
.float-panel .fp-btn{background:transparent;border:none;color:var(--amber);cursor:pointer;font-size:14px;padding:2px 6px;border-radius:6px;}
.float-panel .fp-btn:hover{background:rgba(245,158,11,.2);}
.slider-row{display:flex;align-items:center;gap:8px;margin:6px 0;}
.slider-row label{flex:0 0 78px;font-size:11px;color:var(--steel);margin:0;}
.slider-row input[type=range]{flex:1;margin:0;padding:0;background:transparent;}
.slider-row .val{font-size:11px;font-family:monospace;color:var(--amber);min-width:36px;text-align:right;}
.corner-grid{display:grid;grid-template-columns:1fr 1fr;gap:4px;margin:6px 0;}
.corner-btn{padding:6px;border-radius:6px;border:1.5px solid var(--border);background:var(--bg);color:var(--text2);font-size:11px;font-weight:600;cursor:pointer;}
.corner-btn.active{border-color:var(--amber);background:rgba(245,158,11,.15);color:var(--amber);}
/* SAM overlay highlight */
.sam-highlight-ring{position:absolute;pointer-events:none;border:3px solid var(--amber);border-radius:50%;transform:translate(-50%,-50%);animation:samPulse .5s ease-out forwards;}
@keyframes samPulse{0%{opacity:1;width:24px;height:24px;}100%{opacity:0;width:80px;height:80px;}}
</style>
</head>
<body id="artifacts-component-root-html">
<header>
  <div class="logo">U</div>
  <div style="flex:1"><h1>UNISPAN Dataset v16</h1><p>SAM robusto · Auto-conteo de arrumes · Memoria</p></div>
  <button class="btn btn-sm" style="background:rgba(255,255,255,.1);color:#fff;border:1px solid rgba(255,255,255,.2);flex:none;padding:10px 14px" onclick="downloadApp()">⬇ Descargar</button>
</header>
<div class="tabs">
  <div class="tab active" onclick="switchTab('captura')">📸 Captura</div>
  <div class="tab" onclick="switchTab('historial')">📋 Historial</div>
  <div class="tab" onclick="switchTab('catalogo')">📖 Catálogo</div>
  <div class="tab" onclick="switchTab('experto')">🎓 Experto</div>
</div>
<main>
<div class="page active" id="page-captura">
  <div class="counter">
    <div class="counter-item"><div class="counter-num" id="cnt-session">0</div><div class="counter-lbl">Sesión</div></div>
    <div class="counter-item"><div class="counter-num" id="cnt-total">0</div><div class="counter-lbl">Total</div></div>
    <div class="counter-item"><div class="counter-num" id="cnt-ok" style="color:var(--ok)">0</div><div class="counter-lbl">Exitosas</div></div>
  </div>
  <div class="card">
    <div class="card-title">⚙️ Configuración Roboflow (opcional)</div>
    <label>API Key Roboflow <span style="color:var(--steel);font-size:10px">(solo para subir al dataset)</span></label>
    <input type="password" id="api-key" placeholder="rf_xxxxxxxxxxxxxx (opcional)" autocomplete="off">
    <label>Split destino</label>
    <select id="split"><option value="train">Train</option><option value="valid">Valid</option><option value="test">Test</option></select>
  </div>
  <div class="card">
    <div class="card-title">🏷️ Clase activa</div>
    <div id="recientes-wrap" style="display:none">
      <div style="font-size:11px;color:var(--steel);margin-bottom:6px">Recientes:</div>
      <div class="quick-grid" id="recientes-grid"></div>
    </div>
    <div class="btn-row" style="margin-bottom:8px">
      <button class="btn btn-ghost btn-sm" onclick="openCatModal()">📖 Catálogo</button>
      <input type="text" id="clase-custom" placeholder="ej. PM-2400x600" style="margin-bottom:0;flex:1" oninput="onCustomInput(this.value)">
    </div>
    <div id="current-clase-display" style="display:none;padding:8px 12px;background:rgba(245,158,11,.1);border:1px solid rgba(245,158,11,.3);border-radius:8px;font-family:monospace;font-weight:700;color:var(--amber);font-size:14px"></div>
  </div>
  <div class="card">
    <div class="card-title">🛠️ Herramienta de anotación</div>
    <div class="tool-bar" style="flex-wrap:wrap">
      <div class="tool-btn active" id="tool-bbox" onclick="setTool('bbox')"><span class="tool-icon">⬜</span><span>BBox</span></div>
      <div class="tool-btn" id="tool-corner" onclick="setTool('corner')"><span class="tool-icon">📐</span><span>Esquinero</span></div>
      <div class="tool-btn" id="tool-polygon" onclick="setTool('polygon')"><span class="tool-icon">🔷</span><span>Polígono</span></div>
      <div class="tool-btn" id="tool-sam" onclick="setTool('sam')"><span class="tool-icon">🎯</span><span>Auto</span></div>
    </div>
    <div class="tool-hint" id="tool-hint-bbox">Toca y arrastra para dibujar un rectángulo</div>
    <div class="tool-hint" id="tool-hint-corner" style="display:none">📐 Arrastra para el rectángulo base · luego ajusta el brazo del esquinero</div>
    <div class="tool-hint" id="tool-hint-polygon" style="display:none">Toca para agregar puntos · Doble toque para cerrar</div>
    <div class="tool-hint" id="tool-hint-sam" style="display:none">🎯 Toca exactamente sobre la pieza: contorno se dibuja sobre ella. Sin claves, funciona offline.</div>
    <div id="sam-status" style="display:none;font-size:11px;color:var(--amber);margin-top:6px;padding:6px 10px;background:rgba(245,158,11,.08);border-radius:8px;text-align:center"></div>
    <label style="display:flex;align-items:center;gap:10px;margin-top:10px;padding:10px;background:var(--bg);border:1.5px solid var(--border);border-radius:10px;cursor:pointer" for="arrume-toggle">
      <input type="checkbox" id="arrume-toggle" onchange="toggleArrume(this.checked)" style="width:18px;height:18px;margin:0;accent-color:var(--amber)">
      <div style="flex:1"><div style="font-size:13px;font-weight:700;color:var(--text)">🔗 Modo Arrume</div><div style="font-size:10px;color:var(--steel)">Mantiene la clase activa y dibuja varias piezas iguales</div></div>
      <span id="arrume-counter" style="display:none;font-family:monospace;font-weight:800;color:var(--amber);font-size:16px">×0</span>
    </label>
  </div>
  <div class="card">
    <div class="card-title">📸 Imagen</div>
    <div class="capture-zone" id="capture-zone">
      <span style="font-size:36px">📷</span>
      <span style="font-size:12px;color:var(--steel)">Elige origen de la imagen</span>
      <div class="btn-row" style="width:100%;margin-top:8px">
        <button class="btn btn-cam btn-sm" onclick="document.getElementById('file-input-cam').click()">📷 Cámara</button>
        <button class="btn btn-amber btn-sm" onclick="document.getElementById('file-input-gal').click()">🖼️ Galería</button>
      </div>
    </div>
    <input type="file" id="file-input-cam" accept="image/*" capture="environment">
    <input type="file" id="file-input-gal" accept="image/*" multiple="">
    <div id="bbox-section" style="display:none">
      <div class="btn-row" style="margin-bottom:8px"><button class="btn btn-danger btn-sm" style="flex:1" onclick="discardPhoto()">🗑️ Descartar y tomar/cargar otra</button></div>
      <div class="zoom-viewport" id="zoom-viewport"><div class="bbox-wrap" id="bbox-wrap"><img id="bbox-img" class="bbox-img" alt=""><canvas id="bbox-canvas"></canvas></div></div>
      <div class="zoom-bar" id="zoom-bar">
        <button class="zoom-btn" onclick="zoomBy(1.4)" title="Acercar">➕</button>
        <button class="zoom-btn" onclick="zoomBy(1/1.4)" title="Alejar">➖</button>
        <button class="zoom-btn" onclick="zoomReset()" title="Reiniciar zoom">⟲</button>
        <span class="zoom-lbl" id="zoom-lbl">1.0×</span>
        <span class="zoom-hint">Pellizca 2 dedos para zoom · 1 dedo dibuja</span>
      </div>
      <div class="blur-warn" id="blur-warn" style="display:none"><span id="blur-warn-txt"></span><span id="blur-warn-action"></span><span class="x" onclick="document.getElementById('blur-warn').style.display='none'">✕</span></div>
      <div class="poly-toolbar" id="poly-toolbar" style="display:none">
        <button class="btn btn-amber btn-sm" onclick="closePolygon()">✅ Cerrar polígono</button>
        <button class="btn btn-danger btn-sm" onclick="cancelPolygon()">✕ Cancelar</button>
        <span style="font-size:11px;color:var(--steel);align-self:center" id="poly-pts-count">0 puntos</span>
      </div>
    </div>
  </div>
  <div class="card" id="annos-card" style="display:none">
    <div class="card-title" id="annos-title">📦 Anotaciones (0)</div>
    <div class="anno-list" id="anno-list"></div>
    <div style="margin-top:8px;font-size:11px;color:var(--steel)">✅ marcadas se subirán · ☐ desmarcadas se omitirán · Toca la etiqueta para cambiar clase</div>
  </div>
  <div class="card">
    <div class="card-title" style="display:flex;justify-content:space-between;align-items:center;cursor:pointer" onclick="toggleStats()">
      <span>📊 Balance del dataset <span id="stats-total" style="color:var(--amber);font-weight:800">(0 img · 0 clases)</span></span>
      <span id="stats-caret" style="font-size:14px;color:var(--steel)">▼</span>
    </div>
    <div id="stats-body" style="display:none">
      <div style="font-size:11px;color:var(--steel);margin-bottom:8px">Meta inicial: <b style="color:var(--amber)">30 img/clase</b></div>
      <div id="stats-list"><div style="color:var(--steel);font-size:12px;text-align:center;padding:14px">Sin datos aún.</div></div>
      <div class="btn-row" style="margin-top:8px"><button class="btn btn-ghost btn-sm" onclick="resetStats()">🗑️ Reiniciar contador</button></div>
    </div>
  </div>
  <div class="prog-wrap" id="prog-wrap"><div class="prog-bar" id="prog-bar"></div></div>
  <div class="btn-row">
    <button class="btn btn-ghost btn-sm" onclick="resetAll()" style="flex:none;padding:13px 16px">🔄</button>
    <button class="btn btn-amber" id="btn-review" onclick="openReview()" disabled="">👁️ Revisar</button>
    <button class="btn btn-up" id="btn-upload" onclick="uploadAll()" disabled="">⬆️ Subir</button>
  </div>
</div>
<div class="page" id="page-historial">
  <div class="card"><div class="card-title">📋 Historial de sesión</div><div class="log-list" id="log-list"><p style="color:var(--steel);font-size:13px;text-align:center;padding:20px">Las subidas aparecerán aquí</p></div></div>
</div>
<div class="page" id="page-catalogo">
  <div class="card">
    <div class="card-title">📖 Catálogo UNISPAN</div>
    <div class="cat-search" style="margin-bottom:8px"><span class="ico">🔍</span><input type="text" id="cat-main-search" placeholder="Buscar..." oninput="renderCatalogPage(this.value)" style="margin-bottom:0;padding-left:36px"></div>
    <div class="cat-families" id="cat-main-families"></div>
    <div class="ref-grid" id="cat-main-grid"></div>
  </div>
</div>
<div class="page" id="page-experto">
  <div class="card">
    <div class="card-title">🎓 Agente Experto UNISPAN <span style="font-size:10px;color:var(--ok);font-weight:400;text-transform:none">● Sin claves · 100% local</span></div>
    <div style="font-size:12px;color:var(--steel);margin-bottom:10px">Consulta sobre láminas, bridas, platinas, refuerzos, perforaciones y estructura de paneles. Analiza imágenes directamente del catálogo.</div>
    <div style="background:#0b1220;border:1px solid #334;border-radius:10px;padding:10px;margin-bottom:10px">
      <div style="font-size:12px;color:var(--amber);font-weight:700;margin-bottom:8px">🧮 Calculadora de perforaciones</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:12px">
        <div><label style="color:var(--steel);font-size:11px">Ancho (mm)</label><input type="number" id="calc-w" placeholder="600" oninput="calcFromDims()" style="width:100%;padding:8px;border-radius:8px;border:1px solid #334;background:#0f1520;color:#eee"></div>
        <div><label style="color:var(--steel);font-size:11px">Longitud (mm)</label><input type="number" id="calc-l" placeholder="2400" oninput="calcFromDims()" style="width:100%;padding:8px;border-radius:8px;border:1px solid #334;background:#0f1520;color:#eee"></div>
        <div><label style="color:var(--steel);font-size:11px">Frontales (cont.)</label><input type="number" id="calc-nf" placeholder="12" oninput="calcFromCounts()" style="width:100%;padding:8px;border-radius:8px;border:1px solid #334;background:#0f1520;color:#eee"></div>
        <div><label style="color:var(--steel);font-size:11px">Laterales (cont.)</label><input type="number" id="calc-nl" placeholder="48" oninput="calcFromCounts()" style="width:100%;padding:8px;border-radius:8px;border:1px solid #334;background:#0f1520;color:#eee"></div>
      </div>
      <div id="calc-out" style="margin-top:8px;padding:8px;background:#1a2130;border-radius:8px;font-size:12px;color:#cbd5e1;text-align:center">Ingresa medidas o conteos · inicio 25 mm · paso 50 mm</div>
    </div>
    <div style="background:#0b1220;border:1px solid #334;border-radius:10px;padding:10px;margin-bottom:10px">
      <div style="font-size:12px;color:var(--amber);font-weight:700;margin-bottom:4px">🧠 Análisis de imagen — <span style="color:var(--ok);font-weight:400">sin API key</span></div>
      <div style="font-size:11px;color:var(--steel);margin-bottom:8px">El agente analiza la imagen localmente: detecta contornos, cuenta perforaciones, cruza con el catálogo completo y da la referencia UNISPAN. <b>No requiere ninguna clave.</b></div>
      <div class="btn-row" style="gap:6px">
        <button class="btn btn-amber btn-sm" onclick="analyzeCurrentWithAI()">🔍 Analizar imagen</button>
        <button class="btn btn-ok btn-sm" onclick="runPhysicalProof()">🧪 Auto-detectar piezas</button>
        <button class="btn btn-ghost btn-sm" onclick="showMemorySummary()">📊 Ver memoria</button>
        <button class="btn btn-danger btn-sm" onclick="clearMemory()" style="flex:none;padding:8px 10px">🗑️</button>
      </div>
      <label style="display:flex;align-items:center;gap:8px;margin-top:8px;color:var(--steel);font-size:11px;cursor:pointer">
        <input type="checkbox" id="auto-ai-toggle" onchange="toggleAutoPhysical(this.checked)" style="width:16px;height:16px;margin:0;accent-color:var(--amber)">
        Auto-reconocer pieza al cargar/tomar foto
      </label>
      <div id="physical-proof-out" style="margin-top:8px;padding:8px;background:#0f1520;border-radius:8px;font-size:11px;color:#cbd5e1;display:none"></div>
      <div id="ai-analysis-out" style="margin-top:8px;padding:8px;background:#1a2130;border-radius:8px;font-size:11px;color:#cbd5e1;display:none"></div>
    </div>
    <div id="expert-chips" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px"></div>
    <div id="expert-chat" style="max-height:52vh;overflow-y:auto;padding:8px;background:#0f1520;border-radius:10px;border:1px solid #223;font-size:13px;line-height:1.5"></div>
    <div style="display:flex;gap:6px;margin-top:10px">
      <input type="text" id="expert-input" placeholder="Ej: ¿cómo identifico un PM por perforaciones?" style="flex:1;padding:12px;border-radius:10px;border:1px solid #334;background:#0f1520;color:#eee" onkeydown="if(event.key==='Enter')expertAsk()">
      <button class="btn btn-amber btn-sm" onclick="expertAsk()">Enviar</button>
    </div>
    <div style="font-size:10px;color:var(--steel);margin-top:8px">💡 Base de conocimiento local · funciona sin conexión · sin claves API</div>
  </div>
</div>
</main>
<div class="modal-bg" id="cat-modal-bg" onclick="closeCatModal(event)">
  <div class="modal">
    <div class="modal-title"><span>Seleccionar clase</span><span class="modal-close" onclick="closeCatModalDirect()">✕</span></div>
    <div class="cat-search"><span class="ico">🔍</span><input type="text" id="cat-modal-search" placeholder="Buscar..." oninput="renderCatModal(this.value)" style="margin-bottom:8px;padding-left:36px"></div>
    <div class="cat-families" id="cat-modal-families"><div class="fam-btn active">Todas</div><div class="fam-btn">PM</div><div class="fam-btn">PB</div><div class="fam-btn">EI</div><div class="fam-btn">EE</div></div>
    <div class="cat-list" id="cat-modal-list"><div class="cat-item"><div onclick="setClase('PM-2400x600')"><div class="ci-code">PM-2400x600</div><div class="ci-spec">2400×600mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-2400x600')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-2400x550')"><div class="ci-code">PM-2400x550</div><div class="ci-spec">2400×550mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-2400x550')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-2400x500')"><div class="ci-code">PM-2400x500</div><div class="ci-spec">2400×500mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-2400x500')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-2400x450')"><div class="ci-code">PM-2400x450</div><div class="ci-spec">2400×450mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-2400x450')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-2400x420')"><div class="ci-code">PM-2400x420</div><div class="ci-spec">2400×420mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-2400x420')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-2400x400')"><div class="ci-code">PM-2400x400</div><div class="ci-spec">2400×400mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-2400x400')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-2400x380')"><div class="ci-code">PM-2400x380</div><div class="ci-spec">2400×380mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-2400x380')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-2400x350')"><div class="ci-code">PM-2400x350</div><div class="ci-spec">2400×350mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-2400x350')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-2400x320')"><div class="ci-code">PM-2400x320</div><div class="ci-spec">2400×320mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-2400x320')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-2400x300')"><div class="ci-code">PM-2400x300</div><div class="ci-spec">2400×300mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-2400x300')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-1200x600')"><div class="ci-code">PM-1200x600</div><div class="ci-spec">1200×600mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-1200x600')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-1200x550')"><div class="ci-code">PM-1200x550</div><div class="ci-spec">1200×550mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-1200x550')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-1200x500')"><div class="ci-code">PM-1200x500</div><div class="ci-spec">1200×500mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-1200x500')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-1200x450')"><div class="ci-code">PM-1200x450</div><div class="ci-spec">1200×450mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-1200x450')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-1200x420')"><div class="ci-code">PM-1200x420</div><div class="ci-spec">1200×420mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-1200x420')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-1200x400')"><div class="ci-code">PM-1200x400</div><div class="ci-spec">1200×400mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-1200x400')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-1200x380')"><div class="ci-code">PM-1200x380</div><div class="ci-spec">1200×380mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-1200x380')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-1200x350')"><div class="ci-code">PM-1200x350</div><div class="ci-spec">1200×350mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-1200x350')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-1200x320')"><div class="ci-code">PM-1200x320</div><div class="ci-spec">1200×320mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-1200x320')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-1200x300')"><div class="ci-code">PM-1200x300</div><div class="ci-spec">1200×300mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-1200x300')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-900x600')"><div class="ci-code">PM-900x600</div><div class="ci-spec">900×600mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-900x600')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-900x550')"><div class="ci-code">PM-900x550</div><div class="ci-spec">900×550mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-900x550')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-900x500')"><div class="ci-code">PM-900x500</div><div class="ci-spec">900×500mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-900x500')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-900x450')"><div class="ci-code">PM-900x450</div><div class="ci-spec">900×450mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-900x450')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-900x420')"><div class="ci-code">PM-900x420</div><div class="ci-spec">900×420mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-900x420')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-900x400')"><div class="ci-code">PM-900x400</div><div class="ci-spec">900×400mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-900x400')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-900x380')"><div class="ci-code">PM-900x380</div><div class="ci-spec">900×380mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-900x380')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-900x350')"><div class="ci-code">PM-900x350</div><div class="ci-spec">900×350mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-900x350')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-900x320')"><div class="ci-code">PM-900x320</div><div class="ci-spec">900×320mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-900x320')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-900x300')"><div class="ci-code">PM-900x300</div><div class="ci-spec">900×300mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-900x300')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-800x600')"><div class="ci-code">PM-800x600</div><div class="ci-spec">800×600mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-800x600')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-800x550')"><div class="ci-code">PM-800x550</div><div class="ci-spec">800×550mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-800x550')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-800x500')"><div class="ci-code">PM-800x500</div><div class="ci-spec">800×500mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-800x500')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-800x450')"><div class="ci-code">PM-800x450</div><div class="ci-spec">800×450mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-800x450')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-800x420')"><div class="ci-code">PM-800x420</div><div class="ci-spec">800×420mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-800x420')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-800x400')"><div class="ci-code">PM-800x400</div><div class="ci-spec">800×400mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-800x400')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-800x380')"><div class="ci-code">PM-800x380</div><div class="ci-spec">800×380mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-800x380')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-800x350')"><div class="ci-code">PM-800x350</div><div class="ci-spec">800×350mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-800x350')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-800x320')"><div class="ci-code">PM-800x320</div><div class="ci-spec">800×320mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-800x320')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-800x300')"><div class="ci-code">PM-800x300</div><div class="ci-spec">800×300mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-800x300')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-750x600')"><div class="ci-code">PM-750x600</div><div class="ci-spec">750×600mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-750x600')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-750x550')"><div class="ci-code">PM-750x550</div><div class="ci-spec">750×550mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-750x550')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-750x500')"><div class="ci-code">PM-750x500</div><div class="ci-spec">750×500mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-750x500')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-750x450')"><div class="ci-code">PM-750x450</div><div class="ci-spec">750×450mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-750x450')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-750x420')"><div class="ci-code">PM-750x420</div><div class="ci-spec">750×420mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-750x420')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-750x400')"><div class="ci-code">PM-750x400</div><div class="ci-spec">750×400mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-750x400')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-750x380')"><div class="ci-code">PM-750x380</div><div class="ci-spec">750×380mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-750x380')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-750x350')"><div class="ci-code">PM-750x350</div><div class="ci-spec">750×350mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-750x350')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-750x320')"><div class="ci-code">PM-750x320</div><div class="ci-spec">750×320mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-750x320')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-750x300')"><div class="ci-code">PM-750x300</div><div class="ci-spec">750×300mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-750x300')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-600x600')"><div class="ci-code">PM-600x600</div><div class="ci-spec">600×600mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-600x600')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-600x550')"><div class="ci-code">PM-600x550</div><div class="ci-spec">600×550mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-600x550')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-600x500')"><div class="ci-code">PM-600x500</div><div class="ci-spec">600×500mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-600x500')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-600x450')"><div class="ci-code">PM-600x450</div><div class="ci-spec">600×450mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-600x450')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-600x420')"><div class="ci-code">PM-600x420</div><div class="ci-spec">600×420mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-600x420')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-600x400')"><div class="ci-code">PM-600x400</div><div class="ci-spec">600×400mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-600x400')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-600x380')"><div class="ci-code">PM-600x380</div><div class="ci-spec">600×380mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-600x380')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-600x350')"><div class="ci-code">PM-600x350</div><div class="ci-spec">600×350mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-600x350')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-600x320')"><div class="ci-code">PM-600x320</div><div class="ci-spec">600×320mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-600x320')">📋</span></div><div class="cat-item"><div onclick="setClase('PM-600x300')"><div class="ci-code">PM-600x300</div><div class="ci-spec">600×300mm</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('PM-600x300')">📋</span></div></div>
  </div>
</div>
<div class="modal-bg" id="review-modal-bg" onclick="closeReviewModal(event)">
  <div class="modal">
    <div class="modal-title"><span>👁️ Revisar antes de subir</span><span class="modal-close" onclick="closeReviewModalDirect()">✕</span></div>
    <div class="review-img-wrap"><img id="review-img" class="review-img" alt=""><canvas id="review-canvas"></canvas></div>
    <div class="review-annos" id="review-annos"></div>
    <div class="btn-row"><button class="btn btn-ghost" onclick="closeReviewModalDirect()">Volver</button><button class="btn btn-up" onclick="confirmAndUpload()">✅ Confirmar y subir</button></div>
  </div>
</div>
<div class="toast" id="toast"></div>
<script>
// ═══════════════════════════════════════════════════════════════════
// CATÁLOGO COMPLETO UNISPAN
// ═══════════════════════════════════════════════════════════════════
const CATALOG=[];
[2400,1200,900,800,750,600].forEach(l=>[600,550,500,450,420,400,380,350,320,300].forEach(a=>CATALOG.push({code:`PM-${l}x${a}`,family:"PM",spec:`${l}×${a}mm`,largo:l,ancho:a})));
[2400,1200,900,800,750,600].forEach(l=>[270,250,230,200,150,120,100,90,80].forEach(a=>CATALOG.push({code:`PB-${l}x${a}`,family:"PB",spec:`${l}×${a}mm`,largo:l,ancho:a})));
[2400,1200,900,800,600].forEach(l=>CATALOG.push({code:`EI-${l}x150x150`,family:"EI",spec:`${l}×150×150mm`,largo:l,ancho:150}));
[2400,1200,900,800,600].forEach(l=>CATALOG.push({code:`EE-${l}x150x150`,family:"EE",spec:`${l}×150×150mm`,largo:l,ancho:150}));

// Mapa rápido código→entrada
const CATALOG_MAP={};
CATALOG.forEach(c=>{ CATALOG_MAP[c.code.toUpperCase()]=c; });

// Tabla de perforaciones estándar
const PERF_TABLE={
  ancho:{600:12,550:11,500:10,450:9,420:8,400:8,380:8,350:7,320:6,300:6,270:5,250:5,230:5,200:4,150:3,120:2,100:2,90:2,80:2},
  largo:{2400:48,1200:24,900:18,800:16,750:15,600:12}
};
// Inverso: perforaciones → medida
const PERF_INV_ANCHO={};  Object.entries(PERF_TABLE.ancho).forEach(([mm,n])=>{ if(!PERF_INV_ANCHO[n]) PERF_INV_ANCHO[n]=+mm; });
const PERF_INV_LARGO={};  Object.entries(PERF_TABLE.largo).forEach(([mm,n])=>{ if(!PERF_INV_LARGO[n]) PERF_INV_LARGO[n]=+mm; });
const STD_ANCHOS=Object.keys(PERF_TABLE.ancho).map(Number).sort((a,b)=>b-a);
const STD_LARGOS=Object.keys(PERF_TABLE.largo).map(Number).sort((a,b)=>b-a);

function familyFor(w){ if(w>=300&&w<=600) return "PM"; if(w>=80&&w<=270) return "PB"; return "?"; }
function nearest(v,arr){ return arr.reduce((a,b)=>Math.abs(b-v)<Math.abs(a-v)?b:a); }
function nearestCatalogMatch(family, largo_mm, ancho_mm){
  const cands=CATALOG.filter(c=>c.family===family);
  if(!cands.length) return null;
  let best=null, bestD=Infinity;
  cands.forEach(c=>{
    const d=Math.abs(c.largo-(largo_mm||0))+Math.abs(c.ancho-(ancho_mm||0));
    if(d<bestD){ bestD=d; best=c; }
  });
  return best?{...best, distancia_mm:bestD}:null;
}
function catalogSummaryForPrompt(){
  return `PM: largos {2400,1200,900,800,750,600}mm × anchos {600,550,500,450,420,400,380,350,320,300}mm
PB: largos {2400,1200,900,800,750,600}mm × anchos {270,250,230,200,150,120,100,90,80}mm
EI/EE: largos {2400,1200,900,800,600}mm × 150×150mm
Regla: frontales=ancho/50 | laterales=largo/50 | inicio=25mm | paso=50mm`;
}

const COLORS=["#f59e0b","#3b82f6","#a855f7","#22c55e","#ef4444","#06b6d4","#f97316","#84cc16","#ec4899","#14b8a6"];
const PROJECT="reconocimiento-de-piezas-rllp1";

// ═══════════════════════════════════════════════════════════════════
// ESTADO GLOBAL
// ═══════════════════════════════════════════════════════════════════
let currentClase="", selectedFile=null;
let sessionCount=0, totalCount=+localStorage.getItem("rf_total")||0, okCount=+localStorage.getItem("rf_ok")||0;
let recientes=JSON.parse(localStorage.getItem("rf_recientes")||"[]");
let catModalFam="ALL", catPageFam="ALL", uploadLog=[];
let annotations=[];
let classCounts=JSON.parse(localStorage.getItem("rf_class_counts")||"{}");
const CLASS_GOAL=30;
let catModalMode="select", catReassignId=null;
let zoomScale=1, zoomTx=0, zoomTy=0;
let pinchState=null;
let activeTool="bbox";
let arrumeMode=false, arrumeCount=0;
let bboxDrawing=false, bboxStart={x:0,y:0}, bboxCurrent=null;
let polyPoints=[], polyDrawing=false, polyPreview=null;
let cornerState=null, cornerDrawing=false, cornerBaseStart=null;
let imgNatW=0, imgNatH=0, imgDispW=0, imgDispH=0;
let _segCanvas=null, _segCtx=null, _segData=null, _segW=0, _segH=0;
let imgMemory=JSON.parse(localStorage.getItem("rf_img_memory")||"[]");
let physicalProofs=JSON.parse(localStorage.getItem("rf_physical_proofs")||"[]");
let autoPhysicalOn=localStorage.getItem("rf_auto_physical")!=="0";
let _lastMemoryEntry=null;
let learnedPieces=JSON.parse(localStorage.getItem("rf_learned_pieces")||"[]");

function saveMemory(){ try{ localStorage.setItem("rf_img_memory",JSON.stringify(imgMemory.slice(0,200))); }catch(_){} }
function savePhysicalProofs(){ try{ localStorage.setItem("rf_physical_proofs",JSON.stringify(physicalProofs.slice(0,80))); }catch(_){} }
function saveLearned(){ try{ localStorage.setItem("rf_learned_pieces",JSON.stringify(learnedPieces.slice(0,600))); }catch(_){} }

// ─── Huella visual (dHash) + memoria de piezas confirmadas ────────
function computeFingerprintFromCanvas(srcCanvas){
  try{
    const S=9;
    const c=document.createElement("canvas"); c.width=S; c.height=8;
    const ctx=c.getContext("2d"); ctx.drawImage(srcCanvas,0,0,S,8);
    const d=ctx.getImageData(0,0,S,8).data;
    const gray=[];
    for(let i=0;i<S*8;i++){ const idx=i*4; gray.push(0.299*d[idx]+0.587*d[idx+1]+0.114*d[idx+2]); }
    let bits="";
    for(let y=0;y<8;y++) for(let x=0;x<S-1;x++) bits+= gray[y*S+x]>gray[y*S+x+1] ? "1":"0";
    return bits;
  }catch(_){ return null; }
}
function hashHamming(a,b){ if(!a||!b||a.length!==b.length) return 999; let d=0; for(let i=0;i<a.length;i++) if(a[i]!==b[i]) d++; return d; }
function learnPiece(hash,clase,meta){
  if(!hash||!clase||clase==="POR-IDENTIFICAR") return;
  let best=null,bestD=999;
  learnedPieces.forEach(p=>{ const d=hashHamming(p.hash,hash); if(d<bestD){bestD=d;best=p;} });
  if(best&&bestD<=6){ best.hash=hash; best.clase=clase; best.confirmations=(best.confirmations||1)+1; best.lastSeen=Date.now(); Object.assign(best,meta||{}); }
  else{ learnedPieces.unshift({hash,clase,confirmations:1,lastSeen:Date.now(),...(meta||{})}); }
  if(learnedPieces.length>600) learnedPieces.length=600;
  saveLearned();
}
function matchLearnedPiece(hash){
  if(!hash||!learnedPieces.length) return null;
  let best=null,bestD=999;
  learnedPieces.forEach(p=>{ const d=hashHamming(p.hash,hash); if(d<bestD){ bestD=d; best=p; } });
  if(!best) return null;
  const thr=(best.confirmations||1)>=3?10:7;
  if(bestD>thr) return null;
  const confianza=Math.max(0.55,Math.min(0.97,(1-bestD/16)*Math.min(1,0.5+(best.confirmations||1)*0.12)));
  return {...best,distancia:bestD,confianza};
}
function boundsOfPoints(points){
  const xs=points.map(p=>p.x), ys=points.map(p=>p.y);
  const x=Math.min(...xs), y=Math.min(...ys);
  return {x,y,w:Math.max(1,Math.max(...xs)-x),h:Math.max(1,Math.max(...ys)-y)};
}

const _autoPhysicalToggle=document.getElementById("auto-ai-toggle");
if(_autoPhysicalToggle) _autoPhysicalToggle.checked=autoPhysicalOn;

const savedRfKey=localStorage.getItem("rf_api_key");
if(savedRfKey) document.getElementById("api-key").value=savedRfKey;
document.getElementById("api-key").addEventListener("blur",()=>localStorage.setItem("rf_api_key",document.getElementById("api-key").value.trim()));
document.getElementById("cnt-total").textContent=totalCount;
document.getElementById("cnt-ok").textContent=okCount;

function fetchWithTimeout(url,opts,ms=15000){
  const ctrl=new AbortController();
  const timer=setTimeout(()=>ctrl.abort(),ms);
  return fetch(url,{...opts,signal:ctrl.signal}).finally(()=>clearTimeout(timer));
}
function safeHtml(s){ return String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c])); }
function showToast(msg,type){const t=document.getElementById("toast");t.textContent=msg;t.className=`toast ${type} show`;setTimeout(()=>t.classList.remove("show"),2800);}

// ─── Tabs ────────────────────────────────────────────────────────
function switchTab(n){
  document.querySelectorAll(".tab").forEach((t,i)=>t.classList.toggle("active",["captura","historial","catalogo","experto"][i]===n));
  document.querySelectorAll(".page").forEach(p=>p.classList.toggle("active",p.id==="page-"+n));
  if(n==="catalogo") renderCatalogPage("");
  if(n==="experto") expertInit();
}

// ─── Herramienta ─────────────────────────────────────────────────
function setTool(t){
  activeTool=t;
  ["bbox","corner","polygon","sam"].forEach(k=>{
    document.getElementById("tool-"+k).classList.toggle("active",t===k);
    const h=document.getElementById("tool-hint-"+k); if(h) h.style.display=t===k?"block":"none";
  });
  bboxCurrent=null; bboxDrawing=false;
  cancelPolygon(); cornerCancel();
  if(t==="sam") samStatus("✅ Toca exactamente sobre la pieza a segmentar",true);
}

// ─── Arrume ──────────────────────────────────────────────────────
function toggleArrume(on){
  arrumeMode=on; arrumeCount=0;
  const c=document.getElementById("arrume-counter");
  c.style.display=on?"inline-block":"none"; c.textContent="×0";
  if(on && !currentClase) showToast("⚠️ Selecciona una clase primero","err");
  else if(on) showToast(`🔗 Arrume ON: ${currentClase||"?"}`,"ok");
}
function bumpArrume(){
  if(!arrumeMode) return;
  arrumeCount++;
  document.getElementById("arrume-counter").textContent="×"+arrumeCount;
}
function bumpArrumeBy(n){
  if(!arrumeMode) return;
  arrumeCount+=Math.max(1,Math.round(n));
  document.getElementById("arrume-counter").textContent="×"+arrumeCount;
}

// ─── Clase ───────────────────────────────────────────────────────
function setClase(code){
  if(catModalMode==="reassign" && catReassignId!=null){
    const a=annotations.find(x=>x.id===catReassignId);
    if(a){
      a.clase=code; renderAnnoList(); redraw(); showToast(`✏️ Clase → ${code}`,"ok");
      const codeUp=String(code).toUpperCase();
      if(CATALOG_MAP[codeUp]){
        let hash=a._hash;
        if(!hash){ try{ const box=annotationBounds(a); const loc=localImageAnalysis(box); if(loc&&loc._cv) hash=computeFingerprintFromCanvas(loc._cv); }catch(_){} }
        if(hash){ a._hash=hash; learnPiece(hash,codeUp,{familia:CATALOG_MAP[codeUp].family}); }
      }
    }
    catModalMode="select"; catReassignId=null;
    closeCatModalDirect(); addReciente(code); return;
  }
  currentClase=code;
  document.getElementById("clase-custom").value=code;
  const d=document.getElementById("current-clase-display");
  d.textContent="✏️ Clase activa: "+code; d.style.display="block";
  addReciente(code); closeCatModalDirect();
}
function reassignClass(id){ catModalMode="reassign"; catReassignId=id; openCatModal(); setTimeout(()=>{ const t=document.querySelector("#cat-modal-bg .modal-title span:first-child"); if(t) t.textContent="Reasignar clase"; },50); }
function onCustomInput(v){ currentClase=v.trim().toUpperCase(); const d=document.getElementById("current-clase-display"); if(v){d.textContent="✏️ Clase activa: "+currentClase;d.style.display="block";}else d.style.display="none"; }
function addReciente(code){ recientes=[code,...recientes.filter(r=>r!==code)].slice(0,8); localStorage.setItem("rf_recientes",JSON.stringify(recientes)); renderRecientes(); }
function renderRecientes(){
  const g=document.getElementById("recientes-grid"); g.innerHTML="";
  recientes.forEach(c=>{const b=document.createElement("div");b.className="quick-btn"+(c===currentClase?" active":"");b.textContent=c;b.onclick=()=>setClase(c);g.appendChild(b);});
  document.getElementById("recientes-wrap").style.display=recientes.length?"":"none";
}
renderRecientes();

// ─── Archivo ─────────────────────────────────────────────────────
function loadFile(f){
  if(!f) return;
  selectedFile=f; annotations=[];
  const url=URL.createObjectURL(f);
  const img=document.getElementById("bbox-img");
  img.onload=()=>{
    imgNatW=img.naturalWidth; imgNatH=img.naturalHeight;
    zoomReset(); initCanvas(); analyzeBlur(img); recordMemory(img,f);
    scheduleAutoPhysicalProof();
  };
  img.src=url;
  document.getElementById("capture-zone").classList.add("has-img");
  document.getElementById("bbox-section").style.display="block";
  document.getElementById("annos-card").style.display="none";
  document.getElementById("blur-warn").style.display="none";
  cancelPolygon(); bboxCurrent=null; cornerCancel();
  _segCanvas=null; _segData=null;
  arrumeCount=0; const ac=document.getElementById("arrume-counter"); if(ac&&arrumeMode) ac.textContent="×0";
  renderAnnoList(); updateButtons();
}
function scheduleAutoPhysicalProof(){
  if(!selectedFile||!autoPhysicalOn) return;
  setPhysicalStatus("🧪 Foto cargada · preparando auto-reconocimiento…");
  setTimeout(()=>{ if(selectedFile&&autoPhysicalOn) runPhysicalProof({auto:true}); },700);
}
function toggleAutoPhysical(on){ autoPhysicalOn=!!on; localStorage.setItem("rf_auto_physical",autoPhysicalOn?"1":"0"); showToast(autoPhysicalOn?"🧪 Auto-reconocimiento ON":"🧪 OFF",autoPhysicalOn?"ok":""); }
function setPhysicalStatus(html,show=true){ const el=document.getElementById("physical-proof-out"); if(!el) return; el.style.display=show?"block":"none"; if(show) el.innerHTML=html; }
document.getElementById("file-input-cam").addEventListener("change",e=>loadFile(e.target.files[0]));
document.getElementById("file-input-gal").addEventListener("change",e=>loadFile(e.target.files[0]));

// ─── Blur ────────────────────────────────────────────────────────
function analyzeBlur(img){
  try{
    const S=220; const c=document.createElement("canvas"); c.width=S; c.height=S;
    const g=c.getContext("2d"); g.drawImage(img,0,0,S,S);
    const d=g.getImageData(0,0,S,S).data;
    const lum=new Float32Array(S*S);
    for(let i=0;i<S*S;i++) lum[i]=0.299*d[i*4]+0.587*d[i*4+1]+0.114*d[i*4+2];
    let sum=0,sum2=0,n=0;
    for(let y=1;y<S-1;y++) for(let x=1;x<S-1;x++){ const i=y*S+x; const v=-lum[i-S]-lum[i-1]+4*lum[i]-lum[i+1]-lum[i+S]; sum+=v; sum2+=v*v; n++; }
    const mean=sum/n, variance=(sum2/n)-mean*mean;
    const w=document.getElementById("blur-warn"); const t=document.getElementById("blur-warn-txt"); const act=document.getElementById("blur-warn-action");
    w.classList.remove("ok");
    if(_lastMemoryEntry){ _lastMemoryEntry.blur=Math.round(variance); saveMemory(); }
    if(variance<80){ w.style.display="flex"; t.innerHTML=`⚠️ <b>Foto borrosa</b> (nitidez ${variance.toFixed(0)}).`; act.innerHTML=`<span class="blur-warn-discard" onclick="discardPhoto()">🗑️ Descartar</span>`; }
    else if(variance<180){ w.style.display="flex"; t.innerHTML=`⚠️ Nitidez media (${variance.toFixed(0)}).`; act.innerHTML=`<span class="blur-warn-discard" onclick="discardPhoto()">🗑️ Repetir</span>`; }
    else { w.style.display="flex"; w.classList.add("ok"); t.innerHTML=`✅ Foto nítida (${variance.toFixed(0)}).`; act.innerHTML=""; setTimeout(()=>{ if(w.classList.contains("ok")) w.style.display="none"; },2500); }
  }catch(_){}
}

// ─── Canvas ───────────────────────────────────────────────────────
const canvas=document.getElementById("bbox-canvas");
function initCanvas(){ const img=document.getElementById("bbox-img"); imgDispW=img.offsetWidth; imgDispH=img.offsetHeight; canvas.width=imgDispW; canvas.height=imgDispH; redraw(); }
function getPos(e){
  const rect=canvas.getBoundingClientRect();
  const t=e.touches?e.touches[0]:e;
  return{ x:Math.max(0,Math.min(canvas.width,(t.clientX-rect.left)*(canvas.width/rect.width))), y:Math.max(0,Math.min(canvas.height,(t.clientY-rect.top)*(canvas.height/rect.height))) };
}
window.addEventListener("resize",()=>{ if(selectedFile) initCanvas(); });

// ─── Zoom ─────────────────────────────────────────────────────────
function applyZoom(){ const w=document.getElementById("bbox-wrap"); w.style.transform=`translate(${zoomTx}px,${zoomTy}px) scale(${zoomScale})`; const lbl=document.getElementById("zoom-lbl"); if(lbl) lbl.textContent=zoomScale.toFixed(1)+"×"; }
function zoomReset(){ zoomScale=1; zoomTx=0; zoomTy=0; applyZoom(); }
function zoomBy(factor){ const vp=document.getElementById("zoom-viewport"); if(!vp) return; const r=vp.getBoundingClientRect(); zoomAt(zoomScale*factor,r.width/2,r.height/2); }
function zoomAt(newScale,cx,cy){ newScale=Math.max(1,Math.min(6,newScale)); const kx=(cx-zoomTx)/zoomScale, ky=(cy-zoomTy)/zoomScale; zoomScale=newScale; zoomTx=cx-kx*zoomScale; zoomTy=cy-ky*zoomScale; clampPan(); applyZoom(); }
function clampPan(){ const vp=document.getElementById("zoom-viewport"); if(!vp) return; const r=vp.getBoundingClientRect(); const cW=r.width*zoomScale, cH=r.height*zoomScale; if(zoomScale<=1){ zoomTx=0; zoomTy=0; return; } zoomTx=Math.min(0,Math.max(r.width-cW,zoomTx)); zoomTy=Math.min(0,Math.max(r.height-cH,zoomTy)); }
function touchDist(t1,t2){ return Math.hypot(t1.clientX-t2.clientX,t1.clientY-t2.clientY); }
function touchMid(t1,t2,vpRect){ return{x:(t1.clientX+t2.clientX)/2-vpRect.left,y:(t1.clientY+t2.clientY)/2-vpRect.top}; }

// ─── Eventos canvas ───────────────────────────────────────────────
function pointerDown_(e){ if(activeTool==="bbox") bboxStart_(e); else if(activeTool==="corner") cornerStart_(e); else if(activeTool==="polygon") polyTap(e); else if(activeTool==="sam") samTap(e); }
function pointerMove_(e){ if(activeTool==="bbox") bboxMove_(e); else if(activeTool==="corner") cornerMove_(e); else if(activeTool==="polygon") polyMove_(e); }
function pointerUp_(e){ if(activeTool==="bbox") bboxEnd_(e); else if(activeTool==="corner") cornerEnd_(e); }
canvas.addEventListener("mousedown",e=>{ e.preventDefault(); pointerDown_(e); },{passive:false});
canvas.addEventListener("mousemove",e=>{ e.preventDefault(); pointerMove_(e); },{passive:false});
canvas.addEventListener("mouseup",e=>{ e.preventDefault(); pointerUp_(e); },{passive:false});
canvas.addEventListener("touchstart",e=>{
  e.preventDefault();
  if(e.touches.length===2){
    bboxDrawing=false; bboxCurrent=null;
    const vp=document.getElementById("zoom-viewport").getBoundingClientRect();
    const mid=touchMid(e.touches[0],e.touches[1],vp);
    pinchState={d0:touchDist(e.touches[0],e.touches[1]),s0:zoomScale,cx:mid.x,cy:mid.y,tx0:zoomTx,ty0:zoomTy,mx0:mid.x,my0:mid.y};
  } else pointerDown_(e);
},{passive:false});
canvas.addEventListener("touchmove",e=>{
  e.preventDefault();
  if(pinchState&&e.touches.length===2){
    const vp=document.getElementById("zoom-viewport").getBoundingClientRect();
    const d=touchDist(e.touches[0],e.touches[1]); const mid=touchMid(e.touches[0],e.touches[1],vp);
    const newScale=Math.max(1,Math.min(6,pinchState.s0*(d/pinchState.d0)));
    const kx=(pinchState.cx-pinchState.tx0)/pinchState.s0, ky=(pinchState.cy-pinchState.ty0)/pinchState.s0;
    zoomScale=newScale; zoomTx=pinchState.cx-kx*zoomScale+(mid.x-pinchState.mx0); zoomTy=pinchState.cy-ky*zoomScale+(mid.y-pinchState.my0);
    clampPan(); applyZoom(); return;
  }
  pointerMove_(e);
},{passive:false});
canvas.addEventListener("touchend",e=>{ e.preventDefault(); if(pinchState&&e.touches.length<2){ pinchState=null; return; } pointerUp_(e); },{passive:false});
canvas.addEventListener("dblclick",e=>{ e.preventDefault(); if(activeTool==="polygon") closePolygon(); });

// ─── BBox ─────────────────────────────────────────────────────────
function bboxStart_(e){ if(!checkClase()) return; const p=getPos(e); bboxDrawing=true; bboxStart=p; bboxCurrent=null; }
function bboxMove_(e){ if(!bboxDrawing) return; const p=getPos(e); bboxCurrent={x:Math.min(bboxStart.x,p.x),y:Math.min(bboxStart.y,p.y),w:Math.abs(p.x-bboxStart.x),h:Math.abs(p.y-bboxStart.y)}; redraw(); }
function bboxEnd_(e){
  bboxDrawing=false;
  if(bboxCurrent&&bboxCurrent.w>15&&bboxCurrent.h>15){
    const id=Date.now(); const color=COLORS[annotations.length%COLORS.length];
    const finalBox={...bboxCurrent};
    annotations.push({id,clase:currentClase,type:"bbox",bbox:finalBox,color,checked:true,qty:null});
    bboxCurrent=null; redraw(); renderAnnoList(); updateButtons();
    if(arrumeMode){
      let inc=1, est=null;
      if(finalBox.w>40&&finalBox.h>40){ try{ est=estimateArrumeCount(finalBox); }catch(_){} }
      if(est&&est.estimated>1) inc=est.estimated;
      bumpArrumeBy(inc);
      showToast(inc>1?`🔗 +${inc} ${currentClase} (auto-conteo) → total ${arrumeCount}`:`🔗 +1 ${currentClase} (${arrumeCount})`,"ok");
    }
    else showQtyPromptAt(id, finalBox);
  } else { bboxCurrent=null; redraw(); }
}

// ─── Esquinero ────────────────────────────────────────────────────
function cornerStart_(e){ if(!checkClase()) return; const p=getPos(e); cornerDrawing=true; cornerBaseStart=p; cornerState=null; }
function cornerMove_(e){ if(!cornerDrawing) return; const p=getPos(e); const b={x:Math.min(cornerBaseStart.x,p.x),y:Math.min(cornerBaseStart.y,p.y),w:Math.abs(p.x-cornerBaseStart.x),h:Math.abs(p.y-cornerBaseStart.y)}; cornerState={base:b,corner:"TR",armW:Math.round(b.w*0.4),armH:Math.round(b.h*0.4)}; redraw(); }
function cornerEnd_(e){ cornerDrawing=false; if(!cornerState||cornerState.base.w<20||cornerState.base.h<20){ cornerState=null; redraw(); return; } openCornerPanel(); redraw(); }
function cornerCancel(){ cornerState=null; cornerDrawing=false; const p=document.getElementById("corner-panel"); if(p) p.remove(); redraw(); }
function cornerPolygonPoints(){
  if(!cornerState) return null;
  const {base:b,corner:c,armW:aw,armH:ah}=cornerState;
  const W=Math.min(aw,b.w-4), H=Math.min(ah,b.h-4);
  const TL={x:b.x,y:b.y},TR={x:b.x+b.w,y:b.y},BR={x:b.x+b.w,y:b.y+b.h},BL={x:b.x,y:b.y+b.h};
  if(c==="TR") return [TL,{x:b.x+b.w-W,y:b.y},{x:b.x+b.w-W,y:b.y+H},{x:b.x+b.w,y:b.y+H},BR,BL];
  if(c==="TL") return [{x:b.x+W,y:b.y},TR,BR,BL,{x:b.x,y:b.y+H},{x:b.x+W,y:b.y+H}];
  if(c==="BR") return [TL,TR,{x:b.x+b.w,y:b.y+b.h-H},{x:b.x+b.w-W,y:b.y+b.h-H},{x:b.x+b.w-W,y:b.y+b.h},BL];
  if(c==="BL") return [TL,TR,BR,{x:b.x+W,y:b.y+b.h},{x:b.x+W,y:b.y+b.h-H},{x:b.x,y:b.y+b.h-H}];
  return null;
}
function openCornerPanel(){
  const ex=document.getElementById("corner-panel"); if(ex) ex.remove();
  const b=cornerState.base; const maxW=Math.floor(b.w-4), maxH=Math.floor(b.h-4);
  const div=document.createElement("div"); div.id="corner-panel"; div.className="float-panel";
  div.innerHTML=`<div class="fp-head" id="cp-head"><span style="flex:1">📐 Esquinero</span><button class="fp-btn" onclick="document.getElementById('corner-panel').classList.toggle('min')">▁</button><button class="fp-btn" onclick="cornerCancel()">✕</button></div>
    <div class="fp-body"><div class="corner-grid"><button class="corner-btn" data-c="TL" onclick="cornerSetCorner('TL')">↖ Sup-Izq</button><button class="corner-btn active" data-c="TR" onclick="cornerSetCorner('TR')">↗ Sup-Der</button><button class="corner-btn" data-c="BL" onclick="cornerSetCorner('BL')">↙ Inf-Izq</button><button class="corner-btn" data-c="BR" onclick="cornerSetCorner('BR')">↘ Inf-Der</button></div>
    <div class="slider-row"><label>Brazo ancho</label><input type="range" id="cp-w" min="4" max="${maxW}" value="${cornerState.armW}" oninput="cornerSetArm('w',this.value)"><span class="val" id="cp-w-v">${cornerState.armW}</span></div>
    <div class="slider-row"><label>Brazo alto</label><input type="range" id="cp-h" min="4" max="${maxH}" value="${cornerState.armH}" oninput="cornerSetArm('h',this.value)"><span class="val" id="cp-h-v">${cornerState.armH}</span></div>
    <div class="btn-row" style="margin-top:8px"><button class="btn btn-ghost btn-sm" onclick="cornerCancel()">Cancelar</button><button class="btn btn-amber btn-sm" onclick="cornerConfirm()">✅ Guardar</button></div></div>`;
  document.body.appendChild(div); makeDraggable(div,document.getElementById("cp-head"));
}
function cornerSetCorner(c){ if(!cornerState) return; cornerState.corner=c; document.querySelectorAll("#corner-panel .corner-btn").forEach(b=>b.classList.toggle("active",b.dataset.c===c)); redraw(); }
function cornerSetArm(k,v){ if(!cornerState) return; v=parseInt(v); if(k==="w"){ cornerState.armW=v; document.getElementById("cp-w-v").textContent=v; } else { cornerState.armH=v; document.getElementById("cp-h-v").textContent=v; } redraw(); }
function cornerConfirm(){
  const pts=cornerPolygonPoints(); if(!pts){ cornerCancel(); return; }
  const id=Date.now(); const color=COLORS[annotations.length%COLORS.length];
  annotations.push({id,clase:currentClase,type:"polygon",points:pts,color,checked:true,qty:null,fromCorner:true});
  cornerCancel(); renderAnnoList(); updateButtons();
  if(arrumeMode){ bumpArrume(); showToast(`🔗 +1 ${currentClase} (${arrumeCount})`,"ok"); }
  else showQtyPromptAt(id, null);
}
function makeDraggable(el,handle){
  let sx=0,sy=0,ox=0,oy=0,dragging=false;
  const start=(cx,cy)=>{ dragging=true; sx=cx; sy=cy; const r=el.getBoundingClientRect(); ox=r.left; oy=r.top; el.style.left=ox+"px"; el.style.top=oy+"px"; el.style.right="auto"; };
  const move=(cx,cy)=>{ if(!dragging) return; el.style.left=(ox+cx-sx)+"px"; el.style.top=Math.max(4,oy+cy-sy)+"px"; };
  const end=()=>{ dragging=false; };
  handle.addEventListener("mousedown",e=>{ e.preventDefault(); start(e.clientX,e.clientY); });
  window.addEventListener("mousemove",e=>move(e.clientX,e.clientY));
  window.addEventListener("mouseup",end);
  handle.addEventListener("touchstart",e=>{ const t=e.touches[0]; start(t.clientX,t.clientY); },{passive:true});
  window.addEventListener("touchmove",e=>{ if(!dragging) return; const t=e.touches[0]; move(t.clientX,t.clientY); },{passive:true});
  window.addEventListener("touchend",end);
}

// ─── Polygon ──────────────────────────────────────────────────────
let lastTapTime=0;
function polyTap(e){
  if(!checkClase()) return;
  const now=Date.now();
  if(now-lastTapTime<300){ closePolygon(); lastTapTime=0; return; }
  lastTapTime=now;
  const p=getPos(e); polyPoints.push(p); polyDrawing=true;
  document.getElementById("poly-toolbar").style.display="flex";
  document.getElementById("poly-pts-count").textContent=polyPoints.length+" punto"+(polyPoints.length!==1?"s":"");
  redraw();
}
function polyMove_(e){ if(!polyDrawing||!polyPoints.length) return; polyPreview=getPos(e); redraw(); }
function closePolygon(){
  if(polyPoints.length<3){ showToast("⚠️ Mínimo 3 puntos","err"); return; }
  const id=Date.now(); const color=COLORS[annotations.length%COLORS.length];
  annotations.push({id,clase:currentClase,type:"polygon",points:[...polyPoints],color,checked:true,qty:null});
  cancelPolygon(); redraw(); renderAnnoList(); updateButtons();
  if(arrumeMode){ bumpArrume(); showToast(`🔗 +1 ${currentClase} (${arrumeCount})`,"ok"); }
  else showQtyPromptAt(id,null);
}
function cancelPolygon(){ polyPoints=[]; polyDrawing=false; polyPreview=null; document.getElementById("poly-toolbar").style.display="none"; redraw(); }

// Estima cuántas piezas hay apiladas en un arrume analizando las líneas
// oscuras separadoras (bridas frontales de 47mm) dentro de la región marcada.
function estimateArrumeCount(cropDisplayBox){
  const img=document.getElementById("bbox-img");
  if(!img||!img.naturalWidth||!cropDisplayBox) return null;
  const scX=img.naturalWidth/imgDispW, scY=img.naturalHeight/imgDispH;
  const sx=Math.max(0,Math.round(cropDisplayBox.x*scX)), sy=Math.max(0,Math.round(cropDisplayBox.y*scY));
  const sw=Math.max(10,Math.min(img.naturalWidth-sx,Math.round(cropDisplayBox.w*scX)));
  const sh=Math.max(10,Math.min(img.naturalHeight-sy,Math.round(cropDisplayBox.h*scY)));
  const isVertical=sh>=sw; // el arrume suele apilarse en la dirección más larga
  const W=isVertical?40:160, H=isVertical?160:40;
  const cv=document.createElement("canvas"); cv.width=W; cv.height=H;
  const ctx=cv.getContext("2d"); ctx.drawImage(img,sx,sy,sw,sh,0,0,W,H);
  const data=ctx.getImageData(0,0,W,H).data;
  const n=isVertical?H:W;
  const profile=new Float32Array(n);
  for(let i=0;i<n;i++){
    let sum=0,cnt=0;
    if(isVertical){ for(let x=0;x<W;x++){ const idx=(i*W+x)*4; sum+=0.299*data[idx]+0.587*data[idx+1]+0.114*data[idx+2]; cnt++; } }
    else{ for(let y=0;y<H;y++){ const idx=(y*W+i)*4; sum+=0.299*data[idx]+0.587*data[idx+1]+0.114*data[idx+2]; cnt++; } }
    profile[i]=sum/cnt;
  }
  // suavizado simple
  const smooth=new Float32Array(n);
  for(let i=0;i<n;i++){ let s=0,c=0; for(let d=-1;d<=1;d++){ const j=i+d; if(j>=0&&j<n){ s+=profile[j]; c++; } } smooth[i]=s/c; }
  const mean=smooth.reduce((a,b)=>a+b,0)/n;
  const std=Math.sqrt(smooth.reduce((a,b)=>a+(b-mean)**2,0)/n)||1;
  // detectar valles (líneas separadoras oscuras) con prominencia mínima y separación mínima
  const minGap=Math.max(3,Math.round(n*0.05));
  const valleys=[];
  for(let i=1;i<n-1;i++){
    if(smooth[i]<mean-std*0.35 && smooth[i]<=smooth[i-1] && smooth[i]<=smooth[i+1]){
      if(!valleys.length||i-valleys[valleys.length-1]>=minGap) valleys.push(i);
    }
  }
  const estimated=Math.max(1,Math.min(200,valleys.length+1));
  return {estimated,valles:valleys.length};
}

// ═══════════════════════════════════════════════════════════════════
// SAM MEJORADO: contorno preciso sobre la pieza tocada
// ═══════════════════════════════════════════════════════════════════
function samStatus(msg,show=true){ const el=document.getElementById("sam-status"); if(!el) return; el.style.display=show?"block":"none"; if(show) el.innerHTML=msg; }

function ensureSegCanvas(){
  const img=document.getElementById("bbox-img");
  if(!img||!img.naturalWidth) return false;
  const maxDim=600; // mayor resolución para mejor detección
  const sc=Math.min(1,maxDim/Math.max(img.naturalWidth,img.naturalHeight));
  _segW=Math.round(img.naturalWidth*sc); _segH=Math.round(img.naturalHeight*sc);
  if(!_segCanvas){ _segCanvas=document.createElement("canvas"); _segCtx=_segCanvas.getContext("2d"); }
  _segCanvas.width=_segW; _segCanvas.height=_segH;
  _segCtx.drawImage(img,0,0,_segW,_segH);
  _segData=_segCtx.getImageData(0,0,_segW,_segH).data;
  return true;
}

function colorDist(r1,g1,b1,r2,g2,b2){ return Math.sqrt((r1-r2)**2+(g1-g2)**2+(b1-b2)**2); }

// Flood-fill adaptativo: usa tolerancia variable según la varianza local
function floodFill(startX,startY,threshold){
  const W=_segW, H=_segH, data=_segData;
  const idx0=(startY*W+startX)*4;
  // Muestra color promedio en parche 5×5 para robustez
  let rSum=0,gSum=0,bSum=0,cnt=0;
  for(let dy=-2;dy<=2;dy++) for(let dx=-2;dx<=2;dx++){
    const nx=startX+dx, ny=startY+dy;
    if(nx>=0&&nx<W&&ny>=0&&ny<H){ const i=(ny*W+nx)*4; rSum+=data[i]; gSum+=data[i+1]; bSum+=data[i+2]; cnt++; }
  }
  const mr=rSum/cnt, mg=gSum/cnt, mb=bSum/cnt;
  const visited=new Uint8Array(W*H);
  const mask=new Uint8Array(W*H);
  const stack=[[startX,startY]];
  let count=0;
  const cap=W*H*0.7; // si se desborda más allá, es fondo, no la pieza
  let overflowed=false;
  while(stack.length){
    const [x,y]=stack.pop();
    if(x<0||x>=W||y<0||y>=H) continue;
    const pi=y*W+x;
    if(visited[pi]) continue;
    visited[pi]=1;
    const di=pi*4;
    if(colorDist(data[di],data[di+1],data[di+2],mr,mg,mb)>threshold) continue;
    mask[pi]=1; count++;
    if(count>cap){ overflowed=true; break; }
    stack.push([x+1,y],[x-1,y],[x,y+1],[x,y-1]);
  }
  return {mask,count,overflowed};
}

function nearestActivePixel(bin,W,H,tx,ty,maxR){
  maxR=maxR||Math.max(W,H);
  if(tx>=0&&tx<W&&ty>=0&&ty<H&&bin[ty*W+tx]) return{x:tx,y:ty};
  for(let r=1;r<=maxR;r++){
    for(let dx=-r;dx<=r;dx++) for(let dy=-r;dy<=r;dy++){
      if(Math.max(Math.abs(dx),Math.abs(dy))!==r) continue;
      const x=tx+dx,y=ty+dy;
      if(x>=0&&x<W&&y>=0&&y<H&&bin[y*W+x]) return{x,y};
    }
  }
  return null;
}

// Extrae el componente conectado más grande que contenga el punto tocado
function extractLargestConnectedComponent(mask,W,H,tapX,tapY){
  const visited=new Uint8Array(W*H);
  let bestComp=null, bestSize=0;
  // Primero probar con el componente que contiene el punto tocado
  const seedX=Math.round(tapX), seedY=Math.round(tapY);
  const near=nearestActivePixel(mask,W,H,seedX,seedY,30);
  if(near){
    const comp=bfsMask(mask,visited,W,H,near.x,near.y);
    if(comp.size>20) return comp.pixels;
  }
  // Fallback: componente más grande
  for(let y=0;y<H;y+=2) for(let x=0;x<W;x+=2){
    if(mask[y*W+x]&&!visited[y*W+x]){
      const comp=bfsMask(mask,visited,W,H,x,y);
      if(comp.size>bestSize){ bestSize=comp.size; bestComp=comp; }
    }
  }
  return bestComp?bestComp.pixels:null;
}

function bfsMask(mask,visited,W,H,sx,sy){
  const stack=[[sx,sy]]; const pixels=new Uint8Array(W*H); let size=0;
  while(stack.length){
    const [x,y]=stack.pop();
    if(x<0||x>=W||y<0||y>=H) continue;
    const pi=y*W+x;
    if(visited[pi]||!mask[pi]) continue;
    visited[pi]=1; pixels[pi]=1; size++;
    if(size>W*H*0.7) break;
    stack.push([x+1,y],[x-1,y],[x,y+1],[x,y-1]);
  }
  return{pixels,size};
}

function maskToContour(mask,W,H,tapX,tapY){
  // Obtener solo el componente conectado que el usuario tocó
  const comp=extractLargestConnectedComponent(mask,W,H,tapX,tapY);
  if(!comp) return null;
  // Encontrar punto de inicio del contorno (borde del componente)
  let sx=-1,sy=-1;
  const near=nearestActivePixel(comp,W,H,Math.round(tapX),Math.round(tapY),W);
  if(near){ sx=near.x; sy=near.y; }
  if(sx<0){ for(let y=0;y<H&&sx<0;y++) for(let x=0;x<W;x++){ if(comp[y*W+x]){ sx=x; sy=y; break; } } }
  if(sx<0) return null;
  const dirs=[[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]];
  const contour=[]; let cx=sx,cy=sy,prevDir=6;
  const maxSteps=W*H*2; let steps=0;
  while(steps++<maxSteps){
    contour.push({x:cx,y:cy});
    let found=false;
    for(let i=0;i<8;i++){
      const d=(prevDir+6+i)%8;
      const nx=cx+dirs[d][0],ny=cy+dirs[d][1];
      if(nx>=0&&nx<W&&ny>=0&&ny<H&&comp[ny*W+nx]){ cx=nx; cy=ny; prevDir=(d+4)%8; found=true; break; }
    }
    if(!found) break;
    if(cx===sx&&cy===sy&&contour.length>2) break;
    if(contour.length>6000) break;
  }
  if(contour.length<8) return null;
  const eps=Math.max(2,Math.min(W,H)*0.008);
  return douglasPeucker(contour,eps);
}

function douglasPeucker(pts,eps){
  if(pts.length<3) return pts;
  const keep=new Uint8Array(pts.length); keep[0]=1; keep[pts.length-1]=1;
  const stack=[[0,pts.length-1]];
  while(stack.length){
    const [a,b]=stack.pop();
    let maxD=0,idx=-1;
    const ax=pts[a].x,ay=pts[a].y,bx=pts[b].x,by=pts[b].y;
    const dx=bx-ax,dy=by-ay,len=Math.hypot(dx,dy)||1;
    for(let i=a+1;i<b;i++){
      const d=Math.abs((pts[i].x-ax)*dy-(pts[i].y-ay)*dx)/len;
      if(d>maxD){ maxD=d; idx=i; }
    }
    if(maxD>eps&&idx>0){ keep[idx]=1; stack.push([a,idx],[idx,b]); }
  }
  const out=[];
  for(let i=0;i<pts.length;i++) if(keep[i]) out.push(pts[i]);
  if(out.length>100){ const step=Math.ceil(out.length/100); return out.filter((_,i)=>i%step===0); }
  return out;
}

// Pulso visual en el punto tocado
function showTapRipple(canvasX,canvasY){
  const vp=document.getElementById("zoom-viewport");
  if(!vp) return;
  const vpRect=vp.getBoundingClientRect();
  const canvRect=canvas.getBoundingClientRect();
  const scaleX=canvRect.width/canvas.width, scaleY=canvRect.height/canvas.height;
  const screenX=canvRect.left+canvasX*scaleX-vpRect.left;
  const screenY=canvRect.top+canvasY*scaleY-vpRect.top;
  const ring=document.createElement("div");
  ring.className="sam-highlight-ring";
  ring.style.cssText=`left:${screenX}px;top:${screenY}px;`;
  vp.appendChild(ring);
  setTimeout(()=>ring.remove(),600);
}

async function samTap(e){
  if(!selectedFile){ showToast("⚠️ Toma o carga una foto primero","err"); return; }
  samStatus("⏳ Segmentando pieza…");
  const p=getPos(e);
  // Mostrar pulso visual en el punto exacto tocado
  showTapRipple(p.x,p.y);
  try{
    if(!ensureSegCanvas()){ samStatus("❌ No se pudo procesar la imagen"); return; }
    const sx=Math.round(p.x*(_segW/imgDispW));
    const sy=Math.round(p.y*(_segH/imgDispH));
    if(sx<0||sx>=_segW||sy<0||sy>=_segH){ samStatus("⚠️ Toca dentro de la imagen"); return; }
    // Intentar con tolerancia progresiva, rechazando desbordes al fondo
    let mask=null, count=0;
    for(const thr of [16,22,30,38,48,60,75]){
      const res=floodFill(sx,sy,thr);
      if(res.overflowed) continue; // ese umbral ya se comió el fondo, seguir con el siguiente
      if(res.count>=25){ mask=res.mask; count=res.count; break; }
    }
    let contour=null;
    if(mask&&count>=25) contour=maskToContour(mask,_segW,_segH,sx,sy);
    if(!contour||contour.length<3){
      // Fallback: nunca dejar el toque sin respuesta — caja centrada en el punto tocado
      const fbSizeX=Math.min(_segW*0.35,180), fbSizeY=Math.min(_segH*0.35,180);
      const fx0=Math.max(0,sx-fbSizeX/2), fy0=Math.max(0,sy-fbSizeY/2);
      const scX0=imgDispW/_segW, scY0=imgDispH/_segH;
      const fbBox={x:fx0*scX0,y:fy0*scY0,w:fbSizeX*scX0,h:fbSizeY*scY0};
      const id0=Date.now(); const color0=COLORS[annotations.length%COLORS.length];
      const clase0=resolveClaseForAnnotation();
      const pending0=!currentClase;
      annotations.push({id:id0,clase:clase0,type:"bbox",bbox:fbBox,color:color0,checked:true,qty:null,fromSam:true,fromSamFallback:true,pendingAutoClass:pending0});
      redraw(); renderAnnoList(); updateButtons();
      samStatus("⚠️ Contorno automático no claro — se colocó un cuadro sobre el punto tocado, ajústalo con las esquinas si es necesario.");
      if(pending0) classifyAnnotationLocal(id0);
      else if(!arrumeMode) showQtyPromptAt(id0,fbBox);
      else{ bumpArrume(); showToast(`🔗 +1 ${clase0} (${arrumeCount})`,"ok"); }
      return;
    }
    const scX=imgDispW/_segW, scY=imgDispH/_segH;
    const points=contour.map(pt=>({x:pt.x*scX,y:pt.y*scY}));
    // Verificar que el contorno cubre el punto tocado (corrección de posición)
    const bboxPts={minX:Math.min(...points.map(p=>p.x)),maxX:Math.max(...points.map(p=>p.x)),minY:Math.min(...points.map(p=>p.y)),maxY:Math.max(...points.map(p=>p.y))};
    const id=Date.now(); const color=COLORS[annotations.length%COLORS.length];
    const clase=resolveClaseForAnnotation();
    const pending=!currentClase;
    annotations.push({id,clase,type:"polygon",points,color,checked:true,qty:null,fromSam:true,pendingAutoClass:pending,_bbox:bboxPts});
    redraw(); renderAnnoList(); updateButtons();
    if(arrumeMode){ bumpArrume(); samStatus(`🔗 +1 ${clase} (${arrumeCount}) · toca otra pieza`); }
    else{ samStatus(`✅ Contorno trazado sobre pieza · ${pending?"identificando…":"toca otra o revisa"}`); }
    if(pending) classifyAnnotationLocal(id);
    else if(!arrumeMode) showQtyPromptAt(id,bboxPts);
  }catch(err){
    console.error("Auto-seg:",err);
    samStatus(`❌ Error: ${(err.message||err).toString().slice(0,80)}`);
  }
}

// Auto-detección del contorno real de la pieza (sin toque manual):
// prueba varios puntos semilla y se queda con el componente de tamaño
// más plausible para una pieza (evita fondo completo o ruido pequeño).
function autoDetectPieceContour(){
  if(!ensureSegCanvas()) return null;
  const W=_segW,H=_segH;
  const seeds=[[0.5,0.5],[0.5,0.4],[0.5,0.6],[0.4,0.5],[0.6,0.5],[0.35,0.4],[0.65,0.6],[0.5,0.3]];
  let best=null,bestScore=-1,bestSeed=null;
  for(const [fx,fy] of seeds){
    const sx=Math.min(W-1,Math.max(0,Math.round(fx*W))), sy=Math.min(H-1,Math.max(0,Math.round(fy*H)));
    for(const thr of [26,36,48]){
      const res=floodFill(sx,sy,thr);
      if(res.overflowed) continue;
      const areaFrac=res.count/(W*H);
      if(areaFrac<0.05||areaFrac>0.85) continue;
      const score=1-Math.abs(areaFrac-0.42);
      if(score>bestScore){ bestScore=score; best=res.mask; bestSeed=[sx,sy]; }
      break;
    }
  }
  if(!best) return null;
  const contour=maskToContour(best,W,H,bestSeed[0],bestSeed[1]);
  if(!contour||contour.length<3) return null;
  const scX=imgDispW/W, scY=imgDispH/H;
  return contour.map(pt=>({x:pt.x*scX,y:pt.y*scY}));
}

// ─── Redraw ───────────────────────────────────────────────────────
function redraw(){
  const ctx=canvas.getContext("2d");
  ctx.clearRect(0,0,canvas.width,canvas.height);
  annotations.forEach(a=>{
    if(!a.checked) return;
    ctx.strokeStyle=a.color; ctx.lineWidth=2.5; ctx.globalAlpha=1;
    if(a.type==="bbox"){
      const b=a.bbox;
      ctx.fillStyle="rgba(0,0,0,0.2)";
      ctx.fillRect(0,0,canvas.width,b.y);
      ctx.fillRect(0,b.y+b.h,canvas.width,canvas.height-b.y-b.h);
      ctx.fillRect(0,b.y,b.x,b.h);
      ctx.fillRect(b.x+b.w,b.y,canvas.width-b.x-b.w,b.h);
      ctx.strokeRect(b.x,b.y,b.w,b.h);
      drawCorners(ctx,b.x,b.y,b.w,b.h,a.color);
      drawLabel(ctx,a.clase,b.x,b.y,a.color);
    } else if(a.type==="polygon"){
      const pts=a.points;
      ctx.beginPath(); ctx.moveTo(pts[0].x,pts[0].y);
      pts.forEach(p=>ctx.lineTo(p.x,p.y)); ctx.closePath();
      ctx.fillStyle=a.color+"2a"; ctx.fill(); ctx.stroke();
      // Solo dibujar vértices si son pocos (no en SAM con muchos puntos)
      if(pts.length<=30) pts.forEach(p=>{ ctx.beginPath(); ctx.arc(p.x,p.y,3,0,Math.PI*2); ctx.fillStyle=a.color; ctx.fill(); });
      // Label en el centroide de la pieza
      const cx=pts.reduce((s,p)=>s+p.x,0)/pts.length;
      const cy=pts.reduce((s,p)=>s+p.y,0)/pts.length;
      const minY=Math.min(...pts.map(p=>p.y));
      drawLabel(ctx,a.clase,cx-ctx.measureText(a.clase).width/2-5,minY,a.color);
    }
  });
  if(bboxCurrent&&bboxDrawing){
    ctx.strokeStyle="rgba(255,255,255,.8)"; ctx.lineWidth=2; ctx.setLineDash([6,3]);
    ctx.strokeRect(bboxCurrent.x,bboxCurrent.y,bboxCurrent.w,bboxCurrent.h);
    ctx.setLineDash([]);
  }
  if(cornerState){
    const pts=cornerPolygonPoints();
    if(pts){
      ctx.strokeStyle="#f59e0b"; ctx.lineWidth=2.5; ctx.setLineDash(cornerDrawing?[6,3]:[]);
      ctx.beginPath(); ctx.moveTo(pts[0].x,pts[0].y);
      pts.forEach(p=>ctx.lineTo(p.x,p.y)); ctx.closePath();
      ctx.fillStyle="rgba(245,158,11,.15)"; ctx.fill(); ctx.stroke();
      ctx.setLineDash([]);
      pts.forEach(p=>{ ctx.beginPath(); ctx.arc(p.x,p.y,4,0,Math.PI*2); ctx.fillStyle="#f59e0b"; ctx.fill(); });
    }
  }
  if(polyPoints.length){
    ctx.strokeStyle="rgba(255,255,255,.9)"; ctx.lineWidth=2; ctx.setLineDash([5,3]);
    ctx.beginPath(); ctx.moveTo(polyPoints[0].x,polyPoints[0].y);
    polyPoints.forEach(p=>ctx.lineTo(p.x,p.y));
    if(polyPreview) ctx.lineTo(polyPreview.x,polyPreview.y);
    ctx.stroke(); ctx.setLineDash([]);
    polyPoints.forEach((p,i)=>{ ctx.beginPath(); ctx.arc(p.x,p.y,i===0?6:4,0,Math.PI*2); ctx.fillStyle=i===0?"#f59e0b":"#fff"; ctx.fill(); });
  }
}
function drawCorners(ctx,x,y,w,h,color){ const cs=12; ctx.strokeStyle=color; ctx.lineWidth=4; [[x,y],[x+w,y],[x,y+h],[x+w,y+h]].forEach(([cx,cy])=>{ const dx=cx===x?1:-1,dy=cy===y?1:-1; ctx.beginPath(); ctx.moveTo(cx+dx*cs,cy); ctx.lineTo(cx,cy); ctx.lineTo(cx,cy+dy*cs); ctx.stroke(); }); }
function drawLabel(ctx,text,x,y,color){
  ctx.font="bold 12px -apple-system,sans-serif";
  const tw=ctx.measureText(text).width;
  const lx=Math.max(0,Math.min(canvas.width-tw-12,x));
  const ly=Math.max(18,y-4);
  ctx.fillStyle=color+"dd"; ctx.fillRect(lx,ly-16,tw+10,20);
  ctx.fillStyle="#000"; ctx.fillText(text,lx+5,ly-2);
}
function checkClase(){ if(!currentClase){ showToast("⚠️ Selecciona una clase primero","err"); return false; } return true; }

// ─── Lista anotaciones ────────────────────────────────────────────
function renderAnnoList(){
  const list=document.getElementById("anno-list"); const card=document.getElementById("annos-card"); const title=document.getElementById("annos-title");
  if(!annotations.length){ card.style.display="none"; return; }
  card.style.display="block"; title.textContent=`📦 Anotaciones (${annotations.length})`;
  list.innerHTML="";
  annotations.forEach(a=>{
    const item=document.createElement("div"); item.className="anno-item";
    const qtyBadge=a.qty?`<span style="background:rgba(34,197,94,.2);color:var(--ok);border:1px solid rgba(34,197,94,.3);border-radius:6px;padding:2px 7px;font-size:10px;font-weight:700">×${a.qty}</span>`:"";
    item.innerHTML=`<div class="anno-color" style="background:${a.color}"></div>
      <span class="anno-label" onclick="reassignClass(${a.id})" style="cursor:pointer;text-decoration:underline dotted;text-underline-offset:3px" title="Cambiar clase">${a.clase}</span>
      <span class="anno-type">${a.type==="polygon"?"🔷 Polígono":"⬜ BBox"}</span>
      ${qtyBadge}
      <span class="anno-check" onclick="toggleAnno(${a.id})">${a.checked?"✅":"☐"}</span>
      <span class="anno-del" onclick="deleteAnno(${a.id})">🗑️</span>`;
    list.appendChild(item);
  });
}
function toggleAnno(id){ const a=annotations.find(x=>x.id===id); if(a){a.checked=!a.checked;renderAnnoList();redraw();} }
function deleteAnno(id){ annotations=annotations.filter(x=>x.id!==id); renderAnnoList(); redraw(); updateButtons(); }
function updateButtons(){ const has=annotations.some(a=>a.checked); document.getElementById("btn-review").disabled=!has; document.getElementById("btn-upload").disabled=!has; }

// ═══════════════════════════════════════════════════════════════════
// QTY PROMPT: aparece cerca de la anotación (no en posición fija)
// ═══════════════════════════════════════════════════════════════════
function annotationBounds(a){
  if(!a) return null;
  if(a.type==="bbox") return{...a.bbox};
  if(a._bbox) return{x:a._bbox.minX,y:a._bbox.minY,w:a._bbox.maxX-a._bbox.minX,h:a._bbox.maxY-a._bbox.minY};
  if(a.type==="polygon"&&a.points?.length){ const xs=a.points.map(p=>p.x),ys=a.points.map(p=>p.y); return{x:Math.min(...xs),y:Math.min(...ys),w:Math.max(...xs)-Math.min(...xs),h:Math.max(...ys)-Math.min(...ys)}; }
  return null;
}

function showQtyPromptAt(annoId, bboxHint){
  const ex=document.getElementById("qty-prompt"); if(ex) ex.remove();
  const anno0=annotations.find(a=>a.id===annoId);
  const box0=bboxHint||(anno0?annotationBounds(anno0):null);
  let est=null;
  if(box0&&box0.w>25&&box0.h>25){ try{ est=estimateArrumeCount(box0); }catch(_){} }
  const div=document.createElement("div"); div.id="qty-prompt"; div.className="float-panel"; div.style.width="270px";
  div.innerHTML=`<div class="fp-head" id="qty-head"><span style="flex:1">📦 ¿Cuántas piezas?</span><button class="fp-btn" onclick="document.getElementById('qty-prompt').classList.toggle('min')">▁</button><button class="fp-btn" onclick="skipQty()">✕</button></div>
    <div class="fp-body">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
        <input type="number" id="qty-input" placeholder="Cantidad" min="1" max="999" value="${est&&est.estimated>1?est.estimated:""}" style="flex:1;background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:9px 12px;color:var(--text);font-size:16px;outline:none;margin:0">
        <span style="font-size:12px;color:var(--steel)">piezas</span>
      </div>
      ${est&&est.estimated>1?`<div style="font-size:10px;color:var(--amber);margin-bottom:8px">🔢 Estimado automático del arrume (líneas separadoras): ${est.estimated}. Ajusta si es necesario.</div>`:""}
      <div style="display:flex;gap:6px">
        <button onclick="skipQty()" style="flex:1;padding:9px;border-radius:8px;border:1.5px solid var(--border);background:var(--surface);color:var(--text2);font-size:12px;font-weight:600;cursor:pointer">Sin cantidad</button>
        <button onclick="addQty(${annoId})" style="flex:1;padding:9px;border-radius:8px;border:none;background:var(--amber);color:#0a1628;font-size:12px;font-weight:700;cursor:pointer">✅ Agregar</button>
      </div>
      <div style="font-size:10px;color:var(--steel);margin-top:6px;text-align:center">☝️ Arrastra para mover</div>
    </div>`;
  document.body.appendChild(div);
  // Posicionar cerca de la anotación en pantalla
  const anno=annotations.find(a=>a.id===annoId);
  const b=bboxHint||(anno?annotationBounds(anno):null);
  if(b){
    const canvRect=canvas.getBoundingClientRect();
    const vp=document.getElementById("zoom-viewport");
    const vpRect=vp?vp.getBoundingClientRect():canvRect;
    const scX=canvRect.width/canvas.width, scY=canvRect.height/canvas.height;
    // Centro X de la anotación en pantalla
    const annoScreenX=canvRect.left+(b.x+b.w/2)*scX;
    const annoScreenY=canvRect.top+(b.y+b.h)*scY+8; // debajo de la anotación
    const panelW=270, panelH=130;
    let left=Math.max(8,Math.min(window.innerWidth-panelW-8, annoScreenX-panelW/2));
    let top=Math.min(window.innerHeight-panelH-8, annoScreenY);
    if(top<70) top=canvRect.top+b.y*scY-panelH-8; // encima si no cabe debajo
    div.style.left=left+"px"; div.style.top=Math.max(70,top)+"px"; div.style.right="auto";
  }
  makeDraggable(div,document.getElementById("qty-head"));
  setTimeout(()=>document.getElementById("qty-input")?.focus(),100);
}
function showQtyPrompt(annoId){ showQtyPromptAt(annoId,null); } // compatibilidad
function skipQty(){ const p=document.getElementById("qty-prompt"); if(p) p.remove(); showToast("✅ Anotación añadida","ok"); }
function addQty(annoId){
  const qty=parseInt(document.getElementById("qty-input")?.value);
  const p=document.getElementById("qty-prompt"); if(p) p.remove();
  const anno=annotations.find(a=>a.id===annoId);
  if(!anno||!qty||qty<1){ showToast("✅ Añadida sin cantidad","ok"); return; }
  anno.qty=qty; anno.isArrume=true;
  const b=annotationBounds(anno);
  if(b){
    const qtyId=Date.now()+1;
    annotations.push({id:qtyId,clase:`QTY-${qty}`,type:"bbox",bbox:{x:b.x+4,y:b.y+4,w:Math.min(60,b.w*.25),h:Math.min(30,b.h*.2)},color:"#22c55e",checked:true,isQty:true,parentId:annoId});
  }
  redraw(); renderAnnoList(); updateButtons();
  showToast(`✅ ${anno.clase} × ${qty}`,"ok");
}
function addQtyBadgeForAnnotation(anno,qty){
  qty=Math.max(1,Math.round(+qty||1));
  anno.qty=qty; anno.isArrume=qty>1;
  const old=annotations.find(x=>x.isQty&&x.parentId===anno.id);
  if(old){ old.clase=`QTY-${qty}`; return; }
  const b=annotationBounds(anno); if(!b) return;
  annotations.push({id:Date.now()+Math.floor(Math.random()*999),clase:`QTY-${qty}`,type:"bbox",bbox:{x:b.x+4,y:b.y+4,w:Math.min(64,b.w*.28),h:Math.min(32,b.h*.22)},color:"#22c55e",checked:true,isQty:true,parentId:anno.id});
}

// ─── Review ───────────────────────────────────────────────────────
function openReview(){
  const img=document.getElementById("bbox-img"); const rImg=document.getElementById("review-img");
  rImg.src=img.src; rImg.onload=()=>drawReviewCanvas(); if(rImg.complete) drawReviewCanvas();
  const annos=document.getElementById("review-annos"); annos.innerHTML="";
  annotations.forEach(a=>{
    const div=document.createElement("div"); div.className="review-anno "+(a.checked?"approved":"rejected"); div.id="rev-"+a.id;
    div.innerHTML=`<span class="review-check" onclick="toggleReviewAnno(${a.id})">${a.checked?"✅":"❌"}</span>
      <div style="flex:1"><div style="font-family:monospace;font-weight:700;font-size:14px;color:${a.color}">${a.clase}</div>
      <div style="font-size:11px;color:var(--steel)">${a.type==="polygon"?"🔷 Polígono":"⬜ BBox"} ${a.qty?"· ×"+a.qty+" piezas":""}</div></div>`;
    annos.appendChild(div);
  });
  document.getElementById("review-modal-bg").classList.add("show");
}
function toggleReviewAnno(id){ const a=annotations.find(x=>x.id===id); if(!a) return; a.checked=!a.checked; const div=document.getElementById("rev-"+id); div.className="review-anno "+(a.checked?"approved":"rejected"); div.querySelector(".review-check").textContent=a.checked?"✅":"❌"; renderAnnoList(); redraw(); drawReviewCanvas(); updateButtons(); }
function drawReviewCanvas(){
  const rImg=document.getElementById("review-img"); const rc=document.getElementById("review-canvas");
  rc.width=rImg.offsetWidth; rc.height=rImg.offsetHeight;
  const scX=rImg.offsetWidth/imgDispW, scY=rImg.offsetHeight/imgDispH;
  const ctx=rc.getContext("2d"); ctx.clearRect(0,0,rc.width,rc.height);
  annotations.filter(a=>a.checked).forEach(a=>{
    ctx.strokeStyle=a.color; ctx.lineWidth=2.5;
    if(a.type==="bbox"){ const b={x:a.bbox.x*scX,y:a.bbox.y*scY,w:a.bbox.w*scX,h:a.bbox.h*scY}; ctx.strokeRect(b.x,b.y,b.w,b.h); drawLabel(ctx,a.clase,b.x,b.y,a.color); }
    else if(a.type==="polygon"){ const pts=a.points.map(p=>({x:p.x*scX,y:p.y*scY})); ctx.beginPath(); ctx.moveTo(pts[0].x,pts[0].y); pts.forEach(p=>ctx.lineTo(p.x,p.y)); ctx.closePath(); ctx.fillStyle=a.color+"33"; ctx.fill(); ctx.stroke(); const cx=pts.reduce((s,p)=>s+p.x,0)/pts.length; const minY=Math.min(...pts.map(p=>p.y)); drawLabel(ctx,a.clase,cx,minY,a.color); }
  });
}
function closeReviewModal(e){ if(e.target===document.getElementById("review-modal-bg")) closeReviewModalDirect(); }
function closeReviewModalDirect(){ document.getElementById("review-modal-bg").classList.remove("show"); }
function confirmAndUpload(){ closeReviewModalDirect(); uploadAll(); }

// ─── Catálogo modal ───────────────────────────────────────────────
function openCatModal(){ catModalFam="ALL"; document.getElementById("cat-modal-bg").classList.add("show"); document.getElementById("cat-modal-search").value=""; renderCatModalFams(); renderCatModal(""); setTimeout(()=>document.getElementById("cat-modal-search").focus(),100); }
function closeCatModal(e){ if(e.target===document.getElementById("cat-modal-bg")) closeCatModalDirect(); }
function closeCatModalDirect(){ document.getElementById("cat-modal-bg").classList.remove("show"); }
function renderCatModalFams(){ const w=document.getElementById("cat-modal-families"); w.innerHTML=""; ["ALL","PM","PB","EI","EE"].forEach(f=>{const b=document.createElement("div");b.className="fam-btn"+(f===catModalFam?" active":"");b.textContent=f==="ALL"?"Todas":f;b.onclick=()=>{catModalFam=f;renderCatModalFams();renderCatModal(document.getElementById("cat-modal-search").value);};w.appendChild(b);}); }
function renderCatModal(q){ const list=document.getElementById("cat-modal-list"); list.innerHTML=""; CATALOG.filter(c=>(catModalFam==="ALL"||c.family===catModalFam)&&(!q||c.code.toLowerCase().includes(q.toLowerCase()))).slice(0,60).forEach(c=>{ const item=document.createElement("div"); item.className="cat-item"; item.innerHTML=`<div onclick="setClase('${c.code}')"><div class="ci-code">${c.code}</div><div class="ci-spec">${c.spec}</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('${c.code}')">📋</span>`; list.appendChild(item); }); }
renderCatModalFams(); renderCatModal("");
function renderCatalogPage(q){
  const fw=document.getElementById("cat-main-families"); fw.innerHTML="";
  ["ALL","PM","PB","EI","EE"].forEach(f=>{const b=document.createElement("div");b.className="fam-btn"+(f===catPageFam?" active":"");b.textContent=f==="ALL"?"Todas":f;b.onclick=()=>{catPageFam=f;renderCatalogPage(document.getElementById("cat-main-search").value);};fw.appendChild(b);});
  const g=document.getElementById("cat-main-grid"); g.innerHTML="";
  CATALOG.filter(c=>(catPageFam==="ALL"||c.family===catPageFam)&&(!q||c.code.toLowerCase().includes(q.toLowerCase()))).slice(0,80).forEach(c=>{
    const card=document.createElement("div"); card.className="ref-card";
    card.innerHTML=`<div class="ref-fam ${c.family}">${c.family}</div><div class="ref-info"><div class="ref-code">${c.code}</div><div class="ref-spec">${c.spec}</div></div><span class="ref-copy" onclick="copyCode('${c.code}')">📋</span>`;
    g.appendChild(card);
  });
}
function copyCode(code){ navigator.clipboard?.writeText(code).then(()=>showToast(`📋 ${code}`,"ok")).catch(()=>{ const t=document.createElement("textarea"); t.value=code; document.body.appendChild(t); t.select(); document.execCommand("copy"); document.body.removeChild(t); showToast(`📋 ${code}`,"ok"); }); }

// ─── Upload ───────────────────────────────────────────────────────
async function uploadAll(){
  const apiKey=document.getElementById("api-key").value.trim();
  const split=document.getElementById("split").value;
  const checked=annotations.filter(a=>a.checked);
  if(!apiKey){ showToast("⚠️ Ingresa tu API Key Roboflow","err"); return; }
  if(!selectedFile){ showToast("⚠️ Selecciona imagen","err"); return; }
  if(!checked.length){ showToast("⚠️ Marca al menos una anotación","err"); return; }
  const btn=document.getElementById("btn-upload"),btnR=document.getElementById("btn-review");
  btn.disabled=true; btnR.disabled=true; btn.innerHTML="⏳ Subiendo…"; btn.classList.add("loading");
  const pw=document.getElementById("prog-wrap"),pb=document.getElementById("prog-bar");
  pw.classList.add("show"); pb.style.width="15%";
  const logId=Date.now();
  const ext=selectedFile.name.split(".").pop()||"jpg";
  const baseName=checked.filter(a=>!a.isQty).map(a=>a.clase).join("_")+"_"+logId+"."+ext;
  const previewUrl=URL.createObjectURL(selectedFile);
  try{
    const b64=await fileToB64(selectedFile); pb.style.width="40%";
    const upRes=await fetchWithTimeout(`https://api.roboflow.com/dataset/${PROJECT}/upload?api_key=${apiKey}&name=${encodeURIComponent(baseName)}&split=${split}`,{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:b64.split(",")[1]},30000);
    const upData=await upRes.json();
    if(!upRes.ok||upData.error) throw new Error(upData.error||`HTTP ${upRes.status}`);
    pb.style.width="65%";
    const imageId=upData.id||"";
    if(imageId){
      const scX=imgNatW/imgDispW,scY=imgNatH/imgDispH;
      const annoPayload={width:imgNatW,height:imgNatH,boxes:[]};
      checked.forEach(a=>{
        if(a.type==="bbox"){ const b=a.bbox; annoPayload.boxes.push({label:a.clase,x:(b.x+b.w/2)*scX/imgNatW,y:(b.y+b.h/2)*scY/imgNatH,w:b.w*scX/imgNatW,h:b.h*scY/imgNatH}); }
        else if(a.type==="polygon"){ annoPayload.boxes.push({label:a.clase,points:a.points.map(p=>({x:p.x*scX/imgNatW,y:p.y*scY/imgNatH}))}); }
      });
      const annoRes=await fetchWithTimeout(`https://api.roboflow.com/dataset/${PROJECT}/annotate/${imageId}?api_key=${apiKey}&name=${encodeURIComponent(baseName)}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(annoPayload)},30000);
      const annoData=await annoRes.json(); if(annoData.error) console.warn("Anotación:",annoData.error);
    }
    pb.style.width="100%";
    sessionCount++; totalCount++; okCount++;
    localStorage.setItem("rf_total",totalCount); localStorage.setItem("rf_ok",okCount);
    document.getElementById("cnt-session").textContent=sessionCount;
    document.getElementById("cnt-total").textContent=totalCount;
    document.getElementById("cnt-ok").textContent=okCount;
    const entry={id:logId,url:previewUrl,annos:checked.map(a=>({clase:a.clase,color:a.color,type:a.type})),split,ok:true,file:selectedFile,imageId};
    uploadLog.unshift(entry); addLogItem(entry);
    checked.filter(a=>!a.isQty).forEach(a=>addReciente(a.clase));
    const uniqueClasses=[...new Set(checked.filter(a=>!a.isQty).map(a=>a.clase))];
    uniqueClasses.forEach(c=>{ classCounts[c]=(classCounts[c]||0)+1; });
    localStorage.setItem("rf_class_counts",JSON.stringify(classCounts));
    renderClassStats(); updateMemoryFromUpload(checked);
    checked.filter(a=>!a.isQty).forEach(a=>{
      const codeUp=String(a.clase||"").toUpperCase();
      if(!CATALOG_MAP[codeUp]) return;
      let hash=a._hash;
      if(!hash){ try{ const box=annotationBounds(a); const loc=localImageAnalysis(box); if(loc&&loc._cv) hash=computeFingerprintFromCanvas(loc._cv); }catch(_){} }
      if(hash) learnPiece(hash,codeUp,{familia:CATALOG_MAP[codeUp].family});
    });
    showToast(`✅ ${checked.length} anotación(es) → Dataset`,"ok"); resetAll();
  }catch(err){
    pb.style.background="var(--danger)";
    uploadLog.unshift({id:logId,url:previewUrl,annos:checked.map(a=>({clase:a.clase,color:a.color})),split,ok:false,error:err.message,file:selectedFile});
    addLogItem(uploadLog[0]); showToast(`❌ ${err.message.slice(0,50)}`,"err");
    setTimeout(()=>{pb.style.background="var(--amber)";pb.style.width="0%";pw.classList.remove("show");},2000);
  }finally{
    setTimeout(()=>{pb.style.width="0%";pw.classList.remove("show");},1500);
    btn.disabled=false; btnR.disabled=false; btn.innerHTML="⬆️ Subir"; btn.classList.remove("loading"); updateButtons();
  }
}
function fileToB64(f){ return new Promise((res,rej)=>{ const r=new FileReader(); r.onload=()=>res(r.result); r.onerror=()=>rej(new Error("Error")); r.readAsDataURL(f); }); }
function discardPhoto(){
  if(!selectedFile) return;
  const nAnnos=annotations.length;
  if(!confirm(nAnnos?`¿Descartar foto y ${nAnnos} anotación(es)?`:"¿Descartar foto?")) return;
  resetAll(); showToast("🗑️ Foto descartada","ok");
}
function resetAll(){
  selectedFile=null; annotations=[]; bboxCurrent=null; bboxDrawing=false;
  cancelPolygon(); cornerCancel();
  document.getElementById("capture-zone").classList.remove("has-img");
  document.getElementById("bbox-section").style.display="none";
  document.getElementById("annos-card").style.display="none";
  document.getElementById("file-input-cam").value=""; document.getElementById("file-input-gal").value="";
  canvas.getContext("2d").clearRect(0,0,canvas.width,canvas.height);
  _segCanvas=null; _segData=null; samStatus("",false);
  arrumeCount=0; const ac=document.getElementById("arrume-counter"); if(ac) ac.textContent="×0";
  updateButtons();
}

// ─── Log ──────────────────────────────────────────────────────────
function addLogItem(entry){
  const list=document.getElementById("log-list"); if(list.querySelector("p")) list.innerHTML="";
  const item=document.createElement("div"); item.className="log-item"+(entry.ok?"":" error"); item.id="log-"+entry.id;
  const tags=(entry.annos||[]).map(a=>`<span class="log-anno-tag" style="background:${a.color}22;color:${a.color};border:1px solid ${a.color}44">${a.type==="polygon"?"🔷":"⬜"} ${a.clase}</span>`).join("");
  item.innerHTML=`<div class="log-header"><img class="log-thumb" src="${entry.url}" alt=""><div class="log-info"><div class="log-name">${(entry.annos||[]).length} anotación(es)</div><div class="log-meta">${entry.ok?"✓ "+entry.split:"✗ "+(entry.error||"")}</div><div class="log-annos">${tags}</div></div><div class="log-actions"><span style="cursor:pointer;font-size:18px" onclick="retryEntry(${entry.id})">🔄</span><span style="cursor:pointer;font-size:18px" onclick="deleteEntry(${entry.id})">🗑️</span><span>${entry.ok?"✅":"❌"}</span></div></div>`;
  list.insertBefore(item,list.firstChild);
}
async function retryEntry(id){
  const apiKey=document.getElementById("api-key").value.trim();
  const entry=uploadLog.find(e=>e.id===id);
  if(!entry||!apiKey){ showToast("⚠️ Falta API Key","err"); return; }
  showToast("🔄 Reintentando…","");
  try{
    const b64=await fileToB64(entry.file);
    const name=(entry.annos||[]).map(a=>a.clase).join("_")+"_retry_"+Date.now()+".jpg";
    const res=await fetchWithTimeout(`https://api.roboflow.com/dataset/${PROJECT}/upload?api_key=${apiKey}&name=${encodeURIComponent(name)}&split=${entry.split}`,{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:b64.split(",")[1]},30000);
    const data=await res.json(); if(!res.ok||data.error) throw new Error(data.error||`HTTP ${res.status}`);
    entry.ok=true; entry.imageId=data.id||"";
    const item=document.getElementById("log-"+id); item.classList.remove("error");
    item.querySelector(".log-meta").textContent="✓ "+entry.split+" (reintento ✔)";
    item.querySelector(".log-actions span:last-child").textContent="✅";
    showToast("✅ Reintento exitoso","ok");
  }catch(err){ showToast(`❌ ${err.message.slice(0,50)}`,"err"); }
}
async function deleteEntry(id){
  const apiKey=document.getElementById("api-key").value.trim();
  const entry=uploadLog.find(e=>e.id===id); if(!entry) return;
  if(!confirm("¿Eliminar imagen de Roboflow?")) return;
  if(entry.imageId&&apiKey){ try{ await fetch(`https://api.roboflow.com/dataset/${PROJECT}/images/${entry.imageId}?api_key=${apiKey}`,{method:"DELETE"}); }catch(e){} }
  document.getElementById("log-"+id)?.remove();
  uploadLog=uploadLog.filter(e=>e.id!==id);
  const list=document.getElementById("log-list");
  if(!list.children.length) list.innerHTML='<p style="color:var(--steel);font-size:13px;text-align:center;padding:20px">Las subidas aparecerán aquí</p>';
  showToast("🗑️ Eliminada","ok");
}

// ─── Descarga del propio HTML ─────────────────────────────────────
function downloadApp(){
  const html=document.documentElement.outerHTML;
  const blob=new Blob(['<!DOCTYPE html>\n'+html],{type:'text/html'});
  const url=URL.createObjectURL(blob);
  const a=document.createElement('a'); a.href=url; a.download='UNISPAN-Dataset-v16.html';
  document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url);
  showToast("⬇ Descargado como UNISPAN-Dataset-v16.html","ok");
}

// ─── Stats ────────────────────────────────────────────────────────
function toggleStats(){ const b=document.getElementById("stats-body"),c=document.getElementById("stats-caret"); const open=b.style.display==="none"; b.style.display=open?"block":"none"; c.textContent=open?"▲":"▼"; if(open) renderClassStats(); }
function renderClassStats(){
  const list=document.getElementById("stats-list");
  const total=Object.values(classCounts).reduce((a,b)=>a+b,0);
  document.getElementById("stats-total").textContent=`(${total} img · ${Object.keys(classCounts).length} clases)`;
  if(!list) return;
  const entries=Object.entries(classCounts).sort((a,b)=>b[1]-a[1]);
  if(!entries.length){ list.innerHTML='<div style="color:var(--steel);font-size:12px;text-align:center;padding:14px">Sin datos aún.</div>'; return; }
  list.innerHTML=entries.map(([code,n])=>{
    const pct=Math.min(100,Math.round(n/CLASS_GOAL*100)); const cls=n>=CLASS_GOAL?"ok":n<10?"low":""; const flag=n>=CLASS_GOAL?"✅":n<10?"⚠️":"";
    return `<div class="stat-row" style="flex-direction:column;align-items:stretch;gap:4px"><div style="display:flex;justify-content:space-between;align-items:center"><span class="stat-code">${flag} ${code}</span><span class="stat-count ${cls}">${n}/${CLASS_GOAL}</span></div><div class="stat-bar"><div class="stat-bar-fill" style="width:${pct}%;background:${cls==="ok"?"var(--ok)":cls==="low"?"var(--danger)":"var(--amber)"}"></div></div></div>`;
  }).join("");
}
function resetStats(){ if(!confirm("¿Reiniciar contador local?")) return; classCounts={}; localStorage.setItem("rf_class_counts","{}"); renderClassStats(); }
renderClassStats();

// ═══════════════════════════════════════════════════════════════════
// AGENTE EXPERTO — Base de conocimiento local UNISPAN
// ═══════════════════════════════════════════════════════════════════
const EXPERT_KB=[
 {t:"Lámina (cara de contacto)",k:["lamina","lámina","cara","contacto","superficie","acero","espesor","chapa"],
  a:"La <b>lámina</b> es la cara de contacto con el concreto. En paneles UNISPAN es de acero de 3–5 mm (típ. 3 mm en PM/PB). Se identifica por su superficie lisa continua, bordes soldados al marco perimetral y ausencia de perforaciones en la cara frontal (las perforaciones van en las <i>bridas</i>)."},
 {t:"Bridas / marco perimetral",k:["brida","bridas","marco","perimetral","canto","borde","perfil"],
  a:"Las <b>bridas</b> son los perfiles laterales que forman el marco perimetral. Contienen las <b>perforaciones para pasadores y grapas</b>. Franja perimetral de ~55–65 mm con agujeros equidistantes.<br>• PM/PB: brida plana circular + ranuras.<br>• EI: dos bridas a 90° hacia adentro.<br>• EE: dos bridas a 90° hacia afuera."},
 {t:"Platinas de unión",k:["platina","platinas","union","placa","enlace"],
  a:"Las <b>platinas</b> son placas metálicas planas soldadas que refuerzan uniones entre bridas. Son piezas puntuales (no corren todo el borde), suelen estar en esquinas con 2–4 perforaciones."},
 {t:"Refuerzos transversales",k:["transversal","costilla","horizontal","nervio","separacion"],
  a:"Perfiles tubulares 40×20 mm soldados perpendicularmente a la lámina en la cara posterior, de 3 a 6 por panel según el ancho. Separación entre ejes 200–300 mm. Más refuerzos = panel más ancho (PM vs PB)."},
 {t:"Refuerzo estructural principal",k:["estructural","principal","tubular","viga","rigidez"],
  a:"Par de perfiles principales (tubo 60×40 mm) que corren longitudinalmente. Un PM completo: 2 refuerzos longitudinales + 4–6 transversales."},
 {t:"Ángulos y esquineros EI/EE",k:["angulo","ángulo","esquina","esquinero","EI","EE","interior","exterior"],
  a:"• <b>EI (Esquina Interior)</b>: dos bridas hacia adentro, forman rincón interior. Línea de doblez central visible.<br>• <b>EE (Esquina Exterior)</b>: bridas hacia afuera, forman canto de muro.<br>Ambos tienen perforaciones simétricas. Códigos: EI/EE-{largo}x150x150."},
 {t:"Perforaciones frontales — identificar ancho",k:["frontal","frontales","cara frontal","brida corta","ancho","cuantos"],
  a:"<b>Frontales</b> = perforaciones en las bridas cortas (extremos).<br>Fórmula: <code>n_frontales = ancho_mm / 50</code><br>• 600mm ⇒ 12 · 500mm ⇒ 10 · 400mm ⇒ 8 · 300mm ⇒ 6 · 200mm ⇒ 4<br>Contar frontales es el camino más rápido para conocer el <b>ancho</b>."},
 {t:"Perforaciones laterales — identificar longitud",k:["lateral","laterales","canto","brida larga","longitud","largo"],
  a:"<b>Laterales</b> = perforaciones en las bridas largas.<br>Fórmula: <code>n_laterales = largo_mm / 50</code><br>• 2400mm ⇒ 48 · 1200mm ⇒ 24 · 900mm ⇒ 18 · 800mm ⇒ 16 · 600mm ⇒ 12"},
 {t:"Inicio y paso de perforaciones",k:["inicio","comienzo","primera","borde","25 mm","50 mm","paso","pitch"],
  a:"<b>Inicio:</b> 25 mm desde el borde al centro de la primera perforación.<br><b>Paso:</b> 50 mm entre centros.<br>Estos dos valores son la <b>firma dimensional UNISPAN</b> y aplican a bridas frontales y laterales."},
 {t:"Tabla de perforaciones por referencia",k:["tabla","referencia","lookup","cuantas","cuenta","matriz"],
  a:"<b>Frontales (por ancho) × Laterales (por largo):</b><br><table style='width:100%;border-collapse:collapse;font-size:11px;margin-top:6px'><tr style='background:#0b1220;color:var(--amber)'><th style='padding:4px;border:1px solid #334'>Ancho</th><th style='padding:4px;border:1px solid #334'>F</th><th style='padding:4px;border:1px solid #334'>Largo</th><th style='padding:4px;border:1px solid #334'>L</th></tr><tr><td style='padding:4px;border:1px solid #334'>600</td><td style='padding:4px;border:1px solid #334'>12</td><td style='padding:4px;border:1px solid #334'>2400</td><td style='padding:4px;border:1px solid #334'>48</td></tr><tr><td style='padding:4px;border:1px solid #334'>500</td><td style='padding:4px;border:1px solid #334'>10</td><td style='padding:4px;border:1px solid #334'>1200</td><td style='padding:4px;border:1px solid #334'>24</td></tr><tr><td style='padding:4px;border:1px solid #334'>450</td><td style='padding:4px;border:1px solid #334'>9</td><td style='padding:4px;border:1px solid #334'>900</td><td style='padding:4px;border:1px solid #334'>18</td></tr><tr><td style='padding:4px;border:1px solid #334'>400</td><td style='padding:4px;border:1px solid #334'>8</td><td style='padding:4px;border:1px solid #334'>800</td><td style='padding:4px;border:1px solid #334'>16</td></tr><tr><td style='padding:4px;border:1px solid #334'>300</td><td style='padding:4px;border:1px solid #334'>6</td><td style='padding:4px;border:1px solid #334'>750</td><td style='padding:4px;border:1px solid #334'>15</td></tr><tr><td style='padding:4px;border:1px solid #334'>250</td><td style='padding:4px;border:1px solid #334'>5</td><td style='padding:4px;border:1px solid #334'>600</td><td style='padding:4px;border:1px solid #334'>12</td></tr><tr><td style='padding:4px;border:1px solid #334'>200</td><td style='padding:4px;border:1px solid #334'>4</td><td style='padding:4px;border:1px solid #334'>400</td><td style='padding:4px;border:1px solid #334'>8</td></tr><tr><td style='padding:4px;border:1px solid #334'>150</td><td style='padding:4px;border:1px solid #334'>3</td><td style='padding:4px;border:1px solid #334'>300</td><td style='padding:4px;border:1px solid #334'>6</td></tr><tr><td style='padding:4px;border:1px solid #334'>100</td><td style='padding:4px;border:1px solid #334'>2</td><td style='padding:4px;border:1px solid #334'>200</td><td style='padding:4px;border:1px solid #334'>4</td></tr></table>"},
 {t:"Identificar un panel paso a paso",k:["identificar","como identificar","paso a paso","procedimiento","reconocer","determinar"],
  a:"<b>Procedimiento:</b><br>1) ¿Tiene doblez central? → EI/EE<br>2) Cuenta <b>perforaciones frontales</b> → ancho = n × 50 mm<br>3) Cuenta <b>perforaciones laterales</b> → largo = n × 50 mm<br>4) Ancho 300–600 ⇒ PM | Ancho 80–270 ⇒ PB<br>5) Ej: 12F + 48L = PM-2400×600<br>6) Verifica con refuerzos transversales por atrás"},
 {t:"Diferencia PM vs PB",k:["diferencia","PM","PB","comparar","ancho","estrecho","angosto"],
  a:"<b>PM (Panel Mayor):</b> ancho 300–600 mm. Más refuerzos transversales (4–6). Mayor área de lámina visible.<br><b>PB (Panel Borde/Binche):</b> ancho 80–270 mm. Menos refuerzos (1–3). Usado en completaciones y bordes de encofrado."},
 {t:"Composición de un panel completo",k:["composicion","composición","partes","estructura","componentes","consta","tiene"],
  a:"Un panel UNISPAN completo tiene:<br>• <b>Lámina</b> (cara de contacto) — acero 3mm<br>• <b>Marco perimetral</b> (4 bridas soldadas)<br>• <b>2 refuerzos longitudinales</b> (tubo 60×40)<br>• <b>3–6 refuerzos transversales</b> (tubo 40×20)<br>• <b>Perforaciones</b> cada 50mm en todas las bridas<br>• Primera perforación a 25mm del borde"},
 {t:"Buenas fotos para el dataset",k:["foto","fotos","dataset","calidad","angulo","varios","capturar"],
  a:"Para 30 imágenes por clase: 6 frontales · 6 posteriores · 6 laterales · 6 en arrume · 6 en obra. Asegúrate de que las perforaciones se vean nítidas (son la firma identificatoria)."},
];

let expertInited=false;
function expertInit(){
  if(expertInited) return; expertInited=true;
  const chips=document.getElementById("expert-chips");
  const topics=["Lámina","Bridas","Platinas","Transversales","Estructural","EI/EE","Frontales","Laterales","Inicio/Paso","Tabla perf.","PM vs PB","Composición","Identificar","Dataset"];
  chips.innerHTML=topics.map(t=>`<span onclick="expertSay('${t}')" style="background:#1a2130;color:#f59e0b;padding:6px 10px;border-radius:14px;font-size:11px;cursor:pointer;border:1px solid #334">${t}</span>`).join("");
  expertBot("¡Hola! Soy el <b>agente experto UNISPAN</b>. Pregúntame sobre láminas, bridas, perforaciones o cómo identificar piezas. <b>Funciono 100% sin claves ni conexión.</b> También puedo analizar la imagen cargada localmente.");
}
function expertBot(html){ const c=document.getElementById("expert-chat"); c.insertAdjacentHTML("beforeend",`<div style="margin:6px 0;padding:10px;background:#1a2130;border-radius:8px;border-left:3px solid var(--amber)"><b style="color:var(--amber)">🎓 Experto:</b><br>${html}</div>`); c.scrollTop=c.scrollHeight; }
function expertUser(txt){ const c=document.getElementById("expert-chat"); c.insertAdjacentHTML("beforeend",`<div style="margin:6px 0;padding:8px 10px;background:#0b1220;border-radius:8px;text-align:right;color:#cbd5e1"><b>Tú:</b> ${txt}</div>`); c.scrollTop=c.scrollHeight; }
function expertSay(topic){ document.getElementById("expert-input").value=topic; expertAsk(); }
function normTxt(s){ return s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,""); }
async function expertAsk(){
  const inp=document.getElementById("expert-input"); const q=inp.value.trim(); if(!q) return;
  inp.value=""; expertUser(q);
  const qn=normTxt(q);
  const scored=EXPERT_KB.map(e=>{ const hay=normTxt(e.t+" "+e.k.join(" ")); let s=0; qn.split(/\s+/).filter(w=>w.length>2).forEach(w=>{ if(hay.includes(w)) s+=w.length; }); e.k.forEach(k=>{ if(qn.includes(normTxt(k))) s+=6; }); return{e,s}; }).sort((a,b)=>b.s-a.s);
  // Si pregunta sobre imagen actual, dar análisis local
  const wantsImage=/\b(foto|imagen|captur|actual|analic|reciente|ultim|últim|qu[eé] tom|qu[eé] veo|reconoc|que es|qué es)/i.test(q);
  if(wantsImage && selectedFile){
    expertBot("🔍 Analizando imagen cargada…");
    const local=localImageAnalysis();
    if(local){
      const ref=local.referencia||"sin match";
      expertBot(`📸 <b>Análisis de imagen actual:</b><br>
        • <b>Referencia:</b> <span style="color:var(--amber);font-family:monospace">${ref}</span><br>
        • <b>Familia:</b> ${local.familia}${local.esquinero?" — esquinero "+local.esquinero:""}<br>
        • <b>Perforaciones frontales:</b> ${local.frontales} → ancho ~${local.ancho_mm} mm<br>
        • <b>Perforaciones laterales:</b> ${local.laterales} → largo ~${local.largo_mm} mm<br>
        • <b>Confianza:</b> ${local.confianza>=0.7?"✅ alta":local.confianza>=0.5?"⚠️ media":"❌ baja"}<br>
        ${local.info?`• ${local.info}`:""}
        <div style="margin-top:6px;font-size:10px;color:var(--steel)">Análisis 100% local · sin API key</div>`);
      return;
    }
  }
  if(wantsImage && !selectedFile){ expertBot("⚠️ No hay imagen cargada. Carga una foto en la pestaña 📸 Captura primero."); return; }
  if(scored[0].s===0){
    // Intentar respuesta calculadora
    const numMatch=q.match(/(\d+)\s*(mm|frontales|laterales|perf)/i);
    if(numMatch){
      const n=+numMatch[1];
      const ancho=n*50; const largo=n*50;
      const famW=familyFor(ancho);
      expertBot(`Calculando: ${n} perforaciones × 50mm = <b>${ancho} mm</b>.<br>${famW!=="?"?`Familia por ancho: <b>${famW}</b>`:"Ancho fuera del catálogo estándar."}<br>Usa la <a onclick="switchTab('experto')" style="color:var(--amber);cursor:pointer">calculadora</a> para más opciones.`);
      return;
    }
    expertBot("No encontré coincidencia en la base local. Temas disponibles: <i>lámina, brida, refuerzo transversal, EI/EE, perforación frontal, distancia entre centros, composición, identificar</i>. Toca un chip arriba o recarga con más detalle.");
    return;
  }
  const top=scored[0].e; let out=`<b>${top.t}</b><br>${top.a}`;
  const rel=scored.slice(1,4).filter(x=>x.s>0);
  if(rel.length) out+=`<div style="margin-top:8px;font-size:11px;color:var(--steel)">También: ${rel.map(x=>`<span onclick="expertSay('${x.e.t}')" style="color:var(--amber);cursor:pointer;text-decoration:underline">${x.e.t}</span>`).join(" · ")}</div>`;
  expertBot(out);
}

// ─── Calculadora ─────────────────────────────────────────────────
const PITCH=50, START=25;
function calcOut(html){ document.getElementById("calc-out").innerHTML=html; }
function calcFromDims(){
  const w=+document.getElementById("calc-w").value, l=+document.getElementById("calc-l").value;
  if(!w&&!l){ calcOut("Ingresa medidas o conteos · inicio 25 mm · paso 50 mm"); return; }
  let out=[];
  if(w>0){ const nf=Math.round(w/PITCH); document.getElementById("calc-nf").value=nf; out.push(`Ancho ${w} mm ⇒ <b>${nf} frontales</b>`); }
  if(l>0){ const nl=Math.round(l/PITCH); document.getElementById("calc-nl").value=nl; out.push(`Longitud ${l} mm ⇒ <b>${nl} laterales</b>`); }
  if(w>0&&l>0){ const fam=familyFor(w), sw=nearest(w,STD_ANCHOS), sl=nearest(l,STD_LARGOS); out.push(`<span style="color:var(--amber)">Referencia: <b>${fam}-${sl}x${sw}</b></span>`); }
  calcOut(out.join("<br>"));
}
function calcFromCounts(){
  const nf=+document.getElementById("calc-nf").value, nl=+document.getElementById("calc-nl").value;
  if(!nf&&!nl){ calcOut("Ingresa medidas o conteos · inicio 25 mm · paso 50 mm"); return; }
  let out=[];
  if(nf>0){ const w=nf*PITCH; document.getElementById("calc-w").value=w; out.push(`${nf} frontales ⇒ ancho <b>${w} mm</b>`); }
  if(nl>0){ const l=nl*PITCH; document.getElementById("calc-l").value=l; out.push(`${nl} laterales ⇒ longitud <b>${l} mm</b>`); }
  if(nf>0&&nl>0){ const w=nf*PITCH,l=nl*PITCH,fam=familyFor(w),sw=nearest(w,STD_ANCHOS),sl=nearest(l,STD_LARGOS); out.push(`<span style="color:var(--amber)">Referencia: <b>${fam}-${sl}x${sw}</b></span>`); }
  calcOut(out.join("<br>"));
}

// ═══════════════════════════════════════════════════════════════════
// MEMORIA
// ═══════════════════════════════════════════════════════════════════
function recordMemory(img,file){
  const w=img.naturalWidth, h=img.naturalHeight, aspect=+(w/h).toFixed(3);
  const entry={id:Date.now(),filename:file?.name||"cam",w,h,aspect,orientation:aspect>1.2?"horizontal":aspect<0.83?"vertical":"cuadrada",classes:[],qty:null,blur:null,note:"",aiObs:null,date:new Date().toISOString()};
  imgMemory.unshift(entry); if(imgMemory.length>200) imgMemory.length=200;
  _lastMemoryEntry=entry; saveMemory();
}
function updateMemoryFromUpload(checkedAnnos){
  if(!_lastMemoryEntry) return;
  _lastMemoryEntry.classes=[...new Set(checkedAnnos.filter(a=>!a.isQty).map(a=>a.clase))];
  _lastMemoryEntry.qty=checkedAnnos.find(a=>a.qty)?.qty||null;
  saveMemory();
}
function memoryContextForAI(){
  if(!imgMemory.length) return "Memoria vacía.";
  const byClass={};
  imgMemory.forEach(e=>e.classes.forEach(c=>{ byClass[c]=(byClass[c]||0)+1; }));
  const clsList=Object.entries(byClass).sort((a,b)=>b[1]-a[1]).slice(0,15).map(([c,n])=>`${c}:${n}`).join(", ")||"(sin clases)";
  return `Imágenes: ${imgMemory.length}. Clases: ${clsList}.`;
}

// ═══════════════════════════════════════════════════════════════════
// ANÁLISIS LOCAL MEJORADO — cruza con catálogo completo
// ═══════════════════════════════════════════════════════════════════
function localImageAnalysis(cropDisplayBox){
  const img=document.getElementById("bbox-img");
  if(!img||!img.naturalWidth) return null;
  let sx=0,sy=0,sw=img.naturalWidth,sh=img.naturalHeight;
  if(cropDisplayBox&&imgDispW&&imgDispH){
    const scX=img.naturalWidth/imgDispW, scY=img.naturalHeight/imgDispH;
    const pad=0.06;
    const px=Math.max(0,cropDisplayBox.x-cropDisplayBox.w*pad), py=Math.max(0,cropDisplayBox.y-cropDisplayBox.h*pad);
    const pw=cropDisplayBox.w*(1+pad*2), ph=cropDisplayBox.h*(1+pad*2);
    sx=Math.max(0,Math.round(px*scX)); sy=Math.max(0,Math.round(py*scY));
    sw=Math.max(20,Math.min(img.naturalWidth-sx,Math.round(pw*scX)));
    sh=Math.max(20,Math.min(img.naturalHeight-sy,Math.round(ph*scY)));
  }
  const maxDim=600;
  const sc=Math.min(1,maxDim/Math.max(sw,sh));
  const w=Math.round(sw*sc), h=Math.round(sh*sc);
  const cv=document.createElement("canvas"); cv.width=w; cv.height=h;
  const ctx=cv.getContext("2d"); ctx.drawImage(img,sx,sy,sw,sh,0,0,w,h);
  const data=ctx.getImageData(0,0,w,h).data;

  // Franjas perimetrales más anchas (12%) para detectar mejor las perforaciones en bridas
  const edgeW=Math.round(Math.min(w,h)*0.12);

  // Contar manchas oscuras en cada franja
  const top=   countDarkRegions(data,w,h, 0,    edgeW, 0,   w);
  const bottom=countDarkRegions(data,w,h, h-edgeW, h,  0,   w);
  const left=  countDarkRegions(data,w,h, 0,    h,    0,    edgeW);
  const right= countDarkRegions(data,w,h, 0,    h,    w-edgeW, w);

  // Las bridas cortas (top+bottom) dan frontales, las largas (left+right) dan laterales
  // Tomar el máximo por si la imagen está rotada o no se ven todas las bridas
  const rawF=Math.max(top,bottom);
  const rawL=Math.max(left,right);

  // Ajustar a valores estándar por perforaciones (snap al catálogo)
  const frontales=snapToStdPerf(rawF,"ancho");
  const laterales=snapToStdPerf(rawL,"largo");

  // Calcular dimensiones desde tabla real
  const ancho_mm=PERF_INV_ANCHO[frontales] || (frontales>0?frontales*50:0);
  const largo_mm=PERF_INV_LARGO[laterales] || (laterales>0?laterales*50:0);

  // Familia
  const familia=familyFor(ancho_mm);

  // Buscar referencia en catálogo
  let referencia=null, confianza=0;
  if(familia!=="?"&&largo_mm>0){
    const match=nearestCatalogMatch(familia,largo_mm,ancho_mm);
    if(match){
      referencia=match.code;
      // Confianza según distancia al match
      confianza=match.distancia_mm===0?0.95:match.distancia_mm<=100?0.80:match.distancia_mm<=300?0.60:0.40;
    }
  }

  // Detectar esquinero
  const esquinero=detectCornerFold(data,w,h);
  if(esquinero&&!referencia){
    const match=nearestCatalogMatch(esquinero,largo_mm||2400,150);
    if(match){ referencia=match.code; confianza=0.65; }
  }

  // Información de diagnóstico
  let info=`Franjas: T${top}/B${bottom}/L${left}/R${right} → ${frontales}F×${laterales}L → ${ancho_mm}×${largo_mm}mm`;

  return{frontales,laterales,ancho_mm,largo_mm,familia,referencia,esquinero,confianza,info,raw:{top,bottom,left,right},_cv:cv};
}

// Ajusta conteo crudo al valor más cercano en la tabla de perforaciones estándar
function snapToStdPerf(rawCount, dim){
  if(rawCount<=0) return 0;
  const stdCounts=Object.values(PERF_TABLE[dim==="ancho"?"ancho":"largo"]);
  const unique=[...new Set(stdCounts)].sort((a,b)=>a-b);
  // Tolerancia: ±3 para frontales (bridas cortas difíciles), ±5 para laterales
  const tol=dim==="ancho"?3:5;
  let best=rawCount, bestD=Infinity;
  unique.forEach(n=>{ const d=Math.abs(n-rawCount); if(d<bestD&&d<=tol){ bestD=d; best=n; } });
  return best;
}

// Cuenta regiones oscuras (perforaciones) en una banda rectangular
function countDarkRegions(data,w,h,y0,y1,x0,x1){
  const visited=new Uint8Array(w*h);
  let count=0;
  for(let y=Math.max(0,y0);y<Math.min(h,y1);y+=2){
    for(let x=Math.max(0,x0);x<Math.min(w,x1);x+=2){
      const idx=(y*w+x)*4;
      const lum=0.299*data[idx]+0.587*data[idx+1]+0.114*data[idx+2];
      if(lum<75&&!visited[y*w+x]){
        const stack=[[x,y]]; let size=0;
        while(stack.length&&size<400){
          const [cx,cy]=stack.pop();
          if(cx<x0||cx>=x1||cy<y0||cy>=y1) continue;
          const pi=cy*w+cx; if(visited[pi]) continue;
          const di=pi*4; const l=0.299*data[di]+0.587*data[di+1]+0.114*data[di+2];
          if(l>75) continue;
          visited[pi]=1; size++;
          stack.push([cx+1,cy],[cx-1,cy],[cx,cy+1],[cx,cy-1]);
        }
        if(size>=6&&size<600) count++;
      }
    }
  }
  return count;
}

function detectCornerFold(data,w,h){
  let dark1=0, dark2=0; const steps=Math.min(w,h);
  for(let i=0;i<steps;i+=3){
    if(i<w&&i<h){ const idx=(i*w+i)*4; if(0.299*data[idx]+0.587*data[idx+1]+0.114*data[idx+2]<100) dark1++; }
    const x2=w-1-i;
    if(x2>=0&&i<h){ const idx=(i*w+x2)*4; if(0.299*data[idx]+0.587*data[idx+1]+0.114*data[idx+2]<100) dark2++; }
  }
  const threshold=steps*0.15;
  if(dark1>threshold) return "EI";
  if(dark2>threshold) return "EE";
  return null;
}

// ─── Clasificar anotación individual (local) ──────────────────────
async function classifyAnnotationLocal(annoId){
  const anno=annotations.find(a=>a.id===annoId); if(!anno) return;
  try{
    const box=annotationBounds(anno);
    const local=localImageAnalysis(box);
    const hash=local&&local._cv?computeFingerprintFromCanvas(local._cv):null;
    if(hash) anno._hash=hash;
    const learned=hash?matchLearnedPiece(hash):null;
    if(learned){
      anno.clase=learned.clase; anno.pendingAutoClass=false;
      addReciente(learned.clase); renderAnnoList(); redraw(); updateButtons();
      samStatus(`🧠 Reconocida por memoria: ${learned.clase} (${learned.confirmations||1}× confirmada · ${Math.round(learned.confianza*100)}%)`);
      if(_lastMemoryEntry){ _lastMemoryEntry.aiObs=local; _lastMemoryEntry.classes=[...new Set([...(_lastMemoryEntry.classes||[]),learned.clase])]; saveMemory(); }
      showQtyPromptAt(annoId, box);
      return;
    }
    if(local&&local.referencia){
      anno.clase=local.referencia; anno.pendingAutoClass=false;
      addReciente(local.referencia); renderAnnoList(); redraw(); updateButtons();
      samStatus(`✅ Identificada por catálogo: ${local.referencia} (${local.frontales}F×${local.laterales}L) confianza ${Math.round(local.confianza*100)}%`);
      if(_lastMemoryEntry){ _lastMemoryEntry.aiObs=local; _lastMemoryEntry.classes=[...new Set([...(_lastMemoryEntry.classes||[]),local.referencia])]; saveMemory(); }
      showQtyPromptAt(annoId, box);
      return;
    }
  }catch(_){}
  anno.clase="POR-IDENTIFICAR"; anno.pendingAutoClass=false;
  renderAnnoList(); redraw(); updateButtons();
  samStatus("✅ Pieza marcada. Toca la etiqueta para asignar clase manualmente.");
  showQtyPromptAt(annoId, annotationBounds(anno));
}

// ─── Resolución de clase para anotación SAM ───────────────────────
function resolveClaseForAnnotation(){
  if(currentClase) return currentClase;
  const last=physicalProofs[0];
  const p=last?.piezas?.[0]||last?.arrumes?.[0];
  if(p?.referencia&&p.referencia!=="POR-IDENTIFICAR") return p.referencia;
  return "POR-IDENTIFICAR";
}

// ─── Auto-detect posición de piezas ──────────────────────────────
function normalizedBoxToDisplay(b){
  if(!b) return{x:imgDispW*.08,y:imgDispH*.08,w:imgDispW*.84,h:imgDispH*.84};
  let x=+b.x||0,y=+b.y||0,w=+b.w||0,h=+b.h||0;
  if(b.cx!=null||b.cy!=null){ x=(+b.cx||.5)-w/2; y=(+b.cy||.5)-h/2; }
  if(x>1||y>1||w>1||h>1){ x/=imgNatW; y/=imgNatH; w/=imgNatW; h/=imgNatH; }
  x=Math.max(0,Math.min(.98,x)); y=Math.max(0,Math.min(.98,y)); w=Math.max(.04,Math.min(1-x,w||.84)); h=Math.max(.04,Math.min(1-y,h||.84));
  return{x:x*imgDispW,y:y*imgDispH,w:w*imgDispW,h:h*imgDispH};
}
function applyPhysicalDetections(proof){
  if(!proof||!selectedFile) return;
  const p=(proof.piezas||[])[0];
  if(!p) return;
  if(annotations.filter(a=>a.fromPhysicalAuto).length) return;
  const ref=p.referencia||"POR-IDENTIFICAR";
  const id=Date.now(); const color=COLORS[annotations.length%COLORS.length];
  let anno;
  if(p.contourPoints&&p.contourPoints.length>=3){
    anno={id,clase:ref,type:"polygon",points:p.contourPoints,color,checked:true,qty:null,fromPhysicalAuto:true,fromSam:true,_hash:p.hash||null};
  } else {
    const box=normalizedBoxToDisplay(p.bbox);
    anno={id,clase:ref,type:"bbox",bbox:box,color,checked:true,qty:null,fromPhysicalAuto:true,_hash:p.hash||null};
  }
  annotations.push(anno);
  const qty=+(p.cantidad_estimada||p.cantidad||1)||1;
  if(qty>1) addQtyBadgeForAnnotation(anno,qty);
  if(ref&&ref!=="POR-IDENTIFICAR") addReciente(ref);
  renderAnnoList(); redraw(); updateButtons();
  if(!arrumeMode) showQtyPromptAt(id, anno.type==="polygon"?annotationBounds(anno):anno.bbox);
}

// ─── Auto-prueba física (100% local) ─────────────────────────────
async function runPhysicalProof(opts={}){
  if(!selectedFile){ setPhysicalStatus("⚠️ Toma/carga una foto primero."); return; }
  setPhysicalStatus(opts.auto?"🧪 Auto-reconociendo localmente…":"🧪 Analizando imagen…");
  try{
    const contour=autoDetectPieceContour();
    const cropBox=contour?boundsOfPoints(contour):null;
    const local=localImageAnalysis(cropBox);
    if(!local){ setPhysicalStatus("⚠️ No se pudo procesar la imagen."); return; }
    const hash=local._cv?computeFingerprintFromCanvas(local._cv):null;
    const learned=hash?matchLearnedPiece(hash):null;
    const ref=(learned&&learned.clase)||local.referencia||"POR-IDENTIFICAR";
    const familia=(learned&&learned.familia)||local.familia||"?";
    const confianza=learned?learned.confianza:(local.confianza||0);
    const normBox=cropBox?{x:cropBox.x/imgDispW,y:cropBox.y/imgDispH,w:cropBox.w/imgDispW,h:cropBox.h/imgDispH}:{x:.15,y:.15,w:.7,h:.7};
    const proof={
      date:new Date().toISOString(),
      resumen: learned?`Reconocida por memoria (${learned.confirmations||1}× confirmada)`:`Análisis local: ${local.frontales}F × ${local.laterales}L → ${local.ancho_mm}×${local.largo_mm}mm`,
      conteo_total:1,
      piezas:[{referencia:ref,familia,tipo:local.esquinero||(familia!=="?"?"panel":"?"),cantidad:1,bbox:normBox,contourPoints:contour||null,frontales:local.frontales,laterales:local.laterales,ancho_mm:local.ancho_mm,largo_mm:local.largo_mm,info:local.info,confianza,hash,viaMemoria:!!learned}],
      arrumes:[],
      calidad_foto:_lastMemoryEntry?.blur>180?"nítida":_lastMemoryEntry?.blur>80?"media":"borrosa",
      acciones:"Revisar y confirmar"
    };
    physicalProofs.unshift(proof); if(physicalProofs.length>80) physicalProofs.length=80; savePhysicalProofs();
    applyPhysicalDetections(proof);
    if(_lastMemoryEntry){ _lastMemoryEntry.aiObs=proof; _lastMemoryEntry.classes=[...new Set([...(_lastMemoryEntry.classes||[]),ref].filter(Boolean))]; _lastMemoryEntry.qty=1; saveMemory(); }
    const confPct=Math.round((confianza||0)*100);
    const refHtml=ref!=="POR-IDENTIFICAR"?`<span style="color:var(--amber);font-family:monospace">${ref}</span> (${confPct}% confianza${learned?" · 🧠 memoria":""})`:`<span style='color:var(--steel)'>sin match claro</span>`;
    const html=`<b style="color:var(--ok)">🧪 Análisis completado <span style="color:var(--steel);font-size:10px">(local · sin claves)</span></b><br>
      ${safeHtml(proof.resumen)}<br>
      <b>Referencia:</b> ${refHtml}<br>
      <b>Familia:</b> ${familia}${local.esquinero?" — "+local.esquinero:""}<br>
      <b>Perforaciones:</b> ${local.frontales}F · ${local.laterales}L (raw: T${local.raw.top}/B${local.raw.bottom}/L${local.raw.left}/R${local.raw.right})<br>
      <b>Medidas:</b> ${local.ancho_mm}×${local.largo_mm}mm · Foto: ${proof.calidad_foto}${contour?"":" · <span style=\"color:var(--steel)\">contorno no claro, usa SAM manual para ajustar</span>"}`;
    setPhysicalStatus(html);
    expertInit(); expertBot(`🧪 Resultado análisis:<br>${html}`);
    showToast(learned?"🧠 Reconocida por memoria":"🧪 Análisis completado","ok");
  }catch(err){
    console.error("Prueba física:",err);
    setPhysicalStatus(`❌ Error: ${safeHtml((err.message||err).toString().slice(0,140))}`);
  }
}

// ─── Analizar imagen actual ───────────────────────────────────────
async function analyzeCurrentWithAI(){
  const out=document.getElementById("ai-analysis-out"); out.style.display="block";
  if(!selectedFile){ out.textContent="⚠️ Carga una imagen primero."; return; }
  out.innerHTML="⏳ Analizando…";
  const contour=autoDetectPieceContour();
  const cropBox=contour?boundsOfPoints(contour):null;
  const local=localImageAnalysis(cropBox);
  const e=_lastMemoryEntry;
  if(local){
    const hash=local._cv?computeFingerprintFromCanvas(local._cv):null;
    const learned=hash?matchLearnedPiece(hash):null;
    const refCode=(learned&&learned.clase)||local.referencia;
    const refHtml=refCode?`<span style="color:var(--ok);font-family:monospace">${refCode}</span> ✅ (${Math.round((learned?learned.confianza:local.confianza)*100)}%${learned?" · 🧠 memoria":""})`:`<span style="color:var(--amber)">sin match claro</span>`;
    const catEntry=refCode?CATALOG_MAP[refCode.toUpperCase()]:null;
    const html=`<b style="color:var(--amber)">🔍 Análisis local (sin API key):</b><br>
      • <b>Referencia:</b> ${refHtml}<br>
      • <b>Familia:</b> ${(learned&&learned.familia)||local.familia||"?"}${local.esquinero?" (esquinero "+local.esquinero+")":""}<br>
      • <b>Perforaciones:</b> ${local.frontales} frontales · ${local.laterales} laterales<br>
      • <b>Medidas estimadas:</b> ${local.ancho_mm} × ${local.largo_mm} mm<br>
      ${catEntry?`• <b>Catálogo:</b> ${catEntry.code} — ${catEntry.spec}<br>`:""}
      • <b>Diagnóstico:</b> <span style="font-size:10px;color:var(--steel)">${local.info}</span><br>
      • <b>Dimensiones foto:</b> ${e?.w||"?"}×${e?.h||"?"} px (${e?.orientation||"?"})<br>
      • <b>Nitidez:</b> ${e?.blur??"?"} ${e&&e.blur>180?"✅":e&&e.blur>80?"⚠️":"❌"}`;
    out.innerHTML=html;
    if(_lastMemoryEntry){ _lastMemoryEntry.aiObs=local; saveMemory(); }
    expertInit(); expertBot(`📸 ${html}`);
  } else {
    out.innerHTML="⚠️ No se pudo analizar la imagen. Intenta con una foto más nítida.";
  }
}

function showMemorySummary(){
  const out=document.getElementById("ai-analysis-out"); out.style.display="block";
  if(!imgMemory.length){ out.innerHTML="📭 Sin imágenes en memoria."; return; }
  const byClass={};
  imgMemory.forEach(e=>e.classes.forEach(c=>{ if(!byClass[c]) byClass[c]={n:0,blurs:[]}; byClass[c].n++; if(e.blur) byClass[c].blurs.push(e.blur); }));
  const withAI=imgMemory.filter(e=>e.aiObs).length;
  let html=`<b>🧠 Memoria: ${imgMemory.length} imágenes · ${withAI} analizadas</b><br>
  <b>🎓 Piezas aprendidas:</b> ${learnedPieces.length} huellas (${learnedPieces.reduce((s,p)=>s+(p.confirmations||1),0)} confirmaciones totales)<br><br>`;
  const entries=Object.entries(byClass).sort((a,b)=>b[1].n-a[1].n).slice(0,12);
  if(!entries.length) html+="<i style='color:var(--steel)'>Sin clases anotadas.</i>";
  else{
    html+="<table style='width:100%;border-collapse:collapse;font-size:11px'><tr style='color:var(--amber)'><th style='text-align:left;padding:3px'>Clase</th><th style='padding:3px'>N</th><th style='padding:3px'>Nitidez</th></tr>";
    entries.forEach(([c,d])=>{ const avgB=d.blurs.length?Math.round(d.blurs.reduce((s,x)=>s+x,0)/d.blurs.length):"?"; html+=`<tr style='border-top:1px solid #223'><td style='padding:3px;font-family:monospace'>${c}</td><td style='padding:3px;text-align:center'>${d.n}</td><td style='padding:3px;text-align:center'>${avgB}</td></tr>`; });
    html+="</table>";
  }
  out.innerHTML=html;
}
function clearMemory(){ if(!confirm("¿Borrar toda la memoria? (No afecta Roboflow)")) return; imgMemory=[]; physicalProofs=[]; saveMemory(); savePhysicalProofs(); const out=document.getElementById("ai-analysis-out"); out.style.display="block"; out.textContent="🗑️ Memoria borrada."; setPhysicalStatus("",false); }

// ─── Parse AI JSON helper ─────────────────────────────────────────
function parseAIJson(raw){ if(!raw) return null; try{ return JSON.parse(raw); }catch(_){} const m=String(raw).match(/\{[\s\S]*\}/); if(!m) return null; try{ return JSON.parse(m[0]); }catch(_){ return null; } }
function validateAIReference(obj){ if(!obj) return "POR-IDENTIFICAR"; let ref=String(obj.referencia||obj.referencia_validada||obj.codigo||"").toUpperCase().replace(/×/g,"x"); if(ref&&CATALOG_MAP[ref]) return ref; const fam=String(obj.familia||"").toUpperCase(); const largo=+(obj.largo_mm||obj.longitud_mm||0); const ancho=+(obj.ancho_mm||0); if(["PM","PB","EI","EE"].includes(fam)&&(largo||ancho)){ const match=nearestCatalogMatch(fam,largo,ancho); if(match) return match.code; } return ref||"POR-IDENTIFICAR"; }
function annotationCropDataUrl(a,pad=.08){
  const b=annotationBounds(a); if(!b) return null;
  const img=document.getElementById("bbox-img");
  const scX=imgNatW/imgDispW,scY=imgNatH/imgDispH;
  const px=Math.max(0,b.x-b.w*pad),py=Math.max(0,b.y-b.h*pad);
  const pw=Math.min(imgDispW-px,b.w*(1+pad*2)),ph=Math.min(imgDispH-py,b.h*(1+pad*2));
  const sx=Math.max(0,Math.round(px*scX)),sy=Math.max(0,Math.round(py*scY));
  const sw=Math.max(8,Math.min(imgNatW-sx,Math.round(pw*scX))),sh=Math.max(8,Math.min(imgNatH-sy,Math.round(ph*scY)));
  const cv=document.createElement("canvas"); cv.width=Math.min(1024,sw); cv.height=Math.round(sh*(cv.width/sw));
  cv.getContext("2d").drawImage(img,sx,sy,sw,sh,0,0,cv.width,cv.height);
  return cv.toDataURL("image/jpeg",.86);
}
</script>


</body></html>
