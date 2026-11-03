# Modelos 3 y 4: focalización con información imperfecta (rama `Modelo3`)

> **Actualizado: 3-nov-2026, noche** (corrida automática programada, 21:00 UTC). Responsable: Jerónimo Vélez.
> Sustentación final: noviembre de 2026. Responder en español, paso a paso, revisando con rigor
> los Big-M y el Monte Carlo. Este archivo resume y **no reemplaza** `CONTEXTO_DATOS.md`
> (de Martín, rama `Contexto`). Copia anterior de este archivo (3-nov, mañana): `CLAUDE.md.bak`.
> La copia del 2-nov quedó en el Project: `claude/respaldo-CLAUDE-2nov.md`.
> Resumen de avance más reciente: `claude/resumen-avance-3nov-tarde.md` (Project "Opti1").

## 1. Qué es el proyecto y quién hace qué

Proyecto final de Optimización (Investigación de Operaciones, EAFIT). Se adaptan a Colombia los
cuatro modelos de Hamie, Hlasny & Jouni (2024), *Multidimensional Poverty Alleviation: Policy
Optimization and Impact Simulation* (ERF WP 1742). Son MILP que deciden dónde invierte el Estado para
bajar el IPM (Alkire-Foster, metodología DANE).

| | Información | Quién decide qué hogar recibe | Responsable |
|---|---|---|---|
| Modelo 1 / 2 | perfecta (ve M_ij hogar por hogar) | el optimizador | **Martín Quijano** |
| **Modelo 3** | imperfecta: solo agregados por **zona** (`P3`) | un sorteo (mecanismo estocástico) | **Jerónimo** |
| **Modelo 4** | imperfecta: zona para bienes públicos, **tipo de hogar (clúster)** para privados | sorteo | **Jerónimo** |

**Narrativa que hay que preservar:** M3 y M4 simulan la capacidad real del Estado para focalizar.
El Estado decide **cuánto** cubrir en cada par (indicador, grupo) y el sorteo decide **a quién** le
llega. Los errores de inclusión (gasto en no pobres) y de exclusión son el resultado de política,
no un defecto del modelo.

## 2. Datos: hechos verificados (test de regresión, no re-derivarlos)

Microdato oficial **IPM 2025 del DANE** (catálogo 903), versión DEPARTAMENTAL (87.060 hogares), en
`data/DANE/`. Ya trae los 15 indicadores. Se descartaron los módulos ECV 2023 porque no traen los
indicadores y no cruzan (intersección de `DIRECTORIO` = 0). Detalle: doc `decision-fuente-de-datos`.

| Hecho | Valor |
|---|---|
| Llave de hogar | `(DIRECTORIO, SECUENCIA_P)`; Martín usa `ID_HOGAR = DIRECTORIO_SECUENCIA_P` |
| Columna `IPM` | se reconstruye con los pesos anidados oficiales, error 2,2e-16 |
| Columna `POBRE` | idéntica a `IPM ≥ 1/3` |
| `FEXP` | `FEX_C * PERSONAS` = HS_i × HW_i |
| `P3` (VIVIENDAS) | 1 cabecera, 2 centro poblado, 3 rural disperso |
| Incidencia nacional / cabeceras / rural | 9,91 / 6,30 / 22,44 % (DANE: 9,9 / 6,3 / 22,4) |

- Pobre ⇔ puntaje ≥ 1/3; sale ⇔ puntaje ≤ 0,33 (los pesos son múltiplos de 0,01, así que es exacto).
- Pesos: educación 0,10 c/u; niñez 0,05 c/u; trabajo 0,10 c/u; salud 0,10 c/u; vivienda 0,04 c/u.
- **No hay municipio:** Medellín y el Valle de Aburrá son imposibles con esta base. Solo se
  recuperarían cruzando con la ECV 2025 (catálogo 905) por `DIRECTORIO`; descartado por ahora.
- No hay ingreso ni gasto en la base (relevante para el Modelo 4).

## 3. Escenario (universo común de los 4 modelos)

**Antioquia completa** (`DEPARTAMENTO == 5`), D = las 3 clases de `P3`.

| Zona | Hogares | Pobres | Personas pobres | H0 | A0 | M0 |
|---|---|---|---|---|---|---|
| Cabecera | 1.670 | 127 | 363.286 | 6,21 % | 40,58 % | 0,0252 |
| Centro poblado | 613 | 103 | 69.089 | 17,91 % | 38,56 % | 0,0691 |
| Rural disperso | 1.449 | 293 | 251.031 | 25,18 % | 42,11 % | 0,1060 |
| **Total** | **3.732** | **523** | **683.406** | **9,45 %** | **40,94 %** | **0,038684** |

- Población: 7.231.754 personas. Sev0 = 117.908.
- Pares activos M_ij = 1: 8.602; 45 pares (j, zona) en M3 y 57 pares (j, grupo) en M4.
- Por qué no Antioquia urbana: con un solo valor de `P3` hay una sola zona, E_jd colapsa a E_j y
  M3 = M1. Guarda `|D| ≥ 2` con `sys.exit`: no quitarla.
- **Caso base (desde el 3-nov): rezago escolar no intervenible** (decisión de Martín del 2-nov:
  ningún niño sale del rezago en un año). Se modela como constante en el puntaje (Trampa 14).

## 4. Archivos

