# El movimiento: elemento distintivo, marcas y IA Media

Decidido por Piero el 5-sep-2026. Lo que sigue está construido y medido.

---

## 1 · El elemento: **el pulso**

Sale del propio logo, medido: recorriendo el radio medio del anillo GEW·RD cada
0,05° salen **39 segmentos con 30 colores** y sus anchos angulares reales, de 1°
a 32,75°, con 7,7 % de aire. El pulso usa esos anchos como altura de barra: los
segmentos anchos del anillo dan las barras altas. El ritmo no es decorativo,
es la geometría del logo.

Está en `datos/anillo-segmentos.json`. La cinta y la estela se quedan en
`movimiento.py` como constancia de lo que se comparó, no como opciones vivas.

**⛔ Lo que sigue prohibido**: un arco de la rueda. Sería el logo recortado.

**⚠️ Los 30 colores del anillo dominicano no son los del SVG global.** 32 de los
39 segmentos están a más de 24 de distancia de `color.marca.rueda`. Para
cualquier pieza que ponga un color junto al anillo RD manda la lista medida.

---

## 2 · Dónde y cómo se nombran

Tres bloques, rótulos bilingües, en dos filas:

```
PARTNERS                       PATROCINADORES · SPONSORS
[Fundación Enlata] [IAvanza]   [espacio reservado]

COBERTURA · COVERAGE  [iA MEDIA]
```

| Bloque | Quién | Cuándo |
|---|---|---|
| **PARTNERS** | Fundación Enlata · IAvanza | siempre |
| **PATROCINADORES · SPONSORS** | — | cuando haya acuerdo firmado |
| **COBERTURA · COVERAGE** | IA Media | sólo cobertura: video, recap, galería, revista |

`PARTNERS` se escribe igual en los dos idiomas, así que sólo los otros dos
llevan las dos palabras.

**El hueco de patrocinadores se dibuja aunque esté vacío.** Si se deja sin
reservar, al llegar el primer patrocinador hay que recomponer la pieza entera.
Y sigue en pie la regla: **ninguna marca se imprime antes de que el acuerdo
esté firmado**, por avanzada que esté la conversación. Un acuerdo en
negociación no da derecho a aparecer en una pieza.

### Resuelto: los dos son Partners

Confirmado por Piero el 5-sep-2026. El papel de «National Host» queda retirado
de todo el sistema; `auditar_index.py` falla si reaparece atribuido a Enlata.
La «guía de National Hosts» sigue siendo el nombre del documento de GEN y se
cita como tal.

---

## 3 · El logo de IA Media

No lo inventé: IAvanza ya tiene un patrón de submarca —las 13 comunidades— y
está medido en su `tokens.json`. IA Media se construye igual:

| | |
|---|---|
| cuerpo del texto | 1,0759 × alto del isotipo |
| cap-height | 0,7393 × alto del isotipo |
| solape del texto | −0,024 × ancho del isotipo (anidado, no colisión) |
| alineación | línea base común, **no** centrado vertical |
| tipografía | Archivo SemiExpanded ExtraBold (OFL), convertida a trazo |
| clearspace mínimo | 1/3 del alto del isotipo |
| tamaño mínimo | 120 px de ancho; por debajo, sólo el isotipo |

Cinco variantes en `logo/socios/`: lockup a color, en blanco, para carbón,
isotipo y isotipo blanco. El SVG no depende de ninguna fuente instalada.

### El color: **#8475FF** — aprobado

Cerrado por Piero el 5-sep-2026. Salió del generador de IAvanza —el mismo que
se usó para IA Human e IA Teachers— con su método: ΔE2000 contra las 13
comunidades más el azul de marca y TESTERS, contraste ≥3:1 sobre blanco y
contra el ink, y croma dentro de la familia.

**Va con ΔE = 15,2 y el umbral de aquella vez fue 20. Se aprobó a sabiendas.**
Con croma de marca (C*≥78) no hay ningún hueco mejor: la rueda ya está llena
con 13 comunidades. Bajando el piso de croma sí aparece un ΔE de 24,7 — pero el
ganador es un caqui apagado, que es justo lo que el propio generador de IAvanza
avisa por escrito que hay que evitar. Croma de marca por delante de distancia
de catálogo.

**Por qué no el azul de marca**: `#0262E5` es **exactamente** el color de
encuentro semanal (ΔE 0) y su contraste contra el ink del nombre es 2,27:1, por debajo
del 3:1 que exige el propio sistema.

