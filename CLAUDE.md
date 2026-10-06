# Contexto del proyecto — Modelos 3 y 4 de reducción del IPM (MILP)

## Qué es esto

Proyecto final universitario de Investigación de Operaciones. Se adaptan a Colombia
los cuatro modelos de Hamie, Hlasny & Jouni (2024), *Multidimensional Poverty
Alleviation: Policy Optimization and Impact Simulation* (ERF Working Paper 1742).
Son MILP que minimizan el esfuerzo/presupuesto del Estado sujeto a alcanzar una
meta de reducción del Índice de Pobreza Multidimensional (IPM) del DANE.

**División del trabajo.** Martín Quijano hace los Modelos 1 y 2 (información
perfecta: el planificador observa M_ij hogar por hogar y focaliza
determinísticamente). Jerónimo Vélez hace los **Modelos 3 y 4** (información
imperfecta: el planificador solo observa agregados por celda, y qué hogar recibe
el beneficio lo decide un mecanismo estocástico). Los Modelos 3 y 4 son el único
trabajo que corresponde a este CLAUDE.md.

- **Modelo 3**: focalización geográfica estocástica. El esfuerzo se asigna por
  (indicador, celda geográfica). Genera errores de inclusión y exclusión.
- **Modelo 4**: focalización mixta. Parte los 15 indicadores en V (bienes
  públicos → por celda geográfica) y U (bienes privados → por clúster de hogares
  construido con k-means). Reutiliza exactamente el mecanismo del Modelo 3.

**Narrativa que hay que preservar:** estos modelos simulan la capacidad real y las
limitaciones del Estado para focalizar programas sociales. El error de inclusión
(esfuerzo que cae en hogares no pobres) es el principal resultado de política, no
un defecto del modelo.

Sustentación final: noviembre de 2026.

## Datos

Base: **microdato oficial del IPM 2025 del DANE**, catálogo 903 de
microdatos.dane.gov.co. NO son los módulos de la ECV: es el anexo de Pobreza
Multidimensional, que ya trae los 15 indicadores calculados por el DANE.

```
data/DANE/DEPARTAMENTAL/HOGARES (DEPARTAMENTAL) 2025/...csv    87.060 hogares
data/DANE/DEPARTAMENTAL/PERSONAS (DEPARTAMENTAL) 2025/...csv
data/DANE/DEPARTAMENTAL/VIVIENDAS (DEPARTAMENTAL) 2025/...csv
data/DANE/NACIONAL/...                                          79.125 hogares
```

Se usa la versión DEPARTAMENTAL (muestra más grande, trae `DEPARTAMENTO`).

**Hechos verificados — no re-derivarlos, pero sí usarlos como test de regresión:**

| Hecho | Valor |
|---|---|
| Llave de hogar | `(DIRECTORIO, SECUENCIA_P)`, única, 100% match contra conteo del roster |
| Columna `IPM` | se reconstruye desde los 15 indicadores con pesos anidados oficiales, error 2,2e-16 |
| Columna `POBRE` | idéntica a `IPM >= 1/3`; confirma k = 0,333 |
| `FEXP` | igual a `FEX_C * PERSONAS`, o sea HS_i × HW_i |
| `P3` (en VIVIENDAS) | es la CLASE: 1 cabecera, 2 centro poblado, 3 rural disperso |
| Incidencia recalculada | nacional 9,91% / cabeceras 6,30% / rural 22,44% (oficial DANE: 9,9 / 6,3 / 22,4) |

**Limitación dura: la base no tiene municipio.** La geografía máxima es
`DEPARTAMENTO` (33), `REGION` (6) y `P3` (3). Medellín y Valle de Aburrá son
imposibles con estos datos. No intentar reconstruirlos.

Los 15 indicadores, en 5 dimensiones de peso 0,20 repartido en partes iguales:

```
Educación  (0.10): logro_educativo, analfabetismo
Niñez      (0.05): inasistencia_escolar, rezago_escolar, atencion_integral, trabajo_infantil
Trabajo    (0.10): desempleo_larga_duracion, empleo_formal
Salud      (0.10): aseguramiento_salud, barreras_acceso_salud
Vivienda   (0.04): acueducto, alcantarillado, pisos, paredes, hacinamiento
```

