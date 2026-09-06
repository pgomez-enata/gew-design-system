# Estandarizar las salidas · qué falta y qué se puede usar

Levantado el 5-sep-2026 sobre el sistema tal como está hoy: **11 motores,
3 907 líneas, 394 PNG y 1 PDF en `_salida/`**. Cada hueco de abajo está
medido, no supuesto; el comando que lo midió va entre corchetes.

---

## Parte 1 · El diagnóstico

### 1.1 · La auditoría cubre unas familias ocho veces mejor que otras

| Familia | Piezas | Comprobaciones | Por pieza |
|---|---:|---:|---:|
| campaña (raíz) | 105 | 885 | **8,4** |
| actividad | 9 | 39 | 4,3 |
| cita | 12 | 48 | 4,0 |
| video | 12 | 42 | 3,5 |
| serie | 28 | 84 | 3,0 |
| impreso | 4 | 10 | 2,5 |
| aliados | 192 | 432 | 2,2 |
| **revista** | **32** | **32** | **1,0** |

[comando: `auditoria.audita()` sobre cada fichero, agrupado por carpeta]

**Y la única comprobación que recibe la revista, falla.** `auditoria.py`
reparte por carpeta y no tiene ramal para `revista/`: las 32 páginas caen en
el ramal genérico, que exige un sufijo `--<formato>` en el nombre. Como se
llaman `01.png` … `32.png`, la corrida entera devuelve **32 FALLA** y sale con
código 1.

```
394 piezas · 1572 comprobaciones
  FALLA  formato reconocible: 01.png (umbral sufijo --<formato>) — 1 pieza(s)
  … × 32
```

Esto ya me pasó una vez con los titulares de la revista y lo volví a repetir:
**el informe de `revista.py` dice verde, pero el guardián del sistema no está
mirando ahí.** Son dos informes distintos y sólo uno de ellos es el que manda.

### 1.2 · 358 de 394 ficheros salen sin una sola línea de metadatos

| Metadatos que lleva el PNG | Ficheros |
|---|---:|
| ninguno | **358** |
| sólo `dpi` | 36 |
| autoría, créditos, licencia, fecha, versión del sistema | **0** |
| perfil ICC embebido | **0** |

[comando: `PIL.Image.open(p).info` sobre los 394]

Una pieza que sale del taller no sabe decir quién la hizo, de qué campaña es,
con qué versión del sistema, ni bajo qué condiciones se puede usar. En cuanto
se reenvía por WhatsApp, es un PNG anónimo.

### 1.3 · 48 ficheros se llaman exactamente igual

| | |
|---|---:|
| ficheros PNG | 394 |
| nombres **únicos** | **206** |
| con fecha | **0** |
| con número de versión | **0** |
| con prefijo de campaña | **0** |
| `somos-aliados--historia.png` | **48 copias** |

[comando: conteo sobre `os.path.basename` de los 394]

Dentro de su carpeta cada uno es el de su aliado. Fuera de ella —que es donde
acaban, en la carpeta de descargas de otra persona— son 48 ficheros idénticos
de nombre y distintos de contenido.

### 1.4 · El PDF de la revista no tiene texto: son 32 fotos de texto

```
$ pdffonts _salida/revista/revista.pdf
name    type    encoding    emb sub uni object ID
------  ------  ----------  --- --- --- ---------
                                              ← vacío
```

Ni una fuente embebida: las 32 páginas son PNG de 300 dpi pegados en un PDF de
**9,5 MB**. Consecuencias reales: una errata obliga a re-renderizar en vez de
corregir; el texto pequeño llega a la imprenta con antialias en vez de nítido;
no se puede buscar ni seleccionar; y no puede ser un PDF accesible.

Comparación con el sistema hermano, que sí lo resolvió:

```
$ pdffonts p4f_design_system/…/p4f-patrocinadores.pdf
AAAAAA+Saira-Regular   TrueType  WinAnsi  yes yes yes
AAAAAA+Saira-Bold      TrueType  WinAnsi  yes yes yes
```

