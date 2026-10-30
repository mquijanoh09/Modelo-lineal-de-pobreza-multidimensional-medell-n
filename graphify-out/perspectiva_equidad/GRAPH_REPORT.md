# Graph Report - Perspectiva de equidad del Modelo 1  (2026-10-28)

> Grafo construido a mano en formato graphify (node-link JSON, mismas claves que `graphify-out/graph.json`) para dar contexto a otro Claude sobre la **nueva perspectiva** del proyecto. Los nodos de la comunidad 7 son los mismos IDs del grafo base del 21-oct, así que los dos grafos se pueden unir.

## Contexto en 60 segundos (léelo primero)

- **Qué cambió:** el Modelo 1 (Tomás/Martín, presupuesto fijo) ya no solo maximiza H. Maximizar H premia sacar a los hogares *cerca del umbral* y deja intactos a los más pobres (en Antioquia el 49 % de los hogares pobres está a ≤ 0.05 del umbral). Se añadió un **techo de severidad** (ε-restricción) para que el modelo no abandone a los más pobres.
- **Formulación vigente** (detalle en `docs/informe_modelo1.md` §3.4 y §4):
  - Objetivo: max Σ p_i y_i − λ Σ p_i q_i, con p_i = HW_i·HS_i, λ < min p_i / Sev₀ ≈ 3×10⁻⁴ (desempate por severidad).
  - (1) presupuesto Σ c_ij x_ij ≤ B · (2) salida s_i ≤ 0.33 + M_i(1 − y_i), M_i = c_i⁰ − 0.33 · (4) equidad por zona Σ_{i∈d} p_i y_i ≥ r·Pobres_d⁰ · (5) rezago no intervenible · (7) q_i ≥ 2a·s_i − a² ∀a ∈ A_i · (8) Σ p_i q_i ≤ (1 − ρ)·Sev₀.
  - s_i = Σ_j w_j M_ij (1 − x_ij) es el puntaje **sin censurar** después de intervenir; la severidad se mide sobre los 523 hogares pobres iniciales. Sev₀ ≈ 117,908. Se quitaron C_i y la restricción (3): M0 se recalcula después.
- **ρ y r no se fijan a ojo:** se calculan extremos, se barre y se escoge con el codo o con la regla "la brecha no crece" (A de los que siguen pobres ≤ A₀). Reportar siempre H, A, M0 y severidad.
- **Identificación de pobres sin cambios:** pesos oficiales y k = 1/3. La entropía de Shannon (idea del paper LEPI) se probó y se descartó para identificar: con indicadores binarios premia la rareza (correlación −0.94 con la prevalencia) y bajaría H de 9.5 % a 2.2 %.
- **Costos actualizados (27-oct):** desocupados por perfil según Decreto 533/2024 (30 % 18–28 años, 20 % mujeres 29–56, 15 % hombres 29–61); mujeres ≥ 57 y hombres ≥ 62 → aporte a pensión. La unidad hogar/persona de toda la tabla se verificó con fuentes oficiales.
- **Severidad educativa (28-oct, propuesta para los 4 modelos):** techo sobre los años de atraso de los niños rezagados, Σ HW_k (a_k⁰ − z_k)² ≤ (1 − ρ_e)·SevEdu₀, lineal porque z_k es binaria; la restricción (10) liga z_k con la privación del hogar. Pendiente de acordar con Jerónimo (informe §3.5).
- **Rezago — ESTRATEGIA ADOPTADA (30-oct):** /mnt/project-files/rezago/informe_rezago_brecha_normalizada.md. Brecha normalizada g_k = a_k/(edad−6) al cuadrado, sin tope; m_k grados aprobados (CLEI, Aceleración); año que pasa con cohorte fija y techo contra el escenario sin intervención; (10a)/(10b) con m_k ≥ a_k⁰+1. Pago: corrida 1 sin condición; luego solo se paga a quien ganó el año (A/B descartadas). Pendiente: recalcular SevEdu^N_0 y ρ_e.
- **Costos (30-oct):** regla de fuente oficial. Verificación: https://claude.ai/artifact/Tim5YJJDpGstsHKB53ofj6. Corregidos: pisos/paredes urbano $25.62 M, acueducto+alcantarillado urbano $11.72 M, alcantarillado rural $15.3 M, logro educativo $2.88/3.86 M, analfabetismo CLEI ciclo 1; acueducto rural $43.7 M (BID $9.7 M sensibilidad); rezago = asignación por alumno SGP 2025; CLEI $958,431/$1,286,194. Recalcular rango de B.
- **Simuladores y artefactos (abrir con el enlace):**
  - Simulador de severidad educativa: https://claude.ai/artifact/Ps94qsu6az6vNPoG12JFtd
  - Gráficos "Del LEPI a la severidad": https://claude.ai/artifact/BuBAGxL76fucusQpwhPuHZ
  - Plan de datos compartidos para los 4 modelos: https://claude.ai/artifact/DhpmMww5UJpTMmYEsbC146
  - Bases de datos EAFIT para el proyecto IPM: https://claude.ai/artifact/CRUZ16i5GnYqNE2tHUfuC7
  - Verificación de costos por indicador: https://claude.ai/artifact/Tim5YJJDpGstsHKB53ofj6
