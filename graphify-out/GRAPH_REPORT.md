# Graph Report - Optimizacion_1_S4  (2026-10-21)

## Corpus Check
- 10 files · ~29,847 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 155 nodes · 326 edges · 10 communities (9 shown, 1 thin omitted)
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 57 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Paper: modelos MILP y supuestos
- Modelo 1: formulación y costos
- Validación IPM y zonas P3
- Reglas de conteo u_ij
- Línea base: H, A y M0
- Lectura de microdatos DANE
- Guía del proyecto y datos
- Presupuesto y verificación
- Umbral k y salidas rápidas
- Pobreza urbana (cabecera)

## God Nodes (most connected - your core abstractions)
1. `Reglas de conteo de personas afectadas por privación (u_ij)` - 19 edges
2. `Paper condensado: formulaciones de los 4 modelos (reemplaza leer el PDF)` - 18 edges
3. `Informe del Modelo 1: presupuesto fijo con equidad por zona` - 17 edges
4. `Modelo 2 - hogar, minimiza costo (first best, MILP)` - 14 edges
5. `Hamie, Hlasny & Jouni (2024) - MPI Alleviation: Policy Optimization (ERF WP 1742)` - 14 edges
6. `Costos EpF_j 2025 urbano/rural, cerrados el 21-oct-2026` - 13 edges
7. `Modelo 3 - focalización geográfica` - 12 edges
8. `resumen()` - 11 edges
9. `Modelo 1a - hogar, sin costo, determinístico` - 10 edges
10. `Modelo 1 (nuestro): max H sujeto a presupuesto B y equidad r — "dual" del Modelo 2 del paper` - 10 edges

## Surprising Connections (you probably didn't know these)
- `Heurística greedy (menor costo por punto) como benchmark` --semantically_similar_to--> `Modelo 1a - hogar, sin costo, determinístico`  [INFERRED] [semantically similar]
  docs/informe_modelo1.md → referencias/paper_pobreza_multidimensional_opti1.pdf
- `Equidad: Σ_{i∈d} HW_i·HS_i·y_i ≥ r·Pobres_d⁰ (y_i = 1 si el hogar sale)` --semantically_similar_to--> `Meta de reducción: MPI_post ≤ MPI_s·(1 − MPI_r)`  [INFERRED] [semantically similar]
  docs/resumen_proyecto_ipm.md → referencias/paper_pobreza_multidimensional_opti1.pdf
- `Costos EpF_j 2025 urbano/rural, cerrados el 21-oct-2026` --semantically_similar_to--> `Esfuerzo E_j (función objetivo: min Σ E_j)`  [INFERRED] [semantically similar]
  docs/resumen_proyecto_ipm.md → referencias/paper_pobreza_multidimensional_opti1.pdf
- `Modelo 1 (nuestro): max H sujeto a presupuesto B y equidad r — "dual" del Modelo 2 del paper` --semantically_similar_to--> `Modelo 2 - hogar, minimiza costo (first best, MILP)`  [INFERRED] [semantically similar]
  docs/informe_modelo1.md → referencias/paper_pobreza_multidimensional_opti1.pdf