### 1.5 · Once motores, once maneras de llamarlos

No hay `Makefile`, ni script de orquestación, ni manifiesto de lo producido.
Y los nombres de los interruptores no concuerdan entre sí:

| Motor | El interruptor de «hazlo todo» |
|---|---|
| `campana.py` | `--todas` |
| `impreso.py` | `--todos` |
| `serie.py` | `--todos` |
| `video.py` | `--todos` |
| `aliado.py` | `--kits` |
| `actividad.py` | `--demo` |
| `revista.py` | `--pliego` |
| `cita.py` | `--demo` |
| `prensa.py` | (ninguno) |

[comando: `grep add_argument` sobre los 11 motores]

### 1.6 · 222 frases de texto viven dentro del código

| Motor | Cadenas de copy en el `.py` |
|---|---:|
| revista.py | **103** |
| serie.py | 25 |
| prensa.py | 21 |
| impreso.py | 11 |
| los otros 7 | 62 |
| **total** | **222** |

[comando: extracción de literales en español de >20 caracteres, sin docstrings]

Sólo `campana.json` y `prensa.json` tienen el texto fuera. Cambiar una coma de
la revista es editar Python.

---

## Parte 2 · Los elementos, para seleccionar

Cada uno con lo que cierra, qué hace falta instalar, y cuánto pesa. El
número es para que me digas cuáles.

### Bloque A — cerrar lo que ya está roto

**1 · Ramal de revista en la auditoría**
Hoy la revista recibe 1 comprobación y falla. Ponerle su ramal —lienzo con
sangrado 2620×3370, zona de seguridad de 6 mm, tinta dentro de caja, folio
presente, creep compensado, glifos— la sube a la altura de las demás familias.
*Instalar: nada. Trabajo: medio.* **Es el más urgente: sin esto la corrida del
sistema sale en rojo.**

**2 · Metadatos incrustados en cada pieza**
Autor, créditos, licencia, campaña, versión del sistema y fecha, dentro del
propio fichero. Lo probé en esta máquina: **Pillow escribe el bloque XMP en un
PNG vía chunk `iTXt` y lo relee**, sin instalar nada.
```
escrito OK, releo: {'Author': 'Fundacion Enlata', 'Copyright': '(c) 2026',
 'xmp': b'<x:xmpmeta …>', 'XML:com.adobe.xmp': '<x:xmpmeta …>'}
```
El estándar de campos es **IPTC Photo Metadata 2025.1** (nov-2025): `dc:creator`,
`photoshop:Credit`, `dc:rights`, `xmpRights:WebStatement`. Para JPEG haría falta
`exiftool` (`brew install exiftool`), pero no producimos JPEG.
*Instalar: nada. Trabajo: bajo.*

**3 · Nomenclatura única y fechada**
Un patrón para las 394: `gew26-<familia>-<pieza>--<formato>-<fecha>-v<NN>.png`.
Mata las 48 colisiones y hace que un fichero suelto se pueda ubicar.
Lo comprobé antes de darlo por caro: **el `index.html` no se rompe**. Es
autocontenido —sus 16 imágenes van en base64 y no hay ni una ruta a
`_salida/`—, así que renombrar no arrastra nada detrás.
*Instalar: nada. Trabajo: medio, toca los 11 motores.*

**4 · PDF de la revista con texto vivo**
**`reportlab 5.0.0` ya está instalado en esta máquina.** Y `p4f_design_system/pdf.py`
(504 líneas) ya resolvió exactamente esto: reproduce las operaciones del lienzo
sobre un canvas de reportlab, con las fuentes embebidas. Es el patrón a copiar,
no a reinventar.
*Instalar: nada. Trabajo: alto — es el más caro de la lista.*

**5 · Manifiesto de cada corrida**
Un `manifiesto.json` por tanda: qué se produjo, cuándo, con qué versión de
tokens, qué entradas se usaron, y el hash de cada fichero. Hoy no existe: no
hay forma de saber si el PNG que tienes en el escritorio es el vigente.
*Instalar: nada. Trabajo: bajo.*

