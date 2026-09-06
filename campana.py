#!/usr/bin/env python3
"""
Pieza social de la campaña nacional GEW · RD.

El papel aquí es el de National Host: GEW es la marca primaria y Enlata e
IAvanza van en la banda del pie. Es la plantilla de las láminas 20, 24, 28,
32, 36 y 40 de la guía de National Hosts.

Uso:
    python3 campana.py --audiencia publico --pieza 0
    python3 campana.py --todas
    python3 campana.py --audiencia nextgen --pieza 1 --formato historia
    python3 campana.py --titular "Tu *idea* cuenta" --remate "Empieza hoy."
"""
import argparse, json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.abspath(__file__))
TOK = json.load(open(f"{RAIZ}/tokens/tokens.json", encoding="utf-8"))
CONT = json.load(open(f"{RAIZ}/contenido/campana.json", encoding="utf-8"))

CARBON = TOK["color"]["campana2026"]["carbon"]["hex"]
NARANJA = TOK["color"]["campana2026"]["naranja"]["hex"]
BLANCO = "#FFFFFF"
TINTA = TOK["color"]["marca"]["carbon-wordmark"]["hex"]
CAP = TOK["tipografia"]["cap_ratio_render"]          # 0.725 — el de render, no el de la tabla

FUENTE = {p: f"{RAIZ}/fuentes/VAGRoundedStd{p}.ttf" for p in ("Thin", "Light", "Bold", "Black")}

# Todo se expresa en fracciones del ancho: la pieza escala sin tocar números.
# `escala` multiplica la retícula tipográfica: la retícula va en fracciones del
# ancho, así que sin esto un 9:16 sale con todo diminuto y un 16:9 con todo enorme.
# `segura` es la franja vertical donde la interfaz de la app no tapa nada.
#   ⚠️ Meta NO documenta zona segura para Stories ORGÁNICAS. La única cifra oficial
#   es de las specs de ANUNCIOS (14 % arriba = 269 px, 35 % abajo = 672 px sobre
#   1080×1920). El 35 % inferior reserva sitio para el CTA de un anuncio; en
#   orgánico ahí sólo hay la barra de responder. Por eso hay dos perfiles.
FORMATOS = {
    "retrato":    {"px": (1080, 1350), "escala": 1.00, "segura": None,
                   "uso": "Instagram feed 4:5 · LinkedIn"},
    "historia":   {"px": (1080, 1920), "escala": 1.45, "segura": (269, 1670),
                   "pie": "sangre", "reflow": True,
                   "uso": "Stories y estado de WhatsApp · margen orgánico"},
    "historia-abierta": {"px": (1080, 1920), "escala": 1.55, "segura": (269, 1670),
                   "pie": "sangre", "logos_sobre_carbon": True, "reflow": True,
                   "uso": "Stories sin banda blanca · logos en blanco sobre el carbón"},
    "historia-ads": {"px": (1080, 1920), "escala": 1.45, "segura": (269, 1248),
                   "reflow": True,
                   "uso": "Stories como anuncio · zona segura oficial de Meta"},
    "cuadrado":   {"px": (1080, 1080), "escala": 1.00, "segura": None,
                   "uso": "LinkedIn · Facebook · WhatsApp"},
    # En apaisado la unidad no puede ser el ancho: ahoga el bloque contra el pie.
    # `unidad` la fija a mano y sale del alto.
    "yt-miniatura": {"px": (1280, 720), "escala": 1.00, "unidad": 900, "segura": None,
                   "uso": "Miniatura de vídeo de YouTube 16:9"},
    "enlace":     {"px": (1200, 627), "escala": 1.00, "unidad": 784, "segura": None,
                   "uso": "og:image · vista previa de enlace en LinkedIn y Facebook"},

    # ── piezas de perfil ───────────────────────────────────────────────
    # No son de campaña: se ponen una vez y se quedan. Las construye
    # `perfil.py`, no `pieza()`. Van aquí para que la auditoría reconozca
    # el sufijo del nombre y compruebe el lienzo.
    # Las tres tienen ficha OFICIAL publicada, cosa que no pasa con las de
    # arriba: ver el bloque E de ESTANDARIZAR-salidas.md.
    "yt-portada": {"px": (2560, 1440), "escala": 1.00, "unidad": 1440,
                   "segura": (508, 931), "segura_x": (507, 2053), "perfil": True,
                   "uso": "Portada de canal de YouTube · sólo 1546×423 se ve en todos "
                          "los dispositivos (support.google.com/youtube/answer/2972003)"},
    "li-portada": {"px": (1512, 256), "escala": 1.00, "unidad": 256, "segura": None,
                   "perfil": True, "tope_mb": 3,
                   "uso": "Portada de página de LinkedIn (linkedin.com/help/linkedin/answer/a563309)"},
    "li-logo":    {"px": (400, 400), "escala": 1.00, "unidad": 400, "segura": None,
                   "perfil": True, "tope_mb": 3,
                   "uso": "Logo de página de LinkedIn · mínimo aceptado 268×268"},
}