## Escenario actual

**Antioquia completa** (`DEPARTAMENTO == 5`), con **D = las 3 clases de P3**.

| | |
|---|---|
| Hogares \|I\| | 3.732 |
| Celdas \|D\| | 3 (Cabecera 1.670, Centro poblado 613, Rural disperso 1.449) |
| Hogares pobres | 523 |
| Pares activos \|A\| = {(i,j) : M_ij = 1} | 8.602 de 55.980 (15,4%) |
| H0 | 0,0945 |
| A0 | 0,4094 |
| **M0 = MPI_s** | **0,038684** |
| Personas representadas | 7.231.754 |

Por qué Antioquia completa y no Antioquia urbana (que es lo que usa el compañero
para los Modelos 1 y 2): con el filtro urbano, D queda en **una sola celda**,
E_jd colapsa a E_j, y el mecanismo de focalización geográfica desaparece — el
Modelo 3 deja de distinguirse del Modelo 1. Los Modelos 1 y 2 no usan D, así que
a ellos el filtro urbano no les molesta. `05_modelo3.py` aborta con `sys.exit` si
`|D| < 2`; **no quitar esa guarda.**

## Archivos

| Archivo | Autor | Qué hace |
|---|---|---|
| `utils_dane.py` | compañero | lectura robusta de los CSV (detecta separador y codificación) |
| `02_validar_ipm.py` | compañero | verifica pesos, umbral y factores de expansión |
| `03_preparar_antioquia_urbana.py` | compañero | valida `P3` y construye el subconjunto urbano |
| `04_linea_base.py` | compañero | H0, A0, M0, tasas censuradas, contribuciones por dimensión |
| `05_modelo3.py` | Jerónimo | **el MILP del Modelo 3** — es el archivo en el que se trabaja |

`05_modelo3.py` está parametrizado para que el filtro de datos no importe: todo
lo derivado de la muestra (MPI_s, Den_jd, conjunto activo, hogares pobres, R_ij)
se calcula en tiempo de ejecución. Cambiar de escenario es cambiar `FILTRO` y
`COL_CELDA` en la cabecera.

## Formulación implementada en 05_modelo3.py

Conjuntos: I hogares, J los 15 indicadores, D celdas, I[d] hogares de la celda d,
A = {(i,j) : M_ij = 1}.
Constante por celda: `Den_jd = Σ_{i∈I[d]} HS_i · M_ij` (personas privadas).
Cobertura: `p_jd = Σ_{i∈I[d]} HS_i·(M_ij − N_ij) / Den_jd ∈ [0,1]`.

Variables: `N_ij ∈ {0,1}` para (i,j) ∈ A; `b1_i ∈ {0,1}` solo para hogares pobres
hoy; `E_jd ≥ 0`; `C_i ≥ 0` solo para hogares pobres hoy.

Objetivo: `min Σ_j Σ_d E_jd`

```
R1   E_jd = EF_j · Σ_{i∈I[d]} HS_i·(M_ij − N_ij)                ∀j, ∀d
R2   E_min_j ≤ Σ_d E_jd ≤ E_max_j                               ∀j   [DESACTIVADA]
R3a  E_jd/(EF_j·Den_jd) ≥ R_ij − N_ij                           ∀(i,j)∈A, i∈I[d]
R3b  E_jd/(EF_j·Den_jd) ≤ R_ij − ε + 2·(1 − N_ij)               ∀(i,j)∈A, i∈I[d]
R3c  N_{i1,j} ≤ N_{i2,j}   si R_{i1,j} < R_{i2,j}, misma celda   [cortes de prefijo]
R4   C_i + HS_i·HW_i·b1_i ≥ (Σ_j N_ij·w_j)·HS_i·HW_i            ∀i pobre
R5   C_i − HS_i·HW_i·b1_i ≤ (Σ_j N_ij·w_j)·HS_i·HW_i            ∀i pobre
R6   Σ_j N_ij·w_j − (1 − b1_i) ≤ 0,33                           ∀i pobre
R7   Σ_i C_i ≤ MPI_s·(1 − MPI_r)·Σ_i HS_i·HW_i
```

