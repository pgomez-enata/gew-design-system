#!/usr/bin/env python3
"""
Tarjeta de llamada a la acción · GEW · RD.

La pieza que se pega en los últimos segundos. Sale del punto 5 del catálogo
`VIDEO-tecnicas.md`, y es de lo poco que tiene respaldo publicado: TikTok mide
**+45 % de recall y +19 % de likeability** con una CTA card en el cierre
(*TikTok Marketing Science* con **Lumen Research**). Hasta ahora el sistema
sólo ponía `gew.co` dentro del endcard: eso es un dato, no una llamada.

Tres cosas la separan del resto de las piezas:

**1 · Se compone dentro de la zona segura de ANUNCIO, no de la orgánica.** Un
CTA es exactamente lo que se promociona, y Meta reserva el 35 % inferior en
creatividad de anuncios (40 % si lleva disclaimers). Un CTA debajo de esa línea
es un CTA que la interfaz tapa: no sirve de nada.

**2 · El texto entra por palabras a 6,67 palabras/s** — una por semicorchea a
100 BPM, que cae dentro del 5–10 que TikTok publica. No es una elección
estética: es la cadencia que la rejilla ya daba.

**3 · ⛔ Rechaza el engagement bait.** Meta lo tiene prohibido y definido —pedir
votos, compartidos, comentarios, etiquetas o «me gusta» sin un CTA específico
**reduce la distribución**—. El motor no lo avisa: se niega a generarlo.

⚠️ **Los textos de abajo son una propuesta, no una decisión.** Sólo «Súmate a la
Semana Global de Emprendimiento» existe ya en el sistema (`correo.py`). El tono
lo decide Piero: `--accion` y `--destino` aceptan lo que sea.

Uso:
    python3 cta.py --todas
    python3 cta.py --clave registro --formato vertical
    python3 cta.py --accion "Inscríbete ya" --destino gew.co
"""
import argparse, os, re, sys

from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
from campana import TOK, activo, fuente, marcas, png_alto  # noqa: E402
import animacion as AN  # noqa: E402
import pulso_musica as PM  # noqa: E402
import zonas as ZN  # noqa: E402

C = TOK["campana"]
CARBON = TOK["color"]["campana2026"]["carbon"]["hex"]
NARANJA = TOK["color"]["campana2026"]["naranja"]["hex"]
BLANCO = "#FFFFFF"
FPS = 30
DUR = 2.4          # 4 tiempos = 1 compás a 100 BPM = 72 fotogramas exactos
FORMATOS = {"vertical": (1080, 1920), "retrato": (1080, 1350),
            "horizontal": (1920, 1080), "cuadrado": (1080, 1080)}
PAPEL = "solo"     # la tarjeta va sola: el pulso es `espectro`

# Propuesta de partida. Sólo la primera existe ya en el sistema.
ACCIONES = {
    "sumate": ("Súmate a la Semana Global de Emprendimiento", "enlata.do/gew"),
    "registro": ("Inscríbete", C["sitio"]),
    "actividad": ("Publica tu actividad", C["sitio"]),
    "aliado": ("Sé aliado", "enlata.do/gew"),
}

# ⛔ Meta define esto como engagement bait y baja la distribución de quien lo
# usa. No es una opinión de estilo: está publicado y tiene consecuencia.
CEBO = [
    (r"\b(comenta|comentá|comente|coment[aá]nos)\b", "pedir comentarios"),
    (r"\b(etiqueta|etiquetá|etiquete|menciona|mencion[aá])\b", "pedir etiquetas"),
    (r"\b(comparte|compartí|comparta|reenv[ií]a)\b", "pedir compartidos"),
    (r"\b(dale\s+like|dale\s+me\s+gusta|dame\s+like)\b", "pedir «me gusta»"),
    (r"\b(vota|votá|vote|voten)\b", "pedir votos"),
    (r"\b(tag|tagg?ea)\b", "pedir etiquetas"),
]


def revisa(texto):
    """Devuelve la lista de motivos por los que este texto no puede salir."""
    t = texto.lower()
    return [q for pat, q in CEBO if re.search(pat, t)]


_PLANOS = {}


