#!/usr/bin/env python3
"""
El elemento distintivo del movimiento · GEW · RD.

GEW es la misma marca en 200 países. Lo que hace falta es algo que diga «esto
es de aquí» sin tocar el logo, que GEN no deja variar.

La respuesta sale del propio logo, medida: los **39 segmentos** del anillo
—sus anchos angulares irregulares y sus 30 colores— están en
`datos/anillo-segmentos.json`, sacados recorriendo el radio medio del PNG cada
0,05°. Tres formas de usarlos:

    cinta    la rueda DESENROLLADA en una banda recta, con sus anchos reales
    pulso    los mismos segmentos como barras de altura variable
    estela   segmentos desplazados en diagonal, avanzando

⛔ Lo que NO se puede hacer: un **arco** de la rueda. Sería el logo recortado, y
la regla del sistema es logos completos. Por eso las tres propuestas son
formas rectas: ninguna se lee como una rueda a medias.

Y la jerarquía de marcas, que hoy no existe: el sistema pone «NATIONAL HOST» y
«PARTNERS» y ya. Son tres papeles distintos y sólo estaban dos.

Uso:
    python3 movimiento.py --muestras          las 3 propuestas comparadas
    python3 movimiento.py --piezas            piezas de ejemplo con cada una
    python3 movimiento.py --marcas            la jerarquía de marcas, sola
"""
import argparse, json, os, sys

from PIL import Image, ImageDraw

from campana import (FORMATOS, RAIZ, TOK, fuente, marca_alto, pulso, tinta)

SEG = json.load(open(f"{RAIZ}/datos/anillo-segmentos.json", encoding="utf-8"))
SEGMENTOS = SEG["lista"]
CARBON = TOK["color"]["campana2026"]["carbon"]["hex"]
NARANJA = TOK["color"]["campana2026"]["naranja"]["hex"]
BLANCO = "#FFFFFF"


# ── los tres elementos ─────────────────────────────────────────────────
def cinta(d, x, y, ancho, alto, desde=0, n=None, aire=None, vertical=False):
    """La rueda desenrollada. Los anchos son los grados reales de cada
    segmento, escalados al largo que se pida. El aire entre segmentos es el
    7,7 % que mide el anillo, no un valor inventado."""
    segs = SEGMENTOS[desde:desde + n] if n else SEGMENTOS
    total = sum(s["grados"] for s in segs)
    largo = alto if vertical else ancho
    hueco = SEG["aire_blanco_grados"] / 360 if aire is None else aire
    util = largo * (1 - hueco)
    sep = (largo - util) / max(1, len(segs) - 1)
    p = 0.0
    for s in segs:
        L = util * s["grados"] / total
        if vertical:
            d.rectangle([x, round(y + p), x + ancho - 1, round(y + p + L) - 1],
                        fill=s["hex"])
        else:
            d.rectangle([round(x + p), y, round(x + p + L) - 1, y + alto - 1],
                        fill=s["hex"])
        p += L + sep
    return largo


# `pulso` vive en campana.py desde que pasó a producción: una función en dos
# ficheros se separa sola. Aquí sólo se importa para la lámina comparativa.


def estela(d, x, y, ancho, alto, desde=0, n=None, sesgo=0.42):
    """Segmentos desplazados: cada uno arranca más adelante que el anterior.
    Es la rueda en marcha — de ahí «movimiento»."""
    segs = SEGMENTOS[desde:desde + n] if n else SEGMENTOS
    paso = ancho / len(segs)
    an = max(2, round(paso * 0.70))
    for i, s in enumerate(segs):
        xx = round(x + i * paso)
        dy = round(alto * sesgo * (i / max(1, len(segs) - 1) - 0.5))
        d.polygon([(xx, y + alto + dy), (xx + an, y + alto + dy),
                   (xx + an + round(alto * 0.30), y + dy), (xx + round(alto * 0.30), y + dy)],
                  fill=s["hex"])
    return ancho


ELEMENTOS = {"cinta": cinta, "pulso": pulso, "estela": estela}

# ELEGIDO por Piero el 5-sep-2026. Las otras dos quedan en el fichero como
# constancia de lo que se comparó, no como opciones vivas.
ELEGIDO = "pulso"


