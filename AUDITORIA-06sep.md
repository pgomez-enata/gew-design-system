# Auditoría del sistema · 6-sep-2026

No es la auditoría de las piezas —esa la corre `auditoria.py` y está en
verde—. Es la del **sistema**: qué cubre, qué no mira nadie, y dónde el
sistema promete algo que no cumple.

**Estado: 5 de 10 arreglados el mismo día** (H3, H5, H8, H10 y el reparto de
marcas que salió de H9). Los cinco que quedan están al final, con su coste.

Todo lo de aquí se midió hoy. Cada hallazgo lleva el comando.

---

## Lo que está bien, y conviene dejar dicho

| | medida | comando |
|---|---|---|
| Piezas contra las reglas | **435 piezas · 2 395 comprobaciones · verde** | `python3 auditoria.py` |
| Procedencia | **435 de 435 PNG con XMP** (era 36 de 394) | `grep -l xmpmeta` sobre `_salida` |
| Lotes completos | **11 de 11 familias cuadran** producido/esperado | conteo por `glob` |
| Correos | los 4 por debajo del tope de Gmail; el mayor, **4 735 B de 102 400** | `wc -c` sobre `_salida/correo/*.html` |
| Calendarios | **0 líneas de más de 75 octetos**, CRLF completo (120/120 y 25/25) | conteo en bytes sobre los `.ics` |
| El movimiento | pulso o banda de marcas en **15 motores** | `grep -c "pulso(\|marcas("` |
| Vídeo | 6 MP4, H.264 High, yuv420p, 30 fps, 3/4/5 s exactos, ~5,8 Mbps | `ffprobe` |

El §1.2 de `ESTANDARIZAR-salidas.md` —«358 de 394 ficheros salen sin
metadatos»— queda **cerrado**.

---

## H1 · 119 ficheros salen sin una sola comprobación · 21,5 %

`auditoria.py` recorre `_salida/**/*.png` y nada más. Todo lo que no es PNG
pasa sin que nadie lo mire:

| tipo | n | qué es |
|---|---|---|
| `.html` | 52 | 4 correos + 48 sellos de aliado |
| `.md` | 51 | 48 LÉEME de kit + 3 de prensa |
| `.mp4` | 6 | el kit de vídeo |
| `.txt` | 4 | los correos en texto plano |
| `.pdf` | 2 | la revista y el deck |
| `.ics` | 2 | los calendarios |
| `.json` | 2 | informes |

**Hoy están todos bien** —lo comprobé a mano arriba—, y ese es justo el
problema: la comprobación existe **dentro del motor** y no en la puerta. El
día que un correo pase de 102 KB o que un `.ics` se cuele con una línea
larga, `auditoria.py` seguirá diciendo «todo en verde». Es el frente 7:
un fallo que no avisa.

Los dos entregables más caros del sistema —la revista de 32 páginas y los 6
MP4— son de los que nadie mide.

`comando: find _salida -type f ! -name '*.png' | grep -v demo | grep -v publico | wc -l`

## H2 · Los dos PDF son fotos de texto

| fichero | páginas | peso | ¿lleva fuentes? |
|---|---|---|---|
| `revista/revista.pdf` | 32 | 8,22 MB | **no** |
| `deck/deck.pdf` | 7 | 0,54 MB | **no** |

Ninguno tiene un objeto `/Font`: son PNG metidos en un PDF. Consecuencias
reales, no teóricas:

- no se busca ni se copia una línea;
- un lector de pantalla no lee nada — y la accesibilidad es exigible, no
  opcional (`SALIDAS-v2.md`, Parte 3);
- la imprenta no puede corregir una errata sin volver a generar la página;
- 8,22 MB para 32 páginas de una revista que se va a mandar por WhatsApp.

Estaba diagnosticado para la revista en `ESTANDARIZAR-salidas.md` §1.4. El
deck, que es posterior, heredó el mismo camino.

`comando: búsqueda de /Type/Page y /Font en los bytes del PDF`

## H3 · Dos ficheros distintos se llaman igual

> **ARREGLADO** · 6-sep.

```
_salida/postevento/semana--retrato.png     1080×1350
_salida/serie/agenda/semana--retrato.png   1080×1350
_salida/postevento/semana--cuadrado.png    1080×1080
_salida/serie/agenda/semana--cuadrado.png  1080×1080
```

Mismo nombre, misma medida, contenido distinto: uno es el recap de la semana
y el otro es la programación. Mientras vivan en su carpeta no pasa nada; en
cuanto se sueltan juntos en una carpeta de entrega o se mandan por WhatsApp,
uno pisa al otro y no se nota.

Las otras 6 repeticiones de nombre son los kits de los 48 aliados —cada uno
en su carpeta— y ahí es lo correcto.

`comando: find … | sed 's|.*/||' | sort | uniq -d`

## H4 · Una familia se audita 4,5 veces mejor que otra

| familia | piezas | compr. | por pieza |
|---|---|---|---|
| campaña (raíz) | 106 | 1 106 | **10,4** |
| revista | 32 | 288 | 9,0 |
| actividad | 9 | 48 | 5,3 |
| cita | 12 | 60 | 5,0 |
| video | 12 | 54 | 4,5 |
| serie | 28 | 112 | 4,0 |
| **aliados** | **192** | **576** | **3,0** |
| patrocinio · postevento | 11 | 33 | 3,0 |
| movimiento | 7 | 16 | **2,3** |

