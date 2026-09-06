# Sistema de diseño · Semana Global de Emprendimiento · República Dominicana

Motor que compone las piezas de la campaña **y se niega a sacar una que
incumpla**. Fundación Enlata e IAvanza son los dos Partners de GEW en
República Dominicana; IA Media firma la cobertura.

Sistema v1.0.0 · 37 ficheros · código MIT, marca no — ver [LICENCIAS.md](LICENCIAS.md)

## Qué hace

12 motores producen piezas sociales, flyers de actividad, citas,
frames y endcards de vídeo, carruseles y cuentas atrás, kits para 48 aliados,
credenciales y roll-ups, piezas de perfil y una revista de recap de 32 páginas
con 23 tipos de página. 7 herramientas comprueban que lo que
sale está bien.

Todo sale de **`tokens/tokens.json`**, que es la fuente de verdad, y cada valor
trae de dónde salió. Lo que no está medido está marcado como no medido.

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

## Lo que le falta

Está en `LEEME.md` y en el `Estado` de `index.html`. Lo principal: el perfil
ICC de la imprenta, y cuál de las cuatro fuentes de cifras de GEN se cita —
porque se contradicen entre sí.

## Para usarlo con tu marca

Pon tu logotipo en `logo/` y tu tipografía en `fuentes/` (ninguna de las dos
viaja aquí, ver [LICENCIAS.md](LICENCIAS.md)), ajusta `tokens/tokens.json` y
corre `python3 entorno.py`, que te dirá qué falta.
