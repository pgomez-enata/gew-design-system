"""Zonas seguras y looks de color · fuente única · GEW · RD.

Hasta el 6-sep-2026 cada motor traía sus propios números y no coincidían:
`video.py` reservaba 60 px arriba en horizontal y `movimiento_video.py` 49 (el
4,5 % de respaldo); la skill de reels no leía ninguno y ponía el watermark en
y=69 sobre una zona que GEW declara intocable hasta y=269. Y había tres looks
de color sueltos, dos en `mezzanine.py` y uno inline en el SKILL.md de DTW.

Todo eso vive ahora en `tokens/video.json`. Este módulo sólo lo lee.

Fuera del taller —una skill instalada en otra máquina, un clon del repo— el
JSON puede no estar. Entonces se cae a `RESPALDO`, que son los mismos valores
escritos aquí: el motor sigue corriendo y `de_donde()` dice cuál se usó.

    from video_tokens import zona, look, ETIQUETADO
    z = zona("vertical")            # {'arriba':269,'abajo':250,...}
    g = look()                      # el por defecto
    g = look("calido")              # uno concreto

Ruta del JSON, por orden: $GEW_VIDEO_TOKENS · el de al lado · $GEW_DIR.
"""
import json, os

RESPALDO = {
    "zona_segura": {
        "vertical":     {"px": [1080, 1920], "arriba": 269, "abajo": 250, "izquierda": 0, "derecha": 250},
        "vertical-ads": {"px": [1080, 1920], "arriba": 269, "abajo": 672, "izquierda": 0, "derecha": 250},
        "horizontal":   {"px": [1920, 1080], "arriba": 60, "abajo": 120, "izquierda": 0, "derecha": 0},
        "cuadrado":     {"px": [1080, 1080], "arriba": 60, "abajo": 120, "izquierda": 0, "derecha": 0},
        "retrato":      {"px": [1080, 1350], "arriba": 60, "abajo": 140, "izquierda": 0, "derecha": 0},
        "yt-portada":   {"px": [2560, 1440], "arriba": 508, "abajo": 509, "izquierda": 507, "derecha": 507},
    },
    "audio": {
        "cama": {"ducking": False, "lufs_objetivo": -39.0,
                 "fade_in_s": 0.9, "fade_out_s": 1.2},
        "swell": {"activo": False, "empieza_antes_del_final_s": 3.6,
                  "sube_db": 6.0, "rampa_s": 2.0},
        "master": {"lufs": -14.0, "tp_dbfs": -1.5, "lra": 11},
    },
    "grade": {
        "por_defecto": "base",
        "etiquetado": {"args": ["-color_range", "tv", "-colorspace", "bt709",
                                "-color_primaries", "bt709", "-color_trc", "bt709"]},
        "looks": {
            "base":      {"eq": "eq=brightness=0.03:contrast=1.09:saturation=1.05:gamma=1.04",
                          "colorbalance": "colorbalance=rm=-0.05:gm=-0.02:bm=0.07:rs=-0.02:bs=0.05"},
            "frio":      {"eq": "eq=brightness=0.05:contrast=1.11:saturation=1.05:gamma=1.05",
                          "colorbalance": "colorbalance=rm=-0.08:gm=-0.03:bm=0.11:rs=-0.03:bs=0.07"},
            "calido":    {"eq": "eq=brightness=0.03:contrast=1.08:saturation=1.12:gamma=1.03",
                          "colorbalance": None},
        },
    },
}


def _candidatas():
    aqui = os.path.dirname(os.path.abspath(__file__))
    for r in (os.environ.get("GEW_VIDEO_TOKENS"),
              f"{aqui}/tokens/video.json",
              (os.environ.get("GEW_DIR") or "") + "/tokens/video.json"):
        if r and os.path.exists(r):
            yield r


def _carga():
    for r in _candidatas():
        try:
            return json.load(open(r, encoding="utf-8")), r
        except (OSError, ValueError):
            continue
    return RESPALDO, None


TOK, _RUTA = _carga()


def de_donde():
    """La ruta del JSON, o None si se está usando el respaldo escrito en el módulo."""
    return _RUTA


MARGENES = ("arriba", "abajo", "izquierda", "derecha")


def ficha(formato):
    """Todo lo que el JSON sabe del formato: márgenes, px, `oficial`, `fuente`, `uso`."""
    z = TOK["zona_segura"]
    if formato not in z:
        disponibles = [k for k in z if not k.startswith("_")]
        raise KeyError(f"formato de vídeo desconocido: {formato!r}. Hay: {disponibles}")
    return z[formato]


def zona(formato):
    """SÓLO los cuatro márgenes y el lienzo. Es lo que consume el código de dibujo;
    la procedencia se pide con `ficha()` y no se cuela en el dict de trabajo."""
    f = ficha(formato)
    d = {k: f[k] for k in MARGENES if k in f}
    d["px"] = f["px"]
    return d


def banda(formato):
    """(top, bottom) en píxeles absolutos — la forma en que lo piden `campana` y
    `movimiento_video`, que trabajan con la banda y no con los márgenes."""
    z = zona(formato)
    return z["arriba"], z["px"][1] - z["abajo"]


def look(nombre=None):
    """El look de color pedido, o el que esté por defecto. Devuelve la cadena de
    filtros lista para ffmpeg (eq + colorbalance si lo lleva)."""
    g = TOK["grade"]
    nombre = nombre or g["por_defecto"]
    if nombre not in g["looks"]:
        raise KeyError(f"look desconocido: {nombre!r}. Hay: {list(g['looks'])}")
    lk = g["looks"][nombre]
    partes = [lk["eq"]] + ([lk["colorbalance"]] if lk.get("colorbalance") else [])
    return ",".join(partes)


ETIQUETADO = TOK["grade"]["etiquetado"]["args"]


def audio(bloque=None):
    """Los parámetros de audio: `cama`, `swell` o `master`. Sin argumento, los tres.
    Las claves que empiezan por `_` son notas y no se devuelven."""
    a = TOK["audio"]
    d = a if bloque is None else a[bloque]
    return {k: v for k, v in d.items() if not k.startswith("_")}


def main():
    print(f"fuente: {de_donde() or 'respaldo del módulo (no se encontró el JSON)'}")
    print("\nzonas seguras")
    for f in TOK["zona_segura"]:
        if f.startswith("_"):
            continue
        z = zona(f)
        of = TOK["zona_segura"][f].get("oficial", {})
        marca = lambda k: "·oficial" if of.get(k) else ""
        print(f"  {f:<14} {z['px'][0]:>4}x{z['px'][1]:<5} "
              f"arriba {z['arriba']:>3}{marca('arriba'):<8} abajo {z['abajo']:>3}{marca('abajo'):<8} "
              f"der {z['derecha']:>3}{marca('derecha')}")
    print(f"\nlooks (por defecto: {TOK['grade']['por_defecto']})")
    for n in TOK["grade"]["looks"]:
        print(f"  {n:<10} {look(n)[:96]}")
    print(f"\netiquetado: {' '.join(ETIQUETADO)}")
    a = audio()
    print(f"\naudio · cama {'CON' if a['cama']['ducking'] else 'SIN'} ducking, "
          f"objetivo {a['cama']['lufs_objetivo']} LUFS · "
          f"swell {'activo' if a['swell']['activo'] else 'apagado'} · "
          f"master {a['master']['lufs']} LUFS / {a['master']['tp_dbfs']} dBTP")


if __name__ == "__main__":
    main()
