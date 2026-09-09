#!/usr/bin/env python3
"""
Kit de vídeo · GEW · RD.

El sistema hacía frames; esto los pone en movimiento. Tres piezas, en vertical
y en horizontal:

    apertura    3 s · el pulso barre y entra el lockup
    cuenta      4 s · la cifra de la cuenta atrás, con el pulso creciendo
    endcard     5 s · la tarjeta de cierre, con el pulso animándose

Los frames se componen con PIL —el mismo motor que las piezas— y se montan con
ffmpeg. Se hace así, y no con los filtros de ffmpeg, porque la tipografía, la
retícula y el pulso ya están resueltos en Python: reescribirlos en `drawtext`
sería tener dos sistemas que se separan.

**Sin audio, a propósito.** Una pieza de campaña se ve en silencio en el 80 %
de los casos y la música se pone al montar. Además, el −14 LUFS que se cita
para YouTube no tiene página oficial de Google: es cifra de terceros, y no
quiero fijarla en el motor.

Lo que sí está publicado y se respeta: **H.264 High Profile, MP4, yuv420p**,
que es lo que pide YouTube; y **≥540×960 con ≥516 kbps**, que es el mínimo
documentado de TikTok. Meta no publica el bitrate de Reels.

Uso:
    python3 movimiento_video.py --todos
    python3 movimiento_video.py --tipo cuenta --dias 3 --formato vertical
"""
import argparse, json, math, os, shutil, subprocess, sys

from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
from video_tokens import banda as _banda  # noqa: E402
from campana import (LOGO_COBERTURA, PARTNERS, ROTULOS, SEGMENTOS,  # noqa: E402
                     TOK, activo, fuente, marca_alto, png_alto, pulso, tinta)
import pulso_musica as PM  # noqa: E402
import animacion as AN  # noqa: E402
import zonas as ZN  # noqa: E402

C = TOK["campana"]
CARBON = TOK["color"]["campana2026"]["carbon"]["hex"]
NARANJA = TOK["color"]["campana2026"]["naranja"]["hex"]
BLANCO = "#FFFFFF"
FPS = 30
FORMATOS = {"vertical": (1080, 1920), "horizontal": (1920, 1080),
            "cuadrado": (1080, 1080), "retrato": (1080, 1350)}
# La zona que la interfaz de Stories tapa. Es la misma que usa el resto del
# sistema, y sigue siendo criterio nuestro: Meta no publica las cifras.
# Desde `tokens/video.json`, la misma fuente que `video.py` y `campana.py`.
# Antes este fichero declaraba sólo el vertical y caía a un respaldo del 4,5 %
# del alto para horizontal y cuadrado: 49 px, contra los 60 que declaraba
# `video.py` para esos mismos formatos. Dos números para lo mismo.
SEGURA = {f: _banda(f) for f in FORMATOS}
# Las tres duraciones caen en TIEMPO ENTERO a 100 BPM, decidido por Piero el
# 6-sep-2026. Antes, `cuenta` duraba 4,0 s (6,667 tiempos) y `endcard` 5,0 s
# (8,333): el corte caía a mitad de tiempo y se iba a notar en cuanto alguien
# les pusiera música debajo.
#   apertura  3,0 s =  5 tiempos =  90 fotogramas
#   cuenta    4,2 s =  7 tiempos = 126 fotogramas
#   endcard   4,8 s =  8 tiempos = 144 fotogramas — y es exactamente un bucle
#             entero del pulso, así que el endcard contiene el pulso completo
#             sin repetir ni cortar a medias.
DURACION = {"apertura": 3.0, "cuenta": 4.2, "endcard": 4.8}
# Las tres piezas VAN SOLAS —nadie habla encima— así que su modo es `espectro`
# por la regla que cerró Piero el 6-sep-2026. Si alguna se monta debajo de una
# locución, se pide `--papel voz` y sale en `latido`.
PAPEL = "solo"
# YouTube publica 8 Mbps para 1080p SDR; TikTok documenta 516 kbps como
# mínimo. 6 Mbps queda cómodo entre los dos. Meta no publica el suyo.
BITRATE_KBPS = 6000


# La curva de siempre, que ahora vive en el catálogo compartido con su nombre.
# Es la misma fórmula: no se mueve nada de lo ya aprobado, sólo deja de estar
# suelta dentro de este fichero.
suave = AN.frena


# Cómo entra y cómo SALE cada pieza. Hasta el 6-sep-2026 esta tabla no existía
# y ninguna pieza salía: medido, al último fotograma les quedaba entre el 91,6 %
# y el 98,7 % de la tinta. Todas se cortaban en seco.
# El endcard `mantiene` a propósito —va al final del todo y debe quedarse—, pero
# ahora eso se PIDE, no es lo único posible.
GUION = {
    "apertura": {"entra": "sube", "sale": "apaga", "dur_sale": "2c"},
    "cuenta": {"entra": "crece", "sale": "encoge", "dur_sale": "2c"},
    "endcard": {"entra": "aparece", "sale": "mantiene", "dur_sale": "2c"},
}


