# Qué salida usa cada caso · GEW · RD

El sistema tiene **21 motores de producción** y saca 440 piezas de imagen más
119 ficheros de otros tipos. Lo que no tenía es este documento: **cuál de
todos usar**.

Medido el 6-sep-2026. Cada tabla se puede volver a sacar con el comando que
lleva al pie.

---

## 0 · La pregunta que decide, antes que el formato

Nueve motores producen la misma medida de 1080 × 1350. Ocho producen
1080 × 1920. **El formato no decide nada**: decide quién manda en la pieza.

| Si el mensaje es de… | manda arriba | GEW aparece como | motor |
|---|---|---|---|
| la campaña nacional | GEW · RD | marca primaria | `campana.py` · `serie.py` |
| una actividad concreta | el organizador | sello *Official Activity* | `actividad.py` |
| una persona | su cara | lockup en cabecera | `cita.py` |
| un aliado | su logo | sello de pertenencia | `aliado.py` |
| quien paga | su logo, por nivel | marco de la campaña | `patrocinio.py` |
| los resultados | la cifra | lockup en cabecera | `postevento.py` |

Esa columna —**de quién es el mensaje**— es la que hay que contestar primero.
Contestada, el formato sale solo del canal donde se publica (§4).

Regla corta: *si el logo que va arriba a la izquierda no es el lockup
dominicano de GEW, no es una pieza de campaña.*

---

## 1 · Los nueve tipos de arte

Cada tipo tiene **lo que determina su uso** (la pregunta que hay que
contestar para elegirlo) y **la prueba** (cómo se sabe que salió bien).

### 1 · Arte de campaña — `campana.py`, `serie.py`

Habla la campaña, no un evento. Enlata e IAvanza van abajo, como Partners.

- **Lo determina**: el mensaje sirve aunque no haya ninguna actividad ese día.
- **Cuál de los dos**: una lámina suelta → `campana.py`. Varias que se leen
  seguidas → `serie.py` (carrusel, cuenta atrás, agenda).
- **Salidas**: 7 formatos de campaña × 6 audiencias × 15 piezas de mensaje.
- **La prueba**: 10,4 comprobaciones por pieza, la cobertura más alta del
  sistema. El pulso bajo la cabecera y el lockup arriba se comprueban en píxel.

Las 6 audiencias son las de la guía de GEN: `publico` · `nextgen` ·
`ignorados` · `inquieto` · `estabilidad` · `problema`. No son públicos
demográficos: son **por qué alguien no ha emprendido todavía**. Elegir mal la
audiencia se ve más que elegir mal el formato.

### 2 · Arte de actividad — `actividad.py`, `senal.py`, `calendario.py`

Hay una fecha, un lugar y alguien que la organiza.

- **Lo determina**: si al quitar la fecha la pieza deja de tener sentido, es
  de actividad, no de campaña.
- **Las tres variantes de flyer** y cuándo va cada una:
  - `A · panel` — hay retratos de ponentes. La cabecera blanca los sostiene.
  - `B · sangre` — hay UNA foto buena del sitio o del público. Manda la foto.
  - `C · partido` — hay una foto mediana y mucho texto. El panel carbón salva
    la legibilidad.
  - Sin foto usable: A, con los círculos vacíos. Nunca B.
- **Además del flyer**: `senal.py` el día del evento y `calendario.py` para
  que el aliado lo tenga agendado y no «apuntado».
- **La prueba**: `senal.py` no estima, **declara a qué distancia se lee cada
  cartel** (2,5 cm de letra por cada 3 m). Si no se lee desde donde toca, lo
  dice antes de imprimir.

### 3 · Arte de persona — `cita.py`, `encuadre.py`

Una cara y una frase suya.

- **Lo determina**: que la frase sea de alguien con nombre. Una frase de la
  campaña sin autor no es una cita: es `campana.py`.