- **Rezago (30-oct):** pago condicionado en corridas sucesivas (desde la 2.ª corrida solo se paga a quien ganó el año); se cuenta el año que pasa: a^t = a^{t−1} + 1 − grados aprobados, con cohorte fija (los 215 siguen aunque cumplan 18) y techo contra el escenario sin intervención; dos capas (IPM binario intacto + SevEdu por niño con z_k pagado; x_i,rez sin costo); α = 2 es el menor exponente que prioriza al niño más atrasado; ρ_e ≈ 29 % propuesto (máx 37.4 %); restricción (10) corregida a (10a)/(10b).
- **Abierto:** desempate en una o dos etapas (se recomienda dos, por la tolerancia de HiGHS); comunicar a Jerónimo el cambio de objetivo (afecta lo que se compara entre los Modelos 1–4).

## Summary
- 101 nodes · 139 edges · 10 communities · 9 hyperedges
- Extraction: 95% EXTRACTED · 5% INFERRED · construido manualmente (sin costo de tokens)

## Community Hubs (Navigation)
- Paper LEPI: método y crítica
- Crítica al objetivo H
- Entropía: evaluada y descartada para identificar
- Modelo 1 reformulado: severidad
- Escoger ρ y r: fronteras
- Costos verificados con fuentes oficiales
- Limitaciones y argumentos de defensa
- Grafo base (21-oct) — nodos ya existentes
- Simuladores y artefactos publicados (con enlace)
- Estrategia vigente del rezago (brecha normalizada, 30-oct)

## God Nodes (most connected - your core abstractions)
1. `Severidad educativa (28-oct, versión en años brutos, reemplazada por la brecha normalizada): SevEdu = Σ_k HW_k (a_k⁰ − z_k)² sobre años de atraso de 215 niños rezagados; SevEdu₀ ≈ 1,291,034` - 15 edges
2. `Restricción (8): Σ p_i q_i ≤ (1−ρ)·Sev₀  (ε-restricción)` - 8 edges
3. `Verificación oficial hogar vs persona (27-oct): la división del informe es correcta` - 8 edges
4. `Severidad = Σ_{i∈pobres₀} p_i s_i² (FGT α=2 sobre el puntaje, SIN censurar)` - 7 edges
5. `SIMULADOR de severidad educativa (28-oct): juguete de 6 niños (cuadrados a×a, franja 2a−1), frontera ρ_e vs costo con los 215 niños, solver vs sorteo, α=1/2/3` - 7 edges
6. `Maximizar H premia cruzar el umbral, no reducir privaciones: el modelo atiende primero a los 'menos pobres'` - 6 edges
7. `Objetivo vigente: max Σ p_i y_i − λ Σ p_i q_i (H principal, severidad desempate)` - 6 edges
8. `Barrer ρ entre extremos: ρ=0 (H puro) y min severidad s.a. presupuesto y equidad` - 6 edges
9. `Restricción (10) vigente: (10a) x_i,rez ≤ z_k si a_k⁰ + 1 ≤ m_k; (10b) x_i,rez = 0 si algún a_k⁰ + 1 > m_k (un año regular ya no quita la privación); costo por niño Σ c_k z_k` - 6 edges
10. `ESTRATEGIA ADOPTADA para el rezago (Martín, 30-oct): informe_rezago_brecha_normalizada.md — fuente de verdad del indicador de rezago` - 6 edges

## Hyperedges (group relationships)
- **Formulación vigente del Modelo 1 (27-oct-2026)** — objetivo_c, techo_severidad, q_tangentes, desempate_severidad, bigm_por_hogar, sev_edu_lineal, rest_10_rezago, docs_resumen_proyecto_ipm_restriccion_equidad, docs_informe_modelo1_restriccion_no_intervenibles [EXTRACTED 1.00]
- **Decisiones de la nueva perspectiva (22–27 oct)** — tres_opciones, decision_identificar_oficial, desempate_severidad, bigm_por_hogar, epv_perfil, pension_edad, sev_edu [EXTRACTED 1.00]
- **Cómo escoger ρ y r** — barrido_rho, codo, regla_brecha, barrido_r, malla_r_rho, reportar_cuatro [EXTRACTED 1.00]
- **Severidad educativa del rezago (28-oct)** — sev_edu, sev_edu_lineal, rest_10_rezago, sev_edu_4modelos, precio_focalizar, alpha_fgt, rho_e_eleccion, sim_sevedu, rezago_dos_capas, rezago_reporte, ninos_rezago_csv, pago_condicionado, anio_que_pasa [EXTRACTED 1.00]
- **Simuladores y artefactos para volver a abrir** — sim_sevedu, art_lepi, art_datos, art_bases, art_costos [EXTRACTED 1.00]
- **Estrategia vigente del rezago (30-oct)** — rez_estrategia, brecha_normalizada, sin_tope, m_k_grados, sevedu_n_contrafactual, cohorte_fija, rest_10_rezago, clei_norma, clei_costo, asistencia_pendiente, pago_condicionado, rez_recalcular [EXTRACTED 1.00]
- **Costos verificados con fuente oficial (30-oct)** — regla_costos_oficiales, costos_verificados, costos_corregidos, acueducto_rural, clei_costo, costo_rezago_sgp, art_costos, presupuesto_recalcular [EXTRACTED 1.00]
- **Supuestos y limitaciones a defender** — sup_pension_buscar, sup_efectividad, af_binario, empleo_hipotetico, severidad_agregada [EXTRACTED 1.00]
- **Verificación oficial de unidades de costo** — v_fonvivienda, v_renta, v_upc, v_cdi, v_alfab, empleos_vida [EXTRACTED 1.00]

## Communities (10 total)

