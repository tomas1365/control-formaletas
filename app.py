"""Jornada Ext Laboral (horas extras) · Unispan — servidor.

Misma base que la Bitácora de Herramientas: ingreso con usuario y clave propios,
el primer administrador se crea con el CODIGO_INSTALACION y las demás personas
solicitan acceso. Los datos quedan en Postgres (Supabase) en tablas que empiezan
por hx_, así puede compartir la misma base con la Bitácora sin mezclarse.
"""
import collections
import datetime
import json
import logging
import os
import re
import threading
import time
import urllib.error
import urllib.request
import uuid
import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken
from functools import wraps

import psycopg
from flask import Flask, jsonify, request, send_from_directory, session
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool, PoolTimeout
from werkzeug.security import check_password_hash, generate_password_hash

BASE = os.path.dirname(os.path.abspath(__file__))
APP_ID = "horasextras"

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]
app.config.update(
    SESSION_COOKIE_NAME="hx_sesion",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=bool(os.environ.get("RENDER")),
    PERMANENT_SESSION_LIFETIME=datetime.timedelta(days=30),
    MAX_CONTENT_LENGTH=12 * 1024 * 1024,  # fotos y escaneos del registro de llegada
)


def probar_base_de_datos(url):
    """Conecta una vez antes de abrir el pool para mostrar en el log la causa real si falla."""
    oculto = re.sub(r"://([^:/@]+):[^@]*@", r"://\1:****@", url)
    print(f"Conectando a la base de datos: {oculto}", flush=True)
    if "[" in url or "]" in url or "YOUR-PASSWORD" in url:
        raise SystemExit("ERROR DATABASE_URL: todavía tiene [YOUR-PASSWORD] o corchetes. Pon la contraseña real sin [ ].")
    if "pooler.supabase.com" not in url and "supabase.co" in url:
        print("AVISO: esta es la 'Direct connection'. Render no puede usarla; copia la de 'Session pooler'.", flush=True)
    try:
        psycopg.connect(url, connect_timeout=15).close()
        print("Base de datos conectada.", flush=True)
    except Exception as e:  # noqa: BLE001
        raise SystemExit(f"ERROR AL CONECTAR CON LA BASE DE DATOS: {e}")


def url_base_de_datos():
    """Con el pooler de Supabase se usa el modo TRANSACCIÓN (puerto 6543): la conexión se presta solo mientras dura
    cada consulta. El modo sesión (5432) reserva una conexión fija por cliente y su cupo (pool size, 15 en el plan
    gratuito) se llena cuando varias apps usan la misma base, y entonces la app se queda esperando ("PoolTimeout").
    Para volver al modo sesión, ponga en Render la variable MODO_POOL=sesion."""
    url = os.environ["DATABASE_URL"].strip()
    if "pooler.supabase.com:5432" in url and os.environ.get("MODO_POOL", "").lower() != "sesion":
        url = url.replace("pooler.supabase.com:5432", "pooler.supabase.com:6543")
        print("Base de datos: usando el pooler de Supabase en modo transacción (puerto 6543).", flush=True)
    return url


URL_BD = url_base_de_datos()
probar_base_de_datos(URL_BD)

TCP_VIVO = {"keepalives": 1, "keepalives_idle": 20, "keepalives_interval": 10, "keepalives_count": 3, "tcp_user_timeout": 30000}


def nuevo_pool():
    return ConnectionPool(
    URL_BD,
    min_size=2,
    max_size=10,             # el pooler de Supabase en modo transacción admite muchas; 6 se quedaban cortas en horas pico
    timeout=25,              # espera hasta 25 s por una conexión libre antes de responder 503
    max_idle=120,            # cierra conexiones ociosas antes de que el pooler las corte
    max_lifetime=1800,
    check=ConnectionPool.check_connection,  # descarta conexiones caídas antes de usarlas
    # keepalives y tcp_user_timeout: si el pooler corta una conexión sin avisar, la consulta falla en menos de un minuto
    # en lugar de quedarse esperando para siempre con la conexión tomada (eso dejaba el pool sin conexiones libres)
    kwargs={"row_factory": dict_row, "autocommit": True, "prepare_threshold": None, "connect_timeout": 10, **TCP_VIVO},
    open=True,
)


pool = nuevo_pool()
POOL_LOG = collections.deque(maxlen=6)  # últimos avisos del pool (por ejemplo, por qué no pudo conectar)


class _RegistroPool(logging.Handler):
    def emit(self, rec):
        POOL_LOG.append(time.strftime("%H:%M:%S") + " " + rec.getMessage()[:220])


logging.getLogger("psycopg.pool").addHandler(_RegistroPool())
_REPARADO = {"t": 0.0, "n": 0}


def estado_pool(p=None):
    try:
        st = (p or pool).get_stats()
        return (f"conexiones {st.get('pool_size', 0) - st.get('pool_available', 0)} en uso de {st.get('pool_size', 0)} abiertas "
                f"(máx. {pool.max_size}), {st.get('requests_waiting', 0)} esperando, errores al conectar {st.get('connections_errors', 0)}, "
                f"perdidas {st.get('connections_lost', 0)}, devueltas dañadas {st.get('returns_bad', 0)}")
    except Exception as e:  # noqa: BLE001
        return f"sin estadísticas ({e})"


def reparar_pool(motivo):
    """La base responde pero el pool de la app no entrega conexiones: se arma un pool nuevo (máximo una vez por minuto).
    El anterior se cierra aparte cuando terminen las peticiones que lo están usando."""
    global pool
    if time.time() - _REPARADO["t"] < 60:
        return False
    _REPARADO["t"] = time.time()
    _REPARADO["n"] += 1
    viejo = pool
    print(f"REPARANDO POOL ({motivo}). Antes: {estado_pool(viejo)}. Avisos: {' | '.join(POOL_LOG) or 'ninguno'}", flush=True)
    pool = nuevo_pool()
    threading.Thread(target=lambda: viejo.close(timeout=60), daemon=True, name="cierra-pool").start()
    return True

MAX_INTENTOS = 5
BLOQUEO_MS = 15 * 60 * 1000
ROLES_FIRMA = ("ELABORA", "AUTORIZA", "LIQUIDA")
ESTADOS = ("borrador", "firmado", "legalizado", "cerrado")
CATALOGOS = ("empleados", "jornadas", "config", "metas", "centros", "nomina", "proyectos", "rangos", "divisiones")
# Roles: principal (quien instaló la app; cambia estructura y forma y aprueba accesos),
# admin (ve y edita salarios, recargos y costos) y operario (usuario: registra y firma, sin valores).
ROLES = ("principal", "admin", "operario")
ADMINES = ("principal", "admin")
VERSION = "2026-11-26"
# Permisos que se reparten con los rangos (cargos) de administrador. Un administrador sin rango tiene los
# permisos de siempre (todos menos salarios y nómina, que se dan con sus casillas o con el rango).
PERMISOS = {"valores": "Ver salarios, recargos y costos", "todos": "Ver los libros de todas las personas",
            "metas": "Definir metas", "proyectos": "Crear y editar proyectos", "reabrir": "Reabrir hojas cerradas y quitar firmas",
            "responsable": "Cambiar el responsable de las hojas", "salarios": "Actualizar salarios (Recursos Humanos)",
            "nomina": "Nómina: planos, revisado y pagado", "asistencia": "Registrar llegada y confirmar asistencia",
            "salida": "Registrar salida"}
PERM_BASE = ["valores", "todos", "metas", "proyectos", "reabrir", "responsable", "asistencia", "salida"]
LLEGADA = ("asistencia", "salida")  # se dan por rango tanto a usuarios como a administradores
# Permisos de los rangos (cargos) de usuario. Un usuario sin rango los tiene todos; los administradores también.
PERMISOS_USR = {"valores": "Ver salarios, recargos y costos", "crear": "Crear hojas nuevas", "editar": "Editar hojas con firmas de Elabora o Autoriza (agregar o cambiar colaboradores)",
                "importar": "Cargar libros de Excel", "asistencia": "Registrar llegada y confirmar asistencia",
                "salida": "Registrar salida", "confirmar": "Confirmar hojas y enviarlas a su mes", "cerrar": "Legalizar, cerrar y archivar hojas",
                "eliminar": "Eliminar hojas en borrador",
                "llegada_todos": "Ver la Llegada de todos los responsables (solo marca asistió / no asistió)"}
USR_BASE = [p for p in PERMISOS_USR if p not in ("valores", "llegada_todos")]  # estos dos solo si el rango los da  # ver valores solo si el rango del usuario lo da


def ahora():
    return int(time.time() * 1000)


def crear_tablas():
    """Crea solo las tablas e índices que faltan. No toca lo que ya existe: así un despliegue nuevo no bloquea
    las tablas mientras la versión anterior sigue atendiendo."""
    objetos = [
        ("hx_usuarios", """create table if not exists hx_usuarios(
            id text primary key,
            nombre text not null,
            usuario text unique not null,
            clave text not null,
            rol text not null default 'operario',
            estado text not null default 'pendiente',
            intentos int not null default 0,
            bloqueado_hasta bigint not null default 0,
            creado bigint not null,
            aprobado_por text
        )"""),
        ("hx_fotos", """create table if not exists hx_fotos(
            id text primary key,
            fecha text not null,
            por text,
            ts bigint not null,
            tipo text not null default 'image/jpeg',
            img text not null,
            info jsonb not null default '{}'::jsonb
        )"""),
        ("hx_fotos_fecha", """create index if not exists hx_fotos_fecha on hx_fotos(fecha)"""),
        ("hx_registros", """create table if not exists hx_registros(
            col text not null,
            id text not null,
            data jsonb not null,
            actualizado bigint not null,
            primary key(col, id)
        )"""),
        ("hx_registros_act", """create index if not exists hx_registros_act on hx_registros(actualizado)"""),
        ("hx_firmas", """create table if not exists hx_firmas(
            formato text not null,
            clave text not null,
            data jsonb not null,
            ts bigint not null,
            primary key(formato, clave)
        )""")
    ]
    with pool.connection() as c:
        faltan = [(n, st) for n, st in objetos if not c.execute("select to_regclass(%s) r", (n,)).fetchone()["r"]]
    for n, st in faltan:
        with pool.connection() as c, c.transaction():
            c.execute("set local lock_timeout = '8s'")
            c.execute(st)
            print(f"Arranque: creado {n}", flush=True)


def cargar_datos_iniciales():
    """La primera vez (base vacía) carga los colaboradores y las hojas del libro Excel."""
    ruta = os.path.join(BASE, "datos_iniciales.json")
    if not os.path.exists(ruta):
        return
    with pool.connection() as c, c.transaction():
        c.execute("set local lock_timeout = '10s'")
        c.execute("lock table hx_registros in exclusive mode")
        if c.execute("select 1 from hx_registros limit 1").fetchone():
            return
        with open(ruta, encoding="utf-8") as f:
            d = json.load(f)
        for col, docs in d.items():
            for rid, data in docs.items():
                guardar_registro(c, col, rid, data)
        print(f"Datos iniciales cargados: {len(d.get('formatos', {}))} hojas.", flush=True)


# ---------------------------------------------------------------- utilidades
def error(msg, code=400):
    return jsonify({"error": msg}), code


_CACHE_U = {}


def olvidar_usuarios():
    _CACHE_U.clear()


