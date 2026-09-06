#!/usr/bin/env python3
"""
Piezas de vídeo · GEW · RD.

    frame     overlay con alfa que se superpone al vídeo: lockup, franja y
              espacio reservado para subtítulos
    lower     rótulo de nombre y cargo, también con alfa
    endcard   la tarjeta final, opaca
    guias     el frame con las zonas de interfaz marcadas, para el editor

Los frames y los lower thirds salen con canal alfa: se montan encima del vídeo
en cualquier editor o con ffmpeg:

    ffmpeg -i crudo.mp4 -i frame--vertical.png \\
      -filter_complex "[0][1]overlay=0:0" salida.mp4

Uso:
    python3 video.py --tipo endcard --formato vertical
    python3 video.py --tipo lower --nombre "Nombre Apellido" --cargo "Organización"
    python3 video.py --todos
"""
import argparse, json, os, sys
from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.abspath(__file__))
TOK = json.load(open(f"{RAIZ}/tokens/tokens.json", encoding="utf-8"))
sys.path.insert(0, RAIZ)
from campana import (fuente, marca_alto, png_alto, pin, pulso, marcas)  # noqa: E402

CARBON = TOK["color"]["campana2026"]["carbon"]["hex"]
NARANJA = TOK["color"]["campana2026"]["naranja"]["hex"]
BLANCO = "#FFFFFF"
TINTA = TOK["color"]["marca"]["carbon-wordmark"]["hex"]

# `ui` marca las zonas que la interfaz de la app tapa o usa.
#   vertical: arriba y abajo salen de la zona segura de Stories que ya usa el
#   sistema; la columna derecha son los botones de Reels — NO está documentada
#   por Meta con cifras, es una reserva prudente y va declarada como tal.
FORMATOS = {
    "vertical":   {"px": (1080, 1920), "unidad": 1180,
                   "ui": {"arriba": 269, "abajo": 250, "derecha": 250},
                   "uso": "Reels · Shorts · Stories"},
    "horizontal": {"px": (1920, 1080), "unidad": 1180,
                   "ui": {"arriba": 60, "abajo": 120, "derecha": 0},
                   "uso": "YouTube · web · pantalla de evento"},
    "cuadrado":   {"px": (1080, 1080), "unidad": 1080,
                   "ui": {"arriba": 60, "abajo": 120, "derecha": 0},
                   "uso": "feed de LinkedIn y Facebook"},
}

R = dict(margen=0.0560, franja=0.0180, logo=0.0620, sub=0.1150,
         nombre=0.0300, cargo=0.0215, endlogo=0.3400, fecha=0.0640,
         lema=0.0270, banda=0.1150, endlogos=0.0430)


def hoja(fmt):
    w, h = FORMATOS[fmt]["px"]
    u = FORMATOS[fmt]["unidad"]
    return w, h, u, {k: round(v * u) for k, v in R.items()}


