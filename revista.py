#!/usr/bin/env python3
"""
Revista de recap · GEW · RD.

32 páginas grapadas, 8.5 × 11 pulgadas, 300 dpi, con sangrado de 3 mm y
compensación de creep. Decidido por Piero el 5-sep-2026.

Trece tipos de página. Los cinco primeros vienen de la arquitectura de
`p4f_design_system/revista.py`, que ya los tenía resueltos:

    portada · retiracion_portada · masthead · editorial · indice
    apertura · lectura · datos · tarjetas · galeria · muro
    retiracion_contra · contraportada

⚠️ EL CREEP. En una revista grapada, las hojas de dentro sobresalen porque el
doblez acumula grosor; al recortar a filo, el contenido de las páginas centrales
se corta. Con 32 páginas y papel de 130 g el desplazamiento llega a 0,52 mm. El
motor lo compensa desplazando cada pliego hacia el lomo. Es un fallo del papel
que no avisa: si no se compensa, se ve impreso y ya no hay marcha atrás.

⚠️ EL COLOR. Sale en RGB. La conversión a CMYK necesita el perfil de la imprenta
y ninguna imprenta dominicana lo publica: hay que pedírselo. Con `--cmyk` se
convierte con el perfil genérico de macOS, que sirve para ver, NO para imprimir.

Uso:
    python3 revista.py --pliego            las 32 páginas
    python3 revista.py --pdf               además, el PDF montado
    python3 revista.py --pagina portada
"""
import argparse, json, os, sys
from PIL import Image, ImageDraw, ImageOps

RAIZ = os.path.dirname(os.path.abspath(__file__))
TOK = json.load(open(f"{RAIZ}/tokens/tokens.json", encoding="utf-8"))
sys.path.insert(0, RAIZ)
from campana import (fuente, marca_alto, png_alto, pin, trocear, sello,  # noqa: E402
                     pulso, ROTULOS, PARTNERS, LOGO_COBERTURA)
from aliado import padron  # noqa: E402

CARBON = TOK["color"]["campana2026"]["carbon"]["hex"]
NARANJA = TOK["color"]["campana2026"]["naranja"]["hex"]
BLANCO = "#FFFFFF"
TINTA = TOK["color"]["marca"]["carbon-wordmark"]["hex"]
GRIS = "#8A8A8A"
GRIS_CLARO = "#C6C6C6"

# ── la hoja ────────────────────────────────────────────────────────────
DPI = 300
ANCHO_MM, ALTO_MM = 215.9, 279.4        # 8.5 × 11 pulgadas
SANGRADO_MM = 3.0                        # lo que pide la imprenta
SEGURIDAD_MM = 6.0                       # mínimo para revista
PAGINAS = 32
PAPEL_MM = 0.13                          # grosor de una hoja de 130 g
COLUMNAS = 6


def mm(v):
    return round(v / 25.4 * DPI)


W_HOJA, H_HOJA = mm(ANCHO_MM), mm(ALTO_MM)
SANG = mm(SANGRADO_MM)
W, H = W_HOJA + SANG * 2, H_HOJA + SANG * 2
SEG = mm(SEGURIDAD_MM)
U = W_HOJA                                # unidad de la retícula
MG = mm(16)                               # margen tipográfico
GUT = mm(4)                               # medianil entre columnas
COL = (W_HOJA - MG * 2 - GUT * (COLUMNAS - 1)) / COLUMNAS


def creep(pagina):
    """Desplazamiento hacia el lomo, en px, de una página dada.

    El pliego de más adentro es el que más sobresale. La fórmula estándar:
    creep_total = (nº de hojas / 2) × grosor. Se reparte proporcional al
    número de pliego contando desde fuera."""
    hojas = PAGINAS // 4
    total_mm = hojas / 2 * PAPEL_MM
    # el pliego 0 son las páginas 1-2 y 31-32; el más interno, 15-16-17-18
    desde_fuera = min(pagina - 1, PAGINAS - pagina) // 2
    return round(total_mm * (desde_fuera / max(1, hojas - 1)) / 25.4 * DPI)


def col(n):
    """Ancho de n columnas de la retícula."""
    return round(COL * n + GUT * (n - 1))


