#!/usr/bin/env python3
"""
Piezas en serie · GEW · RD.

    carrusel     portada + láminas de contenido + cierre
    cuenta       la cuenta atrás: faltan 7 · 3 · mañana · hoy · en marcha
    agenda       la programación, de un día o de la semana

Las tres comparten el mismo esqueleto de la campaña: fondo carbón, lockup
dominicano arriba, franja naranja al filo y banda de logos donde toca.

Uso:
    python3 serie.py --tipo carrusel --guion contenido/carrusel-ejemplo.json
    python3 serie.py --tipo cuenta --formato retrato
    python3 serie.py --tipo agenda --dia
    python3 serie.py --todos
"""
import argparse, json, os, sys
from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.abspath(__file__))
TOK = json.load(open(f"{RAIZ}/tokens/tokens.json", encoding="utf-8"))
sys.path.insert(0, RAIZ)
from campana import (fuente, marca_alto, png_alto, pin, trocear, palabras,
                     pulso, marcas,  # noqa: E402
                     repartir, sello)

CARBON = TOK["color"]["campana2026"]["carbon"]["hex"]
NARANJA = TOK["color"]["campana2026"]["naranja"]["hex"]
BLANCO = "#FFFFFF"
TINTA = TOK["color"]["marca"]["carbon-wordmark"]["hex"]
GRIS = "#C6C6C6"

FORMATOS = {
    "retrato":  {"px": (1080, 1350), "unidad": 1080},
    "cuadrado": {"px": (1080, 1080), "unidad": 1010},
    "historia": {"px": (1080, 1920), "unidad": 1180, "segura": (269, 1670)},
}

R = dict(margen=0.0667, franja=0.0222, banda=0.1250, logo=0.0820,
         titular=0.0900, cuerpo=0.0330, numero=0.0330, dato=0.0300,
         hora=0.0290, lema=0.0215, cifra=0.2600, rotulo=0.0330)


def hoja(fmt):
    w, h = FORMATOS[fmt]["px"]
    u = FORMATOS[fmt]["unidad"]
    return w, h, u, {k: round(v * u) for k, v in R.items()}


def envolver(d, texto, font, ancho):
    lineas, act = [], ""
    for p in texto.split():
        t = (act + " " + p).strip()
        if d.textlength(t, font=font) <= ancho or not act:
            act = t
        else:
            lineas.append(act); act = p
    if act:
        lineas.append(act)
    return lineas


def base(fmt, con_banda=True, host=None, socios=None):
    """Lienzo con lockup, franja y (si toca) banda de logos. Devuelve el suelo
    hasta donde puede llegar el contenido."""
    w, h, U, g = hoja(fmt)
    m, fr, bd = g["margen"], g["franja"], g["banda"]
    seg = FORMATOS[fmt].get("segura")
    TOP, BOT = seg if seg else (0, h)
    im = Image.new("RGB", (w, h), CARBON)
    d = ImageDraw.Draw(im)
    d.rectangle([0, (h - fr) if seg else (BOT - fr), w, h if seg else BOT], fill=NARANJA)
    med = {"formato": fmt, "px": [w, h], "zona": [TOP, BOT]}

    lock = png_alto(f"{RAIZ}/logo/gew-rd-lockup-blanco.png", g["logo"])
    im.paste(lock, (m, TOP + m), lock)
    med["lockup"] = [lock.width, lock.height]

    # el pulso, la firma del movimiento
    y_p = TOP + m + lock.height + round(U * 0.028)
    a_p = round(U * 0.032)
    pulso(d, m, y_p, w - m * 2, a_p)
    med["pulso"] = [m, y_p, w - m, y_p + a_p]

    base_banda = BOT if seg else BOT - fr
    if con_banda:
        d.rectangle([0, base_banda - bd, w, base_banda], fill=BLANCO)
        # los tres bloques, desde la biblioteca compartida
        med["marcas"] = marcas(im, d, m, base_banda - bd + round(U * 0.0250),
                               w - m * 2, U, alto_logo=round(U * 0.0450),
                               partners=([host] + list(socios or [])) if host else None)
        suelo = base_banda - bd - round(U * 0.045)
    else:
        suelo = base_banda - round(U * 0.045)
    med["suelo"] = suelo
    return im, d, w, h, U, g, TOP, suelo, med


