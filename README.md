# Sistema de diseño · Semana Global de Emprendimiento · República Dominicana

Motor que compone las piezas de la campaña **y se niega a sacar una que
incumpla**. Fundación Enlata e IAvanza son los dos Partners de GEW en
República Dominicana; IA Media firma la cobertura.

Sistema v1.0.0 · 68 ficheros · código MIT, marca no — ver [LICENCIAS.md](LICENCIAS.md)

## Qué hace

12 motores producen piezas sociales, flyers de actividad, citas,
frames y endcards de vídeo, carruseles y cuentas atrás, kits para 48 aliados,
credenciales y roll-ups, piezas de perfil y una revista de recap de 32 páginas
con 23 tipos de página. 7 herramientas comprueban que lo que
sale está bien.

Todo sale de **`tokens/tokens.json`**, que es la fuente de verdad, y cada valor
trae de dónde salió. Lo que no está medido está marcado como no medido.

## Arranca sin configurar nada

Clona y corre. No lleva la marca real —el logotipo es de la Global
Entrepreneurship Network y VAG Rounded Std es licenciada—, pero sí lleva
**`ejemplo/`**: un lockup de marcador, socios inventados, imágenes sintéticas
y Poppins (SIL Open Font License). Si un activo no está en `logo/` o
`fuentes/`, el sistema lo busca ahí solo.

```bash
git clone https://github.com/pgomez-enata/gew-design-system.git
cd gew-design-system
python3 campana.py --audiencia publico --pieza 0    # ya sale una pieza
```

Cuando pongas tu logotipo en `logo/` y tu tipografía en `fuentes/`, mandan los
tuyos. `python3 entorno.py` te dice cuáles está usando de ejemplo.

## El orden

```bash
python3 entorno.py          # ¿tiene la máquina lo que hace falta?
python3 campana.py --todas  # construir
python3 metadatos.py        # la procedencia, dentro de cada fichero
python3 manifiesto.py       # qué se produjo, con su hash
python3 auditoria.py        # el guardián: 0 = se puede entregar
```

`auditoria.py` sale con código 1 si algo falla. **Una pieza no está terminada
hasta que la auditoría pasa** — no vale el informe del motor que la hizo.

## Lo que hace distinto a este sistema

- **Mide, no estima.** La tinta se mide con la caja real del glifo, no con la
  de la fuente. Los desbordes se cuentan en píxeles. Cada regla devuelve un
  número y lo compara con un umbral.
- **El elemento distintivo sale del logo, medido.** Recorriendo el radio medio
  del anillo cada 0,05° salen 39 segmentos con sus anchos reales; de ahí sale
  «el pulso». Está en `datos/anillo-segmentos.json`.
- **Cada pieza lleva su procedencia dentro**: XMP con campos IPTC 2025.1.
- **Las reglas se prueban en las dos direcciones**: que dejen de marcar lo que
  era falso, y que sigan marcando lo que era real.

## Las capturas de `index.html`

Son **piezas de demostración**: el motor de verdad corriendo, con un lockup de
marcador, socios inventados, imágenes sintéticas y Poppins (SIL Open Font
License) en lugar de VAG Rounded. Los datos son ficticios.

No es maquillaje ni un mockup: es este código produciendo estas piezas. Y es
exactamente lo que puedes hacer tú — poner tu marca en `logo/` y tu tipografía
en `fuentes/` — así que sirve de prueba de que funciona.

## Lo que le falta

Está en `LEEME.md` y en el `Estado` de `index.html`. Lo principal: el perfil
ICC de la imprenta, y cuál de las cuatro fuentes de cifras de GEN se cita —
porque se contradicen entre sí.

## Para usarlo con tu marca

Pon tu logotipo en `logo/` y tu tipografía en `fuentes/` —los de `ejemplo/`
dejan de usarse en cuanto existan los tuyos—, ajusta `tokens/tokens.json` y
corre `python3 entorno.py`, que te dirá cuáles son tuyos y cuáles siguen
saliendo de ejemplo. Ver [LICENCIAS.md](LICENCIAS.md).
