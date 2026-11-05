# Reglas de conteo de personas afectadas por privación

Objetivo: calcular, para cada hogar, **cuántas personas** tienen cada privación ($u_{ij}$),
a partir de `PERSONAS (DEPARTAMENTAL) 2025.csv`. El conteo se valida contra las columnas 0/1
de `HOGARES (DEPARTAMENTAL) 2025.csv`: el hogar debe tener conteo > 0 **exactamente** donde
el DANE marca la privación en 1.

- Llave de unión persona → hogar: `DIRECTORIO` + `SECUENCIA_P`.
- Edad: `P6040`.
- Validación hecha sobre los 87.060 hogares del país (no solo Antioquia).
- Los archivos .csv/.dta/.sav **no traen etiquetas**; los códigos se confirmaron con los datos
  y, cuando se indica, con el catálogo de microdatos del DANE (ECV).

## Definiciones auxiliares

```python
ocupado   = (P6240 == 1) | (P6250 == 1) | (P6260 == 1) | (P6270 == 1)
desocupado = ~ocupado & (P6351 == 1)
```

Años de educación aprobados (`anios`):

| Situación | Regla |
|---|---|
| No estudia (`P8586 == 2`), nivel `P8587` 1–2 | 0 |
| No estudia, nivel 3–5 (primaria, secundaria, media) | `P8587S1` (grado absoluto) |
| No estudia, nivel 6–11 (técnico, tecnológico, universitario) | 11 + `P8587S1` |
| No estudia, nivel 12–13 (posgrado) | 16 + `P8587S1` |
| Estudia (`P8586 == 1`), nivel `P1088` 1 (preescolar) | 0 |
| Estudia, nivel 2–4 | `P1088S1` − 1 |
| Estudia, nivel 5–7 | 11 + `P1088S1` − 1 |
| Estudia, nivel 8 | 16 + `P1088S1` − 1 |

## Reglas validadas

| Indicador | Persona privada si… | Coincidencia hogares |
|---|---|---|
| aseguramiento_salud | `P6040 >= 6` y `P6090` ∈ {2, 9} | 100 % |
| barreras_acceso_salud | `P5665 == 1` y `P8563` ∉ {1, 2} | 100 % |
| trabajo_infantil | 12 ≤ `P6040` ≤ 17 y `ocupado` | 100 % |
| rezago_escolar | 7 ≤ `P6040` ≤ 17 y `anios < P6040 − 6` | 100 % |
| analfabetismo | `P6040 >= 15` y `P6160 == 2` | 99,999 % (1 hogar) |
| inasistencia_escolar | 6 ≤ `P6040` ≤ 16 y `P8586 == 2` | 99,97 % (27 hogares) |
| logro_educativo | Regla del **hogar**: promedio de `anios` de los ≥ 15 años < 9 | 99,96 % (39 hogares) |
| empleo_formal | Ver abajo | 99,67 % |

### empleo_formal (regla del DANE en los datos)

El hogar está privado si se cumple cualquiera:
1. tiene al menos un **ocupado** con `P6920 == 2` (no cotiza a pensión);
2. tiene al menos un **desocupado**;
3. **no tiene ocupados** y alguna persona ≥ 15 años no cotiza ni es pensionada (`P6920` ∉ {1, 3}).

El boletín del DANE solo menciona el punto 1, pero los datos muestran los tres.

**Decisión de costeo (19-oct-2026):** costo por hogar, no precio × personas:

$$c_i = 2{,}73 \cdot n^{\text{ocup. sin pensión}}_i + \sum_{h \in \text{desoc}(i)} EpV_h + 2{,}73 \cdot n^{\text{adultos} \ge 15 \text{ sin cotizar ni pensión}}_i \;(\text{solo si el hogar no tiene ocupados})$$

| Caso | Intervención | Costo |
|---|---|---|
| 1. Ocupado sin pensión | Aporte a pensión (16 % × 12 SMMLV) | $2,73 M por ocupado |
| 2. Desocupado | Empleos para la Vida según perfil (Decreto 533 de 2024): 18–28 años 30 % ($5,12 M); mujer 29–56 20 % ($3,42 M); hombre 29–61 15 % ($2,56 M). Mujer ≥ 57 u hombre ≥ 62: aporte a pensión ($2,73 M) | $EpV_h$ por desocupado (actualizado 27-oct-2026) |
| 3. Hogar sin ocupados | Opción A: aporte a pensión a cada adulto sin cobertura | $2,73 M por adulto |

Sensibilidad del caso 3: opción B, emplear formalmente a un miembro ($5,12 M por hogar).
Supuesto: si el hogar también está privado en desempleo_larga_duracion, ambas privaciones se pagan por separado
(independencia entre indicadores, supuesto 2 del paper).

### rezago_escolar — decisión de costeo (21-oct-2026): opción C

- Años de atraso de cada niño: `atraso = (P6040 − 6) − anios` (rezago si `atraso >= 1`).
- **Intervenible** solo si **todos** los niños rezagados del hogar tienen `atraso == 1`
  (nivelables en el horizonte de un año). Si algún niño tiene `atraso >= 2`, se fija `x_ij = 0` en rezago.
