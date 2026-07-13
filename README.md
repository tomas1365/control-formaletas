<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<meta name="theme-color" content="#0a1628">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<title>UNISPAN — Captura Dataset v13</title>
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
</style>
</head>
<body>
<header>
  <div class="logo">U</div>
  <div style="flex:1"><h1>UNISPAN Dataset v13</h1><p>Auto-segmento + analisis local sin claves + descarga</p></div>
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
    <div class="card-title">⚙️ Configuración</div>
    <label>API Key Roboflow</label>
    <input type="password" id="api-key" placeholder="rf_xxxxxxxxxxxxxx" autocomplete="off">
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
    <div class="tool-hint" id="tool-hint-corner" style="display:none">📐 Arrastra para el rectángulo base · luego ajusta el brazo del esquinero con los deslizadores flotantes</div>
    <div class="tool-hint" id="tool-hint-polygon" style="display:none">Toca para agregar puntos · Doble toque para cerrar</div>
    <div class="tool-hint" id="tool-hint-sam" style="display:none">🎯 Toca una pieza: la app traza su contorno automaticamente por color/borde. Sin descargas, funciona offline.</div>
    <div id="sam-status" style="display:none;font-size:11px;color:var(--amber);margin-top:6px;padding:6px 10px;background:rgba(245,158,11,.08);border-radius:8px;text-align:center"></div>
    <label style="display:flex;align-items:center;gap:10px;margin-top:10px;padding:10px;background:var(--bg);border:1.5px solid var(--border);border-radius:10px;cursor:pointer" for="arrume-toggle">
      <input type="checkbox" id="arrume-toggle" onchange="toggleArrume(this.checked)" style="width:18px;height:18px;margin:0;accent-color:var(--amber)">
      <div style="flex:1"><div style="font-size:13px;font-weight:700;color:var(--text)">🔗 Modo Arrume</div><div style="font-size:10px;color:var(--steel)">Mantiene la clase activa y dibuja varias piezas iguales sin reabrir catálogo</div></div>
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
    <input type="file" id="file-input-gal" accept="image/*" multiple>
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
      <span>📊 Balance del dataset <span id="stats-total" style="color:var(--amber);font-weight:800">0</span></span>
      <span id="stats-caret" style="font-size:14px;color:var(--steel)">▼</span>
    </div>
    <div id="stats-body" style="display:none">
      <div style="font-size:11px;color:var(--steel);margin-bottom:8px">Meta inicial: <b style="color:var(--amber)">30 img/clase</b> (varios ángulos). Se ampliará tras el primer entrenamiento.</div>
      <div id="stats-list"></div>
      <div class="btn-row" style="margin-top:8px"><button class="btn btn-ghost btn-sm" onclick="resetStats()">🗑️ Reiniciar contador</button></div>
    </div>
  </div>
  <div class="prog-wrap" id="prog-wrap"><div class="prog-bar" id="prog-bar"></div></div>
  <div class="btn-row">
    <button class="btn btn-ghost btn-sm" onclick="resetAll()" style="flex:none;padding:13px 16px">🔄</button>
    <button class="btn btn-amber" id="btn-review" onclick="openReview()" disabled>👁️ Revisar</button>
    <button class="btn btn-up" id="btn-upload" onclick="uploadAll()" disabled>⬆️ Subir</button>
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
    <div class="card-title">🎓 Agente Experto UNISPAN</div>
    <div style="font-size:12px;color:var(--steel);margin-bottom:10px">Consulta sobre láminas, bridas, platinas, refuerzos, perforaciones y estructura de las paneles formaletas. Toca un tema o escribe tu pregunta.</div>
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
      <div style="font-size:12px;color:var(--amber);font-weight:700;margin-bottom:8px">🧠 Análisis local y memoria</div>
      <div style="font-size:11px;color:var(--steel);margin-bottom:8px">El agente analiza cada imagen localmente: detecta contornos, cuenta perforaciones, estima medidas y referencia del catálogo. <b>Sin API keys requeridas.</b> Opcional: pega una API key de OpenAI para análisis visual profundo con gpt-4o-mini.</div>
      <label style="font-size:11px;color:var(--steel)">API Key OpenAI (opcional)</label>
      <input type="password" id="openai-key" placeholder="sk-..." autocomplete="off" style="width:100%;padding:8px;border-radius:8px;border:1px solid #334;background:#0f1520;color:#eee;margin-bottom:6px">
      <div class="btn-row" style="gap:6px">
        <button class="btn btn-amber btn-sm" onclick="analyzeCurrentWithAI()">🔍 Analizar imagen</button>
        <button class="btn btn-ok btn-sm" onclick="runPhysicalProof()">🧪 Prueba física</button>
        <button class="btn btn-ghost btn-sm" onclick="showMemorySummary()">📊 Ver memoria</button>
        <button class="btn btn-danger btn-sm" onclick="clearMemory()" style="flex:none;padding:8px 10px">🗑️</button>
      </div>
      <label style="display:flex;align-items:center;gap:8px;margin-top:8px;color:var(--steel);font-size:11px;cursor:pointer">
        <input type="checkbox" id="auto-ai-toggle" onchange="toggleAutoPhysical(this.checked)" style="width:16px;height:16px;margin:0;accent-color:var(--amber)">
        Auto-reconocer pieza y cantidad al cargar/tomar foto
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
    <div style="font-size:10px;color:var(--steel);margin-top:8px">💡 Base de conocimiento local · funciona sin conexión · sin claves</div>
  </div>
</div>
</main>
<div class="modal-bg" id="cat-modal-bg" onclick="closeCatModal(event)">
  <div class="modal">
    <div class="modal-title"><span>Seleccionar clase</span><span class="modal-close" onclick="closeCatModalDirect()">✕</span></div>
    <div class="cat-search"><span class="ico">🔍</span><input type="text" id="cat-modal-search" placeholder="Buscar..." oninput="renderCatModal(this.value)" style="margin-bottom:8px;padding-left:36px"></div>
    <div class="cat-families" id="cat-modal-families"></div>
    <div class="cat-list" id="cat-modal-list"></div>
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
// ── Catálogo ──────────────────────────────────────────────────────────────────
const CATALOG=[];
[2400,1200,900,800,750,600].forEach(l=>[600,550,500,450,420,400,380,350,320,300].forEach(a=>CATALOG.push({code:`PM-${l}x${a}`,family:"PM",spec:`${l}×${a}mm`})));
[2400,1200,900,800,750,600].forEach(l=>[270,250,230,200,150,120,100,90,80].forEach(a=>CATALOG.push({code:`PB-${l}x${a}`,family:"PB",spec:`${l}×${a}mm`})));
[2400,1200,900,800,600].forEach(l=>CATALOG.push({code:`EI-${l}x150x150`,family:"EI",spec:`${l}×150×150mm`}));
[2400,1200,900,800,600].forEach(l=>CATALOG.push({code:`EE-${l}x150x150`,family:"EE",spec:`${l}×150×150mm`}));

function catalogSummaryForPrompt(){
  const byFam={};
  CATALOG.forEach(c=>{
    if(!byFam[c.family]) byFam[c.family]={largos:new Set(),anchos:new Set()};
    const m=c.spec.match(/^(\d+)×(\d+)/);
    if(m){ byFam[c.family].largos.add(+m[1]); byFam[c.family].anchos.add(+m[2]); }
  });
  return Object.entries(byFam).map(([fam,d])=>
    `${fam}: largos {${[...d.largos].sort((a,b)=>a-b).join(",")}} mm × anchos {${[d.anchos].sort((a,b)=>a-b).join(",")}} mm`
  ).join("\n");
}

function nearestCatalogMatch(family, largo_mm, ancho_mm){
  const cands=CATALOG.filter(c=>c.family===family);
  if(!cands.length) return null;
  let best=null, bestD=Infinity;
  cands.forEach(c=>{
    const m=c.spec.match(/^(\d+)×(\d+)/);
    if(!m) return;
    const l=+m[1], a=+m[2];
    const d=Math.abs(l-(largo_mm||0))+Math.abs(a-(ancho_mm||0));
    if(d<bestD){ bestD=d; best=c; }
  });
  return best?{...best, distancia_mm:bestD}:null;
}

const COLORS=["#f59e0b","#3b82f6","#a855f7","#22c55e","#ef4444","#06b6d4","#f97316","#84cc16","#ec4899","#14b8a6"];
const PROJECT="reconocimiento-de-piezas-rllp1";

// ── Estado global ─────────────────────────────────────────────────────────────
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

// ── Modo Arrume ──────────────────────────────────────────────────────────────
let arrumeMode=false, arrumeCount=0;
function toggleArrume(on){
  arrumeMode=on; arrumeCount=0;
  const c=document.getElementById("arrume-counter");
  c.style.display=on?"inline-block":"none";
  c.textContent="×0";
  if(on && !currentClase) showToast("⚠️ Selecciona una clase primero para el arrume","err");
  else if(on) showToast(`🔗 Arrume ON: ${currentClase||"?"}`,"ok");
}
function bumpArrume(){
  if(!arrumeMode) return;
  arrumeCount++;
  document.getElementById("arrume-counter").textContent="×"+arrumeCount;
}

let bboxDrawing=false, bboxStart={x:0,y:0}, bboxCurrent=null;
let polyPoints=[], polyDrawing=false, polyPreview=null;
let cornerState=null, cornerDrawing=false, cornerBaseStart=null;
let imgNatW=0, imgNatH=0, imgDispW=0, imgDispH=0;

let imgMemory=JSON.parse(localStorage.getItem("rf_img_memory")||"[]");
function saveMemory(){ try{ localStorage.setItem("rf_img_memory",JSON.stringify(imgMemory.slice(0,200))); }catch(_){} }

let physicalProofs=JSON.parse(localStorage.getItem("rf_physical_proofs")||"[]");
let autoPhysicalOn=localStorage.getItem("rf_auto_physical")!=="0";
const _autoPhysicalToggle=document.getElementById("auto-ai-toggle");
if(_autoPhysicalToggle) _autoPhysicalToggle.checked=autoPhysicalOn;
function savePhysicalProofs(){ try{ localStorage.setItem("rf_physical_proofs",JSON.stringify(physicalProofs.slice(0,80))); }catch(_){} }
function toggleAutoPhysical(on){ autoPhysicalOn=!!on; localStorage.setItem("rf_auto_physical",autoPhysicalOn?"1":"0"); showToast(autoPhysicalOn?"🧪 Auto-reconocimiento ON":"🧪 Auto-reconocimiento OFF", autoPhysicalOn?"ok":""); }
function setPhysicalStatus(html,show=true){ const el=document.getElementById("physical-proof-out"); if(!el) return; el.style.display=show?"block":"none"; if(show) el.innerHTML=html; }

const savedKey=localStorage.getItem("rf_api_key");
if(savedKey) document.getElementById("api-key").value=savedKey;
document.getElementById("api-key").addEventListener("blur",()=>localStorage.setItem("rf_api_key",document.getElementById("api-key").value.trim()));
document.getElementById("cnt-total").textContent=totalCount;
document.getElementById("cnt-ok").textContent=okCount;

// ── fetch con timeout ─────────────────────────────────────────────────────────
function fetchWithTimeout(url, opts, ms=15000){
  const ctrl=new AbortController();
  const timer=setTimeout(()=>ctrl.abort(), ms);
  return fetch(url, {...opts, signal:ctrl.signal}).finally(()=>clearTimeout(timer));
}

// ── Tabs ──────────────────────────────────────────────────────────────────────
function switchTab(n){
  document.querySelectorAll(".tab").forEach((t,i)=>t.classList.toggle("active",["captura","historial","catalogo","experto"][i]===n));
  document.querySelectorAll(".page").forEach(p=>p.classList.toggle("active",p.id==="page-"+n));
  if(n==="catalogo") renderCatalogPage("");
  if(n==="experto") expertInit();
}

// ── Herramienta ───────────────────────────────────────────────────────────────
function setTool(t){
  activeTool=t;
  ["bbox","corner","polygon","sam"].forEach(k=>{
    document.getElementById("tool-"+k).classList.toggle("active",t===k);
    const h=document.getElementById("tool-hint-"+k); if(h) h.style.display=t===k?"block":"none";
  });
  bboxCurrent=null; bboxDrawing=false;
  cancelPolygon(); cornerCancel();
  if(t==="sam") samStatus("✅ Auto-segmento listo · Toca una pieza",true);
}

// ── Clase ─────────────────────────────────────────────────────────────────────
function setClase(code){
  if(catModalMode==="reassign" && catReassignId!=null){
    const a=annotations.find(x=>x.id===catReassignId);
    if(a){ a.clase=code; renderAnnoList(); redraw(); showToast(`✏️ Clase → ${code}`,"ok"); }
    catModalMode="select"; catReassignId=null;
    closeCatModalDirect(); addReciente(code);
    return;
  }
  currentClase=code;
  document.getElementById("clase-custom").value=code;
  const d=document.getElementById("current-clase-display");
  d.textContent="✏️ Clase activa: "+code; d.style.display="block";
  addReciente(code); closeCatModalDirect();
}
function reassignClass(id){
  catModalMode="reassign"; catReassignId=id;
  openCatModal();
  setTimeout(()=>{ const t=document.querySelector("#cat-modal-bg .modal-title span:first-child"); if(t) t.textContent="Reasignar clase a esta anotación"; },50);
}
function onCustomInput(v){
  currentClase=v.trim().toUpperCase();
  const d=document.getElementById("current-clase-display");
  if(v){d.textContent="✏️ Clase activa: "+currentClase;d.style.display="block";}
  else d.style.display="none";
}
function addReciente(code){
  recientes=[code,...recientes.filter(r=>r!==code)].slice(0,8);
  localStorage.setItem("rf_recientes",JSON.stringify(recientes));
  renderRecientes();
}
function renderRecientes(){
  const g=document.getElementById("recientes-grid"); g.innerHTML="";
  recientes.forEach(c=>{const b=document.createElement("div");b.className="quick-btn"+(c===currentClase?" active":"");b.textContent=c;b.onclick=()=>setClase(c);g.appendChild(b);});
  document.getElementById("recientes-wrap").style.display=recientes.length?"":"none";
}
renderRecientes();

// ── File ──────────────────────────────────────────────────────────────────────
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
  if(!selectedFile || !autoPhysicalOn) return;
  setPhysicalStatus("🧪 Foto cargada · preparando auto-reconocimiento local…");
  setTimeout(()=>{ if(selectedFile && autoPhysicalOn) runPhysicalProof({auto:true}); },650);
}
document.getElementById("file-input-cam").addEventListener("change",e=>loadFile(e.target.files[0]));
document.getElementById("file-input-gal").addEventListener("change",e=>loadFile(e.target.files[0]));

