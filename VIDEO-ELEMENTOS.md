# Los elementos del vídeo · qué hay, qué falta y de dónde sale cada cifra

Complementa [`VIDEO-que-falta.md`](VIDEO-que-falta.md), no lo repite. Aquel
documento cataloga **las piezas** que el sistema GEW debería producir —curvas,
entradas y salidas, transiciones entre piezas, duraciones en tiempos a 100 BPM,
19 piezas por momento de campaña, y las normas de subtítulos y de audio con su
fuente—. Este mira **los elementos que se montan encima del metraje**, y lo hace
sobre **los cinco motores a la vez**, no sólo sobre GEW.

Barrido del 6-sep-2026: 14 elementos, un investigador y un refutador por
elemento, 29 agentes. 43 propuestas, de las que **20 sobrevivieron** a la
refutación. Y 24 cifras tumbadas por no tener fuente.

**Los tres defectos de fondo que encontró quedaron cerrados el mismo día** (§6):
zonas seguras, looks de color y la regla de la música salen ya de un solo sitio.

---

## 0 · El hallazgo de fondo: cinco motores y ningún catálogo común

No hay «un sistema de vídeo». Hay cinco, cada uno con su propia implementación
de los mismos elementos:

| | GEW | reels | DTW | P4F | confedit |
|---|:--:|:--:|:--:|:--:|:--:|
| Elementos flotantes | ✓ | ✓ | | ✓ | |
| Ubicación / zona segura | ✓ | ✓ | | | |
| Transiciones | ✓ | ✓ | | | ✓ |
| Coloración | | ✓ | ✓ | | ✓ |
| Nombre de ponente | ✓ | | | ✓ | ✓ |
| Nombre de evento | ✓ | ✓ | | | ✓ |
| Subtítulos | ✓ | ✓ | ✓ | | ✓ |
| Cortinillas | ✓ | ✓ | ✓ | | ✓ |
| Barra de progreso | | | | | |
| B-roll / PIP | | | | | |
| Audio | ✓ | ✓ | ✓ | | |
| CTA / pantalla final | ✓ | ✓ | ✓ | | |
| Tipografía cinética | ✓ | ✓ | ✓ | | |
| Tratamiento de fondo | | ✓ | | | |

Tres consecuencias medidas, no opinadas:

**1 · Las zonas seguras no coincidían entre sistemas.** *(Cerrado el 6-sep — ver §6.)* `video.py` de GEW declara
que la interfaz tapa 269 px arriba y 250 abajo en vertical. En un reel entregado
(`reel_completo_hookA.mp4`, 40,4 s) el watermark cae en **y = 69–89** y el gancho
en **y = 229–413**: los dos dentro de la franja que el otro sistema declara
intocable. Ninguno de los dos está mal por sí solo — es que **nadie comparte el
número**.

**2 · Había TRES looks de color distintos y ninguno tenía nombre.** *(Cerrado el 6-sep — ver §6.)* Cero ficheros
`.cube` en todo el workspace. El grading vive escrito a mano:

| dónde | filtro |
|---|---|
| `mezzanine.py` (por defecto) | `eq=brightness=0.03:contrast=1.09:saturation=1.05:gamma=1.04` |
| `mezzanine.py` (rama condicional) | `eq=brightness=0.05:contrast=1.11:saturation=1.05:gamma=1.05` |
| `invitacion-dtw/SKILL.md` (inline) | `eq=brightness=0.03:contrast=1.08:saturation=1.12:gamma=1.03` |

Los dos primeros llevan además un `colorbalance` que empuja a azul. Ninguno está
documentado, ninguno se audita, y no está escrito cuándo se usa la rama
condicional. Y `mezzanine.py` **no etiqueta el espacio de color**: 0 ocurrencias
de `colorspace`, `color_range` o `color_primaries` — mientras que
`confedit/render.py` sí lo hace, con `bt709` por defecto en `config.py:40`.