def usuario_actual():
    uid = session.get("uid")
    if not uid:
        return None
    hit = _CACHE_U.get(uid)
    if hit and time.time() - hit[0] < 10:  # el mismo usuario pide datos cada pocos segundos: se reutiliza 10 s
        u = dict(hit[1])
    else:
        u = usuario_por_id(uid)
        if u:
            _CACHE_U[uid] = (time.time(), dict(u))
    if not u or u["estado"] != "activo":
        session.clear()
        return None
    return u


def usuario_por_id(uid):
    """Usuario con los permisos de su rango (también lo usa el bot que lee planillas en segundo plano)."""
    with pool.connection() as c:
        u = c.execute("select id,nombre,usuario,rol,estado,rrhh,nomina,ccs,rango from hx_usuarios where id=%s", (uid,)).fetchone()
        if u and u["rol"] in ("admin", "operario") and u.get("rango"):
            rg = next((x for x in (leer_registro(c, "catalogo", "rangos") or {}).get("lista") or [] if x.get("id") == u["rango"]), None)
            if rg and (rg.get("t") or "admin") != ("admin" if u["rol"] == "admin" else "usuario"):
                rg = None  # el rango es del otro nivel: no aplica
            u["_perm"] = set(rg.get("p") or []) if rg else None
            if rg and not rg.get("v"):  # rango creado antes de existir "Registrar salida": conserva lo que ya podía hacer
                if u["rol"] == "admin":
                    u["_perm"] |= set(LLEGADA)
                elif "asistencia" in u["_perm"]:
                    u["_perm"].add("salida")
            u["rangoNombre"] = rg.get("n") if rg else None
    return u


def requiere(rol=None):
    def deco(f):
        @wraps(f)
        def w(*a, **k):
            # Solo peticiones hechas por la propia app (protege contra formularios de otros sitios).
            if request.method != "GET" and request.headers.get("X-App") != APP_ID:
                return error("Petición no permitida", 403)
            u = usuario_actual()
            if not u:
                return error("Tu sesión terminó. Ingresa de nuevo.", 401)
            if rol == "admin" and u["rol"] not in ADMINES:
                return error("Solo un administrador puede hacer esto.", 403)
            if rol == "principal" and u["rol"] != "principal":
                return error("Solo el administrador principal puede hacer esto.", 403)
            request.u = u
            return f(*a, **k)
        return w
    return deco


def limpiar_usuario(s):
    return re.sub(r"\s+", "", (s or "").strip().lower())


def validar_clave(clave):
    if len(clave or "") < 6:
        return "La clave debe tener al menos 6 caracteres."
    return None


def publico(u):
    return dict({k: u[k] for k in ("id", "nombre", "usuario", "rol", "estado")}, rrhh=puede_salarios(u),
                nomina=puede_nomina(u), ccs=u.get("ccs") or [], rango=u.get("rangoNombre"),
                permisos=[p for p in dict.fromkeys(list(PERMISOS) + USR_BASE) if puede(u, p)])


def puede(u, p):
    """¿El usuario tiene el permiso p? El principal todo; el usuario ninguno; el administrador según su rango."""
    if u["rol"] == "principal":
        return True
    if u["rol"] == "operario" and p in ("valores", "llegada_todos"):
        return p in (u.get("_perm") or ())
    if p in LLEGADA:  # llegada y salida: según el rango, sea usuario o administrador; sin rango, puede
        perm = u.get("_perm")
        return perm is None or p in perm
    if p in PERMISOS_USR and p != "valores":  # lo que hace un usuario en su libro; el administrador siempre puede
        if u["rol"] in ADMINES:
            return True
        perm = u.get("_perm")
        return p in (perm if perm is not None else USR_BASE)
    if u["rol"] != "admin":
        return False
    if p == "salarios" and u.get("rrhh"):
        return True
    if p == "nomina" and u.get("nomina"):
        return True
    perm = u.get("_perm")
    return p in (perm if perm is not None else PERM_BASE)


def puede_nomina(u):
    """Administrador de nómina: descarga los planos semanales y marca revisado y pagado."""
    return puede(u, "nomina")


def puede_salarios(u):
    """Los salarios generales los actualiza Recursos Humanos (y el administrador principal)."""
    return puede(u, "salarios")


# Las claves que asigna el administrador principal se guardan también cifradas (con SECRET_KEY) para que
# él pueda consultarlas. Si la persona cambia su clave, la copia se borra: esa clave solo la conoce ella.
_FERNET = Fernet(base64.urlsafe_b64encode(hashlib.sha256(("hx-claves:" + app.secret_key).encode()).digest()))


def cifrar(clave):
    return _FERNET.encrypt(clave.encode()).decode()


def descifrar(token):
    try:
        return _FERNET.decrypt(token.encode()).decode()
    except (InvalidToken, AttributeError, ValueError):
        return None


def guardar_registro(c, col, rid, data):
    c.execute(
        """insert into hx_registros(col,id,data,actualizado) values(%s,%s,%s,%s)
           on conflict(col,id) do update set data=excluded.data, actualizado=excluded.actualizado""",
        (col, rid, Jsonb(data), ahora()),
    )


def leer_registro(c, col, rid, bloquear=False):
    sql = "select data from hx_registros where col=%s and id=%s" + (" for update" if bloquear else "")
    r = c.execute(sql, (col, rid)).fetchone()
    return r["data"] if r else None


def asignar_cc_hojas(c, uid, ccs):
    """Las horas extras ya cargadas en el libro de una persona se envían a su centro de costo asignado
    (a las hojas que aún no tienen uno, o cuyo centro ya no le corresponde)."""
    if not ccs:
        return 0
    filas = c.execute("""select id,data from hx_registros where col='formatos' and data->>'dueno'=%s
                         and not (data ? '_eliminado')""", (uid,)).fetchall()
    n = 0
    for r in filas:
        f = r["data"]
        if f.get("cc") in ccs:
            continue
        f["cc"] = ccs[0]
        f.setdefault("log", []).append({"t": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                                        "a": "Centro de costo asignado", "d": ccs[0], "por": "Accesos"})
        guardar_registro(c, "formatos", r["id"], f)
        n += 1
    return n


def asignar_sin_responsable(c, uid, nombre):
    """Las horas extras que ya existían (cargadas antes de haber libros por persona) son del administrador principal."""
    c.execute("""update hx_registros set data = data || jsonb_build_object('dueno', %s::text, 'duenoNombre', %s::text),
                 actualizado=%s where col='formatos' and not (data ? '_eliminado') and coalesce(data->>'dueno','')=''""",
              (uid, nombre, ahora()))


def asegurar_principal():
    """Versiones anteriores solo tenían 'admin': el administrador más antiguo pasa a ser el principal."""
    with pool.connection() as c, c.transaction():
        c.execute("set local lock_timeout = '8s'")
        if not c.execute("select 1 from hx_usuarios where rol='principal' limit 1").fetchone():
            c.execute("""update hx_usuarios set rol='principal' where id=(
                         select id from hx_usuarios where rol='admin' order by creado limit 1)""")
        p = c.execute("select id,nombre from hx_usuarios where rol='principal' limit 1").fetchone()
    if p:
        with pool.connection() as c, c.transaction():
            c.execute("set local lock_timeout = '8s'")
            asignar_sin_responsable(c, p["id"], p["nombre"])
    with pool.connection() as c:
        us = c.execute("select id,ccs from hx_usuarios where jsonb_array_length(ccs) > 0").fetchall()
    for u in us:  # una transacción corta por persona
        with pool.connection() as c, c.transaction():
            c.execute("set local lock_timeout = '8s'")
            asignar_cc_hojas(c, u["id"], u["ccs"])


def migrar_usuarios():
    """Agrega solo las columnas que faltan (un "alter table" bloquea la tabla aunque la columna ya exista)."""
    cols = {"clave_ver": "text", "ultimo_ingreso": "bigint", "rrhh": "boolean not null default false",
            "nomina": "boolean not null default false", "ccs": "jsonb not null default '[]'::jsonb", "rango": "text"}
    with pool.connection() as c:
        hay = {r["column_name"] for r in c.execute("""select column_name from information_schema.columns
                                                      where table_name='hx_usuarios' and table_schema=current_schema()""").fetchall()}
    for k, tipo in cols.items():
        if k not in hay:
            with pool.connection() as c, c.transaction():
                c.execute("set local lock_timeout = '8s'")
                c.execute(f"alter table hx_usuarios add column if not exists {k} {tipo}")
                print(f"Arranque: columna {k} agregada", flush=True)


def recalcular_totales():
    """Separa el recargo nocturno de los totales en las hojas guardadas con versiones anteriores."""
    with pool.connection() as c:
        filas = c.execute("""select id,data from hx_registros where col='formatos'
                             and not (data ? 'rh') and not (data ? '_eliminado')""").fetchall()
    for r in filas:
        with pool.connection() as c, c.transaction():
            c.execute("set local lock_timeout = '8s'")
            c.execute("update hx_registros set data=%s where col='formatos' and id=%s", (Jsonb(normalizar_formato(r["data"])), r["id"]))


def paso_inicio(fn):
    """Las tareas de arranque nunca deben impedir que el servidor arranque: si una falla, queda en el registro."""
    try:
        fn()
    except Exception:
        app.logger.exception("Falló la tarea de arranque %s", fn.__name__)


crear_tablas()
paso_inicio(migrar_usuarios)
paso_inicio(asegurar_principal)
paso_inicio(cargar_datos_iniciales)


# ---------------------------------------------------------------- páginas
@app.get("/")
def inicio():
    return send_from_directory(BASE, "index.html", max_age=0)