// ── Blur detection ────────────────────────────────────────────────────────────
function analyzeBlur(img){
  try{
    const S=220; const c=document.createElement("canvas");
    c.width=S; c.height=S;
    const g=c.getContext("2d"); g.drawImage(img,0,0,S,S);
    const d=g.getImageData(0,0,S,S).data;
    const lum=new Float32Array(S*S);
    for(let i=0;i<S*S;i++) lum[i]=0.299*d[i*4]+0.587*d[i*4+1]+0.114*d[i*4+2];
    let sum=0, sum2=0, n=0;
    for(let y=1;y<S-1;y++){
      for(let x=1;x<S-1;x++){
        const i=y*S+x;
        const v=-lum[i-S]-lum[i-1]+4*lum[i]-lum[i+1]-lum[i+S];
        sum+=v; sum2+=v*v; n++;
      }
    }
    const mean=sum/n, variance=(sum2/n)-mean*mean;
    const w=document.getElementById("blur-warn");
    const t=document.getElementById("blur-warn-txt");
    const act=document.getElementById("blur-warn-action");
    w.classList.remove("ok");
    if(_lastMemoryEntry){ _lastMemoryEntry.blur=Math.round(variance); saveMemory(); }
    if(variance<80){
      w.style.display="flex";
      t.innerHTML=`⚠️ <b>Foto borrosa</b> (nitidez ${variance.toFixed(0)}).`;
      act.innerHTML=`<span class="blur-warn-discard" onclick="discardPhoto()">🗑️ Descartar y repetir</span>`;
    } else if(variance<180){
      w.style.display="flex";
      t.innerHTML=`⚠️ Nitidez media (${variance.toFixed(0)}). Aceptable, pero mejor sería más clara.`;
      act.innerHTML=`<span class="blur-warn-discard" onclick="discardPhoto()">🗑️ Repetir</span>`;
    } else {
      w.style.display="flex"; w.classList.add("ok");
      t.innerHTML=`✅ Foto nítida (${variance.toFixed(0)}).`;
      act.innerHTML="";
      setTimeout(()=>{ if(w.classList.contains("ok")) w.style.display="none"; },2500);
    }
  }catch(_){}
}

// ── Canvas init ───────────────────────────────────────────────────────────────
const canvas=document.getElementById("bbox-canvas");
function initCanvas(){
  const img=document.getElementById("bbox-img");
  imgDispW=img.offsetWidth; imgDispH=img.offsetHeight;
  canvas.width=imgDispW; canvas.height=imgDispH;
  redraw();
}
function getPos(e){
  const rect=canvas.getBoundingClientRect();
  const t=e.touches?e.touches[0]:e;
  return{
    x:Math.max(0,Math.min(canvas.width,(t.clientX-rect.left)*(canvas.width/rect.width))),
    y:Math.max(0,Math.min(canvas.height,(t.clientY-rect.top)*(canvas.height/rect.height)))
  };
}
window.addEventListener("resize",()=>{ if(selectedFile) initCanvas(); });

// ── Zoom / Pan ────────────────────────────────────────────────────────────────
function applyZoom(){
  const w=document.getElementById("bbox-wrap");
  w.style.transform=`translate(${zoomTx}px,${zoomTy}px) scale(${zoomScale})`;
  const lbl=document.getElementById("zoom-lbl"); if(lbl) lbl.textContent=zoomScale.toFixed(1)+"×";
}
function zoomReset(){ zoomScale=1; zoomTx=0; zoomTy=0; applyZoom(); }
function zoomBy(factor){
  const vp=document.getElementById("zoom-viewport"); if(!vp) return;
  const r=vp.getBoundingClientRect(); const cx=r.width/2, cy=r.height/2;
  zoomAt(zoomScale*factor, cx, cy);
}
function zoomAt(newScale,cx,cy){
  newScale=Math.max(1,Math.min(6,newScale));
  const kx=(cx-zoomTx)/zoomScale, ky=(cy-zoomTy)/zoomScale;
  zoomScale=newScale;
  zoomTx=cx-kx*zoomScale;
  zoomTy=cy-ky*zoomScale;
  clampPan();
  applyZoom();
}
function clampPan(){
  const vp=document.getElementById("zoom-viewport"); if(!vp) return;
  const r=vp.getBoundingClientRect();
  const cW=r.width*zoomScale, cH=r.height*zoomScale;
  const minX=r.width-cW, minY=r.height-cH;
  if(zoomScale<=1){ zoomTx=0; zoomTy=0; return; }
  zoomTx=Math.min(0,Math.max(minX,zoomTx));
  zoomTy=Math.min(0,Math.max(minY,zoomTy));
}
function touchDist(t1,t2){ const dx=t1.clientX-t2.clientX, dy=t1.clientY-t2.clientY; return Math.hypot(dx,dy); }
function touchMid(t1,t2,vpRect){ return {x:(t1.clientX+t2.clientX)/2-vpRect.left, y:(t1.clientY+t2.clientY)/2-vpRect.top}; }

// ── Eventos canvas ───────────────────────────────────────────────────────────
function pointerDown_(e){
  if(activeTool==="bbox") bboxStart_(e);
  else if(activeTool==="corner") cornerStart_(e);
  else if(activeTool==="polygon") polyTap(e);
  else if(activeTool==="sam") samTap(e);
}
function pointerMove_(e){
  if(activeTool==="bbox") bboxMove_(e);
  else if(activeTool==="corner") cornerMove_(e);
  else if(activeTool==="polygon") polyMove_(e);
}
function pointerUp_(e){
  if(activeTool==="bbox") bboxEnd_(e);
  else if(activeTool==="corner") cornerEnd_(e);
}
canvas.addEventListener("mousedown", e=>{ e.preventDefault(); pointerDown_(e); },{passive:false});
canvas.addEventListener("mousemove", e=>{ e.preventDefault(); pointerMove_(e); },{passive:false});
canvas.addEventListener("mouseup",   e=>{ e.preventDefault(); pointerUp_(e); },{passive:false});
canvas.addEventListener("touchstart",e=>{
  e.preventDefault();
  if(e.touches.length===2){
    bboxDrawing=false; bboxCurrent=null;
    const vp=document.getElementById("zoom-viewport").getBoundingClientRect();
    const mid=touchMid(e.touches[0],e.touches[1],vp);
    pinchState={d0:touchDist(e.touches[0],e.touches[1]),s0:zoomScale,cx:mid.x,cy:mid.y,tx0:zoomTx,ty0:zoomTy,mx0:mid.x,my0:mid.y};
    redraw();
  } else { pointerDown_(e); }
},{passive:false});
canvas.addEventListener("touchmove", e=>{
  e.preventDefault();
  if(pinchState && e.touches.length===2){
    const vp=document.getElementById("zoom-viewport").getBoundingClientRect();
    const d=touchDist(e.touches[0],e.touches[1]);
    const mid=touchMid(e.touches[0],e.touches[1],vp);
    const newScale=Math.max(1,Math.min(6, pinchState.s0*(d/pinchState.d0)));
    const kx=(pinchState.cx-pinchState.tx0)/pinchState.s0, ky=(pinchState.cy-pinchState.ty0)/pinchState.s0;
    zoomScale=newScale;
    zoomTx=pinchState.cx-kx*zoomScale + (mid.x-pinchState.mx0);
    zoomTy=pinchState.cy-ky*zoomScale + (mid.y-pinchState.my0);
    clampPan(); applyZoom();
    return;
  }
  pointerMove_(e);
},{passive:false});
canvas.addEventListener("touchend",  e=>{
  e.preventDefault();
 if(pinchState && e.touches.length<2){ pinchState=null; return; }
  pointerUp_(e);
},{passive:false});
canvas.addEventListener("dblclick",  e=>{ e.preventDefault(); if(activeTool==="polygon") closePolygon(); });

// ── BBox ──────────────────────────────────────────────────────────────────────
function bboxStart_(e){
  if(!checkClase()) return;
  const p=getPos(e); bboxDrawing=true; bboxStart=p; bboxCurrent=null;
}
function bboxMove_(e){
  if(!bboxDrawing) return;
  const p=getPos(e);
  bboxCurrent={x:Math.min(bboxStart.x,p.x),y:Math.min(bboxStart.y,p.y),w:Math.abs(p.x-bboxStart.x),h:Math.abs(p.y-bboxStart.y)};
  redraw();
}
function bboxEnd_(e){
  bboxDrawing=false;
  if(bboxCurrent&&bboxCurrent.w>15&&bboxCurrent.h>15){
    const id=Date.now();
    const color=COLORS[annotations.length%COLORS.length];
    annotations.push({id,clase:currentClase,type:"bbox",bbox:{...bboxCurrent},color,checked:true,qty:null});
    bboxCurrent=null; redraw(); renderAnnoList(); updateButtons();
    if(arrumeMode){ bumpArrume(); showToast(`🔗 +1 ${currentClase} (${arrumeCount})`,"ok"); }
    else showQtyPrompt(id);
  } else { bboxCurrent=null; redraw(); }
}

// ── Esquinero (L-shape) ──────────────────────────────────────────────────────
function cornerStart_(e){
  if(!checkClase()) return;
  const p=getPos(e); cornerDrawing=true; cornerBaseStart=p;
  cornerState=null;
}
function cornerMove_(e){
  if(!cornerDrawing) return;
  const p=getPos(e);
  const b={x:Math.min(cornerBaseStart.x,p.x),y:Math.min(cornerBaseStart.y,p.y),w:Math.abs(p.x-cornerBaseStart.x),h:Math.abs(p.y-cornerBaseStart.y)};
  cornerState={base:b, corner:"TR", armW:Math.round(b.w*0.4), armH:Math.round(b.h*0.4)};
  redraw();
}
function cornerEnd_(e){
  cornerDrawing=false;
  if(!cornerState || cornerState.base.w<20 || cornerState.base.h<20){ cornerState=null; redraw(); return; }
  openCornerPanel();
  redraw();
}
function cornerCancel(){
  cornerState=null; cornerDrawing=false;
  const p=document.getElementById("corner-panel"); if(p) p.remove();
  redraw();
}
function cornerPolygonPoints(){
  if(!cornerState) return null;
  const {base:b, corner:c, armW:aw, armH:ah} = cornerState;
  const W=Math.min(aw,b.w-4), H=Math.min(ah,b.h-4);
  const TL={x:b.x,y:b.y}, TR={x:b.x+b.w,y:b.y}, BR={x:b.x+b.w,y:b.y+b.h}, BL={x:b.x,y:b.y+b.h};
  if(c==="TR") return [TL,{x:b.x+b.w-W,y:b.y},{x:b.x+b.w-W,y:b.y+H},{x:b.x+b.w,y:b.y+H},BR,BL];
  if(c==="TL") return [{x:b.x+W,y:b.y},TR,BR,BL,{x:b.x,y:b.y+H},{x:b.x+W,y:b.y+H}];
  if(c==="BR") return [TL,TR,{x:b.x+b.w,y:b.y+b.h-H},{x:b.x+b.w-W,y:b.y+b.h-H},{x:b.x+b.w-W,y:b.y+b.h},BL];
  if(c==="BL") return [TL,TR,BR,{x:b.x+W,y:b.y+b.h},{x:b.x+W,y:b.y+b.h-H},{x:b.x,y:b.y+b.h-H}];
  return null;
}
function openCornerPanel(){
  const ex=document.getElementById("corner-panel"); if(ex) ex.remove();
  const b=cornerState.base;
  const maxW=Math.floor(b.w-4), maxH=Math.floor(b.h-4);
  const div=document.createElement("div");
  div.id="corner-panel"; div.className="float-panel";
  div.innerHTML=`
    <div class="fp-head" id="cp-head">
      <span style="flex:1">📐 Esquinero — ajusta brazo</span>
      <button class="fp-btn" onclick="document.getElementById('corner-panel').classList.toggle('min')" title="Minimizar">▁</button>
      <button class="fp-btn" onclick="cornerCancel()" title="Cancelar">✕</button>
    </div>
    <div class="fp-body">
      <div style="font-size:10px;color:var(--steel);margin-bottom:6px">Esquina recortada:</div>
      <div class="corner-grid">
        <button class="corner-btn" data-c="TL" onclick="cornerSetCorner('TL')">↖ Sup-Izq</button>
        <button class="corner-btn active" data-c="TR" onclick="cornerSetCorner('TR')">↗ Sup-Der</button>
        <button class="corner-btn" data-c="BL" onclick="cornerSetCorner('BL')">↙ Inf-Izq</button>
        <button class="corner-btn" data-c="BR" onclick="cornerSetCorner('BR')">↘ Inf-Der</button>
      </div>
      <div class="slider-row"><label>Brazo ancho</label><input type="range" id="cp-w" min="4" max="${maxW}" value="${cornerState.armW}" oninput="cornerSetArm('w',this.value)"><span class="val" id="cp-w-v">${cornerState.armW}</span></div>
      <div class="slider-row"><label>Brazo alto</label><input type="range" id="cp-h" min="4" max="${maxH}" value="${cornerState.armH}" oninput="cornerSetArm('h',this.value)"><span class="val" id="cp-h-v">${cornerState.armH}</span></div>
      <div class="btn-row" style="margin-top:8px">
        <button class="btn btn-ghost btn-sm" onclick="cornerCancel()">Cancelar</button>
        <button class="btn btn-amber btn-sm" onclick="cornerConfirm()">✅ Guardar</button>
      </div>
    </div>`;
  document.body.appendChild(div);
  makeDraggable(div, document.getElementById("cp-head"));
}
function cornerSetCorner(c){
  if(!cornerState) return;
  cornerState.corner=c;
  document.querySelectorAll("#corner-panel .corner-btn").forEach(b=>b.classList.toggle("active",b.dataset.c===c));
  redraw();
}
function cornerSetArm(k,v){
  if(!cornerState) return;
  v=parseInt(v);
  if(k==="w"){ cornerState.armW=v; document.getElementById("cp-w-v").textContent=v; }
  else { cornerState.armH=v; document.getElementById("cp-h-v").textContent=v; }
  redraw();
}
function cornerConfirm(){
  const pts=cornerPolygonPoints(); if(!pts){ cornerCancel(); return; }
  const id=Date.now();
  const color=COLORS[annotations.length%COLORS.length];
  annotations.push({id,clase:currentClase,type:"polygon",points:pts,color,checked:true,qty:null,fromCorner:true});
  cornerCancel(); renderAnnoList(); updateButtons();
  if(arrumeMode){ bumpArrume(); showToast(`🔗 +1 ${currentClase} (${arrumeCount})`,"ok"); }
  else showQtyPrompt(id);
}

