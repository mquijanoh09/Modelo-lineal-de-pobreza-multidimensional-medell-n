# Graph Report - Perspectiva de equidad del Modelo 1  (actualizado 2026-11-05)

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

- **REZAGO, INASISTENCIA Y SevEdu — SÍNTESIS VIGENTE (2-nov):** /mnt/project-files/rezago/rezago_inasistencia_sevedu_documento.md (fuente de verdad; reemplaza lo de ρ_e ≈ 29 %). Con reglas oficiales ningún niño sale del rezago binario en un año → SevEdu^N_1 = Σ HW_k((b_k − Σ_s d_ks z_ks)/(e_k+1))², lineal exacta. Estrategias: E0 (asiste, sin pago doble del SGP), E1 regreso $3.0 M/p + cupo SGP, E2 CLEI primaria, E3 CLEI secundaria. **Caso base sin E3** (la ECV no trae años por fuera; decisión de Martín 2-nov), elegibilidad z_ks ≤ e_ks. ρ_e: máx 16.9 % sin E3 (21.2 % con E3); codo 11.5 %; DECIDIDO 2-nov: cobertura obligatoria 6–15 (art. 67) + ρ_e 14 % ($105.8 mm); sensibilidad con E3 cobertura + 20 % ($77.9 mm). Simulador v2: https://claude.ai/artifact/DSSzRA8KbvVstWfiwRJkZp

- **ESTADO DEL PROYECTO (4-nov):** Jerónimo ya subió M3, M4 y su Monte Carlo (branch Modelo3; M4 más barato que M3) y pide esta semana los Modelos 1 y 2 (aunque sea con u = 1), `parametros.py` y `conteo_pares.csv`, más la decisión de la meta del M2 (M0 o H) y el gap del solver. Conflicto abierto: él propone el objetivo del paper como base de M3/M4. El repo de Martín solo tiene los scripts 02–04: faltan 05_conteo_personas, parametros.py, 07 y 08_modelo1. Git: sin atribución de Claude y nunca push sin autorización. Por revisar: costo de trabajo infantil (Renta Ciudadana sin condición verificada), supuesto de logro educativo, fila de rezago del resumen y rango de B. El municipio sí viene en la ECV 2025 pública (P1_MUNICIPIO), lo que permite distinguir Medellín.
- **DATOS COMPARTIDOS Y M3/M4 (5-nov):** el 05 solo cuenta (conteo_pares, empleo_componentes, ninos_rezago) y `parametros.py` pone los precios con `tabla_costos(escenario)`; u_ij condicionado a M_ij = 1 con bandera `u_imputado`; Martín programa el conteo de los no pobres. Resultados de Jerónimo: M4 más barato que M3 (53/43/14 %), precio de la información 25→58 %, k = 4 defendido (k = 8 es artefacto), `info_perfecta.csv` para validar el M1; trampas T14–T16 (constante en s_i, presolve, pulp<4).
- **OBJECIONES DEL HILO 'Debatir' (2-nov; 1, 2, 4 y 5 CERRADAS el 4-nov; sigue abierta la 3):** (1) p = 0.37 infla el máximo de E1 (z debería ser 'ofrecer el pago': beneficio p·coef, costo 3.0 M + p·cupo); (2) posible doble conteo de Renta Ciudadana; (3) el codo debe tomarse sobre H vs SevEdu, no sobre costo; (4) cobertura del art. 67 incompleta; (5) cohorte fija vs reproducir al DANE.

- **MODELO 2 (5-nov): AVANCE** subfases 3.1, 3.2 y 3.3 hechas y probadas (parámetros, censura + meta global, meta por zona + meta_maxima); fase 2 aprobada (herencia con ModeloIPMBase, carpetas Modelos\Modelo_2); POR HACER: 3.4 reglas completas (depende del hilo del M1), 3.5 resolver/recalcular, 3.6–3.7 scripts y barridos. Detalle en la comunidad 14.
- **MODELO 2 (5-nov, aprobado por Martín):** min costo total del año s.a. meta de M0 (`modelo2/formulacion_modelo2.md`). D-M2-1 meta sobre M0 con censura C_i ≥ p_i s_i − U_i y_i; D-M2-2 E-7 siempre, SevEdu solo sensibilidad, sin techo de severidad; D-M2-3 meta en cada zona P3 (implica la global); D-M2-4 (Inas) x_inas ≤ Σ_s z_ks (CLEI cuenta, = D2 del M1). Piso de costo por E-7 aunque m = 0. Plan de programación: https://claude.ai/artifact/B9a3qZtYdcu6CdENKVEpqC; decisiones en `modelo2/justificacion_decisiones_modelo2.md`.

- **PROGRAMACIÓN DEL MODELO 1 (4–5 nov):** base del código = /mnt/project-files/modelo1/formulacion_modelo1.md; decisiones con su porqué en /mnt/project-files/modelo1/justificacion_decisiones.md. D1 dos etapas; D2 el CLEI cuenta como asistencia (E2 quita inasistencia); D3 no asistentes sin rezago con E1 (sin E-7); D4 H sobre la foto inicial (tiempo solo en SevEdu, cierra objeción 5); D5 el hilo hace 05 y parametros.py. Fase 2 en aprobación: módulos datos_modelo.py y modelo1.py + scripts 05, 08_modelo1, 08_modelo1_barridos; PuLP + HiGHS; commits los hace Martín en PyCharm.

