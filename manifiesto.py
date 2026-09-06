#!/usr/bin/env python3
"""
Manifiesto de lo producido · GEW · RD.

Antes de esto no había forma de saber si el PNG que tienes en el escritorio es
el vigente o el de hace tres tandas. El manifiesto responde a eso: qué se
produjo, cuándo, con qué versión del sistema, y el hash de cada fichero.

    python3 manifiesto.py               escribe _salida/manifiesto.json
    python3 manifiesto.py --verificar   compara el disco contra el manifiesto

`--verificar` distingue tres cosas que no son lo mismo:
    CAMBIADO   está en las dos partes pero el hash no coincide
    FALTA      el manifiesto lo declara y en el disco no está
    SOBRA      está en el disco y el manifiesto no lo declara

Un lote que revienta a la mitad no lanza error: entrega menos y parece que
funcionó. `FALTA` es exactamente ese caso.
"""
import argparse, datetime, glob, hashlib, json, os, platform, sys

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
RAIZ = os.path.dirname(os.path.abspath(__file__))
TOK = json.load(open(f"{RAIZ}/tokens/tokens.json", encoding="utf-8"))
DESTINO = f"{RAIZ}/_salida/manifiesto.json"

import metadatos as M


def sha(ruta, bloque=1 << 20):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for trozo in iter(lambda: f.read(bloque), b""):
            h.update(trozo)
    return h.hexdigest()


def ficheros(base):
    """Todo lo que hay en _salida/, menos el propio manifiesto."""
    out = []
    for p in sorted(glob.glob(f"{base}/**/*", recursive=True)):
        # `publico/` y `demo/` son andamios: el paquete para GitHub y el
        # sistema con activos de marcador. Los arman y los borran sus propios
        # scripts; no son producción.
        if any(f"{os.sep}{d}{os.sep}" in p for d in ("publico", "demo")):
            continue
        if os.path.isfile(p) and os.path.abspath(p) != os.path.abspath(DESTINO):
            out.append(p)
    return out


def entrada(p, base):
    e = {"ruta": os.path.relpath(p, base).replace(os.sep, "/"),
         "bytes": os.path.getsize(p),
         "sha256": sha(p)}
    if p.lower().endswith(".png"):
        im = Image.open(p)
        e.update(lienzo=f"{im.width}x{im.height}", modo=im.mode,
                 dpi=im.info.get("dpi", [None])[0], sellado=M.sellado(p))
        e["familia"] = M._familia(p)
    return e


def construir(base):
    fs = ficheros(base)
    ent = [entrada(p, base) for p in fs]
    png = [e for e in ent if "lienzo" in e]
    return {
        "_nota": "Lo que produjo el sistema en esta corrida. Lo escribe "
                 "manifiesto.py; no se edita a mano.",
        "generado": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "sistema": "gew_design_system",
        "version_tokens": TOK["meta"]["version"],
        "entorno": {"python": platform.python_version(),
                    "pillow": Image.__version__,
                    "so": f"{platform.system()} {platform.release()}"},
        "resumen": {
            "ficheros": len(ent),
            "png": len(png),
            "bytes": sum(e["bytes"] for e in ent),
            "sellados": sum(1 for e in png if e.get("sellado")),
            "por_familia": {f: sum(1 for e in png if e.get("familia") == f)
                            for f in sorted({e.get("familia") for e in png} - {None})},
        },
        "ficheros": ent,
    }


def verificar(base):
    if not os.path.exists(DESTINO):
        print("no hay manifiesto: córrelo sin --verificar para crearlo")
        return 1
    viejo = json.load(open(DESTINO, encoding="utf-8"))
    antes = {e["ruta"]: e for e in viejo["ficheros"]}
    ahora = {os.path.relpath(p, base).replace(os.sep, "/"): p for p in ficheros(base)}

    cambiados = [r for r in sorted(set(antes) & set(ahora))
                 if sha(ahora[r]) != antes[r]["sha256"]]
    faltan = sorted(set(antes) - set(ahora))
    sobran = sorted(set(ahora) - set(antes))

    print(f"manifiesto del {viejo['generado']} · tokens {viejo['version_tokens']}")
    print(f"declara {len(antes)} ficheros · en disco hay {len(ahora)}")
    for etq, lista in (("CAMBIADO", cambiados), ("FALTA", faltan), ("SOBRA", sobran)):
        for r in lista[:8]:
            print(f"  {etq}  {r}")
        if len(lista) > 8:
            print(f"  {etq}  … y {len(lista) - 8} más")
    if not (cambiados or faltan or sobran):
        print("  el disco coincide con el manifiesto")
    return 1 if (cambiados or faltan) else 0


def main():
    ap = argparse.ArgumentParser(description="Manifiesto de lo producido")
    ap.add_argument("--verificar", action="store_true")
    ap.add_argument("--salida", default=f"{RAIZ}/_salida")
    a = ap.parse_args()

    if a.verificar:
        sys.exit(verificar(a.salida))

    if not os.path.isdir(a.salida):
        sys.exit(f"no existe {a.salida}: construye algo antes "
                 f"(python3 entorno.py te dice si la máquina puede)")
    m = construir(a.salida)
    os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
    json.dump(m, open(DESTINO, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    r = m["resumen"]
    print(f"{r['ficheros']} ficheros · {r['png']} PNG · {r['bytes']/1e6:.1f} MB")
    print(f"sellados: {r['sellados']} de {r['png']}")
    for f, n in r["por_familia"].items():
        print(f"  {f:12} {n:4}")
    print(DESTINO)
    sys.exit(0 if r["sellados"] == r["png"] else 1)


if __name__ == "__main__":
    main()