### Community 0 - "Paper LEPI: método y crítica"
Nodes (9):
- `lepi_paper` — Paper LEPI: Localized Energy Poverty Index (5 zonas no interconectadas de Colombia)
- `entropia_shannon` — Pesos por entropía de Shannon: w_j = (1−e_j)/Σ(1−e_j); mide qué tan desigual es el reparto, no la gravedad
- `lepi_critica` — Crítica numérica: pesos de Tablas 4-5 no reproducibles, signos mezclados, |·| voltea sentido (Norte −0.56), Pacífico = 3.59 de interrupciones
- `lepi_formula` — Fórmula reconstruida: LEPI_i = |Σ w_j (x_ij − x_ref,j)/x_ref,j|; reproduce Tabla 6 (0, 0.02, 3.93, 0.56, 0.16)
- `lepi_es_madm` — El paper es EVALUACIÓN (MADM), no optimización: alternativas dadas, sin variables ni restricciones  
  _Por qué:_ Tres pruebas: ¿las alternativas existen antes? ¿hay variables de decisión? ¿entrega diagnóstico o acción?
- `madm_vs_modm` — MADM (evaluar alternativas finitas: TOPSIS, AHP, entropía) vs MODM (optimizar región factible: MILP)
- `topsis` — TOPSIS: C_i = d⁻/(d⁺+d⁻); ranking depende de direcciones no declaradas (Amazonía 1.ª solo en 47% de 4,096 combinaciones)
- `lepi_uso_proyecto` — Uso en el proyecto: idea de medir relativo/local; método, no evidencia de resultados
- `lepi_lp_minimax` — Reformulación propuesta del LEPI como LP minimax: min t s.a. t ≥ LEPI_i(x), presupuesto, 0 ≤ x ≤ brecha

### Community 1 - "Crítica al objetivo H"
Nodes (6):
- `severidad_def` — Severidad = Σ_{i∈pobres₀} p_i s_i² (FGT α=2 sobre el puntaje, SIN censurar)  
  _Por qué:_ El cuadrado pesa más a los más hondos: 0.80→0.70 baja 0.15, 0.40→0.30 baja 0.07. Sensible a desigualdad entre pobres: (0.5,0.5)=0.50 < (0.4,0.6)=0.52 con la misma A.
- `critica_objetivo_h` — Maximizar H premia cruzar el umbral, no reducir privaciones: el modelo atiende primero a los 'menos pobres'
- `brecha_relativa` — Lo que sube es A de los que siguen pobres (brecha relativa), no se empeora a nadie
- `tres_opciones` — Tres objetivos evaluados: A severidad, B minimax (Rawls), C ε-restricción — Martín eligió C (22-oct)
- `dato_cerca_umbral` — Antioquia: 49% de hogares pobres a ≤ 0.05 del umbral; 51% de personas pobres con puntaje 0.34–0.40; 3.5% ≥ 0.60
- `m0_parcial` — M0 corrige solo en parte: sigue premiando el cruce (censurado cae a 0)

### Community 2 - "Entropía: evaluada y descartada para identificar"
Nodes (4):
- `entropia_rareza` — Con privaciones binarias la entropía premia la RAREZA: correlación de rangos prevalencia–peso = −0.94
- `entropia_cambia_h` — Con pesos por entropía y mismo k, H pasaría de 9.5% a 2.2% (462 hogares cambian de estado): rompe comparabilidad DANE
- `decision_identificar_oficial` — Decisión: identificar pobres con pesos oficiales y k = 1/3; entropía a lo sumo como sensibilidad en la priorización
- `dato_empleo_trabajo` — Empleo formal: 67% prevalencia, 24% de M0, peso entropía 0.021 (el más bajo); trabajo infantil: 2%, peso 0.098

### Community 3 - "Modelo 1 reformulado: severidad"
Nodes (19):
- `sev_edu` — Severidad educativa (28-oct, versión en años brutos, reemplazada por la brecha normalizada): SevEdu = Σ_k HW_k (a_k⁰ − z_k)² sobre años de atraso de 215 niños rezagados; SevEdu₀ ≈ 1,291,034  
  _Por qué:_ El rezago binario abandona a niños con ≥ 2 años de atraso (132 de 215). Sobre el atraso cardinal la severidad es legítima en Alkire-Foster.
- `techo_severidad` — Restricción (8): Σ p_i q_i ≤ (1−ρ)·Sev₀  (ε-restricción)
- `objetivo_c` — Objetivo vigente: max Σ p_i y_i − λ Σ p_i q_i (H principal, severidad desempate)
- `rest_10_rezago` — Restricción (10) vigente: (10a) x_i,rez ≤ z_k si a_k⁰ + 1 ≤ m_k; (10b) x_i,rez = 0 si algún a_k⁰ + 1 > m_k (un año regular ya no quita la privación); costo por niño Σ c_k z_k  
  _Por qué:_ La versión anterior x ≤ 1 − a⁰ + z daba lado derecho negativo con a⁰ ≥ 3 e infactibilizaba el modelo.
- `pago_condicionado` — Condición de pago multiperiodo (decidido 30-oct): corrida 1 sin condición; corrida t≥2: z_k^t ≤ 1 − z_k^{t−1}(1 − ap_k^{t−1}), ap_k = ganó el año escolar (único requisito; asistencia ≥80% descartada 30-oct); atraso baja solo si cumplió; ap_k por Monte Carlo  
  _Por qué:_ Ejemplo María (gana) sigue elegible; Tomás (pierde) no se le paga el año siguiente. Pendiente: si Tomás queda excluido solo un año o para siempre; probabilidad de aprobar con fuentes MEN.