**Sobre el carbón de GEW hace falta la variante aclarada.** Ningún color puede
cumplir 3:1 sobre blanco y 3:1 sobre `#4A4A4A` a la vez: las dos bandas de
luminancia no se tocan (≤0,300 y ≥0,3054). Por eso existe
`ia-media-lockup-carbon.svg`, con el isotipo en `#9487FF` — 3,03:1 sobre el
carbón — y la palabra en blanco.

**Su casa definitiva no es este sistema.** El logo es de IAvanza. Vive aquí
para poder usarlo, pero su sitio es `iavanza_design_system/logo/`. Lo muevo
cuando lo apruebes.

---

## 4 · El pulso **sonando**: `pulso_musica.py`

El pulso ya estaba, quieto. Esto lo pone a moverse como se mueve la música.
La idea que sostiene el motor entero:

> **el PICO de cada barra es su altura del anillo, exacta.**

Cada barra se normaliza por su propio máximo dentro del bucle, así que en algún
fotograma toda barra alcanza —clavada, 0 px de diferencia— la altura que le da
el logo, y entre golpe y golpe cae al 34 % de ella. El pulso quieto no es un
estado distinto del pulso en movimiento: **es su fotograma de acento**. La
correlación entre el pico de cada barra y los grados de su segmento es
0,999986, y lo que falta es el redondeo a píxel entero.

### Los cuatro modos no son cuatro estilos, son cuatro papeles

| Modo | Qué hace | Cuándo | |
|---|---|---|---|
| **latido** | las 39 a la vez, sobre el tiempo | la pieza **lleva voz encima** | `--papel voz` |
| **espectro** | cada barra es una banda; graves lentos a la izquierda, agudos secos a la derecha | la pieza **va sola** | `--papel solo` |
| **ola** | una cresta recorre las barras, una vez por compás | transiciones y barridos | a mano |
| **chispa** | acentos en corcheas sobre grupos de barras | energía alta, cortes rápidos | a mano |

**Cerrado por Piero el 6-sep-2026**: `latido` en todo lo que lleve voz encima
—talking head, entrevista, testimonio—, porque ahí el pulso es fondo y no debe
robar atención; `espectro` en todo lo que vaya solo —apertura, endcard, bumper,
banda de web—, porque ahí el pulso es el contenido y tiene que sonar.

La regla **vive en el motor**, no sólo aquí: `PAPELES` en `pulso_musica.py`, y
`--papel voz|solo` elige el modo. Pedir un papel y un modo que se contradicen
es un **error**, no un aviso — una regla que hay que recordar es una regla que
se olvida. `ola` y `chispa` siguen vivos, pero no son el defecto de nada.

### La rejilla es musical, y por eso cierra

**100 BPM · 2 compases de 4 · 18 fotogramas por tiempo · 144 fotogramas ·
4,8 s a 30 fps.** A 30 fps sólo valen los BPM de la forma 1800/k; con
cualquier otro, el tiempo cae a medio fotograma y a los treinta segundos el
pulso va desincronizado de la música. Si se pide un BPM que no cierra, el
motor dice cuál es el válido más cercano en vez de tragárselo.

⚠️ **101 BPM —el ritmo medido del recap— no cierra a 30 fps**: haría falta un
bucle de 101 compases. Si alguna vez se monta contra esa pista, se cambia el
BPM del motor o se cambian los fps, pero no se deja a medias.

### Lo que se mide, y por qué esas medidas

- **Periodicidad exacta**: se calcula el fotograma que vendría *después* del
  último y se comprueba que es idéntico al primero. Desviación 0 en los cuatro.
  ⚠️ La primera versión de esta prueba comparaba el salto del cierre contra el
  salto máximo interno, y marcaba `espectro` y `chispa` sin motivo: un ataque
  de tiempo fuerte SÍ salta, y el compás 2 no tiene por qué sonar como el 1.
  La prueba buena es la periodicidad, y esa es exacta.
- **`chispa` no era periódico y la prueba lo cazó**: el grupo de barras
  encendidas ciclaba cada 3 corcheas y el bucle tiene 32. Con el módulo dentro
  de la fórmula, la desviación pasa de 0,92 a 0.
- **Los 30 colores del anillo intactos** en cada salida — 30/30 en el GIF y en
  el ProRes.
- **Cero solapes entre bloques**, medidos con las cajas de tinta reales. La
  primera composición repartía por proporciones y las fechas caían encima del
  bloque de marcas.

### Las salidas: 32 por corrida