**3 · La regla de la música se contradecía consigo misma, dentro de la propia
skill.** *(Cerrado el 6-sep — ver §6.)* `linea-grafica.md` regla 3 pide «cama estable con **ducking**, que sube
al final». La memoria de la corrida DTW dice «preferencia FIRME: cama
**CONSTANTE**, NADA de ducking, `volume=0.04`». Y el código hace las dos cosas
según el motor: `music.py` aplica `sidechaincompress`, `apply_music.py` aplica
ganancia fija. **No la resuelvo yo.**

---

## 1 · Los siete elementos que pediste

### Elementos flotantes
Existe repartido en tres motores. GEW tiene `lower()`, `frame()`, `sello()`,
`pin()` y `flecha()`. La skill de reels tiene chip/píldora (`border-radius:999px`,
gradiente indigo→azul→magenta), watermark permanente (opacidad 0,94, escala 0,62)
y las tarjetas de título. P4F/`streaming.py` es el más completo para directo:
marco de escena, dos variantes de lower third, placa de ganador, cuenta regresiva
y marco de QR.

**Falta de verdad**: una chapa **EN VIVO** animada (existe el icono, no el
overlay) y una **pastilla de dato/contador** sobre vídeo. El QR sí se genera de
verdad en `iavanza_design_system/_qr()` con `qrencode`, pero nadie lo ha
enganchado al `marco_qr()` de P4F.
⚠️ La prueba que proponía el investigador —decodificar el QR con `pyzbar`— **no
se puede correr**: no hay pyzbar ni libzbar ni opencv en esta máquina.

### Ubicación
Es la restricción compartida, no un elemento: no produce ninguna pieza. Y es
donde está el defecto del §0.1.
**Propuesta que sobrevive**: un `zona_segura.py` único —`{formato: {top, bottom,
right, left, fuente, oficial: bool}}`— importado por los motores y por la
auditoría, con el campo `oficial` marcando cuáles vienen de una ficha publicada
y cuáles son criterio nuestro. Hoy la única cifra oficial de Meta es la de
**anuncios** (14 % arriba = 269 px, 35 % abajo sobre 1080×1920); para orgánico
**nadie publica zona segura**, y `LINEAMIENTOS.md` §4.6 ya lo dejó escrito.

### Transiciones
`VIDEO-que-falta.md` §2 ya cataloga cinco entre piezas. Dentro de una pieza, la
skill hace cortes secos, `zoompan` lento (hasta 1,07×) y fundidos de alfa
(0,25 s entrada / 0,4 s salida). `confedit` hace fundidos con rótulo.
⚠️ Dos propuestas cayeron: el **wipe con el pulso** ya está en
`VIDEO-que-falta.md` §2 como `pulso-cortina`, y el **fundido cruzado en confedit**
no es de coste bajo sino de arquitectura — `render.py::_paso_final` pega con el
demuxer `-f concat` sin recodificar, así que no hay dos streams que cruzar.

### Coloración
Lo del §0.2. Lo que sobrevive es barato y no toca el look:
- **Etiquetar el master**: `-color_range tv -colorspace bt709 -color_primaries
  bt709 -color_trc bt709` en el render de `mezzanine.py`. Hoy no se etiqueta, y
  `confedit/render.py` sí lo hace (`-colorspace bt709`, config por defecto).
- **Verificar rango legal antes de entregar**: alerta si `YMIN<16` o `YMAX>235`
  (ITU-R BT.601/709).
- **LUT de marca** (`lut3d=file=x.cube`, malla 17³ o 33³) sólo si Piero lo
  encarga: el `.cube` se diseña, no se programa.

### Nombres de ponentes
Hay **tres implementaciones que no se conocen entre sí**, y la skill de reels no
tiene ninguna. Coinciden en lo esencial —PNG con alfa, placa sólida con filete
de acento, nombre destacado sobre dato secundario, ancla abajo-izquierda— y
**ninguna se anima**: las tres son estáticas y las compone el montador.