| Archivo | Dónde | Rol |
|---|---|---|
| `utils_dane.py`, `02_validar_ipm.py`, `03_preparar_antioquia_urbana.py`, `04_linea_base.py` | `main` (Martín) | lectura, validación, subconjunto urbano, línea base |
| `00_verificar_base.py` | `Modelo3` | 7 chequeos de que la base sirve para M3/M4 |
| `05_modelo3.py` | `Modelo3` | MILP directo (R1–R7); constantes `IND`, `W`, `EPS`, `sortear_R`. Control de equivalencia |
| `06_modelo3_cortes.py` | `Modelo3` | objetivo del paper por cortes: min esfuerzo s.a. meta de M0 |
| `cortes.py`, `test_cortes.py` | `Modelo3` | mecanismo separado del objetivo (cobertura `V`, costo `K`, elegibilidad `elig`); T1–T3 |
| `modelo3_equidad.py`, `correr_m3_equidad.py`, `extremos_m3.py` | `Modelo3` | M3 con la equidad del M1, versión vieja (**ya verificada** por `m34_equidad.py`, que la reemplaza) |
| `costos_provisionales.py` | `Modelo3` | PROVISIONAL: u = 1 con la tabla de Martín. Se borra cuando exista `parametros.py` |
| `07_clusters.py` | `Modelo3` | k-means k = 4 del Modelo 4 |
| `m34_datos.py` | `Modelo3` | carga + línea base con asserts + sorteo R (idéntico a 05). Autocontenido |
| `m34_mecanismo.py` | `Modelo3` = versión 2-nov; **versión 3-nov solo en el Project** | cortes con `grupo` matriz n×J; la del 3-nov agrega `excluir=` (no intervenibles), `pobre0=` (cumNP), `desempate=True` y el reintento con `presolve="off"` |
| `m34_clusters.py` | `Modelo3` | k-means idéntico a 07 (reproduce 1.389 / 1.038 / 849 / 456) |
| `m34_montecarlo.py` | `Modelo3` | MC del 2-nov (sin desempate). Define `EPF`, `precios_u1`, `matriz_grupo` |
| `m34_optimos_alternos.py` | `Modelo3` | rango del error de inclusión entre óptimos alternos |
| `m34_test_regresion.py`, `m34_resumen_mc.py` | `Modelo3` | regresión contra 06 (630 cortes, 153,0, 62,1 %) y tabla/gráfica del MC del 2-nov |
| `resultados/m34/` | `Modelo3` | MC del 2-nov: `mc_m3.csv`, `mc_m4.csv`, `resumen_mc.csv`, `mc_m3_vs_m4.png`, `optimos_alternos_m*.csv` |
| `docs/m34_README.md` | `Modelo3` | cómo correr los `m34_*` |
| `m34_montecarlo_lex.py` | **solo Project** (`claude/codigo-m34/`) | MC con desempate × rezago {intervenible, no_intervenible}, Pool(2) |
| `m34_equidad.py`, `m34_correr_equidad.py` | **solo Project** | objetivo de equidad del M1 para M3 **y** M4 |
| `m34_referencia_info_perfecta.py` | **solo Project** | mismo objetivo de equidad con información perfecta (techo propio; **no** es el M1) |
| `m34_resumen_3nov.py`, `m34_grafica_equidad.py` | **solo Project** | tablas del MC lex y de equidad; gráfica `equidad_m3_m4_ip.png` |
| `m34_sensibilidad_k.py`, `m34_resumen_k.py`, `m34_grafica_k.py` | **solo Project** (3-nov tarde) | M4 con k ∈ {2,3,4,5,6,8}, 50 réplicas pareadas; equidad (B = 10, 25) + paper (meta 10 %, u1); silueta, CH, η² de pobreza; gráfica `sensibilidad_k.png` |
| `m34_barrido_metas_v2.py`, `m34_resumen_barrido_v2.py` | **solo Project** (3-nov tarde) | curva costo–meta 2–30 % (u1, 30 réplicas, desempate, rezago no intervenible); gráfica `barrido_v2.png` |
| `m34_pares_pequenos.py` | **solo Project** (3-nov tarde) | lista los pares (j, g) con pocos hogares privados |
| `notas_jeronimo_borrador.md` | **solo Project** | respuestas a las 7 preguntas de Martín, listas para pegar en "Notas de Jerónimo" |
| Resultados 3-nov (`resumen_mc_lex.csv`, `equidad_m34.csv`, `resumen_equidad.csv`, `info_perfecta.csv`, `resumen_3nov.txt`, `resumen_k.csv`, `calidad_k.csv`, `resumen_barrido_v2.csv`, `pares_pequenos.csv`) | **solo Project** | cifras de §7. Los PNG no están en el Project (son binarios): se regeneran en segundos |
| ~~`m34_barrido_sensibilidad.py`~~ + `barrido_sensibilidad.csv` | solo Project (2-nov) | **Reemplazado por `m34_barrido_metas_v2.py`.** Sus filas `no_intervenible` no sirven (Trampa 14) |

**Pendiente: copiar al repo (rama `Modelo3`) los archivos "solo Project" del 3-nov.** Hasta entonces,
el `m34_mecanismo.py` del repo no tiene `excluir=` ni `desempate=`.

Sin seguimiento en git (no subir): `.vscode/`, `Collaborator.txt`, `Soloparasercolaborador.txt`,
`hello.py`, `contexto_jeronimo/` (copia vieja del 29-oct), `data/processed/hogares_con_cluster.csv`,
`CLAUDE.md.bak`.

## 5. Formulación implementada