def pie_lema(d, w, U, g, m, y):
    """El pin con el lema y gew.co, la línea que cierra la zona carbón."""
    cap = g["lema"]
    while cap > 8:
        f = fuente("Light", cap)
        an = (round(cap * 0.52) * 3.1 + d.textlength(TOK["campana"]["tema_es"], font=f)
              + d.textlength(TOK["campana"]["sitio"], font=f) + round(U * 0.030))
        if an <= w - m * 2:
            break
        cap -= 1
    r = round(cap * 0.52)
    pin(d, m + r, y + round(cap * 0.32), r, TOK["color"]["barra"]["hex"][0])
    d.text((m + r * 3.1, y), TOK["campana"]["tema_es"], font=f, fill=BLANCO)
    bb = d.textbbox((0, 0), TOK["campana"]["sitio"], font=f)
    d.text((w - m - (bb[2] - bb[0]) - bb[0], y), TOK["campana"]["sitio"], font=f, fill=BLANCO)
    return cap


def titular(d, im, texto, x, y, cap_max, util, U, color=BLANCO):
    """Titular con reflow: reparte en las líneas que dejen el cuerpo más grande."""
    lineas = list(trocear(texto))
    pal = palabras(lineas)
    f_ref = fuente("Light", 100)
    anchos = [d.textlength(p, font=f_ref) for p, _ in pal]
    esp = d.textlength(" ", font=f_ref)

    def mayor(lns):
        c = cap_max
        while c > 10:
            f = fuente("Light", c)
            if max(sum(d.textlength(t, font=f) for t, _ in tr) for tr in lns) <= util:
                return c
            c -= 1
        return c

    mejor = (mayor(lineas), lineas)
    for k in range(1, min(5, len(pal)) + 1):
        cand = repartir(pal, k, anchos, esp)
        if not cand:
            continue
        c = mayor(cand)
        if c > mejor[0]:
            mejor = (c, cand)
    cap, lineas = mejor
    f = fuente("Light", cap)
    il = round(cap * 1.30)
    for tr in lineas:
        xx = x
        for t, dest in tr:
            bb = d.textbbox((0, 0), t, font=f)
            d.text((xx - bb[0], y - bb[1]), t, font=f, fill=NARANJA if dest else color)
            xx += d.textlength(t, font=f)
        y += il
    return y - il + cap, cap, len(lineas)


# ─────────────────────────────────────────────────────────── carrusel ──
def carrusel(guion, fmt="retrato", salida=None):
    """guion = {"portada": "...", "laminas": [{"titulo","cuerpo"}], "cierre": {...}}"""
    hechas = []
    n_total = 1 + len(guion["laminas"]) + 1
    for i in range(n_total):
        ultima = i == n_total - 1
        im, d, w, h, U, g, TOP, suelo, med = base(fmt, con_banda=(i == 0 or ultima))
        m = g["margen"]
        util = w - m * 2
        techo = TOP + m + g["logo"] + round(U * 0.075)
        y_lema = suelo - round(U * 0.030)

        if i == 0:
            fin, cap, nl = titular(d, im, guion["portada"], m,
                                   techo + round(U * 0.06), g["titular"], util, U)
            # VAG Rounded no trae la flecha: se dibuja
            f_p = fuente("Bold", round(U * 0.024))
            yp = fin + round(U * 0.055)
            bb = d.textbbox((0, 0), "DESLIZA", font=f_p)
            d.text((m - bb[0], yp - bb[1]), "DESLIZA", font=f_p, fill=NARANJA)
            fx = m + (bb[2] - bb[0]) + round(U * 0.018)
            fy = yp + round(U * 0.024) / 2
            lg_ = round(U * 0.026)
            d.line([(fx, fy), (fx + lg_, fy)], fill=NARANJA, width=max(2, round(U * 0.0035)))
            d.polygon([(fx + lg_, fy - lg_ * 0.28), (fx + lg_, fy + lg_ * 0.28),
                       (fx + lg_ * 1.38, fy)], fill=NARANJA)
            med["papel"] = "portada"
        elif ultima:
            c = guion.get("cierre", {})
            fin, cap, nl = titular(d, im, c.get("titulo", "Nos vemos en noviembre"),
                                   m, techo + round(U * 0.06), g["titular"], util, U)
            f_c = fuente("Light", g["cuerpo"])
            yy = fin + round(U * 0.050)
            for ln in envolver(d, c.get("cuerpo", ""), f_c, util):
                bb = d.textbbox((0, 0), ln, font=f_c)
                d.text((m - bb[0], yy - bb[1]), ln, font=f_c, fill=GRIS)
                yy += round(g["cuerpo"] * 1.45)
            med["papel"] = "cierre"
        else:
            lam = guion["laminas"][i - 1]
            f_n = fuente("Bold", g["numero"])
            num = f"{i:02d}"
            bb = d.textbbox((0, 0), num, font=f_n)
            d.text((m - bb[0], techo - bb[1]), num, font=f_n, fill=NARANJA)
            d.line([(m, techo + g["numero"] + round(U * 0.020)),
                    (m + round(U * 0.070), techo + g["numero"] + round(U * 0.020))],
                   fill=NARANJA, width=max(2, round(U * 0.005)))
            fin, cap, nl = titular(d, im, lam["titulo"], m,
                                   techo + g["numero"] + round(U * 0.055),
                                   round(g["titular"] * 0.74), util, U)
            f_c = fuente("Light", g["cuerpo"])
            yy = fin + round(U * 0.045)
            for ln in envolver(d, lam.get("cuerpo", ""), f_c, util):
                bb = d.textbbox((0, 0), ln, font=f_c)
                d.text((m - bb[0], yy - bb[1]), ln, font=f_c, fill=GRIS)
                yy += round(g["cuerpo"] * 1.45)
            med["papel"] = f"lamina-{i}"
            med["holgura"] = y_lema - yy
        pie_lema(d, w, U, g, m, y_lema)
        med["lamina"] = i
        if salida:
            r = f"{salida}/{i:02d}--{fmt}.png"
            os.makedirs(salida, exist_ok=True)
            im.save(r)
            hechas.append((r, med))
    return hechas


