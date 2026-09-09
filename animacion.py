#!/usr/bin/env python3
"""
Curvas, entradas y salidas · GEW · RD.

El vocabulario de movimiento del sistema, en un solo sitio. Antes vivía repartido
por dentro de cada motor: **una** curva y **nueve** entradas escritas a mano, cada
una con su fracción de segundo suelta. Y **cero salidas** — medido sobre los siete
MP4, al último fotograma les quedaba entre el 91,6 % y el 98,7 % de la tinta que
había a mitad de pieza. Todas entraban bien y se cortaban en seco.

Dos ideas sostienen este módulo:

**1 · Las duraciones se piden en TIEMPOS MUSICALES, no en segundos.** Una entrada
dura una corchea o un tiempo, no «0,45 s». Así el movimiento y el pulso van juntos
por construcción y no por casualidad, y cambiar el BPM no descuadra nada.

**2 · Una pieza declara cómo entra y cómo sale**, y el motor deriva los valores.
`mantiene` es una salida legítima —un endcard que va al final del todo debe
quedarse— pero tiene que **pedirse a propósito**, no ser lo único posible.

Uso desde un motor:

    A = animacion.Reloj(dur=5.0, bpm=100, fps=30)
    a = A.entra("sube", ini="0", dur="1t")        # entra sobre el primer tiempo
    b = A.sale("apaga", dur="1c")                 # se apaga en la última corchea
    opacidad = a * b
"""
import math

# ── unidades musicales ─────────────────────────────────────────────────
# `t` tiempo · `c` corchea (medio tiempo) · `s` semicorchea · `C` compás
UNIDAD = {"t": 1.0, "c": 0.5, "s": 0.25, "C": 4.0}


def en_tiempos(x):
    """«1t», «2c», «0.5C» o un número (que ya son tiempos)."""
    if isinstance(x, (int, float)):
        return float(x)
    x = str(x).strip()
    if x[-1] in UNIDAD:
        return float(x[:-1] or 1) * UNIDAD[x[-1]]
    return float(x)


# ── las curvas ─────────────────────────────────────────────────────────
# Todas van de 0 a 1 y devuelven de 0 a 1. La que había en el sistema era
# `frena`, que aquí conserva su fórmula exacta para no mover lo ya aprobado.
def frena(u):
    """Cúbica que desacelera. Para lo que tiene peso: un lockup, una cifra."""
    return 1 - (1 - u) ** 3


def arranca(u):
    """Acelera al empezar. Para salidas: lo que se va, se va rápido."""
    return u ** 3


def frena_y_arranca(u):
    """Suave en los dos extremos. Para desplazamientos largos."""
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


def golpe(u):
    """Llega, se pasa un poco y vuelve. Para acentos sobre el tiempo fuerte.
    Se pasa un 10 % del recorrido: más que eso deja de leerse como acento y
    empieza a leerse como un rebote de dibujo animado."""
    c = 1.70158
    return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2


def escalon(u):
    """Sin interpolación: salta a la mitad. Para lo que debe sentirse duro."""
    return 0.0 if u < 0.5 else 1.0


CURVAS = {"frena": frena, "arranca": arranca,
          "frena-y-arranca": frena_y_arranca, "golpe": golpe,
          "escalon": escalon}

# ── entradas y salidas ─────────────────────────────────────────────────
# Cada una dice qué curva usa por defecto y qué transforma. El motor recibe un
# número de 0 a 1 y decide qué hacer con él: opacidad, desplazamiento, escala.
ENTRADAS = {
    "aparece": {"curva": "frena", "que": "opacidad"},
    "sube":    {"curva": "frena", "que": "opacidad+desplazamiento"},
    "barre":   {"curva": "frena", "que": "cuántas barras se ven"},
    "crece":   {"curva": "frena", "que": "opacidad+escala"},
    "abre":    {"curva": "frena-y-arranca", "que": "una banda se retira"},
    "escribe": {"curva": "escalon", "que": "palabras que se ven"},
}
SALIDAS = {
    "apaga":    {"curva": "arranca", "que": "opacidad"},
    "baja":     {"curva": "arranca", "que": "opacidad+desplazamiento"},
    "cierra":   {"curva": "frena", "que": "el pulso crece hasta tapar"},
    "encoge":   {"curva": "arranca", "que": "opacidad+escala"},
    "mantiene": {"curva": None, "que": "nada: se queda"},
}


# ── ritmo del texto ────────────────────────────────────────────────────
# TikTok publica «display 5-10 words per second» para el texto sobreimpreso, y
# lo respalda con su propia investigación (TikTok Marketing Science con Lumen
# Research, 2021: +2,1x awareness lift). Es la única cifra de cadencia de texto
# que alguna plataforma publica con fuente nombrada.
#
# La rejilla ya la cumple sin forzar nada: a 100 BPM una semicorchea son 0,15 s,
# así que **una palabra por semicorchea = 6,67 palabras/s**, justo en medio del
# rango. Una por corchea son 3,33 — por debajo. Una por semicorchea es la
# cadencia por defecto y no es una elección estética: es la que cae dentro.
RITMO_MIN, RITMO_MAX = 5.0, 10.0
CADENCIA = "s"          # una palabra por semicorchea


