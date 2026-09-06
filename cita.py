#!/usr/bin/env python3
"""
Plantilla de cita · GEW · RD.

Es la lámina 45 de la guía de Event Organizers: «These templates can be adapted
to showcase an individual's leadership or profile in your community. Add their
photo, title, and a quote related to the campaign goals.»

Entradas: foto, nombre, cargo y cita. Dos variantes:

    panel     foto en la columna derecha, cita en el panel carbón
    apilada   foto arriba a sangre, cita debajo

Uso:
    python3 cita.py --cita "El primer cliente fue mi vecina." \\
        --nombre "Nombre Apellido" --cargo "Fundadora, Organización" --foto retrato.jpg
    python3 cita.py --demo
"""
import argparse, json, os, sys
from PIL import Image, ImageDraw, ImageOps

RAIZ = os.path.dirname(os.path.abspath(__file__))
TOK = json.load(open(f"{RAIZ}/tokens/tokens.json", encoding="utf-8"))
sys.path.insert(0, RAIZ)
from campana import fuente, marca_alto, png_alto, sello, pulso  # noqa: E402

CARBON = TOK["color"]["campana2026"]["carbon"]["hex"]
NARANJA = TOK["color"]["campana2026"]["naranja"]["hex"]
BLANCO = "#FFFFFF"
GRIS = "#C6C6C6"

FORMATOS = {
    "retrato":  {"px": (1080, 1350), "unidad": 1080},
    "historia": {"px": (1080, 1920), "unidad": 1180, "segura": (269, 1670)},
    "cuadrado": {"px": (1080, 1080), "unidad": 1000},
    "enlace":   {"px": (1200, 627), "unidad": 800},
}

R = dict(margen=0.0667, franja=0.0222, comillas=0.1150, cita=0.0480,
         nombre=0.0300, cargo=0.0225, pie=0.0950)


def hoja(fmt):
    w, h = FORMATOS[fmt]["px"]
    u = FORMATOS[fmt]["unidad"]
    return w, h, u, {k: round(v * u) for k, v in R.items()}


def cubrir(ruta, caja, centrado=(0.5, 0.32)):
    return ImageOps.fit(Image.open(ruta).convert("RGB"), caja, Image.LANCZOS,
                        centering=centrado)


def envolver(d, texto, font, ancho):
    """Parte el texto en líneas que quepan en `ancho`."""
    lineas, act = [], ""
    for palabra in texto.split():
        prueba = (act + " " + palabra).strip()
        if d.textlength(prueba, font=font) <= ancho or not act:
            act = prueba
        else:
            lineas.append(act)
            act = palabra
    if act:
        lineas.append(act)
    return lineas


