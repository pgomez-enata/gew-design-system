#!/usr/bin/env python3
"""
Regraba ACTIVOS.md · GEW · RD.

`fuentes/` y `logo/` no entran en git —son activos de terceros y un binario que
entra en el historial ya no se saca—, así que ACTIVOS.md es la única constancia
de qué tiene que haber ahí. Sus hashes los verifica `entorno.py`: un activo que
existe pero ya no es el mismo es peor que uno que falta, porque no avisa.

Se regraba cuando un activo cambia a propósito. Si cambió sin querer, lo que
toca no es regrabar: es averiguar por qué.

    python3 sellar_activos.py
"""
import hashlib, json, os, sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
TOK = json.load(open(f"{RAIZ}/tokens/tokens.json", encoding="utf-8"))
CARPETAS = ("fuentes", "logo")

ORIGEN = {
    "fuentes/": "VAG Rounded Std. Piero confirmó el 5-sep-2026 que hay derecho de uso. "
                "Verificado que el logo de GEW usa el peso Thin (IoU 0,9547 contra "
                "0,8467 del Light). ⚠️ Sigue sin resolverse si la licencia es propia o "
                "derivada del papel ante GEN.",
    "logo/gew-rd": "Lockup dominicano — el que dice «República Dominicana». Es el que "
                   "manda en las piezas, por decisión de Piero del 5-sep-2026. "
                   "Normalizados en un lienzo común de 3438×1174 alineados por el "
                   "anillo. De su anillo salen los 39 segmentos medidos de "
                   "`datos/anillo-segmentos.json`, que son el pulso.",
    "logo/gew-badge": "Badge oficial «Official Activity», bajado del Drive de GEN. "
                      "Archivado: no se usa en las piezas, manda el dominicano.",
    "logo/gew-global": "Lockup global en inglés, de GEN. viewBox 736×281,4.",
    "logo/socios/ia-media": "⚙️ GENERADO, no recibido: sale de `logo_ia_media.py` con "
                            "las proporciones medidas de IAvanza. Color #8475FF, cerrado "
                            "el 5-sep-2026. Su casa es `iavanza_design_system/logo/`, "
                            "donde el generador escribe una copia; aquí vive para que "
                            "GEW no dependa de otro proyecto al renderizar.",
    "logo/socios": "Marcas de la Fundación Enlata y de IAvanza.",
    "logo/banner-web": "Banners de la web.",
}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for t in iter(lambda: f.read(1 << 20), b""):
            h.update(t)
    return h.hexdigest()[:16]


def main():
    filas = []
    for c in CARPETAS:
        for raiz, _, fs in os.walk(f"{RAIZ}/{c}"):
            for f in sorted(fs):
                if f.startswith("."):
                    continue
                p = os.path.join(raiz, f)
                filas.append((os.path.relpath(p, RAIZ), os.path.getsize(p), sha(p)))
    filas.sort()
    if not filas:
        sys.exit("no hay activos que sellar")

    def origen(rel):
        for k in sorted(ORIGEN, key=len, reverse=True):
            if rel.startswith(k):
                return k, ORIGEN[k]
        return rel, "—"

    with open(f"{RAIZ}/ACTIVOS.md", "w", encoding="utf-8") as f:
        f.write(f"""# Activos que el repo NO versiona

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

Medido el {TOK['meta']['actualizado']} · sistema v{TOK['meta']['version']}

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
""")
        for rel, n, h in filas:
            f.write(f"| `{rel}` | {n:,} | `{h}` |\n")
        f.write(f"\n**{len(filas)} ficheros · {sum(n for _, n, _ in filas):,} bytes**\n")
        f.write("\n## De dónde salió cada bloque\n\n")
        vistos = set()
        for rel, _, _ in filas:
            k, o = origen(rel)
            if k not in vistos:
                vistos.add(k)
                f.write(f"**`{k}`** — {o}\n\n")
    print(f"ACTIVOS.md · {len(filas)} ficheros · "
          f"{sum(n for _, n, _ in filas):,} bytes")


if __name__ == "__main__":
    main()
