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

## Rangos de usuario (niveles)
En **Accesos → Rangos de usuario** el principal crea niveles para los usuarios (Operario, Supervisor, Líder de turno…) y
marca lo que cada uno puede hacer en su libro: ver salarios, recargos y costos, crear hojas, editar hojas con firmas de Elabora o Autoriza, cargar libros
de Excel, registrar llegada y asistencia, confirmar hojas, legalizar y cerrar, y eliminar hojas en borrador. Se editan y se
quitan igual que los de administrador, y se asignan con **Editar** en cada usuario (la lista de rangos cambia según el nivel
elegido). Un usuario sin rango puede hacer todo lo de la lista menos ver salarios, recargos y costos, que solo ven los
usuarios cuyo rango tenga marcado ese permiso.
El servidor también aplica estos permisos.

## Editar hojas ya guardadas y firmadas
Las hojas en borrador o firmadas se pueden **Editar** (agregar, cambiar o quitar colaboradores) sin quitar las firmas; las
legalizadas o cerradas se reabren primero. Las firmas de Elabora, Autoriza y Liquida se conservan y la hoja queda anotada
como "Editó la hoja ya firmada". Si se agrega un colaborador que **ya firmó en esa hoja** (otro día u otra fila), su firma se
copia sola a las filas nuevas ("Replicó firma" en el historial). Si a una fila firmada se le cambia la fecha u horario, toma
otra vez la firma de la persona si tiene otra fila firmada; si no, queda pendiente de firmar.

## Proyectos
- En **Informes → Proyectos**, quien tenga el permiso crea proyectos: nombre, **por qué** se hacen las horas extras,
  centro de costo, fechas, meta de horas, estado y personas asignadas (si no marca ninguna, todos pueden usarlo).
- En cada hoja se elige el proyecto: trae el porqué a Observaciones y a los soportes vacíos, y su centro de costo.
- Informes por proyecto: tarjeta con horas, costo, colaboradores, hojas y avance contra la meta; filtro y gráfica por
  proyecto en el tablero; **Informe del proyecto** en Excel. El proyecto también sale en el PDF, el Excel y los planos de nómina.


### Proyectos desde Excel, por colaborador, con horas y costos
- **Informes → Proyectos → Cargar proyectos desde Excel**: una fila por proyecto (o una por colaborador repitiendo el
  proyecto) con CÓDIGO, PROYECTO, POR QUÉ, CENTRO DE COSTO, META HORAS, DESDE, HASTA, ESTADO y COLABORADORES (cédulas o
  nombres separados por coma). Solo PROYECTO es obligatoria. Si el código o el nombre ya existe se actualiza; si no, se crea.
  Antes de guardar, la app muestra cuántos se crean y actualizan, y los colaboradores o centros de costo que no encontró.
- **Descargar plantilla** baja los proyectos actuales en ese formato para editarlos en Excel y volverlos a cargar.
- En cada hoja, además del proyecto de la hoja, **cada fila (colaborador) puede tener su propio proyecto**. Si el colaborador
  está asignado a un proyecto, se propone solo al agregarlo. En "Agregar varios colaboradores" se puede elegir el proyecto de todos.
- Las horas y costos se cargan al proyecto de cada fila. **Informes → Proyectos** muestra la tabla de horas, costos,
  participación, colaboradores, hojas y meta por proyecto; el Tablero tiene "Horas por proyecto" y "Costo por proyecto".
  **Informe de todos los proyectos** descarga un Excel con RESUMEN, POR COLABORADOR y DETALLE (con el rango de fechas elegido).
- En la hoja impresa, la fila con un proyecto distinto al de la hoja lo muestra en la columna SOPORTE.

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
autorización, las filas marcadas "No asistió" no pasan a la legalización. Los planos de nómina traen LLEGADA, SALIDA,
HORAS REALES y ASISTENCIA.

**Salida:** en la misma pantalla, **Salió ahora** o escriba la hora de salida; **Registrar salida de todos ahora** la
anota a todos los de la hoja que ya llegaron. Se compara con la hora fin programada ("min antes" / "min después") y con la
llegada da el **tiempo real** trabajado (también si la jornada pasa la medianoche). Queda quién la registró. Las horas
extras de la hoja no cambian solas.
**Permisos:** "Registrar llegada y confirmar asistencia" y "Registrar salida" son dos permisos que se marcan en los rangos de
usuario y de administrador. Sin rango se tienen los dos. Los rangos creados antes conservan lo que ya podían hacer
(los de administrador quedan con los dos; los de usuario con llegada también quedan con salida).