class Hoja:
    """Una página. Mide su propia tinta y guarda lo que se sale."""

    def __init__(self, numero, fondo=BLANCO, folio=True):
        self.n = numero
        self.im = Image.new("RGB", (W, H), fondo)
        self.d = ImageDraw.Draw(self.im)
        self.fondo = fondo
        self.folio_visible = folio
        self.desbordes = []
        self.glifos = []
        self.cajas = []          # toda la tinta de texto, para poder auditarla
        # El tipo sale del nombre de la función que crea la hoja: cada página
        # se construye dentro de la suya. Es una línea en vez de tocar las 23.
        self.tipo = sys._getframe(1).f_code.co_name
        # la página impar va a la derecha del pliego: el lomo está a su izquierda
        self.impar = numero % 2 == 1
        c = creep(numero)
        self.dx = c if self.impar else -c
        self.creep_px = c

    # ── utilidades de caja ─────────────────────────────────────────────
    @property
    def x0(self):
        return SANG + MG + (self.dx if self.impar else 0)

    @property
    def x1(self):
        return SANG + W_HOJA - MG + (0 if self.impar else self.dx)

    @property
    def y0(self):
        return SANG + MG

    @property
    def y1(self):
        return SANG + H_HOJA - MG

    def texto(self, x, y, s, font, fill, alinear="izq", max_ancho=None):
        """Dibuja y registra si la tinta se sale de la zona segura."""
        faltan = [ch for ch in s if ch not in ("\n",) and font.getmask(ch).getbbox() is None
                  and ch != " "]
        if faltan:
            self.glifos.append((s[:28], "".join(sorted(set(faltan)))))
        bb = self.d.textbbox((0, 0), s, font=font)
        an = bb[2] - bb[0]
        if alinear == "centro":
            x = x - an // 2
        elif alinear == "der":
            x = x - an
        self.d.text((x - bb[0], y - bb[1]), s, font=font, fill=fill)
        caja = (x, y, x + an, y + (bb[3] - bb[1]))
        lim = (SANG + SEG, SANG + SEG, SANG + W_HOJA - SEG, SANG + H_HOJA - SEG)
        fuera = max(0, lim[0] - caja[0], lim[1] - caja[1],
                    caja[2] - lim[2], caja[3] - lim[3])
        if fuera > 0:
            self.desbordes.append((s[:28], fuera))
        self.cajas.append(caja)
        return caja

    def parrafo(self, x, y, s, font, fill, ancho, interlinea=1.45):
        lineas, act = [], ""
        for p in s.split():
            t = (act + " " + p).strip()
            if self.d.textlength(t, font=font) <= ancho or not act:
                act = t
            else:
                lineas.append(act); act = p
        if act:
            lineas.append(act)
        cap = font.size * 0.725
        for l in lineas:
            self.texto(x, y, l, font, fill)
            y += round(cap * interlinea)
        return y

    def titular(self, x, y, texto_, cap_mm, color, ancho, salto_mm=None):
        """Titular con *destacados*. Pasa por `texto()`, así que SE MIDE — los
        titulares que se dibujaban directos no entraban en el informe y un
        desborde de la portada pasó desapercibido."""
        lineas = list(trocear(texto_))
        cap = mm(cap_mm)
        while cap > mm(4):
            f = fuente("Light", cap)
            if max(sum(self.d.textlength(t, font=f) for t, _ in tr)
                   for tr in lineas) <= ancho:
                break
            cap -= mm(0.4)
        f = fuente("Light", cap)
        salto = mm(salto_mm) if salto_mm else round(cap * 1.10)
        for tr in lineas:
            xx = x
            for t, dest in tr:
                self.texto(xx, y, t, f, NARANJA if dest else color)
                xx += self.d.textlength(t, font=f)
            y += salto
        return y - salto + cap, cap

    def foto(self, ruta, caja, centrado=(0.5, 0.36)):
        x0, y0, x1, y1 = caja
        im = ImageOps.fit(Image.open(ruta).convert("RGB"), (x1 - x0, y1 - y0),
                          Image.LANCZOS, centering=centrado)
        self.im.paste(im, (x0, y0))

    def folio(self):
        if not self.folio_visible:
            return
        f = fuente("Light", mm(2.8))
        x = self.x1 if self.impar else self.x0
        self.texto(x, SANG + H_HOJA - mm(10), str(self.n), f, GRIS,
                   "der" if self.impar else "izq")
        f2 = fuente("Light", mm(2.4))
        self.texto(self.x0 if self.impar else self.x1,
                   SANG + H_HOJA - mm(10),
                   "Semana Global de Emprendimiento · RD 2026", f2, GRIS_CLARO,
                   "izq" if self.impar else "der")

    def rejilla(self):
        for i in range(COLUMNAS):
            x = self.x0 + round(COL * i + GUT * i)
            self.d.rectangle([x, self.y0, x + round(COL), self.y1],
                             outline="#FF000030")
        self.d.rectangle([SANG + SEG, SANG + SEG,
                          SANG + W_HOJA - SEG, SANG + H_HOJA - SEG],
                         outline="#0000FF40")

    def informe(self):
        """Lo que esta página declara de sí misma.

        `auditoria.py` lo lee y lo cruza contra los PNG: el informe interno de
        este motor no basta como prueba, porque el guardián del sistema tiene
        que poder comprobarlo desde fuera."""
        if self.cajas:
            env = (min(c[0] for c in self.cajas), min(c[1] for c in self.cajas),
                   max(c[2] for c in self.cajas), max(c[3] for c in self.cajas))
        else:
            env = None
        return {"pagina": self.n, "tipo": self.tipo, "creep_px": self.creep_px,
                "cajas_texto": len(self.cajas), "envolvente": env,
                "desbordes": self.desbordes, "glifos_faltantes": self.glifos}


