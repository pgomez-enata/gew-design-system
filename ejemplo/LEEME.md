# Activos de ejemplo

El sistema no lleva la marca real: el logotipo de la Semana Global de
Emprendimiento es de la Global Entrepreneurship Network, las marcas de los
socios son de cada uno, VAG Rounded Std es una tipografía licenciada y las
fotografías son de eventos con gente a la que nadie preguntó. Nada de eso se
redistribuye.

Lo que hay aquí es un juego **de marcador**, para que el motor arranque sin
más y se pueda ver qué hace:

| | |
|---|---|
| `logo/` | Un lockup con un anillo **liso** —a propósito: no imita la rueda de GEN— y socios inventados. |
| `fuentes/` | **Poppins**, con licencia SIL Open Font (ver `OFL-Poppins.txt`). Se llaman `VAGRoundedStd*` porque es lo que el motor busca; no son VAG Rounded, y se nota. |
| `fotos/` | Imágenes sintéticas: bandas grises que dicen «IMAGEN DE EJEMPLO». |

**Cómo funciona.** Si un activo no está en `logo/` o `fuentes/`, el sistema lo
busca aquí. No hace falta configurar nada. Cuando pongas los tuyos en su sitio,
mandan los tuyos.

`python3 entorno.py` te dice cuáles está usando de ejemplo y cuáles son tuyos.
