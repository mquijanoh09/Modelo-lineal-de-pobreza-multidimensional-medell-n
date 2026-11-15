# Plan para integrar los Modelos 3 y 4 al paper

14 de noviembre de 2026 · Martín Quijano Hoyos · para Jerónimo

## 1. Objetivo

El paper de los Modelos 1 y 2 ya tiene la estructura de Hamie et al. (2024). Este plan dice qué debe entregar Jerónimo para que los Modelos 3 y 4 se intercalen en ese borrador sin reescribirlos. La idea es simple: si su documento usa los mismos títulos de sección, la misma notación y las mismas convenciones de tablas y figuras, integrarlo consiste en pegar cada bloque en su lugar y renumerar.

El documento base es el borrador de Martín (https://claude.ai/artifact/W58ReiYiJecLY7uc9nsC9K). El LaTeX de la rama paper-12nov no se usa como base. Por eso las secciones 01, 02, 03, 05 y 09 de ese LaTeX y sus 16 marcas \pendiente ya no hacen falta: esa parte está escrita en el borrador.

## 2. Qué debe entregar Jerónimo

| Archivo | Contenido |
| --- | --- |
| `M34_para_paper.md` | Todo el texto de los Modelos 3 y 4, en Markdown y en español, organizado con los títulos de la sección 3 de este plan |
| `figuras_m34/*.png` y `*.py` | Cada figura en PNG a 300 dpi, con el script que la genera |
| `datos_m34/*.csv` | El CSV de origen de cada tabla y de cada figura |
| `cifras_m34.csv` | Una fila por cifra citada en el texto: cifra, valor, archivo de origen y columna. Es el equivalente de su `cifras.tex` |

Se pide Markdown porque el borrador lo importa directamente, incluidas las tablas. Si Jerónimo prefiere seguir en LaTeX, el texto se puede convertir, pero las ecuaciones y las tablas habría que revisarlas a mano.

## 3. Dónde va cada pieza

El documento de Jerónimo debe tener exactamente estos títulos, en este orden. Cada bloque se pega en la sección del borrador que lleva el mismo nombre.

| Sección del paper | Qué aporta Jerónimo |
| --- | --- |
| Resumen | Una o dos frases con el resultado principal de los Modelos 3 y 4 (el precio de la información) |
| 1. Motivación | Un párrafo sobre por qué importa la información individual para focalizar |
| 2. Escenarios de política modelados | Sus supuestos y salvedades propios (sorteo R, celdas de focalización, réplicas de Monte Carlo); las subsecciones «Modelo 3» y «Modelo 4» con la misma plantilla de los Modelos 1 y 2 (qué sabe el Estado, qué decide y qué se fija); y las columnas de los Modelos 3 y 4 para la Tabla 1, con las mismas 11 filas y la misma escala S, N o Parcial con una justificación breve |
| 3. Métodos empíricos | Las subsecciones «Modelo 3: formulación» y «Modelo 4: formulación», con conjuntos, parámetros, variables, función objetivo y restricciones, en el mismo orden que el Modelo 1. Además, una subsección nueva, «Diseño de la comparación de los cuatro modelos», con lo que entra y lo que no, los dos criterios, las tres reglas y el número de réplicas (especificación del 12-nov, secciones 3 y 4) |
| 3. Resolución y verificación | Las validaciones con un hogar por celda (11/11) y el resumen de la auditoría del 14-nov |
| 4. Resultados principales | Una subsección nueva, «Comparación de los cuatro modelos», que va después de la Figura 9 (ver la sección 5 de este plan) |
| 5. Discusión | Uno o dos párrafos sobre el precio de la información y las limitaciones de los Modelos 3 y 4. Martín los integra con la discusión existente |
| Apéndice 1 | La linealización propia de los Modelos 3 y 4 (cortes y tangentes) y sus tablas de parámetros |
| Apéndice 2 | Sus sensibilidades: meta global, r = 0, k y u = 1, si se reportan |
| Referencias | La lista completa de lo que cita, con autor, año, título y enlace |

## 4. Convenciones que debe respetar

**Redacción.** Español, registro académico, frases cortas y completas. Sin guiones largos ni flechas.

**Notación.** La misma del borrador, escrita en Unicode y no en LaTeX: pᵢ = HSᵢ · HWᵢ (personas que representa el hogar), cᵢ⁰ (puntaje inicial), sᵢ (puntaje final), yᵢ = 1 si el hogar sale de la pobreza, xᵢⱼ (intervención), qᵢ (severidad), m (meta de reducción de M0), r (tasa mínima de salida por zona), ρ (techo de severidad) y θ (cobertura de un par indicador y celda). Si su código usa b1ᵢ, en el texto se escribe yᵢ. Cualquier símbolo nuevo se define la primera vez que aparece.

**Números.** Punto decimal y coma de miles, como en el resto del paper: 0.036 y 87,034, no 0,036 ni 87.034. Porcentajes con espacio (85.1 %). Dinero en pesos de 2025 y en «mil millones» (por ejemplo, $16.1 mil millones).

**Zonas.** Siempre el total de Antioquia y las tres zonas de P3, con estos nombres: cabeceras, centros poblados y rural disperso.

**Numeración provisional.** Tablas, figuras y ecuaciones con etiquetas provisionales (Tabla M34-1, Figura M34-1, ecuación M3.1). La numeración definitiva se pone al integrar, porque depende de dónde quede cada pieza.

**Tablas.** Cada tabla lleva título, un párrafo antes que diga qué es y cómo se lee, y debajo una nota con la fuente (el CSV) y lo que haga falta aclarar.

**Figuras.** Cada figura lleva título, la imagen, tres párrafos (Cómo se lee, Qué se observa, Interpretación) y una línea de fuente con el CSV. Colores: Modelo 1 en azul #2a78d6 y Modelo 2 en naranja #eb6834, como en la Figura 9. Para el Modelo 3, el Modelo 4 y el placebo se propone usar tres colores fijos y distintos de esos dos en todas las figuras.

## 5. Qué debe calcular y reportar

La mayor parte ya está corrida. Lo que sigue es lo que debe quedar en tablas y CSV finales.

**Criterio de costo, meta de M0 en cada zona (comparación principal).**

1. Las 15 metas del 2 al 30 %, con 100 réplicas para el Modelo 3, el Modelo 4 y el placebo, todas con el mismo sorteo R por réplica.
2. Para cada meta: costo mediano e intervalo entre réplicas, y el precio de la información E_X(m) / E_M2(m), usando como referencia el Modelo 2 sin E-7 con meta por zona.
3. El porcentaje de réplicas en que el Modelo 4 cuesta menos que el Modelo 3.
4. Por zona: el gasto y los valores finales de H, A y M0. Esto es necesario porque la pregunta de investigación es sobre H: hay que mostrar que H también baja en los Modelos 3 y 4.
5. Una figura de costo contra meta, con las cinco curvas (Modelo 2 de referencia, Modelo 3, Modelo 4, placebo y, si aplica, Modelo 1).

**Criterio de presupuesto fijo (resultado sobre equidad).**

1. Para B = 2, 5, 10, 25, 50 y 100 mil millones: la fracción de réplicas factibles con r_B y con r_B y ρ_B (hoy es 0 % en todas). Se reporta como resultado, no se descarta.
2. La tabla del piso máximo garantizable (r_max) para información perfecta, Modelo 3, Modelo 4 y placebo, con la corrección de la auditoría: la infactibilidad es aritmética solo con B ≥ 25.
3. Las personas que salen con r = 0 en los cuatro modelos, como sensibilidad, para poder comparar H.

**Verificación.** El resumen de las validaciones con un hogar por celda y de la auditoría del 14-nov, en un párrafo.

## 6. Lo que Martín debe resolver antes

1. Responder la sección 6 de RESPUESTA_JERONIMO_12NOV.md. r_B, ρ_B y el Modelo 2 con meta por zona ya se verificaron en el computador de Martín el 13-nov y coinciden. Mientras no lo confirme por escrito, Jerónimo los trata como provisionales.
2. Confirmar el formato de entrega (Markdown recomendado).
3. Decidir cómo se conecta la comparación con el caso base. El paper usa B = $424 mil millones, pero la comparación llega hasta B = $100 mil millones y se corre sin E-7 ni SevEdu. Hay dos caminos: agregar valores de B cercanos al caso base, o dejar el rango actual y explicar en una frase por qué la comparación usa otra versión del Modelo 1. La decisión es de Martín.
4. Enviarle a Jerónimo este plan y el borrador exportado, para que lo use como modelo de estilo.

## 7. Cómo se integra cuando llegue

1. Se revisan las cifras contra los CSV, por muestreo.
2. Se insertan los bloques en el borrador, subrayados, sección por sección y con el visto bueno de Martín.
3. Se renumeran tablas, figuras y ecuaciones.
4. Se rehace la Tabla 1 con cuatro columnas.
5. Se actualizan el resumen, la motivación y la discusión, y se completa el glosario EN–ES.