function makeDraggable(el, handle){
  let sx=0, sy=0, ox=0, oy=0, dragging=false;
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

// ── Polygon ───────────────────────────────────────────────────────────────────
let lastTapTime=0;
function polyTap(e){
  if(!checkClase()) return;
  const now=Date.now();
  if(now-lastTapTime<300){ closePolygon(); lastTapTime=0; return; }
  lastTapTime=now;
  const p=getPos(e);
  polyPoints.push(p); polyDrawing=true;
  document.getElementById("poly-toolbar").style.display="flex";
  document.getElementById("poly-pts-count").textContent=polyPoints.length+" punto"+(polyPoints.length!==1?"s":"");
  redraw();
}
function polyMove_(e){
  if(!polyDrawing||!polyPoints.length) return;
  const p=getPos(e); polyPreview=p; redraw();
}
function closePolygon(){
  if(polyPoints.length<3){ showToast("⚠️ Mínimo 3 puntos para cerrar","err"); return; }
  const id=Date.now();
  const color=COLORS[annotations.length%COLORS.length];
  annotations.push({id,clase:currentClase,type:"polygon",points:[...polyPoints],color,checked:true,qty:null});
  cancelPolygon(); redraw(); renderAnnoList(); updateButtons();
  if(arrumeMode){ bumpArrume(); showToast(`🔗 +1 ${currentClase} (${arrumeCount})`,"ok"); }
  else showQtyPrompt(id);
}
function cancelPolygon(){
  polyPoints=[]; polyDrawing=false; polyPreview=null;
  document.getElementById("poly-toolbar").style.display="none";
  redraw();
}

// ── Auto-segmento (flood-fill, reemplaza SAM) ──────────────────────────────────
function samStatus(msg,show=true){
  const el=document.getElementById("sam-status");
  if(!el) return;
  el.style.display=show?"block":"none";
  if(show) el.innerHTML=msg;
}

let _segCanvas=null, _segCtx=null, _segData=null, _segW=0, _segH=0;

function ensureSegCanvas(){
  const img=document.getElementById("bbox-img");
  if(!img||!img.naturalWidth) return false;
  const maxDim=400;
  const sc=Math.min(1, maxDim/Math.max(img.naturalWidth, img.naturalHeight));
  _segW=Math.round(img.naturalWidth*sc);
  _segH=Math.round(img.naturalHeight*sc);
  if(!_segCanvas){ _segCanvas=document.createElement("canvas"); _segCtx=_segCanvas.getContext("2d"); }
  _segCanvas.width=_segW; _segCanvas.height=_segH;
  _segCtx.drawImage(img,0,0,_segW,_segH);
  _segData=_segCtx.getImageData(0,0,_segW,_segH).data;
  return true;
}

function colorDist(r1,g1,b1,r2,g2,b2){ return Math.sqrt((r1-r2)**2+(g1-g2)**2+(b1-b2)**2); }

function floodFill(startX, startY, threshold){
  const W=_segW, H=_segH, data=_segData;
  const idx0=(startY*W+startX)*4;
  const sr=data[idx0], sg=data[idx0+1], sb=data[idx0+2];
  const visited=new Uint8Array(W*H);
  const mask=new Uint8Array(W*H);
  const stack=[[startX,startY]];
  let count=0;
  while(stack.length){
    const [x,y]=stack.pop();
    if(x<0||x>=W||y<0||y>=H) continue;
    const pi=y*W+x;
    if(visited[pi]) continue;
    visited[pi]=1;
    const di=pi*4;
    if(colorDist(data[di],data[di+1],data[di+2], sr,sg,sb) > threshold) continue;
    mask[pi]=1; count++;
    if(count > W*H*0.5) break;
    stack.push([x+1,y],[x-1,y],[x,y+1],[x,y-1]);
  }
  return {mask, count};
}

function nearestActivePixel(bin, W, H, tx, ty, maxR){
  maxR=maxR||Math.max(W,H);
  if(tx>=0&&tx<W&&ty>=0&&ty<H&&bin[ty*W+tx]) return {x:tx,y:ty};
  for(let r=1;r<=maxR;r++){
    for(let dx=-r;dx<=r;dx++){
      for(let dy=-r;dy<=r;dy++){
        if(Math.max(Math.abs(dx),Math.abs(dy))!==r) continue;
        const x=tx+dx, y=ty+dy;
        if(x>=0&&x<W&&y>=0&&y<H&&bin[y*W+x]) return {x,y};
      }
    }
  }
  return null;
}

function maskToContour(mask, W, H, tapX, tapY){
  let sx=-1, sy=-1;
  if(tapX!=null){
    const near=nearestActivePixel(mask, W, H, Math.round(tapX), Math.round(tapY), 80);
    if(near){ sx=near.x; sy=near.y; }
  }
  if(sx<0){
    for(let y=0;y<H&&sx<0;y++) for(let x=0;x<W;x++){ if(mask[y*W+x]){ sx=x; sy=y; break; } }
  }
  if(sx<0) return null;
  const dirs=[[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]];
  const contour=[]; let cx=sx, cy=sy, prevDir=6;
  const maxSteps=W*H*2; let steps=0;
  while(steps++<maxSteps){
    contour.push({x:cx,y:cy});
    let found=false;
    for(let i=0;i<8;i++){
      const d=(prevDir+6+i)%8;
      const nx=cx+dirs[d][0], ny=cy+dirs[d][1];
      if(nx>=0&&nx<W&&ny>=0&&ny<H&&mask[ny*W+nx]){
        cx=nx; cy=ny; prevDir=(d+4)%8; found=true; break;
      }
    }
    if(!found) break;
    if(cx===sx&&cy===sy&&contour.length>2) break;
    if(contour.length>4000) break;
  }
  if(contour.length<8) return null;
  const eps=Math.max(2, Math.min(W,H)*0.01);
  return douglasPeucker(contour, eps);
}

function douglasPeucker(pts, eps){
  if(pts.length<3) return pts;
  const first=0, last=pts.length-1;
  const keep=new Uint8Array(pts.length); keep[first]=1; keep[last]=1;
  const stack=[[first,last]];
  while(stack.length){
    const [a,b]=stack.pop();
    let maxD=0, idx=-1;
    const ax=pts[a].x, ay=pts[a].y, bx=pts[b].x, by=pts[b].y;
    const dx=bx-ax, dy=by-ay, len=Math.hypot(dx,dy)||1;
    for(let i=a+1;i<b;i++){
      const d=Math.abs((pts[i].x-ax)*dy - (pts[i].y-ay)*dx)/len;
      if(d>maxD){ maxD=d; idx=i; }
    }
    if(maxD>eps && idx>0){ keep[idx]=1; stack.push([a,idx]); stack.push([idx,b]); }
  }
  const out=[];
  for(let i=0;i<pts.length;i++) if(keep[i]) out.push(pts[i]);
  if(out.length>80){ const step=Math.ceil(out.length/80); return out.filter((_,i)=>i%step===0); }
  return out;
}

function polygonArea(pts){
  if(!pts||pts.length<3) return 0;
  let a=0; for(let i=0;i<pts.length;i++){ const p=pts[i], q=pts[(i+1)%pts.length]; a+=p.x*q.y-q.x*p.y; }
  return Math.abs(a)/2;
}

async function samTap(e){
  if(!selectedFile){ showToast("⚠️ Toma o carga una foto primero","err"); return; }
  samStatus("⏳ Segmentando…");
  try{
    if(!ensureSegCanvas()){ samStatus("❌ No se pudo procesar la imagen"); return; }
    const p=getPos(e);
    const sx=Math.round(p.x*(_segW/imgDispW));
    const sy=Math.round(p.y*(_segH/imgDispH));
    if(sx<0||sx>=_segW||sy<0||sy>=_segH){ samStatus("⚠️ Toca dentro de la imagen"); return; }
    const {mask, count} = floodFill(sx, sy, 35);
    if(count < 20){ samStatus("⚠️ No se detectó pieza clara. Intenta tocar más al centro."); return; }
    const contour = maskToContour(mask, _segW, _segH, sx, sy);
    if(!contour || contour.length<3){ samStatus("⚠️ No se detectó contorno claro."); return; }
    const scX=imgDispW/_segW, scY=imgDispH/_segH;
    const points=contour.map(pt=>({x:pt.x*scX, y:pt.y*scY}));
    const id=Date.now();
    const color=COLORS[annotations.length%COLORS.length];
    const clase=resolveClaseForAnnotation();
    const pending=!currentClase;
    annotations.push({id,clase,type:"polygon",points,color,checked:true,qty:null,fromSam:true,pendingAutoClass:pending});
    redraw(); renderAnnoList(); updateButtons();
    if(arrumeMode){ bumpArrume(); samStatus(`🔗 +1 ${clase} (${arrumeCount}) · toca otra pieza`); }
    else { samStatus(`✅ Pieza marcada · ${pending?"identificando…":"toca otra o revisa"}`); }
    if(pending) classifyAnnotationLocal(id); else if(!arrumeMode) showQtyPrompt(id);
  }catch(err){
    console.error("Auto-seg:",err);
    samStatus(`❌ Error: ${(err.message||err).toString().slice(0,80)}`);
  }
}

// ── Redraw ────────────────────────────────────────────────────────────────────
function redraw(){
  const ctx=canvas.getContext("2d");
  ctx.clearRect(0,0,canvas.width,canvas.height);
  annotations.forEach(a=>{
    if(!a.checked) return;
    ctx.strokeStyle=a.color; ctx.lineWidth=2.5; ctx.globalAlpha=1;
    if(a.type==="bbox"){
      const b=a.bbox;
      ctx.fillStyle="rgba(0,0,0,0.25)";
      ctx.fillRect(0,0,canvas.width,b.y);
      ctx.fillRect(0,b.y+b.h,canvas.width,canvas.height-b.y-b.h);
      ctx.fillRect(0,b.y,b.x,b.h);
      ctx.fillRect(b.x+b.w,b.y,canvas.width-b.x-b.w,b.h);
      ctx.strokeRect(b.x,b.y,b.w,b.h);
      drawCorners(ctx,b.x,b.y,b.w,b.h,a.color);
      drawLabel(ctx,a.clase,b.x,b.y,a.color);
      if(a.isQty){ drawQtyBox(ctx,a,b.x,b.y,b.w,b.h); }
    } else if(a.type==="polygon"){
      const pts=a.points;
      ctx.beginPath(); ctx.moveTo(pts[0].x,pts[0].y);
      pts.forEach(p=>ctx.lineTo(p.x,p.y)); ctx.closePath();
      ctx.fillStyle=a.color+"33"; ctx.fill();
      ctx.stroke();
      pts.forEach(p=>{ ctx.beginPath(); ctx.arc(p.x,p.y,4,0,Math.PI*2); ctx.fillStyle=a.color; ctx.fill(); });
      drawLabel(ctx,a.clase,pts[0].x,pts[0].y,a.color);
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
    polyPoints.forEach((p,i)=>{
      ctx.beginPath(); ctx.arc(p.x,p.y,i===0?6:4,0,Math.PI*2);
      ctx.fillStyle=i===0?"#f59e0b":"#fff"; ctx.fill();
    });
  }
}
function drawCorners(ctx,x,y,w,h,color){
  const cs=12; ctx.strokeStyle=color; ctx.lineWidth=4;
  [[x,y],[x+w,y],[x,y+h],[x+w,y+h]].forEach(([cx,cy])=>{
    const dx=cx===x?1:-1, dy=cy===y?1:-1;
    ctx.beginPath(); ctx.moveTo(cx+dx*cs,cy); ctx.lineTo(cx,cy); ctx.lineTo(cx,cy+dy*cs); ctx.stroke();
  });
}
function drawLabel(ctx,text,x,y,color){
  ctx.font="bold 12px -apple-system,sans-serif";
  const tw=ctx.measureText(text).width;
  const lx=x, ly=Math.max(20,y-4);
  ctx.fillStyle=color; ctx.fillRect(lx,ly-16,tw+10,20);
  ctx.fillStyle="#000"; ctx.fillText(text,lx+5,ly-2);
}
function drawQtyBox(ctx,a,bx,by,bw,bh){
  const num=a.clase.replace("QTY-","");
  const qw=Math.min(50,bw*0.25), qh=Math.min(28,bh*0.2);
  ctx.fillStyle="#22c55ecc"; ctx.fillRect(bx+4,by+4,qw,qh);
  ctx.fillStyle="#fff"; ctx.font=`bold ${Math.min(qh*.7,18)}px -apple-system,sans-serif`;
  ctx.textAlign="center"; ctx.textBaseline="middle";
  ctx.fillText(num,bx+4+qw/2,by+4+qh/2);
  ctx.textAlign="left"; ctx.textBaseline="alphabetic";
}

function checkClase(){
  if(!currentClase){ showToast("⚠️ Selecciona una clase primero","err"); return false; }
  return true;
}

// ── Lista de anotaciones ──────────────────────────────────────────────────────
function renderAnnoList(){
  const list=document.getElementById("anno-list");
  const card=document.getElementById("annos-card");
  const title=document.getElementById("annos-title");
  if(!annotations.length){ card.style.display="none"; return; }
  card.style.display="block";
  title.textContent=`📦 Anotaciones (${annotations.length})`;
  list.innerHTML="";
  annotations.forEach(a=>{
    const item=document.createElement("div"); item.className="anno-item";
    const qtyBadge=a.qty?`<span style="background:rgba(34,197,94,.2);color:var(--ok);border:1px solid rgba(34,197,94,.3);border-radius:6px;padding:2px 7px;font-size:10px;font-weight:700">×${a.qty}</span>`:"";
    const typeIcon=a.type==="polygon"?"🔷":"⬜";
    const qtyTag=a.isQty?`<span style="color:var(--ok);font-size:10px">📦</span>`:"";
    item.innerHTML=`
      <div class="anno-color" style="background:${a.color}"></div>
      <span class="anno-label" onclick="reassignClass(${a.id})" style="cursor:pointer;text-decoration:underline;text-decoration-style:dotted;text-underline-offset:3px" title="Cambiar clase">${a.clase}</span>
      <span class="anno-type">${typeIcon} ${a.type==="polygon"?"Polígono":"BBox"}</span>
      ${qtyBadge}${qtyTag}
      <span class="anno-check ${a.checked?"checked":"unchecked"}" onclick="toggleAnno(${a.id})">${a.checked?"✅":"☐"}</span>
      <span class="anno-del" onclick="deleteAnno(${a.id})">🗑️</span>`;
    list.appendChild(item);
  });
}
function toggleAnno(id){ const a=annotations.find(x=>x.id===id); if(a){a.checked=!a.checked;renderAnnoList();redraw();} }
function deleteAnno(id){ annotations=annotations.filter(x=>x.id!==id); renderAnnoList(); redraw(); updateButtons(); }
function updateButtons(){
  const has=annotations.some(a=>a.checked);
  document.getElementById("btn-review").disabled=!has;
  document.getElementById("btn-upload").disabled=!has;
}

// ── QTY prompt ────────────────────────────────────────────────────────────────
function showQtyPrompt(annoId){
  const ex=document.getElementById("qty-prompt"); if(ex) ex.remove();
  const div=document.createElement("div"); div.id="qty-prompt"; div.className="float-panel";
  div.style.width="280px";
  div.innerHTML=`
    <div class="fp-head" id="qty-head">
      <span style="flex:1">📦 ¿Cuántas piezas?</span>
      <button class="fp-btn" onclick="document.getElementById('qty-prompt').classList.toggle('min')" title="Minimizar">▁</button>
      <button class="fp-btn" onclick="skipQty()" title="Cerrar">✕</button>
    </div>
    <div class="fp-body">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
        <input type="number" id="qty-input" placeholder="Cantidad" min="1" max="999" style="flex:1;background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:9px 12px;color:var(--text);font-size:16px;outline:none;margin:0">
        <span style="font-size:12px;color:var(--steel)">piezas</span>
      </div>
      <div style="display:flex;gap:6px">
        <button onclick="skipQty()" style="flex:1;padding:9px;border-radius:8px;border:1.5px solid var(--border);background:var(--surface);color:var(--text2);font-size:12px;font-weight:600;cursor:pointer">Sin cantidad</button>
        <button onclick="addQty(${annoId})" style="flex:1;padding:9px;border-radius:8px;border:none;background:var(--amber);color:#0a1628;font-size:12px;font-weight:700;cursor:pointer">✅ Agregar</button>
      </div>
      <div style="font-size:10px;color:var(--steel);margin-top:6px;text-align:center">☝️ Arrastra el título para mover</div>
    </div>`;
  document.body.appendChild(div);
  makeDraggable(div, document.getElementById("qty-head"));
  setTimeout(()=>document.getElementById("qty-input")?.focus(),100);
}
function skipQty(){ const p=document.getElementById("qty-prompt"); if(p) p.remove(); showToast(`✅ Anotación añadida`,"ok"); }
function addQty(annoId){
  const qty=parseInt(document.getElementById("qty-input")?.value);
  const p=document.getElementById("qty-prompt"); if(p) p.remove();
  const anno=annotations.find(a=>a.id===annoId);
  if(!anno||!qty||qty<1){ showToast("✅ Añadida sin cantidad","ok"); return; }
  anno.qty=qty; anno.isArrume=true;
  const qtyId=Date.now()+1;
  let qtyBbox;
  if(anno.type==="bbox"){
    const b=anno.bbox;
    qtyBbox={x:b.x+4,y:b.y+4,w:Math.min(60,b.w*.25),h:Math.min(30,b.h*.2)};
  } else {
    const xs=anno.points.map(p=>p.x), ys=anno.points.map(p=>p.y);
    qtyBbox={x:Math.min(...xs)+4,y:Math.min(...ys)+4,w:60,h:30};
  }
  annotations.push({id:qtyId,clase:`QTY-${qty}`,type:"bbox",bbox:qtyBbox,color:"#22c55e",checked:true,isQty:true,parentId:annoId});
  redraw(); renderAnnoList(); updateButtons();
  showToast(`✅ ${anno.clase} × ${qty} piezas`,"ok");
}

// ── Review modal ──────────────────────────────────────────────────────────────
function openReview(){
  const img=document.getElementById("bbox-img");
  const rImg=document.getElementById("review-img");
  rImg.src=img.src;
  rImg.onload=()=>drawReviewCanvas();
  if(rImg.complete) drawReviewCanvas();
  const annos=document.getElementById("review-annos"); annos.innerHTML="";
  annotations.forEach(a=>{
    const div=document.createElement("div");
    div.className="review-anno "+(a.checked?"approved":"rejected");
    div.id="rev-"+a.id;
    const typeIcon=a.type==="polygon"?"🔷":"⬜";
    div.innerHTML=`
      <span class="review-check" onclick="toggleReviewAnno(${a.id})">${a.checked?"✅":"❌"}</span>
      <div style="flex:1">
        <div style="font-family:monospace;font-weight:700;font-size:14px;color:${a.color}">${a.clase}</div>
        <div style="font-size:11px;color:var(--steel)">${typeIcon} ${a.type==="polygon"?"Polígono ("+a.points?.length+" pts)":"BBox"} ${a.qty?"· ×"+a.qty+" piezas":""}</div>
      </div>`;
    annos.appendChild(div);
  });
  document.getElementById("review-modal-bg").classList.add("show");
}
function toggleReviewAnno(id){
  const a=annotations.find(x=>x.id===id); if(!a) return;
  a.checked=!a.checked;
  const div=document.getElementById("rev-"+id);
  div.className="review-anno "+(a.checked?"approved":"rejected");
  div.querySelector(".review-check").textContent=a.checked?"✅":"❌";
  renderAnnoList(); redraw(); drawReviewCanvas(); updateButtons();
}
function drawReviewCanvas(){
  const rImg=document.getElementById("review-img");
  const rc=document.getElementById("review-canvas");
  rc.width=rImg.offsetWidth; rc.height=rImg.offsetHeight;
  const scX=rImg.offsetWidth/imgDispW, scY=rImg.offsetHeight/imgDispH;
  const ctx=rc.getContext("2d"); ctx.clearRect(0,0,rc.width,rc.height);
  annotations.filter(a=>a.checked).forEach(a=>{
    ctx.strokeStyle=a.color; ctx.lineWidth=2.5;
    if(a.type==="bbox"){
      const b={x:a.bbox.x*scX,y:a.bbox.y*scY,w:a.bbox.w*scX,h:a.bbox.h*scY};
      ctx.strokeRect(b.x,b.y,b.w,b.h);
      drawLabel(ctx,a.clase,b.x,b.y,a.color);
    } else if(a.type==="polygon"){
      const pts=a.points.map(p=>({x:p.x*scX,y:p.y*scY}));
      ctx.beginPath(); ctx.moveTo(pts[0].x,pts[0].y);
      pts.forEach(p=>ctx.lineTo(p.x,p.y)); ctx.closePath();
      ctx.fillStyle=a.color+"33"; ctx.fill(); ctx.stroke();
      drawLabel(ctx,a.clase,pts[0].x,pts[0].y,a.color);
    }
  });
}
function closeReviewModal(e){ if(e.target===document.getElementById("review-modal-bg")) closeReviewModalDirect(); }
function closeReviewModalDirect(){ document.getElementById("review-modal-bg").classList.remove("show"); }
function confirmAndUpload(){ closeReviewModalDirect(); uploadAll(); }

// ── Catálogo modal ────────────────────────────────────────────────────────────
function openCatModal(){
  catModalFam="ALL"; document.getElementById("cat-modal-bg").classList.add("show");
  document.getElementById("cat-modal-search").value="";
  renderCatModalFams(); renderCatModal("");
  setTimeout(()=>document.getElementById("cat-modal-search").focus(),100);
}
function closeCatModal(e){ if(e.target===document.getElementById("cat-modal-bg")) closeCatModalDirect(); }
function closeCatModalDirect(){ document.getElementById("cat-modal-bg").classList.remove("show"); }
function renderCatModalFams(){
  const w=document.getElementById("cat-modal-families"); w.innerHTML="";
  ["ALL","PM","PB","EI","EE"].forEach(f=>{const b=document.createElement("div");b.className="fam-btn"+(f===catModalFam?" active":"");b.textContent=f==="ALL"?"Todas":f;b.onclick=()=>{catModalFam=f;renderCatModalFams();renderCatModal(document.getElementById("cat-modal-search").value);};w.appendChild(b);});
}
function renderCatModal(q){
  const list=document.getElementById("cat-modal-list"); list.innerHTML="";
  CATALOG.filter(c=>(catModalFam==="ALL"||c.family===catModalFam)&&(!q||c.code.toLowerCase().includes(q.toLowerCase()))).slice(0,60).forEach(c=>{
    const item=document.createElement("div"); item.className="cat-item";
    item.innerHTML=`<div onclick="setClase('${c.code}')"><div class="ci-code">${c.code}</div><div class="ci-spec">${c.spec}</div></div><span style="font-size:18px;cursor:pointer;padding:4px" onclick="copyCode('${c.code}')">📋</span>`;
    list.appendChild(item);
  });
}
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
function copyCode(code){ navigator.clipboard?.writeText(code).then(()=>showToast(`📋 ${code} copiado`,"ok")).catch(()=>{const t=document.createElement("textarea");t.value=code;document.body.appendChild(t);t.select();document.execCommand("copy");document.body.removeChild(t);showToast(`📋 ${code} copiado`,"ok");}); }

// ── Upload ────────────────────────────────────────────────────────────────────
async function uploadAll(){
  const apiKey=document.getElementById("api-key").value.trim();
  const split=document.getElementById("split").value;
  const checked=annotations.filter(a=>a.checked);
  if(!apiKey){showToast("⚠️ Ingresa tu API Key","err");return;}
  if(!selectedFile){showToast("⚠️ Selecciona imagen","err");return;}
  if(!checked.length){showToast("⚠️ Marca al menos una anotación","err");return;}
  const btn=document.getElementById("btn-upload"), btnR=document.getElementById("btn-review");
  btn.disabled=true; btnR.disabled=true; btn.innerHTML="⏳ Subiendo…"; btn.classList.add("loading");
  const pw=document.getElementById("prog-wrap"), pb=document.getElementById("prog-bar");
  pw.classList.add("show"); pb.style.width="15%";
  const logId=Date.now();
  const ext=selectedFile.name.split(".").pop()||"jpg";
  const baseName=checked.filter(a=>!a.isQty).map(a=>a.clase).join("_")+"_"+logId+"."+ext;
  const previewUrl=URL.createObjectURL(selectedFile);
  try{
    const b64=await fileToB64(selectedFile);
    pb.style.width="40%";
    const upRes=await fetchWithTimeout(`https://api.roboflow.com/dataset/${PROJECT}/upload?api_key=${apiKey}&name=${encodeURIComponent(baseName)}&split=${split}`,
      {method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:b64.split(",")[1]}, 30000);
    const upData=await upRes.json();
    if(!upRes.ok||upData.error) throw new Error(upData.error||`HTTP ${upRes.status}`);
    pb.style.width="65%";
    const imageId=upData.id||"";
    if(imageId){
      const scX=imgNatW/imgDispW, scY=imgNatH/imgDispH;
      const annoPayload={width:imgNatW,height:imgNatH,boxes:[]};
      checked.forEach(a=>{
        if(a.type==="bbox"){
          const b=a.bbox;
          annoPayload.boxes.push({label:a.clase,x:(b.x+b.w/2)*scX/imgNatW,y:(b.y+b.h/2)*scY/imgNatH,w:b.w*scX/imgNatW,h:b.h*scY/imgNatH});
        } else if(a.type==="polygon"){
          annoPayload.boxes.push({label:a.clase,points:a.points.map(p=>({x:p.x*scX/imgNatW,y:p.y*scY/imgNatH}))});
        }
      });
      const annoRes=await fetchWithTimeout(`https://api.roboflow.com/dataset/${PROJECT}/annotate/${imageId}?api_key=${apiKey}&name=${encodeURIComponent(baseName)}`,
        {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(annoPayload)}, 30000);
      const annoData=await annoRes.json();
      if(annoData.error) console.warn("Anotación:",annoData.error);
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
    renderClassStats();
    updateMemoryFromUpload(checked);
    showToast(`✅ ${checked.length} anotación(es) → Dataset`,"ok");
    resetAll();
  }catch(err){
    pb.style.background="var(--danger)";
    uploadLog.unshift({id:logId,url:previewUrl,annos:checked.map(a=>({clase:a.clase,color:a.color})),split,ok:false,error:err.message,file:selectedFile});
    addLogItem(uploadLog[0]);
    showToast(`❌ ${err.message.slice(0,50)}`,"err");
    setTimeout(()=>{pb.style.background="var(--amber)";pb.style.width="0%";pw.classList.remove("show");},2000);
  }finally{
    setTimeout(()=>{pb.style.width="0%";pw.classList.remove("show");},1500);
    btn.disabled=false; btnR.disabled=false; btn.innerHTML="⬆️ Subir"; btn.classList.remove("loading");
    updateButtons();
  }
}
function fileToB64(f){return new Promise((res,rej)=>{const r=new FileReader();r.onload=()=>res(r.result);r.onerror=()=>rej(new Error("Error"));r.readAsDataURL(f);});}
function discardPhoto(){
  if(!selectedFile){ return; }
  const nAnnos=annotations.length;
  const msg=nAnnos?`¿Descartar esta foto y sus ${nAnnos} anotación(es)? Podrás tomar o cargar otra de inmediato.`:"¿Descartar esta foto y tomar o cargar otra?";
  if(!confirm(msg)) return;
  resetAll();
  showToast("🗑️ Foto descartada · elige cámara o galería","ok");
}
function resetAll(){
  selectedFile=null; annotations=[]; bboxCurrent=null; bboxDrawing=false;
  cancelPolygon(); cornerCancel();
  document.getElementById("capture-zone").classList.remove("has-img");
  document.getElementById("bbox-section").style.display="none";
  document.getElementById("annos-card").style.display="none";
  document.getElementById("file-input-cam").value=""; document.getElementById("file-input-gal").value="";
  const ctx=canvas.getContext("2d"); ctx.clearRect(0,0,canvas.width,canvas.height);
  _segCanvas=null; _segData=null;
  samStatus("",false);
  arrumeCount=0;
  const ac=document.getElementById("arrume-counter"); if(ac) ac.textContent="×0";
  updateButtons();
}

// ── Log ───────────────────────────────────────────────────────────────────────
function addLogItem(entry){
  const list=document.getElementById("log-list");
  if(list.querySelector("p")) list.innerHTML="";
  const item=document.createElement("div");
  item.className="log-item"+(entry.ok?"":" error"); item.id="log-"+entry.id;
  const tags=(entry.annos||[]).map(a=>`<span class="log-anno-tag" style="background:${a.color}22;color:${a.color};border:1px solid ${a.color}44">${a.type==="polygon"?"🔷":"⬜"} ${a.clase}</span>`).join("");
  item.innerHTML=`
    <div class="log-header">
      <img class="log-thumb" src="${entry.url}" alt="">
      <div class="log-info">
        <div class="log-name">${(entry.annos||[]).length} anotación(es)</div>
        <div class="log-meta">${entry.ok?"✓ "+entry.split+" · con anotación":"✗ "+(entry.error||"")}</div>
        <div class="log-annos">${tags}</div>
      </div>
      <div class="log-actions">
        <span style="cursor:pointer;font-size:18px" onclick="retryEntry(${entry.id})" title="Reintentar">🔄</span>
        <span style="cursor:pointer;font-size:18px" onclick="deleteEntry(${entry.id})" title="Eliminar">🗑️</span>
        <span>${entry.ok?"✅":"❌"}</span>
      </div>
    </div>`;
  list.insertBefore(item,list.firstChild);
}
async function retryEntry(id){
  const apiKey=document.getElementById("api-key").value.trim();
  const entry=uploadLog.find(e=>e.id===id);
  if(!entry||!apiKey){showToast("⚠️ Falta API Key","err");return;}
  showToast("🔄 Reintentando…","");
  try{
    const b64=await fileToB64(entry.file);
    const name=(entry.annos||[]).map(a=>a.clase).join("_")+"_retry_"+Date.now()+".jpg";
    const res=await fetchWithTimeout(`https://api.roboflow.com/dataset/${PROJECT}/upload?api_key=${apiKey}&name=${encodeURIComponent(name)}&split=${entry.split}`,
      {method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:b64.split(",")[1]}, 30000);
    const data=await res.json();
    if(!res.ok||data.error) throw new Error(data.error||`HTTP ${res.status}`);
    entry.ok=true; entry.imageId=data.id||"";
    const item=document.getElementById("log-"+id);
    item.classList.remove("error");
    item.querySelector(".log-meta").textContent="✓ "+entry.split+" (reintento ✔)";
    item.querySelector(".log-actions span:last-child").textContent="✅";
    showToast("✅ Reintento exitoso","ok");
  }catch(err){showToast(`❌ ${err.message.slice(0,50)}`,"err");}
}
async function deleteEntry(id){
  const apiKey=document.getElementById("api-key").value.trim();
  const entry=uploadLog.find(e=>e.id===id);
  if(!entry) return;
  if(!confirm(`¿Eliminar imagen de Roboflow?`)) return;
  if(entry.imageId&&apiKey){ try{await fetch(`https://api.roboflow.com/dataset/${PROJECT}/images/${entry.imageId}?api_key=${apiKey}`,{method:"DELETE"});}catch(e){} }
  document.getElementById("log-"+id)?.remove();
  uploadLog=uploadLog.filter(e=>e.id!==id);
  const list=document.getElementById("log-list");
  if(!list.children.length) list.innerHTML='<p style="color:var(--steel);font-size:13px;text-align:center;padding:20px">Las subidas aparecerán aquí</p>';
  showToast("🗑️ Eliminada","ok");
}
function showToast(msg,type){const t=document.getElementById("toast");t.textContent=msg;t.className=`toast ${type} show`;setTimeout(()=>t.classList.remove("show"),2800);}
function downloadApp(){
  const html=document.documentElement.outerHTML;
  const blob=new Blob(['<!DOCTYPE html>\n'+html],{type:'text/html'});
  const url=URL.createObjectURL(blob);
  const a=document.createElement('a');
  a.href=url; a.download='UNISPAN-Dataset-v13.html'; document.body.appendChild(a); a.click();
  document.body.removeChild(a); URL.revokeObjectURL(url);
  showToast("⬇ Archivo descargado","ok");
}

// ── Estadísticas por clase ────────────────────────────────────────────────────
function toggleStats(){
  const b=document.getElementById("stats-body");
  const c=document.getElementById("stats-caret");
  const open=b.style.display==="none";
  b.style.display=open?"block":"none";
  c.textContent=open?"▲":"▼";
  if(open) renderClassStats();
}
function renderClassStats(){
  const list=document.getElementById("stats-list");
  const total=Object.values(classCounts).reduce((a,b)=>a+b,0);
  document.getElementById("stats-total").textContent=`(${total} img · ${Object.keys(classCounts).length} clases)`;
  if(!list) return;
  const entries=Object.entries(classCounts).sort((a,b)=>b[1]-a[1]);
  if(!entries.length){ list.innerHTML='<div style="color:var(--steel);font-size:12px;text-align:center;padding:14px">Sin datos aún. Sube imágenes para ver el balance.</div>'; return; }
  list.innerHTML=entries.map(([code,n])=>{
    const pct=Math.min(100,Math.round(n/CLASS_GOAL*100));
    const cls=n>=CLASS_GOAL?"ok":n<10?"low":"";
    const flag=n>=CLASS_GOAL?"✅":n<10?"⚠️":"";
    return `<div class="stat-row" style="flex-direction:column;align-items:stretch;gap:4px">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span class="stat-code">${flag} ${code}</span>
        <span class="stat-count ${cls}">${n}/${CLASS_GOAL}</span>
      </div>
      <div class="stat-bar"><div class="stat-bar-fill" style="width:${pct}%;background:${cls==="ok"?"var(--ok)":cls==="low"?"var(--danger)":"var(--amber)"}"></div></div>
    </div>`;
  }).join("");
}
function resetStats(){
  if(!confirm("¿Reiniciar el contador local de imágenes por clase? (No borra nada en Roboflow)")) return;
  classCounts={}; localStorage.setItem("rf_class_counts","{}"); renderClassStats();
}
renderClassStats();
// ══════════════════════════════════════════════════════════════════════════════
// AGENTE EXPERTO — Base de conocimiento local sobre paneles formaleta UNISPAN
// ══════════════════════════════════════════════════════════════════════════════
const EXPERT_KB=[
 {t:"Lámina (cara de contacto)",k:["lamina","lámina","cara","contacto","superficie","acero","espesor","chapa"],
  a:"La <b>lámina</b> es la cara de contacto con el concreto. En paneles UNISPAN es de acero de 3–5 mm (típ. 3 mm en PM/PB, 4–5 mm en refuerzos pesados). Se identifica por su superficie lisa continua, bordes soldados al marco perimetral y por la ausencia de perforaciones en su cara frontal (las perforaciones van en las <i>bridas laterales</i>, no en la lámina). Un panel visto de frente muestra: lámina central + marco perimetral con perforaciones."},
 {t:"Bridas / marco perimetral",k:["brida","bridas","marco","perimetral","canto","borde","perfil"],
  a:"Las <b>bridas</b> son los perfiles laterales que forman el marco perimetral del panel. Sostienen la lámina y contienen las <b>perforaciones para pasadores y grapas</b> de unión entre paneles. Se identifican como una franja perimetral de ~55–65 mm de ancho con agujeros equidistantes. Familias:<br>• PM/PB: brida plana con perforaciones circulares y ranuras.<br>• EI (esquina interior): dos bridas a 90°.<br>• EE (esquina exterior): dos bridas a 90° hacia afuera."},
 {t:"Platinas de unión",k:["platina","platinas","union","unión","placa","enlace"],
  a:"Las <b>platinas</b> son placas metálicas planas soldadas o atornilladas que refuerzan uniones entre bridas o entre panel y refuerzo estructural. Suelen ser de acero 4–6 mm con 2 a 4 perforaciones. Se distinguen de una brida porque son <b>piezas puntuales</b> (no corren todo el borde) y suelen estar en esquinas o en cruces de refuerzos transversales."},
 {t:"Refuerzos: tipos generales",k:["refuerzo","refuerzos","costilla","nervio","tipos"],
  a:"Un panel formaleta tiene tres tipos de refuerzos:<br>1) <b>Refuerzo transversal</b> — perfiles horizontales/verticales soldados por detrás de la lámina cada 200–300 mm. Mantienen la planitud bajo presión de concreto.<br>2) <b>Refuerzo estructural (principal)</b> — perfiles más pesados (tubulares o C) que dan rigidez global; suelen ir en pares por la cara posterior.<br>3) <b>Refuerzo de brida</b> — pequeñas cartelas triangulares que unen brida con refuerzo transversal."},
 {t:"Refuerzo transversal",k:["transversal","costilla","horizontal","nervio","separacion","separación"],
  a:"El <b>refuerzo transversal</b> son perfiles (típicamente tubulares 40×20 mm o omega) soldados perpendicularmente a la lámina en la cara posterior. Se cuentan <b>de 3 a 6 refuerzos</b> según el ancho del panel. Regla práctica: separación entre ejes 200–300 mm. Su presencia y cantidad permiten distinguir un PM-2400×600 (más refuerzos) de un PB-2400×150 (uno o dos)."},
 {t:"Refuerzo estructural",k:["estructural","principal","tubular","viga","rigidez"],
  a:"El <b>refuerzo estructural</b> es el par de perfiles principales (tubo rectangular 60×40 o similar) que corren longitudinalmente por la cara posterior. Sostienen los refuerzos transversales y transmiten la carga a los pasadores. Un panel PM completo se identifica por: 2 refuerzos estructurales longitudinales + 4–6 transversales."},
 {t:"Ángulos y esquineros",k:["angulo","ángulo","esquina","esquinero","EI","EE","interior","exterior"],
  a:"Los <b>ángulos</b> son piezas conformadas a 90° para esquinas de muro:<br>• <b>EI (Esquina Interior)</b> — dos bridas hacia adentro, forman rincón interior.<br>• <b>EE (Esquina Exterior)</b> — dos bridas hacia afuera, forman canto de muro.<br>Se identifican por la <b>línea de doblez central</b> visible en la lámina y por tener perforaciones simétricas en ambas alas. Los códigos incluyen el ancho de cada ala (ej. EI-2400×150×150)."},
 {t:"Perforaciones rectangulares",k:["rectangular","rectangulares","ranura","ranuras","oblonga","oblongas","slot"],
  a:"Las <b>perforaciones rectangulares (ranuras)</b> permiten ajuste dimensional en obra. Aparecen en las bridas alternadas con las circulares. Dimensiones típicas: 15×30 mm. Su presencia indica que la pieza es un <b>panel principal</b>; los accesorios (platinas cortas, tapas) usualmente solo tienen circulares."},
 {t:"Perforaciones en la lámina",k:["perforacion lamina","perforación lámina","agujero lamina","cara","frontal lamina"],
  a:"Las <b>perforaciones frontales en la lámina</b> son <b>anómalas</b> en paneles estándar: la cara de contacto debe ser continua. Si aparecen, indican:<br>• Panel para <b>anclajes pasantes</b> (tie-rods) — agujeros de ~22 mm alineados verticalmente.<br>• Panel <b>reparado</b> o modificado (evitar en dataset limpio).<br>Marca estos casos con una clase separada para que el modelo no los confunda con paneles estándar."},
 {t:"Perforaciones frontales (identificación)",k:["frontal","frontales","cara frontal","vista frontal","brida corta","ancho"],
  a:"<b>Perforaciones frontales</b> = las de las <b>bridas cortas (extremos)</b> del panel, sobre el lado del ancho. Con paso de 50 mm y inicio a 25 mm:<br>• Ancho 600 mm ⇒ <b>12 perforaciones frontales</b>.<br>• Ancho 500 mm ⇒ <b>10 perforaciones frontales</b>.<br>• Ancho 400 mm ⇒ 8 · 300 mm ⇒ 6 · 200 mm ⇒ 4.<br>Fórmula: <code>n = (ancho − 2×25)/50 + 1 = ancho/50</code>. Contar las frontales es el camino más rápido para conocer el <b>ancho</b> del panel."},
 {t:"Perforaciones laterales (identificación)",k:["lateral","laterales","canto","vista lateral","perfil lateral","brida larga","longitud"],
  a:"<b>Perforaciones laterales</b> = las de las <b>bridas largas</b>, a lo largo de la longitud del panel. Con paso de 50 mm e inicio a 25 mm:<br>• Longitud 2400 mm ⇒ <b>48 perforaciones laterales</b>.<br>• 1200 ⇒ 24 · 900 ⇒ 18 · 800 ⇒ 16 · 600 ⇒ 12.<br>Fórmula: <code>n = longitud/50</code>. Contar las laterales revela la <b>longitud</b>."},
 {t:"Inicio de las perforaciones",k:["inicio","comienzo","primera perforacion","primera perforación","borde perforacion","distancia borde","25 mm","2.5 cm"],
  a:"El <b>inicio de las perforaciones</b> UNISPAN: <b>25 mm (2.5 cm)</b> desde el borde del panel al centro de la primera perforación, tanto en bridas frontales (cortas) como laterales (largas). Este valor es constante y sirve para verificar que la pieza es UNISPAN estándar."},
 {t:"Medidas entre centros de perforaciones",k:["centro","centros","distancia","paso","pitch","separacion","separación","entre perforaciones","50 mm","5 cm"],
  a:"<b>Paso entre centros UNISPAN: 50 mm (5 cm)</b>, constante en bridas frontales y laterales.<br>Regla: <code>n = (medida − 2×25)/50 + 1 = medida/50</code>.<br>Ej: 2400 mm ⇒ 48 · 600 mm ⇒ 12 · 500 mm ⇒ 10 · 400 mm ⇒ 8.<br>Este par (25 mm inicio + 50 mm paso) es la <b>firma dimensional</b> del sistema."},
 {t:"Tabla de perforaciones por referencia",k:["tabla","referencia","lookup","matriz","cuantas perforaciones","cuántas perforaciones","cuenta"],
  a:"<b>Frontales (por ancho) × Laterales (por longitud):</b><br><table style='width:100%;border-collapse:collapse;font-size:11px;margin-top:6px'><tr style='background:#0b1220;color:var(--amber)'><th style='padding:4px;border:1px solid #334'>Ancho</th><th style='padding:4px;border:1px solid #334'>Frontales</th><th style='padding:4px;border:1px solid #334'>Longitud</th><th style='padding:4px;border:1px solid #334'>Laterales</th></tr><tr><td style='padding:4px;border:1px solid #334'>600</td><td style='padding:4px;border:1px solid #334'>12</td><td style='padding:4px;border:1px solid #334'>2400</td><td style='padding:4px;border:1px solid #334'>48</td></tr><tr><td style='padding:4px;border:1px solid #334'>500</td><td style='padding:4px;border:1px solid #334'>10</td><td style='padding:4px;border:1px solid #334'>1200</td><td style='padding:4px;border:1px solid #334'>24</td></tr><tr><td style='padding:4px;border:1px solid #334'>450</td><td style='padding:4px;border:1px solid #334'>9</td><td style='padding:4px;border:1px solid #334'>900</td><td style='padding:4px;border:1px solid #334'>18</td></tr><tr><td style='padding:4px;border:1px solid #334'>400</td><td style='padding:4px;border:1px solid #334'>8</td><td style='padding:4px;border:1px solid #334'>800</td><td style='padding:4px;border:1px solid #334'>16</td></tr><tr><td style='padding:4px;border:1px solid #334'>350</td><td style='padding:4px;border:1px solid #334'>7</td><td style='padding:4px;border:1px solid #334'>750</td><td style='padding:4px;border:1px solid #334'>15</td></tr><tr><td style='padding:4px;border:1px solid #334'>300</td><td style='padding:4px;border:1px solid #334'>6</td><td style='padding:4px;border:1px solid #334'>600</td><td style='padding:4px;border:1px solid #334'>12</td></tr><tr><td style='padding:4px;border:1px solid #334'>250</td><td style='padding:4px;border:1px solid #334'>5</td><td style='padding:4px;border:1px solid #334'>500</td><td style='padding:4px;border:1px solid #334'>10</td></tr><tr><td style='padding:4px;border:1px solid #334'>200</td><td style='padding:4px;border:1px solid #334'>4</td><td style='padding:4px;border:1px solid #334'>400</td><td style='padding:4px;border:1px solid #334'>8</td></tr><tr><td style='padding:4px;border:1px solid #334'>150</td><td style='padding:4px;border:1px solid #334'>3</td><td style='padding:4px;border:1px solid #334'>300</td><td style='padding:4px;border:1px solid #334'>6</td></tr><tr><td style='padding:4px;border:1px solid #334'>100</td><td style='padding:4px;border:1px solid #334'>2</td><td style='padding:4px;border:1px solid #334'>200</td><td style='padding:4px;border:1px solid #334'>4</td></tr></table><br>Usa la calculadora arriba para cualquier medida."},
 {t:"Cómo identificar un panel paso a paso",k:["identificar","como identificar","cómo identificar","paso a paso","procedimiento","reconocer"],
  a:"<b>Procedimiento de identificación:</b><br>1) ¿Recto o esquinero? Doblez central ⇒ EI/EE.<br>2) Cuenta <b>perforaciones frontales</b> (bridas cortas) → ancho = frontales × 50 mm.<br>3) Cuenta <b>perforaciones laterales</b> (bridas largas) → longitud = laterales × 50 mm.<br>4) Ejemplo: 12 frontales + 48 laterales ⇒ <b>2400 × 600 mm</b>.<br>5) Verifica familia por ancho: PM (300–600), PB (80–270).<br>6) Confirma inicio 25 mm y paso 50 mm.<br>7) Cuenta refuerzos transversales por atrás como validación cruzada."},
 {t:"Buenas fotos para el dataset",k:["foto","fotos","dataset","imagenes","imágenes","calidad","angulo","ángulo","varios"],
  a:"Para <b>30 imágenes por clase</b> (meta inicial v7), cubre estos ángulos:<br>• 6 frontales (cara de contacto, distinta iluminación).<br>• 6 posteriores (mostrando refuerzos).<br>• 6 laterales / canto.<br>• 6 en arrume (varias piezas juntas — anota todas).<br>• 6 en obra / instaladas.<br>Evita fotos borrosas (v5 detector), asegura que las perforaciones se vean nítidas — son la firma identificatoria del panel."},
];

let expertInited=false;
function expertInit(){
  if(expertInited) return; expertInited=true;
  const chips=document.getElementById("expert-chips");
  const topics=["Lámina","Bridas","Platinas","Refuerzos","Transversal","Estructural","Ángulos EI/EE","Rectangulares","Perforaciones frontales","Perforaciones laterales","Inicio de perforación","Distancia entre centros","Tabla de perforaciones","Identificar paso a paso","Buenas fotos"];
  chips.innerHTML=topics.map(t=>`<span onclick="expertSay('${t}')" style="background:#1a2130;color:#f59e0b;padding:6px 10px;border-radius:14px;font-size:11px;cursor:pointer;border:1px solid #334">${t}</span>`).join("");
  expertBot("¡Hola! Soy el <b>agente experto UNISPAN</b>. Pregúntame sobre láminas, bridas, refuerzos, perforaciones o cómo identificar una pieza. También puedes tocar un tema arriba. <b>Funciono sin claves ni conexión.</b>");
}
function expertBot(html){
  const c=document.getElementById("expert-chat");
  c.insertAdjacentHTML("beforeend",`<div style="margin:6px 0;padding:10px;background:#1a2130;border-radius:8px;border-left:3px solid var(--amber)"><b style="color:var(--amber)">🎓 Experto:</b><br>${html}</div>`);
  c.scrollTop=c.scrollHeight;
}
function expertUser(txt){
  const c=document.getElementById("expert-chat");
  c.insertAdjacentHTML("beforeend",`<div style="margin:6px 0;padding:8px 10px;background:#0b1220;border-radius:8px;text-align:right;color:#cbd5e1"><b>Tú:</b> ${txt}</div>`);
  c.scrollTop=c.scrollHeight;
}
function expertSay(topic){ document.getElementById("expert-input").value=topic; expertAsk(); }
function normTxt(s){ return s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,""); }
function memoryContextForAI(){
  if(!imgMemory.length) return "Memoria vacía (aún no se ha capturado ninguna imagen).";
  const byClass={};
  imgMemory.forEach(e=>e.classes.forEach(c=>{ byClass[c]=(byClass[c]||0)+1; }));
  const clsList=Object.entries(byClass).sort((a,b)=>b[1]-a[1]).slice(0,15).map(([c,n])=>`${c}:${n}`).join(", ")||"(sin clases anotadas)";
  const withAI=imgMemory.filter(e=>e.aiObs);
  const lastAI=withAI[0]?.aiObs;
  const lastProof=physicalProofs[0];
  const proofTxt=lastProof?`Última prueba física: conteo_total=${lastProof.conteo_total||"?"}; piezas=${(lastProof.piezas||[]).map(p=>validateAIReference(p)+"×"+(p.cantidad||1)).join(", ")||"-"}; arrumes=${(lastProof.arrumes||[]).map(a=>validateAIReference(a)+"×"+(a.cantidad_estimada||a.cantidad||"?")).join(", ")||"-"}.`:"Sin prueba física todavía.";
  let lastAiTxt="(sin análisis previo)";
  if(lastAI){
    if(typeof lastAI==="object"){
      lastAiTxt=`tipo=${lastAI.tipo||"?"} familia=${lastAI.familia||"?"} ref=${lastAI.referencia_validada||"?"} ancho=${lastAI.ancho_mm||"?"} largo=${lastAI.largo_mm||"?"} frontales=${lastAI.frontales||"?"} laterales=${lastAI.laterales||"?"} anomalias=${lastAI.anomalias||"-"}`;
    } else lastAiTxt=String(lastAI).slice(0,300);
  }
  return `Imágenes capturadas: ${imgMemory.length} (${withAI.length} con análisis).\nClases anotadas: ${clsList}.\nÚltima observación: ${lastAiTxt}.\n${proofTxt}`;
}
async function askAIExpertFallback(question){
  const key=(document.getElementById("openai-key")?.value||"").trim();
  if(!key) return null;
  const ctx=memoryContextForAI();
  const kbBrief=EXPERT_KB.map(e=>`• ${e.t}`).join("\n");
  const sys=`Eres el agente experto UNISPAN. Sabes de láminas, bridas, platinas, refuerzos (transversal, estructural, brida), ángulos EI/EE, perforaciones (inicio 25mm, paso 50mm ⇒ n=medida/50), y de identificar piezas por perforaciones frontales (ancho) y laterales (largo).\nCatálogo real:\n${catalogSummaryForPrompt()}\nTemas conocidos:\n${kbBrief}\nEstado actual de la captura de este usuario:\n${ctx}\nResponde en español, breve y práctico (máx 6 líneas), usando <b> para lo clave. Si la pregunta se refiere a "la foto actual" o "lo que capturé", usa la observación de arriba. Si no hay datos suficientes, dilo.`;
  try{
    const res=await fetchWithTimeout("https://api.openai.com/v1/chat/completions",
      {method:"POST",headers:{"Content-Type":"application/json","Authorization":"Bearer "+key},
      body:JSON.stringify({model:"gpt-4o-mini",messages:[{role:"system",content:sys},{role:"user",content:question}],max_tokens:350})}, 15000);
    const data=await res.json();
    if(!res.ok) throw new Error(data.error?.message||`HTTP ${res.status}`);
    return data.choices?.[0]?.message?.content||null;
  }catch(err){
    return `<span style="color:var(--danger)">❌ IA falló: ${err.message}</span>`;
  }
}
async function expertAsk(){
  const inp=document.getElementById("expert-input");
  const q=inp.value.trim(); if(!q) return;
  inp.value=""; expertUser(q);
  const qn=normTxt(q);
  const scored=EXPERT_KB.map(e=>{
    const hay=normTxt(e.t+" "+e.k.join(" "));
    let s=0;
    qn.split(/\s+/).filter(w=>w.length>2).forEach(w=>{ if(hay.includes(w)) s+=w.length; });
    e.k.forEach(k=>{ if(qn.includes(normTxt(k))) s+=6; });
    return {e,s};
  }).sort((a,b)=>b.s-a.s);
  const wantsContext=/\b(foto|imagen|captur|actual|memoria|analic|reciente|ultim|últim|qu[eé] tom|qu[eé] veo|reconoc)/i.test(q);
  const hasKey=!!(document.getElementById("openai-key")?.value||"").trim();
  if(scored[0].s===0 || wantsContext){
    if(hasKey){
      expertBot("⏳ Consultando IA…");
      const c=document.getElementById("expert-chat"); const loading=c.lastElementChild;
      const ans=await askAIExpertFallback(q);
      if(loading) loading.remove();
      if(ans){ expertBot(`🤖 <i>IA</i>: ${ans}`); return; }
    }
    if(wantsContext){
      const ctx=memoryContextForAI();
      expertBot(`📊 <b>Estado actual de captura:</b><br><pre style="white-space:pre-wrap;font-size:11px;margin-top:4px">${ctx}</pre>`);
      return;
    }
    if(scored[0].s===0){
      expertBot("No encontré una coincidencia clara en la base local. Temas disponibles: <i>lámina, brida, platina, refuerzo transversal, ángulo EI/EE, perforación frontal, distancia entre centros, inicio de perforación</i>. Si agregas una API key OpenAI arriba puedo razonar sobre tus capturas.");
      return;
    }
  }
  const top=scored[0].e;
  let out=`<b>${top.t}</b><br>${top.a}`;
  const rel=scored.slice(1,4).filter(x=>x.s>0);
  if(rel.length){
    out+=`<div style="margin-top:8px;font-size:11px;color:var(--steel)">También relacionado: ${rel.map(x=>`<span onclick="expertSay('${x.e.t}')" style="color:var(--amber);cursor:pointer;text-decoration:underline">${x.e.t}</span>`).join(" · ")}</div>`;
  }
  expertBot(out);
}

// ── Calculadora perforaciones ⇄ medidas ──────────────────────────────────────
const PITCH=50, START=25;
const STD_W=[600,500,450,400,350,300,270,250,230,200,150,120,100,90,80];
const STD_L=[2400,1200,900,800,750,600];
function nearest(v,arr){ return arr.reduce((a,b)=>Math.abs(b-v)<Math.abs(a-v)?b:a); }
function familyFor(w){ if(w>=300&&w<=600) return "PM"; if(w>=80&&w<=270) return "PB"; return "?"; }
function calcOut(html){ document.getElementById("calc-out").innerHTML=html; }
function calcFromDims(){
  const w=+document.getElementById("calc-w").value, l=+document.getElementById("calc-l").value;
  if(!w && !l){ calcOut("Ingresa medidas o conteos · inicio 25 mm · paso 50 mm"); return; }
  let out=[];
  if(w>0){ const nf=Math.round(w/PITCH); document.getElementById("calc-nf").value=nf; out.push(`Ancho ${w} mm ⇒ <b>${nf} frontales</b>`); }
  if(l>0){ const nl=Math.round(l/PITCH); document.getElementById("calc-nl").value=nl; out.push(`Longitud ${l} mm ⇒ <b>${nl} laterales</b>`); }
  if(w>0 && l>0){
    const fam=familyFor(w), sw=nearest(w,STD_W), sl=nearest(l,STD_L);
    out.push(`<span style="color:var(--amber)">Referencia sugerida: <b>${fam}-${sl}x${sw}</b></span>`);
  }
  calcOut(out.join("<br>"));
}
function calcFromCounts(){
  const nf=+document.getElementById("calc-nf").value, nl=+document.getElementById("calc-nl").value;
  if(!nf && !nl){ calcOut("Ingresa medidas o conteos · inicio 25 mm · paso 50 mm"); return; }
  let out=[];
  if(nf>0){ const w=nf*PITCH; document.getElementById("calc-w").value=w; out.push(`${nf} frontales ⇒ ancho <b>${w} mm</b>`); }
  if(nl>0){ const l=nl*PITCH; document.getElementById("calc-l").value=l; out.push(`${nl} laterales ⇒ longitud <b>${l} mm</b>`); }
  if(nf>0 && nl>0){
    const w=nf*PITCH, l=nl*PITCH, fam=familyFor(w), sw=nearest(w,STD_W), sl=nearest(l,STD_L);
    out.push(`<span style="color:var(--amber)">Referencia sugerida: <b>${fam}-${sl}x${sw}</b></span>`);
  }
  calcOut(out.join("<br>"));
}

// ══════════════════════════════════════════════════════════════════════════════
// MEMORIA + ANÁLISIS LOCAL (sin API key requerida)
// ══════════════════════════════════════════════════════════════════════════════
const savedOpenAIKey=localStorage.getItem("openai_key");
if(savedOpenAIKey) { const el=document.getElementById("openai-key"); if(el) el.value=savedOpenAIKey; }
document.addEventListener("blur",e=>{ if(e.target?.id==="openai-key") localStorage.setItem("openai_key",e.target.value.trim()); },true);

let _lastMemoryEntry=null;
function recordMemory(img,file){
  const w=img.naturalWidth, h=img.naturalHeight;
  const aspect=+(w/h).toFixed(3);
  const entry={
    id:Date.now(), filename:file?.name||"cam", w,h,aspect,
    orientation: aspect>1.2?"horizontal":aspect<0.83?"vertical":"cuadrada",
    classes:[], qty:null, blur:null, note:"", aiObs:null,
    date:new Date().toISOString(),
  };
  imgMemory.unshift(entry); if(imgMemory.length>200) imgMemory.length=200;
  _lastMemoryEntry=entry; saveMemory();
}
function updateMemoryFromUpload(checkedAnnos){
  if(!_lastMemoryEntry) return;
  const clsList=[...new Set(checkedAnnos.filter(a=>!a.isQty).map(a=>a.clase))];
  _lastMemoryEntry.classes=clsList;
  _lastMemoryEntry.qty=checkedAnnos.find(a=>a.qty)?.qty||null;
  saveMemory();
}

// ── Análisis local de imagen: detecta contornos y estima dimensiones ────────────
function safeHtml(s){ return String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c])); }
function parseAIJson(raw){
  if(!raw) return null;
  try{ return JSON.parse(raw); }catch(_){ }
  const m=String(raw).match(/\{[\s\S]*\}/);
  if(!m) return null;
  try{ return JSON.parse(m[0]); }catch(_){ return null; }
}
function catalogByCode(code){ return CATALOG.find(c=>c.code.toUpperCase()===String(code||"").toUpperCase()); }
function dimsFromCode(code){
  const s=String(code||"").toUpperCase();
  let m=s.match(/^(PM|PB)-(\d+)X(\d+)$/); if(m) return {family:m[1],largo:+m[2],ancho:+m[3]};
  m=s.match(/^(EI|EE)-(\d+)X(\d+)X(\d+)$/); if(m) return {family:m[1],largo:+m[2],ancho:+m[3]};
  return null;
}
function validateAIReference(obj){
  if(!obj) return null;
  let ref=String(obj.referencia||obj.referencia_validada||obj.codigo||"").toUpperCase().replace(/×/g,"x");
  if(ref && catalogByCode(ref)) return ref;
  const fam=String(obj.familia||dimsFromCode(ref)?.family||"").toUpperCase();
  const largo=+(obj.largo_mm||obj.longitud_mm||dimsFromCode(ref)?.largo||0);
  const ancho=+(obj.ancho_mm||dimsFromCode(ref)?.ancho||0);
  if(["PM","PB","EI","EE"].includes(fam) && (largo||ancho)){
    const match=nearestCatalogMatch(fam,largo,ancho);
    if(match) return match.code;
  }
  return ref || "POR-IDENTIFICAR";
}
function resolveClaseForAnnotation(){
  if(currentClase) return currentClase;
  const last=physicalProofs[0];
  const p=last?.piezas?.[0] || last?.arrumes?.[0];
  const ref=validateAIReference(p||{});
  return ref && ref!=="POR-IDENTIFICAR" ? ref : "POR-IDENTIFICAR";
}
function annotationBounds(a){
  if(!a) return null;
  if(a.type==="bbox") return {...a.bbox};
  if(a.type==="polygon" && a.points?.length){
    const xs=a.points.map(p=>p.x), ys=a.points.map(p=>p.y);
    return {x:Math.min(...xs),y:Math.min(...ys),w:Math.max(...xs)-Math.min(...xs),h:Math.max(...ys)-Math.min(...ys)};
  }
  return null;
}
function annotationCropDataUrl(a,pad=.08){
  const b=annotationBounds(a); if(!b) return null;
  const img=document.getElementById("bbox-img");
  const scX=imgNatW/imgDispW, scY=imgNatH/imgDispH;
  const px=Math.max(0,b.x-b.w*pad), py=Math.max(0,b.y-b.h*pad);
  const pw=Math.min(imgDispW-px,b.w*(1+pad*2)), ph=Math.min(imgDispH-py,b.h*(1+pad*2));
  const sx=Math.max(0,Math.round(px*scX)), sy=Math.max(0,Math.round(py*scY));
  const sw=Math.max(8,Math.min(imgNatW-sx,Math.round(pw*scX))), sh=Math.max(8,Math.min(imgNatH-sy,Math.round(ph*scY)));
  const cv=document.createElement("canvas"); cv.width=Math.min(1024,sw); cv.height=Math.round(sh*(cv.width/sw));
  cv.getContext("2d").drawImage(img,sx,sy,sw,sh,0,0,cv.width,cv.height);
  return cv.toDataURL("image/jpeg",.86);
}
function addQtyBadgeForAnnotation(anno,qty){
  qty=Math.max(1,Math.round(+qty||1));
  anno.qty=qty; anno.isArrume=qty>1;
  const old=annotations.find(x=>x.isQty && x.parentId===anno.id);
  if(old){ old.clase=`QTY-${qty}`; return; }
  const b=annotationBounds(anno); if(!b) return;
  annotations.push({id:Date.now()+Math.floor(Math.random()*999),clase:`QTY-${qty}`,type:"bbox",bbox:{x:b.x+4,y:b.y+4,w:Math.min(64,b.w*.28),h:Math.min(32,b.h*.22)},color:"#22c55e",checked:true,isQty:true,parentId:anno.id});
}

