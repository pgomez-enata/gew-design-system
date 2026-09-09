# Vídeo · qué más se debería poder crear

Catálogo para decidir. Cada propuesta lleva **qué es**, **para qué**, y **qué
cuesta**. Nada de esto está construido: es la lista de la que Piero elige.

Lo que sigue arranca de lo que el sistema **ya hace hoy**, medido:

| | Hoy |
|---|---|
| Piezas de vídeo | apertura (3 s) · cuenta atrás (4 s) · endcard (5 s) · marco/overlay · guías · lower third · 4 bucles del pulso |
| Lienzos de vídeo | **4**: 1920×1080 · 1080×1920 · 1080×1080 · 1920×270 (banda) |
| Lienzos de imagen | **8** — de los que **6 no tienen equivalente en vídeo** |
| Transiciones | **4 técnicas**: fundido, mezcla hacia el fondo, desplazamiento, escalado, más el barrido del pulso |
| Curvas de aceleración | **1**: `suave`, una cúbica que frena al final |
| Entradas | 9 en total, todas del mismo tipo |
| **Salidas** | **ninguna** |

## ⚠️ El hueco más grande: ninguna pieza SALE

Medido sobre los siete MP4: al llegar al último fotograma queda en pantalla
entre el **91,6 % y el 98,7 %** de la tinta que había a mitad de pieza. Es decir,
**todas terminan en seco**. Entran bien y se cortan de golpe.

Eso obliga al montador a resolverlo a mano en cada uso, y es la diferencia entre
un kit que se monta solo y uno que hay que rematar pieza por pieza.

---

## 1 · Entradas y salidas — el catálogo que falta

Hoy hay **una** curva y **cero** salidas. La propuesta es un catálogo con nombre,
para que una pieza se describa como «entra `sube`, sale `apaga`» y no como una
fórmula suelta dentro de cada función.

### Curvas
| Nombre | Qué hace | Para qué |
|---|---|---|
| `frena` | cúbica que desacelera *(la única que hay hoy)* | entradas de elementos con peso: lockup, cifra |
| `arranca` | acelera al empezar | salidas: lo que se va, se va rápido |
| `frena-y-arranca` | suave en los dos extremos | desplazamientos largos |
| `golpe` | llega, se pasa un poco y vuelve | acentos sobre el tiempo fuerte |
| `escalón` | sin interpolación, salta | corte al tiempo, para lo que debe sentirse duro |

### Entradas
| Nombre | Qué hace |
|---|---|
| `aparece` | fundido desde el fondo *(existe)* |
| `sube` | entra desplazándose y se asienta *(existe, sólo para el lockup)* |
| `barre` | el pulso aparece de izquierda a derecha *(existe)* |
| `crece` | escala desde el 72 % *(existe, sólo para la cifra)* |
| `abre` | una banda de color se retira y descubre lo que hay debajo |
| `escribe` | el texto entra por palabras, sobre corcheas |

### Salidas — **ninguna existe**
| Nombre | Qué hace |
|---|---|
| `apaga` | fundido al carbón, 6 fotogramas |
| `baja` | se va por donde entró |
| `cierra` | el pulso crece hasta tapar la pantalla y corta |
| `encoge` | al revés que `crece` |
| `mantiene` | se queda: es lo correcto para un endcard que va al final del todo, y **debe poder pedirse a propósito**, no ser lo único posible |

**Coste**: es el más barato de todos los puntos de este documento y el que más
cambia el resultado. Todo se apoya en la rejilla que ya existe: una entrada dura
media corchea, una corchea o un tiempo, no «0,45 s».

---

## 2 · Transiciones entre piezas

Hoy no existe el concepto: cada pieza es un fichero suelto y el paso de una a
otra lo resuelve quien monta.

| Transición | Qué es | Cuándo |
|---|---|---|
| `corte-al-tiempo` | corte duro que cae exactamente en el tiempo fuerte | lo más barato y lo que más se nota con música |
| `pulso-cortina` | las barras crecen hasta llenar la pantalla, cortan, y decrecen en la pieza siguiente | entre bloques de un recap |
| `banda-wipe` | la banda de marcas cruza la pantalla y al pasar deja la escena nueva | cambio de sección |
| `carbon-6` | fundido al carbón de 6 fotogramas y vuelta | el neutro, para cuando no hay que llamar la atención |
| `pulso-hilo` | el pulso **no se corta** entre clips: sigue sonando y es lo único continuo | recap largo, da sensación de una sola pieza |

