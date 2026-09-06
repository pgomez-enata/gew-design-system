# Sistema de diseño · Semana Global de Emprendimiento · República Dominicana

Fundación Enlata e IAvanza son los dos **Partners** de GEW en República
Dominicana, e **IA Media** firma la cobertura. Este
sistema produce todas las piezas de la campaña, las mide y las firma.

Fuente de verdad: **`tokens/tokens.json`**. Cada valor trae de dónde salió y lo
no medido está marcado. Ningún motor inventa un color, una medida ni un texto
de marca: todo sale de ahí.

---

**Repo público**: <https://github.com/pgomez-enata/gew-design-system>
**El sistema, en pantalla**: <https://pgomez-enata.github.io/gew-design-system/> — código
MIT; la marca, la tipografía y las piezas producidas no viajan (ver
`ACTIVOS.md`). Se rearma con `python3 empaquetar.py`, que **no publica**.

## El orden de los comandos

Los cuatro pasos van en este orden. Saltarse el 2 deja piezas sin procedencia
y la auditoría lo marca en rojo.

```bash
python3 entorno.py          # 0 · ¿tiene la máquina lo que hace falta?
python3 campana.py --todas  # 1 · construir (el motor que toque)
python3 metadatos.py        # 2 · sellar la procedencia dentro de cada fichero
python3 manifiesto.py       # 3 · anotar qué se produjo y con qué hash
python3 auditoria.py        # 4 · el guardián: 0 = se puede entregar
```

`auditoria.py` sale con código 1 si algo falla. **Una pieza no está terminada
hasta que la auditoría pasa** — no vale el informe del motor que la hizo: eso
ya nos costó una revista entera que se creía en verde mientras el guardián no
la estaba mirando.

---

## Los motores

| Motor | Qué saca |
|---|---|
| `campana.py` | Las piezas sociales de campaña. Es además la biblioteca que usan los demás: retícula, tipografía, logos, sello. |
| `actividad.py` | Flyer de actividad, 3 variantes × 3 formatos. |
| `cita.py` | Plantilla de cita con retrato. |
| `video.py` | Frame, guías de zona de interfaz, rótulo y endcard. |
| `serie.py` | Carrusel, cuenta atrás, agenda de día y de semana. |
| `aliado.py` | Kit por aliado: pieza «Somos aliados», sello y LEEME. 48 kits. |
| `impreso.py` | Credencial, certificado, roll-up y backdrop, en cm + dpi + sangrado. |
| `perfil.py` | Portada de canal de YouTube, portada y logo de página de LinkedIn. |
| `revista.py` · `revista_reporte.py` | La revista de recap: 32 páginas, 23 tipos. |
| `prensa.py` | Nota de prensa, boilerplate y ángulos, según la plantilla de GEN. |
| `senal.py` | Señalética de sede. **Declara a qué distancia se lee cada pieza.** |
| `deck.py` | Deck para las charlas: 7 tipos de lámina, PNG y PDF. |
| `correo.py` | Cuatro correos en HTML y texto plano, medidos contra el tope de Gmail. |
| `movimiento_video.py` | Apertura, cuenta atrás y endcard **en movimiento**, con ffmpeg. |
| `patrocinio.py` | Anuncio y placa por nivel. ⛔ Sin acuerdo firmado, `{{PENDIENTE}}`. |
| `postevento.py` | Gracias y los números, por actividad y del total. |
| `calendario.py` | El `.ics` de la semana y de cada actividad. |
| `movimiento.py` | La lámina que compara los tres elementos y las piezas de ejemplo del pulso. |

## Las herramientas

| Herramienta | Qué hace |
|---|---|
| `entorno.py` | Comprueba la máquina **antes** de empezar y dice qué se pierde por cada cosa que falte. |
| `metadatos.py` | Mete la procedencia dentro del PNG: XMP con campos IPTC 2025.1 + chunks legibles. `--verificar` dice cuántas están sin sellar. |
| `manifiesto.py` | Escribe `_salida/manifiesto.json` con el hash de cada fichero. `--verificar` distingue CAMBIADO, FALTA y SOBRA. |
| `auditoria.py` | Las reglas. Cada una devuelve un número y lo compara con su umbral; no opina. |
| `encuadre.py` | Coloca el retrato con el mismo criterio en todos los formatos: cabeza entre 1/3,5 y 1/3 del alto, ojos a 0,38. |