## Confirmar hojas (libro en curso)
El Libro abre en **En curso**: solo las hojas sin confirmar. Cuando una hoja está lista, **Confirmar y enviar a su mes**
(en la hoja o seleccionando varias en el Libro) la pasa al mes de su fecha, dentro del año (Libro ▸ 2026 ▸ Noviembre).
Antes de confirmar avisa si hay firmas o asistencias pendientes. **Devolver a en curso** la regresa.

## Conexión con la base de datos (Supabase)
La app usa el pooler de Supabase en **modo transacción (puerto 6543)** aunque `DATABASE_URL` diga 5432: así varias apps
(la Bitácora y esta) pueden compartir la base sin llenar el cupo del modo sesión, que provocaba
"PoolTimeout: couldn't get a connection" y dejaba la app en "Conectando con el servidor…". Si la base está ocupada,
el servidor responde en 12 segundos y la app reintenta sola. Para volver al modo sesión: variable `MODO_POOL=sesion`.
Para revisar el servidor abra `https://SU-APP.onrender.com/salud`.


## Informes unificados o por aparte: Logístico y Planta
Arriba de los informes hay tres botones: **Unificado**, **Logístico** y **Planta**. Unificado muestra todo junto y además
dos tarjetas (horas, %, costo y colaboradores de cada división) y la gráfica "Logístico y Planta por mes"; al tocar una
tarjeta o una barra se abre esa división por aparte. En Logístico o Planta, todo el informe (tablero, consolidado,
proyectos, recargo nocturno y los Excel) muestra solo las áreas de esa división. El Excel del consolidado unificado trae
además la hoja **POR DIVISIÓN** (cada división con sus áreas y total).
La división se toma del **área del colaborador**. En **Ajustes → Logístico y Planta** el principal asigna cada área. Mientras
no se guarde, la app propone: Logístico = Devoluciones, Despachos; Planta = Bodega de producto terminado, MTTO. Encofrado,
MTTO. Componentes, Técnicos de mantenimiento, Transformaciones y reacondicionamiento. Un área nueva queda "Sin división" hasta asignarla. Incapacidad permanente no se reparte (no es un área de trabajo).


## Nómina: semanas revisadas archivadas por año y mes
La pantalla Nómina abre en **Por revisar**: las semanas sin revisar y las revisadas cuyas horas cambiaron después. Al
**Marcar revisado**, la semana se archiva en su año y mes (el mes del viernes en que cierra la semana). Debajo de **Nómina**
en el menú (PC) aparecen "Por revisar" y los años, que se despliegan para mostrar sus meses; en el celular, los mismos años y
meses están en la pantalla de Nómina. Cada mes muestra sus semanas, el total de horas y valor, y cuántas faltan por pagar.
"Quitar revisado" devuelve la semana a Por revisar.


## Llegada: hora del turno, tarde en rojo y No asistió
La llegada de cada operario trae la **hora del turno** programada (por ejemplo 7:00 a. m.), en gris, hasta que se confirme o
se cambie. **Asistió** la deja con esa hora si no se cambió; **Confirmar asistencia de todos** hace lo mismo con todos los
pendientes. La hora se puede modificar: si es después de la hora del turno, el campo y la hoja la muestran **en rojo**
("Llegó tarde · N min"). **No asistió** borra la llegada y la salida y bloquea esos campos (tocarlo otra vez lo quita).
En Ajustes → Logístico y Planta cada área debe quedar en Logístico o en Planta; no se guarda si falta alguna.


## Llegada desde foto o escáner del registro físico (bot)
En **Llegada**, la tarjeta **Registro físico** tiene **Tomar foto** (abre la cámara del celular) y **Subir imagen o escaneo**
(JPG, PNG o PDF). La foto se guarda con la fecha y quién la tomó (se puede ver o eliminar), y el **bot** la lee: relaciona a
cada operario programado ese día por cédula o nombre y propone llegada, salida y asistencia. Aparece una ventana para
**revisar y corregir** (las lecturas de seguridad baja vienen sin marcar; la llegada tarde sale en rojo; también lista a
quienes no aparecen en la foto y a los de la foto que no estaban programados). **Aplicar a Llegada** llena los campos y queda
en el historial "Llenó llegada desde foto del registro". Respeta los permisos de llegada y de salida.