⛔ Lo que no se puede hacer: nada que gire, recorte o despliegue el anillo. Sería
el logo troceado, y la regla del sistema es logos completos.

---

## 3 · El corte tiene que caer en el tiempo

**CERRADO el 6-sep-2026.** `cuenta` pasó a **4,2 s** (7 tiempos) y `endcard` a
**4,8 s** (8 tiempos). Las tres caen ahora en tiempo entero, y el endcard mide
exactamente un bucle del pulso.

Propuesta: que toda pieza declare su duración **en tiempos**, no en segundos, y
que el motor derive los segundos. Un catálogo de duraciones utilizables a
100 BPM, todas en fotogramas exactos a 30 fps:

| Tiempos | Segundos | Fotogramas | Para qué |
|---|---|---|---|
| 2 | 1,2 | 36 | sting entre clips |
| 4 (1 compás) | 2,4 | 72 | bumper corto, transición |
| 8 (2 compases) | 4,8 | 144 | **el bucle del pulso**, endcard, overlay |
| 10 | 6,0 | 180 | el formato de anuncio no saltable de 6 s |
| 16 (4 compases) | 9,6 | 288 | apertura larga, cuenta atrás |
| 25 | 15,0 | 450 | historia / corte de 15 s |
| 50 | 30,0 | 900 | corte de 30 s |

Y una **pista de clic a 100 BPM** entregada junto al kit, para que quien monte
alinee la música sin adivinar. Las piezas seguirían saliendo sin audio.

---

## 4 · Piezas que no existen

Ordenadas por el momento de la campaña en que hacen falta.

### Antes del evento
| # | Pieza | Qué es | Por qué |
|---|---|---|---|
| 1 | **Sting de marca** (1,2 s) | el lockup con el pulso, entra y sale | el pegamento entre clips; hoy no hay nada de menos de 3 s |
| 2 | **Bumper de 6 s** | pieza cerrada de 6 s, con entrada y salida | es el formato de anuncio no saltable; con 10 tiempos cae exacto |
| 3 | **Invitación por aliado** | la misma pieza con el logo y el nombre de cada aliado | son 48 aliados; hoy se haría a mano 48 veces |
| 4 | **Cuenta atrás por semana** | la que existe, pero en serie: 7, 6, 5… | hoy hay que lanzarla una a una |
| 5 | **Anuncio de actividad** | título, fecha, hora, lugar y organizador, animados | el formato con más demanda de la semana y no existe en vídeo |

### Durante el evento
| # | Pieza | Qué es | Por qué |
|---|---|---|---|
| 6 | **Bucle de espera para pantalla** | fondo en bucle para proyectar entre sesiones | hoy no hay nada para la pantalla de sala |
| 7 | **Cuenta regresiva de sala** | «empezamos en 5:00», descontando | distinta de la cuenta atrás de días |
| 8 | **Cartela de siguiente sesión** | «a continuación: …» | para la pantalla y para el streaming |
| 9 | **Lower third que entra y sale** | el que existe, pero animado | hoy es un PNG: entra cuando el montador quiere |
| 10 | **Marca de agua persistente** | lockup pequeño en esquina, con zona segura resuelta | para streaming largo |
| 11 | **Cartela de EN VIVO** | indicador con el pulso latiendo | sólo tiene sentido animado |

### Después del evento
| # | Pieza | Qué es | Por qué |
|---|---|---|---|
| 12 | **Plantilla de recap** | estructura montable: apertura, bloques, cifras, cierre | existe en revista y en PNG, no en vídeo |
| 13 | **Tarjeta de cifra** | un dato grande que entra sobre el pulso | las cifras del recap hoy sólo existen impresas |
| 14 | **Cita en movimiento** | la tarjeta de cita, animada | existe en PNG |
| 15 | **Muro de aliados en movimiento** | los logos pasando en banda | 48 logos; la banda de 1920×270 ya está |
| 16 | **Agradecimiento a patrocinadores** | la placa, animada | el hueco ya está reservado en todas las piezas |