- Costo: asignación por alumno SGP 2025 de la ETC Antioquia según zona y nivel del grado siguiente ([DNP, Anexo 1 DD SGP-96-2025](https://colaboracion.dnp.gov.co/CDT/Inversiones%20y%20finanzas%20pblicas/Documentos%20GFT/Distribuciones%20SGP/Anexos%201%20al%204%20DD%20SGP-96-2025.xlsx)):
  urbana $2,709,038 / $3,047,670 / $3,216,987 y rural $3,521,752 / $3,961,971 / $4,182,081 (primaria / secundaria / media). Exportar zona y grado por niño. Probablemente sobrestima, porque el 74 %
  de los rezagados ya está matriculado).
- Sensibilidad: A (todo intervenible) como cota alta y B (nada intervenible) como cota baja.
- En la muestra de Antioquia: 215 niños rezagados en hogares pobres; 83 con 1 año de atraso.
- Limitación a declarar: el horizonte de un año no premia nivelar niños con varios años de atraso;
  un modelo multiperiodo lo capturaría (investigación futura).
- **Severidad educativa (28-oct-2026):** exportar una tabla por niño rezagado (hogar, `P3`, tipo, `FEX_C`, `atraso`) para los 4 modelos.
  Distribución: 83 con 1 año, 47 con 2, 27 con 3, 26 con 4, 32 con 5 o más. Ver `docs/informe_modelo1.md` §3.5.

### inasistencia_escolar — decisión de costeo (21-oct-2026): transferencia condicionada

- Intervención: subsidio condicionado a asistencia (tipo Renta Ciudadana), $3,0 M por hogar al año.
- El Estado paga de enero a diciembre; el informe de asistencia de diciembre decide si se renueva el
  año siguiente (fuera del horizonte del modelo). Dentro del año, el gasto ocurre con o sin cumplimiento.
- `p` = proporción de niños subsidiados que sí cumplen con asistir (probabilidad, entre 0 y 1).
- **Optimización:** costo efectivo $3,0 M / p por hogar (el modelo decide sin saber quién cumplirá).
- **Evaluación:** Monte Carlo (~200 corridas) sobre el plan óptimo: cada niño cumple con prob. p;
  la privación del hogar se elimina solo si todos sus niños no escolarizados cumplen. Reportar media y rango de H y M0.
- Escenarios: p = 0,37 (cota pesimista: Renta Ciudadana, ciclo 4 de 2025, hogares que cumplieron todas
  las corresponsabilidades), 0,50 y 0,75.
- Muestra de Antioquia: 39 hogares pobres con inasistencia, 49 niños (29 de 15–16 años);
  21 de esos hogares también tienen trabajo infantil.

## Indicadores que NO se pueden replicar con este archivo

### atencion_integral (mejor regla: 96,5 %)

DANE: hogar privado si tiene un niño de 0 a 5 años sin acceso a **todos** los servicios de
cuidado integral (salud, nutrición y cuidado).

`P51`: ¿Dónde o con quién permanece la mayor parte del tiempo entre semana? (solo 0–4 años)

| Código | Etiqueta | ¿Privación de cuidado en los datos? |
|---|---|---|
| 1 | Asiste a hogar comunitario, jardín, CDI o colegio | No |
| 2 | Con su padre o madre en la casa | **No** |
| 3 | Con su padre o madre en el trabajo | Sí (siempre) |
| 4 | Con empleado(a) o niñero(a) en la casa | No |
| 5 | Al cuidado de un pariente de 18 años o más | No |
| 6 | Al cuidado de un pariente menor de 18 años | Sí (siempre) |
| 7 | En casa solo | Sí |
| 8 | Otro | No |

`P55`: ¿recibe desayuno o almuerzo en el lugar donde permanece? · `P774`: ¿paga por esta alimentación?

Mejor regla encontrada: niño 0–4 con `P51` ∈ {3, 6} **o** `P55 == 2` **o** `P6090` ∈ {2, 9}.
Quedan ~3.000 hogares privados sin explicar: el DANE usa variables que no vienen en este archivo
(p. ej. niños de 5 años, controles de crecimiento o vacunación).

**Implicación para el costo:** quedarse en casa con el padre o la madre NO es privación de cuidado.
- Niño con `P51` ∈ {3, 6, 7}: la privación es de cuidado → CDI ($5,21 M).
- Niño privado por otra causa (salud o nutrición) y en casa con sus padres: una modalidad en el
  hogar con complemento alimentario podría bastar → revisar la decisión de usar CDI en todos los casos.

Conteo propuesto mientras tanto: número de niños de 0 a 5 años del hogar (supuesto declarado).

**Decisión (19-oct-2026):** se mantiene el CDI institucional ($5,21 M por niño) en las tres zonas, porque los
microdatos no permiten identificar qué componente (salud, nutrición o cuidado) causa la privación de cada niño.

### desempleo_larga_duracion (mejor regla: 86,5 %)

DANE: hogar privado si tiene al menos un miembro de la PEA desempleado por más de 12 meses.
Con `P7250` (semanas buscando trabajo) ≥ 52 solo se identifican ~250 de los 11.985 hogares privados:
la variable que usa el DANE no está en este archivo.

Conteo propuesto: número de desocupados del hogar, mínimo 1 si el DANE marca la privación (supuesto declarado).
Costo: $EpV_h$ según el perfil de cada desocupado (ver empleo_formal, caso 2). Si el hogar está privado pero no se identifica ningún desocupado, se usa la tarifa de 30 % ($5,12 M), que es la más alta de Empleos para la Vida sin discapacidad (supuesto conservador).

## Fuentes

- DANE, Boletín técnico Pobreza multidimensional 2025 (14 de abril de 2026):
  https://www.dane.gov.co/files/operaciones/PM/bol-PMultidimensional-2025.pdf
- DANE, catálogo de microdatos ECV, módulo de atención integral de menores de 5 años:
  https://microdatos.dane.gov.co/index.php/catalog/827/data-dictionary/F11
- Categorías de `P51` (ECV 2017, mismo cuestionario):
  https://microdatos.dane.gov.co/index.php/catalog/544/datafile/F82/V4187
