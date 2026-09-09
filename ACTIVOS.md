# Activos que el repo NO versiona

`fuentes/` y `logo/` están en `.gitignore`. No es descuido: son activos de
terceros —tipografía licenciada y marcas de GEN y de los socios— y un binario
que entra en el historial de git ya no se saca, aunque un commit posterior lo
borre. En los dos sistemas hermanos ya hubo fugas al empaquetar el repo público.

La excepción son los de **IA Media**, que no se reciben: se generan con
`logo_ia_media.py`. Ese generador SÍ está versionado, así que el logo es
reproducible con un comando aunque el SVG no viaje.

Este fichero deja constancia de qué tiene que haber ahí, para que un clon sepa
exactamente qué le falta. `python3 entorno.py` comprueba que están **y que son
los mismos**: los hashes de abajo se verifican, no son decoración. Se regraba
con `python3 sellar_activos.py`, y sólo cuando el cambio fue a propósito.

Medido el 2026-09-06 · sistema v1.2.0

## Los 7 que hay que conseguir

De todo lo que hay abajo, **estos siete son los que un clon no puede sacar de
ninguna parte**. Los demás o están archivados y no se usan, o se generan con un
comando, o salen del repo hermano de IAvanza. Los siete tienen marcador en
`ejemplo/`, así que el sistema **arranca sin ellos** — pero lo que produce lleva
marca de marcador, no la de GEW·RD.

| Activo | Bytes | De dónde sale |
|---|---|---|
| `fuentes/VAGRoundedStdThin.ttf` | 32,824 | licenciada · el peso del logo |
| `fuentes/VAGRoundedStdLight.ttf` | 32,448 | licenciada · cuerpo de texto |
| `fuentes/VAGRoundedStdBold.ttf` | 34,596 | licenciada · titulares |
| `fuentes/VAGRoundedStdBlack.ttf` | 33,972 | licenciada · cifras grandes |
| `logo/gew-rd-lockup-color.png` | 159,257 | de GEN · el logo que manda, el dominicano |
| `logo/gew-rd-lockup-blanco.png` | 145,302 | de GEN · el mismo, para fondos oscuros |
| `logo/gew-rd-anillo.png` | 67,287 | de GEN · el anillo, y de él salen los 39 segmentos del pulso |

**505,686 bytes en total.** Las cuatro tipografías son licenciadas: no se
redistribuyen ni una vez, y por eso `ejemplo/fuentes/` lleva **Poppins** (OFL)
con el nombre de fichero de las VAG, para que el motor la encuentre por el
nombre que espera. Los tres PNG dominicanos los provee GEN; no hay vector.

Los otros dos activos que `entorno.py` marca como obligatorios —
`logo/socios/enlata-wordmark.svg` y `logo/socios/iavanza-lockup.svg`— **sí se
pueden conseguir**: viven en el repo público de IAvanza.

| Fichero | Bytes | sha256 (16) |
|---|---:|---|
| `fuentes/VAGRoundedStdBlack.ttf` | 33,972 | `e37c520e37530aba` |
| `fuentes/VAGRoundedStdBold.ttf` | 34,596 | `af01f6de02662712` |
| `fuentes/VAGRoundedStdLight.ttf` | 32,448 | `3689d2cc10f459aa` |
| `fuentes/VAGRoundedStdThin.ttf` | 32,824 | `68e5b5f1bce4197e` |
| `logo/banner-web/banner-1.png` | 317,728 | `cc657e63904fd11a` |
| `logo/banner-web/banner-2.png` | 339,776 | `6c16354821275a9a` |
| `logo/gew-badge-actividad-blanco.png` | 135,520 | `449e5c9e236f54ae` |
| `logo/gew-badge-actividad-full-blanco.png` | 163,317 | `fdf606c0f5da2c57` |
| `logo/gew-badge-actividad.png` | 141,340 | `19e264f785617f12` |
| `logo/gew-badge-actividad.svg` | 27,251 | `4282a685139083c6` |
| `logo/gew-global-lockup.svg` | 27,441 | `4d3ca9c718b5e32c` |
| `logo/gew-rd-anillo.png` | 67,287 | `b35ebcefceb9b876` |
| `logo/gew-rd-lockup-blanco.png` | 145,302 | `5824abe419d51566` |
| `logo/gew-rd-lockup-color.png` | 159,257 | `01cb3b9b7b4f8afa` |
| `logo/socios/enlata-wordmark.svg` | 3,179 | `87950abc9761cd2d` |
| `logo/socios/ia-media-isotipo-blanco.svg` | 1,132 | `9d1c47ecaff9155d` |
| `logo/socios/ia-media-isotipo.svg` | 1,132 | `abedb7bfda487645` |
| `logo/socios/ia-media-lockup-blanco.svg` | 3,276 | `579bda9b336b2e86` |
| `logo/socios/ia-media-lockup-carbon.svg` | 3,276 | `34e3e2726d167f30` |
| `logo/socios/ia-media-lockup.svg` | 3,276 | `0e573074f4b52461` |
| `logo/socios/iavanza-lockup-blanco.svg` | 6,572 | `6f185dc39b5ef8ec` |
| `logo/socios/iavanza-lockup.svg` | 6,696 | `0a86fca28e8bc823` |

**22 ficheros · 1,686,598 bytes**

## De dónde salió cada bloque

**`fuentes/`** — VAG Rounded Std. Piero confirmó el 5-sep-2026 que hay derecho de uso. Verificado que el logo de GEW usa el peso Thin (IoU 0,9547 contra 0,8467 del Light). ⚠️ Sigue sin resolverse si la licencia es propia o derivada del papel ante GEN.

**`logo/banner-web`** — Banners de la web.

**`logo/gew-badge`** — Badge oficial «Official Activity», bajado del Drive de GEN. Archivado: no se usa en las piezas, manda el dominicano.

**`logo/gew-global`** — Lockup global en inglés, de GEN. viewBox 736×281,4.

**`logo/gew-rd`** — Lockup dominicano — el que dice «República Dominicana». Es el que manda en las piezas, por decisión de Piero del 5-sep-2026. Normalizados en un lienzo común de 3438×1174 alineados por el anillo. De su anillo salen los 39 segmentos medidos de `datos/anillo-segmentos.json`, que son el pulso.

**`logo/socios`** — Marcas de la Fundación Enlata y de IAvanza.

**`logo/socios/ia-media`** — ⚙️ GENERADO, no recibido: sale de `logo_ia_media.py` con las proporciones medidas de IAvanza. Color #8475FF, cerrado el 5-sep-2026. Su casa es `iavanza_design_system/logo/`, donde el generador escribe una copia; aquí vive para que GEW no dependa de otro proyecto al renderizar.

