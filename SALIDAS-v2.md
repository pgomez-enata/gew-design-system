# Qué más puede producir el sistema · segunda ronda

Levantado el 5-sep-2026, con el sistema ya en **v1.0.0** y publicado. La ronda
anterior salió con 16 propuestas y hoy hay **13 hechas**. Esto es lo que viene
después, medido contra lo que ya existe y contra el calendario.

**Faltan 72 días para el 16 de noviembre.** Diez semanas. Eso ordena la lista
más que cualquier otra cosa.

---

## Parte 0 · Dónde estamos

| | |
|---|---|
| Piezas en producción | **405** en 10 familias |
| Tipos de fichero que sabe producir | **5**: PNG (405), MD (51), HTML (48), JSON (2), PDF (1) |
| Tipos que **no** produce ninguno | MP4, GIF, SRT/VTT, PPTX, DOCX, ICS, CSV, SVG, EPS, MP3 |

De las 16 propuestas de la ronda anterior:

**Hechas (13)** — backdrop · roll-up · nota de prensa · boilerplate · banner web
del sello · kit del aliado · «Somos aliados» · sello para web y firma · hoja de
uso de marca · credencial · agenda del día · certificado · carrusel.

**Sin hacer (3)** — **señalética** · **reconocimiento a ponentes** · **deck para
las charlas**. Las tres son de evento, y el evento es dentro de diez semanas.

---

## Parte 1 · Lo que ya está construido en casa

Esto no son ideas: son motores probados en los sistemas hermanos. Adaptar, no
inventar. Es la vía más barata que hay.

| Motor | Líneas | Qué hace | En GEW |
|---|---:|---|---|
| `iavanza/correo.py` | 976 | Correos de convocatoria con el sistema de marca | **no** |
| `iavanza/presentacion.py` | 965 | Presentación 16:9, en dos formatos | **no** |
| `p4f/patrocinadores.py` | 605 | Piezas de patrocinio por nivel | **no** |
| `p4f/pdf.py` | 504 | **PDF con texto vivo**, para imprenta | **no** |
| `iavanza/firma.py` | 475 | Firma de correo | **no** |
| `iavanza/postevento.py` | 434 | La pieza de después: gracias y cifras | **no** |
| `iavanza/encuadre.py` | 329 | Coloca el retrato del ponente con el mismo plano en todos los formatos | **no** |
| `p4f/streaming.py` | 295 | Piezas de streaming | **no** |
| `iavanza/zoom.py` | 285 | Fondos virtuales, láminas y rótulo para webinars | **no** |
| `p4f/iconos.py` | 257 | Iconografía propia | **no** |
| `iavanza/guion.py` | 198 | El formato de texto con que se escriben carruseles y decks | **no** |

**Y el vídeo no es empezar de cero.** En esta máquina hay **ffmpeg 8.1.2**, el
motor `confedit` (5 147 líneas, con módulos de marca, subtítulos, música y un
envoltorio de ffmpeg) y el skill **`enlata-iavanza-reels`**, que ya produce
reels 9:16 con subtítulos quemados, música con ducking y logos. Está en línea
gráfica Enlata × IAvanza: para GEW hay que cambiarle la piel, no el motor.

---

## Parte 2 · Evento físico — lo que falta y sus medidas reales

Diez semanas, ~48 actividades en varias sedes. Es lo que más aprieta.

**La regla de la señalética**: **2,5 cm de altura de letra por cada 3 m de
distancia de lectura**. ⚠️ La cifra 1:10 aparece repetida en toda la industria
—ADA la usa de base— pero no encontré el documento SEGD original accesible: va
como estándar de industria, no como norma citada.

| Pieza | Medida | Se lee a | Estado |
|---|---|---|---|
| **Direccional** (pasillo, flecha) | tablero A3/A2, letra 5–8 cm | 5–8 m | falta |
| **Identificación de sala** | tablero A4/A3, letra 3–5 cm | 3–5 m | falta |
| **Rótulo de mesa de registro** | A3 vertical o banner 20×60 cm | 1–2 m | falta |
| **Faldón de mesa** | 427 cm cubre 3 lados de una mesa de 183×76 cm | — | falta |
| **Gafete** | 10,16×7,62 cm horizontal (el más común) · vertical 10,16×15,24 con QR | — | ⚠️ el nuestro es 10×14 |
| **Cordón** | 2 cm de ancho, para gafete de 7,6–10,2 | — | falta |
| **Cartel de wifi / mesa** | 10×15 cm o 14×14 cm | 1 m | falta |
| **Atril** | 114–122 cm; accesible 76–81 cm | — | falta |
| **Backdrop / photocall** | 2,44×2,44 m es el estándar; 3×2,4 m para 4–6 personas | — | ✅ 3×2,4 m |

⚠️ **El gafete nuestro mide 10×14 cm y no es ninguno de los dos estándares.**
El apaisado más común es 10,16×7,62 y el vertical con QR, 10,16×15,24. La
diferencia importa por una razón práctica: las fundas y los cordones se compran
hechos, para esas medidas. Antes de imprimir 500, hay que ver qué funda se
consigue en Santo Domingo.

