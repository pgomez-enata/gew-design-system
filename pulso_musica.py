#!/usr/bin/env python3
"""
El pulso EN MOVIMIENTO · GEW · RD.

El pulso ya existía quieto: 39 barras cuya altura es el ancho angular real de
cada segmento del anillo GEW·RD. Esto lo pone a sonar — a moverse como se
mueve la música, no como se mueve un adorno.

La idea que sostiene todo el motor:

    **el PICO de cada barra es su altura del anillo, exacta.**

Cada barra se normaliza por su propio máximo dentro del bucle, así que en algún
fotograma toda barra alcanza —clavada— la altura que le da el logo. Entre golpe
y golpe cae hasta el 42 % de esa altura. Dicho de otro modo: el pulso quieto no
es un estado distinto del pulso en movimiento, es su fotograma de acento. La
identidad no se parece: es la misma, y se mide (`--medir`).

Cuatro maneras de moverse, que no son cuatro estilos sino cuatro papeles:

    latido     todas las barras a la vez, sobre el tiempo. El más sobrio:
               sirve de fondo debajo de una voz sin robarle atención.
    ola        una cresta recorre las 39 barras, una vez por compás. Para
               transiciones y barridos: tiene dirección, lleva la vista.
    espectro   cada barra es una banda de frecuencia: los graves a la
               izquierda, lentos y con cuerpo; los agudos a la derecha,
               rápidos y secos. El que de verdad se lee como música.
    chispa     acentos en corcheas sobre grupos de barras. Nervioso, para
               energía alta y cortes rápidos.

**Cuál se usa, decidido por Piero el 6-sep-2026 y cerrado**: `latido` en todo
lo que lleve voz encima, `espectro` en todo lo que vaya solo. No hay que
recordarlo: `--papel voz` y `--papel solo` lo eligen. `ola` y `chispa` siguen
vivos, pero se piden a mano — no son el defecto de nada.

**La rejilla es musical, no decorativa.** Todo cuelga de un BPM, y el BPM tiene
que caer en fotogramas enteros: a 30 fps sólo valen los BPM de la forma
1800/k. 100 BPM da 18 fotogramas por tiempo y el bucle cierra al fotograma. Si
se pide otro, el motor dice cuál es el válido más cercano en vez de desajustar
medio fotograma por tiempo y desincronizar a los treinta segundos.

**La cabeza que flota** sobre cada barra es el pico retenido, cayendo despacio,
como en un vúmetro de aguja. Se dibuja SIEMPRE y del color de su barra: cuando
la barra está en su pico queda pegada encima y no se distingue; cuando la barra
cae, se queda arriba y baja sola. No se usa blanco en ningún sitio — los 30
colores del anillo son la identidad y no se tocan.

**El bucle es perfecto por construcción**: toda la modulación es periódica con
periodo igual al bucle. No se comprueba mirándolo: se mide el salto de altura
en el cierre contra el salto máximo dentro del bucle.

Uso:
    python3 pulso_musica.py --todos            los 4 modos × 4 formatos
    python3 pulso_musica.py --modo espectro --formato banda
    python3 pulso_musica.py --medir            sólo los números, sin renderizar
    python3 pulso_musica.py --contacto         las tiras para decidir sin vídeo
"""
import argparse, json, math, os, subprocess, sys

import numpy as np

from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
from campana import (SEGMENTOS, TOK, activo, fuente, marcas, png_alto)  # noqa: E402

C = TOK["campana"]
CARBON = TOK["color"]["campana2026"]["carbon"]["hex"]
NARANJA = TOK["color"]["campana2026"]["naranja"]["hex"]
BLANCO = "#FFFFFF"
N = len(SEGMENTOS)

# ── la rejilla musical ─────────────────────────────────────────────────
FPS = 30
BPM = 100          # 1800/100 = 18 fotogramas por tiempo, exacto
COMPASES = 2       # el bucle entero
TIEMPOS = 4        # por compás
# El acento del compás. El primer tiempo manda; el tercero contesta.
ACENTOS = (1.0, 0.55, 0.85, 0.60)
REPOSO = 0.34      # a cuánto de su pico cae una barra entre golpe y golpe
GRUESO_CABEZA = 4  # px de la cabeza del vúmetro (se escala con la pieza)
CAIDA_CABEZA = 0.028   # cuánto baja el pico retenido por fotograma
# Con 0,055 la cabeza alcanzaba a su barra dentro del mismo tiempo y no se
# veía flotar. A 0,028 tarda algo más de un tiempo en bajar del todo.

FORMATOS = {"banda": (1920, 270), "horizontal": (1920, 1080),
            "vertical": (1080, 1920), "cuadrado": (1080, 1080),
            # 4:5 · el vídeo de feed que más superficie ocupa en un móvil, y el
            # único lienzo de imagen del sistema que faltaba en vídeo. LinkedIn
            # lo publica para anuncios; Meta también, en 1440×1800.
            "retrato": (1080, 1350)}
# La zona que la interfaz de Stories tapa. Criterio nuestro: Meta no la publica.
SEGURA = {"vertical": (269, 1670)}
MODOS = ("latido", "ola", "espectro", "chispa")
# El modo NO se elige por gusto, se elige por el papel de la pieza. Cerrado por
# Piero el 6-sep-2026. Está aquí, en el motor, y no sólo en la documentación,
# porque una regla que hay que recordar es una regla que se olvida.
PAPELES = {"voz": "latido", "solo": "espectro"}
POR_QUE_PAPEL = {
    "voz": "lleva voz encima (talking head, entrevista, testimonio): el pulso "
           "es fondo y no debe robar atención",
    "solo": "va sola, sin nadie hablando (apertura, endcard, bumper, banda de "
            "web): el pulso es el contenido y tiene que sonar",
}
# Las dos hojas de trabajo y su ancho. Va aquí y no en cada función para que
# la auditoría compruebe contra el mismo número que produce el motor: fijar el
# umbral a mano en la auditoría es cómo una hoja de 1278 px falló una regla de
# 1080 escrita para su hermana.
ESC_CONTACTO, ESC_COMPARATIVA = 0.5, 0.62
BITRATE_KBPS = 6000
ANCHO_HOJA = {"contacto": 1080,
              "comparativa": round(1920 * ESC_COMPARATIVA) + 88}
CARBON_RGB = tuple(int(CARBON[i:i + 2], 16) for i in (1, 3, 5))