- `Factor de expansión FEX_C (vs. FEXP) como HW_i` --semantically_similar_to--> `Peso del hogar HW_i y tamaño HS_i`  [INFERRED] [semantically similar]
  02_validar_ipm.py → referencias/paper_pobreza_multidimensional_opti1.pdf

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Los cuatro modelos de focalización (1a/1b, 2, 3, 4)** — referencias_paper_pobreza_multidimensional_opti1_model_1a, referencias_paper_pobreza_multidimensional_opti1_model_1b, referencias_paper_pobreza_multidimensional_opti1_model_2, referencias_paper_pobreza_multidimensional_opti1_model_3, referencias_paper_pobreza_multidimensional_opti1_model_4 [EXTRACTED 1.00]
- **Pipeline de datos: validar IPM → preparar Antioquia → línea base** — utils_dane, 02_validar_ipm, 03_preparar_antioquia, 03_preparar_antioquia_hogares_antioquia_csv, 04_linea_base [EXTRACTED 1.00]
- **Medidas Alkire-Foster calculadas en la línea base** — referencias_paper_pobreza_multidimensional_opti1_headcount_h, referencias_paper_pobreza_multidimensional_opti1_intensity_i, referencias_paper_pobreza_multidimensional_opti1_mpi, referencias_paper_pobreza_multidimensional_opti1_mpi_contribution, referencias_paper_pobreza_multidimensional_opti1_censored_headcount, 04_linea_base_resumen, 04_linea_base_contribuciones [INFERRED 0.95]
- **Hallazgos clave de la línea base** — docs_resumen_proyecto_ipm_hallazgo_informalidad, docs_resumen_proyecto_ipm_hallazgo_educacion_trabajo, docs_resumen_proyecto_ipm_hallazgo_sale_con_una, docs_resumen_proyecto_ipm_hallazgo_cabecera, docs_resumen_proyecto_ipm_linea_base_antioquia [EXTRACTED 1.00]
- **Siguientes scripts 05-09** — docs_resumen_proyecto_ipm_script_05_conteo_personas, docs_resumen_proyecto_ipm_script_06_parametros, docs_resumen_proyecto_ipm_script_07_eficiencia_zona, docs_resumen_proyecto_ipm_script_08_modelo1, docs_resumen_proyecto_ipm_script_09_modelo2 [EXTRACTED 1.00]
- **Decisiones de costeo cerradas (21-oct-2026)** — docs_resumen_proyecto_ipm_decision_cdi, docs_resumen_proyecto_ipm_decision_inasistencia_condicionada, docs_resumen_proyecto_ipm_decision_rezago_opcion_c, docs_resumen_proyecto_ipm_decision_empleo_formal_tres_casos, docs_resumen_proyecto_ipm_costos_epf [EXTRACTED 1.00]
- **Formulación del Modelo 1 (presupuesto fijo)** — docs_informe_modelo1_objetivo_lexicografico, docs_informe_modelo1_restriccion_presupuesto, docs_informe_modelo1_linealizacion_compacta, docs_resumen_proyecto_ipm_restriccion_equidad, docs_informe_modelo1_restriccion_no_intervenibles, docs_informe_modelo1_variables_modelo1 [EXTRACTED 1.00]
- **Plan de experimentos del Modelo 1** — docs_informe_modelo1_validaciones, docs_informe_modelo1_heuristica_greedy, docs_informe_modelo1_precio_equidad, docs_resumen_proyecto_ipm_sensibilidades, referencias_paper_pobreza_multidimensional_opti1_monte_carlo [INFERRED 0.95]
- **Reglas de conteo que reproducen al DANE ≥ 99.9 %** — docs_reglas_conteo_personas_regla_aseguramiento, docs_reglas_conteo_personas_regla_barreras, docs_reglas_conteo_personas_regla_trabajo_infantil, docs_reglas_conteo_personas_regla_rezago, docs_reglas_conteo_personas_regla_analfabetismo, docs_reglas_conteo_personas_regla_inasistencia, docs_reglas_conteo_personas_regla_logro [EXTRACTED 1.00]

## Communities (10 total, 1 thin omitted)

### Community 0 - "Paper: modelos MILP y supuestos"
Cohesion: 0.14
Nodes (23): Prueba B: acueducto/alcantarillado vs. 'no tiene el servicio' (P8520S5/S3), Con 4: E_j = EpF_j Σ HW_i (M_ij − N_ij) (costo por hogar, sin HS_i), Paper condensado: formulaciones de los 4 modelos (reemplaza leer el PDF), Reparto: Modelos 1-2 hogar por hogar (Tomás) · Modelos 3-4 por zona (Jerónimo), Planeado: 09_modelo2.py (meta política, metas por zona), Objetivo: MILP de asignación óptima de inversión pública contra la pobreza multidimensional, Casos: Argelia, Egipto, Irak, Mauritania, Túnez (2011-2019), Clustering de hogares (partición alrededor de medianas) + proxy means test (+15 more)

