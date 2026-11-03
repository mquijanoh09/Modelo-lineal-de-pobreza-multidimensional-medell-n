# Contexto del proyecto — Modelos 3 y 4 de reducción del IPM (MILP)

> Rama `Contexto`. Ver también `CONTEXTO_DATOS.md` (Martín, actualizado 2-nov) y `graphify-out/`.
> **Actualizado: 3-nov-2026, tarde** (segunda corrida automática del día). Resúmenes en el Project:
> `claude/resumen-avance-3nov-tarde.md` (el más reciente), `claude/resumen-avance-3nov.md` y `claude/resumen-avance-2nov.md`.
> Código `m34_*` y resultados del 3-nov (incluidos la sensibilidad a k y el barrido v2): rama `Modelo3`.

## Qué es esto

Proyecto final universitario de Investigación de Operaciones. Se adaptan a Colombia
los cuatro modelos de Hamie, Hlasny & Jouni (2024), *Multidimensional Poverty
Alleviation: Policy Optimization and Impact Simulation* (ERF Working Paper 1742).
Son MILP que minimizan el esfuerzo o presupuesto del Estado sujeto a alcanzar una
meta de reducción del Índice de Pobreza Multidimensional (IPM) del DANE.

**División del trabajo.** Martín Quijano hace los Modelos 1 y 2 (información
perfecta). Jerónimo Vélez hace los **Modelos 3 y 4** (información imperfecta: el
planificador solo observa agregados por grupo, y un mecanismo estocástico decide qué
hogar recibe el beneficio). Este CLAUDE.md cubre solo los Modelos 3 y 4.

- **Modelo 3**: focalización geográfica estocástica. Esfuerzo por (indicador, zona P3).
- **Modelo 4**: focalización mixta. V = {acueducto, alcantarillado} por zona; U = los
  otros 13 indicadores por clúster k-means (k = 4). Mismo mecanismo del Modelo 3.

**Narrativa que hay que preservar:** estos modelos simulan la capacidad real y las
limitaciones del Estado para focalizar programas sociales. El error de inclusión
es el principal resultado de política, no un defecto del modelo.

Sustentación final: noviembre de 2026.

## Datos

Base: **microdato oficial del IPM 2025 del DANE**, catálogo 903, versión
DEPARTAMENTAL (87.060 hogares; incluye `DEPARTAMENTO`). Ya trae los 15 indicadores.

**Hechos verificados — usarlos como test de regresión:**

| Hecho | Valor |
|---|---|
| Llave de hogar | `(DIRECTORIO, SECUENCIA_P)` |
| Columna `IPM` | se reconstruye con los pesos anidados oficiales (error 2,2e-16) |
| Columna `POBRE` | idéntica a `IPM >= 1/3` |
| `FEXP` | `FEX_C * PERSONAS` = HS_i × HW_i |
| `P3` (VIVIENDAS) | clase: 1 cabecera, 2 centro poblado, 3 rural disperso |
| Incidencia nacional / cabeceras / rural | 9,91 / 6,30 / 22,44 % (DANE: 9,9 / 6,3 / 22,4) |

**Limitación dura: no hay municipio.** Con estos datos es imposible aislar Medellín o el Valle de Aburrá.

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
Personas representadas: 7.231.754; personas pobres: 683.406. Sev0 = 117.908. Mantener la guarda `|D| ≥ 2`.

## Archivos