def rejilla(bpm=BPM, compases=COMPASES, tiempos=TIEMPOS, fps=FPS):
    """Los números del bucle. Falla si el BPM no cae en fotogramas enteros."""
    fr = fps * 60 / bpm
    if abs(fr - round(fr)) > 1e-9:
        k = max(1, round(fr))
        raise SystemExit(
            f"{bpm} BPM no cae en fotogramas enteros a {fps} fps "
            f"({fr:.4f} fotogramas por tiempo). El válido más cercano es "
            f"{fps*60/k:g} BPM ({k} fotogramas por tiempo).")
    golpes = compases * tiempos
    frames = round(fr) * golpes
    return {"bpm": bpm, "fps": fps, "compases": compases, "tiempos": tiempos,
            "golpes": golpes, "fr_por_tiempo": round(fr), "frames": frames,
            "dur": frames / fps}


# ── la energía: cuatro maneras de moverse ──────────────────────────────
def _lum(hexa):
    c = [int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contraste(a, b):
    l1, l2 = sorted((_lum(a), _lum(b)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


# WCAG: 4,5:1 para texto normal, 3:1 a partir de 14 pt en negrita = 18,66 px.
# El carbón sobre el naranja de campaña da 3,44:1 — con la pastilla a 16 px no
# llegaba, y en vez de cambiarle el color se sube el cuerpo por encima del
# umbral de «texto grande», que es donde 3,44 sí cumple.
CAP_PASTILLA = 19
PX_TEXTO_GRANDE = 18.66


def _sin01(x):
    return 0.5 + 0.5 * math.sin(2 * math.pi * x)


def _golpe(fase, golpes, k):
    """Un ataque instantáneo en cada tiempo y una caída exponencial. `fase` es
    la posición dentro del bucle, de 0 a 1: al ser exacta la vuelta, el ataque
    del primer tiempo y el cierre del bucle son el mismo instante."""
    pos = fase * golpes
    return ACENTOS[int(pos) % len(ACENTOS)] * math.exp(-k * (pos % 1.0))


def _e(modo, i, b, fase, G, CB):
    """La energía de la barra `i` en la fase `fase` del bucle (0 a 1).

    Toda expresión que dependa del número de golpe lleva su módulo DENTRO:
    sin él la función no es periódica y el bucle no cierra. Pasó con `chispa`,
    donde el patrón de barras encendidas cicla cada 3 corcheas y el bucle tiene
    32: al volver a empezar, el grupo que sonaba no era el mismo."""
    if modo == "latido":
        return _golpe(fase, G, 4.2)
    if modo == "ola":
        u = (fase * CB - i / N) % 1.0
        return 0.10 + 0.90 * math.exp(-(min(u, 1.0 - u) / 0.13) ** 2)
    if modo == "espectro":
        f1 = 1 + round(b * 3)
        f2 = f1 + 2 + (i % 3)
        osc = (0.58 * _sin01(f1 * fase + (i * 0.6180339887) % 1.0)
               + 0.42 * _sin01(f2 * fase + (i * 0.3819660113) % 1.0))
        return 0.38 * osc + 0.62 * _golpe(fase, G, 3.2 + 3.0 * b) * (1 - 0.45 * b)
    if modo == "chispa":
        pos = fase * G * 2                      # corcheas
        paso, frac = int(pos) % (G * 2), pos % 1.0
        on = ((i * 7 + paso * 13) % N) < 15
        return 0.08 + (0.92 * math.exp(-6.0 * frac) if on else 0.0)
    raise SystemExit(f"modo desconocido: {modo}")


def energia(modo, R, extra=0):
    """Matriz [barra][fotograma] en 0..1, periódica en el bucle.

    Al final cada FILA se normaliza por su propio máximo: por eso el pico de
    cada barra es su altura del anillo, exacta, y no una aproximación.
    Con `extra=1` se calcula un fotograma de más —el que vendría después del
    último— para comprobar que es idéntico al primero."""
    F, G, CB = R["frames"], R["golpes"], R["compases"]
    E = []
    for i in range(N):
        b = i / (N - 1)          # 0 = grave (izquierda) · 1 = agudo (derecha)
        fila = [max(0.0, min(1.0, _e(modo, i, b, f / F, G, CB)))
                for f in range(F + extra)]
        mx = max(fila[:F]) or 1.0
        E.append([v / mx for v in fila])
    return E


def cabezas(E, caida=CAIDA_CABEZA):
    """El pico retenido de cada barra, cayendo `caida` por fotograma. Se mira
    el bucle en círculo, así que la cabeza tampoco salta al volver a empezar."""
    F = len(E[0])
    H = []
    for fila in E:
        h = []
        for f in range(F):
            v = fila[f]
            for k in range(1, F):
                techo = 1.0 - caida * k
                if techo <= v:
                    break
                cand = fila[(f - k) % F] - caida * k
                if cand > v:
                    v = cand
            h.append(min(1.0, v))
        H.append(h)
    return H


# ── el dibujo ──────────────────────────────────────────────────────────
_MAXG = max(s["grados"] for s in SEGMENTOS)
BASES = [0.22 + 0.78 * s["grados"] / _MAXG for s in SEGMENTOS]   # la del sistema


def dibuja(d, x, y, ancho, alto, E, H, f, grueso=None, n=None):
    """El pulso en el fotograma `f`. Devuelve las alturas en px, medidas.

    `n` dibuja sólo las primeras `n` barras SIN estirar el resto: el paso sigue
    siendo `ancho/39`, así que el pulso APARECE de izquierda a derecha en su
    sitio definitivo. El `pulso()` estático recalcula el paso al recortar y las
    barras crecen a lo ancho; para un barrido animado eso se lee como un
    estiramiento, no como una entrada."""
    paso = ancho / N
    an = max(2, round(paso * 0.62))
    gr = grueso or max(2, round(alto * 0.030))
    alturas = []
    for i, s in enumerate(SEGMENTOS[:n] if n else SEGMENTOS):
        techo = alto * BASES[i]                       # su altura del anillo
        h = max(3, round(techo * (REPOSO + (1 - REPOSO) * E[i][f])))
        hp = max(3, round(techo * (REPOSO + (1 - REPOSO) * H[i][f])))
        xx = round(x + i * paso)
        d.rectangle([xx, y + alto - h, xx + an - 1, y + alto - 1], fill=s["hex"])
        yc = y + alto - hp
        d.rectangle([xx, yc, xx + an - 1, yc + gr - 1], fill=s["hex"])
        alturas.append(max(h, hp + gr))
    return alturas


def geometria(fmt):
    """Dónde va el pulso y cuánto mide, por formato."""
    w, h = FORMATOS[fmt]
    if fmt == "banda":
        m = round(w * 0.033)
        mv = round(h * 0.15)
        return {"w": w, "h": h, "x": m, "ancho": w - 2 * m,
                "y": mv, "alto": h - 2 * mv, "texto": False}
    top, bot = SEGURA.get(fmt, (round(h * 0.06), h - round(h * 0.06)))
    m = round(w * 0.0667)
    return {"w": w, "h": h, "x": m, "ancho": w - 2 * m, "top": top, "bot": bot,
            "m": m, "texto": True}


# El plano de la pieza se calcula UNA vez por formato, no por fotograma: pegar
# los logos para medir el bloque de marcas cuesta, y son 144 fotogramas.
_PLANOS = {}


def _tinta(d, txt, f):
    b = d.textbbox((0, 0), txt, font=f)
    return b, b[3] - b[1], b[2] - b[0]


def _cap_que_entra(d, txt, cap, ancho_max, peso="Bold"):
    """Baja el cuerpo hasta que la línea entra a lo ancho. La primera versión
    repartía por proporciones y las fechas se comían el bloque de marcas."""
    while cap > 8:
        f = fuente(peso, cap)
        if d.textlength(txt, font=f) <= ancho_max:
            return cap, f
        cap -= 1
    return cap, fuente(peso, cap)


def plano(fmt):
    """Apila la pieza de abajo arriba con medidas reales y devuelve las cajas
    de cada bloque, para que el solape se compruebe con números."""
    if fmt in _PLANOS:
        return _PLANOS[fmt]
    g = geometria(fmt)
    if not g["texto"]:
        _PLANOS[fmt] = g
        return g
    w, top, bot, m, U = g["w"], g["top"], g["bot"], g["m"], g["w"]
    tmp = Image.new("RGB", (g["w"], g["h"]), CARBON)
    d = ImageDraw.Draw(tmp)

    lock = png_alto(activo("logo/gew-rd-lockup-blanco.png"), round(w * 0.085))
    y_lock = top + round(w * 0.020)
    hueco = round(w * 0.030)

    # el bloque de marcas se MIDE pegándolo en una imagen de descarte
    med = marcas(tmp, d, m, 0, w - 2 * m, U, oscuro=True, cobertura=True)
    y_rot = bot - med["alto_usado"]

    cap_s, f_s = _cap_que_entra(d, C["sitio"], round(w * 0.030),
                                (w - 2 * m) * 0.9)
    cap_f, f_f = _cap_que_entra(d, C["fechas"], round(w * 0.038),
                                (w - 2 * m) * 0.9)
    b_s, h_s, an_s = _tinta(d, C["sitio"], f_s)
    b_f, h_f, an_f = _tinta(d, C["fechas"], f_f)

    base_s = y_rot - hueco                       # base de la tinta del sitio
    base_f = base_s - h_s - round(cap_f * 0.34)  # base de la tinta de la fecha
    tope_txt = base_f - h_f

    ini = y_lock + lock.height + hueco
    libre = tope_txt - hueco - ini
    alto_p = max(60, min(libre, round((bot - top) * 0.26)))
    y_p = ini + max(0, (libre - alto_p) // 2)

    P = dict(g)
    P.update({"lock": lock, "y_lock": y_lock, "x_lock": (w - lock.width) // 2,
              "f_sitio": f_s, "f_fechas": f_f, "b_sitio": b_s, "b_fechas": b_f,
              "base_sitio": base_s, "base_fechas": base_f,
              "y_rot": y_rot, "y_p": y_p, "alto_p": alto_p,
              "marcas": med, "U": U,
              "cajas": [("lockup", y_lock, y_lock + lock.height),
                        ("pulso", y_p, y_p + alto_p),
                        ("fechas", base_f - h_f, base_f),
                        ("sitio", base_s - h_s, base_s),
                        ("marcas", y_rot, y_rot + med["alto_usado"])],
              "anchos": [("fechas", an_f), ("sitio", an_s),
                         ("marcas", med["derecha"] - m)]})
    _PLANOS[fmt] = P
    return P


def solapes(fmt):
    """Cruza las cajas del plano. Cero es el único resultado aceptable."""
    P = plano(fmt)
    if not P.get("texto"):
        return []
    mal = []
    cs = P["cajas"]
    for i in range(len(cs)):
        for j in range(i + 1, len(cs)):
            (na, a0, a1), (nb, b0, b1) = cs[i], cs[j]
            px = min(a1, b1) - max(a0, b0)
            if px > 0:
                mal.append((na, nb, px))
    # y lo que se sale de la pieza, arriba, abajo o a lo ancho
    if cs[0][1] < P["top"]:
        mal.append(("lockup", "borde superior", P["top"] - cs[0][1]))
    if cs[-1][2] > P["bot"]:
        mal.append(("marcas", "borde inferior", cs[-1][2] - P["bot"]))
    for n, an in P["anchos"]:
        if an > P["ancho"]:
            mal.append((n, "ancho útil", an - P["ancho"]))
    return mal


def bucle(modo, R=None):
    """La pareja (energía, cabezas) de un modo, lista para dibujar. Es lo que
    piden los motores de vídeo: se calcula una vez y se pasa a cada fotograma."""
    R = R or rejilla()
    E = energia(modo, R)
    return E, cabezas(E), R


def frame(fmt, f, E, H, alfa=False):
    P = plano(fmt)
    w, h = P["w"], P["h"]
    im = (Image.new("RGBA", (w, h), (0, 0, 0, 0)) if alfa
          else Image.new("RGB", (w, h), CARBON))
    d = ImageDraw.Draw(im)
    if not P["texto"]:
        dibuja(d, P["x"], P["y"], P["ancho"], P["alto"], E, H, f)
        return im

    im.paste(P["lock"], (P["x_lock"], P["y_lock"]), P["lock"])
    dibuja(d, P["x"], P["y_p"], P["ancho"], P["alto_p"], E, H, f)
    for clave, col, base, fo, bb in (
            ("fechas", BLANCO, P["base_fechas"], P["f_fechas"], P["b_fechas"]),
            ("sitio", NARANJA, P["base_sitio"], P["f_sitio"], P["b_sitio"])):
        txt = C[clave]
        d.text(((w - (bb[2] - bb[0])) // 2 - bb[0], base - bb[3]), txt,
               font=fo, fill=col)
    marcas(im, ImageDraw.Draw(im), P["m"], P["y_rot"], w - 2 * P["m"], P["U"],
           oscuro=True, cobertura=True)
    return im


# ── montaje ────────────────────────────────────────────────────────────
def monta(fmt, modo, E, H, R, salida, alfa=False):
    g = geometria(fmt)
    w, h = g["w"], g["h"]
    return monta_seq((frame(fmt, f, E, H, alfa=alfa) for f in range(R["frames"])),
                     w, h, salida, R["fps"], alfa)


def monta_seq(ims, w, h, salida, fps=FPS, alfa=False):
    """Monta una secuencia de imágenes PIL. Los otros motores de vídeo la usan
    tal cual: el conocimiento de ffmpeg vive en un solo sitio."""
    if alfa:
        # ⚠️ NO es WebM/VP9, y conviene saber por qué. Pidiéndole yuva420p,
        # este ffmpeg escribe `alpha_mode=1` en el contenedor —la etiqueta que
        # todo el mundo mira— y codifica el flujo en yuv420p: el fichero dice
        # que lleva alfa y al abrirlo el fondo sale negro opaco. Se midió
        # decodificando un fotograma, no leyendo la etiqueta.
        # ProRes 4444 sí lo lleva, es lo que traga cualquier montador, y al ser
        # 4:4:4 devuelve los hex del anillo exactos en vez de corridos por el
        # submuestreo de color.
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo",
               "-pix_fmt", "rgba", "-s", f"{w}x{h}", "-r", str(fps),
               "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444",
               "-pix_fmt", "yuva444p10le", salida]
    else:
        # H.264 High + yuv420p es lo que pide YouTube. CBR estricto porque con
        # CRF un fondo plano baja de los 516 kbps que documenta TikTok.
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo",
               "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps),
               "-i", "-", "-c:v", "libx264", "-profile:v", "high",
               "-pix_fmt", "yuv420p", "-b:v", f"{BITRATE_KBPS}k",
               "-minrate", f"{BITRATE_KBPS}k", "-maxrate", f"{BITRATE_KBPS}k",
               "-bufsize", f"{BITRATE_KBPS}k", "-x264-params", "nal-hrd=cbr",
               "-preset", "medium", "-movflags", "+faststart", salida]
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                         stderr=subprocess.PIPE)
    for im in ims:
        p.stdin.write(im.tobytes())
    p.stdin.close()
    err = p.stderr.read().decode()[:200]
    if p.wait():
        return {"error": err}
    m = sonda(salida)
    if alfa:
        m.update(alfa_real(salida))
    return m


def alfa_real(ruta):
    """¿El alfa está DENTRO, o sólo en la etiqueta? Se decodifica un fotograma
    y se mira. Además se cuenta cuántos de los 30 colores del anillo salen
    intactos: el submuestreo de color los corre uno o dos puntos."""
    tmp = f"{ruta}.frame.png"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", ruta,
                    "-frames:v", "1", "-pix_fmt", "rgba", tmp],
                   capture_output=True)
    if not os.path.exists(tmp):
        return {"fondo_alfa": None, "hay_opaco": False, "del_anillo": 0}
    im = Image.open(tmp).convert("RGBA")
    px = im.load()
    esquina = px[0, 0][3]
    cols = im.getcolors(1 << 22) or []
    opacos = {"#%02X%02X%02X" % c[1][:3] for c in cols if c[1][3] == 255}
    os.remove(tmp)
    anillo = {s["hex"].upper() for s in SEGMENTOS}
    return {"fondo_alfa": esquina, "hay_opaco": bool(opacos),
            "del_anillo": len(anillo & opacos), "anillo_total": len(anillo)}


