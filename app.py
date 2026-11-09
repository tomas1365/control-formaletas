"""
Página pública de solicitud de devoluciones (para clientes).

El cliente llena el formulario → por cada registro se envía un correo al buzón
de devoluciones (MAILBOX_USER) con asunto "DEVOLUCIÓN - <obra>" y los datos en
un código con los datos al pie → el bot de la oficina (automatizacion/main.py) lo toma,
lo registra en el sistema real y le confirma al cliente por correo.

No toca el sistema interno ni guarda base de datos: el buzón es la cola.

Despliegue (Render):
    Build:  pip install -r requirements.txt
    Start:  gunicorn app:app
    Variables: AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, MAILBOX_USER,
               CLAVE_PROGRAMADOR (para gestionar contactos), DATA_DIR (disco persistente)
Local:
    py -3.11 app.py   → http://localhost:5000
"""

import base64
import hashlib
import secrets
import hmac
import html
import json
import os
import re
import threading
import time
from collections import defaultdict, deque
from datetime import date, timedelta

import requests
from flask import Flask, jsonify, render_template, request, session

import almacen
import catalogo
import operacion
import seguridad

try:  # certificados de Windows (red UNISPAN); en Render no hace falta
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

_AQUI = os.path.dirname(os.path.abspath(__file__))
# index.html en templates/ (estructura normal) o junto a app.py (repositorio subido sin carpetas)
app = Flask(__name__, template_folder="templates" if os.path.isdir(os.path.join(_AQUI, "templates")) else ".")
app.config["TEMPLATES_AUTO_RELOAD"] = True  # al reemplazar index.html se ve sin reiniciar
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # solo la sincronización del PC envía datos grandes
# Sesión (cookie firmada): guarda qué NIT verificó este navegador con el código enviado al correo del cliente.
app.secret_key = os.environ.get("SECRET_KEY") or hashlib.sha256(
    ("sesion-devoluciones|" + os.environ.get("CLAVE_SYNC", "") + "|" + os.environ.get("AZURE_CLIENT_SECRET", "")
     + "|" + os.environ.get("CLAVE_PROGRAMADOR", "")).encode()).hexdigest()
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Strict",
                  SESSION_COOKIE_SECURE=bool(os.environ.get("RENDER")), PERMANENT_SESSION_LIFETIME=4 * 3600)


@app.after_request
def _sin_cache(resp):
    # la página siempre se pide fresca (evita ver versiones viejas tras actualizar)
    if request.path == "/" or request.path.startswith("/api/"):
        resp.headers["Cache-Control"] = "no-store"
    return seguridad.encabezados(resp, request)


# Rutas que exigen la clave de programador (se permiten aunque el equipo esté bloqueado:
# la clave se valida igual y sus fallos también bloquean).
RUTAS_CLAVE = ("/api/contactos/sincronizar", "/api/bloqueos", "/api/reasignaciones", "/api/coordinador")


@app.errorhandler(Exception)
def _error_interno(exc):
    """Registra el detalle completo en los Logs y muestra en la página el tipo de error."""
    from werkzeug.exceptions import HTTPException
    if isinstance(exc, HTTPException):
        return exc
    import traceback
    detalle = traceback.format_exc()
    print("ERROR INTERNO:", request.path, "\n" + detalle, flush=True)
    ref = secrets.token_hex(3).upper()  # referencia para buscar el detalle en los Logs (no se muestra el error)
    print(f"ERROR INTERNO ref {ref}", flush=True)
    if request.path.startswith("/api/"):
        return jsonify(ok=False, error=f"Error interno (ref. {ref}). Avísale al coordinador."), 500
    return "Error interno. Intenta de nuevo en un momento.", 500


@app.before_request
def _filtro_seguridad():
    if request.path.startswith("/api/sync/"):
        return None  # lo usa el PC de la oficina (bot); se protege con CLAVE_SYNC
    if (request.content_length or 0) > 256 * 1024:
        return jsonify(ok=False, error="Petición demasiado grande."), 413
    if request.method in ("POST", "PUT", "DELETE") and not seguridad.origen_valido(request):
        return jsonify(ok=False, error="Origen no permitido."), 403
    ip = seguridad.ip_cliente(request)
    if not seguridad.bloqueo(ip):
        return None
    libre = request.path in ("/", "/salud", "/api/estado", "/api/desbloqueo") or request.path.startswith(RUTAS_CLAVE) \
        or (request.path == "/api/contactos" and request.method in ("POST", "DELETE"))
    if not libre:
        return jsonify(ok=False, bloqueado=True,
                       error="La página está bloqueada para este equipo. Solicita el desbloqueo al coordinador."), 423
    return None

MARCADOR = "DATOS_DEVOLUCION"  # el bot busca "DATOS_DEVOLUCION:<base64>" en el cuerpo
MAX_REGISTROS = 10
MAX_TONELADAS = 500

ZONAS = ["Cali", "Bogotá", "Cundinamarca", "Costa", "Barranquilla", "Eje Cafetero"]
VEHICULOS = ["Turbo", "Sencillo", "Dobletroque", "Tractomula"]
# Contactos (programadores, administradores de proyectos, asesores) — los
# gestiona el programador desde la página con su clave. Se guardan en
# DATA_DIR/contactos.json (en Render, DATA_DIR debe ser un disco persistente).
DATA_DIR = os.environ.get("DATA_DIR", os.path.dirname(os.path.abspath(__file__)))
seguridad.configurar(DATA_DIR)
catalogo.configurar(DATA_DIR)
CONTACTOS_PATH = os.path.join(DATA_DIR, "contactos.json")
CONTACTOS_INICIALES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contactos.json")
TIPOS = {"programadores": False, "administradores": True, "asesores": True}  # tipo → requiere zona
_lock = threading.Lock()


def _contactos() -> dict:
    datos = {}
    # Si aún no hay datos guardados, arranca con la lista inicial del proyecto
    for ruta in (CONTACTOS_PATH, CONTACTOS_INICIALES):
        try:
            with open(ruta, encoding="utf-8") as f:
                datos = json.load(f)
            break
        except FileNotFoundError:
            continue
    return {t: datos.get(t, []) for t in TIPOS}


def _guardar_contactos(datos: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = CONTACTOS_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    os.replace(tmp, CONTACTOS_PATH)  # escritura atómica
    almacen.guardado(CONTACTOS_PATH)


def _error_clave(clave: str):
    """Devuelve una respuesta de error si la clave no sirve, o None si está bien."""
    if not os.environ.get("CLAVE_PROGRAMADOR"):
        return jsonify(ok=False, error="El servidor no tiene clave configurada: agrega la línea "
                       "CLAVE_PROGRAMADOR=tu_clave en el archivo .env de pagina_solicitud y reinicia la página."), 503
    ip = seguridad.ip_cliente(request)
    if not _clave_ok(clave):
        restantes, bloqueado = seguridad.registrar_fallo(ip, "clave", request.path)
        if bloqueado:
            _alerta_bloqueo(ip)
            return jsonify(ok=False, bloqueado=True, error="Clave incorrecta. La página quedó bloqueada para este "
                           "equipo; solicita el desbloqueo al coordinador."), 423
        return jsonify(ok=False, error=f"Clave de programador incorrecta. Intentos restantes: {restantes}."), 403
    seguridad.registrar_exito(ip, "clave")
    return None


def _clave_ok(clave: str) -> bool:
    esperada = os.environ.get("CLAVE_PROGRAMADOR", "")
    return bool(esperada) and hmac.compare_digest(str(clave or ""), esperada)


RE_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _es_interno(correo: str) -> bool:
    """Correos de UNISPAN (administradores, asesores, directores…): NO son correos del cliente. Los del
    personal se toman de los contactos por zona; los que vienen pegados en las obras del sistema se ignoran
    (si no, llegaban administradores de otras zonas a las solicitudes)."""
    return str(correo or "").strip().lower().endswith("@" + os.environ.get("DOMINIO_INTERNO", "unispan.com.co").lower())

# Límite simple anti-abuso: máx. 5 envíos por IP cada 10 minutos
_envios_por_ip: dict[str, deque] = defaultdict(deque)


def _limite_excedido(ip: str) -> bool:
    ahora = time.time()
    cola = _envios_por_ip[ip]
    while cola and ahora - cola[0] > 600:
        cola.popleft()
    if len(cola) >= 5:
        return True
    cola.append(ahora)
    return False


# ---------------------------------------------------------------- Graph
_token = {"valor": None, "expira": 0.0}


def _token_graph() -> str:
    if _token["valor"] and time.time() < _token["expira"] - 60:
        return _token["valor"]
    r = requests.post(
        f"https://login.microsoftonline.com/{os.environ['AZURE_TENANT_ID']}/oauth2/v2.0/token",
        data={
            "grant_type": "client_credentials",
            "client_id": os.environ["AZURE_CLIENT_ID"],
            "client_secret": os.environ["AZURE_CLIENT_SECRET"],
            "scope": "https://graph.microsoft.com/.default",
        },
        timeout=30,
    )
    if not r.ok:
        raise RuntimeError(f"Token {r.status_code}: {r.text[:300]}")
    d = r.json()
    _token.update(valor=d["access_token"], expira=time.time() + int(d.get("expires_in", 3600)))
    return _token["valor"]


_carpeta_avisos_id = {}


def _carpeta_avisos() -> str:
    """Carpeta 'AVISOS AUTOMATIZACION' dentro de la Bandeja de entrada (la crea si no existe)."""
    nombre = os.environ.get("CARPETA_AVISOS", "AVISOS AUTOMATIZACION")
    if nombre in _carpeta_avisos_id:
        return _carpeta_avisos_id[nombre]
    buzon = os.environ["MAILBOX_USER"]
    h = {"Authorization": f"Bearer {_token_graph()}"}
    r = requests.get(f"https://graph.microsoft.com/v1.0/users/{buzon}/mailFolders/Inbox/childFolders?$top=200",
                     headers=h, timeout=30)
    for f in (r.json().get("value", []) if r.ok else []):
        if f.get("displayName", "").strip().lower() == nombre.lower():
            _carpeta_avisos_id[nombre] = f["id"]
            return f["id"]
    r = requests.post(f"https://graph.microsoft.com/v1.0/users/{buzon}/mailFolders/Inbox/childFolders",
                      headers=h, json={"displayName": nombre}, timeout=30)
    if not r.ok:
        return "inbox"
    _carpeta_avisos_id[nombre] = r.json()["id"]
    return _carpeta_avisos_id[nombre]


def _enviar_al_buzon(asunto: str, cuerpo_html: str, responder_a: str, carpeta: str = "inbox"):
    """Deja la solicitud DIRECTAMENTE en la Bandeja de entrada del buzón, como correo no leído.
    (Enviarse un correo a sí mismo con sendMail no llegaba: el buzón lo descartaba.)
    La propiedad 0x0E07 = 1 hace que quede como mensaje recibido y no como borrador."""
    buzon = os.environ["MAILBOX_USER"]
    r = requests.post(
        f"https://graph.microsoft.com/v1.0/users/{buzon}/mailFolders/{carpeta}/messages",
        headers={"Authorization": f"Bearer {_token_graph()}"},
        json={
            "subject": asunto,
            "body": {"contentType": "HTML", "content": cuerpo_html},
            "from": {"emailAddress": {"address": responder_a, "name": f"Página de solicitudes ({responder_a})"}},
            "sender": {"emailAddress": {"address": responder_a}},
            "toRecipients": [{"emailAddress": {"address": buzon}}],
            "replyTo": [{"emailAddress": {"address": responder_a}}],
            "isRead": False,
            "singleValueExtendedProperties": [{"id": "Integer 0x0E07", "value": "1"}],
        },
        timeout=30,
    )
    if not r.ok:
        raise RuntimeError(f"Graph {r.status_code}: {r.text[:300]}")


# ---------------------------------------------------------------- validación
def _texto(valor, maximo=200) -> str:
    return str(valor or "").strip()[:maximo]


def _fecha(valor):
    try:
        return date.fromisoformat(valor) if valor else None
    except ValueError:
        return None


DIAS_HABILES_MAX = 5  # regla de la compañía (igual que automatizacion/reglas.py)


def _dias_habiles(desde: date, n: int) -> date:
    d, c = desde, 0
    while c < n:
        d += timedelta(days=1)
        if d.weekday() < 5:
            c += 1
    return d


def _lista_correos(valor) -> list:
    partes = valor if isinstance(valor, list) else re.split(r"[;,\s]+", _texto(valor, 800))
    return list(dict.fromkeys(c.strip().lower() for c in partes if c and c.strip()))[:15]


def _lista_celulares(valor) -> list:
    partes = valor if isinstance(valor, list) else _texto(valor, 300).split(";")
    return list(dict.fromkeys(re.sub(r"[^\d+ ]", "", str(c)).strip() for c in partes if str(c).strip()))[:10]


# Correos y celulares del cliente por obra (los recuerda la página para la próxima solicitud)
CORREOS_OBRAS_PATH = os.path.join(DATA_DIR, "correos_obras.json")


def _nit_base(nit) -> str:
    """Sin dígito de verificación: 8605134931 / 860513493-1 → 860513493 (así se guarda y se busca)."""
    d = re.sub(r"\D", "", str(nit or "").split("-")[0])
    return d[:9] if len(d) == 10 else d


def _clave_obra(nit, obra) -> str:
    nit_d = _nit_base(nit)
    obra_n = re.sub(r"[^A-Z0-9]+", " ", str(obra or "").upper()).strip()
    return nit_d + "|" + obra_n


def _correos_obras() -> dict:
    try:
        with open(CORREOS_OBRAS_PATH, encoding="utf-8") as f:
            crudos = json.load(f)
    except (FileNotFoundError, ValueError):
        return {}
    # Correos que se guardaron con el NIT + dígito de verificación (10 dígitos): se unen a la clave correcta
    datos = {}
    for k, v in crudos.items():
        if not isinstance(v, dict) or "|" not in str(k) or str(k).startswith("MANUAL:"):
            datos[k] = v
            continue
        n, o = str(k).split("|", 1)
        k2 = _nit_base(n) + "|" + o
        previo = datos.get(k2)
        if previo:
            nuevo, viejo = (v, previo) if v.get("actualizado", "") >= previo.get("actualizado", "") else (previo, v)
            v = {**viejo, **nuevo, "correos": list(dict.fromkeys((nuevo.get("correos") or []) + (viejo.get("correos") or [])))}
        datos[k2] = v
    return datos


def _clave_manual(cliente, obra) -> str:
    """Obras registradas a mano (sin NIT): se recuerdan por constructora + obra."""
    return "MANUAL:" + re.sub(r"[^A-Z0-9]+", " ", str(cliente or "").upper()).strip() + _clave_obra("", obra)


def _guardar_correos_obra(nit, obra, correos, celulares, cliente="", extra=None):
    if not obra or not (nit or cliente):
        return
    with _lock:
        datos = _correos_obras()
        k = _clave_obra(nit, obra) if nit else _clave_manual(cliente, obra)
        previo = datos.get(k) if isinstance(datos.get(k), dict) else {}
        if not celulares:  # quien no ve los celulares guardados no los borra
            celulares = previo.get("celulares") or []
        datos[k] = {**previo, "obra": obra, "correos": correos, "celulares": celulares,
                    "actualizado": date.today().isoformat()}
        if not nit:
            datos[k].update({"cliente": cliente, "manual": True, **{a: b for a, b in (extra or {}).items() if b}})
        os.makedirs(DATA_DIR, exist_ok=True)
        tmp = CORREOS_OBRAS_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=1)
        os.replace(tmp, CORREOS_OBRAS_PATH)
        almacen.guardado(CORREOS_OBRAS_PATH)