| Archivo | Dónde | Qué hace |
|---|---|---|
| `utils_dane.py`, `02`, `03`, `04` | `main` (Martín) | lectura, validación, subconjunto urbano, línea base |
| `00_verificar_base.py` | `Modelo3` | 7 chequeos de que la base sirve para M3/M4 |
| `05_modelo3.py` | `Modelo3` | MILP directo; control de equivalencia |
| `06_modelo3_cortes.py` | `Modelo3` | MILP por cortes con el objetivo del paper |
| `cortes.py`, `test_cortes.py` | `Modelo3` | mecanismo separado del objetivo (V cobertura, K costo, elig) |
| `modelo3_equidad.py`, `correr_m3_equidad.py`, `extremos_m3.py` | `Modelo3` | M3 con el objetivo de equidad del M1 (versión vieja; reemplazada por `m34_equidad.py`) |
| `costos_provisionales.py` | `Modelo3` | sensibilidad u = 1 (provisional) |
| `07_clusters.py` | `Modelo3` | k-means k = 4 del Modelo 4 |
| **`m34_datos.py`** | `Modelo3` | carga + línea base con asserts + sorteo R (idéntico a 05) |
| **`m34_mecanismo.py`** | `Modelo3` | cortes con `grupo` como **matriz n×J**; `excluir=` (no intervenibles) y `pobre0=` (cumNP); MILP del paper con `desempate=True`; métricas |
| **`m34_clusters.py`** | `Modelo3` | k-means idéntico a 07 (reproduce 1.389/1.038/849/456) |
| **`m34_montecarlo.py`** | `Modelo3` | MC del 2-nov (sin desempate). Define `EPF`, `precios_u1` y `matriz_grupo` |
| **`m34_montecarlo_lex.py`** | `Modelo3` | MC con desempate lexicográfico × rezago {intervenible, no_intervenible}, Pool(2) |
| **`m34_equidad.py`**, **`m34_correr_equidad.py`** | `Modelo3` | objetivo de equidad del M1 para M3 **y** M4 (dos etapas, tangentes, ρ y r) |
| **`m34_referencia_info_perfecta.py`** | `Modelo3` | mismo objetivo de equidad con información perfecta (techo propio; **no** es el M1) |
| **`m34_resumen_3nov.py`**, **`m34_grafica_equidad.py`** | `Modelo3` | tablas del MC lex y de equidad; gráfica IP vs M4 vs M3 |
| **`m34_sensibilidad_k.py`**, `m34_resumen_k.py`, `m34_grafica_k.py` | `Modelo3` | M4 con k ∈ {2,3,4,5,6,8}, 50 réplicas pareadas, equidad (B = 10, 25) + paper (10 %, u1); silueta, CH, η² de pobreza |
| **`m34_barrido_metas_v2.py`**, `m34_resumen_barrido_v2.py` | `Modelo3` | curva costo–meta 2–30 % (u1, 30 réplicas, desempate, rezago no intervenible); mide el costo en pares con n < 10 |
| `m34_pares_pequenos.py` | `Modelo3` | lista los pares (j, g) con pocos hogares privados |
| **`m34_optimos_alternos.py`** | `Modelo3` | rango del error de inclusión entre óptimos alternos |
| **`m34_test_regresion.py`**, **`m34_resumen_mc.py`** | `Modelo3` | regresión contra 06 (630 cortes, 153,0) y tabla/gráficas del MC del 2-nov |
| ~~`m34_barrido_sensibilidad.py`~~ | Project (2-nov) | **Reemplazado por `m34_barrido_metas_v2.py`.** Sus filas `no_intervenible` no sirven (Trampa 14) |

Los `m34_*` son autocontenidos (no importan 05/06/07) y usan el prefijo `m34_` propuesto a Martín.
Los resultados del 2-nov y del 3-nov están en `resultados/m34/` de la rama `Modelo3`
(`resumen_mc_lex.csv`, `equidad_m34.csv`, `info_perfecta.csv`, `resumen_k.csv`, `calidad_k.csv`,
`resumen_barrido_v2.csv`, `pares_pequenos.csv`).

## Formulación (por cortes; equivalente a R1–R7 de 05)

```
z[j,g,c] ∈ {0,1}  ∀ c ∈ F_jg   (cortes auto-consistentes: R_(c) ≤ p(c) ≤ R_(c+1) − ε)
C1   Σ_c z[j,g,c] = 1
     cur_ij = Σ_{c ≥ rank_ij} z[j,g,c];   s_i = Σ_j w_j M_ij − Σ_{j intervenible} w_j cur_ij
     Costo_jg = Σ_c cumK(c) · z[j,g,c]        (incluye no pobres → error de inclusión)
Objetivo del paper:
R4   C_i + HS_i·HW_i·b1_i ≥ s_i·HS_i·HW_i        ∀ i pobre
R5   C_i − HS_i·HW_i·b1_i ≤ s_i·HS_i·HW_i        ∀ i pobre
R6   s_i − (1 − b1_i) ≤ 0,33                      ∀ i pobre
R7   Σ_i C_i ≤ MPI_s·(1 − MPI_r)·Σ_i HS_i·HW_i   (MPI_s = M0)
min  Σ_jg Costo_jg;   etapa 2 (desempate): min Σ cumNP·z  s.a.  Σ Costo ≤ E*(1 + 1e-6)
Objetivo de equidad (M1): (1) Σ Costo ≤ B; (2) s_i ≤ 0,33 + (s0_i − 0,33)(1 − y_i);
     (4) equidad por zona; (7) tangentes q_i; (8) Σ p_i q_i ≤ (1 − ρ) Sev0;
     etapa 1 max Σ p_i y_i, etapa 2 min Σ p_i q_i s.a. Σ p_i y_i ≥ H*
```
M3: g(i,j) = zona P3. M4: g(i,j) = zona si j ∈ V, clúster si j ∈ U.