**Bot gratis (Gemini):** el bot usa la capa gratuita de la API de Gemini de Google. La clave se crea gratis en
https://aistudio.google.com (Get API key) y va en Render → Environment como `GEMINI_API_KEY`. Usa el modelo
gemini-3.5-flash-lite (el de más cupo gratis, del orden de 500 lecturas al día y 10 por minuto); si Google lo retira, prueba
solo los siguientes (gemini-flash-lite-latest, gemini-3.1-flash-lite, gemini-3.8-flash). Se puede fijar otro con
`MODELO_GEMINI`. Si se acaba el cupo, la app lo avisa, la foto queda guardada y se llena a mano o se reintenta luego.
Importante: en la capa gratuita Google puede usar lo enviado para mejorar sus modelos (las planillas llevan nombres,
cédulas y horas). Si la empresa no lo acepta, active facturación en ese proyecto de Google o use `ANTHROPIC_API_KEY`
(Claude, de pago) en lugar de `GEMINI_API_KEY`.
Para mejores lecturas: foto derecha, con buena luz, la planilla completa y sin sombras.


### Varias planillas a la vez y no programados
Se pueden juntar **varias fotos o escaneos** (hasta 8) antes de leerlos: "Tomar otra foto" o "Subir imágenes o escaneos"
(se pueden elegir varios). Aparecen en miniatura con ✕ para quitar, y **Leer con el bot** las lee una por una y junta el
resultado en una sola revisión (si una persona sale en dos hojas, se toma la llegada de una y la salida de la otra).
Si el bot pone como "no programado" a alguien que sí está programado (misma cédula o nombre), la app lo relaciona sola.
Los que de verdad no estaban programados ese día se pueden **marcar y agregar a una hoja del día** (quedan con el turno de
esa hoja y la hora leída; deben existir en Personal). Si Google está saturado con un modelo, el bot prueba otro solo.


### Cola del bot cuando Google está ocupado
El servicio gratis de Google a veces responde "saturado" en horas pico o se queda sin cupo. Entonces la planilla **no se
pierde**: queda **En cola** y el servidor la vuelve a intentar solo (al minuto, a los 2, 4, 8 y luego cada 15 minutos, hasta
unas 8 horas), aunque nadie tenga la app abierta. En Llegada cada planilla muestra su estado: En cola (con el próximo
intento y "Intentar ya"), Leída (botón **Revisar**; con varias, "Revisar las N leídas juntas"), Aplicada o No se pudo leer
(con "Reintentar"). Si la pantalla está abierta, avisa cuando una planilla de la cola queda leída.


### Llegada por fecha y por Responsable del proceso
Llegada muestra **solo los registros de la fecha elegida**, sin juntar días: si una hoja tiene filas del 21/11 y del 22/11,
el 21/11 muestra solo las del 21 (y avisa cuántas filas de otras fechas tiene la hoja). Los formatos aparecen separados por
**Responsable del proceso** (nombre, cantidad de formatos y operarios, y el día). Arriba hay botones de **Responsable** para ver
uno a la vez (los contadores se ajustan) y de **Fechas con registros** (una semana antes y después) para pasar de un día a otro.


## Arranque sin trabar la base de datos (desde 2026-11-24g)
Antes, cada vez que Render arrancaba la app (en cada despliegue) se ejecutaban "alter table" y un bloqueo exclusivo de la
tabla de usuarios aunque no hubiera nada que cambiar. Si la versión anterior seguía atendiendo, las consultas de ingreso
quedaban en fila detrás de ese bloqueo y la app mostraba "La base de datos no respondió a tiempo". Ahora:
- Solo se crean tablas, índices o columnas que **faltan**; si ya existen no se toca nada.
- Toda transacción de la app espera un bloqueo **máximo 10 s** (nunca se queda colgada).
- Un **guardián** revisa cada 20 s: si una consulta de la app lleva más de 25 s esperando y quien la bloquea es una sesión
  abierta sin hacer nada (o una consulta de estas tablas de más de 2 minutos), la termina. Queda en Logs como "GUARDIÁN: …".
- Si igual falla, /salud y la pantalla de error muestran qué consultas están trabadas.
Para destrabar a mano (Supabase → SQL Editor):
  select pg_terminate_backend(pid) from pg_stat_activity where datname = current_database() and pid <> pg_backend_pid()
    and (state like 'idle in transaction%' or wait_event_type = 'Lock') and query ilike '%hx_%';


### Horas pico (2026-11-25)
- Hasta **10 conexiones** a la base (antes 6) y cada petición espera hasta **25 s** una conexión libre (antes 12 s).
- El usuario y su rango se reutilizan **10 s** entre peticiones (menos consultas); si se cambian usuarios, claves o rangos,
  aplica de inmediato.
- Los celulares sincronizan cada **30 s** (antes 15 s).
- Al guardar una planilla en Llegada, si la base está ocupada un momento, la app reintenta sola hasta 3 veces.
- Si aun así falla, el mensaje y el registro de Render ("POOL AGOTADO …") dicen cuántas conexiones estaban en uso y
  cuántas peticiones esperaban.


