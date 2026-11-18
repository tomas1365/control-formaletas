"""Horas Extras Unispan — servidor.

Misma base que la Bitácora de Herramientas: ingreso con usuario y clave propios,
el primer administrador se crea con el CODIGO_INSTALACION y las demás personas
solicitan acceso. Los datos quedan en Postgres (Supabase) en tablas que empiezan
por hx_, así puede compartir la misma base con la Bitácora sin mezclarse.
"""
import datetime
import json
import os
import re
import time
import uuid
import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken
from functools import wraps

import psycopg
from flask import Flask, jsonify, request, send_from_directory, session
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool
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
    MAX_CONTENT_LENGTH=4 * 1024 * 1024,
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


probar_base_de_datos(os.environ["DATABASE_URL"].strip())

pool = ConnectionPool(
    os.environ["DATABASE_URL"].strip(),
    min_size=1,
    max_size=5,
    kwargs={"row_factory": dict_row, "autocommit": True, "prepare_threshold": None},
    open=True,
)

MAX_INTENTOS = 5
BLOQUEO_MS = 15 * 60 * 1000
ROLES_FIRMA = ("ELABORA", "AUTORIZA", "LIQUIDA")
ESTADOS = ("borrador", "firmado", "legalizado", "cerrado")
CATALOGOS = ("empleados", "jornadas", "config", "metas")
# Roles: principal (quien instaló la app; cambia estructura y forma y aprueba accesos),
# admin (ve y edita salarios, recargos y costos) y operario (usuario: registra y firma, sin valores).
ROLES = ("principal", "admin", "operario")
ADMINES = ("principal", "admin")


def ahora():
    return int(time.time() * 1000)


def crear_tablas():
    with pool.connection() as c:
        c.execute("""
        create table if not exists hx_usuarios(
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
        );
        create table if not exists hx_registros(
            col text not null,
            id text not null,
            data jsonb not null,
            actualizado bigint not null,
            primary key(col, id)
        );
        create index if not exists hx_registros_act on hx_registros(actualizado);
        create table if not exists hx_firmas(
            formato text not null,
            clave text not null,
            data jsonb not null,
            ts bigint not null,
            primary key(formato, clave)
        );
        """)


def cargar_datos_iniciales():
    """La primera vez (base vacía) carga los colaboradores y las hojas del libro Excel."""
    ruta = os.path.join(BASE, "datos_iniciales.json")
    if not os.path.exists(ruta):
        return
    with pool.connection() as c, c.transaction():
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


def usuario_actual():
    uid = session.get("uid")
    if not uid:
        return None
    with pool.connection() as c:
        u = c.execute("select id,nombre,usuario,rol,estado,rrhh from hx_usuarios where id=%s", (uid,)).fetchone()
    if not u or u["estado"] != "activo":
        session.clear()
        return None
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
    return dict({k: u[k] for k in ("id", "nombre", "usuario", "rol", "estado")}, rrhh=puede_salarios(u))


def puede_salarios(u):
    """Los salarios generales los actualiza Recursos Humanos (y el administrador principal)."""
    return u["rol"] == "principal" or (u["rol"] == "admin" and bool(u.get("rrhh")))


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


def asignar_sin_responsable(c, uid, nombre):
    """Las horas extras que ya existían (cargadas antes de haber libros por persona) son del administrador principal."""
    c.execute("""update hx_registros set data = data || jsonb_build_object('dueno', %s::text, 'duenoNombre', %s::text),
                 actualizado=%s where col='formatos' and not (data ? '_eliminado') and coalesce(data->>'dueno','')=''""",
              (uid, nombre, ahora()))


def asegurar_principal():
    """Versiones anteriores solo tenían 'admin': el administrador más antiguo pasa a ser el principal."""
    with pool.connection() as c, c.transaction():
        c.execute("lock table hx_usuarios in exclusive mode")
        if not c.execute("select 1 from hx_usuarios where rol='principal' limit 1").fetchone():
            c.execute("""update hx_usuarios set rol='principal' where id=(
                         select id from hx_usuarios where rol='admin' order by creado limit 1)""")
        p = c.execute("select id,nombre from hx_usuarios where rol='principal' limit 1").fetchone()
        if p:
            asignar_sin_responsable(c, p["id"], p["nombre"])


def migrar_usuarios():
    with pool.connection() as c:
        c.execute("alter table hx_usuarios add column if not exists clave_ver text")
        c.execute("alter table hx_usuarios add column if not exists ultimo_ingreso bigint")
        c.execute("alter table hx_usuarios add column if not exists rrhh boolean not null default false")


