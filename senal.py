#!/usr/bin/env python3
"""
Señalética de sede · GEW · RD.

Lo que hace falta el día de la actividad y no estaba: direccional de pasillo,
identificación de sala, rótulo de la mesa de registro, cartel de wifi y el
horario para pegar en la puerta.

⭐ LO QUE HACE DISTINTO A ESTE MOTOR: **declara a qué distancia se lee cada
pieza**. La regla de industria es **2,5 cm de altura de letra por cada 3 m de
distancia** —ADA la usa de base— y aquí no se estima: se mide la tinta real del
titular con `textbbox`, se convierte a centímetros con el dpi de la pieza y se
imprime la distancia que sale. Si un cartel no se lee desde donde tiene que
leerse, el motor lo dice antes de mandarlo a imprimir.

⚠️ La proporción 1:10 está repetida en toda la industria, pero no encontré el
documento original de SEGD accesible: va como estándar de industria, no como
norma citada.

Uso:
    python3 senal.py --todas
    python3 senal.py --tipo sala --texto "Taller de finanzas" --detalle "Aula 204"
"""
import argparse, json, os, sys

from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
from campana import (TOK, activo, fuente, marca_alto, png_alto, pin,  # noqa: E402
                     pulso, trocear)

CARBON = TOK["color"]["campana2026"]["carbon"]["hex"]
NARANJA = TOK["color"]["campana2026"]["naranja"]["hex"]
BLANCO, GRIS = "#FFFFFF", "#8A8F94"

# La regla: 1 pulgada (2,54 cm) de alto de letra por cada 10 pies (3,05 m).
CM_POR_METRO = 2.54 / 3.048


def distancia_de_lectura(alto_cm):
    """A cuántos metros se lee una letra de este alto. La medida que manda."""
    return alto_cm / CM_POR_METRO


def alto_para(metros):
    """Qué alto de letra hace falta para leerse a esta distancia."""
    return metros * CM_POR_METRO


#   tipo: (ancho_cm, alto_cm, dpi, sangrado_mm, distancia objetivo en m)
PIEZAS = {
    "direccional": (42.0, 59.4, 150, 3, 8.0),    # A2 vertical: en A3 no
                                                 # llegaba a los 8 m
    "sala":        (42.0, 29.7, 150, 3, 5.0),    # A3 apaisado: en A4 el
                                                 # nombre no llegaba a 5 m
    "registro":    (29.7, 42.0, 150, 3, 3.0),    # A3 vertical
    "wifi":        (14.0, 14.0, 300, 3, 1.0),
    "puerta":      (21.0, 29.7, 150, 3, 2.0),    # A4 vertical, el horario
}
FLECHAS = {"izquierda": 180, "derecha": 0, "arriba": 90, "abajo": 270}


def px(cm, dpi):
    return round(cm / 2.54 * dpi)


def cm(px_, dpi):
    return px_ / dpi * 2.54


def lienzo(tipo):
    a, al, dpi, sang_mm, dist = PIEZAS[tipo]
    s = round(sang_mm / 10 / 2.54 * dpi)
    return px(a, dpi) + s * 2, px(al, dpi) + s * 2, s, dpi, a, al, dist


def marcas_corte(d, w, h, s):
    """Las marcas van FUERA del área de recorte, nunca encima."""
    lg = max(6, s)
    for x in (s, w - s):
        d.line([(x, 0), (x, max(0, s - 2))], fill="#999999", width=2)
        d.line([(x, h - max(0, s - 2)), (x, h)], fill="#999999", width=2)
    for y in (s, h - s):
        d.line([(0, y), (max(0, s - 2), y)], fill="#999999", width=2)
        d.line([(w - max(0, s - 2), y), (w, y)], fill="#999999", width=2)