- `sev_edu_4modelos` — SevEdu reproducible en los 4 modelos (1-2 solver elige z_k; 3-4 por sorteo R) — pendiente de acordar con Jerónimo
- `alpha_fgt` — Exponente α (FGT): α=0 abandona a los muy atrasados, α=1 es indiferente entre niños, α=2 es el menor que prioriza al más atrasado (nivelar vale 2a−1); Σa² = N(μ²+σ²) mide promedio y desigualdad
- `rezago_dos_capas` — Rezago en DOS CAPAS (30-oct): (1) IPM oficial intacto, privación del hogar sí/no (peso 0.05) define H; (2) SevEdu por niño debajo, z_k pagado a $6.3 M·HW_k; x_i,rez sin costo propio  
  _Por qué:_ Así H sigue siendo comparable con el DANE y el techo atiende a los niños con 2+ años de atraso, que este año no cambian el IPM.
- `anio_que_pasa` — Contar el año que pasa (decidido 30-oct): a_k^t = a_k^{t−1} + 1 − g_k (grados aprobados: 1 regular, 2 CLEI ciclos 2–4, 3 ciclo 1, 0 si pierde); COHORTE FIJA (los 215 siguen aunque cumplan 18); techo contra el escenario sin intervención; un año regular aprobado solo evita que el atraso crezca (detalle: informe_rezago_brecha_normalizada §4.6)  
  _Por qué:_ Ej.: 17 años con 6 de atraso que aprueba CLEI ciclo 3 queda en 5 y sigue en la cohorte. El atraso neto solo baja con CLEI o Aceleración del Aprendizaje.
- `desempate_severidad` — Desempate por severidad (decidido 26-oct): λ < min p_i / Sev₀ ≈ 3×10⁻⁴
- `ninos_rezago_csv` — Datos: tabla por niño ninos_rezago.csv (hogar, zona, edad, atraso a_k⁰, FEX_C) exportada por el 05 para los 4 modelos; 215 niños, 149 hogares
- `sin_ci` — Se quitan C_i y la restricción (3): M0 se recalcula después de resolver
- `sev_edu_lineal` — (a⁰ − z)² = (a⁰)² − (2a⁰ − 1)z con z binaria: techo (9) lineal y exacto; nivelar 1 año baja 1, 3 años baja 5
- `sev0` — Sev₀ ≈ 117,908 (0.0163 por persona; M0 = 0.0387)
- `q_tangentes` — Restricción (7): q_i ≥ 2a·s_i − a² ∀a ∈ A_i (valores alcanzables de s_i); 6,571 cortes  
  _Por qué:_ s² − T_a(s) = (s−a)² ≥ 0: tangentes por debajo, iguales en s = a ⇒ exacto en los puntos alcanzables. Funciona por convexidad + techo ≤.
- `dos_etapas` — Pendiente: hacer el desempate en DOS ETAPAS (max H; luego min Σp q con Σp y ≥ H*) — recomendado por tolerancia de HiGHS (mip_rel_gap 1e-4 ≈ 68 personas)
- `bigm_por_hogar` — bigM por hogar M_i = c_i⁰ − 0.33 (27-oct): mismo óptimo, relajación más ajustada (hogar 0.40: y ≤ 0.93 con M=1 vs y ≤ 0)
- `menor_estricto` — '< 0.34' se escribe '≤ 0.33': pesos múltiplos de 0.01; MILP no admite desigualdad estricta
- `severidad_agregada` — El techo es agregado: no garantiza ayuda a cada hogar muy pobre, hace infactible abandonarlos a todos

### Community 4 - "Escoger ρ y r: fronteras"
Nodes (10):
- `barrido_rho` — Barrer ρ entre extremos: ρ=0 (H puro) y min severidad s.a. presupuesto y equidad
- `rho_e_eleccion` — [CALCULADO CON AÑOS BRUTOS — RECALCULAR con brecha normalizada] Escoger ρ_e: máx 37.4% en un año; sin techo solo 1.3%; codos 29% (todos con atraso ≥3, $151 mm) y 33.6% (≥2, $220 mm); propuesta ρ_e≈29% central, sensibilidad 20% y 33.6%; confirmar con MILP completo (H vs ρ_e)
- `barrido_r` — r: cota r_libre = min_d salidas_d/Pobres_d (con r=0) y r_max por maximin; barrer entre ellas → precio de la equidad
- `precio_focalizar` — Resultado esperado: modelos 3-4 necesitan más esfuerzo para el mismo ρ_e (precio de no poder focalizar)
- `rezago_reporte` — Reportar para rezago: SevEdu, niños nivelados por años de atraso y hogares que salen del rezago, además de H, A, M0 y severidad
- `codo` — Codo (knee point): punto de la frontera más lejos de la recta entre extremos; rendimientos decrecientes
- `regla_brecha` — Regla 'la brecha no crece': ρ más laxo con A(pobres restantes) ≤ A₀
- `reportar_cuatro` — Reportar siempre H, A, M0 y severidad
- `malla_r_rho` — Malla (r, ρ): fijar r primero, luego barrer ρ; (4) y (8) pueden chocar → mapa de factibilidad
- `equidad_dos_tipos` — (4) = equidad entre territorios (salidas por zona); (8) = equidad entre pobres (profundidad)

