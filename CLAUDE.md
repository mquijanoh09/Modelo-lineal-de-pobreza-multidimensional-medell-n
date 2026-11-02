# Contexto del proyecto — Modelos 3 y 4 de reducción del IPM (MILP)

> Rama `Contexto`. Ver también `CONTEXTO_DATOS.md` (Martín, actualizado 2-nov) y `graphify-out/`.
> **Actualizado: 2-nov-2026** (corrida automática). Resumen de esa corrida en el Project:
> `claude/resumen-avance-2nov.md`; el código `m34_*` y sus resultados están en la rama `Modelo3`.

## Qué es esto

Proyecto final universitario de Investigación de Operaciones. Se adaptan a Colombia
los cuatro modelos de Hamie, Hlasny & Jouni (2024), *Multidimensional Poverty
Alleviation: Policy Optimization and Impact Simulation* (ERF Working Paper 1742).
Son MILP que minimizan el esfuerzo/presupuesto del Estado sujeto a alcanzar una
meta de reducción del Índice de Pobreza Multidimensional (IPM) del DANE.

**División del trabajo.** Martín Quijano hace los Modelos 1 y 2 (información
perfecta). Jerónimo Vélez hace los **Modelos 3 y 4** (información imperfecta: el
planificador solo observa agregados por grupo, y qué hogar recibe el beneficio lo
decide un mecanismo estocástico). Solo los Modelos 3 y 4 corresponden a este CLAUDE.md.

- **Modelo 3**: focalización geográfica estocástica. Esfuerzo por (indicador, zona P3).
- **Modelo 4**: focalización mixta. V = {acueducto, alcantarillado} por zona; U = los
  otros 13 por clúster k-means (k = 4). Mismo mecanismo del Modelo 3.

**Narrativa que hay que preservar:** estos modelos simulan la capacidad real y las
limitaciones del Estado para focalizar programas sociales. El error de inclusión
es el principal resultado de política, no un defecto del modelo.

Sustentación final: noviembre de 2026.

## Datos

Base: **microdato oficial del IPM 2025 del DANE**, catálogo 903, versión
DEPARTAMENTAL (87.060 hogares; trae `DEPARTAMENTO`). Ya trae los 15 indicadores.

**Hechos verificados — usarlos como test de regresión:**

| Hecho | Valor |
|---|---|
| Llave de hogar | `(DIRECTORIO, SECUENCIA_P)` |
| Columna `IPM` | se reconstruye con pesos anidados oficiales, error 2,2e-16 |
| Columna `POBRE` | idéntica a `IPM >= 1/3` |
| `FEXP` | `FEX_C * PERSONAS` = HS_i × HW_i |
| `P3` (VIVIENDAS) | clase: 1 cabecera, 2 centro poblado, 3 rural disperso |
| Incidencia nacional / cabeceras / rural | 9,91 / 6,30 / 22,44 % (DANE: 9,9 / 6,3 / 22,4) |

**Limitación dura: no hay municipio.** Medellín y Valle de Aburrá imposibles con estos datos.

Pesos: Educación 0,10 c/u (logro, analfabetismo); Niñez 0,05 c/u (inasistencia, rezago,
atención integral, trabajo infantil); Trabajo 0,10 c/u; Salud 0,10 c/u; Vivienda 0,04 c/u.

## Escenario (universo común de los 4 modelos)

**Antioquia completa** (`DEPARTAMENTO == 5`), D = las 3 clases de P3.

| Zona | Hogares | Pobres | H0 | A0 | M0 |
|---|---|---|---|---|---|
| Cabecera | 1.670 | 127 | 6,21 % | 40,58 % | 0,0252 |
| Centro poblado | 613 | 103 | 17,91 % | 38,56 % | 0,0691 |
| Rural disperso | 1.449 | 293 | 25,18 % | 42,11 % | 0,1060 |
| **Total** | **3.732** | **523** | **9,45 %** | **40,94 %** | **0,038684** |

Pares activos M_ij = 1: 8.602 (45 pares (j, zona); 57 pares (j, grupo) en M4).
Personas representadas 7.231.754. Sev0 = 117.908. Guarda `|D| ≥ 2`: no quitarla.

## Archivos

