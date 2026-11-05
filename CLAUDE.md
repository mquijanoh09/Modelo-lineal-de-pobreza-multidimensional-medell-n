# Modelos 3 y 4: focalización con información imperfecta (rama `Modelo3`)

> **Actualizado: 4-nov-2026, tarde** (corrida automática programada, 19:48 UTC). Responsable: Jerónimo Vélez.
> Sustentación final: noviembre de 2026. Responder en español, paso a paso, revisando con rigor
> los Big-M y el Monte Carlo. Este archivo resume y **no reemplaza** `CONTEXTO_DATOS.md`
> (de Martín, rama `Contexto`). Copia anterior de este archivo (3-nov, noche): `CLAUDE.md.bak`.
> Copia del 2-nov en el Project: `claude/respaldo-CLAUDE-2nov.md`.
> Resúmenes más recientes (Project "Opti1"): `claude/resumen-avance-4nov.md` (costos reales) y
> `claude/auditoria-m34-3nov.md` (auditoría con hallazgos abiertos, §7.0).

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
- **(4-nov) Reglas de conteo u_ij validadas contra la bandera del DANE** en los 87.060 hogares
  (`m34_costos_reales.py`): analfabetismo (≥ 15 años y `P6160 = 2`), aseguramiento (≥ 6 años y
  `P6090 ≠ 1`) y barreras (`P5665 = 1` y `P8563 ≥ 3`) coinciden al 100 %; logro educativo (≥ 15 años
  con < 9 años de educación) cubre el 99,5 % de los privados; atención integral (niños de 0 a 5) el
  100 %; desempleo (`P6351 = 1`, no ocupados, mínimo 1) da 86,5 %, igual que Martín.

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
- **Caso base: rezago escolar no intervenible** (decisión de Martín del 2-nov: ningún niño sale del
  rezago en un año). Se modela como constante en el puntaje (Trampa 14).
- **Costos del caso base (propuesta del 4-nov):** costos reales provisionales (u_ij reconstruido,
  §7.8); u = 1 como sensibilidad. Pendiente de confirmar con Martín (§10).

## 4. Archivos

| Archivo | Dónde | Rol |
|---|---|---|
| `utils_dane.py`, `02_validar_ipm.py`, `03_preparar_antioquia_urbana.py`, `04_linea_base.py` | `main` (Martín) | lectura, validación, subconjunto urbano, línea base |
| `00_verificar_base.py` | `Modelo3` | 7 chequeos de que la base sirve para M3/M4 |
| `05_modelo3.py` | `Modelo3` | MILP directo (R1–R7); constantes `IND`, `W`, `EPS`, `sortear_R`. Control de equivalencia |
| `06_modelo3_cortes.py` | `Modelo3` | objetivo del paper por cortes: min esfuerzo s.a. meta de M0 |
| `cortes.py`, `test_cortes.py` | `Modelo3` | mecanismo separado del objetivo (cobertura `V`, costo `K`, elegibilidad `elig`); T1–T3 |
| `modelo3_equidad.py`, `correr_m3_equidad.py`, `extremos_m3.py` | `Modelo3` | M3 con la equidad del M1, versión vieja (**ya verificada** por `m34_equidad.py`, que la reemplaza) |
| `costos_provisionales.py` | `Modelo3` | u = 1 con la tabla de Martín. Se borra cuando exista `parametros.py` |
| `07_clusters.py` | `Modelo3` | k-means k = 4 del Modelo 4 |
| `m34_datos.py` | `Modelo3` | carga + línea base con asserts + sorteo R (idéntico a 05). Autocontenido |
| `m34_mecanismo.py` | `Modelo3` | cortes con `grupo` matriz n×J; `excluir=` (no intervenibles), `pobre0=` (cumNP), `desempate=True` y reintento con `presolve="off"` |
| `m34_clusters.py` | `Modelo3` | k-means idéntico a 07 (reproduce 1.389 / 1.038 / 849 / 456) |
| `m34_montecarlo.py` | `Modelo3` | MC del 2-nov (sin desempate). Define `EPF`, `precios_u1`, `matriz_grupo` |
| `m34_optimos_alternos.py` | `Modelo3` | rango del error de inclusión entre óptimos alternos |
| `m34_test_regresion.py`, `m34_resumen_mc.py` | `Modelo3` | regresión contra 06 (630 cortes, 153,0, 59,6 %; 62,1 % antes del 5-nov) y tabla/gráfica del MC del 2-nov |
| `m34_montecarlo_lex.py` | `Modelo3` | MC con desempate × rezago {intervenible, no_intervenible}, Pool(2) |
| `m34_equidad.py`, `m34_correr_equidad.py` | `Modelo3` | objetivo de equidad del M1 para M3 **y** M4 |
| `m34_referencia_info_perfecta.py` | `Modelo3` | mismo objetivo de equidad con información perfecta (techo propio; **no** es el M1) |
| `m34_resumen_3nov.py`, `m34_grafica_equidad.py` | `Modelo3` | tablas del MC lex y de equidad; gráfica `equidad_m3_m4_ip.png` |
| `m34_sensibilidad_k.py`, `m34_resumen_k.py`, `m34_grafica_k.py` | `Modelo3` | M4 con k ∈ {2,3,4,5,6,8}, 50 réplicas pareadas; silueta, CH, η² de pobreza; `sensibilidad_k.png` |
| `m34_barrido_metas_v2.py`, `m34_resumen_barrido_v2.py` | `Modelo3` | curva costo–meta 2–30 % (u1, 30 réplicas); `barrido_v2.png` |
| `m34_pares_pequenos.py` | `Modelo3` | lista los pares (j, g) con pocos hogares privados |
| `docs/m34_README.md` | `Modelo3` | cómo correr los `m34_*` |
| `resultados/m34/` | `Modelo3` | resultados del 2 y 3-nov (MC, equidad, IP, k, barrido, pares chicos, 4 gráficas) |
| `m34_costos_reales.py` | `Modelo3` (4-nov, ajustado el 5-nov) | u_ij y costo_ij provisionales con las reglas de Martín (§2.6, §3, §4 de `CONTEXTO_DATOS.md`), validados contra el DANE. V = u·HW, K = costo_hogar·HW. El conteo de Martín solo entra con `fuente="martin"` (§7.0a) |
| `m34_corridas_costos_reales.py` | `Modelo3` (4-nov, ajustado el 5-nov) | modos `barrido` / `equidad` / `ip` con costos reales (mismo sorteo, k = 4, desempate, rezago no intervenible) |
| `m34_comparar_u1_real.py` | `Modelo3` (4-nov) | tablas pareadas u1 vs. real y gráfica `u1_vs_real.png` |
| Resultados 4-nov (`costos_reales_tabla.csv`, `comparacion_barrido_u1_real.csv`, `comparacion_equidad_u1_real.csv`, `info_perfecta_real.csv`, `equidad_real.csv`, `barrido_real_crudo.csv`, `u1_vs_real.png`) | `Modelo3` (`resultados/m34/`) | cifras de §7.8 |
| "Notas de Jerónimo" | `Contexto` (`CONTEXTO_DATOS.md`) | respuestas a las 7 preguntas de Martín y pendientes con fecha |
| ~~`m34_barrido_sensibilidad.py`~~ + `barrido_sensibilidad.csv` | solo Project (2-nov) | **Reemplazado por `m34_barrido_metas_v2.py`.** Sus filas `no_intervenible` no sirven (Trampa 14) |