## Trampas ya encontradas y corregidas — NO revertirlas

1. **Unidades de p_jd.** El PDF original lo definía con numerador en personas
   (`Σ HS_i·(M−N)`) y denominador en hogares (`Σ M_ij`). Eso deja p_jd entre 1,70
   y 4,81; como `R_ij ~ U[0,1]`, todo hogar privado se cura siempre, el mecanismo
   estocástico queda inerte y el Modelo 3 se vuelve el Modelo 1. El denominador
   **tiene que ser** `Σ HS_i·M_ij` (personas).
2. **MPI_s es M0, no H0.** El lado izquierdo de R7 es la tasa ajustada
   (H×A) = 0,038684, no la incidencia 0,0945. Si se pone H0, R7 queda holgada por
   un factor 2,4 y el modelo devuelve esfuerzo cero.
3. **Desigualdades estrictas.** Un solver no las acepta. En R6, como los pesos son
   múltiplos de 0,01, `< 1/3` es exactamente `≤ 0,33` — sin epsilon. En R3b se usa
   `ε = 1e-6` solo para romper el empate `p_jd == R_ij`.
4. **Big-M ajustado, no un M global grande.** Con las variables acotadas, casi
   todos los M valen 1 (N binaria, p y R en [0,1], puntaje ponderado en [0,1]). El
   único que no es 1 está en R4/R5 y es `HS_i·HW_i`, **indexado por hogar**. Un M
   global grande no cambia el óptimo entero pero destroza la relajación lineal y
   CBC nunca cierra el gap.
5. **N_ij y b2_ij son la misma variable.** Trabajando Lin 6/8/9 del PDF con M = 1
   y `b3 = 1 − b2` resulta `N_ij = b2_ij` idénticamente. Por eso b2 y b3 no
   existen en el código. No reintroducirlos.
6. **Solo los pares con M_ij = 1 llevan variable.** Si M_ij = 0 entonces N_ij = 0
   por construcción. Declarar todo I×J multiplica las binarias por 14.
7. **`C_i` tiene que declararse con `lowBound=0`.** Cuando `b1_i = 1` (hogar no
   pobre) nada en R4/R5 fuerza `C_i = 0`: funciona solo porque R7 es `≤` y al
   optimizador le conviene bajarla. Si se declara libre, R7 se vuelve
   trivialmente factible y el modelo miente.
8. **Nunca inline-ar una expresión grande dentro de un bucle de restricciones.**
   El bug original: `p_jd` se construía como una suma de ~1.000 términos y se
   usaba dentro de un bucle de ~1.000 restricciones, generando millones de
   términos; PuLP se colgaba antes de llamar al solver. Se escribe `p_jd` usando
   la variable `E_jd` ya definida en R1, lo que deja 2 términos por restricción.
9. **Las cotas inferiores de R2 son la causa #1 de infactibilidad.** Obligan a
   gastar en indicadores donde la celda casi no tiene hogares privados — `paredes`
   en Centro poblado tiene UN solo hogar privado. R2 está desactivada a propósito.
10. **Semilla de R_ij derivada del ID del hogar**, no de su posición en la tabla
    (`np.random.SeedSequence([SEMILLA, replica, DIRECTORIO, SECUENCIA_P])`). Así
    cada hogar conserva su R al cambiar el filtro o el tamaño de muestra, y las
    corridas son comparables. No cambiar a `rng.random((n, 15))`.

## Estado actual

**Funciona:**
- `MPI_r = 0` → esfuerzo exactamente 0, óptimo en segundos. Es el test de capa 1:
  la línea base ya cumple la meta. Si esto no da 0, R4–R7 están mal.
- Muestra de desarrollo estratificada por **celda × condición de pobreza**, con
  recalibración de FEX_C por estrato. `N_POR_CELDA = 200` → 600 hogares, 1.560
  binarias, óptimo en ~6,7 s. H0 se preserva exacto (0,0945); M0 queda a ~3% del
  real (el residuo es A0, que depende de los puntajes de los pobres muestreados y
  no se arregla con pesos).
- Con `N_POR_CELDA = 200` y `MPI_r = 0,10`: esfuerzo 20,0 personas-privación, 5
  privaciones resueltas, H 0,0945 → 0,0843, **error de inclusión 35,0%**.

