#!/usr/bin/env python3
"""
Correos de la campaña · GEW · RD.

El aliado se entera por correo, no por Instagram. Cuatro correos: invitación a
sumarse, confirmación con lo que tiene que mandar, recordatorio y cierre.

Tres cosas mandan aquí, y las tres se comprueban en la salida:

  · **Gmail recorta el mensaje a partir de 102 KB** de HTML y CSS. No cuenta el
    peso de las imágenes. *(Cifra no confirmada por Google, pero citada por
    Litmus y Mailchimp desde 2018.)* El motor mide y avisa.
  · **El Outlook clásico ignora flexbox y grid**: usa el motor de Word.
    Microsoft lo retira en octubre de 2026, pero el parque instalado sigue
    hasta 2028-29. Aquí se maqueta con `<table>`, que es lo que entiende.
  · **Ancho 600 px**, que es convención de la industria, no norma.

Las imágenes NO se incrustan: van enlazadas. Un correo con el logo en base64
engorda el HTML y es justo lo que dispara el recorte.

Uso:
    python3 correo.py --todos
    python3 correo.py --tipo invitacion --texto-plano
"""
import argparse, html, json, os, re, sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
TOK = json.load(open(f"{RAIZ}/tokens/tokens.json", encoding="utf-8"))
C = TOK["campana"]
COL = TOK["color"]["campana2026"]
CARBON, NARANJA = COL["carbon"]["hex"], COL["naranja"]["hex"]
ANCHO = 600
TOPE_GMAIL = 102 * 1024
# El sello vive en la web, no dentro del correo. Cambiar por la URL real.
SELLO = "{{URL_DEL_SELLO}}"
DESTINO_POR_DEFECTO = f"{RAIZ}/_salida/correo"


def _p(txt, tam=16, color="#3C4043", peso="normal", alto=1.55):
    return (f'<p style="margin:0 0 16px;font-family:Helvetica,Arial,sans-serif;'
            f'font-size:{tam}px;line-height:{alto};color:{color};'
            f'font-weight:{peso}">{txt}</p>')


def _boton(texto, url):
    """Un botón que es una tabla: los <a> con padding se rompen en Outlook."""
    return (f'<table role="presentation" cellpadding="0" cellspacing="0" '
            f'border="0" style="margin:8px 0 24px"><tr>'
            f'<td bgcolor="{NARANJA}" style="border-radius:6px">'
            f'<a href="{url}" style="display:inline-block;padding:14px 28px;'
            f'font-family:Helvetica,Arial,sans-serif;font-size:16px;'
            f'font-weight:bold;color:#FFFFFF;text-decoration:none">{texto}</a>'
            f'</td></tr></table>')


def _lista(puntos):
    filas = "".join(
        f'<tr><td width="18" valign="top" style="font-family:Helvetica,Arial,'
        f'sans-serif;font-size:16px;line-height:1.55;color:{NARANJA}">·</td>'
        f'<td style="font-family:Helvetica,Arial,sans-serif;font-size:16px;'
        f'line-height:1.55;color:#3C4043;padding-bottom:8px">{p}</td></tr>'
        for p in puntos)
    return (f'<table role="presentation" cellpadding="0" cellspacing="0" '
            f'border="0" width="100%" style="margin:0 0 18px">{filas}</table>')


def envoltorio(asunto, cuerpo, preencabezado=""):
    """El armazón. Todo con tablas: es lo que entiende el Outlook de Word."""
    return f"""<!DOCTYPE html>
<html lang="es"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<title>{html.escape(asunto)}</title>
</head>
<body style="margin:0;padding:0;background:#F2F3F4">
<div style="display:none;max-height:0;overflow:hidden;opacity:0">{
    html.escape(preencabezado)}</div>
<table role="presentation" cellpadding="0" cellspacing="0" border="0"
       width="100%" bgcolor="#F2F3F4"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" cellpadding="0" cellspacing="0" border="0"
       width="{ANCHO}" style="width:{ANCHO}px;max-width:100%;background:#FFFFFF;
       border-radius:10px;overflow:hidden">
  <tr><td bgcolor="{CARBON}" style="padding:26px 32px">
    <p style="margin:0;font-family:Helvetica,Arial,sans-serif;font-size:13px;
       letter-spacing:1.4px;color:#B8BCC0">SEMANA GLOBAL DE EMPRENDIMIENTO</p>
    <p style="margin:4px 0 0;font-family:Helvetica,Arial,sans-serif;
       font-size:22px;font-weight:bold;color:#FFFFFF">República Dominicana ·
       {C['anio']}</p>
  </td></tr>
  <tr><td height="6" bgcolor="{NARANJA}" style="height:6px;line-height:6px;
      font-size:0">&nbsp;</td></tr>
  <tr><td style="padding:32px">{cuerpo}</td></tr>
  <tr><td bgcolor="#F7F8F9" style="padding:22px 32px">
    <p style="margin:0 0 6px;font-family:Helvetica,Arial,sans-serif;
       font-size:13px;line-height:1.5;color:#8A8F94">
       {C['fechas']} de {C['anio']} · <a href="https://{C['sitio']}"
       style="color:{NARANJA};text-decoration:none">{C['sitio']}</a></p>
    <p style="margin:0;font-family:Helvetica,Arial,sans-serif;font-size:12px;
       line-height:1.5;color:#A9AEB2">Fundación Enlata e IAvanza son Partners de
       la Semana Global de Emprendimiento en República Dominicana.<br>
       Si no quieres recibir estos correos, responde con «baja».</p>
  </td></tr>
</table></td></tr></table></body></html>"""