def flecha(d, cx, cy, largo, grosor, color, grados=0):
    """Una flecha maciza, dibujada por puntos: no depende de ningún glifo."""
    import math
    r = math.radians(grados)
    def rot(x, y):
        return (cx + x * math.cos(r) - y * math.sin(r),
                cy + x * math.sin(r) + y * math.cos(r))
    L, g = largo / 2, grosor / 2
    cab = largo * 0.42
    pts = [(-L, -g), (L - cab, -g), (L - cab, -grosor), (L, 0),
           (L - cab, grosor), (L - cab, g), (-L, g)]
    d.polygon([rot(x, y) for x, y in pts], fill=color)


def _cabecera(im, d, s, w, dpi, U, oscuro=True):
    """Lockup arriba y el pulso debajo. Igual en las cinco piezas."""
    # el lockup escala con la pieza: 2,2 cm fijos se perdían en un A2
    m = px(1.6, dpi)
    alto_l = round(w * 0.075)
    lock = png_alto(activo("logo/gew-rd-lockup-blanco.png" if oscuro
                           else "logo/gew-rd-lockup-color.png"), alto_l)
    im.paste(lock, (s + m, s + m), lock)
    y = s + m + lock.height + px(0.5, dpi)
    pulso(d, s + m, y, w - (s + m) * 2, px(0.55, dpi))
    return y + px(0.55, dpi)


def _cabe(d, texto, peso, cap, ancho):
    """Baja el cap hasta que el texto quepa. El titular ya se ajustaba; el
    detalle no, y con otra tipografía se salía por los dos lados del cartel."""
    while cap > 8:
        f = fuente(peso, cap)
        if d.textlength(texto, font=f) <= ancho:
            return f
        cap -= 2
    return fuente(peso, 8)


def _titular(d, x, y, texto, ancho, dpi, dist_m, color=BLANCO, peso="Bold",
             alto_max=None):
    """Escribe el titular al mayor tamaño que quepa **en los dos ejes**, y
    devuelve el alto de letra REAL en cm — que es lo que decide a qué distancia
    se lee.

    La primera versión sólo miraba el ancho y el cartel de sala se comía su
    propio detalle por abajo. Que quepa en horizontal no es que quepa."""
    cap = px(alto_para(dist_m) * 1.15, dpi)     # de partida, con holgura
    while cap > 8:
        f = fuente(peso, cap)
        pal, lineas, act = texto.split(), [], ""
        for p in pal:
            t = (act + " " + p).strip()
            if d.textlength(t, font=f) <= ancho:
                act = t
            else:
                if act:
                    lineas.append(act)
                act = p
        if act:
            lineas.append(act)
        cabe_ancho = max((d.textlength(l, font=f) for l in lineas),
                         default=0) <= ancho
        cabe_alto = alto_max is None or round(cap * 1.28) * len(lineas) <= alto_max
        if cabe_ancho and cabe_alto:
            break
        cap -= 4
    f = fuente(peso, cap)
    paso = round(cap * 1.28)
    alto_real = 0
    for i, l in enumerate(lineas):
        b = d.textbbox((x, y + i * paso), l, font=f)
        d.text((x - (b[0] - x), y + i * paso - (b[1] - (y + i * paso))), l,
               font=f, fill=color)
        alto_real = max(alto_real, b[3] - b[1])
    # el alto de letra que manda es el de una MAYÚSCULA, no el de la línea
    bM = d.textbbox((0, 0), "M", font=f)
    return (y + paso * len(lineas), cm(bM[3] - bM[1], dpi), len(lineas))