def ritmo(palabras, segundos):
    """Palabras por segundo. Sin redondear: el umbral se comprueba con esto."""
    return palabras / segundos if segundos > 0 else 0.0


def ritmo_ok(palabras, segundos):
    return RITMO_MIN <= ritmo(palabras, segundos) <= RITMO_MAX


# La otra mitad, y no es la misma cosa. Lo de arriba es la cadencia a la que se
# PRESENTA un texto que entra palabra a palabra. Esto es cuánto tiene que estar
# en pantalla un texto que aparece y se queda, para que dé tiempo a leerlo.
#
# Aquí la fuente es otra: **BBC Subtitle Guidelines** (160–180 palabras/min,
# ~15 caracteres por segundo) y la guía de Netflix (17 cps). Se toma la más
# conservadora de las dos —15— porque un rótulo de campaña se lee de pasada y
# compitiendo con el resto de la pieza, no como un subtítulo al que se atiende.
CPS_LECTURA = 15.0
MINIMO_EN_PANTALLA = 0.8       # ningún rótulo por debajo, por corto que sea


def tiempo_de_lectura(texto, cps=CPS_LECTURA):
    """Cuántos segundos necesita este texto en pantalla para poder leerse."""
    return max(MINIMO_EN_PANTALLA, len(str(texto).strip()) / cps)


def se_lee(texto, segundos_en_pantalla, cps=CPS_LECTURA):
    return segundos_en_pantalla + 1e-9 >= tiempo_de_lectura(texto, cps)


class Reloj:
    """El reloj de una pieza. Traduce tiempos musicales a segundos y responde
    cuánto vale una entrada o una salida en el instante `t`."""

    def __init__(self, dur, bpm=100, fps=30):
        self.dur, self.bpm, self.fps = float(dur), float(bpm), int(fps)
        self.seg_por_tiempo = 60.0 / self.bpm
        fr = fps * 60 / bpm
        if abs(fr - round(fr)) > 1e-9:
            raise SystemExit(
                f"{bpm:g} BPM no cae en fotogramas enteros a {fps} fps. "
                f"El válido más cercano es {fps*60/max(1, round(fr)):g}.")
        self.fr_por_tiempo = round(fr)
        # ⚠️ El último fotograma de una pieza NO cae en `dur`, cae en
        # `dur - 1/fps`. Si la salida se calcula contra `dur`, en el último
        # fotograma todavía vale ~0,16 y la pieza acaba con un 15 % de imagen
        # encima: parece que sale y no termina de salir. Medido: quedaba el
        # 77 % de la tinta con una salida ya puesta.
        self.ultimo = self.dur - 1.0 / self.fps

    def seg(self, x):
        """Unidades musicales → segundos."""
        return en_tiempos(x) * self.seg_por_tiempo

    def tiempos_de_la_pieza(self):
        return self.dur / self.seg_por_tiempo

    def cae_en_tiempo(self):
        n = self.tiempos_de_la_pieza()
        return abs(n - round(n)) < 1e-9

    def _tramo(self, t, ini, dur, curva):
        d = max(1e-9, self.seg(dur))
        u = (t - self.seg(ini)) / d
        return CURVAS[curva](min(1.0, max(0.0, u)))

    def entra(self, nombre, ini=0, dur="1t", curva=None):
        """0 antes de empezar, 1 cuando ha terminado de entrar."""
        if nombre not in ENTRADAS:
            raise SystemExit(f"entrada desconocida: {nombre}. "
                             f"Hay: {', '.join(sorted(ENTRADAS))}")
        return lambda t: self._tramo(t, ini, dur,
                                     curva or ENTRADAS[nombre]["curva"])

    def escribe(self, texto, ini=0, cadencia=CADENCIA):
        """Cuántas palabras se ven en el instante `t`, una por unidad de
        `cadencia`. Devuelve (función, palabras, segundos, palabras/s)."""
        pal = [p for p in str(texto).split() if p]
        paso = self.seg(cadencia)
        dur_txt = paso * len(pal)
        t0 = self.seg(ini)

        def cuantas(t):
            if t < t0:
                return 0
            return min(len(pal), int((t - t0) / paso) + 1)
        return cuantas, len(pal), dur_txt, ritmo(len(pal), dur_txt)

    def sale(self, nombre, dur="2c", curva=None):
        """1 mientras la pieza vive, 0 al acabar. `mantiene` devuelve 1 siempre
        — es una salida legítima, pero hay que pedirla."""
        if nombre not in SALIDAS:
            raise SystemExit(f"salida desconocida: {nombre}. "
                             f"Hay: {', '.join(sorted(SALIDAS))}")
        if nombre == "mantiene":
            return lambda t: 1.0
        d = max(1e-9, self.seg(dur))
        ini = self.ultimo - d          # termina EN el último fotograma, no después
        c = curva or SALIDAS[nombre]["curva"]
        return lambda t: 1.0 - self._tramo(t, ini / self.seg_por_tiempo,
                                           dur, c)
