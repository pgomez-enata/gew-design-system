#!/usr/bin/env python3
"""
Encuadre de retratos · GEW · RD.

Con 48 aliados y sus ponentes, colocar cada foto a mano es donde se va el
tiempo y donde se pierde la consistencia: una cara grande al lado de una
pequeña se nota más que cualquier error de color.

**El criterio es propio y está escrito aquí**, no heredado:

  1. **La cabeza ocupa entre 1/3,5 y 1/3 del alto.** Es el rango que ya está
     cerrado para los flyers —«3 a 3,5 cabezas de alto»— y funciona porque deja
     sitio al nombre sin que la cara se pierda.
  2. **Los ojos van a 0,38 del alto**, contando desde arriba. La regla clásica
     de retrato es el tercio; 0,38 baja un poco la mirada y deja más aire
     abajo, que es donde va el nombre y el cargo.
  3. **La coronilla no se corta.** Antes de nada se comprueba que quepa el
     cráneo entero con un dedo de aire.
  4. **Sin cara detectada**, recorte centrado con el centro óptico a 0,42 del
     alto. No se inventa: el informe dice que no había cara.

Y todo se mide: cuántas cabezas de alto quedó, dónde cayeron los ojos, y si
hubo que rellenar por haberse salido del original.

El detector es Vision de macOS, compilado aquí (`herramientas-rostro.swift`).
No hace falta instalar nada.

Uso:
    python3 encuadre.py foto.jpg --ancho 1080 --alto 1350
    python3 encuadre.py --prueba
"""
import argparse, json, os, shutil, subprocess, sys

from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.abspath(__file__))
DETECTOR = f"{RAIZ}/_cache/rostro"
FUENTE_SWIFT = f"{RAIZ}/herramientas-rostro.swift"

CABEZAS_MIN, CABEZAS_MAX = 3.0, 3.5     # de alto
OJOS_EN = 0.38                          # altura de los ojos, desde arriba
SIN_CARA_CENTRO = 0.42                  # centro óptico cuando no hay cara
AIRE_CORONILLA = 0.22                   # del alto de la caja de la cara


def _compilar():
    if os.path.exists(DETECTOR):
        return True
    if not (shutil.which("swiftc") and os.path.exists(FUENTE_SWIFT)):
        return False
    os.makedirs(os.path.dirname(DETECTOR), exist_ok=True)
    r = subprocess.run(["swiftc", "-O", "-o", DETECTOR, FUENTE_SWIFT],
                       capture_output=True, text=True)
    return r.returncode == 0


def rostros(ruta):
    """Las caras de una imagen, con sus ojos. [] si no hay o no se puede."""
    if not _compilar():
        return None
    r = subprocess.run([DETECTOR, ruta], capture_output=True, text=True)
    for l in r.stdout.strip().split("\n"):
        if not l.strip():
            continue
        try:
            d = json.loads(l)
        except json.JSONDecodeError:
            continue
        if d.get("f", "").endswith(os.path.basename(ruta)):
            return d.get("caras", [])
    return []


def encuadrar(ruta, ancho, alto, cabezas=None):
    """Devuelve (imagen recortada, medidas). No estima: mide y lo dice."""
    im = Image.open(ruta).convert("RGB")
    W, H = im.size
    cs = rostros(ruta)
    med = {"origen": [W, H], "destino": [ancho, alto],
           "detector": "no disponible" if cs is None else "vision"}

    if cs:
        c = max(cs, key=lambda x: x["w"] * x["h"])
        cab_px = c["h"] * 1.42          # la caja de Vision no incluye el pelo
        objetivo = cabezas or (CABEZAS_MIN + CABEZAS_MAX) / 2
        escala = (alto / objetivo) / cab_px
        ojo_x = c["ojoX"] if c["ojoX"] is not None else c["x"] + c["w"] / 2
        ojo_y = c["ojoY"] if c["ojoY"] is not None else c["y"] + c["h"] * 0.42
        med.update(cara=[c["x"], c["y"], c["w"], c["h"]], confianza=c["conf"],
                   ojos=[ojo_x, ojo_y])
    else:
        escala = max(ancho / W, alto / H)
        ojo_x, ojo_y = W / 2, H * SIN_CARA_CENTRO
        med["cara"] = None

    # nunca se amplía por debajo de cubrir el destino: mejor cabeza pequeña
    # que un recorte con bordes vacíos
    escala = max(escala, ancho / W, alto / H)
    nW, nH = max(1, round(W * escala)), max(1, round(H * escala))
    im2 = im.resize((nW, nH), Image.LANCZOS)
    ox, oy = ojo_x * escala, ojo_y * escala

    x = round(ox - ancho / 2)
    y = round(oy - alto * OJOS_EN)
    # que no se salga
    x = max(0, min(x, nW - ancho))
    y = max(0, min(y, nH - alto))
    corte = im2.crop((x, y, x + ancho, y + alto))

    if cs:
        cab_final = c["h"] * 1.42 * escala
        med["cabezas_de_alto"] = round(alto / cab_final, 2)
        med["ojos_en"] = round((oy - y) / alto, 3)
        # ¿queda aire sobre la coronilla?
        top_cabeza = (c["y"] - c["h"] * AIRE_CORONILLA) * escala - y
        med["aire_coronilla_px"] = round(top_cabeza)
        med["corta_coronilla"] = top_cabeza < 0
        med["en_rango"] = CABEZAS_MIN <= med["cabezas_de_alto"] <= CABEZAS_MAX
    else:
        med.update(cabezas_de_alto=None, ojos_en=None, corta_coronilla=False,
                   en_rango=None, aire_coronilla_px=None)
    med["escala"] = round(escala, 4)
    return corte, med


