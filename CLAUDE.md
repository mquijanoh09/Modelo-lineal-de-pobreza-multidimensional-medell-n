# Avance general del proyecto — IPM Colombia (rama `Contexto`)

> Actualizado: 1-nov-2026, según las referencias locales (último fetch: 1-nov, 14:40).
> Proyecto final de Optimización 1, EAFIT. Sustentación: noviembre de 2026.
> Este archivo resume cómo va el trabajo de **Jerónimo Vélez** (Modelos 3 y 4) y cómo encaja con
> el de **Martín Quijano** (Modelos 1 y 2). El contexto de datos de Martín está en
> `CONTEXTO_DATOS.md`; el detalle técnico del Modelo 3, en el `CLAUDE.md` de la rama `Modelo3`.

## 1. En una mirada

| Modelo | Información del planificador | Responsable | Estado |
|---|---|---|---|
| 1 y 2 | Perfecta: ve cada hogar | Martín | Reformulación y costos en `CONTEXTO_DATOS.md`; `parametros.py` y `05_conteo_personas.py` por hacer |
| 3 | Solo agregados por zona, con sorteo | Jerónimo | MILP por cortes completo y probado; **falta el Monte Carlo** y decidir el objetivo del caso base |
| 4 | Zona para bienes públicos, clúster para privados, con sorteo | Jerónimo | Clústeres listos y validados; **MILP sin escribir** |

Universo común de los 4 modelos: **Antioquia completa**, 3.732 hogares, 523 pobres, H0 = 9,45 %,
M0 = 0,038684. Los Modelos 3 y 4 simulan la capacidad real del Estado para focalizar: los errores
de inclusión y de exclusión son el resultado de política.

## 2. Cómo ha avanzado el trabajo

**Datos**
- Se empezó con los módulos de la ECV 2023, pero no traen los 15 indicadores calculados.
- Se pasó a la base IPM 2025 del DANE, que aportó Martín; reproduce las cifras oficiales. Costo: no
  hay municipio, así que se descartó Medellín.
- Martín identificó `P3` como la clase urbano/rural. Antioquia urbana dejaba una sola zona y anulaba
  el Modelo 3, por lo que se pasó a Antioquia completa.

**Formulación del Modelo 3**
- La lógica Big-M del apéndice estaba bien, pero la cobertura mezclaba personas y hogares y llegaba
  a 4,81. Eso dejaba el sorteo inerte y convertía M3 en M1. Se corrigió.
- También se corrigieron la meta (MPI_s es M0, no H0), las desigualdades estrictas y el Big-M global.

**Cómputo (hasta el 22-oct)**
- La formulación directa no cerraba en > 200 s en la base completa.
- El hallazgo fue que el Estado elige cuántos, no cuáles: los curados forman un prefijo del orden del
  sorteo. La formulación por cortes pasó de 9.125 a 1.153 binarias y corre en unos 2 s.

**Modelo 4**
- Los clústeres usan solo lo que el Estado observa (tipo Sisbén), no las privaciones: k = 4. Separan
  la pobreza 4,3× sin usarla.
- Partición validada: V = acueducto y alcantarillado por zona; U = los otros 13 por clúster.

**Lo más reciente (31-oct)**
- Subidos a `Modelo3`: `06_modelo3_cortes.py`, `00_verificar_base.py`, `07_clusters.py` (`6f1d024`).
- `cortes.py` separa el mecanismo del objetivo, con cobertura y costo por separado, lo que permite
  usar los costos de Martín y sirve para el Modelo 4 (`16a4e4f`).
- `modelo3_equidad.py` implementa el Modelo 3 con el objetivo de equidad del Modelo 1, usando costos
  provisionales u = 1 (`16a4e4f`).

## 3. Resultados hasta ahora

Modelo 3, objetivo del paper, réplica 0 (no definitivos: falta el Monte Carlo):

| Meta de reducción de M0 | Esfuerzo | H final | Error de inclusión |
|---|---|---|---|
| 5 % | 60,0 | 0,0903 | 41,7 % |
| 10 % | 153,0 | 0,0854 | 62,1 % |
| 20 % | 349,0 | 0,0756 | 68,5 % |

El error de inclusión crece con la ambición de la meta.

**Verificado el 1-nov:** en `origin/Modelo3` pasan `test_cortes.py` (incluido el 153,0 de la meta de
10 %) y la capa 0 de equidad, que reproduce 523 pobres, H0 = 9,45 % y Sev0 = 117.908 de Martín.

**Sin verificar:** con equidad, u = 1 y B = $500 mm, el commit reporta 419.550 personas que salen y
42,6 % del gasto en no pobres. El entorno `opti1` no tiene `highspy`, así que no se pudo reproducir.
No citar esta cifra todavía.

Clústeres del Modelo 4:

| Clúster | Hogares | H |
|---|---|---|
| Adultos sin dependientes | 1.389 | 3,7 % |
| Adultos mayores | 1.038 | 11,8 % |
| Con hijos escolares | 849 | 9,1 % |
| Primera infancia | 456 | 16,1 % |

Parte de esa separación es estructural: atención integral solo aplica a hogares con menores de 5.

## 4. Dónde está cada cosa

| Rama | Qué tiene |
|---|---|
| `main` (`91e7b97`) | Scripts base de Martín: `utils_dane.py`, `02`, `03`, `04` |
| `Contexto` | `CONTEXTO_DATOS.md`, grafo en `graphify-out/perspectiva_equidad/` y este archivo |
| `Modelo3` (`16a4e4f`) | Todo el código de M3 y `07_clusters.py` del Modelo 4 |

Fuera del repo, en la carpeta Opti1: `docs_proyecto/` (bitácora, revisión matemática y decisión de
fuente de datos) y los PDF de selección de variables.

Todavía no existen en ninguna rama: `parametros.py`, `05_conteo_personas.py`,
`03_preparar_antioquia.py`, `m34_08_modelo4.py` y `NOTAS_JERONIMO.md`.

## 5. Respuestas a las preguntas de Martín (borrador)

Corresponden a la sección 8 de `CONTEXTO_DATOS.md`. **Es un borrador: Jerónimo aún no las ha
confirmado ni escrito en "Notas de Jerónimo".**

1. **SevEdu:** sí, pero primero como métrica ex post en el Monte Carlo de M3/M4. El sorteo por niño
   rompe el prefijo por hogar. *A confirmar.*
2. **Objetivo del Modelo 1:** **punto abierto, ver sección 6.** La respuesta redactada decía que M3/M4
   no cambian de objetivo, pero `modelo3_equidad.py` ya prueba el objetivo de equidad.
3. **u_ij = 1 en empleo formal y desempleo:** sí, como sensibilidad, no como caso base.
4. **Inasistencia (3,0/p):** de acuerdo. En la optimización el costo es 3,0/p; el cumplimiento p entra
   solo en el Monte Carlo.
5. **Conteo de no pobres en el mismo 05:** sí, imprescindible para medir el error de inclusión.
   Revisarlo cuando se suba.
6. **`parametros.py` y choque de `05_`:** importar de ahí `IND`, `W` y la semilla. Renumeración
   propuesta con prefijo `m34_`. *A confirmar.*
7. **Costos:** logro educativo = 3 ciclos CLEI (base), 1 ciclo por año (sensibilidad). Acueducto rural
   de $43,7 M *a confirmar* con fuente verificable; BID $9,7 M como sensibilidad baja.

## 6. Decisiones que hay que tomar juntos

1. **Objetivo de M3/M4 y comparación final.** Hay dos opciones en código: min esfuerzo s.a. meta de M0
   (paper) y max personas que salen s.a. presupuesto (equidad, como M1). La decisión define qué se
   compara entre los 4 modelos y conviene cerrarla antes del Monte Carlo.
2. **Solver y tolerancias:** Martín usa HiGHS; 05 y 06 usan CBC. Unificar o reportar los gaps.
3. **Pares no intervenibles:** si cuentan o no en el denominador de la cobertura.
4. **Tangentes:** Jerónimo tiene 6.048 y Martín 6.571. La diferencia es 523, el número de hogares
   pobres, probablemente por omitir a = 0 en cada hogar. Falta confirmarlo.

## 7. Lo que sigue

**Jerónimo**
1. Instalar `highspy` en `opti1` y reproducir los resultados de equidad.
2. Responder a Martín en "Notas de Jerónimo" y cerrar el objetivo de M3/M4.
3. Monte Carlo del Modelo 3: ~100 réplicas × 3 metas, reportando la distribución.
4. Escribir el MILP del Modelo 4 y su Monte Carlo.
5. Actualizar los PDF de selección de variables.

**Depende de Martín**
- `parametros.py`, `conteo_pares.csv` y `empleo_componentes.csv`, para pasar M3/M4 a costos reales.
  Hasta entonces se usa `costos_provisionales.py` con u = 1.
- `03_preparar_antioquia.py`, para leer el universo común y comprobar 3.732 / 523 / 0,038684.

**Juntos**
- Comparación final de los 4 modelos sobre el mismo universo, con H, A, M0 y severidad por zona y total.
  La comparación limpia es el costo en pesos: M2 frente a M3/M4 con la misma meta mide el precio de no
  tener información de hogar.

## 8. Reglas de trabajo

- Repo compartido: **no hacer commit ni push sin que el dueño lo pida.** No poner atribución de Claude
  en commits ni en PR.
- Este archivo resume y no reemplaza `CONTEXTO_DATOS.md`, que sigue siendo de Martín.
- Responder en español.