| Archivo | Dónde | Qué hace |
|---|---|---|
| `utils_dane.py`, `02`, `03`, `04` | `main` (Martín) | lectura, validación, subconjunto urbano, línea base |
| `00_verificar_base.py` | `Modelo3` | 7 chequeos de que la base sirve para M3/M4 |
| `05_modelo3.py` | `Modelo3` | MILP directo; control de equivalencia |
| `06_modelo3_cortes.py` | `Modelo3` | MILP por cortes, objetivo del paper |
| `cortes.py`, `test_cortes.py` | `Modelo3` | mecanismo separado del objetivo (V cobertura, K costo, elig) |
| `modelo3_equidad.py`, `correr_m3_equidad.py`, `extremos_m3.py` | `Modelo3` | M3 con objetivo de equidad del M1 (**sin verificar**) |
| `costos_provisionales.py` | `Modelo3` | sensibilidad u = 1 (provisional) |
| `07_clusters.py` | `Modelo3` | k-means k = 4 del Modelo 4 |
| **`m34_datos.py`** | `Modelo3` | carga + línea base con asserts + sorteo R (idéntico a 05) |
| **`m34_mecanismo.py`** | `Modelo3` | cortes con `grupo` **matriz n×J** (sirve para M3 y M4), MILP del paper, métricas |
| **`m34_clusters.py`** | `Modelo3` | k-means idéntico a 07 (reproduce 1.389/1.038/849/456) |
| **`m34_montecarlo.py`** | `Modelo3` | MC: réplicas × metas {5,10,20 %} × costos {pp, u1}, para `m3` o `m4` |
| **`m34_optimos_alternos.py`** | `Modelo3` | rango del error de inclusión entre óptimos alternos |
| **`m34_test_regresion.py`**, **`m34_resumen_mc.py`** | `Modelo3` | regresión contra 06 (630 cortes, 153,0) y tabla/gráficas del MC |

Los `m34_*` son autocontenidos (no importan 05/06/07) y siguen la renumeración
`m34_` propuesta a Martín. Los resultados están en `resultados/m34/` de esa rama.

## Formulación (por cortes; equivalente a R1–R7 de 05)

```
z[j,g,c] ∈ {0,1}  ∀ c ∈ F_jg   (cortes auto-consistentes: R_(c) ≤ p(c) ≤ R_(c+1) − ε)
C1   Σ_c z[j,g,c] = 1
     N_ij = 1 − elig_ij · Σ_{c ≥ rank_ij} z[j,g,c]
     Costo_jg = Σ_c cumK(c) · z[j,g,c]        (incluye no pobres → error de inclusión)
R4   C_i + HS_i·HW_i·b1_i ≥ (Σ_j w_j N_ij)·HS_i·HW_i        ∀ i pobre
R5   C_i − HS_i·HW_i·b1_i ≤ (Σ_j w_j N_ij)·HS_i·HW_i        ∀ i pobre
R6   Σ_j w_j N_ij − (1 − b1_i) ≤ 0,33                        ∀ i pobre
R7   Σ_i C_i ≤ MPI_s·(1 − MPI_r)·Σ_i HS_i·HW_i               (MPI_s = M0)
min  Σ_jg Costo_jg
```
M3: g(i,j) = zona P3. M4: g(i,j) = zona si j ∈ V, clúster si j ∈ U.

## Trampas ya encontradas y corregidas — NO revertirlas

