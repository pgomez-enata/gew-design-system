#!/usr/bin/env python3
"""
Kit de vídeo · GEW · RD.

El sistema hacía frames; esto los pone en movimiento. Tres piezas, en vertical
y en horizontal:

    apertura    3 s · el pulso barre y entra el lockup
    cuenta      4 s · la cifra de la cuenta atrás, con el pulso creciendo
    endcard     5 s · la tarjeta de cierre, con el pulso animándose

Los frames se componen con PIL —el mismo motor que las piezas— y se montan con
ffmpeg. Se hace así, y no con los filtros de ffmpeg, porque la tipografía, la
retícula y el pulso ya están resueltos en Python: reescribirlos en `drawtext`
sería tener dos sistemas que se separan.

**Sin audio, a propósito.** Una pieza de campaña se ve en silencio en el 80 %
de los casos y la música se pone al montar. Además, el −14 LUFS que se cita
para YouTube no tiene página oficial de Google: es cifra de terceros, y no
quiero fijarla en el motor.

Lo que sí está publicado y se respeta: **H.264 High Profile, MP4, yuv420p**,
que es lo que pide YouTube; y **≥540×960 con ≥516 kbps**, que es el mínimo
documentado de TikTok. Meta no publica el bitrate de Reels.

Uso:
    python3 movimiento_video.py --todos
    python3 movimiento_video.py --tipo cuenta --dias 3 --formato vertical
"""
import argparse, json, math, os, shutil, subprocess, sys

from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
from campana import (SEGMENTOS, TOK, activo, fuente, png_alto, pulso,  # noqa: E402
                     tinta)

C = TOK["campana"]
CARBON = TOK["color"]["campana2026"]["carbon"]["hex"]
NARANJA = TOK["color"]["campana2026"]["naranja"]["hex"]
BLANCO = "#FFFFFF"
FPS = 30
FORMATOS = {"vertical": (1080, 1920), "horizontal": (1920, 1080),
            "cuadrado": (1080, 1080)}
# La zona que la interfaz de Stories tapa. Es la misma que usa el resto del
# sistema, y sigue siendo criterio nuestro: Meta no publica las cifras.
SEGURA = {"vertical": (269, 1670)}
DURACION = {"apertura": 3.0, "cuenta": 4.0, "endcard": 5.0}
# YouTube publica 8 Mbps para 1080p SDR; TikTok documenta 516 kbps como
# mínimo. 6 Mbps queda cómodo entre los dos. Meta no publica el suyo.
BITRATE_KBPS = 6000


def suave(t):
    """Una entrada que frena al final. Nada de movimiento lineal."""
    return 1 - (1 - t) ** 3


def pulso_parcial(d, x, y, ancho, alto, avance):
    """El pulso, dibujado sólo hasta `avance` (0 a 1). Es el barrido."""
    n = max(1, round(len(SEGMENTOS) * min(1.0, max(0.0, avance))))
    pulso(d, x, y, ancho, alto, n=n)