CORREOS = {
    "invitacion": {
        "asunto": "Tu organización en la Semana Global de Emprendimiento",
        "pre": "Del 16 al 22 de noviembre. Registrar tu actividad toma 10 minutos.",
        "bloques": [
            ("h", "Súmate a la Semana Global de Emprendimiento"),
            ("p", "Del <b>{fechas} de {anio}</b> se celebra en 200 países la mayor "
                  "campaña del mundo dedicada a acercar el emprendimiento a quien "
                  "nunca lo ha visto como una opción. En República Dominicana la "
                  "hacemos entre todos."),
            ("p", "Si tu organización quiere abrir una actividad —un taller, una "
                  "mesa, una mentoría, lo que ya sabes hacer—, esto es lo que hay "
                  "que saber:"),
            ("l", ["La actividad es tuya: el tema, el formato y la sede los pones tú.",
                   "Nosotros ponemos el arte, el sello y la difusión.",
                   "Entrada libre salvo que decidas otra cosa.",
                   "Se registra en gew.co para que cuente en la campaña global."]),
            ("b", ("Quiero registrar mi actividad", "{{URL_FORMULARIO}}")),
            ("p", "Si tienes dudas antes de decidir, responde a este correo."),
        ]},
    "confirmacion": {
        "asunto": "Recibimos tu actividad · lo que sigue",
        "pre": "Tres cosas que necesitamos para hacerte el arte.",
        "bloques": [
            ("h", "Ya estás dentro"),
            ("p", "Recibimos el registro de <b>{{ACTIVIDAD}}</b>. Para hacerte el "
                  "arte y ponerte en la agenda necesitamos tres cosas:"),
            ("l", ["El <b>logo de tu organización</b> en PNG con fondo transparente "
                   "o en vector. Cuanto más grande, mejor.",
                   "Una <b>foto horizontal</b> de una actividad tuya, si la tienes.",
                   "El <b>enlace de inscripción</b>, si vas a pedir registro."]),
            ("b", ("Enviar los materiales", "{{URL_MATERIALES}}")),
            ("p", "Cuando los tengamos te mandamos tu kit: el flyer en tres "
                  "formatos, el sello para tu web y una hoja con lo que puedes y "
                  "lo que no puedes hacer con la marca."),
        ]},
    "recordatorio": {
        "asunto": "Faltan dos semanas · tu kit está listo",
        "pre": "Descarga tus piezas y publica cuando quieras.",
        "bloques": [
            ("h", "Faltan dos semanas"),
            ("p", "Tu kit ya está: el flyer de tu actividad en los tres formatos "
                  "que se usan, el sello para tu web y tu firma, y la hoja de uso "
                  "de marca."),
            ("b", ("Descargar mi kit", "{{URL_KIT}}")),
            ("l", ["Publica cuando quieras: no hay fecha coordinada.",
                   "Etiquétanos y usa {hashtag} para que aparezca en el muro.",
                   "Si cambias hora o sede, respóndenos y rehacemos el arte."]),
        ]},
    "cierre": {
        "asunto": "Gracias · así se vivió la semana",
        "pre": "Las cifras, las fotos y lo que viene.",
        "bloques": [
            ("h", "Gracias"),
            ("p", "La Semana terminó y tu actividad fue parte. En las próximas "
                  "semanas te mandamos la revista de recap con las cifras, las "
                  "fotos y lo que salió de cada actividad."),
            ("p", "Si tienes fotos de la tuya, mándalas: entran en la revista."),
            ("b", ("Enviar mis fotos", "{{URL_FOTOS}}")),
        ]},
}