**Ojo (5-nov):** los resultados del 4-nov se generaron con el código anterior a la limpieza del 5-nov
(§7.0a). El barrido real se repitió en el Mac y dio idéntico al del Project en las 900 corridas (2 de
ellas hubo que repetirlas, Trampa 21). Sus CSV traen `inclusion_personas` sin HW y no traen
`estado_highs` ni `gap`. Las tablas y la gráfica usan `inclusion_pesos`, que no cambia; una corrida
nueva sí daría esa columna distinta.

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
- **Auditoría del 3-nov:** el MILP coincide con fuerza bruta en 40/40 instancias (los dos objetivos)
  y un verificador independiente (regla R ≤ p directa, sin prefijo) reproduce 36/36 soluciones.
  Big-M opcionalmente más ajustado: R4/R5 con pers_i·s0_i y R6 con s0_i − 0,33 (no hace falta).

**Variantes de costo:**
- `pp` = V = K = HS (como 06; personas **de la muestra**, sin HW). **Defectuosa, ver §7.0 hallazgo 1.**
- `u1` = V = HW, K = EpF_j^zona·HW (tabla de Martín §4, millones de $ de 2025).
- **`real` (4-nov)** = V = u_ij·HW, K = costo_hogar_ij·HW, con u_ij reconstruido (§2). Misma unidad
  arriba y abajo (Trampa 1); el ε no cambia.

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

- SevEdu (9) no está implementada: necesita un sorteo por niño. `metricas` recalcula todo desde los
  cortes elegidos y no confía en `y` ni en `q`. Es la misma función para M3 y M4.
- La "severidad" es Σ p_i·s_i² sobre los pobres **iniciales, sin censurar** (un hogar que sale sigue
  sumando). No es la severidad AF censurada: declararlo o censurarla (§7.0 hallazgo 5).

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
    `presolve="off"`; ya está en `m34_mecanismo` y `m34_equidad`.
16. **(3-nov) PuLP 4.x rompe `LpVariable(cat=...)`.** Instalar con `requirements.txt` (`pulp<4`).
17. **Clústeres sin privaciones:** el k-means usa solo variables que el Estado observa (tamaño,
    composición por edades, dependencia, edad/sexo/educación del jefe). Agrupar por privaciones
    contradice el supuesto de información imperfecta.
18. **(3-nov tarde) Un k grande en M4 simula información individual.** Con k = 8 hay 26 pares
    (j, clúster) con menos de 10 hogares privados y un clúster de solo 81 hogares. **No presentar
    k = 8 como mejor.** Regla: menos del 15 % de los pares con n < 10 (k = 4: 8/53; k = 5: 14/64).
19. **(4-nov) Reglas de conteo u_ij: no usar `P6090 == 2` ni `P8563 != 1`.** El DANE cuenta como no
    asegurado a `P6090 != 1` (incluye "no sabe", 9) y solo a las personas de 6 años o más; con `== 2`
    se pierde el 6,9 % de los hogares privados. En barreras el DANE usa `P8563 ≥ 3` (el promotor o
    enfermero, 2, cuenta como atendido); con `!= 1` sobran 307 hogares. Desocupados = no ocupados con
    `P6351 = 1`; con esa regla el 98 % de los hogares privados en desempleo queda imputado (u = 1).
20. **(5-nov) `Pool` con `fork`.** Las tareas leen `G_`/`EQ` heredados del proceso padre. Con `spawn`,
    el defecto en macOS, llegan vacíos (`KeyError: 'hog'`). Usar `get_context("fork").Pool(2)`.