# Cada rótulo, cuándo aparece y cuándo se lo lleva la salida. Sirve para
# comprobar que da tiempo a leerlo — 15 caracteres por segundo, que es la cifra
# de las BBC Subtitle Guidelines, la más conservadora de las dos que hay.
def rotulos(tipo, dias=3):
    d = DURACION[tipo]
    fin = d - 0.6                       # la salida se lleva la última corchea
    if tipo == "apertura":
        return [(C["fechas"], 0.90, fin)]
    if tipo == "cuenta":
        pie = "días" if isinstance(dias, int) and dias != 1 else "día"
        return [(str(dias), 0.0, fin), (pie, 0.0, fin), (C["tema_es"], 0.0, fin)]
    return [(C["fechas"], 1.30, d), (C["sitio"], 1.30, d)]


# Qué tiene que quedar en pantalla al último fotograma, según la salida. Es la
# prueba de que la salida hizo lo suyo, y se comprueba sobre el MP4 entregado.
ESPERADO_AL_FINAL = {
    "apaga":    {"dice": "la pantalla vacía (<25 %)", "ok": lambda q: q < 25},
    "baja":     {"dice": "la pantalla vacía (<25 %)", "ok": lambda q: q < 25},
    "encoge":   {"dice": "la pantalla vacía (<25 %)", "ok": lambda q: q < 25},
    # `cierra` no se mide por la tinta que queda sino por el fondo que NO
    # queda: una cortina que cierra deja 0 % de fondo a la vista.
    "cierra":   {"dice": "la pantalla tapada del todo (0 % de fondo)",
                 "ok": lambda q: q > 150, "fondo": 0.5},
    "mantiene": {"dice": "la pieza entera en pantalla (>75 %)",
                 "ok": lambda q: q > 75},
}


