#!/usr/bin/env python3
"""
Piezas de patrocinio · GEW · RD.

El hueco de patrocinadores ya está reservado en la banda de todas las piezas.
Esto es lo que se le entrega **al que firma**: el anuncio para redes, la placa
para su web y su firma, y el certificado de patrocinio.

⛔ **Ninguna marca se compone antes de que el acuerdo esté firmado.** El motor
lo exige: sin `--firmado` sale con el nombre en `{{PENDIENTE}}` y lo dice en el
informe. No es burocracia — poner un logo antes de tiempo ha costado disgustos.

Los tres niveles y lo que cada uno recibe salen de `contenido/patrocinio.json`,
que se edita sin tocar código.

Uso:
    python3 patrocinio.py --demo
    python3 patrocinio.py --nivel principal --marca "Nombre" --logo logo.png --firmado
"""
import argparse, json, os, sys

from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
from campana import (FORMATOS, TOK, activo, fuente, marca_alto, png_alto,  # noqa: E402
                     pulso, tinta)

C = TOK["campana"]
CARBON = TOK["color"]["campana2026"]["carbon"]["hex"]
NARANJA = TOK["color"]["campana2026"]["naranja"]["hex"]
BLANCO, GRIS = "#FFFFFF", "#B8BCC0"
PENDIENTE = "{{PENDIENTE}}"

# Los niveles salen de `contenido/patrocinio.json`, que se edita sin tocar
# código — el docstring lo prometía desde el 5-sep y el fichero no existía: los
# valores estaban aquí. Si el JSON falta, se cae a estos, para que un clon
# recién bajado arranque igual.
_POR_DEFECTO = {
    "principal":   {"rotulo": "PATROCINADOR PRINCIPAL", "escala": 1.00,
                    "piezas": ["anuncio", "placa", "certificado"]},
    "patrocinador": {"rotulo": "PATROCINADOR", "escala": 0.74,
                     "piezas": ["anuncio", "placa", "certificado"]},
    "colaborador": {"rotulo": "COLABORA", "escala": 0.52,
                    "piezas": ["placa", "certificado"]},
}
_JSON = f"{RAIZ}/contenido/patrocinio.json"
try:
    NIVELES = json.load(open(_JSON, encoding="utf-8"))["niveles"]
except (OSError, KeyError, ValueError):
    NIVELES = _POR_DEFECTO


def anuncio(nivel, marca, logo=None, fmt="retrato", firmado=False):
    """La pieza que se publica cuando se anuncia el patrocinio."""
    w, h = FORMATOS[fmt]["px"]
    U = w
    m = round(U * 0.0667)
    im = Image.new("RGB", (w, h), CARBON)
    d = ImageDraw.Draw(im)
    TOP, BOT = FORMATOS[fmt]["segura"] or (0, h)
    lock = png_alto(activo("logo/gew-rd-lockup-blanco.png"), round(U * 0.089))
    im.paste(lock, (m, TOP + m), lock)
    y = TOP + m + lock.height + round(U * 0.030)
    pulso(d, m, y, w - m * 2, round(U * 0.034))

    rot = NIVELES[nivel]["rotulo"]
    f_r = fuente("Bold", round(U * 0.026))
    y += round(U * 0.034) + round(U * 0.075)
    d.text((m, y), rot, font=f_r, fill=NARANJA)
    y += round(U * 0.026) + round(U * 0.030)

    nombre = marca if firmado else PENDIENTE
    cap = round(U * 0.085 * NIVELES[nivel]["escala"] + U * 0.030)
    while cap > 20:
        f_n = fuente("Bold", cap)
        if d.textlength(nombre, font=f_n) <= w - m * 2:
            break
        cap -= 3
    b = tinta(d, (m, y), nombre, f_n, fill=BLANCO)
    y = b[3] + round(U * 0.045)

    if logo and firmado and os.path.exists(logo):
        lg = marca_alto(logo, round(U * 0.11 * NIVELES[nivel]["escala"]),
                        blanco=True)
        im.paste(lg, (m, y), lg)
        y += lg.height + round(U * 0.030)

    f_t = fuente("Light", round(U * 0.030))
    for t in ("de la Semana Global de Emprendimiento",
              f"{C['fechas']} · República Dominicana"):
        b = tinta(d, (m, y), t, f_t, fill=GRIS)
        y = b[3] + round(U * 0.014)
    return im, {"pieza": "anuncio", "nivel": nivel, "formato": fmt,
                "firmado": firmado, "cap": cap,
                "nombre_visible": nombre, "derecha": b[2]}