// ── Análisis local de imagen (sin API key) ────────────────────────────────────
// Cuenta regiones oscuras (perforaciones) en los bordes y estima dimensiones
function localImageAnalysis(){
  const img=document.getElementById("bbox-img");
  if(!img||!img.naturalWidth) return null;
  const maxDim=500;
  const sc=Math.min(1, maxDim/Math.max(img.naturalWidth, img.naturalHeight));
  const w=Math.round(img.naturalWidth*sc), h=Math.round(img.naturalHeight*sc);
  const cv=document.createElement("canvas"); cv.width=w; cv.height=h;
  const ctx=cv.getContext("2d"); ctx.drawImage(img,0,0,w,h);
  const data=ctx.getImageData(0,0,w,h).data;
  // Detectar bordes: buscar regiones oscuras (perforaciones) en franjas perimetrales
  const edgeW=Math.round(Math.min(w,h)*0.08); // franja perimetral ~8%
  // Contar agujeros oscuros en franjas horizontales (top+bottom = frontales) y verticales (left+right = laterales)
  const frontales=countDarkSpotsInBand(data,w,h,0,edgeW,0,w,"h")+countDarkSpotsInBand(data,w,h,h-edgeW,h,0,w,"h");
  const laterales=countDarkSpotsInBand(data,w,h,0,h,0,edgeW,"v")+countDarkSpotsInBand(data,w,h,0,h,w-edgeW,w,"v");
  const ancho_mm=Math.round(frontales*50);
  const largo_mm=Math.round(laterales*50);
  const fam=familyFor(ancho_mm);
  let ref=null;
  if(fam!=="?" && largo_mm>0) ref=nearestCatalogMatch(fam,largo_mm,ancho_mm)?.code;
  // Detectar si es esquinero (doblez diagonal)
  const esq=detectCornerFold(data,w,h);
  if(esq && !ref){ ref=nearestCatalogMatch(esq,largo_mm||2400,150)?.code; }
  return {frontales, laterales, ancho_mm, largo_mm, familia:fam, referencia:ref, esquinero:esq};
}