Notación: I hogares, J 15 indicadores, g(i, j) grupo del par. `Den_jg` = total de cobertura `V` de
los privados del grupo. Cobertura `p_jg = cumV(c) / Den_jg`. Sorteo `R_ij ~ U[0,1]`: el hogar sale
de la privación ⇔ `R_ij ≤ p_jg`.

**Hallazgo central: el Estado elige cuántos, no cuáles.** Dentro de (j, g) los curados son siempre
un prefijo del orden por R_ij. Un corte c es auto-consistente si `R_(c) ≤ p(c) ≤ R_(c+1) − ε`. Los
cortes factibles se enumeran antes de optimizar (630 en M3, 713 en M4). La propiedad solo usa el
orden de los R, así que vale con cualquier V > 0.

```
z[j,g,c] ∈ {0,1}  ∀ c ∈ F_jg
C1   Σ_c z[j,g,c] = 1
     cur_ij = elig_ij · Σ_{c ≥ rank_ij} z[j,g,c]
     s_i = Σ_j w_j M_ij − Σ_{j intervenible} w_j cur_ij        (lo no intervenible queda constante)
     Costo_jg = Σ_c cumK(c) · z[j,g,c]                         (incluye no pobres → inclusión)
R4   C_i + HS_i·HW_i·b1_i ≥ s_i·HS_i·HW_i                       ∀ i pobre
R5   C_i − HS_i·HW_i·b1_i ≤ s_i·HS_i·HW_i                       ∀ i pobre
R6   s_i − (1 − b1_i) ≤ 0,33                                    ∀ i pobre
R7   Σ_i C_i ≤ MPI_s·(1 − MPI_r)·Σ_i HS_i·HW_i                  (MPI_s = M0)
min  Σ_jg Costo_jg
Etapa 2 (desempate lexicográfico): min Σ cumNP·z  s.a.  Σ Costo ≤ E*·(1 + 1e-6)
```

- **M3:** g(i, j) = zona `P3`. **M4:** g(i, j) = zona si j ∈ V, clúster si j ∈ U.
- Equivalente a la formulación directa de `05_modelo3.py` (misma región factible; en una muestra de
  600 hogares da el mismo óptimo, 20,0, y es 22,6× más rápida; en la base completa, 2,1 s vs > 200 s).
- Big-M de R4/R5 = HS_i·HW_i por hogar; los demás M valen 1. b1_i y C_i solo para los 523 pobres.
- La lógica Big-M del Apéndice 1 del paper (Lin 6–10) se verificó rama por rama y es correcta; lo que
  se corrigió fueron unidades, desigualdades estrictas, el M global y MPI_s (doc `revision-formulacion-modelo3`).

**Variantes de costo:** `pp` = V = K = HS (como 06; la cobertura usa HS **sin** HW y hay que
declararlo); `u1` = V = HW, K = EpF_j^zona·HW (tabla de Martín §4, millones de $ de 2025). Con los
costos reales de Martín: V = u_ij·HW_i y K = EpF_j·u_ij·HW_i (misma unidad arriba y abajo; el ε no cambia).

### 5.1 Objetivo de equidad (`m34_equidad.py`, numeración del Modelo 1)

`p_i = HW_i·HS_i`; `s_i` como arriba, para i pobre al inicio.

```
Etapa 1  max Σ p_i y_i
Etapa 2  min Σ p_i q_i   s.a. Σ p_i y_i ≥ H*·(1 − 1e-7)
(1) Σ_jg Costo_jg ≤ B
(2) s_i ≤ 0,33 + M_i(1 − y_i),   M_i = s_i^0 − 0,33
(4) Σ_{i∈d} p_i y_i ≥ r·Pobres_d^0
(7) q_i ≥ 2a·s_i − a²   ∀a ∈ A_i, a > 0
(8) Σ p_i q_i ≤ (1 − ρ)·Sev0
```

SevEdu (9) no está implementada: necesita un sorteo por niño. `metricas` recalcula todo desde los
cortes elegidos y no confía en `y` ni en `q`. Es la misma función para M3 y M4 (recibe la matriz de grupo).

## 6. Trampas ya corregidas: NO revertirlas

1. **Unidades de p_jd:** numerador y denominador en la misma unidad. Con hogares abajo y personas
   arriba, p_jd llegaba a 4,81, el sorteo quedaba inerte y M3 = M1.
2. **MPI_s es M0 (0,038684), no H0.** Con H0 el esfuerzo da 0. Nunca hardcodearlo.
3. **Desigualdades estrictas:** `< 1/3` ⇔ `≤ 0,33` exacto; umbral estocástico `≤ R − ε`, con
   ε = 1e-6 en 05 y en la enumeración de cortes. Si cambia uno, cambia el otro.
4. **Big-M ajustado por hogar.** Nada de M global: CBC no cierra el gap.
5. **N_ij ≡ b2_ij:** b2 y b3 eliminadas. Solo los pares con M_ij = 1 llevan variable.
6. **`C_i` con `lowBound=0`.** Si es libre, la meta se cumple trivialmente.
7. **No inline-ar expresiones grandes** dentro de bucles de restricciones: PuLP se colgaba.
8. **Cotas inferiores de esfuerzo desactivadas** (causa #1 de infactibilidad: `paredes` en centro
   poblado tiene 1 hogar privado).
9. **Semilla de R_ij derivada del hogar:**
   `np.random.SeedSequence([SEMILLA, replica, DIRECTORIO, SECUENCIA_P])`, SEMILLA = 2026. No cambiar
   a `rng.random((n,15))`.