- **Las dos variantes**: `panel` cuando la foto es buena de cintura para
  arriba; `apilada` cuando la foto es horizontal o el encuadre es difícil.
- **`encuadre.py` no es una pieza, es un insumo**: recorta un retrato al
  criterio del sistema (cabeza entre 1/3,5 y 1/3 del alto, ojos a 0,38, la
  coronilla nunca cortada) y devuelve las medidas. Se pasa antes de `cita.py`
  o de `actividad.py --variante A`.
- **La prueba**: el informe dice cuántas cabezas de alto quedó y dónde
  cayeron los ojos. Sin cara detectada, lo declara — no lo inventa.

### 4 · Arte de tercero — `aliado.py`, `patrocinio.py`

La marca que manda no es nuestra.

- **Lo determina**: ¿aportó dinero? → `patrocinio.py`. ¿Aportó actividad,
  sala, difusión o público? → `aliado.py`.
- **`aliado.py` da tres cosas por aliado**: la pieza que él publica (`somos`),
  el sello para su web y su firma con el HTML ya escrito (`sello`), y la
  carpeta completa con el paso a paso (`kit`). Los 48 salen de una pasada.
- ⛔ **`patrocinio.py` no compone ninguna marca sin `--firmado`.** Sale con el
  nombre en `{{PENDIENTE}}`. No es burocracia: poner un logo antes de tiempo
  ya costó disgustos.
- **La prueba**: el padrón no se teclea, se lee del muro publicado en
  enlata.do/gew, que es la fuente de verdad.

### 5 · Arte en movimiento — `video.py`, `movimiento_video.py`

- **Lo determina**: ¿hay un vídeo grabado debajo? Sí → `video.py` (PNG con
  canal alfa que se superpone). No → `movimiento_video.py` (MP4 que se basta).
- `video.py`: `frame` (marco + sitio para subtítulos) · `lower` (nombre y
  cargo) · `endcard` (tarjeta final, opaca) · `guias` (el frame con las zonas
  de interfaz marcadas, **para el editor, no para publicar**).
- `movimiento_video.py`: `apertura` 3 s · `cuenta` 4 s · `endcard` 5 s.
- **Sin audio, a propósito.** Una pieza de campaña se ve en silencio la mayor
  parte de las veces y la música se pone al montar. El −14 LUFS que se cita
  para YouTube no tiene página oficial de Google.
- **La prueba**: H.264 High Profile, MP4, yuv420p —lo que YouTube publica— y
  ≥540×960 con ≥516 kbps, el mínimo documentado de TikTok.

### 6 · Arte de imprenta — `impreso.py`, `revista.py`, `revista_reporte.py`

Aquí no hay píxeles sueltos: hay centímetros, dpi y sangrado.

- **Lo determina**: que alguien lo vaya a tocar con la mano.
- `impreso.py`: `credencial` 10×14 cm (en lote desde la lista) · `certificado`
  carta apaisada · `rollup` 85×200 cm · `backdrop` 3×2,4 m.
- `revista.py` + `revista_reporte.py`: 32 páginas grapadas, 8,5×11", 300 dpi,
  23 tipos de página entre los dos.
- ⚠️ **El lockup dominicano no tiene vector** (3377×1173 px de tinta). En gran
  formato eso pone un techo real; el motor avisa cuando el logo se queda corto.
- ⚠️ **El creep**: con 32 páginas y papel de 130 g el desplazamiento llega a
  0,52 mm y se compensa hacia el lomo. Si no se compensa, se ve impreso y ya
  no hay marcha atrás.
- **La prueba**: las marcas de corte van en capa aparte (`--marcas`); el arte
  limpio no las lleva.

### 7 · Arte de documento — `correo.py`, `prensa.py`, `deck.py`

Texto que lleva la marca encima, no marca que lleva texto.

- **Lo determina**: el destinatario lo va a leer entero, no a mirar.
- `correo.py`: 4 envíos —`invitacion`, `confirmacion`, `recordatorio`,
  `cierre`— en HTML y en texto plano.