def frame(fmt="vertical", subtitulos=True, guias=False, salida=None):
    """Overlay con alfa. Con guias=True marca lo que tapa la interfaz."""
    w, h, U, g = hoja(fmt)
    m, fr = g["margen"], g["franja"]
    ui = FORMATOS[fmt]["ui"]
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    med = {"tipo": "guias" if guias else "frame", "formato": fmt, "px": [w, h], "ui": ui}

    # franja naranja al filo inferior
    d.rectangle([0, h - fr, w, h], fill=NARANJA)

    # lockup GEW, dentro de la zona que la interfaz deja libre
    lock = png_alto(f"{RAIZ}/logo/gew-rd-lockup-blanco.png", g["logo"])
    im.paste(lock, (m, ui["arriba"] + m), lock)
    med["lockup"] = [lock.width, lock.height]

    y_p = ui["arriba"] + m + lock.height + round(U * 0.024)
    a_p = round(U * 0.028)
    pulso(d, m, y_p, w - m * 2, a_p)
    med["pulso"] = [m, y_p, w - m, y_p + a_p]

    # zona de subtítulos: un velo suave para que el texto quemado se lea siempre
    if subtitulos:
        alto_sub = g["sub"]
        base = h - fr - ui["abajo"]
        velo = Image.new("RGBA", (w, alto_sub), (0, 0, 0, 0))
        vd = ImageDraw.Draw(velo)
        for i in range(alto_sub):
            vd.line([(0, i), (w, i)], fill=(28, 26, 26, int(190 * (i / alto_sub) ** 1.4)))
        im.alpha_composite(velo, (0, base - alto_sub))
        med["zona_subtitulos"] = [base - alto_sub, base]

    if guias:
        rojo = (228, 17, 21, 210)
        for y in (ui["arriba"], h - fr - ui["abajo"]):
            d.line([(0, y), (w, y)], fill=rojo, width=3)
        if ui["derecha"]:
            d.line([(w - ui["derecha"], 0), (w - ui["derecha"], h)], fill=rojo, width=3)
        f = fuente("Bold", round(U * 0.020))
        d.text((m, ui["arriba"] + 10), f'INTERFAZ · {ui["arriba"]} px', font=f, fill=rojo)
        d.text((m, h - fr - ui["abajo"] - round(U * 0.030)),
               f'INTERFAZ · {ui["abajo"]} px', font=f, fill=rojo)
        if ui["derecha"]:
            d.text((w - ui["derecha"] + 10, h // 2), f'BOTONES · {ui["derecha"]} px',
                   font=f, fill=rojo)

    if salida:
        os.makedirs(os.path.dirname(salida), exist_ok=True)
        im.save(salida)
    return im, med


def lower(nombre, cargo="", fmt="vertical", salida=None):
    """Rótulo de nombre y cargo, con alfa."""
    w, h, U, g = hoja(fmt)
    m, fr = g["margen"], g["franja"]
    ui = FORMATOS[fmt]["ui"]
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f_nom = fuente("Bold", g["nombre"])
    f_car = fuente("Light", g["cargo"])
    pad_x, pad_y = round(U * 0.026), round(U * 0.020)
    an = d.textlength(nombre, font=f_nom)
    ac = d.textlength(cargo, font=f_car) if cargo else 0
    bw = round(max(an, ac)) + pad_x * 2
    bh = g["nombre"] + (round(U * 0.012) + g["cargo"] if cargo else 0) + pad_y * 2
    y0 = h - fr - ui["abajo"] - round(U * 0.075) - bh
    d.rectangle([0, y0, bw, y0 + bh], fill=CARBON)
    d.rectangle([0, y0 + bh, bw, y0 + bh + round(U * 0.007)], fill=NARANJA)
    bb = d.textbbox((0, 0), nombre, font=f_nom)
    d.text((m - bb[0] + pad_x - m, y0 + pad_y - bb[1]), nombre, font=f_nom, fill=BLANCO)
    if cargo:
        bb = d.textbbox((0, 0), cargo, font=f_car)
        d.text((pad_x - bb[0], y0 + pad_y + g["nombre"] + round(U * 0.012) - bb[1]),
               cargo, font=f_car, fill="#C6C6C6")
    if salida:
        os.makedirs(os.path.dirname(salida), exist_ok=True)
        im.save(salida)
    return im, {"tipo": "lower", "formato": fmt, "px": [w, h], "caja": [bw, bh]}


def endcard(fmt="vertical", host=None, socios=None, salida=None):
    """Tarjeta final, opaca."""
    w, h, U, g = hoja(fmt)
    m, fr = g["margen"], g["franja"]
    ui = FORMATOS[fmt]["ui"]
    host = host or f"{RAIZ}/logo/socios/enlata-wordmark.svg"
    socios = socios if socios is not None else [f"{RAIZ}/logo/socios/iavanza-lockup.svg"]
    im = Image.new("RGB", (w, h), CARBON)
    d = ImageDraw.Draw(im)
    med = {"tipo": "endcard", "formato": fmt, "px": [w, h]}

    # La banda crece un 55 %: con dos filas —partners/patrocinadores arriba y
    # cobertura debajo— la del endcard normal se quedaba corta y la segunda
    # fila se cortaba contra la franja naranja. Medido, no supuesto.
    bd = round(g["banda"] * 1.55)
    d.rectangle([0, h - fr - bd, w, h - fr], fill=BLANCO)
    d.rectangle([0, h - fr, w, h], fill=NARANJA)

    # el bloque central se centra en lo que queda libre de interfaz
    techo, suelo = ui["arriba"], h - fr - bd - ui["abajo"] // 2
    lock = png_alto(f"{RAIZ}/logo/gew-rd-lockup-blanco.png",
                    min(g["endlogo"], round((w - m * 2) / 2.928)))
    f_fecha = fuente("Light", g["fecha"])
    f_lema = fuente("Light", g["lema"])
    fecha = f'{TOK["campana"]["fechas"]}'
    alto = lock.height + round(U * 0.050) + g["fecha"] + round(U * 0.026) + g["lema"]
    y = techo + max(0, (suelo - techo - alto) // 2)
    med["bloque_top"] = y
    med["holgura"] = suelo - techo - alto

    im.paste(lock, ((w - lock.width) // 2, y), lock)
    y += lock.height + round(U * 0.050)
    for texto, f_, col in ((fecha, f_fecha, BLANCO),
                           (TOK["campana"]["tema_es"], f_lema, "#DCDCDC")):
        bb = d.textbbox((0, 0), texto, font=f_)
        d.text(((w - (bb[2] - bb[0])) // 2 - bb[0], y - bb[1]), texto, font=f_, fill=col)
        y += (g["fecha"] if f_ is f_fecha else g["lema"]) + round(U * 0.026)

    bb = d.textbbox((0, 0), TOK["campana"]["sitio"], font=f_lema)
    y_sitio = h - fr - bd - round(U * 0.085)
    d.text(((w - (bb[2] - bb[0])) // 2 - bb[0], y_sitio - bb[1]),
           TOK["campana"]["sitio"], font=f_lema, fill=NARANJA)
    # el pulso, de remate sobre la banda
    a_p = round(U * 0.022)
    pulso(d, m, h - fr - bd - round(U * 0.026) - a_p, w - m * 2, a_p)

    # los tres bloques. El endcard es pieza de cobertura: lleva IA Media.
    med_m = marcas(im, d, m, h - fr - bd + round(U * 0.0230), w - m * 2, U,
                   alto_logo=g["endlogos"], cobertura=True,
                   partners=[host] + list(socios))
    med["marcas"] = med_m
    med["marcas_desborda"] = med_m["desborda"]

    if salida:
        os.makedirs(os.path.dirname(salida), exist_ok=True)
        im.save(salida)
    return im, med


def main():
    ap = argparse.ArgumentParser(description="Frames y endcards de vídeo GEW · RD")
    ap.add_argument("--tipo", choices=["frame", "guias", "lower", "endcard"],
                    default="frame")
    ap.add_argument("--formato", choices=list(FORMATOS), default="vertical")
    ap.add_argument("--nombre", default="Nombre Apellido")
    ap.add_argument("--cargo", default="Cargo · organización")
    ap.add_argument("--sin-subtitulos", action="store_true")
    ap.add_argument("--todos", action="store_true")
    ap.add_argument("--salida", default=f"{RAIZ}/_salida/video")
    a = ap.parse_args()

    def una(tipo, fmt):
        r = f"{a.salida}/{tipo}--{fmt}.png"
        if tipo == "frame":
            _, mm = frame(fmt, not a.sin_subtitulos, False, r)
        elif tipo == "guias":
            _, mm = frame(fmt, not a.sin_subtitulos, True, r)
        elif tipo == "lower":
            _, mm = lower(a.nombre, a.cargo, fmt, r)
        else:
            _, mm = endcard(fmt, salida=r)
        return r, mm

    if a.todos:
        tipos = ["frame", "guias", "lower", "endcard"]
        esperadas = len(tipos) * len(FORMATOS)
        hechas = [una(t, f) for t in tipos for f in FORMATOS]
        print(f"producidas {len(hechas)} de {esperadas} esperadas")
        malas = [(r, mm["holgura"]) for r, mm in hechas if mm.get("holgura", 0) < 0]
        for r, hh in malas:
            print(f"  HOLGURA NEGATIVA {hh} px — {os.path.basename(r)}")
        for r, _ in hechas:
            print(r)
        if malas:
            sys.exit(f"{len(malas)} pieza(s) con el bloque fuera de sitio")
    else:
        r, mm = una(a.tipo, a.formato)
        print(json.dumps(mm, ensure_ascii=False))
        print(r)


if __name__ == "__main__":
    main()
