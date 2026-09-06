#!/usr/bin/env python3
"""
Post-evento · GEW · RD.

La pieza de después: gracias y los números. Es la que cierra el ciclo con el
aliado, y la que más se comparte porque la gente se busca en las cifras.

Dos alcances:
    actividad   los números de UNA actividad, para que el aliado la publique
    semana      el total de la campaña

⚠️ **Las cifras van como `{{N}}` mientras no existan.** Un recap con un número
inventado es peor que uno con un hueco: el hueco se rellena y el número falso
se cita en la propuesta del año siguiente. El motor cuenta cuántos huecos
quedan y lo dice.

Uso:
    python3 postevento.py --demo
    python3 postevento.py --alcance actividad --titulo "Taller" --cifras 1=48 2=6
"""
import argparse, json, os, sys

from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
from campana import (FORMATOS, TOK, activo, fuente, marcas, png_alto,  # noqa: E402
                     pulso, tinta)

C = TOK["campana"]
CARBON = TOK["color"]["campana2026"]["carbon"]["hex"]
NARANJA = TOK["color"]["campana2026"]["naranja"]["hex"]
BLANCO, GRIS = "#FFFFFF", "#B8BCC0"
HUECO = "{{N}}"

CIFRAS = {
    "actividad": [("personas", HUECO), ("organizaciones", HUECO),
                  ("horas", HUECO)],
    "semana": [("actividades", HUECO), ("personas", HUECO),
               ("organizaciones aliadas", "48"), ("provincias", HUECO)],
}
TITULOS = {"actividad": "Gracias por venir", "semana": "Así se vivió la semana"}


def pieza(alcance="semana", titulo=None, cifras=None, fmt="retrato",
          cobertura=True):
    w, h = FORMATOS[fmt]["px"]
    U = w
    m = round(U * 0.0667)
    TOP, BOT = FORMATOS[fmt]["segura"] or (0, h)
    im = Image.new("RGB", (w, h), CARBON)
    d = ImageDraw.Draw(im)

    lock = png_alto(activo("logo/gew-rd-lockup-blanco.png"), round(U * 0.089))
    im.paste(lock, (m, TOP + m), lock)
    y = TOP + m + lock.height + round(U * 0.030)
    pulso(d, m, y, w - m * 2, round(U * 0.034))
    y += round(U * 0.034) + round(U * 0.070)

    tit = titulo or TITULOS[alcance]
    cap = round(U * 0.082)
    while cap > 24:
        f_t = fuente("Bold", cap)
        if d.textlength(tit, font=f_t) <= w - m * 2:
            break
        cap -= 3
    b = tinta(d, (m, y), tit, f_t, fill=BLANCO)
    y = b[3] + round(U * 0.055)

    datos = cifras or CIFRAS[alcance]
    huecos = 0
    # las cifras se ajustan al hueco que queda hasta la banda. Con cuatro y el
    # cap fijo, la última se metía dentro: cabía en retrato y no en cuadrado.
    alto_banda = round(U * (0.200 if cobertura else 0.140))
    suelo = BOT - m - alto_banda - round(U * 0.030)
    cap_v = round(U * 0.105)
    while cap_v > 26:
        paso = round(cap_v * 1.30)
        if y + paso * len(datos) <= suelo:
            break
        cap_v -= 3
    for etq, val in datos:
        v = str(val)
        if HUECO in v:
            huecos += 1
        f_v = fuente("Black", cap_v)
        bv = tinta(d, (m, y), v, f_v, fill=NARANJA)
        f_e = fuente("Light", round(cap_v * 0.33))
        tinta(d, (bv[2] + round(U * 0.028), y + round(cap_v * 0.42)), etq, f_e,
              fill=GRIS)
        y += round(cap_v * 1.30)

    med_m = marcas(im, d, m, BOT - m - alto_banda, w - m * 2, U, oscuro=True,
                   cobertura=cobertura)
    return im, {"alcance": alcance, "formato": fmt, "cifras": len(datos),
                "huecos": huecos, "cap_titular": cap, "cap_cifra": cap_v,
                "marcas_desborda": med_m["desborda"],
                "base_texto": y, "suelo": BOT - m - alto_banda}


def main():
    ap = argparse.ArgumentParser(description="Pieza de post-evento GEW · RD")
    ap.add_argument("--alcance", choices=sorted(CIFRAS), default="semana")
    ap.add_argument("--titulo")
    ap.add_argument("--formato", choices=["retrato", "cuadrado", "historia"],
                    default="retrato")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--salida", default=f"{RAIZ}/_salida/postevento")
    a = ap.parse_args()

    os.makedirs(a.salida, exist_ok=True)
    trabajos = ([(al, f) for al in sorted(CIFRAS)
                 for f in ("retrato", "cuadrado", "historia")] if a.demo
                else [(a.alcance, a.formato)])
    hechas, fallos, huecos = [], [], 0
    print(f"{'pieza':26} {'cifras':>7} {'huecos':>7} {'texto acaba':>12} "
          f"{'suelo':>7} {'banda':>7}")
    for al, f in trabajos:
        im, med = pieza(al, a.titulo, None, f)
        p = f"{a.salida}/{al}--{f}.png"
        im.save(p); hechas.append(p); huecos += med["huecos"]
        print(f"  {al+'/'+f:24} {med['cifras']:7} {med['huecos']:7} "
              f"{med['base_texto']:12} {med['suelo']:7} "
              f"{med['marcas_desborda']:7}")
        if med["base_texto"] > med["suelo"]:
            fallos.append(f"  FALLA {al}/{f}: el texto acaba en "
                          f"{med['base_texto']} y la banda empieza en "
                          f"{med['suelo']}")
        if med["marcas_desborda"]:
            fallos.append(f"  FALLA {al}/{f}: la banda desborda "
                          f"{med['marcas_desborda']} px")

    print(f"\nproducidas {len(hechas)} de {len(trabajos)} esperadas")
    print(f"⚠️ {huecos} cifra(s) sin rellenar en total. Salen del formulario de "
          f"actividades y de las hojas de registro; no se inventan.")
    for x in fallos:
        print(x)
    for h in hechas:
        print(h)
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