# ───────────────────────────────────────────────────────── cuenta atrás ──
CUENTA = [("7", "días"), ("3", "días"), ("1", "día"), ("HOY", ""), ("YA", "")]
ROTULO = {"7": "Faltan", "3": "Faltan", "1": "Falta", "HOY": "Empieza",
          "YA": "Estamos en marcha"}
BAJADA = {"7": "Siete días para que el país entero hable de emprender.",
          "3": "Tres días. Ve apartando la agenda.",
          "1": "Mañana arranca la semana.",
          "HOY": "Hoy empieza la Semana Global de Emprendimiento.",
          "YA": "Toda la semana, en todo el país."}


def cuenta(clave, fmt="retrato", salida=None):
    im, d, w, h, U, g, TOP, suelo, med = base(fmt)
    m = g["margen"]
    util = w - m * 2
    techo = TOP + m + g["logo"] + round(U * 0.075)
    y_lema = suelo - round(U * 0.030)
    unidad = dict(CUENTA)[clave]

    f_rot = fuente("Light", g["rotulo"])
    bb = d.textbbox((0, 0), ROTULO[clave], font=f_rot)
    # la cifra ocupa el centro; el rótulo va encima
    cap = g["cifra"]
    while cap > 20:
        f_c = fuente("Bold", cap)
        if d.textlength(clave, font=f_c) <= util:
            break
        cap -= 2
    f_c = fuente("Bold", cap)
    alto = g["rotulo"] + round(U * 0.030) + cap + round(U * 0.030) + g["cuerpo"] * 2
    y = techo + max(0, round((y_lema - round(U * 0.055) - techo - alto) * 0.42))

    d.text((m - bb[0], y - bb[1]), ROTULO[clave], font=f_rot, fill=GRIS)
    y += g["rotulo"] + round(U * 0.030)
    bc = d.textbbox((0, 0), clave, font=f_c)
    d.text((m - bc[0], y - bc[1]), clave, font=f_c, fill=NARANJA)
    if unidad:
        f_u = fuente("Light", round(cap * 0.24))
        bu = d.textbbox((0, 0), unidad, font=f_u)
        d.text((m + (bc[2] - bc[0]) + round(U * 0.022) - bu[0],
                y + cap - (bu[3] - bu[1]) - bu[1]), unidad, font=f_u, fill=BLANCO)
    y += cap + round(U * 0.040)
    f_b = fuente("Light", g["cuerpo"])
    for ln in envolver(d, BAJADA[clave], f_b, util):
        bb2 = d.textbbox((0, 0), ln, font=f_b)
        d.text((m - bb2[0], y - bb2[1]), ln, font=f_b, fill=BLANCO)
        y += round(g["cuerpo"] * 1.45)
    med["holgura"] = y_lema - round(U * 0.030) - y
    med["cifra"] = [clave, cap]
    pie_lema(d, w, U, g, m, y_lema)
    if salida:
        os.makedirs(salida, exist_ok=True)
        r = f"{salida}/cuenta-{clave}--{fmt}.png"
        im.save(r)
        return r, med
    return im, med


