"""
Operación de la página de devoluciones:
  1. Calendario: solo lunes a viernes, sin festivos de Colombia y sin días llenos (capacidad máxima).
  2. Alertas de confirmación al cliente (Costa: 3 días hábiles antes; otras zonas: 2 y 1 día antes),
     con respuesta "confirmo" o "no podré cumplir" + motivo, y alerta al comercial/asesores para que
     continúen el cobro de arrendamiento cuando se incumple.
  3. Asistente de ayuda para llenar la solicitud.

Los datos vienen de la base del sistema (tarea "Unispan - Sincronizar devoluciones" cada 15 min):
ocupación por día y devoluciones próximas. Se registra con registrar(app, ctx).
"""
import base64
import hashlib
import hmac
import html
import json
import os
import re
import threading
import time
import unicodedata
from collections import defaultdict, deque
from datetime import date, datetime, timedelta

import requests
from flask import jsonify, request

import festivos_co as fco

# ------------------------------------------------------------------ capacidad (igual que reglas.py del bot)
CAPACIDAD_TON = {0: 70.0, 1: 100.0, 2: 100.0, 3: 100.0, 4: 70.0, 5: 0.0, 6: 0.0}
MAX_VEHICULOS_DIA = int(os.environ.get("MAX_VEHICULOS_DIA", "8"))
COSTA = ("BARRANQUILLA", "CARTAGENA", "SANTA MARTA", "SOLEDAD", "MALAMBO", "PUERTO COLOMBIA", "GALAPA",
         "MONTERIA", "SINCELEJO", "VALLEDUPAR", "RIOHACHA", "TURBACO", "SABANALARGA", "CIENAGA", "MAICAO",
         "COVENAS", "TOLU", "ARJONA", "MAGANGUE", "BARANOA", "ATLANTICO", "BOLIVAR", "MAGDALENA", "CORDOBA",
         "SUCRE", "CESAR", "GUAJIRA", "SAN ANDRES")
MOTIVOS = [
    "Inconvenientes logísticos: consecución del vehículo",
    "Inconvenientes logísticos: fallas del vehículo",
    "El equipo continúa en uso en la obra",
    "No se cuenta con personal para cargar el vehículo",
    "El equipo no está listo / falta desarmar o agrupar",
    "Clima o restricción de acceso a la obra",
    "Otro motivo",
]
ETAPAS = {"costa": [3], "otras": [2, 1]}
# Obras de PRUEBA (para aprobar el proyecto): todo lo de estas obras —correo al cliente, alertas al comercial—
# le llega SOLO al coordinador (carpeta AVISOS AUTOMATIZACION), a cualquier hora y sin el aviso [PRUEBA].
OBRAS_PRUEBA = [x.strip() for x in os.environ.get("OBRAS_PRUEBA", "PRUEBA AUTOMATIZACION").split(";") if x.strip()]


def es_prueba(o_o_nombre) -> bool:
    nombre = o_o_nombre.get("obra") if isinstance(o_o_nombre, dict) else o_o_nombre
    n = re.sub(r"[^A-Z0-9 ]", " ", _norm(nombre))
    return any(re.sub(r"[^A-Z0-9 ]", " ", _norm(p)) in n for p in OBRAS_PRUEBA)

ctx: dict = {}
_lock = threading.Lock()


def _norm(t) -> str:
    t = unicodedata.normalize("NFKD", str(t or ""))
    return re.sub(r"\s+", " ", "".join(c for c in t if not unicodedata.combining(c))).upper().strip()


def _hoy() -> date:  # Colombia (UTC-5), aunque el servidor esté en UTC
    return (datetime.utcnow() - timedelta(hours=5)).date()


def _ahora_col() -> datetime:
    return datetime.utcnow() - timedelta(hours=5)


def _ruta(nombre):
    return os.path.join(ctx["DATA_DIR"], nombre)


