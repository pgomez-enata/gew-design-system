#!/usr/bin/env python3
"""
Páginas de reportería de la revista · GEW · RD.

Diez tipos más, sobre la misma hoja y la misma retícula de `revista.py`:

    reporteria         el cuadro de mando de la semana
    eventos            cuántas actividades, y de qué tipo
    impacto            a cuánta gente llegó, y a quién
    mapa               las 32 provincias, marcando dónde hubo algo
    calendario         los siete días de un vistazo
    cobertura          un evento contado a fondo
    resumen_aliados    qué hizo cada uno
    patrocinadores     quién lo pagó
    carta_host         la carta institucional del anfitrión
    promocional        el espacio que se vende o se cede

⚠️ Las cifras van como `{{N}}` hasta que existan. Una revista de recap con un
número inventado es peor que una con un hueco: el hueco se rellena, el número
falso se cita.

El mapa sale de `datos/rd-provincias.geojson` — Natural Earth, dominio público.
"""
import json, math, os, sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
from PIL import Image, ImageDraw  # noqa: E402
from campana import fuente, marca_alto, png_alto  # noqa: E402
from revista import (Hoja, mm, col, trocear, W, H, W_HOJA, H_HOJA, SANG,  # noqa: E402
                     CARBON, NARANJA, BLANCO, TINTA, GRIS, GRIS_CLARO, DPI)

GEO = f"{RAIZ}/datos/rd-provincias.geojson"


# ── el mapa ────────────────────────────────────────────────────────────
def _proyectar(features, caja):
    """Equirectangular con corrección por latitud. Para un país de 2° de alto
    la distorsión es despreciable y evita meter una dependencia de geo."""
    x0, y0, x1, y1 = caja
    pts = []
    for f in features:
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for poly in polys:
            for ring in poly:
                pts += ring
    lons = [p[0] for p in pts]; lats = [p[1] for p in pts]
    lon0, lon1 = min(lons), max(lons)
    lat0, lat1 = min(lats), max(lats)
    k = math.cos(math.radians((lat0 + lat1) / 2))
    an_geo, al_geo = (lon1 - lon0) * k, (lat1 - lat0)
    esc = min((x1 - x0) / an_geo, (y1 - y0) / al_geo)
    ox = x0 + ((x1 - x0) - an_geo * esc) / 2
    oy = y0 + ((y1 - y0) - al_geo * esc) / 2

    def pr(lon, lat):
        return (ox + (lon - lon0) * k * esc, oy + (lat1 - lat) * esc)
    return pr, esc


def mapa(n, activas=None, titulo="Dónde *pasó*"):
    """activas = {"Santiago": 6, ...} — nº de actividades por provincia."""
    activas = activas or {}
    h = Hoja(n, CARBON)
    h.texto(h.x0, h.y0, "ALCANCE TERRITORIAL", fuente("Bold", mm(3.2)), NARANJA)
    h.titular(h.x0, h.y0 + mm(10), titulo, 11, BLANCO, col(5))

    d = json.load(open(GEO, encoding="utf-8"))
    feats = d["features"]
    caja = (h.x0, h.y0 + mm(30), h.x1, h.y0 + mm(30) + mm(140))
    pr, esc = _proyectar(feats, caja)

    con, sin = 0, 0
    for f in feats:
        nombre = f["properties"]["name"]
        cnt = activas.get(nombre, 0)
        relleno = NARANJA if cnt else "#5E5E5E"
        if cnt:
            con += 1
        else:
            sin += 1
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for poly in polys:
            anillo = [pr(x, y) for x, y in poly[0]]
            if len(anillo) > 2:
                h.d.polygon(anillo, fill=relleno, outline=CARBON)

    # leyenda
    y = caja[3] + mm(14)
    for color, texto in ((NARANJA, f"{con} provincias con actividad"),
                         ("#5E5E5E", f"{sin} sin actividad registrada")):
        h.d.rectangle([h.x0, y, h.x0 + mm(6), y + mm(6)], fill=color)
        h.texto(h.x0 + mm(10), y + mm(1), texto, fuente("Light", mm(4)), BLANCO)
        y += mm(11)
    h.texto(h.x0, y + mm(4),
            "Geometría: Natural Earth, dominio público", fuente("Light", mm(2.6)), GRIS)
    f2 = fuente("Light", mm(2.8))
    h.texto(h.x1, SANG + H_HOJA - mm(10), str(h.n), f2, GRIS_CLARO, "der")
    h.folio_visible = False
    return h