**Escenario y grabación**: la plantilla de presentación va en 16:9 (1920×1080)
con **10 % de margen de seguridad** en los cuatro lados; los títulos, dentro del
**80 % central** (título seguro de SMPTE), y el tercio inferior ocupa entre el
12 y el 15 % del alto.

**Merchandising**: camiseta 20–25 cm de pecho, tote 25–30 cm de ancho útil,
taza 20×9,5 cm, pin de 5,7 cm, sticker desde 1,9 cm. **No lo priorizaría**: para
48 actividades es sobredimensionado salvo que sea un kit de staff o de ponente.

⚠️ **Impresión en RD**: no hay norma publicada. En el mercado dominicano se
venden Carta y A4 como productos distintos, sin que ninguna fuente diga cuál
manda. Los anchos de rollo de gran formato que circulan (1,52 m y hasta 3,20 m)
son de proveedores de la región, **no verificados en una imprenta dominicana**.
Eso hay que preguntarlo, igual que el perfil de color.

---

## Parte 3 · Canales donde el sistema todavía no llega

### Vídeo — el salto más grande, y el que menos cuesta

Hoy el sistema hace **frames**, no vídeo. Pero ffmpeg 8.1.2 está instalado y
`confedit` ya envuelve ffprobe/ffmpeg, hace subtítulos y camas musicales.

Lo que se puede producir por código, sin editor:
- **Cuenta atrás animada** y texto sobre vídeo con `drawtext` y la variable de
  tiempo `t`.
- **Subtítulos quemados** con el filtro `subtitles=` sobre libass.
- **Tarjeta de apertura y endcard** en movimiento: los PNG que ya existen, con
  una entrada.

⚠️ **Meta no publica el bitrate de Reels.** Las cifras de 3 500–10 000 kbps que
circulan son de terceros. Lo que sí está publicado: TikTok pide ≥540×960 y
≥516 kbps para anuncios; YouTube pide 8 Mbps para 1080p SDR con H.264 High
Profile y AAC-LC a 48 kHz. Y **el −14 LUFS de YouTube tampoco tiene página
oficial**: es cifra de terceros, aunque consistente.

### Correo — hay motor, pero con una trampa medida

`iavanza/correo.py` ya existe (976 líneas). Dos cosas que hay que respetar:

- **Gmail recorta el mensaje a partir de 102 KB** de HTML y CSS. No cuenta el
  peso de las imágenes. *(Cifra no confirmada por Google, pero citada por
  Litmus y Mailchimp desde 2018.)*
- **El Outlook clásico ignora flexbox y grid por completo** — usa el motor de
  Word. Microsoft lo retira en octubre de 2026, pero el parque instalado sigue
  hasta 2028-29. Ancho de 600–640 px, que es convención, no norma.

### WhatsApp — donde de verdad se mueve la convocatoria

⚠️ **WhatsApp no publica specs de estado ni de difusión normal.** El
«1080×1920, 16 MB» que circula es inferencia. Lo único documentado es la API de
negocio: **imagen 5 MB máximo**, vídeo 16 MB con H.264 perfil Main sin
B-frames. Y recomprime siempre, salvo que se envíe como documento.

### Presentaciones

| Formato | A favor | En contra |
|---|---|---|
| **PDF** | imprime igual en cualquier equipo | no lo puedes editar |
| **PPTX** (`python-pptx`) | **lo editas tú en PowerPoint** | sin animaciones ni transiciones; exportar a PDF pide LibreOffice |
| HTML | se versiona bien | frágil para «enviar y que se vea igual» |

Para un deck que se proyecta **y** se envía: generar PPTX y exportar el PDF del
mismo fuente. `iavanza/presentacion.py` ya hace la parte visual.

### Accesibilidad — lo que es exigible, no opcional

- **Subtítulos sincronizados**: WCAG 1.2.2, **nivel A**. Todo vídeo con audio.
- **Texto alternativo**: 1.1.1, nivel A.
- **Audiodescripción**: 1.2.5, nivel AA. Una transcripción sola no basta.
- **Contraste 4,5:1**: aplica también al texto quemado sobre vídeo.

---

## Parte 4 · Las propuestas, para seleccionar

Ordenadas por **cuándo hacen falta**, no por lo bonitas que son. Faltan diez
semanas.

### Bloque A — antes de que se cierre la convocatoria (~6 semanas)

**1 · Correo de convocatoria y de confirmación.**
El aliado se entera por correo, no por Instagram. `iavanza/correo.py` ya existe:
es cambiarle la piel. Con el tope de 102 KB de Gmail medido en la salida.
*Adaptar · alto valor · bajo coste.*

**2 · Kit de vídeo: cuenta atrás, apertura y endcard en movimiento.**
Los PNG ya están; falta que se muevan. ffmpeg y el motor de reels también.
Es lo que multiplica alcance en las cuatro semanas previas.
*Adaptar · alto valor · coste medio.*