def _leer(nombre, defecto):
    try:
        with open(_ruta(nombre), encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return defecto


def _escribir(nombre, datos):
    os.makedirs(ctx["DATA_DIR"], exist_ok=True)
    ruta = _ruta(nombre)
    tmp = ruta + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    os.replace(tmp, ruta)
    ctx["guardado"](ruta)


def es_costa(ciudad: str) -> bool:
    c = _norm(ciudad)
    return any(x in c for x in COSTA)


# ------------------------------------------------------------------ 1. calendario
def guardar_ocupacion(lista):
    ocup = {}
    for x in lista if isinstance(lista, list) else []:
        if isinstance(x, dict) and x.get("dia"):
            ocup[str(x["dia"])[:10]] = {"vehiculos": int(x.get("vehiculos") or 0),
                                        "toneladas": float(x.get("toneladas") or 0)}
    _escribir("ocupacion.json", {"hora": _ahora_col().strftime("%Y-%m-%d %H:%M"), "dias": ocup})


def dia_lleno(d: date) -> bool:
    o = (_leer("ocupacion.json", {}).get("dias") or {}).get(d.isoformat())
    if not o:
        return False
    return o["vehiculos"] >= MAX_VEHICULOS_DIA or o["toneladas"] >= CAPACIDAD_TON.get(d.weekday(), 0)


def motivo_fecha(d: date) -> str:
    """'' si se puede programar ese día; si no, por qué."""
    if d.weekday() >= 5:
        return "solo se programa de lunes a viernes"
    f = fco.es_festivo(d)
    if f:
        return f"es festivo ({f})"
    if dia_lleno(d):
        return "ese día ya está con la capacidad máxima de devoluciones"
    return ""


def calendario(dias=120) -> dict:
    hoy = _hoy()
    llenos, disponibles = [], []
    for i in range(1, dias + 1):
        d = hoy + timedelta(days=i)
        if d.weekday() < 5 and not fco.es_festivo(d):
            (llenos if dia_lleno(d) else disponibles).append(d.isoformat())
    return {"hoy": hoy.isoformat(), "festivos": fco.lista(hoy, dias), "llenos": llenos,
            "disponibles": disponibles[:40]}


# ------------------------------------------------------------------ 2. alertas de confirmación
def _firma(texto: str) -> str:
    return hmac.new(ctx["secreto"].encode(), texto.encode(), hashlib.sha256).hexdigest()[:24]


def _token(orden_id, etapa) -> str:
    carga = base64.urlsafe_b64encode(json.dumps({"i": orden_id, "e": etapa,
                                                 "x": int(time.time()) + 15 * 86400}).encode()).decode()
    return carga + "." + _firma(carga)


def _leer_token(t):
    carga, _, firma = str(t).partition(".")
    if not carga or not hmac.compare_digest(_firma(carga), firma):
        return None
    try:
        d = json.loads(base64.urlsafe_b64decode(carga.encode()).decode())
    except Exception:  # noqa: BLE001
        return None
    return d if d.get("x", 0) > time.time() else None


def _correos_cliente(o: dict) -> list:
    if es_prueba(o):
        return [ctx["correo_prueba"]]
    propios = re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", o.get("email") or "")
    try:
        propios += ctx["correos_de_obra"](o.get("nit"), o.get("obra"))
    except Exception:  # noqa: BLE001
        pass
    return [c for c in dict.fromkeys(x.lower() for x in propios) if not ctx["es_interno"](c)]


def comercial_y_asesores(comercial: str, ciudad: str) -> list:
    """Correo del asesor comercial de la obra (nombre corto del sistema, p. ej. 'CRISTIAN C.')."""
    c = buscar_asesor(comercial)
    return [c["correo"]] if c else []


def buscar_asesor(corto: str):
    """'CRISTIAN C.' / 'JUAN C. R.' / 'MIGUEL  S.' → el ÚNICO asesor de los contactos cuyo primer nombre
    coincide y cuyas iniciales siguientes aparecen en sus apellidos/nombres."""
    partes = [p for p in re.split(r"[\s.]+", _norm(corto)) if p]
    if not partes:
        return None
    primero, iniciales = partes[0], [p[0] for p in partes[1:]]
    cands = []
    contactos = ctx["contactos"]()
    for c in contactos.get("asesores", []) + contactos.get("administradores", []):
        pal = [p for p in re.split(r"[\s.]+", _norm(c.get("nombre"))) if p]
        if not pal or pal[0] != primero:
            continue
        resto = [p[0] for p in pal[1:]]
        if all(i in resto for i in iniciales):
            cands.append(c)
    unicos = {c.get("correo"): c for c in cands if c.get("correo")}
    return list(unicos.values())[0] if len(unicos) == 1 else None


def _detalle_orden(o: dict) -> list:
    return [("Obra", o.get("obra")), ("Cliente", o.get("cliente")), ("Ciudad", o.get("ciudad")),
            ("Fecha de devolución", f"{o.get('fecha')} {o.get('hora') or ''}"), ("Vehículo", o.get("vehiculo")),
            ("Peso (ton)", o.get("peso")), ("Comercial", o.get("comercial"))]


# ------------------------------------------------------------------ diseño institucional (azul y blanco)
AZUL, AZUL_CLARO, LINEA = "#0033A0", "#EEF3FB", "#C9D6EE"


def _cuadro(filas) -> str:
    """Cuadro organizado: etiqueta en azul claro, valor en blanco (funciona en Outlook y Gmail)."""
    celdas = "".join(
        f"<tr><td style='padding:9px 14px;background:{AZUL_CLARO};color:{AZUL};font-weight:600;width:42%;"
        f"border-bottom:1px solid {LINEA};font-size:14px'>{html.escape(str(k))}</td>"
        f"<td style='padding:9px 14px;background:#ffffff;color:#14213d;font-weight:700;border-bottom:1px solid {LINEA};"
        f"font-size:14px'>{html.escape(str(v if v not in (None, '') else '—'))}</td></tr>" for k, v in filas)
    return (f"<table role='presentation' cellspacing='0' cellpadding='0' style='width:100%;border-collapse:collapse;"
            f"border:1px solid {LINEA};border-radius:8px;overflow:hidden;margin:12px 0'>{celdas}</table>")


def _boton(url, texto, relleno=True):
    estilo = (f"background:{AZUL};color:#ffffff;border:2px solid {AZUL}" if relleno
              else f"background:#ffffff;color:{AZUL};border:2px solid {AZUL}")
    return (f"<a href='{html.escape(url)}' style='display:inline-block;margin:6px 8px 6px 0;padding:12px 22px;{estilo};"
            f"border-radius:8px;text-decoration:none;font-weight:700;font-size:15px;font-family:Segoe UI,Arial'>{texto}</a>")


def _marco(titulo: str, contenido: str, pie: str = "") -> str:
    """Encabezado azul con la marca UNISPAN, cuerpo blanco y pie gris (correo y páginas)."""
    return (f"<table role='presentation' cellspacing='0' cellpadding='0' style='width:100%;max-width:620px;margin:0 auto;"
            f"border:1px solid {LINEA};border-radius:10px;overflow:hidden;font-family:Segoe UI,Arial,sans-serif;"
            f"background:#ffffff'><tr><td style='background:{AZUL};padding:16px 22px;color:#ffffff'>"
            f"<div style='font-size:20px;font-weight:800;letter-spacing:3px'>UNISPAN</div>"
            f"<div style='font-size:13px;opacity:.9;margin-top:2px'>{html.escape(titulo)}</div></td></tr>"
            f"<tr><td style='padding:20px 22px;color:#14213d;font-size:15px;line-height:1.5'>{contenido}</td></tr>"
            f"<tr><td style='background:{AZUL_CLARO};padding:10px 22px;color:#51607a;font-size:12px'>"
            f"{pie or 'UNISPAN Colombia · Logística de devoluciones · coordinadorplanta@unispan.com.co'}</td></tr></table>")


# ------------------------------------------------------------------ trazabilidad (historial de 1 año)
TIPOS_EVENTO = {"alerta": "Confirmación pedida al cliente", "confirma": "Cliente confirmó",
                "incumple": "Cliente NO cumple", "vencida": "Fecha vencida sin confirmar",
                "reprogramada": "Reprogramada en el sistema", "cancelada": "Cancelada / eliminada en el sistema"}


def registrar_evento(tipo: str, o: dict, detalle: str = ""):
    with _lock_hist:
        h = _leer("historial_devoluciones.json", [])
        h.append({"hora": _ahora_col().strftime("%Y-%m-%d %H:%M"), "tipo": tipo, "orden": str(o.get("id", "")),
                  "obra": o.get("obra", ""), "cliente": o.get("cliente", ""), "ciudad": o.get("ciudad", ""),
                  "comercial": o.get("comercial", ""), "fecha": o.get("fecha", ""), "detalle": detalle[:400]})
        limite = (_hoy() - timedelta(days=366)).isoformat()
        _escribir("historial_devoluciones.json", [x for x in h if x["hora"][:10] >= limite])


_lock_hist = threading.Lock()


def _comparar_con_anterior(lista: list):
    """Órdenes que estaban programadas y cambiaron de fecha (reprogramadas) o desaparecieron (canceladas)."""
    hoy = _hoy().isoformat()
    previas = {str(o.get("id")): o for o in _leer("proximas.json", []) if isinstance(o, dict)}
    if not previas:
        return
    nuevas = {str(o.get("id")): o for o in lista if isinstance(o, dict)}
    for oid, p in previas.items():
        n = nuevas.get(oid)
        if n is None:
            if str(p.get("fecha", ""))[:10] >= hoy:  # desapareció antes de su fecha: se canceló o eliminó
                registrar_evento("cancelada", p, "La orden ya no aparece en la programación del sistema.")
        elif str(n.get("fecha")) != str(p.get("fecha")):
            registrar_evento("reprogramada", n, f"De {p.get('fecha')} {p.get('hora') or ''} a {n.get('fecha')} {n.get('hora') or ''}")


def procesar_proximas(lista, base_url: str) -> int:
    """Llamado en cada sincronización (cada 15 min). Envía las alertas que correspondan, una sola vez."""
    if not isinstance(lista, list):
        return 0
    try:
        _comparar_con_anterior(lista)
    except Exception as exc:  # noqa: BLE001
        print(f"AVISO trazabilidad: {exc}", flush=True)
    _escribir("proximas.json", lista)
    ahora = _ahora_col()
    # correos a clientes solo en horario laboral (las obras de PRUEBA se procesan a cualquier hora)
    fuera_de_horario = not (7 <= ahora.hour < 18) or not fco.es_habil(ahora.date())
    if fuera_de_horario and not any(es_prueba(o) for o in lista if isinstance(o, dict)):
        return 0
    hoy = ahora.date()
    enviados = 0
    with _lock:
        estado = _leer("alertas.json", {})
        for o in lista:
            if not isinstance(o, dict) or not o.get("id") or not o.get("fecha"):
                continue
            try:
                fecha = date.fromisoformat(str(o["fecha"])[:10])
            except ValueError:
                continue
            if fuera_de_horario and not es_prueba(o):
                continue
            oid = str(o["id"])
            e = estado.setdefault(oid, {"etapas": [], "obra": o.get("obra"), "fecha": o["fecha"]})
            if e.get("fecha") != o["fecha"]:  # se reprogramó: vuelven a correr las alertas
                e.update({"etapas": [], "fecha": o["fecha"], "respuesta": None, "vencida": False})
            faltan = fco.habiles_entre(hoy, fecha)
            zona = "costa" if es_costa(o.get("ciudad")) else "otras"
            respuesta = e.get("respuesta") or {}
            # a) confirmación previa al cliente
            for etapa in ETAPAS[zona]:
                if faltan == etapa and etapa not in e["etapas"] and respuesta.get("tipo") != "confirma" and fecha > hoy:
                    destinos = _correos_cliente(o)
                    url_si = f"{base_url}/confirmar/{_token(oid, etapa)}?r=si"
                    url_no = f"{base_url}/confirmar/{_token(oid, etapa)}?r=no"
                    cuerpo = _marco("Confirmación de devolución de equipo", (
                        f"<p style='margin:0 0 6px'>Buen día,</p><p style='margin:0'>Les recordamos la <b>devolución "
                        f"de equipo programada para el {fecha.strftime('%d/%m/%Y')}</b> (faltan {faltan} día(s) "
                        "hábil(es)).</p>" + _cuadro(_detalle_orden(o))
                        + "<p style='margin:14px 0 4px'><b>Por favor confirmen si la devolución se realizará en la "
                          "fecha pactada:</b></p>"
                        + _boton(url_si, "✔ Confirmo la devolución", True)
                        + _boton(url_no, "✖ No podremos cumplir", False)
                        + "<p style='color:#51607a;font-size:12px;margin:12px 0 0'>Si no se cumple la fecha pactada, "
                          "el equipo continúa generando arrendamiento.</p>"))
                    asunto_c = f"Confirmación de devolución — {o.get('obra')} — {fecha.strftime('%d/%m/%Y')}"
                    if es_prueba(o):
                        ctx["enviar_prueba"](asunto_c, cuerpo)
                    elif destinos:
                        ctx["enviar"](destinos, asunto_c, cuerpo)
                    else:
                        ctx["notificar"](f"[Devolución sin correo de cliente] {o.get('obra')} {o['fecha']}",
                                         "<p>No hay correo del cliente para pedir la confirmación de esta devolución.</p>"
                                         + ctx["tabla"](_detalle_orden(o)))
                    e["etapas"].append(etapa)
                    registrar_evento("alerta", o, f"{etapa} día(s) hábil(es) antes · a: {', '.join(destinos) or 'SIN CORREO'}")
                    enviados += 1
            # b) fecha pactada vencida sin confirmación → alerta al comercial y asesores
            # (solo si se le pidió confirmación: en la primera sincronización no se alertan devoluciones viejas)
            if fecha < hoy and not e.get("vencida") and e["etapas"] and respuesta.get("tipo") != "confirma":
                _alerta_incumplimiento(o, respuesta.get("motivo") or "El cliente no confirmó la devolución "
                                                                        "y la fecha pactada ya pasó.",
                                       respuesta.get("comentario", ""))
                e["vencida"] = True
                registrar_evento("vencida", o, "Alerta a comercial y coordinador: continuar cobro de arrendamiento.")
                enviados += 1
        # limpieza: órdenes viejas
        limite = (hoy - timedelta(days=30)).isoformat()
        estado = {k: v for k, v in estado.items() if str(v.get("fecha", "9999"))[:10] >= limite}
        _escribir("alertas.json", estado)
    return enviados


def _alerta_incumplimiento(o: dict, motivo: str, comentario: str = "", nueva_fecha: str = ""):
    destinos = comercial_y_asesores(o.get("comercial"), o.get("ciudad"))
    cuerpo = _marco("Incumplimiento de devolución", (
        f"<p style='margin:0;padding:10px 12px;border-left:4px solid {AZUL};background:{AZUL_CLARO}'><b>El cliente no "
        "cumple la fecha de devolución pactada.</b> Continuar con el cobro de arrendamiento del equipo hasta que se "
        "realice la devolución.</p>"
        + _cuadro(_detalle_orden(o) + [("Motivo", motivo), ("Comentario del cliente", comentario),
                                        ("Nueva fecha propuesta", nueva_fecha)])))
    asunto = f"[Incumplimiento devolución] {o.get('obra')} — {o.get('fecha')} — continuar cobro de arrendamiento"
    if es_prueba(o):  # obra de prueba: solo al coordinador, mostrando a qué comercial le habría llegado
        ctx["enviar_prueba"](asunto, cuerpo + f"<p style='color:#666'>(En una obra real iría a: "
                                              f"{html.escape(', '.join(destinos) or 'comercial no encontrado')} y al coordinador.)</p>")
        return
    if destinos:
        ctx["enviar"](destinos, asunto, cuerpo)
    ctx["notificar"](asunto, cuerpo + ("" if destinos else "<p>⚠ No se encontró el correo del comercial "
                                                          f"«{html.escape(str(o.get('comercial') or ''))}» en los contactos.</p>"))


def _pagina(titulo, cuerpo):
    return (f"<!doctype html><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{html.escape(titulo)} — UNISPAN</title><body style='margin:0;padding:24px 12px;background:#F3F6FB'>"
            + _marco(titulo, cuerpo) + "</body>")


def _orden(oid):
    return next((o for o in _leer("proximas.json", []) if isinstance(o, dict) and str(o.get("id")) == str(oid)),
                None) or {"id": oid, **({k: v for k, v in (_leer("alertas.json", {}).get(str(oid)) or {}).items()
                                         if k in ("obra", "fecha")})}


def registrar(app, contexto: dict):
    ctx.update(contexto)
    consultas = defaultdict(deque)

    @app.get("/api/calendario")
    def api_calendario():
        return jsonify(ok=True, **calendario())

    @app.get("/confirmar/<token>")
    def confirmar_ver(token):
        t = _leer_token(token)
        if not t:
            return _pagina("Enlace no válido", "<p>El enlace venció o no es válido.</p>"), 410
        o = _orden(t["i"])
        r = (_leer("alertas.json", {}).get(str(t["i"])) or {}).get("respuesta")
        previo = (f"<p style='background:#eef6ff;padding:8px;border-radius:6px'>Ya respondieron: <b>"
                  f"{'Confirma' if r.get('tipo') == 'confirma' else 'No cumple'}</b> ({html.escape(r.get('hora', ''))}). "
                  "Pueden cambiar la respuesta.</p>") if r else ""
        opciones = "".join(f"<option>{html.escape(m)}</option>" for m in MOTIVOS)
        no = request.args.get("r") == "no"
        cal = calendario(60)
        campo = (f"width:100%;box-sizing:border-box;padding:9px 11px;border:1px solid {LINEA};border-radius:8px;"
                 "font:inherit;font-size:14px;background:#fff;color:#14213d")
        boton = "padding:12px 22px;border-radius:8px;font:inherit;font-weight:700;font-size:15px;cursor:pointer;"
        envio = ("<script>document.addEventListener('submit',function(e){var b=e.target.querySelectorAll('button');"
                 "for(var i=0;i<b.length;i++){b[i].disabled=true;}var s=e.submitter;if(s){s.textContent='Enviando…';"
                 "var h=document.createElement('input');h.type='hidden';h.name='r';h.value=s.value;e.target.appendChild(h);}});"
                 "</script>")
        return _pagina("Confirmación de devolución",
            previo + _cuadro(_detalle_orden(o))
            + "<form method='post' style='margin-top:6px'>"
            + ("" if no else f"<button name='r' value='si' style='{boton}background:{AZUL};color:#fff;"
                             f"border:2px solid {AZUL}'>✔ Confirmo la devolución</button>")
            + f"<div style='margin-top:16px;padding:14px;border:1px solid {LINEA};border-radius:10px;background:{AZUL_CLARO}'>"
            + f"<div style='color:{AZUL};font-weight:700;margin-bottom:8px'>¿No podrán cumplir? Indiquen el motivo</div>"
            + f"<select name='motivo' style='{campo}'>{opciones}</select>"
            + f"<textarea name='comentario' maxlength='500' placeholder='Comentario (opcional)' "
              f"style='{campo};margin-top:8px;min-height:70px'></textarea>"
            + f"<label style='display:block;margin-top:10px;font-size:13px;color:#51607a'>Nueva fecha propuesta "
              f"(opcional, lunes a viernes no festivo)<input type='date' name='nueva_fecha' "
              f"min='{cal['disponibles'][0] if cal['disponibles'] else ''}' style='{campo};margin-top:4px;max-width:220px'>"
              "</label>"
            + f"<button name='r' value='no' style='{boton}margin-top:12px;background:#fff;color:{AZUL};"
              f"border:2px solid {AZUL}'>✖ No podremos cumplir</button></div></form>" + envio)

    @app.post("/confirmar/<token>")
    def confirmar_guardar(token):
        t = _leer_token(token)
        if not t:
            return _pagina("Enlace no válido", "<p>El enlace venció o no es válido.</p>"), 410
        o = _orden(t["i"])
        si = request.form.get("r") == "si"
        motivo = str(request.form.get("motivo") or "")[:120]
        motivo = motivo if motivo in MOTIVOS else "Otro motivo"
        comentario = str(request.form.get("comentario") or "").strip()[:500]
        nueva = str(request.form.get("nueva_fecha") or "")[:10]
        aviso_fecha = ""
        if nueva:
            try:
                m = motivo_fecha(date.fromisoformat(nueva))
            except ValueError:
                m = "fecha no válida"
            if m:
                aviso_fecha, nueva = f"<p>La nueva fecha no se registró: {html.escape(m)}.</p>", ""
        with _lock:
            estado = _leer("alertas.json", {})
            e = estado.setdefault(str(t["i"]), {"etapas": [], "obra": o.get("obra"), "fecha": o.get("fecha")})
            e["respuesta"] = {"tipo": "confirma" if si else "incumple", "motivo": "" if si else motivo,
                              "comentario": comentario, "nueva_fecha": nueva,
                              "hora": _ahora_col().strftime("%Y-%m-%d %H:%M")}
            _escribir("alertas.json", estado)
        registrar_evento("confirma" if si else "incumple", o,
                         "" if si else f"{motivo}" + (f" · {comentario}" if comentario else "")
                         + (f" · nueva fecha propuesta {nueva}" if nueva else ""))
        if si:
            return _pagina("Devolución confirmada", f"<p style='font-size:17px;color:{AZUL};font-weight:700;margin:0 0 6px'>"
                                                    "✔ ¡Gracias!</p><p style='margin:0'>Quedó <b>confirmada</b> la "
                                                    "devolución. Los esperamos en la fecha pactada.</p>"
                                                    + _cuadro(_detalle_orden(o)))
        _alerta_incumplimiento(o, motivo, comentario, nueva)
        return _pagina("Respuesta registrada",
                       f"<p style='font-size:17px;color:{AZUL};font-weight:700;margin:0 0 6px'>Respuesta registrada</p>"
                       "<p>Registramos que <b>no podrán cumplir</b> la fecha pactada. El equipo de UNISPAN se "
                       "comunicará con ustedes para reprogramar.</p><p style='color:#666'>Mientras el equipo no se "
                       "devuelva, continúa generando arrendamiento.</p>" + aviso_fecha)

    @app.get("/seguimiento")
    def seguimiento():
        if not ctx["es_coordinador"]():
            return _pagina("Seguimiento", "<p>Solo el coordinador. Entra a la página con «Acceso coordinador» y "
                                          "vuelve a abrir este enlace.</p>"), 403
        tipo = request.args.get("tipo", "")
        h = list(reversed(_leer("historial_devoluciones.json", [])))
        if tipo:
            h = [x for x in h if x["tipo"] == tipo]
        if request.args.get("formato") == "csv":
            import csv as _csv
            import io
            buf = io.StringIO()
            w = _csv.writer(buf, delimiter=";")
            w.writerow(["Hora", "Evento", "Orden", "Obra", "Cliente", "Ciudad", "Comercial", "Fecha devolución", "Detalle"])
            for x in h:
                w.writerow([x["hora"], TIPOS_EVENTO.get(x["tipo"], x["tipo"]), x["orden"], x["obra"], x["cliente"],
                            x["ciudad"], x["comercial"], x["fecha"], x["detalle"]])
            return ("\ufeff" + buf.getvalue(), 200, {"Content-Type": "text/csv; charset=utf-8",
                    "Content-Disposition": "attachment; filename=seguimiento_devoluciones.csv"})
        conteo = {k: sum(1 for x in _leer("historial_devoluciones.json", []) if x["tipo"] == k) for k in TIPOS_EVENTO}
        colores = {"confirma": "#067647", "incumple": "#b42318", "vencida": "#b42318", "cancelada": "#9a3412",
                   "reprogramada": "#1f8fc2", "alerta": "#475467"}
        filtros = " ".join(
            f"<a href='?tipo={k}' style='margin:2px;padding:4px 9px;border-radius:999px;border:1px solid #cbd5e1;"
            f"text-decoration:none;color:{colores[k]};{'background:#e0f2fe;' if k == tipo else ''}'>{v} ({conteo[k]})</a>"
            for k, v in TIPOS_EVENTO.items())
        filas = "".join(
            f"<tr><td>{html.escape(x['hora'])}</td><td style='color:{colores.get(x['tipo'], '#000')};font-weight:600'>"
            f"{html.escape(TIPOS_EVENTO.get(x['tipo'], x['tipo']))}</td><td>{html.escape(x['obra'])}<br><small>"
            f"{html.escape(x['cliente'])} · {html.escape(x['ciudad'])}</small></td><td>{html.escape(x['fecha'])}</td>"
            f"<td>{html.escape(x['comercial'])}</td><td>{html.escape(x['detalle'])}</td></tr>" for x in h[:500])
        tabla = ("<table style='width:100%;border-collapse:collapse;font-size:13px'><tr style='background:#e0f2fe'>"
                 "<th align=left>Hora</th><th align=left>Evento</th><th align=left>Obra</th><th align=left>Fecha dev.</th>"
                 "<th align=left>Comercial</th><th align=left>Detalle</th></tr>" + filas + "</table>") if h else \
                "<p>Aún no hay eventos registrados.</p>"
        return (f"<!doctype html><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
                f"<title>Seguimiento de devoluciones</title><body style='font-family:Segoe UI,Arial;margin:16px;color:#14213d'>"
                f"<h2 style='margin:0 0 6px'>UNISPAN · Seguimiento de devoluciones</h2>"
                f"<p style='margin:0 0 8px'><a href='?'>Todos</a> {filtros} · <a href='?tipo={html.escape(tipo)}&formato=csv'>"
                f"Descargar Excel (CSV)</a></p><style>td,th{{border-bottom:1px solid #e2e8f0;padding:5px 6px;vertical-align:top}}"
                f"</style>{tabla}</body>")

    # -------------------------------------------------------------- 3. asistente
    @app.post("/api/asistente")
    def asistente():
        ip = ctx["ip"]()
        q, ahora = consultas[ip], time.time()
        while q and ahora - q[0] > 600:
            q.popleft()
        if len(q) >= 30:
            return jsonify(ok=False, respuesta="Hiciste muchas preguntas seguidas. Intenta en unos minutos."), 429
        q.append(ahora)
        d = request.get_json(silent=True) or {}
        hist = [m for m in (d.get("mensajes") or [])[-8:] if isinstance(m, dict)]
        pregunta = str((hist[-1] if hist else {}).get("texto") or "").strip()[:600]
        if not pregunta:
            return jsonify(ok=False, respuesta="Escribe tu pregunta."), 400
        return jsonify(ok=True, respuesta=_responder(hist))


GUIA = """Eres el asistente de la página de SOLICITUD DE DEVOLUCIONES de formaleta/equipo de UNISPAN Colombia.
Ayudas a clientes (constructoras) a llenar la solicitud. Responde en español, breve (máx. 6 líneas), amable y
concreto. Si preguntan algo fuera de este tema, di que solo ayudas con la solicitud de devoluciones.
NUNCA inventes correos, obras, NIT, fechas ocupadas ni datos de clientes; no tienes acceso a datos de clientes.

CÓMO SE LLENA:
1. Registro: escribir el NIT del cliente (sin puntos ni dígito de verificación) y pulsar la lupa. Si no lo
   recuerda: "¿No recuerdas el NIT?" → nombre de la constructora y de la obra. Si no aparece: registro manual
   (lo valida el coordinador). Más de 3 NIT equivocados en 24 h bloquean la página; se pide desbloqueo.
2. Obra: elegirla de la lista. Se llenan solos el administrador de proyectos, la zona y el asesor comercial.
3. Correos del cliente: los ya registrados aparecen tapados con candado (por seguridad) y reciben la
   programación; se pueden AGREGAR correos con "+" (no quitar los registrados). Celulares opcionales.
4. Toneladas (peso aproximado del equipo a devolver) y tipo de vehículo si lo conoce. Si supera la capacidad
   de una tractomula (34 t) se programan varios vehículos.
5. Fechas: fecha mínima y máxima en que pueden entregar. SOLO lunes a viernes, NO festivos de Colombia y NO
   días que ya están con la capacidad máxima (la página los rechaza y muestra días disponibles). En la Costa se
   necesitan mínimo 3 días hábiles; en otras zonas 1 día hábil; se programa dentro de 5 días hábiles.
6. Datos de quien solicita (nombre, cédula, celular) y observaciones (acceso a la obra, horarios, etc.).
7. "Agregar a la lista" y luego "Enviar solicitud". Llega por correo la programación (fecha, hora, vehículo).
REPROGRAMAR: pestaña "Reprogramación" (fecha actual asignada, nueva fecha y motivo).
CONFIRMACIONES: antes de la devolución llega un correo para confirmar (Costa 3 días hábiles antes; otras zonas
2 y 1 día antes). Si no pueden cumplir deben indicar el motivo (vehículo, fallas, equipo en uso, falta de
personal para cargar, etc.). Si la devolución no se hace en la fecha pactada, el equipo sigue generando
arrendamiento."""


def _responder(hist: list) -> str:
    cal = calendario(30)
    contexto = (f"\nHOY: {cal['hoy']}. Próximos días hábiles disponibles: {', '.join(cal['disponibles'][:8])}. "
                f"Festivos próximos: {', '.join(f['fecha'] + ' ' + f['nombre'] for f in cal['festivos'][:4]) or 'ninguno'}. "
                f"Días llenos: {', '.join(cal['llenos'][:6]) or 'ninguno'}.")
    clave = os.environ.get("ANTHROPIC_API_KEY", "")
    if clave:
        try:
            msgs = []
            for m in hist:
                rol = "assistant" if m.get("rol") == "asistente" else "user"
                texto = str(m.get("texto") or "")[:600]
                if texto and (not msgs or msgs[-1]["role"] != rol):
                    msgs.append({"role": rol, "content": texto})
            while msgs and msgs[0]["role"] != "user":
                msgs.pop(0)
            r = requests.post("https://api.anthropic.com/v1/messages", timeout=30,
                              headers={"x-api-key": clave, "anthropic-version": "2023-06-01",
                                       "content-type": "application/json"},
                              json={"model": os.environ.get("MODELO_ASISTENTE", "claude-haiku-4-5"),
                                    "max_tokens": 350, "system": GUIA + contexto, "messages": msgs})
            if r.ok:
                return "".join(b.get("text", "") for b in r.json().get("content", [])).strip()
            print(f"AVISO asistente: {r.status_code} {r.text[:150]}", flush=True)
        except Exception as exc:  # noqa: BLE001
            print(f"AVISO asistente: {exc}", flush=True)
    return _respuesta_guia(str(hist[-1].get("texto") or ""), cal)


def _respuesta_guia(p: str, cal: dict) -> str:
    """Sin clave de IA: respuestas guiadas por palabras clave."""
    t = _norm(p)
    reglas = [
        (("NIT", "BLOQUE"), "Escribe el NIT completo, sin puntos ni dígito de verificación, y pulsa la lupa. Si no "
                            "lo recuerdas usa «¿No recuerdas el NIT?». Más de 3 errores en 24 h bloquean la página."),
        (("FECHA", "DIA", "FESTIVO", "CUANDO", "LLENO", "DISPONIBLE"),
         "Solo se programa de lunes a viernes, sin festivos ni días llenos. Próximos días disponibles: "
         + ", ".join(cal["disponibles"][:6]) + ". Costa: mínimo 3 días hábiles; otras zonas: 1."),
        (("CORREO", "EMAIL", "CANDADO"), "Los correos ya registrados salen tapados con 🔒 y reciben la programación. "
                                         "Puedes agregar otros con «+»."),
        (("TONELADA", "PESO", "VEHICULO", "TRACTOMULA"), "Escribe el peso aproximado en toneladas. Si pasa de 34 t "
                                                         "(una tractomula) se programan varios vehículos."),
        (("REPROGRAM", "CAMBIAR", "MOVER"), "Usa la pestaña «Reprogramación»: fecha actual, nueva fecha y motivo."),
        (("OBRA",), "Elige la obra de la lista después de buscar el NIT. Si no aparece, usa el registro manual."),
        (("CONFIRM", "CUMPLIR", "INCUMPL", "MOTIVO"), "Antes de la devolución llega un correo para confirmarla. Si no "
                                                     "pueden cumplir, indiquen el motivo; el equipo sigue generando "
                                                     "arrendamiento hasta devolverlo."),
    ]
    for claves, resp in reglas:
        if any(k in t for k in claves):
            return resp
    return ("Puedo ayudarte con: NIT y obra, correos, toneladas y vehículo, fechas disponibles (lunes a viernes sin "
            "festivos), reprogramación y confirmaciones. ¿Sobre cuál tienes la duda?")