def se_mueve(ruta, a, b):
    """¿El pulso cambia de verdad entre dos fotogramas de la pieza ENTREGADA?

    Se mide sobre el MP4, no sobre lo que compuse: si el bucle se quedara
    clavado en el fotograma 0 —un `% frames` mal puesto, un `t` que no avanza—
    el vídeo saldría con el pulso quieto y todo lo demás seguiría en verde.
    Un lote que revienta a la mitad no lanza error; uno que se queda quieto,
    tampoco."""
    fr = []
    for i in (a, b):
        tmp = f"{ruta}.{i}.png"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", ruta,
                        "-vf", f"select=eq(n\\,{i})", "-vsync", "0",
                        "-frames:v", "1", tmp], capture_output=True)
        if not os.path.exists(tmp):
            return None
        fr.append(np.array(Image.open(tmp).convert("RGB")).astype(int))
        os.remove(tmp)
    return int((np.abs(fr[0] - fr[1]).sum(axis=2) > 20).sum())


def queda_al_final(ruta, umbral=30):
    """Cuánta tinta queda en el último fotograma frente a la que había a mitad
    de pieza. Es la medida que destapó que ninguna pieza salía: las siete
    terminaban con el 91,6–98,7 % en pantalla, cortadas en seco."""
    n = sonda(ruta).get("frames") or 0
    if n < 3:
        return None
    def tinta(i):
        t = f"{ruta}.q{i}.png"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", ruta,
                        "-vf", f"select=eq(n\\,{i})", "-vsync", "0",
                        "-frames:v", "1", t], capture_output=True)
        if not os.path.exists(t):
            return None
        a = np.array(Image.open(t).convert("RGB")).astype(int)
        os.remove(t)
        return int((np.abs(a - np.array(CARBON_RGB)).sum(axis=2) > umbral).sum())
    antes, final = tinta(round(n * 0.60)), tinta(n - 1)
    if antes is None or final is None or not antes:
        return None
    # Y cuánto FONDO queda a la vista en el último fotograma: es lo que
    # distingue una cortina que cierra de una que sólo crece. La primera
    # versión de `cierra` daba 460 % de tinta y seguía dejando ver el
    # contenido por los huecos entre barras.
    tot = None
    t = f"{ruta}.libre.png"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", ruta,
                    "-vf", f"select=eq(n\\,{n-1})", "-vsync", "0",
                    "-frames:v", "1", t], capture_output=True)
    if os.path.exists(t):
        a = np.array(Image.open(t).convert("RGB")).astype(int)
        os.remove(t)
        tot = 100 * int((np.abs(a - np.array(CARBON_RGB)).sum(axis=2)
                         <= umbral).sum()) / (a.shape[0] * a.shape[1])
    return {"antes": antes, "final": final, "queda": 100 * final / antes,
            "fondo_libre": tot}


