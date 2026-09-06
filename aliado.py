#!/usr/bin/env python3
"""
Piezas de los aliados · GEW · RD.

    somos     la pieza que publica el aliado: su logo + el sello
    sello     el sello para su web y su firma, con el HTML para pegar
    kit       una carpeta por aliado con todo lo suyo y el paso a paso

El padrón sale del muro publicado en enlata.do/gew — 48 aliados, 42 con logo y
6 en pastilla. No se teclea a mano: se lee del HTML, que es la fuente de verdad.

Uso:
    python3 aliado.py --listar
    python3 aliado.py --aliado "Organización"
    python3 aliado.py --kits            # los 48
"""
import argparse, html, json, os, re, sys
from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.abspath(__file__))
TOK = json.load(open(f"{RAIZ}/tokens/tokens.json", encoding="utf-8"))
sys.path.insert(0, RAIZ)
from campana import (fuente, marca_alto, png_alto, pin, pulso,  # noqa: E402
                     sello as sello_gew)

CARBON = TOK["color"]["campana2026"]["carbon"]["hex"]
NARANJA = TOK["color"]["campana2026"]["naranja"]["hex"]
BLANCO = "#FFFFFF"
TINTA = TOK["color"]["marca"]["carbon-wordmark"]["hex"]
GRIS = "#C6C6C6"

WEB = os.environ.get("GEW_PADRON", os.path.join(RAIZ, "_entrada", "muro"))

FORMATOS = {
    "retrato":  {"px": (1080, 1350), "unidad": 1080},
    "cuadrado": {"px": (1080, 1080), "unidad": 1010},
    "historia": {"px": (1080, 1920), "unidad": 1330, "segura": (269, 1670)},
}
R = dict(margen=0.0667, franja=0.0222, logo=0.0780, rotulo=0.0250,
         nombre=0.0560, marca=0.2000, lema=0.0215, sello=0.1050)


def padron():
    """Lee los 48 aliados del muro publicado. Devuelve [(nombre, ruta|None)]."""
    h = open(f"{WEB}/gew.html", encoding="utf-8", errors="replace").read()
    i0 = h.index('<ul class="muro"')
    b = h[i0:h.index("</ul>", i0)]
    out = []
    for li in re.findall(r"<li class=\"muro__[lp].*?</li>", b, re.S):
        alt = re.search(r'alt="([^"]+)"', li)
        src = re.search(r'src="([^"]+)"', li)
        if alt and src:
            out.append((html.unescape(alt.group(1)), f"{WEB}/{src.group(1)}"))
        else:
            txt = html.unescape(re.sub(r"<[^>]+>", "", li).strip())
            if txt:
                out.append((txt, None))
    return out


def hoja(fmt):
    w, h = FORMATOS[fmt]["px"]
    u = FORMATOS[fmt]["unidad"]
    return w, h, u, {k: round(v * u) for k, v in R.items()}


def ajustar(d, texto, cap, util, peso="Light"):
    while cap > 12:
        f = fuente(peso, cap)
        if d.textlength(texto, font=f) <= util:
            return f, cap
        cap -= 1
    return fuente(peso, cap), cap


