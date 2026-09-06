#!/usr/bin/env python3
"""
Piezas de perfil · GEW · RD.

Las tres que sí tienen ficha OFICIAL publicada por la plataforma, a diferencia
de los formatos de campaña —Meta no publica especificaciones para las
publicaciones orgánicas de Instagram, así que el 1080×1350 que usa todo el
mundo es consenso de terceros, no norma—.

    yt-portada   2560×1440   sólo 1546×423 se ve en TODOS los dispositivos
                             support.google.com/youtube/answer/2972003
    li-portada   1512×256    tope 3 MB · linkedin.com/help/linkedin/answer/a563309
    li-logo        400×400   mínimo aceptado 268×268 · tope 3 MB

No son piezas de campaña: se ponen una vez y se quedan. Por eso no pasan por
`pieza()` ni por la retícula de campaña — cada una tiene su composición.

Uso:
    python3 perfil.py --todas
    python3 perfil.py --tipo yt-portada
"""
import argparse, os, sys
from PIL import Image, ImageDraw

from campana import (FORMATOS, RAIZ, TOK, fuente, png_alto, pulso, repartir,
                     tinta)

CARBON = TOK["color"]["campana2026"]["carbon"]["hex"]
NARANJA = TOK["color"]["campana2026"]["naranja"]["hex"]
BLANCO = "#FFFFFF"
BARRA = TOK["color"]["barra"]["hex"]
FECHAS = TOK["campana"]["fechas"]
LEMA = TOK["campana"]["tema_es"]
SITIO = TOK["campana"]["sitio"]


def barra_multicolor(d, x, y, ancho, alto):
    """El pulso a sangre en el pie. Antes eran los 6 tramos iguales de GEN;
    desde que el pulso es el elemento del movimiento (Piero, 5-sep-2026) manda
    él, que además sale de la geometría medida del propio anillo."""
    pulso(d, x, y, ancho, alto)


def encajar(d, texto, peso, cap, ancho_max, lineas_max=2):
    """Baja el cap hasta que el texto quepa en `ancho_max`, probando de 1 a
    `lineas_max` líneas. Mide con la tinta real, no con la caja de fuente.

    Devuelve (font, [líneas], cap_usado). Nunca estima: si no cabe, encoge."""
    pal = texto.split()
    while cap >= 10:
        f = fuente(peso, cap)
        anchos = [d.textlength(w, font=f) for w in pal]
        esp = d.textlength(" ", font=f)
        for k in range(1, min(lineas_max, len(pal)) + 1):
            r = repartir([(w, False) for w in pal], k, anchos, esp)
            if not r:
                continue
            # `repartir` devuelve líneas de tramos (texto, destacado); aquí no
            # hay destacados, así que cada línea es un solo tramo.
            lineas = ["".join(t for t, _ in ln) for ln in r]
            if max(d.textlength(ln, font=f) for ln in lineas) <= ancho_max:
                return f, lineas, cap
        cap -= 2
    return fuente(peso, 10), [texto], 10


def _lienzo(fmt, fondo=CARBON):
    w, h = FORMATOS[fmt]["px"]
    im = Image.new("RGB", (w, h), fondo)
    return im, ImageDraw.Draw(im), w, h