def sonda(ruta):
    """Lo que el fichero ES, preguntado a ffprobe. Nunca lo que yo supuse."""
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,r_frame_rate,nb_frames,codec_name,profile,pix_fmt",
         "-show_entries", "format=duration,size,bit_rate", "-of", "json", ruta],
        capture_output=True, text=True)
    d = json.loads(r.stdout or "{}")
    s = (d.get("streams") or [{}])[0]
    fo = d.get("format", {})
    num, den = (s.get("r_frame_rate", "0/1").split("/") + ["1"])[:2]
    n = int(s.get("nb_frames") or 0)
    if not n:   # VP9 en webm no siempre lo declara: se cuenta
        c = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                            "-count_frames", "-show_entries",
                            "stream=nb_read_frames", "-of", "csv=p=0", ruta],
                           capture_output=True, text=True)
        n = int((c.stdout.strip() or "0").rstrip(","))
    return {"px": f"{s.get('width')}x{s.get('height')}",
            "fps": round(int(num) / max(1, int(den)), 2), "frames": n,
            "codec": s.get("codec_name"), "perfil": s.get("profile") or "—",
            "pix_fmt": s.get("pix_fmt"),
            "seg": round(float(fo.get("duration", 0)), 3),
            "bytes": int(fo.get("size", 0)),
            "kbps": round(int(fo.get("bit_rate", 0)) / 1000)}


