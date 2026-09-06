# El movimiento: elemento distintivo, marcas y IA Media

Decidido por Piero el 5-sep-2026. Lo que sigue está construido y medido.

---

## 1 · El elemento: **el pulso**

Sale del propio logo, medido: recorriendo el radio medio del anillo GEW·RD cada
0,05° salen **39 segmentos con 30 colores** y sus anchos angulares reales, de 1°
a 32,75°, con 7,7 % de aire. El pulso usa esos anchos como altura de barra: los
segmentos anchos del anillo dan las barras altas. El ritmo no es decorativo,
es la geometría del logo.

Está en `datos/anillo-segmentos.json`. La cinta y la estela se quedan en
`movimiento.py` como constancia de lo que se comparó, no como opciones vivas.

**⛔ Lo que sigue prohibido**: un arco de la rueda. Sería el logo recortado.

**⚠️ Los 30 colores del anillo dominicano no son los del SVG global.** 32 de los
39 segmentos están a más de 24 de distancia de `color.marca.rueda`. Para
cualquier pieza que ponga un color junto al anillo RD manda la lista medida.

---

## 2 · Dónde y cómo se nombran

Tres bloques, rótulos bilingües, en dos filas:

```
PARTNERS                       PATROCINADORES · SPONSORS
[Fundación Enlata] [IAvanza]   [espacio reservado]

COBERTURA · COVERAGE  [iA MEDIA]
```

| Bloque | Quién | Cuándo |
|---|---|---|
| **PARTNERS** | Fundación Enlata · IAvanza | siempre |
| **PATROCINADORES · SPONSORS** | — | cuando haya acuerdo firmado |
| **COBERTURA · COVERAGE** | IA Media | sólo cobertura: video, recap, galería, revista |

`PARTNERS` se escribe igual en los dos idiomas, así que sólo los otros dos
llevan las dos palabras.

**El hueco de patrocinadores se dibuja aunque esté vacío.** Si se deja sin
reservar, al llegar el primer patrocinador hay que recomponer la pieza entera.
Y sigue en pie la regla: **ninguna marca se imprime antes de que el acuerdo
esté firmado** — Banreservas está en negociación, no cerrado.

### Resuelto: los dos son Partners

Confirmado por Piero el 5-sep-2026. El papel de «National Host» queda retirado
de todo el sistema; `auditar_index.py` falla si reaparece atribuido a Enlata.
La «guía de National Hosts» sigue siendo el nombre del documento de GEN y se
cita como tal.

---

## 3 · El logo de IA Media

No lo inventé: IAvanza ya tiene un patrón de submarca —las 13 comunidades— y
está medido en su `tokens.json`. IA Media se construye igual:

| | |
|---|---|
| cuerpo del texto | 1,0759 × alto del isotipo |
| cap-height | 0,7393 × alto del isotipo |
| solape del texto | −0,024 × ancho del isotipo (anidado, no colisión) |
| alineación | línea base común, **no** centrado vertical |
| tipografía | Archivo SemiExpanded ExtraBold (OFL), convertida a trazo |
| clearspace mínimo | 1/3 del alto del isotipo |
| tamaño mínimo | 120 px de ancho; por debajo, sólo el isotipo |

Cinco variantes en `logo/socios/`: lockup a color, en blanco, para carbón,
isotipo y isotipo blanco. El SVG no depende de ninguna fuente instalada.

### El color: **#8475FF** — aprobado

Cerrado por Piero el 5-sep-2026. Salió del generador de IAvanza —el mismo que
se usó para IA Human e IA Teachers— con su método: ΔE2000 contra las 13
comunidades más el azul de marca y TESTERS, contraste ≥3:1 sobre blanco y
contra el ink, y croma dentro de la familia.

**Va con ΔE = 15,2 y el umbral de aquella vez fue 20. Se aprobó a sabiendas.**
Con croma de marca (C*≥78) no hay ningún hueco mejor: la rueda ya está llena
con 13 comunidades. Bajando el piso de croma sí aparece un ΔE de 24,7 — pero el
ganador es un caqui apagado, que es justo lo que el propio generador de IAvanza
avisa por escrito que hay que evitar. Croma de marca por delante de distancia
de catálogo.

**Por qué no el azul de marca**: `#0262E5` es **exactamente** el color de
encuentro semanal (ΔE 0) y su contraste contra el ink del nombre es 2,27:1, por debajo
del 3:1 que exige el propio sistema.

**Sobre el carbón de GEW hace falta la variante aclarada.** Ningún color puede
cumplir 3:1 sobre blanco y 3:1 sobre `#4A4A4A` a la vez: las dos bandas de
luminancia no se tocan (≤0,300 y ≥0,3054). Por eso existe
`ia-media-lockup-carbon.svg`, con el isotipo en `#9487FF` — 3,03:1 sobre el
carbón — y la palabra en blanco.

**Su casa definitiva no es este sistema.** El logo es de IAvanza. Vive aquí
para poder usarlo, pero su sitio es `iavanza_design_system/logo/`. Lo muevo
cuando lo apruebes.

---

## 4 · Estado

**Todo cerrado.** El elemento, los rótulos, los tres bloques, el papel de Enlata
y el color de IA Media están decididos, y el pulso y la banda ya viven en los
once motores con sus reglas en la auditoría — no en `movimiento.py`, que se
queda sólo con la lámina comparativa como constancia de lo que se comparó.

Lo único que sigue fuera de nuestra mano:

1. **Mover el logo de IA Media a `iavanza_design_system`**, que es su casa. No
   lo hice solo porque ese sistema tiene su propia puerta, su `_sello.json` de
   hashes y su empaquetador: meterle un logo sin revisarlos puede romperlos.
2. El **perfil ICC de la imprenta** y el gramaje real del papel.
3. Cuál de las **cuatro fuentes de cifras de GEN** se cita.