def placa(nivel, marca, firmado=False, ancho=1200):
    """El PNG que el patrocinador pone en su web y en su firma."""
    alto = round(ancho * 0.34)
    im = Image.new("RGB", (ancho, alto), BLANCO)
    d = ImageDraw.Draw(im)
    m = round(ancho * 0.055)
    lock = png_alto(activo("logo/gew-rd-lockup-color.png"), round(alto * 0.40))
    im.paste(lock, (m, round(alto * 0.20)), lock)
    x = m + lock.width + round(ancho * 0.045)
    d.line([(x - round(ancho * 0.022), round(alto * 0.20)),
            (x - round(ancho * 0.022), round(alto * 0.78))],
           fill="#D5D5D5", width=2)
    # los dos textos tienen que caber en lo que queda a la derecha del logo:
    # «PATROCINADOR PRINCIPAL» con otra tipografía salía cortado por el borde
    util = ancho - x - round(ancho * 0.045)

    def cabe(txt, peso, cap):
        while cap > 8:
            f = fuente(peso, cap)
            if d.textlength(txt, font=f) <= util:
                return f
            cap -= 1
        return fuente(peso, 8)

    rot = NIVELES[nivel]["rotulo"]
    nom = marca if firmado else PENDIENTE
    f_r = cabe(rot, "Bold", round(alto * 0.115))
    d.text((x, round(alto * 0.24)), rot, font=f_r, fill=NARANJA)
    f_n = cabe(nom, "Light", round(alto * 0.135))
    d.text((x, round(alto * 0.46)), nom, font=f_n, fill="#3C4043")
    pulso(d, 0, alto - round(alto * 0.055), ancho, round(alto * 0.055))
    der = max(d.textlength(rot, font=f_r), d.textlength(nom, font=f_n)) + x
    return im, {"pieza": "placa", "nivel": nivel, "px": [ancho, alto],
                "firmado": firmado, "derecha": round(der),
                "desborda": max(0, round(der) - (ancho - round(ancho * 0.045)))}


def main():
    ap = argparse.ArgumentParser(description="Piezas de patrocinio GEW · RD")
    ap.add_argument("--nivel", choices=sorted(NIVELES))
    ap.add_argument("--marca", default="Marca de ejemplo")
    ap.add_argument("--logo")
    ap.add_argument("--firmado", action="store_true",
                    help="⛔ sólo con el acuerdo firmado: sin esto sale {{PENDIENTE}}")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--salida", default=f"{RAIZ}/_salida/patrocinio")
    a = ap.parse_args()
    if not a.nivel and not a.demo:
        a.demo = True

    os.makedirs(a.salida, exist_ok=True)
    niveles = sorted(NIVELES) if a.demo else [a.nivel]
    hechas, avisos = [], []
    print(f"{'pieza':26} {'nivel':14} {'firmado':>8} {'nombre visible':>16}")
    for nv in niveles:
        for pieza in NIVELES[nv]["piezas"]:
            if pieza == "anuncio":
                im, med = anuncio(nv, a.marca, a.logo, "retrato", a.firmado)
                p = f"{a.salida}/{nv}-anuncio--retrato.png"
            elif pieza == "placa":
                im, med = placa(nv, a.marca, a.firmado)
                p = f"{a.salida}/{nv}-placa.png"
            else:
                continue          # el certificado sale del motor de impresos
            im.save(p)
            hechas.append(p)
            print(f"  {pieza:24} {nv:14} {('sí' if a.firmado else 'NO'):>8} "
                  f"{med.get('nombre_visible', a.marca if a.firmado else PENDIENTE):>16}")
            if not a.firmado:
                avisos.append(f"  AVISO {nv}/{pieza}: sale con {PENDIENTE}. "
                              f"Ninguna marca se compone antes de firmar.")

    print(f"\nproducidas {len(hechas)} de "
          f"{sum(len([x for x in NIVELES[n]['piezas'] if x != 'certificado']) for n in niveles)} "
          f"esperadas")
    print("el certificado de patrocinio sale de impreso.py, que ya lo resuelve")
    for x in dict.fromkeys(avisos):
        print(x)
    for h in hechas:
        print(h)
    sys.exit(0)


if __name__ == "__main__":
    main()