# ── 1 · portada de canal de YouTube ────────────────────────────────────
def yt_portada():
    """2560×1440. Todo lo que importa vive dentro de los 1546×423 centrados:
    es la única franja que YouTube garantiza visible en móvil, tele y web."""
    fmt = "yt-portada"
    im, d, W, H = _lienzo(fmt)
    sx0, sx1 = FORMATOS[fmt]["segura_x"]
    sy0, sy1 = FORMATOS[fmt]["segura"]
    alto_seg, ancho_seg = sy1 - sy0, sx1 - sx0

    # fuera de la zona segura sólo va fondo y la barra a sangre: si YouTube la
    # recorta no se pierde nada.
    barra_multicolor(d, 0, H - 24, W, 24)

    lock = png_alto(f"{RAIZ}/logo/gew-rd-lockup-blanco.png", round(alto_seg * 0.55))
    gap = round(alto_seg * 0.15)
    hueco = ancho_seg - lock.width - gap          # lo que le queda al texto
    im.paste(lock, (sx0, sy0 + (alto_seg - lock.height) // 2), lock)

    x = sx0 + lock.width + gap
    f_lema, lineas, _ = encajar(d, LEMA, "Bold", round(alto_seg * 0.15), hueco, 2)
    f_fecha, l_fecha, _ = encajar(d, FECHAS, "Light", round(alto_seg * 0.095), hueco, 1)
    f_sitio = fuente("Bold", round(alto_seg * 0.070))

    paso = round(f_lema.size * 0.92)
    alto_txt = paso * len(lineas) + round(alto_seg * 0.10) + f_fecha.size \
        + round(alto_seg * 0.09) + f_sitio.size
    y = sy0 + max(0, (alto_seg - alto_txt) // 2)
    for ln in lineas:
        tinta(d, (x, y), ln, f_lema, fill=BLANCO)
        y += paso
    y += round(alto_seg * 0.06)
    b = tinta(d, (x, y), l_fecha[0], f_fecha, fill=BLANCO)
    tinta(d, (x, b[3] + round(alto_seg * 0.07)), SITIO.upper(), f_sitio, fill=NARANJA)
    return im, fmt


# ── 2 · portada de página de LinkedIn ──────────────────────────────────
def li_portada():
    """1512×256. Una banda muy baja: el lockup manda y el texto acompaña."""
    fmt = "li-portada"
    im, d, W, H = _lienzo(fmt)
    barra_multicolor(d, 0, H - 10, W, 10)

    mg = 56
    lock = png_alto(f"{RAIZ}/logo/gew-rd-lockup-blanco.png", round(H * 0.56))
    im.paste(lock, (mg, (H - 10 - lock.height) // 2), lock)

    x = mg + lock.width + 48
    hueco = W - x - mg
    f_lema, lineas, _ = encajar(d, LEMA, "Bold", 40, hueco, 1)
    f_pie, l_pie, _ = encajar(d, f"{FECHAS} · {SITIO}", "Light", 27, hueco, 1)
    alto_txt = f_lema.size + 14 + f_pie.size
    y = (H - 10 - alto_txt) // 2
    b = tinta(d, (x, y), lineas[0], f_lema, fill=BLANCO)
    tinta(d, (x, b[3] + 10), l_pie[0], f_pie, fill=NARANJA)
    return im, fmt


# ── 3 · logo de página de LinkedIn ─────────────────────────────────────
def li_logo():
    """400×400. En el feed se ve a ~60 px: a ese tamaño el lockup de cuatro
    líneas no se lee y lo que se reconoce es el anillo. Es la misma regla de
    MIN_LOCKUP que ya usa el sello de las piezas."""
    fmt = "li-logo"
    im, d, W, H = _lienzo(fmt)
    anillo = png_alto(f"{RAIZ}/logo/gew-rd-anillo.png", round(H * 0.60))
    im.paste(anillo, ((W - anillo.width) // 2, round(H * 0.14)), anillo)

    f = fuente("Bold", 34)
    b = d.textbbox((0, 0), "GEW · RD", font=f)
    tinta(d, ((W - (b[2] - b[0])) // 2 - b[0], round(H * 0.79)), "GEW · RD", f,
          fill=BLANCO)
    return im, fmt


# nombre de la pieza → (función, formato del lienzo). El sufijo `--<formato>`
# del fichero es lo que la auditoría usa para saber qué reglas aplicar.
TIPOS = {"portada-canal": yt_portada,
         "portada-pagina": li_portada,
         "logo-pagina": li_logo}


def medir(im, fmt, ruta):
    """Devuelve las líneas del informe de esta pieza."""
    out = []
    esperado = tuple(FORMATOS[fmt]["px"])
    out.append(("lienzo", f"{im.width}x{im.height}",
                f"{esperado[0]}x{esperado[1]}", (im.width, im.height) == esperado))
    mb = os.path.getsize(ruta) / 1e6
    tope = FORMATOS[fmt].get("tope_mb")
    if tope:
        out.append(("peso", f"{mb:.2f} MB", f"≤ {tope} MB", mb <= tope))
    else:
        out.append(("peso", f"{mb:.2f} MB", "sin tope publicado", True))

    sx = FORMATOS[fmt].get("segura_x")
    sy = FORMATOS[fmt].get("segura")
    if sx and sy:
        # nada de tinta distinta del fondo fuera de la zona segura, salvo la
        # barra a sangre del pie, que se recorta sin pérdida
        import numpy as np
        a = np.array(im.convert("RGB")).astype(int)
        fondo = np.array([int(CARBON[i:i + 2], 16) for i in (1, 3, 5)])
        dif = np.abs(a - fondo).sum(axis=2) > 30
        dif[im.height - 24:, :] = False          # la barra del pie
        dentro = dif[sy[0]:sy[1], sx[0]:sx[1]].sum()
        fuera = dif.sum() - dentro
        out.append(("contenido fuera de la zona segura", f"{fuera} px",
                    "0 px (la barra del pie no cuenta)", fuera == 0))
        out.append(("zona segura usada", f"{sx[1]-sx[0]}x{sy[1]-sy[0]}",
                    "1546x423", (sx[1] - sx[0], sy[1] - sy[0]) == (1546, 423)))
    return out


def main():
    ap = argparse.ArgumentParser(description="Piezas de perfil GEW · RD")
    ap.add_argument("--tipo", choices=sorted(TIPOS))
    ap.add_argument("--todas", action="store_true")
    ap.add_argument("--salida", default=f"{RAIZ}/_salida/perfil")
    a = ap.parse_args()
    if not a.tipo and not a.todas:
        a.todas = True

    os.makedirs(a.salida, exist_ok=True)
    tipos = sorted(TIPOS) if a.todas else [a.tipo]
    hechas, fallos = [], []
    for t in tipos:
        im, fmt = TIPOS[t]()
        ruta = f"{a.salida}/{t}--{fmt}.png"
        im.save(ruta)
        hechas.append(ruta)
        for regla, med, umbral, ok in medir(im, fmt, ruta):
            if not ok:
                fallos.append(f"  FALLA {t} · {regla}: {med} (umbral {umbral})")
            else:
                print(f"  {t:12} {regla:36} {med:>12}  (umbral {umbral})")

    print(f"producidas {len(hechas)} de {len(tipos)} esperadas")
    for f in fallos:
        print(f)
    for h in hechas:
        print(h)
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
