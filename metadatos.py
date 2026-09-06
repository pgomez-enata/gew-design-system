#!/usr/bin/env python3
"""
Procedencia dentro del fichero · GEW · RD.

Antes de esto, 358 de 394 piezas salían sin un solo metadato: ni quién las
hizo, ni de qué campaña son, ni con qué licencia. Un PNG anónimo en la carpeta
de descargas de otra persona.

Escribe en cada PNG:
  · un bloque XMP/RDF con los campos del IPTC Photo Metadata Standard 2025.1,
    en un chunk `iTXt` llamado `XML:com.adobe.xmp` — que es como Pillow puede
    escribir XMP en PNG (el parámetro `xmp=` de `save()` sólo vale para WebP);
  · chunks `tEXt` sueltos (Author, Copyright, Description, Software) que
    cualquier visor enseña sin saber de XMP;
  · un namespace propio `enlata:` con la familia, la pieza, el formato y la
    versión de tokens con la que se generó.

No hace falta instalar nada: se probó en esta máquina con Pillow 11.3.0.
`exiftool` haría falta sólo para JPEG, y no producimos JPEG.

Uso:
    python3 metadatos.py                 sella todo _salida/
    python3 metadatos.py --leer RUTA     enseña lo que lleva dentro un fichero
    python3 metadatos.py --verificar     dice cuántas piezas están sin sellar
"""
import argparse, datetime, glob, json, os, sys
from xml.sax.saxutils import escape

from PIL import Image
from PIL.PngImagePlugin import PngInfo

RAIZ = os.path.dirname(os.path.abspath(__file__))
TOK = json.load(open(f"{RAIZ}/tokens/tokens.json", encoding="utf-8"))
PROC = TOK["procedencia"]
VERSION = TOK["meta"]["version"]

CLAVE_XMP = "XML:com.adobe.xmp"
MARCA = "enlata:sistema"          # lo que busca la auditoría para saber si está sellado

# La familia sale de la carpeta. La raíz de _salida/ son las piezas de campaña.
FAMILIAS = {
    "": "campaña", "actividad": "actividad", "cita": "cita", "video": "video",
    "serie": "serie", "aliados": "aliado", "impreso": "impreso",
    "revista": "revista", "perfil": "perfil", "prensa": "prensa",
}


def _familia(ruta):
    rel = os.path.relpath(ruta, f"{RAIZ}/_salida")
    partes = rel.split(os.sep)
    return FAMILIAS.get(partes[0] if len(partes) > 1 else "", partes[0])


def _formato(nombre):
    """El sufijo `--<formato>` del nombre, si lo lleva."""
    base = os.path.splitext(nombre)[0]
    return base.split("--")[-1] if "--" in base else None


def bloque_xmp(campos):
    """XMP/RDF con los campos IPTC. `campos` son los propios de la pieza."""
    def alt(v):
        return (f'<rdf:Alt><rdf:li xml:lang="x-default">{escape(v)}'
                f'</rdf:li></rdf:Alt>')

    def seq(v):
        return f'<rdf:Seq><rdf:li>{escape(v)}</rdf:li></rdf:Seq>'

    propias = "".join(f'\n      <enlata:{k}>{escape(str(v))}</enlata:{k}>'
                      for k, v in campos["enlata"].items())
    return f'''<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:xmp="http://ns.adobe.com/xap/1.0/"
    xmlns:photoshop="http://ns.adobe.com/photoshop/1.0/"
    xmlns:xmpRights="http://ns.adobe.com/xap/1.0/rights/"
    xmlns:enlata="https://enlata.do/ns/gew/1.0/">
      <dc:creator>{seq(PROC["creador"])}</dc:creator>
      <dc:rights>{alt(PROC["derechos"])}</dc:rights>
      <dc:title>{alt(campos["titulo"])}</dc:title>
      <dc:description>{alt(campos["descripcion"])}</dc:description>
      <photoshop:Credit>{escape(PROC["credito"])}</photoshop:Credit>
      <xmpRights:WebStatement>{escape(PROC["web_derechos"])}</xmpRights:WebStatement>
      <xmpRights:Marked>True</xmpRights:Marked>
      <xmp:CreateDate>{campos["fecha"]}</xmp:CreateDate>
      <xmp:CreatorTool>{escape(PROC["herramienta"])} {VERSION}</xmp:CreatorTool>{propias}
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>'''