### Community 1 - "Modelo 1: formulación y costos"
Cohesion: 0.12
Nodes (19): Figura: costo promedio por punto de puntaje por indicador (barreras $0.04 M; pisos $8.48 M), Hallazgo: un punto de puntaje en vivienda cuesta 60-200× más que en barreras de salud, Experimentos: curva B → H/M0 por zona, greedy, precio de la equidad, sensibilidad, Monte Carlo de inasistencia, Heurística greedy (menor costo por punto) como benchmark, Implicación A ⇒ B equivale a B ∨ ¬A: una binaria elige el camino, Informe del Modelo 1: presupuesto fijo con equidad por zona, Linealización compacta: s_i ≤ 0.33 + (1 − y_i) y C_i ≥ s_i − y_i (bigM = 1), Modelo 1 (nuestro): max H sujeto a presupuesto B y equidad r — "dual" del Modelo 2 del paper (+11 more)

### Community 2 - "Validación IPM y zonas P3"
Cohesion: 0.15
Nodes (14): Factor de expansión FEX_C (vs. FEXP) como HW_i, cargar_con_p3(), incidencia(), Prueba A: H por zona vs. cifras oficiales DANE 2025, Zonas P3: cabecera / centro poblado / rural disperso, Nomenclatura Tabla A1: I, J, k, w_j, M_ij, HS_i, HW_i, EpF_j, N_ij, E_j, C_i, Llave persona → hogar: DIRECTORIO + SECUENCIA_P, Decisión: base DANE IPM 2025 DEPARTAMENTAL (15 privaciones ya calculadas) (+6 more)

### Community 3 - "Reglas de conteo u_ij"
Cohesion: 0.15
Nodes (16): Años de educación aprobados desde P8587/P8587S1 (no estudia) y P1088/P1088S1 (estudia), atencion_integral no replicable (96.5 %): P51 = 2 (con padre/madre en casa) no es privación, Ocupado = P6240 = 1 o P6250/P6260/P6270 = 1; desocupado = no ocupado y P6351 = 1, desempleo_larga_duracion no replicable (86.5 %): la variable del DANE no está en el archivo, P51: ¿dónde o con quién permanece el niño entre semana? (ECV, 8 categorías), analfabetismo: ≥ 15 años y P6160 = 2 (99.999 %), aseguramiento_salud: ≥ 6 años y P6090 ∈ {2, 9} (100 %), barreras_acceso_salud: P5665 = 1 y P8563 ∉ {1, 2} (100 %) (+8 more)

### Community 4 - "Línea base: H, A y M0"
Cohesion: 0.18
Nodes (15): contribuciones(), resumen(), Decisiones abiertas: objetivo H o M0; acuerdo con Jerónimo, Figura: contribución de cada dimensión a M0 por zona (educación y trabajo dominan; vivienda 19 % en lo rural), "IPM" del DANE = H; "MPI" del paper = M0 = H × A, Objetivo: max Σ HW_i HS_i y_i − λ Σ HW_i HS_i C_i (H principal, M0 desempate), Hallazgo: Educación + Trabajo ≈ 65% de M0; Vivienda pesa el doble en lo rural (19% vs 10%), Pendiente: confirmar objetivo H con M0 como desempate lexicográfico (+7 more)

### Community 5 - "Lectura de microdatos DANE"
Cohesion: 0.18
Nodes (6): Archivo PERSONAS (DEPARTAMENTAL) 2025: respuestas de la encuesta, sin etiquetas, a_numero(), detectar_separador(), leer(), leer_cabecera(), ruta_csv()

### Community 6 - "Guía del proyecto y datos"
Cohesion: 0.19
Nodes (10): data/processed/hogares_antioquia.csv (base común de los 4 modelos), Convenciones: Python 3.13 .venv, pandas 3, PuLP 3.3 + HiGHS, parámetros en 06_parametros.py, reportar por zona, Entrada de los modelos: data/processed/hogares_antioquia.csv (3,732 hogares, 24 columnas), Fuentes de contexto: resumen (fuente de verdad), reglas de conteo, informe del Modelo 1, paper condensado, CLAUDE.md: guía de trabajo del proyecto para Claude Code, Línea base: 3,732 hogares, 523 pobres, H₀ 9.45%, M0 0.0387 (rural 25.18%), Resumen del proyecto IPM (fuente de verdad, actualizado 21-oct-2026), Planeado: 08_modelo1.py (presupuesto fijo + equidad r) (+2 more)