- `prensa.py`: la nota y el bloque de créditos que la guía de GEN obliga.
- `deck.py`: 7 tipos de lámina a 1920×1080 para el ponente.
- **La prueba**: Gmail recorta a partir de 102 KB de HTML y el motor lo mide;
  el Outlook clásico usa el motor de Word, así que se maqueta con `<table>`;
  el deck respeta el 10 % de margen y el título dentro del 80 % central,
  porque el proyector recorta.

### 8 · Arte de cierre — `postevento.py`

Gracias y los números. Es la pieza que más se comparte, porque la gente se
busca en las cifras.

- **Lo determina**: el evento ya pasó y hay datos.
- `actividad` para que lo publique el aliado · `semana` para el total.
- ⚠️ **Las cifras van como `{{N}}` mientras no existan.** Un recap con un
  número inventado es peor que uno con un hueco: el hueco se rellena y el
  número falso se cita en la propuesta del año que viene.
- **La prueba**: el motor cuenta cuántos huecos quedan y lo dice.

### 9 · Identidad permanente — `perfil.py`, `logo_ia_media.py`

Se pone una vez y se queda. **No pasa por la retícula de campaña.**

- **Lo determina**: que la plataforma publique una ficha oficial. Sólo tres
  la tienen: portada de canal de YouTube (2560×1440, y sólo 1546×423 se ve en
  todos los dispositivos), portada de página de LinkedIn (1512×256) y logo de
  página (400×400).
- El 1080×1350 de Instagram **no** es norma: Meta no publica especificación
  para publicaciones orgánicas. Es consenso de terceros y así está declarado.

---

## 2 · Del encargo a la salida

| Lo que se pide | Comando |
|---|---|
| «Anuncia la semana» | `campana.py --audiencia publico --pieza 0` |
| «Ponlo en historias» | `campana.py … --formato historia` |
| «Súbelo como anuncio» | `campana.py … --formato historia-ads` |
| «Que se vea al compartir el enlace» | `campana.py … --formato enlace` |
| «Miniatura del vídeo» | `campana.py … --formato yt-miniatura` |
| «Todo lo de la campaña» | `campana.py --todas` |
| «Un carrusel que explique X» | `serie.py --tipo carrusel --guion x.json` |
| «Cuenta atrás» | `serie.py --tipo cuenta` |
| «La programación» | `serie.py --tipo agenda --dia` |
| «Flyer del taller del 18» | `actividad.py --variante A --titulo … --fecha …` |
| «Que se lo agenden» | `calendario.py --actividad "Taller" --dia 18` |
| «Carteles para la sede» | `senal.py --todas` |
| «Un cartel de sala» | `senal.py --tipo sala --texto … --detalle …` |
| «La frase de la fundadora» | `cita.py --cita … --nombre … --foto x.jpg` |
| «Las fotos están descuadradas» | `encuadre.py foto.jpg` |
| «Que los aliados publiquen» | `aliado.py --kits` |
| «Lo de un aliado suelto» | `aliado.py --aliado "Nombre"` |
| «Firmó un patrocinador» | `patrocinio.py --nivel principal --marca … --logo … --firmado` |
| «Rótulo con el nombre del ponente» | `video.py --tipo lower --nombre … --cargo …` |
| «Marco para el vídeo» | `video.py --tipo frame --formato vertical` |
| «Cortinilla de entrada» | `movimiento_video.py --tipo apertura` |
| «Gafetes» | `impreso.py --tipo credencial --lista personas.txt` |
| «Certificados» | `impreso.py --tipo certificado --nombre …` |
| «Roll-up» / «fondo de escenario» | `impreso.py --tipo rollup` / `--tipo backdrop` |
| «La revista» | `revista.py --pliego --pdf` |
| «Escribir a los aliados» | `correo.py --todos` |
| «Nota de prensa» | `prensa.py` |
| «Plantilla para el ponente» | `deck.py --guion charla.json --pdf` |
| «Cerrar con las cifras» | `postevento.py --alcance semana` |
| «Portadas de los canales» | `perfil.py --todas` |