def _validar(payload: dict):
    """Devuelve (cabecera, registros, errores)."""
    errores = []
    lista = _contactos()
    correos_de = lambda tipo: {c["correo"].lower() for c in lista.get(tipo, [])}

    programador = _texto(payload.get("correo_programador"), 120).lower()
    administrador = _texto(payload.get("correo_administrador"), 120).lower()
    asesores = [_texto(a, 120).lower() for a in (payload.get("correos_asesores") or []) if a]

    zona = _texto(payload.get("zona"), 30)
    admin = next((c for c in lista["administradores"] if c["correo"].lower() == administrador), None)
    if programador not in correos_de("programadores"):
        errores.append("Selecciona el correo del programador.")
    if not admin:
        errores.append("Selecciona un administrador de proyectos de la lista.")
    elif not zona:
        zona = admin.get("zona", "")
    if zona not in ZONAS:
        errores.append("Elige la zona.")
    if any(a not in correos_de("asesores") for a in asesores):
        errores.append("Algún correo de asesor no es válido.")
    por_correo = lambda tipo: {c["correo"].lower(): c for c in lista.get(tipo, [])}
    cabecera = {
        "zona": zona,
        "contacto_programador": por_correo("programadores").get(programador, {}),
        "contacto_administrador": admin or {},
        "contacto_asesores": [por_correo("asesores")[a] for a in asesores if a in por_correo("asesores")],
        "programador": programador,
        "administrador": administrador,
        "asesores": asesores,
    }

    registros = []
    crudos = payload.get("registros") or []
    if not isinstance(crudos, list) or not crudos:
        errores.append("Crea al menos un registro.")
        crudos = []
    if len(crudos) > MAX_REGISTROS:
        errores.append(f"Máximo {MAX_REGISTROS} registros por solicitud.")
        crudos = crudos[:MAX_REGISTROS]

    manana = date.today() + timedelta(days=1)
    for i, r in enumerate(crudos, start=1):
        n = f"Registro {i}"
        cliente, obra = _texto(r.get("cliente")), _texto(r.get("obra"))
        nit = re.sub(r"\D", "", _texto(r.get("nit"), 20))
        zona = cabecera["zona"]
        vehiculo = _texto(r.get("tipo_vehiculo"), 30)
        try:
            ton = round(float(str(r.get("toneladas", "")).replace(",", ".")), 2)
        except ValueError:
            ton = 0
        f_min, f_max = _fecha(r.get("fecha_minima")), _fecha(r.get("fecha_maxima"))
        for etiqueta, fx in (("fecha mínima", f_min), ("fecha máxima", f_max)):
            if fx and operacion.motivo_fecha(fx):
                errores.append(f"{n}: la {etiqueta} {fx.strftime('%d/%m/%Y')} no se puede programar: "
                               f"{operacion.motivo_fecha(fx)}.")

        clientes = [c for c in _lista_correos(r.get("correos_clientes"))
                    if not _es_interno(c) or operacion.es_prueba(r.get("obra"))]
        celulares = _lista_celulares(r.get("celulares_clientes"))
        if not clientes:
            errores.append(f"{n}: ingresa al menos un correo del cliente.")
        malos = [c for c in clientes if not RE_EMAIL.match(c)]
        if malos:
            errores.append(f"{n}: correos no válidos: {', '.join(malos)}")
        if not cliente:
            errores.append(f"{n}: falta el cliente.")
        if not obra:
            errores.append(f"{n}: falta la obra.")
        if not (0 < ton <= MAX_TONELADAS):
            errores.append(f"{n}: las toneladas deben ser mayores a 0 y hasta {MAX_TONELADAS}.")
        if f_min and f_min < manana:
            errores.append(f"{n}: la fecha mínima debe ser a partir de mañana.")
        if f_min and f_max and f_max < f_min:
            errores.append(f"{n}: la fecha máxima es anterior a la mínima.")
        if vehiculo and vehiculo not in VEHICULOS:
            errores.append(f"{n}: tipo de vehículo no válido.")

        registros.append({
            "nit": nit or None,
            "manual": bool(r.get("manual")),
            "clientes": clientes,
            "celulares_clientes": celulares,
            "cliente": cliente,
            "obra": obra,
            "zona": zona,
            "toneladas": ton,
            "fecha_minima": f_min.isoformat() if f_min else None,
            "fecha_maxima": (f_max or f_min).isoformat() if (f_max or f_min) else None,
            "tipo_vehiculo": vehiculo or None,
            "funcionario": _texto(r.get("funcionario")),
            "cedula": re.sub(r"\D", "", _texto(r.get("cedula"), 20)),
            "celular": _texto(r.get("celular"), 30),
            "observaciones": _texto(r.get("observaciones"), 500),
        })
    return cabecera, registros, errores


def _persona(c: dict) -> str:
    """'Nombre <correo> · cel' para el resumen del correo."""
    if not c:
        return ""
    texto = f"{c.get('nombre', '')} <{c.get('correo', '')}>"
    return f"{texto} · {c['celular']}" if c.get("celular") else texto


def _correo_registro(cab: dict, reg: dict) -> tuple[str, str]:
    copia = [c for c in [cab["programador"], cab["administrador"], *cab["asesores"]] if c]
    datos = {
        "registro_manual": reg.get("manual", False),
        "correo_por_aprobar": reg.get("correo_por_aprobar"),
        "nit": reg.get("nit"),
        "cliente": reg["cliente"],
        "obra": reg["obra"],
        "zona": reg["zona"],
        "toneladas": reg["toneladas"],
        "fecha_minima": reg["fecha_minima"],
        "fecha_maxima": reg["fecha_maxima"],
        "tipo_vehiculo": reg["tipo_vehiculo"],
        "funcionario": reg["funcionario"] or None,
        "cedula": reg["cedula"] or None,
        "celular": reg["celular"] or None,
        "observaciones": reg["observaciones"] or None,
        "correo_cliente": ",".join(reg["clientes"]),
        "correo_copia": ",".join(copia),
        "celulares_clientes": reg["celulares_clientes"],
        "telefonos": {
            "programador": cab["contacto_programador"].get("celular"),
            "administrador": cab["contacto_administrador"].get("celular"),
            "asesores": {a["correo"]: a.get("celular") for a in cab["contacto_asesores"]},
        },
        "origen": "pagina_solicitud",
    }
    filas = [
        ("Registro", "MANUAL (sin NIT) — validar cliente y obra" if reg.get("manual") else "Con NIT"),
        ("Verificación", f"CORREO POR APROBAR: {reg['correo_por_aprobar']} — aprobar antes de programar"
                         if reg.get("correo_por_aprobar") else ("Sin verificar (registro manual)"
                                                                 if reg.get("manual") else "Correo verificado")),
        ("NIT", reg.get("nit")), ("Cliente", reg["cliente"]), ("Obra", reg["obra"]), ("Zona", reg["zona"]),
        ("Toneladas", reg["toneladas"]),
        ("Fecha mínima", reg["fecha_minima"]), ("Fecha máxima", reg["fecha_maxima"]),
        ("Tipo de vehículo", reg["tipo_vehiculo"] or "Automático según peso"),
        ("Funcionario", reg["funcionario"]), ("C.C.", reg["cedula"]), ("Cel", reg["celular"]),
        ("Observaciones", reg["observaciones"]),
        ("Correos de clientes", "; ".join(reg["clientes"])),
        ("Celulares de clientes", "; ".join(reg["celulares_clientes"])),
        ("Programador", _persona(cab["contacto_programador"])),
        ("Administrador", _persona(cab["contacto_administrador"])),
        ("Asesores", "; ".join(_persona(a) for a in cab["contacto_asesores"])),
    ]
    tabla = "".join(
        f"<tr><td style='padding:4px 10px;color:#555'>{html.escape(k)}</td>"
        f"<td style='padding:4px 10px'><b>{html.escape(str(v or '—'))}</b></td></tr>"
        for k, v in filas
    )
    # Datos para el bot: JSON en base64 en un pie de texto pequeño (sobrevive a
    # cualquier limpieza de HTML que haga Exchange).
    codigo = base64.b64encode(json.dumps(datos, ensure_ascii=False).encode()).decode()
    cuerpo = (
        f"<p>Solicitud en devoluciones recibida desde la página web.</p>"
        f"<table style='border-collapse:collapse;font-family:Segoe UI,Arial'>{tabla}</table>"
        f"<p style='color:#999;font-size:9px;word-break:break-all'>{MARCADOR}:{codigo}</p>"
    )
    asunto = f"DEVOLUCIÓN - {reg['obra']} - {reg['cliente']}"[:150]
    return asunto, cuerpo


# ---------------------------------------------------------------- rutas
@app.get("/")
def inicio():
    hoy = date.today()
    bloqueo = seguridad.bloqueo(seguridad.ip_cliente(request))
    return render_template("index.html", bloqueo=bloqueo, motivos_reprog=MOTIVOS_REPROGRAMACION, zonas=ZONAS, vehiculos=VEHICULOS, max_registros=MAX_REGISTROS,
                           fecha_min=(hoy + timedelta(days=1)).isoformat(),
                           fecha_max=_dias_habiles(hoy, DIAS_HABILES_MAX).isoformat())


# Grupos de Outlook con los asesores de cada zona: correo_del_grupo=Zona;...
GRUPOS_ASESORES = os.environ.get(
    "GRUPOS_ASESORES",
    "asesorescali@unispan.com.co=Cali;asesorescosta@unispan.com.co=Costa;asesorescentro@unispan.com.co=Bogotá",
)


def _grupos_asesores() -> list:
    pares = []
    for item in GRUPOS_ASESORES.split(";"):
        if "=" in item:
            g, z = item.split("=", 1)
            pares.append((g.strip().lower(), z.strip()))
    return pares


def _graph_get(ruta: str, **kw):
    r = requests.get("https://graph.microsoft.com/v1.0" + ruta, timeout=30,
                     headers={"Authorization": f"Bearer {_token_graph()}", "ConsistencyLevel": "eventual"}, **kw)
    if r.status_code == 403:
        raise PermissionError("Microsoft no dio permiso para leer los grupos de Outlook. En Azure → la app → "
                              "Permisos de API: agregar GroupMember.Read.All y User.Read.All (Aplicación) y "
                              "pedir de nuevo el consentimiento del administrador.")
    if not r.ok:
        raise RuntimeError(f"Graph {r.status_code}: {r.text[:200]}")
    return r.json()


GRUPOS_ADMINISTRADORES = os.environ.get("GRUPOS_ADMINISTRADORES", "")  # opcional, mismo formato


def _zona_de_texto(texto: str) -> str:
    t = (texto or "").upper()
    if any(x in t for x in ("EJE", "CAFETER", "PEREIRA", "MANIZALES", "ARMENIA", "RISARALDA", "CALDAS", "QUINDIO", "QUINDÍO")):
        return "Eje Cafetero"
    if "CALI" in t or "VALLE" in t:
        return "Cali"
    if any(x in t for x in ("BARRANQUILLA", "CARTAGENA", "SANTA MARTA", "COSTA", "ATLANTICO", "ATLÁNTICO")):
        return "Costa"
    if "BOGOT" in t or "CENTRO" in t or "CUNDINAMARCA" in t:
        return "Bogotá"
    return ""