Los 192 PNG de los aliados son **el 44 % de todo lo que produce el sistema** y
reciben 3 comprobaciones cada uno: van por la rama genérica, que sólo mira el
sello y el lienzo. Son además las piezas que **publica alguien de fuera**,
donde un fallo se ve en la cuenta de otro.

`ESTANDARIZAR-salidas.md` §1.1 medía 8×; ha bajado a 4,5× pero no está
cerrado.

`comando: instrumentar auditoria.audita() y contar reglas por familia`

## H5 · `patrocinio.py` documenta un fichero que no existe

> **ARREGLADO** · 6-sep.

Su docstring dice:

> Los tres niveles y lo que cada uno recibe salen de
> `contenido/patrocinio.json`, que se edita sin tocar código.

`contenido/` tiene dos ficheros: `campana.json` y `prensa.json`. Los niveles
están en el código, en `NIVELES`, línea 35. Quien quiera cambiar qué recibe un
patrocinador buscará un JSON que no está.

`comando: ls contenido/ + grep -n NIVELES patrocinio.py`

## H6 · 474 frases de contenido viven dentro del código

De 490 cadenas de tres o más palabras, sólo 16 son ayudas de CLI. Las otras
474 son texto que sale impreso en la pieza, repartido así:

```
revista.py 111 · correo.py 52 · serie.py 46 · campana.py 26
revista_reporte.py 25 · deck.py 25 · impreso.py 23 · movimiento.py 22
```

Contra dos ficheros de contenido externo. Cambiar una frase de la revista es
editar Python; y quien las escribe no es quien programa.

`ESTANDARIZAR-salidas.md` §1.6 medía 222 con menos motores.

`comando: recorrer el AST y contar ast.Constant de tipo str con >=3 palabras`

## H7 · Ocho maneras de decir «sácamelo todo»

| bandera | motores |
|---|---|
| `--demo` | actividad · cita · deck · patrocinio · postevento |
| `--todos` | correo · impreso · movimiento_video · serie · video |
| `--todas` | campana · perfil · senal |
| `--kits` | aliado |
| `--pliego` | revista |
| `--semana` | calendario |
| `--muestras` / `--piezas` | movimiento |
| ninguna | prensa |

Es el §1.5 de `ESTANDARIZAR-salidas.md`, sin cerrar. Cuesta poco y se nota
cada vez que se usa el sistema desde fuera.

## H8 · `campana.py` es el único motor sin carpeta

> **ARREGLADO** · 6-sep.

106 PNG sueltos en la raíz de `_salida/`; los otros 19 motores escriben en su
subcarpeta. Es la familia más grande del sistema y la única desordenada.

`comando: ls _salida/*.png | wc -l`

## H9 · Nueve motores producen la misma medida y nada decía cuál usar

| medida | motores que la producen |
|---|---|
| 1080×1350 | **9** |
| 1080×1920 | 8 |
| 1080×1080 | 8 |

Y dos de esos nueve no producen piezas publicables: `encuadre.py` devuelve un
insumo y `movimiento.py` saca muestras para comparar.

Es el hallazgo que motiva `USOS.md`, escrito hoy: la decisión no la da el
formato, la da de quién es el mensaje.

## H10 · La puerta del index cuenta 19 motores y hay 20

> **ARREGLADO** · 6-sep.

`auditar_index.py → MOTORES` lista 19 ficheros. Falta `logo_ia_media.py`, que
produce las 5 piezas de `_salida/ia-media/` y que **sí tiene ramal propio** en
`auditoria.py` (`audita_ia_media`). El index publicado, por tanto, declara un
motor menos de los que hay.

Es de una línea, pero cambia una cifra que ya está publicada en el sitio.

`comando: grep -n MOTORES auditar_index.py + ls *.py`

---

## Lo que propongo, por coste

### Hecho el 6-sep-2026

| | qué se hizo | cierra |
|---|---|---|
| ✓ | La agenda de semana se llama `agenda-semana--*`: **0 colisiones** | H3 |
| ✓ | `contenido/patrocinio.json` existe y se lee, con caída al código si falta | H5 |
| ✓ | `campana.py` escribe en `_salida/campana/`: **0 PNG en la raíz** | H8 |
| ✓ | `logo_ia_media.py` en `MOTORES` y el index al día | H10 |
| ✓ | Los dos Partners donde faltaban: `cita.py`, `deck.py`, `impreso.py`, `movimiento_video.py`, y el endcard de `video.py` deja de repartir «host + socios» | — |

### Pendiente, por coste

| | arreglo | cuesta | cierra |
|---|---|---|---|
| 1 | Ramal de auditoría para MP4, PDF, HTML, ICS y TXT | medio | H1 |
| 2 | Una sola bandera `--todo` en los motores, conservando las viejas | bajo | H7 |
| 3 | Ramal propio para `aliados` (192 piezas, 3 comprobaciones) | medio | H4 |
| 4 | Sacar el texto de `revista.py` y `correo.py` a JSON | alto | H6 |
| 5 | PDF con texto real en vez de imágenes | alto | H2 |

Los cinco pendientes no están hechos: qué se arregla de ellos lo decides tú.
El 5 es el más caro y el que más cambia — obliga a rehacer el motor de página
con texto vectorial en vez de PIL.

⚠️ Las cifras de esta auditoría se midieron con 435 piezas. Mientras se
escribía, otra sesión añadió `pulso_musica.py` y sus salidas: hoy son **440
piezas y 21 motores**. Los porcentajes se mueven un punto; los hallazgos no.