# ── reportería ─────────────────────────────────────────────────────────
def reporteria(n, titulo, filas, nota=None):
    """filas = [(concepto, valor, fuente)]"""
    h = Hoja(n)
    h.texto(h.x0, h.y0, "REPORTE DE LA CAMPAÑA", fuente("Bold", mm(3.2)), NARANJA)
    h.titular(h.x0, h.y0 + mm(10), titulo, 11, TINTA, col(5))
    y = h.y0 + mm(32)
    h.texto(h.x0, y, "CONCEPTO", fuente("Bold", mm(2.8)), GRIS)
    h.texto(h.x0 + col(3), y, "CIFRA", fuente("Bold", mm(2.8)), GRIS)
    h.texto(h.x0 + col(4), y, "DE DÓNDE SALE", fuente("Bold", mm(2.8)), GRIS)
    y += mm(6)
    h.d.line([(h.x0, y), (h.x1, y)], fill=TINTA, width=3)
    y += mm(7)
    for concepto, valor, fte in filas:
        h.texto(h.x0, y, concepto, fuente("Light", mm(4)), TINTA)
        h.texto(h.x0 + col(3), y, valor, fuente("Bold", mm(4.6)),
                NARANJA if "{{" not in valor else GRIS_CLARO)
        h.parrafo(h.x0 + col(4), y, fte, fuente("Light", mm(2.8)), GRIS, col(2))
        y += mm(12)
        h.d.line([(h.x0, y - mm(4)), (h.x1, y - mm(4))], fill="#EAEAEA", width=1)
    if nota:
        h.parrafo(h.x0, y + mm(8), nota, fuente("Light", mm(3.2)), GRIS, col(5))
    h.folio()
    return h


def _cifra_con_barras(h, y, cifra, pie, desglose, color_fondo_claro=True):
    """Una cifra grande y, debajo, el desglose en barras horizontales."""
    tinta_ = TINTA if color_fondo_claro else BLANCO
    h.texto(h.x0, y, cifra, fuente("Bold", mm(28)), NARANJA)
    h.texto(h.x0, y + mm(34), pie, fuente("Light", mm(5.4)), tinta_)
    y += mm(50)
    if not desglose:
        return y
    mx = max((v for _, v in desglose if isinstance(v, (int, float))), default=1) or 1
    for etq, v in desglose:
        h.texto(h.x0, y, etq, fuente("Light", mm(3.6)), tinta_)
        an = col(3)
        h.d.rectangle([h.x0 + col(2), y, h.x0 + col(2) + an, y + mm(4)],
                      fill="#EFEFEF" if color_fondo_claro else "#5E5E5E")
        if isinstance(v, (int, float)):
            h.d.rectangle([h.x0 + col(2), y, h.x0 + col(2) + round(an * v / mx),
                           y + mm(4)], fill=NARANJA)
            h.texto(h.x1, y, str(v), fuente("Bold", mm(3.6)), NARANJA, "der")
        else:
            h.texto(h.x1, y, str(v), fuente("Light", mm(3.6)), GRIS_CLARO, "der")
        y += mm(11)
    return y


def eventos(n, total, desglose, nota=None):
    h = Hoja(n)
    h.texto(h.x0, h.y0, "ACTIVIDADES", fuente("Bold", mm(3.2)), NARANJA)
    h.titular(h.x0, h.y0 + mm(10), "Cuántas *cosas* pasaron", 11, TINTA, col(5))
    y = _cifra_con_barras(h, h.y0 + mm(34), total, "actividades en toda la semana", desglose)
    if nota:
        h.parrafo(h.x0, y + mm(8), nota, fuente("Light", mm(3.2)), GRIS, col(5))
    h.folio()
    return h