def _miembros(pares) -> tuple[dict, list]:
    vistos, sin_grupo = {}, []
    for grupo, zona in pares:
        g = _graph_get("/groups", params={"$filter": f"mail eq '{grupo}'", "$select": "id,displayName"})
        if not g.get("value"):
            sin_grupo.append(grupo)
            continue
        url = f"/groups/{g['value'][0]['id']}/transitiveMembers/microsoft.graph.user"
        params = {"$select": "displayName,mail,mobilePhone,businessPhones", "$top": "999", "$count": "true"}
        for u in _graph_get(url, params=params).get("value", []):
            correo = (u.get("mail") or "").strip().lower()
            if correo and correo not in vistos:
                cel = u.get("mobilePhone") or ", ".join(u.get("businessPhones") or [])
                vistos[correo] = {"nombre": (u.get("displayName") or correo).strip(), "correo": correo,
                                  "celular": cel or "", "zona": zona, "origen": "outlook"}
    return vistos, sin_grupo


def _administradores_de_fletes() -> tuple[dict, list]:
    """Nombres de 'Administrador de Proyecto' en FLETES → usuario de Outlook (correo, celular, ciudad)."""
    import fuente_clientes as fc
    nombres = sorted({o.get("administrador", "").strip() for o in fc.Quantify.desde_nube().obras
                      if o.get("administrador", "").strip()})
    vistos, sin_usuario = {}, []
    for nombre in nombres:
        limpio = re.sub(r"[^\w\s]", " ", nombre).strip()
        try:
            r = _graph_get("/users", params={"$search": f'"displayName:{limpio}"', "$top": "5",
                                             "$select": "displayName,mail,mobilePhone,businessPhones,city,officeLocation,department"})
        except PermissionError:
            raise
        except Exception:  # noqa: BLE001
            r = {}
        usuarios = [u for u in r.get("value", []) if u.get("mail")]
        if len(usuarios) != 1:
            sin_usuario.append(nombre)
            continue
        u = usuarios[0]
        correo = u["mail"].strip().lower()
        zona = _zona_de_texto(" ".join(str(u.get(k) or "") for k in ("city", "officeLocation", "department")))
        vistos[correo] = {"nombre": nombre, "correo": correo,
                          "celular": u.get("mobilePhone") or ", ".join(u.get("businessPhones") or []),
                          "zona": zona, "origen": "outlook"}
    return vistos, sin_usuario


# ------------------------------------------------- contactos desde el Excel "Contactos Unispan"
CONTACTOS_EXCEL_URL = os.environ.get("CONTACTOS_EXCEL_URL", "").strip()
_EXCLUIR = ("jefe de servicio", "planta", "logistic", "nomina", "gestion humana", "almacen",
            "proyectista", "desarrollo", "despacho", "mantenimiento", "marketing", "gerente")