function countDarkSpotsInBand(data,w,h,y0,y1,x0,x1,dir){
  // Cuenta grupos de pixeles oscuros en una banda
  const visited=new Uint8Array(w*h);
  let count=0;
  for(let y=y0;y<y1;y+=2){
    for(let x=x0;x<x1;x+=2){
      const idx=(y*w+x)*4;
      const lum=0.299*data[idx]+0.587*data[idx+1]+0.114*data[idx+2];
      if(lum<80 && !visited[y*w+x]){
        // BFS para agrupar
        const stack=[[x,y]]; let size=0;
        while(stack.length && size<200){
          const [cx,cy]=stack.pop();
          if(cx<0||cx>=w||cy<0||cy>=h) continue;
          const pi=cy*w+cx;
          if(visited[pi]) continue;
          const di=pi*4;
          const l=0.299*data[di]+0.587*data[di+1]+0.114*data[di+2];
          if(l>80) continue;
          visited[pi]=1; size++;
          stack.push([cx+1,cy],[cx-1,cy],[cx,cy+1],[cx,cy-1]);
        }
        if(size>8 && size<500) count++;
      }
    }
  }
  return count;
}

function detectCornerFold(data,w,h){
  // Busca una linea diagonal oscura que cruce la imagen (doblez del esquinero)
  let darkCount=0;
  for(let i=0;i<Math.min(w,h);i+=3){
    const x=i, y=i;
    if(x<w && y<h){
      const idx=(y*w+x)*4;
      const lum=0.299*data[idx]+0.587*data[idx+1]+0.114*data[idx+2];
      if(lum<100) darkCount++;
    }
  }
  if(darkCount > Math.min(w,h)*0.15) return "EI";
  // Anti-diagonal
  darkCount=0;
  for(let i=0;i<Math.min(w,h);i+=3){
    const x=w-1-i, y=i;
    if(x>=0 && y<h){
      const idx=(y*w+x)*4;
      const lum=0.299*data[idx]+0.587*data[idx+1]+0.114*data[idx+2];
      if(lum<100) darkCount++;
    }
  }
  if(darkCount > Math.min(w,h)*0.15) return "EE";
  return null;
}