| Salida | Formato | Para qué |
|---|---|---|
| **MP4** ×16 | banda 1920×270 · horizontal · vertical · cuadrado | H.264 High, yuv420p, CBR 6 000 kbps |
| **ProRes 4444** ×4 | banda, con alfa real | superponer sobre otro vídeo al montar |
| **GIF** ×4 | banda 960×135, 72 fotogramas | donde no entra vídeo |
| **SVG animado** ×4 | banda, ~77 KB | web y repo: pesa poco y escala |
| **Tira de contacto** ×4 | 1080×1118 | elegir modo sin abrir un vídeo |

⚠️⚠️ **El overlay NO es WebM/VP9, y conviene saber por qué.** Pidiéndole
`yuva420p`, este ffmpeg escribe `alpha_mode=1` en el contenedor —la etiqueta
que todo el mundo mira— y codifica el flujo en `yuv420p`: **el fichero dice
que lleva alfa y al abrirlo el fondo sale negro opaco**. Se vio decodificando
un fotograma y midiendo el canal, no leyendo la etiqueta. ProRes 4444 sí lo
lleva (fondo con alfa 0 medido), es lo que traga cualquier montador, y al ser
4:4:4 devuelve los 30 hex exactos en vez de corridos por el submuestreo.

⚠️ **El SVG lleva `y` y `height` estáticos además de las animaciones.** Sin
ellos, cualquier visor que no ejecute SMIL —`rsvg-convert`, más de una vista
previa, cualquier conversor a PDF— dibuja rectángulos de altura cero y el
fichero se ve vacío. Y el `<rect id="fondo">` se puede quitar o pintar por CSS:
el mismo fichero sirve sobre transparente.

El bucle del SVG se comprobó en Chrome, no de palabra: capturas a 133 ms y a
4 933 ms —un bucle exacto de distancia— salen con **0 px de diferencia**,
mientras que un solo fotograma de distancia cambia 5 278 px.

### La cabeza que flota

Sobre cada barra va su pico retenido, cayendo despacio, como la aguja de un
vúmetro. Se dibuja **siempre** y **del color de su barra**: cuando la barra
está en su pico queda pegada encima y no se distingue; cuando cae, se queda
arriba y baja sola. No se usa blanco en ningún sitio — los 30 colores del
anillo son la identidad y no se tocan.

---

## 5 · El pulso vivo **dentro de los motores de vídeo**

Los dos motores que hacen vídeo llevan ya el pulso sonando, cada uno con el
modo que le toca por su papel:

| Motor | Pieza | Papel | Modo | Sale como |
|---|---|---|---|---|
| `movimiento_video.py` | apertura · cuenta · endcard | va sola | `espectro` | MP4 H.264 |
| `video.py` | frame (marco con subtítulos) | encima de una voz | `latido` | **ProRes 4444 con alfa** |
| `video.py` | endcard | va solo | `espectro` | MP4 H.264 |

Los overlays animados duran el **bucle exacto: 4,8 s / 144 fotogramas**, así que
se repiten sin salto durante lo que dure el crudo. Los PNG fijos siguen
saliendo igual: las dos rutas comparten la misma composición, así que el
overlay animado y el fijo no se pueden separar.

**El barrido de entrada cambió.** Antes se dibujaba el pulso quieto recortado,
y al recortar se recalculaba el paso: las barras crecían a lo ancho y se leía
como un estiramiento. Ahora aparecen en su sitio definitivo y **ya se están
moviendo cuando entran**.

### ⚠️⚠️ Lo que destapó meterlo: tres composiciones repartidas a ojo

Las tres piezas de `movimiento_video.py` calculaban su reparto con fórmulas de
proporciones, no con la tinta real. En el endcard en horizontal la fórmula daba
**598 px de bloque para una zona de 546**, el `max(0, …)` del centrado colapsaba
y **«gew.co» caía encima de los logos de Enlata e IAvanza**. Estaba así antes de
tocar nada; se vio al mirar el fotograma.

Las tres se rehicieron con **cajas de tinta medidas**, apiladas de abajo arriba,
con un bucle que encoge hasta que cabe y una comprobación —`cajas_malas()`— que
**para el motor** si dos bloques se cruzan o si algo se sale de la zona segura.
Cero solapes en los tres tipos por los tres formatos.

### La rejilla contra la duración de cada pieza — **CERRADO el 6-sep-2026**

Piero decidió llevar `cuenta` a 4,2 s y `endcard` a 4,8 s. **Las tres duraciones
caen ahora en tiempo entero**:

| Pieza | Dura | Tiempos a 100 BPM | Fotogramas | |
|---|---|---|---|---|
| apertura | 3,0 s | **5,000** | 90 | |
| cuenta | **4,2 s** | **7,000** | 126 | antes 4,0 s = 6,667 |
| endcard | **4,8 s** | **8,000** | 144 | antes 5,0 s = 8,333 · **y es exactamente un bucle entero del pulso** |