**No funciona todavía:**
- La **base completa** (3.732 hogares, 9.125 binarias) con `MPI_r = 0,10` no
  cierra el gap en CBC: más de 200 segundos sin terminar.

## Lo que sigue, en orden

1. **Reformulación por cortes de prefijo.** Es el trabajo principal pendiente.
   Dentro de cada (indicador, celda), como todo hogar sale si y solo si
   `R_ij ≤ p_jd`, el conjunto de curados es siempre un **prefijo** del orden de
   R_ij ascendente. Entonces la decisión real no son 8.602 binarias: es un punto
   de corte por cada uno de los 45 pares (indicador, celda). Contando los cortes
   auto-consistentes (los c que cumplen `R_(c) ≤ p(c) < R_(c+1)` con
   `p(c) = cumsum(HS ordenado por R)/Den`) salen **631 en total**.
   Reformular con un selector `z[j,d,c]` por corte factible y
   `Σ_c z[j,d,c] = 1`: 631 + 523 = 1.154 binarias en vez de 9.125, con
   estructura "escoge una opción por celda" que CBC resuelve sin problema.
   `N_ij = 1 − Σ_{c ≥ rank_ij} z[j,d,c]`, lineal; `E_jd` también.
2. Barrido de `MPI_r` (0,05 / 0,10 / 0,20) sobre la base completa.
3. Bucle de Monte Carlo: N réplicas variando `REPLICA`, guardando la solución de
   cada una, y reportando distribución del esfuerzo y del error de inclusión.
4. Calibrar `EF_j` (hoy en 1,0, así que el objetivo mide personas-privación
   resueltas) con costos unitarios del DNP/DPS, y recién entonces activar R2.
5. Decidir y documentar la regla para los pares (indicador, celda) con
   denominador muy pequeño: fijar `E_jd = 0`, agrupar celdas, o poner un piso.
6. Modelo 4: `06_modelo4.py`. Hereda todo lo anterior. Nuevo: k-means para
   construir T (número de clústeres por método del codo + silueta, fijado ANTES
   de optimizar, no es variable de decisión), partición J = U ∪ V, variable
   `E_jt`, y R2 pasa a acotar `Σ_d E_jd + Σ_t E_jt`.

## Entorno y cómo correrlo

```bash
cd <raíz del repo>
python3 05_modelo3.py          # usa MPI_R de la cabecera
python3 05_modelo3.py 0.10     # sobrescribe la meta por argv
```

- Python 3.10, con `pandas`, `numpy`, `pulp` (CBC), `pyarrow`, `scikit-learn`.
  Entorno conda `opti1`. **PuLP fijado en 2.9.0**: PuLP 4.0 cambió la API
  (`LpVariable(cat=)` y `PULP_CBC_CMD` ya no existen) y no trae CBC.
- Los scripts importan `utils_dane`, que está en la raíz. Si se corre desde otro
  directorio o con `python3 -I`, hay que pasar `PYTHONPATH=<raíz del repo>`.
- **El `timeLimit` de `PULP_CBC_CMD` no se respeta de forma confiable** (con 120 s
  configurados siguió más de 200). Para corridas largas, envolver en un `timeout`
  del sistema.
- Los CSV del DANE vienen separados por coma y en UTF-8 con BOM en esta base;
  `utils_dane.leer()` lo detecta solo. No hardcodear `sep` ni `encoding`.

## Convenciones

- Nada de valores derivados de los datos hardcodeados en el código. MPI_s, Den_jd,
  el conjunto activo y la lista de hogares pobres se calculan de la muestra que se
  le pase. Si aparece un `0.038684` literal en el código, es un bug.
- Los comentarios del script explican *por qué*, no *qué*. Son material de estudio
  para la sustentación: mantenerlos y ampliarlos, no limpiarlos.
- Cualquier cambio en una decisión metodológica (umbral, pesos, definición de D,
  partición U/V) debe reflejarse también en
  `Seleccion_Variables_Restricciones_Modelo3.pdf` / `Modelo4.pdf`, que están en la
  carpeta del proyecto, un nivel arriba del repo.