# ── los trece tipos de página ──────────────────────────────────────────
def portada(ed, foto=None):
    h = Hoja(1, CARBON, folio=False)
    if foto:
        h.foto(foto, (0, 0, W, round(H * 0.62)), (0.5, 0.34))
        velo = Image.new("RGBA", (W, round(H * 0.30)), (0, 0, 0, 0))
        vd = ImageDraw.Draw(velo)
        for i in range(velo.height):
            vd.line([(0, i), (W, i)], fill=(28, 26, 26, int(235 * (i / velo.height) ** 1.3)))
        h.im.paste(velo, (0, round(H * 0.62) - velo.height), velo)
    lock = png_alto(f"{RAIZ}/logo/gew-rd-lockup-blanco.png", mm(22))
    h.im.paste(lock, (h.x0, SANG + mm(14)), lock)
    y, _ = h.titular(h.x0, round(H * 0.66), ed["titular"], 19, BLANCO,
                     h.x1 - h.x0, 20)
    y += mm(6)
    h.parrafo(h.x0, y, ed["bajada"], fuente("Light", mm(6)), GRIS_CLARO, col(4))
    h.texto(h.x0, SANG + H_HOJA - mm(24), ed["fechas"], fuente("Light", mm(7)), BLANCO)
    h.d.rectangle([0, H - SANG - mm(6), W, H], fill=NARANJA)
    return h


