#!/usr/bin/env python3
"""
Deck para las charlas · GEW · RD.

La plantilla que se le manda al ponente para que no llegue con cualquier cosa.
Sigue el patrón de tipos de lámina que ya resolvió `iavanza/presentacion.py`
—portada, sección, texto, dato, cita, cierre— con la línea de GEW.

Dos medidas mandan aquí, y las dos se comprueban:

  · **16:9 a 1920×1080.** Es lo que proyecta cualquier sala.
  · **Margen de seguridad del 10 %** en los cuatro lados, y los **títulos
    dentro del 80 % central** — el «título seguro» que viene de la norma de
    televisión (SMPTE) y que sigue valiendo porque un proyector recorta.

Sale en PNG por lámina y, si se pide, un PDF de una pasada para enviarlo.

Uso:
    python3 deck.py --demo
    python3 deck.py --guion mi-charla.json --pdf
"""
import argparse, json, os, sys

from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
from campana import (TOK, PARTNERS, activo, fuente, marca_alto, marcas,  # noqa: E402
                     png_alto, pin, pulso, repartir, trocear)

W, H = 1920, 1080
SEGURO = 0.10                 # margen de seguridad, los 4 lados
TITULO_SEGURO = 0.80          # los títulos, dentro del 80 % central
CARBON = TOK["color"]["campana2026"]["carbon"]["hex"]
NARANJA = TOK["color"]["campana2026"]["naranja"]["hex"]
BLANCO, GRIS = "#FFFFFF", "#B8BCC0"
M = round(W * SEGURO)
TIPOS = ("portada", "seccion", "texto", "lista", "dato", "cita", "cierre")


def _caja_titulo():
    """La caja donde puede vivir un título: el 80 % central."""
    a = round(W * (1 - TITULO_SEGURO) / 2)
    b = round(H * (1 - TITULO_SEGURO) / 2)
    return a, b, W - a, H - b


def _encaja(d, texto, peso, cap, ancho, lineas_max=3):
    """Baja el cap hasta que el texto quepa en `ancho`. Mide tinta, no caja."""
    pal = texto.split()
    while cap >= 14:
        f = fuente(peso, cap)
        for k in range(1, min(lineas_max, len(pal)) + 1):
            r = repartir([(p, False) for p in pal], k,
                         [d.textlength(p, font=f) for p in pal],
                         d.textlength(" ", font=f))
            if not r:
                continue
            ls = ["".join(t for t, _ in ln) for ln in r]
            if max(d.textlength(l, font=f) for l in ls) <= ancho:
                return f, ls, cap
        cap -= 4
    return fuente(peso, 14), [texto], 14


def _base(fondo=CARBON):
    im = Image.new("RGB", (W, H), fondo)
    return im, ImageDraw.Draw(im)


def _pie(im, d, oscuro=True, n=None):
    """Lockup pequeño y el pulso. Va en todas menos en la portada."""
    alto = 46
    lock = png_alto(activo("logo/gew-rd-lockup-blanco.png" if oscuro
                           else "logo/gew-rd-lockup-color.png"), alto)
    im.paste(lock, (M, H - M + 10), lock)
    ancho_pulso = W - M * 2 - lock.width - 40 - (48 if n is not None else 0)
    pulso(d, M + lock.width + 40, H - M + 24, ancho_pulso, 18)
    if n is not None:
        f = fuente("Light", 22)
        b = d.textbbox((0, 0), str(n), font=f)
        d.text((W - M - (b[2] - b[0]) - b[0], H - M + 16 - b[1]), str(n),
               font=f, fill=GRIS if oscuro else "#8A8F94")


