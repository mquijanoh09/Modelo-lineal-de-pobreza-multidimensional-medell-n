# Justificación de las decisiones de programación del Modelo 1

*Proyecto IPM Antioquia, Optimización 1 (EAFIT). Se registran aquí las decisiones que se toman al programar, con el porqué. Cada entrada dice qué se decidió, quién y cuándo, qué alternativas había, por qué se escogió una y qué consecuencia tiene en el código.*

Base del modelo: `modelo1/formulacion_modelo1.md`. Plan de programación: https://claude.ai/artifact/3sV7174gcSy4xDzqyZwZzT

---

## D1. Desempate por severidad en dos etapas

**Decisión (Martín, 4-nov-2026):** el desempate se hace en dos etapas, no en una sola corrida con λ.

1. **Etapa 1:** max Σ p_i·y_i con todas las restricciones. Resultado: H* (personas que salen).
2. **Etapa 2:** min Σ p_i·q_i con las mismas restricciones más Σ p_i·y_i ≥ H*.

**Alternativa descartada:** una sola corrida con max Σ p_i·y_i − λ·Σ p_i·q_i y λ < min p_i / Sev₀ ≈ 3×10⁻⁴.

**Por qué:**
- Con λ tan pequeño, todo el término de severidad vale como máximo λ·Sev₀ ≈ 35 personas, mientras que el término de H vale cientos de miles de personas (683,406 pobres en la línea base).
- HiGHS se detiene por defecto cuando el gap relativo es ≤ 1e-4 (opción `mip_rel_gap`, [documentación de HiGHS](https://ergo-code.github.io/HiGHS/dev/options/definitions/)). Aquí eso equivale a unas 68 personas. El solver puede declarar "óptimo" sin haber resuelto el desempate, e incluso dejar sin sacar a un hogar pequeño.
- Para que la versión de 1 etapa fuera confiable habría que poner `mip_rel_gap = 0`. Eso hace las corridas más lentas y más sensibles a errores numéricos, porque mezcla coeficientes de órdenes de magnitud muy distintos.
- En 2 etapas, cada objetivo trabaja en su propia escala, así que el gap de cada etapa tiene sentido, y H* se reporta limpio. Es una optimización lexicográfica: primero H y, entre los planes con ese H, el de menor severidad.

**Ejemplo:** dos planes sacan a las mismas 1,000 personas. El plan A deja una severidad de 100,000 y el B de 95,000. En 2 etapas siempre se elige B; en 1 etapa con el gap por defecto el solver puede detenerse en A.

**Consecuencia en el código:**
- Cada punto de un barrido (B, r, ρ, ρ_e) cuesta dos corridas. Siguen siendo de segundos.
- En la etapa 2, H* se toma del valor de la solución encontrada en la etapa 1 (la incumbente), no de la cota del solver. Así la restricción Σ p_i·y_i ≥ H* siempre es factible, porque esa misma solución la cumple.
- Se reportan el estado y el gap de las dos etapas.
- El techo de severidad (8) sigue haciendo el trabajo principal de equidad; el desempate solo decide en qué se gasta el presupuesto que sobra entre planes con el mismo H.

**Para la defensa:** "El desempate no es un ajuste fino de un peso: es un segundo problema que solo puede mejorar la severidad sin perder ni una persona que sale de la pobreza."

---

## D2. El CLEI cuenta como asistencia y quita la inasistencia del hogar

**Decisión (Martín, 5-nov-2026):** sí, el CLEI quita la inasistencia en el caso base.

**Hecho verificado (5-nov-2026):** un joven matriculado en un CLEI cuenta como "asiste" para el DANE. La nota de la pregunta P8586 de la ECV 2025 ("¿actualmente estudia?") dice textualmente: "Se consideran asistiendo: [...] Las personas que cursan programas para jóvenes y adultos por ciclos." También dice que "No se consideran asistiendo: Las personas que están validando la Primaria o el Bachillerato" ([DANE, ECV 2025, variable P8586](https://microdatos.dane.gov.co/index.php/catalog/905/variable/F24/V2686)). El IPM usa P8586 para la inasistencia (Comité de Expertos DANE, 2022, num. 2.1, verificado en el hilo de costos oficiales).

**Consecuencia para el modelo:**
- E2 (CLEI de primaria, 13 años o más con máximo 3 grados aprobados, Decreto 1075 de 2015) **sí** quita la inasistencia del niño, igual que E1.
- E3 (CLEI de secundaria, desde 15 años) también la quitaría para los de 15 y 16 años, pero E3 sigue fuera del caso base por la falta del dato de años por fuera del colegio (mejora #2).
- Restricción E-6b: x_i,inas ≤ Σ_s z_ks para cada niño k del hogar que no asiste (6 a 16 años), con s en las estrategias activas del escenario.

**Recomendación anterior que queda superada:** el 4-nov se propuso que el CLEI no contara en el caso base porque no estaba verificado. Con la fuente oficial ya no hace falta esa cautela.

**Por qué importa:** para un joven de 13 a 16 años que no asiste, E2 cuesta unas 10 veces menos que E1 ($0.96 M o $1.29 M por ciclo frente a unos $11 M por regreso), así que el modelo puede sacar de la inasistencia a esos hogares mucho más barato.

---

## D3. Los niños que no asisten y no tienen rezago también pueden recibir E1

**Decisión (Martín, 5-nov-2026):** se agregan al modelo los niños de 6 a 16 años que no asisten y **no** están entre los 215 rezagados (conjunto K^I), con la estrategia E1 (Renta Ciudadana $3.0 M/p por hogar + cupo SGP del nivel).

**Por qué:**
- La privación de inasistencia del DANE mira a todos los niños de 6 a 16 años que no asisten, tengan rezago o no. Ejemplos: un niño de 6 años que nunca entró (el rezago se mide desde los 7) o uno de 10 que va al día pero dejó de estudiar este año.
- La restricción E-6b exige que vuelvan **todos** los no asistentes del hogar. Si uno de ellos no tuviera variable z, ese hogar nunca podría quitar la inasistencia, y el modelo subestimaría lo que se puede lograr.

**Alcance:**
- Su coeficiente en SevEdu es 0, porque no tienen atraso: solo aportan a H.
- **No** quedan bajo la cobertura obligatoria del art. 67 (E-7). Por la decisión del 4-nov, E-7 cubre solo a los no asistentes de 6 a 15 años entre los 215; ampliarla es la mejora #4 (`mejoras/mejoras_modelo.md`). El modelo los atiende solo si le conviene para H.
- E2 no aplica a ellos en la práctica: quien tiene 13 años o más con máximo 3 grados aprobados ya tiene al menos 4 de atraso, así que está entre los 215.

**Consecuencia en el código:** el conteo (05) exporta la tabla por niño con todos los no asistentes de 6 a 16 años de hogares pobres, con una bandera `en_cohorte_sevedu` para los 215.

---

## D4. El H binario se mide sobre la foto inicial

**Decisión (Martín, 5-nov-2026, en el hilo "Continuar asesoría del modelo MILP"):** H se calcula con las edades de hoy (lectura a). Nadie envejece dentro de H. El puntaje final de cada hogar es el puntaje de hoy menos las privaciones que el modelo pagó. El paso del tiempo solo se modela en SevEdu. Queda escrito en el §6 de `modelo1/formulacion_modelo1.md`.

**Alternativa descartada (lectura b):** medir H al final del año, con los niños un año mayores. Un joven rezagado de 17 años saldría del rezago al cumplir 18, y un no asistente de 16 saldría de la inasistencia al cumplir 17.

**Por qué:**
- **Sin salidas gratis.** Con (b), un hogar con puntaje 0.36 cuya privación de rezago viene solo de un joven de 17 años quedaría en 0.31 y saldría de la pobreza sin gastar un peso. Entre los 215 rezagados hay 27 de 17 años, y hay 14 no asistentes de 16: (b) inflaría H por el paso del tiempo, no por la intervención.
- **Coherencia entre indicadores.** No se modela qué pasa en un año con el empleo, la salud o la vivienda. Envejecer solo dos indicadores mezclaría una foto con una proyección.
- **Igual que el paper.** El modelo de Hamie et al. (2024) es estático: solo cambian las privaciones intervenidas.
- **Comparable con el DANE.** H usa la regla oficial con los datos de la ECV tal como están.

**Dónde sí entra el tiempo:** en SevEdu, medido al final del año contra el escenario sin intervenir y con cohorte fija (los 215 siguen contando aunque cumplan 18). Ahí el paso del tiempo es explícito y no se confunde con logro del modelo.

**Consecuencia en el código:** s_i = Σ w_j·M_ij·(1 − x_ij) con las M_ij de la ECV. Las edades solo se usan en el conteo (05) para construir la tabla por niño y los coeficientes de SevEdu.

---

## D5. Este hilo programa también el conteo de personas y `parametros.py`

**Decisión (Martín, 5-nov-2026):** el hilo de programación del Modelo 1 escribe también `05_conteo_personas.py` y completa `parametros.py`.

**Por qué:**
- El Modelo 1 no puede correr sin u_ij (costos por hogar), sin la tabla por niño (SevEdu, rezago e inasistencia) y sin la tabla por adulto (logro y analfabetismo).
- Jerónimo necesita esta semana `parametros.py`, `conteo_pares.csv` y `ninos_rezago.csv` para los Modelos 3 y 4. Si los hace una sola persona con las mismas reglas, los cuatro modelos usan exactamente los mismos datos.
- `parametros.py` se construye sobre el archivo que ya existe (trabajo infantil, CLEI y barreras de salud), sin duplicar valores.