def retiracion_portada(ed):
    h = Hoja(2, CARBON, folio=False)
    f_c = fuente("Bold", mm(46))
    h.texto(SANG + W_HOJA // 2, SANG + mm(70), ed["cifra"], f_c, NARANJA, "centro")
    h.texto(SANG + W_HOJA // 2, SANG + mm(112), ed["cifra_pie"],
            fuente("Light", mm(7)), BLANCO, "centro")
    h.parrafo(h.x0 + col(1), SANG + mm(140), ed["cifra_texto"],
              fuente("Light", mm(4.4)), GRIS_CLARO, col(4))
    return h


def masthead(ed):
    h = Hoja(3)
    lock = png_alto(f"{RAIZ}/logo/gew-rd-lockup-color.png", mm(18))
    h.im.paste(lock, (h.x0, h.y0), lock)
    y = h.y0 + mm(26)
    h.texto(h.x0, y, "QUIÉN HACE ESTA REVISTA", fuente("Bold", mm(3.4)), NARANJA)
    y += mm(9)
    for rol, quien in ed["creditos"]:
        h.texto(h.x0, y, rol, fuente("Bold", mm(3.2)), GRIS)
        h.texto(h.x0 + col(2), y, quien, fuente("Light", mm(4)), TINTA)
        y += mm(8)
    y += mm(8)
    h.texto(h.x0, y, "RECONOCIMIENTOS", fuente("Bold", mm(3.4)), NARANJA)
    y += mm(9)
    y = h.parrafo(h.x0, y, ed["kauffman"], fuente("Light", mm(3.8)), TINTA, col(4))
    y += mm(6)
    y = h.parrafo(h.x0, y, ed["sobre_gew"], fuente("Light", mm(3.8)), GRIS, col(4))
    h.folio()
    return h


def editorial(ed):
    h = Hoja(4)
    h.texto(h.x0, h.y0, "EDITORIAL", fuente("Bold", mm(3.4)), NARANJA)
    y, _ = h.titular(h.x0, h.y0 + mm(12), ed["editorial_titular"], 13, TINTA, col(5), 14)
    y += mm(12)
    for p in ed["editorial"]:
        y = h.parrafo(h.x0, y, p, fuente("Light", mm(4.2)), TINTA, col(4)) + mm(5)
    y += mm(6)
    h.texto(h.x0, y, ed["firma"], fuente("Bold", mm(4.4)), TINTA)
    h.texto(h.x0, y + mm(7), ed["firma_cargo"], fuente("Light", mm(3.6)), GRIS)
    h.folio()
    return h


def indice(ed):
    h = Hoja(5)
    h.texto(h.x0, h.y0, "EN ESTE NÚMERO", fuente("Bold", mm(3.4)), NARANJA)
    y = h.y0 + mm(14)
    for pag, titulo, sec in ed["indice"]:
        h.texto(h.x0, y, f"{pag:02d}", fuente("Bold", mm(7)), NARANJA)
        h.texto(h.x0 + col(1), y, titulo, fuente("Light", mm(6)), TINTA)
        h.texto(h.x0 + col(1), y + mm(8), sec, fuente("Light", mm(3.4)), GRIS)
        y += mm(17)
        h.d.line([(h.x0, y - mm(5)), (h.x1, y - mm(5))], fill="#E4E4E4", width=2)
    h.folio()
    return h


def apertura(n, seccion, titular, foto=None):
    h = Hoja(n, CARBON, folio=False)
    if foto:
        h.foto(foto, (0, 0, W, H), (0.5, 0.38))
        velo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        vd = ImageDraw.Draw(velo)
        for i in range(H):
            vd.line([(0, i), (W, i)], fill=(24, 22, 22, int(30 + 195 * (i / H) ** 1.7)))
        h.im.paste(velo, (0, 0), velo)
    h.texto(h.x0, SANG + H_HOJA - mm(78), seccion.upper(), fuente("Bold", mm(3.6)), NARANJA)
    h.titular(h.x0, SANG + H_HOJA - mm(66), titular, 17, BLANCO, h.x1 - h.x0, 18)
    h.d.rectangle([0, H - SANG - mm(5), W, H], fill=NARANJA)
    return h


def lectura(n, seccion, titular, entradilla, cuerpo, destacado=None):
    h = Hoja(n)
    h.texto(h.x0, h.y0, seccion.upper(), fuente("Bold", mm(3.2)), NARANJA)
    y, _ = h.titular(h.x0, h.y0 + mm(10), titular, 11, TINTA, col(5), 12)
    y += mm(9)
    y = h.parrafo(h.x0, y, entradilla, fuente("Light", mm(5)), NARANJA, col(5)) + mm(7)
    # dos columnas
    ancho_c = col(3)
    x_izq, x_der = h.x0, h.x0 + col(3) + GUT
    mitad = len(cuerpo) // 2
    y_i = h.parrafo(x_izq, y, " ".join(cuerpo[:mitad]), fuente("Light", mm(4)), TINTA, ancho_c)
    y_d = h.parrafo(x_der, y, " ".join(cuerpo[mitad:]), fuente("Light", mm(4)), TINTA, ancho_c)
    if destacado:
        yy = max(y_i, y_d) + mm(10)
        h.d.rectangle([h.x0, yy - mm(4), h.x0 + mm(3), yy + mm(22)], fill=NARANJA)
        h.parrafo(h.x0 + mm(10), yy, destacado, fuente("Light", mm(7)), TINTA, col(5))
    h.folio()
    return h


def datos(n, seccion, titulo, cifras):
    h = Hoja(n, CARBON)
    h.texto(h.x0, h.y0, seccion.upper(), fuente("Bold", mm(3.2)), NARANJA)
    y = h.y0 + mm(10)
    y, _ = h.titular(h.x0, y, titulo, 11, BLANCO, col(5))
    y += mm(20)
    for i, (cifra, pie, fuente_) in enumerate(cifras):
        cx = h.x0 + (i % 2) * (col(3) + GUT)
        cy = y + (i // 2) * mm(46)
        h.texto(cx, cy, cifra, fuente("Bold", mm(17)), NARANJA)
        h.parrafo(cx, cy + mm(20), pie, fuente("Light", mm(4)), BLANCO, col(3))
        h.texto(cx, cy + mm(36), fuente_, fuente("Light", mm(2.8)), GRIS)
    h.folio_visible = True
    f = fuente("Light", mm(2.8))
    h.texto(h.x1, SANG + H_HOJA - mm(10), str(h.n), f, GRIS_CLARO, "der")
    return h


def tarjetas(n, seccion, titulo, items):
    h = Hoja(n)
    h.texto(h.x0, h.y0, seccion.upper(), fuente("Bold", mm(3.2)), NARANJA)
    h.titular(h.x0, h.y0 + mm(10), titulo, 11, TINTA, col(5))
    y = h.y0 + mm(30)
    for i, it in enumerate(items):
        cx = h.x0 + (i % 2) * (col(3) + GUT)
        cy = y + (i // 2) * mm(44)
        h.d.rectangle([cx, cy, cx + col(3), cy + mm(38)], outline="#E0E0E0")
        h.d.rectangle([cx, cy, cx + mm(2), cy + mm(38)], fill=NARANJA)
        h.texto(cx + mm(7), cy + mm(6), it["titulo"], fuente("Bold", mm(4.6)), TINTA)
        h.parrafo(cx + mm(7), cy + mm(14), it["texto"], fuente("Light", mm(3.4)),
                  GRIS, col(3) - mm(12))
    h.folio()
    return h


def galeria(n, seccion, titulo, fotos, pies):
    h = Hoja(n)
    h.texto(h.x0, h.y0, seccion.upper(), fuente("Bold", mm(3.2)), NARANJA)
    h.titular(h.x0, h.y0 + mm(10), titulo, 11, TINTA, col(5))
    y = h.y0 + mm(28)
    an = col(3)
    al = round(an * 0.72)
    for i, f in enumerate(fotos[:6]):
        cx = h.x0 + (i % 2) * (an + GUT)
        cy = y + (i // 2) * (al + mm(14))
        h.foto(f, (cx, cy, cx + an, cy + al))
        if i < len(pies):
            h.texto(cx, cy + al + mm(3), pies[i], fuente("Light", mm(3)), GRIS)
    h.folio()
    return h


def muro(n, aliados):
    h = Hoja(n)
    h.texto(h.x0, h.y0, "QUIÉNES LO HICIERON POSIBLE", fuente("Bold", mm(3.4)), NARANJA)
    h.texto(h.x0, h.y0 + mm(10), f"{len(aliados)} organizaciones aliadas",
            fuente("Light", mm(9)), TINTA)
    y = h.y0 + mm(26)
    cols, an = 4, round((W_HOJA - MG * 2 - GUT * 3) / 4)
    al = round(an * 0.44)
    for i, (nombre, logo) in enumerate(aliados):
        cx = h.x0 + (i % cols) * (an + GUT)
        cy = y + (i // cols) * (al + mm(4))
        if cy + al > h.y1 - mm(6):
            break
        if logo and os.path.exists(logo):
            lg = Image.open(logo).convert("RGBA")
            esc = min((an - mm(4)) / lg.width, (al - mm(3)) / lg.height)
            lg = lg.resize((max(1, round(lg.width * esc)), max(1, round(lg.height * esc))),
                           Image.LANCZOS)
            h.im.paste(lg, (cx + (an - lg.width) // 2, cy + (al - lg.height) // 2), lg)
        else:
            f = fuente("Light", mm(2.6))
            h.parrafo(cx, cy + al // 2 - mm(2), nombre, f, GRIS, an - mm(3))
    h.folio()
    return h


def retiracion_contra(n, aliados):
    h = muro(n, aliados)
    h.n = n
    h.folio_visible = False
    return h


def contraportada(ed):
    h = Hoja(PAGINAS, CARBON, folio=False)
    lock = png_alto(f"{RAIZ}/logo/gew-rd-lockup-blanco.png", mm(30))
    h.im.paste(lock, ((W - lock.width) // 2, SANG + mm(52)), lock)
    h.texto(SANG + W_HOJA // 2, SANG + mm(96), ed["fechas"],
            fuente("Light", mm(9)), BLANCO, "centro")
    h.texto(SANG + W_HOJA // 2, SANG + mm(110), TOK["campana"]["tema_es"],
            fuente("Light", mm(5.6)), GRIS_CLARO, "centro")
    h.texto(SANG + W_HOJA // 2, SANG + mm(124), TOK["campana"]["sitio"],
            fuente("Light", mm(6)), NARANJA, "centro")

    # Los tres bloques del movimiento. La revista ES pieza de cobertura, así
    # que lleva IA Media; y la banda crece a 42 mm para las dos filas.
    bd = mm(42)
    base = SANG + H_HOJA - mm(34)
    h.d.rectangle([0, base - bd, W, base], fill=BLANCO)
    f_rot = fuente("Bold", mm(2.6))
    alto_l = mm(9)
    y_rot = base - bd + mm(6)
    for ruta, x_b, rot in ((PARTNERS, h.x0, ROTULOS["partners"]),
                           (None, h.x0 + col(3) + mm(4), ROTULOS["patrocinadores"])):
        h.texto(x_b, y_rot, rot, f_rot, GRIS)
        if ruta:
            xl = x_b
            for p in ruta:
                lg = marca_alto(f"{RAIZ}/{p}", alto_l)
                h.im.paste(lg, (xl, y_rot + mm(7)), lg)
                xl += lg.width + mm(8)
        else:
            w_h = col(2)
            h.d.rectangle([x_b, y_rot + mm(7), x_b + w_h, y_rot + mm(7) + alto_l],
                          outline="#C8C8C8", width=2)
            h.texto(x_b + w_h // 2, y_rot + mm(10), "espacio reservado",
                    fuente("Light", mm(2.4)), GRIS_CLARO, "centro")
    y_cob = y_rot + mm(7) + alto_l + mm(4)
    h.texto(h.x0, y_cob, ROTULOS["cobertura"], fuente("Bold", mm(2.4)), GRIS)
    lm = marca_alto(f"{RAIZ}/{LOGO_COBERTURA['claro']}", mm(6))
    h.im.paste(lm, (h.x0 + mm(38), y_cob - mm(1)), lm)

    # el pulso, a sangre sobre la banda
    pulso(h.d, 0, base - bd - mm(4), W, mm(4))

    h.parrafo(h.x0, base + mm(6), ed["kauffman"], fuente("Light", mm(2.8)),
              GRIS_CLARO, col(5))
    h.d.rectangle([0, H - SANG - mm(6), W, H], fill=NARANJA)
    return h


# ── contenido de muestra ───────────────────────────────────────────────
# Las fotos de muestra no viven en el repositorio: son de eventos reales, con
# caras de gente a la que nadie preguntó. `GEW_FOTOS` dice dónde están; sin esa
# variable se usan las de `ejemplo/fotos`, que son sintéticas y sí viajan.
F = os.environ.get("GEW_FOTOS", os.path.join(RAIZ, "ejemplo", "fotos"))

ED = {
    "titular": "Una semana en la que\nel país *emprendió*",
    "bajada": "Lo que pasó del 16 al 22 de noviembre, contado sin épica.",
    "fechas": TOK["campana"]["fechas"] + " de 2026",
    "cifra": "48",
    "cifra_pie": "organizaciones abrieron sus puertas",
    "cifra_texto": "Universidades, incubadoras, cámaras, colectivos y proyectos de una "
                   "sola persona. Ninguna cobró por participar y ninguna pidió permiso "
                   "para empezar.",
    "creditos": [("Edición", "Fundación Enlata"), ("Dirección", "{{NOMBRE}}"),
                 ("Diseño", "Sistema GEW · RD"), ("Fotografía", "Equipo de voluntarios"),
                 ("Contacto", "{{CORREO}}")],
    "kauffman": "La Semana Global de Emprendimiento es una iniciativa de la Global "
                "Entrepreneurship Network, cuyo socio fundador es la Kauffman Foundation.",
    "sobre_gew": "Millones de personas tienen las ideas, el talento y la ambición para "
                 "construir algo mejor, pero nunca han visto el emprendimiento como un "
                 "camino a su alcance. La Semana Global de Emprendimiento cambia eso.",
    "editorial_titular": "Nadie pidió *permiso*",
    "editorial": [
        "Cuando empezamos a llamar organizaciones en agosto, la pregunta que más nos "
        "hicieron fue quién pagaba. La respuesta era incómoda: nadie. Cada quien pone "
        "su sala, su tiempo y su gente.",
        "Cuarenta y ocho dijeron que sí de todos modos. Eso es lo que cuenta esta "
        "revista: no una semana de eventos, sino cuarenta y ocho decisiones de abrir "
        "la puerta sin saber cuánta gente iba a entrar.",
        "Lo que sigue son las cifras, las caras y las cosas que no salieron como "
        "esperábamos. También esas, porque el año que viene hay que hacerlo mejor.",
    ],
    "firma": "{{NOMBRE}}",
    "firma_cargo": "Presidente · Fundación Enlata",
    "indice": [(6, "Así se vivió", "Crónica de los siete días"),
               (12, "La semana en cifras", "Datos y alcance"),
               (16, "Las actividades", "Qué hizo cada aliado"),
               (22, "Las caras", "Galería"),
               (28, "Lo que falló", "Aprendizajes")],
}
CUERPO = [
    "La primera actividad abrió a las nueve de la mañana del lunes en la Cámara de "
    "Comercio, con más gente de la que cabía sentada.",
    "Para el miércoles el patrón ya estaba claro: las sesiones de la tarde llenaban y "
    "las de la mañana costaban.",
    "En los talleres pasó algo que no estaba en el plan: la mitad de las preguntas no "
    "eran sobre cómo empezar, sino sobre cómo sostener lo que ya estaba andando.",
    "El sábado, la final de Competencia Demo llenó el teatro de la Demo y dejó tres "
    "proyectos con reunión de seguimiento antes de fin de mes.",
    "El domingo cerramos en Sala Demo sin programa, solo con la gente que quiso "
    "quedarse a conversar. Fue la sesión más larga de la semana.",
]
CIFRAS = [("48", "organizaciones aliadas", "padrón del muro, enlata.do/gew"),
          ("{{N}}", "actividades registradas", "pendiente: sale del formulario"),
          ("{{N}}", "personas participantes", "pendiente: hoja de registro"),
          ("200", "países celebraron a la vez", "genglobal.org/gew")]
ITEMS = [{"titulo": "Talleres", "texto": "Formación práctica en sala, de dos a cuatro horas."},
         {"titulo": "Mesas de trabajo", "texto": "Conversaciones con moderación sobre un problema concreto."},
         {"titulo": "Competencias", "texto": "Pitch, hackathon y retos con jurado."},
         {"titulo": "Puertas abiertas", "texto": "Visitas a espacios que normalmente no se visitan."},
         {"titulo": "Encuentros", "texto": "Sin programa: gente que se conoce."},
         {"titulo": "En línea", "texto": "Para quien no pudo moverse de su provincia."}]
FOTOS = [f"{F}/v-tarima.webp", f"{F}/v-publico.webp", f"{F}/v-equipo.webp",
         f"{F}/v-acreditacion.webp", f"{F}/v-energia.webp", f"{F}/v-detalles.webp"]
PIES = ["La apertura, lunes 16", "Sala llena el miércoles", "El equipo de voluntarios",
        "Acreditación", "Cierre en Sala Demo", "Los detalles"]


# datos de reportería. Las cifras que no existen van como {{N}} a propósito.
PROV = {"Santo Domingo": 14, "Distrito Nacional": 11, "Santiago": 6,
        "La Vega": 2, "Puerto Plata": 2, "San Cristóbal": 1, "La Altagracia": 1,
        "Duarte": 1, "Espaillat": 1}
DESGLOSE_EV = [("Talleres", "{{N}}"), ("Mesas de trabajo", "{{N}}"),
               ("Competencias", "{{N}}"), ("Puertas abiertas", "{{N}}"),
               ("Encuentros", "{{N}}"), ("En línea", "{{N}}")]
DESGLOSE_IMP = [("Presencial", "{{N}}"), ("En línea", "{{N}}"),
                ("Estudiantes", "{{N}}"), ("Ya emprendiendo", "{{N}}"),
                ("Primera vez", "{{N}}")]
REPORTE = [
    ("Organizaciones aliadas", "48", "padrón del muro de enlata.do/gew"),
    ("Provincias con actividad", str(len(PROV)), "registro de actividades"),
    ("Actividades registradas", "{{N}}", "pendiente: formulario de actividades"),
    ("Personas participantes", "{{N}}", "pendiente: hojas de registro"),
    ("Menciones en prensa", "{{N}}", "pendiente: seguimiento de medios"),
    ("Alcance en redes", "{{N}}", "pendiente: métricas de IG y LinkedIn"),
]
DIAS = [("LUN 16", [("9:00", "Apertura nacional"), ("18:00", "Encuentro de aliados")]),
        ("MAR 17", [("10:00", "Taller de validación"), ("19:00", "Encuentro *semanal*")]),
        ("MIÉ 18", [("9:00", "Financiamiento sin banco"), ("18:00", "Taller de *finanzas*")]),
        ("JUE 19", [("8:00", "Ruta universitaria"), ("16:00", "Mesa de jóvenes")]),
        ("VIE 20", [("9:00", "Mujeres que emprenden"), ("17:00", "Networking")]),
        ("SÁB 21", [("14:00", "Competencia Demo · final")]),
        ("DOM 22", [("11:00", "Cierre y celebración")])]
EVENTO = {
    "seccion": "Cobertura", "titulo": "La final de *Competencia Demo*",
    "foto": f"{F}/v-tarima.webp",
    "ficha": [("Cuándo", "Sábado 21 · 5:00 pm"), ("Dónde", "Teatro Demo"),
              ("Organiza", "Fundación Enlata · IAvanza"),
              ("Asistencia", "{{N}} personas")],
    "cronica": "Ocho equipos, cinco minutos cada uno y un jurado que no dejó pasar "
               "ni una cifra sin fuente. La sala se llenó media hora antes de empezar "
               "y hubo gente de pie hasta el final. Lo que más se repitió en las "
               "preguntas del panel no fue el modelo de negocio: fue quién es el "
               "primer cliente y por qué va a pagar.",
    "cita": "No vinimos a ganar. Vinimos a que alguien nos dijera en la cara qué "
            "está mal.",
}
ALIADOS_RESUMEN = [
    ("JCI República Dominicana", "Taller y mesa de trabajo", "{{N}}"),
    ("Demo", "Sede de la final y ruta universitaria", "{{N}}"),
    ("PUCMM", "Dos talleres en Santiago", "{{N}}"),
    ("El Hueco", "Puertas abiertas toda la semana", "{{N}}"),
    ("Alterna Academy", "Formación en línea", "{{N}}"),
    ("Techstars", "Mentoría a los finalistas", "{{N}}"),
    ("Dominicana Tech Week", "Panel de tecnología", "{{N}}"),
    ("Organización", "Encuentro de creativos", "{{N}}"),
]
NIVELES = [("Patrocinador principal", [("{{PENDIENTE}}", None)], 22),
           ("Patrocinadores", [("{{PENDIENTE}}", None), ("{{PENDIENTE}}", None)], 16),
           ("Colaboran", [("{{PENDIENTE}}", None), ("{{PENDIENTE}}", None),
                          ("{{PENDIENTE}}", None)], 12)]
CARTA = {
    "fecha": "Santo Domingo, diciembre de 2026",
    "saludo": "A quienes abrieron una puerta esta semana:",
    "cuerpo": [
        "La Fundación Enlata es la organización anfitriona de la Semana Global de "
        "Emprendimiento en República Dominicana. Eso, en la práctica, significa muy "
        "poco: no organizamos las actividades, no ponemos las salas y no pagamos los "
        "cafés. Lo que hacemos es llamar, insistir y sostener el calendario.",
        "Las cuarenta y ocho organizaciones que aparecen en estas páginas son las que "
        "hicieron el trabajo. Cada una decidió abrir su espacio sin saber cuánta gente "
        "iba a entrar, y varias lo hicieron por primera vez.",
        "El año que viene queremos que sean más, y que lleguen a las provincias donde "
        "este año no llegamos. Si tu organización está leyendo esto y no participó, "
        "esa es la invitación.",
    ],
    "despedida": "Gracias por el tiempo y por la sala.",
    "firma": "{{NOMBRE}}",
    "cargo": "Presidente · Fundación Enlata · National Host GEW República Dominicana",
    "pie": "La Semana Global de Emprendimiento es una iniciativa de la Global "
           "Entrepreneurship Network, cuyo socio fundador es la Kauffman Foundation.",
}


def construir(rejilla=False):
    from revista_reporte import (mapa, reporteria, eventos, impacto, calendario,
                                 cobertura, resumen_aliados, patrocinadores,
                                 carta_host, promocional)
    ali = padron()
    hojas = [
        portada(ED, FOTOS[0]),
        retiracion_portada(ED),
        masthead(ED),
        editorial(ED),
        indice(ED),
        apertura(6, "Crónica", "Así se *vivió*", FOTOS[1]),
        lectura(7, "Crónica", "Siete días, *cuarenta y ocho* puertas",
                "Lo que pasó, en orden y sin adornos.", CUERPO,
                "La mitad de las preguntas no eran sobre cómo empezar, "
                "sino sobre cómo sostener."),
        datos(8, "Datos", "La semana en *cifras*", CIFRAS),
        tarjetas(9, "Actividades", "Qué *hizo* cada aliado", ITEMS),
        galeria(10, "Galería", "Las *caras* de la semana", FOTOS, PIES),
        muro(11, ali),
        carta_host(12, CARTA),
        reporteria(13, "La semana en *números*", REPORTE,
                   "Las cifras marcadas quedan pendientes hasta que cierren el "
                   "formulario de actividades y las hojas de registro. Un recap con "
                   "un número inventado es peor que uno con un hueco."),
        eventos(14, "{{N}}", DESGLOSE_EV,
                "El desglose sale del tipo que marcó cada aliado al registrar."),
        impacto(15, "{{N}}", DESGLOSE_IMP,
                "Presencial y en línea se cuentan por separado: no se suman."),
        mapa(16, PROV),
        calendario(17, DIAS),
        cobertura(18, EVENTO),
        resumen_aliados(19, ALIADOS_RESUMEN, 1, 6),
        patrocinadores(20, NIVELES,
                       "Los niveles y los nombres quedan pendientes de cerrar. "
                       "Ninguna marca se imprime antes de que el acuerdo esté firmado."),
        promocional(21),
    ]
    # el resto de páginas del pliego, en blanco pero contadas
    for n in range(22, PAGINAS - 1):
        h = Hoja(n)
        h.texto(h.x0, h.y0, "· en blanco ·", fuente("Light", mm(3.4)), "#DDDDDD")
        h.folio()
        hojas.append(h)
    hojas.append(retiracion_contra(PAGINAS - 1, ali))
    hojas.append(contraportada(ED))
    if rejilla:
        for h in hojas:
            h.rejilla()
    return hojas


def main():
    ap = argparse.ArgumentParser(description="Revista de recap GEW · RD")
    ap.add_argument("--pliego", action="store_true")
    ap.add_argument("--pdf", action="store_true")
    ap.add_argument("--rejilla", action="store_true")
    ap.add_argument("--cmyk", action="store_true",
                    help="convierte con el perfil genérico de macOS · sólo para ver")
    ap.add_argument("--salida", default=f"{RAIZ}/_salida/revista")
    a = ap.parse_args()

    os.makedirs(a.salida, exist_ok=True)
    hojas = construir(a.rejilla)
    print(f"producidas {len(hojas)} de {PAGINAS} esperadas")
    print(f"hoja {ANCHO_MM}×{ALTO_MM} mm @ {DPI} dpi = {W_HOJA}×{H_HOJA} px "
          f"· con sangrado de {SANGRADO_MM} mm = {W}×{H} px")
    print(f"creep máximo compensado: {creep(PAGINAS // 2)} px "
          f"({creep(PAGINAS // 2) / DPI * 25.4:.2f} mm)")

    malas, glifos, informes = 0, 0, []
    for h in hojas:
        inf = h.informe()
        informes.append(inf)
        if inf["desbordes"]:
            malas += 1
            for s, f in inf["desbordes"][:2]:
                print(f"  DESBORDE pág {h.n}: «{s}» se sale {f} px de la zona segura")
        if inf["glifos_faltantes"]:
            glifos += 1
            for s, g in inf["glifos_faltantes"]:
                print(f"  GLIFO FALTA pág {h.n}: «{s}» → {g}")
        im = h.im
        if a.cmyk:
            im = im.convert("CMYK")
        im.save(f"{a.salida}/{h.n:02d}.png", dpi=(DPI, DPI))
    print(f"páginas con desborde: {malas} · con glifos faltantes: {glifos}")

    # El informe se escribe para que `auditoria.py` pueda cruzarlo contra los
    # PNG. Sin esto la revista quedaba fuera del guardián del sistema: un
    # informe en verde que no cubre lo que se dibuja no vale de nada.
    with open(f"{a.salida}/informe.json", "w", encoding="utf-8") as f:
        json.dump({
            "_nota": "Lo que declara revista.py de cada página. Lo verifica "
                     "auditoria.py contra los PNG; no se edita a mano.",
            "generado": __import__("datetime").datetime.now()
                        .astimezone().isoformat(timespec="seconds"),
            "geometria": {
                "dpi": DPI, "paginas": PAGINAS,
                "hoja_mm": [ANCHO_MM, ALTO_MM], "hoja_px": [W_HOJA, H_HOJA],
                "sangrado_mm": SANGRADO_MM, "sangrado_px": SANG,
                "seguridad_mm": SEGURIDAD_MM, "seguridad_px": SEG,
                "lienzo_px": [W, H],
                "caja_segura_px": [SANG + SEG, SANG + SEG,
                                   SANG + W_HOJA - SEG, SANG + H_HOJA - SEG],
                "creep_max_px": creep(PAGINAS // 2),
            },
            "paginas": informes,
        }, f, ensure_ascii=False, indent=1)
    print(f"{a.salida}/informe.json")

    if a.pdf:
        ims = [Image.open(f"{a.salida}/{h.n:02d}.png").convert("RGB") for h in hojas]
        ims[0].save(f"{a.salida}/revista.pdf", save_all=True, append_images=ims[1:],
                    resolution=DPI)
        mb = os.path.getsize(f"{a.salida}/revista.pdf") / 1e6
        print(f"PDF: {len(ims)} páginas · {mb:.1f} MB")
    if malas:
        sys.exit(f"{malas} página(s) con contenido fuera de la zona segura")


if __name__ == "__main__":
    main()