1. **Unidades de p_jd:** numerador y denominador en la misma unidad (si no, p llega a 4,81 y M3 = M1).
2. **MPI_s es M0, no H0** (con H0 el esfuerzo da 0). Nunca hardcodear 0,038684.
3. **Desigualdades estrictas:** `< 1/3` ⇔ `≤ 0,33`; `≤ R − ε` con ε = 1e-6 (mismo ε en la enumeración).
4. **Big-M por hogar** (HS_i·HW_i), nunca global.
5. **N_ij ≡ b2_ij**; solo pares con M_ij = 1 llevan variable.
6. **`C_i` con `lowBound=0`.**
7. **No inline-ar expresiones grandes** en bucles de restricciones.
8. **Cotas inferiores de esfuerzo desactivadas** (causa #1 de infactibilidad).
9. **Semilla de R por ID del hogar:** `SeedSequence([2026, replica, DIRECTORIO, SECUENCIA_P])`.
10. **Guarda |D| ≥ 2.**
11. **Gap de HiGHS por etapa** en equidad: 1e-6 (etapa 1) y 1e-4 (etapa 2).
12. **Submuestras solo para depurar.**
13. **(nuevo 2-nov) Óptimos alternos:** con esfuerzo en personas-privación hay empates; en la
    réplica 0, meta 5 %, el error de inclusión va de 41,7 % a 61,7 % con el mismo esfuerzo (60,0).
    Reportar con desempate lexicográfico (min inclusión s.a. esfuerzo ≤ E*) o como intervalo.
    El 41,7 % histórico era uno de esos óptimos, no un error.

## Estado actual (2-nov-2026)

**Modelo 3: completo con Monte Carlo (objetivo del paper).** **Modelo 4: MILP y Monte Carlo
hechos (objetivo del paper).** 1.200 MILP (100 réplicas × 3 metas × 2 costos × 2 modelos),
todos óptimos, 1–6 s cada uno. Mediana [p5; p95]:

| Meta | Modelo | Esfuerzo pp | Costo u=1 (mil millones $) | Inclusión (pp) | Exclusión | H final |
|---|---|---|---|---|---|---|
| 5 % | M3 | 83 [41; 124] | 12,2 [6,4; 17,4] | 59 % [32; 76] | 94 % | 0,0894 |
| 5 % | M4 | 57 [30; 79] | 6,0 [3,2; 6,6] | 41 % [16; 64] | 94 % | 0,0892 |
| 10 % | M3 | 164 [115; 223] | 23,5 [15,0; 32,9] | 64 % [44; 79] | 88 % | 0,0843 |
| 10 % | M4 | 133 [92; 162] | 13,4 [10,3; 16,9] | 45 % [23; 57] | 88 % | 0,0844 |
| 20 % | M3 | 365 [303; 420] | 44,2 [40,5; 47,8] | 62 % [45; 69] | 74 % | 0,0753 |
| 20 % | M4 | 345 [290; 383] | 38,3 [33,5; 41,9] | 35 % [27; 51] | 72 % | 0,0763 |

Pareado (misma R), por meta de 5 / 10 / 20 %:

- **Costo:** con u = 1, M4 es más barato en 97–99 % de las réplicas (ahorro mediano 53 / 43 / 13 %).
  Con `pp`, su esfuerzo es menor en 83 / 85 / 75 % (ahorro mediano 36 / 19 / 6 %).
- **Inclusión:** con `pp`, M4 tiene menos en 78 / 92 / 98 % de las réplicas. Con u = 1, en 33 / 76 / 92 %:
  con meta 5 % la mediana **sube** de 49 % a 60 %.

Hallazgos:
- **M4 (focalización demográfica tipo Sisbén) reduce el costo en casi todas las réplicas con u = 1 y el
  error de inclusión con `pp`**: resultado central. Con u = 1 la inclusión baja en metas de 10 y 20 %,
  pero sube en la de 5 %.
- **CORRECCIÓN:** "la inclusión crece con la meta (42→62→69 %)" era de una réplica; en el MC la
  mediana de M3 es plana (~60 %). Lo robusto es el nivel alto, no la tendencia.
- La variabilidad por el azar cae con la ambición: CV del esfuerzo M3 32 % (5 %) → 10 % (20 %).
- Exclusión 74–94 %: con metas pequeñas sobre M0 la mayoría de los pobres no recibe nada.
- M3 invierte casi todo en Cabecera (salud y analfabetismo); M4 en el clúster de primera infancia (T3).
- Rezago casi nunca se elige (≤ 5 % de réplicas en M3, ≤ 13 % en M4).

Etiquetas de clúster (k-means, random_state 2026): T0 adultos sin dependientes (1.389, H 3,7 %),
T1 adultos mayores (1.038, 11,8 %), T2 con hijos escolares (849, 9,1 %), T3 primera infancia (456, 16,1 %).

Variantes de costo: `pp` = V = K = HS (como 06; HS **sin** HW en la cobertura, hay que
declararlo); `u1` = V = HW, K = EpF_j^zona·HW (tabla de Martín §4, millones de $ 2025).

**Sin verificar todavía:** M3 con objetivo de equidad (`modelo3_equidad.py`). En la corrida
automática no se pudo ejecutar el código del repo.

## Lo que cambió en el equipo

**30-oct.** Martín subió `CONTEXTO_DATOS.md` (costos oficiales, reglas u_ij, propuesta de
`parametros.py`) y el grafo, con 7 preguntas (sección 8). Borrador de respuestas de Jerónimo:
1. SevEdu: sí, primero como métrica ex post en el MC de M3/M4 (el sorteo por niño rompe el prefijo por hogar).
2. M3/M4 no cambian de objetivo por defecto; comparación ex post en H, A, M0, severidad, SevEdu y pesos, por zona y total.
3. u_ij = 1 en empleo como sensibilidad, no como caso base.
4. Inasistencia: costo 3,0/p en la optimización; p solo en el MC.
5. Conteo de no pobres en el 05: imprescindible (error de inclusión).
6. Importar `IND`, `W` y la semilla de `parametros.py`; prefijo `m34_` para los archivos de Jerónimo.
7. Logro educativo = 3 ciclos CLEI (base); acueducto rural $43,7 M a confirmar con la fuente (BID $9,7 M como sensibilidad).
**Estas respuestas siguen sin escribirse en "Notas de Jerónimo" de `CONTEXTO_DATOS.md`.**

**2-nov (commit `72c9d02`, solo documentación, sin código).**
- Rezago decidido: con las reglas oficiales ningún niño sale del rezago en un año; estrategias por
  niño E0–E3; caso base sin E3 con cobertura obligatoria 6–15 + ρ_e = 14 % (≈ $105,8 mil millones);
  sensibilidad con E3: ρ_e = 20 %. Para M3/M4: en caso base, rezago con `elig = 0` (se paga, no cura)
  hasta tener sorteo por niño.
- Respondió: `05_conteo_personas` cuenta u_ij para los 3.732 hogares. Pendiente: meta del M2
  (¿M0 o H?), p de inasistencia del caso base (0,37 vs 0,50) y gap del solver.
- Siguen sin existir: `parametros.py`, `05_conteo_personas.py`, `03_preparar_antioquia.py`.
  Último código de Martín en el repo: 6-oct.

### Duda técnica: unidades con los costos de Martín

Con `costo = EpF_j·u_ij·HW_i`, la cobertura debe ser V = u_ij·HW_i (misma unidad arriba y
abajo; Trampa 1). `m34_mecanismo.enumerar_cortes` ya acepta V y K separados, y el ε no cambia.

## Para acordar con Martín (agenda de la próxima reunión)

Ordenado por qué tanto bloquea. Cada punto: qué se decide y qué propone Jerónimo.

| # | Tema | Propuesta de Jerónimo | Por qué importa |
|---|---|---|---|
| 1 | **Fecha límite de `parametros.py`, `05_conteo_personas.py` (`conteo_pares.csv`, `empleo_componentes.csv`, `ninos_rezago.csv`) y `03_preparar_antioquia.py`** | Fecha fija esta semana; si no llegan, M3/M4 se sustentan con u = 1 y se declara como limitación | Sin esto M3/M4 no tienen costos reales y no se puede comparar en pesos |
| 2 | **Objetivo de M3/M4** | Paper (min costo s.a. meta de M0) como caso base; equidad (como M1) como sensibilidad | Define qué se compara entre los 4 modelos |
| 3 | **Meta del Modelo 2: ¿sobre M0 o sobre H?** | Sobre M0, como el paper | Si M2 usa H, la comparación M2 ↔ M3/M4 (precio de no tener información) no cuadra |
| 4 | **Caso base común**: p de inasistencia (0,369 vs 0,50), solver y gap | p = 0,369 (dato oficial, ciclo 4 de 2025); HiGHS; reportar el gap de cada corrida | Las cifras de los 4 modelos tienen que salir con los mismos supuestos |
| 5 | **Nombres de archivos y ramas** | Archivos de Jerónimo con prefijo `m34_`; los de Martín conservan `02`–`05`; `IND`, `W` y `SEMILLA` se importan de `parametros.py`; ¿cuándo se fusiona `Modelo3` y `Contexto` a `main`? | Evitar el choque `05_` y que cada uno tenga su copia de los pesos |
| 6 | **Rezago en M3/M4** | Caso base con `elig = 0` (se paga, no cura) y SevEdu solo como métrica ex post; el sorteo por niño queda como trabajo futuro | Su decisión del 2-nov (ningún niño sale en un año) cambia el mecanismo |
| 7 | **Costos abiertos** | Logro = 3 ciclos CLEI (base); acueducto rural $43,7 M solo con la fuente verificable, BID $9,7 M como sensibilidad | Afecta el costo de vivienda rural, que es lo que más pesa en pesos |
| 8 | **Tangentes de severidad: 6.048 (Jerónimo) vs 6.571 (Martín)** | Confirmar que la diferencia de 523 es por incluir a = 0 en cada hogar | Si no, Sev0 y el techo de severidad no son comparables |
| 9 | **Pares no intervenibles** (columna `intervenible`) | N_ij = 1 fijo y excluirlos del denominador de cobertura | Contarlos deja la cobertura máxima < 1 |
| 10 | **Formato de la comparación final** | Tabla común: H, A, M0, severidad, SevEdu y costo en pesos, por zona `P3` y total; misma meta para M2, M3 y M4 | Es la diapositiva central de la sustentación |
| 11 | **Respuestas a sus 7 preguntas** | Escribirlas en "Notas de Jerónimo" de `CONTEXTO_DATOS.md` (hoy está vacía) | Martín no ha visto el borrador |
| 12 | **Reparto de la sustentación** | Definir quién presenta qué, el hilo narrativo (información perfecta → imperfecta → demográfica) y la fecha del ensayo | Faltan pocas semanas |

## Lo que sigue, en orden

1. **Escribir las respuestas en "Notas de Jerónimo"** y cerrar con Martín: objetivo de M3/M4
   (propuesta: el del paper como base, equidad como sensibilidad), fecha límite de
   `parametros.py`/`conteo_pares.csv`, p y gap del caso base, meta del M2 sobre M0.
2. Agregar el desempate lexicográfico (min inclusión) al MC.
3. M4 con objetivo de equidad: reutilizar `modelo3_equidad.py` pasando la matriz de grupo.
4. Cambiar a costos reales cuando lleguen (V = u·HW, K = costo_ij, elig de rezago = 0) y repetir el MC.
5. Regla para pares con denominador pequeño (`paredes` en centro poblado = 1 hogar).
6. Actualizar los PDF de selección de variables (Trampa 1, MC, M4) y preparar las diapositivas.
7. Comparación final de los 4 modelos sobre el mismo universo (H, A, M0, severidad, pesos; por zona y total).

## Decisiones abiertas

- Objetivo del caso base de M3/M4 (paper vs equidad).
- Pesos w_j: solo como sensibilidad (múltiplos de 0,01).
- Valle de Aburrá: solo con los módulos ECV 2025 (catálogo 905) cruzados por `DIRECTORIO`. Descartado por ahora.
- Solver único: CBC y HiGHS dan lo mismo en la regresión (153,0); el MC usó HiGHS con gap 1e-6.

## Entorno y cómo correrlo

```bash
python3 m34_test_regresion.py data/DANE/DEPARTAMENTAL
python3 m34_montecarlo.py data/DANE/DEPARTAMENTAL m3 0 100 out/mc_m3.csv   # ~25 s/réplica
python3 m34_montecarlo.py data/DANE/DEPARTAMENTAL m4 0 100 out/mc_m4.csv   # ~17 s/réplica
python3 m34_resumen_mc.py out/mc_m3.csv out/mc_m4.csv
```
- Entorno `opti1`: Python 3.10, PuLP 2.9.0 con CBC y HiGHS (`highspy` instalado).
  Los `m34_*` también corren con PuLP 3.x + highspy.
- `timeLimit` de CBC no es confiable; envolver en `timeout` (en Mac: `perl -e 'alarm 240; exec @ARGV' ...`).
- CSV del DANE: coma y UTF-8 con BOM.

## Convenciones

- Nada derivado de los datos hardcodeado (un `0.038684` literal es un bug; en `m34_datos` solo vive como assert).
- Los comentarios explican el porqué: son material de sustentación.
- Cambios metodológicos → también en `Seleccion_Variables_Restricciones_Modelo3.pdf` / `Modelo4.pdf`.
- Repo compartido: no hacer commit ni push sin que Jerónimo lo pida; sin atribución de Claude.
- Documentos del Project "Opti1": `decision-fuente-de-datos`, `revision-formulacion-modelo3`,
  `bitacora-problemas-y-soluciones`, `resumen-avance-2nov`, `codigo-m34/`.

## Reglas de trabajo

- Este archivo resume y no reemplaza `CONTEXTO_DATOS.md`, que sigue siendo de Martín.
- Responder en español.
