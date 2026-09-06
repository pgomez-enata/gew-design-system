#!/usr/bin/env python3
"""
Calendario · GEW · RD.

Un fichero `.ics` que el aliado abre y se le mete la actividad en el móvil.
Nadie lo hace y cuesta muy poco: es la diferencia entre «anótalo» y que esté
anotado.

Saca dos cosas:
    gew-rd-2026.ics       la semana entera, un evento por día
    <actividad>.ics       una actividad suelta, para el aliado

Lo que hay que respetar del formato (RFC 5545), y que rompe si no se hace:

  · **Las líneas se pliegan a 75 octetos.** No a 75 caracteres: a octetos. Con
    acentos y eñes, una línea de 75 caracteres puede pasar de 75 octetos y hay
    clientes que la cortan mal. Aquí se cuenta en bytes.
  · **Los saltos son CRLF**, no LF.
  · Las comas, los puntos y coma y las barras van escapados dentro del texto.
  · `UID` único y `DTSTAMP` en UTC.

Uso:
    python3 calendario.py --semana
    python3 calendario.py --actividad "Taller de finanzas" --dia 18 --hora 18:00
"""
import argparse, datetime as dt, hashlib, json, os, sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
TOK = json.load(open(f"{RAIZ}/tokens/tokens.json", encoding="utf-8"))
C = TOK["campana"]
ANIO = C["anio"]
# «16-22 de noviembre» → los dos extremos. Se lee del token, no se escribe aquí.
_d = C["fechas"].split(" de ")[0].split("-")
DIA_INI, DIA_FIN = int(_d[0]), int(_d[1])
MES = 11
TZ = "America/Santo_Domingo"          # RD no cambia de hora desde 2000
SITIO = C["sitio"]


def esc(t):
    """RFC 5545: coma, punto y coma y barra se escapan; los saltos, a \\n."""
    return (str(t).replace("\\", "\\\\").replace(";", "\;")
            .replace(",", "\\,").replace("\n", "\\n"))


def plegar(linea):
    """Pliega a 75 OCTETOS, no a 75 caracteres. Con acentos no es lo mismo, y
    un cliente que cuente bytes corta a mitad de carácter."""
    b = linea.encode("utf-8")
    if len(b) <= 75:
        return linea
    out, resto = [], b
    lim = 75
    while len(resto) > lim:
        corte = lim
        # no partir un carácter multibyte por la mitad
        while corte > 0 and (resto[corte] & 0xC0) == 0x80:
            corte -= 1
        out.append(resto[:corte].decode("utf-8"))
        resto = resto[corte:]
        lim = 74                      # las continuaciones llevan un espacio
    out.append(resto.decode("utf-8"))
    return "\r\n ".join(out)


def _uid(*partes):
    h = hashlib.sha256("·".join(map(str, partes)).encode()).hexdigest()[:20]
    return f"{h}@gew-rd.{SITIO}"


def evento(titulo, inicio, fin, lugar="", descripcion="", url=""):
    sello = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    ls = ["BEGIN:VEVENT",
          f"UID:{_uid(titulo, inicio)}",
          f"DTSTAMP:{sello}",
          f"DTSTART;TZID={TZ}:{inicio.strftime('%Y%m%dT%H%M%S')}",
          f"DTEND;TZID={TZ}:{fin.strftime('%Y%m%dT%H%M%S')}",
          f"SUMMARY:{esc(titulo)}"]
    if lugar:
        ls.append(f"LOCATION:{esc(lugar)}")
    if descripcion:
        ls.append(f"DESCRIPTION:{esc(descripcion)}")
    if url:
        ls.append(f"URL:{esc(url)}")
    ls += ["BEGIN:VALARM", "TRIGGER:-PT2H", "ACTION:DISPLAY",
           f"DESCRIPTION:{esc(titulo)}", "END:VALARM", "END:VEVENT"]
    return ls


def calendario(eventos, nombre="Semana Global de Emprendimiento · RD"):
    ls = ["BEGIN:VCALENDAR", "VERSION:2.0",
          "PRODID:-//Fundacion Enlata//GEW RD//ES", "CALSCALE:GREGORIAN",
          "METHOD:PUBLISH", f"X-WR-CALNAME:{esc(nombre)}",
          f"X-WR-TIMEZONE:{TZ}"]
    for e in eventos:
        ls += e
    ls.append("END:VCALENDAR")
    return "\r\n".join(plegar(l) for l in ls) + "\r\n"


