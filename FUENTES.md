# Tipografía del sistema GEW — Fase 0 cerrada

**Cerrado el 5-sep-2026.** Nada de aquí es opinión: cada valor trae el comando que lo produjo.

## La familia

**VAG Rounded Std**, cuatro pesos, en `fuentes/`:

| Fichero | bytes | family (name id 1) | full (id 4) | versión |
|---|---|---|---|---|
| `VAGRoundedStdThin.ttf` | 32 824 | VAGRoundedStdThin | VAGRoundedStd-Thin | OTF 1.022 · makeotf.lib1.4.1585 |
| `VAGRoundedStdLight.ttf` | 32 448 | VAGRoundedStdLight | VAGRoundedStd-Light | idem |
| `VAGRoundedStdBold.ttf` | 34 596 | VAGRoundedStdBold | VAGRoundedStd-Bold | idem |
| `VAGRoundedStdBlack.ttf` | 33 972 | VAGRoundedStdBlack | VAGRoundedStd-Black | idem |

Métricas idénticas en los cuatro: `unitsPerEm 1000` · `capHeight 712` · `xHeight 532` · 16 tablas.

## Procedencia y licencia

Los cuatro salieron de **`https://www.genglobal.org/themes/custom/gen/fonts/`**, que es el servidor con el que GEN compone su propia marca. Piero confirmó el 5-sep-2026 que hay derecho de uso.

⚠️ **Pendiente de aclarar**: tener licencia de VAG Rounded y tomar los ficheros del servidor de GEN son cosas distintas. Si la licencia es propia (Monotype/Adobe), hay que sustituir estos cuatro por los ficheros licenciados. Si el derecho viene de ser anfitrión nacional, estos son los correctos y no hay nada que hacer.

⛔ Estos `.ttf` **no salen del taller**: si el sistema se empaqueta o se publica, la carpeta `fuentes/` se queda fuera.

## Qué peso usa el logo — medido, no supuesto

Se rasterizó el wordmark del `logo-gew.svg` oficial a 4× (2944 px), se separó de la rueda por el hueco de 64 px que hay entre ambos (x 1134-1198), se partió en sus 26 glifos por columnas vacías, y se comparó cada glifo contra el mismo carácter en cada peso, escalado al mismo alto y con alineación fina de ±10 px.

| Peso | IoU medio sobre 26 glifos |
|---|---|
| **Thin** | **0,9547** |
| Light | 0,8467 |
| Bold | 0,5225 |
| Black | 0,4832 |

**El wordmark de GEW está compuesto en VAG Rounded Std Thin.** El segundo candidato queda 11 puntos por debajo; no hay ambigüedad.

Por línea: GLOBAL 0,9377 · ENTREPRENEURSHIP 0,9542 · WEEK 0,9817.

## Geometría del wordmark

| Qué | Valor |
|---|---|
| cap-height de **render real** | **0,725 del cuerpo** |
| cap-height declarado en la tabla OS/2 | 0,712 |
| cap de GLOBAL / ENTREPRENEURSHIP | 152 / 151 px al 4× |
| cap de WEEK | 296 px = **1,947 ×** el de las otras dos |
| interlineado entre líneas | **1,21 caps** (185 y 184 px al 4×) |
| tracking, milésimas de eme | GLOBAL −6,2 · ENTREPRENEURSHIP +16,8 · WEEK +0,4 |

⚠️ **La trampa del cap-height.** La tabla dice 0,712 pero el render real da 0,725: es el overshoot de las curvas redondeadas, que en esta familia es grande justamente porque todos los terminales son redondos. Un motor que dimensione con 0,712 saca las piezas **1,8 % grandes**. El sistema usa 0,725.

⚠️ **El tracking está medido sin kerning** (PIL coloca carácter a carácter). Los tres valores caen en ±17 milésimas, que es ruido de kerning más que una decisión de diseño: para componer texto nuevo, tracking 0 con kerning activo y se comprueba contra el original.

## Reglas de uso que pone GEN

De `genglobal.org/gew/brand-and-promo-resources`, literal:

- La tipografía del logo GEN es VAG Rounded Thin y se usa en todos los activos de marca.
- Se puede usar Light y/o Thin **en mayúsculas** para énfasis o titulares.
- **No usar Bold ni Black** salvo que sea imprescindible, y con moderación.
- El sitio sirve además **Noto Sans** para cuerpo de texto.

Traducido al sistema: **Thin y Light para todo lo que sea marca y titular. Bold y Black existen en la carpeta pero su uso pide justificación. Noto Sans para cuerpo.**

## Prueba visual

`_pruebas/fase0-tipografia.png` — 2200 × 1760 px. Superposición glifo a glifo, la tabla de IoU, la geometría y las cuatro muestras.