def construir(clave):
    c = CORREOS[clave]
    fmt = {"fechas": C["fechas"], "anio": C["anio"],
           "hashtag": C["hashtags"][0]}
    partes = []
    for tipo, dato in c["bloques"]:
        if tipo == "h":
            partes.append(
                f'<p style="margin:0 0 18px;font-family:Helvetica,Arial,'
                f'sans-serif;font-size:26px;line-height:1.3;font-weight:bold;'
                f'color:{CARBON}">{dato.format(**fmt)}</p>')
        elif tipo == "p":
            partes.append(_p(dato.format(**fmt)))
        elif tipo == "l":
            partes.append(_lista([x.format(**fmt) for x in dato]))
        elif tipo == "b":
            partes.append(_boton(dato[0], dato[1]))
    return c["asunto"], envoltorio(c["asunto"], "".join(partes), c["pre"])


def texto_plano(html_):
    """La versión de texto. Un correo sin ella cae en spam más fácil."""
    t = re.sub(r"<(script|style|title)[^>]*>.*?</\1>", " ", html_, flags=re.S)
    t = re.sub(r'<div style="display:none.*?</div>', " ", t, flags=re.S)
    t = re.sub(r"<a [^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>", r"\2 (\1)", t, flags=re.S)
    t = re.sub(r"</(p|tr|table|h\d)>", "\n", t)
    t = html.unescape(re.sub(r"<[^>]+>", "", t))
    return re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t]+", " ", t)).strip()


def mide(html_):
    n = len(html_.encode("utf-8"))
    return {"bytes": n, "pct_de_gmail": round(n / TOPE_GMAIL * 100, 1),
            "recorta_gmail": n > TOPE_GMAIL,
            "usa_flex_o_grid": bool(re.search(r"display\s*:\s*(flex|grid)", html_)),
            "imagenes_incrustadas": html_.count("data:image"),
            "ancho": ANCHO}


def main():
    ap = argparse.ArgumentParser(description="Correos de campaña GEW · RD")
    ap.add_argument("--tipo", choices=sorted(CORREOS))
    ap.add_argument("--todos", action="store_true")
    ap.add_argument("--salida", default=DESTINO_POR_DEFECTO)
    a = ap.parse_args()
    if not a.tipo and not a.todos:
        a.todos = True

    os.makedirs(a.salida, exist_ok=True)
    claves = sorted(CORREOS) if a.todos else [a.tipo]
    hechos, fallos = [], []
    print(f"{'correo':14} {'bytes':>7} {'% del tope':>11} {'flex/grid':>10} "
          f"{'img incrust.':>13}")
    for k in claves:
        asunto, h_ = construir(k)
        m = mide(h_)
        ph = f"{a.salida}/{k}.html"
        open(ph, "w", encoding="utf-8").write(h_)
        pt = f"{a.salida}/{k}.txt"
        open(pt, "w", encoding="utf-8").write(f"{asunto}\n\n{texto_plano(h_)}\n")
        hechos += [ph, pt]
        print(f"  {k:12} {m['bytes']:7,} {m['pct_de_gmail']:10.1f}% "
              f"{('SÍ' if m['usa_flex_o_grid'] else 'no'):>10} "
              f"{m['imagenes_incrustadas']:13}")
        if m["recorta_gmail"]:
            fallos.append(f"  FALLA {k}: {m['bytes']:,} bytes — Gmail recorta "
                          f"a partir de {TOPE_GMAIL:,}")
        if m["usa_flex_o_grid"]:
            fallos.append(f"  FALLA {k}: usa flex o grid, y el Outlook clásico "
                          f"los ignora")
        if m["imagenes_incrustadas"]:
            fallos.append(f"  FALLA {k}: {m['imagenes_incrustadas']} imagen(es) "
                          f"incrustadas — engordan el HTML y disparan el recorte")

    print(f"\nproducidos {len(hechos)} de {len(claves)*2} esperados "
          f"(HTML y texto plano de cada uno)")
    print(f"ancho {ANCHO} px · tope de Gmail {TOPE_GMAIL:,} bytes · "
          f"maquetado con <table> para el Outlook de motor Word")
    for f in fallos:
        print(f)
    for h in hechos:
        print(h)
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
