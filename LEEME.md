# Horas Extras · Unispan

App web para registrar, firmar y legalizar horas extras con el formato
"REPORTE DE NOVEDADES HORAS EXTRAS". Funciona igual que la Bitácora de Herramientas:
Render + Supabase, ingreso con usuario y clave propios, desde el celular o el PC.

## Archivos
- `app.py` – servidor (Flask), igual a la Bitácora.
- `index.html` – la aplicación.
- `render.yaml`, `requirements.txt` – configuración de Render.
- `datos_iniciales.json` – 115 colaboradores y las 12 hojas del libro Excel. Se cargan solos la primera vez.
- `logo.jpg` – logo para el PDF y el Excel.
- `sw.js` e `icono-*.png` – permiten instalarla como app en el celular (ícono de Unispan).

**El repositorio debe ser PRIVADO**: `datos_iniciales.json` tiene cédulas y salarios.

## Publicar (10 minutos)
1. **GitHub** → New repository → nombre `Horas-Extras` → **Private** → Create.
   Luego "uploading an existing file", arrastre los 6 archivos y "Commit changes".
2. **Render** → New + → **Blueprint** → elija el repositorio `Horas-Extras` → Apply.
   (O New + → Web Service, con los mismos comandos de `render.yaml`.)
3. En Render, pestaña **Environment**, ponga:
   - `DATABASE_URL`: la **misma** de la Bitácora (Session pooler de Supabase).
     Las tablas de esta app empiezan por `hx_` y no tocan las de la Bitácora.
   - `CODIGO_INSTALACION`: un código nuevo que solo usted conozca.
   - `SECRET_KEY` se genera solo.
4. Abra la dirección que da Render (ej. `https://horas-extras.onrender.com`),
   escriba el código de instalación y cree su usuario. Ese usuario queda como **administrador principal**.
5. **App en el celular**: abra la dirección en Chrome (Android) y toque **Instalar** en el aviso azul,
   o menú ⋮ → **Instalar app**. En iPhone: Safari → Compartir → **Agregar a pantalla de inicio**.
   Queda con el ícono de Unispan y se abre en pantalla completa, como una app.

## Uso
1. **Registro**: Nuevo → Autorización o Legalización → "Agregar varios colaboradores"
   (misma fecha, jornada, horario y actividad) o fila por fila.
2. **Firmas**: cada colaborador firma su fila ("Firmar uno tras otro" en la tableta) y
   firman Elabora, Autoriza y Liquida GH. Con Elabora y Autoriza la hoja queda firmada.
3. **Legalización**: la autorización firmada se legaliza, se ajustan las horas reales,
   se firman y se **cierra y archiva** en el libro.
- **Imprimir**, **PDF** y **Excel** preguntan el tamaño de hoja (Carta, Oficio 21,6 × 33, Legal, A4, A3) y la orientación.
  El tamaño por defecto se define en Ajustes → Impresión. Cada hoja sale completa en **una sola página**
  (la letra y las filas se reducen solas cuando hay muchas filas).
- **Excel** descarga el libro con una pestaña por hoja (nombrada con las fechas) y un resumen; cada pestaña
  está configurada para imprimirse en una sola página.
- **Actualizar desde Excel** (Libro o Personal, solo administrador): suba `FORMATO HORAS EXTRAS TOMAS.xlsm`.
  De la hoja BD se actualizan los colaboradores y de cada hoja con fechas se crean o actualizan los formatos
  (se reconocen por el nombre de la pestaña). Antes de aplicar se muestra un resumen. **Las firmas se conservan**: las filas
  que no cambian mantienen su firma, los días nuevos de un colaborador que ya firmó reciben la misma firma y
  las firmas del pie se mantienen. Solo las hojas ya legalizadas no se tocan, y la plantilla
  "FORMATO PARA DILIGENCIAR" se ignora.
- Otras personas piden acceso desde la pantalla de ingreso (o usted las crea con su clave); usted las aprueba en el menú Accesos.

## Niveles de acceso
| Nivel | Qué puede hacer |
|---|---|
| **Usuario** | Registra, firma, legaliza y descarga. No ve salarios, recargos ni costos: el servidor no se los envía y calcula los costos por él. |
| **Administrador** | Además ve y edita salarios, recargos y costos, el Personal y la actualización desde Excel. Al descargar elige si incluye los valores. |
| **Administrador principal** | Quien instaló la app. Además es el único que cambia jornadas, recargos, divisor, firmantes, el formato de impresión y los accesos. |

En el menú Accesos el principal crea accesos, y con **Editar o cambiar clave** cambia nombre, usuario, nivel y clave
(botón **Generar** para una clave nueva). La clave se muestra al crearla o cambiarla, con botones para copiar o
enviar por WhatsApp, y queda disponible en el botón Ver mientras la persona no la cambie. Si alguien la olvida, se le asigna una nueva.

Si la app ya estaba publicada, al actualizar el administrador más antiguo pasa a ser el principal automáticamente.