# ── GIF con los colores exactos ────────────────────────────────────────
def _paleta_exacta():
    """La paleta del GIF se construye a mano con los hex del anillo y el
    carbón. Con paleta adaptativa el cuantizador inventa tonos intermedios y
    los 30 colores medidos dejan de ser los 30 colores medidos."""
    cols = [CARBON] + sorted({s["hex"] for s in SEGMENTOS})
    datos = []
    for c in cols:
        datos += [int(c[i:i + 2], 16) for i in (1, 3, 5)]
    datos += [0, 0, 0] * (256 - len(cols))
    p = Image.new("P", (1, 1))
    p.putpalette(datos)
    return p, cols


def gif(modo, E, H, R, salida, escala=0.5, salta=2):
    """El bucle en GIF, para donde no entra vídeo. A media escala y a la mitad
    de fotogramas: un GIF de 1920 px y 144 fotogramas no lo abre nadie."""
    pal, cols = _paleta_exacta()
    w, h = FORMATOS["banda"]
    tam = (round(w * escala), round(h * escala))
    ims = []
    for f in range(0, R["frames"], salta):
        # NEAREST a propósito: cualquier otro filtro mezcla píxeles vecinos e
        # inventa colores que no están en el anillo.
        im = frame("banda", f, E, H).resize(tam, Image.NEAREST)
        ims.append(im.quantize(palette=pal, dither=Image.Dither.NONE))
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    ims[0].save(salida, save_all=True, append_images=ims[1:], loop=0,
                duration=round(1000 * salta / R["fps"]), disposal=2,
                optimize=False)
    # se mide sobre el fichero ya escrito, no sobre lo que creo que escribí
    leido = Image.open(salida)
    vistos = set()
    for i in range(leido.n_frames):
        leido.seek(i)
        vistos |= {"#%02X%02X%02X" % c[1] for c in
                   leido.convert("RGB").getcolors(65536)}
    anillo = {s["hex"].upper() for s in SEGMENTOS}
    return {"px": f"{tam[0]}x{tam[1]}", "frames": leido.n_frames,
            "bytes": os.path.getsize(salida),
            "seg": round(leido.n_frames * salta / R["fps"], 3),
            "colores": len(vistos),
            "del_anillo": len(anillo & vistos), "anillo_total": len(anillo)}


# ── SVG animado, para la web y el repo ─────────────────────────────────
def svg(modo, E, H, R, salida):
    """El mismo bucle en SVG con SMIL: pesa poco, escala sin perder y no
    necesita reproductor. Los valores son los MISMOS que los del vídeo —
    salen de la misma matriz—, así que la web y el MP4 no se separan."""
    g = geometria("banda")
    w, h, x0, y0, ancho, alto = (g["w"], g["h"], g["x"], g["y"], g["ancho"],
                                 g["alto"])
    paso = ancho / N
    an = max(2, round(paso * 0.62))
    gr = max(2, round(alto * 0.022))
    F, dur = R["frames"], R["dur"]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
           f'width="{w}" height="{h}" role="img" '
           f'aria-label="Pulso GEW RD, modo {modo}">',
           f'<title>Pulso GEW · RD — {modo}</title>',
           # con id para poder quitarlo o cambiarlo por CSS: sin este rect,
           # el mismo fichero sirve de overlay sobre transparente
           f'<rect id="fondo" width="{w}" height="{h}" fill="{CARBON}"/>']
    base = y0 + alto

    def serie(fn):
        # F+1 valores: el último repite el primero y el bucle cierra sin salto
        v = [fn(f % F) for f in range(F + 1)]
        return ";".join(str(round(u, 1)) for u in v)

    for i, s in enumerate(SEGMENTOS):
        techo = alto * BASES[i]
        xx = round(x0 + i * paso)
        alt = lambda f, M=E[i]: max(3, round(techo * (REPOSO + (1 - REPOSO) * M[f])))
        # ⚠️ `y` y `height` van TAMBIÉN como atributos estáticos, con el valor
        # del fotograma 0. Sin ellos, cualquier visor que no ejecute SMIL
        # —rsvg-convert, más de una vista previa, cualquier conversor a PDF—
        # dibuja rectángulos de altura cero y el fichero se ve vacío.
        out.append(
            f'<rect x="{xx}" width="{an}" y="{base - alt(0)}" '
            f'height="{alt(0)}" fill="{s["hex"]}">'
            f'<animate attributeName="y" dur="{dur}s" repeatCount="indefinite" '
            f'calcMode="linear" values="{serie(lambda f: base - alt(f))}"/>'
            f'<animate attributeName="height" dur="{dur}s" '
            f'repeatCount="indefinite" calcMode="linear" '
            f'values="{serie(alt)}"/></rect>')
        altp = lambda f, M=H[i]: max(3, round(techo * (REPOSO + (1 - REPOSO) * M[f])))
        out.append(
            f'<rect x="{xx}" width="{an}" height="{gr}" y="{base - altp(0)}" '
            f'fill="{s["hex"]}">'
            f'<animate attributeName="y" dur="{dur}s" repeatCount="indefinite" '
            f'calcMode="linear" values="{serie(lambda f: base - altp(f))}"/>'
            f'</rect>')
    out.append("</svg>")
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    txt = "\n".join(out)
    open(salida, "w", encoding="utf-8").write(txt)
    return {"bytes": len(txt.encode()), "barras": N, "animaciones": N * 3,
            "valores": N * 3 * (F + 1), "dur": dur}


