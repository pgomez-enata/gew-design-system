#!/usr/bin/env python3
"""
Comprueba la máquina ANTES de empezar · GEW · RD.

El 5-sep-2026 descubrí midiendo, no antes de empezar, que en esta máquina no
estaban exiftool, ImageMagick, Ghostscript, qpdf, scikit-image ni jsonschema —
y que sí estaban reportlab, tificc, pdffonts y rsvg-convert. Eso lo tiene que
decir un comando en dos segundos, no un rato de investigación.

Distingue tres cosas:
    OBLIGATORIO   sin esto el sistema no corre. Falta uno → sale con código 1.
    OPCIONAL      sin esto se pierde una capacidad concreta, que se nombra.
    ACTIVO        un fichero que el código referencia y que tiene que existir.

Uso:
    python3 entorno.py
    python3 entorno.py --instalar     enseña los comandos de lo que falta
"""
import argparse, importlib, json, os, shutil, subprocess, sys

RAIZ = os.path.dirname(os.path.abspath(__file__))

PY_MIN = (3, 9)

MODULOS = [
    # (import, obligatorio, para qué, cómo se instala)
    ("PIL", True, "componer todas las piezas", "pip3 install Pillow"),
    ("numpy", True, "medir tinta y contraste en la auditoría", "pip3 install numpy"),
    ("fontTools", False, "leer las tablas de la tipografía (cap-height, glifos)",
     "pip3 install fonttools"),
    ("reportlab", False, "PDF de la revista con texto vivo en vez de 32 imágenes",
     "pip3 install reportlab"),
    ("skimage", False, "comparar contra imágenes de referencia (regresión visual)",
     "pip3 install scikit-image"),
    ("jsonschema", False, "validar las entradas de un motor antes de renderizar",
     "pip3 install jsonschema"),
]

BINARIOS = [
    # (comando, obligatorio, para qué, cómo se instala)
    ("rsvg-convert", True, "rasterizar los SVG de los logos", "brew install librsvg"),
    ("pdffonts", False, "comprobar si un PDF lleva texto vivo o son imágenes",
     "brew install poppler"),
    ("tificc", False, "marcar colores fuera del gamut CMYK", "brew install little-cms2"),
    ("exiftool", False, "escribir metadatos IPTC en JPEG (en PNG no hace falta)",
     "brew install exiftool"),
    ("gs", False, "producir PDF/X-1 o X-3 para la imprenta", "brew install ghostscript"),
    ("magick", False, "comparación perceptual y conversión con perfil ICC",
     "brew install imagemagick"),
]

ACTIVOS = [
    ("tokens/tokens.json", True, "la fuente de verdad del sistema"),
    ("fuentes/VAGRoundedStdThin.ttf", True, "el peso del logo"),
    ("fuentes/VAGRoundedStdLight.ttf", True, "cuerpo de texto"),
    ("fuentes/VAGRoundedStdBold.ttf", True, "titulares"),
    ("fuentes/VAGRoundedStdBlack.ttf", True, "cifras grandes"),
    ("logo/gew-rd-lockup-color.png", True, "el logo que manda: el dominicano"),
    ("logo/gew-rd-lockup-blanco.png", True, "el mismo, para fondos oscuros"),
    ("logo/gew-rd-anillo.png", True, "el anillo, cuando el lockup no se lee"),
    ("logo/socios/enlata-wordmark.svg", True, "marca del anfitrión nacional"),
    ("logo/socios/iavanza-lockup.svg", True, "marca del partner"),
    ("datos/rd-provincias.geojson", False, "el mapa de las 32 provincias de la revista"),
]

VERDE, ROJO, GRIS = "  OK  ", " FALTA", "  --  "


def _version_modulo(m):
    for at in ("__version__", "version", "VERSION", "Version"):
        v = getattr(m, at, None)
        if isinstance(v, str):
            return v
    return "?"