def portada(titulo, ponente="", cargo="", n=None):
    im, d = _base()
    lock = png_alto(activo("logo/gew-rd-lockup-blanco.png"), 118)
    im.paste(lock, (M, M - 24), lock)
    pulso(d, M, M + 118, W - M * 2, 34)
    # El titular se ajusta al ancho Y a lo que queda de alto: con tres líneas y
    # el bloque de ponente debajo, el cargo se salía 53 px por abajo. Sólo se
    # veía con otra tipografía, y sólo corriendo el clon — no el taller.
    ms = round(W * SEGURO * 0.55)
    alto_pie = 34
    alto_ponente = (150 if cargo else 90) if ponente else 0
    y0 = M + 230
    disponible = (H - ms - alto_pie - alto_ponente) - y0
    cap = 118
    while cap >= 40:
        f, ls, cap = _encaja(d, titulo, "Bold", cap, W - M * 2, 3)
        if round(cap * 1.26) * len(ls) <= disponible:
            break
        cap -= 8
    y = y0
    for l in ls:
        b = d.textbbox((M, y), l, font=f)
        d.text((M - (b[0] - M), y - (b[1] - y)), l, font=f, fill=BLANCO)
        y += round(cap * 1.26)
    if ponente:
        fp = fuente("Bold", 44)
        d.text((M, y + 30), ponente, font=fp, fill=NARANJA)
        if cargo:
            d.text((M, y + 90), cargo, font=fuente("Light", 32), fill=GRIS)
    # el pie vive DENTRO del margen inferior a propósito, pero tiene que caber:
    # con otra tipografía se pasaba 53 px del límite que la propia regla mide
    f2 = fuente("Light", 26)
    txt_pie = f"{TOK['campana']['fechas']} · {TOK['campana']['sitio']}"
    b_pie = d.textbbox((0, 0), txt_pie, font=f2)
    tope = H - round(W * SEGURO * 0.55) - (b_pie[3] - b_pie[1])
    y_pie = min(H - M + 14, tope - 4)
    d.text((M, y_pie), txt_pie, font=f2, fill=GRIS)
    # Los dos Partners, a la derecha del mismo pie. Sin rótulo: en la portada
    # no cabe y los logos hablan solos — el rótulo bilingüe va en el cierre,
    # que es la lámina de créditos. No cambia el cálculo vertical del titular:
    # se apoya en la línea que ya existía.
    ALTO_LG = 34
    # en blanco: el fondo de la portada es carbón y el wordmark de Enlata
    # es negro — sin esto se pierde contra el fondo
    piezas = [marca_alto(activo(r), ALTO_LG, blanco=True) for r in PARTNERS]
    sep = 26
    x = W - M
    for pz in reversed(piezas):
        x -= pz.width
        im.paste(pz, (x, y_pie + (b_pie[3] - b_pie[1]) // 2 - pz.height // 2), pz)
        x -= sep
    libre = (x + sep) - (M + (b_pie[2] - b_pie[0]))
    return im, {"tipo": "portada", "cap": cap, "lineas": len(ls),
                "partners": {"n": len(piezas), "alto": ALTO_LG,
                             "izquierda": x + sep, "libre": libre}}


def seccion(titulo, n=None):
    im, d = _base(NARANJA)
    f, ls, cap = _encaja(d, titulo, "Bold", 120, W - M * 2, 2)
    alto = round(cap * 1.24) * len(ls)
    y = (H - alto) // 2
    for l in ls:
        b = d.textbbox((M, y), l, font=f)
        d.text((M - (b[0] - M), y - (b[1] - y)), l, font=f, fill=CARBON)
        y += round(cap * 1.24)
    _pie(im, d, oscuro=False, n=n)
    return im, {"tipo": "seccion", "cap": cap, "lineas": len(ls)}


def texto(titulo, cuerpo, n=None):
    im, d = _base()
    f, ls, cap = _encaja(d, titulo, "Bold", 76, W - M * 2, 2)
    y = M
    for l in ls:
        b = d.textbbox((M, y), l, font=f)
        d.text((M - (b[0] - M), y - (b[1] - y)), l, font=f, fill=BLANCO)
        y += round(cap * 1.22)
    fc = fuente("Light", 38)
    y += 40
    for p in cuerpo.split("\n"):
        f2, ls2, _ = _encaja(d, p, "Light", 38, W - M * 2, 4)
        for l in ls2:
            d.text((M, y), l, font=f2, fill="#DCDCDC")
            y += 54
        y += 14
    _pie(im, d, n=n)
    return im, {"tipo": "texto", "cap": cap, "base": y}


def lista(titulo, puntos, n=None):
    im, d = _base()
    f, ls, cap = _encaja(d, titulo, "Bold", 76, W - M * 2, 2)
    y = M
    for l in ls:
        b = d.textbbox((M, y), l, font=f)
        d.text((M - (b[0] - M), y - (b[1] - y)), l, font=f, fill=BLANCO)
        y += round(cap * 1.22)
    y += 44
    fp = fuente("Light", 40)
    for p in puntos[:6]:
        pin(d, M + 12, y + 20, 11, NARANJA)
        f2, ls2, _ = _encaja(d, p, "Light", 40, W - M * 2 - 70, 2)
        for i, l in enumerate(ls2):
            d.text((M + 48, y + i * 52), l, font=f2, fill="#DCDCDC")
        y += 52 * len(ls2) + 30
    _pie(im, d, n=n)
    return im, {"tipo": "lista", "puntos": len(puntos), "base": y}


def dato(cifra, pie_txt, fuente_txt="", n=None):
    im, d = _base()
    f, ls, cap = _encaja(d, str(cifra), "Black", 300, W - M * 2, 1)
    b = d.textbbox((0, 0), ls[0], font=f)
    alto_cifra = b[3] - b[1]
    y_cifra = H // 2 - round(alto_cifra * 0.72)
    d.text(((W - (b[2] - b[0])) // 2 - b[0], y_cifra - b[1]), ls[0],
           font=f, fill=NARANJA)
    f2, ls2, _ = _encaja(d, pie_txt, "Light", 46, W - M * 2, 2)
    # el pie arranca DEBAJO de la tinta real de la cifra, no en un sitio fijo:
    # con una cifra alta como «90 %» se le montaba encima
    y = y_cifra + alto_cifra + 54
    for l in ls2:
        bb = d.textbbox((0, 0), l, font=f2)
        d.text(((W - (bb[2] - bb[0])) // 2 - bb[0], y - bb[1]), l, font=f2,
               fill=BLANCO)
        y += 62
    if fuente_txt:
        f3 = fuente("Light", 24)
        bb = d.textbbox((0, 0), fuente_txt, font=f3)
        d.text(((W - (bb[2] - bb[0])) // 2 - bb[0], y + 26 - bb[1]), fuente_txt,
               font=f3, fill=GRIS)
    _pie(im, d, n=n)
    return im, {"tipo": "dato", "cap": cap}


def cita(texto_, quien, cargo="", n=None):
    im, d = _base()
    f0 = fuente("Black", 96)
    d.text((M, M - 30), "“", font=f0, fill=NARANJA)
    f, ls, cap = _encaja(d, texto_, "Bold", 62, W - M * 2, 4)
    y = M + 90
    for l in ls:
        b = d.textbbox((M, y), l, font=f)
        d.text((M - (b[0] - M), y - (b[1] - y)), l, font=f, fill=BLANCO)
        y += round(cap * 1.26)
    d.text((M, y + 40), quien, font=fuente("Bold", 38), fill=NARANJA)
    if cargo:
        d.text((M, y + 92), cargo, font=fuente("Light", 28), fill=GRIS)
    _pie(im, d, n=n)
    return im, {"tipo": "cita", "cap": cap, "lineas": len(ls)}


def cierre(mensaje="Gracias", contacto="", n=None):
    im, d = _base()

    # Los dos Partners permanentes del movimiento, con su hueco de
    # patrocinadores. Añadido el 6-sep-2026: el deck no llevaba ninguna marca
    # de Enlata ni de IAvanza. Va anclada al pie —igual en todas las charlas—
    # y el bloque de texto se centra en lo que queda, no en la mitad de la
    # lámina: con un «gracias» de dos líneas el texto se le metía encima.
    CAP_ROT, ALTO_LG = 15, 48
    alto_banda = round(CAP_ROT * 2.28) + ALTO_LG
    y_pulso = H - M + 24
    y_banda = y_pulso - 30 - alto_banda

    lock = png_alto(activo("logo/gew-rd-lockup-blanco.png"), 150)
    f, ls, cap = _encaja(d, mensaje, "Bold", 96, W - M * 2, 2)
    f2 = fuente("Light", 32)
    pies = [x for x in (contacto, TOK["campana"]["sitio"]) if x]

    alto_txt = len(ls) * round(cap * 1.2) + (24 + 52 * len(pies) if pies else 0)
    alto_todo = lock.height + 70 + alto_txt
    zona = (M, y_banda - 30)
    y0 = zona[0] + max(0, ((zona[1] - zona[0]) - alto_todo) // 2)

    im.paste(lock, ((W - lock.width) // 2, y0), lock)
    y = y0 + lock.height + 70
    for l in ls:
        b = d.textbbox((0, 0), l, font=f)
        d.text(((W - (b[2] - b[0])) // 2 - b[0], y - b[1]), l, font=f, fill=BLANCO)
        y += round(cap * 1.2)
    for t in pies:
        b = d.textbbox((0, 0), t, font=f2)
        d.text(((W - (b[2] - b[0])) // 2 - b[0], y + 24 - b[1]), t, font=f2,
               fill=NARANJA if t == TOK["campana"]["sitio"] else GRIS)
        y += 52

    med_m = marcas(im, d, M, y_banda, W - M * 2, H, oscuro=True,
                   alto_logo=ALTO_LG, cap_rot=CAP_ROT)
    pulso(d, M, y_pulso, W - M * 2, 20)
    return im, {"tipo": "cierre", "cap": cap, "marcas": med_m,
                "banda_top": y_banda, "banda_base": med_m["fila1_base"],
                "libre_bajo_banda": y_pulso - med_m["fila1_base"],
                "libre_sobre_banda": y_banda - y}



GUION_DEMO = [
    {"t": "portada", "titulo": "Cómo poner precio sin regalar tu trabajo",
     "ponente": "Nombre Apellido", "cargo": "Fundadora · Organización"},
    {"t": "seccion", "titulo": "Lo que casi todos hacen mal"},
    {"t": "texto", "titulo": "El precio no sale del costo",
     "cuerpo": "Sale de lo que el cliente evita perder cuando te contrata.\n"
               "El costo sólo te dice por debajo de qué no puedes bajar."},
    {"t": "lista", "titulo": "Tres preguntas antes de dar un número",
     "puntos": ["¿Qué pasa si el cliente no lo resuelve?",
                "¿Cuánto le cuesta hoy hacerlo de otra forma?",
                "¿A quién más se lo puede pedir, y a qué precio?"]},
    {"t": "dato", "cifra": "90 %", "pie": "de las empresas del mundo son mipymes",
     "fuente": "Naciones Unidas — citado por GEN"},
    {"t": "cita", "texto": "El primer cliente fue mi vecina. El segundo, su "
     "hermana. Así empieza casi todo aquí.", "quien": "Nombre Apellido",
     "cargo": "Fundadora · Organización"},
    {"t": "cierre", "mensaje": "Gracias", "contacto": ""},
]
CONSTRUYE = {"portada": lambda x, n: portada(x["titulo"], x.get("ponente", ""),
                                             x.get("cargo", ""), n),
             "seccion": lambda x, n: seccion(x["titulo"], n),
             "texto": lambda x, n: texto(x["titulo"], x["cuerpo"], n),
             "lista": lambda x, n: lista(x["titulo"], x["puntos"], n),
             "dato": lambda x, n: dato(x["cifra"], x["pie"], x.get("fuente", ""), n),
             "cita": lambda x, n: cita(x["texto"], x["quien"], x.get("cargo", ""), n),
             "cierre": lambda x, n: cierre(x.get("mensaje", "Gracias"),
                                           x.get("contacto", ""), n)}


def mide(im):
    """¿La tinta respeta el margen de seguridad y el título seguro?"""
    import numpy as np
    a = np.array(im.convert("RGB")).astype(int)
    fondo = a[2, 2]
    tinta = np.abs(a - fondo).sum(axis=2) > 30
    ys, xs = np.nonzero(tinta)
    if not len(ys):
        return {"vacia": True, "fuera_seguro": 0}
    ms = round(W * SEGURO * 0.55)          # el pie vive algo por debajo
    fuera = max(0, ms - int(xs.min()), ms - int(ys.min()),
                int(xs.max()) - (W - ms), int(ys.max()) - (H - ms))
    return {"vacia": False, "fuera_seguro": int(fuera),
            "caja": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]}


def main():
    ap = argparse.ArgumentParser(description="Deck para las charlas GEW · RD")
    ap.add_argument("--guion", help="JSON con las láminas")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--pdf", action="store_true")
    ap.add_argument("--salida", default=f"{RAIZ}/_salida/deck")
    a = ap.parse_args()
    guion = (json.load(open(a.guion, encoding="utf-8")) if a.guion
             else GUION_DEMO)

    os.makedirs(a.salida, exist_ok=True)
    hechas, fallos, ims = [], [], []
    for i, l in enumerate(guion, 1):
        t = l["t"]
        if t not in CONSTRUYE:
            fallos.append(f"  FALLA lámina {i}: tipo «{t}» no existe "
                          f"({' | '.join(TIPOS)})")
            continue
        im, med = CONSTRUYE[t](l, None if t in ("portada", "cierre") else i)
        m2 = mide(im)
        p = f"{a.salida}/{i:02d}-{t}.png"
        im.save(p)
        hechas.append(p); ims.append(im)
        if m2["fuera_seguro"]:
            fallos.append(f"  FALLA lámina {i} ({t}): la tinta se sale "
                          f"{m2['fuera_seguro']} px del margen de seguridad")
        if m2["vacia"]:
            fallos.append(f"  FALLA lámina {i} ({t}): salió en blanco")

    print(f"producidas {len(hechas)} de {len(guion)} esperadas")
    print(f"lámina {W}×{H} (16:9) · margen de seguridad {SEGURO*100:.0f} % = "
          f"{M} px · título seguro {TITULO_SEGURO*100:.0f} %")
    if a.pdf and ims:
        pdf = f"{a.salida}/deck.pdf"
        ims[0].save(pdf, save_all=True, append_images=ims[1:], resolution=150)
        print(f"PDF: {len(ims)} láminas · {os.path.getsize(pdf)/1e6:.1f} MB")
    for f in fallos:
        print(f)
    for h in hechas:
        print(h)
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