### Conexiones que se quedaban colgadas (2026-11-25b)
Si el pooler de Supabase corta una conexión sin avisar, una consulta podía quedarse esperando para siempre con la conexión
tomada; cuando se colgaban todas, la app decía "las conexiones de la app estaban ocupadas o se cayeron" aunque la base
respondía. Ahora las conexiones usan **keepalive TCP** (una conexión muerta se detecta en menos de un minuto) y, si el pool
de la app deja de entregar conexiones mientras la base sí responde, se **arma un pool nuevo solo** (máximo una vez por
minuto; queda en Logs como "REPARANDO POOL"). /salud muestra el estado del pool ("pool"), cuántas reparaciones van y,
si falla, el error exacto ("falla") y los últimos avisos del pool.


## Fines de semana y festivos · Mis actividades (2026-11-25c)
- La app conoce los **festivos de Colombia** (fijos, Ley Emiliani y los de Semana Santa). En "Agregar varios colaboradores",
  al elegir un **sábado, domingo o festivo** el horario queda en **7:00 a. m. – 1:00 p. m.** (se puede cambiar) y lo dice debajo.
  En un festivo la jornada pasa sola a la festiva (FD/FN), como el domingo pasa a dominical (DD/ND).
- **Mis actividades:** cada usuario crea y guarda su propia lista de actividades para Soporte ("Mis actividades" en Nuevo /
  Editar, o el botón Guardar junto a Soporte). Aparecen primero en el desplegable de Soporte, en todas sus hojas. Se pueden
  quitar con ✕. Cada usuario ve solo las suyas.

- **Ajustes → Horario fines de semana:** aplica la regla a hojas ya registradas. Muestra cada fila de sábado, domingo o festivo
  que no termina a la 1:00 p. m. (antes → después, con la diferencia de horas), separadas en hojas abiertas (marcadas) y
  cerradas o legalizadas (sin marcar, porque normalmente ya se pagaron). Solo cambia filas diurnas que empiezan antes de la
  1:00 p. m.; no toca turnos de tarde o noche, recargo nocturno ni horas manuales. Recalcula horas y costos, conserva firmas
  y deja nota en el historial.
- **Mis actividades:** además de crear, se pueden **editar** (Editar) y **eliminar** (✕, con confirmación). "Traer N
  actividades usadas en mis hojas" pasa a la lista los soportes que el usuario ya usó, para poder editarlos o quitarlos.
  El desplegable de Soporte muestra solo la lista del usuario.

- **Llegada:** la **Salida** muestra en gris la **hora programada** (en sábado, domingo y festivo, 1:00 p. m. para turnos que
  empiezan antes de la 1), igual que la llegada muestra la hora del turno. "Salida de todos a la hora programada" la registra
  a todos los pendientes de la hoja. **↺ Reiniciar** (aparece cuando hay una hora registrada) deshace una hora errónea: la
  llegada vuelve a la hora del turno y la salida queda sin registrar; queda nota en el historial.


## Programación repetida y permisos de Llegada (2026-11-25f)
- **Repetidos:** si el mismo colaborador está programado el mismo día con horario cruzado en dos hojas (por ejemplo, la hoja
  del sábado trae también las filas del domingo que ya están en la hoja del domingo), la app lo marca en rojo en **Llegada**
  (aviso del día y en cada operario), en la **hoja** y en **Nómina**. Nómina no deja marcar revisado ni pagado esa semana hasta
  quitar la fila sobrante. "Quitar de esta hoja" (responsable, administradores, Nómina) borra esa fila con nota en el historial.
  No cuentan las autorizaciones ya legalizadas ni el recargo nocturno.
- **Horas en Llegada:** las horas de llegada y salida (y Llegó/Salió ahora, Reiniciar, salidas de todos) las cambian solo el
  **responsable de la hoja**, los **administradores** y **Nómina**; el servidor también lo exige. Cualquier otra persona que vea
  la hoja solo marca **Asistió / No asistió**.
- **Rango tipo portería:** el permiso de usuario **"Ver la Llegada de todos los responsables"** muestra en Llegada las hojas de
  todos (sin salarios), solo para marcar asistencia. Esas hojas no aparecen en su Libro, informes ni nómina.


### Nómina: ocultar semanas antiguas (2026-11-26)
En Nómina, "Ocultar semanas hasta" (solo Nómina) oculta todas las semanas que cierran (viernes) en el mes elegido o antes:
no salen en Por revisar, en el archivo por año y mes del menú ni en los contadores, y sus repetidos no estorban. "Ver N semanas
ocultas" las muestra un momento con la etiqueta "Oculta". La elección se guarda para todos los de Nómina; "No ocultar ninguna"
la quita. No borra ni cambia ningún registro.