# ── la tira de contacto: decidir sin abrir un vídeo ────────────────────
def contacto(modo, E, H, R, salida, tomas=6):
    """Seis instantes repartidos por el bucle, apilados y rotulados con su
    posición musical. Es la pieza que se mira para elegir modo."""
    esc = ESC_CONTACTO
    w, h = FORMATOS["banda"]
    tw, th = round(w * esc), round(h * esc)
    W = ANCHO_HOJA["contacto"]
    m = (W - tw) // 2
    cab, rot = 92, 26
    Hh = cab + tomas * (th + rot) + m
    im = Image.new("RGB", (W, max(1080, Hh)), CARBON)
    d = ImageDraw.Draw(im)
    ft = fuente("Bold", 34)
    fr = fuente("Light", 19)
    tit = f"pulso · {modo}"
    d.text((m, 34), tit, font=ft, fill=BLANCO)
    sub = (f'{R["bpm"]} BPM · {R["compases"]} compases · {R["dur"]:g} s · '
           f'{R["frames"]} fotogramas')
    bb = d.textbbox((0, 0), sub, font=fr)
    d.text((W - m - (bb[2] - bb[0]) - bb[0], 44), sub, font=fr, fill="#B8B8B8")
    for j in range(tomas):
        f = round(j * R["frames"] / tomas)
        y = cab + j * (th + rot)
        im.paste(frame("banda", f, E, H).resize((tw, th), Image.NEAREST), (m, y))
        t_mus = f / R["fr_por_tiempo"]
        d.text((m, y + th + 4),
               f'compás {int(t_mus // R["tiempos"]) + 1} · tiempo '
               f'{int(t_mus % R["tiempos"]) + 1} · fotograma {f}',
               font=fr, fill="#9A9A9A")
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    im.save(salida)
    return {"px": f"{im.width}x{im.height}", "tomas": tomas,
            "bytes": os.path.getsize(salida)}


def comparativa(R, salida, f_muestra=8):
    """Los cuatro modos en el MISMO instante del compás, apilados. Es la hoja
    que enseña la diferencia entre los cuatro de un vistazo: el mismo golpe,
    cuatro maneras de repartirlo entre las 39 barras."""
    esc = ESC_COMPARATIVA
    w, h = FORMATOS["banda"]
    tw, th = round(w * esc), round(h * esc)
    W = ANCHO_HOJA["comparativa"]
    rot = 44
    tit = "el pulso sonando · los cuatro modos"
    sub = (f'mismo fotograma ({f_muestra}) · {R["bpm"]:g} BPM · '
           f'{R["dur"]:g} s · bucle exacto')
    ft, fr = fuente("Bold", 36), fuente("Light", 21)
    tmp = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    # ⚠️ la primera versión ponía el subtítulo a la derecha del título en la
    # misma línea y se pisaban 230 px. Van apilados y se comprueba con las
    # cajas, no a ojo.
    an_t = tmp.textlength(tit, font=ft)
    an_s = tmp.textlength(sub, font=fr)
    una_linea = an_t + 40 + an_s <= W - 88
    cab = 96 if una_linea else 128
    im = Image.new("RGB", (W, cab + len(MODOS) * (th + rot) + 30), CARBON)
    d = ImageDraw.Draw(im)
    d.text((44, 30), tit, font=ft, fill=BLANCO)
    bb = d.textbbox((0, 0), sub, font=fr)
    d.text((W - 44 - (bb[2] - bb[0]) - bb[0], 40) if una_linea
           else (44, 84 - bb[1]), sub, font=fr, fill="#B8B8B8")
    if not una_linea and 44 + an_t > W - 44:
        raise SystemExit("el título de la comparativa no cabe a lo ancho")
    QUE = {"latido": "todas a la vez, sobre el tiempo · fondo bajo una voz",
           "ola": "una cresta recorre las 39 · transiciones, tiene dirección",
           "espectro": "cada barra una banda · el que se lee como música",
           "chispa": "acentos en corcheas por grupos · energía alta"}
    DEF = {v: k for k, v in PAPELES.items()}
    for j, m in enumerate(MODOS):
        E = energia(m, R)
        y = cab + j * (th + rot)
        im.paste(frame("banda", f_muestra, E, cabezas(E)).resize((tw, th),
                                                                 Image.NEAREST),
                 (44, y))
        d.text((44, y + th + 8), m, font=fuente("Bold", 24), fill=BLANCO)
        x = 44 + d.textlength(m, font=fuente("Bold", 24)) + 14
        if m in DEF:
            # la pastilla del defecto: naranja de campaña, texto en carbón
            et = f"por defecto · {DEF[m]}"
            fe = fuente("Bold", CAP_PASTILLA)
            an = d.textlength(et, font=fe)
            d.rounded_rectangle([x, y + th + 10, x + an + 24, y + th + 42],
                                radius=16, fill=NARANJA)
            d.text((x + 12, y + th + 15), et, font=fe, fill=CARBON)
            x += an + 36
        d.text((x, y + th + 12), QUE[m], font=fuente("Light", 19), fill="#9A9A9A")
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    im.save(salida)
    ratio = contraste(CARBON, NARANJA)
    umbral = 3.0 if CAP_PASTILLA >= PX_TEXTO_GRANDE else 4.5
    if ratio < umbral:
        raise SystemExit(f"la pastilla del defecto da {ratio:.2f}:1 y su cuerpo "
                         f"de {CAP_PASTILLA} px pide {umbral}:1")
    return {"px": f"{im.width}x{im.height}", "modos": len(MODOS),
            "pastilla": f"{ratio:.2f}:1 a {CAP_PASTILLA} px (umbral {umbral})",
            "cabecera": "1 línea" if una_linea else "2 líneas",
            "solape_cabecera": max(0, round(44 + an_t + 40 - (W - 44 - an_s)))
            if una_linea else 0,
            "bytes": os.path.getsize(salida)}