### Bloque B — estándares de fuera que sí encajan

**6 · Formato DTCG para `tokens.json`**
El **Design Tokens Format Module 2025.10** salió como versión estable el
28-oct-2025 (designtokens.org/tr/2025.10/format/). Es JSON plano: cada token
lleva `$value` y `$type`, con `$description` y `$extensions` para la
procedencia — que es justo lo que ya hacemos a mano. Adoptar el *formato* hace
que Figma y Tokens Studio lean nuestros tokens sin traducción.
⚠️ **La herramienta Style Dictionary (v5.5.2) no la recomiendo**: es Node, y el
motor ya lee JSON en Python. Se adopta el vocabulario, no la maquinaria.
*Instalar: nada. Trabajo: bajo, pero toca todos los motores que leen tokens.*

**7 · `$deprecated` para retirar activos sin romper lo publicado**
La misma spec define `$deprecated` (booleano o texto con el motivo). Encaja
exacto con la regla vigente de que lo publicado no se retoca: el activo
retirado sigue resolviendo, pero queda marcado para trabajo nuevo. Aplicable
ya a la pastilla índigo de Enlata y al badge global en inglés.
*Instalar: nada. Trabajo: bajo.*

**8 · Contrato de entradas con JSON Schema**
Un `.schema.json` por motor, declarando qué necesita y de qué tipo. **Draft
2020-12** sigue siendo el vigente. Se valida en Python con la librería
`jsonschema` (`pip install jsonschema` — hoy **no está instalada**). Sirve
para que un motor se niegue a renderizar con datos incompletos en vez de
sacar una pieza con un hueco.
⚠️ Para que rellenes un formulario web en vez de un JSON haría falta una capa
en React (RJSF o JSON Forms). Eso es otro proyecto, no lo meto aquí.
*Instalar: `jsonschema`. Trabajo: medio.*

**9 · Perfil de color y verificación de gamut CMYK**
Hoy los 394 salen **RGB sin perfil embebido**. Para la revista impresa eso
significa que la imprenta decide el color por ti. Esta máquina ya tiene
`tificc` (Little CMS) y el `Generic CMYK Profile.icc` de macOS, así que la
comprobación de fuera de gamut se puede montar sin instalar nada.
⚠️ El perfil bueno no es el genérico de Apple: **lo tiene que dar la imprenta**,
y sigue sin decidirse cuál es.
*Instalar: nada para probar; el perfil real lo pone la imprenta. Trabajo: medio.*

**10 · PDF/X para la imprenta**
Depende del 4. PDF/X-1a es el que piden las revistas por compatibilidad;
PDF/X-4 mantiene transparencia y color vivos pero no todo RIP lo acepta.
Ghostscript (`brew install ghostscript`, hoy no está) genera X-1 y X-3, no
X-1a ni X-4 literales; X-4 real exige InDesign o Acrobat.
*Instalar: Ghostscript. Trabajo: medio. **Preguntar primero a la imprenta.***

### Bloque C — que un cambio no rompa lo que ya salía bien

**11 · Imágenes de referencia (regresión visual)**
Guardar una copia aprobada de cada pieza y comparar en cada corrida. Con
`scikit-image` (`structural_similarity`) o ImageMagick `compare -metric SSIM`.
Ninguno de los dos está instalado; `numpy 2.0.2` sí, y con eso ya se puede
hacer una comparación píxel a píxel decente.
⚠️ **No hay umbral normativo.** El 0,1 % de píxeles distintos o SSIM 0,99 que
circula son convenciones de la industria, no una norma. El umbral lo calibro y
lo dejo escrito, no lo copio de un blog.
*Instalar: nada si vamos con numpy. Trabajo: medio.*

**12 · Puerta única antes de publicar**
`iavanza_design_system/prepublicar.py` (442 líneas) y el de P4F (667) ya son
esto: la puerta que revisa antes de que algo salga del taller. GEW no tiene
ninguna. Se adapta, no se escribe de cero.
*Instalar: nada. Trabajo: medio.*