def revisar():
    """Devuelve (filas, faltan_obligatorios, comandos_de_instalacion)."""
    filas, faltan, cmds = [], [], []

    ok_py = sys.version_info[:2] >= PY_MIN
    filas.append(("python", ok_py, True, ".".join(map(str, sys.version_info[:3])),
                  f"mínimo {PY_MIN[0]}.{PY_MIN[1]}"))
    if not ok_py:
        faltan.append("python")

    for nombre, obl, para, cmd in MODULOS:
        try:
            m = importlib.import_module(nombre)
            filas.append((nombre, True, obl, _version_modulo(m), para))
        except Exception:
            filas.append((nombre, False, obl, "—", para))
            (faltan.append(nombre) if obl else None)
            cmds.append((nombre, cmd, obl))

    for nombre, obl, para, cmd in BINARIOS:
        ruta = shutil.which(nombre)
        v = "—"
        if ruta:
            try:
                v = (subprocess.run([nombre, "--version"], capture_output=True,
                                    text=True, timeout=6).stdout or "").strip()
                v = v.split("\n")[0][:28] or "sí"
            except Exception:
                v = "sí"
        filas.append((nombre, bool(ruta), obl, v, para))
        if not ruta:
            (faltan.append(nombre) if obl else None)
            cmds.append((nombre, cmd, obl))

    # Los hashes de ACTIVOS.md no son decoración: se verifican. Un activo que
    # existe pero ya no es el mismo es peor que uno que falta, porque no avisa.
    sellos = {}
    act = f"{RAIZ}/ACTIVOS.md"
    if os.path.exists(act):
        import re as _re
        for m in _re.finditer(r"\| `([^`]+)` \| ([\d,]+) \| `([0-9a-f]{16})` \|",
                              open(act, encoding="utf-8").read()):
            sellos[m.group(1)] = (int(m.group(2).replace(",", "")), m.group(3))

    def _sha(ruta):
        import hashlib
        h = hashlib.sha256()
        with open(ruta, "rb") as f:
            for t in iter(lambda: f.read(1 << 20), b""):
                h.update(t)
        return h.hexdigest()[:16]

    cambiados = []
    for rel, (n_esp, h_esp) in sellos.items():
        p_ = f"{RAIZ}/{rel}"
        if os.path.exists(p_) and (os.path.getsize(p_) != n_esp or _sha(p_) != h_esp):
            cambiados.append(rel)
    filas.append(("ACTIVOS.md · hashes", not cambiados, False,
                  f"{len(sellos) - len(cambiados)}/{len(sellos)}",
                  "los activos son los que declara ACTIVOS.md"
                  + (f" — CAMBIÓ: {', '.join(cambiados[:3])}" if cambiados else "")))

    from campana import activo, EJEMPLO      # noqa: E402
    de_ejemplo = 0
    for rel, obl, para in ACTIVOS:
        p = f"{RAIZ}/{rel}"
        real = activo(rel)
        hay = os.path.exists(real)
        es_ej = hay and real.startswith(EJEMPLO)
        de_ejemplo += 1 if es_ej else 0
        tam = f"{os.path.getsize(real)/1024:.0f} KB" if hay else "—"
        filas.append((rel, hay, obl,
                      tam + ("  ← ejemplo" if es_ej else ""), para))
        if not hay and obl:
            faltan.append(rel)
    if de_ejemplo:
        filas.append(("activos propios", True, False,
                      f"{len(ACTIVOS) - de_ejemplo}/{len(ACTIVOS)}",
                      f"los otros {de_ejemplo} salen de ejemplo/ — el sistema "
                      f"corre, pero con marca de marcador"))
    return filas, faltan, cmds


def main():
    ap = argparse.ArgumentParser(description="Comprueba la máquina")
    ap.add_argument("--instalar", action="store_true",
                    help="enseña los comandos de lo que falta")
    a = ap.parse_args()

    filas, faltan, cmds = revisar()
    print(f"gew_design_system · entorno · {RAIZ}")
    tok = f"{RAIZ}/tokens/tokens.json"
    if os.path.exists(tok):
        print("tokens v" + json.load(open(tok, encoding="utf-8"))["meta"]["version"])
    print()
    for nombre, hay, obl, v, para in filas:
        marca = VERDE if hay else (ROJO if obl else GRIS)
        etq = "" if hay else ("  ← OBLIGATORIO" if obl else "")
        print(f"{marca}  {nombre:34} {v:30} {para}{etq}")

    print()
    n_ok = sum(1 for f in filas if f[1])
    print(f"{n_ok} de {len(filas)} presentes · "
          f"{len([f for f in filas if not f[1] and f[2]])} obligatorios faltan · "
          f"{len([f for f in filas if not f[1] and not f[2]])} opcionales faltan")

    if cmds and (a.instalar or faltan):
        print("\npara instalar lo que falta:")
        for nombre, cmd, obl in cmds:
            print(f"  {'!' if obl else ' '} {cmd:38} # {nombre}")

    if faltan:
        sys.exit(f"\nfaltan {len(faltan)} obligatorios: {', '.join(faltan)}")
    print("\nla máquina tiene todo lo obligatorio")


if __name__ == "__main__":
    main()