- **COSTOS 4–5 NOV (hilo 'Verificar costos', comunidad 13):** tabla única de justificación en /mnt/project-files/costos/justificacion_costos.md (14 indicadores, norma, artículo, enlace, sensibilidades, pendientes). Trabajo infantil: Renta Ciudadana retirada (sin condición de trabajo infantil); sensibilidad apoyo psicosocial $3,329,442. Barreras: 4 consultas descartadas (mejora #7). Renta Ciudadana: Res. 652/2025 exige MATRÍCULA 5–17, no asistencia → limitación mejora #8. **CLEI sí cuenta como 'asiste' en P8586** (nota de instrucción ECV 2025: 'programas para jóvenes y adultos por ciclos'; la validación NO cuenta); edades CLEI 13+ primaria, 15+ secundaria (Dec. 1075/2015 art. 2.3.3.5.3.4.2). Pendientes: PSAP en empleo formal, cupo SGP ausente en informe §6.7, resolución de los 6 ciclos de RC.

- **DECISIONES 4–5 NOV (hilo 'Continuar asesoría', comunidad 16):** costos por indicador CERRADOS con fuente oficial: trabajo infantil $5.32 M por niño (externado ICBF 6 meses, ficha I-12-122); logro educativo máx. 1 ciclo CLEI por adulto/año con (11) Σ g_a v_a ≥ D_i x_logro y (12) x_analf ≤ v_a (solo 33 de 503 hogares pueden salir); barreras de salud 1 consulta $52,100 (código 39141, Circular 25/2024) + prima rural = $203,894. Objeciones 1, 2, 4 y 5 cerradas como limitaciones o mejoras (mejoras 3, 4, 9); cohorte fija solo en SevEdu; D4: H = foto inicial. Modelo 2 = min costo s.a. meta M0 (E-7 sí, SevEdu sensibilidad). Formulaciones: modelo1/formulacion_modelo1.md y modelo2/formulacion_modelo2.md. Falta: rango de B (requiere 05) y objeción 3.

## Summary
- 224 nodes · 365 edges · 17 communities · 18 hyperedges
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
- Conclusiones rezago, inasistencia y SevEdu (1–2 nov)
- Modelo 2: formulación y programación (5-nov)
- Costos verificados 4–5 nov (hilo 'Verificar costos')

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
- **Conclusiones de rezago, inasistencia y SevEdu (1–2 nov)** — doc_sintesis_edu, binario_no_mueve, fgt_alpha2, no_pagar_dos_veces, estrategias_e0_e3, costo_e1, clei_requisitos, caso_base_sin_e3, elegibilidad_param, rango_factible_edu, codo_kneedle_edu, cobertura_art67, propuesta_rho_e_final, eps_restriccion, mejoras_doc, sim_sevedu_v2, sevedu_n_contrafactual, brecha_normalizada, cohorte_fija [EXTRACTED 1.00]
- **Verificación oficial de unidades de costo** — v_fonvivienda, v_renta, v_upc, v_cdi, v_alfab, empleos_vida [EXTRACTED 1.00]
- **Datos compartidos y resultados de M3/M4 (29-oct a 4-nov)** — datos_diseno_05_06, u_condicionado, conteo_no_pobres, nombre_parametros, m4_vs_m3_resultados, precio_informacion, k_sensibilidad, ref_info_perfecta, trampas_m34, tangentes_523, rezago_m34, inasistencia_m34, jer_m3_m4, art_datos [EXTRACTED 1.00]

## Communities (17 total)

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

### Community 10 - "Conclusiones rezago, inasistencia y SevEdu (1–2 nov)"
Nodes (23):
- `doc_sintesis_edu` — DOCUMENTO DE SÍNTESIS (2-nov): rezago_inasistencia_sevedu_documento.md — cómo se calculan y reducen rezago e inasistencia, con énfasis en SevEdu; fuente de verdad vigente  
  _Por qué:_ Martín pidió un .md con todo lo concluido, justificado con fuentes. Reúne informe del rezago, casos, justificación de ρ_e, simulación de Tomás y mejoras.
- `binario_no_mueve` — Con las reglas oficiales NINGÚN niño de los 215 sale del rezago binario en un año (requiere m_k ≥ a_k⁰+1; CLEI primaria exige ≥4 de atraso, E3 solo quitaría atraso 1): sin SevEdu el modelo no invierte en rezago  
  _Por qué:_ Verificado niño por niño en el simulador (2-nov). Es el argumento central de por qué SevEdu es necesaria.
- `fgt_alpha2` — Base teórica: FGT (Foster, Greer y Thorbecke 1984, Econometrica 52(3):761–766) con α=2 + brecha normalizada de Alkire-Foster (2011); aporte propio: Scopus 8 docs, ninguno mide severidad del atraso en un IPM  
  Fuente: https://econometricsociety.org/publications/econometrica/1984/05/01/notes-and-comments-class-decomposable-poverty-measures
- `no_pagar_dos_veces` — Regla de costos: a quien asiste no se le paga otra vez el cupo (el SGP ya lo paga); el regreso de quien no asiste sí es gasto nuevo. 160 de 215 asisten → E0
- `estrategias_e0_e3` — Catálogo: E0 ninguna (asiste); E1 regreso = Renta Ciudadana + cupo SGP (6–16 que no asisten, m=1); E2 CLEI primaria (≥13, g≤3, m=3−g o 2); E3 CLEI secundaria (≥15, primaria, ≥2 años por fuera, m=2 o 1)
- `costo_e1` — Costo E1 por regreso logrado = $3.0 M/p por hogar + cupo SGP por niño (p=0.37 → Tomás $11.2 M); Monte Carlo: $412.8 M / 37 regresos (aprobado por Martín 1-nov)
- `clei_requisitos` — Requisitos CLEI verificados (Decreto 1075/2015): art. 2.3.3.5.3.4.2 ≥13 con máx. 3 grados o ≥15 con primaria y ≥2 años por fuera; 2.3.3.5.3.5.1 media solo ≥18 con 9.º; 2.3.3.5.3.4.3 <13 nivelación en colegio regular  
  Fuente: https://normativa.colpensiones.gov.co/colpens/docs/decreto_1075_2015_pr017.htm
- `caso_base_sin_e3` — CASO BASE SIN E3 (decisión de Martín 2-nov): la ECV 2025 (F24, 82 variables) no trae años por fuera del colegio; atraso ≥2 es solo condición necesaria (33 de 34). 15–16 años que no asisten → solo E1. E3 = sensibilidad  
  _Por qué:_ Regla del proyecto: solo lo verificable entra al modelo. Martín: "dejemos claro porqué se tomó esta y no la que queremos debido a falta de datos".
- `elegibilidad_param` — Elegibilidad como parámetro: z_ks ≤ e_ks, Σ_s z_ks ≤ 1; e_k,E3 = 0 (base) o 1[edad≥15]·1[no asiste]·1[g∈5..8]·1[a≥θ] (sensibilidad θ=2,3,4); si llega el dato real solo cambia e_k,E3
- `rango_factible_edu` — Rango factible de ρ_e (normalizada, p=0.37): sin E3 máx 16.9 % ($201.6 mm); con E3 21.2 % ($83.3 mm); con A3 24.1 %. El 29 % del 28-oct es INFACTIBLE
- `codo_kneedle_edu` — Codo Kneedle (Satopää 2011; Branke et al. 2004): sin E3 en 11.5 % ($31.2 mm, se acaban los CLEI de primaria); con E3 en 13.7 % ($20.4 mm, 32 jóvenes con CLEI)
- `cobertura_art67` — Cobertura obligatoria 6–15 años que no asisten (Constitución art. 67: "obligatoria entre los cinco y los quince años"): el codo dejaba a 23 de 55 sin atender (8–14 años, poco atraso, solo E1)  
  Fuente: https://minciencias.gov.co/sites/default/files/upload/reglamentacion/ConstitucionPoliticaColombia-1991.pdf
- `propuesta_rho_e_final` — DECISIÓN FINAL ρ_e (Martín 2-nov): caso base sin E3 = cobertura obligatoria 6–15 + ρ_e 14 % ($105.8 mm); sensibilidad con E3 = cobertura + 20 % ($77.9 mm)
- `eps_restriccion` — ε-restricción (Haimes, Lasdon y Wismer 1971, IEEE SMC 1(3):296–297): H objetivo, SevEdu como techo Σ coef_ks z_ks ≥ ρ_e·SevEdu^N_1,sin (≈21,562)
- `mejoras_doc` — mejoras/mejoras_modelo.md: (1) costo oficial de permanencia (PTAFI, sin costo por estudiante; derecho de petición MEN); (2) años por fuera del colegio para habilitar E3 (SIMAT vía derecho de petición)

_Comunidad 8 (simuladores) suma:_ `sim_sevedu_v2` — SIMULADOR SevEdu v2 (1-nov): 215 niños reales con asistencia ECV, estrategias E1–E3, paso del tiempo, frontera ρ_e vs costo  
  Fuente: https://claude.ai/artifact/DSSzRA8KbvVstWfiwRJkZp
- `casos_modelo_doc` — CASOS DEL MODELO (1-nov): casos_rezago_inasistencia_modelo.md — A1–A4 asisten (E0; A3 CLEI pendiente), B1–B8 de 6 a 16 que no asisten (E1/E2/E3), C1–C3 de 17 que no asisten (E2, E3 o nada); catálogo de estrategias y costos  
  _Por qué:_ Martín pidió un .md con todos los casos posibles de jóvenes con rezago y/o inasistencia y cómo actúa el modelo con cada uno.
- `casos_7_ejemplos` — 7 casos ilustrativos (1-nov): Luis 8, María 15 asiste, Tomás 15 no asiste, Esteban 17 asiste, Martín 17 no asiste, Ema 19, Rober 19: distinguen indicadores (inasistencia 6–16, rezago 7–17, logro ≥15) de estrategias y costos
- `sim_tomas_doc` — Simulación de Tomás (1-nov): fase 1 optimiza con costo fijo $11.2 M por regreso logrado; fase 2 Monte Carlo (200 corridas) mide gasto real ($6.05 M si vuelve, $3.0 M si no) y salidas reales  
  _Por qué:_ Martín no entendía de dónde salían los $11.2 M; la corrida desmenuzada mostró que el costo cae en los que sí regresan.
- `valor_anio_regular` — Valor del año regular (aporte de Martín, 1-nov): no baja el atraso pero evita que crezca; efecto d_k = m_k − q_k (q_k = 0 si no asiste, ap_k si asiste) → vale para quien no asiste, casi nada para quien iba a avanzar solo
- `menores_13_nivelacion` — Menores de 13 atrasados: nivelación en colegio regular (Decreto 1075, art. 2.3.3.5.3.4.3) sin costo oficial propio → se usa E1; Aceleración del Aprendizaje (MEN) solo para extraedad que ya lee; promoción anticipada (Dec. 1290/2009 art. 7) sin costo
- `jovenes_17` — Jóvenes de 17: salen del rezago al cumplir 18 con o sin intervención; la media de adultos exige 18 años; si no asisten y no son elegibles a CLEI (caso C3) no hay estrategia verificada (Renta Ciudadana no aplica: la inasistencia llega a 16)
- `pendientes_edu` — Pendientes educativos: ap_k (tasas de aprobación y deserción del MEN); ¿la ECV cuenta el CLEI como "asiste"? (define si E2/E3 quitan inasistencia); probabilidad de terminar el CLEI (supuesto: 1); caso A3 (CLEI para quien asiste) por decidir
- `rho_e_costos_cobertura` — Cobertura + techo (2-nov): sin E3 solo cobertura 11.8 % $104.2 mm, +14 % $105.8 mm (2 jóvenes de 17 con CLEI primaria), +15 % $142.3 mm, 20 % infactible; con E3 +14 % $66.6 mm, +20 % $77.9 mm
  _Por qué:_ Martín pidió un .md con todos los casos posibles de jóvenes con rezago y/o inasistencia y cómo actúa el modelo con cada uno.
  _Por qué:_ Martín no entendía de dónde salían los $11.2 M; la corrida desmenuzada mostró que el costo cae en los que sí regresan.

## Edges
- `m2_fase2` --extends--> `m2_plan`
- `m2_fase2` --implements--> `m2_formulacion`
- `m2_herencia` --part_of--> `m2_fase2`
- `m2_carpetas` --part_of--> `m2_fase2`
- `m2_sub31` --step_of--> `m2_fase2`
- `m2_sub32` --follows--> `m2_sub31`
- `m2_sub33` --follows--> `m2_sub32`
- `m2_sub32` --implements--> `m2_meta_m0`
- `m2_sub33` --implements--> `m2_meta_zona`
- `m2_bug_binary` --found_in--> `m2_sub33`
- `m2_bug_binary` --warns--> `m2_pend34`
- `m2_pend34` --follows--> `m2_sub33`
- `m2_pend34` --requires--> `m2_herencia`
- `m2_pend34` --implements--> `m2_inas_clei`
- `m2_pend34` --measures--> `m2_piso_e7`
- `m2_pend35` --follows--> `m2_pend34`
- `m2_pend367` --follows--> `m2_pend35`
- `m2_pend367` --implements--> `m2_cruce_m1`
- `m2_pend_gap` --requires--> `jer_pide`
- `m2_pend_gap` --affects--> `m2_pend367`
- `m2_formulacion` --adapts--> `referencias_paper_pobreza_multidimensional_opti1_model_2`
- `m2_formulacion` --dual_of--> `docs_informe_modelo1_modelo1_presupuesto_fijo`
- `m2_meta_m0` --resolves--> `meta_m2`
- `m2_meta_m0` --part_of--> `m2_formulacion`
- `m2_capas` --keeps--> `cobertura_art67`
- `m2_capas` --sensitivity_of--> `propuesta_rho_e_final`
- `m2_capas` --part_of--> `m2_formulacion`
- `m2_meta_zona` --analog_of--> `equidad_dos_tipos`
- `m2_meta_zona` --part_of--> `m2_formulacion`
- `m2_inas_clei` --uses--> `clei_requisitos`
- `m2_inas_clei` --corrects--> `estrategias_e0_e3`
- `m2_inas_clei` --part_of--> `m2_formulacion`
- `m2_piso_e7` --caused_by--> `cobertura_art67`
- `m2_piso_e7` --caused_by--> `m2_meta_zona`
- `m2_cruce_m1` --validates--> `m2_formulacion`
- `m2_plan` --implements--> `m2_formulacion`
- `jer_pide` --answered_by--> `m2_formulacion`
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
- `doc_sintesis_edu` --extends--> `rez_estrategia`
- `doc_sintesis_edu` --explains--> `sevedu_n_contrafactual`
- `binario_no_mueve` --motivates--> `sevedu_n_contrafactual`
- `binario_no_mueve` --follows_from--> `rest_10_rezago`
- `fgt_alpha2` --justifies--> `brecha_normalizada`
- `fgt_alpha2` --justifies--> `sevedu_n_contrafactual`
- `no_pagar_dos_veces` --constrains--> `estrategias_e0_e3`
- `estrategias_e0_e3` --uses--> `costo_e1`
- `estrategias_e0_e3` --constrained_by--> `clei_requisitos`
- `clei_requisitos` --refines--> `clei_norma`
- `estrategias_e0_e3` --uses--> `clei_costo`
- `clei_requisitos` --causes--> `caso_base_sin_e3`
- `caso_base_sin_e3` --implemented_by--> `elegibilidad_param`
- `caso_base_sin_e3` --documented_in--> `mejoras_doc`
- `elegibilidad_param` --constrains--> `sevedu_n_contrafactual`
- `eps_restriccion` --uses--> `sevedu_n_contrafactual`
- `eps_restriccion` --same_method_as--> `techo_severidad`
- `rango_factible_edu` --supersedes--> `rho_e_eleccion`
- `rango_factible_edu` --resolves--> `rez_recalcular`
- `caso_base_sin_e3` --determines--> `rango_factible_edu`
- `codo_kneedle_edu` --applies--> `codo`
- `rango_factible_edu` --precedes--> `codo_kneedle_edu`
- `cobertura_art67` --corrects--> `codo_kneedle_edu`
- `codo_kneedle_edu` --informs--> `propuesta_rho_e_final`
- `cobertura_art67` --informs--> `propuesta_rho_e_final`
- `sim_sevedu_v2` --computes--> `rango_factible_edu`
- `sim_sevedu_v2` --supersedes--> `sim_sevedu`
- `costo_e1` --prices--> `cobertura_art67`
- `doc_sintesis_edu` --concludes--> `propuesta_rho_e_final`
- `doc_sintesis_edu` --references--> `mejoras_doc`
- `datos_diseno_05_06` --specified_in--> `art_datos`
- `datos_diseno_05_06` --produces--> `ninos_rezago_csv`
- `datos_diseno_05_06` --pending_in--> `codigo_pendiente`
- `u_condicionado` --part_of--> `datos_diseno_05_06`
- `conteo_no_pobres` --part_of--> `datos_diseno_05_06`
- `conteo_no_pobres` --needed_by--> `jer_m3_m4`
- `nombre_parametros` --part_of--> `datos_diseno_05_06`
- `nombre_parametros` --refines--> `numeracion_scripts`
- `m4_vs_m3_resultados` --reported_in--> `jer_m3_m4`
- `m4_vs_m3_resultados` --quantifies--> `precio_focalizar`
- `precio_informacion` --reported_in--> `jer_m3_m4`
- `precio_informacion` --quantifies--> `precio_focalizar`
- `k_sensibilidad` --refines--> `m4_vs_m3_resultados`
- `ref_info_perfecta` --checks--> `objetivo_c`
- `ref_info_perfecta` --requested_in--> `jer_pide`
- `trampas_m34` --applies_to--> `objetivo_c`
- `trampas_m34` --reported_in--> `jer_m3_m4`
- `tangentes_523` --compares--> `q_tangentes`
- `rezago_m34` --adapts--> `sev_edu_4modelos`
- `rezago_m34` --uses--> `rest_10_rezago`
- `inasistencia_m34` --adapts--> `docs_resumen_proyecto_ipm_decision_inasistencia_condicionada`
- `inasistencia_m34` --reported_in--> `jer_m3_m4`

### Community 11 - "Estado del proyecto y coordinación con Jerónimo (4-nov)"

- `jer_m3_m4` — Jerónimo subió a la branch Modelo3 el Modelo 3, el Modelo 4 y el Monte Carlo de ambos; M4 sale más barato que M3 (ahorro mediano 13–53 % con u = 1); respondió las 7 preguntas en 'Notas de Jerónimo' (desempate, rezago no intervenible, equidad)
- `jer_pide` — Jerónimo pide ESTA SEMANA: Modelos 1 y 2 en el repo (aunque sea con u = 1), parametros.py y conteo_pares.csv; que Martín decida si la meta del M2 es sobre M0 (él propone M0) y el gap del solver; agenda de 12 puntos
- `jer_objetivo_paper` — Conflicto abierto: Jerónimo propone el objetivo del paper (Hamie et al.) como caso base de M3/M4, aunque antes se acordó 'mismo objetivo'; el M1 vigente es H con techo de severidad
- `meta_m2` — [RESUELTO 5-nov: meta sobre M0, ver `m2_meta_m0`] el gap del solver sigue pendiente (fase 2 del Modelo 2)
- `numeracion_scripts` — Numeración de scripts: Modelo3 usa 05_/06_/07_ que chocan con los de Martín; propuesta: datos compartidos 02–07 y modelos con prefijo m3_/m4_ (Jerónimo propone m34_)
- `git_reglas` — Git: NUNCA push sin autorización de Martín; commits y PRs SIN atribución de Claude (decidido 2/3-nov); Claude no debe figurar como contribuidor. Commits con Claude: Contexto 4ff4a12, be471be, 72c9d02 y Modelo3 6f1d024, 16a4e4f; Jerónimo los quita; al fusionar a main, squash
- `branch_contexto` — Branch Contexto: CONTEXTO_DATOS.md (lo que concluyó Martín de los datos) + este grafo; Jerónimo deja 'Notas de Jerónimo'; revisión diaria 17:36 Bogotá de lo que suba
- `codigo_pendiente` — Código pendiente de Martín: el repo solo tiene 02_validar_ipm, 03_preparar_antioquia y 04_linea_base; faltan 05_conteo_personas.py (con tabla por niño), parametros.py (costos, Sev₀, A_i, λ, SevEdu^N), 07_eficiencia_por_zona.py y 08_modelo1.py; nada commiteado en main
- `revisar_tabla_costos` — Por revisar en la tabla de costos: trabajo infantil usa Renta Ciudadana ($3.0 M) sin verificar que tenga condición sobre trabajo infantil; logro educativo supone 3 ciclos CLEI para todo adulto con < 9 años (supuesto); la fila de rezago del resumen aún dice 'Opción C'
- `municipio_ecv` — DANE (respuesta 30-oct, radicado 202620022798): el municipio SÍ viene en la ECV 2025 pública de ANDA (tabla 'Datos de la vivienda', P1_DEPARTAMENTO y P1_MUNICIPIO, rellenar con ceros), cruzable por DIRECTORIO; no hace falta la sala SPEE. Permite distinguir Medellín (ETC 05001) del resto de Antioquia
- `reglas_trabajo` — Reglas de Martín: mencionar su nombre en cada respuesta; todo costo con fuente oficial y real; solo información 100 % segura (lo de memoria se marca como no verificado y no entra al modelo); hacer de abogado del diablo SOLO en el hilo 'Debatir mis decisiones'
- `datos_diseno_05_06` — Diseño de datos compartidos (29-oct): el 05 solo CUENTA (conteo_pares.csv, empleo_componentes.csv, ninos_rezago.csv) y parametros.py PONE PRECIOS con tabla_costos(escenario) → costo_ij = EpF_zona · u_ij · HW_i; así una sensibilidad (p, rezago, u = 1) no obliga a rehacer el 05 y los dos usan el mismo escenario
- `u_condicionado` — u_ij solo existe donde M_ij = 1 del DANE; si la regla da 0 personas pero el DANE marca la privación → u_ij = 1 y bandera u_imputado (logro 39 hogares, inasistencia 27, empleo formal 0,33 %). Atención integral (96,5 %) y desempleo (86,5 %) son aproximaciones y pesan más en los no pobres
- `conteo_no_pobres` — Conteo de los no pobres (3.732 hogares): lo programa Martín en el mismo 05 (es el mismo código sin filtrar por 'pobre'); Jerónimo revisa y valida. En M3/M4 el sorteo cae también en no pobres y ese gasto ES el error de inclusión
- `nombre_parametros` — El archivo se llama parametros.py, no 06_parametros.py: Python no importa módulos cuyo nombre empieza por un número; el CLAUDE.md decía 05_parametros.py y hay que corregirlo. Ahí viven pesos, k, EpF, escenarios, malla de B, r, ρ, ρ_e y la semilla
- `m4_vs_m3_resultados` — Resultados de Jerónimo (3-nov, u = 1): M4 más barato que M3 en 97–99 % de las réplicas (ahorro mediano 53/43/14 % para metas 5/10/20 %); con meta 5 % M4 no reduce la inclusión (48→54 %); el costo pasa de ~1,8 a ~5 mil millones por punto de M0; la ventaja de M4 no es monótona (máxima con metas 4–10 %)
- `precio_informacion` — Precio de la información (equidad, B = 10→200 mil millones): M3 logra 25→58 % de lo que lograría la información perfecta y M4 44→60 %; M4 es además más predecible (B = 25: M3 de 47 mil a 113 mil personas, M4 de 103 mil a 116 mil)
- `k_sensibilidad` — Sensibilidad a k en M4: k = 2 (separa por tamaño del hogar, η² ≈ 0) es peor que M3; desde k = 4 la ganancia se aplana; k = 8 deja 26 pares con n < 10 y simula información individual → no presentarlo como mejor. Regla: < 15 % de pares con n < 10; k = 4 se defiende, k = 5 alternativa
- `ref_info_perfecta` — Referencia info_perfecta.csv de Jerónimo (mismo objetivo de equidad con información perfecta; techo propio, NO es el M1): al subir el M1 compararlo con mismo B, u = 1 y rezago no intervenible; si difiere más de ~1 % hay un supuesto distinto que encontrar
- `trampas_m34` — Trampas de Jerónimo que afectan al M1/M2: (T14) un indicador excluido debe quedar como CONSTANTE en el puntaje, s_i = w·M_i − Σ w_j cur_ij, o se 'cura' gratis su peso; (T15) el presolve de HiGHS declara a veces infactible la etapa 2 → reintentar con presolve='off'; (T16) PuLP 4.x rompe LpVariable(cat=...) → pulp<4
- `tangentes_523` — Tangentes de severidad: Jerónimo 6.048 vs Martín 6.571; la diferencia (523 = hogares pobres) sería por omitir a = 0 (tangente q ≥ 0, ya implícita en la variable); falta que Jerónimo lo confirme para que Sev₀ y el techo sean comparables
- `rezago_m34` — Rezago en M3/M4 (acuerdo 3-nov): caso base no intervenible (se paga, no cura) y SevEdu solo como métrica ex post en el Monte Carlo, porque el sorteo por niño rompe el prefijo por hogar de los cortes; sorteo por niño queda como trabajo futuro
- `inasistencia_m34` — Inasistencia en M3/M4 (propuesta, decide Jerónimo): en la optimización el sorteo queda fijo y el costo es 3,0/p; el cumplimiento p entra solo en el Monte Carlo de evaluación, para no contar dos veces el azar; p = 0,369 como caso base

### Community 12 - "Objeciones abiertas del hilo 'Debatir mis decisiones' (2-nov)"

- `obj_p_infla` — Objeción 1 (la que cambia números): p = 0.37 infla el máximo de E1. Con z = 1 se da beneficio completo a HW hogares pero solo volverían p·HW. Corrección: z = 'el Estado ofrece el pago', beneficio p·coef y costo HW·(3.0 M + p·cupo). Baja el 16.9 % y el 11.8 %; pendiente: ¿z es resultado o decisión?
- `obj_doble_rc` — Objeción 2: posible doble conteo de Renta Ciudadana (muchos hogares pobres ya la reciben; choca con la regla de no pagar dos veces). p = 0.369 sí está verificado (Prosperidad Social), falta citarlo en el §3.3
- `obj_codo_frente` — Objeción 3: el codo (Branke 2004) se toma sobre el frente entre objetivos (H vs SevEdu), no sobre costo (B es fijo); con la cobertura impuesta la frontera empieza en 11.8 % y el codo hay que recalcularlo. Propuesta: no fijar ρ_e hasta tener la curva H vs ρ_e
- `obj_art67` — Objeción 4: la cobertura del art. 67 queda incompleta: deja fuera a los que no asisten sin rezago y a 14 jóvenes de 16 años que sí cuentan en la inasistencia del DANE
- `obj_cohorte_ipm` — Objeción 5: la cohorte fija contradice el 'IPM intacto': con la regla oficial quien cumple 18 sale del indicador; si se congela también en el H binario, ya no se reproduce al DANE
- `obj_costo_detalle` — Detalle: el niño de 10 años en primaria cuesta $10.8 M (8.11 + 2.71), no $11.2 M
- `casos_modelo_doc` --details--> `estrategias_e0_e3`
- `casos_7_ejemplos` --precedes--> `casos_modelo_doc`
- `doc_sintesis_edu` --summarizes--> `casos_modelo_doc`
- `sim_tomas_doc` --explains--> `costo_e1`
- `doc_sintesis_edu` --references--> `sim_tomas_doc`
- `valor_anio_regular` --refines--> `sevedu_n_contrafactual`
- `valor_anio_regular` --supports--> `no_pagar_dos_veces`
- `menores_13_nivelacion` --constrains--> `estrategias_e0_e3`
- `menores_13_nivelacion` --follows_from--> `clei_requisitos`
- `jovenes_17` --motivates--> `cohorte_fija`
- `jovenes_17` --follows_from--> `clei_requisitos`
- `casos_modelo_doc` --contains--> `jovenes_17`
- `pendientes_edu` --listed_in--> `doc_sintesis_edu`
- `pendientes_edu` --related_to--> `caso_base_sin_e3`
- `rho_e_costos_cobertura` --supports--> `propuesta_rho_e_final`
- `cobertura_art67` --priced_by--> `rho_e_costos_cobertura`
- `mejoras_doc` --addresses--> `pendientes_edu`

### Community 14 - "Modelo 2: formulación y programación (5-nov)"

- `m2_formulacion` — Modelo 2 VIGENTE (aprobado por Martín 5-nov): min costo total del año (= lado izquierdo del presupuesto (1) del M1) s.a. meta de M0; mismas reglas de intervención y costos del M1; sin B. Formulación: modelo2/formulacion_modelo2.md
- `m2_meta_m0` — D-M2-1 DECIDIDO (Martín 5-nov): meta sobre M0, no H: Σ C_i ≤ (1 − m)·M0⁰·Pob (Pob = toda la población); censura C_i ≥ p_i s_i − U_i y_i, U_i = p_i c_i⁰; metas m = 5/10/20 % (las de Jerónimo) + barrido
- `m2_capas` — D-M2-2 DECIDIDO (Martín 5-nov): E-7 (art. 67) siempre; SevEdu (E-5, ρ_e 14 %) solo como sensibilidad; SIN techo de severidad ni tangentes (M0 cumple ese papel); sin q_i no hay desempate
- `m2_meta_zona` — D-M2-3 DECIDIDO (Martín 5-nov, "tanto lo urbano como lo rural"): meta (M-d) en cada una de las 3 zonas P3 en el caso base, Σ_{i∈d} C_i ≤ (1 − m)·M0⁰_d·Pob_d; implica la global; meta solo global = sensibilidad (mide el costo de la equidad territorial)
- `m2_inas_clei` — D-M2-4 DECIDIDO (5-nov, = D2 del M1): (Inas) x_i,inas ≤ Σ_s z_ks: el CLEI cuenta como asistencia (nota P8586 ECV 2025). Corregido en formulacion_modelo2.md (proyecto y PC); formulacion_modelo1.md pendiente de corregir por el hilo del M1
- `m2_piso_e7` — Consecuencia: por E-7 el Modelo 2 tiene un costo mínimo aunque la meta sea m = 0; reportarlo aparte. La meta máxima factible la fija la zona que menos puede bajar M0
- `m2_cruce_m1` — Prueba cruzada M1 ↔ M2: si el M2 cumple la meta m con costo B*, el M1 con B = B* saca al menos tantas personas; si el M1 con B logra M0 = m, el M2 lo logra con costo ≤ B
- `m2_plan` — Plan de programación del Modelo 2 (fase 1, 5-nov): https://claude.ai/artifact/B9a3qZtYdcu6CdENKVEpqC; decisiones en modelo2/justificacion_decisiones_modelo2.md; fases plan → cómo → código con aprobación de Martín; reutiliza 05 y parametros.py del hilo del M1. Pendiente fase 2: estructura de scripts, gap del solver
- `m2_fase2` — Fase 2 aprobada (5-nov): modelo2.py + 09_modelo2.py + 09_modelo2_barridos.py + sección 10 de parametros.py; objetivo en millones de pesos; HiGHS con gapRel 1e-6, una sola etapa, timeLimit 300 s (F2-1, F2-2); meta_maxima() antes de barrer m (F2-3). Plan: sección 8 de https://claude.ai/artifact/B9a3qZtYdcu6CdENKVEpqC
- `m2_herencia` — F2-4 DECIDIDO por Martín: POO con clase madre ModeloIPMBase (modelo_base.py, la escribe el hilo del M1 después del 05 y datos_modelo.py); Modelo1 y Modelo2 heredan; construir() es template method (crear_variables, agregar_reglas_intervencion, agregar_restricciones_propias, definir_objetivo); SevEdu = método agregar_sevedu(rho_e) que cada hija decide llamar; M3/M4 no heredan
- `m2_carpetas` — F2-5 DECIDIDO por Martín: todo el código en Optimizacion_1_S4\Modelos\ (común), Modelos\Modelo_1 y Modelos\Modelo_2 (renombradas sin espacio); los scripts de las subcarpetas hacen sys.path.insert(parents[1]); rutas de datos desde utils_dane (RAIZ, BASE, OUT)
- `m2_sub31` — Subfase 3.1 HECHA: parametros.py sección 10 (METAS_M2 5/10/20 %, CASO_BASE_M2 meta_por_zona=True y usar_sevedu=False, SENSIBILIDADES_M2, SOLVER_M2, ESCALA_COSTO 1e6, escenario_m2(), malla_m2())
- `m2_sub32` — Subfase 3.2 HECHA: núcleo con C_i ≥ p_i s_i − U_i y_i y meta global Σ C_i ≤ (1−m) Σ p_i c0_i (la población Pob se cancela); probado con 50 hogares contra un algoritmo exacto por frontera (costo, contribución): coincide con m = 10/30/50 % y la prueba falla si se rompe la censura
- `m2_sub33` — Subfase 3.3 HECHA: meta por zona (Meta_<d>) probada contra la suma de exactos por zona, y meta_maxima() (un problema sin meta que minimiza Σ C_i; el barrido de m llega a la zona que menos baja); coincide con la enumeración exacta; infactible justo encima del tope
- `m2_bug_binary` — Lección: en PuLP una variable cat=Binary ignora upBound y vuelve a 0..1; lo no removible se declara entero 0..0 con crear_x(); la prueba contra el método exacto lo detectó (100 % vs 65 %). Usar crear_x en las reglas de la 3.4. PuLP 4.x ya no acepta cat=: mantener PuLP 3.3.2
- `m2_pend34` — POR HACER 3.4: conectar las reglas de intervención (educación z/t, E-1..E-3, E-7, 10a/10b, Inas con Σ_s z_ks, logro (11), analfabetismo (12)) heredando de ModeloIPMBase; medir el piso de costo con m = 0 (E-7). Depende de 05_conteo_personas.py, datos_modelo.py y modelo_base.py del hilo del M1 (aún no existen)
- `m2_pend35` — POR HACER 3.5: resolver() con estado y gap de HiGHS, solucion() y recalcular() y tabla común (H, A, M0, severidad, SevEdu, costo por zona y total, gasto por indicador E_j)
- `m2_pend367` — POR HACER 3.6 y 3.7: 09_modelo2.py (caso base m = 5/10/20 %) y 09_modelo2_barridos.py (curva costo vs. meta hasta meta_maxima, meta global vs. por zona, sensibilidades p = 0.50/0.75, u = 1, E3 y SevEdu, prueba cruzada con el M1); resultados en Modelos\Modelo_2\resultados\
- `m2_pend_gap` — Pendiente con Jerónimo: unificar o reportar el gap del solver de cada corrida (él usa 1e-6 en la etapa 1 y 1e-4 en la etapa 2 del M3/M4); el M2 usa 1e-6 en su única etapa


### Community 15 - "Programación del Modelo 1 (4–5 nov)"

- `m1prog_hilo` — Hilo de programación del Modelo 1 en 3 fases con aprobación de Martín entre cada una: (1) plan qué, (2) cómo, (3) código paso a paso. Plan: https://claude.ai/artifact/3sV7174gcSy4xDzqyZwZzT
- `m1_formulacion_base` — BASE DEL CÓDIGO: /mnt/project-files/modelo1/formulacion_modelo1.md (copia docs/formulacion_modelo1.md); junta informe §4, SevEdu E-1..E-7, v_a (11)(12), costos del 4-nov y D1–D5
- `m1_justificacion` — Registro de decisiones de programación: /mnt/project-files/modelo1/justificacion_decisiones.md (copia docs/ del PC); Martín pidió justificar ahí cada decisión que se tome al programar
- `d1_dos_etapas` — D1 DECIDIDO (Martín 4-nov): desempate en DOS ETAPAS: max Σp y → H* (valor de la incumbente); luego min Σp q s.a. Σp y ≥ H*(1−1e-6). Con λ: λ·Sev0 ≈ 35 personas < gap 1e-4 de HiGHS ≈ 68 personas
- `d2_clei_asiste` — D2 DECIDIDO (Martín 5-nov): el CLEI SÍ cuenta como asistencia (nota P8586 ECV 2025: "se consideran asistiendo... programas para jóvenes y adultos por ciclos"; validar no cuenta) → E2 quita la inasistencia: x_i,inas ≤ Σ_s z_ks
- `d3_noasist_sinrezago` — D3 DECIDIDO (Martín 5-nov): los no asistentes de 6–16 SIN rezago (fuera de los 215) entran con E1; coef SevEdu = 0 (solo aportan a H); sin obligación E-7
- `d4_h_foto` — D4 DECIDIDO (Martín 5-nov): H binario sobre la FOTO INICIAL (nadie envejece en H; puntaje final = hoy − privaciones pagadas). El tiempo solo en SevEdu. Evita salidas gratis (27 rezagados de 17 años, 14 no asistentes de 16)
- `d5_conteo_en_hilo` — D5 DECIDIDO (Martín 5-nov): el hilo de programación hace también 05_conteo_personas.py y completa parametros.py (sobre el archivo existente)
- `f2_archivos` — FASE 2 (5-nov, en aprobación): parametros.py + utils_dane.resumen_ipm (módulos); 05_conteo_personas.py → conteo_pares.csv, ninos.csv, adultos_clei.csv, empleo_componentes.csv; datos_modelo.py y modelo1.py (importables, sin número); 08_modelo1.py y 08_modelo1_barridos.py
- `f2_solver` — FASE 2: PuLP 3.3.2 + HiGHS (highspy 1.15.1) del .venv; restricciones con nombre (Pres, Sal_i, Eq_d, Tan_i_a, Sev, SevEdu, E7_k, Inas_i_k, Log_i, Analf_i_a); gap reportado por etapa
- `f2_orden` — FASE 2: orden por capas, cada una probada con 50 hogares y luego 523: H puro (vs enumeración) → equidad → q/tangentes/techo → bloque educativo → logro (v_a) → dos etapas; regresión 523 pobres, M0 0.038684, Sev0 ≈117,908, SevEdu ≈21,562
- `f2_git` — FASE 2: Claude escribe los archivos en el PC; git en el equipo no puede borrar sus locks → commits los hace Martín en PyCharm, sin atribución, sin push sin autorización. Pendiente: qué hacer con 03_preparar_antioquia_urbana.py borrado y 04 modificado

### Community 16 - "Decisiones 4–5 nov: costos cerrados y formulación M1/M2"

- `dec_obj1_limitacion` — Objeción 1 CERRADA (Martín 4-nov): p = 0.37 en E1 se deja como limitación; z = 'ofrecer el pago' no se implementa; 16.9 % y 11.8 % se presentan como cotas optimistas (mejoras §3)
- `dec_obj2_limitacion` — Objeción 2 CERRADA (Martín 4-nov): hogares que ya reciben Renta Ciudadana: costo de E1 sobrestimado e intervención posiblemente no nueva; la ECV no lo pregunta → supuesto 8 del informe §7 y mejora 9
- `dec_obj4_mejora` — Objeción 4 CERRADA (Martín 4-nov): E-7 se queda con los 29 no asistentes rezagados de 6–15 + ρ_e 14 %; ampliarla a no asistentes sin rezago queda como mejora 4; los de 16 años no tienen obligación (art. 67 llega a 15)
- `dec_cohorte_solo_sevedu` — Objeción 5 CERRADA (Martín 4-nov): la cohorte fija se usa SOLO en SevEdu; el H binario sigue la regla del DANE
- `dec_d4_h_foto` — D4 DECIDIDA (Martín 5-nov): H = foto inicial (lectura a): nadie envejece dentro de H; puntaje final = hoy − privaciones pagadas; no infla H (sin salidas ni entradas 'solas'). El paso del tiempo vive solo en SevEdu
- `efecto_frontera_edad` — Efecto frontera por edad (mejora 10, 5-nov): el joven de 17 que cumple 18 sale del rezago sin mejorar; malo como impacto, cosmético como estadística; no simétrico (hay entradas solas); opción (c) separaría efecto demográfico y de política
- `costo_trabajo_infantil_icbf` — Trabajo infantil (Martín 4-nov): $5,316,348 por niño 12–17 que trabaja = externado media jornada ICBF 6 meses × $886,058 (Res. 0001/2025 ficha I-12-122, act. Res. 0296/2025); psicosocial $3,329,442 sensibilidad; se retira Renta Ciudadana (sin condición sobre trabajo infantil, Dec. Ley 1960/2023)
- `costo_logro_un_ciclo` — Logro educativo (Martín 4-nov, opción A): CLEI ≥ 40 semanas/ciclo ⇒ máx. 1 ciclo por adulto/año (v_a); privación = promedio del hogar < 9; (11) Σ g_a v_a ≥ D_i x_logro; (12) x_analf ≤ v_a (ciclo 1 se paga una vez); solo 33 de 503 hogares pobres pueden salir en un año. Doc: costos/logro_educativo_analisis.md
- `mejora_sev_logro` — Severidad de logro NO entra (Martín 4-nov): falta investigación; ponderar por probabilidad de completar el ciclo según edad (Martín propuso entropía del hogar; ojo: la entropía mide mezcla, no juventud) → mejora 6
- `costo_barreras_1consulta` — Barreras de salud (Martín 4-nov): 1 consulta, código 39141 'Consulta ambulatoria de medicina general' 4,51 UVB = $52,100 (Circular Externa 25/2024 Minsalud, p. 34); rural + prima dispersión $151,794 = $203,894; las 4 consultas se descartan (mejora 7)
- `rc_condicion_res652` — Condición educativa de Renta Ciudadana verificada: Res. 652/2025 Prosperidad Social, art. 1.6.1 num. 2.1 (NNA 5–17 matriculados, verificado cada 2 ciclos); exige matrícula, no asistencia → mejora 8. Costo de inasistencia sin cambios
- `resumen_sin_opcion_c` — Resumen del proyecto corregido (4-nov): la fila de rezago ya no dice 'Opción C', sino el esquema de dos capas (z_ks por niño, x_rez sin costo, (10a)/(10b)); sensibilidades rezago A/B reemplazadas por E3 + ρ_e 20 %
- `parametros_py` — parametros.py creado en el PC de Martín (4-nov): trabajo infantil, CLEI (costo por ciclo, FIN_SIGUIENTE_CICLO, ganancia_ciclo()) y barreras de salud; el resto de la tabla se completa paso a paso
- `formulacion_m1_doc` — Formulación consolidada del Modelo 1 para programar (4-nov): /mnt/project-files/modelo1/formulacion_modelo1.md (y docs/ del PC): conjuntos, parámetros, 6 variables (x,y,q,z,t,v), objetivo y 16 restricciones con su propósito
- `formulacion_m2_doc` — Modelo 2 DECIDIDO (Martín 5-nov): min costo s.a. meta sobre M0, Σ C_i ≤ (1−m)·M0⁰·Pob, con C_i ≥ p_i s_i − U_i y_i (una sola linealización); meta por zona opcional; E-7 sí; SevEdu solo sensibilidad; sin techo de severidad. Doc: /mnt/project-files/modelo2/formulacion_modelo2.md
- `costos_cerrados` — Costos por indicador CERRADOS (4-nov): todos con fuente oficial; solo falta recalcular el rango de B, que requiere el conteo 05


### Actualización 5-nov (hilo Programar el Modelo 1): avance y pendientes — comunidad 15

- `f3_estado` — FASE 3 (5-nov): fase 2 aprobada por Martín; se programa por pasos 3.1–3.7 y Martín da luz verde tras cada uno. Hechos: 3.1, 3.2, 3.3 (3.3 espera luz verde)
- `f3_1_parametros` — HECHO 3.1: Modelos/parametros.py (secciones 1–9: pesos IPM, costos con fuente, escenarios CASO_BASE/SENSIBILIDADES, CUPO_SGP, COSTO_CICLO_CLEI, ganancia_ciclo); P1–P5
- `f3_2_utils` — HECHO 3.2: utils_dane.py con RAIZ/BASE, puntaje() y resumen_ipm(p, puntaje, k); 04_linea_base.py importa de ahí con salida idéntica; P6
- `f3_3_conteo` — HECHO 3.3 (espera luz verde): Modelos/05_conteo_personas.py → conteo_pares, ninos, adultos_clei, logro_hogar, empleo_componentes.csv. Valida 99.67–100 %; 215 niños/149 hogares, 83/47/27/26/32, 160/55, E-7=29, SevEdu=21,562; P9
- `f3_3_abiertos` — ABIERTO 3.3: (1) 32 vs 33 hogares que salen de logro con 1 ciclo (regla estricta; 5 casos a 1 año); (2) 219 u_ij imputados (218 desempleo LD) con aporte pensión sin fuente; (3) 14 hogares sin ocupados con desocupados: posible doble conteo en caso 3 de empleo (pregunta a Martín)
- `f3_4_datos_modelo` — POR HACER 3.4: datos_modelo.py: A_i, M_i, Sev0, coef_ks, b, SevEdu^N; regresión 523 pobres, M0=0.038684, Sev0≈117,908, SevEdu≈21,562; calcular rango de B con los costos nuevos (MALLA_B)
- `f3_5_modelos` — POR HACER 3.5: modelo_base.py (ModeloIPMBase, template method; Modelo2 hereda) y Modelo_1/modelo1.py por capas: H puro vs enumeración en 50 hogares → equidad → q/tangentes/techo → bloque educativo → logro v_a → dos etapas. Instalar pulp + highspy donde se corra
- `f3_6_7_scripts` — POR HACER 3.6–3.7: 08_modelo1.py (corrida base) y 08_modelo1_barridos.py (barridos B, ρ, ρ_e); reportes por zona y sensibilidades (E3, ρ_e 20 %)
- `f3_estructura_carpetas` — ESTRUCTURA (5-nov): código en Optimizacion_1_S4/Modelos (común), Modelos/Modelo_1 y Modelos/Modelo_2; data/ docs/ graphify-out/ en la raíz; Martín hace los commits en PyCharm; commit de respaldo 51082ad en main sin push