**13 · Comprobación de entorno**
`iavanza_design_system/entorno.py` (152 líneas) comprueba que la máquina tiene
lo que el sistema necesita **antes** de empezar. Aquí serviría de inmediato:
acabo de descubrir midiendo que **no están instalados exiftool, ImageMagick,
Ghostscript, qpdf, scikit-image ni jsonschema**, y que **sí están** reportlab
5.0.0, tificc, pdffonts, rsvg-convert 2.62.3 y numpy 2.0.2. Eso debería
decirlo un comando, no un rato de investigación.
*Instalar: nada. Trabajo: bajo.*

**14 · Tope de peso por plataforma**
Medido hoy: 394 PNG, 74,4 MB en total, el mayor de 5,89 MB. Ninguna pieza de
redes pasa de 2 MB; las 4 que sí lo hacen son páginas de revista, donde no
aplica. Está sano, pero nadie lo está vigilando: conviene que sea una regla de
la auditoría antes de que deje de estarlo.
*Instalar: nada. Trabajo: bajo.*

### Bloque D — lo que ya está hecho en los sistemas hermanos

No son ideas: son ficheros que existen, funcionan y se pueden adaptar.

| Fichero | Líneas | Qué hace | ¿En GEW? |
|---|---:|---|---|
| `iavanza/build.py` | 1 300 | orquestador único del sistema | **no** |
| `p4f/nucleo.py` | 1 367 | núcleo con el lienzo abstracto | **no** |
| `p4f/pdf.py` | 504 | PDF vectorial con texto vivo | **no** |
| `iavanza/empaquetar.py` | 767 | convierte el sistema en repo público | **no** |
| `iavanza/prepublicar.py` | 442 | la puerta antes de publicar | **no** |
| `p4f/escanear_fuera.py` | 173 | audita el repo ya publicado, desde fuera | **no** |
| `iavanza/entorno.py` | 152 | comprueba la máquina antes de empezar | **no** |
| `iavanza/INVENTARIO.md` · `DECISIONES.md` | — | inventario y bitácora de decisiones | **no** |

**15 · Orquestador único** (`build.py` o un `Makefile`). Un comando que lo
construye todo y unifica los interruptores: hoy son `--todas`, `--todos`,
`--kits`, `--demo` y `--pliego` para la misma idea.
*Instalar: nada. Trabajo: bajo si es Makefile, medio si es build.py.*

**16 · Copy fuera del código.** Los 222 literales a JSON, empezando por los
103 de la revista. Es la condición para que puedas cambiar un texto sin que yo
toque Python.
*Instalar: nada. Trabajo: alto en revista, bajo en el resto.*

**17 · `INVENTARIO.md` y `DECISIONES.md`.** El sistema ya arrastra 4 decisiones
cerradas y 5 pendientes dentro de `tokens.json`. Sacarlas a un fichero propio
con fecha y autor es lo que hace IAvanza.
*Instalar: nada. Trabajo: bajo.*

**18 · Control de versiones.** ⚠️ **Ninguno de los tres sistemas de diseño está
en git.** No hay historial, no hay vuelta atrás, no hay forma de saber qué
cambió entre el lunes y hoy. Semver aplicado a un design system es práctica
del gremio, no norma —MAJOR si se quita o cambia de significado un token,
MINOR si se añade, PATCH si se corrige un valor—, pero el historial sí es
elemental.
*Instalar: nada. Trabajo: bajo. **Es el elemento con mejor relación entre lo
que cuesta y lo que evita.***

### Bloque E — los formatos, cotejados contra lo que publican las plataformas hoy

Fui a las fuentes primarias de cada plataforma. El resultado más útil es
saber **qué de lo que damos por norma no lo es**.

Nuestros 7 formatos, uno por uno:

| Nuestro formato | px | Veredicto |
|---|---|---|
| `enlace` | 1200×627 | **Coincide exacto** con lo que publica LinkedIn (1,91:1, tope 3 MB). Vigente. |
| `yt-miniatura` | 1280×720 | **Vigente**: sigue siendo el recomendado. Google añade que se puede subir hasta 3840×2160. |
| `retrato` | 1080×1350 | Mismo 4:5 que la ficha oficial de Meta, pero **la ficha dice 1440×1800**. No está mal, está por debajo. |
| `cuadrado` | 1080×1080 | Sin ficha oficial que cotejar. |
| `historia` / `-abierta` / `-ads` | 1080×1920 | Sin ficha oficial que cotejar. |

**⚠️ Meta no publica especificaciones para publicaciones orgánicas de
Instagram.** Sólo publica las de anuncios. El «1080×1080 / 1080×1350 /
1080×1920» que usa todo el mundo —nosotros incluidos— es consenso de terceros
sobre lo que la plataforma acepta, no un documento de Meta. Funciona; pero no
es una norma y conviene no citarla como tal.

**⚠️ Y hay que reabrir nuestra zona segura de historias.** Tenemos
`historia-ads` con la franja 269–1248, sacada de los porcentajes 14 % / 35 %.
La búsqueda en el sitio de Meta **no encontró esas cifras publicadas en
texto**: lo que Meta ofrece es una guía visual dentro del Ads Manager, y los
píxeles que circulan son mediciones de terceros sobre esa herramienta. Antes de
tratar el 1248 como oficial hay que volver a la fuente.

**La única zona segura oficial con cifra que encontré en todo el barrido** es
la portada de canal de YouTube: **1546×423** es la franja visible en todos los
dispositivos (support.google.com/youtube/answer/2972003). De Shorts y de TikTok
no hay artículo con cifras: todo lo que circula es de guías de terceros.

**19 · Tres formatos que faltan y sí tienen ficha oficial**

| Pieza | px | Tope | Fuente |
|---|---|---|---|
| Portada de canal de YouTube | 2560×1440, zona segura 1546×423 | — | support.google.com/youtube/answer/2972003 |
| Portada de página de LinkedIn | 1512×256 | 3 MB | linkedin.com/help/linkedin/answer/a563309 |
| Logo de página de LinkedIn | 400×400 (mín. 268×268) | 3 MB | ídem |

Los tres son piezas de perfil, no de campaña: se hacen una vez y se quedan
puestas. Es el elemento más barato de todos.
*Instalar: nada. Trabajo: bajo.*

**20 · Texto alternativo como salida del sistema**
Hoy cada pieza sale sin su alt escrito, así que lo redacta quien publica, si se
acuerda. El motor sabe qué dice la pieza: puede escribir el alt en un `.txt`
al lado del PNG. **La única plataforma que publica un límite es X: 1 000
caracteres.** LinkedIn y Meta no lo publican, y el «120 caracteres» que circula
es de blogs.
*Instalar: nada. Trabajo: bajo.*

**21 · Nomenclatura con respaldo institucional** (refina el elemento 3)
Dos guías concretas, por si el patrón se discute:
- **Harvard Medical School**: `[ID]_[YYYYMMDD]_[secuencia]_[estado]`, fecha ISO
  sin guiones, versión al final (`_v01`), 40–50 caracteres, sin espacios ni
  signos.
- **Oklahoma State University Library**: `institución_departamento_IDobjeto_parte.ext`,
  sólo guion y guion bajo, máximo 31 caracteres.

Nuestro `--` doble como separador de formato no aparece en ninguna guía, pero
es inequívoco y ya está en 310 de 394 ficheros. Lo mantendría.

**22 · El index enseña 16 piezas de 394**
El `index.html` es autocontenido y lleva 16 imágenes en base64 sobre 17
secciones. Está bien como vista del sistema, pero **no es un catálogo**: el 96 %
de lo que produce el taller no se ve por ahí. Si lo que quieres es poder
enseñarle a un aliado todo lo que existe, eso es una galería aparte que lea
`_salida/` en vez de llevar las imágenes dentro.
*Instalar: nada. Trabajo: bajo.*