// ── Clasificar anotación individual (local + IA opcional) ─────────────────────
async function classifyAnnotationLocal(annoId){
  const anno=annotations.find(a=>a.id===annoId);
  if(!anno) return;
  const key=(document.getElementById("openai-key")?.value||"").trim();
  // Análisis local primero: siempre funciona
  try{
    const local=localImageAnalysis();
    if(local && local.referencia){
      anno.clase=local.referencia; anno.pendingAutoClass=false;
      addReciente(local.referencia); renderAnnoList(); redraw(); updateButtons();
      samStatus(`✅ Identificada localmente: ${local.referencia} (${local.frontales}F × ${local.laterales}L)`);
      if(_lastMemoryEntry){ _lastMemoryEntry.aiObs=local; _lastMemoryEntry.classes=[...new Set([...(_lastMemoryEntry.classes||[]), local.referencia])]; saveMemory(); }
      showQtyPrompt(annoId);
      return;
    }
  }catch(_){}
  // Si hay API key, usar IA como respaldo
  if(key){
    samStatus("🤖 Identificando pieza con IA…");
    try{
      const crop=annotationCropDataUrl(anno);
      const prompt=`Eres experto en formaletas metálicas UNISPAN. Identifica SOLO la pieza tocada/recortada. Catálogo:\n${catalogSummaryForPrompt()}\nReglas: perforaciones cada 50mm; frontales=ancho/50; laterales=largo/50; PM anchos 300-600; PB 80-270; EI/EE esquineros. Devuelve SOLO JSON: {"referencia":"PM-2400x600","familia":"PM|PB|EI|EE|ACCESORIO","tipo":"","frontales":0,"laterales":0,"ancho_mm":0,"largo_mm":0,"cantidad_estimada":1,"info":"","confianza":0.0}`;
      const res=await fetchWithTimeout("https://api.openai.com/v1/chat/completions",
        {method:"POST",headers:{"Content-Type":"application/json","Authorization":"Bearer "+key},
        body:JSON.stringify({model:"gpt-4o-mini",messages:[{role:"user",content:[{type:"text",text:prompt},{type:"image_url",image_url:{url:crop}}]}],max_tokens:360})}, 15000);
      const data=await res.json(); if(!res.ok) throw new Error(data.error?.message||`HTTP ${res.status}`);
      const parsed=parseAIJson(data.choices?.[0]?.message?.content||"");
      if(parsed){
        const ref=validateAIReference(parsed);
        anno.clase=ref; anno.pendingAutoClass=false;
        if((+parsed.cantidad_estimada||1)>1) addQtyBadgeForAnnotation(anno,+parsed.cantidad_estimada);
        addReciente(ref); renderAnnoList(); redraw(); updateButtons();
        samStatus(`✅ Identificada: ${ref}`);
        expertInit(); expertBot(`🎯 Pieza identificada: <b>${safeHtml(ref)}</b> · ${safeHtml(parsed.tipo||"")} · confianza ${Math.round((parsed.confianza||0)*100)}%`);
        if(_lastMemoryEntry){ _lastMemoryEntry.aiObs=parsed; _lastMemoryEntry.classes=[...new Set([...(_lastMemoryEntry.classes||[]), ref])]; saveMemory(); }
        return;
      }
    }catch(err){
      console.error("IA pieza:",err);
    }
  }
  // Sin identificación: dejar como POR-IDENTIFICAR
  anno.clase="POR-IDENTIFICAR"; anno.pendingAutoClass=false;
  renderAnnoList(); redraw(); updateButtons();
  samStatus("✅ Pieza marcada. Toca la etiqueta para asignar clase manualmente.");
  showQtyPrompt(annoId);
}