def recalcular_totales():
    """Separa el recargo nocturno de los totales en las hojas guardadas con versiones anteriores."""
    with pool.connection() as c, c.transaction():
        for r in c.execute("select id,data from hx_registros where col='formatos'").fetchall():
            f = r["data"]
            if f.get("_eliminado") or "rh" in f:
                continue
            c.execute("update hx_registros set data=%s where col='formatos' and id=%s", (Jsonb(normalizar_formato(f)), r["id"]))


crear_tablas()
migrar_usuarios()
asegurar_principal()
cargar_datos_iniciales()


# ---------------------------------------------------------------- páginas
@app.get("/")
def inicio():
    return send_from_directory(BASE, "index.html", max_age=0)


@app.get("/manifest.json")
def manifest():
    return jsonify({
        "id": "/",
        "name": "Horas Extras Unispan",
        "short_name": "Horas Extras",
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
        c.execute("lock table hx_usuarios in exclusive mode")
        if c.execute("select 1 from hx_usuarios where rol in ('principal','admin') limit 1").fetchone():
            return error("La app ya tiene administrador. Ingresa con tu usuario.", 409)
        uid = uuid.uuid4().hex
        c.execute("insert into hx_usuarios(id,nombre,usuario,clave,rol,estado,creado,ultimo_ingreso) values(%s,%s,%s,%s,'principal','activo',%s,%s)",
                  (uid, nombre, usuario, generate_password_hash(clave), ahora(), ahora()))
        asignar_sin_responsable(c, uid, nombre)
    session.clear(); session.permanent = True; session["uid"] = uid
    return jsonify({"ok": True})


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
        rows = c.execute("""select id,nombre,usuario,rol,estado,creado,ultimo_ingreso,rrhh,
                            (clave_ver is not null) as clave_visible from hx_usuarios order by estado='pendiente' desc, nombre""").fetchall()
    return jsonify({"usuarios": rows})


@app.delete("/api/usuarios/<uid>")
@requiere("principal")
def eliminar_usuario(uid):
    """Elimina un usuario. Sus hojas pasan al libro del administrador principal, o se eliminan si así se pide."""
    hojas = (request.args.get("hojas") or "pasar")
    with pool.connection() as c, c.transaction():
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
    if not usuario or not nombre:
        return error("Escribe el nombre y un usuario.")
    if not re.fullmatch(r"[a-z0-9._-]{3,30}", usuario):
        return error("El usuario debe tener de 3 a 30 letras o números, sin espacios.")
    if (m := validar_clave(clave)):
        return error(m)
    with pool.connection() as c:
        if c.execute("select 1 from hx_usuarios where usuario=%s", (usuario,)).fetchone():
            return error("Ese usuario ya existe. Elige otro.", 409)
        c.execute("insert into hx_usuarios(id,nombre,usuario,clave,rol,estado,creado,aprobado_por,clave_ver,rrhh) values(%s,%s,%s,%s,%s,'activo',%s,%s,%s,%s)",
                  (uuid.uuid4().hex, nombre[:80], usuario, generate_password_hash(clave), rol, ahora(), request.u["id"], cifrar(clave), rrhh))
    return jsonify({"ok": True})


@app.post("/api/usuarios/<uid>")
@requiere("principal")
def gestionar_usuario(uid):
    d = request.get_json(silent=True) or {}
    accion = d.get("accion")
    with pool.connection() as c, c.transaction():
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
            c.execute("update hx_usuarios set nombre=%s, usuario=%s, rol=%s, rrhh=%s where id=%s", (nombre[:80], usuario, rol, rrhh, uid))
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
        rows = c.execute("select col,id,data from hx_registros where actualizado>%s", (desde - 2000 if desde else -1,)).fetchall()
    out = {}
    ver = request.u["rol"] in ADMINES
    for r in rows:
        data = r["data"]
        if r["col"] == "formatos" and not data.get("_eliminado") and not puede_ver(request.u, data):
            data = {"_eliminado": True}  # no es suya (o se reasignó a otra persona)
        out.setdefault(r["col"], {})[r["id"]] = data if ver else sin_valores(r["col"], r["id"], data)
    return jsonify({"registros": out, "ahora": marca, "yo": publico(request.u)})


def puede_ver(u, f):
    """Los administradores ven todo el libro; cada usuario ve solo las hojas de las que es responsable."""
    return u["rol"] in ADMINES or (f or {}).get("dueno") == u["id"]


def sin_valores(col, rid, data):
    """Copia sin salarios, recargos ni costos, para usuarios que no son administradores."""
    if col == "formatos" and not data.get("_eliminado"):
        data = {k: v for k, v in data.items() if k not in ("div", "tc", "rc")}
        data["filas"] = [{k: v for k, v in r.items() if k not in ("s", "r", "co")} for r in data.get("filas") or []]
    elif col == "catalogo" and rid == "empleados":
        data = dict(data, lista=[e[:3] + [None] + e[4:] for e in data.get("lista") or []])
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
        if admin and d.get("dueno") and d.get("dueno") != antes.get("dueno"):
            dueno = d["dueno"], d.get("duenoNombre")
    else:
        dueno = request.u["id"], request.u["nombre"]
        if admin and d.get("dueno") and d["dueno"] != request.u["id"]:
            otro = c.execute("select id,nombre from hx_usuarios where id=%s and estado='activo'", (d["dueno"],)).fetchone()
            if otro:
                dueno = otro["id"], otro["nombre"]  # el administrador carga la hoja en el libro de esa persona
    d["dueno"], d["duenoNombre"] = dueno
    d = completar_valores(c, d, antes, confiar=admin)
    return normalizar_formato(d)


@app.post("/api/formatos")
@requiere()
def crear_formato():
    """Crea una hoja nueva; el número lo asigna el servidor para que no se repita entre usuarios."""
    d = (request.get_json(silent=True) or {}).get("data")
    if not isinstance(d, dict):
        return error("Datos no válidos.")
    with pool.connection() as c, c.transaction():
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
        alertas = evaluar_metas(c, fid, d, request.u["rol"] in ADMINES)
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
        antes = leer_registro(c, "formatos", fid, bloquear=True)
        if antes and antes.get("_eliminado"):
            antes = None
        if nuevo is None and not antes:
            return error("Use la opción de crear hoja.", 400)
        if antes and not puede_ver(request.u, antes):
            return error("Esta hoja es de otra persona.", 403)
        admin = request.u["rol"] in ADMINES
        if antes and antes.get("estado") == "cerrado" and d.get("estado") != "cerrado" and not admin:
            return error("Solo un administrador puede reabrir una hoja cerrada.", 403)
        if antes and antes.get("estado") == "cerrado" and d.get("estado") == "cerrado" and not admin:
            sin = lambda fs: [{k: v for k, v in r.items() if k not in ("s", "r", "co")} for r in fs or []]
            if sin(d.get("filas")) != sin(antes.get("filas")):
                return error("La hoja está cerrada. Reábrela para cambiarla.", 409)
        sobrepasa = bool(d.pop("_superaMeta", None))
        d.pop("id", None)
        d["act"] = ahora()
        d["actPor"] = request.u["nombre"]
        if not antes:
            d["creadoPor"] = request.u["nombre"]
        d = preparar(c, fid, d, antes)
        metas = leer_registro(c, "catalogo", "metas") or {}
        if not admin and metas.get("modo") == "bloquear" and (not antes or d.get("filas") != antes.get("filas")):
            if any(a["nivel"] == "supera" for a in evaluar_metas(c, fid, d, False)):
                return error("La hoja supera una meta de horas extras fijada por los administradores. Pida a un administrador que la apruebe.", 409)
        guardar_registro(c, "formatos", fid, d)
    out = d if admin else sin_valores("formatos", fid, d)
    return jsonify({"ok": True, "id": fid, "data": out})


@app.delete("/api/formatos/<fid>")
@requiere()
def eliminar_formato(fid):
    with pool.connection() as c, c.transaction():
        f = leer_registro(c, "formatos", fid, bloquear=True)
        if not f or f.get("_eliminado") or not puede_ver(request.u, f):
            return error("La hoja no existe.", 404)
        if (f.get("estado") != "borrador" or f.get("pie")) and request.u["rol"] not in ADMINES:
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
    if doc not in ("empleados", "metas") and request.u["rol"] != "principal":
        return error("Solo el administrador principal cambia jornadas, recargos y configuración.", 403)
    d = (request.get_json(silent=True) or {}).get("data")
    if not isinstance(d, dict):
        return error("Datos no válidos.")
    with pool.connection() as c:
        guardar_registro(c, "catalogo", doc, d)
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
        if f and f.get("estado") == "cerrado" and request.u["rol"] not in ADMINES:
            return error("La hoja está cerrada.", 409)
        c.execute("delete from hx_firmas where formato=%s and clave=%s", (fid, clave))
    return jsonify({"ok": True})


recalcular_totales()  # al final: usa normalizar_formato


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