10. **Guarda `|D| ≥ 2`.**
11. **Gap de HiGHS por etapa** en equidad: 1e-6 (etapa 1) y 1e-4 (etapa 2).
12. **Submuestras solo para depurar,** nunca para resultados (estratificar zona × pobreza).
13. **Óptimos alternos** (cerrada el 3-nov): con el esfuerzo en personas-privación hay empates
    (réplica 0, meta 5 %: inclusión de 41,7 a 61,7 % con el mismo esfuerzo, 60,0). Se resuelve con
    `desempate=True`. Impacto: la inclusión baja en 3–14 % de las réplicas `pp` y en 0 % de las u1.
14. **(3-nov) Indicadores no intervenibles = constante en el puntaje.** Si s_i solo suma los pares
    con variable, excluir un indicador lo "cura" gratis (M4 cumplía metas del 5–10 % con costo 0).
    Usar `s_i = w·M_i − Σ w_j cur_ij`. Las filas `no_intervenible` del barrido del 2-nov no sirven.
15. **(3-nov) Falso infactible del presolve de HiGHS en la etapa 2** (12/2.400 corridas del paper y
    2/300 de equidad), aunque la solución de la etapa 1 sea factible. Reintentar con
    `presolve="off"`; ya está en `m34_mecanismo` y `m34_equidad` (versión del Project).
16. **(3-nov) PuLP 4.x rompe `LpVariable(cat=...)`.** Instalar con `requirements.txt` (`pulp<4`).
17. **Clústeres sin privaciones:** el k-means usa solo variables que el Estado observa (tamaño,
    composición por edades, dependencia, edad/sexo/educación del jefe). Agrupar por privaciones
    contradice el supuesto de información imperfecta.
18. **(3-nov tarde) Un k grande en M4 simula información individual.** Con k = 8 hay 26 pares
    (j, clúster) con menos de 10 hogares privados y un clúster de solo 81 hogares. En un par de 1–3
    hogares el corte equivale a escoger hogar por hogar. La "ganancia" de subir k más allá de 4 es en
    buena parte un artefacto de la muestra. **No presentar k = 8 como mejor.** Regla: menos del 15 %
    de los pares con n < 10 (k = 4: 8/53; k = 5: 14/64).

## 7. Estado y resultados (3-nov-2026, noche)

**M3 y M4 técnicamente completos con u = 1:** objetivo del paper + MC con desempate, objetivo de
equidad + MC, referencia de información perfecta, **sensibilidad a k**, **curva costo–meta del 2 al
30 %** y diagnóstico de los pares chicos. Lo que falta depende de Martín (costos reales, M1/M2 en el
repo) o es redacción (PDF y diapositivas). Regresión vigente: 630 cortes, 153,0 e inclusión 62,1 %,
con HiGHS y con CBC.

### 7.1 Verificaciones de base (1-nov, entorno `opti1`, CBC)

| Prueba | Resultado |
|---|---|
| `test_cortes.py` T1 | 45 pares, 630 cortes, mismos cortes que 06, objetivo 153,0 |
| `test_cortes.py` T2 | 511 cortes con pesos aleatorios, 0 inconsistentes |
| `test_cortes.py` T3 | celda Cabecera: 243/243 cubiertos, 243 siguen privados, costo 953 |
| `correr_m3_equidad.py capa0` | 523 pobres, H0 = 9,45 %, Sev0 = 117.908, 518 cortes con u = 1 |
| Costo de cubrir todo (u = 1) | $29.358 mm, de los cuales $8.946 mm en hogares pobres |

**Tangentes:** el código da 6.048 y Martín 6.571. La diferencia es exactamente 523 (hogares pobres)
porque el código omite a = 0. Falta confirmarlo con Martín.

### 7.2 Objetivo del paper: MC con desempate, rezago no intervenible (3-nov)

2.400 MILP (100 réplicas × 3 metas × 2 costos × 2 modelos × 2 versiones de rezago), todos óptimos.
Mediana [p5; p95]. Inclusión en personas con `pp` y en pesos con u1.

| Meta | Modelo | Esfuerzo pp | Inclusión pp | Costo u1 (mil mill. $) | Inclusión u1 | Exclusión |
|---|---|---|---|---|---|---|
| 5 % | M3 | 83 [42; 124] | 56 % [29; 76] | 12,2 [6,4; 17,4] | 48 % [24; 77] | 94 % |
| 5 % | M4 | 57 [30; 79] | 41 % [16; 64] | 6,0 [3,2; 6,6] | 54 % [24; 61] | 92–94 % |
| 10 % | M3 | 164 [115; 223] | 64 % [44; 79] | 23,5 [15,0; 32,9] | 74 % [39; 78] | 86–88 % |
| 10 % | M4 | 132 [92; 162] | 44 % [22; 56] | 13,4 [10,3; 16,9] | 57 % [28; 68] | 87–88 % |
| 20 % | M3 | 364 [303; 420] | 62 % [45; 70] | 44,3 [40,4; 47,8] | 65 % [56; 67] | 74 % |
| 20 % | M4 | 346 [292; 385] | 36 % [27; 50] | 38,3 [33,5; 41,9] | 41 % [28; 61] | 72 % |

- **Pareado M4 vs M3 (misma R):** más barato en pesos en 97–99 % de las réplicas (ahorro mediano
  53 / 43 / 14 %); con `pp`, en 83 / 85 / 73 %. Menos inclusión pp en 76 / 92 / 98 %; en pesos, en
  50 / 84 / 95 %. **Con meta del 5 % y u1, M4 no reduce la inclusión (48 → 54 %): hay que decirlo.**