# ── la jerarquía de marcas ─────────────────────────────────────────────
# Corregido por Piero el 5-sep-2026: **Enlata e IAvanza son los dos Partners**,
# no anfitrión + aliado. Y hace falta un espacio para los patrocinadores del
# movimiento, que antes no existía.
#
# Confirmado el 5-sep-2026: el papel de «National Host» queda retirado del
# sistema. `auditar_index.py` falla si reaparece atribuido a Enlata.
#
# Los rótulos van BILINGÜES por decisión suya. «PARTNERS» se escribe igual en
# los dos idiomas, así que sólo los otros dos llevan las dos palabras.
BLOQUES = [
    {"clave": "partners", "rotulo": "PARTNERS",
     "marcas": ["logo/socios/enlata-wordmark.svg", "logo/socios/iavanza-lockup.svg"],
     "cuando": "siempre"},
    {"clave": "patrocinadores", "rotulo": "PATROCINADORES · SPONSORS",
     "marcas": [], "cuando": "cuando haya acuerdo firmado",
     "vacio": "espacio reservado"},
    {"clave": "cobertura", "rotulo": "COBERTURA · COVERAGE",
     "marcas": ["logo/socios/ia-media-lockup-carbon.svg"], "cuando": "sólo cobertura"},
]


def banda_marcas(im, d, x, y, ancho, alto, oscuro=True, con_cobertura=False,
                 patrocinadores=None, cap_rot=None, marcar_hueco=True):
    """La banda del pie, en dos filas.

    Fila 1: partners y patrocinadores, lado a lado.
    Fila 2: la cobertura, más pequeña — no tiene el peso de un partner.

    Devuelve las medidas para que la auditoría las pueda comprobar."""
    rot_col = "#B8B8B8" if oscuro else "#8A8A8A"
    tinta_col = BLANCO if oscuro else CARBON
    cap_rot = cap_rot or max(9, round(alto * 0.098))
    f_rot = fuente("Bold", cap_rot)
    med = {"bloques": [], "avisos": []}

    # ── fila 1 ─────────────────────────────────────────────────────────
    h_fila1 = round(alto * (0.52 if con_cobertura else 0.86))
    alto_logo = round(h_fila1 * 0.50)
    y_logo = y + round(h_fila1 * 0.40)
    # el hueco de patrocinadores se reserva aunque esté vacío: si no, cuando
    # llegue el primero habrá que recomponer la pieza entera
    mitad = round(ancho * 0.56)

    xx = x
    for b in BLOQUES[:2]:
        d.text((xx, y), b["rotulo"], font=f_rot, fill=rot_col)
        b_rot = d.textbbox((xx, y), b["rotulo"], font=f_rot)
        marcas = patrocinadores if b["clave"] == "patrocinadores" and patrocinadores \
            else b["marcas"]
        xl, an = xx, b_rot[2] - xx
        for ruta in marcas:
            lg = marca_alto(f"{RAIZ}/{ruta}", alto_logo, blanco=oscuro)
            im.paste(lg, (xl, y_logo), lg)
            xl += lg.width + round(ancho * 0.032)
        if marcas:
            an = max(an, xl - round(ancho * 0.032) - xx)
        elif marcar_hueco:
            # el hueco se dibuja para que se vea que está reservado, no olvidado
            w_h = round(ancho * 0.30)
            d.rectangle([xx, y_logo, xx + w_h, y_logo + alto_logo],
                        outline="#6E6E6E", width=2)
            f_h = fuente("Light", round(cap_rot * 0.92))
            bb = d.textbbox((0, 0), b["vacio"], font=f_h)
            tinta(d, (xx + (w_h - (bb[2] - bb[0])) // 2,
                      y_logo + (alto_logo - (bb[3] - bb[1])) // 2), b["vacio"], f_h,
                  fill="#8A8A8A")
            an = max(an, w_h)
        med["bloques"].append({"clave": b["clave"], "x": xx, "ancho": an,
                               "marcas": len(marcas)})
        xx = x + mitad if b["clave"] == "partners" else xx + an
    med["derecha"] = xx

    # ── fila 2 · la cobertura ──────────────────────────────────────────
    if con_cobertura:
        b = BLOQUES[2]
        y2 = y + h_fila1 + round(alto * 0.14)
        f_r2 = fuente("Bold", round(cap_rot * 0.88))
        d.text((x, y2), b["rotulo"], font=f_r2, fill=rot_col)
        b_r2 = d.textbbox((x, y2), b["rotulo"], font=f_r2)
        alto_m = round(alto * 0.20)
        lg = marca_alto(f"{RAIZ}/{b['marcas'][0]}", alto_m, blanco=False)
        x_m = b_r2[2] + round(ancho * 0.030)
        im.paste(lg, (x_m, y2 - round(alto_m * 0.26)), lg)
        med["bloques"].append({"clave": "cobertura", "x": x,
                               "ancho": x_m + lg.width - x, "marcas": 1})
        med["derecha"] = max(med["derecha"], x_m + lg.width)
        med["alto_usado"] = y2 + alto_m - y
    else:
        med["alto_usado"] = h_fila1 + alto_logo

    med["desborda"] = max(0, med["derecha"] - (x + ancho))
    return med


# ── muestras y piezas de ejemplo ───────────────────────────────────────
def lamina_muestras(salida):
    """Los tres elementos, uno debajo del otro, en claro y en oscuro."""
    W, H = 1600, 1760
    im = Image.new("RGB", (W, H), BLANCO)
    d = ImageDraw.Draw(im)
    m = 90
    f_t = fuente("Bold", 44)
    f_n = fuente("Bold", 26)
    f_p = fuente("Light", 21)

    tinta(d, (m, 70), "Elemento distintivo", f_t, fill=CARBON)
    tinta(d, (m, 140), f"Los {len(SEGMENTOS)} segmentos del anillo GEW·RD, medidos "
          f"del propio logo. Tres formas de usarlos.", f_p, fill="#666666")
    tinta(d, (m, 176), "Ninguna es un arco: un arco sería el logo recortado.",
          f_p, fill="#666666")
    tinta(d, (m, 212), "⚠ Los 30 colores del anillo RD no coinciden con los del SVG "
          "global: 32 de 39 a más de 24 de distancia.", fuente("Light", 18),
          fill="#B0392E")

    y = 262
    for clave, titulo, nota in (
            ("cinta", "1 · La cinta",
             "La rueda desenrollada. Anchos y aire reales del anillo (7,7 % de aire)."),
            ("pulso", "2 · El pulso",
             "Cada barra mide lo que mide su segmento: de 1° a 32,75°. Eso da el ritmo."),
            ("estela", "3 · La estela",
             "Los mismos segmentos, desplazados. La rueda en marcha.")):
        tinta(d, (m, y), titulo, f_n, fill=CARBON)
        tinta(d, (m, y + 38), nota, f_p, fill="#777777")
        yy = y + 86
        # sobre blanco, ancho completo
        ELEMENTOS[clave](d, m, yy, W - m * 2, 44)
        # sobre carbón, la mitad
        d.rectangle([m, yy + 76, W - m, yy + 76 + 110], fill=CARBON)
        ELEMENTOS[clave](d, m + 40, yy + 108, (W - m * 2) // 2 - 40, 44)
        # a tamaño pequeño, para ver si aguanta
        ELEMENTOS[clave](d, W // 2 + 60, yy + 118, 380, 20)
        tinta(d, (W // 2 + 60, yy + 92), "a 380 px", fuente("Light", 15), fill="#999999")
        y += 300

    # la banda de marcas: tres bloques, rótulos bilingües
    tinta(d, (m, y + 10), "Dónde y cómo se nombran", f_n, fill=CARBON)
    tinta(d, (m, y + 48), "Enlata e IAvanza son los dos Partners. Los patrocinadores "
          "tienen su hueco aunque esté vacío.", f_p, fill="#777777")
    for i, (cob, etq) in enumerate(((False, "pieza de campaña"),
                                    (True, "pieza de cobertura"))):
        yy = y + 100 + i * 214
        d.rectangle([m, yy, W - m, yy + 176], fill=CARBON)
        tinta(d, (m + 40, yy + 14), etq, fuente("Light", 15), fill="#8A8A8A")
        banda_marcas(im, d, m + 40, yy + 46, W - m * 2 - 80, 116,
                     oscuro=True, con_cobertura=cob)
    im.save(salida)
    return im


def pieza_ejemplo(clave, salida, fmt="retrato", con_registro=False):
    """Una pieza de campaña con el elemento aplicado, para verlo en su sitio."""
    W, H = FORMATOS[fmt]["px"]
    im = Image.new("RGB", (W, H), CARBON)
    d = ImageDraw.Draw(im)
    U = W
    m = round(U * 0.0667)
    # En historia la interfaz de Instagram se come 269 px arriba y 250 abajo.
    # La primera versión de esta pieza ponía el lockup en y=72 y la banda en
    # y=1681: los dos FUERA. Se ve al medirlo, no al mirarlo.
    TOP, BOT = FORMATOS[fmt]["segura"] or (0, H)

    lock = marca_alto(f"{RAIZ}/logo/gew-rd-lockup-blanco.png", round(U * 0.0889))
    im.paste(lock, (m, TOP + (m if TOP == 0 else round(U * 0.028))), lock)

    # el elemento, justo debajo de la cabecera: es la firma del movimiento
    y_el = TOP + (m if TOP == 0 else round(U * 0.028)) + lock.height + round(U * 0.055)
    alto_el = round(U * (0.042 if clave == "pulso" else
                         0.038 if clave == "estela" else 0.030))
    ELEMENTOS[clave](d, m, y_el, W - m * 2, alto_el)

    f_f = fuente("Black", round(U * 0.063))
    b = tinta(d, (m, y_el + alto_el + round(U * 0.075)), "16—22", f_f, fill=NARANJA)
    f_t = fuente("Bold", round(U * 0.077))
    y = b[3] + round(U * 0.035)
    for ln in ("Aquí los", "emprendedores", "prosperan"):
        bb = tinta(d, (m, y), ln, f_t, fill=BLANCO)
        y = bb[3] + round(U * 0.022)

    alto_banda = round(U * (0.200 if con_registro else 0.140))
    y_banda = BOT - (m if BOT == H else round(U * 0.028)) - alto_banda
    med = banda_marcas(im, d, m, y_banda, W - m * 2, alto_banda,
                       oscuro=True, con_cobertura=con_registro)
    med["zona_segura"] = [TOP, BOT]
    med["fuera_arriba"] = max(0, TOP - (TOP + (m if TOP == 0 else round(U * 0.028))))
    med["fuera_abajo"] = max(0, (y_banda + alto_banda) - BOT)
    im.save(salida)
    return im, med


def main():
    ap = argparse.ArgumentParser(description="Elemento distintivo del movimiento")
    ap.add_argument("--muestras", action="store_true")
    ap.add_argument("--piezas", action="store_true")
    ap.add_argument("--marcas", action="store_true")
    ap.add_argument("--salida", default=f"{RAIZ}/_salida/movimiento")
    a = ap.parse_args()
    if not (a.muestras or a.piezas or a.marcas):
        a.muestras = a.piezas = True

    os.makedirs(a.salida, exist_ok=True)
    hechas, avisos = [], []

    if a.muestras or a.marcas:
        p = f"{a.salida}/propuestas--muestra.png"
        lamina_muestras(p)
        hechas.append(p)

    if a.piezas:
        # sólo el elegido. Las otras dos siguen en la lámina comparativa, como
        # constancia de lo que se comparó.
        for fmt in ("retrato", "cuadrado", "historia"):
            for cob, etq in ((False, "campana"), (True, "cobertura")):
                p = f"{a.salida}/{ELEGIDO}-{etq}--{fmt}.png"
                _, med = pieza_ejemplo(ELEGIDO, p, fmt=fmt, con_registro=cob)
                hechas.append(p)
                if med["desborda"] or med["fuera_abajo"] or med["fuera_arriba"]:
                    avisos.append(
                        f"  FALLA {ELEGIDO}/{etq}/{fmt}: desborda {med['desborda']} px "
                        f"· fuera de la zona segura {med['fuera_arriba']}↑ "
                        f"{med['fuera_abajo']}↓ px")

    esperadas = (1 if (a.muestras or a.marcas) else 0) + (6 if a.piezas else 0)
    print(f"producidas {len(hechas)} de {esperadas} esperadas")
    print(f"elemento elegido: {ELEGIDO}")
    print(f"segmentos del anillo: {len(SEGMENTOS)} · colores {SEG['colores_unicos']} · "
          f"aire {SEG['aire_blanco_grados']:.1f}° ({SEG['aire_blanco_grados']/3.6:.1f} %)")
    for x in avisos:
        print(x)
    for h in hechas:
        print(h)
    sys.exit(1 if avisos else 0)


if __name__ == "__main__":
    main()