# ── lo que se mide del movimiento, no de los ficheros ──────────────────
def medidas(modo, E, H, R, alto=300):
    """Las tres preguntas que decide este motor:
    ¿el pico sigue siendo el anillo? ¿el bucle cierra? ¿se mueve de verdad?"""
    picos = [max(f for f in fila) for fila in E]
    techo = [alto * b for b in BASES]
    pico_px = [round(t * (REPOSO + (1 - REPOSO) * p)) for t, p in zip(techo, picos)]
    grados = [s["grados"] for s in SEGMENTOS]

    def pearson(a, b):
        n = len(a)
        ma, mb = sum(a) / n, sum(b) / n
        num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
        da = math.sqrt(sum((x - ma) ** 2 for x in a))
        db = math.sqrt(sum((y - mb) ** 2 for y in b))
        return num / (da * db) if da and db else 0.0

    F = R["frames"]
    # La prueba de bucle perfecto no es «el cierre no salta»: un ataque de
    # tiempo fuerte SÍ salta, y es lo que tiene que hacer. La prueba es que el
    # fotograma que vendría después del último sea idéntico al primero.
    Ex = energia(modo, R, extra=1)
    periodico = max(abs(f[F] - f[0]) for f in Ex)
    series = [[max(3, round(techo[i] * (REPOSO + (1 - REPOSO) * E[i][f])))
               for f in range(F)] for i in range(N)]
    salto_int = max(max(abs(s[f + 1] - s[f]) for f in range(F - 1)) for s in series)
    salto_cierre = max(abs(s[0] - s[-1]) for s in series)
    # y el salto del cierre tiene que ser el MISMO que el del tiempo fuerte
    # equivalente dentro del bucle: el downbeat del compás siguiente.
    db = F // R["compases"]
    salto_db = max(abs(s[db] - s[db - 1]) for s in series)
    recorridos = [max(s) - min(s) for s in series]
    quietas = sum(1 for r in recorridos if r < 3)
    return {
        "pico_normalizado": round(min(picos), 6),
        "pico_vs_grados": round(pearson(pico_px, grados), 6),
        "estatico_vs_pico": max(abs(round(t) - p) for t, p in zip(techo, pico_px)),
        "periodico": periodico,
        "bucle_cierra": periodico < 1e-12,
        "salto_cierre": salto_cierre, "salto_downbeat": salto_db,
        "salto_interno": salto_int,
        "cierre_como_downbeat": abs(salto_cierre - salto_db) <= 1,
        "recorrido_min": min(recorridos), "recorrido_med": round(
            sum(recorridos) / N, 1), "recorrido_max": max(recorridos),
        "barras_quietas": quietas,
    }


# ── corrida ────────────────────────────────────────────────────────────
DIR_MOV = f"{RAIZ}/_salida/pulso-mov"
DIR_PNG = f"{RAIZ}/_salida/pulso"


