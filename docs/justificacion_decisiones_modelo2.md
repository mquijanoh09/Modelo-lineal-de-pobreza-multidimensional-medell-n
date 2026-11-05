# Justificación de las decisiones de programación del Modelo 2

*Proyecto IPM Antioquia, Optimización 1 (EAFIT). Aquí quedan las decisiones que se toman al programar el Modelo 2, cada una con su porqué: qué se decidió, quién lo decidió y cuándo, qué alternativas había y qué consecuencia tiene en el código.*

Plan de programación (fase 1): https://claude.ai/artifact/B9a3qZtYdcu6CdENKVEpqC
Base heredada: `modelo1/formulacion_modelo1.md` y `modelo1/justificacion_decisiones.md` (D1–D3 aplican también aquí).

## D-M2-1. La meta es sobre M0

**Decisión (Martín, 5-nov-2026, al aprobar `modelo2/formulacion_modelo2.md`):** la meta es Σ C_i ≤ (1 − m)·M0⁰·Pob, con C_i ≥ p_i·s_i − U_i·y_i.

**Alternativa descartada:** meta sobre H (Σ p_i y_i ≥ m_H Σ p_i).

**Por qué:** es la meta del paper (Con 6) y la de los Modelos 3 y 4, así que los modelos 2 a 4 se comparan igual. Además M0 = H × A premia quitar privaciones a quien sigue pobre, que es la perspectiva de equidad del proyecto; con H solo contaría sacar a los que están cerca del umbral.

**Consecuencia en el código:** se agregan 523 variables continuas C_i y 523 restricciones de censura; se quita la (1) presupuesto.

## D-M2-2. Capas de equidad

**Decisión (Martín, 5-nov-2026):** E-7 (cobertura del art. 67) siempre activa; SevEdu (E-5, ρ_e = 14 %) solo como sensibilidad; sin techo de severidad ni tangentes.

**Por qué:** E-7 es una obligación constitucional, no una preferencia. M0 ya cumple el papel del techo de severidad. Con meta de M0 el rezago binario no se mueve en un año, así que la sensibilidad con SevEdu mide cuánto cuesta no abandonar a los niños más atrasados.

**Consecuencia en el código:** sin q_i ni las 6,571 tangentes; E-5 queda como interruptor. Hay un costo mínimo aunque m = 0 (el piso de E-7), que se reporta aparte.

## D-M2-3. La meta se exige en cada zona

**Decisión (Martín, 5-nov-2026):** "Tomaremos tanto lo urbano como lo rural". La restricción (M-d) entra en el caso base: Σ_{i∈d} C_i ≤ (1 − m)·M0⁰_d·Pob_d para cada zona d, con m_d = m.

**Lectura tomada:** se usan las 3 zonas de `P3` (cabecera, centro poblado y rural disperso), igual que la restricción (4) del Modelo 1. Lo "rural" son el centro poblado y el rural disperso. Si Martín prefiere solo 2 grupos (urbano y rural), basta con cambiar el agrupador.

**Alternativa descartada:** solo la meta global, que concentraría el plan en la cabecera (53 % de los pobres) porque allí es más barato bajar M0.

**Por qué:** que ninguna zona quede abandonada, sobre todo la rural dispersa (M0 = 0.106, la más alta). Como Σ_d C_d ≤ (1 − m)·Σ_d M0⁰_d·Pob_d = (1 − m)·M0⁰·Pob, cumplir la meta en cada zona implica cumplir la global, así que la (M) se vuelve redundante pero se deja como chequeo.

**Consecuencia en el código:** 3 restricciones en vez de 1. La meta máxima factible es la de la zona que menos puede bajar, así que el barrido de m llega hasta ese mínimo. La meta solo global queda como sensibilidad, para mostrar cuánto cuesta la equidad territorial (diferencia de costo entre las dos versiones).

## D-M2-4. El CLEI también quita la inasistencia del hogar

**Decisión (Martín, 5-nov-2026, como D2 del Modelo 1):** (Inas) queda x_i,inas ≤ Σ_s z_ks para cada niño k del hogar que no asiste, no solo con z_k,E1.

