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

## Subfase 3.4 (6-nov-2026): reglas completas — en curso

- **F3-11. Clase Modelo2 escrita contra la interfaz de la base.** `Modelo2(ModeloIPMBase)` solo define `agregar_restricciones_propias()` (C_i, `Cen_<i>`, `Meta_<d>` o `Meta`, y SevEdu si la sensibilidad está activa) y `definir_objetivo()` (min `costo_total()` en millones). Hereda de la base las variables, la salida `Sal_<i>` y todas las reglas de intervención. Borrador en `modelo2/codigo/borrador/modelo2_clase.py`; no se copia al PC hasta que exista el `modelo_base.py` real.
- **F3-12. meta_maxima() con todas las reglas.** Pasa a ser un método de clase que arma el mismo modelo con `objetivo="contribucion"` y sin meta. Así el tope por zona incluye lo que el rezago binario y el logro no dejan quitar (`datos.quitable`), y no solo lo que supuse en la prueba 3.3.
- **F3-13. Lo que ya se verificó.** `datos_modelo.py` del Modelo 1 pasa su regresión en mi entorno (523 pobres, M0 0.038684, Sev₀ 117,908, SevEdu 21,562, 6,571 tangentes, 32 hogares con logro quitable, 0 con rezago). El borrador de Modelo2 corre contra una base de pruebas con solo x, y, s y Sal (sin educación), y resuelve con m = 5 % y 10 %; esa base de pruebas no es el modelo y no se entrega.

## Subfase 3.4 terminada (6-nov-2026): Modelo 2 completo

- **F3-14. Archivos.** `modelo2.py` es ahora la clase `Modelo2(ModeloIPMBase)`, con solo C_i, `Cen_<i>`, `Meta_<d>` (o `Meta`), SevEdu como sensibilidad y el objetivo de costo en millones. El núcleo aislado de las subfases 3.2 y 3.3 pasó a `nucleo_pruebas.py` y solo lo usan `prueba_3_2.py` y `prueba_3_3.py`, que validan la censura contra un algoritmo exacto. La base cambió un detalle respecto a lo acordado: `sentido()` es un gancho nuevo que cada hija define (`LpMinimize` en el M2).
- **F3-15. Piso de costo: $104.4 mil millones con meta 0 %.** La cobertura obligatoria del art. 67 (E-7) cubre 29 niños de la cohorte, y cada uno representa muchos niños por el factor de expansión. Ese piso coincide al peso con una cuenta independiente (por hogar, la combinación más barata de estrategias; E1 paga la Renta Ciudadana una vez). El piso es casi todo el costo en las metas pequeñas: meta 5 % cuesta $105.6 mil millones, 10 % cuesta $108.7 y 20 % cuesta $118.9.
- **F3-16. El tope de la meta es 100 %.** Con M0 censurado, un hogar deja de aportar en cuanto sale de la pobreza, y los 523 hogares pueden salir quitando privaciones que sí son intervenibles. Esto corrige lo que se esperaba en la 3.3 (un tope menor que 100 %). La meta no limita el barrido; lo acota el costo: m = 30 % cuesta $134.2 mil millones, 50 % cuesta $193.6, 70 % cuesta $296.7, 90 % cuesta $467.8 y 100 % cuesta $660.6 (saca a los 523 hogares). `malla_m2(m_max)` hay que redefinirla en la 3.7 con un tope de costo o de meta, no con `meta_maxima()`. **Actualización (F4-9, 9-nov):** las cifras de costo de 90 % y 100 % valían antes de decidir que el desempleo sin persona identificada no se quita. Con esa decisión (caso base actual): 90 % = $481.4 mil millones y 100 % = $740.4. Las metas de 5, 10, 20 y 50 % no cambian.
- **F3-17. Meta por zona frente a solo global.** Exigir la meta en cada zona cuesta más: con 5 % es $105.6 contra $104.7 mil millones; con 10 % es $108.7 contra $105.4; con 20 % es $118.9 contra $109.1. La diferencia es el precio de no abandonar ninguna zona; es el resultado que se grafica en la 3.7.
- **F3-18. Verificación.** `prueba_3_4.py` comprueba que el costo recalculado con la cuenta independiente de la base coincide con el MILP, que cada zona cumple su meta, que el costo no baja al subir la meta, que las 631 privaciones no quitables quedan en 0 y que HiGHS cierra con gap ≤ 1e-6 en 2 a 55 s por corrida. Se corrió con PuLP 3.3.2.

## Subfase 3.5 (6-nov-2026): resultados, tabla común y guardado