| | GEW `video.py:lower` | P4F `streaming.py` | confedit `kit16x9.py` |
|---|---|---|---|
| forma | rectángulo recto | corte diagonal −12° | rectángulo recto |
| filete | horizontal, naranja fijo | vertical 12 px, **color por rol** (verde pitcher / azul experto) | vertical 8 px, color de la paleta activa |
| líneas | 2 (nombre + cargo) | 3 (etiqueta de rol + nombre + detalle) | 3 (nombre / cargo / organización) |
| formatos | **3** (vertical, horizontal, cuadrado) con zonas `ui` | 1920×1080 | 16:9 |
| ancla | margen fijo por formato | contra el «suelo» del reproductor de YouTube | margen |
| ¿mide? | no | no | **sí** — avisa por consola si el texto se sale |

Ninguna resuelve **nombre en dos líneas** cuando no cabe en una, y ninguna
soporta **dos ponentes a la vez** (los tres patrones de consenso son: placas
apiladas, rótulo conjunto «A & B», o identificar sólo a quien tiene el turno).

**Norma que sí existe, y que el sistema no cita**: SMPTE **RP 218:2009** fija
acción segura 90 %/90 % y título seguro 80 %/80 %; **ST 2046-1** (2009), para
pantallas de matriz fija, los sube a 93 %/93 % y 90 %/90 %. Los márgenes de P4F
(3,5 % acción, 5 % título) coinciden con la norma moderna sin nombrarla.
Y Meta **sí publica** un área segura de **1080×1420** (250 px arriba y abajo)
para creatividades de Reels **de anuncios** — muy cerca de los 269/250 que
`video.py` usa hoy como «reserva prudente sin cifra oficial». Sirve de respaldo,
no convierte la cifra en oficial para orgánico.

**Sobrevive**: un `lower_third.py` en la skill de reels que **reuse el patrón ya
cerrado de `video.py:lower`** en vez de inventar un cuarto; partir el nombre en
dos líneas cuando no quepa; y un `_contraste(fg, bg)` con la fórmula de
luminancia de WCAG en el reporte de consola de los tres —hoy los tres confían en
que blanco sobre placa oscura basta, sin medirlo nunca.

⚠️ Este elemento hubo que relanzarlo: el primer investigador devolvió
literalmente `"A"`, `"C"` y `"D"` como propuesta. Un fallo del barrido, no un
resultado — y sin mirar el JSON habría pasado como un elemento más.

### Nombre del evento
GEW lo resuelve con el lockup en el `frame`; la skill con el watermark
permanente; confedit tiene `marca_agua()`. Ninguno acepta **el nombre de la
actividad** como texto.
**Sobrevive**: un parámetro `--evento` en `marca_agua()` de confedit y una placa
de actividad junto al lockup en `video.py:frame()`.

## El bloque de marca se puede anclar abajo

`video.py --tipo frame --bloque abajo` saca el mismo overlay con el par
lockup+pulso anclado **encima de la zona de subtítulos** en vez de bajo la zona
segura superior. En vertical el par lockup+pulso pasa de pintar en **y=335–468** a
**y=1313–1446**, medido sobre el PNG con cualquier umbral de alfa; el velo
de subtítulos y la franja naranja no se mueven.

Sale a `frame--<formato>--abajo.png`: el fichero canónico **no se pisa**.

Para qué: un 16:9 escalado para cubrir un 9:16 deja el recorte clavado al borde,
así que una cara alta no se puede bajar. Piero, 9-sep-2026: «la franja superior
se puede ubicar abajo si hay algún rostro que se tape en el vídeo». Quién decide
es el motor de cobertura (`montaje.elegir_bloque`), una vez por pieza.
⚠️ La propuesta traía dos cifras malas: `0.018×U` citado como «el múltiplo del
espaciado del pulso» cuando el real es `0.024`, y «acción segura = 95 % central»
atribuido a EBU R95, que fija **93 %**. (Y no confundirlo con SMPTE RP 218, que
para lo mismo dice 90 %: son dos documentos distintos con cifras distintas.)