### Transversales
| # | Pieza | Qué es | Por qué |
|---|---|---|---|
| 17 | **Subtítulos quemados** | el sistema ya reserva la zona, pero no escribe en ella | es lo que hace que un vídeo funcione en silencio |
| 18 | **Fondo animado de videollamada** | 1920×1080 en bucle | para las sesiones en línea |
| 19 | **Pista de clic a 100 BPM** | audio de referencia junto al kit | para que quien monte alinee la música sin adivinar |

---

## 5 · Dimensiones

### El que falta y se usa todos los días
**1080×1350 (4:5)** — existe en imagen (`retrato`) y **no en vídeo**. Es el vídeo
de feed que más superficie ocupa en un móvil. De los 8 lienzos de imagen del
sistema, 6 no tienen equivalente en vídeo, pero los otros 5 son portadas y
miniaturas que no necesitan moverse. **Éste sí.**

**Y no es una estimación: lo probé.** Metí 1080×1350 en el motor del pulso como
un formato más y salió a la primera — **0 solapes**, plano recalculado solo,
1 080×1 350 · 4,8 s · 144 fotogramas · 5 881 kbps · 3,53 MB, **1,3 s de render**.
Los planos se calculan con medidas, así que un lienzo nuevo no obliga a
recomponer nada. Añadirlo a los tres motores es de las cosas más baratas de
esta lista.

### Pantalla de evento — y lo que NO se puede decidir aquí
No existe una resolución de entrega estándar para un LED de escenario: **cada
muro tiene su resolución nativa según su pixel pitch**, y el proveedor de AV
pide el contenido a esa resolución y a ese aspecto exactos. Fuentes: blogs del
sector, no norma publicada.

Lo que sí es norma: **ANSI/AVIXA V202.01 (DISCAS)**, «Display Image Size for 2D
Content», que da la fórmula del alto de imagen necesario según la distancia del
espectador más lejano —`IH = FV / (200 × %EH)` en el método de decisión básica—.
Existe también **ANSI/AVIXA V201.01:2021** de relación de contraste, pero es de
pago y sus valores no están en fuentes abiertas.

**Comprobé nuestra regla de señalética contra esa norma, y sale bien.** `senal.py`
usa «2,54 cm de alto de letra por cada 3,05 m», que es `alto = distancia / 120`.
DISCAS, para el propio texto, pide `alto = distancia / 200`. O sea: **nuestra
regla exige letras 1,67× más altas que el mínimo de la norma**, en las cinco
piezas por igual.

| Pieza | Alto de letra que pedimos | Se lee a | Mínimo DISCAS | Margen |
|---|---|---|---|---|
| direccional | 6,67 cm | 8,0 m | 4,00 cm | **1,67×** |
| sala | 4,17 cm | 5,0 m | 2,50 cm | 1,67× |
| registro | 2,50 cm | 3,0 m | 1,50 cm | 1,67× |
| puerta | 1,67 cm | 2,0 m | 1,00 cm | 1,67× |
| wifi | 0,83 cm | 1,0 m | 0,50 cm | 1,67× |

Estamos **del lado seguro**, no del peligroso. Lo que sí conviene es escribir en
`senal.py` de dónde sale la regla y que es más exigente que DISCAS, para que
nadie la «optimice» a la baja creyendo que sobra margen.

⚠️ Aparte: la cifra de «≥48 pt en 1080p» que circula **sale de un blog que
interpreta DISCAS, no de AVIXA**. No la usemos.

**Propuesta**: no fijar un lienzo de pantalla de evento por nuestra cuenta. En su
lugar, que el motor **acepte cualquier lienzo** y avise si el aspecto se aleja
tanto que la composición deja de funcionar. El proveedor da la cifra; nosotros
damos el fichero.

### WhatsApp
La única fuente **oficial verificada** es la documentación de Meta for
Developers: **mp4, H.264 perfil Main o Baseline** (evitar High con B-frames en
Android), audio AAC, tope de 100 MB en la API. Las cifras que circulan del lado
de consumidor —90 s de Estado, 16 MB, 720p en HD— vienen de prensa y de terceros
que dicen citar el FAQ; **no se pudo verificar el texto del FAQ**.