---

## 3 · Los tres sitios donde hoy se duda

### 3.1 · Nueve motores hacen 1080 × 1350

| medida | motores |
|---|---|
| 1080×1350 | actividad · aliado · campana · cita · encuadre · movimiento · patrocinio · postevento · serie |
| 1080×1920 | los mismos menos encuadre y patrocinio, más video |
| 1080×1080 | idem |

Se desata con la tabla del §0. Y dos de esos nueve **no producen piezas
publicables**: `encuadre.py` devuelve un recorte (insumo) y `movimiento.py`
saca muestras del elemento para comparar. Publicar cualquiera de las dos es
un error.

`comando: python3 -c "…Image.open…"` sobre `_salida/`, ver §5.

### 3.2 · Tres formatos son 1080 × 1920 y no son lo mismo

| formato | zona segura | pie | cuándo |
|---|---|---|---|
| `historia` | 269 – 1670 | franja al filo | historia orgánica y estado de WhatsApp |
| `historia-abierta` | 269 – 1670 | franja al filo, logos en blanco sobre carbón | cuando la banda blanca corta la foto |
| `historia-ads` | 269 – **1248** | dentro | **sólo** si se va a pagar |

El 1248 no es capricho: es el 35 % inferior que Meta reserva al CTA **en las
specs de anuncios**. Usarlo en orgánico regala 422 px de alto. Y al revés
—subir `historia` como anuncio— mete el remate debajo del botón.

⚠️ Meta **no documenta zona segura para historias orgánicas**. El perfil
orgánico es criterio del sistema, no norma citada.

### 3.3 · `video.py` o `movimiento_video.py`

PNG con alfa que se monta encima de un vídeo → `video.py`.
MP4 que se publica solo → `movimiento_video.py`.
`--tipo guias` no se publica nunca: es para el editor.

---

## 4 · El formato, una vez elegido el motor

| Dónde se publica | formato |
|---|---|
| Feed de Instagram · LinkedIn | `retrato` 1080×1350 |
| Historias · estado de WhatsApp | `historia` 1080×1920 |
| Historias pagadas | `historia-ads` |
| LinkedIn · Facebook · WhatsApp | `cuadrado` 1080×1080 |
| Vista previa de un enlace | `enlace` 1200×627 |
| Miniatura de YouTube | `yt-miniatura` 1280×720 |
| Reel · TikTok · Short | `vertical` 1080×1920 |
| Proyector | 1920×1080 |
| Imprenta | centímetros y dpi, nunca píxeles |

Cada uno lo declara el propio `FORMATOS` de `campana.py`, en su campo `uso`.

---

## 5 · Las marcas: quién aparece, dónde y con qué rótulo

Tres bloques, rótulos bilingües, y viven en una sola función —
`campana.marcas()` — para que los motores no inventen cada uno la suya.

| bloque | rótulo | quién | cuándo |
|---|---|---|---|
| 1 | `PARTNERS` | **Fundación Enlata + IAvanza** | **siempre**, en toda pieza del movimiento |
| 2 | `PATROCINADORES · SPONSORS` | quien firma | el hueco **se dibuja aunque esté vacío** |
| 3 | `COBERTURA · COVERAGE` | **IA Media** | sólo en piezas de cobertura y de cierre |

### 5.1 · Los Partners son permanentes

Enlata e IAvanza son **los dos Partners** de GEW · RD. No hay anfitrión ni
socio principal: son dos, van juntos y van siempre. Esto no es una opción del
motor — la lista canónica es `campana.PARTNERS` y quien la necesite la importa
de ahí, nunca escribe la ruta a mano.