21. **(5-nov) `Optimal` falso por el reloj.** Dos corridas del barrido marcaron ~2.700–2.900 s con
    límite de 180 s, probablemente por una suspensión del Mac (no comprobado): una dio `Not Solved` y
    otra `Optimal` con costo 128.327, cuando el óptimo es 117.342 (+9,4 %). Revisar `segundos` y
    `estado_highs`; repetir lo sospechoso.

## 7. Estado y resultados (4-nov-2026)

**M3 y M4 técnicamente completos**, con u = 1 y, desde el 4-nov, con **costos reales provisionales**.
M1 y M2 **sí existen**: están en la rama `origin/modelos-1-2` (carpeta `Modelos/`, con `parametros.py`,
`modelo_base.py` y `data/processed/conteo_pares.csv`), aún sin fusionar con `Modelo3`. Quedan abiertos
los hallazgos de las auditorías (§7.0 y `claude/auditoria-4modelos-4nov.md`) y la redacción.
Regresión vigente (5-nov): 630 cortes y 153,0 con HiGHS y con CBC; inclusión **59,6 %** (antes 62,1 %:
desde el 5-nov `inclusion_personas` usa personas expandidas HS·HW).

### 7.0a Limpieza del 5-nov (auditoría de los cuatro modelos, 4-nov)

- **Hallazgo 2 (cerrado):** `cargar_costos(hog, raiz, fuente="provisional")`. El conteo de Martín solo
  entra con `fuente="martin"` y se valida: hoy falla con un error claro porque trae u = 0 en
  1.940 pares privados (1.939 de logro y **1 de inasistencia**). `enumerar_cortes` tiene `assert Den > 0`.
- **Hallazgo 9 (cerrado):** `m34_mecanismo.estado_real` lee el estado y el `mip_gap` de HiGHS; si HiGHS no
  certificó optimalidad (p. ej. tiempo), el estado pasa a `NoOptimo:<motivo>` y la fila no se cuenta como
  óptima. `resolver_paper` y `m34_equidad.resolver` devuelven `estado_highs` y `gap`; el barrido v2 y la
  equidad real los guardan por fila.
- **Hallazgo 12 (parcial):** `inclusion_personas` con HS·HW; la variante `pp` salió de
  `m34_barrido_metas_v2`. Sigue en los scripts históricos `m34_montecarlo.py` y `m34_montecarlo_lex.py`.
- Pendientes que dependen de Martín: escenario común (h1, h3, h4), jóvenes en z y v (h7), doble pago del
  desocupado (h8), fusión de ramas. Pendientes propios: placebo M4 (h6), equidad real a 30 réplicas (h10),
  `requirements-lock.txt` desde el Mac (h5).

### 7.0 Auditoría del 3-nov (`claude/auditoria-m34-3nov.md`): hallazgos abiertos

Lo que **sí se sostiene**: todo lo que está en pesos (u1 y real) y todo el objetivo de equidad usan
costo ponderado (K = EpF·HW) y la inclusión en pesos está bien ponderada. **Esos son los resultados a
defender.** Lo que hay que corregir o declarar:

| # | Severidad | Hallazgo | Qué hacer |
|---|---|---|---|
| 1 | **Crítico** | Variante `pp`: V = K = HS (personas de la muestra) mientras la meta R7 está ponderada por HS·HW. Curar un hogar de cabecera (FEX ~1.309) cuesta igual que uno rural (~220) y baja M0 ~6× más. Corregido (V = K = HS·HW), M3 pasa del 99–100 % del esfuerzo en cabecera al 4–9 %, su inclusión baja de ~60 % a ~20 % y **la ventaja de M4 en esfuerzo desaparece** (ahorro +1,7 / −0,8 / −11,6 % con metas 5 / 10 / 20 %) | Definir `pp` como HS·HW y repetir el MC del paper (~85 min), o **retirar las columnas pp** de §7.2 y frases como "M3 invierte casi todo en la cabecera" |
| 2 | Alto | `inclusion_personas` = Σ HS·cub sin HW (la exclusión sí usa HS·HW). Diferencia mediana 4,5 pp, máx. 29,6 pp | `esf_h = (HS*HW*cub).sum(1)` en `m34_mecanismo.metricas` |
| 3 | Alto | **Placebo de M4:** con clústeres al azar (mismos tamaños), equidad B = 25 da 1,64× las personas de M3 (M4 real 1,78×) y con meta 5 % cuesta el 59 % de M3 (M4 real 51 %). La mayor parte de la ventaja de M4 viene **del cambio de partición**, no de la demografía; la demografía pesa de verdad con B = 10 (1,36× → 1,98×). Solo 10 réplicas | Correr el placebo con 100 réplicas y reformular el hallazgo de M4 |
| 4 | Alto | Reproducibilidad: **resuelto el 3-nov** para los `m34_*` del 3-nov (commit `450840c`). Los scripts del 4-nov se subieron el 5-nov. Falta fijar versiones exactas (`pip freeze`) | Fijar versiones |
| 5 | Medio | Severidad sin censurar (§5.1) | Declararlo o censurarla; confirmar con Martín qué usa el M1 |
| 6 | Medio | PuLP mapea `kTimeLimit` de HiGHS a `Optimal`; no se guarda el gap. **Se materializó el 5-nov** con el reloj alterado (Trampa 21) | **Cerrado:** `estado_real` (§7.0a) |
| 7 | Medio | n del MC sin justificar con la ec. (8) del paper; p5/p95 con n = 100 son ruidosos | IC bootstrap de la mediana y de la diferencia pareada M4 − M3 |
| 8 | Medio | Desviaciones respecto al paper dispersas (unidades de p_jd, cotas 5*/6*, clustering sin privaciones ni ingreso, rezago no intervenible, D = P3) | Tabla "Desviaciones respecto al paper" en el informe |
| 9 | Bajo | Clustering: `StandardScaler` sin pesos, `educ_jefe` categórico tratado como continuo | Opcional: escalado ponderado, años de educación |