### Estilos de subtítulos
`VIDEO-que-falta.md` §6 ya trae las normas con su fuente: WebVTT (W3C), 37
caracteres y 2 líneas (BBC), 17 car/s (Netflix), contraste 4,5:1 (WCAG 2.2
§1.4.3). Lo que añade el barrido es el estado real del código y su desajuste:

**Corrección**: teníamos escrito «fs56, MarginV 360». El `Style:` real de
`subs.py` es **Fontsize 60, MarginV 430**, Poppins ExtraBold, contorno 4,
sombra 2, `ScaledBorderAndShadow: yes`, `PlayRes 1080×1920`.

**Sobrevive**: un `qa_subtitulos.py` que valide CPS y troceo contra las reglas ya
cerradas (≤44 caracteres, ≤2 líneas, duración mínima 1,0 s), y un
`contraste_subtitulo.py` que **mida el contraste real del texto contra el vídeo
debajo** en vez de suponerlo — hoy se supone.

---

## 2 · Los siete que propongo

| # | Elemento | Estado | Lo que sobrevive |
|---|---|---|---|
| 8 | **Cortinillas: bumper de entrada y separadores** | parcial | `intro_card()` de **1,0 s** para reels (los 3 s de GEW se comen el 10–20 % de un reel de 15–30 s). ⚠️ El separador de 1,2 s **ya está catalogado** en `VIDEO-que-falta.md` §4 como «Sting de marca» |
| 9 | **Barra de progreso y capítulos** | **no existe** | `contador_pasos()` («1 de 5»), `barra_avance_quemada()` (1000×6 px, relleno `#0262E5`), y `--progreso` en `pulso_musica.py` que apaga al 35 % las barras aún no alcanzadas — el pulso haciendo de barra sin dejar de ser el pulso |
| 10 | **B-roll, PIP y capturas** | **no existe** | `broll.py` (cutaway con tope de 2,5 s), `screencap.py` (marco con radio 12 px y sombra). El PIP queda bloqueado: **Piero no graba con dos fuentes** |
| 11 | **Audio: cama, ducking, sonic logo** | parcial | `loudnorm` de dos pasadas en `music.py`, y un **logo sonoro** de 2–4 notas / 0,6–1,2 s a validar. ⚠️ La medición LUFS del master **ya existe** en el sistema: hay que portarla, no reescribirla |
| 12 | **CTA y pantalla final** | parcial | CTA **por reel** en vez de global, y una verificación de que el CTA no pisa la franja de subtítulos. Los QR no los genera el sistema, por decisión tuya |
| 13 | **Tipografía cinética** | parcial | Karaoke por palabra (60 ms de transición, tope 3 cambios/s para no acercarse a WCAG 2.3.1), entrada por palabra con *stagger* de 80 ms, y **contador animado de cifras** — que resultó barato: `drawtext` con `expansion=normal` y `%{eif:...}` corre en este ffmpeg (probado: 665 px de tinta en el PNG) |
| 14 | **Tratamiento de fondo** | parcial | `boxblur=22:2` para relleno al reencuadrar (ya medido y en producción), flag de `vignette`, y **matting de persona** para que el texto pase por detrás |

---

## 3 · Correcciones a cosas que dábamos por buenas

Esto es lo más valioso del barrido: cuatro datos que teníamos escritos y son
falsos.