def pieza(tipo, texto, detalle="", sentido="derecha", salida=None):
    w, h, s, dpi, a_cm, al_cm, dist = lienzo(tipo)
    oscuro = tipo != "wifi"
    im = Image.new("RGB", (w, h), CARBON if oscuro else BLANCO)
    d = ImageDraw.Draw(im)
    m = px(1.6, dpi)
    U = w
    y = _cabecera(im, d, s, w, dpi, U, oscuro)
    util = w - (s + m) * 2
    med = {"tipo": tipo, "cm": [a_cm, al_cm], "dpi": dpi, "px": [w, h],
           "distancia_objetivo_m": dist}

    if tipo == "direccional":
        y += px(2.2, dpi)
        y2, alto_letra, n = _titular(d, s + m, y, texto, util, dpi, dist,
                                     alto_max=(h - s - m - y) * 0.34)
        flecha(d, w // 2, y2 + px(5.0, dpi), util * 0.62, px(1.6, dpi),
               NARANJA, FLECHAS[sentido])
        if detalle:
            f = _cabe(d, detalle, "Light", px(alto_para(dist) * 0.42, dpi), util)
            b = d.textbbox((0, 0), detalle, font=f)
            d.text(((w - (b[2] - b[0])) // 2 - b[0], y2 + px(9.0, dpi) - b[1]),
                   detalle, font=f, fill="#DCDCDC")
    elif tipo == "sala":
        y += px(1.4, dpi)
        y2, alto_letra, n = _titular(d, s + m, y, texto, util, dpi, dist,
                                     alto_max=(h - s - m - y) * 0.62)
        if detalle:
            f = _cabe(d, detalle, "Light", px(alto_para(dist) * 0.40, dpi), util)
            d.text((s + m, y2 + px(0.6, dpi)), detalle, font=f, fill=NARANJA)
    elif tipo == "registro":
        y += px(3.5, dpi)
        y2, alto_letra, n = _titular(d, s + m, y, texto or "REGISTRO", util,
                                     dpi, dist, alto_max=(h - s - m - y) * 0.55)
        if detalle:
            f = _cabe(d, detalle, "Light", px(alto_para(dist) * 0.38, dpi), util)
            d.text((s + m, y2 + px(1.2, dpi)), detalle, font=f, fill="#DCDCDC")
    elif tipo == "wifi":
        y += px(0.8, dpi)
        y2, alto_letra, n = _titular(d, s + m, y, "WIFI", util, dpi, dist,
                                     color=CARBON, alto_max=(h - s - m - y) * 0.34)
        f = fuente("Bold", px(0.75, dpi))
        for i, l in enumerate((texto or "red", detalle or "clave")):
            d.text((s + m, y2 + px(0.5 + i * 1.25, dpi)), l, font=f, fill=NARANJA)
        alto_letra = cm(d.textbbox((0, 0), "M", font=f)[3], dpi)
    else:                                            # puerta · el horario
        y += px(1.2, dpi)
        y2, alto_letra, n = _titular(d, s + m, y, texto or "Hoy aquí", util,
                                     dpi, dist, alto_max=(h - s - m - y) * 0.28)
        f = fuente("Light", px(0.62, dpi))
        for i, l in enumerate((detalle or "").split("\n")[:8]):
            d.text((s + m, y2 + px(0.9 + i * 1.05, dpi)), l, font=f,
                   fill="#DCDCDC")

    d.rectangle([0, h - s - px(0.6, dpi), w, h - s], fill=NARANJA)
    marcas_corte(d, w, h, s)

    # ⭐ La comprobación que este motor no tenía y todos los demás sí: que la
    # tinta quepa. Medir la distancia de lectura no sirve de nada si el cartel
    # se come su propio detalle por abajo — pasó con el de sala.
    import numpy as np
    fondo = np.array([int((CARBON if oscuro else BLANCO)[i:i + 2], 16)
                      for i in (1, 3, 5)])
    arr = np.array(im.convert("RGB")).astype(int)
    tinta = np.abs(arr - fondo).sum(axis=2) > 30
    tinta[:s, :] = False; tinta[h - s:, :] = False       # marcas de corte
    tinta[:, :s] = False; tinta[:, w - s:] = False
    # la franja naranja del pie va A SANGRE por diseño: no es contenido que se
    # sale, es el borde de la pieza. Sin excluirla, las cinco daban 30 px.
    tinta[h - s - px(0.6, dpi) - 2:, :] = False
    ys, xs = np.nonzero(tinta)
    seg = px(0.5, dpi)                                   # 5 mm desde el corte
    fuera = 0
    if len(ys):
        fuera = max(0, (s + seg) - int(xs.min()), (s + seg) - int(ys.min()),
                    int(xs.max()) - (w - s - seg), int(ys.max()) - (h - s - seg))
    med["fuera_de_zona_segura_px"] = int(fuera)
    med["cabe"] = fuera == 0

    med["alto_letra_cm"] = round(alto_letra, 2)
    med["se_lee_a_m"] = round(distancia_de_lectura(alto_letra), 1)
    med["cumple"] = med["se_lee_a_m"] >= dist
    med["lineas"] = n
    if salida:
        os.makedirs(os.path.dirname(salida), exist_ok=True)
        im.save(salida, dpi=(dpi, dpi))
    return im, med


DEMO = {
    "direccional": ("TALLER", "Segundo piso · 6:00 pm", "derecha"),
    "sala": ("Taller de finanzas", "Aula 204 · 6:00 pm", "derecha"),
    "registro": ("REGISTRO", "Ten a mano tu correo de confirmación", "derecha"),
    "wifi": ("GEW-Invitados", "prospera2026", "derecha"),
    "puerta": ("Hoy aquí", "9:00  Validación de ideas\n11:00  Mentoría abierta\n"
               "14:00  Taller de finanzas\n18:00  Cierre y networking", "derecha"),
}


def main():
    ap = argparse.ArgumentParser(description="Señalética de sede GEW · RD")
    ap.add_argument("--tipo", choices=sorted(PIEZAS))
    ap.add_argument("--texto", default="")
    ap.add_argument("--detalle", default="")
    ap.add_argument("--sentido", choices=sorted(FLECHAS), default="derecha")
    ap.add_argument("--todas", action="store_true")
    ap.add_argument("--salida", default=f"{RAIZ}/_salida/senal")
    a = ap.parse_args()
    if not a.tipo and not a.todas:
        a.todas = True

    tipos = sorted(PIEZAS) if a.todas else [a.tipo]
    hechas, fallos = [], []
    print(f"{'pieza':13} {'cm':>12} {'dpi':>4} {'letra':>7} {'se lee a':>9} "
          f"{'objetivo':>9} {'cabe':>6}")
    for t in tipos:
        txt, det, sen = DEMO[t] if a.todas else (a.texto or DEMO[t][0],
                                                 a.detalle or DEMO[t][1],
                                                 a.sentido)
        p = f"{a.salida}/{t}.png"
        _, med = pieza(t, txt, det, sen, salida=p)
        hechas.append(p)
        marca = "" if med["cumple"] else "  ← NO SE LEE DESDE DONDE DEBE"
        print(f"  {t:11} {med['cm'][0]:5.1f}x{med['cm'][1]:<5.1f} {med['dpi']:4} "
              f"{med['alto_letra_cm']:6.2f}cm {med['se_lee_a_m']:8.1f}m "
              f"{med['distancia_objetivo_m']:8.1f}m "
              f"{('sí' if med['cabe'] else str(med['fuera_de_zona_segura_px'])+'px'):>6}"
              f"{marca}")
        if not med["cumple"]:
            fallos.append(f"  FALLA {t}: se lee a {med['se_lee_a_m']} m y "
                          f"tiene que leerse a {med['distancia_objetivo_m']} m")
        if not med["cabe"]:
            fallos.append(f"  FALLA {t}: la tinta se sale "
                          f"{med['fuera_de_zona_segura_px']} px de la zona segura")

    print(f"\nproducidas {len(hechas)} de {len(tipos)} esperadas")
    print(f"regla: {CM_POR_METRO:.2f} cm de alto de letra por cada metro de "
          f"distancia (2,54 cm por 3,05 m — estándar de industria)")
    for f in fallos:
        print(f)
    for h in hechas:
        print(h)
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
