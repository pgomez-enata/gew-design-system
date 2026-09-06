#!/usr/bin/env python3
"""
Piezas de imprenta · GEW · RD.

    credencial   gafete de 10 × 14 cm, se genera en lote desde la lista
    certificado  carta apaisada, participación o reconocimiento
    rollup       banner vertical de 85 × 200 cm
    backdrop     fondo de escenario, por defecto 3 × 2,4 m

Aquí no se trabaja en píxeles sueltos: cada pieza se define en centímetros y a
una resolución declarada, con su sangrado. El fichero sale con las marcas de
corte en una capa aparte (`--marcas`) para que la imprenta las vea y el arte
limpio no las lleve.

⚠️ El lockup dominicano NO tiene vector: su tinta mide 3377 × 1173 px. En gran
formato eso pone un techo real al tamaño al que se puede poner. El motor lo
calcula y AVISA cuando el logo se queda por debajo de la resolución pedida.

Uso:
    python3 impreso.py --tipo credencial --nombre "Nombre Apellido" --org "Organización"
    python3 impreso.py --tipo certificado --nombre "Nombre Apellido"
    python3 impreso.py --tipo rollup
    python3 impreso.py --todos
"""
import argparse, csv, json, math, os, sys
from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.abspath(__file__))
TOK = json.load(open(f"{RAIZ}/tokens/tokens.json", encoding="utf-8"))
sys.path.insert(0, RAIZ)
from campana import (fuente, marca_alto, png_alto, pin, trocear, pulso,  # noqa: E402
                     activo)

CARBON = TOK["color"]["campana2026"]["carbon"]["hex"]
NARANJA = TOK["color"]["campana2026"]["naranja"]["hex"]
BLANCO = "#FFFFFF"
TINTA = TOK["color"]["marca"]["carbon-wordmark"]["hex"]
GRIS = "#8A8A8A"

# tinta real del lockup dominicano, medida sobre el PNG normalizado
LOGO_TINTA_PX = 3377

PIEZAS = {
    # cm_ancho, cm_alto, dpi, sangrado_mm
    "credencial":  (10.0, 14.0, 300, 3),
    "certificado": (27.94, 21.59, 300, 3),      # carta apaisada
    "rollup":      (85.0, 200.0, 100, 20),
    "backdrop":    (300.0, 240.0, 100, 50),
}


def px(cm, dpi):
    return round(cm / 2.54 * dpi)


def lienzo(tipo, dpi=None, cm=None):
    a_cm, h_cm, dpi_def, sang_mm = PIEZAS[tipo]
    if cm:
        a_cm, h_cm = cm
    dpi = dpi or dpi_def
    sang = round(sang_mm / 10 / 2.54 * dpi)
    w, h = px(a_cm, dpi) + sang * 2, px(h_cm, dpi) + sang * 2
    return w, h, sang, dpi, a_cm, h_cm


def logo_maximo(ancho_util, dpi):
    """Hasta qué ancho se puede poner el lockup sin bajar de la resolución."""
    return LOGO_TINTA_PX, LOGO_TINTA_PX / ancho_util


def marcas(d, w, h, sang, U):
    """Marcas de corte fuera del área de sangrado."""
    lg = round(sang * 0.62)
    gr = max(1, round(U * 0.0012))
    for x in (sang, w - sang):
        d.line([(x, 0), (x, lg)], fill="#000000", width=gr)
        d.line([(x, h - lg), (x, h)], fill="#000000", width=gr)
    for y in (sang, h - sang):
        d.line([(0, y), (lg, y)], fill="#000000", width=gr)
        d.line([(w - lg, y), (w, y)], fill="#000000", width=gr)


