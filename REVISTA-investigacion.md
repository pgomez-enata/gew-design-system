# Revista GEW · RD — lo que hace falta saber antes de construirla

Levantado el 5-sep-2026. Cada dato trae su fuente; lo que no se encontró va
marcado, no rellenado.

---

## 0 · Ya existe un motor de revista y conviene mirarlo

`04 Marca/p4f_design_system/revista.py` — 476 líneas, hecho para Competencia Demo.
Hay dos PDF producidos con él en `Organizado/02 Pitch4Fun/`.

Ya resuelve: hoja **8.5 × 11 a 150 dpi**, retícula de **6 columnas**, línea base
de **14 pt**, y cinco tipos de página —`portada`, `apertura`, `lectura`, `datos`,
`tarjetas`—. Mide la tinta real con `textbbox`, no la caja de fuente, y marca en
un informe la hoja que se desborda en vez de entregarla en silencio. También
detecta **glifos faltantes**, que es exactamente el fallo que tuvimos con la
flecha «→» del carrusel.

**No se copia** —los sistemas están separados por decisión tuya— pero la
arquitectura y el informe se adoptan tal cual. Lo que le falta para GEW:
contraportada y las dos retiraciones.

---

## 1 · Formato de página

| Formato | mm | pulgadas | Dónde manda |
|---|---|---|---|
| **US Letter** «magazine 8.5 × 11» | 216 × 279 | 8,5 × 11 | EE. UU.: entre el 60 y el 70 % de las revistas de consumo |
| A4 | 210 × 297 | 8,27 × 11,69 | Europa y la mayoría de editoriales internacionales |
| 210 × 280 mm | 210 × 280 | 8,27 × 11,02 | Semanarios europeos |

⚠️ **Para República Dominicana no hay dato.** Ninguna fuente da el porcentaje por
país. Lo que sí está documentado: México y buena parte de Latinoamérica adoptaron
US Letter por influencia estadounidense, mientras el resto del mundo usa ISO 216.
RD no aparece nombrada. Como Competencia Demo ya va en 8.5 × 11 y el papel carta es el
que se consigue aquí, **es la apuesta razonable** — pero es una apuesta, no un
dato.

## 2 · Lo que pide la imprenta

| Qué | Valor | Fuente |
|---|---|---|
| Sangrado | **3 mm** por lado; 5 mm si la revista es gruesa | printsimple.eu, mainlandprinting.com |
| Margen de seguridad | **6 mm** mínimo desde el corte, para revista | discmakers.com, ballantine.com |
| Resolución | **300 dpi** para offset y para digital de calidad | palgraphic.com, lhgraficos.com |
| Color | **CMYK**, nunca RGB | naturprint.com |
| Medianil, lomo cuadrado | 20–30 mm, más 3–6 mm extra si pasa de 200 pp. | printster.in, printivity.com |
| Medianil, grapa | **no hay regla dura publicada** más allá del margen de seguridad | — |

⚠️ **El perfil ICC concreto de las imprentas latinoamericanas no está
documentado.** GRACoL y SWOP mandan en Norteamérica, FOGRA en Europa; ninguna
fuente dice cuál calibra LatAm. La recomendación de las propias fuentes es
preguntárselo a la imprenta.

## 3 · Número de páginas

Una revista se imprime en **pliegos**: un doblez son 4 páginas, dos son 8, tres
16, cuatro 32. Por eso el total tiene que ser **múltiplo de 4**; si no, el último
pliego queda incompleto y se paga igual.

| Encuadernación | Cuándo |
|---|---|
| **Grapa** (saddle stitch) | hasta 48–64 páginas |
| Zona gris | 48–116 páginas: cualquiera de las dos |
| **Lomo cuadrado** (perfect binding) | por encima de 68, obligatorio pasadas 96–116 |

⚠️ **El «creep» de la grapa.** En una revista grapada, las hojas interiores del
cuadernillo sobresalen porque el doblez acumula grosor; al recortar a filo, la
hoja de más adentro queda más angosta. Se compensa con *shingling*: aumentar el
medianil progresivamente hacia el centro. **Si no se compensa, el contenido de
las páginas centrales se corta.** Es el equivalente impreso del texto que se sale
del lienzo, y no avisa.

En lomo cuadrado el pegado «traga» contenido junto al doblez, así que hay que
dar más margen y evitar imágenes que crucen el lomo.