- El desempate casi no cambia las medianas (solo M3 pp 5 %: 59 → 56 %). El MC del 2-nov sigue en pie.
- Rezago no intervenible: el costo sube en 0–13 % de las réplicas; mediana +0,0 %.
- Azar: el CV del esfuerzo de M3 baja de 32 % (meta 5 %) a 10 % (meta 20 %). Exclusión del 72 al 94 %:
  con metas pequeñas sobre M0, la mayoría de los pobres no recibe nada.
- M3 invierte casi todo en la cabecera (salud y analfabetismo); M4, en el clúster de primera infancia (T3).
- Corrección ya hecha: "la inclusión crece con la meta" salía de una sola réplica; en el MC tiene forma de campana (§7.5).

### 7.3 Objetivo de equidad (el del M1): M3 vs M4 vs información perfecta (3-nov)

**Verificado:** `m34_equidad.py` reproduce `modelo3_equidad.py` (B = $500 mm, réplica 0: 419.550
personas, inclusión 42,6 %). 30 réplicas, u = 1, rezago no intervenible, ρ = 0. Personas que salen
(mediana); hay 683.406 personas pobres.

| B (mil mill. $) | Info. perfecta | M3 | M4 | M3/IP | M4/IP | Inclusión M3/M4 | Severidad −: IP/M3/M4 |
|---|---|---|---|---|---|---|---|
| 10 | 139.968 | 35.000 [24k; 64k] | 61.400 [55k; 70k] | 25 % | 44 % | 51/52 % | 7,6/2,5/4,3 % |
| 25 | 205.291 | 79.900 [47k; 113k] | 109.000 [103k; 116k] | 39 % | 53 % | 62/62 % | 11,9/6,2/8,3 % |
| 50 | 286.428 | 147.000 [141k; 152k] | 159.000 [151k; 169k] | 51 % | 55 % | 61/43 % | 17,0/11,3/15,2 % |
| 100 | 400.969 | 210.000 [201k; 223k] | 233.000 [228k; 239k] | 52 % | 58 % | 40/39 % | 26,2/18,2/23,7 % |
| 200 | 545.651 | 319.000 [313k; 329k] | 325.000 [320k; 333k] | 58 % | 60 % | 41/38 % | 41,0/29,3/31,1 % |

- M4 saca más personas que M3 en 90–100 % de las réplicas; razón mediana 1,78 / 1,37 / 1,09 / 1,10 / 1,02.
- **ρ = 10 %:** infactible con B = 10 en M3 y M4 (0/30; con IP sí es factible). Con B = 25: 0/30
  en M3 y 6/30 en M4. Con B ≥ 50 siempre es factible y no está activo.

### 7.4 Sensibilidad a k en M4 (3-nov tarde; 50 réplicas pareadas, 1.050 MILP óptimos)

Mismas R para todos los k y para M3. Rezago no intervenible, u = 1. Mediana; `resumen_k.csv`,
`calidad_k.csv`, `sensibilidad_k.png`.

| k | Silueta | η² pobreza | Pares n < 10 | Salen B = 10 (miles) | Salen B = 25 | M4/M3 (B = 10) | Costo meta 10 % (mil mill.) |
|---|---|---|---|---|---|---|---|
| M3 | — | — | 2 | 31,1 [25; 61] | 74,7 [46; 112] | 1,00 | 23,1 |
| 2 | 0,260 | 0,002 | 4 | 21,8 [13; 56] | 69,0 [32; 108] | **0,71** | 24,9 |
| 3 | 0,271 | 0,024 | 4 | 44,6 [18; 70] | 99,8 [88; 115] | 1,19 | 12,9 |
| **4** | 0,272 | 0,022 | 8 | **61,2 [53; 70]** | **107,6 [103; 118]** | **1,92** | **13,6** |
| 5 | 0,277 | 0,027 | 14 | 61,4 [55; 74] | 115,7 [104; 123] | 1,93 | 12,5 |
| 6 | 0,274 | 0,031 | 16 | 64,7 [56; 78] | 117,4 [109; 126] | 1,99 | 11,8 |
| 8 | 0,283 | 0,061 | **26** | 76,2 [72; 90] | 123,2 [119; 133] | 2,44 | 9,1 |

- **La silueta no decide k** (0,26–0,28): los rasgos tipo Sisbén no forman grupos naturales, así que
  elegir k es una **decisión de política** (qué tan fino es el sistema de información del Estado).
- **k = 2 es peor que M3:** ese k-means separa por tamaño del hogar (η² ≈ 0). La información
  demográfica solo sirve si está correlacionada con la privación.
- Desde k = 4 la ganancia se aplana y crecen las celdas chicas (Trampa 18). **k = 4 se defiende** por
  interpretabilidad + tamaño mínimo de celda; k = 5 queda como alternativa.

### 7.5 Curva costo–meta del 2 al 30 % (3-nov tarde; u1, 30 réplicas, 900 MILP óptimos)

`resumen_barrido_v2.csv` (15 metas) y `barrido_v2.png`. Reemplaza al barrido del 2-nov.