### Community 7 - "Presupuesto y verificación"
Cohesion: 0.22
Nodes (7): Probar primero con 50 hogares pobres y luego con los 523, Reglas para scripts de modelación (05 en adelante), Tras resolver: estado, objetivo, recalcular H y M0 desde N_ij con resumen() y reportar por zona, Restricción de presupuesto: Σ c_ij x_ij ≤ B, Validaciones: B = 0 reproduce la línea base; B ≥ $0.50 billones da H = 0; recalcular H y M0 desde x_ij, Presupuesto B con horizonte de un año, Rango de B: ≈ $0.50 billones sacan a todos los pobres; ≈ $7.29 billones quitan todas las privaciones

### Community 8 - "Umbral k y salidas rápidas"
Cohesion: 0.39
Nodes (8): Pesos IPM-Colombia: 5 dimensiones × 0.2, 15 indicadores, k = 1/3, Distancia al umbral y 'sale con 1' privación, Figura: distribución de puntajes de los 523 hogares pobres (135 en 0.34, justo sobre el umbral), Hallazgo: 77.6% de los hogares pobres sale con una sola intervención, Planeado: 06_parametros.py (costos, unidades, pesos y k en un solo lugar), MPI Árabe revisado (5 dimensiones, 14 indicadores, k = 20%), Umbral de pobreza k (P_i = 1 si Σ M_ij·w_j ≥ k), Ratio 2: P(sale de pobreza al quitar solo la privación j)

## Knowledge Gaps
- **11 isolated node(s):** `Cotas de esfuerzo l_j ≤ E_j ≤ u_j`, `Matriz aleatoria R ~ U[0,1] para el cambio estocástico de privaciones`, `Ratio 1: P(privado en j ⇒ pobre MD)`, `Stack: Python + PuLP + solver HiGHS`, `Hallazgo: 53% de las personas pobres vive en la cabecera` (+6 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 25 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Informe del Modelo 1: presupuesto fijo con equidad por zona` connect `Modelo 1: formulación y costos` to `Paper: modelos MILP y supuestos`, `Reglas de conteo u_ij`, `Línea base: H, A y M0`, `Guía del proyecto y datos`, `Presupuesto y verificación`, `Umbral k y salidas rápidas`?**
  _High betweenness centrality (0.207) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Modelo 2 - hogar, minimiza costo (first best, MILP)` (e.g. with `Modelo 1 (nuestro): max H sujeto a presupuesto B y equidad r — "dual" del Modelo 2 del paper` and `Objetivo: MILP de asignación óptima de inversión pública contra la pobreza multidimensional`) actually correct?**
  _`Modelo 2 - hogar, minimiza costo (first best, MILP)` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Cotas de esfuerzo l_j ≤ E_j ≤ u_j`, `Matriz aleatoria R ~ U[0,1] para el cambio estocástico de privaciones`, `Ratio 1: P(privado en j ⇒ pobre MD)` to the rest of the system?**
  _11 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Paper: modelos MILP y supuestos` be split into smaller, more focused modules?**
  _Cohesion score 0.14245014245014245 - nodes in this community are weakly interconnected._
- **Why does `Reglas de conteo de personas afectadas por privación (u_ij)` connect `Reglas de conteo u_ij` to `Modelo 1: formulación y costos`, `Validación IPM y zonas P3`, `Lectura de microdatos DANE`, `Guía del proyecto y datos`?**
  _High betweenness centrality (0.181) - this node is a cross-community bridge._
- **Should `Modelo 1: formulación y costos` be split into smaller, more focused modules?**
  _Cohesion score 0.11956521739130435 - nodes in this community are weakly interconnected._
- **Why does `Paper condensado: formulaciones de los 4 modelos (reemplaza leer el PDF)` connect `Paper: modelos MILP y supuestos` to `Modelo 1: formulación y costos`, `Validación IPM y zonas P3`, `Línea base: H, A y M0`, `Guía del proyecto y datos`, `Presupuesto y verificación`?**
  _High betweenness centrality (0.167) - this node is a cross-community bridge._