def somos(nombre, logo=None, fmt="retrato", salida=None):
    """La pieza que publica el aliado."""
    w, h, U, g = hoja(fmt)
    m, fr = g["margen"], g["franja"]
    seg = FORMATOS[fmt].get("segura")
    TOP, BOT = seg if seg else (0, h)
    im = Image.new("RGB", (w, h), CARBON)
    d = ImageDraw.Draw(im)
    d.rectangle([0, (h - fr) if seg else (BOT - fr), w, h if seg else BOT], fill=NARANJA)
    med = {"aliado": nombre, "formato": fmt, "px": [w, h]}
    util = w - m * 2

    lock = png_alto(f"{RAIZ}/logo/gew-rd-lockup-blanco.png", g["logo"])
    im.paste(lock, (m, TOP + m), lock)
    y_p = TOP + m + lock.height + round(U * 0.028)
    a_p = round(U * 0.032)
    pulso(d, m, y_p, w - m * 2, a_p)

    suelo = (BOT if seg else BOT - fr) - round(U * 0.055)
    y_lema = suelo - g["lema"]

    # el rótulo y el nombre del aliado
    f_rot = fuente("Bold", g["rotulo"])
    techo = TOP + m + g["logo"] + round(U * 0.085)
    bb = d.textbbox((0, 0), "SOMOS ALIADOS DE", font=f_rot)
    d.text((m - bb[0], techo - bb[1]), "SOMOS ALIADOS DE", font=f_rot, fill=NARANJA)
    y = techo + g["rotulo"] + round(U * 0.030)
    f_n, cap_n = ajustar(d, "la Semana Global de Emprendimiento", g["nombre"], util)
    bb = d.textbbox((0, 0), "la Semana Global de Emprendimiento", font=f_n)
    d.text((m - bb[0], y - bb[1]), "la Semana Global de Emprendimiento",
           font=f_n, fill=BLANCO)
    y += cap_n + round(U * 0.020)
    f_f = fuente("Light", round(cap_n * 0.62))
    bb = d.textbbox((0, 0), TOK["campana"]["fechas"], font=f_f)
    d.text((m - bb[0], y - bb[1]), TOK["campana"]["fechas"], font=f_f, fill=GRIS)
    y += round(cap_n * 0.62) + round(U * 0.070)

    # la marca del aliado, en una tarjeta blanca
    caja_h = g["marca"]
    caja_y = y + max(0, round((y_lema - round(U * 0.075) - g["sello"] - y - caja_h) * 0.44))
    d.rectangle([m, caja_y, w - m, caja_y + caja_h], fill=BLANCO)
    if logo and os.path.exists(logo):
        lg = Image.open(logo).convert("RGBA")
        esc = min((util - round(U * 0.090)) / lg.width,
                  (caja_h - round(U * 0.048)) / lg.height)
        lg = lg.resize((max(1, round(lg.width * esc)), max(1, round(lg.height * esc))),
                       Image.LANCZOS)
        im.paste(lg, (m + (util - lg.width) // 2,
                      caja_y + (caja_h - lg.height) // 2), lg)
        med["logo_px"] = [lg.width, lg.height]
    else:
        f_p, cap_p = ajustar(d, nombre, round(caja_h * 0.30), util - round(U * 0.090), "Bold")
        bb = d.textbbox((0, 0), nombre, font=f_p)
        d.text((m + (util - (bb[2] - bb[0])) // 2 - bb[0],
                caja_y + (caja_h - cap_p) // 2 - bb[1]), nombre, font=f_p, fill=TINTA)
        med["logo_px"] = None
    med["holgura"] = y_lema - round(U * 0.060) - (caja_y + caja_h)

    # el sello y el lema
    _, clase = sello_gew(im, d, m, y_lema - round(U * 0.075) - g["sello"],
                         g["sello"], U, oscuro=True)
    med["sello"] = clase
    f_l = fuente("Light", g["lema"])
    r = round(g["lema"] * 0.52)
    pin(d, m + r, y_lema + round(g["lema"] * 0.32), r, TOK["color"]["barra"]["hex"][0])
    d.text((m + r * 3.1, y_lema), TOK["campana"]["tema_es"], font=f_l, fill=BLANCO)
    bb = d.textbbox((0, 0), TOK["campana"]["sitio"], font=f_l)
    d.text((w - m - (bb[2] - bb[0]) - bb[0], y_lema), TOK["campana"]["sitio"],
           font=f_l, fill=BLANCO)

    if salida:
        os.makedirs(os.path.dirname(salida), exist_ok=True)
        im.save(salida)
    return im, med


def sello_web(salida=None, alto=120):
    """El sello para pegar en una web o una firma, con su HTML."""
    lock = png_alto(f"{RAIZ}/logo/gew-rd-lockup-color.png", round(alto * 0.66))
    f = fuente("Bold", max(9, round(alto * 0.13)))
    tmp = Image.new("RGBA", (10, 10))
    d0 = ImageDraw.Draw(tmp)
    txt = "ALIADO OFICIAL"
    bb = d0.textbbox((0, 0), txt, font=f)
    w = max(lock.width, bb[2] - bb[0]) + round(alto * 0.30)
    im = Image.new("RGBA", (w, alto), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    im.paste(lock, ((w - lock.width) // 2, round(alto * 0.10)), lock)
    d.text(((w - (bb[2] - bb[0])) // 2 - bb[0], round(alto * 0.78) - bb[1]),
           txt, font=f, fill=TINTA)
    if salida:
        os.makedirs(os.path.dirname(salida), exist_ok=True)
        im.save(salida)
    return im, {"px": [w, alto]}


HTML_SELLO = """<!-- Sello de aliado · Semana Global de Emprendimiento RD -->
<a href="https://enlata.do/gew" target="_blank" rel="noopener"
   style="display:inline-block;line-height:0">
  <img src="sello-aliado-gew-rd.png" alt="Aliado oficial · Semana Global de
Emprendimiento República Dominicana · 16-22 de noviembre" style="height:60px;
width:auto">
</a>"""

LEEME = """# Tu material · Semana Global de Emprendimiento · RD

Hola, {nombre}.

Aquí está todo lo que necesitas para contar que eres aliado de la Semana Global
de Emprendimiento en República Dominicana, del **16 al 22 de noviembre**.

## Qué hay en esta carpeta

| Archivo | Para qué |
|---|---|
| `somos-aliados--retrato.png` | Para publicar en Instagram y LinkedIn (1080×1350) |
| `somos-aliados--cuadrado.png` | Para Facebook, LinkedIn y WhatsApp (1080×1080) |
| `somos-aliados--historia.png` | Para historias de Instagram y estados (1080×1920) |
| `sello-aliado-gew-rd.png` | Para tu web y tu firma de correo |
| `sello-para-tu-web.html` | El código, ya escrito, para pegar en tu sitio |

## Cómo publicar la pieza

1. Abre el archivo que corresponda a donde vas a publicar.
2. Súbelo como cualquier otra foto.
3. En el texto, menciona que es parte de la Semana Global de Emprendimiento.
   Te dejamos abajo una frase lista.
4. Usa las etiquetas **#GEW2026** y **#EntrepreneursThriveHere**.

## Cómo poner el sello en tu web

1. Descarga `sello-aliado-gew-rd.png` a tu computadora.
2. Súbelo a tu sitio como subes cualquier imagen.
3. Abre `sello-para-tu-web.html`, copia todo lo que hay dentro y pégalo donde
   quieras que aparezca el sello.
4. Si tu sitio lo hizo otra persona, mándale los dos archivos y este paso: lo
   entenderá enseguida.

## Cómo ponerlo en tu firma de correo

1. En Gmail: rueda dentada arriba a la derecha → **Ver todos los ajustes**.
2. Baja hasta **Firma** y haz clic en la tuya.
3. Pulsa el icono de imagen (una montañita) y sube `sello-aliado-gew-rd.png`.
4. Haz clic en la imagen ya insertada y elige **Pequeño**.
5. Baja del todo y pulsa **Guardar cambios**.

## Una frase que puedes copiar

> Somos aliados de la Semana Global de Emprendimiento 2026 en República
> Dominicana, del 16 al 22 de noviembre. Una semana en la que cientos de
> organizaciones abrimos las puertas para que más gente descubra que emprender
> también es para ella. Todo el programa en gew.co. #GEW2026
> #EntrepreneursThriveHere

## Lo que no se puede hacer con el logo

La red global que organiza la Semana no acepta ninguna variación de su marca:

- No lo recolorees ni le cambies el fondo.
- No lo recortes ni uses solo una parte.
- No lo estires: si lo redimensionas, mantén la proporción.
- No lo pongas encima de una foto donde no se lea.

Si necesitas una versión distinta, escríbenos antes en vez de modificarlo.

---

Cualquier duda: **{correo}** · Todo el programa en **gew.co**
"""


def kit(nombre, logo, destino):
    """Genera la carpeta de un aliado. Devuelve los ficheros creados."""
    slug = re.sub(r"[^a-z0-9]+", "-", nombre.lower()).strip("-")[:48]
    car = f"{destino}/{slug}"
    os.makedirs(car, exist_ok=True)
    hechos, medidas = [], []
    for fmt in FORMATOS:
        r = f"{car}/somos-aliados--{fmt}.png"
        _, mm = somos(nombre, logo, fmt, r)
        hechos.append(r); medidas.append(mm)
    r = f"{car}/sello-aliado-gew-rd.png"
    sello_web(r); hechos.append(r)
    with open(f"{car}/sello-para-tu-web.html", "w", encoding="utf-8") as f:
        f.write(HTML_SELLO)
    hechos.append(f"{car}/sello-para-tu-web.html")
    with open(f"{car}/LEEME.md", "w", encoding="utf-8") as f:
        f.write(LEEME.format(nombre=nombre, correo=TOK["contacto"]["correo"]
                             if "contacto" in TOK else "{{CORREO}}"))
    hechos.append(f"{car}/LEEME.md")
    return hechos, medidas


def main():
    ap = argparse.ArgumentParser(description="Piezas de aliado GEW · RD")
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--aliado")
    ap.add_argument("--kits", action="store_true")
    ap.add_argument("--salida", default=f"{RAIZ}/_salida/aliados")
    a = ap.parse_args()

    p = padron()
    if a.listar:
        print(f"{len(p)} aliados · {sum(1 for _, l in p if l)} con logo, "
              f"{sum(1 for _, l in p if not l)} sin logo")
        for n, l in p:
            print(f"  {'L' if l else 'P'}  {n}")
        return

    if a.kits:
        hechos, malas = [], []
        for n, l in p:
            fs, ms = kit(n, l, a.salida)
            hechos += fs
            malas += [(n, m["holgura"]) for m in ms if m["holgura"] < 0]
        esperados = len(p) * 6
        print(f"producidos {len(hechos)} de {esperados} esperados · {len(p)} kits")
        for n, hh in malas[:6]:
            print(f"  HOLGURA NEGATIVA {hh} px — {n}")
        if len(hechos) != esperados or malas:
            sys.exit("la corrida no cuadra")
        return

    if a.aliado:
        m = [(n, l) for n, l in p if a.aliado.lower() in n.lower()]
        if not m:
            sys.exit(f"no encuentro «{a.aliado}» en el padrón")
        n, l = m[0]
        fs, ms = kit(n, l, a.salida)
        print(json.dumps(ms[0], ensure_ascii=False))
        for f in fs:
            print(f)
        return
    ap.error("hace falta --listar, --aliado o --kits")


if __name__ == "__main__":
    main()