// ── Prueba física: análisis local + IA opcional ───────────────────────────────
function normalizedBoxToDisplay(b){
  if(!b) return {x:imgDispW*.08,y:imgDispH*.08,w:imgDispW*.84,h:imgDispH*.84};
  let x=+b.x||0, y=+b.y||0, w=+b.w||0, h=+b.h||0;
  if(b.cx!=null || b.cy!=null){ x=(+b.cx||.5)-w/2; y=(+b.cy||.5)-h/2; }
  if(x>1||y>1||w>1||h>1){ x/=imgNatW; y/=imgNatH; w/=imgNatW; h/=imgNatH; }
  x=Math.max(0,Math.min(.98,x)); y=Math.max(0,Math.min(.98,y)); w=Math.max(.04,Math.min(1-x,w||.84)); h=Math.max(.04,Math.min(1-y,h||.84));
  return {x:x*imgDispW,y:y*imgDispH,w:w*imgDispW,h:h*imgDispH};
}
function applyPhysicalDetections(proof){
  if(!proof || !selectedFile) return;
  const items=[];
  (proof.piezas||[]).forEach(p=>items.push({...p,_kind:"pieza"}));
  (proof.arrumes||[]).forEach(p=>items.push({...p,_kind:"arrume",cantidad_estimada:p.cantidad_estimada||p.cantidad||p.qty}));
  if(!items.length) return;
  const existingAuto=annotations.filter(a=>a.fromPhysicalAuto).length;
  if(existingAuto) return;
  items.slice(0,12).forEach((it,idx)=>{
    const ref=validateAIReference(it);
    const box=normalizedBoxToDisplay(it.bbox||it.box||it.rect);
    const id=Date.now()+idx;
    const color=COLORS[annotations.length%COLORS.length];
    const qty=+(it.cantidad_estimada||it.cantidad||1)||1;
    const anno={id,clase:ref,type:"bbox",bbox:box,color,checked:true,qty:null,fromPhysicalAuto:true,physicalInfo:it.info||it.observacion||""};
    annotations.push(anno);
    if(qty>1) addQtyBadgeForAnnotation(anno,qty);
    if(ref && ref!=="POR-IDENTIFICAR") addReciente(ref);
  });
  renderAnnoList(); redraw(); updateButtons();
}
async function runPhysicalProof(opts={}){
  if(!selectedFile){ setPhysicalStatus("⚠️ Toma/carga una foto primero."); return; }
  const key=(document.getElementById("openai-key")?.value||"").trim();
  // Análisis local primero (siempre funciona)
  setPhysicalStatus(opts.auto?"🧪 Auto-reconociendo pieza localmente…":"🧪 Ejecutando análisis local…");
  try{
    const local=localImageAnalysis();
    if(local){
      const proof={
        date:new Date().toISOString(),
        resumen:`Análisis local: ${local.frontales} perforaciones frontales, ${local.laterales} laterales`,
        conteo_total:1,
        piezas:[{
          referencia:local.referencia||"POR-IDENTIFICAR",
          familia:local.familia||"?",
          tipo:local.esquinero||(local.familia!=="?"?"panel":"?"),
          cantidad:1,
          bbox:{x:0.05,y:0.05,w:0.9,h:0.9},
          frontales:local.frontales, laterales:local.laterales,
          ancho_mm:local.ancho_mm, largo_mm:local.largo_mm,
          info:`Detectado localmente: ${local.frontales}F × ${local.laterales}L ⇒ ${local.ancho_mm}×${local.largo_mm}mm`,
          confianza:local.referencia?0.65:0.35
        }],
        arrumes:[],
        calidad_foto:_lastMemoryEntry?.blur>180?"nítida":_lastMemoryEntry?.blur>80?"media":"borrosa",
        acciones:"Revisar y confirmar detección"
      };
      physicalProofs.unshift(proof); if(physicalProofs.length>80) physicalProofs.length=80; savePhysicalProofs();
      applyPhysicalDetections(proof);
      if(_lastMemoryEntry){ _lastMemoryEntry.aiObs=proof; _lastMemoryEntry.classes=[...new Set([...(_lastMemoryEntry.classes||[]), validateAIReference(proof.piezas[0])].filter(Boolean))]; _lastMemoryEntry.qty=proof.conteo_total||null; saveMemory(); }
      const p=proof.piezas[0];
      const ref=validateAIReference(p);
      const html=`<b style="color:var(--ok)">🧪 Análisis local completado</b><br>
        ${safeHtml(proof.resumen)}<br>
        <b>Referencia:</b> ${ref!=="POR-IDENTIFICAR"?`<span style="color:var(--amber);font-family:monospace">${ref}</span>`:"<span style='color:var(--steel)'>sin match claro</span>"}<br>
        <b>Perforaciones:</b> ${p.frontales} frontales · ${p.laterales} laterales<br>
        <b>Medidas:</b> ${p.ancho_mm} × ${p.largo_mm} mm<br>
        <b>Familia:</b> ${p.familia}<br>
        <b>Foto:</b> ${proof.calidad_foto} · confianza ${Math.round((p.confianza||0)*100)}%<br>
        <span style="color:var(--steel)">Se marcó automáticamente. Revisa antes de subir.</span>`;
      setPhysicalStatus(html);
      expertInit(); expertBot(`🧪 Resultado análisis local:<br>${html}`);
      showToast("🧪 Análisis local completado","ok");
      return;
    }
    // Si análisis local falla y hay key, usar IA
    if(!key){
      setPhysicalStatus("🧪 Análisis local listo. Agrega API key OpenAI (opcional) para análisis visual más preciso.");
      return;
    }
    // IA con timeout
    setPhysicalStatus("🧪 Analizando con IA…");
    const b64=await fileToB64(selectedFile);
    const prompt=`Eres un inspector experto de formaletas metálicas UNISPAN. Reconoce referencias y cuenta piezas/arrumes. Catálogo:\n${catalogSummaryForPrompt()}\nReglas: perforaciones frontales=ancho/50, laterales=largo/50, inicio 25mm, paso 50mm. PM ancho 300-600; PB 80-270; EI/EE esquineros 150x150.\nDevuelve SOLO JSON: {"resumen":"","conteo_total":0,"piezas":[{"referencia":"PM-2400x600","familia":"PM","tipo":"panel","cantidad":1,"bbox":{"x":0.1,"y":0.1,"w":0.8,"h":0.5},"frontales":0,"laterales":0,"ancho_mm":0,"largo_mm":0,"info":"","confianza":0.0}],"arrumes":[],"calidad_foto":"","acciones":""}`;
    const res=await fetchWithTimeout("https://api.openai.com/v1/chat/completions",
      {method:"POST",headers:{"Content-Type":"application/json","Authorization":"Bearer "+key},
      body:JSON.stringify({model:"gpt-4o-mini",messages:[{role:"user",content:[{type:"text",text:prompt},{type:"image_url",image_url:{url:b64}}]}],max_tokens:700})}, 20000);
    const data=await res.json(); if(!res.ok) throw new Error(data.error?.message||`HTTP ${res.status}`);
    const proof=parseAIJson(data.choices?.[0]?.message?.content||"");
    if(!proof) throw new Error("respuesta IA sin JSON");
    proof.date=new Date().toISOString();
    physicalProofs.unshift(proof); if(physicalProofs.length>80) physicalProofs.length=80; savePhysicalProofs();
    applyPhysicalDetections(proof);
    if(_lastMemoryEntry){ _lastMemoryEntry.aiObs=proof; _lastMemoryEntry.classes=[...new Set([...(proof.piezas||[]).map(validateAIReference),(proof.arrumes||[]).map(validateAIReference)].filter(Boolean))]; _lastMemoryEntry.qty=proof.conteo_total||null; saveMemory(); }
    const piezaLines=(proof.piezas||[]).slice(0,5).map(p=>`• <b>${safeHtml(validateAIReference(p))}</b>${p.cantidad?` ×${safeHtml(p.cantidad)}`:""} · ${safeHtml(p.info||p.tipo||"")} · ${Math.round((p.confianza||0)*100)}%`).join("<br>");
    const html=`<b style="color:var(--ok)">🧪 Prueba IA completada</b><br>${safeHtml(proof.resumen||"")}<br><b>Conteo:</b> ${safeHtml(proof.conteo_total||"?")}<br>${piezaLines?`<br><b>Piezas:</b><br>${piezaLines}`:""}<br><span style="color:var(--steel)">Se marcaron automáticamente.</span>`;
    setPhysicalStatus(html);
    expertInit(); expertBot(`🧪 Resultado de prueba IA:<br>${html}`);
    showToast("🧪 Análisis IA completado","ok");
  }catch(err){
    console.error("Prueba física:",err);
    setPhysicalStatus(`❌ Error: ${safeHtml((err.message||err).toString().slice(0,140))}`);
  }
}