# Los formatos de campaña son los de arriba MENOS los de perfil. Sin esta
# lista, `--todas` intentaba componer una pieza de campaña en li-portada
# (unidad 256) y reventaba: es el efecto colateral de haber ampliado FORMATOS.
FMT_CAMPANA = [k for k, v in FORMATOS.items() if not v.get("perfil")]

R = dict(                    # retícula, en fracciones del ancho
    margen=0.0667,           # 72 px a 1080
    franja=0.0222,           # franja naranja del fondo
    banda=0.1389,            # banda blanca de logos
    logo_gew=0.0889,         # alto del lockup GEW en la cabecera
    fecha=0.0630,            # cap del "16-22"
    titular=0.0787,          # cap del titular (techo: baja solo si no cabe)
    remate=0.0519,           # cap del texto de la pastilla
    lema=0.0213,             # cap del lema y del gew.co
)


def hoja(fmt):
    w, h = FORMATOS[fmt]["px"]
    e = FORMATOS[fmt]["escala"]
    u = FORMATOS[fmt].get("unidad", w)      # unidad de la retícula
    # el margen no escala: es aire de borde
    return w, h, u, {k: round(v * u * (1 if k == "margen" else e)) for k, v in R.items()}


def fuente(peso, cap_px):
    """Tamaño de cuerpo para un cap-height dado. Usa 0.725, no el 0.712 de la tabla."""
    return ImageFont.truetype(FUENTE[peso], max(1, round(cap_px / CAP)))


def tinta(draw, xy, texto, font, **kw):
    """Dibuja y devuelve la caja de tinta real (no la caja de fuente)."""
    draw.text(xy, texto, font=font, **kw)
    return draw.textbbox(xy, texto, font=font)


def svg_png(svg, alto):
    """Rasteriza un SVG a una altura dada, con caché."""
    if not os.path.exists(svg):
        raise SystemExit(
            f"falta el activo: {os.path.relpath(svg, RAIZ)}\n"
            f"Los logotipos no viajan en el repositorio: son de terceros.\n"
            f"Corre  python3 entorno.py  para ver qué falta.")
    nombre = os.path.basename(svg).replace(".svg", "")
    out = f"{RAIZ}/_cache/{nombre}-h{alto}.png"
    if not os.path.exists(out):
        os.makedirs(f"{RAIZ}/_cache", exist_ok=True)
        subprocess.run(["rsvg-convert", "-h", str(alto), "-o", out, svg], check=True)
    return Image.open(out).convert("RGBA")


def png_alto(ruta, alto):
    # Sin `logo/` —que no viaja en el repo público por ser marca de terceros—
    # esto reventaba con un FileNotFoundError y una ruta interna. Un clon
    # merece saber qué le falta y dónde mirarlo.
    if not os.path.exists(ruta):
        raise SystemExit(
            f"falta el activo: {os.path.relpath(ruta, RAIZ)}\n"
            f"Los logotipos y la tipografía no viajan en el repositorio: son de "
            f"terceros.\nCorre  python3 entorno.py  para ver qué falta, y mira "
            f"ACTIVOS.md y LICENCIAS.md.")
    im = Image.open(ruta).convert("RGBA")
    return im.resize((max(1, round(im.width * alto / im.height)), alto), Image.LANCZOS)