def credencial(nombre, org="", rol="", con_marcas=False, salida=None):
    w, h, sang, dpi, a_cm, h_cm = lienzo("credencial")
    U = w - sang * 2
    m = round(U * 0.090)
    im = Image.new("RGB", (w, h), BLANCO)
    d = ImageDraw.Draw(im)
    med = {"tipo": "credencial", "cm": [a_cm, h_cm], "dpi": dpi, "px": [w, h],
           "sangrado_px": sang}

    # cabecera carbón hasta el sangrado
    cab = sang + round((h - sang * 2) * 0.30)
    d.rectangle([0, 0, w, cab], fill=CARBON)
    pulso(d, 0, cab, w, round(U * 0.016))          # credencial: bajo la cabecera
    lock = png_alto(f"{RAIZ}/logo/gew-rd-lockup-blanco.png", round(U * 0.150))
    im.paste(lock, ((w - lock.width) // 2, sang + round(U * 0.075)), lock)

    # el nombre, ajustado al ancho útil
    util = w - sang * 2 - m * 2
    cap = round(U * 0.115)
    lineas = nombre.split(" ", 1) if len(nombre) > 16 else [nombre]
    while cap > 14:
        f = fuente("Bold", cap)
        if max(d.textlength(l, font=f) for l in lineas) <= util:
            break
        cap -= 1
    y = cab + round(U * 0.130)
    for l in lineas:
        bb = d.textbbox((0, 0), l, font=f)
        d.text(((w - (bb[2] - bb[0])) // 2 - bb[0], y - bb[1]), l, font=f, fill=TINTA)
        y += round(cap * 1.24)
    med["cap_nombre"] = cap

    for texto, cap_, col in ((org, round(U * 0.052), GRIS),
                             (rol, round(U * 0.044), NARANJA)):
        if not texto:
            continue
        f2 = fuente("Light" if col == GRIS else "Bold", cap_)
        bb = d.textbbox((0, 0), texto, font=f2)
        d.text(((w - (bb[2] - bb[0])) // 2 - bb[0], y + round(U * 0.020) - bb[1]),
               texto, font=f2, fill=col)
        y += cap_ + round(U * 0.030)

    # pie
    f3 = fuente("Light", round(U * 0.036))
    t = TOK["campana"]["fechas"]
    bb = d.textbbox((0, 0), t, font=f3)
    d.text(((w - (bb[2] - bb[0])) // 2 - bb[0], h - sang - round(U * 0.105) - bb[1]),
           t, font=f3, fill=TINTA)
    pulso(d, 0, h - sang - round(U * 0.030), w, round(U * 0.030))   # credencial: pie
    med["holgura"] = (h - sang - round(U * 0.115)) - y

    if con_marcas:
        marcas(d, w, h, sang, U)
    if salida:
        os.makedirs(os.path.dirname(salida), exist_ok=True)
        im.save(salida, dpi=(dpi, dpi))
    return im, med


def reconocimiento(nombre, rol="ponente", org="", texto=None, con_marcas=False,
                   salida=None):
    """Reconocimiento a quien puso el contenido. Es el certificado con otro
    encabezado y un renglón más: el papel y la organización de quien lo recibe.
    Se le da a ponentes, moderadores y a quien prestó la sede.

    No es un certificado de participación con otro título: al ponente se le
    reconoce lo que hizo, y eso va escrito."""
    por_defecto = {
        "ponente": "por compartir lo que sabe con quien está empezando",
        "moderador": "por conducir la conversación y dejar hablar a todos",
        "jurado": "por evaluar con criterio y devolver algo útil",
        "sede": "por abrir sus puertas a la Semana Global de Emprendimiento",
        "mentor": "por sentarse a resolver problemas ajenos como si fueran suyos",
    }
    txt = texto or por_defecto.get(rol, por_defecto["ponente"])
    return certificado(nombre, texto=txt, tipo=f"reconocimiento · {rol}",
                       con_marcas=con_marcas, salida=salida, org=org,
                       encabezado="RECONOCIMIENTO")


def certificado(nombre, texto=None, tipo="participación", con_marcas=False,
                salida=None, org="", encabezado=None):
    w, h, sang, dpi, a_cm, h_cm = lienzo("certificado")
    U = w - sang * 2
    m = round(U * 0.095)
    im = Image.new("RGB", (w, h), BLANCO)
    d = ImageDraw.Draw(im)
    med = {"tipo": "reconocimiento" if encabezado else "certificado",
           "cm": [a_cm, h_cm], "dpi": dpi, "px": [w, h], "sangrado_px": sang,
           "rol": tipo}

    pulso(d, 0, 0, w, sang + round(U * 0.020))     # certificado: arriba y abajo
    pulso(d, 0, h - sang - round(U * 0.020), w, round(U * 0.020))
    lock = png_alto(f"{RAIZ}/logo/gew-rd-lockup-color.png", round(U * 0.075))
    im.paste(lock, ((w - lock.width) // 2, sang + round(U * 0.055)), lock)

    y = sang + round(U * 0.055) + lock.height + round(U * 0.060)
    f_r = fuente("Bold", round(U * 0.021))
    t = encabezado or f"CERTIFICADO DE {tipo.upper()}"
    bb = d.textbbox((0, 0), t, font=f_r)
    d.text(((w - (bb[2] - bb[0])) // 2 - bb[0], y - bb[1]), t, font=f_r, fill=NARANJA)
    y += round(U * 0.021) + round(U * 0.045)

    f_a = fuente("Light", round(U * 0.026))
    t = "Se otorga a"
    bb = d.textbbox((0, 0), t, font=f_a)
    d.text(((w - (bb[2] - bb[0])) // 2 - bb[0], y - bb[1]), t, font=f_a, fill=GRIS)
    y += round(U * 0.026) + round(U * 0.030)

    cap = round(U * 0.078)
    while cap > 18:
        f_n = fuente("Light", cap)
        if d.textlength(nombre, font=f_n) <= w - sang * 2 - m * 2:
            break
        cap -= 1
    bb = d.textbbox((0, 0), nombre, font=f_n)
    d.text(((w - (bb[2] - bb[0])) // 2 - bb[0], y - bb[1]), nombre, font=f_n, fill=TINTA)
    y += cap + round(U * 0.022)
    if org:
        f_o = fuente("Bold", round(U * 0.026))
        bb = d.textbbox((0, 0), org, font=f_o)
        d.text(((w - (bb[2] - bb[0])) // 2 - bb[0], y - bb[1]), org, font=f_o,
               fill=NARANJA)
        y += round(U * 0.026) + round(U * 0.016)
    d.line([((w - round(U * 0.42)) // 2, y), ((w + round(U * 0.42)) // 2, y)],
           fill=NARANJA, width=max(2, round(U * 0.0035)))
    y += round(U * 0.045)
    med["cap_nombre"] = cap
    med["con_org"] = bool(org)

    cuerpo = texto or (f"por su participación en la Semana Global de Emprendimiento "
                       f"{TOK['campana']['anio']} en República Dominicana, celebrada "
                       f"del {TOK['campana']['fechas']}.")
    y_firmas = h - sang - round(U * 0.135)
    hueco = y_firmas - round(U * 0.045) - y
    cap_c = round(U * 0.026)
    while cap_c > 10:
        f_c = fuente("Light", cap_c)
        palabras_, ln, lns = cuerpo.split(), "", []
        for p in palabras_:
            t2 = (ln + " " + p).strip()
            if d.textlength(t2, font=f_c) <= round(U * 0.72) or not ln:
                ln = t2
            else:
                lns.append(ln); ln = p
        if ln:
            lns.append(ln)
        if len(lns) * round(cap_c * 1.5) <= hueco:
            break
        cap_c -= 1
    med["cap_cuerpo"] = [cap_c, round(U * 0.026)]
    for l in lns:
        bb = d.textbbox((0, 0), l, font=f_c)
        d.text(((w - (bb[2] - bb[0])) // 2 - bb[0], y - bb[1]), l, font=f_c, fill=TINTA)
        y += round(cap_c * 1.5)

    # firmas
    y_f = y_firmas
    f_fi = fuente("Light", round(U * 0.019))
    for cx, quien, cargo in ((round(w * 0.30), "{{NOMBRE}}", "Presidente · Fundación Enlata"),
                             (round(w * 0.70), "", "Partner · GEW República Dominicana")):
        d.line([(cx - round(U * 0.13), y_f), (cx + round(U * 0.13), y_f)],
               fill="#C0C0C0", width=max(1, round(U * 0.0016)))
        if quien:
            bb = d.textbbox((0, 0), quien, font=f_fi)
            d.text((cx - (bb[2] - bb[0]) // 2 - bb[0], y_f + round(U * 0.016) - bb[1]),
                   quien, font=f_fi, fill=TINTA)
        bb = d.textbbox((0, 0), cargo, font=f_fi)
        d.text((cx - (bb[2] - bb[0]) // 2 - bb[0],
                y_f + round(U * 0.016) + (round(U * 0.026) if quien else 0) - bb[1]),
               cargo, font=f_fi, fill=GRIS)
    med["holgura"] = y_f - round(U * 0.030) - y

    if con_marcas:
        marcas(d, w, h, sang, U)
    if salida:
        os.makedirs(os.path.dirname(salida), exist_ok=True)
        im.save(salida, dpi=(dpi, dpi))
    return im, med


def gran_formato(tipo, titular="Aquí los emprendedores *prosperan*",
                 con_marcas=False, cm=None, salida=None):
    w, h, sang, dpi, a_cm, h_cm = lienzo(tipo, cm=cm)
    U = min(w, h)
    m = round(U * 0.080)
    im = Image.new("RGB", (w, h), CARBON)
    d = ImageDraw.Draw(im)
    med = {"tipo": tipo, "cm": [a_cm, h_cm], "dpi": dpi, "px": [w, h],
           "sangrado_px": sang}

    pulso(d, 0, h - sang - round(U * 0.030), w, round(U * 0.030))   # gran formato: pie

    # el lockup, tan grande como permita su resolución
    util = w - sang * 2 - m * 2
    ancho_logo = min(round(util * 0.86), LOGO_TINTA_PX)
    alto_logo = round(ancho_logo / 2.928)
    # por `activo()`, no directo: si el logo no está se usa el de ejemplo/, y
    # si tampoco, el mensaje dice qué falta en vez de soltar un traceback
    lock = Image.open(activo("logo/gew-rd-lockup-blanco.png")).convert("RGBA")
    lock = lock.resize((ancho_logo, round(lock.height * ancho_logo / lock.width)),
                       Image.LANCZOS)
    dpi_logo = LOGO_TINTA_PX / (ancho_logo / dpi)
    med["logo_ancho_px"] = ancho_logo
    med["logo_dpi_efectivo"] = round(dpi_logo)
    med["logo_pct_del_ancho"] = round(100 * ancho_logo / (w - sang * 2))
    # medio punto de tolerancia: si no, el redondeo dispara un falso positivo
    cm_max = LOGO_TINTA_PX / dpi * 2.54
    med["logo_cm_max_a_dpi"] = round(cm_max, 1)
    med["aviso_logo"] = None if dpi_logo >= dpi - 0.5 else (
        f"el lockup queda a {round(dpi_logo)} dpi, por debajo de los {dpi} pedidos; "
        f"a {dpi} dpi su ancho máximo es {cm_max:.1f} cm")

    # el bloque se reparte en la zona útil en vez de anclarse arriba: en un
    # roll-up de 2 m, anclarlo dejaba media pieza vacía
    bd_prev = round(U * 0.105)
    techo = sang + round((h - sang * 2) * 0.06)
    suelo = h - sang - round(U * 0.030) - bd_prev - round(U * 0.040)
    f_prev = fuente("Light", round(U * 0.062))
    alto_bloque = (lock.height + round(U * 0.080)
                   + round(U * 0.115) * 2.2 + round(U * 0.060)
                   + (round(U * 0.062) + round(U * 0.028)) * 2)
    y = techo + max(0, round((suelo - techo - alto_bloque) * 0.40))
    med["holgura_bloque"] = suelo - techo - alto_bloque
    im.paste(lock, ((w - lock.width) // 2, y), lock)
    y += lock.height + round(U * 0.080)

    # titular
    lineas = list(trocear(titular))
    cap = round(U * 0.115)
    while cap > 20:
        f = fuente("Light", cap)
        if max(sum(d.textlength(t, font=f) for t, _ in tr) for tr in lineas) <= util:
            break
        cap -= 2
    il = round(cap * 1.28)
    for tr in lineas:
        an = sum(d.textlength(t, font=f) for t, _ in tr)
        x = (w - an) // 2
        for t, dest in tr:
            bb = d.textbbox((0, 0), t, font=f)
            d.text((x - bb[0], y - bb[1]), t, font=f, fill=NARANJA if dest else BLANCO)
            x += d.textlength(t, font=f)
        y += il
    y += round(U * 0.060) - il + cap
    med["cap_titular"] = cap

    f_f = fuente("Light", round(U * 0.062))
    for texto, col in ((TOK["campana"]["fechas"], BLANCO),
                       (TOK["campana"]["sitio"], NARANJA)):
        bb = d.textbbox((0, 0), texto, font=f_f)
        d.text(((w - (bb[2] - bb[0])) // 2 - bb[0], y - bb[1]), texto, font=f_f, fill=col)
        y += round(U * 0.062) + round(U * 0.028)

    # banda de logos abajo
    bd = round(U * 0.105)
    base = h - sang - round(U * 0.030)
    d.rectangle([0, base - bd, w, base], fill=BLANCO)
    alto_l = round(bd * 0.42)
    lg = marca_alto(f"{RAIZ}/logo/socios/enlata-wordmark.svg", alto_l)
    ls = marca_alto(f"{RAIZ}/logo/socios/iavanza-lockup.svg", alto_l)
    hueco = round(U * 0.060)
    x0 = (w - (lg.width + hueco + ls.width)) // 2
    yl = base - bd + (bd - alto_l) // 2
    im.paste(lg, (x0, yl), lg)
    im.paste(ls, (x0 + lg.width + hueco, yl), ls)
    med["holgura"] = (base - bd - round(U * 0.040)) - y

    if con_marcas:
        marcas(d, w, h, sang, U)
    if salida:
        os.makedirs(os.path.dirname(salida), exist_ok=True)
        im.save(salida, dpi=(dpi, dpi))
    return im, med


def main():
    ap = argparse.ArgumentParser(description="Piezas de imprenta GEW · RD")
    ap.add_argument("--tipo", choices=list(PIEZAS))
    ap.add_argument("--nombre", default="Nombre Apellido")
    ap.add_argument("--org", default="")
    ap.add_argument("--rol", default="")
    ap.add_argument("--lista", help="CSV con nombre,org,rol para generar en lote")
    ap.add_argument("--reconocimiento", metavar="ROL",
                    help="ponente | moderador | jurado | sede | mentor")
    ap.add_argument("--marcas", action="store_true", help="añade las marcas de corte")
    ap.add_argument("--todos", action="store_true")
    ap.add_argument("--salida", default=f"{RAIZ}/_salida/impreso")
    a = ap.parse_args()

    hechas = []
    if a.todos:
        hechas.append(("credencial", *credencial("Nombre Apellido", "Organización",
                                                 "PONENTE", a.marcas,
                                                 f"{a.salida}/credencial.png")[1:]))
        hechas.append(("certificado", *certificado("Nombre Apellido", con_marcas=a.marcas,
                                                   salida=f"{a.salida}/certificado.png")[1:]))
        hechas.append(("reconocimiento",
                       *reconocimiento("Nombre Apellido", "ponente", "Organización",
                                       con_marcas=a.marcas,
                                       salida=f"{a.salida}/reconocimiento.png")[1:]))
        for t in ("rollup", "backdrop"):
            hechas.append((t, *gran_formato(t, con_marcas=a.marcas,
                                            salida=f"{a.salida}/{t}.png")[1:]))
        print(f"producidas {len(hechas)} de 5 esperadas")
        for t, med in hechas:
            aviso = med.get("aviso_logo")
            print(f"  {t:12s} {med['cm'][0]:g}×{med['cm'][1]:g} cm @ {med['dpi']} dpi "
                  f"= {med['px'][0]}×{med['px'][1]} px  holgura {med['holgura']}")
            if aviso:
                print(f"    AVISO  {aviso}")
        malas = [t for t, m in hechas if m["holgura"] < 0]
        if malas:
            sys.exit(f"holgura negativa en: {', '.join(malas)}")
    elif a.lista:
        with open(a.lista, encoding="utf-8") as f:
            filas = list(csv.DictReader(f))
        for i, fila in enumerate(filas):
            r = f"{a.salida}/lote/{i:03d}-{a.tipo}.png"
            if a.tipo == "credencial":
                credencial(fila["nombre"], fila.get("org", ""), fila.get("rol", ""),
                           a.marcas, r)
            else:
                certificado(fila["nombre"], con_marcas=a.marcas, salida=r)
            hechas.append(r)
        print(f"producidas {len(hechas)} de {len(filas)} esperadas")
        if len(hechas) != len(filas):
            sys.exit("faltan salidas")
    elif a.tipo in ("credencial", "certificado"):
        f = credencial if a.tipo == "credencial" else certificado
        args = ((a.nombre, a.org, a.rol) if a.tipo == "credencial" else (a.nombre,))
        _, med = f(*args, con_marcas=a.marcas, salida=f"{a.salida}/{a.tipo}.png")
        print(json.dumps(med, ensure_ascii=False))
    elif a.tipo:
        _, med = gran_formato(a.tipo, con_marcas=a.marcas,
                              salida=f"{a.salida}/{a.tipo}.png")
        print(json.dumps(med, ensure_ascii=False))
    else:
        ap.error("hace falta --tipo o --todos")


if __name__ == "__main__":
    main()