---

## Los formatos

Siete de campaña y tres de perfil. **Sólo los tres de perfil tienen ficha
oficial publicada por la plataforma**: Meta no publica especificaciones para
las publicaciones orgánicas de Instagram, así que el 1080×1350 que usa todo el
mundo es consenso de terceros. Funciona, pero no se cita como norma.

| Formato | px | Ficha oficial |
|---|---|---|
| `retrato` | 1080×1350 | no · Meta sólo publica la de anuncios (1440×1800 en 4:5) |
| `historia` · `-abierta` · `-ads` | 1080×1920 | no |
| `cuadrado` | 1080×1080 | no |
| `yt-miniatura` | 1280×720 | **sí** · vigente |
| `enlace` | 1200×627 | **sí** · coincide exacto con LinkedIn |
| `yt-portada` | 2560×1440 | **sí** · sólo 1546×423 se ve en todos los dispositivos |
| `li-portada` | 1512×256 | **sí** · tope 3 MB |
| `li-logo` | 400×400 | **sí** · mínimo 268×268 |

---

## El movimiento: el pulso y los tres bloques

Desde el 5-sep-2026 toda pieza lleva **el pulso** —39 barras cuya altura es el
ancho angular real de cada segmento del anillo GEW·RD— y **los tres bloques de
marca**. Los dos viven en `campana.py` y los usan los diecinueve motores: una función
en dos ficheros se separa sola.

```
PARTNERS                       PATROCINADORES · SPONSORS
[Fundación Enlata] [IAvanza]   [espacio reservado]

COBERTURA · COVERAGE  [iA MEDIA]      ← sólo en piezas de cobertura
```

- **Enlata e IAvanza son los DOS Partners** — cerrado por Piero el 5-sep-2026.
  El papel de «National Host» queda retirado del sistema y `auditar_index.py`
  falla si reaparece atribuido a Enlata.
- **El hueco de patrocinadores se dibuja aunque esté vacío.** Si no se reserva,
  al llegar el primero hay que recomponer la pieza. ⛔ Ninguna marca se imprime
  antes de que el acuerdo esté firmado.
- **La cobertura sólo en piezas de cobertura**: endcard de video, recap,
  galería y revista.
- **`actividad` variantes B y C y `cita` mantienen su pie propio** —badge del
  organizador de la actividad—, que es lo correcto: son piezas de una actividad
  concreta, no del movimiento. Sí llevan el pulso.
- El logo de IA Media lo genera `logo_ia_media.py` con las proporciones medidas
  de IAvanza. Color **`#8475FF`**, cerrado el 5-sep-2026 con ΔE 15,2 y a
  sabiendas: ver `MOVIMIENTO.md`. Sobre carbón manda la variante `#9487FF`.

## Reglas duras

- **El logo que manda es el dominicano**, el que dice «República Dominicana».
  El badge global en inglés está archivado. Decisión de Piero, 5-sep-2026.
- **Ninguna cifra sin fuente.** Las cifras globales de GEW van como
  `{{CIFRA_...}}` porque las cuatro fuentes oficiales de GEN se contradicen.
  Sólo coinciden en 200 países y 10 millones de personas.
- **Lo ya publicado no se retoca.** Lo nuevo sale del sistema.
- **Los activos de terceros no entran en git.** Ver `ACTIVOS.md`.

## Qué sigue abierto

Está en `tokens.json → meta.decisiones_pendientes` y en
`ESTANDARIZAR-salidas.md → Parte 5`. Lo que bloquea trabajo hoy:

1. **El perfil ICC de la imprenta.** Sin él, la revista no se puede preparar
   de verdad para imprimir.
2. **Cuál de las cuatro fuentes de cifras de GEN se cita.**
3. **El texto de créditos** que se incrusta en cada fichero
   (`tokens.json → procedencia`) es redacción de trabajo, sin aprobar.
4. **Mover el logo de IA Media** a `iavanza_design_system`, que es su casa.
