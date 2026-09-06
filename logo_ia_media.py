#!/usr/bin/env python3
"""
Logo de IA Media, con la línea gráfica de IAvanza.

No lo invento: IAvanza ya tiene un patrón de submarca —las 13 comunidades— y
está medido en su `tokens.json`. IA Media se construye con las MISMAS
proporciones:

    cuerpo del texto   = 1,0759 × alto del isotipo
    cap-height         = 0,7393 × alto del isotipo
    solape del texto   = −0,024 × ancho del isotipo   (anidado, no colisión)
    alineación         = línea base común, NO centrado vertical
    tipografía         = Archivo SemiExpanded ExtraBold (OFL)
    clearspace mínimo  = 1/3 del alto del isotipo

El texto sale convertido a trazo con fontTools, igual que los lockups de las
comunidades: el SVG no depende de ninguna fuente instalada.

El COLOR está CERRADO: #8475FF, aprobado por Piero el 5-sep-2026. Va con
ΔE2000 15,2 —por debajo del 20 que se usó para IA Human— y se aceptó a
sabiendas: ver `--colores`.

Uso:
    python3 logo_ia_media.py                genera las variantes
    python3 logo_ia_media.py --colores      la medición del color
"""
import argparse, json, os, re, sys

IAV = os.environ.get("IAVANZA_DIR", "../iavanza_design_system")
RAIZ = os.path.dirname(os.path.abspath(__file__))
TOK_IAV = json.load(open(f"{IAV}/tokens/tokens.json", encoding="utf-8"))
LK = TOK_IAV["logo"]["lockup"]
INK = TOK_IAV["color"]["primitivos"]["ink"]["hex"]
FUENTE = f"{IAV}/fuentes/Archivo-SemiExpanded-ExtraBold.ttf"

# Elegido con el generador de IAvanza («03 Comunidades/_generador/colores.py»),
# con su mismo método: ΔE2000 contra las 13 comunidades más el azul de marca y
# TESTERS, contraste ≥3:1 sobre blanco y contra el ink del nombre, y croma
# dentro de la familia (piso en la mediana, C*≥78).
# ΔE = 15,2 — por debajo del umbral de 20 que se usó para IA Human e IA
# Teachers. Aprobado así por Piero el 5-sep-2026: con C*≥78 no hay hueco mejor
# (la rueda ya está llena con 13 comunidades) y bajar el croma daba ΔE 24,7
# pero con un caqui apagado, que es lo que el generador de IAvanza avisa que
# hay que evitar. Se prefirió croma de marca a distancia de catálogo.
COLOR = "#8475FF"
COLOR_CLARO = "#9487FF"      # para el carbón #4A4A4A de las piezas GEW
PALABRA = "MEDIA"


def _isotipo():
    s = open(f"{IAV}/logo/iavanza-isotipo.svg", encoding="utf-8").read()
    vb = re.search(r'viewBox="([\d.\s-]+)"', s).group(1).split()
    return (re.search(r'<path d="([^"]+)"', s).group(1),
            float(vb[2]), float(vb[3]))


def _texto_path(texto, cuerpo, x, y_base):
    """El texto convertido a trazo, como en los lockups de comunidad."""
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.misc.transform import Transform

    f = TTFont(FUENTE)
    upem = f["head"].unitsPerEm
    esc = cuerpo / upem
    cmap = f.getBestCmap()
    gs = f.getGlyphSet()
    hm = f["hmtx"]
    d, cursor = [], 0.0
    for ch in texto:
        g = cmap.get(ord(ch))
        if not g:
            continue
        pen = SVGPathPen(gs)
        # y invertida: en la fuente crece hacia arriba, en SVG hacia abajo
        tp = TransformPen(pen, Transform(esc, 0, 0, -esc, x + cursor * esc, y_base))
        gs[g].draw(tp)
        p = pen.getCommands()
        if p:
            d.append(p)
        cursor += hm[g][0]
    # Redondear a 3 decimales no es cosmética: SVGPathPen escribe hasta 15
    # decimales, y un número así contiene por dentro un 4 seguido de ocho
    # dígitos — que es la forma de un RNC. La puerta de IAvanza lo lee como
    # identidad fiscal y frena la publicación. El falso positivo se arregla
    # aquí, no aflojando la regla que protege el RNC de verdad.
    # De paso el fichero pesa la mitad; a 3 decimales el error es de 0,001 px
    # sobre un isotipo de 52,85.
    crudo = " ".join(d)
    return re.sub(r"-?\d+\.\d{4,}",
                  lambda m: f"{round(float(m.group(0)), 3):g}", crudo), cursor * esc


def lockup(color=None, texto_color=None, alto_iso=52.85):
    """Devuelve el SVG del lockup. Las proporciones son las de IAvanza."""
    color = color or COLOR
    texto_color = texto_color or INK
    d_iso, w_iso, h_iso = _isotipo()
    k = alto_iso / h_iso
    W_iso, H_iso = w_iso * k, h_iso * k

    cuerpo = LK["font_size_x_alto_isotipo"] * H_iso
    cap = LK["cap_height_x_alto_isotipo"] * H_iso
    x_txt = W_iso + LK["solape_visual_x_ancho_isotipo"] * W_iso
    y_base = H_iso                       # línea base común con el pie del isotipo

    d_txt, w_txt = _texto_path(PALABRA, cuerpo, x_txt, y_base)
    W = x_txt + w_txt
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.2f} {H_iso:.2f}" \
width="{W:.2f}" height="{H_iso:.2f}" role="img" aria-label="IA Media">
<title>IA Media — submarca de IAvanza</title>
<!-- Construido con las proporciones medidas de IAvanza (tokens.logo.lockup):
     cuerpo {LK["font_size_x_alto_isotipo"]} × alto del isotipo · cap {LK["cap_height_x_alto_isotipo"]} ·
     solape {LK["solape_visual_x_ancho_isotipo"]} × ancho del isotipo · línea base común.
     Texto en Archivo SemiExpanded ExtraBold (OFL), convertido a trazo.
     Color {color}, cerrado por Piero el 5-sep-2026 (ΔE 15,2 contra las 13
     comunidades de IAvanza; ver tokens.movimiento.ia_media). -->