def aplica_salida(im, nombre, s, PU=None, fondo=None):
    """Aplica la salida al fotograma ya compuesto. Se hace aquí y no dentro de
    cada composición para que valga igual en las tres piezas y en las que
    vengan: una salida es qué le pasa a la pieza entera, no a un bloque."""
    if nombre == "mantiene" or s >= 0.999:
        return im
    w, h = im.size
    base = Image.new("RGB", (w, h), fondo or CARBON)
    if nombre == "apaga":
        return Image.blend(base, im, s)
    if nombre == "baja":
        d = round(h * 0.10 * (1 - s))
        cap = base.copy()
        cap.paste(im.crop((0, 0, w, h - d)), (0, d))
        return Image.blend(base, cap, s)
    if nombre == "encoge":
        k = 0.80 + 0.20 * s
        nw, nh = max(1, round(w * k)), max(1, round(h * k))
        cap = base.copy()
        cap.paste(im.resize((nw, nh), Image.LANCZOS),
                  ((w - nw) // 2, (h - nh) // 2))
        return Image.blend(base, cap, s)
    if nombre == "cierra":
        # El pulso crece desde abajo hasta TAPAR la pieza.
        # ⚠️ La primera versión llamaba a `PM.dibuja`, que respeta el aire
        # entre barras (62 % del paso) y la altura de cada segmento. Al final
        # quedaban huecos de carbón y se veía el contenido detrás: medido,
        # cerraba al 460 % de tinta pero sin cerrar. Aquí las barras se
        # ensanchan hasta juntarse y todas suben hasta el techo, así que al
        # último fotograma la pantalla es una cortina llena.
        av = 1.0 - s                      # 0 al empezar, 1 al cerrar
        cap = im.copy()
        d = ImageDraw.Draw(cap)
        n = len(PM.SEGMENTOS)
        paso = w / n
        for i, seg in enumerate(PM.SEGMENTOS):
            an = paso * (0.62 + 0.38 * min(1.0, av * 1.6))
            base = PM.BASES[i]
            alto_b = h * (base + (1 - base) * min(1.0, av * 1.25)) * av * 1.15
            if alto_b < 1:
                continue
            x0 = round(x_i := i * paso + (paso - an) / 2)
            d.rectangle([x0, round(h - alto_b), round(x_i + an), h],
                        fill=seg["hex"])
        return cap
    raise SystemExit(f"salida sin implementar: {nombre}")


def pulso_vivo(d, x, y, ancho, alto, avance, PU, t):
    """El pulso SONANDO, entrando hasta `avance` (0 a 1).

    Antes esto era `pulso_parcial`: dibujaba el pulso quieto recortado, y al
    recortar el paso se recalculaba, así que las barras crecían a lo ancho —se
    leía como un estiramiento, no como una entrada. Ahora las barras aparecen
    en su sitio definitivo y ya se están moviendo cuando entran."""
    if avance <= 0:
        return
    E, H, R = PU
    n = max(1, round(len(SEGMENTOS) * min(1.0, avance)))
    PM.dibuja(d, x, y, ancho, alto, E, H, round(t * R["fps"]) % R["frames"], n=n)


def en_tiempos(dur, R):
    """Cuántos tiempos musicales dura la pieza. Si no es entero, el corte cae a
    mitad de tiempo y se nota en cuanto alguien le ponga música."""
    return dur * R["bpm"] / 60


def al_tiempo(dur, R):
    """La duración más cercana que sí cae en tiempo entero."""
    return max(1, round(en_tiempos(dur, R))) * 60 / R["bpm"]


CARBON_RGB = tuple(int(CARBON[i:i + 2], 16) for i in (1, 3, 5))
_PLANOS_A, _PLANOS_C = {}, {}


def plano_apertura(fmt):
    """Lockup, pulso y fechas apilados y centrados, con las cajas medidas."""
    if fmt in _PLANOS_A:
        return _PLANOS_A[fmt]
    w, h = FORMATOS[fmt]
    TOP, BOT = SEGURA[fmt]
    U = min(w, h)
    m = round(w * 0.0667)
    d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    hueco = round(U * 0.048)
    alto_p = round(U * 0.075)
    for escala in (1.0, 0.92, 0.84, 0.76, 0.68, 0.60):
        lock = png_alto(activo("logo/gew-rd-lockup-blanco.png"),
                        round(U * 0.20 * escala))
        f_t = fuente("Bold", round(U * 0.058 * escala))
        bb = d.textbbox((0, 0), C["fechas"], font=f_t)
        h_t = bb[3] - bb[1]
        bloque = lock.height + hueco + alto_p + hueco + h_t
        if bloque <= BOT - TOP and bb[2] - bb[0] <= w - 2 * m:
            break
    y0 = TOP + max(0, ((BOT - TOP) - bloque) // 2)
    y_p = y0 + lock.height + hueco
    base_t = y_p + alto_p + hueco + h_t
    P = {"w": w, "h": h, "TOP": TOP, "BOT": BOT, "m": m, "lock": lock,
         "y_lock": y0, "f_t": f_t, "bb": bb, "base_t": base_t,
         "y_p": y_p, "alto_p": alto_p, "escala": escala,
         "cajas": [("lockup", y0, y0 + lock.height),
                   ("pulso", y_p, y_p + alto_p),
                   ("fechas", base_t - h_t, base_t)]}
    _valida("apertura", fmt, P)
    _PLANOS_A[fmt] = P
    return P


def plano_cuenta(fmt, dias):
    """Lockup y pulso arriba, la cifra en el centro, el tema abajo."""
    clave = (fmt, str(dias))
    if clave in _PLANOS_C:
        return _PLANOS_C[clave]
    w, h = FORMATOS[fmt]
    TOP, BOT = SEGURA[fmt]
    U = min(w, h)
    m = round(w * 0.0667)
    d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    lock = png_alto(activo("logo/gew-rd-lockup-blanco.png"), round(U * 0.095))
    y_lock = TOP + round(U * 0.030)
    alto_p = round(U * 0.070)
    y_p = y_lock + lock.height + round(U * 0.030)
    f3 = fuente("Light", round(U * 0.032))
    b3 = d.textbbox((0, 0), C["tema_es"], font=f3)
    base_tema = BOT - round(U * 0.020)
    txt = str(dias)
    pie = "días" if isinstance(dias, int) and dias != 1 else "día"
    for escala in (1.0, 0.92, 0.84, 0.76, 0.68, 0.60):
        f = fuente("Black", round(U * 0.34 * escala))
        bb = d.textbbox((0, 0), txt, font=f)
        f2 = fuente("Bold", round(U * 0.060 * escala))
        b2 = d.textbbox((0, 0), pie, font=f2)
        alto_c = (bb[3] - bb[1]) + round(U * 0.030) + (b2[3] - b2[1])
        libre = (base_tema - (b3[3] - b3[1]) - round(U * 0.040)) - \
                (y_p + alto_p + round(U * 0.040))
        if alto_c <= libre and bb[2] - bb[0] <= w - 2 * m:
            break
    y_c = y_p + alto_p + round(U * 0.040) + max(0, (libre - alto_c) // 2)
    base_cifra = y_c + (bb[3] - bb[1])
    base_pie = base_cifra + round(U * 0.030) + (b2[3] - b2[1])
    P = {"w": w, "h": h, "TOP": TOP, "BOT": BOT, "m": m, "lock": lock,
         "y_lock": y_lock, "y_p": y_p, "alto_p": alto_p, "escala": escala,
         "f": f, "bb": bb, "base_cifra": base_cifra, "pie": pie, "f2": f2,
         "b2": b2, "base_pie": base_pie, "f3": f3, "b3": b3,
         "base_tema": base_tema,
         "cajas": [("lockup", y_lock, y_lock + lock.height),
                   ("pulso", y_p, y_p + alto_p),
                   ("cifra", base_cifra - (bb[3] - bb[1]), base_cifra),
                   ("pie", base_pie - (b2[3] - b2[1]), base_pie),
                   ("tema", base_tema - (b3[3] - b3[1]), base_tema)]}
    _valida("cuenta", fmt, P)
    _PLANOS_C[clave] = P
    return P


def _valida(tipo, fmt, P):
    mal = cajas_malas(P["cajas"])
    if mal:
        raise SystemExit(f"{tipo}/{fmt}: bloques que se cruzan — " +
                         "; ".join(f"{a}/{b} {px} px" for a, b, px in mal))
    arriba = min(c[1] for c in P["cajas"])
    abajo = max(c[2] for c in P["cajas"])
    if arriba < P["TOP"] or abajo > P["BOT"]:
        raise SystemExit(f"{tipo}/{fmt}: se sale de la zona segura "
                         f"({arriba} arriba, {abajo} abajo; vale "
                         f'{P["TOP"]}–{P["BOT"]})')


def frame_apertura(fmt, t, PU):
    P = plano_apertura(fmt)
    w, h, m = P["w"], P["h"], P["m"]
    im = Image.new("RGB", (w, h), CARBON)
    d = ImageDraw.Draw(im)
    # el lockup entra desde arriba y se asienta
    a = suave(min(1.0, t / 0.55))
    y = round(P["y_lock"] - (1 - a) * h * 0.10)
    cap = im.copy()
    cap.paste(P["lock"], ((w - P["lock"].width) // 2, y), P["lock"])
    im = Image.blend(im, cap, a) if a < 1 else cap
    d = ImageDraw.Draw(im)
    # el pulso entra barriendo, y ya está sonando cuando entra
    b = suave(max(0.0, min(1.0, (t - 0.30) / 0.60)))
    pulso_vivo(d, m, P["y_p"], w - m * 2, P["alto_p"], b, PU, t)
    # Las fechas, en el TIEMPO 2 (0,6 s a 100 BPM), no a 1,35.
    # ⚠️ Antes entraban tan tarde que **no daba tiempo a leerlas**: 18
    # caracteres necesitan 1,20 s a los 15 car/s de la BBC y sólo quedaban
    # 1,05 s legibles antes de la salida. Medido, no estimado.
    c = suave(max(0.0, min(1.0, (t - 0.60) / 0.30)))
    if c > 0.02:
        bb = P["bb"]
        col = tuple(round(CARBON_RGB[i] + (255 - CARBON_RGB[i]) * c)
                    for i in range(3))
        d.text(((w - (bb[2] - bb[0])) // 2 - bb[0], P["base_t"] - bb[3]),
               C["fechas"], font=P["f_t"], fill=col)
    return im


def frame_cuenta(fmt, t, dias, PU):
    P = plano_cuenta(fmt, dias)
    w, h, m = P["w"], P["h"], P["m"]
    im = Image.new("RGB", (w, h), CARBON)
    d = ImageDraw.Draw(im)
    im.paste(P["lock"], (m, P["y_lock"]), P["lock"])
    pulso_vivo(d, m, P["y_p"], w - m * 2, P["alto_p"],
               suave(min(1.0, t / 1.0)), PU, t)
    # la cifra entra creciendo: escala hacia su caja, sin salirse de ella
    a = suave(min(1.0, t / 0.6))
    bb = P["bb"]
    cap_im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dc = ImageDraw.Draw(cap_im)
    dc.text(((w - (bb[2] - bb[0])) // 2 - bb[0], P["base_cifra"] - bb[3]),
            str(dias), font=P["f"], fill=NARANJA)
    if a < 1:
        k = 0.72 + 0.28 * a
        nw, nh = max(1, round(w * k)), max(1, round(h * k))
        chico = cap_im.resize((nw, nh), Image.LANCZOS)
        cap_im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        cap_im.paste(chico, ((w - nw) // 2, round((h - nh) * 0.5)), chico)
    im.paste(cap_im, (0, 0), cap_im)
    d = ImageDraw.Draw(im)
    b2 = P["b2"]
    d.text(((w - (b2[2] - b2[0])) // 2 - b2[0], P["base_pie"] - b2[3]),
           P["pie"], font=P["f2"], fill=BLANCO)
    b3 = P["b3"]
    d.text(((w - (b3[2] - b3[0])) // 2 - b3[0], P["base_tema"] - b3[3]),
           C["tema_es"], font=P["f3"], fill="#DCDCDC")
    return im


# El reparto del endcard se calcula UNA vez por formato, y midiendo.
# ⚠️ La versión anterior estimaba el alto del bloque con una fórmula de
# proporciones (`w*0.02 + w*0.075 + cap`) que no era la tinta real: en
# horizontal daba 598 px para una zona de 546, el `max(0, …)` colapsaba el
# centrado y **«gew.co» caía encima de los logos de partners**. Ahora se apila
# de abajo arriba con las cajas medidas, se encoge hasta que cabe, y si algo se
# cruza el motor se para.
_PLANOS_V = {}


def cajas_malas(cajas):
    """Cruza las cajas verticales. Cero es el único resultado aceptable."""
    mal = []
    for i in range(len(cajas)):
        for j in range(i + 1, len(cajas)):
            (na, a0, a1), (nb, b0, b1) = cajas[i], cajas[j]
            px = min(a1, b1) - max(a0, b0)
            if px > 0:
                mal.append((na, nb, px))
    return mal


def plano_endcard(fmt):
    if fmt in _PLANOS_V:
        return _PLANOS_V[fmt]
    w, h = FORMATOS[fmt]
    TOP, BOT = SEGURA[fmt]
    U = min(w, h)      # en apaisado el ancho no sirve de unidad: el lockup
    m = round(w * 0.0667)               # salía a 365 px en un lienzo de 1080
    d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    hueco = round(U * 0.030)
    alto_pt = round(U * 0.038)
    alto_ia = round(alto_pt * 0.78)
    cap_rot = round(U * 0.0135)
    alto_pulso = round(U * 0.075)

    P = None
    for escala in (1.0, 0.94, 0.88, 0.82, 0.76, 0.70, 0.64, 0.58):
        alto_l = round(U * 0.19 * escala)
        cap_t = round(w * 0.050 * escala)
        lock = png_alto(activo("logo/gew-rd-lockup-blanco.png"), alto_l)
        f_t = fuente("Bold", cap_t)
        b_f = d.textbbox((0, 0), C["fechas"], font=f_t)
        b_s = d.textbbox((0, 0), C["sitio"], font=f_t)
        h_f, h_s = b_f[3] - b_f[1], b_s[3] - b_s[1]
        y_pulso = BOT - alto_pulso
        y_ia = y_pulso - hueco - alto_ia
        y_rot = y_ia - round(cap_rot * 1.55)
        y_pt = y_rot - round(U * 0.020) - alto_pt
        base_s = y_pt - hueco
        base_f = base_s - h_s - round(cap_t * 0.34)
        tope_txt = base_f - h_f
        libre = tope_txt - hueco - TOP
        if libre < lock.height and escala > 0.58:
            continue
        y_lock = TOP + max(0, (libre - lock.height) // 2)
        P = {"w": w, "h": h, "TOP": TOP, "BOT": BOT, "U": U, "m": m,
             "lock": lock, "y_lock": y_lock, "cap_t": cap_t, "f_t": f_t,
             "b_f": b_f, "b_s": b_s, "base_f": base_f, "base_s": base_s,
             "y_pt": y_pt, "alto_pt": alto_pt, "y_rot": y_rot, "y_ia": y_ia,
             "alto_ia": alto_ia, "cap_rot": cap_rot, "y_pulso": y_pulso,
             "alto_pulso": alto_pulso, "escala": escala,
             "cajas": [("lockup", y_lock, y_lock + lock.height),
                       ("fechas", base_f - h_f, base_f),
                       ("sitio", base_s - h_s, base_s),
                       ("partners", y_pt, y_pt + alto_pt),
                       ("cobertura", y_rot, y_ia + alto_ia),
                       ("pulso", y_pulso, y_pulso + alto_pulso)]}
        break
    if P is None:
        raise SystemExit(f"endcard/{fmt}: no cabe ni al 58 %")
    mal = cajas_malas(P["cajas"])
    if mal:
        raise SystemExit(f"endcard/{fmt}: bloques que se cruzan — " +
                         "; ".join(f"{a}/{b} {px} px" for a, b, px in mal))
    if P["cajas"][0][1] < TOP or P["cajas"][-1][2] > BOT:
        raise SystemExit(f"endcard/{fmt}: el bloque se sale de la zona segura")
    _PLANOS_V[fmt] = P
    return P


def frame_endcard(fmt, t, PU):
    P = plano_endcard(fmt)
    w, h, m, U = P["w"], P["h"], P["m"], P["U"]
    im = Image.new("RGB", (w, h), CARBON)
    d = ImageDraw.Draw(im)
    a = suave(min(1.0, t / 0.7))
    cap = im.copy()
    cap.paste(P["lock"], ((w - P["lock"].width) // 2, P["y_lock"]), P["lock"])
    im = Image.blend(im, cap, a) if a < 1 else cap
    d = ImageDraw.Draw(im)

    b = suave(max(0.0, min(1.0, (t - 0.5) / 0.8)))
    if b > 0.02:
        for i, (txt, bb, base, col) in enumerate((
                (C["fechas"], P["b_f"], P["base_f"], BLANCO),
                (C["sitio"], P["b_s"], P["base_s"], NARANJA))):
            rgb = tuple(int(col[j:j + 2], 16) for j in (1, 3, 5))
            mez = tuple(round(CARBON_RGB[k] + (rgb[k] - CARBON_RGB[k]) * b)
                        for k in range(3))
            d.text(((w - (bb[2] - bb[0])) // 2 - bb[0], base - bb[3]), txt,
                   font=P["f_t"], fill=mez)
        # Los dos Partners permanentes y, en segunda fila y más pequeña, IA
        # Media como cobertura: la misma jerarquía que las piezas fijas.
        piezas = [marca_alto(activo(r), P["alto_pt"], blanco=True)
                  for r in PARTNERS]
        sep = round(U * 0.045)
        total = sum(pz.width for pz in piezas) + sep * (len(piezas) - 1)
        cap_pt = im.copy()
        d2 = ImageDraw.Draw(cap_pt)
        x = (w - total) // 2
        for pz in piezas:
            cap_pt.paste(pz, (x, P["y_pt"]), pz)
            x += pz.width + sep
        f_r = fuente("Bold", P["cap_rot"])
        ia = marca_alto(activo(LOGO_COBERTURA["oscuro"]), P["alto_ia"])
        rot = ROTULOS["cobertura"]
        an_r = d2.textlength(rot, font=f_r)
        bb_r = d2.textbbox((0, 0), rot, font=f_r)
        d2.text(((w - an_r) // 2 - bb_r[0], P["y_rot"] - bb_r[1]), rot,
                font=f_r, fill="#B8B8B8")
        cap_pt.paste(ia, ((w - ia.width) // 2, P["y_ia"]), ia)
        im = Image.blend(im, cap_pt, b) if b < 1 else cap_pt
        d = ImageDraw.Draw(im)
    pulso_vivo(d, m, P["y_pulso"], w - m * 2, P["alto_pulso"],
               suave(max(0.0, min(1.0, (t - 0.3) / 1.1))), PU, t)
    return im


CONSTRUYE = {"apertura": lambda fmt, t, dias, PU: frame_apertura(fmt, t, PU),
             "cuenta": frame_cuenta,
             "endcard": lambda fmt, t, dias, PU: frame_endcard(fmt, t, PU)}


def render(tipo, fmt, dias=3, salida=None, fps=FPS, papel=PAPEL, dur=None,
           sale=None, bpm=None):
    """Compone los frames y los monta. Devuelve la ruta y lo medido."""
    dur = dur or DURACION[tipo]
    n = round(dur * fps)
    # El bucle del pulso se calcula UNA vez por pieza, no por fotograma.
    R = PM.rejilla(bpm or PM.BPM, fps=fps)
    PU = PM.bucle(PM.PAPELES[papel], R)
    G = GUION[tipo]
    sale = sale or G["sale"]
    reloj = AN.Reloj(dur=dur, bpm=R["bpm"], fps=fps)
    f_sale = reloj.sale(sale, dur=G["dur_sale"])
    tmp = f"{RAIZ}/_cache/_v/{tipo}-{fmt}"
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp, exist_ok=True)
    for i in range(n):
        t = i / fps
        im = CONSTRUYE[tipo](fmt, t, dias, PU)
        im = aplica_salida(im, sale, f_sale(t), PU)
        im.save(f"{tmp}/{i:04d}.png")

    salida = salida or f"{RAIZ}/_salida/video-mp4/{tipo}--{fmt}.mp4"
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    # H.264 High Profile + yuv420p es lo que pide YouTube y lo que traga todo.
    # `+faststart` mueve el índice al principio: sin eso, algunas apps no
    # empiezan a reproducir hasta descargarlo entero.
    # ⚠️ CBR ESTRICTO, y conviene saber por qué. Con CRF, un fondo plano bajaba
    # a 130–415 kbps: se ve perfecto, pero queda por debajo del mínimo
    # documentado de TikTok (516 kbps) y las plataformas recomprimen lo que les
    # llega flojo. Con bitrate «objetivo» x264 tampoco lo gastaba: si no hace
    # falta, no lo usa. Con `nal-hrd=cbr` sí se garantiza el suelo, **rellenando
    # con bits de padding**. Es decir: parte de estos megas no son calidad, son
    # relleno para cumplir un requisito publicado. Se hace a sabiendas.
    r = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps),
         "-i", f"{tmp}/%04d.png", "-c:v", "libx264", "-profile:v", "high",
         "-pix_fmt", "yuv420p", "-b:v", f"{BITRATE_KBPS}k",
         "-minrate", f"{BITRATE_KBPS}k", "-maxrate", f"{BITRATE_KBPS}k",
         "-bufsize", f"{BITRATE_KBPS}k", "-x264-params", "nal-hrd=cbr",
         "-preset", "medium",
         "-movflags", "+faststart", salida],
        capture_output=True, text=True)
    shutil.rmtree(tmp, ignore_errors=True)
    if r.returncode:
        return salida, {"error": r.stderr.strip()[:160]}
    return salida, sonda(salida)


def sonda(ruta):
    """Lo que el fichero ES, preguntado a ffprobe. Nunca lo que yo supuse."""
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,r_frame_rate,nb_frames,codec_name,profile,pix_fmt",
         "-show_entries", "format=duration,size,bit_rate", "-of", "json", ruta],
        capture_output=True, text=True)
    d = json.loads(r.stdout or "{}")
    s = (d.get("streams") or [{}])[0]
    f = d.get("format", {})
    num, den = (s.get("r_frame_rate", "0/1").split("/") + ["1"])[:2]
    return {"px": f"{s.get('width')}x{s.get('height')}",
            "fps": round(int(num) / max(1, int(den)), 2),
            "frames": int(s.get("nb_frames") or 0),
            "codec": s.get("codec_name"), "perfil": s.get("profile"),
            "pix_fmt": s.get("pix_fmt"),
            "seg": round(float(f.get("duration", 0)), 3),
            "bytes": int(f.get("size", 0)),
            "kbps": round(int(f.get("bit_rate", 0)) / 1000)}


def main():
    ap = argparse.ArgumentParser(description="Kit de vídeo GEW · RD")
    ap.add_argument("--tipo", choices=sorted(DURACION))
    ap.add_argument("--formato", choices=sorted(FORMATOS))
    ap.add_argument("--dias", type=int, default=3)
    ap.add_argument("--todos", action="store_true")
    ap.add_argument("--salida", default=f"{RAIZ}/_salida/video-mp4")
    ap.add_argument("--papel", choices=sorted(PM.PAPELES), default=PAPEL,
                    help="solo → espectro (defecto: nadie habla encima) · "
                         "voz → latido")
    ap.add_argument("--al-tiempo", action="store_true", dest="al_tiempo",
                    help="ajusta la duración al tiempo musical entero más cercano")
    ap.add_argument("--sale", choices=sorted(AN.SALIDAS),
                    help="fuerza la salida de todas las piezas "
                         "(por defecto, la que declara GUION)")
    a = ap.parse_args()
    if not (a.tipo and a.formato) and not a.todos:
        a.todos = True

    if not shutil.which("ffmpeg"):
        sys.exit("falta ffmpeg: brew install ffmpeg")

    trabajos = ([(t, f) for t in ("apertura", "cuenta", "endcard")
                 for f in ("vertical", "retrato", "horizontal", "cuadrado")]
                if a.todos
                else [(a.tipo, a.formato)])
    hechos, fallos, movidos = [], [], []
    RJ = PM.rejilla()
    modo = PM.PAPELES[a.papel]
    print(f'pulso «{modo}» (papel {a.papel}) · {RJ["bpm"]:g} BPM · bucle de '
          f'{RJ["frames"]} fotogramas · {PM.POR_QUE_PAPEL[a.papel]}')
    # La duración en tiempos musicales. No es un fallo —estas piezas salen sin
    # audio a propósito— pero si el corte no cae en tiempo entero se nota en
    # cuanto alguien les ponga música debajo, y eso hay que decirlo antes.
    DUR = dict(DURACION)
    print(f'\n{"pieza":12} {"seg":>6} {"tiempos":>9} {"cae en tiempo":>14} '
          f'{"al tiempo sería":>16} {"entra":>9} {"sale":>10}')
    for t in sorted(DUR):
        tm = en_tiempos(DUR[t], RJ)
        ok = abs(tm - round(tm)) < 1e-9
        alt = al_tiempo(DUR[t], RJ)
        print(f'  {t:10} {DUR[t]:6.2f} {tm:9.3f} {("sí" if ok else "NO"):>14} '
              f'{alt:14.2f} s {GUION[t]["entra"]:>9} '
              f'{(a.sale or GUION[t]["sale"]):>10}')
        if a.al_tiempo:
            DUR[t] = alt
    print(f"{'pieza':22} {'px':>10} {'fps':>5} {'seg':>6} {'frames':>7} "
          f"{'códec':>8} {'perfil':>6} {'kbps':>6} {'MB':>5}")
    for tipo, fmt in trabajos:
        p, m = render(tipo, fmt, a.dias,
                      salida=f"{a.salida}/{tipo}--{fmt}.mp4",
                      papel=a.papel, dur=DUR[tipo], sale=a.sale)
        if "error" in m:
            fallos.append(f"  FALLA {tipo}/{fmt}: {m['error']}")
            continue
        hechos.append(p)
        print(f"  {tipo+'/'+fmt:20} {m['px']:>10} {m['fps']:5} {m['seg']:6.2f} "
              f"{m['frames']:7} {m['codec']:>8} {m['perfil']:>6} {m['kbps']:6} "
              f"{m['bytes']/1e6:5.2f}")
        esp_px = "x".join(map(str, FORMATOS[fmt]))
        if m["px"] != esp_px:
            fallos.append(f"  FALLA {tipo}/{fmt}: lienzo {m['px']}, esperado {esp_px}")
        if abs(m["seg"] - DUR[tipo]) > 0.05:
            fallos.append(f"  FALLA {tipo}/{fmt}: dura {m['seg']} s y debía "
                          f"durar {DUR[tipo]}")
        if m["frames"] != round(DUR[tipo] * FPS):
            fallos.append(f"  FALLA {tipo}/{fmt}: {m['frames']} fotogramas, "
                          f"esperados {round(DUR[tipo]*FPS)}")
        # el pulso tiene que MOVERSE dentro de la pieza, medido en el MP4
        n_fin = m["frames"] - 1
        # ⚠️ la ventana va en mitad de la pieza, no al final: con las salidas
        # puestas, medir en el 90 % mezclaba el movimiento del pulso con el
        # desvanecido y el número dejaba de significar lo que dice.
        mov = PM.se_mueve(p, round(n_fin * 0.45), round(n_fin * 0.60))
        movidos.append((f"{tipo}/{fmt}", mov))
        if not mov:
            fallos.append(f"  FALLA {tipo}/{fmt}: entre los fotogramas "
                          f"{round(n_fin*0.75)} y {round(n_fin*0.90)} no cambia "
                          f"un solo píxel — el pulso está quieto")
        if m["pix_fmt"] != "yuv420p":
            fallos.append(f"  FALLA {tipo}/{fmt}: pix_fmt {m['pix_fmt']}, "
                          f"y hace falta yuv420p")
        if m["kbps"] < 516:
            fallos.append(f"  FALLA {tipo}/{fmt}: {m['kbps']} kbps, por debajo "
                          f"del mínimo documentado de TikTok (516)")

    if hechos:
        print(f'\n{"la pieza SALE":26} {"tinta al 60 %":>14} {"al final":>10} '
              f'{"queda":>7} {"fondo libre":>12}')
        for ruta in hechos:
            q = PM.queda_al_final(ruta)
            if q:
                # ⚠️ Python 3.9 no admite comillas dobles dentro de un
                # f-string con comillas dobles: se calcula fuera.
                fl = q.get("fondo_libre")
                fl_txt = "—" if fl is None else f"{fl:.2f} %"
                print(f'  {os.path.basename(ruta):24} {q["antes"]:14} '
                      f'{q["final"]:10} {q["queda"]:6.1f} % {fl_txt:>12}')
                tipo = os.path.basename(ruta).split("--")[0]
                esperada = (a.sale or GUION[tipo]["sale"])
                # Cada salida deja la pantalla de una forma distinta y el
                # umbral tiene que saberlo: `cierra` NO vacía la pieza, la
                # LLENA de barras. Medirla con el umbral de `apaga` la daba
                # por rota cuando estaba haciendo exactamente lo suyo.
                esp = ESPERADO_AL_FINAL[esperada]
                if "fondo" in esp and q.get("fondo_libre") is not None:
                    if q["fondo_libre"] > esp["fondo"]:
                        fallos.append(
                            f'  FALLA {os.path.basename(ruta)}: la cortina '
                            f'deja {q["fondo_libre"]:.2f} % de fondo a la '
                            f'vista y debe tapar del todo')
                if not esp["ok"](q["queda"]):
                    fallos.append(f'  FALLA {os.path.basename(ruta)}: salida '
                                  f'«{esperada}» debía dejar {esp["dice"]} y '
                                  f'queda el {q["queda"]:.1f} %')
    # ¿Da tiempo a LEER cada rótulo?
    print(f'\n{"rótulo":34} {"car":>4} {"necesita":>9} {"en pantalla":>12} {"":>4}')
    for tipo in sorted({t for t, _ in trabajos}):
        for txt, ap, des in rotulos(tipo, a.dias):
            en = des - ap
            nec = AN.tiempo_de_lectura(txt)
            ok = AN.se_lee(txt, en)
            print(f'  {tipo[:8]:8} «{txt[:22]:22}» {len(txt):4} {nec:8.2f} s '
                  f'{en:10.2f} s  {("sí" if ok else "NO"):>4}')
            if not ok:
                fallos.append(f'  FALLA {tipo}: «{txt}» necesita {nec:.2f} s '
                              f'para leerse a {AN.CPS_LECTURA:g} car/s y está '
                              f'{en:.2f} s en pantalla')
    if movidos:
        print(f'\n{"el pulso se mueve":26} {"px que cambian":>15}')
        for n, v in movidos:
            print(f"  {n:24} {v if v is not None else 'no medible':>15}")
    # el aviso del nivel «anuncio»: qué se cortaría si la pieza se promociona
    avisos = []
    for tipo, fmt in trabajos:
        P = ({"apertura": plano_apertura, "endcard": plano_endcard}.get(tipo)
             or (lambda f: plano_cuenta(f, a.dias)))(fmt)
        for niv in ("anuncio", "anuncio-disclaimer"):
            avisos += ZN.informe(P["cajas"], FORMATOS[fmt], fmt, niv)
    if avisos:
        print()
        for x in dict.fromkeys(avisos):
            print(x)
    print(f"\nproducidos {len(hechos)} de {len(trabajos)} esperados")
    print("H.264 High + yuv420p (lo que pide YouTube) · sin audio a propósito · "
          "≥516 kbps es el mínimo documentado de TikTok")
    for f in fallos:
        print(f)
    for h in hechos:
        print(h)
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