def impacto(n, total, desglose, nota=None):
    h = Hoja(n, CARBON)
    h.texto(h.x0, h.y0, "ALCANCE", fuente("Bold", mm(3.2)), NARANJA)
    h.titular(h.x0, h.y0 + mm(10), "A cuánta *gente* llegó", 11, BLANCO, col(5))
    y = _cifra_con_barras(h, h.y0 + mm(34), total, "personas participaron",
                          desglose, color_fondo_claro=False)
    if nota:
        h.parrafo(h.x0, y + mm(8), nota, fuente("Light", mm(3.2)), GRIS_CLARO, col(5))
    f2 = fuente("Light", mm(2.8))
    h.texto(h.x1, SANG + H_HOJA - mm(10), str(h.n), f2, GRIS_CLARO, "der")
    h.folio_visible = False
    return h


# ── calendario ─────────────────────────────────────────────────────────
def calendario(n, dias):
    """dias = [(etiqueta, [ (hora, titulo) ]) ] — siete columnas."""
    h = Hoja(n)
    h.texto(h.x0, h.y0, "PROGRAMA", fuente("Bold", mm(3.2)), NARANJA)
    h.titular(h.x0, h.y0 + mm(10), "La *semana* completa", 11, TINTA, col(5))
    y = h.y0 + mm(32)
    an = round((h.x1 - h.x0 - mm(2) * 6) / 7)
    for i, (etq, items) in enumerate(dias):
        cx = h.x0 + i * (an + mm(2))
        h.d.rectangle([cx, y, cx + an, y + mm(9)], fill=NARANJA)
        h.texto(cx + an // 2, y + mm(2), etq, fuente("Bold", mm(3)), BLANCO, "centro")
        cy = y + mm(13)
        for hora, titulo in items:
            h.texto(cx, cy, hora, fuente("Bold", mm(2.6)), NARANJA)
            cy = h.parrafo(cx, cy + mm(4), titulo, fuente("Light", mm(2.8)),
                           TINTA, an - mm(2), 1.30) + mm(5)
        h.d.line([(cx + an + mm(1), y), (cx + an + mm(1), h.y1 - mm(14))],
                 fill="#EEEEEE", width=1)
    h.folio()
    return h


# ── cobertura de un evento ─────────────────────────────────────────────
def cobertura(n, evento):
    h = Hoja(n)
    if evento.get("foto"):
        h.foto(evento["foto"], (0, 0, W, round(H * 0.42)), (0.5, 0.38))
    y = round(H * 0.42) + mm(12)
    h.texto(h.x0, y, evento["seccion"].upper(), fuente("Bold", mm(3.2)), NARANJA)
    y, _ = h.titular(h.x0, y + mm(9), evento["titulo"], 12, TINTA, col(5))
    y += mm(12)
    # ficha
    for etq, val in evento["ficha"]:
        h.texto(h.x0, y, etq.upper(), fuente("Bold", mm(2.6)), GRIS)
        h.texto(h.x0 + col(1), y, val, fuente("Light", mm(3.6)), TINTA)
        y += mm(8)
    y += mm(6)
    y = h.parrafo(h.x0, y, evento["cronica"], fuente("Light", mm(3.8)), TINTA, col(5))
    if evento.get("cita"):
        y += mm(8)
        h.d.rectangle([h.x0, y - mm(3), h.x0 + mm(2), y + mm(18)], fill=NARANJA)
        h.parrafo(h.x0 + mm(8), y, f'«{evento["cita"]}»', fuente("Light", mm(5.4)),
                  TINTA, col(5))
    h.folio()
    return h


# ── resumen de aliados ─────────────────────────────────────────────────
def resumen_aliados(n, filas, pagina=1, total_pag=1):
    """filas = [(aliado, que_hizo, cuantos)]"""
    h = Hoja(n)
    h.texto(h.x0, h.y0, "LOS ALIADOS", fuente("Bold", mm(3.2)), NARANJA)
    h.titular(h.x0, h.y0 + mm(10),
              "Qué hizo *cada uno*" if pagina == 1 else "Qué hizo cada uno",
              11, TINTA, col(5))
    y = h.y0 + mm(32)
    h.texto(h.x0, y, "ORGANIZACIÓN", fuente("Bold", mm(2.6)), GRIS)
    h.texto(h.x0 + col(3), y, "QUÉ HIZO", fuente("Bold", mm(2.6)), GRIS)
    h.texto(h.x1, y, "ACTIVIDADES", fuente("Bold", mm(2.6)), GRIS, "der")
    y += mm(5)
    h.d.line([(h.x0, y), (h.x1, y)], fill=TINTA, width=3)
    y += mm(6)
    for aliado, hizo, cuantos in filas:
        if y > h.y1 - mm(16):
            break
        h.parrafo(h.x0, y, aliado, fuente("Light", mm(3.4)), TINTA, col(3) - mm(4), 1.25)
        h.parrafo(h.x0 + col(3), y, hizo, fuente("Light", mm(3.2)), GRIS, col(2) - mm(4), 1.25)
        h.texto(h.x1, y, str(cuantos), fuente("Bold", mm(3.6)),
                NARANJA if str(cuantos).isdigit() else GRIS_CLARO, "der")
        y += mm(9)
        h.d.line([(h.x0, y - mm(3)), (h.x1, y - mm(3))], fill="#EFEFEF", width=1)
    if total_pag > 1:
        h.texto(h.x1, h.y1 - mm(6), f"{pagina} de {total_pag}",
                fuente("Light", mm(2.8)), GRIS_CLARO, "der")
    h.folio()
    return h


# ── patrocinadores ─────────────────────────────────────────────────────
def patrocinadores(n, niveles, nota=None):
    """niveles = [(rotulo, [ (nombre, ruta_logo|None) ], alto_mm)]"""
    h = Hoja(n)
    h.texto(h.x0, h.y0, "QUIÉN LO HIZO POSIBLE", fuente("Bold", mm(3.2)), NARANJA)
    h.titular(h.x0, h.y0 + mm(10), "Los *patrocinadores*", 11, TINTA, col(5))
    y = h.y0 + mm(34)
    for rotulo, marcas, alto in niveles:
        h.texto(h.x0, y, rotulo.upper(), fuente("Bold", mm(2.8)), NARANJA)
        h.d.line([(h.x0 + col(2), y + mm(2)), (h.x1, y + mm(2))], fill="#EAEAEA", width=1)
        y += mm(9)
        x = h.x0
        alto_px = mm(alto)
        fila_alta = 0
        for nombre, logo in marcas:
            if logo and os.path.exists(logo):
                lg = Image.open(logo).convert("RGBA")
                esc = alto_px / lg.height
                lg = lg.resize((max(1, round(lg.width * esc)), alto_px), Image.LANCZOS)
                if x + lg.width > h.x1:
                    x = h.x0; y += alto_px + mm(8)
                h.im.paste(lg, (x, y), lg)
                x += lg.width + mm(12)
                fila_alta = max(fila_alta, alto_px)
            else:
                f = fuente("Bold", round(alto_px * 0.34))
                bb = h.d.textbbox((0, 0), nombre, font=f)
                an = bb[2] - bb[0]
                if x + an > h.x1:
                    x = h.x0; y += alto_px + mm(8)
                h.d.rectangle([x, y, x + an + mm(10), y + alto_px], outline="#DDDDDD")
                h.texto(x + mm(5), y + alto_px // 2 - round(alto_px * 0.17), nombre, f, GRIS)
                x += an + mm(22)
                fila_alta = max(fila_alta, alto_px)
        y += fila_alta + mm(16)
    if nota:
        h.parrafo(h.x0, y, nota, fuente("Light", mm(3)), GRIS, col(5))
    h.folio()
    return h


# ── carta del anfitrión ────────────────────────────────────────────────
def carta_host(n, carta):
    h = Hoja(n)
    lock = png_alto(f"{RAIZ}/logo/gew-rd-lockup-color.png", mm(16))
    h.im.paste(lock, (h.x0, h.y0), lock)
    h.texto(h.x1, h.y0 + mm(4), carta["fecha"], fuente("Light", mm(3.2)), GRIS, "der")
    y = h.y0 + mm(30)
    h.texto(h.x0, y, "CARTA DEL ANFITRIÓN NACIONAL", fuente("Bold", mm(3.2)), NARANJA)
    y += mm(12)
    h.texto(h.x0, y, carta["saludo"], fuente("Light", mm(4.6)), TINTA)
    y += mm(12)
    for p in carta["cuerpo"]:
        y = h.parrafo(h.x0, y, p, fuente("Light", mm(4)), TINTA, col(5)) + mm(6)
    y += mm(8)
    h.texto(h.x0, y, carta["despedida"], fuente("Light", mm(4)), TINTA)
    y += mm(20)
    h.d.line([(h.x0, y), (h.x0 + col(2), y)], fill="#C0C0C0", width=2)
    h.texto(h.x0, y + mm(5), carta["firma"], fuente("Bold", mm(4.4)), TINTA)
    h.texto(h.x0, y + mm(12), carta["cargo"], fuente("Light", mm(3.4)), GRIS)
    h.parrafo(h.x0, h.y1 - mm(18), carta["pie"], fuente("Light", mm(2.8)), GRIS, col(5))
    h.folio()
    return h


# ── espacio promocional ────────────────────────────────────────────────
def promocional(n, anuncio=None):
    """Si `anuncio` trae una imagen a sangre, se coloca tal cual. Si no, sale la
    plantilla con las medidas, para mandársela a quien compra el espacio."""
    h = Hoja(n, BLANCO, folio=False)
    if anuncio and os.path.exists(anuncio):
        h.foto(anuncio, (0, 0, W, H), (0.5, 0.5))
        return h
    # Marcas de corte en las esquinas, DENTRO del sangrado — que es donde van.
    # Antes esto era un rectángulo continuo dibujado justo sobre la línea de
    # corte: la auditoría lo marcó y tenía razón. Una línea sobre el corte sale
    # desigual (el guillotinado tiene ±1 mm de tolerancia) o se come entera.
    for x, y in ((SANG, SANG), (SANG + W_HOJA, SANG),
                 (SANG, SANG + H_HOJA), (SANG + W_HOJA, SANG + H_HOJA)):
        dx = -1 if x == SANG else 1
        dy = -1 if y == SANG else 1
        h.d.line([x, y + dy, x, y + dy * SANG], fill="#BBBBBB", width=2)
        h.d.line([x + dx, y, x + dx * SANG, y], fill="#BBBBBB", width=2)
    seg = mm(6)
    h.d.rectangle([SANG + seg, SANG + seg, SANG + W_HOJA - seg, SANG + H_HOJA - seg],
                  outline="#FF7C1055", width=2)
    cx = SANG + W_HOJA // 2
    h.texto(cx, SANG + mm(110), "ESPACIO PROMOCIONAL", fuente("Bold", mm(4.4)),
            NARANJA, "centro")
    y = SANG + mm(124)
    for l in (f"Página completa · {round(W_HOJA / DPI * 25.4)} × "
              f"{round(H_HOJA / DPI * 25.4)} mm",
              "Sangrado: 3 mm por cada lado",
              "Zona segura: 6 mm desde el corte",
              "Resolución: 300 dpi · CMYK",
              "Formato: PDF o TIFF sin capas"):
        h.texto(cx, y, l, fuente("Light", mm(3.6)), GRIS, "centro")
        y += mm(8)
    h.texto(cx, SANG + H_HOJA - mm(30), "El perfil de color lo confirma la imprenta",
            fuente("Light", mm(2.8)), GRIS_CLARO, "centro")
    return h