Consecuencia práctica: nuestras piezas ya salen en H.264, pero en **perfil High**.
Para WhatsApp conviene una salida en **Main**, que es lo que Meta documenta.

---

## 6 · Subtítulos: lo que sí está normado

El sistema ya reserva la zona de subtítulos en el marco y le pone un velo, pero
**no escribe nada en ella**. Si se construye, estas son las cifras y de dónde
salen — porque aquí sí hay norma y guías reales:

| Qué | Cifra | Quién lo dice | Tipo |
|---|---|---|---|
| Formato | **WebVTT** | W3C, *WebVTT: The Web Video Text Tracks Format* | **norma** |
| Formato | SRT | — | **sin norma formal**: nadie lo regula |
| Velocidad | 160–180 palabras/min (~15 car/s) | BBC Subtitle Guidelines | guía de referencia |
| Línea | máx. **37 caracteres**, máx. **2 líneas** | BBC Subtitle Guidelines | guía de referencia |
| Velocidad | 17 car/s adultos · 42 car/línea | Netflix Timed Text Style Guide | práctica de plataforma |
| Contraste del texto | **4,5:1**, o 3:1 si es texto grande | WCAG 2.2 · 1.4.3 | **norma** |

⚠️ **WCAG no tiene una regla especial para texto sobre vídeo en movimiento.**
Aplica el 1.4.3 de siempre, contra el «fondo efectivo». Eso significa que nuestro
velo tiene que garantizar 4,5:1 **contra el fotograma más claro que pueda pasar
por debajo**, no contra un gris de referencia. Lo medí, y **la mitad de esa zona no cumple**:

| Dónde, dentro del velo | Color resultante sobre blanco puro | Texto blanco encima |
|---|---|---|
| arriba del degradado (α 0,25) | `#C6C6C6` | **1,71:1 — no llega ni al 3** |
| a media altura (α 0,50) | `#8E8C8C` | 3,34:1 — sólo texto grande |
| abajo del todo (α 0,745) | `#565454` | **7,52:1 — cumple de sobra** |

O sea: el velo **sólo garantiza la lectura en su tercio inferior**. Si el
subtítulo se escribe arriba de esa caja y por debajo pasa un plano claro —una
pared blanca, un cielo—, no se lee y nadie se entera hasta verlo. Al construir
los subtítulos hay que **fijar la línea base dentro del tramo que cumple**, o
aplanar el degradado.

**Y esto justifica los subtítulos quemados**: el W3C recomienda subtítulos
cerrados por defecto, pero **abiertos —quemados— cuando el reproductor no da
control**, que es exactamente el caso de la reproducción automática y en silencio
de las redes sociales. No es una preferencia nuestra: es la guía de la fuente.

### Criterios de accesibilidad que aplican a nuestras piezas
| Criterio | Nivel | Cuándo |
|---|---|---|
| 1.2.1 Vídeo sin audio (grabado) | A | **nuestras piezas de hoy**, que van sin sonido |
| 1.2.2 Subtítulos (grabado) | A | en cuanto haya una voz |
| 1.2.3 y 1.2.5 Audiodescripción | A / AA | en cuanto haya una voz |
| 2.3.1 Tres destellos o menos | A | **cualquier pieza**: nos afecta directamente si el pulso llegara a parpadear |

El **2.3.1** lo medí y hoy estamos holgados: a 100 BPM el acento cae **1,667
veces por segundo** contra un umbral de 3, y el pulso ocupa entre el **3,66 % y
el 6,50 %** del lienzo. Deja de ser cierto en cuanto alguien pida el doble de
tempo (200 BPM = 3,33/s, **por encima del umbral**) o un modo estroboscópico.
**Propuesta: que el motor lo compruebe solo** y se niegue a pasar de ahí.

---

## 7 · Audio: por qué las piezas salen mudas, y qué cambiaría

Salen sin audio a propósito, y eso sigue siendo lo correcto: la música se pone
al montar. Pero si algún día se entrega con sonido, esto es lo que hay:

| Objetivo | Cifra | Quién | Tipo |
|---|---|---|---|
| Medición de sonoridad | LUFS/LKFS | ITU-R BS.1770-5 | **norma** (el algoritmo, sin objetivo) |
| Spots y promos cortos | **−23 LUFS ±0,2** · máx. corto plazo −18 · pico real **−1 dBTP** | EBU R128 s1 | **norma técnica**, y es la que aplica a una pieza de campaña |
| Emisión general | −23 LUFS ±0,5 | EBU R128 | norma de industria |
| Streaming musical | −14 LUFS, máster ≤ −1 dBTP | Spotify, en su soporte oficial | **publicado por la plataforma** |
| YouTube | −14 LUFS / −1 dBTP | **sólo terceros** | ⚠️ no hay página oficial de Google que lo diga |

Esto **confirma lo que el motor ya declara**: el −14 de YouTube no tiene fuente
oficial y por eso no está fijado en el código. La norma que sí aplicaría a una
pieza corta de campaña es **EBU R128 s1**.

⚠️ Y sigue en pie la trampa ya medida en nuestro flujo: **R128 suma canales**.
Medir en estéreo y entregar en mono deja la ganancia corta.

---

## 8 · Lo que cuesta

Medido en esta máquina, para dimensionar los lotes:

| Trabajo | Tiempo |
|---|---|
| 1 pieza MP4 de 5,0 s en 1080×1920 | **3,4 s** |
| 1 bucle de banda 1920×270 de 4,8 s | **0,3 s** |
| Lote de 48 invitaciones de 5 s | ~4–7 min *(extrapolado, no medido con 48 de verdad)* |

Es decir: **el coste de producir no es el problema**. El coste está en construir
cada motor una vez, y en el peso de lo que sale — el kit del pulso ya ocupa
115 MB y los overlays en ProRes, 66 MB.

---

## 9 · Lo que publican las plataformas — y lo que NO

Consultado el 6-sep-2026 sobre las páginas oficiales, no sobre resúmenes.

### ⚠️ El hallazgo que más cambia las cosas: **para contenido orgánico, nadie publica su zona segura**

Ni YouTube, ni LinkedIn, ni Meta, ni TikTok publican cifras de zona segura para
contenido **orgánico**. Todo lo que circula —«el centro 1080×1080», «10 % de
margen», «150 px arriba y 250 abajo»— es de terceros: herramientas, agencias y
plantillas, no la plataforma. La única excepción es **Meta para creatividad de
anuncios**, y va más abajo porque cambia las cosas.

Eso **confirma que hicimos lo correcto** al declarar nuestra zona segura de
Stories (269 arriba, 1670 abajo) como *criterio nuestro* y no como cifra
oficial. No se va a poder «verificar» nunca contra una fuente: lo honesto es
seguir marcándola como decisión propia y medirla contra capturas reales.

### YouTube
| | Vídeo normal | Shorts |
|---|---|---|
| Códec | **MP4 · H.264 High profile · 4:2:0** | igual |
| Bitrate 1080p SDR | **8 Mbps** | no publicado aparte |
| Duración | máx. 12 h / 256 GB | **máx. 3 min** |
| Aspecto | 16:9 | dicen «cuadrado o vertical», **no dicen 9:16** |
| Subtítulos | SRT, WebVTT, TTML, SCC y más | sin página aparte |
| Miniatura | 1280×720 | **2160×3840** recomendada |

✅ **Lo que ya hacemos cuadra**: nuestras piezas salen en H.264 High + yuv420p
—exactamente lo que YouTube documenta— y a 5 881 kbps, muy cerca de los 8 Mbps
que recomienda para 1080p.

⚠️ La miniatura de Shorts que YouTube recomienda es **2160×3840** y el sistema
sólo tiene `yt-miniatura` en 1280×720 (16:9). Falta la vertical.

### LinkedIn
| | Feed de página | Anuncio |
|---|---|---|
| Aspecto | ratio de **1:2,4 a 2,4:1** | 16:9 · 1:1 · **4:5 (1080×1350)** · 9:16 |
| Duración | **3 s – 10 min** | 3 s – 30 min |
| Tamaño | 75 KB – 5 GB | 75 KB – 500 MB |
| Subtítulos | **SRT obligatorio** para publicar con subtítulos; VTT no publicado | SRT opcional |