@app.get("/manifest.json")
def manifest():
    return jsonify({
        "id": "/",
        "name": "Jornada Ext Laboral · Unispan",
        "short_name": "Jornada Ext Laboral",
        "description": "Registro, firmas y legalización de horas extras",
        "lang": "es-CO",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "orientation": "any",
        "background_color": "#14246e",
        "theme_color": "#14246e",
        "icons": [
            {"src": "/icono-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "/icono-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "/icono-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
            {"src": "/icono.svg", "sizes": "any", "type": "image/svg+xml"},
        ],
    })


@app.get("/sw.js")
def service_worker():
    r = send_from_directory(BASE, "sw.js", max_age=0)
    r.headers["Cache-Control"] = "no-cache"
    r.headers["Service-Worker-Allowed"] = "/"
    return r


@app.get("/<nombre>.png")
def iconos_png(nombre):
    if nombre not in ("icono-180", "icono-192", "icono-512", "icono-maskable"):
        return error("No encontrado", 404)
    return send_from_directory(BASE, nombre + ".png", max_age=86400)


ICONO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96"><rect width="96" height="96" rx="20" fill="#14246e"/>
<g transform="translate(14 10.5) scale(.56)"><path d="M63 0L0 33V101L62 134V66L122 34.5V31L106 23L43 56V91C43 97 36 99 30 95C25 92 22 88 22 84V44L83 11Z" fill="#ffffff"/></g></svg>"""


@app.get("/icono.svg")
def icono():
    return app.response_class(ICONO, mimetype="image/svg+xml")


@app.get("/logo.jpg")
def logo():
    return send_from_directory(BASE, "logo.jpg", max_age=86400)


# ---------------------------------------------------------------- acceso
logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
logging.getLogger("psycopg.pool").setLevel(logging.WARNING)  # deja en el registro de Render por qué no conecta
_DIAG = {"t": 0.0, "txt": ""}


def diagnostico_bd():
    """Cuando no hay conexión, prueba conectar directo para saber la causa real (máximo una vez cada 30 s)."""
    if time.time() - _DIAG["t"] < 30 and _DIAG["txt"]:
        return _DIAG["txt"]
    try:
        with psycopg.connect(URL_BD, connect_timeout=8, prepare_threshold=None, **TCP_VIVO, autocommit=True, row_factory=dict_row) as cx:
            cx.execute("set statement_timeout = '6s'")
            txt = "la base de datos responde, pero las conexiones de la app estaban ocupadas o se cayeron"
            trab = cx.execute("""select pid, state, wait_event_type, extract(epoch from now()-coalesce(xact_start, query_start))::int seg,
                                 left(regexp_replace(query, '\s+', ' ', 'g'), 90) q from pg_stat_activity
                                 where datname = current_database() and pid <> pg_backend_pid() and state <> 'idle'
                                 and (wait_event_type = 'Lock' or state like 'idle in transaction%%')
                                 order by seg desc limit 6""").fetchall()
            if trab:
                txt = "hay consultas trabadas esperando un bloqueo: " + "; ".join(
                    f"{t['state']} {t['seg']}s «{t['q']}»" for t in trab)
                # se sueltan solo las de las tablas de esta app que llevan más de 45 s trabadas
                for t in trab:
                    if t["seg"] > 45 and "hx_" in (t["q"] or ""):
                        cx.execute("select pg_terminate_backend(%s)", (t["pid"],))
                        txt += f" · se soltó la consulta {t['pid']}"
    except Exception as e:  # noqa: BLE001
        txt = re.sub(r"://([^:/@]+):[^@]*@", r"://\1:****@", str(e)).replace("\n", " ").strip()[:300] or type(e).__name__
    _DIAG.update(t=time.time(), txt=txt)
    print(f"DIAGNÓSTICO BASE DE DATOS: {txt}", flush=True)
    return txt


@app.errorhandler(PoolTimeout)
def base_ocupada(_e):
    uso, diag = estado_pool(), diagnostico_bd()
    print(f"POOL AGOTADO: {uso}. Avisos: {' | '.join(POOL_LOG) or 'ninguno'}", flush=True)
    reparado = "responde" in diag and reparar_pool("petición sin conexión")
    return jsonify({"error": "La base de datos no respondió a tiempo (" + uso + "). Causa: " + diag
                    + (". Se reinició la conexión: vuelva a intentar." if reparado else "")}), 503


@app.errorhandler(psycopg.OperationalError)
def base_caida(e):
    print(f"Base de datos no disponible: {e}", flush=True)
    return jsonify({"error": "No hay conexión con la base de datos. Causa: " + diagnostico_bd()}), 503


@app.get("/salud")
def salud():
    """Dirección liviana para que un monitor externo (cron-job.org, UptimeRobot) mantenga despierto el servidor.
    Hace una consulta mínima a la base de datos para que también quede lista la conexión."""
    try:
        with pool.connection(timeout=10) as c:
            c.execute("select 1")
        r = jsonify({"ok": True, "hora": ahora(), "version": VERSION, "pool": estado_pool(), "reparaciones": _REPARADO["n"]})
    except Exception as e:  # noqa: BLE001
        diag, antes = diagnostico_bd(), estado_pool()
        det = {"ok": False, "version": VERSION, "error": diag, "falla": f"{type(e).__name__}: {str(e)[:200]}",
               "pool": antes, "avisos_pool": list(POOL_LOG)}
        if "responde" in diag and reparar_pool("salud"):
            try:  # se prueba de nuevo con el pool nuevo
                with pool.connection(timeout=10) as c:
                    c.execute("select 1")
                return jsonify(dict(det, ok=True, reparado=True, pool=estado_pool()))
            except Exception as e2:  # noqa: BLE001
                det["despues_de_reparar"] = f"{type(e2).__name__}: {str(e2)[:200]}"
        return jsonify(det), 503
    r.headers["Cache-Control"] = "no-store"
    return r


@app.get("/api/estado")
def estado():
    with pool.connection() as c:
        hay = c.execute("select 1 from hx_usuarios where rol in ('principal','admin') limit 1").fetchone()
    u = usuario_actual()
    return jsonify({"instalado": bool(hay), "usuario": publico(u) if u else None})


@app.post("/api/instalar")
def instalar():
    """Crea el primer administrador. Exige el código de instalación definido en Render."""
    if request.headers.get("X-App") != APP_ID:
        return error("Petición no permitida", 403)
    d = request.get_json(silent=True) or {}
    codigo = os.environ.get("CODIGO_INSTALACION", "")
    if not codigo or d.get("codigo") != codigo:
        time.sleep(1)
        return error("El código de instalación no es correcto.", 403)
    usuario, nombre, clave = limpiar_usuario(d.get("usuario")), (d.get("nombre") or "").strip(), d.get("clave") or ""
    if not usuario or not nombre:
        return error("Escribe tu nombre y un usuario.")
    if (m := validar_clave(clave)):
        return error(m)
    with pool.connection() as c, c.transaction():
        c.execute("set local lock_timeout = '10s'")
        c.execute("lock table hx_usuarios in exclusive mode")
        if c.execute("select 1 from hx_usuarios where rol in ('principal','admin') limit 1").fetchone():
            return error("La app ya tiene administrador. Ingresa con tu usuario.", 409)
        uid = uuid.uuid4().hex
        c.execute("insert into hx_usuarios(id,nombre,usuario,clave,rol,estado,creado,ultimo_ingreso) values(%s,%s,%s,%s,'principal','activo',%s,%s)",
                  (uid, nombre, usuario, generate_password_hash(clave), ahora(), ahora()))
        asignar_sin_responsable(c, uid, nombre)
    session.clear(); session.permanent = True; session["uid"] = uid
    return jsonify({"ok": True})


@app.after_request
def _cambios_de_usuarios(resp):
    """Si cambian usuarios, claves o rangos, el permiso nuevo aplica en la siguiente petición (sin esperar los 10 s)."""
    if request.method != "GET" and (request.path.startswith(("/api/usuarios", "/api/cambiar-clave", "/api/ingresar", "/api/salir"))
                                    or request.path == "/api/catalogo/rangos"):
        olvidar_usuarios()
    return resp


@app.post("/api/ingresar")
def ingresar():
    if request.headers.get("X-App") != APP_ID:
        return error("Petición no permitida", 403)
    d = request.get_json(silent=True) or {}
    usuario, clave = limpiar_usuario(d.get("usuario")), d.get("clave") or ""
    with pool.connection() as c:
        u = c.execute("select * from hx_usuarios where usuario=%s", (usuario,)).fetchone()
        if not u:
            time.sleep(0.7)
            return error("Usuario o clave incorrectos.", 401)
        if u["bloqueado_hasta"] > ahora():
            mins = max(1, (u["bloqueado_hasta"] - ahora()) // 60000)
            return error(f"Demasiados intentos. Intenta de nuevo en {mins} min.", 429)
        if not check_password_hash(u["clave"], clave):
            n = u["intentos"] + 1
            hasta = ahora() + BLOQUEO_MS if n >= MAX_INTENTOS else 0
            c.execute("update hx_usuarios set intentos=%s, bloqueado_hasta=%s where id=%s",
                      (0 if hasta else n, hasta, u["id"]))
            time.sleep(0.7)
            return error("Usuario o clave incorrectos.", 401)
        c.execute("update hx_usuarios set intentos=0, bloqueado_hasta=0, ultimo_ingreso=%s where id=%s", (ahora(), u["id"]))
    if u["estado"] == "pendiente":
        return error("Tu solicitud aún no ha sido aprobada por el administrador.", 403)
    if u["estado"] != "activo":
        return error("Tu acceso está desactivado. Habla con el administrador.", 403)
    session.clear(); session.permanent = True; session["uid"] = u["id"]
    return jsonify({"ok": True})


@app.post("/api/salir")
def salir():
    session.clear()
    return jsonify({"ok": True})


@app.post("/api/solicitar")
def solicitar():
    if request.headers.get("X-App") != APP_ID:
        return error("Petición no permitida", 403)
    d = request.get_json(silent=True) or {}
    usuario, nombre, clave = limpiar_usuario(d.get("usuario")), (d.get("nombre") or "").strip(), d.get("clave") or ""
    if not usuario or not nombre:
        return error("Escribe tu nombre completo y un usuario.")
    if not re.fullmatch(r"[a-z0-9._-]{3,30}", usuario):
        return error("El usuario debe tener de 3 a 30 letras o números, sin espacios.")
    if (m := validar_clave(clave)):
        return error(m)
    with pool.connection() as c:
        if c.execute("select 1 from hx_usuarios where usuario=%s", (usuario,)).fetchone():
            return error("Ese usuario ya existe. Elige otro.", 409)
        if c.execute("select count(*) n from hx_usuarios where estado='pendiente'").fetchone()["n"] >= 50:
            return error("Hay demasiadas solicitudes pendientes. Avisa al administrador.", 429)
        c.execute("insert into hx_usuarios(id,nombre,usuario,clave,rol,estado,creado) values(%s,%s,%s,%s,'operario','pendiente',%s)",
                  (uuid.uuid4().hex, nombre[:80], usuario, generate_password_hash(clave), ahora()))
    return jsonify({"ok": True})


@app.post("/api/cambiar-clave")
@requiere()
def cambiar_clave():
    d = request.get_json(silent=True) or {}
    if (m := validar_clave(d.get("nueva"))):
        return error(m)
    with pool.connection() as c:
        u = c.execute("select clave from hx_usuarios where id=%s", (request.u["id"],)).fetchone()
        if not check_password_hash(u["clave"], d.get("actual") or ""):
            return error("La clave actual no es correcta.", 403)
        c.execute("update hx_usuarios set clave=%s, clave_ver=null where id=%s", (generate_password_hash(d["nueva"]), request.u["id"]))
    return jsonify({"ok": True})


@app.get("/api/usuarios")
@requiere("principal")
def usuarios():
    with pool.connection() as c:
        rows = c.execute("""select id,nombre,usuario,rol,estado,creado,ultimo_ingreso,rrhh,nomina,ccs,rango,
                            (clave_ver is not null) as clave_visible from hx_usuarios order by estado='pendiente' desc, nombre""").fetchall()
    return jsonify({"usuarios": rows})


@app.delete("/api/usuarios/<uid>")
@requiere("principal")
def eliminar_usuario(uid):
    """Elimina un usuario. Sus hojas pasan al libro del administrador principal, o se eliminan si así se pide."""
    hojas = (request.args.get("hojas") or "pasar")
    with pool.connection() as c, c.transaction():
        c.execute("set local lock_timeout = '10s'")
        u = c.execute("select id,nombre,rol from hx_usuarios where id=%s for update", (uid,)).fetchone()
        if not u:
            return error("Usuario no encontrado.", 404)
        if u["rol"] == "principal" or uid == request.u["id"]:
            return error("El administrador principal no se puede eliminar.")
        n = 0
        for r in c.execute("select id,data from hx_registros where col='formatos' and data->>'dueno'=%s for update", (uid,)).fetchall():
            f = r["data"]
            if hojas == "eliminar":
                guardar_registro(c, "formatos", r["id"], {"_eliminado": True})
                c.execute("delete from hx_firmas where formato=%s", (r["id"],))
            else:
                f["dueno"], f["duenoNombre"] = request.u["id"], request.u["nombre"]
                f.setdefault("log", []).append({"t": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                                                "a": "Pasó al libro de " + request.u["nombre"], "d": "Se eliminó el usuario " + u["nombre"],
                                                "por": request.u["nombre"]})
                guardar_registro(c, "formatos", r["id"], f)
            n += 1
        c.execute("delete from hx_usuarios where id=%s", (uid,))
    return jsonify({"ok": True, "hojas": n})


@app.get("/api/usuarios/<uid>/clave")
@requiere("principal")
def ver_clave(uid):
    with pool.connection() as c:
        u = c.execute("select clave_ver from hx_usuarios where id=%s", (uid,)).fetchone()
    clave = descifrar(u["clave_ver"]) if u and u["clave_ver"] else None
    if not clave:
        return error("Esta clave la definió la persona; no se puede ver. Puede asignarle una nueva.", 404)
    return jsonify({"clave": clave})


@app.post("/api/usuarios")
@requiere("principal")
def crear_usuario():
    """El administrador principal crea directamente un usuario o administrador con su clave."""
    d = request.get_json(silent=True) or {}
    usuario, nombre, clave = limpiar_usuario(d.get("usuario")), (d.get("nombre") or "").strip(), d.get("clave") or ""
    rol = d.get("rol") if d.get("rol") in ("admin", "operario") else "operario"
    rrhh = bool(d.get("rrhh")) and rol == "admin"
    nomina = bool(d.get("nomina")) and rol == "admin"
    ccs = [str(x)[:40] for x in d.get("ccs") or [] if str(x).strip()][:30]
    rango = str(d.get("rango"))[:40] if d.get("rango") and rol != "principal" else None
    if not usuario or not nombre:
        return error("Escribe el nombre y un usuario.")
    if not re.fullmatch(r"[a-z0-9._-]{3,30}", usuario):
        return error("El usuario debe tener de 3 a 30 letras o números, sin espacios.")
    if (m := validar_clave(clave)):
        return error(m)
    with pool.connection() as c:
        if c.execute("select 1 from hx_usuarios where usuario=%s", (usuario,)).fetchone():
            return error("Ese usuario ya existe. Elige otro.", 409)
        c.execute("insert into hx_usuarios(id,nombre,usuario,clave,rol,estado,creado,aprobado_por,clave_ver,rrhh,nomina,ccs,rango) values(%s,%s,%s,%s,%s,'activo',%s,%s,%s,%s,%s,%s,%s)",
                  (uuid.uuid4().hex, nombre[:80], usuario, generate_password_hash(clave), rol, ahora(), request.u["id"], cifrar(clave), rrhh, nomina, Jsonb(ccs), rango))
    return jsonify({"ok": True})


@app.post("/api/usuarios/<uid>")
@requiere("principal")
def gestionar_usuario(uid):
    d = request.get_json(silent=True) or {}
    accion = d.get("accion")
    with pool.connection() as c, c.transaction():
        c.execute("set local lock_timeout = '10s'")
        u = c.execute("select * from hx_usuarios where id=%s for update", (uid,)).fetchone()
        if not u:
            return error("Usuario no encontrado.", 404)
        if u["rol"] == "principal" and accion in ("desactivar", "rol", "rechazar"):
            return error("El administrador principal no se puede cambiar ni desactivar.")
        es_ultimo_admin = False
        if accion == "aprobar":
            rol = d.get("rol") if d.get("rol") in ("admin", "operario") else "operario"
            c.execute("update hx_usuarios set estado='activo', rol=%s, aprobado_por=%s where id=%s", (rol, request.u["id"], uid))
        elif accion == "rechazar":
            if u["estado"] != "pendiente":
                return error("Solo se pueden rechazar solicitudes pendientes.")
            c.execute("delete from hx_usuarios where id=%s", (uid,))
        elif accion == "desactivar":
            if es_ultimo_admin:
                return error("No puedes desactivar al único administrador.")
            c.execute("update hx_usuarios set estado='inactivo' where id=%s", (uid,))
        elif accion == "activar":
            c.execute("update hx_usuarios set estado='activo', intentos=0, bloqueado_hasta=0 where id=%s", (uid,))
        elif accion == "rol":
            rol = d.get("rol")
            if rol not in ("admin", "operario"):
                return error("Rol no válido.")
            c.execute("update hx_usuarios set rol=%s where id=%s", (rol, uid))
        elif accion == "editar":
            nombre, usuario = (d.get("nombre") or "").strip(), limpiar_usuario(d.get("usuario"))
            if not nombre or not re.fullmatch(r"[a-z0-9._-]{3,30}", usuario):
                return error("Escribe el nombre y un usuario de 3 a 30 letras o números, sin espacios.")
            if c.execute("select 1 from hx_usuarios where usuario=%s and id<>%s", (usuario, uid)).fetchone():
                return error("Ese usuario ya existe. Elige otro.", 409)
            rol = u["rol"] if u["rol"] == "principal" else (d.get("rol") if d.get("rol") in ("admin", "operario") else u["rol"])
            rrhh = bool(d.get("rrhh")) and rol == "admin"
            nomina = bool(d.get("nomina")) and rol == "admin"
            ccs = [str(x)[:40] for x in d.get("ccs") or [] if str(x).strip()][:30]
            rango = str(d.get("rango"))[:40] if d.get("rango") and rol != "principal" else None
            c.execute("update hx_usuarios set nombre=%s, usuario=%s, rol=%s, rrhh=%s, nomina=%s, ccs=%s, rango=%s where id=%s",
                      (nombre[:80], usuario, rol, rrhh, nomina, Jsonb(ccs), rango, uid))
            asignar_cc_hojas(c, uid, ccs)
            if d.get("clave"):
                if (m := validar_clave(d.get("clave"))):
                    return error(m)
                c.execute("update hx_usuarios set clave=%s, clave_ver=%s, intentos=0, bloqueado_hasta=0 where id=%s",
                          (generate_password_hash(d["clave"]), cifrar(d["clave"]) if uid != request.u["id"] else None, uid))
        elif accion == "clave":
            if (m := validar_clave(d.get("clave"))):
                return error(m)
            c.execute("update hx_usuarios set clave=%s, clave_ver=%s, intentos=0, bloqueado_hasta=0 where id=%s",
                      (generate_password_hash(d["clave"]), cifrar(d["clave"]), uid))
        else:
            return error("Acción no válida.")
    return jsonify({"ok": True})


# ---------------------------------------------------------------- datos
@app.get("/api/datos")
@requiere()
def datos():
    desde = request.args.get("desde", type=int) or 0
    marca = ahora()
    with pool.connection() as c:
        rows = c.execute("select col,id,data from hx_registros where actualizado>%s and col <> 'actividades'",
                         (desde - 2000 if desde else -1,)).fetchall()
    out = {}
    ver = puede(request.u, "valores")
    for r in rows:
        data = r["data"]
        if r["col"] == "formatos" and not data.get("_eliminado") and not puede_ver(request.u, data):
            if solo_llegada(request.u, data):
                data = dict(data, _soloLlegada=True)  # la ve únicamente en Llegada, para marcar asistencia
            else:
                data = {"_eliminado": True}  # no es suya (o se reasignó a otra persona)
        out.setdefault(r["col"], {})[r["id"]] = data if ver else sin_valores(r["col"], r["id"], data)
    return jsonify({"registros": out, "ahora": marca, "yo": publico(request.u)})


@app.get("/api/actividades")
@requiere()
def mis_actividades():
    """Lista de actividades (soportes) que cada usuario crea y guarda para elegirlas en sus hojas."""
    with pool.connection() as c:
        d = leer_registro(c, "actividades", request.u["id"]) or {}
    return jsonify({"lista": d.get("lista") or []})


@app.put("/api/actividades")
@requiere()
def guardar_actividades():
    lista = (request.get_json(silent=True) or {}).get("lista")
    if not isinstance(lista, list):
        return error("Datos no válidos.")
    limpia = []
    for x in lista:
        t = " ".join(str(x or "").split())[:150]
        if t and t.upper() not in {y.upper() for y in limpia}:
            limpia.append(t)
    with pool.connection() as c, c.transaction():
        c.execute("set local lock_timeout = '10s'")
        guardar_registro(c, "actividades", request.u["id"], {"lista": limpia[:150]})
    return jsonify({"ok": True, "lista": limpia[:150]})


def solo_llegada(u, f):
    """Rango tipo portería: ve en Llegada las hojas de todos (no legalizadas) solo para marcar asistió / no asistió."""
    return puede(u, "llegada_todos") and (f or {}).get("estado") != "legalizado"


def puede_horas(u, f):
    """Cambiar horas de llegada y salida: el responsable de la hoja, los administradores y Nómina."""
    return u["rol"] in ADMINES or puede(u, "nomina") or (f or {}).get("dueno") == u["id"]


def puede_ver(u, f):
    """Los administradores ven todo el libro; cada usuario ve solo las hojas de las que es responsable."""
    return puede(u, "todos") or (f or {}).get("dueno") == u["id"]


def sin_valores(col, rid, data):
    """Copia sin salarios, recargos ni costos, para usuarios que no son administradores."""
    if col == "formatos" and not data.get("_eliminado"):
        data = {k: v for k, v in data.items() if k not in ("div", "tc", "rc")}
        data["filas"] = [{k: v for k, v in r.items() if k not in ("s", "r", "co")} for r in data.get("filas") or []]
    elif col == "catalogo" and rid == "empleados":
        data = dict(data, lista=[e[:3] + [None] + e[4:] for e in data.get("lista") or []])
    elif col == "catalogo" and rid == "nomina":
        data = {}
    elif col == "catalogo" and rid == "metas":
        data = dict(data, globalMesC=None, areas=[dict(a, c=None) for a in data.get("areas") or []])
    elif col == "catalogo" and rid == "jornadas":
        data = dict(data, lista=[{k: v for k, v in j.items() if k != "r"} for j in data.get("lista") or []])
    return data


def num(v, defecto=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return defecto


def completar_valores(c, f, antes, confiar):
    """Pone salario, recargo y divisor de cada fila. Los usuarios no los ven ni los envían:
    se conservan los de la misma fila (en esta hoja o en la autorización de origen) y, si la fila
    es nueva o cambió de colaborador o jornada, se toman del listado de personal y de las jornadas."""
    previas = {}
    origen = leer_registro(c, "formatos", f["origen"]) if isinstance(f.get("origen"), str) else None
    for h in (origen, antes):
        for r in (h or {}).get("filas") or []:
            if isinstance(r, dict) and r.get("id"):
                previas[r["id"]] = r
    cache = {}

    def cat(doc):
        if doc not in cache:
            cache[doc] = leer_registro(c, "catalogo", doc) or {}
        return cache[doc]

    if not (confiar and num(f.get("div"))):
        f["div"] = num((antes or {}).get("div")) or num((origen or {}).get("div")) or num(cat("config").get("divisor"), 210) or 210
    for r in f.get("filas") or []:
        if not isinstance(r, dict):
            continue
        p = previas.get(r.get("id"))
        if not (confiar and isinstance(r.get("s"), (int, float))):
            if p and p.get("c") == r.get("c") and isinstance(p.get("s"), (int, float)):
                r["s"] = p["s"]
            else:
                e = next((e for e in cat("empleados").get("lista") or [] if str(e[0]) == str(r.get("c"))), None)
                r["s"] = num(e[3]) if e else 0
        if not (confiar and isinstance(r.get("r"), (int, float))):
            if p and p.get("j") == r.get("j") and isinstance(p.get("r"), (int, float)):
                r["r"] = p["r"]
            else:
                j = next((j for j in cat("jornadas").get("lista") or [] if j.get("c") == r.get("j")), None)
                r["r"] = num(j.get("r")) if j else 0
    return f


def es_rn(r):
    """Fila de recargo nocturno (no es hora extra)."""
    return r.get("j") == "RN" or "RECARGO" in str(r.get("jn") or "").upper()


def normalizar_formato(f):
    """Recalcula en el servidor costos, totales, fechas y estado, para que nadie altere los valores."""
    div = num(f.get("div"), 210) or 210
    filas = []
    for r in f.get("filas") or []:
        if not isinstance(r, dict):
            continue
        r = dict(r)
        r["h"] = round(num(r.get("h")), 2)
        r["s"] = num(r.get("s"))
        r["r"] = num(r.get("r"))
        r["co"] = round(r["s"] / div * r["r"] * r["h"], 2)
        filas.append(r)
    f["filas"] = filas
    # El recargo nocturno no es hora extra: se lleva aparte para no inflar los totales ni los indicadores.
    ext = [r for r in filas if not es_rn(r)]
    rn = [r for r in filas if es_rn(r)]
    f["th"] = round(sum(r["h"] for r in ext), 2)
    f["tc"] = round(sum(r["co"] for r in ext), 2)
    f["rh"] = round(sum(r["h"] for r in rn), 2)
    f["rc"] = round(sum(r["co"] for r in rn), 2)
    fechas = sorted(r.get("f") for r in filas if r.get("f"))
    f["fi"], f["ff"] = (fechas[0], fechas[-1]) if fechas else (None, None)
    pie = f.get("pie") or {}
    if f.get("estado") not in ESTADOS:
        f["estado"] = "borrador"
    if f["estado"] in ("borrador", "firmado"):
        f["estado"] = "firmado" if pie.get("ELABORA") and pie.get("AUTORIZA") else "borrador"
    f["log"] = (f.get("log") or [])[-60:]
    return f


MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def cuenta_en_totales(f):
    """Una autorización ya legalizada no se suma: sus horas reales están en la legalización."""
    return isinstance(f, dict) and not f.get("_eliminado") and f.get("estado") != "legalizado"


def semana(fecha):
    d = datetime.date.fromisoformat(fecha)
    lunes = d - datetime.timedelta(days=d.weekday())
    return lunes.isoformat()


def evaluar_metas(c, fid, d, ver):
    """Compara la hoja d con las metas que fijaron los administradores.
    Devuelve una lista de alertas: nivel 'supera' (pasa la meta) o 'cerca' (llega al 90 %)."""
    m = leer_registro(c, "catalogo", "metas") or {}
    filas = [r for r in d.get("filas") or [] if r.get("f") and not es_rn(r)]  # el recargo nocturno no cuenta en las metas
    if not filas:
        return []
    otras = []
    for r in c.execute("select id,data from hx_registros where col='formatos'").fetchall():
        f = r["data"]
        if r["id"] in (fid, d.get("origen")) or not cuenta_en_totales(f):
            continue
        otras.extend((x, f) for x in f.get("filas") or [] if x.get("f") and not es_rn(x))
    todas = [(x, d) for x in filas] + otras
    alertas = []

    def fmt(v, unidad):
        return f"{v:g} h" if unidad == "h" else "$ " + f"{round(v):,}".replace(",", ".")

    def revisar(meta, unidad, quien, periodo, dentro, valor):
        meta = num(meta)
        if meta <= 0:
            return
        total = sum(valor(x) for x, f in todas if dentro(x, f))
        nuevo = sum(valor(x) for x in filas if dentro(x, d))
        if nuevo <= 0:
            return
        nivel = "supera" if total > meta + 1e-9 else "cerca" if total >= meta * 0.9 else None
        if not nivel:
            return
        if unidad == "$" and not ver:
            txt = f"{quien}: el costo {periodo} queda en el {round(total / meta * 100)} % de la meta"
        else:
            txt = f"{quien}: {fmt(total, unidad)} {periodo} (meta {fmt(meta, unidad)}; esta hoja suma {fmt(nuevo, unidad)})"
        alertas.append({"nivel": nivel, "texto": txt, "pct": round(total / meta * 100)})

    h = lambda x: num(x.get("h"))
    co = lambda x: num(x.get("co"))
    meses = sorted({x["f"][:7] for x in filas})
    nom_mes = lambda k: f"en {MESES[int(k[5:7]) - 1]} {k[:4]}"
    personas = {x.get("c"): x.get("n") for x in filas}
    for ced, nombre in personas.items():
        for sem in sorted({semana(x["f"]) for x in filas if x.get("c") == ced}):
            ds = datetime.date.fromisoformat(sem).strftime("%d/%m/%Y")
            revisar(m.get("colSemana"), "h", nombre, f"en la semana del {ds}",
                    lambda x, f, ced=ced, sem=sem: x.get("c") == ced and semana(x["f"]) == sem, h)
        for k in sorted({x["f"][:7] for x in filas if x.get("c") == ced}):
            revisar(m.get("colMes"), "h", nombre, nom_mes(k), lambda x, f, ced=ced, k=k: x.get("c") == ced and x["f"][:7] == k, h)
    for k in meses:
        for a in m.get("areas") or []:
            area = a.get("a")
            if any(x.get("a") == area and x["f"][:7] == k for x in filas):
                dentro = lambda x, f, area=area, k=k: x.get("a") == area and x["f"][:7] == k
                revisar(a.get("h"), "h", f"Área {area}", nom_mes(k), dentro, h)
                revisar(a.get("c"), "$", f"Área {area}", nom_mes(k), dentro, co)
        for r in m.get("usuarios") or []:
            if r.get("u") == d.get("dueno"):
                revisar(r.get("h"), "h", f"Libro de {r.get('n') or 'este responsable'}", nom_mes(k),
                        lambda x, f, k=k: f.get("dueno") == d.get("dueno") and x["f"][:7] == k, h)
        revisar(m.get("globalMesH"), "h", "Total de la empresa", nom_mes(k), lambda x, f, k=k: x["f"][:7] == k, h)
        revisar(m.get("globalMesC"), "$", "Total de la empresa", nom_mes(k), lambda x, f, k=k: x["f"][:7] == k, co)
    alertas.sort(key=lambda a: (a["nivel"] != "supera", -a["pct"]))
    return alertas


def preparar(c, fid, d, antes):
    """Completa valores, responsable y totales de una hoja antes de guardarla o revisarla."""
    admin = request.u["rol"] in ADMINES
    if antes:
        dueno = antes.get("dueno"), antes.get("duenoNombre")
        if puede(request.u, "responsable") and d.get("dueno") and d.get("dueno") != antes.get("dueno"):
            dueno = d["dueno"], d.get("duenoNombre")
    else:
        dueno = request.u["id"], request.u["nombre"]
        if admin and d.get("dueno") and d["dueno"] != request.u["id"]:
            otro = c.execute("select id,nombre from hx_usuarios where id=%s and estado='activo'", (d["dueno"],)).fetchone()
            if otro:
                dueno = otro["id"], otro["nombre"]  # el administrador carga la hoja en el libro de esa persona
    d["dueno"], d["duenoNombre"] = dueno
    # Centro de costo de la hoja: las horas se cargan a él, sin importar el área del colaborador.
    mios = request.u.get("ccs") or []
    if not admin and mios and d.get("cc") not in mios:
        d["cc"] = (antes or {}).get("cc") if (antes or {}).get("cc") in mios else mios[0]
    if not d.get("cc"):
        due = c.execute("select ccs from hx_usuarios where id=%s", (d["dueno"],)).fetchone()
        d["cc"] = (due["ccs"] or [None])[0] if due else None
    d = completar_valores(c, d, antes, confiar=puede(request.u, "valores"))
    return normalizar_formato(d)


@app.post("/api/formatos")
@requiere()
def crear_formato():
    """Crea una hoja nueva; el número lo asigna el servidor para que no se repita entre usuarios."""
    d = (request.get_json(silent=True) or {}).get("data")
    if not isinstance(d, dict):
        return error("Datos no válidos.")
    falta = "cerrar" if d.get("origen") else "importar" if d.get("imp") else "crear"
    if not puede(request.u, falta):
        return error({"cerrar": "Su rango no permite legalizar hojas.", "importar": "Su rango no permite cargar libros de Excel.",
                      "crear": "Su rango no permite crear hojas."}[falta], 403)
    with pool.connection() as c, c.transaction():
        c.execute("set local lock_timeout = '10s'")
        c.execute("lock table hx_registros in share row exclusive mode")
        n = c.execute("select coalesce(max(substring(id from 2)::int),0)+1 n from hx_registros where col='formatos' and id ~ '^h[0-9]+$'").fetchone()["n"]
        fid = f"h{n}"
        guardar_registro(c, "formatos", fid, {"_eliminado": True, "_reservada": True})  # reserva el número
    d["num"] = n
    return guardar_formato(fid, d)


@app.post("/api/revisar-metas")
@requiere()
def revisar_metas():
    b = request.get_json(silent=True) or {}
    d, fid = b.get("data"), b.get("id") or ""
    if not isinstance(d, dict):
        return error("Datos no válidos.")
    with pool.connection() as c:
        antes = leer_registro(c, "formatos", fid) if fid else None
        if antes and not puede_ver(request.u, antes):
            return error("Esta hoja es de otra persona.", 403)
        d = preparar(c, fid, dict(d), antes if antes and not antes.get("_eliminado") else None)
        alertas = evaluar_metas(c, fid, d, puede(request.u, "valores"))
        duplicada = buscar_duplicada(c, fid, d) if b.get("buscarDuplicada") else None
        modo = (leer_registro(c, "catalogo", "metas") or {}).get("modo") or "avisar"
    return jsonify({"alertas": alertas, "bloquea": modo == "bloquear" and request.u["rol"] not in ADMINES, "duplicada": duplicada})


def buscar_duplicada(c, fid, d):
    """Evita contar dos veces la misma hoja cuando dos personas cargan el mismo libro Excel:
    busca otra hoja (de cualquier responsable) con los mismos colaboradores, fechas y horarios."""
    firma = lambda fs: {(str(r.get("c")), r.get("f"), r.get("hi"), r.get("hf")) for r in fs or [] if isinstance(r, dict)}
    mia = firma(d.get("filas"))
    if not mia:
        return None
    for r in c.execute("select id,data from hx_registros where col='formatos'").fetchall():
        f = r["data"]
        if r["id"] == fid or f.get("_eliminado") or f.get("tipo") != d.get("tipo"):
            continue
        otra = firma(f.get("filas"))
        if otra and len(mia & otra) >= 0.9 * max(len(mia), len(otra)):
            return {"id": r["id"], "titulo": f.get("titulo"), "responsable": f.get("duenoNombre") or "sin responsable", "dueno": f.get("dueno"),
                    "estado": f.get("estado")}
    return None


@app.post("/api/salarios/aplicar")
@requiere("admin")
def aplicar_salarios():
    """Recalcula con los salarios vigentes las filas desde la fecha indicada en las hojas abiertas de todos los libros.
    Las hojas legalizadas o cerradas conservan el salario con que se liquidaron."""
    if not puede_salarios(request.u):
        return error("Solo Recursos Humanos puede aplicar salarios.", 403)
    desde = str((request.get_json(silent=True) or {}).get("desde") or "")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", desde):
        return error("Indique desde qué fecha rigen los salarios.")
    hojas = filas_cambiadas = 0
    with pool.connection() as c, c.transaction():
        c.execute("set local lock_timeout = '10s'")
        emp = {str(e[0]): num(e[3]) for e in (leer_registro(c, "catalogo", "empleados") or {}).get("lista") or [] if num(e[3]) > 0}
        for r in c.execute("select id,data from hx_registros where col='formatos' for update").fetchall():
            f = r["data"]
            if f.get("_eliminado") or f.get("estado") in ("legalizado", "cerrado"):
                continue
            n = 0
            for x in f.get("filas") or []:
                nuevo = emp.get(str(x.get("c")))
                if nuevo and (x.get("f") or "") >= desde and num(x.get("s")) != nuevo:
                    x["s"] = nuevo
                    n += 1
            if n:
                f = normalizar_formato(f)
                f.setdefault("log", []).append({"t": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                                                "a": "Salarios actualizados por Recursos Humanos",
                                                "d": f"{n} filas desde {desde[8:10]}/{desde[5:7]}/{desde[:4]}", "por": request.u["nombre"]})
                guardar_registro(c, "formatos", r["id"], f)
                hojas += 1
                filas_cambiadas += n
    return jsonify({"ok": True, "hojas": hojas, "filas": filas_cambiadas})


@app.get("/api/permisos")
@requiere()
def lista_permisos():
    return jsonify({"permisos": PERMISOS, "base": PERM_BASE, "usuario": PERMISOS_USR})


@app.get("/api/responsables")
@requiere("admin")
def responsables():
    with pool.connection() as c:
        rows = c.execute("select id,nombre,rol from hx_usuarios where estado='activo' order by nombre").fetchall()
    return jsonify({"responsables": rows})


@app.put("/api/formatos/<fid>")
@requiere()
def guardar_formato(fid, nuevo=None):
    if not re.fullmatch(r"h\d{1,7}", fid):
        return error("Identificador no válido.")
    d = nuevo if nuevo is not None else (request.get_json(silent=True) or {}).get("data")
    if not isinstance(d, dict):
        return error("Datos no válidos.")
    if len(json.dumps(d)) > 900_000:
        return error("La hoja es demasiado grande.")
    with pool.connection() as c, c.transaction():
        c.execute("set local lock_timeout = '10s'")
        antes = leer_registro(c, "formatos", fid, bloquear=True)
        if antes and antes.get("_eliminado"):
            antes = None
        if nuevo is None and not antes:
            return error("Use la opción de crear hoja.", 400)
        if antes and not puede_ver(request.u, antes):
            if not solo_llegada(request.u, antes) or not puede(request.u, "asistencia"):
                return error("Esta hoja es de otra persona.", 403)
            return guardar_solo_asistencia(c, fid, antes, d)
        admin = request.u["rol"] in ADMINES
        reabre = puede(request.u, "reabrir")
        if antes and antes.get("estado") == "cerrado" and d.get("estado") != "cerrado" and not reabre:
            return error("Solo un administrador puede reabrir una hoja cerrada.", 403)
        if antes and antes.get("estado") == "cerrado" and d.get("estado") == "cerrado" and not reabre:
            sin = lambda fs: [{k: v for k, v in r.items() if k not in ("s", "r", "co")} for r in fs or []]
            if sin(d.get("filas")) != sin(antes.get("filas")):
                return error("La hoja está cerrada. Reábrela para cambiarla.", 409)
        if antes:
            motivo = cambio_restringido(request.u, antes, d)
            if motivo:
                return error(motivo, 403)
        quitar = [k for k in (d.pop("_quitarFirmas", None) or []) if isinstance(k, str)][:400]
        sobrepasa = bool(d.pop("_superaMeta", None))
        d.pop("id", None)
        d.pop("_soloLlegada", None)
        d["act"] = ahora()
        d["actPor"] = request.u["nombre"]
        if not antes:
            d["creadoPor"] = request.u["nombre"]
        d = preparar(c, fid, d, antes)
        metas = leer_registro(c, "catalogo", "metas") or {}
        if not admin and metas.get("modo") == "bloquear" and (not antes or d.get("filas") != antes.get("filas")):
            if any(a["nivel"] == "supera" for a in evaluar_metas(c, fid, d, False)):
                return error("La hoja supera una meta de horas extras fijada por los administradores. Pida a un administrador que la apruebe.", 409)
        if antes and quitar:  # filas cambiadas o quitadas en el editor: su firma ya no vale
            c.execute("delete from hx_firmas where formato=%s and clave = any(%s)", (fid, quitar))
        replicadas = replicar_firmas(c, fid, d)
        guardar_registro(c, "formatos", fid, d)
    out = d if puede(request.u, "valores") else sin_valores("formatos", fid, d)
    return jsonify({"ok": True, "id": fid, "data": out, "replicadas": replicadas})


@app.delete("/api/formatos/<fid>")
@requiere()
def eliminar_formato(fid):
    with pool.connection() as c, c.transaction():
        c.execute("set local lock_timeout = '10s'")
        f = leer_registro(c, "formatos", fid, bloquear=True)
        if not f or f.get("_eliminado") or not puede_ver(request.u, f):
            return error("La hoja no existe.", 404)
        if not puede(request.u, "eliminar"):
            return error("Su rango no permite eliminar hojas.", 403)
        if (f.get("estado") != "borrador" or f.get("pie")) and not puede(request.u, "reabrir"):
            return error("Solo un administrador puede eliminar una hoja firmada o cerrada.", 403)
        c.execute("delete from hx_firmas where formato=%s", (fid,))
        guardar_registro(c, "formatos", fid, {"_eliminado": True})
    return jsonify({"ok": True})


@app.put("/api/catalogo/<doc>")
@requiere("admin")
def guardar_catalogo(doc):
    if doc not in CATALOGOS:
        return error("Catálogo no válido.", 404)
    if doc == "empleados" and not puede_salarios(request.u):
        return error("Los colaboradores y salarios generales los actualiza Recursos Humanos.", 403)
    if doc == "nomina" and not puede_nomina(request.u):
        return error("Solo el administrador de nómina marca revisado y pagado.", 403)
    if doc == "metas" and not puede(request.u, "metas"):
        return error("Su rango no permite definir metas.", 403)
    if doc == "proyectos" and not puede(request.u, "proyectos"):
        return error("Su rango no permite crear o editar proyectos.", 403)
    if doc not in ("empleados", "metas", "nomina", "proyectos") and request.u["rol"] != "principal":
        return error("Solo el administrador principal cambia jornadas, recargos y configuración.", 403)
    d = (request.get_json(silent=True) or {}).get("data")
    if not isinstance(d, dict):
        return error("Datos no válidos.")
    with pool.connection() as c:
        guardar_registro(c, "catalogo", doc, d)
    return jsonify({"ok": True})


def guardar_solo_asistencia(c, fid, antes, d):
    """Toma de lo enviado solo Asistió / No asistió (y quién y cuándo). No asistió borra llegada y salida."""
    nuevas = {r.get("id"): r for r in d.get("filas") or [] if isinstance(r, dict)}
    out, n = json.loads(json.dumps(antes)), 0
    for r in out.get("filas") or []:
        x = nuevas.get(r.get("id"))
        if not x or (x.get("as"), x.get("asPor"), x.get("asT")) == (r.get("as"), r.get("asPor"), r.get("asT")):
            continue
        n += 1
        for k in ("as", "asPor", "asT"):
            if x.get(k) is None:
                r.pop(k, None)
            else:
                r[k] = x[k]
        if r.get("as") == "no":
            for k in ("ll", "sa", "saPor", "saT"):
                r.pop(k, None)
    if n:
        t = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-5))).strftime("%Y-%m-%dT%H:%M:%S")  # como la app
        out["log"] = (out.get("log") or [])[-59:] + [{"t": t, "a": "Marcó asistencia (Llegada)", "d": f"{n} colaboradores", "por": request.u["nombre"]}]
        out["act"] = ahora()
        guardar_registro(c, "formatos", fid, out)
    return jsonify({"ok": True, "id": fid, "data": dict(sin_valores("formatos", fid, out), _soloLlegada=True), "replicadas": 0})


def cambio_restringido(u, antes, d):
    """Revisa los cambios que dependen del rango del usuario. Devuelve el motivo si no se permite."""
    base = lambda fs: [(r.get("id"), r.get("f"), r.get("j"), str(r.get("c")), r.get("hi"), r.get("hf"), r.get("h"))
                       for r in fs or [] if isinstance(r, dict)]
    firmada = antes.get("estado") != "borrador" or bool(antes.get("pie"))
    if firmada and base(d.get("filas")) != base(antes.get("filas")) and not puede(u, "editar"):
        return "Su rango no permite editar hojas ya firmadas."
    if (d.get("conf") or None) != (antes.get("conf") or None) and not puede(u, "confirmar"):
        return "Su rango no permite confirmar hojas."
    if d.get("estado") in ("legalizado", "cerrado") and d.get("estado") != antes.get("estado") and not puede(u, "cerrar"):
        return "Su rango no permite legalizar ni cerrar hojas."
    asis = lambda fs: {r.get("id"): (r.get("ll"), r.get("as")) for r in fs or [] if isinstance(r, dict)}
    a0 = asis(antes.get("filas"))
    if any(v != a0.get(k, (None, None)) for k, v in asis(d.get("filas")).items()) and not puede(u, "asistencia"):
        return "Su rango no permite registrar llegada ni asistencia."
    noAs0 = {r.get("id") for r in d.get("filas") or [] if isinstance(r, dict) and r.get("as") == "no"}
    hrs = lambda fs: {r.get("id"): (r.get("ll"), r.get("sa")) for r in fs or [] if isinstance(r, dict)}
    h0 = hrs(antes.get("filas"))
    if not puede_horas(u, antes) and any(v != h0.get(k, (None, None)) and not (v == (None, None) and k in noAs0)
                                         for k, v in hrs(d.get("filas")).items()):
        return "Las horas de llegada y salida las cambian el responsable de la hoja, los administradores y Nómina."
    sal = lambda fs: {r.get("id"): r.get("sa") for r in fs or [] if isinstance(r, dict)}
    s0, noAs = sal(antes.get("filas")), {r.get("id") for r in d.get("filas") or [] if isinstance(r, dict) and r.get("as") == "no"}
    if any(v != s0.get(k) and not (v is None and k in noAs) for k, v in sal(d.get("filas")).items()) and not puede(u, "salida"):
        return "Su rango no permite registrar la salida."
    return None


def replicar_firmas(c, fid, d):
    """Si un colaborador que ya firmó se repite en la hoja (otro día u otra fila agregada al editar),
    su firma se copia a esas filas. Devuelve cuántas filas recibieron la firma."""
    filas = [r for r in d.get("filas") or [] if isinstance(r, dict) and r.get("id") and r.get("c")]
    firm = dict(d.get("firmadas") or {})
    if not filas or not firm:
        return 0
    hay = {r["clave"]: r["data"] for r in c.execute("select clave,data from hx_firmas where formato=%s", (fid,)).fetchall()}
    de = {}
    for r in filas:
        if firm.get(r["id"]) and r["id"] in hay and str(r["c"]) not in de:
            de[str(r["c"])] = hay[r["id"]]
    n, t = 0, datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-5))).strftime("%Y-%m-%dT%H:%M:%S")  # como la app (Colombia)
    for r in filas:
        if str(r["c"]) in de and not firm.get(r["id"]):
            c.execute("""insert into hx_firmas(formato,clave,data,ts) values(%s,%s,%s,%s)
                         on conflict(formato,clave) do update set data=excluded.data, ts=excluded.ts""",
                      (fid, r["id"], Jsonb(de[str(r["c"])]), ahora()))
            firm[r["id"]] = t
            n += 1
    if n:
        d["firmadas"] = firm
        d["log"] = (d.get("log") or [])[-59:] + [{"t": t, "a": "Replicó firma", "d": f"{n} fila(s) de colaboradores que ya habían firmado",
                                                 "por": request.u["nombre"]}]
    return n


# ---------------------------------------------------------------- foto o escáner del registro de llegada
MODELO_IA = os.environ.get("MODELO_IA", "claude-sonnet-5-5")
HORA = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")


def filas_del_dia(c, u, fecha):
    """Operarios programados ese día en las hojas que el usuario puede ver (igual que la pantalla Llegada)."""
    out = []
    for r in c.execute("select id,data from hx_registros where col='formatos' and not (data ? '_eliminado')").fetchall():
        f = r["data"]
        if f.get("estado") == "legalizado" or not (puede_ver(u, f) or solo_llegada(u, f)):
            continue
        for x in f.get("filas") or []:
            if isinstance(x, dict) and x.get("f") == fecha:
                out.append({"k": f"{r['id']}|{x.get('id')}", "c": str(x.get("c") or ""), "n": x.get("n") or "",
                            "hi": x.get("hi") or "", "hf": x.get("hf") or "", "hoja": f.get("titulo") or ""})
    return out


class BotOcupado(RuntimeError):
    """Google saturado o sin cupo por ahora: la planilla queda en cola y se reintenta sola."""


def _post_json(url, cuerpo, headers, timeout=60):
    req = urllib.request.Request(url, data=json.dumps(cuerpo).encode(), method="POST", headers=dict(headers, **{"content-type": "application/json"}))
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _pedido_ia(fecha, filas):
    lista = "\n".join(f'{x["k"]} | cédula {x["c"]} | {x["n"]} | turno {x["hi"]}-{x["hf"]}' for x in filas)
    return f"""Fecha del registro: {fecha}.
Operarios programados ese día (clave | cédula | nombre | turno programado):
{lista}

La imagen es la planilla física (escrita a mano o impresa) de llegada y salida de horas extras de Unispan Colombia.
Para cada operario programado que aparezca en la planilla, lea la hora de llegada, la de salida y si dice que no asistió.
Relacione por cédula o por nombre (puede estar abreviado o con errores de escritura). Convierta las horas a formato 24 h HH:MM
(7 a. m. = 07:00, 3:30 p. m. = 15:30). No invente: si una hora no se lee con claridad, use null y explíquelo en "nota".
Responda SOLO con este JSON, sin texto adicional:
{{"filas":[{{"clave":"<clave de la lista>","llegada":"HH:MM o null","salida":"HH:MM o null","asistio":true|false|null,"seguridad":"alta|media|baja","nota":""}}],
"no_programados":[{{"nombre":"","cedula":"","llegada":"","salida":""}}],"observaciones":""}}"""


SISTEMA_IA = "Usted transcribe planillas de asistencia con exactitud. Nunca inventa datos."
# Gemini gratis (Google AI Studio): se prueba el primer modelo que exista; Flash-Lite tiene el cupo diario más alto.
MODELOS_GEMINI = [m for m in [os.environ.get("MODELO_GEMINI", "").strip(), "gemini-3.5-flash-lite", "gemini-flash-lite-latest",
                              "gemini-3.1-flash-lite", "gemini-3.8-flash", "gemini-flash-latest"] if m]
GEMINI_URL = os.environ.get("GEMINI_URL", "https://generativelanguage.googleapis.com/v1beta")


def _leer_gemini(clave, tipo, datos_b64, texto, plazo=95):
    cuerpo = {"systemInstruction": {"parts": [{"text": SISTEMA_IA}]},
              "contents": [{"role": "user", "parts": [{"inline_data": {"mime_type": tipo, "data": datos_b64}}, {"text": texto}]}],
              "generationConfig": {"temperature": 0, "responseMimeType": "application/json", "maxOutputTokens": 8000}}
    ultimo, saturado, limite = "", False, time.time() + plazo  # gunicorn corta a los 120 s
    for modelo in [m for m in MODELOS_GEMINI for _ in (0, 1)]:  # dos intentos por modelo
        if time.time() > limite:
            break
        try:
            r = _post_json(f"{GEMINI_URL}/models/{modelo}:generateContent", cuerpo, {"x-goog-api-key": clave},
                           timeout=max(10, min(60, limite - time.time())))
        except urllib.error.HTTPError as e:
            det = e.read().decode(errors="ignore")[:300]
            if e.code == 404:  # ese modelo ya no existe: probar el siguiente
                ultimo = det
                continue
            if e.code in (500, 502, 503, 504):  # Google saturado con ese modelo: probar otro
                saturado, ultimo = True, det
                print(f"Bot Gemini: {modelo} saturado ({e.code}), probando otro", flush=True)
                time.sleep(3)
                continue
            if e.code == 429:
                raise BotOcupado("Se acabó por ahora el cupo gratis de Google (límite por minuto o por día).") from None
            if e.code in (400, 401, 403) and ("API key" in det or "PERMISSION" in det or "API_KEY" in det):
                raise RuntimeError("La clave GEMINI_API_KEY no es válida o no tiene permiso. Revísela en Google AI Studio y en Render.") from None
            raise RuntimeError(f"El bot no pudo leer la foto (error {e.code}). {det}") from None
        except TimeoutError:
            saturado = True
            continue
        except Exception as e:  # noqa: BLE001
            raise RuntimeError(f"El bot no respondió: {e}") from None
        cand = (r.get("candidates") or [{}])[0]
        txt = "".join(p.get("text", "") for p in (cand.get("content") or {}).get("parts") or [])
        if not txt:
            raise RuntimeError("El bot no entregó resultado (" + str(cand.get("finishReason") or r.get("promptFeedback") or "sin texto") + "). Intente con otra foto.")
        print(f"Bot Gemini: modelo {modelo}", flush=True)
        return txt
    if saturado:
        raise BotOcupado("Google está saturado en este momento (le pasa al servicio gratis en horas pico).")
    raise RuntimeError("Ningún modelo gratis de Gemini respondió. Indique uno en la variable MODELO_GEMINI de Render. " + ultimo)


def _leer_claude(clave, tipo, datos_b64, texto):
    bloque = ({"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": datos_b64}} if tipo == "application/pdf"
              else {"type": "image", "source": {"type": "base64", "media_type": tipo, "data": datos_b64}})
    try:
        r = _post_json("https://api.anthropic.com/v1/messages", {"model": MODELO_IA, "max_tokens": 4000, "system": SISTEMA_IA,
                       "messages": [{"role": "user", "content": [bloque, {"type": "text", "text": texto}]}]},
                       {"x-api-key": clave, "anthropic-version": "2023-06-01"})
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"El bot no pudo leer la foto (error {e.code}). {e.read().decode(errors='ignore')[:300]}") from None
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"El bot no respondió: {e}") from None
    return "".join(b.get("text", "") for b in r.get("content") or [] if b.get("type") == "text")


def leer_registro_ia(tipo, datos_b64, fecha, filas, plazo=95):
    """El bot lee la planilla física: Gemini gratis si hay GEMINI_API_KEY; si no, Claude con ANTHROPIC_API_KEY."""
    prueba = os.environ.get("IA_RESPUESTA_PRUEBA")  # solo para pruebas locales sin conexión
    if prueba:
        return json.load(open(prueba, encoding="utf-8"))
    texto = _pedido_ia(fecha, filas)
    g, a = os.environ.get("GEMINI_API_KEY", "").strip(), os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if g:
        txt = _leer_gemini(g, tipo, datos_b64, texto, plazo)
    elif a:
        txt = _leer_claude(a, tipo, datos_b64, texto)
    else:
        raise RuntimeError("El bot no está activado: falta la variable GEMINI_API_KEY en Render. La foto quedó guardada; llene las horas a mano.")
    m = re.search(r"\{.*\}", txt, re.S)
    try:
        res = json.loads(m.group(0)) if m else None
    except ValueError:
        res = None
    if isinstance(res, dict):
        return res
    raise RuntimeError("El bot no entregó un resultado legible. Intente con una foto más clara y derecha.")


def armar_lectura(res, filas):
    """Valida lo que devolvió el bot contra los operarios programados y relaciona los "no programados" que sí lo están."""
    validas = {x["k"] for x in filas}
    hora = lambda v: v if isinstance(v, str) and HORA.match(v.strip()) else None
    prop = []
    for x in res.get("filas") or []:
        k = str(x.get("clave") or "")
        if k in validas and k not in {p["k"] for p in prop}:
            prop.append({"k": k, "ll": hora(x.get("llegada")), "sa": hora(x.get("salida")),
                         "as": {True: "si", False: "no"}.get(x.get("asistio")), "seg": str(x.get("seguridad") or "")[:6],
                         "nota": str(x.get("nota") or "")[:200]})
    digitos = lambda v: re.sub(r"\D", "", str(v or ""))
    nom = lambda v: " ".join(re.sub(r"[^A-Z ]", "", str(v or "").upper().translate(str.maketrans("ÁÉÍÓÚÜÑ", "AEIOUUN"))).split())
    ya, extra = {p["k"] for p in prop}, []
    for x in res.get("no_programados") or []:
        if not isinstance(x, dict):
            continue
        fila = next((f for f in filas if (digitos(x.get("cedula")) and digitos(x.get("cedula")) == digitos(f["c"]))
                     or (nom(x.get("nombre")) and nom(x.get("nombre")) == nom(f["n"]))), None)
        if fila:  # el bot lo puso como no programado, pero sí está programado
            if fila["k"] not in ya:
                ya.add(fila["k"])
                prop.append({"k": fila["k"], "ll": hora(x.get("llegada")), "sa": hora(x.get("salida")), "as": "si" if hora(x.get("llegada")) else None,
                             "seg": "media", "nota": "Relacionado por cédula o nombre"})
            continue
        extra.append({"nombre": str(x.get("nombre") or "")[:80], "cedula": digitos(x.get("cedula"))[:15],
                      "llegada": hora(x.get("llegada")), "salida": hora(x.get("salida"))})
    return {"propuestas": prop, "extra": extra[:40], "obs": str(res.get("observaciones") or "")[:500]}


def _info_foto(c, fid, **cambios):
    c.execute("update hx_fotos set info = info || %s where id=%s", (Jsonb(cambios), fid))


def leer_foto(fid, plazo):
    """Lee una foto guardada con el bot. Devuelve el resultado, o deja la foto en cola o con error."""
    with pool.connection() as c:
        r = c.execute("select fecha,tipo,img,info from hx_fotos where id=%s", (fid,)).fetchone()
    if not r:
        return None
    info = r["info"] or {}
    u = usuario_por_id(info.get("usuario"))
    if not u or u["estado"] != "activo":
        with pool.connection() as c:
            _info_foto(c, fid, estado="error", error="El usuario que tomó la foto ya no está activo.")
        return None
    with pool.connection() as c:
        filas = filas_del_dia(c, u, r["fecha"])
    if not filas:
        with pool.connection() as c:
            _info_foto(c, fid, estado="error", error="Ya no hay operarios programados ese día.")
        return None
    try:
        res = armar_lectura(leer_registro_ia(r["tipo"], r["img"].split(",", 1)[1], r["fecha"], filas, plazo), filas)
    except BotOcupado as e:
        n = int(info.get("intentos") or 0) + 1
        espera = min(15 * 60, 60 * 2 ** min(n - 1, 4))  # 1, 2, 4, 8 y luego cada 15 minutos
        with pool.connection() as c:
            if n > 40:  # unas 8 horas intentando
                _info_foto(c, fid, estado="error", intentos=n, error=str(e) + " No se pudo leer en todo el día; vuelva a intentarlo.")
            else:
                _info_foto(c, fid, estado="cola", intentos=n, proximo=ahora() + espera * 1000, error=str(e))
        return None
    except RuntimeError as e:
        with pool.connection() as c:
            _info_foto(c, fid, estado="error", error=str(e))
        return None
    with pool.connection() as c:
        _info_foto(c, fid, estado="leida", leidas=len(res["propuestas"]), lectura=res, error=None, leidaTs=ahora())
    return dict(res, filas=filas)


def ciclo_cola_bot():
    """Hilo en segundo plano: reintenta las planillas que quedaron en cola porque Google estaba ocupado."""
    while True:
        time.sleep(45)
        try:
            with pool.connection() as c:
                ids = [r["id"] for r in c.execute("""select id from hx_fotos where info->>'estado'='cola'
                       and coalesce((info->>'proximo')::bigint,0) <= %s order by ts limit 3""", (ahora(),)).fetchall()]
            for fid in ids:
                leer_foto(fid, 90)
                time.sleep(8)  # respeta el cupo por minuto del servicio gratis
        except Exception as e:  # noqa: BLE001
            print(f"Cola del bot: {e}", flush=True)


threading.Thread(target=ciclo_cola_bot, daemon=True, name="cola-bot").start()


def guardian_bloqueos():
    """Cada 20 s revisa si alguna consulta de la app lleva más de 25 s esperando un bloqueo. Si quien la bloquea es una
    sesión que quedó abierta sin hacer nada ("idle in transaction", por ejemplo de un despliegue anterior que se cortó)
    o una consulta de estas tablas que lleva más de 2 minutos, la termina para que la app no se quede trabada."""
    while True:
        time.sleep(20)
        try:
            with psycopg.connect(URL_BD, connect_timeout=8, prepare_threshold=None, **TCP_VIVO, autocommit=True, row_factory=dict_row) as cx:
                cx.execute("set statement_timeout = '8s'")
                rs = cx.execute("""
                    select w.pid wpid, b.pid bpid, b.state bstate,
                           extract(epoch from now() - coalesce(b.state_change, b.query_start))::int bseg,
                           extract(epoch from now() - b.query_start)::int bqseg,
                           left(regexp_replace(w.query, '\s+', ' ', 'g'), 70) wq, left(regexp_replace(b.query, '\s+', ' ', 'g'), 70) bq
                    from pg_stat_activity w
                    cross join lateral unnest(pg_blocking_pids(w.pid)) bp(pid)
                    join pg_stat_activity b on b.pid = bp.pid
                    where w.datname = current_database() and w.wait_event_type = 'Lock'
                      and w.query ilike '%%hx_%%' and now() - w.query_start > interval '25 seconds'""").fetchall()
                hechos = set()
                for r in rs:
                    ocioso = (r["bstate"] or "").startswith("idle in transaction") and r["bseg"] > 20
                    largo = r["bstate"] == "active" and r["bqseg"] > 120 and "hx_" in (r["bq"] or "")
                    if (ocioso or largo) and r["bpid"] not in hechos:
                        hechos.add(r["bpid"])
                        cx.execute("select pg_terminate_backend(%s)", (r["bpid"],))
                        print(f"GUARDIÁN: se terminó la sesión {r['bpid']} ({r['bstate']}, {r['bseg']} s, «{r['bq']}») que trababa «{r['wq']}»", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"Guardián de bloqueos: {e}", flush=True)


threading.Thread(target=guardian_bloqueos, daemon=True, name="guardian").start()


@app.post("/api/llegada/escanear")
@requiere()
def escanear_llegada():
    u = request.u
    if not (puede(u, "asistencia") or puede(u, "salida")):
        return error("Su rango no permite registrar llegada ni salida.", 403)
    d = request.get_json(silent=True) or {}
    fecha, img = str(d.get("fecha") or "")[:10], str(d.get("img") or "")
    m = re.match(r"^data:(image/(?:jpeg|png|webp)|application/pdf);base64,(.+)$", img, re.S)
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", fecha) or not m:
        return error("Envíe una foto (JPG o PNG) o un PDF del registro.")
    with pool.connection() as c:
        if not filas_del_dia(c, u, fecha):
            return error("No hay operarios programados ese día para relacionar con la foto.")
    fid = "ft" + uuid.uuid4().hex[:10]
    with pool.connection() as c:  # la foto queda guardada aunque el bot falle
        c.execute("insert into hx_fotos(id,fecha,por,ts,tipo,img,info) values(%s,%s,%s,%s,%s,%s,%s)",
                  (fid, fecha, u["nombre"], ahora(), m.group(1), img, Jsonb({"usuario": u["id"], "estado": "leyendo"})))
    res = leer_foto(fid, 70)
    if res:
        return jsonify(dict(res, ok=True, foto=fid))
    with pool.connection() as c:
        info = c.execute("select info from hx_fotos where id=%s", (fid,)).fetchone()["info"]
    if info.get("estado") == "cola":
        return jsonify({"ok": False, "cola": True, "foto": fid, "error": info.get("error")})
    return jsonify({"ok": False, "foto": fid, "error": info.get("error") or "El bot no pudo leer la foto."})


@app.get("/api/llegada/fotos/<fid>/lectura")
@requiere()
def lectura_foto(fid):
    with pool.connection() as c:
        r = c.execute("select fecha,info from hx_fotos where id=%s", (fid,)).fetchone()
        if not r or not (puede(request.u, "todos") or (r["info"] or {}).get("usuario") == request.u["id"]):
            return error("No se encontró la foto.", 404)
        if not (r["info"] or {}).get("lectura"):
            return error("Esta planilla todavía no se ha leído.")
        filas = filas_del_dia(c, request.u, r["fecha"])
    lec, validas = r["info"]["lectura"], {x["k"] for x in filas}
    return jsonify(dict(lec, ok=True, foto=fid, filas=filas, propuestas=[p for p in lec.get("propuestas") or [] if p["k"] in validas]))


@app.post("/api/llegada/fotos/<fid>/<accion>")
@requiere()
def accion_foto(fid, accion):
    with pool.connection() as c:
        r = c.execute("select info from hx_fotos where id=%s", (fid,)).fetchone()
        if not r or not (puede(request.u, "todos") or (r["info"] or {}).get("usuario") == request.u["id"]):
            return error("No se encontró la foto.", 404)
        if accion == "reintentar":
            _info_foto(c, fid, estado="cola", proximo=0, error=None)
        elif accion == "aplicada":
            _info_foto(c, fid, aplicada=ahora(), aplicadaPor=request.u["nombre"])
        else:
            return error("Acción no válida.")
    return jsonify({"ok": True})


@app.get("/api/llegada/fotos")
@requiere()
def fotos_llegada():
    fecha = str(request.args.get("fecha") or "")[:10]
    with pool.connection() as c:
        rs = c.execute("select id,fecha,por,ts,tipo,info from hx_fotos where fecha=%s order by ts", (fecha,)).fetchall()
    vis = [r for r in rs if puede(request.u, "todos") or (r["info"] or {}).get("usuario") == request.u["id"]]
    campos = ("leidas", "estado", "intentos", "proximo", "error", "aplicada")
    return jsonify({"fotos": [dict(id=r["id"], por=r["por"], ts=r["ts"], tipo=r["tipo"], **{k: (r["info"] or {}).get(k) for k in campos}) for r in vis]})


@app.get("/api/llegada/fotos/<fid>")
@requiere()
def foto_llegada(fid):
    with pool.connection() as c:
        r = c.execute("select img,info from hx_fotos where id=%s", (fid,)).fetchone()
    if not r or not (puede(request.u, "todos") or (r["info"] or {}).get("usuario") == request.u["id"]):
        return error("No se encontró la foto.", 404)
    return jsonify({"img": r["img"]})


@app.delete("/api/llegada/fotos/<fid>")
@requiere()
def borrar_foto_llegada(fid):
    with pool.connection() as c:
        r = c.execute("select info from hx_fotos where id=%s", (fid,)).fetchone()
        if not r or not (puede(request.u, "reabrir") or (r["info"] or {}).get("usuario") == request.u["id"]):
            return error("No puede eliminar esta foto.", 403)
        c.execute("delete from hx_fotos where id=%s", (fid,))
    return jsonify({"ok": True})


# ---------------------------------------------------------------- firmas
@app.get("/api/firmas/<fid>")
@requiere()
def firmas(fid):
    with pool.connection() as c:
        if not puede_ver(request.u, leer_registro(c, "formatos", fid)):
            return error("Esta hoja es de otra persona.", 403)
        rows = c.execute("select clave,data from hx_firmas where formato=%s", (fid,)).fetchall()
    return jsonify({"firmas": {r["clave"]: r["data"] for r in rows}})


@app.post("/api/firmas/<fid>/<clave>")
@requiere()
def firmar(fid, clave):
    d = request.get_json(silent=True) or {}
    img = d.get("img")
    if not isinstance(img, str) or not img.startswith("data:image/png;base64,") or len(img) > 600_000:
        return error("La firma no es válida.")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", clave):
        return error("Firma no válida.")
    with pool.connection() as c, c.transaction():
        c.execute("set local lock_timeout = '10s'")
        f = leer_registro(c, "formatos", fid)
        if not f or f.get("_eliminado") or not puede_ver(request.u, f):
            return error("La hoja no existe.", 404)
        filas = {r.get("id") for r in f.get("filas") or []}
        claves = [clave] + [k for k in (d.get("tambien") or []) if isinstance(k, str)]
        if any(k not in ROLES_FIRMA and k not in filas for k in claves):
            return error("La fila ya no existe.", 404)
        data = {"img": img, "w": int(num(d.get("w"), 300)), "h": int(num(d.get("h"), 100)),
                "nombre": (d.get("nombre") or "")[:120], "cargo": (d.get("cargo") or "")[:120],
                "fecha": d.get("fecha") or "", "por": request.u["nombre"]}
        # Una sola firma del colaborador se copia a todos sus días de la hoja.
        for k in claves[:200]:
            c.execute("""insert into hx_firmas(formato,clave,data,ts) values(%s,%s,%s,%s)
                         on conflict(formato,clave) do update set data=excluded.data, ts=excluded.ts""",
                      (fid, k, Jsonb(data), ahora()))
    return jsonify({"ok": True})


@app.delete("/api/firmas/<fid>/<clave>")
@requiere()
def quitar_firma(fid, clave):
    with pool.connection() as c:
        f = leer_registro(c, "formatos", fid)
        if not puede_ver(request.u, f):
            return error("Esta hoja es de otra persona.", 403)
        if f and f.get("estado") == "cerrado" and not puede(request.u, "reabrir"):
            return error("La hoja está cerrada.", 409)
        c.execute("delete from hx_firmas where formato=%s and clave=%s", (fid, clave))
    return jsonify({"ok": True})


paso_inicio(recalcular_totales)  # al final: usa normalizar_formato


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