⚠️ El sitio donde más se rompía era en los valores por defecto: un motor que
pone «Enlata» como *organizador* o como *host* y deja a IAvanza fuera está
usando un reparto que ya no existe. El 6-sep-2026 se corrigieron dos:
`cita.py` ponía a Enlata sola en el papel de organizador, y el endcard de
`video.py` componía «host + socios».

### 5.2 · El hueco de patrocinadores se dibuja vacío

Es deliberado: un espacio marcado *espacio reservado* le dice a quien mira la
pieza que ese sitio existe y se puede comprar. Se rellena con `--logo` cuando
hay acuerdo, y ⛔ **nunca antes de que esté firmado** (`patrocinio.py` lo
impide: sin `--firmado` sale `{{PENDIENTE}}`).

### 5.3 · IA Media va en cobertura, y sólo ahí

IA Media es la unidad de contenido audiovisual, no un partner ni un
patrocinador: por eso tiene su propio bloque, en **segunda fila y más
pequeño**. Aparece en el endcard de vídeo —el PNG y el MP4—, en el
post-evento y en los créditos de la revista. No aparece en una pieza de
campaña, porque ahí no hay nada que cubrir.

Medido sobre las 440 piezas: el color de IA Media sale en `video` (los 3
endcard), `postevento` (las 6), `revista` (la página de créditos) y
`movimiento` (las muestras del elemento). En ninguna otra. Y en el MP4,
comprobado sobre el **último fotograma extraído del vídeo montado**, no sobre
el frame en memoria.

### 5.4 · Qué lleva cada motor

| motor | Partners | Patroc. | Cobertura | forma |
|---|---|---|---|---|
| `campana.py` | ✓ | ✓ | — | banda completa |
| `serie.py` | ✓ | ✓ | — | banda completa |
| `actividad.py` | ✓ | ✓ | — | banda completa |
| `postevento.py` | ✓ | ✓ | **✓** | banda completa |
| `video.py` · endcard | ✓ | ✓ | **✓** | banda completa |
| `deck.py` · cierre | ✓ | ✓ | — | banda completa |
| `impreso.py` · rollup, backdrop | ✓ | ✓ | — | banda completa |
| `revista.py` · créditos | ✓ | ✓ | **✓** | a su retícula |
| `cita.py` | ✓ | — | — | los dos logos en el pie |
| `deck.py` · portada | ✓ | — | — | los dos logos, sin rótulo |
| `impreso.py` · certificado | ✓ | — | — | los dos logos bajo las firmas |
| `movimiento_video.py` · endcard | ✓ | — | **✓** | dos filas, sin rótulo de patrocinio |
| `impreso.py` · credencial | ✓ | — | — | los dos logos agrupados con el pie |

### 5.5 · Lo que NO lleva Partners, y por qué

| motor | por qué |
|---|---|
| `aliado.py` | la pieza es del aliado: manda su logo y lleva el sello de pertenencia |
| `patrocinio.py` | manda la marca que firma, con su nivel |
| `perfil.py` | portadas de canal: identidad permanente, no pieza de campaña |
| `senal.py` | señalética de orientación; lleva el lockup y nada más |
| `video.py` · frame, lower, guias | son capas transparentes que se montan sobre metraje |
| `encuadre.py` | devuelve un recorte, no una pieza |
| `correo.py` · `prensa.py` · `calendario.py` | los créditos van en texto, no en logo |

Las dos que estaban abiertas las cerró Piero el 6-sep: la **credencial** lleva
los dos logos agrupados con el pie —tenía 566 px de aire en el centro y
sueltos ahí se leían como parte del bloque del nombre—, y el **MP4** lleva
también IA Media, en segunda fila con su rótulo.

---

## 6 · Cómo se vuelve a medir todo esto

```bash
python3 auditoria.py                    # las piezas contra las reglas
python3 manifiesto.py                   # qué se produjo
python3 entorno.py                      # la máquina, antes de empezar
```