### 7.1 Verificaciones de base (1-nov, entorno `opti1`, CBC)

| Prueba | Resultado |
|---|---|
| `test_cortes.py` T1 | 45 pares, 630 cortes, mismos cortes que 06, objetivo 153,0 |
| `test_cortes.py` T2 | 511 cortes con pesos aleatorios, 0 inconsistentes |
| `test_cortes.py` T3 | celda Cabecera: 243/243 cubiertos, 243 siguen privados, costo 953 |
| `correr_m3_equidad.py capa0` | 523 pobres, H0 = 9,45 %, Sev0 = 117.908, 518 cortes con u = 1 |
| Costo de cubrir todo (u = 1) | $29.358 mm, de los cuales $8.946 mm en hogares pobres (con costos reales: $33,5 billones, +14 %) |

**Tangentes:** el código da 6.048 y Martín 6.571. La diferencia es exactamente 523 porque el código
omite a = 0 (q_i ≥ 0, redundante con `lowBound = 0`). Inocua; falta confirmarlo con Martín.

### 7.2 Objetivo del paper: MC con desempate, rezago no intervenible (3-nov, u1)

2.400 MILP, todos óptimos. Mediana [p5; p95]. **Columnas pp retiradas** por el hallazgo 1 de §7.0
(están en `resumen_mc_lex.csv` si se corrigen).

| Meta | Modelo | Costo u1 (mil mill. $) | Inclusión u1 | Exclusión |
|---|---|---|---|---|
| 5 % | M3 | 12,2 [6,4; 17,4] | 48 % [24; 77] | 94 % |
| 5 % | M4 | 6,0 [3,2; 6,6] | 54 % [24; 61] | 92–94 % |
| 10 % | M3 | 23,5 [15,0; 32,9] | 74 % [39; 78] | 86–88 % |
| 10 % | M4 | 13,4 [10,3; 16,9] | 57 % [28; 68] | 87–88 % |
| 20 % | M3 | 44,3 [40,4; 47,8] | 65 % [56; 67] | 74 % |
| 20 % | M4 | 38,3 [33,5; 41,9] | 41 % [28; 61] | 72 % |

- Pareado M4 vs M3: más barato en pesos en 97–99 % de las réplicas (ahorro mediano 53 / 43 / 14 %).
  Menos inclusión en pesos en 50 / 84 / 95 %. **Con meta del 5 %, M4 no reduce la inclusión (48 → 54 %).**
- Rezago no intervenible: el costo sube en 0–13 % de las réplicas; mediana +0,0 %.
- Exclusión del 72 al 94 %: con metas pequeñas sobre M0, la mayoría de los pobres no recibe nada.

### 7.3 Objetivo de equidad: M3 vs M4 vs información perfecta (3-nov, u1)

**Verificado:** `m34_equidad.py` reproduce `modelo3_equidad.py` (B = $500 mm, réplica 0: 419.550
personas, inclusión 42,6 %). 30 réplicas, rezago no intervenible, ρ = 0. Personas que salen (mediana).

| B (mil mill. $) | Info. perfecta | M3 | M4 | M3/IP | M4/IP | Inclusión M3/M4 | Severidad −: IP/M3/M4 |
|---|---|---|---|---|---|---|---|
| 10 | 139.968 | 35.000 [24k; 64k] | 61.400 [55k; 70k] | 25 % | 44 % | 51/52 % | 7,6/2,5/4,3 % |
| 25 | 205.291 | 79.900 [47k; 113k] | 109.000 [103k; 116k] | 39 % | 53 % | 62/62 % | 11,9/6,2/8,3 % |
| 50 | 286.428 | 147.000 [141k; 152k] | 159.000 [151k; 169k] | 51 % | 55 % | 61/43 % | 17,0/11,3/15,2 % |
| 100 | 400.969 | 210.000 [201k; 223k] | 233.000 [228k; 239k] | 52 % | 58 % | 40/39 % | 26,2/18,2/23,7 % |
| 200 | 545.651 | 319.000 [313k; 329k] | 325.000 [320k; 333k] | 58 % | 60 % | 41/38 % | 41,0/29,3/31,1 % |

