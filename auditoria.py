#!/usr/bin/env python3
"""
Audita las piezas de _salida/ contra las reglas del sistema.

No opina: cada regla devuelve un número y lo compara con su umbral.
Salida distinta de 0 si alguna regla FALLA (los AVISO no tumban la corrida).

    python3 auditoria.py
    python3 auditoria.py _salida/publico-0--retrato.png
"""
import glob, json, os, re, sys
import numpy as np
from PIL import Image

RAIZ = os.path.dirname(os.path.abspath(__file__))
TOK = json.load(open(f"{RAIZ}/tokens/tokens.json", encoding="utf-8"))
sys.path.insert(0, RAIZ)
from campana import FORMATOS, R  # noqa: E402
from actividad import FORMATOS as FMT_ACT, R as R_ACT  # noqa: E402
from cita import FORMATOS as FMT_CITA, R as R_CITA  # noqa: E402
from video import FORMATOS as FMT_VID, R as R_VID  # noqa: E402
from serie import FORMATOS as FMT_SER, R as R_SER  # noqa: E402
from aliado import FORMATOS as FMT_ALI, R as R_ALI  # noqa: E402
import impreso as IMP  # noqa: E402
import metadatos as MET  # noqa: E402

Image.MAX_IMAGE_PIXELS = None