## Trampas ya encontradas y corregidas — NO revertirlas

1. **Unidades de p_jd:** numerador y denominador en la misma unidad (si no, p llega a 4,81 y M3 = M1).
2. **MPI_s es M0, no H0** (con H0 el esfuerzo da 0). Nunca hardcodear 0,038684.
3. **Desigualdades estrictas:** `< 1/3` ⇔ `≤ 0,33`; `≤ R − ε` con ε = 1e-6 (el mismo ε en la enumeración).
4. **Big-M por hogar** (HS_i·HW_i), nunca global.
5. **N_ij ≡ b2_ij**; solo los pares con M_ij = 1 llevan variable.
6. **`C_i` con `lowBound=0`.**
7. **No inline-ar expresiones grandes** en bucles de restricciones.
8. **Cotas inferiores de esfuerzo desactivadas** (causa #1 de infactibilidad).
9. **Semilla de R por ID del hogar:** `SeedSequence([2026, replica, DIRECTORIO, SECUENCIA_P])`.
10. **Guarda |D| ≥ 2.**
11. **Gap de HiGHS por etapa** en equidad: 1e-6 (etapa 1) y 1e-4 (etapa 2).
12. **Submuestras solo para depurar.**
13. **Óptimos alternos (2-nov):** con el esfuerzo en personas-privación hay empates. **Cerrada el 3-nov** con
    `desempate=True` (min inclusión s.a. esfuerzo ≤ E*). Impacto real: la inclusión baja solo en 3–14 % de las
    réplicas `pp` y en 0 % de las u1; las medianas casi no cambian.
14. **(3-nov) Indicadores no intervenibles = constante en el puntaje.** Si s_i solo suma los pares con variable,
    excluir un indicador "cura" gratis su peso (M4 cumplía metas del 5–10 % con costo 0). Usar
    `s_i = w·M_i − Σ w_j cur_ij`. Las filas `no_intervenible` del barrido del 2-nov no sirven.
15. **(3-nov) Falso infactible del presolve de HiGHS en la etapa 2** (12/2.400 corridas del paper y 2/300 de
    equidad), aunque la solución de la etapa 1 sea factible. Hay que reintentar con `presolve="off"`. Ya está en
    `m34_mecanismo` y `m34_equidad`.
16. **(3-nov) PuLP 4.x rompe `LpVariable(cat=...)`.** Instalar con `requirements.txt` (`pulp<4`).
17. **(3-nov tarde) Un k grande en M4 simula información individual.** Con k = 8 hay 26 pares (j, clúster) con menos de
    10 hogares privados, y uno de solo 81 hogares en total. En un par de 1–3 hogares el corte equivale a escoger hogar
    por hogar. La "ganancia" de subir k más allá de 4 es en buena parte un artefacto de muestra. **No presentar
    k = 8 como mejor.** Regla: < 15 % de pares con n < 10 (k = 4: 8/53; k = 5: 14/64).

## Estado actual (3-nov-2026, tarde)

**Modelos 3 y 4 técnicamente completos con u = 1:** objetivo del paper + MC con desempate, objetivo de equidad
+ MC, referencia de información perfecta, **sensibilidad a k** y **curva costo–meta del 2 al 30 %**. Caso base:
rezago no intervenible. Solo falta lo que depende de Martín (costos reales, M1/M2 en el repo) y la redacción
(PDF y diapositivas). La regresión pasa (630 cortes, 153,0, 62,1 %, HiGHS y CBC).

### Objetivo del paper (MC con desempate, rezago no intervenible): 2.400 MILP, todos óptimos

Mediana [p5; p95]. La inclusión se mide en personas con `pp` y en pesos con u1.

| Meta | Modelo | Esfuerzo pp | Inclusión pp | Costo u1 (mil mill. $) | Inclusión u1 | Exclusión |
|---|---|---|---|---|---|---|
| 5 % | M3 | 83 [42; 124] | 56 % [29; 76] | 12,2 [6,4; 17,4] | 48 % [24; 77] | 94 % |
| 5 % | M4 | 57 [30; 79] | 41 % [16; 64] | 6,0 [3,2; 6,6] | 54 % [24; 61] | 92–94 % |
| 10 % | M3 | 164 [115; 223] | 64 % [44; 79] | 23,5 [15,0; 32,9] | 74 % [39; 78] | 86–88 % |
| 10 % | M4 | 132 [92; 162] | 44 % [22; 56] | 13,4 [10,3; 16,9] | 57 % [28; 68] | 87–88 % |
| 20 % | M3 | 364 [303; 420] | 62 % [45; 70] | 44,3 [40,4; 47,8] | 65 % [56; 67] | 74 % |
| 20 % | M4 | 346 [292; 385] | 36 % [27; 50] | 38,3 [33,5; 41,9] | 41 % [28; 61] | 72 % |

Pareado M4 vs M3: más barato en pesos en 97–99 % de las réplicas (ahorro mediano 53 / 43 / 14 %). Menos inclusión
pp en 76 / 92 / 98 % de las réplicas. Menos inclusión en pesos en 50 / 84 / 95 %: **con meta del 5 % y u1, M4 no
reduce la inclusión** (48 → 54 %). El rezago no intervenible no mueve las medianas (el costo sube en ≤ 13 % de
las réplicas).

### Curva costo–meta del 2 al 30 % (u1, 30 réplicas, 900 MILP óptimos; `resumen_barrido_v2.csv`, `barrido_v2.png`)

| Meta | M3 (mil mill.) | M4 | Ahorro M4 | Inclusión M3 / M4 |
|---|---|---|---|---|
| 2 % | 3,6 | 3,0 | 6 % (más barato en 60 %) | 40 / 44 % |
| 6 % | 12,5 | 6,2 | **53 %** | 55 / 55 % |
| 10 % | 22,9 | 13,4 | 35 % | 73 / 58 % |
| 16 % | 33,4 | 26,8 | 14 % | 75 / 62 % |
| 20 % | 44,7 | 37,7 | 16 % | 65 / 41 % |
| 30 % | 95,2 | 75,4 | 22 % | 40 / 38 % |

Costo convexo (~1,8 → ~5 mil millones por punto de M0). La ventaja de M4 no es monótona: es máxima con metas del
4–10 %, baja al 11–16 % entre el 16 y el 20 % y se recupera al ~22 % con metas altas. La inclusión tiene forma de
campana (pico de ~75 % en M3 entre el 10 y el 16 %). **El costo en pares con n < 10 es 0 % en las 900 corridas.**

### Objetivo de equidad (el del M1): 30 réplicas × B × ρ, u = 1

**Verificado:** reproduce `modelo3_equidad.py` (B = $500 mm, réplica 0: 419.550 personas, inclusión 42,6 %).
Personas que salen (mediana), con ρ = 0:

| B (mil mill.) | Info. perfecta | M3 | M4 | M3/IP | M4/IP | Inclusión M3/M4 | Severidad −: IP/M3/M4 |
|---|---|---|---|---|---|---|---|
| 10 | 139.968 | 35.000 | 61.400 | 25 % | 44 % | 51/52 % | 7,6/2,5/4,3 % |
| 25 | 205.291 | 79.900 | 109.000 | 39 % | 53 % | 62/62 % | 11,9/6,2/8,3 % |
| 50 | 286.428 | 147.000 | 159.000 | 51 % | 55 % | 61/43 % | 17,0/11,3/15,2 % |
| 100 | 400.969 | 210.000 | 233.000 | 52 % | 58 % | 40/39 % | 26,2/18,2/23,7 % |
| 200 | 545.651 | 319.000 | 325.000 | 58 % | 60 % | 41/38 % | 41,0/29,3/31,1 % |

M4 saca más personas que M3 en 90–97 % de las réplicas (razón mediana 1,78 → 1,02 al subir B). Con B = 25, el
p5–p95 de M3 va de 47 mil a 113 mil y el de M4 de 103 mil a 116 mil: **M4 además es más predecible**.
Con ρ = 10 %: es infactible con B = 10 en M3 y M4 (con IP es factible). Con B = 25 es factible en 0/30 réplicas
de M3 y en 6/30 de M4. Con B ≥ 50 es factible siempre.

### Sensibilidad a k en M4 (50 réplicas pareadas; `resumen_k.csv`, `calidad_k.csv`, `sensibilidad_k.png`)

| k | Silueta | η² pobreza | Pares n < 10 | Salen B = 10 (miles) | Salen B = 25 | Costo meta 10 % |
|---|---|---|---|---|---|---|
| M3 | — | — | 2 | 31,1 | 74,7 | 23,1 |
| 2 | 0,260 | 0,002 | 4 | 21,8 (× 0,71 vs M3) | 69,0 | 24,9 |
| 3 | 0,271 | 0,024 | 4 | 44,6 | 99,8 | 12,9 |
| **4** | 0,272 | 0,022 | 8 | **61,2** (× 1,92) | **107,6** | **13,6** |
| 5 | 0,277 | 0,027 | 14 | 61,4 | 115,7 | 12,5 |
| 6 | 0,274 | 0,031 | 16 | 64,7 | 117,4 | 11,8 |
| 8 | 0,283 | 0,061 | 26 | 76,2 | 123,2 | 9,1 |

La silueta no decide k (0,26–0,28). Con k = 2 (separa por tamaño del hogar, η² ≈ 0) M4 es **peor** que M3: la
información demográfica solo sirve si está correlacionada con la privación. Desde k = 4 la ganancia se aplana y crecen
las celdas chicas (Trampa 17). **k = 4 se defiende** por interpretabilidad + tamaño mínimo de celda.

### Hallazgos (narrativa de la sustentación)

- **Precio de la información:** con poca plata, M3 logra el 25 % de lo que lograría la información perfecta;
  con mucha, el 58 %.
- **M4 (tipo Sisbén) vale más cuando el presupuesto es escaso o la meta es modesta**, y reduce la varianza del resultado.
- **No cualquier información demográfica sirve:** k = 2 es peor que solo geografía. Lo que vale es la correlación
  de los rasgos con la privación.
- **Focalizar sin información individual tiene rendimientos decrecientes:** el costo por punto de M0 casi se triplica.
- La inclusión es alta (~40–75 %) con los dos objetivos. La exclusión es de 57–97 % según la meta.
- Los techos de severidad son lo que más se degrada sin información individual.
- M3 invierte sobre todo en la cabecera (salud, analfabetismo); M4 en el clúster de primera infancia (T3).
- El rezago casi nunca se elige.

Etiquetas de clúster (k-means, random_state 2026): T0 adultos sin dependientes (1.389, H 3,7 %),
T1 adultos mayores (1.038, 11,8 %), T2 con hijos escolares (849, 9,1 %), T3 primera infancia (456, 16,1 %).

Variantes de costo: `pp` = V = K = HS (como en 06; la cobertura usa HS **sin** HW y hay que declararlo); `u1` = V = HW,
K = EpF_j^zona·HW (tabla de Martín §4, millones de $ de 2025).

### Pares con muestra chica (pendiente #5, diagnosticado)

M3: 2 de 45 pares con n < 10 (`paredes` en centro poblado = 1 hogar; `trabajo_infantil` en centro poblado = 9).
M4 (k = 4): 8 de 57 pares (el mínimo: inasistencia y trabajo infantil en T1, con 2 hogares). El MILP no les asigna
gasto en ninguna corrida del barrido, así que **no hace falta fusionar celdas en el caso base**. Hay que volver a
revisarlo con los costos reales o si se cambia k.

## Lo que cambió en el equipo

**3-nov (tarde).** Martín **sigue sin subir nada** desde el 2-nov (`72c9d02`). `main` sigue en el 6-oct. No hay
código de M1 ni M2 en el repo.

**3-nov.** Martín no subió nada. Siguen sin existir `parametros.py`, `05_conteo_personas.py` y
`03_preparar_antioquia.py`. Jerónimo escribió "Notas de Jerónimo" en `CONTEXTO_DATOS.md`
y subió a `Modelo3` los `m34_*` del 3-nov.

**2-nov (commit `72c9d02`, solo documentación).**
- Rezago: con las reglas oficiales ningún niño sale del rezago en un año. Estrategias E0–E3; caso base sin E3,
  con cobertura obligatoria 6–15 + ρ_e = 14 % (≈ $105,8 mil millones); sensibilidad con E3: ρ_e = 20 %.
  Para M3/M4 → rezago no intervenible (**implementado el 3-nov**).
- `05_conteo_personas` cuenta u_ij para los 3.732 hogares. Pendiente: meta del M2 (¿M0 o H?), p de inasistencia
  (0,37 vs 0,50) y gap del solver.

**30-oct.** Martín subió `CONTEXTO_DATOS.md` (costos oficiales, reglas u_ij) con 7 preguntas. Las respuestas están
en el borrador de "Notas de Jerónimo" (en resumen: SevEdu ex post; objetivo del paper como base y la equidad como
puente; u = 1 en empleo como sensibilidad; inasistencia 3,0/p con p solo en el MC; conteo de no pobres
imprescindible; prefijo `m34_`; CLEI 3 ciclos y acueducto rural con fuente verificable).

### Duda técnica: unidades con los costos de Martín

Con `costo = EpF_j·u_ij·HW_i`, la cobertura debe ser V = u_ij·HW_i (misma unidad arriba y
abajo; Trampa 1). `m34_mecanismo.enumerar_cortes` ya acepta V y K por separado, y el ε no cambia.

## Para acordar con Martín (agenda de la próxima reunión)

| # | Tema | Propuesta de Jerónimo | Por qué importa |
|---|---|---|---|
| 1 | **M1 y M2 en el repo** (aunque sea con u = 1) | Esta semana | Sin ellos no hay comparación de los 4 modelos; mientras tanto, M3/M4 usan la referencia de información perfecta |
| 2 | **`parametros.py`, `conteo_pares.csv`, `03_preparar_antioquia.py`** | Fecha fija; si no llegan, M3/M4 se sustentan con u = 1 como limitación | Costos reales |
| 3 | **Objetivo de M3/M4** | El del paper como caso base; la equidad (ya hecha) como puente con el M1 | Define qué se compara |
| 4 | **Meta del Modelo 2: ¿sobre M0 o sobre H?** | Sobre M0, como el paper | Comparación M2 ↔ M3/M4 |
| 5 | **Caso base común**: p de inasistencia, solver y gap | p = 0,369; HiGHS; reportar el gap; `presolve="off"` como respaldo (T15) | Mismos supuestos |
| 6 | **Validar el M1 contra `info_perfecta.csv`** | Mismo B, u = 1 y rezago no intervenible → diferencia < 1 % | Detectar diferencias de supuestos |
| 7 | **Nombres de archivos y ramas** | Prefijo `m34_`; ¿cuándo se fusionan `Modelo3` y `Contexto` a `main`? | Evitar choques |
| 8 | **Rezago en M3/M4** | No intervenible (hecho); SevEdu ex post | Ya implementado |
| 9 | **Costos abiertos** | CLEI 3 ciclos; acueducto rural con fuente | Vivienda rural |
| 10 | **Tangentes 6.048 vs 6.571** | La diferencia (523) es por a = 0 | Sev0 comparable |
| 11 | **Pares no intervenibles** (columna `intervenible`) | `excluir` por par (T14: como constante en s_i) | Cobertura máxima |
| 12 | **Formato de la comparación final** | Tabla H, A, M0, severidad, costo por zona y total + la gráfica IP/M4/M3 | Diapositiva central |
| 13 | **Respuestas a sus 7 preguntas** | Pegar `notas_jeronimo_borrador.md` en "Notas de Jerónimo" | Martín no las ha visto |
| 14 | **Reparto de la sustentación** | Hilo: información perfecta → imperfecta → demográfica; fecha del ensayo | Quedan pocas semanas |

## Lo que sigue, en orden

1. **Hecho (3-nov):** "Notas de Jerónimo" escritas y `m34_*` del 3-nov en la rama `Modelo3`.
2. Cerrar con Martín los puntos 1–4 de la agenda.
3. Actualizar los PDF de selección de variables (T1, T13–T17, M4, equidad, k) y armar las diapositivas
   (tablas del 3-nov + `equidad_m3_m4_ip.png`, `sensibilidad_k.png`, `barrido_v2.png`).
4. Cambiar a costos reales cuando lleguen (V = u·HW, K = costo_ij) y repetir los dos MC y el barrido (~2,5 h de cómputo).
5. Volver a revisar los pares chicos (n < 10) con los costos reales.
6. Comparación final de los 4 modelos sobre el mismo universo.

## Decisiones abiertas

- Objetivo del caso base de M3/M4 (paper vs equidad). Ya están los dos implementados.
- Pesos w_j: solo como sensibilidad (múltiplos de 0,01).
- Valle de Aburrá: solo con los módulos ECV 2025 (catálogo 905) cruzados por `DIRECTORIO`. Descartado por ahora.
- Solver único: HiGHS (gap 1e-6 en el paper y en la etapa 1 de equidad, 1e-4 en la etapa 2); CBC solo para la regresión.
- k = 4 en M4 (defendido el 3-nov con la sensibilidad a k; k = 5 como alternativa).

## Entorno y cómo correrlo

```bash
R=data/DANE/DEPARTAMENTAL
python3 m34_test_regresion.py $R                                   # 630 cortes, 153,0, 62,1 %
python3 m34_montecarlo_lex.py $R 100 out/mc_lex                    # 800 tareas, ~85 min con 2 núcleos
python3 m34_correr_equidad.py $R 0 30 out/equidad_m34.csv 10 25 50 100 200   # ~30 min
python3 m34_referencia_info_perfecta.py $R out/info_perfecta.csv 10 25 50 100 200   # ~1 min
python3 m34_sensibilidad_k.py $R 50 out/sens_k                     # 350 tareas, ~13 min
python3 m34_resumen_k.py out/sens_k out/resumen_k.csv && python3 m34_grafica_k.py out/sens_k out/sensibilidad_k.png
python3 m34_barrido_metas_v2.py $R 30 out/barrido_v2               # 62 tareas, ~32 min
python3 m34_resumen_barrido_v2.py out/barrido_v2 out/resumen_barrido_v2.csv out/barrido_v2.png
python3 m34_pares_pequenos.py $R out/pares_pequenos.csv            # segundos
python3 m34_resumen_3nov.py out/mc_lex out/equidad_m34.csv out/info_perfecta.csv resultados/m34/mc_m3.csv resultados/m34/mc_m4.csv
python3 m34_grafica_equidad.py out/equidad_m34.csv out/info_perfecta.csv out/equidad_m3_m4_ip.png
```
- Entorno `opti1`: Python 3.10, PuLP 2.9.0 con CBC y HiGHS (`highspy`). También probado con PuLP 3.3.2 + highspy 1.x
  (Python 3.13). **No usar PuLP 4.x** (T16).
- `timeLimit` de CBC no es confiable; envolver el comando en `timeout` (en Mac: `perl -e 'alarm 240; exec @ARGV' ...`).
- CSV del DANE: separados por coma y en UTF-8 con BOM.

## Convenciones

- Nada derivado de los datos va hardcodeado (un `0.038684` literal es un bug; en `m34_datos` solo vive como assert).
- Los comentarios explican el porqué: son material de sustentación.
- Los cambios metodológicos se reflejan también en `Seleccion_Variables_Restricciones_Modelo3.pdf` / `Modelo4.pdf`.
- Repo compartido: no hacer commit ni push sin que Jerónimo lo pida; sin atribución de Claude.
- Documentos del Project "Opti1": `decision-fuente-de-datos`, `revision-formulacion-modelo3`,
  `bitacora-problemas-y-soluciones`, `bitacora-adenda-noviembre`, `resumen-avance-2nov`, `resumen-avance-3nov`,
  `resumen-avance-3nov-tarde`, `codigo-m34/`.

## Reglas de trabajo

- Este archivo resume `CONTEXTO_DATOS.md` y no lo reemplaza; ese archivo sigue siendo de Martín.
- Responder en español.