- M4 saca más personas que M3 en 90–100 % de las réplicas; razón mediana 1,78 / 1,37 / 1,09 / 1,10 / 1,02
  (recordar el placebo, §7.0 #3).
- **ρ = 10 %:** infactible con B = 10 en M3 y M4 (con IP sí). Con B = 25: 0/30 en M3 y 6/30 en M4.

### 7.4 Sensibilidad a k en M4 (3-nov tarde; 50 réplicas pareadas, u1)

| k | Silueta | η² pobreza | Pares n < 10 | Salen B = 10 (miles) | Salen B = 25 | M4/M3 (B = 10) | Costo meta 10 % |
|---|---|---|---|---|---|---|---|
| M3 | — | — | 2 | 31,1 | 74,7 | 1,00 | 23,1 |
| 2 | 0,260 | 0,002 | 4 | 21,8 | 69,0 | **0,71** | 24,9 |
| 3 | 0,271 | 0,024 | 4 | 44,6 | 99,8 | 1,19 | 12,9 |
| **4** | 0,272 | 0,022 | 8 | **61,2** | **107,6** | **1,92** | **13,6** |
| 5 | 0,277 | 0,027 | 14 | 61,4 | 115,7 | 1,93 | 12,5 |
| 6 | 0,274 | 0,031 | 16 | 64,7 | 117,4 | 1,99 | 11,8 |
| 8 | 0,283 | 0,061 | **26** | 76,2 | 123,2 | 2,44 | 9,1 |

- **La silueta no decide k** (0,26–0,28): elegir k es una **decisión de política** (qué tan fino es el
  sistema de información del Estado). k = 2 es peor que M3 (separa por tamaño, η² ≈ 0).
- Desde k = 4 la ganancia se aplana y crecen las celdas chicas (Trampa 18). **k = 4 se defiende**;
  k = 5 queda como alternativa. Parte de la ganancia con k es granularidad (§7.0 #3).

### 7.5 Curva costo–meta del 2 al 30 % (3-nov tarde; u1, 30 réplicas, 900 MILP óptimos)

| Meta | Costo M3 | Costo M4 | Ahorro M4 | M4 más barato | Inclusión M3 / M4 | Exclusión M3 / M4 |
|---|---|---|---|---|---|---|
| 2 % | 3,6 | 3,0 | 6 % | 60 % | 40 / 44 % | 97 / 97 % |
| 6 % | 12,5 | 6,2 | **53 %** | 97 % | 55 / 55 % | 92 / 92 % |
| 10 % | 22,9 | 13,4 | 35 % | 97 % | 73 / 58 % | 86 / 87 % |
| 16 % | 33,4 | 26,8 | 14 % | 93 % | 75 / 62 % | 79 / 79 % |
| 20 % | 44,7 | 37,7 | 16 % | 100 % | 65 / 41 % | 74 / 71 % |
| 26 % | 74,3 | 56,9 | 24 % | 100 % | 47 / 45 % | 64 / 63 % |
| 30 % | 95,2 | 75,4 | 22 % | 100 % | 40 / 38 % | 58 / 57 % |

Costo convexo (~1,8 → ~5 mil millones por punto de M0). Ventaja de M4 no monótona. Inclusión en
forma de campana (pico ~75 % en M3 entre el 10 y el 16 %).

### 7.6 Pares con muestra chica (pendiente #5)

- M3: 2 de 45 pares con n < 10 (`paredes` en centro poblado, 1 hogar; `trabajo_infantil` en centro poblado, 9).
- M4 (k = 4): 8 de 57 pares.
- Con u1: **0 %** del costo en esos pares en las 900 corridas. **Con costos reales (4-nov) sí gasta,
  aunque poco:** en el 8,7 % de las corridas de M3 y el 6,9 % de las de M4 (mediana 0; máximo 17,8 %
  y 10,3 % del costo). No hace falta fusionar celdas en el caso base, pero **hay que declararlo**. La
  prueba de blindaje sería fusionar los pares con n < 10 con su vecino y repetir el barrido (decisión
  de Jerónimo, porque cambia la definición de celdas).

### 7.7 Hallazgos para la sustentación (revisados el 4-nov con la auditoría y los costos reales)

1. **Precio de no tener información (el resultado más sólido):** M3 logra el 22–57 % de lo que
   lograría la información perfecta con costos reales (23–59 % con u = 1); M4 el 43–60 %.
2. **M4 vale más cuando la plata es poca o la meta es modesta** (× 1,7–1,8 con B ≤ 25; ahorro de
   34–49 % con metas del 6–10 %), **desde metas del ~4 %** (con meta del 2 % y costos reales, M4 ya no
   es más barato). Matiz obligatorio: buena parte de la ventaja es por la partición (placebo, §7.0 #3).
3. **M4 es más predecible:** con B = 25 el p5–p95 de M3 va de 47 mil a 113 mil personas; el de M4, de
   103 mil a 116 mil.
4. **No cualquier información demográfica sirve:** k = 2 es peor que solo geografía.
5. **Rendimientos decrecientes:** el costo por punto de M0 casi se triplica a lo largo de la curva
   (~2,2 → ~6 mil millones con costos reales).
6. **Los techos de severidad son lo que más se degrada:** con costos reales, ρ = 10 % es infactible
   con B = 10 incluso con información perfecta.
7. **La inclusión es alta (~35–70 % con costos reales)** con ambos objetivos: es el costo estructural
   de focalizar sin información individual.
8. **Robustez:** al pasar de u = 1 a costos reales todo cuesta 25–40 % más, pero el precio de la
   información y la ventaja de M4 casi no cambian (gráfica `u1_vs_real.png`).
9. El rezago casi nunca se elige; tratarlo como no intervenible no mueve los resultados.

Hilo sugerido: información perfecta (techo) → M3 (geografía) → M4 (geografía + demografía, con el
placebo) → robustez a costos (u1 vs. reales) → k → limitaciones (pares chicos, sin municipio, rezago
no intervenible, severidad sin censurar). Gráficas: `equidad_m3_m4_ip.png` (central),
`u1_vs_real.png`, `sensibilidad_k.png`, `barrido_v2.png`.

### 7.8 Costos reales provisionales (4-nov; `resumen-avance-4nov.md`)

Costo de todos los pares privados: 29,4 → 33,5 billones (+14 %; logro × 1,60, empleo formal × 1,47,
aseguramiento × 1,41, barreras × 1,31; vivienda y servicios no cambian). 1.200 MILP (900 del barrido +
300 de equidad), todos óptimos, pareados con u1 (mismo sorteo, k = 4, desempate, rezago no intervenible).

**Curva costo–meta (mediana de 30 réplicas, mil millones de $ 2025):**

| Meta | M3 u1 → real | M4 u1 → real | Ahorro M4 u1 → real | M4 más barato (real) | Inclusión M3 u1 → real | Inclusión M4 u1 → real |
|---|---|---|---|---|---|---|
| 2 % | 3,6 → 4,4 | 3,0 → 4,5 | 6 % → **−7 %** | 47 % | 40 → 35 % | 44 → 44 % |
| 6 % | 12,5 → 17,4 | 6,2 → 9,5 | 53 → 49 % | 93 % | 55 → 48 % | 55 → 47 % |
| 10 % | 22,9 → 31,5 | 13,4 → 19,6 | 35 → 34 % | 97 % | 73 → 62 % | 58 → 50 % |
| 16 % | 33,4 → 43,4 | 26,8 → 37,2 | 14 → 13 % | 97 % | 75 → 68 % | 62 → 51 % |
| 20 % | 44,7 → 59,3 | 37,7 → 49,4 | 16 → 16 % | 100 % | 65 → 59 % | 41 → 40 % |
| 30 % | 95,2 → 119,1 | 75,4 → 93,5 | 22 → 21 % | 100 % | 40 → 36 % | 38 → 38 % |

**Equidad (ρ = 0, 15 réplicas; personas que salen):**

| B | IP u1 → real | M3 u1 → real | M4 u1 → real | M3/IP real | M4/IP real | M4/M3 real |
|---|---|---|---|---|---|---|
| 10 | 139.968 → 114.913 | 32.312 → 24.881 | 63.201 → 49.180 | 22 % | 43 % | × 1,70 |
| 25 | 205.291 → 183.742 | 60.991 → 47.367 | 107.014 → 87.395 | 26 % | 48 % | × 1,80 |
| 50 | 286.428 → 255.038 | 146.756 → 131.418 | 159.382 → 136.568 | 52 % | 54 % | × 1,05 |
| 100 | 400.969 → 348.451 | 212.086 → 181.862 | 232.588 → 208.507 | 52 % | 60 % | × 1,14 |
| 200 | 545.651 → 479.389 | 319.908 → 275.184 | 323.453 → 282.950 | 57 % | 59 % | × 1,03 |

- Con el mismo B salen 10–23 % menos personas, pero el precio de la información casi no cambia.
- ρ = 10 %: infactible con B = 10 incluso con IP; con B = 25 infactible en M3 y M4 en todas las
  réplicas; con B = 50, M3 cumple en el 60 % y M4 en el 100 %.
- En qué se gasta: con meta del 10 %, 86–89 % en salud; con meta del 30 %, ~55–59 % en educación.

**Supuestos a declarar:** logro cuenta adultos con < 9 años (el DANE usa el **promedio** del hogar);
EpV de los desocupados imputados = $5,12 M; en empleo formal los desocupados entran en las dos
fórmulas (empleo y desempleo), como en la tabla de Martín → posible doble pago (preguntarle).

## 8. Modelo 4

- Partición: **V (bienes públicos, por zona) = {acueducto, alcantarillado}**; **U = los otros 13, por
  clúster**. Validada: acueducto discrimina 14,5× por zona y 4,1× por clúster; alcantarillado 4,7× y
  3,2×; atención integral 2.119×, inasistencia 51,7× y hacinamiento 26,6× por clúster.
- k-means, `random_state` 2026, **k = 4** (defendido con la sensibilidad a k, §7.4).
- Clústeres: T0 adultos sin dependientes (1.389, H 3,7 %), T1 adultos mayores (1.038, 11,8 %), T2 con
  hijos escolares (849, 9,1 %), T3 primera infancia (456, 16,1 %). Separan la pobreza 4,3× sin usarla.
  Honestidad: parte es estructural (la atención integral solo aplica a hogares con menores de 5).
- MILP: el mismo de §5 con `grupo` matriz n×J; 57 pares, 713 cortes, 1–6 s.
- **Placebo (auditoría):** con etiquetas permutadas al azar la mayor parte de la ventaja persiste
  (§7.0 #3). Narrativa: "el valor de M4 depende de cuán fino focalice el Estado; la demografía suma
  sobre todo con presupuestos pequeños", en línea con el paper (p. 10: con granularidad máxima M3 → M2).
  Variante a considerar: celdas zona × clúster para los privados.
- Hecho: objetivo del paper, equidad, MC con desempate, sensibilidad a k, curva costo–meta y costos reales.

## 9. Respuestas a las preguntas de Martín (§8 de `CONTEXTO_DATOS.md`)

Escritas el 3-nov en "Notas de Jerónimo" de `CONTEXTO_DATOS.md` (rama `Contexto`, commit `66bc989`):

1. **SevEdu:** primero como métrica ex post en el MC de M3/M4; como techo (ρ_e = 14 %), trabajo futuro.
2. **Objetivo:** el del paper como caso base de M3/M4 (mide inclusión y exclusión); la equidad como
   puente con el M1. Comparación ex post en H, A, M0, severidad, SevEdu y costo, por zona y total.
3. **u_ij = 1 en empleo:** como sensibilidad, no como caso base.
4. **Inasistencia:** costo 3,0/p en la optimización; el cumplimiento p solo en el MC de evaluación.
5. **Conteo de no pobres en el 05:** imprescindible (es el error de inclusión). Martín confirmó que
   cuenta los 3.732 hogares.
6. **`parametros.py`:** importar de ahí `IND`, `W` y la semilla; prefijo `m34_` para Jerónimo.
7. **Costos:** logro = 3 ciclos CLEI (base); acueducto rural de $43,7 M solo con fuente verificable;
   el BID ($9,7 M) como sensibilidad.

Preguntas de Jerónimo a Martín: u_ij para no pobres → **respondida** (sí). Meta del M2 sobre M0 o H →
**pendiente**. p de inasistencia (0,369 vs 0,50) y gap → **pendiente**. Doble cuenta de desocupados
→ **nueva (4-nov), pendiente**. Martín **no ha respondido** las "Notas de Jerónimo" (1 día en el repo).

## 10. Decisiones abiertas

1. **Objetivo del caso base de M3/M4** (paper vs equidad). Los dos están implementados; propuesta: paper.
2. **Costos del caso base:** reales provisionales (propuesta del 4-nov) con u = 1 como sensibilidad,
   o esperar el `conteo_pares.csv` de Martín.
3. **Variante `pp`:** corregirla (HS·HW) y repetir el MC, o retirarla de la sustentación (§7.0 #1).
4. **Cómo presentar M4 tras el placebo** (§7.0 #3); ¿variante zona × clúster?
5. **Severidad censurada o no** (§5.1), igual que el M1 de Martín.
6. **Meta del Modelo 2 sobre M0 o sobre H.** Si es H, la comparación M2 ↔ M3/M4 no cuadra.
7. **Caso base común:** p = 0,369 (propuesta) vs 0,50; HiGHS con el gap reportado por corrida
   (1e-6 en el paper y la etapa 1, 1e-4 en la etapa 2; `presolve="off"` de respaldo); CBC solo para la
   regresión. Martín usa 1e-4.
8. **Validar el M1 de Martín contra `info_perfecta.csv` / `info_perfecta_real.csv`** (mismo B y supuestos):
   una diferencia > 1 % indica diferencia de supuestos (rezago, empleo, tangentes).
9. **Fusionar o no los pares con n < 10** con costos reales (§7.6).
10. **Pesos w_j:** solo como sensibilidad, en los 4 modelos a la vez y en múltiplos de 0,01.
11. **k en M4:** k = 4 (defendido); k = 5 como alternativa.
12. **Cuándo se fusionan `Modelo3` y `Contexto` a `main`.**

## 11. Lo que sigue, en orden

1. **Hecho (5-nov):** los 3 scripts del 4-nov y sus resultados están en `Modelo3`.
2. **Corregir los hallazgos 1 y 2 de la auditoría** (`pp` con HS·HW e `inclusion_personas` con HW) o
   retirar las cifras `pp`. Correr el placebo con 100 réplicas.
3. **Con Martín, con fecha límite:** M1 y M2 en el repo, `parametros.py`, `05_conteo_personas.py`
   (`conteo_pares.csv`), meta del M2, doble cuenta de desocupados y severidad censurada. Avisarle que
   M3/M4 ya tienen costos reales provisionales y pedirle que compare su conteo con `costos_reales_tabla.csv`.
   Si no llega el M1, usar `info_perfecta_real.csv` como techo.
4. Actualizar `Seleccion_Variables_Restricciones_Modelo3.pdf` / `Modelo4.pdf` (carpeta Opti1, un nivel
   arriba) con T1, T13–T19, M4, equidad, k, costos reales y la tabla de desviaciones respecto al paper.
5. Diapositivas con las tablas de §7 y las gráficas (hilo de §7.7).
6. Opcional: guardar estado/gap de HiGHS por corrida, IC bootstrap, fijar versiones con `pip freeze`.
7. Comparación final de los 4 modelos: tabla común H, A, M0, severidad, SevEdu y costo, por zona y
   total, con la misma meta para M2, M3 y M4. Reparto de la sustentación y fecha del ensayo.

## 12. Entorno y cómo correrlo

Correr desde la raíz del repo (los scripts viejos cargan `05_` y `06_` por ruta relativa).

```bash
PY=/opt/anaconda3/envs/opti1/bin/python
R=data/DANE/DEPARTAMENTAL
$PY test_cortes.py
$PY 06_modelo3_cortes.py 0.10          # producción + control de equivalencia ("solo" = sin control)
$PY m34_test_regresion.py $R                                       # 630 cortes, 153,0, 59,6 %
$PY m34_montecarlo.py $R m3 0 100 out/mc_m3.csv                    # MC 2-nov, ~25 s/réplica
# 3-nov
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
# 4-nov: costos reales provisionales (scripts en el Project, claude/codigo-m34/)
$PY m34_costos_reales.py $R out/costos_reales_tabla.csv            # validación y tabla, segundos
$PY m34_corridas_costos_reales.py ip $R out/info_perfecta_real.csv 10 25 50 100 200   # ~2 min
$PY m34_corridas_costos_reales.py barrido $R 30 out/barrido_real                      # 60 tareas, ~30 min
$PY m34_corridas_costos_reales.py equidad $R 15 out/equidad_real.csv 10 25 50 100 200 # ~8 min
$PY m34_comparar_u1_real.py resultados/m34/barrido_v2_crudo.csv out/barrido_real resultados/m34/equidad_m34.csv \
    out/equidad_real.csv resultados/m34/info_perfecta.csv out/info_perfecta_real.csv out/comparacion
```

- `opti1`: Python 3.10.18, PuLP 2.9.0 con CBC y HiGHS (`highspy`). `requirements.txt`:
  `pulp>=2.9,<4`, `highspy>=1.7` (rangos, no versiones exactas). También probado con PuLP 3.3.2 + highspy.
- El `python3` por defecto trae PuLP 4.0.0 sin solvers: no usarlo (T16).
- Las gráficas necesitan `matplotlib`, que no está en `requirements.txt` (instalado en `opti1` el 4-nov: 3.10.9).
- Corridas largas en el Mac: `caffeinate -i <cmd>` y la tapa abierta. Si se suspende, repetir lo afectado (T21).
- El `timeLimit` de CBC no es confiable y este Mac no tiene `timeout`: `perl -e 'alarm 240; exec @ARGV' <cmd>`.
- CSV del DANE: coma y UTF-8 con BOM. `utils_dane.leer()` lo detecta; no hardcodear.

## 13. Convenciones

- Nada derivado de los datos va hardcodeado: un `0.038684` literal es un bug (en `m34_datos` solo vive como assert).
- Los comentarios explican el porqué y son material de sustentación: ampliarlos, no limpiarlos.
- Cambios metodológicos (umbral, pesos, D, k, costos) → también en los PDF de selección de variables.
- Con Martín: y_i = 1 ⇔ el hogar **sale**; HW_i siempre multiplica el costo, HS_i nunca (las personas
  ya están en u_ij); reportar H, A, M0 y severidad por zona `P3` y total; sensibilidades mínimas
  compartidas: caso base y u_ij = 1.
- Repo compartido: **no hacer commit, push, pull, fetch ni cambiar de rama sin que Jerónimo lo pida.**
  Jerónimo hace los commits a mano. Sin atribución de Claude en los commits.
- Problemas resueltos → `bitacora-problemas-y-soluciones.md` y `bitacora-adenda-noviembre.md` (Project "Opti1").
- Docs del Project: `decision-fuente-de-datos`, `revision-formulacion-modelo3`,
  `bitacora-problemas-y-soluciones`, `bitacora-adenda-noviembre`, `resumen-avance-2nov`,
  `resumen-avance-3nov`, `resumen-avance-3nov-tarde`, `resumen-avance-4nov`, `auditoria-m34-3nov`,
  `CLAUDE-contexto-pendiente-de-push` (versión para la rama `Contexto`, al 4-nov), `respaldo-CLAUDE-2nov`,
  `codigo-m34/`.

## 14. Cambios de Martín que pueden modificar el plan

Revisión del 4-nov-2026, noche, con `git fetch origin`. **Martín subió trabajo nuevo a `main`.**
Las §4, §7, §9, §10 y §11 se escribieron antes de esto y dan por pendiente parte de lo que ya
existe: **falta revisarlas.** Todavía no se ha leído el código nuevo ni se ha comparado con M3/M4.

| Rama | Último commit | Autor |
|---|---|---|
| `origin/main` | `0389805` (4-nov), antes `51082ad` (4-nov) y `91e7b97` (6-oct) | Martín |
| `origin/Contexto` | `ba8fc47`: actualiza el grafo de `perspectiva_equidad`; solo toca `graphify-out/` | Claude. `CONTEXTO_DATOS.md` no cambia desde `66bc989` ("Notas de Jerónimo") |
| `origin/modelos-1-2` | `c94365b` (4-nov): M1 y M2 con pruebas y resultados; no revisada aquí | `jero020` |
| `origin/Modelo3` | 5-nov: incluye lo del 4-nov y la limpieza; sin los commits nuevos de `main` | Jerónimo |

- **Ya existen en `main`:** `Modelos/parametros.py`, `Modelos/05_conteo_personas.py`,
  `Modelos/03_preparar_antioquia.py`, `Modelos/Modelo_2/modelo2.py`, `data/processed/conteo_pares.csv`,
  `docs/reglas_conteo_personas.md`, `docs/formulacion_modelo1.md`, `docs/formulacion_modelo2.md` y
  `docs/informe_modelo1.md`.
- **Modelo 1:** `main` trae su formulación y su informe, pero ningún script con ese nombre.
- **Martín movió** `utils_dane.py` y los scripts 02–04 a `Modelos/`. Un merge de `main` en `Modelo3`
  rompería los imports de M3/M4: hacerlo aparte y con cuidado.
- No hay archivos `NOTAS_*.md` en `main` ni en `Contexto`. Falta ver si los docs nuevos responden
  las "Notas de Jerónimo"; en `CONTEXTO_DATOS.md` no hay respuesta.

Lo siguiente: comparar `conteo_pares.csv` con `costos_reales_tabla.csv`, revisar la meta del M2 en
`docs/formulacion_modelo2.md` y validar `info_perfecta_real.csv` contra `docs/informe_modelo1.md`.

Lo ya incorporado del 2-nov, por si hay que recordarlo:

| Cambio | Por qué afecta a M3/M4 | Ajuste |
|---|---|---|
| Rezago: ningún niño sale en un año; estrategias E0–E3; ρ_e = 14 % (base) / 20 % (con E3) | El rezago deja de curarse con un año regular | **Hecho (3-nov):** no intervenible, constante en s_i (T14); medianas +0,0 % |
| u_ij para los 3.732 hogares | Permite medir la inclusión en pesos | **Hecho provisionalmente (4-nov)** con `m34_costos_reales.py`; `conteo_pares.csv` ya está en `main`: comparar par por par (si difiere > ~1 % del costo total, repetir las corridas, ~40 min) |
| p de inasistencia 0,37 (0,50 y 0,75 como sensibilidad) | Cambia el costo de inasistencia (3,0/p) | Los MC usan 0,369; confirmarlo como caso base |
