#!/usr/bin/env python3
"""
Audita el index contra el sistema · GEW · RD.

El `index.html` está escrito a mano y por eso se desactualiza en silencio: el
5-sep-2026 declaraba 362 piezas cuando ya había 410, y seguía hablando de
«National Host» después de que Piero cerrara que Enlata es Partner.

Esto no lo arregla, lo detecta: compara lo que el index DICE contra lo que el
sistema ES, y falla si no cuadran. Lo que mide un navegador —desbordes,
imágenes rotas— no entra aquí; eso se mide aparte, en el propio navegador.

    python3 auditar_index.py
"""
import glob, json, os, re, sys

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
RAIZ = os.path.dirname(os.path.abspath(__file__))
TOK = json.load(open(f"{RAIZ}/tokens/tokens.json", encoding="utf-8"))
INDEX = f"{RAIZ}/index.html"

# Qué es un motor lo dice esta lista, y sólo esta. Antes había una lista de
# EXCLUSIÓN y se rompía cada vez que nacía una herramienta: pasó con
# sellar_activos.py y volvió a pasar con empaquetar.py. Una lista de inclusión
# no se rompe sola: si nace un motor y no se apunta, el auditor lo dice.
# `empaquetar.py` la tiene igual, pero no viaja al repo público y este fichero
# sí, así que no puede depender de él.
# Cifras que dependen de haber construido, o de tener el padrón real. Que
# falten aquí no es un defecto del index.
MEDIBLES_SI_HAY_SALIDA = {"piezas", "kits", "páginas"}

MOTORES = ["campana.py", "actividad.py", "cita.py", "video.py", "serie.py",
           "aliado.py", "impreso.py", "perfil.py", "revista.py",
           "revista_reporte.py", "prensa.py", "movimiento.py",
           "senal.py", "deck.py", "correo.py", "movimiento_video.py",
           "patrocinio.py", "postevento.py", "calendario.py"]

# Términos retirados: si aparecen, el index habla de algo que ya no es.
RETIRADOS = {
    "NATIONAL HOST": "el rótulo de la banda ya no existe",
    "anfitrión nacional": "Enlata es Partner, no anfitrión",
    "pastilla índigo": "retirada del sistema de Enlata",
    "seis tramos": "la barra de 6 de GEN la sustituyó el pulso",
}
# «National Host» a secas NO se puede prohibir: es el nombre del documento de
# GEN («guía de National Hosts») y sale también en la nota que explica por qué
# se retiró el término. Se prohíbe sólo cuando se lo atribuye a Enlata.
RETIRADOS_CONTEXTO = [
    (r"Enlata\s+(?:es|como)\s+(?:«)?National Host",
     "Enlata es Partner (cerrado por Piero el 5-sep-2026)"),
    (r"(?:pieza|piezas|crédito|banda)\s+(?:social\s+)?(?:de[l]?\s+)?National Host",
     "las piezas ya no se atribuyen a un National Host"),
]
# Términos que TIENEN que estar: si faltan, el index no cuenta lo que hay.
EXIGIDOS = {
    "pulso": "el elemento distintivo del movimiento",
    "IA Media": "el tercer papel, en las piezas de cobertura",
    "PATROCINADORES": "el bloque de patrocinadores de la banda",
    "COBERTURA": "el rótulo del tercer bloque",
}


def texto_plano():
    s = open(INDEX, encoding="utf-8").read()
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", s, flags=re.S)
    t = re.sub(r'data:image/[^"]*', " ", t)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t)), s


def real():
    """Lo que el sistema ES, medido ahora mismo.

    En un clon recién bajado no hay `_salida/`, así que las cifras que salen de
    ahí no son «0»: son «no se pudo medir». Devolverlas como 0 haría que el
    auditor acusara al index de mentir cuando el que no sabe es él."""
    import campana as C
    # los andamios (`publico/`, `demo/`) no son piezas del sistema
    png = [p for p in glob.glob(f"{RAIZ}/_salida/**/*.png", recursive=True)
           if not any(f"{os.sep}{d}{os.sep}" in p for d in ("publico", "demo"))]
    motores = [f for f in MOTORES if os.path.exists(f"{RAIZ}/{f}")]
    hay_salida = os.path.isdir(f"{RAIZ}/_salida")
    # El padrón manda sobre DOS cifras, no una: con el de ejemplo hay 24 kits
    # en vez de 48, y por tanto 144 piezas de aliado en vez de 288. Comparar el
    # total contra lo que declara el index acusaba al index de una diferencia
    # que es del padrón. Se vio en el clon, no aquí.
    from aliado import padron, PADRON_EJEMPLO
    padron_real = padron() != list(PADRON_EJEMPLO)
    d = {}
    if hay_salida and padron_real:
        d["piezas"] = len(png)
        d["kits"] = len(glob.glob(f"{RAIZ}/_salida/aliados/*"))
    d.update({
        "formatos": len(C.FORMATOS),
        "formatos de campaña": len(C.FMT_CAMPANA),
        "motores": len(motores),
        "segmentos": len(C.SEGMENTOS),
    })
    inf = f"{RAIZ}/_salida/revista/informe.json"
    if os.path.exists(inf):
        d["páginas"] = json.load(open(inf, encoding="utf-8"))["geometria"]["paginas"]
    return d, hay_salida