- **F3-19. Gasto por rubro y zona (el E_j del paper).** `gasto_por_indicador()` reparte el costo en los 11 indicadores simples (se pagan con x_ij) y en dos rubros de educación: `educacion_ninos` (z y Renta Ciudadana t) y `educacion_adultos` (ciclos CLEI v). No se puede repartir lo de los niños entre rezago e inasistencia, porque un mismo z sirve a los dos; por eso van juntos. La tabla suma exactamente el costo total (comprobado al peso) y su gasto por zona coincide con el que recalcula la base.
- **F3-20. Tabla común de los 4 modelos.** `tabla_comun()` entrega, por zona y total: personas y hogares que salen, H, A, M0 (inicial y final), reducción de M0, severidad, SevEdu y costo en pesos, que son las columnas del punto 10 de la agenda de Jerónimo. Se calcula con `recalcular()` de la base, que no usa las y del MILP.
- **F3-21. Una fila por corrida y archivos.** `resumen()` devuelve una fila (meta, estado, gap, segundos, costo, reducción por zona) para armar la curva costo vs. meta en la 3.7. `guardar(carpeta, nombre)` escribe cinco CSV (tabla común, gasto, plan por hogar, por niño y por adulto), en UTF-8 con BOM para que Excel abra bien los acentos.
- **F3-22. Qué se ve con m = 10 %.** El costo es $108.7 mil millones, de los cuales $104.4 (96 %) son educación de niños, el piso de E-7; solo $2.6 van a ciclos CLEI de adultos y $1.65 a barreras de salud. Salen 29 hogares. SevEdu baja de 21,562 a 19,015 (11.8 %) solo por el art. 67, sin exigir SevEdu.

## Subfase 3.6 (6-nov-2026): 09_modelo2.py, caso base

- **F3-23. Qué valida el script antes de dar resultados.** (a) Con meta 0 % el costo es el piso de E-7 y coincide con una cuenta independiente. (b) El costo del MILP coincide con el que recalcula la base. (c) Cada zona cumple su meta de M0. (d) El costo no baja al subir la meta. Si alguna falla, el script termina con error y dice cuál.
- **F3-24. Resultados del caso base** (p = 0.369, sin E3, meta en cada zona, HiGHS gap ≤ 1e-6, todas las corridas Optimal en 2 a 3 s):

| Meta de M0 | Costo (mil millones) | Hogares que salen | H final | Rubros que se agregan al piso |
| --- | --- | --- | --- | --- |
| 0 % | 104.41 | 0 | 9.45 % | educación de niños (E-7) |
| 5 % | 105.58 | 19 | 8.96 % | barreras de salud 1.17 |
| 10 % | 108.66 | 29 | 8.43 % | + ciclos CLEI de adultos 2.60; barreras 1.65 |
| 20 % | 118.86 | 65 | 7.39 % | + CLEI 10.50; barreras 3.30; aseguramiento 0.66 |