def _sin_tildes(t: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", t or "") if unicodedata.category(c) != "Mn").lower()


def _clasificar(cargo: str, zona: str):
    """Reglas de UNISPAN: administrador de proyectos, líder y director (excepto el de Cali) →
    administradores; asesor y coordinador (de zona) → asesores; jefe de servicio en obra y el resto → nada."""
    c = _sin_tildes(cargo)
    if any(x in c for x in _EXCLUIR):
        return None
    if "asistente comercial" in c or "asistente de comercial" in c:
        return "ambos"  # funcionan como administradores y como asesores
    if "director" in c:
        return None if zona == "Cali" else "administradores"
    if re.search(r"administrador(a)?\b", c) or re.search(r"\blider\b", c):
        return "administradores"
    if "asesor" in c or "coordinador" in c:
        return "asesores"
    return None


def _zona_excel(texto: str) -> str:
    t = _sin_tildes(texto).upper()
    if "CUNDINAMARCA" in t:
        return "Cundinamarca"
    return _zona_de_texto(t)


_ENCAB = {"nombre": ("nombre", "contacto", "usuario", "funcionario"),
          "correo": ("correo", "email", "e-mail", "mail"),
          "cargo": ("cargo", "rol", "puesto"),
          "zona": ("zona", "regional", "sede", "ciudad"),
          "celular": ("celular", "movil", "telefono")}


def _tablas_con_encabezado(filas: list) -> list:
    """Detecta tablas con fila de encabezados (Nombre | Correo | Cargo | Zona | Celular…), aunque haya
    varias lado a lado. Devuelve dicts {nombre, correo, cargo, zona, celular, titulo}."""
    salida, titulo_col = [], {}
    for i, fila in enumerate(filas):
        celdas = [str(x).strip() if x is not None else "" for x in fila]
        llenas = [k for k, x in enumerate(celdas) if x]
        if 1 <= len(llenas) <= 2 and not any(re.search(r"\d{5,}|@", celdas[k]) for k in llenas):
            for k in llenas:
                for j in range(k - 1, k + 6):
                    titulo_col[j] = celdas[k]
        # ¿fila de encabezados? (al menos nombre + (correo o cargo))
        mapa = {}
        for k, x in enumerate(celdas):
            t = _sin_tildes(x)
            for campo, claves in _ENCAB.items():
                if t and any(t == c or t.startswith(c) for c in claves) and len(t) <= 25:
                    mapa.setdefault(campo, []).append(k)
        if "nombre" not in mapa or not ({"correo", "cargo"} & mapa.keys()):
            continue
        for inicio in mapa["nombre"]:  # una tabla por cada columna "Nombre"
            cols = {c: min((k for k in ks if k >= inicio), default=None) for c, ks in mapa.items()}
            fin = min([k for k in mapa["nombre"] if k > inicio] or [len(celdas) + 50])
            cols = {c: k for c, k in cols.items() if k is not None and k < fin}
            for f2 in filas[i + 1:]:
                c2 = [str(x).strip() if x is not None else "" for x in f2]
                val = lambda campo: c2[cols[campo]] if campo in cols and cols[campo] < len(c2) else ""
                if not val("nombre") and not val("correo"):
                    if not any(c2[inicio:fin]):
                        break  # fin de la tabla
                    continue
                if _sin_tildes(val("nombre")) in _ENCAB["nombre"]:
                    break  # empieza otra tabla
                salida.append({"nombre": val("nombre"), "correo": val("correo").lower(), "cargo": val("cargo"),
                               "zona": val("zona"), "celular": re.sub(r"\D", "", val("celular")),
                               "titulo": titulo_col.get(inicio, "")})
    return salida


def _leer_excel_contactos() -> tuple[list, list, dict, list]:
    """Devuelve (personas, omitidos, correos_por_nombre, resumen_hojas).
    Lee TODAS las hojas: las que tienen encabezados (p. ej. hoja 'Correo') y el directorio por tablas."""
    import fuente_clientes as fc
    libro = fc.LibroExcel(CONTACTOS_EXCEL_URL)
    hojas = [os.environ["CONTACTOS_EXCEL_HOJA"]] if os.environ.get("CONTACTOS_EXCEL_HOJA") else libro.hojas()
    personas, omitidos, correos, resumen = [], [], {}, []
    vistos = set()
    for hoja in hojas:
        filas, _ = libro.leer(hoja)
        filas_hoja = _tablas_con_encabezado(filas)
        n_hoja = 0
        for r in filas_hoja:
            if r["correo"] and "@" in r["correo"] and r["nombre"]:
                correos.setdefault(" ".join(sorted(_tokens(r["nombre"]))), r["correo"])
            if not r["nombre"] or _sin_tildes(r["nombre"]) in ("libre", "vacante"):
                continue
            cargo = r["cargo"]
            par = re.search(r"\(([^)]+)\)", cargo)
            zona = (_zona_excel(r["zona"]) or (_zona_excel(par.group(1)) if par else "")
                    or _zona_excel(cargo) or _zona_excel(r["titulo"]))
            tipo = _clasificar(cargo, zona) if cargo else None
            if not tipo:
                if cargo and re.search(r"asesor|administrador|director|lider|líder|coordinador|jefe", cargo, re.I):
                    omitidos.append(f"{r['nombre']} ({cargo}) — hoja {hoja}")
                continue
            clave = r["correo"] or _sin_tildes(r["nombre"])
            if clave in vistos:
                continue
            vistos.add(clave)
            personas.append({"tipo": tipo, "nombre": r["nombre"], "cargo": cargo, "zona": zona,
                             "correo": r["correo"] if "@" in r["correo"] else "", "celular": r["celular"]})
            n_hoja += 1
        resumen.append(f"Hoja '{hoja}': {len(filas)} filas, {len(filas_hoja)} contactos en tablas, "
                       f"{n_hoja} asesores/administradores")
    # nombres repetidos entre hojas (el mismo con y sin correo): queda uno solo
    unicos = {}
    for p in personas:
        k = " ".join(sorted(_tokens(p["nombre"])))
        if k not in unicos or (p["correo"] and not unicos[k]["correo"]) or (p["zona"] and not unicos[k]["zona"]):
            previo = unicos.get(k, {})
            p["zona"] = p["zona"] or previo.get("zona", "")
            p["correo"] = p["correo"] or previo.get("correo", "")
            unicos[k] = p
        else:
            unicos[k]["zona"] = unicos[k]["zona"] or p["zona"]
    return list(unicos.values()), omitidos, correos, resumen


def _todos_los_usuarios() -> list:
    """Directorio completo de Outlook (una sola consulta paginada)."""
    usuarios, ruta = [], "/users"
    params = {"$select": "displayName,mail,mobilePhone,businessPhones,jobTitle,city,officeLocation",
              "$top": "999"}
    while ruta:
        d = _graph_get(ruta, params=params)
        usuarios += [u for u in d.get("value", []) if u.get("mail")]
        nxt = d.get("@odata.nextLink")
        ruta, params = (nxt.replace("https://graph.microsoft.com/v1.0", ""), None) if nxt else (None, None)
    return usuarios


def _tokens(t: str) -> set:
    return {x for x in re.findall(r"[a-z]+", _sin_tildes(t)) if len(x) > 1 and x not in ("de", "del", "la", "los")}


def _telefonos(u: dict) -> str:
    return re.sub(r"\D", "", " ".join([u.get("mobilePhone") or ""] + (u.get("businessPhones") or [])))


def _buscar_usuario(nombre: str, celular: str, usuarios: list, en_grupo: set):
    if celular and len(celular) >= 7:
        por_cel = [u for u in usuarios if celular[-7:] in _telefonos(u)]
        if len(por_cel) == 1:
            return por_cel[0]
    tn = _tokens(nombre)
    if not tn:
        return None
    candidatos = [u for u in usuarios if tn <= _tokens(u.get("displayName", ""))]
    if not candidatos and len(tn) >= 3:  # "Juan Carlos Restrepo" vs "Juan Restrepo …": basta nombre + apellido
        lista = [x for x in re.findall(r"[a-z]+", _sin_tildes(nombre)) if len(x) > 1]
        clave = {lista[0], lista[-1]} if len(lista) >= 2 else set(lista)
        candidatos = [u for u in usuarios if clave <= _tokens(u.get("displayName", ""))]
    if len(candidatos) > 1:
        candidatos = [u for u in candidatos if u["mail"].lower() in en_grupo] or candidatos
    return candidatos[0] if len(candidatos) == 1 else None


def _sincronizar_desde_excel():
    """Mezcla: Excel de contactos (cargo y zona) + Outlook (correo, celular y zona por grupo
    ASESORES CALI / COSTA / CENTRO). Quien está en un grupo y no en el Excel también se agrega."""
    personas, omitidos, correos_excel, resumen = _leer_excel_contactos()
    for p in personas:  # correo de la hoja 'Correo' (u otra) por nombre
        if not p["correo"]:
            p["correo"] = correos_excel.get(" ".join(sorted(_tokens(p["nombre"]))), "")
    try:
        usuarios = _todos_los_usuarios()
    except PermissionError:
        usuarios = []
        omitidos.append("(sin permiso para leer el directorio de Outlook: falta User.Read.All concedido)")
    zona_grupo = {}
    try:
        miembros, _ = _miembros(_grupos_asesores())
        zona_grupo = {c: m["zona"] for c, m in miembros.items()}
    except PermissionError:
        omitidos.append("(sin permiso para leer los grupos de Outlook: falta GroupMember.Read.All concedido)")
    except Exception as exc:  # noqa: BLE001
        omitidos.append(f"(no se pudieron leer los grupos de Outlook: {exc})")
    sin_correo, validas = [], {}
    for p in personas:
        if not p["correo"]:
            u = _buscar_usuario(p["nombre"], p["celular"], usuarios, set(zona_grupo))
            if u:
                p["correo"] = u["mail"].strip().lower()
                p["celular"] = p["celular"] or re.sub(r"\D", "", u.get("mobilePhone") or "")
        if not p["correo"]:
            sin_correo.append(f"{p['nombre']} ({p['cargo']})")
            continue
        p["zona"] = p["zona"] or zona_grupo.get(p["correo"], "")
        if not p["zona"]:
            omitidos.append(f"{p['nombre']} ({p['cargo']}): sin zona en el Excel ni en los grupos de Outlook")
            continue
        if not _clasificar(p["cargo"], p["zona"]):  # p. ej. Director cuya zona (Cali) salió del grupo
            omitidos.append(f"{p['nombre']} ({p['cargo']} — {p['zona']})")
            continue
        validas.setdefault(p["correo"], p)
    # En un grupo de asesores de Outlook pero no en el Excel
    por_correo = {u["mail"].lower(): u for u in usuarios}
    solo_outlook = []
    for correo, zona in zona_grupo.items():
        if correo in validas:
            continue
        u = por_correo.get(correo, {})
        cargo = u.get("jobTitle") or "Asesor (grupo de Outlook)"
        tipo = _clasificar(cargo, zona)
        if tipo is None and not u.get("jobTitle"):
            tipo = "asesores"
        if not tipo:
            omitidos.append(f"{u.get('displayName', correo)} ({cargo}) — grupo {zona}")
            continue
        validas[correo] = {"tipo": tipo, "nombre": u.get("displayName", correo), "cargo": cargo, "zona": zona,
                           "correo": correo, "celular": re.sub(r"\D", "", u.get("mobilePhone") or "")}
        solo_outlook.append(f"{validas[correo]['nombre']} — {zona} — {cargo}")
    cuenta = {}
    with _lock:
        datos = _contactos()
        for tipo in ("administradores", "asesores"):
            nuevos = {c: p for c, p in validas.items() if p["tipo"] in (tipo, "ambos")}
            previos = {a.get("correo", "").lower(): a for a in datos[tipo]}
            manuales = [a for a in datos[tipo] if a.get("origen") not in ("outlook", "excel")
                        and a.get("correo", "").lower() not in validas]
            importados = []
            for p in nuevos.values():
                reg = {"nombre": p["nombre"], "correo": p["correo"], "celular": p["celular"],
                       "zona": p["zona"], "cargo": p["cargo"], "origen": "excel"}
                if previos.get(p["correo"], {}).get("asesores"):  # se conserva el amarre administrador → asesores
                    reg["asesores"] = previos[p["correo"]]["asesores"]
                importados.append(reg)
            datos[tipo] = sorted(manuales + importados, key=lambda x: (x.get("zona", ""), x.get("nombre", "")))
            cuenta[tipo] = len(importados)
        _guardar_contactos(datos)
    msg = (f"Excel + Outlook: {cuenta['administradores']} administradores y {cuenta['asesores']} asesores "
           f"({len(usuarios)} usuarios revisados en Outlook).")
    detalle = {t: [f"{p['nombre']} — {p['zona']} — {p['cargo']}" for p in validas.values() if p["tipo"] in (t, "ambos")]
               for t in ("administradores", "asesores")}
    detalle["hojas leídas del Excel"] = resumen
    detalle["agregados desde grupos de Outlook (no están en el Excel)"] = solo_outlook
    detalle["sin correo en Outlook (agrégalos a mano)"] = sin_correo
    detalle["no cargados (por regla o sin zona)"] = omitidos
    return msg, datos, detalle


@app.post("/api/contactos/sincronizar")
def sincronizar_contactos():
    """Asesores: grupos de Outlook (ASESORES CALI / COSTA / CENTRO).
    Administradores: nombres de FLETES buscados en Outlook (y grupos opcionales GRUPOS_ADMINISTRADORES)."""
    d = request.get_json(silent=True) or {}
    error = _error_clave(d.get("clave"))
    if error:
        return error
    if not CONTACTOS_EXCEL_URL:
        return jsonify(ok=False, error="Falta CONTACTOS_EXCEL_URL en el .env de pagina_solicitud (enlace del "
                                       "Excel 'Contactos Unispan' en OneDrive). Agrégalo y reinicia la página."), 400
    if CONTACTOS_EXCEL_URL:
        try:
            msg, datos, detalle = _sincronizar_desde_excel()
        except PermissionError as exc:
            return jsonify(ok=False, error=str(exc)), 403
        except Exception as exc:  # noqa: BLE001
            return jsonify(ok=False, error=f"No se pudo leer el Excel de contactos: {exc}"), 502
        return jsonify(ok=True, mensaje=msg, contactos=datos, detalle=detalle)
    tipo = d.get("tipo") or "asesores"
    if tipo not in ("asesores", "administradores"):
        return jsonify(ok=False, error="Tipo no válido."), 400
    faltantes = []
    try:
        if tipo == "asesores":
            vistos, faltantes = _miembros(_grupos_asesores())
        else:
            pares = [(g.strip().lower(), z.strip()) for g, _, z in
                     (x.partition("=") for x in GRUPOS_ADMINISTRADORES.split(";")) if z]
            vistos, faltantes = _miembros(pares) if pares else ({}, [])
            de_fletes, sin_usuario = _administradores_de_fletes()
            for c, v in de_fletes.items():
                vistos.setdefault(c, v)
            faltantes += sin_usuario
    except PermissionError as exc:
        return jsonify(ok=False, error=str(exc)), 403
    except Exception as exc:  # noqa: BLE001
        return jsonify(ok=False, error=f"No se pudo leer Outlook: {exc}"), 502

    with _lock:
        datos = _contactos()
        nuevos = actualizados = quitados = 0
        lista = []
        for a in datos[tipo]:
            c = a.get("correo", "").lower()
            if c in vistos:
                o = vistos.pop(c)
                a.update(nombre=o["nombre"], origen="outlook", celular=a.get("celular") or o["celular"],
                         zona=o["zona"] or a.get("zona", ""))
                actualizados += 1
                lista.append(a)
            elif a.get("origen") == "outlook" and tipo == "asesores":
                quitados += 1  # ya no está en ningún grupo
            else:
                lista.append(a)  # agregado a mano: se conserva
        for o in vistos.values():
            lista.append(o)
            nuevos += 1
        datos[tipo] = sorted(lista, key=lambda x: (x.get("zona", "") or "~", x.get("nombre", "")))
        _guardar_contactos(datos)
    sin_zona = sum(1 for x in datos[tipo] if not x.get("zona"))
    msg = f"{tipo.capitalize()} desde Outlook: {nuevos} nuevos, {actualizados} actualizados, {quitados} retirados."
    if sin_zona:
        msg += f" {sin_zona} sin zona: edítalos para asignarla."
    if faltantes:
        msg += f" No encontrados en Outlook: {', '.join(faltantes[:15])}{'…' if len(faltantes) > 15 else ''}."
    return jsonify(ok=True, mensaje=msg, contactos=datos)


_consultas_nit = defaultdict(deque)


def _agregar_correos(datos: dict):
    """Correos y celulares guardados por obra (página, sistema o catálogo del PC)."""
    guardados = _correos_obras()
    # En el sistema una obra puede estar a nombre de otra empresa del grupo (LAS ROSAS: FLETES → Bolívar S.A,
    # sistema → Bolívar Cali S.A): se buscan los correos en todos los NIT del grupo.
    nits = {datos["nit"]} | {o.get("nit") for o in datos["obras"] if o.get("nit")}
    del_nit = {}
    for k2, v in guardados.items():
        if "|" not in str(k2) or not isinstance(v, dict):
            continue
        n2, o2 = str(k2).split("|", 1)
        if n2 in nits:
            del_nit.setdefault(o2, v)
    for o in datos["obras"]:
        nit_o = o.get("nit") or datos["nit"]
        k = _clave_obra(nit_o, o["obra"])
        g = guardados.get(k) or del_nit.get(k.split("|", 1)[1])
        if not g:  # el nombre en el sistema puede variar ("826 AUSTRAL" ↔ "AUSTRAL")
            n = k.split("|", 1)[1]
            parecidas = [v for o2, v in del_nit.items() if n and (n in o2 or o2 in n)]
            g = parecidas[0] if len(parecidas) == 1 else {}
            if not g:  # mismas palabras en otro orden o con una letra distinta ("VALLEVERDE ALTOS" ↔ "ALTOS DE VALLEVERDE")
                parecidas = [v for o2, v in del_nit.items() if n and (catalogo._coincide(n, o2) or catalogo._coincide(o2, n))]
                g = parecidas[0] if len(parecidas) == 1 else {}
        g = g if isinstance(g, dict) else {}
        o["correos"] = [str(x) for x in (g.get("correos") or o.get("correos_guardados") or [])
                        if x and (not _es_interno(x) or operacion.es_prueba(o.get("obra")))]
        o["celulares"] = [str(x) for x in (g.get("celulares") or o.get("celulares_guardados") or []) if x]
        o.pop("correos_guardados", None)
        o.pop("celulares_guardados", None)


def _buscar_manual(cliente, obra):
    hallados = [v for k, v in _correos_obras().items()
                if str(k).startswith("MANUAL:") and isinstance(v, dict)
                and catalogo._coincide(cliente, v.get("cliente", "")) and catalogo._coincide(obra, v.get("obra", ""))]
    clientes = {catalogo.fc.normalizar(v.get("cliente", "")) for v in hallados}
    if not hallados or len(clientes) != 1:
        return None
    obras = [{"obra": v["obra"], "nit": "", "cliente": v["cliente"], "manual": True,
              "administrador": v.get("administrador", ""), "zona": v.get("zona", ""), "asesores": v.get("asesores") or [],
              "correos": v.get("correos") or [], "celulares": v.get("celulares") or []} for v in hallados]
    return {"nit": "", "cliente": hallados[0]["cliente"], "manual": True, "grupo": False,
            "obras": sorted(obras, key=lambda o: o["obra"]), "correos": []}


# ------------------------------------------------------------- verificación con código al correo del cliente
# Quien escribe un NIT (dato público) NO ve obras ni correos: se envía un código de 6 dígitos a los correos
# que el cliente ya tiene registrados, y solo con ese código se entregan los datos (4 horas en ese navegador).
CODIGO_A_PRUEBA = os.environ.get("CODIGO_A_PRUEBA", "1") == "1"
# 0 (por defecto): se entra solo con el NIT y los correos registrados se muestran TAPADOS (no se pueden ver,
# quitar ni cambiar; se usan igual para notificar). 1: hay que verificar con código al correo del cliente.
ACCESO_CON_CODIGO = os.environ.get("ACCESO_CON_CODIGO", "0") == "1"  # 1: el código le llega solo al coordinador
DOMINIO_INTERNO = os.environ.get("DOMINIO_INTERNO", "unispan.com.co").lower()
_verificaciones: dict[str, dict] = {}
_envios_codigo: dict[str, deque] = defaultdict(deque)


def _es_coordinador() -> bool:
    return float(session.get("coord") or 0) > time.time()


def _tiene_acceso(llave: str) -> bool:
    if _es_coordinador():
        return True
    return float((session.get("acceso") or {}).get(llave, 0)) > time.time()


def _tapar_datos(datos: dict) -> dict:
    """Copia para el público: sin correos ni celulares a la vista (solo tapados: j***@empresa.com)."""
    obras = []
    for o in datos.get("obras") or []:
        propios = [c for c in (o.get("correos") or [])
                   if not c.lower().endswith("@" + DOMINIO_INTERNO) or operacion.es_prueba(o.get("obra"))]
        obras.append({**o, "correos": [], "celulares": [], "correos_tapados": [_tapar(c) for c in propios]})
    return {**datos, "obras": obras, "correos": [], "tapados": True,
            "correos_tapados": [_tapar(c) for c in datos.get("correos") or []]}


def _tiene_basico(llave: str) -> bool:
    return float((session.get("basico") or {}).get(llave, 0)) > time.time()


def _correos_registrados(nit: str, obra: str) -> list:
    """Correos guardados (sistema / página) de esa obra; si no tiene, los aprobados del cliente."""
    datos = catalogo.buscar_nit(_nit_base(nit)) if catalogo.disponible() else None
    if not datos:
        return []
    datos = {**datos, "obras": [dict(o) for o in datos.get("obras") or []]}
    _agregar_correos(datos)
    n = lambda t: re.sub(r"[^A-Z0-9]+", " ", str(t or "").upper()).strip()  # noqa: E731
    o = next((x for x in datos["obras"] if n(x.get("obra")) == n(obra)), None)
    lista = (o or {}).get("correos") or list(datos.get("correos") or [])
    return [c for c in lista if RE_EMAIL.match(c)]


def _dar_acceso(llaves, pendiente: str = "", basico: bool = False):
    clave = "pendiente" if pendiente else ("basico" if basico else "acceso")
    acceso = {k: v for k, v in (session.get(clave) or {}).items()
              if float(v[1] if isinstance(v, list) else v) > time.time()}
    for k in llaves:
        acceso[k] = [pendiente, time.time() + 4 * 3600] if pendiente else time.time() + 4 * 3600
    session.permanent = True
    session[clave] = acceso


def _correo_pendiente(llave: str) -> str:
    """Correo verificado por el usuario pero aún no aprobado por el coordinador (o '' si no hay)."""
    v = (session.get("pendiente") or {}).get(llave)
    if not v or float(v[1]) < time.time():
        return ""
    estado = ((_verificados().get(llave) or {}).get(v[0]) or {}).get("estado")
    return "" if estado == "rechazado" else v[0]


def _tapar(correo: str) -> str:
    usuario, _, dominio = correo.partition("@")
    return (usuario[:1] + "***@" + dominio) if dominio else "***"


def _correos_del_cliente(datos: dict) -> list:
    """Correos ya registrados del cliente (aprobados + guardados por obra), sin los internos de UNISPAN."""
    todos = list(datos.get("correos") or [])
    for o in datos.get("obras") or []:
        todos += list(o.get("correos") or [])
    ver = _verificados()
    for k in _llaves(datos):
        todos += [c for c, x in (ver.get(k) or {}).items() if x.get("estado") == "aprobado"]
    todos = list(dict.fromkeys(c.strip().lower() for c in todos if c and RE_EMAIL.match(c.strip())))
    return [c for c in todos if not c.endswith("@" + DOMINIO_INTERNO)]


def _llaves(datos: dict) -> list:
    if datos.get("manual"):
        return [_clave_manual(o.get("cliente") or datos["cliente"], o["obra"]) for o in datos.get("obras") or []]
    return list(dict.fromkeys([_nit_base(datos["nit"])] + [_nit_base(o["nit"]) for o in datos.get("obras") or []
                                                         if o.get("nit")]))


def _enviar_codigo(destinos: list, codigo: str, cliente: str):
    cuerpo = ("<p>Tu código para la página de solicitudes de devolución de UNISPAN es:</p>"
              f"<p style='font-size:26px;font-weight:bold;letter-spacing:6px'>{codigo}</p>"
              "<p>Vence en 10 minutos. Si no lo pediste, ignora este correo.</p>")
    buzon = os.environ["MAILBOX_USER"]
    if CODIGO_A_PRUEBA:  # pruebas: solo le llega al coordinador, con la lista de a quién le llegaría
        cuerpo = (f"<p><b>PRUEBA Y VERIFICACIÓN</b> — en producción este código iría a: "
                  f"{html.escape(', '.join(destinos))} ({html.escape(cliente)}).</p>" + cuerpo)
        _enviar_al_buzon(f"[Código página] {cliente}", cuerpo, buzon, _carpeta_avisos())
        return
    r = requests.post(f"https://graph.microsoft.com/v1.0/users/{buzon}/sendMail",
                      headers={"Authorization": f"Bearer {_token_graph()}"}, timeout=30,
                      json={"message": {"subject": "Código de verificación — Devoluciones UNISPAN",
                                        "body": {"contentType": "HTML", "content": cuerpo},
                                        "toRecipients": [{"emailAddress": {"address": d}} for d in destinos[:10]]},
                            "saveToSentItems": False})
    if not r.ok:
        raise RuntimeError(f"sendMail {r.status_code}: {r.text[:200]}")


def _entregar_o_verificar(datos: dict, ip: str):
    """Coordinador o navegador ya verificado → datos completos. Si no → se envía el código."""
    if not datos.get("manual"):  # las obras manuales ya traen sus correos
        _agregar_correos(datos)
        _agregar_asignaciones(datos)
    llaves = _llaves(datos)
    if llaves and all(_tiene_acceso(k) for k in llaves):
        return jsonify(ok=True, **datos)
    if not ACCESO_CON_CODIGO:
        _dar_acceso(llaves, basico=True)
        return jsonify(ok=True, **_tapar_datos(datos))
    ctx = _nuevo_contexto(datos, llaves, ip)  # permite pedir el código a "mi correo" (ver /api/codigo-correo)
    destinos = _correos_del_cliente(datos)
    if not destinos:
        return jsonify(ok=False, sin_correo=True, ctx=ctx,
                       error="Este cliente aún no tiene correos registrados. Escribe tu correo corporativo: te "
                             "enviamos un código y el coordinador aprueba tu correo."), 409
    ahora = time.time()
    q = _envios_codigo[ip]
    while q and ahora - q[0] > 3600:
        q.popleft()
    if len(q) >= 6:
        return jsonify(ok=False, error="Se enviaron demasiados códigos desde este equipo. Intenta en una hora."), 429
    q.append(ahora)
    for k in [k for k, v in _verificaciones.items() if v["vence"] < ahora]:
        _verificaciones.pop(k, None)
    codigo = f"{secrets.randbelow(10 ** 6):06d}"
    vid = secrets.token_urlsafe(18)
    _verificaciones[vid] = {"hash": hashlib.sha256((vid + codigo).encode()).hexdigest(), "vence": ahora + 600,
                            "intentos": 0, "ip": ip, "datos": datos, "llaves": llaves}
    try:
        _enviar_codigo(destinos, codigo, datos.get("cliente", ""))
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR enviando código: {exc}", flush=True)
        return jsonify(ok=False, error="No pudimos enviar el código. Intenta de nuevo en un momento."), 502
    return jsonify(ok=False, verificar=True, vid=vid, ctx=ctx, destinos=[_tapar(c) for c in destinos[:5]],
                   prueba=CODIGO_A_PRUEBA)


@app.post("/api/verificar")
def verificar_codigo():
    d = request.get_json(silent=True) or {}
    ip = seguridad.ip_cliente(request)
    vid = str(d.get("vid") or "")
    v = _verificaciones.get(vid)
    if not v or v["vence"] < time.time() or v["ip"] != ip:
        return jsonify(ok=False, vencido=True, error="El código venció. Vuelve a buscar para recibir uno nuevo."), 410
    codigo = re.sub(r"\D", "", str(d.get("codigo") or ""))
    if not hmac.compare_digest(hashlib.sha256((vid + codigo).encode()).hexdigest(), v["hash"]):
        v["intentos"] += 1
        if v["intentos"] >= 5:
            _verificaciones.pop(vid, None)
        restantes, bloqueado = seguridad.registrar_fallo(ip, "nit", "código incorrecto")
        if bloqueado:
            _alerta_bloqueo(ip)
            return jsonify(ok=False, bloqueado=True,
                           error="Superaste los intentos permitidos: la página quedó bloqueada."), 423
        return jsonify(ok=False, error=f"Código incorrecto. Intentos restantes: {restantes}."), 403
    _verificaciones.pop(vid, None)
    seguridad.registrar_exito(ip, "nit")
    propio = v.get("propio")
    if propio and not v.get("dominio_ok"):
        # correo verificado (es suyo) pero de un dominio que no es del cliente: queda POR APROBAR.
        for k in v["llaves"]:
            _guardar_verificado(k, propio, "pendiente", v["datos"].get("cliente", ""))
        _dar_acceso(v["llaves"], pendiente=propio)
        _pedir_aprobacion(v["llaves"], propio, v["datos"].get("cliente", ""), ip)
        limpio = {**v["datos"], "correos": [],
                  "obras": [{**o, "correos": [], "celulares": []} for o in v["datos"].get("obras") or []]}
        return jsonify(ok=True, pendiente=True, correo_propio=propio, **limpio)
    if propio:  # dominio corporativo del cliente: queda aprobado de una vez
        for k in v["llaves"]:
            _guardar_verificado(k, propio, "aprobado", v["datos"].get("cliente", ""))
    _dar_acceso(v["llaves"])
    return jsonify(ok=True, **v["datos"])


# Correos que el propio cliente verificó en la página (aprobados o por aprobar por el coordinador)
VERIFICADOS_PATH = os.path.join(DATA_DIR, "correos_verificados.json")
PUBLICOS = {"gmail.com", "hotmail.com", "hotmail.es", "outlook.com", "outlook.es", "live.com", "yahoo.com",
            "yahoo.es", "icloud.com", "msn.com", "aol.com", "protonmail.com", "proton.me"}
_contextos: dict[str, dict] = {}


def _nuevo_contexto(datos, llaves, ip) -> str:
    ahora = time.time()
    for k in [k for k, c in _contextos.items() if c["vence"] < ahora]:
        _contextos.pop(k, None)
    ctx = secrets.token_urlsafe(18)
    _contextos[ctx] = {"datos": datos, "llaves": llaves, "ip": ip, "vence": ahora + 1800}
    return ctx


def _verificados() -> dict:
    try:
        with open(VERIFICADOS_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return {}


def _guardar_verificado(llave, correo, estado, cliente=""):
    with _lock:
        d = _verificados()
        d.setdefault(llave, {})[correo] = {"estado": estado, "cliente": cliente,
                                          "fecha": time.strftime("%Y-%m-%d %H:%M")}
        os.makedirs(DATA_DIR, exist_ok=True)
        tmp = VERIFICADOS_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        os.replace(tmp, VERIFICADOS_PATH)
        almacen.guardado(VERIFICADOS_PATH)


def _dominio(correo: str) -> str:
    return correo.rsplit("@", 1)[-1].lower()


@app.post("/api/codigo-correo")
def codigo_a_mi_correo():
    """El cliente no tiene acceso a los correos registrados (o no hay): escribe SU correo y se le envía el
    código. Si el dominio es el de la empresa del cliente, queda aprobado; si no, queda por aprobar."""
    d = request.get_json(silent=True) or {}
    ip = seguridad.ip_cliente(request)
    c = _contextos.get(str(d.get("ctx") or ""))
    if not c or c["vence"] < time.time() or c["ip"] != ip:
        return jsonify(ok=False, error="La búsqueda venció. Vuelve a escribir el NIT."), 410
    correo = _texto(d.get("correo"), 120).lower()
    if not RE_EMAIL.match(correo):
        return jsonify(ok=False, error="Escribe un correo válido."), 400
    if correo.endswith("@" + DOMINIO_INTERNO):
        return jsonify(ok=False, error="Usa el correo de tu empresa (no uno de UNISPAN)."), 400
    conocidos = _correos_del_cliente(c["datos"])
    dominios = {_dominio(x) for x in conocidos} - PUBLICOS
    dominio_ok = correo in conocidos or _dominio(correo) in dominios
    ahora = time.time()
    q = _envios_codigo[ip]
    while q and ahora - q[0] > 3600:
        q.popleft()
    if len(q) >= 6:
        return jsonify(ok=False, error="Se enviaron demasiados códigos desde este equipo. Intenta en una hora."), 429
    q.append(ahora)
    codigo = f"{secrets.randbelow(10 ** 6):06d}"
    vid = secrets.token_urlsafe(18)
    _verificaciones[vid] = {"hash": hashlib.sha256((vid + codigo).encode()).hexdigest(), "vence": ahora + 600,
                            "intentos": 0, "ip": ip, "datos": c["datos"], "llaves": c["llaves"],
                            "propio": correo, "dominio_ok": dominio_ok}
    try:
        _enviar_codigo([correo], codigo, c["datos"].get("cliente", ""))
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR enviando código: {exc}", flush=True)
        return jsonify(ok=False, error="No pudimos enviar el código. Intenta de nuevo en un momento."), 502
    return jsonify(ok=False, verificar=True, vid=vid, ctx=d.get("ctx"), destinos=[_tapar(correo)],
                   aprobacion=not dominio_ok, prueba=CODIGO_A_PRUEBA)


# ---- aprobación del coordinador con un enlace firmado (POST con botón: los antivirus que "abren" enlaces no aprueban)
def _firma(texto: str) -> str:
    return hmac.new(app.secret_key.encode(), texto.encode(), hashlib.sha256).hexdigest()[:32]


def _token_aprobacion(llaves, correo, cliente) -> str:
    carga = base64.urlsafe_b64encode(json.dumps({"l": llaves, "c": correo, "n": cliente,
                                                 "e": int(time.time()) + 7 * 86400}).encode()).decode()
    return carga + "." + _firma(carga)


def _leer_token(token: str):
    carga, _, firma = str(token).partition(".")
    if not carga or not hmac.compare_digest(_firma(carga), firma):
        return None
    try:
        d = json.loads(base64.urlsafe_b64decode(carga.encode()).decode())
    except Exception:  # noqa: BLE001
        return None
    return d if d.get("e", 0) > time.time() else None


def _pedir_aprobacion(llaves, correo, cliente, ip):
    enlace = request.host_url.rstrip("/") + "/aprobar/" + _token_aprobacion(llaves, correo, cliente)
    _notificar_coordinador(
        f"[Aprobar correo página] {correo} — {cliente}",
        "<p>Un usuario verificó este correo en la página de devoluciones, pero su dominio no es uno de los "
        "registrados para el cliente. Sus solicitudes llegan marcadas <b>CORREO POR APROBAR</b> y el bot no las "
        "programa hasta que lo apruebes.</p>"
        + _tabla_html([("Correo", correo), ("Cliente", cliente), ("NIT / clave", ", ".join(llaves)), ("Equipo (IP)", ip)])
        + f"<p><a href='{html.escape(enlace)}' style='background:#0a7a3e;color:#fff;padding:10px 16px;"
          f"border-radius:6px;text-decoration:none;font-weight:bold'>Revisar y aprobar / rechazar</a></p>"
          "<p style='color:#888;font-size:12px'>El enlace vence en 7 días.</p>")


def _pagina_simple(titulo, cuerpo):
    return (f"<!doctype html><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{html.escape(titulo)}</title><body style='font-family:Segoe UI,Arial;max-width:560px;margin:40px auto;"
            f"padding:0 16px;color:#14213d'><h2>{html.escape(titulo)}</h2>{cuerpo}</body>")


@app.get("/aprobar/<token>")
def aprobar_ver(token):
    t = _leer_token(token)
    if not t:
        return _pagina_simple("Enlace no válido", "<p>El enlace venció o no es válido.</p>"), 410
    estado = {(_verificados().get(k) or {}).get(t["c"], {}).get("estado") for k in t["l"]}
    return _pagina_simple("Aprobar correo de cliente",
        f"<p><b>{html.escape(t['c'])}</b> para <b>{html.escape(t['n'])}</b> ({html.escape(', '.join(t['l']))}).</p>"
        f"<p>Estado actual: <b>{html.escape(', '.join(x or 'sin registro' for x in estado))}</b></p>"
        "<form method='post'><button name='accion' value='aprobar' style='padding:10px 18px;background:#0a7a3e;"
        "color:#fff;border:0;border-radius:6px;font-weight:bold'>Aprobar</button> "
        "<button name='accion' value='rechazar' style='padding:10px 18px;background:#b42318;color:#fff;border:0;"
        "border-radius:6px'>Rechazar</button></form>")


@app.post("/aprobar/<token>")
def aprobar_guardar(token):
    t = _leer_token(token)
    if not t:
        return _pagina_simple("Enlace no válido", "<p>El enlace venció o no es válido.</p>"), 410
    aprobar = request.form.get("accion") == "aprobar"
    for k in t["l"]:
        _guardar_verificado(k, t["c"], "aprobado" if aprobar else "rechazado", t["n"])
    if aprobar:
        try:
            cuerpo = ("<p>Tu correo quedó <b>aprobado</b> en la página de solicitudes de devolución de UNISPAN para "
                      f"{html.escape(t['n'])}. Ya puedes usarla con tu NIT; el código te llegará a este correo.</p>")
            if CODIGO_A_PRUEBA:
                _enviar_al_buzon(f"[Código página] Aprobado {t['c']}", "<p><b>PRUEBA</b> — iría a "
                                 f"{html.escape(t['c'])}</p>" + cuerpo, os.environ["MAILBOX_USER"], _carpeta_avisos())
            else:
                requests.post(f"https://graph.microsoft.com/v1.0/users/{os.environ['MAILBOX_USER']}/sendMail",
                              headers={"Authorization": f"Bearer {_token_graph()}"}, timeout=30,
                              json={"message": {"subject": "Correo aprobado — Devoluciones UNISPAN",
                                                "body": {"contentType": "HTML", "content": cuerpo},
                                                "toRecipients": [{"emailAddress": {"address": t["c"]}}]},
                                    "saveToSentItems": False})
        except Exception as exc:  # noqa: BLE001
            print(f"AVISO: no se avisó la aprobación a {t['c']} ({exc})", flush=True)
    return _pagina_simple("Listo", f"<p>{html.escape(t['c'])} quedó <b>{'APROBADO' if aprobar else 'RECHAZADO'}</b>.</p>")


@app.post("/api/buscar-obra")
def buscar_obra_por_nombre():
    """Sin NIT: constructora + obra. Las búsquedas sin resultado cuentan como intento fallido."""
    if not catalogo.disponible():
        return jsonify(ok=False, error="Catálogo no configurado."), 503
    if not catalogo.listo():
        return jsonify(ok=False, cargando=True, error="Cargando clientes y obras. Intenta en 1 minuto."), 503
    d = request.get_json(silent=True) or {}
    ip = seguridad.ip_cliente(request)
    datos, motivo = catalogo.buscar_por_nombre(_texto(d.get("cliente"), 120), _texto(d.get("obra"), 120))
    if not datos:  # ¿la registró antes a mano? queda amarrada a sus correos, administrador y zona
        datos = _buscar_manual(_texto(d.get("cliente"), 120), _texto(d.get("obra"), 120))
        if datos:
            return _entregar_o_verificar(datos, ip)
    if not datos:
        restantes, bloqueado = seguridad.registrar_fallo(ip, "nit", f"nombre: {d.get('cliente')} / {d.get('obra')}"[:60])
        if bloqueado:
            _alerta_bloqueo(ip)
            return jsonify(ok=False, bloqueado=True, error="Superaste los intentos permitidos: la página quedó bloqueada."), 423
        return jsonify(ok=False, restantes=restantes, error=f"{motivo} Intentos restantes: {restantes}."), 404
    return _entregar_o_verificar(datos, ip)  # el contador de fallos se limpia solo con el código correcto


@app.get("/api/nit/<nit>")
def consultar_nit(nit):
    """Datos del cliente por NIT COMPLETO: nombre, obras y correos aprobados."""
    if not catalogo.disponible():
        return jsonify(ok=False, error="Catálogo no configurado (falta QUANTIFY_URL)."), 503
    ip = seguridad.ip_cliente(request)
    q, ahora = _consultas_nit[ip], time.time()
    while q and ahora - q[0] > 600:
        q.popleft()
    if len(q) >= 40:
        return jsonify(ok=False, error="Demasiadas consultas. Intenta en unos minutos."), 429
    q.append(ahora)
    if not catalogo.listo():  # recién arrancó: no se cuenta como intento fallido
        return jsonify(ok=False, cargando=True,
                       error="Cargando la información de clientes y obras. Intenta de nuevo en 1 minuto."), 503
    datos = catalogo.buscar_nit(nit)
    if not datos:
        restantes, bloqueado = seguridad.registrar_fallo(ip, "nit", re.sub(r"\D", "", nit)[:15])
        if bloqueado:
            _alerta_bloqueo(ip)
            return jsonify(ok=False, bloqueado=True, restantes=0,
                           error="NIT no encontrado. Superaste los intentos permitidos: la página quedó bloqueada."), 423
        return jsonify(ok=False, restantes=restantes,
                       error=f"NIT no encontrado. Escríbelo completo, sin puntos. Intentos restantes: {restantes}."), 404
    return _entregar_o_verificar(datos, ip)  # el contador de fallos se limpia solo con el código correcto


@app.put("/api/obra-correos")
def actualizar_correos_obra():
    """Agregar / quitar / cambiar los correos y celulares del cliente para una obra."""
    d = request.get_json(silent=True) or {}
    ip = seguridad.ip_cliente(request)
    if _limite_excedido(ip):
        return jsonify(ok=False, error="Demasiados cambios seguidos. Intenta en unos minutos."), 429
    nit, obra = re.sub(r"\D", "", _texto(d.get("nit"), 20)), _texto(d.get("obra"))
    cliente = _texto(d.get("cliente")) if d.get("manual") and not nit else ""
    correos, celulares = _lista_correos(d.get("correos")), _lista_celulares(d.get("celulares"))
    if not obra or not (nit or cliente):
        return jsonify(ok=False, error="Primero elige el NIT (o la constructora) y la obra."), 400
    if nit and catalogo.disponible() and not catalogo.buscar_nit(nit):
        return jsonify(ok=False, error="NIT no encontrado."), 404
    llave = _nit_base(nit) if nit else _clave_manual(cliente, obra)
    if nit and not _tiene_acceso(llave) and _tiene_basico(llave):
        correos = list(dict.fromkeys(_correos_registrados(nit, obra) + correos))  # agrega, no quita
    elif not _tiene_acceso(llave) and (nit or llave in _correos_obras()):
        return jsonify(ok=False, error="Primero busca el NIT del cliente."), 403
    malos = [c for c in correos if not RE_EMAIL.match(c)]
    if malos:
        return jsonify(ok=False, error=f"Correos no válidos: {', '.join(malos)}"), 400
    _guardar_correos_obra(nit, obra, correos, celulares, cliente=cliente)
    if nit and not _tiene_acceso(llave):  # al público se le responde tapado
        return jsonify(ok=True, correos=[], correos_tapados=[_tapar(c) for c in correos
                                                                  if not c.lower().endswith("@" + DOMINIO_INTERNO)],
                       celulares=[])
    return jsonify(ok=True, correos=correos, celulares=celulares)


@app.post("/api/solicitud")
def recibir_solicitud():
    payload = request.get_json(silent=True) or {}
    if payload.get("zz_ctrl"):  # campo trampa para bots
        return jsonify(ok=True, enviados=0)
    ip = seguridad.ip_cliente(request)
    if _limite_excedido(ip):
        return jsonify(ok=False, errores=["Demasiados envíos seguidos. Intenta en unos minutos."]), 429

    for r in payload.get("registros") or []:
        if isinstance(r, dict) and r.get("nit") and not _tiene_acceso(_nit_base(r["nit"])) \
                and _tiene_basico(_nit_base(r["nit"])):
            nuevos = _lista_correos(r.get("correos_clientes"))
            r["correos_clientes"] = "; ".join(dict.fromkeys(_correos_registrados(r["nit"], r.get("obra")) + nuevos))
    cabecera, registros, errores = _validar(payload)
    sin_acceso = []
    for r in registros:
        if not r.get("nit") or _tiene_acceso(_nit_base(r["nit"])) or _tiene_basico(_nit_base(r["nit"])):
            continue
        pendiente = _correo_pendiente(_nit_base(r["nit"]))
        if pendiente:
            r["correo_por_aprobar"] = pendiente  # el bot no la programa hasta que el coordinador apruebe
        else:
            sin_acceso.append(r["obra"])
    if sin_acceso:
        errores.append("Verifica el NIT con el código enviado al correo antes de enviar (obras: "
                       + ", ".join(sin_acceso) + ").")
    if errores:
        return jsonify(ok=False, errores=errores), 400

    enviados = 0
    try:
        for reg in registros:
            asunto, cuerpo = _correo_registro(cabecera, reg)
            _enviar_al_buzon(asunto, cuerpo, reg["clientes"][0])
            if reg.get("correo_por_aprobar"):
                enviados += 1  # correo aún no aprobado: no cambia los correos guardados de la obra
                continue
            if not reg.get("nit") and not _tiene_acceso(_clave_manual(reg["cliente"], reg["obra"])) \
                    and _clave_manual(reg["cliente"], reg["obra"]) in _correos_obras():
                enviados += 1  # obra manual ya registrada por otro: no se cambian sus correos sin verificar
                continue
            _guardar_correos_obra(reg.get("nit"), reg["obra"], reg["clientes"], reg["celulares_clientes"],
                                  cliente=reg["cliente"],
                                  extra={"administrador": (cabecera.get("contacto_administrador") or {}).get("nombre", ""),
                                         "zona": cabecera.get("zona"), "asesores": cabecera.get("asesores")})
            enviados += 1
    except Exception as exc:  # noqa: BLE001
        app.logger.error("Fallo enviando solicitud: %s", exc)
        print(f"ERROR enviando solicitud: {exc}", flush=True)
        return jsonify(
            ok=False,
            enviados=enviados,
            errores=["No pudimos enviar la solicitud. Intenta de nuevo o escríbenos por correo."],
        ), 502
    return jsonify(ok=True, enviados=enviados)


@app.get("/api/contactos")
def listar_contactos():
    datos = _contactos()
    if _es_coordinador():
        return jsonify(datos)
    # al público: nombre, correo, zona y amarres (lo que la página necesita); sin celulares ni otros datos
    publico = {}
    for tipo, lista in datos.items():
        if isinstance(lista, list):
            publico[tipo] = [{k: v for k, v in c.items() if k not in ("celular", "telefono", "cedula")}
                             if isinstance(c, dict) else c for c in lista]
        else:
            publico[tipo] = lista
    return jsonify(publico)


# ------------------------------------------------------------ amarres del coordinador
# 1) obra → administrador de proyectos (para obras sin administrador en FLETES o para corregirlo)
# 2) administrador → asesores (por zona y por administrador); se cargan solos en cada solicitud.
ASIGNACIONES_PATH = os.path.join(DATA_DIR, "asignaciones_obras.json")


def _asignaciones() -> dict:
    try:
        with open(ASIGNACIONES_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return {}


def _agregar_asignaciones(datos: dict):
    """o['admin_asignado'] = el que amarró el coordinador; si la obra no tiene administrador en FLETES,
    o['admin_sugerido'] = el administrador más frecuente en las demás obras del cliente."""
    asig = _asignaciones()
    conteo: dict = {}
    for o in datos.get("obras") or []:
        if o.get("administrador"):
            conteo[o["administrador"]] = conteo.get(o["administrador"], 0) + 1
    sugerido = max(conteo, key=conteo.get) if conteo else ""
    for o in datos.get("obras") or []:
        a = asig.get(_clave_obra(o.get("nit") or datos.get("nit"), o.get("obra")))
        if a:
            o["admin_asignado"] = {"correo": a.get("correo"), "nombre": a.get("nombre"), "zona": a.get("zona")}
        elif not o.get("administrador") and sugerido:
            o["admin_sugerido"] = sugerido


def _es_coord_req(d) -> bool:
    return _es_coordinador() or (d.get("clave") and _error_clave(d.get("clave")) is None)


@app.post("/api/obra-admin")
def amarrar_obra_admin():
    d = request.get_json(silent=True) or {}
    if not _es_coord_req(d):
        return jsonify(ok=False, error="Solo el coordinador puede amarrar administradores."), 403
    nit, obra = _nit_base(d.get("nit")), _texto(d.get("obra"))
    correo = _texto(d.get("correo"), 120).lower()
    if not nit or not obra:
        return jsonify(ok=False, error="Falta el NIT o la obra."), 400
    with _lock:
        asig = _asignaciones()
        k = _clave_obra(nit, obra)
        if not correo:
            asig.pop(k, None)
        else:
            a = next((c for c in _contactos()["administradores"] if c["correo"].lower() == correo), None)
            if not a:
                return jsonify(ok=False, error="Ese administrador no está en los contactos."), 400
            asig[k] = {"obra": obra, "correo": a["correo"], "nombre": a["nombre"], "zona": a.get("zona", ""),
                       "fecha": time.strftime("%Y-%m-%d %H:%M")}
        os.makedirs(DATA_DIR, exist_ok=True)
        tmp = ASIGNACIONES_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(asig, f, ensure_ascii=False, indent=1)
        os.replace(tmp, ASIGNACIONES_PATH)
        almacen.guardado(ASIGNACIONES_PATH)
    return jsonify(ok=True)


@app.post("/api/admin-asesores")
def amarrar_admin_asesores():
    d = request.get_json(silent=True) or {}
    if not _es_coord_req(d):
        return jsonify(ok=False, error="Solo el coordinador puede amarrar asesores."), 403
    correo = _texto(d.get("correo"), 120).lower()
    asesores = [str(x).lower() for x in (d.get("asesores") or []) if RE_EMAIL.match(str(x))][:40]
    with _lock:
        datos = _contactos()
        a = next((c for c in datos["administradores"] if c["correo"].lower() == correo), None)
        if not a:
            return jsonify(ok=False, error="Administrador no encontrado."), 404
        a["asesores"] = asesores
        _guardar_contactos(datos)
    return jsonify(ok=True, contactos=datos)


@app.post("/api/contactos")
def agregar_contacto():
    d = request.get_json(silent=True) or {}
    error = _error_clave(d.get("clave"))
    if error:
        return error
    tipo = d.get("tipo")
    nombre, correo, zona = _texto(d.get("nombre"), 80), _texto(d.get("correo"), 120).lower(), _texto(d.get("zona"), 30)
    celular = re.sub(r"[^\d+ ]", "", _texto(d.get("celular"), 30)).strip()
    original = _texto(d.get("correo_original"), 120).lower()  # al editar: correo anterior
    if tipo not in TIPOS:
        return jsonify(ok=False, error="Tipo no válido."), 400
    if not nombre or not RE_EMAIL.match(correo):
        return jsonify(ok=False, error="Nombre y correo válido son obligatorios."), 400
    if TIPOS[tipo] and zona not in ZONAS:
        return jsonify(ok=False, error="Elige la zona."), 400
    with _lock:
        datos = _contactos()
        if correo != original and any(c["correo"].lower() == correo for c in datos[tipo]):
            return jsonify(ok=False, error="Ya existe un contacto con ese correo."), 400
        quitar = {correo, original}
        anterior = next((c for c in datos[tipo] if c["correo"].lower() in quitar), {})
        datos[tipo] = [c for c in datos[tipo] if c["correo"].lower() not in quitar]  # editar = reemplazar
        nuevo = {k: v for k, v in anterior.items() if k in ("origen", "cargo", "asesores")}
        nuevo.update(nombre=nombre, correo=correo)
        if tipo == "administradores" and isinstance(d.get("asesores"), list):
            nuevo["asesores"] = [x.lower() for x in d["asesores"] if RE_EMAIL.match(str(x))][:30]
        if celular:
            nuevo["celular"] = celular
        if TIPOS[tipo]:
            nuevo["zona"] = zona
        datos[tipo].append(nuevo)
        datos[tipo].sort(key=lambda c: c["nombre"].lower())
        _guardar_contactos(datos)
    return jsonify(ok=True, contactos=datos)


@app.delete("/api/contactos")
def eliminar_contacto():
    d = request.get_json(silent=True) or {}
    error = _error_clave(d.get("clave"))
    if error:
        return error
    tipo, correo = d.get("tipo"), _texto(d.get("correo"), 120).lower()
    if tipo not in TIPOS:
        return jsonify(ok=False, error="Tipo no válido."), 400
    with _lock:
        datos = _contactos()
        datos[tipo] = [c for c in datos[tipo] if c["correo"].lower() != correo]
        _guardar_contactos(datos)
    return jsonify(ok=True, contactos=datos)


# ------------------------------------------------------------- alertas y bloqueos
def _destinos_coordinador() -> list:
    d = [c["correo"] for c in _contactos().get("programadores", []) if c.get("correo")]
    d += [x.strip() for x in os.environ.get("NOTIFICAR_A", "").replace(";", ",").split(",") if x.strip()]
    return list(dict.fromkeys(x.lower() for x in d))


def _notificar_coordinador(asunto: str, html_cuerpo: str):
    """Correo al coordinador en segundo plano (no demora la respuesta de la página)."""
    def enviar():
        buzon = os.environ.get("MAILBOX_USER", "").lower()
        for dest in _destinos_coordinador():
            try:
                if dest == buzon:  # a sí mismo: se deja en la carpeta de avisos (sendMail se pierde)
                    _enviar_al_buzon(asunto, html_cuerpo, buzon, _carpeta_avisos())
                    continue
                r = requests.post(f"https://graph.microsoft.com/v1.0/users/{buzon}/sendMail",
                                  headers={"Authorization": f"Bearer {_token_graph()}"}, timeout=30,
                                  json={"message": {"subject": asunto,
                                                    "body": {"contentType": "HTML", "content": html_cuerpo},
                                                    "toRecipients": [{"emailAddress": {"address": dest}}]},
                                        "saveToSentItems": False})
                if not r.ok:
                    print(f"AVISO alerta a {dest}: {r.status_code} {r.text[:150]}", flush=True)
            except Exception as exc:  # noqa: BLE001
                print(f"AVISO alerta a {dest}: {exc}", flush=True)
    threading.Thread(target=enviar, daemon=True).start()


def _tabla_html(filas) -> str:
    return "<table>" + "".join(
        f"<tr><td style='padding:3px 10px;color:#555'>{html.escape(str(k))}</td>"
        f"<td style='padding:3px 10px'><b>{html.escape(str(v or '—'))}</b></td></tr>" for k, v in filas) + "</table>"


def _alerta_bloqueo(ip: str):
    b = seguridad.bloqueo(ip) or {}
    _notificar_coordinador(
        f"[ALERTA] Página de devoluciones bloqueada — equipo {ip}",
        "<p>La página de solicitudes se bloqueó por intentos fallidos.</p>"
        + _tabla_html([("Equipo (IP)", ip), ("Motivo", b.get("motivo")), ("Desde", b.get("desde")),
                       ("Intentos", " | ".join(b.get("intentos", [])))])
        + "<p>Para habilitarlo: en la página, botón + de Programadores → <b>Ver bloqueos</b> → Habilitar.</p>")


@app.post("/api/coordinador")
def acceso_coordinador():
    d = request.get_json(silent=True) or {}
    if d.get("salir"):
        session.pop("coord", None)
        return jsonify(ok=True)
    error = _error_clave(d.get("clave"))
    if error:
        return error
    session.permanent = True
    session["coord"] = time.time() + 8 * 3600
    return jsonify(ok=True)


@app.get("/api/catalogo/estado")
def estado_catalogo():
    e = catalogo.estado
    return jsonify(listo=catalogo.listo(), progreso=e["progreso"], etapa=e["etapa"], error=e["error"],
                   almacen=almacen.estado if almacen.activo() and _es_coordinador() else None)


@app.get("/api/estado")
def estado():
    b = seguridad.bloqueo(seguridad.ip_cliente(request))
    return jsonify(bloqueado=bool(b), motivo=(b or {}).get("motivo"), desde=(b or {}).get("desde"),
                   solicitudes=len((b or {}).get("solicitudes", [])))


@app.post("/api/desbloqueo")
def solicitar_desbloqueo():
    ip = seguridad.ip_cliente(request)
    if not seguridad.bloqueo(ip):
        return jsonify(ok=True, mensaje="La página no está bloqueada para este equipo.")
    d = request.get_json(silent=True) or {}
    sol = {"nombre": _texto(d.get("nombre"), 80), "empresa": _texto(d.get("empresa"), 120),
           "nit": re.sub(r"\D", "", _texto(d.get("nit"), 20)), "correo": _texto(d.get("correo"), 120).lower(),
           "celular": _texto(d.get("celular"), 30), "mensaje": _texto(d.get("mensaje"), 500)}
    if not sol["nombre"] or not RE_EMAIL.match(sol["correo"]) or not sol["empresa"]:
        return jsonify(ok=False, error="Nombre, empresa y un correo válido son obligatorios."), 400
    if not seguridad.agregar_solicitud(ip, sol):
        return jsonify(ok=False, error="Ya enviaste el máximo de solicitudes. El coordinador te contactará."), 429
    _notificar_coordinador(
        f"[Desbloqueo] Solicitud de habilitación de la página — {sol['empresa']}",
        "<p>Una persona pide habilitar la página de solicitudes de devolución.</p>"
        + _tabla_html([("Equipo (IP)", ip), *[(k.capitalize(), v) for k, v in sol.items()]])
        + "<p>Para habilitarlo: en la página, botón + de Programadores → <b>Ver bloqueos</b> → Habilitar.</p>")
    return jsonify(ok=True, mensaje="Solicitud enviada al coordinador. Te avisaremos cuando la página esté habilitada.")


@app.post("/api/bloqueos")
def ver_bloqueos():
    d = request.get_json(silent=True) or {}
    error = _error_clave(d.get("clave"))
    if error:
        return error
    if d.get("habilitar"):
        ip = seguridad.ip_cliente(request) if d["habilitar"] == "este" else _texto(d["habilitar"], 60)
        seguridad.habilitar(ip)
    return jsonify(ok=True, bloqueos=seguridad.listar())


# ------------------------------------------------------------- reasignación de obras
@app.post("/api/reasignaciones")
def reasignaciones():
    """Obras de un administrador (según FLETES) que pasan a otro (p. ej. quien ya no labora)."""
    d = request.get_json(silent=True) or {}
    error = _error_clave(d.get("clave"))
    if error:
        return error
    accion = d.get("accion") or "listar"
    if accion == "guardar":
        de, a = _texto(d.get("de"), 120), _texto(d.get("a"), 120)
        if not de or not a:
            return jsonify(ok=False, error="Indica de quién y a quién se reasignan las obras."), 400
        catalogo.guardar_reasignacion(de, a)
    elif accion == "quitar":
        catalogo.quitar_reasignacion(_texto(d.get("de"), 120))
    return jsonify(ok=True, reasignaciones=catalogo.reasignaciones(), administradores_fletes=catalogo.administradores())


# ------------------------------------------------------------- reprogramación
MOTIVOS_REPROGRAMACION = ["Cambio de fecha solicitado por el cliente", "Incumplimiento en la entrega o recogida",
                          "Cambio de toneladas o vehículo", "Otro"]


@app.post("/api/reprogramacion")
def reprogramacion():
    ip = seguridad.ip_cliente(request)
    d = request.get_json(silent=True) or {}
    if d.get("zz_ctrl"):
        return jsonify(ok=True)
    if _limite_excedido(ip):
        return jsonify(ok=False, errores=["Demasiados envíos seguidos. Intenta en unos minutos."]), 429
    nit = re.sub(r"\D", "", _texto(d.get("nit"), 20))
    cat = catalogo.buscar_nit(nit) if catalogo.disponible() and nit else None
    cliente = (cat or {}).get("cliente") or _texto(d.get("cliente"))
    obra, motivo = _texto(d.get("obra")), _texto(d.get("motivo"), 80)
    actual, f_min, f_max = _fecha(d.get("fecha_actual")), _fecha(d.get("fecha_minima")), _fecha(d.get("fecha_maxima"))
    correos = _lista_correos(d.get("correos"))
    errores = []
    for etiqueta, fx in (("nueva fecha", f_min), ("fecha hasta", f_max)):
        if fx and operacion.motivo_fecha(fx):
            errores.append(f"La {etiqueta} {fx.strftime('%d/%m/%Y')} no se puede programar: {operacion.motivo_fecha(fx)}.")
    if catalogo.disponible() and not cat:
        errores.append("NIT no encontrado.")
    elif nit and not _tiene_acceso(_nit_base(nit)) and not _correo_pendiente(_nit_base(nit)) \
            and not _tiene_basico(_nit_base(nit)):
        errores.append("Verifica el NIT con el código enviado al correo.")
    if not obra:
        errores.append("Falta la obra.")
    if motivo not in MOTIVOS_REPROGRAMACION:
        errores.append("Elige el motivo.")
    if not f_min:
        errores.append("Indica la nueva fecha.")
    elif f_min < date.today() + timedelta(days=1):
        errores.append("La nueva fecha debe ser a partir de mañana.")
    if f_min and f_max and f_max < f_min:
        errores.append("La fecha máxima es anterior a la mínima.")
    if not correos or any(not RE_EMAIL.match(c) for c in correos):
        errores.append("Ingresa al menos un correo válido.")
    if errores:
        return jsonify(ok=False, errores=errores), 400
    datos = {"tipo": "reprogramacion", "origen": "pagina_solicitud", "nit": nit, "cliente": cliente, "obra": obra,
             "motivo": motivo, "fecha_actual": actual.isoformat() if actual else None,
             "fecha_minima": f_min.isoformat(), "fecha_maxima": (f_max or f_min).isoformat(),
             "toneladas": _texto(d.get("toneladas"), 10) or None, "correo_cliente": ",".join(correos),
             "celular": _texto(d.get("celular"), 30), "observaciones": _texto(d.get("observaciones"), 800)}
    filas = [("Tipo", "REPROGRAMACIÓN"), ("Motivo", motivo), ("NIT", nit), ("Cliente", cliente), ("Obra", obra),
             ("Fecha asignada actual", datos["fecha_actual"]), ("Nueva fecha", datos["fecha_minima"]),
             ("Hasta", datos["fecha_maxima"]), ("Toneladas", datos["toneladas"]),
             ("Correos", "; ".join(correos)), ("Celular", datos["celular"]), ("Observaciones", datos["observaciones"])]
    codigo = base64.b64encode(json.dumps(datos, ensure_ascii=False).encode()).decode()
    cuerpo = ("<p>Solicitud de <b>reprogramación</b> recibida desde la página web.</p>" + _tabla_html(filas)
              + f"<p style='font-size:8px;color:#bbb'>{MARCADOR}:{codigo}</p>")
    try:
        _enviar_al_buzon(f"REPROGRAMACIÓN DEVOLUCIÓN - {obra} - {cliente}", cuerpo, correos[0])
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR reprogramación: {exc}", flush=True)
        return jsonify(ok=False, errores=["No pudimos enviar la solicitud. Intenta de nuevo."]), 502
    return jsonify(ok=True)


# ------------------------------------------------------------- sincronización con el PC de la oficina
# El bot (PC con acceso al sistema interno) sube aquí lo que extrae: obras del sistema, correos por obra,
# contactos; y baja las reasignaciones. Protegido con la clave CLAVE_SYNC (encabezado X-Clave-Sync).
ARCHIVOS_SYNC = {"contactos": "contactos.json", "correos_obras": "correos_obras.json",
                 "obras_sistema": "obras_sistema.json", "reasignaciones": "reasignaciones.json",
                 "catalogo_cache": "catalogo_cache.json"}


def _sync_autorizado():
    esperada = os.environ.get("CLAVE_SYNC", "")
    ip = seguridad.ip_cliente(request)
    if seguridad.bloqueo(ip):
        return jsonify(ok=False, error="Equipo bloqueado."), 423
    if not esperada or not hmac.compare_digest(request.headers.get("X-Clave-Sync", ""), esperada):
        restantes, bloqueado = seguridad.registrar_fallo(ip, "clave", "sync")
        if bloqueado:
            _alerta_bloqueo(ip)
        return jsonify(ok=False, error="Clave de sincronización incorrecta."), 403
    return None


def _ruta_sync(nombre):
    return os.path.join(DATA_DIR, ARCHIVOS_SYNC[nombre])


@app.get("/api/sync/archivo")
def sync_bajar():
    error = _sync_autorizado()
    if error:
        return error
    nombre = request.args.get("nombre", "")
    if nombre not in ARCHIVOS_SYNC:
        return jsonify(ok=False, error="Archivo no permitido."), 400
    if nombre == "reasignaciones":
        return jsonify(ok=True, datos=catalogo.reasignaciones())
    if nombre == "contactos":
        return jsonify(ok=True, datos=_contactos())
    try:
        with open(_ruta_sync(nombre), encoding="utf-8") as f:
            return jsonify(ok=True, datos=json.load(f))
    except (FileNotFoundError, ValueError):
        return jsonify(ok=True, datos={})


@app.post("/api/sync/archivo")
def sync_subir():
    error = _sync_autorizado()
    if error:
        return error
    d = request.get_json(silent=True) or {}
    nombre, datos, modo = d.get("nombre"), d.get("datos"), d.get("modo", "unir")
    if nombre not in ARCHIVOS_SYNC or not isinstance(datos, dict):
        return jsonify(ok=False, error="Datos no válidos."), 400
    with _lock:
        ruta = _ruta_sync(nombre)
        try:
            with open(ruta, encoding="utf-8") as f:
                actual = json.load(f)
        except (FileNotFoundError, ValueError):
            actual = {}
        if modo == "reemplazar" and nombre == "contactos":
            nuevo = {}
            for tipo in set(actual) | set(datos):
                previos = {str(c.get("correo", "")).lower(): c for c in actual.get(tipo) or [] if isinstance(c, dict)}
                lista = []
                for c in datos.get(tipo) or []:
                    if not isinstance(c, dict):
                        continue
                    p = previos.pop(str(c.get("correo", "")).lower(), {})
                    if p.get("asesores") and not c.get("asesores"):
                        c = {**c, "asesores": p["asesores"]}  # amarres hechos en la página se conservan
                    lista.append(c)
                lista += [p for p in previos.values() if p.get("origen") != "excel"]  # agregados en la página
                nuevo[tipo] = lista
        elif modo == "reemplazar":
            nuevo = datos
        elif nombre == "correos_obras":  # se suman los correos (no se pierden los que agregaron los clientes)
            nuevo = dict(actual)
            for k, v in datos.items():
                previo = nuevo.get(k, {})
                nuevo[k] = {**previo, **v, "correos": list(dict.fromkeys((v.get("correos") or []) + (previo.get("correos") or []))),
                            "celulares": previo.get("celulares") or v.get("celulares") or []}
        else:
            nuevo = {**actual, **datos}
        os.makedirs(DATA_DIR, exist_ok=True)
        tmp = ruta + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(nuevo, f, ensure_ascii=False, indent=1)
        os.replace(tmp, ruta)
        almacen.guardado(ruta)
    if nombre == "catalogo_cache":  # catálogo armado por el PC: queda en uso de inmediato
        catalogo.cargar_cache()
    elif nombre in ("obras_sistema", "reasignaciones"):
        catalogo._cache["hora"] = 0  # el catálogo se recarga con lo nuevo
    return jsonify(ok=True, registros=len(nuevo))


# ------------------------------------------------------------ réplica directa de la base de datos del sistema
# La tarea "Unispan - Sincronizar devoluciones" (sincronizar_devoluciones.ps1, en el servidor de la BD) envía
# cada 15 min las obras con su cliente/NIT y correos. Usa su propia clave (CLAVE_BD), que SOLO sirve aquí.
RE_MAIL_BD = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
ESTADO_BD = os.path.join(DATA_DIR, "estado_bd.json")


@app.post("/api/sync/bd")
def sync_bd():
    clave = os.environ.get("CLAVE_BD", "")
    if len(clave) < 24 or not hmac.compare_digest(request.headers.get("X-Token", ""), clave):
        seguridad.registrar_fallo(seguridad.ip_cliente(request), "clave", "sync bd")
        return jsonify(ok=False, error="No autorizado."), 401
    d = request.get_json(silent=True) or {}
    obras, pedidos = d.get("obras"), d.get("correos_pedidos") or []
    if not isinstance(obras, list) or not obras:
        return jsonify(ok=False, error="Sin obras."), 400
    hoy = date.today().isoformat()
    de_pedidos: dict = {}
    for p in pedidos if isinstance(pedidos, list) else []:
        if isinstance(p, dict) and p.get("obra_id"):
            de_pedidos.setdefault(str(p["obra_id"]), []).extend(m.lower() for m in RE_MAIL_BD.findall(str(p.get("email") or "")))
    sistema, correos_bd = {}, {}
    for o in obras:
        if not isinstance(o, dict):
            continue
        nit, nombre = _nit_base(o.get("nit")), str(o.get("obra") or "").strip()[:200]
        if not nit or not nombre:
            continue
        cliente = re.sub(r"\s*\(\d+\)\s*$", "", str(o.get("cliente") or "").strip())[:200]
        if o.get("activo", True):
            s = sistema.setdefault(nit, {"cliente": cliente, "obras": [], "actualizado": hoy, "origen": "bd",
                                         "detalle": {}})
            if nombre not in s["obras"]:
                s["obras"].append(nombre)
            det = {k: str(o.get(k) or "").strip()[:80] for k in ("comercial", "ciudad") if o.get(k)}
            if det:
                s["detalle"][nombre] = det
        lista = [c for c in dict.fromkeys([m.lower() for m in RE_MAIL_BD.findall(str(o.get("correos") or ""))]
                                          + de_pedidos.get(str(o.get("id")), []))
                 if not _es_interno(c) or operacion.es_prueba(nombre)][:30]
        if lista:
            correos_bd[_clave_obra(nit, nombre)] = {"obra": nombre, "correos": lista}
    for s in sistema.values():
        s["obras"].sort()

    with _lock:
        actuales = _correos_obras()
        cambios = 0
        for k, v in correos_bd.items():
            previo = actuales.get(k) if isinstance(actuales.get(k), dict) else {}
            unidos = list(dict.fromkeys(v["correos"] + [c for c in previo.get("correos") or []
                                                        if c not in v["correos"] and not _es_interno(c)]))
            if unidos != previo.get("correos"):
                cambios += 1
            actuales[k] = {**previo, "obra": v["obra"], "correos": unidos, "celulares": previo.get("celulares") or [],
                           "actualizado": previo.get("actualizado") if unidos == previo.get("correos") else hoy,
                           "origen": "bd"}
        ruta_sis = _ruta_sync("obras_sistema")
        try:
            with open(ruta_sis, encoding="utf-8") as f:
                sis_actual = json.load(f)
        except (FileNotFoundError, ValueError):
            sis_actual = {}
        cambia_obras = any((sis_actual.get(n) or {}).get("obras") != s["obras"] for n, s in sistema.items())
        sis_actual.update(sistema)
        os.makedirs(DATA_DIR, exist_ok=True)
        for ruta, datos in ((CORREOS_OBRAS_PATH, actuales), (ruta_sis, sis_actual),
                            (ESTADO_BD, {"hora": time.strftime("%Y-%m-%d %H:%M:%S"), "equipo": str(d.get("equipo"))[:60],
                                         "obras": len(obras), "con_correos": len(correos_bd), "cambios": cambios})):
            tmp = ruta + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False, indent=1)
            os.replace(tmp, ruta)
            almacen.guardado(ruta)
    # (no se recarga todo el catálogo: buscar_nit suma obras_sistema.json al día en cada consulta)
    alertas = 0
    try:
        if "ocupacion" in d:
            operacion.guardar_ocupacion(d.get("ocupacion"))
        if "proximas" in d:
            base = (os.environ.get("PAGINA_PUBLICA") or request.host_url).rstrip("/")
            if base.startswith("http://") and "localhost" not in base and "127.0.0.1" not in base:
                base = "https://" + base[len("http://"):]
            alertas = operacion.procesar_proximas(d.get("proximas"), base)
    except Exception as exc:  # noqa: BLE001
        print(f"AVISO calendario/alertas: {exc}", flush=True)
    return jsonify(ok=True, clientes=len(sistema), obras_con_correos=len(correos_bd), cambios=cambios,
                   obras_nuevas=cambia_obras, alertas=alertas)


# Correos a clientes y asesores (alertas). En pruebas (ALERTAS_A_PRUEBA=1, por defecto) todo le llega SOLO al
# coordinador, en la carpeta de avisos, indicando a quién le habría llegado.
ALERTAS_A_PRUEBA = os.environ.get("ALERTAS_A_PRUEBA", "1") == "1"


def _enviar_correo(destinos: list, asunto: str, cuerpo: str):
    def enviar():
        buzon = os.environ.get("MAILBOX_USER", "")
        try:
            if ALERTAS_A_PRUEBA:
                _enviar_al_buzon(f"[PRUEBA] {asunto}", "<p style='background:#fff3cd;padding:8px'><b>PRUEBA Y "
                                 "VERIFICACIÓN</b> — en producción este correo iría a: "
                                 f"{html.escape(', '.join(destinos))}</p>" + cuerpo, buzon, _carpeta_avisos())
                return
            r = requests.post(f"https://graph.microsoft.com/v1.0/users/{buzon}/sendMail",
                              headers={"Authorization": f"Bearer {_token_graph()}"}, timeout=30,
                              json={"message": {"subject": asunto, "body": {"contentType": "HTML", "content": cuerpo},
                                                "toRecipients": [{"emailAddress": {"address": x}} for x in destinos[:15]],
                                                "replyTo": [{"emailAddress": {"address": buzon}}]},
                                    "saveToSentItems": True})
            if not r.ok:
                print(f"AVISO correo '{asunto}': {r.status_code} {r.text[:150]}", flush=True)
        except Exception as exc:  # noqa: BLE001
            print(f"AVISO correo '{asunto}': {exc}", flush=True)
    threading.Thread(target=enviar, daemon=True).start()


@app.get("/salud")
def salud():
    return "ok"


# Respaldo en OneDrive (plan gratis de Render: el disco se borra al reiniciar)
almacen.configurar(DATA_DIR, _token_graph)
catalogo.cargar_cache()  # el catálogo queda disponible al instante con la última copia


def _contactos_automaticos():
    """Si la página arranca SIN contactos (p. ej. se perdió el respaldo), los trae sola del Excel de contactos.
    Si ya hay contactos no los toca: los amarres del coordinador se respetan."""
    while True:
        try:
            c = _contactos()
            # SOLO si no hay contactos: nunca se pisa lo que el coordinador ya amarró
            vacio = not c.get("administradores") and not c.get("asesores")
            if CONTACTOS_EXCEL_URL and vacio:
                msg, _, _ = _sincronizar_desde_excel()
                print(f"Contactos automáticos: {msg}", flush=True)
        except Exception as exc:  # noqa: BLE001
            print(f"AVISO contactos automáticos: {exc}", flush=True)
        time.sleep(3600)


if os.environ.get("RENDER") or os.environ.get("CONTACTOS_AUTOMATICOS") == "1":
    threading.Thread(target=_contactos_automaticos, daemon=True).start()

if os.environ.get("RENDER"):  # en Render (gunicorn) se carga el catálogo al arrancar
    catalogo.precargar()

operacion.registrar(app, {
    "DATA_DIR": DATA_DIR, "guardado": almacen.guardado, "secreto": app.secret_key, "contactos": _contactos,
    "es_interno": _es_interno, "correos_de_obra": lambda nit, obra: _correos_registrados(nit or "", obra or ""),
    "tabla": _tabla_html, "enviar": _enviar_correo,
    # sin esperar a Outlook: la página del cliente responde de inmediato
    "notificar": lambda asunto, cuerpo: threading.Thread(target=_notificar_coordinador, args=(asunto, cuerpo),
                                                         daemon=True).start(),
    "ip": lambda: seguridad.ip_cliente(request), "es_coordinador": _es_coordinador,
    "correo_prueba": os.environ.get("CORREO_PRUEBA") or os.environ.get("MAILBOX_USER", ""),
    "enviar_prueba": lambda asunto, cuerpo: threading.Thread(target=lambda: _enviar_al_buzon(
        "[PRUEBA AUTOMATIZACIÓN] " + asunto, cuerpo, os.environ.get("MAILBOX_USER", ""), _carpeta_avisos()),
        daemon=True).start(),
})


if __name__ == "__main__":
    catalogo.precargar()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