### Community 5 - "Costos verificados con fuentes oficiales"
Nodes (16):
- `verif_hogar_persona` — Verificación oficial hogar vs persona (27-oct): la división del informe es correcta
- `costos_corregidos` — Costos corregidos (30-oct): pisos/paredes urbano $25.62 M (18 SMMLV, Dec. 0413/2025); acueducto+alcantarillado urbano $11.72 M (8.23 SMMLV, Dec. 1275/2021); alcantarillado rural $15.3 M (2022→2025); logro educativo $2.88 M / $3.86 M (3 ciclos CLEI); analfabetismo CLEI ciclo 1
- `epv_perfil` — Costo por desocupado según perfil: 18–28 30% ($5.12 M), mujer 29–56 20% ($3.42 M), hombre 29–61 15% ($2.56 M)
- `costo_rezago_sgp` — Costo del rezago (30-oct): asignación por alumno SGP 2025, ETC Antioquia (Anexo 1 DD SGP-96-2025): urbana 2.71/3.05/3.22 M, rural 3.52/3.96/4.18 M (primaria/secundaria/media); reemplaza $6.3 M sin fuente  
  Fuente: https://colaboracion.dnp.gov.co/CDT/Inversiones%20y%20finanzas%20pblicas/Documentos%20GFT/Distribuciones%20SGP/Anexos%201%20al%204%20DD%20SGP-96-2025.xlsx
- `clei_costo` — Costo CLEI por ciclo 2025: $958,431 urbano / $1,286,194 rural (asignación por alumno, Anexo 1 DD SGP-96-2025, DNP)  
  Fuente: https://colaboracion.dnp.gov.co/CDT/Inversiones%20y%20finanzas%20pblicas/Documentos%20GFT/Distribuciones%20SGP/Anexos%201%20al%204%20DD%20SGP-96-2025.xlsx
- `empleos_vida` — Empleos para la Vida (Decreto 533/2024): incentivo al EMPLEADOR por trabajador adicional; hasta 24 meses  
  Fuente: https://www.funcionpublica.gov.co/eva/gestornormativo/norma_pdf.php?i=239156
- `costos_verificados` — Costos verificados (30-oct): SMMLV $1,423,500 (Dec. 1572/2024); UPC-S y prima rural 11.47% (Res. 2717/2024); EpV 30/20/15% (Dec. 533/2024); pensión 16% = $2,733,120; Renta Ciudadana; CDI $5,210,277 (Res. 5288/2025); hacinamiento 22 SMMLV; vivienda rural $35.2 M
- `acueducto_rural` — Acueducto rural base $43.7 M (Minvivienda, Alpujarra, 2025) — decisión de Martín; BID $9.7 M queda como sensibilidad baja
- `pension_edad` — Mujeres ≥ 57 y hombres ≥ 62 desocupados: aporte a pensión ($2.73 M) en vez de Empleos para la Vida (decisión de Martín)
- `v_fonvivienda` — Fonvivienda: subsidio por hogar, ≤ 22 SMMLV por unidad habitacional (Res. 0990/2024)  
  Fuente: https://www.minvivienda.gov.co/sites/default/files/normativa/0990-02-12-2024.pdf
- `v_renta` — Renta Ciudadana: transferencia por hogar (hasta $500,000 cada 45 días)  
  Fuente: https://prosperidadsocial.gov.co/Noticias/hoy-nace-renta-ciudadana-la-evolucion-de-los-programas-contra-la-pobreza-extrema-en-colombia-directora-laura-sarabia/
- `v_upc` — UPC-S 2025 por afiliado: $1,323,403; con dispersión 11.47%: $1,475,197 (Res. 2717/2024)  
  Fuente: https://minsalud.gov.co/Normatividad_Nuevo/Resolución%20No%202717%20de%202024.pdf
- `v_cdi` — CDI ICBF por cupo (niño): $504,695/mes, $5,210,277/año (Res. 5288/2025)
- `v_alfab` — Alfabetización MEN financiada por proyecto (≈ $0.71 M por persona derivado); usamos $0.78 M
- `dato_desocupados` — 34 desocupados en 32 hogares pobres: 13 jóvenes, 7 mujeres, 10 hombres, 4 en edad de pensión; costo $174 M → $127 M
- `discap_10pct` — Discapacidad (35%) no aplicable: PERSONAS no trae la variable; 10% adicional (par. 7) como sensibilidad

### Community 6 - "Limitaciones y argumentos de defensa"
Nodes (10):
- `af_binario` — Alkire-Foster define M_α (α≥1) solo para indicadores cardinales; con binarios solo M0 → la severidad es extensión FGT
- `rezago_equidad` — Rezago: la opción C resuelve eficiencia, no equidad; niños con 3+ años de atraso no se premian en 1 año (ni con severidad)
- `regla_costos_oficiales` — Regla de Martín (30-oct): todo costo debe tener fuente oficial y ser real (norma, resolución o documento con enlace); si no hay fuente, decirlo
- `presupuesto_recalcular` — Pendiente: recalcular el rango de B ($0.50 y $7.29 billones) con los costos nuevos (el acueducto rural lo sube bastante)
- `rezago_vs_inasistencia` — No confundir: Monte Carlo + p es de INASISTENCIA (¿asistirá?), no de rezago (límite de tiempo)
- `sup_pension_buscar` — Supuesto: al quedar cubierto por pensión, el desocupado deja de buscar empleo (si no, la privación sigue)
- `sup_efectividad` — Supuesto: pagar el incentivo se traduce en contratación (el empleador decide)
- `empleo_hipotetico` — Aporte a pensión de informales: intervención hipotética costeada con la tasa de cotización (no existe subsidio oficial)
- `pendiente_jeronimo` — Pendiente: contarle a Jerónimo el cambio de objetivo (cambia lo que se compara entre modelos)
- `hogares_pobres_porque` — Solo 523 hogares: no pobres no aportan al objetivo, intervenirlos solo cuesta, y por supuesto no se vuelven pobres