def main():
    if not os.path.exists(INDEX):
        sys.exit("no hay index.html")
    txt, crudo = texto_plano()
    R, hay_salida = real()
    fallos, avisos = [], []

    for t, por_que in RETIRADOS.items():
        n = txt.count(t)
        if n:
            fallos.append(f'  FALLA  término retirado: «{t}» aparece {n} vez(ces) — {por_que}')
    for pat, por_que in RETIRADOS_CONTEXTO:
        for m in re.finditer(pat, txt):
            fallos.append(f'  FALLA  «{m.group(0)}» — {por_que}')

    # ⭐ El término retirado se vigilaba SÓLO en el index, y se coló en la firma
    # del reconocimiento y en el masthead de la revista: dos piezas que se
    # imprimen. Ahora se barre todo el código y el contenido, que es de donde
    # salen las piezas.
    for otro in sorted(glob.glob(f"{RAIZ}/*.py")
                       + glob.glob(f"{RAIZ}/contenido/*.json")):
        if os.path.basename(otro) == "auditar_index.py":
            continue          # este fichero habla de la regla, no la incumple
        cont = open(otro, encoding="utf-8", errors="ignore").read()
        for pat, por_que in RETIRADOS_CONTEXTO + [
                (r"National Host(?!s)", "el papel de Enlata es Partner; "
                 "«guía de National HostS» en plural sí se puede citar")]:
            for m in re.finditer(pat, cont):
                fallos.append(f"  FALLA  {os.path.basename(otro)}: "
                              f"«{m.group(0)}» — {por_que}")
    for t, por_que in EXIGIDOS.items():
        if t not in txt:
            fallos.append(f'  FALLA  falta «{t}» — {por_que}')

    # Las cifras del index van marcadas con `data-real="<clave>"`. Antes esto
    # buscaba «N piezas» por texto y capturaba también «15 piezas» de campaña o
    # «5 piezas» de un carrusel: el auditor daba tres cifras distintas para lo
    # mismo. Marcarlas en el HTML quita la adivinanza.
    marcadas = {}
    for m in re.finditer(r'data-real="([^"]+)"[^>]*>([\d.,]+)<', crudo):
        marcadas.setdefault(m.group(1), set()).add(m.group(2).replace(".", "").replace(",", ""))
    for clave, valor in R.items():
        dichas = marcadas.get(clave)
        if not dichas:
            avisos.append(f'  AVISO  el index no declara «{clave}» con data-real '
                          f"(real: {valor})")
            continue
        malas = sorted(x for x in dichas if x != str(valor))
        if malas:
            fallos.append(f'  FALLA  «{clave}»: el index dice {", ".join(malas)} '
                          f"y el sistema tiene {valor}")
    # la versión: es lo primero que se queda viejo y no lleva data-real
    vs = set(re.findall(r"v(\d+\.\d+\.\d+)", txt))
    malas_v = sorted(x for x in vs if x != TOK["meta"]["version"])
    if malas_v:
        fallos.append(f'  FALLA  versión: el index dice v{", v".join(malas_v)} '
                      f'y tokens va por v{TOK["meta"]["version"]}')
    elif not vs:
        avisos.append("  AVISO  el index no declara la versión del sistema")

    # Lo que no se puede medir no es un fallo del index: es que aquí no se ha
    # construido. `páginas` sale del informe de la revista, que sólo existe si
    # se corrió — en un clon con otros motores corridos, `_salida/` existe pero
    # ese informe no, y el auditor acusaba al index de mentir.
    # Tres cosas distintas, y confundirlas hacía que el auditor acusara al index
    # de mentir cuando el que no podía medir era él:
    #   · lo que real() sabe medir pero aquí no hay → aviso
    #   · lo que real() no conoce                   → fallo, sobra o falta código
    sin_medir = set(marcadas) - set(R)
    aqui_no_hay = {c for c in sin_medir if c in MEDIBLES_SI_HAY_SALIDA}
    for clave in sorted(sin_medir - aqui_no_hay):
        fallos.append(f'  FALLA  data-real="{clave}" no lo mide el auditor: '
                      "o sobra en el HTML o falta en real()")
    if aqui_no_hay:
        avisos.append("  AVISO  no se pueden comprobar en esta copia: "
                      + ", ".join(sorted(aqui_no_hay)))

    print(f"index {os.path.getsize(INDEX):,} bytes · "
          f"{len(re.findall(r'<h2', crudo))} secciones · "
          f"{len(re.findall(r'<img', crudo))} imágenes")
    if not hay_salida:
        print("  (no hay _salida/: las cifras que salen de las piezas no se "
              "comprueban en esta copia — construye antes)")
    elif "piezas" not in R:
        print("  (padrón de ejemplo: piezas y kits no se comparan, dependen de "
              "los 48 aliados reales)")
    print(f"sistema v{TOK['meta']['version']} · " +
          " · ".join(f"{v} {k}" for k, v in R.items()))
    for x in fallos + avisos:
        print(x)
    if not fallos and not avisos:
        print("  el index cuadra con el sistema")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