| Lo que creíamos | Lo que hay |
|---|---|
| «El ASR está caído: el venv de faster-whisper ya no existe» | El venv no existe, cierto — pero **el ASR está vivo**: `/opt/homebrew/bin/whisper-cli` arranca con BLAS y Metal, y los pesos están en `05 Codigo/confedit/modelos/ggml-large-v3-turbo-q8_0.bin`. Lo que falla es el `import` de Python que exigen los `transcribe.py` de las dos skills, no la transcripción |
| «No hay matting de persona en esta máquina» | **Sí lo hay, compilado y en producción desde el 1-ago**: `04 Marca/flyer_se_vale_todo/herramientas/recorte.swift` usa `VNGenerateForegroundInstanceMaskRequest`, con erosión de 8 px y blur de 1,2 px. Nunca se ha aplicado a vídeo |
| Subtítulos a «fs56, MarginV 360» | **Fontsize 60, MarginV 430** |
| «Sólo `encoder.py` etiqueta el espacio de color» | `confedit/render.py` también, con `bt709` por defecto y configurable |

Y una que no es un dato sino un método: **`carrusel.py` ya numera sus láminas**
(`_remate` escribe `i/total`). El investigador de «progreso» dijo que no existía
nada; el refutador lo tumbó con el grep.

---

## 4 · Las 24 cifras que no se sostienen

Los refutadores tumbaron 45 afirmaciones. Por qué:

| Motivo | n |
|---|---|
| Cifra sin fuente rastreable | 17 |
| Ya existe en el sistema | 10 |
| Imposible con este entorno | 8 |
| No aporta nada | 8 |
| Contradice una decisión de Piero | 2 |

Las que más importan, porque son las que se habrían publicado:

- **Zona segura de TikTok** (130–170 px arriba, 340–484 abajo) y de **YouTube
  Shorts** (180–380 / 350–400): cifras de blogs. `LINEAMIENTOS.md` ya había hecho
  ese trabajo y concluyó que para orgánico **no hay cifra oficial**.
- **«Los capítulos de YouTube exigen 33 s de duración mínima»**, atribuido a una
  página de soporte concreta: **esa página no lo dice**.
- **«Facebook hace autoplay con sonido desde 2016»**, con URL de ayuda: **la
  página no lo dice**.
- **«Netflix: 20 cps adulto / 17 infantil»**: las fuentes públicas se contradicen
  entre sí (17/13 en unas, 20/17 en otras).
- El **margen del 4,5 % del alto** que `movimiento_video.py` usa como zona segura
  de respaldo en horizontal y cuadrado (líneas 148 y 183): es un número nuestro,
  sin fuente, y está en producción.

---

## 5 · Seis elementos que faltaban en mi propia lista

| Elemento | Por qué importa aquí | Coste |
|---|---|---|
| **La voz como pista propia** (de-reverb, EQ, de-esser, nivel de diálogo) | Casi todo lo que se graba es talking-head en salas prestadas; la inteligibilidad manda sobre cualquier overlay | medio |
| **Reencuadre y escala del plano** (16:9 → 9:16, seguimiento del hablante) | Cada cobertura de evento se graba en horizontal y se publica en vertical | medio |
| **Ritmo del montaje**: dónde caen los cortes y a qué cadencia | Es lo que separa un recap que se ve de uno que se abandona; hoy no está escrito en ningún sitio | medio |
| **Continuidad de audio en las juntas** (room tone, L-cut y J-cut) | Un corte limpio en imagen con un salto en el ruido de sala se oye como un error | bajo |
| **Velocidad**: rampas, cámara lenta, timelapse | El montaje de eventos vive de comprimir tiempo muerto | bajo |
| **Portada de la pieza**: primer fotograma del reel y miniatura 16:9 | El primer fotograma es lo que decide si alguien pulsa; hoy es el que toque | bajo |

Y seis de los catorce **se solapan**: flotantes + ponentes + evento son una sola
capa de overlay; subtítulos + cinética son un solo renderizador ASS; cortinilla
de salida + CTA son la misma pieza; coloración + fondo son una sola cadena de
filtros antes de cualquier overlay.

---

## 6 · Unificado el 6-sep-2026

