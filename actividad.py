#!/usr/bin/env python3
"""
Flyer de una actividad dentro de GEW · RD.

El papel aquí es el contrario al de campana.py: manda la marca del organizador y
el badge Official Activity entra como sello de apoyo. Es la lámina 42 de la guía
de National Hosts, con sus tres variantes:

    A · panel      cabecera blanca, retratos circulares, banda de partners
    B · sangre     una foto de fondo a sangre, texto encima
    C · partido    panel carbón a la izquierda, foto a la derecha

Uso:
    python3 actividad.py --variante A --titulo "Taller de *finanzas*" \\
        --lugar "Santo Domingo" --fecha "18 de noviembre · 6:00 pm" \\
        --fotos a.jpg b.jpg c.jpg --socios logo1.svg logo2.png
    python3 actividad.py --demo
"""
import argparse, json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

RAIZ = os.path.dirname(os.path.abspath(__file__))
TOK = json.load(open(f"{RAIZ}/tokens/tokens.json", encoding="utf-8"))
sys.path.insert(0, RAIZ)
from campana import (fuente, marca_alto, png_alto, pin, trocear, sello,  # noqa: E402
                     pulso, marcas, PARTNERS, CAP)

CARBON = TOK["color"]["campana2026"]["carbon"]["hex"]
NARANJA = TOK["color"]["campana2026"]["naranja"]["hex"]
BLANCO = "#FFFFFF"
TINTA = TOK["color"]["marca"]["carbon-wordmark"]["hex"]
GRIS = "#8A8A8A"

FORMATOS = {
    "retrato":  {"px": (1080, 1350), "unidad": 1080},
    "historia": {"px": (1080, 1920), "unidad": 1180, "segura": (269, 1670)},
    "cuadrado": {"px": (1080, 1080), "unidad": 1000},
}

R = dict(margen=0.0667, franja=0.0222, cabecera=0.1000, badge=0.1050,
         titulo=0.0880, dato=0.0280, lema=0.0210, pie=0.1250, logo=0.0430)


def hoja(fmt):
    w, h = FORMATOS[fmt]["px"]
    u = FORMATOS[fmt]["unidad"]
    return w, h, u, {k: round(v * u) for k, v in R.items()}


def cubrir(ruta, caja):
    """Recorta al centro para llenar la caja sin deformar."""
    return ImageOps.fit(Image.open(ruta).convert("RGB"), caja,
                        Image.LANCZOS, centering=(0.5, 0.42))


def circulo(ruta, d):
    im = ImageOps.fit(Image.open(ruta).convert("RGB"), (d, d), Image.LANCZOS,
                      centering=(0.5, 0.36))
    m = Image.new("L", (d * 4, d * 4), 0)
    ImageDraw.Draw(m).ellipse([0, 0, d * 4 - 1, d * 4 - 1], fill=255)
    im.putalpha(m.resize((d, d), Image.LANCZOS))
    return im


def ajustar(d, lineas, cap, util, peso="Light"):
    """Baja el cap hasta que la línea más larga entre en el ancho útil."""
    while cap > 8:
        f = fuente(peso, cap)
        if max(sum(d.textlength(t, font=f) for t, _ in tr) for tr in lineas) <= util:
            return f, cap
        cap -= 1
    return fuente(peso, cap), cap


