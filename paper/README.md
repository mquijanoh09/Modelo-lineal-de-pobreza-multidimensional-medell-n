# Paper final — Optimización 1

Compilar: `latexmk -pdf main.tex` dentro de `paper/` (o subir la carpeta a Overleaf).
Lo pendiente sale en **rojo** en el PDF; para entregar, poner `\borradorfalse` en `main.tex`.

## Reglas para editar los dos a la vez

1. **Cada quien edita solo sus archivos.** El responsable está en la primera línea de cada `.tex`.
   Así casi nunca hay conflictos de git.
2. **Las cifras van en `cifras.tex`**, cada una con el CSV de donde sale. Nunca se escriben a mano en el texto.
3. **Notación única:** la de `notacion.tex` y la Tabla 1 (`secciones/04_notacion_comun.tex`). Si hace falta
   un símbolo nuevo, se agrega ahí.
4. Para dejar un comentario al otro dentro del texto: `\nota{Martín}{...}` o `\nota{Jerónimo}{...}`.
5. `git pull` antes de empezar y commits pequeños. Si hay conflicto, lo resuelve el último que hace commit.

## Quién escribe qué

| Archivo | Martín | Jerónimo |
|---|:-:|:-:|
| 01 Introducción · 02 Literatura · `refs.bib` | ✔ | |
| 03 Datos, IPM y línea base · Apéndice C (costos) | ✔ | |
| 05 Modelos 1 y 2 · 09 Resultados M1/M2 | ✔ | |
| 04 Notación común y jerarquía de información | | ✔ |
| 06 Modelo 3 · 07 Modelo 4 · 08 Diseño experimental | | ✔ |
| 10 Resultados M3/M4 · 11 Comparación de los 4 modelos · 12 Discusión | | ✔ |
| Apéndice A (Lin 1–5 Martín, Lin 6–10 Jerónimo) · Apéndice B (desviaciones) | ✔ | ✔ |
| 00 Resumen · 13 Conclusiones | ✔ | ✔ |

## Plan hasta la entrega (martes 10-nov)

| Cuándo | Martín | Jerónimo |
|---|---|---|
| **Dom 8, tarde y noche** | Leer este README; empezar 02 Literatura (buscar 10–15 fuentes) | 04 Notación común + 06 Modelo 3 |
| **Lun 9, mañana** | 03 Datos + 05 Modelos 1 y 2 (a partir de `docs/informe_modelo1.md` y `formulacion_*.md`) | 07 Modelo 4 + 08 Diseño experimental; congelar cifras M3/M4 en `cifras.tex` y copiar figuras |
| **Lun 9, 12 m — punto de control** | **Subir las cifras de M1/M2 del escenario común** | Revisar que la notación de 05 coincida con la Tabla 1 |
| **Lun 9, tarde** | 09 Resultados M1/M2 + 01 Introducción + Apéndice C | 10 Resultados M3/M4 + 11 Comparación |
| **Lun 9, noche** | Cerrar 02 Literatura | 12 Discusión + Apéndices A y B; juntos: 13 Conclusiones |
| **Mar 10, mañana** | Juntos: 00 Resumen y revisión final (cifras contra CSV, notación, referencias, sin rojo), `\borradorfalse` y entrega | |

**Plan B por si las cifras de M1/M2 no llegan el lunes a las 12 m:** la comparación usa
`resultados/m34/info_perfecta_comun.csv` como techo de información perfecta y se declara en 08.

**Si la profe da más tiempo,** lo que se pasa para después es: profundizar la literatura, la figura
conceptual de la escalera de información y las sensibilidades extra. La versión del martes tiene que
estar completa aunque sea corta.
