#!/usr/bin/env python3
"""
Zona segura, en dos niveles · GEW · RD.

Hasta ahora el sistema tenía UNA zona segura: 269 px arriba y 1670 abajo en
1080×1920, declarada como criterio nuestro. Sigue siéndolo, y con razón:
**ninguna plataforma publica zona segura para contenido orgánico**. Ni YouTube,
ni LinkedIn, ni Meta, ni TikTok. Todo lo que circula —«150 px arriba, 250
abajo», «el centro 1080×1080»— es de agencias y plantillas, no de la plataforma.
Consultado el 6-sep-2026 sobre sus páginas oficiales.

La excepción, y es la que obliga a este módulo: **Meta SÍ publica una zona
segura para creatividad de ANUNCIOS — 14 % arriba, 35 % abajo, 6 % a los
lados.** Comparada con la nuestra:

    arriba   269 px = 14,01 %   contra el 14 % de Meta  → coincide clavado
    abajo    250 px = 13,02 %   contra el 35 % de Meta  → nos faltan 422 px

Para lo orgánico no es un error: no hay cifra oficial que incumplir. Pero si una
pieza se promociona, la interfaz de anuncios se come esos 422 px de abajo. Medido
sobre las piezas verticales, ahí caen **los cinco bloques inferiores del
endcard** —fechas, sitio, los dos Partners, IA Media y el pulso—.

⛔ **Lo que este módulo NO hace es cambiar la zona de hoy.** Aplicar el 35 % de
Meta a todo desperdiciaría un tercio de la pantalla en piezas que nunca se van a
promocionar. Lo que hace es **avisar**: dice qué bloques caerían fuera si la
pieza se usara como anuncio, y deja la decisión donde va.

Uso:
    import zonas
    zonas.franja((1080, 1920), "anuncio")      → (269, 1248, 65, 1015)
    zonas.bloques_dentro(cajas, (1080,1920), "anuncio")   → los que se cortarían
"""
NIVELES = {
    # Criterio NUESTRO. No hay fuente oficial y no la va a haber: se mide contra
    # capturas reales, no contra una página. Sólo aplica a 9:16.
    "organico": {"arriba": 269 / 1920, "abajo": 250 / 1920, "lados": 0.0,
                 "fuente": "criterio propio, medido contra capturas de Stories",
                 "oficial": False},
    # Meta, publicado, SÓLO para creatividad de anuncios.
    "anuncio": {"arriba": 0.14, "abajo": 0.35, "lados": 0.06,
                "fuente": "Meta · especificaciones de anuncios de Reels y "
                          "Stories (14 % arriba · 35 % abajo · 6 % lados)",
                "oficial": True},
    # ⚠️ Meta publica TRES cifras distintas para tres cosas distintas, y se
    # confunden con facilidad. Esta es la más estricta: en anuncios de Reels
    # hay que dejar libre el 40 % inferior porque ahí van los disclaimers
    # legales. Si la pieza los va a llevar, manda ésta y no la de arriba.
    "anuncio-disclaimer": {"arriba": 0.14, "abajo": 0.40, "lados": 0.06,
                           "fuente": "Meta · anuncios de Reels, 40 % inferior "
                                     "libre para disclaimers",
                           "oficial": True},
    # Y ésta es la más suave: sólo reserva sitio para que el sticker de enlace
    # de Stories no tape nada. No es la zona de la creatividad entera.
    "sticker-stories": {"arriba": 0.14, "abajo": 0.20, "lados": 0.0,
                        "fuente": "Instagram · sitio libre para el sticker de "
                                  "enlace en Stories (~14 % arriba / ~20 % "
                                  "abajo)",
                        "oficial": True},
}
# Dónde tapa la interfaz de verdad. Sólo el 9:16 a pantalla completa —Stories y
# Reels—. En apaisado, en cuadrado y en 4:5 de feed **no** se aplica: la reserva
# de Stories no se traslada porque el lienzo sea vertical. Meta publica su
# 14/35/6 para creatividad de Reels y Stories, no para el 4:5 del feed.
CON_INTERFAZ = {"vertical"}


def franja(px, nivel="organico", con_interfaz=True):
    """(arriba, abajo, izquierda, derecha) en píxeles. `abajo` y `derecha` son
    coordenadas, no márgenes: lo utilizable es el rectángulo entre ellas."""
    w, h = px
    if nivel not in NIVELES:
        raise SystemExit(f"nivel desconocido: {nivel}. "
                         f"Hay: {', '.join(sorted(NIVELES))}")
    if not con_interfaz:
        return 0, h, 0, w
    N = NIVELES[nivel]
    return (round(h * N["arriba"]), round(h * (1 - N["abajo"])),
            round(w * N["lados"]), round(w * (1 - N["lados"])))


def bloques_dentro(cajas, px, nivel="anuncio", con_interfaz=True):
    """Qué bloques de una pieza caen en la franja que tapa ese nivel.

    `cajas` son (nombre, y0, y1) — las mismas que ya devuelven los planos de los
    motores. Devuelve [(nombre, y0, y1, dónde)]."""
    arriba, abajo, _, _ = franja(px, nivel, con_interfaz)
    fuera = []
    for n, a, b in cajas:
        if a < arriba:
            fuera.append((n, a, b, "arriba"))
        elif b > abajo:
            fuera.append((n, a, b, "abajo"))
    return fuera


def informe(cajas, px, fmt=None, nivel="anuncio"):
    """Una línea por bloque en riesgo, lista para imprimir en la corrida."""
    ci = fmt is None or fmt in CON_INTERFAZ
    if not ci:
        return [f"  {fmt}: sin interfaz que tape · nada que avisar"]
    mal = bloques_dentro(cajas, px, nivel, ci)
    if not mal:
        return []
    N = NIVELES[nivel]
    return ([f'  AVISO nivel «{nivel}» ({N["fuente"]}):'] +
            [f"    {n} ({a}-{b}) queda {d} de la franja utilizable"
             for n, a, b, d in mal])