⚠️⚠️ **Nuestra banda de 1920×270 no se puede subir a LinkedIn**: su ratio es
7,11:1 y el máximo que admite el feed es 2,4:1. La banda sirve como overlay y
como elemento de web, **no como pieza publicable ahí**. Conviene que el motor lo
diga en vez de dejar que se descubra al subirla.

⚠️ **La duración mínima de LinkedIn son 3 s.** El sting de 1,2 s que propongo en
el punto 1 **no se puede publicar solo** en LinkedIn: es pegamento de montaje,
no pieza suelta. Hay que decirlo en el propio kit.

✅ **LinkedIn publica 4:5 (1080×1350) para anuncios**, que es justo el lienzo que
falta en vídeo y que ya existe en imagen. Es la dimensión número uno a añadir.

⚠️ Y una de formato: la norma de subtítulos es **WebVTT (W3C)**, pero **LinkedIn
sólo documenta SRT** —que no tiene norma formal, nadie lo regula—. Si se hacen
subtítulos, hay que emitir **los dos**.

### ⚠️⚠️ Meta sí publica una zona segura — pero sólo para ANUNCIOS

**14 % arriba · 35 % abajo · 6 % a los lados.** Para contenido **orgánico** no
publica ninguna cifra: lo que circula («150–200 px arriba, 250–300 abajo») es de
agencias y plantillas, no de Meta. TikTok no publica cifras en texto ni para
orgánico ni para anuncios: su documentación remite a una plantilla descargable.

Comparado con la nuestra, en 1080×1920:

| | Nuestra (criterio propio) | Meta, para anuncios |
|---|---|---|
| Arriba | 269 px = **14,01 %** | 14 % = 269 px → **coincide clavado** |
| Abajo | 250 px = **13,02 %** | 35 % = 672 px → **nos faltan 422 px** |
| Lados | 250 px = 23,1 % *(en el marco de vídeo)* | 6 % = 65 px → vamos más holgados |

**El margen superior coincide exactamente.** El inferior es **menos de la mitad**
del que Meta reserva en anuncios. Para lo orgánico no es un error —no hay cifra
oficial que incumplir— pero medí qué pasaría si una pieza se promociona:

| Pieza vertical | Bloques que caen dentro del 35 % inferior de Meta |
|---|---|
| **endcard** | **5**: fechas, sitio, partners, cobertura y el pulso |
| cuenta | 2: el pie («días») y el tema |
| apertura | **0** |

Es decir: **si el endcard vertical se promociona como anuncio, la interfaz se
come el bloque de marcas entero** — los dos Partners y IA Media. La apertura
aguanta sin tocarla.

**Propuesta**: una zona segura de dos niveles —`organico` (la de hoy) y
`anuncio` (14/35/6)— y que el motor avise cuando una pieza pensada para
promocionarse tenga contenido en la franja de anuncios. No cambiar la de hoy:
la cifra de Meta es para anuncios y aplicarla a todo desperdiciaría un tercio
de la pantalla.

### Lo demás de Meta y TikTok

| | Dato | Cómo estamos |
|---|---|---|
| IG Reels orgánico | **perfil alto · GOP cerrado · croma 4:2:0 · AAC ≥128 kbps** | ✅ perfil High y 4:2:0. ⚠️ **el GOP cerrado no lo forzamos** |
| TikTok In-Feed | bitrate **≥516 kbps** | ✅ vamos a 5 881 |
| TikTok TopView | bitrate **≥2 500 kbps** · duración **5–60 s**, recomendado 9–15 | ✅ el bitrate. ⚠️ **nuestras piezas de 3–5 s no llegan al mínimo de 5 s** |
| FB Feed | ancho **≤1280 px y divisible entre 16**, ≤30 fps | ⚠️ 1080 **no es divisible entre 16** (67,5) y 1920 pasa de 1280 |
| Canal alfa | **ningún documento oficial de Meta ni TikTok lo menciona** | el ProRes con alfa es para montar, no para subir. Está bien así |
| Subtítulos | Meta y TikTok generan automáticos; **subir .srt sólo por el gestor de anuncios** en Meta | si hacemos subtítulos, quemados es la vía real |

---

## 10 · Qué haría primero

Ordenado por lo que más cambia el resultado dividido por lo que cuesta. **Nada
de esto está decidido: es la lista de la que eliges.**