**Por qué:** la nota de la pregunta P8586 de la ECV 2025 dice que "las personas que cursan programas para jóvenes y adultos por ciclos" se consideran asistiendo. Ver `modelo1/justificacion_decisiones.md`, D2.

**Consecuencia en el código:** para un joven de 13 a 16 años elegible a E2, el modelo puede quitar la inasistencia con un ciclo CLEI ($958,431 o $1,286,194) en vez de E1 (Renta Ciudadana más el cupo SGP). Se corrigió la fila (Inas) de `modelo2/formulacion_modelo2.md` el 5-nov.

## Fase 2 (propuesta del 5-nov-2026, esperando aprobación de Martín)

- **F2-1. Objetivo en millones de pesos.** Los costos llegan a ~10¹¹ pesos y los coeficientes de M0 a ~10⁴. Escalar el objetivo deja todo el MILP en magnitudes parecidas y reduce los errores numéricos de HiGHS. El resultado se reporta en pesos.
- **F2-2. gapRel = 1e-6, una sola etapa, límite de 300 s.** Con un costo de ~$100 mil millones, el 1e-4 por defecto deja ~$10 M de holgura (lo que cuesta un hogar); con 1e-6 queda en ~$0.1 M. Es la misma tolerancia que Jerónimo usa al minimizar costo en M3/M4. Sin q_i no hay desempate, así que basta una etapa.
- **F2-3. meta_maxima() antes de barrer.** Es un auxiliar que calcula la reducción máxima de M0 en cada zona, con E-7 activa y sin meta. El barrido de m se detiene en la menor de las tres reducciones, porque más allá el caso base con meta por zona es infactible.
- **F2-4. Clase madre con herencia (DECIDIDO por Martín, 5-nov-2026).** Martín propuso usar programación orientada a objetos: `modelo_base.py` define la clase `ModeloIPMBase` con lo compartido (variables x, y, z, t, v; reglas de intervención (2), E-1 a E-3, E-7, 10a, 10b, Inas, 11 y 12; `costo_total()`; `recalcular()`), y `Modelo1` y `Modelo2` heredan de ella. Cada hija escribe en su archivo solo lo suyo: el M1 el presupuesto, la equidad r, las tangentes, la severidad, SevEdu y las dos etapas; el M2 C_i, la censura, la meta y el objetivo de costo. Es el patrón *template method*: `construir()` de la madre llama, en orden, a `crear_variables()`, `agregar_reglas_intervencion()`, `agregar_restricciones_propias()` y `definir_objetivo()`, y estos dos últimos los implementa cada hija.
  - **Por qué es mejor que copiar el código:** cada regla tiene una sola fuente de verdad (principio DRY). Así no se repite lo de la inasistencia, que quedó corregida en una formulación y no en la otra.
  - **Por qué es mejor que importar de modelo1.py:** el M2 no queda atado a cosas que no usa (las tangentes, las dos etapas).
  - **Riesgo controlado:** un cambio en la madre afecta a los dos modelos. Las pruebas de regresión del M1 (523 pobres, M0 = 0.038684, Sev₀ ≈ 117,908) detectan si algo se rompe.
  - **Qué no va en la madre:** lo que cumple un papel distinto en cada modelo, aunque los dos lo usen. Por ejemplo, SevEdu es una restricción fija en el M1 y una sensibilidad en el M2, así que es un método que cada hija decide si llama.
  - **Alcance:** los Modelos 3 y 4 no heredan, porque deciden por zona y no por hogar.