### Community 7 - "Grafo base (21-oct) — nodos ya existentes"
Nodes (13):
- `docs_resumen_proyecto_ipm_decision_rezago_opcion_c` — Decisión: rezago opción C
- `docs_informe_modelo1_modelo1_presupuesto_fijo` — Modelo 1 (nuestro): max H sujeto a presupuesto B y equidad r
- `docs_informe_modelo1_linealizacion_compacta` — Linealización compacta s_i ≤ 0.33 + (1 − y_i), C_i ≥ s_i − y_i
- `docs_informe_modelo1_objetivo_lexicografico` — Objetivo anterior: max Σp·y − λ Σp·C (M0 desempate) — REEMPLAZADO
- `docs_resumen_proyecto_ipm_restriccion_equidad` — Equidad: Σ_{i∈d} p_i y_i ≥ r·Pobres_d⁰
- `docs_resumen_proyecto_ipm_decision_empleo_formal_tres_casos` — Decisión: empleo_formal en 3 casos
- `docs_resumen_proyecto_ipm_decision_inasistencia_condicionada` — Decisión: inasistencia condicionada (p + Monte Carlo)
- `docs_resumen_proyecto_ipm_costos_epf` — Costos EpF_j 2025 urbano/rural
- `docs_informe_modelo1_limitacion_multiperiodo` — Limitación: horizonte de un año (multiperiodo = futuro)
- `docs_resumen_proyecto_ipm_parametros_validados` — Parámetros validados: w_j, k ≥ 0.34, HS_i, HW_i, P3
- `docs_informe_modelo1_restriccion_no_intervenibles` — No intervenibles: x_ij = 0 (rezago ≥ 2 años)
- `docs_resumen_proyecto_ipm_solo_hogares_pobres` — Solo importan los hogares pobres (reducción exacta)
- `referencias_paper_pobreza_multidimensional_opti1_model_2` — Hamie et al. Modelo 2 (min costo s.a. meta)

### Community 8 - "Simuladores y artefactos publicados (con enlace)"
Nodes (5):
- `sim_sevedu` — SIMULADOR de severidad educativa (28-oct): juguete de 6 niños (cuadrados a×a, franja 2a−1), frontera ρ_e vs costo con los 215 niños, solver vs sorteo, α=1/2/3  
  _Por qué:_ Para entender cómo se escoge ρ_e y por qué α=2. Sorteo (M3-4) cuesta $295 mm vs $151 mm del solver para ρ_e=29% (costos SGP 2025 por zona y nivel; v2 30-oct).  
  Fuente: https://claude.ai/artifact/Ps94qsu6az6vNPoG12JFtd
- `art_lepi` — GRÁFICOS 'Del LEPI a la severidad' (26-oct): análisis del paper LEPI, entropía vs gravedad, ejemplo de ρ  
  _Por qué:_ Gráficas reales del análisis del paper y de por qué se descartó la entropía para identificar.  
  Fuente: https://claude.ai/artifact/BuBAGxL76fucusQpwhPuHZ
- `art_costos` — DOC 'Verificación de costos por indicador del IPM' (30-oct): 10 verificados, 4 corregidos, acueducto rural decidido  
  Fuente: https://claude.ai/artifact/Tim5YJJDpGstsHKB53ofj6
- `art_datos` — DOC 'Datos compartidos para los 4 modelos: plan del 05 y el 06' (29-oct)  
  _Por qué:_ Plan de conteo_pares.csv, ninos_rezago.csv y parametros.py compartidos con Jerónimo.  
  Fuente: https://claude.ai/artifact/DhpmMww5UJpTMmYEsbC146
- `art_bases` — DOC 'Bases de datos EAFIT para el proyecto IPM' (29-oct)  
  Fuente: https://claude.ai/artifact/CRUZ16i5GnYqNE2tHUfuC7

### Community 9 - "Estrategia vigente del rezago (brecha normalizada, 30-oct)"
Nodes (9):
- `rez_estrategia` — ESTRATEGIA ADOPTADA para el rezago (Martín, 30-oct): informe_rezago_brecha_normalizada.md — fuente de verdad del indicador de rezago  
  _Por qué:_ Martín: 'Por el momento tomaremos como estrategia para calcular el indicador de rezago estudiantil la anexada en el .md'. Archivo en /mnt/project-files/rezago/.
- `brecha_normalizada` — Brecha normalizada Alkire-Foster: g_k = a_k/e_k, e_k = edad−6, entre 0 y 1; se usa g_k² en vez de a_k² (11 años de atraso pesa 1, no 121)
- `m_k_grados` — m_k = grados que el niño aprueba en el año: 1 año regular, 2 promoción anticipada o CLEI ciclos 2–4, 3 CLEI ciclo 1, Aceleración = lo que falte de primaria; nivelación neta m_k − 1
- `sevedu_n_contrafactual` — SevEdu^N_1 = Σ HW_k((b_k − d_k z_k)/(e_k+1))², b_k = a_k⁰ + 1 − asiste_k·ap_k (sin intervenir), d_k = m_k − asiste_k·ap_k; techo SevEdu^N_1 ≤ (1−ρ_e)·SevEdu^N_1,sin; lineal (z binaria)
- `cohorte_fija` — Cohorte fija: los 215 niños siguen en la suma y en la privación del hogar aunque cumplan 18 (si no, el modelo reduce H gratis)
- `rez_recalcular` — Pendiente: recalcular SevEdu^N_0 (el 1,291,034 en años² ya no sirve), b_k, rango y codos de ρ_e (el 29% era con años brutos), simulador en dos escalas; contar a Jerónimo
- `sin_tope` — No poner tope al atraso: cortar es abandonar a los más rezagados; con g el peso máximo ya es 1; reportar aparte a los g = 1 (nunca han aprobado un año)
- `clei_norma` — CLEI (Decreto 1075/2015): ciclos 1 (1.º–3.º), 2 (4.º–5.º), 3 (6.º–7.º), 4 (8.º–9.º) de 40 semanas; media 2 ciclos de 22 semanas; ingreso ≥13 sin primaria o ≥15 con primaria  
  Fuente: https://normativa.colpensiones.gov.co/colpens/docs/decreto_1075_2015_pr017.htm