def plano(fmt, accion, destino):
    """Apila la tarjeta de abajo arriba con las cajas medidas, y la mete entera
    dentro de la franja que Meta deja libre en anuncios."""
    clave = (fmt, accion, destino)
    if clave in _PLANOS:
        return _PLANOS[clave]
    w, h = FORMATOS[fmt]
    U = min(w, h)
    m = round(w * 0.0667)
    # La franja de ANUNCIO, no la orgánica: es la diferencia de esta pieza.
    con_ui = fmt in ZN.CON_INTERFAZ
    top, bot, izq, der = ZN.franja((w, h), "anuncio", con_ui)
    if not con_ui:
        top, bot = round(h * 0.06), h - round(h * 0.06)
    ancho = min(der, w - m) - max(izq, m)
    x0 = max(izq, m)
    d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    hueco = round(U * 0.035)
    alto_p = round(U * 0.050)

    for esc in (1.0, 0.92, 0.84, 0.76, 0.68, 0.60, 0.52, 0.45):
        lock = png_alto(activo("logo/gew-rd-lockup-blanco.png"),
                        round(U * 0.105 * esc))
        cap_a = round(U * 0.082 * esc)
        # el titular se parte en líneas que quepan a lo ancho
        f_a = fuente("Black", cap_a)
        lineas = parte(accion, f_a, ancho, d)
        h_lin = round(cap_a * 1.16)
        f_d = fuente("Bold", round(U * 0.052 * esc))
        b_d = d.textbbox((0, 0), destino, font=f_d)
        med = marcas(Image.new("RGB", (w, h), CARBON),
                     ImageDraw.Draw(Image.new("RGB", (w, h), CARBON)),
                     x0, 0, ancho, U, oscuro=True, cobertura=False)
        alto_total = (lock.height + hueco + alto_p + hueco
                      + h_lin * len(lineas) + hueco
                      + (b_d[3] - b_d[1]) + hueco + med["alto_usado"])
        if (alto_total <= bot - top
                and max(d.textlength(x, font=f_a) for x in lineas) <= ancho
                and b_d[2] - b_d[0] <= ancho):
            break

    y = top + max(0, (bot - top - alto_total) // 2)
    y_lock, y = y, y + lock.height + hueco
    y_p, y = y, y + alto_p + hueco
    y_txt = y
    y += h_lin * len(lineas) + hueco
    base_d = y + (b_d[3] - b_d[1])
    y_rot = base_d + hueco
    cajas = ([("lockup", y_lock, y_lock + lock.height),
              ("pulso", y_p, y_p + alto_p)]
             + [(f"linea{i+1}", y_txt + i * h_lin, y_txt + (i + 1) * h_lin)
                for i in range(len(lineas))]
             + [("destino", base_d - (b_d[3] - b_d[1]), base_d),
                ("marcas", y_rot, y_rot + med["alto_usado"])])
    P = {"w": w, "h": h, "x": x0, "ancho": ancho, "m": m, "U": U, "top": top,
         "bot": bot, "lock": lock, "y_lock": y_lock, "y_p": y_p,
         "alto_p": alto_p, "lineas": lineas, "f_a": f_a, "h_lin": h_lin,
         "y_txt": y_txt, "f_d": f_d, "b_d": b_d, "base_d": base_d,
         "y_rot": y_rot, "escala": esc, "cajas": cajas,
         "en_zona_anuncio": con_ui}
    mal = _cruces(cajas)
    if mal:
        raise SystemExit(f"cta/{fmt}: bloques que se cruzan — " +
                         "; ".join(f"{a}/{b} {px} px" for a, b, px in mal))
    if cajas[0][1] < top or cajas[-1][2] > bot:
        raise SystemExit(f"cta/{fmt}: se sale de la franja de anuncio "
                         f"({cajas[0][1]}–{cajas[-1][2]}; vale {top}–{bot})")
    _PLANOS[clave] = P
    return P


def parte(texto, font, ancho, d):
    """Parte el titular en líneas EQUILIBRADAS.

    ⚠️ El reparto codicioso —meter palabras hasta que no quepa— dejaba «de»
    solo en una línea entera en «Súmate a la Semana Global de Emprendimiento».
    Aquí se prueban todos los repartos en k líneas y se elige el que menos
    hueco desperdicia, que es el que reparte parejo. Con titulares de una
    docena de palabras el coste es nulo."""
    pal = texto.split()
    if not pal:
        return [""]
    anchos = [d.textlength(p, font=font) for p in pal]
    esp = d.textlength(" ", font=font)

    def largo(i, j):
        return sum(anchos[i:j]) + esp * (j - i - 1)

    for k in range(1, len(pal) + 1):
        mejor, corte = None, None
        # todos los repartos de las palabras en k trozos contiguos
        def busca(ini, faltan, acc):
            nonlocal mejor, corte
            if faltan == 1:
                L = largo(ini, len(pal))
                if L > ancho:
                    return
                coste = sum((ancho - x) ** 2 for x in acc + [L])
                if mejor is None or coste < mejor:
                    mejor, corte = coste, acc + [(ini, len(pal))]
                return
            for j in range(ini + 1, len(pal) - faltan + 2):
                L = largo(ini, j)
                if L > ancho:
                    break
                busca(j, faltan - 1, acc + [L] if False else acc + [L])
        # `acc` guarda longitudes; los cortes se rehacen al final
        res = []

        def busca2(ini, faltan, trozos, largos):
            nonlocal mejor, res
            if faltan == 1:
                L = largo(ini, len(pal))
                if L > ancho:
                    return
                coste = sum((ancho - x) ** 2 for x in largos + [L])
                if mejor is None or coste < mejor:
                    mejor = coste
                    res = trozos + [(ini, len(pal))]
                return
            for j in range(ini + 1, len(pal) - faltan + 2):
                L = largo(ini, j)
                if L > ancho:
                    break
                busca2(j, faltan - 1, trozos + [(ini, j)], largos + [L])

        busca2(0, k, [], [])
        if res:
            return [" ".join(pal[i:j]) for i, j in res]
    return [" ".join(pal)]          # no cabe ni partido: lo dirá el encogido


def _cruces(cajas):
    mal = []
    for i in range(len(cajas)):
        for j in range(i + 1, len(cajas)):
            (na, a0, a1), (nb, b0, b1) = cajas[i], cajas[j]
            if min(a1, b1) - max(a0, b0) > 0:
                mal.append((na, nb, min(a1, b1) - max(a0, b0)))
    return mal


def frame(fmt, t, accion, destino, PU, reloj, escrito, f_sale):
    P = plano(fmt, accion, destino)
    w, h = P["w"], P["h"]
    im = Image.new("RGB", (w, h), CARBON)
    d = ImageDraw.Draw(im)

    # el lockup aparece de entrada: el titular manda y no se hace esperar
    a = AN.frena(min(1.0, t / reloj.seg("1c")))
    cap = im.copy()
    cap.paste(P["lock"], ((w - P["lock"].width) // 2, P["y_lock"]), P["lock"])
    im = Image.blend(im, cap, a) if a < 1 else cap
    d = ImageDraw.Draw(im)

    f_pulso = round(t * PU[2]["fps"]) % PU[2]["frames"]
    PM.dibuja(d, P["x"], P["y_p"], P["ancho"], P["alto_p"], PU[0], PU[1], f_pulso)

    # la acción, palabra a palabra sobre la semicorchea
    n = escrito(t)
    vistas, puestas = [], 0
    for linea in P["lineas"]:
        pal = linea.split()
        if puestas >= n:
            break
        vistas.append(" ".join(pal[:max(0, n - puestas)]))
        puestas += len(pal)
    for i, linea in enumerate(vistas):
        if not linea:
            continue
        bb = d.textbbox((0, 0), linea, font=P["f_a"])
        d.text(((w - (bb[2] - bb[0])) // 2 - bb[0],
                P["y_txt"] + i * P["h_lin"] - bb[1]), linea,
               font=P["f_a"], fill=BLANCO)

    # el destino entra cuando ya está escrita la acción
    tot = sum(len(x.split()) for x in P["lineas"])
    if n >= tot:
        bb = P["b_d"]
        d.text(((w - (bb[2] - bb[0])) // 2 - bb[0], P["base_d"] - bb[3]),
               destino, font=P["f_d"], fill=NARANJA)

    marcas(im, ImageDraw.Draw(im), P["x"], P["y_rot"], P["ancho"], P["U"],
           oscuro=True, cobertura=False)
    s = f_sale(t)
    if s < 0.999:
        im = Image.blend(Image.new("RGB", (w, h), CARBON), im, s)
    return im


def render(fmt, accion, destino, salida, dur=DUR, fps=FPS, sale="apaga"):
    motivos = revisa(accion)
    if motivos:
        raise SystemExit(
            f"⛔ ese texto es engagement bait ({', '.join(motivos)}). Meta lo "
            f"tiene prohibido y BAJA LA DISTRIBUCIÓN de quien lo usa. "
            f"Texto: «{accion}»")
    R = PM.rejilla(fps=fps)
    PU = PM.bucle(PM.PAPELES[PAPEL], R)
    reloj = AN.Reloj(dur=dur, bpm=R["bpm"], fps=fps)
    escrito, n_pal, seg_txt, r = reloj.escribe(accion, ini="1c")
    f_sale = reloj.sale(sale, dur="2c")
    n = round(dur * fps)
    w, h = FORMATOS[fmt]
    m = PM.monta_seq((frame(fmt, i / fps, accion, destino, PU, reloj, escrito,
                            f_sale) for i in range(n)), w, h, salida, fps)
    if "error" in m:
        return m
    m.update({"palabras": n_pal, "seg_texto": round(seg_txt, 2),
              "ritmo": round(r, 2), "ritmo_ok": AN.ritmo_ok(n_pal, seg_txt),
              "tiempos": round(dur * R["bpm"] / 60, 3), "sale": sale})
    m.update({"queda": (PM.queda_al_final(salida) or {}).get("queda")})
    return m


DIR = f"{RAIZ}/_salida/cta"


def main():
    ap = argparse.ArgumentParser(description="Tarjeta de CTA · GEW·RD")
    ap.add_argument("--clave", choices=sorted(ACCIONES))
    ap.add_argument("--accion")
    ap.add_argument("--destino")
    ap.add_argument("--formato", choices=sorted(FORMATOS))
    ap.add_argument("--dur", type=float, default=DUR)
    ap.add_argument("--sale", choices=sorted(AN.SALIDAS), default="apaga")
    ap.add_argument("--todas", action="store_true")
    ap.add_argument("--salida", default=DIR)
    a = ap.parse_args()
    if not (a.clave or a.accion) and not a.todas:
        a.todas = True

    R = PM.rejilla()
    tiempos = a.dur * R["bpm"] / 60
    if abs(tiempos - round(tiempos)) > 1e-9:
        sys.exit(f"{a.dur} s son {tiempos:.3f} tiempos a {R['bpm']:g} BPM: "
                 f"el corte caería a mitad de tiempo.")
    print(f'tarjeta de CTA · {a.dur:g} s = {tiempos:.0f} tiempos · '
          f'{round(a.dur*FPS)} fotogramas · pulso «{PM.PAPELES[PAPEL]}»')
    print("dentro de la franja de ANUNCIO de Meta (14 % arriba · 35 % abajo · "
          "6 % lados): un CTA que la interfaz tapa no sirve de nada")

    if a.todas:
        trabajos = [(k, f) for k in sorted(ACCIONES) for f in sorted(FORMATOS)]
    else:
        clave = a.clave or "libre"
        if a.accion:
            ACCIONES[clave] = (a.accion, a.destino or C["sitio"])
        trabajos = [(clave, f) for f in
                    ([a.formato] if a.formato else sorted(FORMATOS))]

    hechas, fallos = [], []
    print(f'\n{"tarjeta":26} {"px":>10} {"seg":>6} {"fr":>4} {"palabras":>9} '
          f'{"pal/s":>7} {"5–10":>6} {"queda":>7} {"MB":>5}')
    for clave, fmt in trabajos:
        accion, destino = ACCIONES[clave]
        ruta = f"{a.salida}/{clave}--{fmt}.mp4"
        m = render(fmt, accion, destino, ruta, dur=a.dur, sale=a.sale)
        if "error" in m:
            fallos.append(f'  FALLA {clave}/{fmt}: {m["error"]}')
            continue
        hechas.append(ruta)
        print(f'  {clave+"/"+fmt:24} {m["px"]:>10} {m["seg"]:6.2f} '
              f'{m["frames"]:4} {m["palabras"]:9} {m["ritmo"]:7.2f} '
              f'{("sí" if m["ritmo_ok"] else "NO"):>6} '
              f'{(m["queda"] or 0):6.1f} % {m["bytes"]/1e6:5.2f}')
        esp = "x".join(map(str, FORMATOS[fmt]))
        if m["px"] != esp:
            fallos.append(f'  FALLA {clave}/{fmt}: lienzo {m["px"]}')
        if m["frames"] != round(a.dur * FPS):
            fallos.append(f'  FALLA {clave}/{fmt}: {m["frames"]} fotogramas')
        if not m["ritmo_ok"]:
            fallos.append(f'  FALLA {clave}/{fmt}: el texto va a '
                          f'{m["ritmo"]:.2f} palabras/s y TikTok publica 5–10')
        if a.sale != "mantiene" and (m["queda"] or 0) > 25:
            fallos.append(f'  FALLA {clave}/{fmt}: salida «{a.sale}» y queda '
                          f'el {m["queda"]:.1f} % de la tinta')
        # y lo propio de esta pieza: que quepa entera en la franja de anuncio
        P = plano(fmt, accion, destino)
        fuera = ZN.bloques_dentro(P["cajas"], FORMATOS[fmt], "anuncio",
                                  fmt in ZN.CON_INTERFAZ)
        if fuera:
            fallos.append(f'  FALLA {clave}/{fmt}: ' +
                          "; ".join(f"{n} fuera por {d}" for n, _, _, d in fuera))

    print(f"\nproducidas {len(hechas)} de {len(trabajos)} esperadas")
    if len(hechas) != len(trabajos):
        fallos.append(f"  FALLA el lote: {len(hechas)} de {len(trabajos)}")
    print("texto a una palabra por semicorchea · CTA card al cierre "
          "(+45 % recall, TikTok Marketing Science con Lumen) · "
          "⛔ sin engagement bait")
    for f in fallos:
        print(f)
    print(f"\n{len(fallos)} fallos")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