| Meta | Costo M3 (mil mill.) | Costo M4 | Ahorro M4 (mediano) | M4 más barato | Inclusión M3 / M4 | Exclusión M3 / M4 |
|---|---|---|---|---|---|---|
| 2 % | 3,6 | 3,0 | 6 % | 60 % | 40 / 44 % | 97 / 97 % |
| 6 % | 12,5 | 6,2 | **53 %** | 97 % | 55 / 55 % | 92 / 92 % |
| 10 % | 22,9 | 13,4 | 35 % | 97 % | 73 / 58 % | 86 / 87 % |
| 16 % | 33,4 | 26,8 | 14 % | 93 % | 75 / 62 % | 79 / 79 % |
| 20 % | 44,7 | 37,7 | 16 % | 100 % | 65 / 41 % | 74 / 71 % |
| 26 % | 74,3 | 56,9 | 24 % | 100 % | 47 / 45 % | 64 / 63 % |
| 30 % | 95,2 | 75,4 | 22 % | 100 % | 40 / 38 % | 58 / 57 % |

- **Costo convexo:** el punto de M0 cuesta ~1,8 mil millones al principio y ~5 mil millones entre el
  26 y el 30 %. Cuando se acaban los pares baratos toca comprar vivienda.
- **La ventaja de M4 no es monótona:** es máxima con metas del 4–10 % (35–53 %), cae al 11–16 % entre
  el 16 y el 20 % y sube otra vez al ~22 % con metas altas.
- **Inclusión en forma de campana**, con un pico de ~75 % en M3 entre el 10 y el 16 %. En ese tramo M4
  es el que más la reduce (−18 a −24 puntos con metas del 18–22 %).
- Reproduce el MC del 3-nov: meta 10 % → 22,9 vs 23,5; meta 20 % → 44,7 vs 44,3 (M3).

### 7.6 Pares con muestra chica (pendiente #5: diagnosticado el 3-nov tarde)

- M3: 2 de 45 pares con n < 10 (`paredes` en centro poblado, 1 hogar; `trabajo_infantil` en centro poblado, 9).
- M4 (k = 4): 8 de 57 pares (los más chicos: inasistencia y trabajo infantil en T1, con 2 hogares;
  hacinamiento en T0, 3 hogares sin pobres).
- **Impacto medido: 0 %.** En las 900 corridas del barrido el MILP no gasta nada en pares con n < 10.
  No hace falta fusionar celdas en el caso base. Hay que volver a revisarlo con los costos reales o si se cambia k.

### 7.7 Hallazgos para la sustentación

1. **Precio de no tener información:** con $10 mil millones M3 logra el 25 % de lo que lograría la
   información perfecta; con $200 mil millones, el 58 %.
2. **La focalización demográfica (M4, tipo Sisbén) vale más cuando la plata es poca o la meta es
   modesta** (× 1,78 con B = 10 y × 1,02 con B = 200; ahorro máximo de 53 % con metas del 4–10 %).
3. **M4 además es más predecible:** con B = 25 el p5–p95 de M3 va de 47 mil a 113 mil personas; el de
   M4, de 103 mil a 116 mil.
4. **No cualquier información demográfica sirve:** k = 2 es peor que focalizar solo por geografía.
5. **Focalizar sin información individual tiene rendimientos decrecientes:** el costo por punto de M0
   casi se triplica a lo largo de la curva.
6. **Los techos de severidad son lo que más se degrada** sin información individual.
7. **La inclusión es alta (~40–75 %) con ambos objetivos:** la filtración a no pobres es el costo
   estructural de focalizar sin información individual. M4 no domina a M3 por construcción, porque la
   demografía es un proxy.
8. El rezago casi nunca se elige; tratarlo como no intervenible no mueve los resultados.

Hilo sugerido de la exposición: (1) información perfecta (techo) → (2) M3, solo geografía → (3) M4,
geografía + demografía. Gráficas: `equidad_m3_m4_ip.png` (diapositiva central), `sensibilidad_k.png`
y `barrido_v2.png`.

## 8. Modelo 4

- Partición: **V (bienes públicos, por zona) = {acueducto, alcantarillado}**; **U = los otros 13, por
  clúster**. Validada: acueducto discrimina 14,5× por zona y 4,1× por clúster; alcantarillado 4,7× y
  3,2×; atención integral 2.119×, inasistencia 51,7× y hacinamiento 26,6× por clúster.
- k-means, `random_state` 2026, **k = 4**. El codo apunta a 5 y la silueta es plana (0,26–0,28). Se
  defendió el 3-nov tarde con la sensibilidad a k (§7.4): k = 2 es peor que M3, la ganancia se aplana
  desde k = 4 y con k ≥ 5 crecen los pares de 1–3 hogares (Trampa 18).
- Clústeres: T0 adultos sin dependientes (1.389, H 3,7 %), T1 adultos mayores (1.038, 11,8 %), T2 con
  hijos escolares (849, 9,1 %), T3 primera infancia (456, 16,1 %). Separan la pobreza 4,3× sin usarla.
  Honestidad: parte es estructural (la atención integral solo aplica a hogares con menores de 5).
- MILP: el mismo de §5 con `grupo` matriz n×J; 57 pares, 713 cortes, 1–6 s.
- Hecho el 3-nov: M4 con el objetivo de equidad, MC con desempate, sensibilidad a k y curva costo–meta.

## 9. Respuestas a las preguntas de Martín (§8 de `CONTEXTO_DATOS.md`)

Borrador de Jerónimo, **listo para pegar** en `claude/codigo-m34/notas_jeronimo_borrador.md`. **Siguen
sin escribirse en "Notas de Jerónimo"** de `CONTEXTO_DATOS.md` (vacía al 3-nov, noche).