- `asistencia_pendiente` — Asistencia: opciones A/B DESCARTADAS (30-oct). Corrida 1 sin condición; luego el único requisito de pago es ganar el año (ap_k). Los 49 de 132 que no asisten pueden entrar (≥13 años vía CLEI)

## Edges
- `lepi_paper` --classified_as--> `lepi_es_madm`
- `lepi_es_madm` --explained_by--> `madm_vs_modm`
- `lepi_paper` --uses--> `entropia_shannon`
- `lepi_paper` --uses--> `topsis`
- `lepi_paper` --defines--> `lepi_formula`
- `lepi_formula` --criticized_by--> `lepi_critica`
- `entropia_shannon` --criticized_by--> `lepi_critica`
- `topsis` --criticized_by--> `lepi_critica`
- `lepi_paper` --informs--> `lepi_uso_proyecto`
- `lepi_lp_minimax` --reformulates--> `lepi_formula`
- `madm_vs_modm` --contrasts_with--> `docs_informe_modelo1_modelo1_presupuesto_fijo`
- `lepi_uso_proyecto` --motivates--> `critica_objetivo_h`  [INFERRED 0.8]
- `critica_objetivo_h` --criticizes--> `docs_informe_modelo1_objetivo_lexicografico`
- `dato_cerca_umbral` --supports--> `critica_objetivo_h`
- `critica_objetivo_h` --precised_by--> `brecha_relativa`
- `critica_objetivo_h` --partially_fixed_by--> `m0_parcial`
- `critica_objetivo_h` --fixed_by--> `severidad_def`
- `severidad_def` --used_in--> `tres_opciones`
- `tres_opciones` --chosen_as--> `techo_severidad`
- `entropia_shannon` --tested_on_antioquia--> `entropia_rareza`
- `dato_empleo_trabajo` --supports--> `entropia_rareza`
- `entropia_rareza` --implies--> `entropia_cambia_h`
- `entropia_cambia_h` --leads_to--> `decision_identificar_oficial`
- `decision_identificar_oficial` --keeps--> `docs_resumen_proyecto_ipm_parametros_validados`
- `objetivo_c` --replaces--> `docs_informe_modelo1_objetivo_lexicografico`
- `objetivo_c` --modifies--> `docs_informe_modelo1_modelo1_presupuesto_fijo`
- `techo_severidad` --constrains--> `objetivo_c`
- `severidad_def` --measured_by--> `techo_severidad`
- `sev0` --parameter_of--> `techo_severidad`
- `q_tangentes` --linearizes--> `techo_severidad`
- `desempate_severidad` --part_of--> `objetivo_c`
- `dos_etapas` --alternative_to--> `desempate_severidad`
- `bigm_por_hogar` --refines--> `docs_informe_modelo1_linealizacion_compacta`
- `menor_estricto` --justifies--> `docs_informe_modelo1_linealizacion_compacta`
- `sin_ci` --simplifies--> `docs_informe_modelo1_linealizacion_compacta`
- `sin_ci` --consequence_of--> `desempate_severidad`
- `severidad_agregada` --clarifies--> `techo_severidad`
- `barrido_rho` --tunes--> `techo_severidad`
- `codo` --selects_on--> `barrido_rho`
- `regla_brecha` --selects_on--> `barrido_rho`
- `regla_brecha` --operationalizes--> `brecha_relativa`
- `reportar_cuatro` --accompanies--> `barrido_rho`
- `barrido_r` --tunes--> `docs_resumen_proyecto_ipm_restriccion_equidad`
- `barrido_r` --same_trick_as--> `lepi_lp_minimax`  [INFERRED 0.8]
- `malla_r_rho` --combines--> `barrido_r`
- `malla_r_rho` --combines--> `barrido_rho`
- `equidad_dos_tipos` --explains--> `docs_resumen_proyecto_ipm_restriccion_equidad`
- `equidad_dos_tipos` --explains--> `techo_severidad`
- `verif_hogar_persona` --validates--> `docs_resumen_proyecto_ipm_costos_epf`
- `v_fonvivienda` --evidence_for--> `verif_hogar_persona`
- `v_renta` --evidence_for--> `verif_hogar_persona`
- `v_upc` --evidence_for--> `verif_hogar_persona`
- `v_cdi` --evidence_for--> `verif_hogar_persona`
- `v_alfab` --evidence_for--> `verif_hogar_persona`
- `empleos_vida` --evidence_for--> `verif_hogar_persona`
- `empleos_vida` --determines--> `epv_perfil`
- `epv_perfil` --updates--> `docs_resumen_proyecto_ipm_decision_empleo_formal_tres_casos`
- `pension_edad` --exception_to--> `epv_perfil`
- `dato_desocupados` --quantifies--> `epv_perfil`
- `discap_10pct` --limits--> `epv_perfil`
- `sup_pension_buscar` --required_by--> `pension_edad`
- `sup_efectividad` --required_by--> `empleos_vida`
- `af_binario` --qualifies--> `severidad_def`
- `rezago_equidad` --limits--> `docs_resumen_proyecto_ipm_decision_rezago_opcion_c`
- `rezago_equidad` --same_as--> `docs_informe_modelo1_limitacion_multiperiodo`
- `rezago_vs_inasistencia` --clarifies--> `docs_resumen_proyecto_ipm_decision_inasistencia_condicionada`
- `rezago_vs_inasistencia` --clarifies--> `docs_resumen_proyecto_ipm_decision_rezago_opcion_c`
- `empleo_hipotetico` --qualifies--> `docs_resumen_proyecto_ipm_decision_empleo_formal_tres_casos`
- `pendiente_jeronimo` --about--> `objetivo_c`
- `hogares_pobres_porque` --justifies--> `docs_resumen_proyecto_ipm_solo_hogares_pobres`
- `docs_informe_modelo1_modelo1_presupuesto_fijo` --dual_of--> `referencias_paper_pobreza_multidimensional_opti1_model_2`
- `rezago_equidad` --not_captured_by--> `severidad_def`  [INFERRED 0.85]
- `sev_edu` --fixes--> `rezago_equidad`
- `sev_edu_lineal` --linearizes--> `sev_edu`
- `rest_10_rezago` --generalizes--> `docs_resumen_proyecto_ipm_decision_rezago_opcion_c`
- `rest_10_rezago` --links_to_ipm--> `sev_edu`
- `sev_edu` --analogous_to--> `severidad_def`
- `sev_edu_4modelos` --extends--> `sev_edu`
- `precio_focalizar` --result_of--> `sev_edu_4modelos`
- `sev_edu` --answers--> `af_binario`  [INFERRED 0.85]
- `sev_edu` --constrains--> `objetivo_c`
- `alpha_fgt` --parametrizes--> `sev_edu`
- `alpha_fgt` --answers--> `af_binario`  [INFERRED 0.85]
- `rho_e_eleccion` --tunes--> `sev_edu`
- `rho_e_eleccion` --applies--> `codo`
- `rho_e_eleccion` --analogous_to--> `barrido_rho`
- `sim_sevedu` --simulates--> `sev_edu`
- `sim_sevedu` --illustrates--> `sev_edu_lineal`
- `sim_sevedu` --illustrates--> `alpha_fgt`
- `sim_sevedu` --computes--> `rho_e_eleccion`
- `sim_sevedu` --quantifies--> `precio_focalizar`
- `art_lepi` --illustrates--> `lepi_critica`
- `art_lepi` --illustrates--> `entropia_shannon`
- `art_lepi` --illustrates--> `severidad_def`
- `art_datos` --implements--> `sev_edu_4modelos`
- `art_bases` --references--> `docs_resumen_proyecto_ipm_parametros_validados`  [INFERRED 0.7]
- `rezago_dos_capas` --structures--> `sev_edu`
- `rezago_dos_capas` --links_via--> `rest_10_rezago`
- `rezago_dos_capas` --keeps--> `docs_resumen_proyecto_ipm_decision_rezago_opcion_c`
- `rest_10_rezago` --replaces_for_rezago--> `docs_informe_modelo1_restriccion_no_intervenibles`
- `rezago_reporte` --reports--> `rezago_dos_capas`
- `rezago_reporte` --extends--> `reportar_cuatro`
- `ninos_rezago_csv` --feeds--> `sev_edu`
- `ninos_rezago_csv` --enables--> `sev_edu_4modelos`
- `art_datos` --specifies--> `ninos_rezago_csv`
- `pago_condicionado` --conditions--> `sev_edu`
- `pago_condicionado` --implements--> `docs_informe_modelo1_limitacion_multiperiodo`
- `pago_condicionado` --analogous_to--> `docs_resumen_proyecto_ipm_decision_inasistencia_condicionada`  [INFERRED 0.8]
- `costo_rezago_sgp` --prices--> `rest_10_rezago`
- `costo_rezago_sgp` --feeds--> `sim_sevedu`
- `anio_que_pasa` --updates_state_of--> `pago_condicionado`
- `anio_que_pasa` --changes--> `sev_edu`
- `rez_estrategia` --adopts--> `brecha_normalizada`
- `rez_estrategia` --adopts--> `sevedu_n_contrafactual`
- `rez_estrategia` --adopts--> `cohorte_fija`
- `rez_estrategia` --adopts--> `m_k_grados`
- `rez_estrategia` --adopts--> `sin_tope`
- `rez_estrategia` --updates--> `rest_10_rezago`
- `brecha_normalizada` --replaces--> `sev_edu`
- `brecha_normalizada` --keeps_alpha_2--> `alpha_fgt`
- `brecha_normalizada` --follows--> `af_binario`
- `sevedu_n_contrafactual` --formalizes--> `anio_que_pasa`
- `cohorte_fija` --qualifies--> `anio_que_pasa`
- `m_k_grados` --defined_by--> `clei_norma`
- `clei_costo` --prices--> `m_k_grados`
- `clei_costo` --complements--> `costo_rezago_sgp`
- `asistencia_pendiente` --resolved_by--> `pago_condicionado`
- `rez_recalcular` --invalidates--> `rho_e_eleccion`
- `rez_recalcular` --requires_update--> `sim_sevedu`
- `art_costos` --documents--> `costos_verificados`
- `art_costos` --documents--> `costos_corregidos`
- `art_costos` --documents--> `acueducto_rural`
- `costos_corregidos` --updates--> `docs_resumen_proyecto_ipm_costos_epf`
- `costos_verificados` --extends--> `verif_hogar_persona`
- `costos_corregidos` --uses--> `clei_costo`
- `regla_costos_oficiales` --motivated--> `costos_corregidos`
- `regla_costos_oficiales` --motivated--> `costo_rezago_sgp`
- `presupuesto_recalcular` --caused_by--> `costos_corregidos`
- `presupuesto_recalcular` --caused_by--> `acueducto_rural`