def frame_apertura(fmt, t):
    w, h = FORMATOS[fmt]
    TOP, BOT = SEGURA.get(fmt, (0, h))
    im = Image.new("RGB", (w, h), CARBON)
    d = ImageDraw.Draw(im)
    m = round(w * 0.0667)
    # el lockup entra desde arriba y se asienta
    a = suave(min(1.0, t / 0.55))
    alto_l = round(w * 0.16)
    lock = png_alto(activo("logo/gew-rd-lockup-blanco.png"), alto_l)
    y_fin = TOP + (BOT - TOP) // 2 - lock.height
    y = round(y_fin - (1 - a) * h * 0.10)
    cap = im.copy()
    cap.paste(lock, ((w - lock.width) // 2, y), lock)
    im = Image.blend(im, cap, a) if a < 1 else cap
    d = ImageDraw.Draw(im)
    # el pulso barre después
    b = suave(max(0.0, min(1.0, (t - 0.45) / 0.9)))
    pulso_parcial(d, m, y + lock.height + round(w * 0.05), w - m * 2,
                  round(w * 0.045), b)
    # y al final, las fechas
    c = suave(max(0.0, min(1.0, (t - 1.35) / 0.7)))
    if c > 0.02:
        f = fuente("Bold", round(w * 0.052))
        txt = C["fechas"]
        bb = d.textbbox((0, 0), txt, font=f)
        col = tuple(round(CARBON_RGB[i] + (255 - CARBON_RGB[i]) * c) for i in range(3))
        d.text(((w - (bb[2] - bb[0])) // 2 - bb[0],
                y + lock.height + round(w * 0.135) - bb[1]), txt, font=f, fill=col)
    return im


CARBON_RGB = tuple(int(CARBON[i:i + 2], 16) for i in (1, 3, 5))


def frame_cuenta(fmt, t, dias):
    w, h = FORMATOS[fmt]
    TOP, BOT = SEGURA.get(fmt, (0, h))
    im = Image.new("RGB", (w, h), CARBON)
    d = ImageDraw.Draw(im)
    m = round(w * 0.0667)
    alto_l = round(w * 0.089)
    lock = png_alto(activo("logo/gew-rd-lockup-blanco.png"), alto_l)
    im.paste(lock, (m, TOP + m), lock)
    pulso_parcial(d, m, TOP + m + lock.height + round(w * 0.028), w - m * 2,
                  round(w * 0.034), suave(min(1.0, t / 1.0)))
    # la cifra entra creciendo
    a = suave(min(1.0, t / 0.6))
    cap = round(w * 0.30 * (0.72 + 0.28 * a))
    f = fuente("Black", cap)
    txt = str(dias) if isinstance(dias, int) else str(dias)
    bb = d.textbbox((0, 0), txt, font=f)
    cy = TOP + (BOT - TOP) // 2
    d.text(((w - (bb[2] - bb[0])) // 2 - bb[0], cy - (bb[3] - bb[1]) // 2 - bb[1]),
           txt, font=f, fill=NARANJA)
    pie = ("días" if isinstance(dias, int) and dias != 1 else
           "día" if isinstance(dias, int) else "")
    if pie:
        f2 = fuente("Bold", round(w * 0.055))
        b2 = d.textbbox((0, 0), pie, font=f2)
        d.text(((w - (b2[2] - b2[0])) // 2 - b2[0],
                cy + (bb[3] - bb[1]) // 2 + round(w * 0.03) - b2[1]), pie,
               font=f2, fill=BLANCO)
    f3 = fuente("Light", round(w * 0.030))
    b3 = d.textbbox((0, 0), C["tema_es"], font=f3)
    d.text(((w - (b3[2] - b3[0])) // 2 - b3[0], BOT - m - round(w * 0.05) - b3[1]),
           C["tema_es"], font=f3, fill="#DCDCDC")
    return im


def frame_endcard(fmt, t):
    w, h = FORMATOS[fmt]
    TOP, BOT = SEGURA.get(fmt, (0, h))
    im = Image.new("RGB", (w, h), CARBON)
    d = ImageDraw.Draw(im)
    m = round(w * 0.0667)
    a = suave(min(1.0, t / 0.7))
    alto_l = round(w * 0.19)
    lock = png_alto(activo("logo/gew-rd-lockup-blanco.png"), alto_l)
    cy = TOP + (BOT - TOP) // 2
    cap = im.copy()
    cap.paste(lock, ((w - lock.width) // 2, cy - lock.height - round(w * 0.06)), lock)
    im = Image.blend(im, cap, a) if a < 1 else cap
    d = ImageDraw.Draw(im)
    b = suave(max(0.0, min(1.0, (t - 0.5) / 0.8)))
    if b > 0.02:
        f = fuente("Bold", round(w * 0.050))
        for i, txt in enumerate((C["fechas"], C["sitio"])):
            bb = d.textbbox((0, 0), txt, font=f)
            col = NARANJA if i else BLANCO
            rgb = tuple(int(col[j:j + 2], 16) for j in (1, 3, 5))
            mez = tuple(round(CARBON_RGB[k] + (rgb[k] - CARBON_RGB[k]) * b)
                        for k in range(3))
            d.text(((w - (bb[2] - bb[0])) // 2 - bb[0],
                    cy + round(w * 0.02) + i * round(w * 0.075) - bb[1]),
                   txt, font=f, fill=mez)
    pulso_parcial(d, m, BOT - m - round(w * 0.05), w - m * 2, round(w * 0.038),
                  suave(max(0.0, min(1.0, (t - 0.3) / 1.1))))
    return im


CONSTRUYE = {"apertura": lambda fmt, t, dias: frame_apertura(fmt, t),
             "cuenta": frame_cuenta,
             "endcard": lambda fmt, t, dias: frame_endcard(fmt, t)}


def render(tipo, fmt, dias=3, salida=None, fps=FPS):
    """Compone los frames y los monta. Devuelve la ruta y lo medido."""
    dur = DURACION[tipo]
    n = round(dur * fps)
    tmp = f"{RAIZ}/_cache/_v/{tipo}-{fmt}"
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp, exist_ok=True)
    for i in range(n):
        CONSTRUYE[tipo](fmt, i / fps, dias).save(f"{tmp}/{i:04d}.png")

    salida = salida or f"{RAIZ}/_salida/video-mp4/{tipo}--{fmt}.mp4"
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    # H.264 High Profile + yuv420p es lo que pide YouTube y lo que traga todo.
    # `+faststart` mueve el índice al principio: sin eso, algunas apps no
    # empiezan a reproducir hasta descargarlo entero.
    # ⚠️ CBR ESTRICTO, y conviene saber por qué. Con CRF, un fondo plano bajaba
    # a 130–415 kbps: se ve perfecto, pero queda por debajo del mínimo
    # documentado de TikTok (516 kbps) y las plataformas recomprimen lo que les
    # llega flojo. Con bitrate «objetivo» x264 tampoco lo gastaba: si no hace
    # falta, no lo usa. Con `nal-hrd=cbr` sí se garantiza el suelo, **rellenando
    # con bits de padding**. Es decir: parte de estos megas no son calidad, son
    # relleno para cumplir un requisito publicado. Se hace a sabiendas.
    r = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps),
         "-i", f"{tmp}/%04d.png", "-c:v", "libx264", "-profile:v", "high",
         "-pix_fmt", "yuv420p", "-b:v", f"{BITRATE_KBPS}k",
         "-minrate", f"{BITRATE_KBPS}k", "-maxrate", f"{BITRATE_KBPS}k",
         "-bufsize", f"{BITRATE_KBPS}k", "-x264-params", "nal-hrd=cbr",
         "-preset", "medium",
         "-movflags", "+faststart", salida],
        capture_output=True, text=True)
    shutil.rmtree(tmp, ignore_errors=True)
    if r.returncode:
        return salida, {"error": r.stderr.strip()[:160]}
    return salida, sonda(salida)


def sonda(ruta):
    """Lo que el fichero ES, preguntado a ffprobe. Nunca lo que yo supuse."""
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,r_frame_rate,nb_frames,codec_name,profile,pix_fmt",
         "-show_entries", "format=duration,size,bit_rate", "-of", "json", ruta],
        capture_output=True, text=True)
    d = json.loads(r.stdout or "{}")
    s = (d.get("streams") or [{}])[0]
    f = d.get("format", {})
    num, den = (s.get("r_frame_rate", "0/1").split("/") + ["1"])[:2]
    return {"px": f"{s.get('width')}x{s.get('height')}",
            "fps": round(int(num) / max(1, int(den)), 2),
            "frames": int(s.get("nb_frames") or 0),
            "codec": s.get("codec_name"), "perfil": s.get("profile"),
            "pix_fmt": s.get("pix_fmt"),
            "seg": round(float(f.get("duration", 0)), 3),
            "bytes": int(f.get("size", 0)),
            "kbps": round(int(f.get("bit_rate", 0)) / 1000)}


def main():
    ap = argparse.ArgumentParser(description="Kit de vídeo GEW · RD")
    ap.add_argument("--tipo", choices=sorted(DURACION))
    ap.add_argument("--formato", choices=sorted(FORMATOS))
    ap.add_argument("--dias", type=int, default=3)
    ap.add_argument("--todos", action="store_true")
    ap.add_argument("--salida", default=f"{RAIZ}/_salida/video-mp4")
    a = ap.parse_args()
    if not (a.tipo and a.formato) and not a.todos:
        a.todos = True

    if not shutil.which("ffmpeg"):
        sys.exit("falta ffmpeg: brew install ffmpeg")

    trabajos = ([(t, f) for t in ("apertura", "cuenta", "endcard")
                 for f in ("vertical", "horizontal")] if a.todos
                else [(a.tipo, a.formato)])
    hechos, fallos = [], []
    print(f"{'pieza':22} {'px':>10} {'fps':>5} {'seg':>6} {'frames':>7} "
          f"{'códec':>8} {'perfil':>6} {'kbps':>6} {'MB':>5}")
    for tipo, fmt in trabajos:
        p, m = render(tipo, fmt, a.dias,
                      salida=f"{a.salida}/{tipo}--{fmt}.mp4")
        if "error" in m:
            fallos.append(f"  FALLA {tipo}/{fmt}: {m['error']}")
            continue
        hechos.append(p)
        print(f"  {tipo+'/'+fmt:20} {m['px']:>10} {m['fps']:5} {m['seg']:6.2f} "
              f"{m['frames']:7} {m['codec']:>8} {m['perfil']:>6} {m['kbps']:6} "
              f"{m['bytes']/1e6:5.2f}")
        esp_px = "x".join(map(str, FORMATOS[fmt]))
        if m["px"] != esp_px:
            fallos.append(f"  FALLA {tipo}/{fmt}: lienzo {m['px']}, esperado {esp_px}")
        if abs(m["seg"] - DURACION[tipo]) > 0.05:
            fallos.append(f"  FALLA {tipo}/{fmt}: dura {m['seg']} s y debía "
                          f"durar {DURACION[tipo]}")
        if m["frames"] != round(DURACION[tipo] * FPS):
            fallos.append(f"  FALLA {tipo}/{fmt}: {m['frames']} fotogramas, "
                          f"esperados {round(DURACION[tipo]*FPS)}")
        if m["pix_fmt"] != "yuv420p":
            fallos.append(f"  FALLA {tipo}/{fmt}: pix_fmt {m['pix_fmt']}, "
                          f"y hace falta yuv420p")
        if m["kbps"] < 516:
            fallos.append(f"  FALLA {tipo}/{fmt}: {m['kbps']} kbps, por debajo "
                          f"del mínimo documentado de TikTok (516)")

    print(f"\nproducidos {len(hechos)} de {len(trabajos)} esperados")
    print("H.264 High + yuv420p (lo que pide YouTube) · sin audio a propósito · "
          "≥516 kbps es el mínimo documentado de TikTok")
    for f in fallos:
        print(f)
    for h in hechos:
        print(h)
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