def marca_alto(ruta, alto, blanco=False):
    im = svg_png(ruta, alto) if ruta.endswith(".svg") else png_alto(ruta, alto)
    if blanco:
        # tiñe conservando el alfa: sólo vale para marcas monocromas
        b = Image.new("RGBA", im.size, (255, 255, 255, 0))
        b.putalpha(im.getchannel("A"))
        return b
    return im


# ── el pulso · elemento distintivo del movimiento ──────────────────────
# Elegido por Piero el 5-sep-2026. Sale de la geometría medida del propio
# anillo GEW·RD: 39 segmentos, 30 colores, anchos de 1° a 32,75°. Cada barra
# mide lo que mide su segmento — el ritmo no es decorativo.
_SEG = json.load(open(f"{RAIZ}/datos/anillo-segmentos.json", encoding="utf-8"))
SEGMENTOS = _SEG["lista"]


def pulso(d, x, y, ancho, alto, desde=0, n=None):
    """El elemento, dibujado de izquierda a derecha sobre la línea base `y+alto`."""
    segs = SEGMENTOS[desde:desde + n] if n else SEGMENTOS
    mx = max(s["grados"] for s in segs)
    paso = ancho / len(segs)
    an = max(2, round(paso * 0.62))
    for i, s in enumerate(segs):
        h = max(3, round(alto * (0.22 + 0.78 * s["grados"] / mx)))
        xx = round(x + i * paso)
        d.rectangle([xx, y + alto - h, xx + an - 1, y + alto - 1], fill=s["hex"])
    return ancho


# ── los tres bloques de marca ──────────────────────────────────────────
# Enlata e IAvanza son los DOS Partners (corregido por Piero el 5-sep-2026).
# Los patrocinadores tienen hueco propio, que se dibuja aunque esté vacío: si
# no se reserva, al llegar el primero hay que recomponer la pieza entera.
# La cobertura (IA Media) va en segunda fila y sólo en piezas de cobertura.
# Rótulos bilingües; «PARTNERS» se escribe igual en los dos idiomas.
ROTULOS = {"partners": "PARTNERS",
           "patrocinadores": "PATROCINADORES · SPONSORS",
           "cobertura": "COBERTURA · COVERAGE"}
PARTNERS = ["logo/socios/enlata-wordmark.svg", "logo/socios/iavanza-lockup.svg"]
LOGO_COBERTURA = {"claro": "logo/socios/ia-media-lockup.svg",
                  "oscuro": "logo/socios/ia-media-lockup-carbon.svg"}
HUECO_PATROCINIO = "espacio reservado"