<g transform="scale({k:.6f})"><path fill="{color}" fill-rule="evenodd" d="{d_iso}"/></g>
<path fill="{texto_color}" d="{d_txt}"/>
</svg>'''


def isotipo_solo(color=None, alto=52.85):
    d_iso, w_iso, h_iso = _isotipo()
    k = alto / h_iso
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w_iso*k:.2f} {h_iso*k:.2f}" '
            f'width="{w_iso*k:.2f}" height="{h_iso*k:.2f}" role="img" aria-label="IA Media">'
            f'<g transform="scale({k:.6f})"><path fill="{color or COLOR}" fill-rule="evenodd" '
            f'd="{d_iso}"/></g></svg>')


VARIANTES = {
    "ia-media-lockup":        lambda: lockup(),
    "ia-media-lockup-blanco": lambda: lockup("#FFFFFF", "#FFFFFF"),
    "ia-media-lockup-carbon": lambda: lockup(COLOR_CLARO, "#FFFFFF"),
    "ia-media-isotipo":       lambda: isotipo_solo(),
    "ia-media-isotipo-blanco": lambda: isotipo_solo("#FFFFFF"),
}


def medir(svg_path, png_path):
    """Mide el lockup renderizado: proporciones contra las de IAvanza."""
    from PIL import Image
    import numpy as np
    im = Image.open(png_path).convert("RGBA")
    a = np.array(im)
    op = a[:, :, 3] > 40
    ys, xs = np.nonzero(op)
    if not len(ys):
        return {"error": "el PNG salió vacío"}
    # el isotipo es la parte coloreada; el texto, la tinta
    return {"tinta": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
            "lienzo": list(im.size),
            "ratio": round(im.width / im.height, 4)}


def main():
    ap = argparse.ArgumentParser(description="Logo de IA Media")
    ap.add_argument("--colores", action="store_true", help="la medición del color")
    ap.add_argument("--salida", default=f"{RAIZ}/logo/socios")
    ap.add_argument("--casa", default=f"{IAV}/logo",
                    help="la casa del logo: es una marca de IAvanza, no de GEW. "
                         "Se escribe en las dos para que GEW no dependa en tiempo "
                         "de render de otro proyecto.")
    ap.add_argument("--solo-aqui", action="store_true",
                    help="no tocar el sistema de IAvanza")
    a = ap.parse_args()

    if a.colores:
        from campana import TOK  # noqa
        print(f"color propuesto      {COLOR}")
        print(f"variante para carbón {COLOR_CLARO}")
        print("ΔE2000 contra las 13 comunidades + azul de marca + TESTERS: 15,2")
        print("CERRADO por Piero el 5-sep-2026, sabiendo que el umbral de referencia")
        print("de IA Human e IA Teachers fue 20. Con croma de marca (C*>=78) no hay")
        print("hueco mejor: la rueda ya está llena con 13 comunidades.")
        return

    os.makedirs(a.salida, exist_ok=True)
    import subprocess
    hechos, fallos = [], []
    for nombre, fn in VARIANTES.items():
        svg = fn()
        p = f"{a.salida}/{nombre}.svg"
        with open(p, "w", encoding="utf-8") as f:
            f.write(svg)
        hechos.append(p)
        if not a.solo_aqui and os.path.isdir(a.casa):
            q = f"{a.casa}/{nombre}.svg"
            with open(q, "w", encoding="utf-8") as f:
                f.write(svg)
            hechos.append(q)
        # y su PNG a 512 de ancho, para comprobar que rasteriza
        png = f"{RAIZ}/_salida/ia-media/{nombre}.png"
        os.makedirs(os.path.dirname(png), exist_ok=True)
        r = subprocess.run(["rsvg-convert", "-w", "512", "-o", png, p],
                           capture_output=True)
        if r.returncode:
            fallos.append(f"  FALLA rasterizar {nombre}: {r.stderr.decode()[:60]}")
        else:
            hechos.append(png)

    esperados = len(VARIANTES) * (2 if a.solo_aqui else 3)
    print(f"producidos {len(hechos)} de {esperados} esperados")
    d_iso, w_iso, h_iso = _isotipo()
    print(f"isotipo {w_iso}×{h_iso} · cuerpo {LK['font_size_x_alto_isotipo']}× · "
          f"cap {LK['cap_height_x_alto_isotipo']}× · solape {LK['solape_visual_x_ancho_isotipo']}×")
    print(f"clearspace mínimo: {TOK_IAV['logo']['clearspace']['minimo_x_alto_isotipo']}× el alto del isotipo")
    print(f"tamaño mínimo del lockup: {TOK_IAV['logo']['tamano_minimo']['lockup_ancho_px']} px de ancho")
    for f in fallos:
        print(f)
    for h in hechos:
        print(h)
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