def flyer(titulo, lugar, fecha, variante="A", fmt="retrato", fotos=None,
          organizador=None, socios=None, salida=None):
    w, h, U, g = hoja(fmt)
    m, fr = g["margen"], g["franja"]
    seg = FORMATOS[fmt].get("segura")
    TOP, BOT = seg if seg else (0, h)
    med = {"variante": variante, "formato": fmt, "px": [w, h], "zona": [TOP, BOT]}

    fotos = fotos or []
    organizador = organizador or f"{RAIZ}/logo/socios/enlata-wordmark.svg"
    # Los partners del movimiento son los DOS. Antes el defecto era sólo
    # IAvanza y Enlata sólo salía si además era el organizador.
    socios = socios if socios is not None else [f"{RAIZ}/{p}" for p in PARTNERS]
    util = w - m * 2

    im = Image.new("RGB", (w, h), BLANCO)
    d = ImageDraw.Draw(im)

    # ── franja naranja del pie, común a las tres ──────────────────────────
    d.rectangle([0, BOT - fr, w, BOT], fill=NARANJA)
    if seg:
        d.rectangle([0, 0, w, TOP], fill=BLANCO)
        d.rectangle([0, BOT, w, h], fill=BLANCO)

    alto_pie = g["pie"] if variante == "A" else round(g["pie"] * 0.62)
    y_pie = BOT - fr - alto_pie
    lineas = list(trocear(titulo))

    # ── cabecera: badge + regla + logo del organizador (solo A) ───────────
    if variante == "A":
        ancho_sello, clase = sello(im, d, m, TOP + m, g["badge"], U)
        med["sello_cabecera"] = clase
        x_regla = m + ancho_sello + round(U * 0.030)
        d.line([(x_regla, TOP + m), (x_regla, TOP + m + g["badge"])], fill="#D5D5D5", width=2)
        lg = marca_alto(organizador, round(g["badge"] * 0.92))
        im.paste(lg, (x_regla + round(U * 0.030),
                      TOP + m + (g["badge"] - lg.height) // 2), lg)
        med["cabecera_der"] = x_regla + round(U * 0.030) + lg.width
        y_p = TOP + m + g["badge"] + round(U * 0.024)
        a_p = round(U * 0.028)
        pulso(d, m, y_p, w - m * 2, a_p)
        med["pulso"] = [m, y_p, w - m, y_p + a_p]
        y = y_p + a_p + round(U * 0.038)

        med["techo_A"] = y      # los retratos se colocan más abajo, ya con el texto medido

    # ── B: foto a sangre ocupando de la cabecera al pie ───────────────────
    elif variante == "B":
        caja = (w, y_pie - TOP)
        if fotos:
            im.paste(cubrir(fotos[0], caja), (0, TOP))
        else:
            d.rectangle([0, TOP, w, y_pie], fill=CARBON)
        # velo inferior para que el texto tenga dónde apoyarse
        velo = Image.new("RGBA", (w, round(caja[1] * 0.62)), (0, 0, 0, 0))
        vd = ImageDraw.Draw(velo)
        for i in range(velo.height):
            vd.line([(0, i), (w, i)], fill=(28, 26, 26, int(232 * (i / velo.height) ** 1.5)))
        im.paste(velo, (0, y_pie - velo.height), velo)
        med["velo_alto"] = velo.height

    # ── C: panel carbón a la izquierda, foto a la derecha ─────────────────
    elif variante == "C":
        panel = round(w * 0.58)
        d.rectangle([0, TOP, panel, y_pie], fill=CARBON)
        if fotos:
            im.paste(cubrir(fotos[0], (w - panel, y_pie - TOP)), (panel, TOP))
        util = panel - m * 2
        med["panel"] = panel

    # ── título, lugar y fecha ─────────────────────────────────────────────
    claro = variante == "A"
    col = TINTA if claro else BLANCO
    f_tit, cap_tit = ajustar(d, lineas, g["titulo"], util)
    il = round(cap_tit * 1.30)
    f_dato = fuente("Light", g["dato"])
    f_lema = fuente("Light", g["lema"])

    n_datos = sum(1 for t in (lugar, fecha) if t)
    alto_txt = ((len(lineas) - 1) * il + cap_tit + round(U * 0.042)
                + round(g["dato"] * 1.42) * n_datos + round(U * 0.020) + g["lema"])

    if variante == "A":
        # el conjunto retratos + texto se reparte en el hueco, con sesgo hacia arriba
        techo = med["techo_A"]
        hueco_r = round(U * 0.030)
        n_f = min(3, len(fotos))
        diam = (util - hueco_r * (n_f - 1)) // max(1, n_f) if n_f else 0
        aire_r = round(U * 0.055) if n_f else 0
        alto_conj = diam + aire_r + alto_txt
        y0 = techo + max(0, round((y_pie - round(U * 0.055) - techo - alto_conj) * 0.50))
        for i in range(n_f):
            c = circulo(fotos[i], diam)
            im.paste(c, (m + i * (diam + hueco_r), y0), c)
        med["retrato_diam"] = diam
        med["holgura_A"] = y_pie - round(U * 0.055) - techo - alto_conj
        y = y0 + diam + aire_r
    elif variante == "C":
        y = TOP + max(m, round((y_pie - TOP - alto_txt) * 0.56))
    else:
        y = y_pie - round(U * 0.062) - alto_txt
        y = max(y, TOP + m)
    med["titulo_top"] = y

    for tr in lineas:
        x = m
        for texto, destaca in tr:
            bb = d.textbbox((0, 0), texto, font=f_tit)
            d.text((x - bb[0], y - bb[1]), texto, font=f_tit,
                   fill=NARANJA if destaca else col)
            x += d.textlength(texto, font=f_tit)
        med.setdefault("titulo_anchos", []).append(round(x - m))
        y += il
    y += round(U * 0.042) - il + cap_tit

    for linea in (lugar, fecha):
        if not linea:
            continue
        bb = d.textbbox((0, 0), linea, font=f_dato)
        d.text((m - bb[0], y - bb[1]), linea, font=f_dato,
               fill=GRIS if claro else "#DCDCDC")
        y += round(g["dato"] * 1.42)

    # lema con el pin
    y += round(U * 0.020)
    r_pin = round(g["lema"] * 0.52)
    pin_col = TOK["color"]["barra"]["hex"][0]
    pin(d, m + r_pin, y + round(g["lema"] * 0.32), r_pin, pin_col)
    # el hueco del pin se rellena con el fondo real de la variante
    d.ellipse([m + r_pin - r_pin * 0.38, y + round(g["lema"] * 0.32) - r_pin * 0.38,
               m + r_pin + r_pin * 0.38, y + round(g["lema"] * 0.32) + r_pin * 0.38],
              fill=BLANCO if claro else CARBON)
    d.text((m + r_pin * 3.1, y), TOK["campana"]["tema_es"], font=f_lema,
           fill=GRIS if claro else "#DCDCDC")
    med["lema_base"] = y + g["lema"]

    # ── pie ───────────────────────────────────────────────────────────────
    d.rectangle([0, y_pie, w, BOT - fr], fill=BLANCO)
    f_rot = fuente("Bold", round(U * 0.0130))
    if variante == "A":
        # los tres bloques del movimiento, desde la biblioteca compartida
        med["marcas"] = marcas(im, d, m, y_pie + round(U * 0.026), w - m * 2, U,
                               alto_logo=g["logo"], partners=list(socios[:4]))
        med["pie_der"] = med["marcas"]["derecha"]
    else:
        # badge a la izquierda, logo del organizador a la derecha
        h_sello = round(alto_pie * 0.62)
        _, clase = sello(im, d, m, y_pie + (alto_pie - h_sello) // 2, h_sello, U)
        med["sello_pie"] = clase
        lg = marca_alto(organizador, round(alto_pie * 0.52))
        im.paste(lg, (w - m - lg.width, y_pie + (alto_pie - lg.height) // 2), lg)
        med["pie_logo"] = [lg.width, lg.height]

    med["holgura_pie"] = y_pie - med["lema_base"]
    if salida:
        os.makedirs(os.path.dirname(salida), exist_ok=True)
        im.save(salida)
    return im, med


def main():
    ap = argparse.ArgumentParser(description="Flyer de actividad GEW · RD")
    ap.add_argument("--variante", choices=["A", "B", "C"], default="A")
    ap.add_argument("--formato", choices=list(FORMATOS), default="retrato")
    ap.add_argument("--titulo", default="Título de *tu actividad*")
    ap.add_argument("--lugar", default="")
    ap.add_argument("--fecha", default="")
    ap.add_argument("--fotos", nargs="*", default=[])
    ap.add_argument("--organizador")
    ap.add_argument("--socios", nargs="*")
    ap.add_argument("--demo", action="store_true", help="las 3 variantes en los 3 formatos")
    ap.add_argument("--salida", default=f"{RAIZ}/_salida/actividad")
    a = ap.parse_args()

    if a.demo:
        # Las fotos de muestra no viven en el repositorio: son de eventos reales, con
        # caras de gente a la que nadie preguntó. `GEW_FOTOS` dice dónde están; sin esa
        # variable se usan las de `_salida/demo/fotos`, que son sintéticas.
        F = os.environ.get("GEW_FOTOS", os.path.join(RAIZ, "_salida", "demo", "fotos"))
        demo = dict(
            A=("Taller de *finanzas*", "Universidad Demo · Santo Domingo", "18 de noviembre · 6:00 pm",
               [f"{F}/v-tarima.webp", f"{F}/v-acreditacion.webp", f"{F}/v-detalles.webp"]),
            B=("Encuentro *semanal*", "Sala Demo · Ciudad", "17 de noviembre · 7:00 pm",
               [f"{F}/v-publico.webp"]),
            C=("Competencia Demo · *final*", "Teatro Demo", "21 de noviembre · 5:00 pm",
               [f"{F}/v-tarima.webp"]),
        )
        hechas, esperadas = [], len(demo) * len(FORMATOS)
        for v, (t, l, f_, ph) in demo.items():
            for fmt in FORMATOS:
                r = f"{a.salida}/demo-{v}--{fmt}.png"
                _, mm = flyer(t, l, f_, v, fmt, ph, salida=r)
                hechas.append((r, mm))
        print(f"producidas {len(hechas)} de {esperadas} esperadas")
        malas = [(r, mm["holgura_pie"]) for r, mm in hechas if mm["holgura_pie"] < 0]
        for r, hh in malas:
            print(f"  HOLGURA NEGATIVA {hh} px — {os.path.basename(r)}")
        for r, _ in hechas:
            print(r)
        if malas:
            sys.exit(f"{len(malas)} pieza(s) con el texto pisando el pie")
    else:
        r = f"{a.salida}/flyer-{a.variante}--{a.formato}.png"
        _, mm = flyer(a.titulo, a.lugar, a.fecha, a.variante, a.formato, a.fotos,
                      a.organizador, a.socios, salida=r)
        print(json.dumps(mm, ensure_ascii=False))
        print(r)


if __name__ == "__main__":
    main()