// ── Analizar imagen actual (local + IA opcional) ──────────────────────────────
async function analyzeCurrentWithAI(){
  const out=document.getElementById("ai-analysis-out");
  out.style.display="block";
  if(!selectedFile){ out.textContent="⚠️ Carga una imagen primero (Cámara o Galería)."; return; }
  const key=(document.getElementById("openai-key")?.value||"").trim();
  // Análisis local primero
  const local=localImageAnalysis();
  const e=_lastMemoryEntry;
  if(local){
    const refHtml=local.referencia
      ? `<span style="color:var(--ok);font-family:monospace">${local.referencia}</span> ✅`
      : `<span style="color:var(--amber)">sin match claro en catálogo</span>`;
    const html=`<b style="color:var(--amber)">🔍 Análisis local:</b><br>
      • <b>Referencia:</b> ${refHtml}<br>
      • <b>Familia:</b> ${local.familia||"?"} ${local.esquinero?"(esquinero "+local.esquinero+")":""}<br>
      • <b>Perforaciones:</b> ${local.frontales} frontales · ${local.laterales} laterales<br>
      • <b>Medidas estimadas:</b> ${local.ancho_mm} × ${local.largo_mm} mm<br>
      • <b>Dimensiones:</b> ${e?.w||"?"}×${e?.h||"?"} px · aspecto ${e?.aspect||"?"} (${e?.orientation||"?"})<br>
      • <b>Nitidez:</b> ${e?.blur??"?"} ${e&&e.blur>180?"✅ nítida":e&&e.blur>80?"⚠️ media":"❌ borrosa"}<br>
      ${!key?'<span style="color:var(--steel)">Agrega API key OpenAI para análisis visual profundo con gpt-4o-mini.</span>':''}`;
    out.innerHTML=html;
    if(_lastMemoryEntry){ _lastMemoryEntry.aiObs=local; saveMemory(); }
    if(!key) return; // sin key, terminamos con análisis local
  } else if(!key){
    if(!e){ out.textContent="⚠️ Sin datos aún."; return; }
    out.innerHTML=`<b>Observación local (sin IA):</b><br>
      • Dimensiones: ${e.w}×${e.h} px · aspecto ${e.aspect} (${e.orientation})<br>
      • Nitidez: ${e.blur??"?"} ${e.blur>180?"✅ nítida":e.blur>80?"⚠️ media":"❌ borrosa"}<br>
      • Clases anotadas: ${e.classes.length?e.classes.join(", "):"(ninguna)"}<br>
      <span style="color:var(--steel)">Agrega API key OpenAI para análisis visual profundo.</span>`;
    return;
  }
  // IA con timeout
  localStorage.setItem("openai_key",key);
  out.innerHTML="⏳ Analizando con gpt-4o-mini…";
  try{
    const b64=await fileToB64(selectedFile);
    const prompt=`Eres un experto en formaletas metálicas UNISPAN (acero 3mm). Catálogo REAL:\n${catalogSummaryForPrompt()}\nReglas: inicio 25mm, paso 50mm. N=medida/50. Bridas cortas→ancho, largas→largo. PM 300-600, PB 80-270, EI/EE esquineros.\nAnaliza y devuelve SOLO JSON: {"tipo":"","familia":"PM|PB|EI|EE|ACCESORIO","estructura":"","frontales":0,"laterales":0,"ancho_mm":0,"largo_mm":0,"cantidad_estimada":1,"anomalias":"","calidad_foto":"","confianza":0.0}`;
    const res=await fetchWithTimeout("https://api.openai.com/v1/chat/completions",
      {method:"POST",headers:{"Content-Type":"application/json","Authorization":"Bearer "+key},
      body:JSON.stringify({model:"gpt-4o-mini",messages:[{role:"user",content:[{type:"text",text:prompt},{type:"image_url",image_url:{url:b64}}]}],max_tokens:400})}, 20000);
    const data=await res.json();
    if(!res.ok) throw new Error(data.error?.message||`HTTP ${res.status}`);
    const raw=data.choices?.[0]?.message?.content||"";
    let parsed=null;
    try{ const m=raw.match(/\{[\s\S]*\}/); if(m) parsed=JSON.parse(m[0]); }catch(_){}
    if(parsed){
      const fam=(parsed.familia||"").toUpperCase().trim();
      const match=["PM","PB","EI","EE"].includes(fam)?nearestCatalogMatch(fam,parsed.largo_mm,parsed.ancho_mm):null;
      parsed.referencia_validada=match?match.code:null;
      parsed.distancia_catalogo_mm=match?match.distancia_mm:null;
    }
    if(_lastMemoryEntry){ _lastMemoryEntry.aiObs=parsed||raw; saveMemory(); }
    if(parsed){
      const refHtml=parsed.referencia_validada
        ?(parsed.distancia_catalogo_mm<=25
          ?`<span style="color:var(--ok);font-family:monospace">${parsed.referencia_validada}</span> ✅`
          :`<span style="color:var(--amber);font-family:monospace">${parsed.referencia_validada}</span> ⚠️`)
        :`<span style="color:var(--danger)">sin match</span>`;
      const html=`<b style="color:var(--amber)">🤖 Análisis IA:</b><br>
        • <b>Tipo:</b> ${parsed.tipo||"?"} (familia ${parsed.familia||"?"})<br>
        • <b>Referencia:</b> ${refHtml}<br>
        • <b>Estructura:</b> ${parsed.estructura||"?"}<br>
        • <b>Perforaciones:</b> ${parsed.frontales||"?"} frontales · ${parsed.laterales||"?"} laterales<br>
        • <b>Medidas:</b> ${parsed.ancho_mm||"?"} × ${parsed.largo_mm||"?"} mm<br>
        • <b>Cantidad:</b> ×${parsed.cantidad_estimada||1}<br>
        • <b>Anomalías:</b> ${parsed.anomalias||"ninguna"}<br>
        • <b>Foto:</b> ${parsed.calidad_foto||"?"} · confianza ${((parsed.confianza||0)*100).toFixed(0)}%<br>
        <span style="color:var(--steel);font-size:10px">Guardado en memoria.</span>`;
      out.innerHTML=html;
      if(document.getElementById("expert-chat")){ expertInit(); expertBot(`📸 Análisis IA: ${html}`); }
    } else {
      out.innerHTML=`<b>🤖 Análisis IA (texto):</b><br><pre style="white-space:pre-wrap;font-size:11px">${raw}</pre>`;
    }
  }catch(err){
    out.innerHTML=`❌ Error IA: ${err.message}`;
  }
}

function showMemorySummary(){
  const out=document.getElementById("ai-analysis-out");
  out.style.display="block";
  if(!imgMemory.length){ out.innerHTML="📭 Aún no hay imágenes en memoria."; return; }
  const byClass={};
  imgMemory.forEach(e=>e.classes.forEach(c=>{
    if(!byClass[c]) byClass[c]={n:0,aspects:[],blurs:[]};
    byClass[c].n++;
    byClass[c].aspects.push(e.aspect);
    if(e.blur) byClass[c].blurs.push(e.blur);
  }));
  const withAI=imgMemory.filter(e=>e.aiObs).length;
  let html=`<b>🧠 Memoria: ${imgMemory.length} imágenes · ${withAI} con análisis</b><br><br>`;
  const entries=Object.entries(byClass).sort((a,b)=>b[1].n-a[1].n).slice(0,12);
  if(!entries.length){ html+="<i style='color:var(--steel)'>Sin clases anotadas todavía.</i>"; }
  else{
    html+="<table style='width:100%;border-collapse:collapse;font-size:11px'><tr style='color:var(--amber)'><th style='text-align:left;padding:3px'>Clase</th><th style='padding:3px'>N</th><th style='padding:3px'>Aspecto</th><th style='padding:3px'>Nitidez</th></tr>";
    entries.forEach(([c,d])=>{
      const avgA=(d.aspects.reduce((s,x)=>s+x,0)/d.aspects.length).toFixed(2);
      const avgB=d.blurs.length?Math.round(d.blurs.reduce((s,x)=>s+x,0)/d.blurs.length):"?";
      html+=`<tr style='border-top:1px solid #223'><td style='padding:3px;font-family:monospace'>${c}</td><td style='padding:3px;text-align:center'>${d.n}</td><td style='padding:3px;text-align:center'>${avgA}</td><td style='padding:3px;text-align:center'>${avgB}</td></tr>`;
    });
    html+="</table>";
  }
  out.innerHTML=html;
}
function clearMemory(){
  if(!confirm("¿Borrar toda la memoria de imágenes analizadas? (No afecta al dataset en Roboflow)")) return;
  imgMemory=[]; physicalProofs=[]; saveMemory(); savePhysicalProofs();
  const out=document.getElementById("ai-analysis-out");
  out.style.display="block"; out.textContent="🗑️ Memoria y pruebas borradas.";
  setPhysicalStatus("",false);
}
</script>
</body>
</html>