1. **SevEdu:** sí, primero como métrica ex post en el MC de M3/M4. El sorteo por niño rompe el prefijo
   por hogar; como techo con ρ_e = 14 % queda como trabajo futuro.
2. **Objetivo:** el del paper (min costo s.a. meta de M0) como caso base de M3/M4, porque mide
   inclusión y exclusión; la equidad (ya implementada para M3 y M4) como puente con el M1. Comparación
   ex post en H, A, M0, severidad, SevEdu y costo, por zona y total.
3. **u_ij = 1 en empleo:** como sensibilidad, no como caso base.
4. **Inasistencia:** costo 3,0/p en la optimización; el cumplimiento p solo en el MC de evaluación.
5. **Conteo de no pobres en el 05:** imprescindible (es el error de inclusión). Martín ya confirmó que
   cuenta los 3.732 hogares.
6. **`parametros.py`:** importar de ahí `IND`, `W` y la semilla; los archivos de Jerónimo usan el
   prefijo `m34_` (resuelve el choque con `05_conteo_personas.py`).
7. **Costos:** logro = 3 ciclos CLEI (base); acueducto rural de $43,7 M solo con fuente verificable, y
   el BID ($9,7 M) como sensibilidad.

Preguntas de Jerónimo a Martín: u_ij para no pobres → **respondida** (sí). Meta del M2 sobre M0 o H →
**pendiente**. p de inasistencia (0,369 vs 0,50) y gap del caso base → **pendiente**.

## 10. Decisiones abiertas

1. **Objetivo del caso base de M3/M4** (paper vs equidad). Los dos están implementados; propuesta: paper.
2. **Meta del Modelo 2 sobre M0 o sobre H.** Si es H, la comparación M2 ↔ M3/M4 no cuadra.
3. **Caso base común:** p = 0,369 (propuesta) vs 0,50; HiGHS con el gap reportado por corrida
   (1e-6 en el paper y la etapa 1, 1e-4 en la etapa 2; `presolve="off"` de respaldo); CBC solo para la
   regresión. Martín usa 1e-4.
4. **Validar el M1 de Martín contra `info_perfecta.csv`** (mismo B, u = 1, rezago no intervenible):
   una diferencia > 1 % indica diferencia de supuestos (rezago, empleo, tangentes).
5. **Pares no intervenibles** (columna `intervenible`): `excluir` por par, como constante en s_i (T14).
6. **Denominador pequeño:** diagnosticado sin impacto en el caso base (§7.6). Revisar con costos reales.
7. **Pesos w_j:** solo como sensibilidad, en los 4 modelos a la vez y en múltiplos de 0,01.
8. **k en M4:** k = 4 (defendido); k = 5 como alternativa.
9. **Cuándo se fusionan `Modelo3` y `Contexto` a `main`.**

## 11. Lo que sigue, en orden

1. **Jerónimo (a mano):** pegar `notas_jeronimo_borrador.md` en "Notas de Jerónimo" (rama `Contexto`)
   y copiar a la rama `Modelo3` los `m34_*` y resultados del 3-nov que están en el Project; luego
   commit y push.
2. **Con Martín, con fecha límite:** M1 y M2 en el repo (aunque sea con u = 1), `parametros.py`,
   `05_conteo_personas.py` (`conteo_pares.csv`, `empleo_componentes.csv`, `ninos_rezago.csv`),
   `03_preparar_antioquia.py` y la meta del M2 (sobre M0). Si no llegan, sustentar M3/M4 con u = 1
   como limitación declarada y usar `info_perfecta.csv` como sustituto provisional del M1.
3. Actualizar `Seleccion_Variables_Restricciones_Modelo3.pdf` / `Modelo4.pdf` (carpeta Opti1, un nivel
   arriba) con T1, T13–T18, M4, equidad y k; verificar contra el Apéndice 1 del paper el error de
   unidades de p_jd.
4. Diapositivas con las tablas de §7 y las gráficas `equidad_m3_m4_ip.png`, `sensibilidad_k.png` y
   `barrido_v2.png`.
5. Cuando lleguen los costos reales (V = u·HW, K = costo_ij): repetir los dos MC y el barrido
   (~2,5 h con 2 núcleos) y revisar otra vez los pares chicos.
6. Comparación final de los 4 modelos: tabla común H, A, M0, severidad, SevEdu y costo, por zona y
   total, con la misma meta para M2, M3 y M4. Reparto de la sustentación y fecha del ensayo.

## 12. Entorno y cómo correrlo

Correr desde la raíz del repo (los scripts viejos cargan `05_` y `06_` por ruta relativa).