Que el endcard mida justo un bucle no es casualidad buscada, pero conviene
saberlo: **contiene el ciclo completo del pulso sin repetirlo ni cortarlo a
medias**. Es la pieza que mejor aguanta ir en loop.

`--al-tiempo` sigue en el motor, pero ya no cambia nada: las tres duraciones por
defecto son las correctas.

### Un pulso quieto no lanza error

Por eso se mide sobre el fichero ENTREGADO: se extraen dos fotogramas del MP4 y
se cuentan los píxeles que cambian. Si el bucle se quedara clavado —un `%` mal
puesto, un `t` que no avanza— el vídeo saldría con el pulso congelado y todo lo
demás seguiría en verde. Probado en las dos direcciones: congelando el
fotograma, la medida cae a 0 px.

---

## 6 · Entradas, salidas y zona segura de dos niveles

Tres cosas cerradas el 6-sep-2026. Salieron del catálogo `VIDEO-que-falta.md`.

### `animacion.py` — el vocabulario de movimiento

Hasta hoy el sistema tenía **una** curva y **nueve** entradas escritas a mano
dentro de cada motor, y **cero salidas**. Medido: las siete piezas terminaban con
el **91,6–98,7 %** de la tinta en pantalla. Todas entraban bien y se cortaban en
seco.

Ahora hay cinco curvas —`frena` (la de siempre, misma fórmula), `arranca`,
`frena-y-arranca`, `golpe`, `escalon`—, seis entradas y **cinco salidas**. Y las
duraciones **se piden en tiempos musicales**: `1t`, `2c`, `1C`. Una entrada dura
una corchea, no «0,45 s», así que el movimiento y el pulso van juntos por
construcción y cambiar el BPM no descuadra nada.

Cada pieza declara su guion. `endcard` sale con **`mantiene`** —va al final del
todo y debe quedarse—, pero eso ahora **se pide**, no es lo único posible:

| Pieza | Entra | Sale | Al último fotograma queda |
|---|---|---|---|
| apertura | `sube` | `apaga` | **0,0 %** |
| cuenta | `crece` | `encoge` | **0,0 %** |
| endcard | `aparece` | `mantiene` | 98,3–98,7 % *(a propósito)* |

⚠️ **El último fotograma no cae en `dur`, cae en `dur − 1/fps`.** Calculando la
salida contra `dur`, en el último fotograma todavía valía 0,16 y la pieza acababa
con un 15 % de imagen encima: **medido, quedaba el 77 %** con la salida ya
puesta. Parecía que salía y no terminaba de salir.

⚠️ **`cierra` no vacía la pantalla: la LLENA.** Medirla con el umbral de `apaga`
la daba por rota haciendo exactamente lo suyo. Cada salida tiene su umbral, y el
de `cierra` no es la tinta que queda sino **el fondo que no queda**: una cortina
que cierra deja **0 % de fondo a la vista**. La primera versión llamaba a
`PM.dibuja`, que respeta el aire entre barras, y dejaba huecos por los que se
veía el contenido: 460 % de tinta y sin cerrar. Ahora las barras se ensanchan
hasta juntarse y suben al techo.

### 4:5 — el lienzo que faltaba

**1080×1350** en los tres motores. Existía en imagen (`retrato`) y no en vídeo, y
es el que más superficie ocupa en el feed de un móvil; LinkedIn lo publica para
anuncios. Entró **sin tocar ninguna composición**: los planos se calculan con
medidas, así que un lienzo nuevo se recalcula solo. **0 solapes** en las tres
piezas y en el pulso.

### `zonas.py` — zona segura en dos niveles

**Ninguna plataforma publica zona segura para contenido orgánico.** Ni YouTube,
ni LinkedIn, ni Meta, ni TikTok: lo que circula es de agencias y plantillas.
Consultado el 6-sep-2026 sobre sus páginas oficiales. Eso confirma que la nuestra
tiene que seguir declarada como criterio propio.

La excepción: **Meta publica 14 % arriba · 35 % abajo · 6 % lados, para
creatividad de ANUNCIOS.**

| | Nuestra | Meta, anuncios |
|---|---|---|
| Arriba | 269 px = **14,01 %** | 14 % → **coincide clavado** |
| Abajo | 250 px = **13,02 %** | 35 % → **faltan 422 px** |

⛔ **No se cambia la zona de hoy**: aplicar el 35 % a todo desperdiciaría un
tercio de la pantalla en piezas que nunca se van a promocionar. El motor **avisa**
y la decisión queda donde va. Hoy avisa de que el endcard vertical, si se
promociona, pierde sus cinco bloques inferiores —fechas, sitio, los dos Partners,
IA Media y el pulso—.