## 4 · Qué páginas lleva una revista, y en qué orden

```
1   Portada
2   Retiración de portada        ← el reverso de la portada
3   Créditos / masthead
4   Editorial
5   Índice
6…  Secciones y artículos
n-1 Retiración de contraportada  ← el reverso de la contraportada
n   Contraportada
```

**Retiración** es la cara interna de una cubierta. No es una página añadida: es
el otro lado de la misma hoja. Por eso las cubiertas aportan siempre 4 páginas al
total.

**Numeración**: portada y contraportada y sus retiraciones no llevan folio
visible, pero sí cuentan. La portada es la página 1 aunque no lo diga.

## 5 · Imprentas en Santo Domingo

| Imprenta | Web | ¿Revistas? | ¿Specs públicas? |
|---|---|---|---|
| Amigo del Hogar | imprentaamigodelhogar.com | **Sí** — tiene línea editorial; imprime la revista *Amigo del Hogar* y los informes del Banco Popular | No |
| Editora Corripio | editoracorripio.com.do | **Sí** — revistas, libros, afiches | No |
| Print Studio | printstudio.com.do | No las menciona | No |
| Serigraf · Indar Graf | serigraf.com.do · indargraf.net | Se anuncian como editoras de revistas | No se pudo verificar: los dominios no respondieron |

⚠️ **Ninguna imprenta dominicana publica sus especificaciones de entrega.** Las
tres que sí cargan remiten a contacto directo. Eso significa que **el sangrado,
el perfil de color y el medianil hay que confirmarlos con la imprenta elegida
antes de maquetar**, no después.

---

## 6 · Los elementos que propongo montar

Trece tipos de página. Los cinco primeros ya existen resueltos en el motor de
Competencia Demo; los ocho restantes son nuevos.

### Cubiertas (4 páginas, siempre)

| # | Página | Qué lleva |
|---|---|---|
| 1 | **Portada** | Lockup, el año, un titular y la foto o el collage |
| 2 | **Retiración de portada** | Editorial breve o una cifra grande a toda página |
| n-1 | **Retiración de contraportada** | El muro de los 48 aliados |
| n | **Contraportada** | Lockup, lema, gew.co, banda de Partners, y los créditos que GEN obliga |

### Preliminares

| # | Página | Qué lleva |
|---|---|---|
| 5 | **Créditos / masthead** | Quién hace la revista, contacto, y el bloque de Kauffman y patrocinadores globales |
| 6 | **Editorial** | La carta, con firma |
| 7 | **Índice** | Secciones con su folio, y una foto de ancla |

### Interiores

| # | Página | Qué lleva |
|---|---|---|
| 8 | **Apertura de sección** | Titular a toda página con foto a sangre |
| 9 | **Lectura** | Texto corrido a dos o tres columnas, con entradilla y destacado |
| 10 | **Datos** | Las cifras de la semana, en rejilla |
| 11 | **Tarjetas** | Una ficha por actividad, por aliado o por proyecto |
| 12 | **Galería** | Cuadrícula de fotos con pie |
| 13 | **Muro de aliados** | Los 48 logos, que ya salen del padrón del `gew.html` |

**Obligación de GEN que aplica de lleno aquí**: toda pieza de más de una hoja
carta debe reconocer a la Kauffman Foundation y a los patrocinadores globales.
Va en el masthead y se repite en la contraportada. El bloque ya está escrito en
`prensa.py`.

---

## 7 · Lo que hace falta decidir antes de maquetar

1. **¿Recap o programa?** Una revista de después del evento —fotos, cifras, lo
   que pasó— y una de antes —programa, cómo participar, quién es quién— no
   comparten ni estructura ni tono. Cambia todo.
2. **¿Cuántas páginas?** Determina la encuadernación, y la encuadernación
   determina el medianil. Con 32 o 48 va grapada; pasando de 68 hay que ir a lomo
   cuadrado.
3. **¿Se imprime o es sólo digital?** Si se imprime hay que fijar CMYK, sangrado
   y compensación de creep, y hay que preguntarle a la imprenta su perfil. Si es
   sólo digital, nada de eso aplica y se gana margen de maniobra.
4. **¿Qué imprenta?** De ella salen el sangrado real, el perfil ICC y el medianil.