def main():
    ap = argparse.ArgumentParser(description="El pulso en movimiento · GEW·RD")
    ap.add_argument("--modo", choices=MODOS)
    ap.add_argument("--papel", choices=sorted(PAPELES),
                    help="voz → latido · solo → espectro (la regla del sistema)")
    ap.add_argument("--formato", choices=sorted(FORMATOS))
    ap.add_argument("--bpm", type=float, default=BPM)
    ap.add_argument("--compases", type=int, default=COMPASES)
    ap.add_argument("--fps", type=int, default=FPS)
    ap.add_argument("--todos", action="store_true")
    ap.add_argument("--medir", action="store_true",
                    help="sólo los números del movimiento, sin renderizar")
    ap.add_argument("--contacto", action="store_true",
                    help="sólo las tiras para decidir modo")
    a = ap.parse_args()
    if a.papel and a.modo and PAPELES[a.papel] != a.modo:
        sys.exit(f"--papel {a.papel} pide «{PAPELES[a.papel]}» y se pidió "
                 f"«{a.modo}». Se elige uno de los dos, no los dos.")
    if a.papel:
        a.modo = PAPELES[a.papel]
        print(f"papel «{a.papel}» → modo «{a.modo}»: {POR_QUE_PAPEL[a.papel]}")
    R = rejilla(a.bpm, a.compases, fps=a.fps)
    modos = [a.modo] if a.modo else list(MODOS)
    E = {m: energia(m, R) for m in modos}
    H = {m: cabezas(E[m]) for m in modos}

    print(f'rejilla · {R["bpm"]:g} BPM · {R["compases"]} compases de '
          f'{R["tiempos"]} · {R["fr_por_tiempo"]} fotogramas por tiempo · '
          f'{R["frames"]} fotogramas · {R["dur"]:g} s a {R["fps"]} fps')

    fallos, hechos, esperados = [], [], 0
    print(f'\n{"modo":10} {"pico=anillo":>12} {"r(pico,grados)":>15} '
          f'{"periódico":>10} {"cierre/downbt":>15} {"recorrido px":>18} '
          f'{"quietas":>8}')
    for m in modos:
        M = medidas(m, E[m], H[m], R)
        print(f'  {m:8} {"sí" if M["estatico_vs_pico"] == 0 else "NO":>12} '
              f'{M["pico_vs_grados"]:15.6f} '
              f'{("sí" if M["bucle_cierra"] else "NO"):>10} '
              f'{str(M["salto_cierre"]) + " / " + str(M["salto_downbeat"]):>15} '
              f'{str(M["recorrido_min"]) + "–" + str(M["recorrido_max"]):>10} '
              f'(med {M["recorrido_med"]:>5}) {M["barras_quietas"]:8}')
        if M["estatico_vs_pico"] != 0:
            fallos.append(f'  FALLA {m}: el pico no es la altura del anillo '
                          f'({M["estatico_vs_pico"]} px de diferencia)')
        if M["pico_vs_grados"] < 0.9999:
            fallos.append(f'  FALLA {m}: r(pico, grados) = '
                          f'{M["pico_vs_grados"]:.6f}, y debe ser 1')
        if not M["bucle_cierra"]:
            fallos.append(f'  FALLA {m}: el bucle no es periódico — el '
                          f'fotograma siguiente al último se desvía '
                          f'{M["periodico"]:.6g} del primero')
        # `cierre / downbeat` es INFORMATIVO, no una regla. Se probó como
        # regla y marcaba `espectro` y `chispa`: en los dos, el compás 2 no
        # suena igual que el 1 —osciladores en otra posición, otro grupo de
        # barras encendidas— y eso es justo lo que evita que el bucle se note.
        # Lo que sí es regla es la periodicidad, y esa es exacta.
        if M["barras_quietas"]:
            fallos.append(f'  FALLA {m}: {M["barras_quietas"]} barras no se '
                          f'mueven (recorrido < 3 px)')
    if a.medir:
        print(f"\n{len(fallos)} fallos")
        for f in fallos:
            print(f)
        sys.exit(1 if fallos else 0)

    if not shutil_which("ffmpeg"):
        sys.exit("falta ffmpeg: brew install ffmpeg")

    if a.contacto:
        print()
        for m in modos:
            esperados += 1
            r = contacto(m, E[m], H[m], R, f"{DIR_PNG}/{m}--contacto.png")
            hechos.append(f"{DIR_PNG}/{m}--contacto.png")
            print(f'  contacto {m:10} {r["px"]:>10} {r["tomas"]} tomas '
                  f'{r["bytes"]/1024:8.0f} KB')
        cierra(hechos, esperados, fallos)

    fmts = [a.formato] if a.formato else sorted(FORMATOS)
    print(f'\n{"pieza":26} {"px":>10} {"fps":>5} {"seg":>6} {"frames":>7} '
          f'{"códec":>10} {"pix_fmt":>9} {"kbps":>6} {"MB":>6}')
    for m in modos:
        for fmt in fmts:
            esperados += 1
            p = f"{DIR_MOV}/pulso-{m}--{fmt}.mp4"
            s = monta(fmt, m, E[m], H[m], R, p)
            if "error" in s:
                fallos.append(f'  FALLA {m}/{fmt}: {s["error"]}')
                continue
            hechos.append(p)
            print(f'  {m+"/"+fmt:24} {s["px"]:>10} {s["fps"]:5} {s["seg"]:6.2f} '
                  f'{s["frames"]:7} {s["codec"]:>10} {s["pix_fmt"]:>9} '
                  f'{s["kbps"]:6} {s["bytes"]/1e6:6.2f}')
            esp = "x".join(map(str, FORMATOS[fmt]))
            if s["px"] != esp:
                fallos.append(f'  FALLA {m}/{fmt}: lienzo {s["px"]}, esperado {esp}')
            if s["frames"] != R["frames"]:
                fallos.append(f'  FALLA {m}/{fmt}: {s["frames"]} fotogramas, '
                              f'esperados {R["frames"]}')
            if abs(s["seg"] - R["dur"]) > 0.05:
                fallos.append(f'  FALLA {m}/{fmt}: dura {s["seg"]} s y el bucle '
                              f'es de {R["dur"]:g}')
            if s["pix_fmt"] != "yuv420p":
                fallos.append(f'  FALLA {m}/{fmt}: pix_fmt {s["pix_fmt"]}')
            if s["kbps"] < 516:
                fallos.append(f'  FALLA {m}/{fmt}: {s["kbps"]} kbps, por debajo '
                              f'del mínimo documentado de TikTok (516)')

    if not a.formato:
        print(f'\n{"banda con alfa (prores)":26} {"px":>10} {"frames":>7} '
              f'{"pix_fmt":>14} {"fondo α":>8} {"MB":>6}')
        for m in modos:
            esperados += 1
            p = f"{DIR_MOV}/pulso-{m}--banda-alfa.mov"
            s = monta("banda", m, E[m], H[m], R, p, alfa=True)
            if "error" in s:
                fallos.append(f'  FALLA {m}/alfa: {s["error"]}')
                continue
            hechos.append(p)
            print(f'  {m:24} {s["px"]:>10} {s["frames"]:7} {s["pix_fmt"]:>14} '
                  f'{str(s["fondo_alfa"]):>8} {s["bytes"]/1e6:6.2f}')
            if not s["pix_fmt"].startswith("yuva"):
                fallos.append(f'  FALLA {m}/alfa: {s["pix_fmt"]}, y el alfa '
                              f'necesita un pix_fmt con «a»')
            if s["fondo_alfa"] != 0:
                fallos.append(f'  FALLA {m}/alfa: el fondo del fotograma '
                              f'decodificado tiene alfa {s["fondo_alfa"]}, y '
                              f'debe ser 0 — la etiqueta del contenedor no basta')
            if not s["hay_opaco"]:
                fallos.append(f'  FALLA {m}/alfa: no hay ningún píxel opaco; '
                              f'el fichero está entero transparente')
            if s["del_anillo"] != s["anillo_total"]:
                fallos.append(f'  FALLA {m}/alfa: {s["del_anillo"]} de los '
                              f'{s["anillo_total"]} colores del anillo intactos')
            if s["frames"] != R["frames"]:
                fallos.append(f'  FALLA {m}/alfa: {s["frames"]} fotogramas, '
                              f'esperados {R["frames"]}')

        print(f'\n{"banda en gif":26} {"px":>10} {"frames":>7} {"colores":>8} '
              f'{"del anillo":>11} {"MB":>6}')
        for m in modos:
            esperados += 1
            p = f"{DIR_MOV}/pulso-{m}--banda.gif"
            s = gif(m, E[m], H[m], R, p)
            hechos.append(p)
            print(f'  {m:24} {s["px"]:>10} {s["frames"]:7} {s["colores"]:8} '
                  f'{str(s["del_anillo"])+"/"+str(s["anillo_total"]):>11} '
                  f'{s["bytes"]/1e6:6.2f}')
            if s["del_anillo"] != s["anillo_total"]:
                fallos.append(f'  FALLA {m}/gif: sólo {s["del_anillo"]} de los '
                              f'{s["anillo_total"]} colores del anillo sobreviven')

        print(f'\n{"banda en svg animado":26} {"KB":>8} {"animaciones":>12} '
              f'{"valores":>9} {"seg":>6}')
        for m in modos:
            esperados += 1
            p = f"{DIR_MOV}/pulso-{m}--banda.svg"
            s = svg(m, E[m], H[m], R, p)
            hechos.append(p)
            print(f'  {m:24} {s["bytes"]/1024:8.0f} {s["animaciones"]:12} '
                  f'{s["valores"]:9} {s["dur"]:6.2f}')
            if s["bytes"] > 400 * 1024:
                fallos.append(f'  FALLA {m}/svg: {s["bytes"]//1024} KB, y por '
                              f'encima de 400 no vale para web')

        print()
        for m in modos:
            esperados += 1
            p = f"{DIR_PNG}/{m}--contacto.png"
            r = contacto(m, E[m], H[m], R, p)
            hechos.append(p)
            print(f'  contacto {m:14} {r["px"]:>10} {r["tomas"]} tomas '
                  f'{r["bytes"]/1024:8.0f} KB')
        esperados += 1
        pc = f"{DIR_PNG}/comparativa--modos.png"
        rc = comparativa(R, pc)
        hechos.append(pc)
        print(f'  comparativa {"":11} {rc["px"]:>10} {rc["modos"]} modos '
              f'{rc["bytes"]/1024:8.0f} KB')

    cierra(hechos, esperados, fallos)


def cierra(hechos, esperados, fallos):
    print(f"\nproducidos {len(hechos)} de {esperados} esperados")
    if len(hechos) != esperados:
        fallos.append(f"  FALLA el lote: {len(hechos)} salidas de {esperados}")
    print("el pico de cada barra ES su altura del anillo · bucle cerrado al "
          "fotograma · los 30 colores intactos")
    for f in fallos:
        print(f)
    print(f"\n{len(fallos)} fallos")
    sys.exit(1 if fallos else 0)


def shutil_which(x):
    import shutil
    return shutil.which(x)


if __name__ == "__main__":
    main()
