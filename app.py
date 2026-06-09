import streamlit as st
import sqlite3
from datetime import datetime

# Configuración de página amigable para celular
st.set_page_config(page_title="Control Formaletas", page_icon="🏗️", layout="centered")

# Función para conectar a la base de datos
def conectar_db():
    conn = sqlite3.connect("formaletas.db")
    return conn

# Crear tablas e insertar catálogo inicial si no existen
def inicializar_db():
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Tabla colaboradores
    cursor.execute('''CREATE TABLE IF NOT EXISTS colaboradores (
                        id_operario INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL)''')
    
    # Tabla catálogo
    cursor.execute('''CREATE TABLE IF NOT EXISTS catalogo (
                        id_ref INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL,
                        area_m2 REAL NOT NULL)''')
    
    # Tabla registros
    cursor.execute('''CREATE TABLE IF NOT EXISTS registros (
                        id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha TEXT,
                        operario TEXT,
                        codigo TEXT,
                        referencia TEXT,
                        area_m2 REAL,
                        defectos TEXT)''')
    
    # Insertar operarios de prueba si está vacía
    cursor.execute("SELECT COUNT(*) FROM colaboradores")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO colaboradores (nombre) VALUES (?)", 
                           [("Juan Pérez",), ("Carlos Gómez",), ("Andrés Cortés",)])
        
    # Insertar referencias clave si está vacía
    cursor.execute("SELECT COUNT(*) FROM catalogo")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO catalogo (nombre, area_m2) VALUES (?,?)", [
            ("PM 2400x600 (Estándar)", 1.44),
            ("PM 750x600 (Estándar)", 0.45),
            ("PM 2400x120 (Angosto)", 0.288),
            ("PM 2400x80 (Angosto)", 0.192),
            ("EI 2400 (Esquinero)", 0.720),
            ("EI 1200 (Esquinero)", 0.360)
        ])
    conn.commit()
    conn.close()

inicializar_db()

# --- INTERFAZ DE LA APLICACIÓN ---
st.title("🏗️ Registro de Formaletas")
st.write("Control de reparación y trazabilidad")

conn = conectar_db()
cursor = conn.cursor()

# Obtener listas para los menús desplegables
cursor.execute("SELECT nombre FROM colaboradores")
lista_operarios = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT nombre, area_m2 FROM catalogo")
datos_catalogo = cursor.fetchall()
lista_referencias = [row[0] for row in datos_catalogo]
diccionario_areas = {row[0]: row[1] for row in datos_catalogo}

conn.close()

# Formulario de registro
with st.form("formulario_registro", clear_on_submit=True):
    st.subheader("Nuevo Registro de Mantenimiento")
    
    operario_sel = st.selectbox("1. Selecciona el Colaborador:", lista_operarios)
    
    codigo_sel = st.text_input("2. Código de la Formaleta (1-3 dígitos):", placeholder="Ej: 123")
    
    ref_sel = st.selectbox("3. Tipo de Pieza / Referencia:", lista_referencias)
    
    defectos_sel = st.multiselect("4. Defectos detectados (puedes elegir varios):", 
                                  ["Soldadura desprendida", "Ondulación de lámina", "Refuerzo deformado", "Ninguno"])
    
    # Botón grande para enviar desde el celular
    boton_guardar = st.form_submit_submit_button("💾 GUARDAR REPARACIÓN", use_container_width=True)

if boton_guardar:
    if not codigo_sel:
        st.error("⚠️ Por favor ingresa el código de la formaleta.")
    else:
        area_calculada = diccionario_areas[ref_sel]
        defectos_texto = ", ".join(defectos_sel) if defectos_sel else "Ninguno"
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Guardar en base de datos
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO registros (fecha, operario, codigo, referencia, area_m2, defectos) 
                          VALUES (?, ?, ?, ?, ?, ?)''', 
                       (fecha_actual, operario_sel, codigo_sel, ref_sel, area_calculada, defectos_texto))
        conn.commit()
        conn.close()
        
        st.success(f"✔️ ¡Registrado! Se sumaron {area_calculada} m² a {operario_sel}")

# --- HISTORIAL RÁPIDO ---
st.markdown("---")
st.subheader("📋 Últimas Reparaciones del Turno")
conn = conectar_db()
cursor = conn.cursor()
cursor.execute("SELECT fecha, operario, codigo, referencia, area_m2 FROM registros ORDER BY id_registro DESC LIMIT 5")
ultimos_registros = cursor.fetchall()
conn.close()

if ultimos_registros:
    for reg in ultimos_registros:
        st.info(f"**{reg[1]}** reparó **{reg[3]}** (Cod: {reg[2]}) -> **{reg[4]} m²** \n_Fecha: {reg[0]}_")
else:
    st.caption("No hay reparaciones registradas el día de hoy.")