- **F3-25. Lectura.** El piso de E-7 domina el costo de las metas pequeñas, y el costo marginal de bajar M0 es bajo porque los primeros hogares que salen lo hacen con barreras de salud ($52,100 por persona urbana), logro por CLEI y aseguramiento. SevEdu queda en 19,015 en las tres metas (11.8 % menos que sin intervenir): la meta de M0 no mueve más educación que el art. 67.
- **F3-26. Archivos.** Cada meta guarda sus cinco CSV con prefijo `m05_`, `m10_`, `m20_` en `Modelos\Modelo_2\resultados\caso_base\`, más `resumen_caso_base.csv`.

## Subfase 3.7 (7-nov-2026): 09_modelo2_barridos.py

- **F3-27. Malla.** Como la meta máxima alcanzable es 100 % (cuesta $660.64 mil M, los 523 hogares salen), el barrido va de 0 % a 100 % de 5 en 5 %, no acotado por `meta_maxima` como decía `malla_m2`. (El costo de 100 % de $660.64 es el de antes de la decisión sobre desempleo imputado; hoy es $740.37, ver F4-9.) 21 metas x 2 variantes, todas Optimal con gap ≤ 1e-6 (las más lentas, 25 a 56 s, entre 65 % y 90 %).
- **F3-28. Costo de la equidad territorial** (meta en cada zona menos meta solo global): 0.91 en 5 %, 3.23 en 10 %, 9.72 en 20 % (máximo 9.86 en 25 %), baja a 0 en 100 %. Exigir la meta en cada zona nunca cuesta menos que la global (validado).
- **F3-29. Sensibilidades** (metas 5/10/20 %, mil millones): p = 0.50 → 88.90/91.98/102.19; p = 0.75 → 73.24/76.32/86.53; SevEdu activa (rho_e 0.14) → 107.09/110.18/120.38; E3 + SevEdu (rho_e 0.20) → 78.71/81.35/91.00. Mayor p baja el costo porque Renta Ciudadana se divide por p. Mismos hogares que salen con p distinto (19/29/65).
- **F3-30. Fuera de 3.7 por ahora.** u = 1 (datos_modelo lanza NotImplementedError) y la prueba cruzada con el Modelo 1 (el hilo del Modelo 1 aún no entrega su clase). Sin tocar `malla_m2` en parametros.py: queda con paso 0.025 y m_max como argumento.

## Auditoría del Modelo 2, fase 1 (7-nov-2026): H1 y H2

- **F4-1. H1 (M2-H1).** El `modelo2.py` del PC era la versión de la subfase 3.4 (3,941 bytes); la completa (7,449 bytes, con `tabla_comun`, `guardar`, `resumen`, `gasto_por_indicador`) no se había copiado en 3.5. Error de entrega mío. Se copió la completa al PC. Pasos para probarla: se sincronizaron `modelo_base.py`, `parametros.py` y `datos_modelo.py` actuales del PC y se corrió `09_modelo2.py`.
- **F4-2. H2 (M2-H2).** La corrección está en `ModeloIPMBase.resolver()` (hilo del Modelo 1): el estado pasa a "Cortado" si `sol_status` no es óptimo, y `GAP_REL` por defecto es 1e-6. Modelo2 usa SOLVER_M2 con 1e-6 y compara `estado == "Optimal"`, así que una corrida cortada ya hace fallar la validación. Resultado tras el cambio: `09_modelo2.py` termina en "TODO OK" con los mismos costos (105.58 / 108.66 / 118.86 mil millones).

## Auditoría del Modelo 2, fase 2 (8-nov-2026): H3 y H4

- **F4-3. H3, reporte en tres cifras.** `Modelo2.piso_e7(datos)` calcula el costo mínimo de E-7 sin el MILP (antes era `piso_exacto` dentro de 09_modelo2.py). `resumen()` y los CSV de barridos ahora traen `piso_E7` y `costo_incremental` = costo − piso. Caso base: incremental 1.17 / 4.25 / 14.45 mil millones para 5 / 10 / 20 % (el piso es 104.41).
- **F4-4. Versión comparable con M3/M4.** Se agregó `"sin_E7": {"cobertura_art67": False}` a `SENSIBILIDADES` de parametros.py (cambio aditivo). El barrido corre `escenario_m2("sin_E7", "meta_global")`: costo 0.35 / 1.32 / 6.47 mil millones para 5 / 10 / 20 %. Falta acordar con Jerónimo por escrito que este es el "first best" que usa.
- **F4-5. H4, brecha A.** `resumen()` y los barridos traen `A` de los que siguen pobres y `A_inicial` (0.4094). Caso base: 0.4101 / 0.4125 / 0.4186.

## Re-auditoría del Modelo 2, fase A (9-nov-2026): N1, N3 y desempleo imputado en los barridos

- **F4-7. N1, costo de la meta.** En los barridos, `costo_incremental_mil_millones` = costo con meta − costo del MISMO escenario con meta 0 % (`piso_escenario_mil_millones`, resuelto con el MILP). Así no se mezcla el gasto que SevEdu exige con o sin meta. Antes, con E3 y SevEdu 20 %, la meta de 5 % aparecía costando 12.87; ahora 0.68 (10 %: 3.31; 20 %: 12.96). Con SevEdu 14 % sobre el caso base: 1.17 / 4.25 / 14.45, igual que sin SevEdu. `Modelo2.piso_e7()` queda como validación independiente del caso base (en `resumen()` el incremental solo vale si E-7 es la única obligación; así consta en el código).
- **F4-8. N3, unidades.** `piso_E7` pasó a `piso_E7_mil_millones`; todo el CSV de barridos queda en mil millones. `resumen_caso_base.csv` sigue en pesos.
- **F4-9. Sensibilidad `desempleo_imputado` en los barridos** (el desempleo sin persona identificada vuelve a ser quitable): metas 5/10/20 % = 105.58 / 108.66 / 118.86; 80 % = 371.76; 90 % = 467.84; 95 % = 540.43; 100 % = 660.64 (mil millones). Son las cifras de F3-16 y F3-27, que valían ANTES de la decisión del 7-nov de no quitar el desempleo imputado. Con esa decisión (caso base actual) 100 % cuesta 740.37, 95 % 574.30, 90 % 481.43 y 80 % 373.53; las metas de 5, 10 y 20 % no cambian. Pendiente en fase B: anotar esto en F3-16 y F3-27 y en el grafo.

## Re-auditoría del Modelo 2, fase B (9-nov-2026): documentación

- **F4-10.** Se corrigieron F3-16 y F3-27 (nota con las cifras vigentes de desempleo imputado) y `formulacion_modelo2.md` (meta por zona = caso base, prueba cruzada hecha, regla de desempleo). Las copias de ambos documentos en `docs\` del PC se actualizan con este cambio.

## Tercera auditoría del Modelo 2 (9-nov-2026): B1, B2 y B3

- **F4-11. B1.** En `resumen()` la columna `costo_incremental` pasó a `costo_sobre_piso_E7_mil_millones`: el nombre dice que se resta solo el piso de E-7, válido en el caso base. El costo de una meta en otros escenarios sale de los barridos (`costo_incremental_mil_millones`, contra el piso del mismo escenario).
- **F4-12. B2.** `resumen_caso_base.csv` ahora trae `costo_mil_millones` y `piso_E7_mil_millones` además de las columnas en pesos, y el resumen impreso de `09_modelo2.py` usa mil millones, igual que los barridos.
- **F4-13. B3.** Se borró `modelo2/codigo/parametros_con_sin_E7.py` (copia del 8-nov, desactualizada). La versión vigente de `parametros.py` está en `/mnt/project-files/modelo1/codigo/parametros.py` y en el PC. No se tocó ningún archivo compartido.