| # | Qué | Por qué está aquí |
|---|---|---|
| ~~**1**~~ | ~~Salidas~~ | ✅ **HECHO**: `animacion.py`, 5 curvas · 6 entradas · 5 salidas. Apertura y cuenta acaban al 0,0 % |
| ~~**2**~~ | ~~1080×1350 (4:5)~~ | ✅ **HECHO**: en los tres motores, 0 solapes |
| ~~**3**~~ | ~~Duraciones en tiempos, no en segundos~~ | ✅ **HECHO el 6-sep-2026**: cuenta 4,2 s y endcard 4,8 s |
| **4** | **Subtítulos quemados**, con la línea base dentro del tramo del velo que sí cumple 4,5:1 | el W3C recomienda quemados justo para autoplay en silencio, y la zona ya está reservada |
| **5** | **Sting de 1,2 s + bumper de 6 s** | el kit no tiene nada por debajo de 3 s ni una pieza cerrada de 6 |
| **6** | **Transiciones con nombre** (`corte-al-tiempo`, `pulso-cortina`, `carbon-6`, `pulso-hilo`) | hoy cada paso entre piezas lo resuelve el montador a mano |
| **7** | **Lower third que entra y sale** | existe como PNG; animado es media hora de trabajo |
| **8** | **Anuncio de actividad en vídeo** | el formato con más demanda de la semana, y no existe |
| **9** | **Bucle de espera y cuenta regresiva de sala** | no hay nada para la pantalla del evento |
| **10** | **Pista de clic a 100 BPM** junto al kit | resuelve la desincronía de raíz y cuesta casi nada |
| **11** | **Invitación por aliado en lote** (48) | ~4–7 min de máquina; hoy sería a mano 48 veces |
| **12** | **Plantilla de recap y tarjeta de cifra** | existen impresas, no en vídeo |
| **13** | **Muro de aliados y placa de patrocinadores animados** | el hueco ya está reservado en todas las piezas |
| **14** | **Salida en H.264 perfil Main** para WhatsApp | es lo único que Meta documenta oficialmente; hoy salimos en High |
| **15** | **Miniatura vertical 2160×3840** para Shorts | YouTube la recomienda y el sistema sólo tiene la de 16:9 |
| ~~**16**~~ | ~~Zona segura de dos niveles~~ | ✅ **HECHO**: `zonas.py`, y son **cuatro** niveles — Meta publica tres cifras distintas |
| **17** | **Forzar GOP cerrado** en la salida | Instagram lo pide por escrito para Reels orgánico y hoy no lo forzamos |

### Y seis cosas que no son piezas, sino deudas que encontré midiendo

| | Qué | Estado |
|---|---|---|
| A | **El velo de subtítulos sólo cumple en su tercio inferior** (1,71:1 arriba, 7,52:1 abajo) | defecto medido, sin arreglar |
| B | **La regla de distancia de lectura de `senal.py`** («2,54 cm por cada 3,05 m») no es la norma del sector: ANSI/AVIXA V202.01 (DISCAS) trabaja con ángulo de visión | hay que comprobar de dónde salió la nuestra antes de imprimir más |
| C | **La banda de 1920×270 no es publicable en LinkedIn** (7,11:1 contra un máximo de 2,4:1) | el motor debería decirlo |
| D | **Nuestro margen inferior es el 13,02 % y Meta reserva el 35 % en anuncios** — el superior, en cambio, coincide clavado en 14,01 % | decisión: dos niveles de zona segura, no cambiar la de hoy |
| E | **1080 px de ancho no es divisible entre 16** (67,5) y Facebook lo pide así para el feed | aviso, no urgencia |
| F | **Las piezas de 3–5 s no llegan al mínimo de 5 s de TikTok TopView** ni a los 9–15 s que recomienda | afecta sólo si se compra ese formato |

### Lo que NO propongo hacer
- **Fijar un lienzo de pantalla de evento.** No existe resolución estándar: cada
  LED tiene la suya según su pixel pitch y la da el proveedor de AV.
- **Generar QR.** Ya lo decidiste: no los hace el sistema.
- **Entregar con audio.** Sale mudo a propósito y así está bien; lo que falta es
  la pista de clic, no la música.
- **Nada que gire, recorte o despliegue el anillo.** Sería el logo troceado.