def cita(texto, nombre, cargo, foto=None, variante="panel", fmt="retrato",
         organizador=None, salida=None):
    w, h, U, g = hoja(fmt)
    m, fr = g["margen"], g["franja"]
    seg = FORMATOS[fmt].get("segura")
    TOP, BOT = seg if seg else (0, h)
    med = {"variante": variante, "formato": fmt, "px": [w, h], "zona": [TOP, BOT]}
    organizador = organizador or f"{RAIZ}/logo/socios/enlata-wordmark.svg"

    im = Image.new("RGB", (w, h), CARBON)
    d = ImageDraw.Draw(im)
    if seg:
        d.rectangle([0, 0, w, TOP], fill=BLANCO)
        d.rectangle([0, BOT, w, h], fill=BLANCO)

    # con zona segura el pie va a sangre: la banda acaba en el borde de la zona
    # y la franja baja al filo del lienzo, como en campana.py
    alto_pie = g["pie"]
    # el sello se ata al alto del pie, no a la unidad: así no se queda enano
    # en los formatos apaisados, donde la unidad es pequeña
    g["badge"] = round(alto_pie * 0.66)
    base_pie = BOT if seg else BOT - fr
    y_pie = base_pie - alto_pie
    d.rectangle([0, y_pie, w, base_pie], fill=BLANCO)
    d.rectangle([0, (h - fr) if seg else (BOT - fr), w, h if seg else BOT], fill=NARANJA)
    med["pie_sangre"] = bool(seg)

    # ── la foto ───────────────────────────────────────────────────────────
    if variante == "panel":
        col = round(w * 0.40)
        x_foto = w - col
        if foto:
            im.paste(cubrir(foto, (col, y_pie - TOP)), (x_foto, TOP))
        util = x_foto - m * 2
        med["columna_foto"] = col
    else:  # apilada
        alto_foto = round((y_pie - TOP) * 0.44)
        if foto:
            im.paste(cubrir(foto, (w, alto_foto), (0.5, 0.30)), (0, TOP))
        util = w - m * 2
        med["alto_foto"] = alto_foto

    # ── las comillas ──────────────────────────────────────────────────────
    f_com = fuente("Bold", g["comillas"])
    y = (TOP + m) if variante == "panel" else (TOP + alto_foto + round(U * 0.040))
    # el pulso, la firma del movimiento, sobre el pie
    a_p = round(U * 0.026)
    pulso(d, m, y_pie - round(U * 0.030) - a_p, w - m * 2, a_p)
    med["pulso"] = [m, y_pie - round(U * 0.030) - a_p, w - m, y_pie - round(U * 0.030)]
    bb = d.textbbox((0, 0), "“", font=f_com)
    d.text((m - bb[0], y - bb[1]), "“", font=f_com, fill=NARANJA)
    y += round(g["comillas"] * 0.62)
    med["comillas_top"] = y

    # ── la cita: se ajusta hasta caber en el hueco disponible ─────────────
    tope = y_pie - round(U * 0.055) - (g["nombre"] + g["cargo"] + round(U * 0.030))
    cap = g["cita"]
    while cap > 10:
        f_cita = fuente("Light", cap)
        lns = envolver(d, texto, f_cita, util)
        if y + len(lns) * round(cap * 1.42) <= tope:
            break
        cap -= 1
    med["cap_cita"] = [cap, g["cita"]]
    med["lineas_cita"] = len(lns)
    for ln in lns:
        bb = d.textbbox((0, 0), ln, font=f_cita)
        d.text((m - bb[0], y - bb[1]), ln, font=f_cita, fill=BLANCO)
        y += round(cap * 1.42)

    # ── nombre y cargo, anclados sobre el pie ─────────────────────────────
    f_nom = fuente("Bold", g["nombre"])
    f_car = fuente("Light", g["cargo"])
    y_nom = y_pie - round(U * 0.050) - g["cargo"] - round(U * 0.014) - g["nombre"]
    bb = d.textbbox((0, 0), nombre, font=f_nom)
    d.text((m - bb[0], y_nom - bb[1]), nombre, font=f_nom, fill=BLANCO)
    if cargo:
        bb = d.textbbox((0, 0), cargo, font=f_car)
        d.text((m - bb[0], y_nom + g["nombre"] + round(U * 0.014) - bb[1]),
               cargo, font=f_car, fill=GRIS)
    med["holgura_cita"] = y_nom - y

    # ── pie: sello GEW + logo del organizador ─────────────────────────────
    # Por debajo de 70 px de alto el badge completo no se lee: sus cuatro líneas
    # de texto desaparecen. Ahí va el anillo con el reconocimiento en tipografía,
    # que es la misma regla que sigue enlata.do/gew.
    _, med["sello"] = sello(im, d, m, y_pie + (alto_pie - g["badge"]) // 2,
                            g["badge"], U)
    lg = marca_alto(organizador, round(g["badge"] * 0.86))
    im.paste(lg, (w - m - lg.width, y_pie + (alto_pie - lg.height) // 2), lg)
    med["pie_logo_ancho"] = lg.width

    if salida:
        os.makedirs(os.path.dirname(salida), exist_ok=True)
        im.save(salida)
    return im, med


def main():
    ap = argparse.ArgumentParser(description="Plantilla de cita GEW · RD")
    ap.add_argument("--cita", default="Aquí los emprendedores prosperan.")
    ap.add_argument("--nombre", default="Nombre Apellido")
    ap.add_argument("--cargo", default="Cargo, organización")
    ap.add_argument("--foto")
    ap.add_argument("--variante", choices=["panel", "apilada"], default="panel")
    ap.add_argument("--formato", choices=list(FORMATOS), default="retrato")
    ap.add_argument("--organizador")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--salida", default=f"{RAIZ}/_salida/cita")
    a = ap.parse_args()

    if a.demo:
        # Las fotos de muestra no viven en el repositorio: son de eventos reales, con
        # caras de gente a la que nadie preguntó. `GEW_FOTOS` dice dónde están; sin esa
        # variable se usan las de `_salida/demo/fotos`, que son sintéticas.
        F = os.environ.get("GEW_FOTOS", os.path.join(RAIZ, "_salida", "demo", "fotos"))
        demo = [
            ("panel", "El primer cliente fue mi vecina. El segundo, su hermana. "
                      "Así empieza casi todo aquí.", "Nombre Apellido",
             "Fundadora · Organización", f"{F}/v-acreditacion.webp"),
            ("apilada", "Nadie me dijo que se podía. Lo descubrí viendo a alguien "
                        "parecido a mí hacerlo primero.", "Nombre Apellido",
             "Champion · IA Datos", f"{F}/v-tarima.webp"),
        ]
        hechas, esperadas = [], len(demo) * len(FORMATOS)
        for v, t, n, c, ph in demo:
            for fmt in FORMATOS:
                r = f"{a.salida}/demo-{v}--{fmt}.png"
                _, mm = cita(t, n, c, ph, v, fmt, salida=r)
                hechas.append((r, mm))
        print(f"producidas {len(hechas)} de {esperadas} esperadas")
        malas = [(r, mm["holgura_cita"]) for r, mm in hechas if mm["holgura_cita"] < 0]
        for r, hh in malas:
            print(f"  HOLGURA NEGATIVA {hh} px — {os.path.basename(r)}")
        for r, _ in hechas:
            print(r)
        if malas:
            sys.exit(f"{len(malas)} pieza(s) con la cita pisando el nombre")
    else:
        r = f"{a.salida}/cita-{a.variante}--{a.formato}.png"
        _, mm = cita(a.cita, a.nombre, a.cargo, a.foto, a.variante, a.formato,
                     a.organizador, salida=r)
        print(json.dumps(mm, ensure_ascii=False))
        print(r)


if __name__ == "__main__":
    main()
