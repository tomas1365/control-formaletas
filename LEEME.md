# Jornada Ext Laboral · Unispan

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

## Que la app no se duerma
En el plan gratuito, Render duerme el servidor después de 15 minutos sin uso y tarda alrededor de un minuto en despertar.
- Mientras alguien tenga la app abierta, no se duerme (la app consulta el servidor cada 15 segundos).
- Al abrirla con el servidor dormido, la pantalla aparece al instante con "Conectando con el servidor…" y entra sola.
- **Para que no se duerma nunca (gratis):** cree una cuenta en https://cron-job.org, **Create cronjob**, URL
  `https://SU-APP.onrender.com/salud`, cada **10 minutos**. Si la Bitácora también está en el plan gratuito de la misma
  cuenta de Render, limite el horario (por ejemplo lunes a sábado de 6:00 a 19:00, zona America/Bogota): las dos apps
  comparten 750 horas gratis al mes y, si se agotan, Render suspende ambas hasta el mes siguiente.
- **Opción sin límites:** en Render, servicio → Settings → Instance Type → **Starter** (USD 7 al mes); no se duerme nunca.

## Centros de costo
- En **Accesos → Centros de costo** el principal crea los centros (código y nombre) y, con **Editar**, asigna a cada persona
  los suyos.
- Cada hoja tiene un **centro de costo** (en el editor). Las horas se cargan a ese centro, sin importar el área del
  colaborador. Un usuario solo puede elegir entre los centros que tiene asignados; por defecto se usa el primero.
- Informes tiene filtro y gráfica por centro de costo; aparece también en el PDF, el Excel, el consolidado y los planos de nómina.

## Libro por años y meses
El Libro abre en el **mes en curso** (o el último con hojas). Arriba están los años y sus meses con cuántas hojas tiene cada
uno, y en el PC también en la barra lateral, debajo de "Libro". "Todos los meses" muestra todo; con fechas o búsqueda
se busca en todos los meses.

## Nómina
- En Accesos marque a un administrador como **Nómina** (el principal también tiene el permiso).
- Menú **Nómina**: una tarjeta por semana de **sábado a viernes**, con colaboradores, horas extras, recargo nocturno, valor y
  cuántos registros fueron en **festivo** o domingo.
- **Descargar plano** genera un Excel con tres hojas: **PLANO** (una fila por colaborador, centro de costo y concepto
  —código de jornada D, N, DD, ND, FD, FN, RN— con factor, horas, horas en festivo, salario, valor hora y valor),
  **DETALLE** (cada registro) y **CONTROL** (totales por concepto y estado).
- Control: **Marcar revisado** y después **Marcar pagado** (queda quién y cuándo). Si las horas de una semana cambian
  después de revisarla, la tarjeta lo avisa para revisarla de nuevo.
- Por defecto se pagan las **legalizaciones**; se pueden incluir autorizaciones que aún no se han legalizado.

## Rangos de administrador (cargos)
En **Accesos → Rangos de administrador** el principal crea cargos (Coordinador, Jefe de área, Gerente…) y marca sus
permisos: ver salarios y costos, ver todos los libros, definir metas, crear proyectos, reabrir hojas y quitar firmas,
cambiar responsable, actualizar salarios y nómina. Con **Editar** se asigna el rango a cada administrador. Un administrador
sin rango tiene los permisos básicos (todos menos salarios y nómina, que se dan con su casilla o con el rango).
El servidor aplica los permisos: por ejemplo, un rango sin "ver salarios" no recibe salarios ni costos.

## Proyectos
- En **Informes → Proyectos**, quien tenga el permiso crea proyectos: nombre, **por qué** se hacen las horas extras,
  centro de costo, fechas, meta de horas, estado y personas asignadas (si no marca ninguna, todos pueden usarlo).
- En cada hoja se elige el proyecto: trae el porqué a Observaciones y a los soportes vacíos, y su centro de costo.
- Informes por proyecto: tarjeta con horas, costo, colaboradores, hojas y avance contra la meta; filtro y gráfica por
  proyecto en el tablero; **Informe del proyecto** en Excel. El proyecto también sale en el PDF, el Excel y los planos de nómina.

## Centros de costo de las hojas ya cargadas
Al asignar centros de costo a una persona, sus hojas que no tenían centro (o tenían uno que no es suyo) pasan a su primer
centro asignado, y queda anotado en el historial de cada hoja. El Libro muestra los años **cerrados**: al tocar un año se
despliegan sus meses.

## Llegada de operarios y asistencia
Menú **Llegada**: elija la fecha (Hoy, Ayer, Mañana o cualquier día) y aparecen los operarios programados en las hojas de
ese día. Por cada uno: **Llegó ahora** (anota la hora actual) o escriba la hora de llegada, y marque **✓ Asistió** o
**✕ No asistió**. Si llegó más de 5 minutos después de la hora programada se marca "min tarde". **Confirmar a todos los que
llegaron** confirma de una vez a quienes ya tienen hora de llegada. Queda quién confirmó y cuándo.
En la hoja, cada nombre muestra su llegada y asistencia, y un indicador "Asistencia confirmada x/y". Al legalizar una
autorización, las filas marcadas "No asistió" no pasan a la legalización. Los planos de nómina traen LLEGADA y ASISTENCIA.

## Confirmar hojas (libro en curso)
El Libro abre en **En curso**: solo las hojas sin confirmar. Cuando una hoja está lista, **Confirmar y enviar a su mes**
(en la hoja o seleccionando varias en el Libro) la pasa al mes de su fecha, dentro del año (Libro ▸ 2026 ▸ Noviembre).
Antes de confirmar avisa si hay firmas o asistencias pendientes. **Devolver a en curso** la regresa.