Los dos defectos del §0.1 y §0.2 están cerrados. La fuente única es
[`tokens/video.json`](tokens/video.json), y se lee con
[`video_tokens.py`](video_tokens.py).

### Zonas seguras

Un solo sitio, seis formatos, y cada número dice **si es oficial o criterio
nuestro**:

| formato | arriba | abajo | derecha | fuente |
|---|---:|---:|---:|---|
| `vertical` | 269 ✓ | 250 ✓ | 250 | Meta, specs de anuncios (Stories 14 % · Reels 1080×1420) |
| `vertical-ads` | 269 ✓ | 672 ✓ | 250 | Meta, specs de Stories de anuncios (35 % abajo = el CTA) |
| `horizontal` | 60 | 120 | 0 | criterio nuestro, más conservador que SMPTE ST 2046-1 |
| `cuadrado` | 60 | 120 | 0 | criterio nuestro |
| `retrato` | 60 | 140 | 0 | criterio nuestro |
| `yt-portada` | 508 ✓ | 509 ✓ | 507 ✓ | support.google.com/youtube/answer/2972003 |

✓ = respaldado por una ficha publicada. Lo demás es nuestro y así queda escrito.

**El conflicto interno que había**: `video.py` reservaba 60 px arriba en
horizontal y `movimiento_video.py` usaba 49 (un respaldo del 4,5 % del alto que
nadie había declarado). Ahora los dos leen 60, y el respaldo del 4,5 %
desaparece del código.

**La columna derecha sólo aplica a lo anclado a la derecha.** Un texto centrado
puede cruzarla: los iconos de la app se apoyan en el borde. Se descubrió midiendo
—el endcard de GEW llega a x=859 con el límite en 830 y está bien—, y por eso va
como aviso y no como fallo.

**La skill de reels no mueve nada.** Su watermark sigue en y=69 y su gancho en
y=229: dónde va cada elemento lo decides tú, no un script. Lo que sí hay ahora es
[`zona.py`](../../../.claude/skills/enlata-iavanza-reels/scripts/zona.py), que
lee el número canónico y mide cualquier PNG o MP4 contra él:

```bash
python3 zona.py reel_completo_hookA.mp4
```

Sobre el reel entregado dice: `y[145-168] invade 124 px` · `y[229-413] invade
40 px` · 2 bloques fuera. Sobre el endcard de GEW: 0.

### Los tres looks de color

Ahora tienen nombre y viven en el mismo JSON. Y uno estaba mal entendido: la
rama `--warm` de `mezzanine.py` **no calienta** — empuja a frío para compensar
luz de tungsteno. Se llama `frio`.

| look | era | ΔE vs crudo | quema | croma | cuándo |
|---|---|---:|---:|---:|---|
| **`base`** | el defecto de `mezzanine.py` | 6,07 | 0,017 % | 34,17 | **por defecto** |
| `frio` | la rama `--warm` | 8,48 | 0,056 % | 33,81 | luz de tungsteno o cocina |
| `calido` | inline en el SKILL.md de DTW | 6,74 | 0,013 % | 36,84 | cuando se quiere más color |

`base` es el que queda por defecto: es el que menos quema (3 veces menos que
`frio`) y el que menos satura la piel (−7 % de croma frente a `calido`), y es el
que más producción tiene detrás. **Cambiarlo es una línea del JSON** y afecta
sólo a lo que se produzca después: lo publicado no se toca.

⚠️ Los tres llevan el crudo de Y max 250,3 a **255**: los tres queman altas luces
donde el original no lo hacía. Si eso molesta, se baja el contraste — no se
cambia de look.

### La música: cama constante, sin ducking

Decidido por Piero el 6-sep. Cierra la contradicción que llevaba abierta desde
julio, y que estaba **dentro de la propia skill**: la regla 3 de
`linea-grafica.md` pedía ducking y swell final, la corrida DTW pedía cama
constante, y el código hacía las dos cosas según el motor.