def semana():
    evs = []
    for d in range(DIA_INI, DIA_FIN + 1):
        ini = dt.datetime(ANIO, MES, d, 9, 0)
        evs.append(evento(
            f"Semana Global de Emprendimiento · día {d - DIA_INI + 1}",
            ini, dt.datetime(ANIO, MES, d, 21, 0),
            "República Dominicana",
            f"{C['tema_es']}. La programación completa está en {SITIO}.",
            f"https://{SITIO}"))
    return evs


def mide(texto):
    """Lo que el fichero ES. Las tres cosas que rompen un .ics."""
    ls = texto.split("\r\n")
    largas = [l for l in ls if len(l.encode("utf-8")) > 75]
    return {"bytes": len(texto.encode("utf-8")), "lineas": len(ls),
            "eventos": texto.count("BEGIN:VEVENT"),
            "lineas_de_mas_de_75_octetos": len(largas),
            "crlf": texto.count("\r\n") == len(ls) - 1,
            "lf_sueltos": len([1 for i, c in enumerate(texto)
                               if c == "\n" and (i == 0 or texto[i-1] != "\r")]),
            "cierra_bien": texto.rstrip().endswith("END:VCALENDAR")}


def main():
    ap = argparse.ArgumentParser(description="Calendario .ics GEW · RD")
    ap.add_argument("--semana", action="store_true")
    ap.add_argument("--actividad")
    ap.add_argument("--dia", type=int, default=18)
    ap.add_argument("--hora", default="18:00")
    ap.add_argument("--duracion", type=float, default=2.0)
    ap.add_argument("--lugar", default="")
    ap.add_argument("--salida", default=f"{RAIZ}/_salida/calendario")
    a = ap.parse_args()
    if not a.semana and not a.actividad:
        a.semana = True

    os.makedirs(a.salida, exist_ok=True)
    hechos, fallos = [], []
    print(f"{'fichero':32} {'bytes':>7} {'ev.':>4} {'líneas':>7} "
          f"{'>75 octetos':>12} {'CRLF':>6}")

    trabajos = []
    if a.semana:
        trabajos.append(("gew-rd-2026.ics", calendario(semana())))
    if a.actividad:
        hh, mm = (a.hora.split(":") + ["0"])[:2]
        ini = dt.datetime(ANIO, MES, a.dia, int(hh), int(mm))
        fin = ini + dt.timedelta(hours=a.duracion)
        slug = "".join(ch if ch.isalnum() else "-"
                       for ch in a.actividad.lower())[:40].strip("-")
        trabajos.append((f"{slug}.ics", calendario(
            [evento(a.actividad, ini, fin, a.lugar,
                    f"Actividad de la Semana Global de Emprendimiento. "
                    f"{C['tema_es']}.", f"https://{SITIO}")],
            f"{a.actividad} · GEW RD")))

    for nombre, txt in trabajos:
        p = f"{a.salida}/{nombre}"
        open(p, "w", encoding="utf-8", newline="").write(txt)
        m = mide(txt)
        hechos.append(p)
        print(f"  {nombre:30} {m['bytes']:7,} {m['eventos']:4} {m['lineas']:7} "
              f"{m['lineas_de_mas_de_75_octetos']:12} "
              f"{('sí' if m['crlf'] else 'NO'):>6}")
        if m["lineas_de_mas_de_75_octetos"]:
            fallos.append(f"  FALLA {nombre}: {m['lineas_de_mas_de_75_octetos']} "
                          f"línea(s) de más de 75 octetos, sin plegar")
        if m["lf_sueltos"]:
            fallos.append(f"  FALLA {nombre}: {m['lf_sueltos']} salto(s) LF "
                          f"sueltos; el RFC pide CRLF")
        if not m["cierra_bien"]:
            fallos.append(f"  FALLA {nombre}: no cierra con END:VCALENDAR")
        if not m["eventos"]:
            fallos.append(f"  FALLA {nombre}: no lleva ningún evento")

    print(f"\nproducidos {len(hechos)} de {len(trabajos)} esperados · "
          f"zona {TZ} · plegado a 75 OCTETOS (RFC 5545)")
    for f in fallos:
        print(f)
    for h in hechos:
        print(h)
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