**3 · Deck para las charlas.** De la lista anterior, sin hacer. Portada,
láminas y cierre para que los ponentes no lleguen con cualquier cosa. Con
16:9, margen del 10 % y títulos dentro del 80 % central.
*Adaptar `iavanza/presentacion.py` · coste medio.*

**4 · Firma de correo y fondo de videollamada.** Cuarenta y ocho aliados
mandando correos y entrando a reuniones con el sello puesto, gratis.
`iavanza/firma.py` y `iavanza/zoom.py`.
*Adaptar · bajo coste.*

### Bloque B — antes de imprimir (~8 semanas)

**5 · Señalética de sede.** Direccional, sala, mesa de registro, wifi. Con la
regla de 2,5 cm de letra por cada 3 m. De la lista anterior, sin hacer.
*Nuevo · coste medio · **es lo que más se echa en falta el día del evento**.*

**6 · Reconocimiento a ponentes.** De la lista anterior, sin hacer. Es otra
plantilla del motor de certificados, que ya está.
*Adaptar · bajo coste.*

**7 · PDF con texto vivo.** La revista sale hoy como 32 fotos de texto. Una
errata obliga a re-renderizar. `p4f/pdf.py` ya lo resolvió.
*Adaptar · alto coste · sólo si la revista se imprime de verdad.*

**8 · QR en las piezas.** Para inscripción, agenda y wifi. Hoy el sistema no
sabe hacer uno: no hay `qrcode` ni `segno` instalados.
*Nuevo · bajo coste.*

### Bloque C — durante y después

**9 · Piezas de patrocinio por nivel.** El hueco de patrocinadores ya está
reservado en la banda; falta la pieza que se le entrega al que firma.
`p4f/patrocinadores.py`. *Adaptar.*

**10 · Pieza de post-evento.** Gracias y los números, por actividad y del total.
`iavanza/postevento.py`. *Adaptar · es la que cierra el ciclo con el aliado.*

**11 · Piezas de streaming.** Si alguna actividad se transmite: contraportada,
«ya empezamos», tercios inferiores. `p4f/streaming.py`. *Adaptar.*

**12 · Informe de resultados.** Lo que se le manda a GEN y a los patrocinadores.
Hoy la revista tiene las páginas de reportería pero con `{{N}}`: falta el
formulario que las llene. *Nuevo · depende de datos que aún no existen.*

### Bloque D — infraestructura, no piezas

**13 · Encuadre automático de retratos.** `iavanza/encuadre.py` coloca la cara
con el mismo plano en todos los formatos. Con 48 aliados y sus ponentes, esto
se paga solo. *Adaptar.*

**14 · Iconografía propia.** `p4f/iconos.py`. Hoy GEW no tiene iconos y los pide
la señalética, la agenda y el deck. *Adaptar.*

**15 · Calendario `.ics`.** Un fichero que el aliado abre y le mete su actividad
en el móvil. Nadie lo hace y cuesta cincuenta líneas. *Nuevo · bajo coste.*

**16 · Exportar el padrón a CSV.** Para la web, el formulario y el informe.
*Nuevo · bajo coste.*

---

## Parte 5 · Lo que decides tú

1. **Cuáles de las 16 entran, y en qué orden.** Mi recomendación por lo que
   aprieta el calendario: **1** (correo), **5** (señalética), **3** (deck) y
   **2** (vídeo). Las cuatro tienen motor en casa o casi, y las cuatro se
   necesitan antes de la semana. El **7** (PDF vectorial) es el más caro y sólo
   vale la pena si la revista se imprime de verdad.

2. **La medida del gafete.** 10×14 cm no es ninguno de los dos estándares, y
   las fundas se compran hechas. Hay que ver qué se consigue aquí antes de
   imprimir.

3. **Si hay merchandising**, y para quién. Yo no lo priorizaría: para 48
   actividades es sobredimensionado salvo como kit de staff o de ponente.

4. **Si alguna actividad se transmite.** De eso depende el 11.

Y sigue abierto lo de siempre, que no depende de nosotros: el **perfil ICC de
la imprenta** con el gramaje real, y **cuál de las cuatro fuentes de cifras de
GEN** se cita.

---

## Anexo · Lo que NO recomiendo, y por qué

**Merchandising completo.** Camisetas, totes, tazas y pines para una semana de
48 actividades es catálogo, no necesidad. Un kit de staff sí; el resto no.

**Generar el deck en HTML.** Se versiona bien pero es frágil para «enviar y que
se vea igual». PPTX más PDF del mismo fuente cubre las dos cosas.

**Citar como norma lo que no lo es.** Tres cifras que circulan y que este
documento deja marcadas: el bitrate de Reels (Meta no lo publica), el −14 LUFS
de YouTube (no hay página oficial) y las specs de estado de WhatsApp (tampoco).
Si acaban en una plantilla, que sea sabiendo de dónde salen.