CARBON = TOK["color"]["campana2026"]["carbon"]["hex"]
NARANJA = TOK["color"]["campana2026"]["naranja"]["hex"]


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(h):
    r, g, b = rgb(h)
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contraste(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def formato_de(nombre):
    for f in FORMATOS:
        if nombre.endswith(f"--{f}.png"):
            return f
    return None


def audita_actividad(ruta):
    """Reglas del flyer de actividad. El fondo puede ser foto, así que aquí no
    se puede exigir margen limpio: se comprueban lienzo, franja, badge y pie."""
    n = os.path.basename(ruta)
    fmt = next((f for f in FMT_ACT if n.endswith(f"--{f}.png")), None)
    if not fmt:
        return out + [("FALLA", "formato reconocible", n,
                       "sufijo --<formato>", False)]
    out = []
    esperado = FMT_ACT[fmt]["px"]
    a = np.array(Image.open(ruta).convert("RGB"))
    h_, w_ = a.shape[:2]
    out.append(("FALLA", "lienzo", f"{w_}x{h_}", f"{esperado[0]}x{esperado[1]}",
                (w_, h_) == tuple(esperado)))
    U = FMT_ACT[fmt]["unidad"]
    m = round(R_ACT["margen"] * U)
    fr = round(R_ACT["franja"] * U)
    TOP, BOT = FMT_ACT[fmt].get("segura") or (0, h_)

    fila = a[BOT - max(1, fr // 2), w_ // 2]
    out.append(("FALLA", "franja naranja del pie", "#%02X%02X%02X" % tuple(fila),
                NARANJA, tuple(fila) == rgb(NARANJA)))

    variante = "A" if "-A-" in n else ("B" if "-B-" in n else "C")
    alto_pie = round(R_ACT["pie"] * U) if variante == "A" else round(R_ACT["pie"] * U * 0.62)
    y_pie = BOT - fr - alto_pie
    banda = a[y_pie:BOT - fr, :, :]
    blanco = (np.abs(banda.astype(int) - 255).sum(axis=2) < 20).mean()
    out.append(("FALLA", "banda de pie blanca", f"{blanco*100:.0f}% blanco", ">= 70%",
                blanco >= 0.70))

    # el badge tiene que estar: en A arriba a la izquierda, en B y C en el pie
    if variante == "A":
        caja = a[TOP + m:TOP + m + round(R_ACT["badge"] * U), m:m + round(U * 0.34)]
    else:
        caja = a[y_pie:BOT - fr, m:m + round(U * 0.34)]
    tinta = (np.abs(caja.astype(int) - 255).sum(axis=2) > 30).sum()
    out.append(("FALLA", "sello de actividad oficial presente", f"{tinta} px", "> 2000",
                tinta > 2000))

    if FMT_ACT[fmt].get("segura"):
        out.append(("FALLA", "pie dentro de la zona segura", f"acaba en {BOT}",
                    f"<= {FMT_ACT[fmt]['segura'][1]}", BOT <= FMT_ACT[fmt]["segura"][1]))
    return out


def audita_cita(ruta):
    """La cita: lienzo, franja, banda de pie y badge."""
    n = os.path.basename(ruta)
    fmt = next((f for f in FMT_CITA if n.endswith(f"--{f}.png")), None)
    if not fmt:
        return out + [("FALLA", "formato reconocible", n,
                       "sufijo --<formato>", False)]
    out = []
    esperado = FMT_CITA[fmt]["px"]
    a = np.array(Image.open(ruta).convert("RGB"))
    h_, w_ = a.shape[:2]
    out.append(("FALLA", "lienzo", f"{w_}x{h_}", f"{esperado[0]}x{esperado[1]}",
                (w_, h_) == tuple(esperado)))
    U = FMT_CITA[fmt]["unidad"]
    m, fr = round(R_CITA["margen"] * U), round(R_CITA["franja"] * U)
    seg = FMT_CITA[fmt].get("segura")
    TOP, BOT = seg or (0, h_)
    y_fr = (h_ - max(1, fr // 2)) if seg else (BOT - max(1, fr // 2))
    fila = a[y_fr, w_ // 2]
    out.append(("FALLA", "franja naranja", "#%02X%02X%02X" % tuple(fila), NARANJA,
                tuple(fila) == rgb(NARANJA)))
    base_pie = BOT if seg else BOT - fr
    alto_pie = round(R_CITA["pie"] * U)
    banda = a[base_pie - alto_pie:base_pie, :, :]
    blanco = (np.abs(banda.astype(int) - 255).sum(axis=2) < 20).mean()
    out.append(("FALLA", "banda de pie blanca", f"{blanco*100:.0f}% blanco", ">= 70%",
                blanco >= 0.70))
    caja = a[base_pie - alto_pie:base_pie, m:m + round(U * 0.30)]
    tinta = (np.abs(caja.astype(int) - 255).sum(axis=2) > 30).sum()
    out.append(("FALLA", "sello GEW en el pie", f"{tinta} px", "> 1500", tinta > 1500))
    return out


def audita_video(ruta):
    """Frames y rótulos llevan alfa; el endcard es opaco. El lockup tiene que
    caer fuera de lo que tapa la interfaz."""
    n = os.path.basename(ruta)
    fmt = next((f for f in FMT_VID if n.endswith(f"--{f}.png")), None)
    if not fmt:
        return out + [("FALLA", "formato reconocible", n,
                       "sufijo --<formato>", False)]
    tipo = n.split("--")[0]
    out = []
    esperado = FMT_VID[fmt]["px"]
    im = Image.open(ruta)
    w_, h_ = im.size
    out.append(("FALLA", "lienzo", f"{w_}x{h_}", f"{esperado[0]}x{esperado[1]}",
                (w_, h_) == tuple(esperado)))
    tiene_alfa = im.mode == "RGBA"
    debe = tipo in ("frame", "guias", "lower")
    out.append(("FALLA", f"{'con' if debe else 'sin'} canal alfa",
                im.mode, "RGBA" if debe else "RGB", tiene_alfa == debe))
    ui = FMT_VID[fmt]["ui"]
    U = FMT_VID[fmt]["unidad"]
    fr = round(R_VID["franja"] * U)
    a = np.array(im.convert("RGBA"))
    if tipo in ("frame", "guias"):
        # el lockup vive bajo la franja de interfaz superior
        m = round(R_VID["margen"] * U)
        caja = a[ui["arriba"] + m:ui["arriba"] + m + round(R_VID["logo"] * U),
                 m:m + round(U * 0.30), 3]
        out.append(("FALLA", "lockup fuera de la zona de interfaz",
                    f"{(caja > 10).sum()} px", "> 1500", (caja > 10).sum() > 1500))
        # nada opaco por encima de la franja de interfaz
        arriba = a[:ui["arriba"] - 4, :, 3]
        out.append(("FALLA", "nada dibujado bajo la interfaz superior",
                    f"{(arriba > 10).sum()} px", "0" if tipo == "frame" else "cualquiera",
                    (arriba > 10).sum() == 0 or tipo == "guias"))
    if tipo == "endcard":
        fila = a[h_ - max(1, fr // 2), w_ // 2, :3]
        out.append(("FALLA", "franja naranja", "#%02X%02X%02X" % tuple(fila), NARANJA,
                    tuple(fila) == rgb(NARANJA)))
        bd = round(R_VID["banda"] * U)
        banda = a[h_ - fr - bd:h_ - fr, :, :3]
        blanco = (np.abs(banda.astype(int) - 255).sum(axis=2) < 20).mean()
        out.append(("FALLA", "banda de logos blanca", f"{blanco*100:.0f}% blanco",
                    ">= 70%", blanco >= 0.70))
    return out


def _carbon_lockup_franja(ruta, FMT, R_, nombre_familia):
    """Reglas comunes a las piezas de fondo carbón: lienzo, lockup y franja."""
    n = os.path.basename(ruta)
    fmt = next((f for f in FMT if n.endswith(f"--{f}.png")), None)
    if not fmt:
        return out + [("FALLA", "formato reconocible", n,
                       "sufijo --<formato>", False)]
    out = []
    esperado = FMT[fmt]["px"]
    a = np.array(Image.open(ruta).convert("RGB"))
    h_, w_ = a.shape[:2]
    out.append(("FALLA", "lienzo", f"{w_}x{h_}", f"{esperado[0]}x{esperado[1]}",
                (w_, h_) == tuple(esperado)))
    U = FMT[fmt].get("unidad", w_)
    m, fr = round(R_["margen"] * U), round(R_["franja"] * U)
    seg = FMT[fmt].get("segura")
    TOP, BOT = seg or (0, h_)
    y_fr = (h_ - max(1, fr // 2)) if seg else (BOT - max(1, fr // 2))
    fila = a[y_fr, w_ // 2]
    out.append(("FALLA", "franja naranja", "#%02X%02X%02X" % tuple(fila), NARANJA,
                tuple(fila) == rgb(NARANJA)))
    caja = a[TOP + m:TOP + m + round(R_["logo"] * U), m:m + round(U * 0.32)]
    dif = (np.abs(caja.astype(int) - np.array(rgb(CARBON))).sum(axis=2) > 24).sum()
    out.append(("FALLA", "lockup en la cabecera", f"{dif} px", "> 2000", dif > 2000))
    return out


def audita_impreso(ruta):
    """Imprenta: el lienzo tiene que cuadrar con los cm y el dpi declarados."""
    n = os.path.basename(ruta).replace(".png", "")
    tipo = next((t for t in IMP.PIEZAS if n.startswith(t) or n.endswith(t)), None)
    if not tipo:
        return [("FALLA", "pieza reconocible", n, " | ".join(IMP.PIEZAS), False)]
    out = []
    w_esp, h_esp, sang, dpi, a_cm, h_cm = IMP.lienzo(tipo)
    im = Image.open(ruta)
    w_, h_ = im.size
    out.append(("FALLA", f"lienzo de {a_cm:g}x{h_cm:g} cm a {dpi} dpi",
                f"{w_}x{h_}", f"{w_esp}x{h_esp}", (w_, h_) == (w_esp, h_esp)))
    a = np.array(im.convert("RGB"))
    # El pie ya NO es una franja naranja plana: desde el 5-sep-2026 es el pulso.
    # La regla no se borra, se sustituye por la que ahora corresponde — contar
    # los colores de la fila. Una franja plana daría 1 y volvería a fallar.
    fila = a[h_ - max(1, sang + 4), :, :]
    colores = len({tuple(px) for px in fila[::max(1, w_ // 400)]})
    out.append(("FALLA", "el pulso remata el pie", f"{colores} colores en la fila",
                ">= 5 (una franja plana da 1)", colores >= 5))
    # el lockup no puede quedar por debajo de la resolución de la pieza
    if tipo in ("rollup", "backdrop"):
        _, med = IMP.gran_formato(tipo)
        out.append(("FALLA", "lockup a la resolución de la pieza",
                    f'{med["logo_dpi_efectivo"]} dpi', f">= {dpi} dpi",
                    med["aviso_logo"] is None))
    return out



# ── revista ────────────────────────────────────────────────────────────
# Hasta el 5-sep-2026 la revista recibía UNA comprobación —la del sufijo del
# nombre— y fallaba. El informe de revista.py decía verde, pero el guardián
# del sistema no estaba mirando ahí. Dos informes, y el que manda no cubría la
# familia. Este ramal cierra ese hueco: mide el PNG por su cuenta y además
# cruza lo que el motor declaró.
INFORME_REV = f"{RAIZ}/_salida/revista/informe.json"
_rev_cache = {}


def _informe_revista():
    if "d" not in _rev_cache:
        try:
            _rev_cache["d"] = json.load(open(INFORME_REV, encoding="utf-8"))
        except Exception:
            _rev_cache["d"] = None
    return _rev_cache["d"]


def audita_revista(ruta):
    n = os.path.basename(ruta)
    if n == "informe.json":
        return []
    d = _informe_revista()
    if d is None:
        return [("FALLA", "informe de revista.py presente",
                 "no está", "_salida/revista/informe.json", False)]
    g = d["geometria"]
    out = []
    try:
        pag = int(os.path.splitext(n)[0])
    except ValueError:
        return [("FALLA", "página numerada", n, "NN.png", False)]

    im = Image.open(ruta)
    w_, h_ = im.size
    esp = tuple(g["lienzo_px"])
    out.append(("FALLA", "lienzo con sangrado", f"{w_}x{h_}",
                f"{esp[0]}x{esp[1]}", (w_, h_) == esp))
    dpi = (im.info.get("dpi") or [None])[0]
    out.append(("FALLA", "dpi declarado", str(dpi), str(g["dpi"]),
                dpi is not None and round(dpi) == g["dpi"]))

    a = np.array(im.convert("RGB")).astype(int)
    # 1 · la página no puede estar en blanco: un lote que revienta a la mitad
    #     entrega menos y parece que funcionó
    tinta = int((np.abs(a - a[0, 0]).sum(axis=2) > 24).sum())
    out.append(("FALLA", "la página tiene contenido", f"{tinta} px", "> 0 px",
                tinta > 0))

    # 2 · el error clásico del sangrado: el fondo de color acaba en el corte y
    #     los 3 mm de fuera quedan en blanco. Al recortar sale una línea blanca,
    #     y no avisa: se ve cuando la revista ya está impresa.
    #
    #     Ojo con la primera versión de esta regla: exigía que el borde exterior
    #     fuese IGUAL al interior, y marcó las 4 páginas con foto a sangre —una
    #     foto varía de una fila a otra, claro—. Lo que hay que buscar no es la
    #     diferencia, es el blanco donde debajo no lo hay.
    sg = g["sangrado_px"]
    bordes = {
        "arriba": (a[0, :, :], a[sg + 2, :, :]),
        "abajo": (a[-1, :, :], a[-(sg + 3), :, :]),
        "izquierda": (a[:, 0, :], a[:, sg + 2, :]),
        "derecha": (a[:, -1, :], a[:, -(sg + 3), :]),
    }
    peor, peor_lado = 0, ""
    for lado, (fuera, dentro) in bordes.items():
        blanco_fuera = fuera.min(axis=1) > 245
        color_dentro = dentro.min(axis=1) <= 245
        malos = int((blanco_fuera & color_dentro).sum())
        if malos > peor:
            peor, peor_lado = malos, lado
    tol = round(max(w_, h_) * 0.02)      # 2 % del borde puede ser transición
    out.append(("FALLA", "el sangrado no deja línea blanca al cortar",
                f"{peor} px blancos sobre fondo ({peor_lado or 'ninguno'})",
                f"<= {tol} px", peor <= tol))

    # 3 · cruce con lo que declaró el motor
    inf = next((x for x in d["paginas"] if x["pagina"] == pag), None)
    if inf is None:
        return out + [("FALLA", "la página está en el informe", f"pág {pag}",
                       "declarada por revista.py", False)]
    out.append(("FALLA", "sin desbordes de la zona segura",
                f"{len(inf['desbordes'])}", "0", not inf["desbordes"]))
    out.append(("FALLA", "sin glifos faltantes",
                f"{len(inf['glifos_faltantes'])}", "0", not inf["glifos_faltantes"]))
    env, cs = inf["envolvente"], g["caja_segura_px"]
    if env:
        fuera = max(0, cs[0] - env[0], cs[1] - env[1], env[2] - cs[2], env[3] - cs[3])
        out.append(("FALLA", "toda la tinta dentro de la zona segura",
                    f"{fuera:.0f} px fuera", "0 px", fuera <= 0))
    out.append(("AVISO", "creep compensado", f"{inf['creep_px']} px",
                f"<= {g['creep_max_px']} px", inf["creep_px"] <= g["creep_max_px"]))
    return out


def audita_revista_corrida():
    """Reglas que no son de una página suelta sino del pliego entero."""
    d = _informe_revista()
    if d is None:
        return []
    g = d["geometria"]
    hay = len(glob.glob(f"{RAIZ}/_salida/revista/*.png"))
    return [("FALLA", "páginas producidas", f"{hay}", f"{g['paginas']}",
             hay == g["paginas"]),
            ("FALLA", "páginas declaradas en el informe", f"{len(d['paginas'])}",
             f"{g['paginas']}", len(d["paginas"]) == g["paginas"]),
            ("FALLA", "el pliego es múltiplo de 4", f"{g['paginas']}",
             "múltiplo de 4", g["paginas"] % 4 == 0)]




# ── IA Media: el logo, no una pieza ────────────────────────────────────
def audita_ia_media(ruta):
    """Un logo no tiene formato de plataforma: tiene proporción, tinta y
    contraste. Se le comprueba que rasterice, que respete el ratio del SVG y
    que sus colores se vean sobre el fondo al que van destinados.

    OJO: la regla de sellado se aplica antes, en `audita()`. No hay exención
    aquí para nadie."""
    import logo_ia_media as LM
    n = os.path.basename(ruta).replace(".png", "")
    im = Image.open(ruta).convert("RGBA")
    a = np.array(im)
    op = a[:, :, 3] > 40
    out = [("FALLA", "el logo tiene tinta", f"{int(op.sum())} px", "> 0 px",
            bool(op.sum()))]
    if not op.sum():
        return out

    svg = f"{RAIZ}/logo/socios/{n}.svg"
    if os.path.exists(svg):
        vb = re.search(r'viewBox="([\d.\s-]+)"', open(svg, encoding="utf-8").read())
        w_v, h_v = (float(x) for x in vb.group(1).split()[2:4])
        # La tolerancia va en PÍXELES, no en ratio. Con un lockup de 89 px de
        # alto, un solo píxel de redondeo del rasterizador mueve el ratio 0,065
        # y una tolerancia de ±0,01 lo marcaba como error. El rasterizador
        # redondea; el vector no está mal.
        h_esp = im.width * h_v / w_v
        out.append(("FALLA", "el PNG conserva la proporción del vector",
                    f"{im.height} px de alto", f"{h_esp:.1f} ±1 px",
                    abs(im.height - h_esp) <= 1.0))
    else:
        out.append(("FALLA", "el SVG del que sale existe", "no está",
                    f"logo/socios/{n}.svg", False))

    # el tamaño mínimo del lockup lo fija el propio sistema de IAvanza
    if "lockup" in n:
        out.append(("AVISO", "por encima del ancho mínimo de lockup",
                    f"{im.width} px", "120 px", im.width >= 120))

    # contraste del color contra el fondo al que va destinada la variante
    fondo = CARBON if n.endswith("carbon") else "#FFFFFF"
    if not n.endswith("blanco"):
        col = LM.COLOR_CLARO if n.endswith("carbon") else LM.COLOR
        c = contraste(col, fondo)
        out.append(("FALLA", f"el isotipo se ve sobre {fondo}", f"{c:.2f}:1",
                    ">= 3:1", c >= 3.0))
    return out


# ── movimiento: muestras y propuestas del elemento distintivo ──────────
def audita_movimiento(ruta):
    """No son piezas de producción, son propuestas para decidir. Se les exige
    lo que sí aplica: lienzo del formato que declaran y respeto de la zona
    segura de la plataforma.

    OJO con la exención: la lámina comparativa no tiene formato porque es una
    hoja de trabajo, pero SÍ pasa por la regla de sellado, que se aplica antes
    en `audita()`. Una exención declarada para una regla no la heredan sus
    hermanas — en este fichero ya pasó dos veces."""
    n = os.path.basename(ruta)
    if n == "propuestas--muestra.png":
        im = Image.open(ruta)
        return [("FALLA", "la lámina tiene contenido", f"{im.width}x{im.height}",
                 "> 0", im.width > 0 and im.height > 0)]
    fmt = formato_de(n)
    if not fmt:
        return [("FALLA", "formato reconocible", n, "sufijo --<formato>", False)]
    im = Image.open(ruta)
    esp = tuple(FORMATOS[fmt]["px"])
    out = [("FALLA", "lienzo", f"{im.width}x{im.height}", f"{esp[0]}x{esp[1]}",
            (im.width, im.height) == esp)]
    seg = FORMATOS[fmt].get("segura")
    if seg:
        a = np.array(im.convert("RGB")).astype(int)
        dif = np.abs(a - np.array(rgb(CARBON))).sum(axis=2) > 30
        ys = np.nonzero(dif)[0]
        arriba = max(0, seg[0] - int(ys.min())) if len(ys) else 0
        abajo = max(0, int(ys.max()) - seg[1]) if len(ys) else 0
        out.append(("FALLA", "dentro de la zona segura del formato",
                    f"{arriba} px arriba · {abajo} px abajo", "0 px",
                    arriba == 0 and abajo == 0))
    return out


# ── piezas de perfil ───────────────────────────────────────────────────
def audita_perfil(ruta):
    """Las tres piezas que sí tienen ficha oficial publicada."""
    n = os.path.basename(ruta)
    fmt = formato_de(n)
    if not fmt or not FORMATOS[fmt].get("perfil"):
        return [("FALLA", "formato de perfil reconocible", n,
                 "sufijo --yt-portada | --li-portada | --li-logo", False)]
    F = FORMATOS[fmt]
    im = Image.open(ruta)
    esp = tuple(F["px"])
    out = [("FALLA", "lienzo", f"{im.width}x{im.height}",
            f"{esp[0]}x{esp[1]}", (im.width, im.height) == esp)]
    mb = os.path.getsize(ruta) / 1e6
    if F.get("tope_mb"):
        out.append(("FALLA", "peso bajo el tope de la plataforma", f"{mb:.2f} MB",
                    f"<= {F['tope_mb']} MB", mb <= F["tope_mb"]))
    sx, sy = F.get("segura_x"), F.get("segura")
    if sx and sy:
        a = np.array(im.convert("RGB")).astype(int)
        dif = np.abs(a - np.array(rgb(CARBON))).sum(axis=2) > 30
        dif[im.height - 24:, :] = False          # la barra a sangre del pie
        fuera = int(dif.sum() - dif[sy[0]:sy[1], sx[0]:sx[1]].sum())
        out.append(("FALLA", "nada fuera de la zona segura de la plataforma",
                    f"{fuera} px", "0 px", fuera == 0))
        out.append(("FALLA", "zona segura del tamaño que publica YouTube",
                    f"{sx[1]-sx[0]}x{sy[1]-sy[0]}", "1546x423",
                    (sx[1] - sx[0], sy[1] - sy[0]) == (1546, 423)))
    return out


# Ficheros que viven en _salida pero no son piezas de formato: el sello que se
# reparte a los aliados es un activo suelto, no una pieza con lienzo.
NO_SON_PIEZA = ("sello-aliado-gew-rd.png",)


def audita(ruta):
    """Devuelve [(nivel, regla, medida, umbral, ok)]."""
    if os.path.basename(ruta) in NO_SON_PIEZA:
        return []
    # Regla global: una pieza sin su procedencia dentro no está terminada.
    # 358 de 394 salían así hasta el 5-sep-2026.
    marca = [("FALLA", "procedencia dentro del fichero",
              "sellada" if MET.sellado(ruta) else "sin sellar",
              "XMP + enlata:sistema (python3 metadatos.py)", MET.sellado(ruta))]

    if os.sep + "revista" + os.sep in ruta:
        return marca + audita_revista(ruta)
    if os.sep + "perfil" + os.sep in ruta:
        return marca + audita_perfil(ruta)
    if os.sep + "movimiento" + os.sep in ruta:
        return marca + audita_movimiento(ruta)
    if os.sep + "ia-media" + os.sep in ruta:
        return marca + audita_ia_media(ruta)
    if os.sep + "impreso" + os.sep in ruta:
        return marca + audita_impreso(ruta)
    if os.sep + "serie" + os.sep in ruta:
        return marca + _carbon_lockup_franja(ruta, FMT_SER, R_SER, "serie")
    if os.sep + "aliados" + os.sep in ruta:
        return marca + _carbon_lockup_franja(ruta, FMT_ALI, R_ALI, "aliados")
    if os.sep + "cita" + os.sep in ruta:
        return marca + audita_cita(ruta)
    if os.sep + "video" + os.sep in ruta:
        return marca + audita_video(ruta)
    if os.sep + "actividad" + os.sep in ruta:
        return marca + audita_actividad(ruta)
    n = os.path.basename(ruta)
    fmt = formato_de(n)
    out = list(marca)
    if not fmt:
        return out + [("FALLA", "formato reconocible", n,
                       "sufijo --<formato>", False)]

    esperado = FORMATOS[fmt]["px"]
    im = Image.open(ruta).convert("RGB")
    a = np.array(im)
    h_, w_ = a.shape[:2]
    out.append(("FALLA", "lienzo", f"{w_}x{h_}", f"{esperado[0]}x{esperado[1]}",
                (w_, h_) == tuple(esperado)))

    U = FORMATOS[fmt].get("unidad", w_)
    m = round(R["margen"] * U)
    TOP, BOT = FORMATOS[fmt]["segura"] or (0, h_)
    fr = round(R["franja"] * U * FORMATOS[fmt]["escala"])
    bd = round(R["banda"] * U * FORMATOS[fmt]["escala"])

    # 1 · nada de contenido dentro del margen lateral, en la zona carbón
    sangre_ = FORMATOS[fmt].get("pie") == "sangre"
    zona = a[TOP:(BOT if sangre_ else BOT - fr) - bd, :, :]
    no_fondo = (np.abs(zona.astype(int) - np.array(rgb(CARBON))).sum(axis=2) > 24)
    izq = no_fondo[:, :m].sum()
    der = no_fondo[:, w_ - m:].sum()
    out.append(("FALLA", "margen izquierdo limpio", f"{izq} px con tinta", "0", izq == 0))
    out.append(("FALLA", "margen derecho limpio", f"{der} px con tinta", "0", der == 0))

    # 2 · la banda de logos, dentro de la zona segura
    if FORMATOS[fmt]["segura"]:
        base = BOT
        out.append(("FALLA", "banda dentro de la zona segura",
                    f"acaba en {base}", f"<= {FORMATOS[fmt]['segura'][1]}",
                    base <= FORMATOS[fmt]["segura"][1]))

    # 3 · la franja naranja del pie: al filo del lienzo o dentro de la zona
    sangre = FORMATOS[fmt].get("pie") == "sangre"
    y_fr = (h_ - max(1, fr // 2)) if sangre else (BOT - max(1, fr // 2))
    fila = a[y_fr, w_ // 2]
    out.append(("FALLA", f"franja naranja ({'al filo' if sangre else 'en la zona'})",
                "#%02X%02X%02X" % tuple(fila), NARANJA, tuple(fila) == rgb(NARANJA)))

    # 4 · el fondo de la banda de logos: blanco, o carbón si van en blanco encima
    base_banda = BOT if sangre else BOT - fr
    fila_b = a[base_banda - bd // 2, 4]
    if FORMATOS[fmt].get("logos_sobre_carbon"):
        out.append(("FALLA", "zona de logos sobre carbón", "#%02X%02X%02X" % tuple(fila_b),
                    CARBON, tuple(fila_b) == rgb(CARBON)))
    else:
        out.append(("FALLA", "banda de logos blanca", "#%02X%02X%02X" % tuple(fila_b),
                    "#FFFFFF", tuple(fila_b) == (255, 255, 255)))

    # 5 · contraste del texto
    c1 = contraste("#FFFFFF", CARBON)
    out.append(("FALLA", "blanco sobre carbón", f"{c1:.2f}", ">= 4.5", c1 >= 4.5))
    c2 = contraste(TOK["color"]["marca"]["carbon-wordmark"]["hex"], NARANJA)
    out.append(("FALLA", "texto de la pastilla sobre naranja", f"{c2:.2f}", ">= 4.5",
                c2 >= 4.5))

    # 6 · el pulso: la firma del movimiento tiene que estar. Se busca en la
    #     banda que va bajo la cabecera y se cuentan sus colores: una franja
    #     plana o su ausencia dan menos de 5.
    y0_p = TOP + m + round(U * 0.0889) + round(U * 0.020)
    y1_p = min(h_, y0_p + round(U * 0.060))
    tira = a[y0_p:y1_p, m:w_ - m]
    cols_p = len({tuple(px) for px in tira.reshape(-1, 3)[::17]})
    out.append(("FALLA", "el pulso está bajo la cabecera",
                f"{cols_p} colores", ">= 5", cols_p >= 5))

    # 7 · el lockup GEW aparece arriba a la izquierda
    caja = a[TOP + m:TOP + m + round(R["logo_gew"] * U * FORMATOS[fmt]["escala"]), m:m + round(w_ * 0.34)]
    dif = (np.abs(caja.astype(int) - np.array(rgb(CARBON))).sum(axis=2) > 24).sum()
    out.append(("FALLA", "lockup GEW en la cabecera", f"{dif} px", "> 3000", dif > 3000))
    return out


def main():
    # `publico/` y `demo/` son andamios, no producción: el paquete para
    # GitHub y el sistema corriendo con activos de marcador.
    ANDAMIOS = (f"{os.sep}publico{os.sep}", f"{os.sep}demo{os.sep}")
    rutas = sys.argv[1:] or [
        p for p in (sorted(glob.glob(f"{RAIZ}/_salida/*.png"))
                    + sorted(glob.glob(f"{RAIZ}/_salida/*/*.png"))
                    + sorted(glob.glob(f"{RAIZ}/_salida/*/*/*.png")))
        if not any(a in p for a in ANDAMIOS)]
    if not rutas:
        sys.exit("no hay nada que auditar en _salida/")
    fallos, avisos, reglas = [], [], 0
    for r in rutas:
        for nivel, regla, med, umbral, ok in audita(r):
            reglas += 1
            if not ok:
                (fallos if nivel == "FALLA" else avisos).append(
                    (os.path.basename(r), regla, med, umbral))
    # reglas del pliego entero, no de una página suelta
    if not sys.argv[1:]:
        for nivel, regla, med, umbral, ok in audita_revista_corrida():
            reglas += 1
            if not ok:
                (fallos if nivel == "FALLA" else avisos).append(
                    ("revista (pliego)", regla, med, umbral))

    print(f"{len(rutas)} piezas · {reglas} comprobaciones")
    for etq, lista in (("FALLA", fallos), ("AVISO", avisos)):
        vistos = {}
        for f, regla, med, umbral in lista:
            vistos.setdefault((regla, med, umbral), []).append(f)
        for (regla, med, umbral), fs in vistos.items():
            print(f"  {etq}  {regla}: {med} (umbral {umbral}) — {len(fs)} pieza(s)"
                  + ("" if len(fs) > 3 else " " + ", ".join(fs)))
    if not fallos and not avisos:
        print("  todo en verde")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