⚠️ La reserva de Stories **no se traslada** al 4:5 de feed ni al apaisado:
`CON_INTERFAZ` es sólo `vertical`.

⚠️⚠️ **Meta publica TRES cifras distintas y se confunden con facilidad.** Están
las tres como niveles separados, cada una con su fuente:

| Nivel | Abajo | Para qué |
|---|---|---|
| `anuncio` | 35 % | la creatividad del anuncio |
| `anuncio-disclaimer` | **40 %** | anuncios de Reels que lleven disclaimers legales |
| `sticker-stories` | 20 % | sólo dejar sitio al sticker de enlace de Stories |

Con el 40 %, **la apertura vertical deja de estar limpia**: sus fechas caen
dentro. Con el 35 % pasaba.

---

## 7 · Ritmo de texto y tarjeta de CTA

Puntos 4 y 5 de `VIDEO-tecnicas.md`, cerrados el 6-sep-2026.

### Dos reglas de texto, y no son la misma

| | Qué mide | Cifra | Fuente |
|---|---|---|---|
| **Cadencia** | a qué ritmo se PRESENTA un texto que entra palabra a palabra | **5–10 palabras/s** | TikTok, con su *Marketing Science* y **Lumen Research** |
| **Lectura** | cuánto tiene que estar en pantalla un texto que aparece y se queda | **15 caracteres/s** | **BBC Subtitle Guidelines** (la más conservadora; Netflix da 17) |

La rejilla ya cumplía la primera sin forzar nada: a 100 BPM una semicorchea son
0,15 s, así que **una palabra por semicorchea = 6,67 palabras/s**, justo en medio
del rango. Es la cadencia por defecto de la entrada `escribe`, y no es una
elección estética: es la que cae dentro.

⚠️ **La segunda regla destapó un defecto en la apertura.** Las fechas entraban a
1,35 s y quedaban **1,05 s legibles** antes de la salida, cuando 18 caracteres
necesitan **1,20 s**. Ahora entran en el **tiempo 2** (0,60 s) y quedan 1,50 s.
Los seis rótulos del kit pasan la comprobación, que corre en cada corrida.

### `cta.py` — la tarjeta de llamada a la acción

**2,4 s = 1 compás = 72 fotogramas**, en los cuatro formatos. Es de lo poco con
respaldo publicado: TikTok mide **+45 % de recall y +19 % de likeability** con
una CTA card en el cierre. Hasta ahora el sistema sólo ponía `gew.co` dentro del
endcard, y eso es un dato, no una llamada.

Tres cosas la separan del resto de las piezas:

1. **Se compone dentro de la franja de ANUNCIO** (14 % arriba / 35 % abajo /
   6 % lados), no de la orgánica. Un CTA es exactamente lo que se promociona, y
   un CTA por debajo de esa línea es un CTA que la interfaz tapa.
2. **El titular entra por palabras a 6,67 palabras/s.**
3. ⛔ **Rechaza el engagement bait.** Meta lo tiene prohibido y definido, y
   **reduce la distribución**. El motor no avisa: **se niega a generarlo**.

⚠️ El reparto de líneas es **equilibrado, no codicioso**: metiendo palabras hasta
que no quepan, «Súmate a la Semana Global de Emprendimiento» dejaba **«de» solo
en una línea entera**. Ahora se prueban todos los repartos y gana el que menos
hueco desperdicia.

**Los cuatro textos son una propuesta, no una decisión.** Sólo «Súmate a la
Semana Global de Emprendimiento» existía ya en el sistema (`correo.py`). El tono
lo decide Piero; `--accion` y `--destino` aceptan lo que sea.

---

## 8 · Estado

**Todo cerrado.** El elemento, los rótulos, los tres bloques, el papel de Enlata
y el color de IA Media están decididos, y el pulso y la banda ya viven en los
doce motores con sus reglas en la auditoría — no en `movimiento.py`, que se
queda sólo con la lámina comparativa como constancia de lo que se comparó.

Lo único que sigue fuera de nuestra mano:

1. **Mover el logo de IA Media a `iavanza_design_system`**, que es su casa. No
   lo hice solo porque ese sistema tiene su propia puerta, su `_sello.json` de
   hashes y su empaquetador: meterle un logo sin revisarlos puede romperlos.
2. El **perfil ICC de la imprenta** y el gramaje real del papel.
3. Cuál de las **cuatro fuentes de cifras de GEN** se cita.