## Accesos (solo el administrador principal)
Menú **Accesos**: administradores y usuarios en grupos separados, con último ingreso y número de hojas de cada uno.
- **Crear** un administrador o usuario con su clave (o **Generar** una). Se muestra para copiarla o enviarla por WhatsApp.
- Las claves asignadas antes de esta versión no se pueden ver: el botón **Asignar claves nuevas** les da una clave nueva
  a todas esas personas de una vez y muestra la lista para enviarla.
- **Ver** la clave de cada persona: las claves que usted asigna se guardan cifradas y solo usted puede verlas. Si la persona
  cambia su clave desde Mi cuenta, la copia se borra y ya no se puede ver (usted puede asignarle otra en cualquier momento).
- **Editar o cambiar clave**: nombre, usuario, nivel y clave.
- **Cargar su libro Excel**: usted carga una sola vez el libro de cada persona; las hojas quedan en el libro de ella y desde
  ahí la persona sigue registrando. Si alguna hoja de ese Excel ya está registrada en otro libro (por ejemplo en el suyo),
  no se carga dos veces.

## Recargo nocturno (registro aparte)
Las filas de **Recargo Nocturno** (jornada RN) no son horas extras: no suman en el total de horas extras de la hoja, del
libro ni de los informes, no aparecen en las gráficas y no disparan las metas. Se muestran aparte: una fila
"RECARGO NOCTURNO" debajo del total en la hoja, el PDF y el Excel; un indicador propio en el Libro y en Informes; y columnas
propias en el consolidado.

## Salarios generales: Recursos Humanos
- En Accesos, al crear o editar un **administrador**, marque **Recursos Humanos**. Solo esas personas (y el administrador
  principal) actualizan colaboradores y salarios; para los demás, Personal queda en solo consulta.
- Recursos Humanos carga su libro Excel (Personal → Elegir el libro Excel). Puede elegir **Solo actualizar colaboradores y
  salarios**. Si hay salarios nuevos, indica **desde qué fecha rigen** (por defecto, el primer día del mes).
- Esos salarios aplican para todos: las hojas nuevas de cualquier usuario o administrador los toman, y las hojas abiertas
  (borrador o firmadas) de todos los libros se recalculan desde esa fecha y queda anotado en su historial. Las hojas
  legalizadas o cerradas conservan el salario con que se liquidaron.
- Cuando otra persona carga su libro, la hoja BD de su archivo se ignora: sus salarios no cambian los generales.

- Si el libro trae hojas que ya están registradas en otro libro (mismos colaboradores, fechas y horarios), el resumen las
  lista y usted elige: **pasarlas** al libro de esta persona con los cambios del archivo, **no cargarlas**, o cargar una copia.
- **Eliminar usuario**: sus hojas pasan a su libro o se eliminan con sus firmas, según elija. **Quitar acceso** solo lo bloquea.

## Libro por responsable
Cada hoja tiene un **responsable** (quien la creó o cargó). Un usuario ve solo su libro; los administradores ven todos los
libros y pueden cambiar el responsable de una hoja (menú ⋯ → Cambiar responsable). Las horas extras que ya existían
(las 12 hojas del Excel inicial) quedan en el libro del administrador principal.
Cada usuario puede **cargar su libro Excel** (Libro → Cargar mi libro Excel): se cargan sus hojas, pero no los colaboradores ni
los salarios. Si una hoja ya está registrada en el libro de otra persona, no se carga dos veces.

## Informes, consolidado y metas
- **Consolidado** (usuarios): sus horas por mes, jornada, área y colaborador, y la tabla por colaborador. Sin valores en pesos.
- **Informe global** (administradores): todo lo anterior con costos y horas por responsable, y una dona de
  **participación por área**. Las barras van en una escala de azul: las de más horas, más oscuras. La **línea de meta**
  punteada aparece en horas y costo por mes y en colaboradores; en áreas y responsables la meta es una marca negra en cada barra. Al tocar una barra se filtra todo el
  tablero (mes, área, jornada, colaborador o responsable). **Descargar consolidado** genera un Excel con el resumen y el detalle.
- **Metas** (administradores): horas por colaborador a la semana y al mes, horas y costo por área y de toda la empresa al mes, y
  horas al mes por responsable. Al guardar una hoja que supera una meta (o llega al 90 %) aparece un aviso. Puede elegir
  **Solo avisar** (se guarda y queda anotado en el historial) o **No permitir** (los usuarios no pueden guardarla).
- Una autorización ya legalizada no se suma en informes ni metas: cuentan las horas reales de su legalización.

## Compartir la app
En **Mi cuenta → Compartir la app** está el enlace con botones para copiar, compartir o enviar por WhatsApp.
Quien lo abra la usa en el navegador del PC o la instala en el celular, y pide acceso desde la pantalla de ingreso.
- Costo = salario ÷ 210 × recargo × horas (divisor y recargos en Ajustes).