```bash
PY=/opt/anaconda3/envs/opti1/bin/python
R=data/DANE/DEPARTAMENTAL
$PY test_cortes.py
$PY 06_modelo3_cortes.py 0.10          # producción + control de equivalencia ("solo" = sin control)
$PY m34_test_regresion.py $R                                       # 630 cortes, 153,0, 62,1 %
$PY m34_montecarlo.py $R m3 0 100 out/mc_m3.csv                    # MC 2-nov, ~25 s/réplica
# Scripts del 3-nov (hoy solo en el Project, claude/codigo-m34/):
$PY m34_montecarlo_lex.py $R 100 out/mc_lex                        # 800 tareas, ~85 min con 2 núcleos
$PY m34_correr_equidad.py $R 0 30 out/equidad_m34.csv 10 25 50 100 200    # ~30 min
$PY m34_referencia_info_perfecta.py $R out/info_perfecta.csv 10 25 50 100 200   # ~1 min
$PY m34_sensibilidad_k.py $R 50 out/sens_k                         # 350 tareas, ~13 min
$PY m34_resumen_k.py out/sens_k out/resumen_k.csv && $PY m34_grafica_k.py out/sens_k out/sensibilidad_k.png
$PY m34_barrido_metas_v2.py $R 30 out/barrido_v2                   # 62 tareas, ~32 min
$PY m34_resumen_barrido_v2.py out/barrido_v2 out/resumen_barrido_v2.csv out/barrido_v2.png
$PY m34_pares_pequenos.py $R out/pares_pequenos.csv                # segundos
$PY m34_resumen_3nov.py out/mc_lex out/equidad_m34.csv out/info_perfecta.csv resultados/m34/mc_m3.csv resultados/m34/mc_m4.csv
$PY m34_grafica_equidad.py out/equidad_m34.csv out/info_perfecta.csv out/equidad_m3_m4_ip.png
```

- `opti1`: Python 3.10.18, PuLP 2.9.0 con CBC y HiGHS (`highspy`). `requirements.txt`:
  `pulp>=2.9,<4`, `highspy>=1.7`. También probado con PuLP 3.3.2 + highspy (Python 3.13).
- El `python3` por defecto trae PuLP 4.0.0 sin solvers: no usarlo (T16).
- El `timeLimit` de CBC no es confiable y este Mac no tiene `timeout`: `perl -e 'alarm 240; exec @ARGV' <cmd>`.
- CSV del DANE: coma y UTF-8 con BOM. `utils_dane.leer()` lo detecta; no hardcodear.

## 13. Convenciones

- Nada derivado de los datos va hardcodeado: un `0.038684` literal es un bug (en `m34_datos` solo vive como assert).
- Los comentarios explican el porqué y son material de sustentación: ampliarlos, no limpiarlos.
- Cambios metodológicos (umbral, pesos, D, k) → también en los PDF de selección de variables.
- Con Martín: y_i = 1 ⇔ el hogar **sale**; HW_i siempre multiplica el costo, HS_i nunca (las personas
  ya están en u_ij); reportar H, A, M0 y severidad por zona `P3` y total; sensibilidades mínimas
  compartidas: caso base y u_ij = 1.
- Repo compartido: **no hacer commit, push, pull, fetch ni cambiar de rama sin que Jerónimo lo pida.**
  Jerónimo hace los commits a mano. Sin atribución de Claude en los commits.
- Problemas relevantes resueltos → `bitacora-problemas-y-soluciones.md` y
  `bitacora-adenda-noviembre.md` (Project "Opti1").
- Docs del Project: `decision-fuente-de-datos`, `revision-formulacion-modelo3`,
  `bitacora-problemas-y-soluciones`, `bitacora-adenda-noviembre`, `resumen-avance-2nov`,
  `resumen-avance-3nov`, `resumen-avance-3nov-tarde`, `CLAUDE-contexto-pendiente-de-push`,
  `respaldo-CLAUDE-2nov`, `codigo-m34/`.

## 14. Cambios de Martín que pueden modificar el plan

Revisión del 3-nov-2026, 21:00 UTC, sobre las referencias locales del clon. No se hizo fetch: el
último fetch es del 3-nov a las 00:56 UTC, así que lo que Martín haya subido después no se ve aquí.

| Rama | Último commit | Autor |
|---|---|---|
| `main` / `origin/main` | `91e7b97` (6-oct) | Martín |
| `Contexto` / `origin/Contexto` | `8bd01d1` (1-nov) | Jerónimo. El último cambio a `CONTEXTO_DATOS.md` es `72c9d02` (2-nov, solo documentación, ya incorporado) |
| `Modelo3` / `origin/Modelo3` | `055be94` (1-nov) | Jerónimo |

- `parametros.py`, `05_conteo_personas.py` y `03_preparar_antioquia.py` siguen sin existir en ninguna
  rama, y **no hay código de M1 ni M2**.
- `CONTEXTO_DATOS.md` no cambió desde `72c9d02`; su §8 sigue con la meta del M2, la p de inasistencia y
  el gap pendientes, y "Notas de Jerónimo" sigue vacía.
- No hay archivos `NOTAS_*.md` en el repo.

**Sin cambios relevantes** desde la última revisión (3-nov, tarde).

Riesgo que se mantiene (no es un cambio, pero condiciona el plan): sin M1/M2 en el repo no hay
comparación oficial de los 4 modelos; mientras tanto, M3/M4 se comparan con `info_perfecta.csv`.

Lo ya incorporado del 2-nov, por si hay que recordarlo:

| Cambio | Por qué afecta a M3/M4 | Ajuste |
|---|---|---|
| Rezago: ningún niño sale en un año; estrategias E0–E3; ρ_e = 14 % (base) / 20 % (con E3) | El rezago deja de curarse con un año regular | **Hecho (3-nov):** rezago no intervenible como caso base, constante en s_i (T14); impacto en las medianas +0,0 % |
| u_ij para los 3.732 hogares | Permite medir la inclusión en pesos | Usar V = u·HW y K = costo_ij cuando llegue `conteo_pares.csv` |
| p de inasistencia 0,37 (0,50 y 0,75 como sensibilidad) | Cambia el costo de inasistencia (3,0/p) | Los MC usan 0,369; confirmarlo como caso base |