---

## Parte 3 · Lo que investigué y NO recomiendo

Va aquí para que no se proponga otra vez dentro de tres meses.

**C2PA / Content Credentials.** Firma criptográfica dentro del fichero, con
cadena de custodia. La herramienta se fusionó en `contentauth/c2pa-rs` en
dic-2024 y funciona. Pero exige montar infraestructura de firma y confianza, y
eso se justifica en fotoperiodismo o en verificación anti-IA, no en 394 piezas
de una campaña. El XMP del punto 2 da la atribución sin el aparato.

**Style Dictionary.** v5.5.2, ago-2026, ya entiende el formato DTCG. Es Node.
Meter una cadena de build en JavaScript para alimentar motores que ya leen JSON
en Python es coste sin ganancia. Adoptamos el formato, no la herramienta.

**APCA para medir contraste.** Es el algoritmo que se proponía para WCAG 3.
**Fue retirado del borrador a mediados de 2023 por falta de consenso**, y a
día de hoy WCAG 3 sigue en Working Draft con el algoritmo de contraste sin
decidir. No es normativo, ninguna legislación lo referencia, y no hay librería
de referencia en Python. Nos quedamos con WCAG 2.2, que es lo que ya mide la
auditoría.

**Formulario web sobre JSON Schema (RJSF / JSON Forms).** Funcionan y están
vivos, pero son React. Es un proyecto aparte, no un elemento de este sistema.

**PDF/UA completo.** ReportLab 4+ genera PDF etiquetado con `tagged="1"` y pasa
el validador en casos simples. Una revista de 32 páginas con esta maquetación
no es un caso simple: la vía probada sigue siendo InDesign más Acrobat Pro.
Si la revista se va a distribuir en digital, conviene decidirlo aparte.

---

## Parte 4 · Dos cosas de las que investigué que conviene que sepas

**No hay norma de tamaño mínimo de texto en una imagen.** Busqué ISO, W3C y las
guías de las plataformas. Lo único cercano es ISO 9241-303, que da tamaño
angular para pantallas —ergonomía, no diseño gráfico— y el umbral de Lighthouse,
que es una heurística de una herramienta. El «16 px mínimo en móvil» que
circula no es un estándar. Lo que hagamos aquí será una regla nuestra, y hay
que escribirla como tal.

**Tampoco hay método normativo para medir contraste sobre una foto.** WCAG 2.2
fija los umbrales (4,5:1 y 3:1) pero asume fondo uniforme; para una imagen con
variación deja la excepción sin procedimiento de cálculo. La práctica del
gremio es medir en el punto peor del área de texto, normalmente detrás de un
velo. Es lo que ya hace el sistema con el velo de los subtítulos y el degradado
de la variante B — pero conviene saber que eso es criterio nuestro, no norma.

---

## Parte 5 · Lo que decides tú

1. **Cuáles de los 22 elementos entran, y en qué orden.** Mi recomendación de
   arranque, por relación coste-beneficio: **1** (la auditoría está en rojo),
   **18** (git, quince minutos), **13** (entorno), **2** (metadatos), **5**
   (manifiesto) y **19** (los tres formatos de perfil que faltan). Los seis
   juntos no llegan al coste del **4** solo.
2. **Si se renombran las 394 salidas** (elemento 3). Rompe el `index.html`, así
   que es ahora o no es.
3. **Si la revista pasa a PDF vectorial** (elemento 4). Es el más caro con
   diferencia, y sólo merece la pena si de verdad se imprime.
4. **Perfil ICC de la imprenta.** Sigue pendiente desde el trabajo de la
   revista. Sin ese dato, los elementos 9 y 10 se quedan a medias.

Y sigue abierto lo de antes: la fuente de cifras de GEN, la frase de Kauffman,
el gramaje del papel, el origen de la licencia de VAG Rounded, y los nombres en
español de las 6 audiencias.