# ───────────────────────────────────────────────────────────── agenda ──
def agenda(titulo, items, fmt="retrato", salida=None, nombre="agenda"):
    """items = [{"hora","titulo","lugar"}]"""
    im, d, w, h, U, g, TOP, suelo, med = base(fmt)
    m = g["margen"]
    util = w - m * 2
    techo = TOP + m + g["logo"] + round(U * 0.070)
    y_lema = suelo - round(U * 0.030)

    fin, cap, nl = titular(d, im, titulo, m, techo, round(g["titular"] * 0.72), util, U)
    y = fin + round(U * 0.050)
    disponible = y_lema - round(U * 0.050) - y

    # el cuerpo de la lista se ajusta al número de entradas
    # el alto de cada fila depende de cuántas líneas ocupe su título: estimarlo
    # con una constante deja la lista pisando el pie
    col_hora = round(U * 0.150)
    cap_h = g["hora"]
    while cap_h > 11:
        f_t_ = fuente("Light", round(cap_h * 1.15))
        f_l_ = fuente("Light", round(cap_h * 0.86))
        total = 0
        for it in items:
            nl_ = min(2, len(envolver(d, it["titulo"], f_t_, util - col_hora)))
            total += nl_ * round(cap_h * 1.42)
            if it.get("lugar"):
                total += round(cap_h * 1.15)
            total += round(U * 0.026)
        if total <= disponible:
            break
        cap_h -= 1
    f_h = fuente("Bold", cap_h)
    f_t = fuente("Light", round(cap_h * 1.15))
    f_l = fuente("Light", round(cap_h * 0.86))
    med["cap_hora"] = [cap_h, g["hora"]]

    for it in items:
        bb = d.textbbox((0, 0), it["hora"], font=f_h)
        d.text((m - bb[0], y - bb[1]), it["hora"], font=f_h, fill=NARANJA)
        tt = envolver(d, it["titulo"], f_t, util - col_hora)
        yy = y
        for ln in tt[:2]:
            bb = d.textbbox((0, 0), ln, font=f_t)
            d.text((m + col_hora - bb[0], yy - bb[1]), ln, font=f_t, fill=BLANCO)
            yy += round(cap_h * 1.42)
        if it.get("lugar"):
            bb = d.textbbox((0, 0), it["lugar"], font=f_l)
            d.text((m + col_hora - bb[0], yy - bb[1]), it["lugar"], font=f_l, fill=GRIS)
            yy += round(cap_h * 1.15)
        y = yy + round(U * 0.026)
        d.line([(m, y - round(U * 0.013)), (w - m, y - round(U * 0.013))],
               fill="#5E5E5E", width=1)
    med["holgura"] = y_lema - round(U * 0.030) - y
    med["entradas"] = len(items)
    pie_lema(d, w, U, g, m, y_lema)
    if salida:
        os.makedirs(salida, exist_ok=True)
        r = f"{salida}/{nombre}--{fmt}.png"
        im.save(r)
        return r, med
    return im, med