def main():
    ap = argparse.ArgumentParser(description="Encuadre de retratos GEW · RD")
    ap.add_argument("foto", nargs="?")
    ap.add_argument("--ancho", type=int, default=1080)
    ap.add_argument("--alto", type=int, default=1350)
    ap.add_argument("--cabezas", type=float)
    ap.add_argument("--prueba", action="store_true",
                    help="corre sobre las fotos de ejemplo y sobre un retrato real")
    ap.add_argument("--salida")
    a = ap.parse_args()

    if a.prueba:
        import glob
        fotos = sorted(glob.glob(f"{RAIZ}/ejemplo/fotos/*.webp"))[:2]
        # una foto con cara de verdad para que la prueba signifique algo. Sale
        # de la variable, no de una ruta escrita: un repo no describe el disco
        # de nadie, y la puerta lo marcaba con razón.
        extra = os.environ.get("GEW_RETRATO_PRUEBA", "")
        if extra and os.path.exists(extra):
            fotos.append(extra)
        else:
            print("  (sin GEW_RETRATO_PRUEBA no hay ninguna foto con cara: "
                  "la prueba sólo comprueba el camino sin rostro)")
        if not fotos:
            sys.exit("no hay fotos con las que probar")
        print(f"{'foto':30} {'cara':>6} {'cabezas':>8} {'ojos en':>8} "
              f"{'coronilla':>10} {'en rango':>9}")
        malos = 0
        for f in fotos:
            _, m = encuadrar(f, a.ancho, a.alto, a.cabezas)
            hay = "sí" if m["cara"] else "no"
            cab = f"{m['cabezas_de_alto']:.2f}" if m["cabezas_de_alto"] else "—"
            ojo = f"{m['ojos_en']:.3f}" if m["ojos_en"] else "—"
            cor = ("corta" if m["corta_coronilla"] else
                   (f"{m['aire_coronilla_px']} px" if m["aire_coronilla_px"] is not None
                    else "—"))
            rango = ("sí" if m["en_rango"] else "NO") if m["en_rango"] is not None else "—"
            print(f"  {os.path.basename(f)[:28]:28} {hay:>6} {cab:>8} {ojo:>8} "
                  f"{cor:>10} {rango:>9}")
            if m["cara"] and (not m["en_rango"] or m["corta_coronilla"]):
                malos += 1
        print(f"\nregla: cabeza entre 1/{CABEZAS_MAX} y 1/{CABEZAS_MIN} del alto · "
              f"ojos a {OJOS_EN} · sin cara, centro a {SIN_CARA_CENTRO}")
        print(f"fotos con cara fuera de criterio: {malos}")
        sys.exit(1 if malos else 0)

    if not a.foto:
        sys.exit("dime qué foto encuadrar, o corre con --prueba")
    im, m = encuadrar(a.foto, a.ancho, a.alto, a.cabezas)
    salida = a.salida or f"{RAIZ}/_salida/encuadre/{os.path.splitext(os.path.basename(a.foto))[0]}--{a.ancho}x{a.alto}.png"
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    im.save(salida)
    for k, v in m.items():
        print(f"  {k:20} {v}")
    print(salida)
    sys.exit(0 if (m["cara"] is None or (m["en_rango"] and not m["corta_coronilla"]))
            else 1)


if __name__ == "__main__":
    main()