def marcas(im, d, x, y, ancho, U, alto_logo=None, oscuro=False, cobertura=False,
           patrocinadores=None, con_hueco=True, cap_rot=None, partners=None):
    """Los tres bloques. Devuelve medidas para que la auditoría las compruebe.

    `y` es la línea del rótulo; los logos van debajo."""
    rot_col = "#B8B8B8" if oscuro else "#9A9A9A"
    cap_rot = cap_rot or round(U * 0.0130)
    f_rot = fuente("Bold", cap_rot)
    alto_logo = alto_logo or round(U * 0.0463)
    y_logo = y + round(cap_rot * 2.28)
    med = {"bloques": [], "cap_rot": cap_rot, "alto_logo": alto_logo}

    def pega(rutas, xl):
        for r in rutas:
            lg = marca_alto(f"{RAIZ}/{r}", alto_logo, blanco=oscuro)
            im.paste(lg, (xl, y_logo), lg)
            xl += lg.width + round(U * 0.037)
        return xl - round(U * 0.037)

    # bloque 1 · partners
    d.text((x, y), ROTULOS["partners"], font=f_rot, fill=rot_col)
    b = d.textbbox((x, y), ROTULOS["partners"], font=f_rot)
    der = max(b[2], pega(partners if partners is not None else PARTNERS, x))
    med["bloques"].append({"clave": "partners", "x": x, "derecha": der})

    # bloque 2 · patrocinadores, a la derecha
    x2 = x + round(ancho * 0.56)
    if patrocinadores or con_hueco:
        d.text((x2, y), ROTULOS["patrocinadores"], font=f_rot, fill=rot_col)
        b2 = d.textbbox((x2, y), ROTULOS["patrocinadores"], font=f_rot)
        if patrocinadores:
            der2 = max(b2[2], pega(patrocinadores, x2))
        else:
            w_h = round(ancho * 0.30)
            d.rectangle([x2, y_logo, x2 + w_h, y_logo + alto_logo],
                        outline="#8E8E8E" if oscuro else "#C8C8C8", width=2)
            f_h = fuente("Light", round(cap_rot * 0.92))
            bb = d.textbbox((0, 0), HUECO_PATROCINIO, font=f_h)
            d.text((x2 + (w_h - (bb[2] - bb[0])) // 2 - bb[0],
                    y_logo + (alto_logo - (bb[3] - bb[1])) // 2 - bb[1]),
                   HUECO_PATROCINIO, font=f_h, fill=rot_col)
            der2 = max(b2[2], x2 + w_h)
        med["bloques"].append({"clave": "patrocinadores", "x": x2, "derecha": der2})
        der = max(der, der2)
    med["fila1_base"] = y_logo + alto_logo

    # bloque 3 · cobertura, segunda fila y más pequeño
    if cobertura:
        y3 = med["fila1_base"] + round(U * 0.017)
        f_r3 = fuente("Bold", round(cap_rot * 0.94))
        d.text((x, y3), ROTULOS["cobertura"], font=f_r3, fill=rot_col)
        b3 = d.textbbox((x, y3), ROTULOS["cobertura"], font=f_r3)
        h_m = round(alto_logo * 0.62)
        lg = marca_alto(f"{RAIZ}/{LOGO_COBERTURA['oscuro' if oscuro else 'claro']}",
                        h_m, blanco=False)
        x_m = b3[2] + round(U * 0.026)
        im.paste(lg, (x_m, y3 - round(h_m * 0.24)), lg)
        med["bloques"].append({"clave": "cobertura", "x": x, "derecha": x_m + lg.width})
        der = max(der, x_m + lg.width)
        med["base"] = y3 + h_m
    else:
        med["base"] = med["fila1_base"]

    med["derecha"] = der
    med["desborda"] = max(0, der - (x + ancho))
    med["alto_usado"] = med["base"] - y
    return med


# El logo que manda en las piezas es el DOMINICANO — el que dice «República
# Dominicana» —, no el badge global en inglés. GEN lo permite explícitamente:
# los partners usan el badge Official Activity «o el logo nacional GEW que la
# organización provea». El reconocimiento en texto va aparte, en tipografía.
#
# Por debajo de este alto el lockup no se lee (lleva cuatro líneas) y se cambia
# por el anillo, que sí se reconoce. Es la misma regla de enlata.do/gew.
MIN_LOCKUP = 90
RECONOCIMIENTO = "ACTIVIDAD OFICIAL"


def sello(im, d, x, y, alto, U, oscuro=False):
    """Sello de actividad oficial, con el logo dominicano.

    Devuelve (ancho ocupado, forma usada)."""
    raiz = os.path.dirname(os.path.abspath(__file__))
    col = "#FFFFFF" if oscuro else TOK["color"]["marca"]["carbon-wordmark"]["hex"]
    if alto >= MIN_LOCKUP:
        f = "gew-rd-lockup-blanco.png" if oscuro else "gew-rd-lockup-color.png"
        alto_lock = round(alto * 0.72)
        lock = png_alto(f"{raiz}/logo/{f}", alto_lock)
        im.paste(lock, (x, y), lock)
        f_s = fuente("Bold", max(9, round(alto * 0.135)))
        bb = d.textbbox((0, 0), RECONOCIMIENTO, font=f_s)
        d.text((x - bb[0], y + alto_lock + round(alto * 0.10) - bb[1]),
               RECONOCIMIENTO, font=f_s, fill=col)
        return max(lock.width, bb[2] - bb[0]), "lockup"
    anillo = png_alto(f"{raiz}/logo/gew-rd-anillo.png", alto)
    im.paste(anillo, (x, y), anillo)
    f_s = fuente("Bold", max(9, round(alto * 0.30)))
    bb = d.textbbox((0, 0), RECONOCIMIENTO, font=f_s)
    hueco = round(U * 0.016)
    d.text((x + anillo.width + hueco - bb[0],
            y + alto // 2 - (bb[3] - bb[1]) // 2 - bb[1]), RECONOCIMIENTO,
           font=f_s, fill=col)
    return anillo.width + hueco + (bb[2] - bb[0]), "anillo"


def trocear(titular):
    """'La economía no se *construye*' -> [(texto, destacado?), ...] por línea."""
    for linea in titular.split("\n"):
        trozos, resto = [], linea
        while "*" in resto:
            antes, _, resto = resto.partition("*")
            dentro, _, resto = resto.partition("*")
            if antes:
                trozos.append((antes, False))
            if dentro:
                trozos.append((dentro, True))
        if resto:
            trozos.append((resto, False))
        yield trozos


def palabras(lineas):
    """Aplana las líneas troceadas a una lista de (palabra, destacada)."""
    out = []
    for tr in lineas:
        for texto, dest in tr:
            for w_ in texto.split(" "):
                if w_:
                    out.append((w_, dest))
    return out


def repartir(pal, k, anchos, esp):
    """Reparte las palabras en exactamente k líneas minimizando el ancho de la
    línea más larga. El greedy por caracteres se equivoca — esto es DP sobre los
    anchos reales de la fuente."""
    n = len(pal)
    if k > n:
        return None
    INF = float("inf")
    # ancho[i][j] = ancho de las palabras i..j-1 en una línea
    def ancho(i, j):
        return sum(anchos[i:j]) + esp * (j - i - 1)
    memo = {}

    def dp(i, lineas):
        if lineas == 1:
            return ancho(i, n), [n]
        if (i, lineas) in memo:
            return memo[(i, lineas)]
        mejor = (INF, None)
        for j in range(i + 1, n - lineas + 2):
            a = ancho(i, j)
            resto, cortes = dp(j, lineas - 1)
            val = max(a, resto)
            if val < mejor[0]:
                mejor = (val, [j] + cortes)
        memo[(i, lineas)] = mejor
        return mejor

    _, cortes = dp(0, k)
    if cortes is None:
        return None
    salida, ini = [], 0
    for c in cortes:
        ln, tramos = pal[ini:c], []
        for w_, dest in ln:
            if tramos and tramos[-1][1] == dest:
                tramos[-1] = (tramos[-1][0] + " " + w_, dest)
            else:
                if tramos:
                    # el espacio se queda en el tramo anterior; si no, las
                    # palabras de distinto color salen pegadas
                    tramos[-1] = (tramos[-1][0] + " ", tramos[-1][1])
                tramos.append((w_, dest))
        salida.append(tramos)
        ini = c
    return salida


def pin(draw, x, y, r, color):
    """Gota de ubicación: círculo con punta abajo."""
    draw.ellipse([x - r, y - r, x + r, y + r], fill=color)
    draw.polygon([(x - r * 0.62, y + r * 0.55), (x + r * 0.62, y + r * 0.55),
                  (x, y + r * 1.9)], fill=color)
    rr = r * 0.38
    draw.ellipse([x - rr, y - rr, x + rr, y + rr], fill=CARBON)


def pieza(titular, remate, fmt="retrato", host=None, socios=None, salida=None):
    w, h, U, g = hoja(fmt)
    m, fr, bd = g["margen"], g["franja"], g["banda"]
    im = Image.new("RGB", (w, h), CARBON)
    d = ImageDraw.Draw(im)
    medidas = {"formato": fmt, "px": [w, h]}

    # Todo se compone entre TOP y BOT. En historia esos límites son la zona
    # segura de Stories: fuera de ella Instagram pone su propia interfaz encima.
    segura = FORMATOS[fmt]["segura"]
    TOP, BOT = (segura if segura else (0, h))
    medidas["zona"] = [TOP, BOT]

    # --- banda de logos + franja naranja ---
    sangre = FORMATOS[fmt].get("pie") == "sangre"
    sobre_carbon = FORMATOS[fmt].get("logos_sobre_carbon", False)
    if sangre:
        # la banda acaba justo en el borde de la zona segura y la franja se va
        # al filo del lienzo: la pieza llena la pantalla sin perder los logos
        base_banda = BOT
        d.rectangle([0, h - fr, w, h], fill=NARANJA)
    else:
        base_banda = BOT - fr
        d.rectangle([0, BOT - fr, w, BOT], fill=NARANJA)
    if not sobre_carbon:
        d.rectangle([0, base_banda - bd, w, base_banda], fill=BLANCO)
    medidas["banda_top"] = base_banda - bd
    medidas["pie"] = "sangre" if sangre else "zona"

    # --- cabecera: lockup GEW a la izquierda ---
    gew = png_alto(f"{RAIZ}/logo/gew-rd-lockup-blanco.png", g["logo_gew"])
    im.paste(gew, (m, TOP + m), gew)
    medidas["logo_gew"] = [gew.width, gew.height]

    # --- el pulso: la firma del movimiento, justo bajo la cabecera ---
    y_pulso = TOP + m + gew.height + round(U * 0.030)
    alto_pulso = round(U * 0.034)
    pulso(d, m, y_pulso, w - m * 2, alto_pulso)
    medidas["pulso"] = [m, y_pulso, w - m, y_pulso + alto_pulso]

    # --- cabecera: fecha a la derecha ---
    f_dia = fuente("Light", g["fecha"])
    f_mes = fuente("Light", round(g["fecha"] * 0.34))
    dia, mes = TOK["campana"]["fechas"].split(" de ")[0], "NOVIEMBRE"
    bd_ = d.textbbox((0, 0), dia, font=f_dia)
    bm_ = d.textbbox((0, 0), mes, font=f_mes)
    x_dia = w - m - (bd_[2] - bd_[0])
    y_dia = TOP + m
    d.text((x_dia - bd_[0], y_dia - bd_[1]), dia, font=f_dia, fill=BLANCO)
    d.text((w - m - (bm_[2] - bm_[0]) - bm_[0], y_dia + g["fecha"] * 1.32 - bm_[1]),
           mes, font=f_mes, fill=BLANCO)
    medidas["fecha_izq"] = x_dia

    # --- pie de la zona carbón: lema + gew.co ---
    cap_lema = max(9, g["lema"])      # por debajo de 9 el lema no se lee
    f_lema = fuente("Light", cap_lema)  # definida siempre: el while puede no entrar
    while cap_lema > 8:
        f_lema = fuente("Light", cap_lema)
        ancho_lema = (round(cap_lema * 0.52) * 3.1
                      + d.textlength(TOK["campana"]["tema_es"], font=f_lema)
                      + d.textlength(TOK["campana"]["sitio"], font=f_lema)
                      + round(U * 0.030))
        if ancho_lema <= w - m * 2:
            break
        cap_lema -= 1
    medidas["cap_lema"] = [cap_lema, g["lema"]]
    y_lema = base_banda - bd - round(U * 0.055)
    r_pin = round(cap_lema * 0.52)
    pin(d, m + r_pin, y_lema + round(cap_lema * 0.32), r_pin, TOK["color"]["barra"]["hex"][0])
    d.text((m + r_pin * 3.1, y_lema), TOK["campana"]["tema_es"], font=f_lema, fill=BLANCO)
    b_web = d.textbbox((0, 0), TOK["campana"]["sitio"], font=f_lema)
    d.text((w - m - (b_web[2] - b_web[0]) - b_web[0], y_lema),
           TOK["campana"]["sitio"], font=f_lema, fill=BLANCO)

    util = w - m * 2

    # --- ajuste del titular al ancho útil ---
    # El cap nominal es un techo, no una promesa: si la línea más larga no cabe,
    # baja hasta que quepa. Sin esto el texto se sale del lienzo en silencio.
    lineas = list(trocear(titular))

    def cabe_en_ancho(lns, cap):
        f = fuente("Light", cap)
        return max(sum(d.textlength(t, font=f) for t, _ in tr) for tr in lns) <= util

    def mayor_cap(lns):
        c = g["titular"]
        while c > 8 and not cabe_en_ancho(lns, c):
            c -= 1
        return c

    if FORMATOS[fmt].get("reflow"):
        # busca el reparto en k líneas que deje el cuerpo más grande
        pal = palabras(lineas)
        f_ref = fuente("Light", 100)
        anchos = [d.textlength(w_, font=f_ref) for w_, _ in pal]
        esp = d.textlength(" ", font=f_ref)
        alto_zona = (FORMATOS[fmt]["segura"][1] - FORMATOS[fmt]["segura"][0]
                     if FORMATOS[fmt]["segura"] else h)
        mejor = (mayor_cap(lineas), lineas)
        for k in range(1, min(6, len(pal)) + 1):
            cand = repartir(pal, k, anchos, esp)
            if not cand:
                continue
            c = mayor_cap(cand)
            # el alto también manda: más líneas con cuerpo grande puede no caber
            if c * 1.42 * len(cand) > alto_zona * 0.46:
                continue
            if c > mejor[0]:
                mejor = (c, cand)
        cap_tit, lineas = mejor
        medidas["reflow_lineas"] = len(lineas)
    else:
        cap_tit = mayor_cap(lineas)

    # --- ajuste del remate ---
    pad_x, pad_y = round(U * 0.030), round(U * 0.024)
    lineas_r = remate.split("\n")
    cap_rem = g["remate"]
    while cap_rem > 6:
        f_rem = fuente("Light", cap_rem)
        ancho_r = max(d.textlength(l, font=f_rem) for l in lineas_r) + pad_x * 2
        if ancho_r <= util:
            break
        cap_rem -= 1

    # --- alto del bloque titular + pastilla, y su sitio ---
    # El ajuste es en dos ejes: el de arriba metió el texto en el ancho, éste lo
    # mete en el alto. Sin él, en 16:9 el bloque pisa el lema del pie.
    techo = TOP + m + g["logo_gew"] + round(U * 0.075)
    suelo = y_lema - round(U * 0.052)
    aire = round(U * 0.055)

    def bloque(ct, cr):
        f_t = fuente("Light", ct)
        f_r = fuente("Light", cr)
        il = round(ct * 1.42)
        ilr = round(cr * 1.42)
        at = (len(lineas) - 1) * il + ct
        anchos = [d.textbbox((0, 0), l, font=f_r) for l in lineas_r]
        pw_ = round(max(a[2] - a[0] for a in anchos)) + pad_x * 2
        ph_ = ilr * (len(lineas_r) - 1) + cr + pad_y * 2
        return f_t, f_r, il, ilr, at, pw_, ph_, at + aire + ph_

    while cap_tit > 8:
        f_tit, f_rem, interlinea, interlinea_r, alto_tit, pw, ph, alto_bloque = bloque(cap_tit, cap_rem)
        if alto_bloque <= suelo - techo:
            break
        cap_tit -= 1
        cap_rem = max(6, round(cap_rem * 0.985))
    medidas["cap_titular"] = [cap_tit, g["titular"]]
    medidas["cap_remate"] = [cap_rem, g["remate"]]

    y_tit = techo + max(0, round((suelo - techo - alto_bloque) * 0.62))
    medidas["titular_top"] = y_tit
    medidas["holgura_bloque"] = suelo - techo - alto_bloque

    y = y_tit
    for trozos in lineas:
        x = m
        for texto, destaca in trozos:
            bb = d.textbbox((0, 0), texto, font=f_tit)
            d.text((x - bb[0], y - bb[1]), texto, font=f_tit,
                   fill=NARANJA if destaca else BLANCO)
            x += d.textlength(texto, font=f_tit)
        medidas.setdefault("titular_anchos", []).append(round(x - m))
        y += interlinea

    py = y_tit + alto_tit + aire
    d.rectangle([m, py, m + pw, py + ph], fill=NARANJA)
    for i, l in enumerate(lineas_r):
        bb = d.textbbox((0, 0), l, font=f_rem)
        d.text((m + pad_x - bb[0], py + pad_y + i * interlinea_r - bb[1]),
               l, font=f_rem, fill=TINTA)
    medidas["pastilla"] = [pw, ph]
    medidas["pastilla_base"] = py + ph

    # --- los tres bloques de marca ---
    # Enlata e IAvanza son los dos Partners; el hueco de patrocinadores se
    # reserva aunque esté vacío. Vive en `marcas()` para que los once motores
    # usen la misma, y no cinco copias que se van separando.
    med_m = marcas(im, d, m, base_banda - bd + round(U * 0.0269), w - m * 2, U,
                   oscuro=sobre_carbon,
                   partners=([host] + list(socios or [])) if host else None)
    medidas["marcas"] = med_m
    medidas["marcas_desborda"] = med_m["desborda"]

    if salida:
        os.makedirs(os.path.dirname(salida), exist_ok=True)
        im.save(salida)
    return im, medidas


def main():
    ap = argparse.ArgumentParser(description="Pieza social de campaña GEW · RD")
    ap.add_argument("--audiencia", choices=list(CONT["audiencias"]))
    ap.add_argument("--pieza", type=int, default=0)
    ap.add_argument("--titular")
    ap.add_argument("--remate", default="")
    ap.add_argument("--formato", choices=list(FORMATOS), default="retrato")
    ap.add_argument("--todas", action="store_true",
                    help="las 15 piezas en los formatos de campaña")
    ap.add_argument("--salida", default=f"{RAIZ}/_salida")
    a = ap.parse_args()

    hechas = []
    if a.todas:
        esperadas = (sum(len(v["piezas"]) for v in CONT["audiencias"].values())
                     * len(FMT_CAMPANA))
        for clave, aud in CONT["audiencias"].items():
            for i, p in enumerate(aud["piezas"]):
                for fmt in FMT_CAMPANA:
                    ruta = f"{a.salida}/{clave}-{i}--{fmt}.png"
                    _, med = pieza(p["titular"], p["remate"], fmt, salida=ruta)
                    hechas.append((ruta, med))
        malas = [(r, m["holgura_bloque"]) for r, m in hechas if m["holgura_bloque"] < 0]
        print(f"producidas {len(hechas)} de {esperadas} esperadas")
        if malas:
            for r, hh in malas[:5]:
                print(f"  HOLGURA NEGATIVA {hh} px — {os.path.basename(r)}")
            sys.exit(f"{len(malas)} pieza(s) con el bloque fuera de sitio")
        if len(hechas) != esperadas:
            sys.exit(f"FALTAN {esperadas - len(hechas)}")
    else:
        if a.titular:
            tit, rem = a.titular, a.remate
            nombre = "libre"
        elif a.audiencia:
            p = CONT["audiencias"][a.audiencia]["piezas"][a.pieza]
            tit, rem, nombre = p["titular"], p["remate"], f"{a.audiencia}-{a.pieza}"
        else:
            ap.error("hace falta --audiencia o --titular")
        ruta = f"{a.salida}/{nombre}--{a.formato}.png"
        _, med = pieza(tit, rem, a.formato, salida=ruta)
        hechas.append((ruta, med))
        print(json.dumps(med, ensure_ascii=False))
    for r, _ in hechas:
        print(r)


if __name__ == "__main__":
    main()