# ─────────────────────────────────────────────────────────────── CLI ──
DEMO_CARRUSEL = {
    "portada": "Cinco formas de *entrar* a la Semana Global",
    "laminas": [
        {"titulo": "Ve a una actividad",
         "cuerpo": "Más de cuarenta organizaciones abren sus puertas del 16 al 22. "
                   "Entrada libre en casi todas."},
        {"titulo": "Lleva a alguien",
         "cuerpo": "La persona que nunca se ha planteado emprender es justo la que "
                   "queremos en la sala."},
        {"titulo": "Cuenta tu problema",
         "cuerpo": "Lo que te frustra de tu barrio o de tu trabajo puede ser el "
                   "negocio de otro. O el tuyo."},
        {"titulo": "Abre tu puerta",
         "cuerpo": "Si tienes un local, un aula o una sala, puedes ser sede. "
                   "Se registra en un formulario."},
        {"titulo": "Comparte lo que sabes",
         "cuerpo": "Una charla de treinta minutos sobre lo que haces todos los días "
                   "vale más de lo que crees."},
    ],
    "cierre": {"titulo": "Del *16 al 22* de noviembre",
               "cuerpo": "Todo el programa en gew.co. Búscanos también en la comunidad "
                         "de IAvanza."},
}
DEMO_AGENDA_DIA = ("Lunes *17* de noviembre", [
    {"hora": "9:00", "titulo": "Apertura · Semana Global de Emprendimiento",
     "lugar": "Cámara de Comercio · Santo Domingo"},
    {"hora": "11:00", "titulo": "Taller: valida tu idea en una semana",
     "lugar": "Universidad Demo · Aula magna"},
    {"hora": "14:00", "titulo": "Mesa: financiar sin banco",
     "lugar": "Sala Demo · Ciudad"},
    {"hora": "17:00", "titulo": "Taller de *finanzas*", "lugar": "Universidad Demo"},
    {"hora": "19:00", "titulo": "Encuentro *semanal* · edición especial",
     "lugar": "Sala Demo"},
])
DEMO_AGENDA_SEMANA = ("La *semana* completa", [
    {"hora": "LUN 16", "titulo": "Apertura nacional", "lugar": "Santo Domingo"},
    {"hora": "MAR 17", "titulo": "Día de los constructores", "lugar": "Santiago y SD"},
    {"hora": "MIÉ 18", "titulo": "Financiamiento y capital", "lugar": "Todo el país"},
    {"hora": "JUE 19", "titulo": "Jóvenes y universidades", "lugar": "12 campus"},
    {"hora": "VIE 20", "titulo": "Mujeres que emprenden", "lugar": "Todo el país"},
    {"hora": "SÁB 21", "titulo": "Competencia Demo · final", "lugar": "Teatro Demo"},
    {"hora": "DOM 22", "titulo": "Cierre y celebración", "lugar": "Sala Demo"},
])


def main():
    ap = argparse.ArgumentParser(description="Piezas en serie GEW · RD")
    ap.add_argument("--tipo", choices=["carrusel", "cuenta", "agenda"])
    ap.add_argument("--formato", choices=list(FORMATOS), default="retrato")
    ap.add_argument("--guion")
    ap.add_argument("--dia", action="store_true")
    ap.add_argument("--todos", action="store_true")
    ap.add_argument("--salida", default=f"{RAIZ}/_salida/serie")
    a = ap.parse_args()

    hechas = []
    if a.todos:
        esperadas = 0
        for fmt in ("retrato", "cuadrado"):
            hechas += carrusel(DEMO_CARRUSEL, fmt, f"{a.salida}/carrusel-{fmt}")
            esperadas += 2 + len(DEMO_CARRUSEL["laminas"])
        for fmt in ("retrato", "historia"):
            for c, _ in CUENTA:
                hechas.append(cuenta(c, fmt, f"{a.salida}/cuenta")); esperadas += 1
        for fmt in ("retrato", "cuadrado"):
            t, it = DEMO_AGENDA_DIA
            hechas.append(agenda(t, it, fmt, f"{a.salida}/agenda", "dia")); esperadas += 1
            t, it = DEMO_AGENDA_SEMANA
            hechas.append(agenda(t, it, fmt, f"{a.salida}/agenda", "semana")); esperadas += 1
        print(f"producidas {len(hechas)} de {esperadas} esperadas")
        malas = [(r, m["holgura"]) for r, m in hechas if m.get("holgura", 0) < 0]
        for r, hh in malas:
            print(f"  HOLGURA NEGATIVA {hh} px — {os.path.basename(r)}")
        if len(hechas) != esperadas or malas:
            sys.exit("la corrida no cuadra")
    elif a.tipo == "carrusel":
        g = json.load(open(a.guion, encoding="utf-8")) if a.guion else DEMO_CARRUSEL
        hechas = carrusel(g, a.formato, f"{a.salida}/carrusel-{a.formato}")
    elif a.tipo == "cuenta":
        hechas = [cuenta(c, a.formato, f"{a.salida}/cuenta") for c, _ in CUENTA]
    elif a.tipo == "agenda":
        t, it = DEMO_AGENDA_DIA if a.dia else DEMO_AGENDA_SEMANA
        hechas = [agenda(t, it, a.formato, f"{a.salida}/agenda",
                         "dia" if a.dia else "semana")]
    else:
        ap.error("hace falta --tipo o --todos")
    for r, _ in hechas:
        print(r)


if __name__ == "__main__":
    main()