- **F2-5. Estructura de carpetas (DECIDIDO por Martín, 5-nov-2026, 01:30).** Todo el código va en `C:\Users\marti\PycharmProjects\Optimizacion_1_S4\Modelos\`:
  - Lo común (`parametros.py`, `utils_dane.py`, el 05, `datos_modelo.py`, `modelo_base.py`) va directamente en `Modelos\`. Lo mueve el hilo del Modelo 1.
  - Lo exclusivo del M1 va en `Modelos\Modelo 1\`.
  - Lo exclusivo del M2 (`modelo2.py`, `09_modelo2.py`, `09_modelo2_barridos.py`, `resultados\`) va en `Modelos\Modelo 2\`.
  - **Importar con un espacio en el nombre:** "Modelo 2" no puede ser un paquete de Python. Cada script de esa carpeta hace `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))` antes de `import parametros`. `modelo2.py` se importa sin problema porque está en la misma carpeta que los scripts 09.
  - **Rutas a datos:** se toman de `utils_dane` (`RAIZ` = raíz del repo, `MODELOS`, `BASE` = data/, `OUT` = data/processed/). Es la convención del hilo del M1 (5-nov, 01:31), que es la misma para los dos modelos. Así el script corre igual desde PyCharm o desde la terminal.

## Interfaz acordada con el hilo del Modelo 1 (5-nov-2026, 01:20)

El hilo del Modelo 1 escribe `modelo_base.py` después del 05 y de `datos_modelo.py`; `Modelo2` hereda de esa clase. Si el hilo del M1 cambia algo de lo que sigue, avisa antes.

- **Clase:** `ModeloIPMBase(datos, esc)`.
- **Atributos:**
  - `self.datos`: lo que devuelve `datos_modelo.cargar(esc)`.
  - `self.esc`: el dict de `parametros.escenario()`.
  - `self.prob`: el `pulp.LpProblem`.
  - Variables, cada una en un dict: `self.x[(i, j)]`, `self.y[i]`, `self.z[(k, s)]`, `self.t[i]`, `self.v[a]`.
  - Expresión `self.s[i]`: el puntaje del hogar después de intervenir.
- **Llaves:**
  - i = ID_HOGAR (`DIRECTORIO_SECUENCIA_P`).
  - k y a = ID_PERSONA (`ID_HOGAR_ORDEN`).
  - s ∈ {"E1", "E2", "E3"}.
  - j = nombre del indicador.
  - El modelo solo incluye a los hogares pobres iniciales (I).
- **Métodos:**
  - `construir()`, como template method: llama a `crear_variables`, `agregar_reglas_intervencion`, `agregar_restricciones_propias` (abstracto) y `definir_objetivo` (abstracto).
  - `costo_total()`: devuelve una `LpAffineExpression`.
  - `agregar_sevedu(rho_e)`: método aparte; cada hija decide si lo llama.
  - `resolver(gap_rel=None, time_limit=None)`: devuelve un dict con estado, gap y objetivo.
  - `solucion()`: devuelve los DataFrames `plan_hogar`, `plan_nino` y `plan_adulto`.
  - `recalcular()`: H, A, M0, Sev, SevEdu y costo, por zona y total.
- **Restricciones comunes** (solo se crean z donde e_ks = 1, así que no hace falta una restricción de elegibilidad): `Sal_<i>`, `E2_<k>`, `E3_<k>`, `E7_<k>`, `Rez_<i>_<k>`, `Inas_<i>_<k>`, `Log_<i>`, `Analf_<i>_<a>`.
- **Lo que agrega el Modelo 1:** `self.q`, `Pres`, `Eq_<d>`, `Tan_<i>_<a>`, `Sev`, `SevEdu` y las dos etapas.
- **Lo que agrega el Modelo 2:** `self.C[i]`, `Cen_<i>`, `Meta_<d>` y `Meta`; el objetivo es min `costo_total()` en millones; `meta_maxima()`. `resolver()` se llama con gap_rel = 1e-6 y time_limit = 300.

## Subfase 3.2 (5-nov-2026): censura y meta global

- **F3-1. La población total se cancela.** M0⁰·Pob = Σ p_i c0_i (el numerador de M0), así que la meta queda Σ C_i ≤ (1 − m)·Σ p_i c0_i. El modelo no necesita calcular Pob (7.23 M), y la meta por zona usa el mismo truco con el numerador de cada zona.
- **F3-2. C_i es el producto p_i·s_i, no el puntaje solo.** La formulación aprobada define C_i como contribución al numerador de M0, es decir p_i·s_i si el hogar sigue pobre y 0 si sale. Se escribe C_i ≥ p_i·s_i − U_i·y_i con U_i = p_i·c0_i.
- **F3-3. Prueba contra un algoritmo exacto distinto.** El MILP se compara con una enumeración por hogar de los 2ⁿ subconjuntos de privaciones, que conserva solo la frontera (costo, contribución). Coincide con el MILP en costo, y la prueba falla si se rompe la censura (comprobado quitando el término −U_i·y_i).
- **F3-4. Costos de prueba sintéticos.** La prueba usa costos u = 1 con valores de relleno donde todavía no hay u_ij (empleo, logro, inasistencia…). Solo prueban la lógica, no son los costos del modelo.
- **F3-5. Versiones.** El código se probó con PuLP 3.3.2, la versión del `.venv` de Martín. PuLP 4.x cambió la firma de `LpVariable` (ya no acepta `cat=`), así que no hay que actualizar PuLP sin avisar.
- **F3-6. Carpetas.** Martín renombró las carpetas a `Modelo_1` y `Modelo_2` (sin espacio). El `sys.path.insert` se mantiene porque el script se ejecuta desde su carpeta y no desde `Modelos\`.

## Subfase 3.3 (5-nov-2026): meta por zona y meta_maxima()

- **F3-7. La meta por zona se prueba sumando exactos.** Como cada zona tiene su propia meta y las zonas no comparten nada, el costo mínimo es la suma de los mínimos de cada zona. La prueba compara el MILP contra esa suma, calculada con el algoritmo exacto de la 3.2. Coinciden con m = 10 % y 30 %. La meta por zona cuesta igual o más que la global (la implica), y la prueba lo verifica.
- **F3-8. meta_maxima() resuelve un solo problema.** Minimiza Σ C_i sin meta. Como las zonas no se tocan, minimizar el total minimiza también cada zona, y de ahí salen la reducción máxima por zona y la total. El barrido de m se detiene en la menor de las tres. Con una meta apenas por encima el modelo es infactible; apenas por debajo, factible (ambos comprobados).
- **F3-9. Error encontrado por la prueba.** En PuLP una variable con `cat="Binary"` ignora `upBound` y vuelve a quedar en 0..1. La primera versión de `meta_maxima` creía haber fijado x = 0, pero no lo hacía, y daba 100 % contra 65 % del método exacto. Ahora las privaciones fijas se declaran enteras con cotas 0..0 (`crear_x`). Esto vale también para las reglas de la 3.4: lo que no se puede quitar (rezago binario, logro en 470 hogares) debe usar `crear_x`.
- **F3-10. Alcance de la prueba.** Usa 6 indicadores no removibles (caso extremo, solo para la prueba). Con solo 3, todos los hogares podían salir igual de la pobreza quitando otras privaciones, el máximo daba 100 % y la prueba no discriminaba. En el modelo real el máximo será menor que 100 % por el rezago binario y el logro.

## Fase 3.4–3.7 — programación completada (Jerónimo, 5-nov-2026)

*Completado a partir del commit `0389805` de Martín. Las funciones de núcleo de las subfases 3.2 y 3.3 se conservan tal
cual (las usan `prueba_3_2.py` y `prueba_3_3.py`, que siguen pasando); se agregaron `fijos_cero` y `meta_maxima()`, que la
prueba 3.3 ya importaba.*

- **F3-1. Clase `Modelo2(ModeloIPMBase)`.** Hereda las reglas comunes (2), E-1 a E-3, E-7, (10a)/(10b), (Inas), (11) y (12). Agrega solo (3), la meta (M) o (M-d) y el objetivo de costo. La (2) ya no se duplica: la pone la madre.
- **F3-2. `meta_maxima` en una sola corrida.** Min $\sum_i C_i$ sin meta ni costo. Todas las restricciones son por hogar (o por niño dentro del hogar), así que el problema se separa: cada hogar llega a su menor $C_i$ y la suma por zona es la menor posible en cada zona. Una corrida da las tres zonas.
- **F3-3. Piso de E-7.** El barrido empieza en m = 0, que da el costo de E-7 sin meta. `09_modelo2_barridos.py` reporta el costo total y el costo sobre ese piso.
- **F3-4. Validación cruzada con el Modelo 1** (formulación §6). Se usa el plan del M2 *con SevEdu*, porque el Modelo 1 tiene E-5 fijo y el plan sin SevEdu podría no ser factible allí.