| | antes | ahora |
|---|---|---|
| `music.py` (reels) | `sidechaincompress` threshold 0.030 ratio 6 | ⛔ fuera |
| `apply_music.py` (DTW) | ganancia fija `volume=0.04`… | …y el comentario decía «con ducking» |
| nivel de la cama | un factor escrito a mano | se **mide** la cama y se lleva a −39 LUFS |
| swell final | siempre activo, +1,75 de ganancia | programado y **apagado** |

**El nivel no se fija a ojo.** Un `volume=0.04` sirve para el beat de hip-hop de
DTW (−10,6 LUFS de partida) y no para el pad de `music.py` (−20 LUFS): el mismo
factor da resultados que no se parecen. Ahora los dos motores miden su cama con
`ebur128` y calculan la ganancia que la deja en **−39 LUFS**, la cifra que Piero
aprobó tras pedir bajarla varias veces.

**Medido en las dos direcciones.** Con un clip de prueba —voz a 2 500 Hz en
ráfagas de 1 s, cama a 180 Hz— se aísla la cama con un paso bajo y se compara su
nivel en los tramos con voz y sin voz:

| motor | con voz | sin voz | diferencia | |
|---|---:|---:|---:|---|
| `music.py` nuevo | −29,71 dB | −30,10 dB | **−0,39 dB** | cama plana |
| `music.py` viejo | −22,39 dB | −18,51 dB | **+3,88 dB** | duckea |
| `apply_music.py` | −35,25 dB | −36,07 dB | **−0,82 dB** | cama plana |

La fila del medio es la que importa: demuestra que la prueba **sí detecta** un
ducking, así que el «cama plana» de las otras dos no es un falso negativo.

El master sale a **−13,9 LUFS** contra el objetivo de −14. Y sigue escrito en el
JSON que ese −14 **no tiene página oficial de Google**: la norma que aplicaría a
una pieza corta de campaña es EBU R128 s1 (−23 LUFS, pico real −1 dBTP). Se
mantiene −14 porque es lo que ya está en producción, no porque esté normado.

⚠️ El swell se queda programado y apagado, no borrado: «cama constante» quiere
decir constante, pero la regla de julio era tuya. Encenderlo es
`swell.activo: true` en el JSON, sin tocar código.

### Y el espacio de color, que no se etiquetaba

El master de `mezzanine.py` salía sin declarar nada y el reproductor lo
adivinaba. Ahora sale con `-color_range tv -colorspace bt709 -color_primaries
bt709 -color_trc bt709`, verificado con `ffprobe` sobre un master real.

### Qué pasa fuera de este Mac

Las skills viven en `~/.claude/skills/` y el JSON en el workspace. Si el JSON no
está —otra máquina, la skill sola— los motores **caen a los mismos valores
escritos en el propio módulo** y lo dicen: `grade: base (de respaldo local)`.
Probado en las dos direcciones.

---

## 7 · Lo que decides tú

1. **Si el swell final vuelve**: hoy está apagado porque «cama constante» lo
   dice, pero la regla de julio era tuya y se enciende con una línea.
2. **Si `calido` sigue siendo el look de DTW** o si DTW pasa también a `base`.
   Hoy lo mantiene, porque quitárselo cambia el aspecto de una línea entregada.
3. **Si hay LUT de marca**: es diseño, no programación.
4. **El logo sonoro**: si el movimiento tiene firma sonora o no.
5. **La zona segura de orgánico**: nadie la publica, así que es criterio nuestro
   y hay que fijar un número y escribirlo una vez.
6. **El rótulo de ponente**: cuánto dura en pantalla y cuándo reaparece (el
   consenso son 3–7 s, sin norma), si el de la skill de reels lleva la paleta de
   GEW o la de IAvanza —conviven las dos marcas en la misma skill—, y qué patrón
   se usa con dos ponentes a la vez.
