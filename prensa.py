#!/usr/bin/env python3
"""
Nota de prensa y boilerplate · GEW · RD.

Sigue la estructura de la plantilla oficial de GEN («GEW 2026_Campaign Launch
Announcement_For Partners»), traducida y con los créditos que la guía de
National Hosts obliga a incluir.

Saca dos cosas:
    nota.md        la nota lista para rellenar y enviar
    creditos.md    el bloque de boilerplate y créditos, para pegar al pie de
                   cualquier pieza de más de una hoja

⚠️ Las cifras globales de GEW NO se rellenan solas: las cuatro fuentes oficiales
de GEN se contradicen. El motor deja `{{CIFRA_...}}` a la vista para que nadie
publique un número sin elegirlo. Ver `_conflicto` en contenido/prensa.json.

Uso:
    python3 prensa.py
    python3 prensa.py --titular "..." --ciudad "Santo Domingo"
"""
import argparse, json, os, sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
TOK = json.load(open(f"{RAIZ}/tokens/tokens.json", encoding="utf-8"))
P = json.load(open(f"{RAIZ}/contenido/prensa.json", encoding="utf-8"))

NOTA = """# PARA PUBLICACIÓN INMEDIATA

# {titular}

**{ciudad} — {fecha}.** {apertura}

{contexto}

{dato_local}

{campana}

> «{cita_lider}»
>
> — **{lider_nombre}**, {lider_cargo}

> «{cita_aliado}»
>
> — **{aliado_nombre}**, {aliado_cargo}

{llamado}

---

## En cifras

⚠️ **Sin rellenar a propósito.** Las cuatro fuentes oficiales de GEN dan cifras
distintas para lo mismo. Lo único que coincide en todas: **200 países** y
**10 millones de personas** al año. Elige la fuente antes de publicar y borra
este aviso.

- Países donde se celebra: **200**
- Personas alcanzadas al año: **10 millones**
- Actividades: `{{{{CIFRA_ACTIVIDADES}}}}`  ·  Organizaciones aliadas: `{{{{CIFRA_PARTNERS}}}}`
- En República Dominicana: `{{{{CIFRA_RD}}}}` actividades y **{aliados_rd} organizaciones aliadas**

## Contacto de prensa

{contacto_nombre} · {contacto_cargo}
Fundación Enlata
{contacto_correo} · {contacto_telefono}

---

{creditos}
"""

MARCAS = """## El movimiento

**Partners**: Fundación Enlata · IAvanza
**Patrocinadores**: {{PATROCINADORES}} — no se nombra ninguna marca hasta que el
acuerdo esté firmado.
**Cobertura**: IA Media

"""

CREDITOS = """## Sobre la Fundación Enlata

{enlata}

## Sobre la Semana Global de Emprendimiento

{gew}

## Sobre la Global Entrepreneurship Network

{gen}

{kauffman}
"""


def creditos():
    b = P["boilerplate"]
    return MARCAS + CREDITOS.format(enlata=b["enlata"]["es"], gew=b["gew"]["es"],
                           gen=b["gen"]["es"], kauffman=P["kauffman"]["frase_es"])


def nota(**kw):
    d = dict(
        titular="La Semana Global de Emprendimiento vuelve a República Dominicana "
                "con {aliados_rd} organizaciones aliadas",
        ciudad="Santo Domingo, República Dominicana",
        fecha="{{FECHA}}",
        apertura="La Fundación Enlata anunció hoy la programación de la Semana Global "
                 "de Emprendimiento 2026 en República Dominicana, que se celebrará del "
                 f"{TOK['campana']['fechas']} con actividades abiertas en todo el país.",
        contexto="La Semana Global de Emprendimiento es la mayor campaña del mundo "
                 "dedicada a acercar el emprendimiento a quien nunca lo ha visto como "
                 "una opción. Se celebra simultáneamente en 200 países y este año lleva "
                 f"por lema «{TOK['campana']['tema_es']}».",
        dato_local="{{DATO_LOCAL}} — aquí va una cifra dominicana verificada, con su "
                   "fuente. Sin fuente, se quita.",
        campana="Durante los siete días, las organizaciones aliadas abrirán talleres, "
                "mesas de trabajo, competencias y encuentros. La programación completa "
                "está en gew.co y en enlata.do/gew.",
        cita_lider="{{CITA}}",
        lider_nombre="{{NOMBRE}}", lider_cargo="presidente de la Fundación Enlata",
        cita_aliado="{{CITA}}",
        aliado_nombre="{{NOMBRE}}", aliado_cargo="{{CARGO}}",
        llamado="Las actividades son de entrada libre salvo donde se indique. "
                "El programa completo y el registro están en **gew.co**.",
        aliados_rd="48",
        contacto_nombre="{{NOMBRE}}", contacto_cargo="{{CARGO}}",
        contacto_correo="{{CORREO}}", contacto_telefono="{{TELEFONO}}",
    )
    d.update({k: v for k, v in kw.items() if v})
    d["titular"] = d["titular"].format(aliados_rd=d["aliados_rd"])
    return NOTA.format(creditos=creditos(), **d)


def main():
    ap = argparse.ArgumentParser(description="Nota de prensa GEW · RD")
    ap.add_argument("--titular")
    ap.add_argument("--ciudad")
    ap.add_argument("--fecha")
    ap.add_argument("--salida", default=f"{RAIZ}/_salida/prensa")
    a = ap.parse_args()

    os.makedirs(a.salida, exist_ok=True)
    hechos = []
    with open(f"{a.salida}/nota.md", "w", encoding="utf-8") as f:
        f.write(nota(titular=a.titular, ciudad=a.ciudad, fecha=a.fecha))
    hechos.append(f"{a.salida}/nota.md")
    with open(f"{a.salida}/creditos.md", "w", encoding="utf-8") as f:
        f.write(creditos())
    hechos.append(f"{a.salida}/creditos.md")
    with open(f"{a.salida}/angulos.md", "w", encoding="utf-8") as f:
        f.write("# Ángulos de prensa · GEW RD\n\n"
                "Los seis que propone GEN, con su estadística y a qué medio van. "
                "Cada cifra lleva su fuente: si no la puedes citar, no la uses.\n\n")
        for i, x in enumerate(P["angulos"], 1):
            f.write(f"## {i} · {x['titular']}\n\n"
                    f"**El dato**: {x['dato']}\n\n"
                    f"**Fuente**: {x['fuente_dato']}\n\n"
                    f"**A quién**: {x['medios']}\n\n---\n\n")
    hechos.append(f"{a.salida}/angulos.md")

    print(f"producidos {len(hechos)} de 3 esperados")
    huecos = nota().count("{{")
    print(f"huecos por rellenar en la nota: {huecos}")
    print(f"ángulos: {len(P['angulos'])}")
    print("AVISO  las cifras globales quedan sin rellenar: las 4 fuentes de GEN "
          "se contradicen (ver _conflicto en contenido/prensa.json)")
    for h in hechos:
        print(h)


if __name__ == "__main__":
    main()