def campos_de(ruta):
    fam = _familia(ruta)
    nombre = os.path.basename(ruta)
    pieza = os.path.splitext(nombre)[0].split("--")[0]
    fmt = _formato(nombre)
    im = Image.open(ruta)
    return {
        "titulo": f"GEW {TOK['campana']['anio']} · RD — {pieza}",
        "descripcion": (f"Pieza de {fam}"
                        + (f", formato {fmt}" if fmt else "")
                        + f". {TOK['campana']['tema_es']}. "
                        f"{TOK['campana']['fechas']} de {TOK['campana']['anio']}."),
        "fecha": datetime.date.today().isoformat(),
        "enlata": {
            "sistema": "gew_design_system",
            "version": VERSION,
            "campana": f"GEW {TOK['campana']['anio']} · República Dominicana",
            "familia": fam,
            "pieza": pieza,
            "formato": fmt or "—",
            "lienzo": f"{im.width}x{im.height}",
        },
    }


def sellar(ruta):
    """Reescribe el PNG con su procedencia dentro. Conserva el dpi."""
    im = Image.open(ruta)
    dpi = im.info.get("dpi")
    campos = campos_de(ruta)
    m = PngInfo()
    m.add_itxt(CLAVE_XMP, bloque_xmp(campos), zip=False)
    m.add_text("Author", PROC["creador"])
    m.add_text("Copyright", PROC["derechos"])
    m.add_text("Description", campos["descripcion"])
    m.add_text("Software", f"{PROC['herramienta']} {VERSION}")
    m.add_text("Creation Time", campos["fecha"])
    for k, v in campos["enlata"].items():
        m.add_text(f"enlata:{k}", str(v))
    kw = {"pnginfo": m}
    if dpi:
        kw["dpi"] = dpi
    im.save(ruta, **kw)
    return campos


def sellado(ruta):
    """¿Este fichero lleva su procedencia dentro?"""
    try:
        info = Image.open(ruta).info
    except Exception:
        return False
    return MARCA in info and CLAVE_XMP in info


def leer(ruta):
    info = Image.open(ruta).info
    return {k: v for k, v in info.items() if k != CLAVE_XMP}


def main():
    ap = argparse.ArgumentParser(description="Procedencia dentro del fichero")
    ap.add_argument("--leer", metavar="RUTA")
    ap.add_argument("--verificar", action="store_true")
    ap.add_argument("--salida", default=f"{RAIZ}/_salida")
    a = ap.parse_args()

    if a.leer:
        for k, v in leer(a.leer).items():
            print(f"  {k:22} {str(v)[:96]}")
        print(f"\n  XMP: {'sí' if CLAVE_XMP in Image.open(a.leer).info else 'NO'}")
        return

    Image.MAX_IMAGE_PIXELS = None
    rutas = [p for p in sorted(glob.glob(f"{a.salida}/**/*.png", recursive=True))
             if not any(f"{os.sep}{d}{os.sep}" in p
                        for d in ("publico", "demo"))]
    if not rutas:
        sys.exit("no hay nada que sellar en _salida/")

    if a.verificar:
        sin = [r for r in rutas if not sellado(r)]
        print(f"{len(rutas) - len(sin)} de {len(rutas)} piezas selladas")
        for r in sin[:10]:
            print(f"  SIN SELLAR  {os.path.relpath(r, RAIZ)}")
        if len(sin) > 10:
            print(f"  … y {len(sin) - 10} más")
        sys.exit(1 if sin else 0)

    hechas, fallos = 0, []
    for r in rutas:
        try:
            sellar(r)
            hechas += 1
        except Exception as e:                       # un lote no se cae entero
            fallos.append((os.path.relpath(r, RAIZ), str(e)[:70]))
    print(f"selladas {hechas} de {len(rutas)} esperadas")
    for r, e in fallos:
        print(f"  FALLA {r}: {e}")
    # comprobación en la otra dirección: releer y confirmar que quedó dentro
    ok = sum(1 for r in rutas if sellado(r))
    print(f"releídas y confirmadas: {ok} de {len(rutas)}")
    sys.exit(1 if fallos or ok != len(rutas) else 0)


if __name__ == "__main__":
    main()
