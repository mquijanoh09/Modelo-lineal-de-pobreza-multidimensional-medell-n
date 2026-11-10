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

---

# Fase 3 — decisiones al programar

## P1. `parametros.py`: costos calculados desde el dato de la fuente (5-nov-2026)

**Qué se hizo:** los costos que vienen de una cuenta (acueducto y alcantarillado rurales, pisos y paredes urbanos, hacinamiento, PCI urbano, aporte a pensión, Empleos para la Vida) se escriben como la cuenta, no como el resultado redondeado. Ejemplo: `5_789e6 / 551 * 3.3 * IPC_2022_A_2025` en vez de `43_700_000`.

**Por qué:** si la profesora pregunta de dónde sale un número, la línea de código muestra la fuente y la operación. Si cambia un insumo (el SMMLV o el factor IPC), todos los costos que dependen de él cambian solos.

**Consecuencia:** el acueducto rural queda en $43,685,412 (el informe lo redondea a $43.7 M) y el alcantarillado rural en $15,280,851 ($15.3 M).

## P2. p = 0.369, no 0.37 (5-nov-2026)

**Qué se hizo:** se usa el cumplimiento del ciclo 4 de 2025 de Renta Ciudadana con tres decimales, 0.369, igual que en los modelos de Jerónimo.

**Por qué:** es el valor verificado (Prosperidad Social) y así los cuatro modelos usan el mismo número. Con 0.369 la transferencia por regreso logrado cuesta $8,130,081 por hogar.

## P3. Escenarios como "caso base + cambios" (5-nov-2026)

**Qué se hizo:** `CASO_BASE` es un diccionario con todos los supuestos, y cada sensibilidad solo dice qué cambia (`{"p": 0.50}`). La función `escenario(nombre)` arma el escenario completo.

**Por qué:** una sensibilidad nunca puede olvidar un supuesto del caso base, porque lo hereda. Para correr una sensibilidad nueva basta agregar una línea.

## P4. Empleo y desempleo se costean persona por persona en el 05 (5-nov-2026)

**Qué se hizo:** `empleo_formal` y `desempleo_larga_duracion` no tienen un EpF fijo en la tabla. `parametros.py` da los precios unitarios (aporte a pensión y `costo_desocupado(edad, mujer)`), y el 05 suma el costo de cada persona del hogar según los tres casos del informe §6.5.

**Por qué:** el costo depende de quién es cada persona (ocupado sin pensión, desocupado joven, mujer en edad de pensión...). Un solo precio por hogar no lo puede representar.

## P5. La malla de B queda vacía por ahora (5-nov-2026)

**Qué se hizo:** `MALLA_B = None`.

**Por qué:** los rangos viejos ($0.50 y $7.29 billones) se calcularon con costos que ya cambiaron. La malla se fija después de calcular con los datos el costo mínimo de sacar a los 523 hogares (validación 2 del plan). Escribir números ahora sería escribirlos a ojo.

## P6. `resumen_ipm()` y `puntaje()` pasan a `utils_dane.py` (5-nov-2026)

**Qué se hizo:** la fórmula de H, A y M0 que vivía dentro de `04_linea_base.py` pasó a `utils_dane.resumen_ipm(p, puntaje, k)`, y el redondeo del puntaje a `utils_dane.puntaje(M, w)`. El 04 ahora importa esas funciones y los pesos de `parametros.py`.

**Por qué:**
- Python no puede importar `04_linea_base.py` porque su nombre empieza por un dígito. Sin moverla, el Modelo 1 tendría que copiar la fórmula, y dos copias pueden terminar diciendo cosas distintas.
- La misma función sirve antes de intervenir (línea base) y después de resolver (recalcular H, A y M0 desde x_ij). Así se cumple la regla de no confiar en el valor del objetivo.
- Recibe el puntaje y calcula quién es pobre con `>= k`, en vez de recibir una columna `POBRE` ya hecha: después de intervenir esa columna no existe.

**Verificación:** la salida completa del 04 es idéntica antes y después del cambio (comparada con `diff`). El ejemplo de 10 personas del informe §3.3 da H = 0.20, A = 0.60 y M0 = 0.12.

## P7. Modelos 1 y 2 comparten una clase madre (decidido por Martín, 5-nov-2026)

**Qué se hará:** `modelo_base.py` con la clase `ModeloIPMBase(datos, esc)`. `construir()` sigue siempre el mismo orden (patrón *template method*): `crear_variables()` (x, y, z, t, v), `agregar_reglas_intervencion()` (salida, E-2, E-3, E-7, rezago, inasistencia, logro y analfabetismo), `agregar_restricciones_propias()` y `definir_objetivo()`. Los dos últimos los escribe cada hija. La clase madre también tiene `costo_total()`, `agregar_sevedu(rho_e)`, `resolver()`, `solucion()` y `recalcular()`.
- `Modelo1(ModeloIPMBase)`, en `modelo1.py`: presupuesto, equidad por zona, tangentes, techo de severidad, techo de SevEdu y las dos etapas.
- `Modelo2(ModeloIPMBase)`, en `modelo2.py` (hilo del Modelo 2): C_i, censura, meta de M0 por zona y mínimo costo.

**Por qué:** las reglas que traducen el IPM y las estrategias educativas a restricciones son las mismas en los dos modelos. Si cada uno las copiara, un arreglo en uno podría no llegar al otro y los resultados dejarían de ser comparables. SevEdu queda como método aparte porque en el Modelo 2 solo es sensibilidad.

## P8. Todo el código pasa a `Modelos/` (decidido por Martín, 5-nov-2026)

**Qué se hizo:**
- `parametros.py`, `utils_dane.py`, `02_validar_ipm.py`, `03_preparar_antioquia.py` y `04_linea_base.py` pasaron de la raíz a `Modelos/`. Lo común a los dos modelos (`05_conteo_personas.py`, `datos_modelo.py`, `modelo_base.py`) también irá ahí; lo del Modelo 1 en `Modelos/Modelo_1/` y lo del Modelo 2 en `Modelos/Modelo_2/` (Martín quitó el espacio de los nombres el mismo día).
- `data/`, `docs/` y `graphify-out/` se quedan en la raíz.
- `utils_dane.py` arma las rutas desde su propia ubicación: `RAIZ = Path(__file__).resolve().parents[1]`. El 04 lee el CSV desde `utils_dane.OUT`. Así los scripts funcionan sin importar desde qué carpeta se corran.
- Los scripts numerados de `Modelo_1/` y `Modelo_2/` empiezan con `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))` para importar lo común. Es la misma convención que usa el hilo del Modelo 2.
- Se actualizaron el mapa del código de `CLAUDE.md` y las rutas de `.claude/rules/modelos_milp.md`.

**Por qué el `sys.path`:** sin espacio, `Modelo_1` y `Modelo_2` ya se pueden importar como paquetes desde `Modelos/` (`from Modelo_1.modelo1 import Modelo1`). Pero un script que se corre directamente (`python Modelos/Modelo_1/08_modelo1.py`) solo ve su propia carpeta, así que agrega `Modelos/` al path para encontrar `parametros.py` y `modelo_base.py`. En PyCharm también se puede marcar `Modelos/` como *Sources Root*.

**Por qué `mv` y no `git mv`:** desde aquí git no puede borrar sus archivos de bloqueo. Cuando hagas el commit con `git add -A`, git detecta el movimiento como un *rename* porque el contenido es casi igual, así que el historial de cada archivo se conserva.

**Verificación:** la salida de `04_linea_base.py` es idéntica a la de antes, corrida desde la raíz y desde `Modelos/`; la de `parametros.py` también. 02 y 03 compilan. Desde `Modelos/Modelo_1/` se importan `parametros` y `utils_dane` sin error.

## P9. Paso 3.3: conteo por persona (05_conteo_personas.py)

- **Qué decidí:** el 05 produce cinco tablas (conteo_pares, ninos, adultos_clei, logro_hogar, empleo_componentes) con el conteo físico de personas; los costos y coeficientes SevEdu se calculan después en datos_modelo.py.
- **Por qué:** así el 05 no depende del escenario (E3, ρ_e, sensibilidades) y se puede reusar en el Modelo 2.
- **Validación:** la parte 1 reproduce el indicador del hogar (HOGARES) con 99.67 %–100 %; la parte 2 reproduce 215 niños, 83/47/27/26/32, 160/55, E-7 = 29 y SevEdu^N = 21,562.
- **D6. 32 hogares y no 33 en logro (DECIDIDO por Martín, 6-nov):** con la regla "el adulto no asiste, tiene 8 años o menos y hace un ciclo CLEI al año" salen 32 hogares que pueden salir de logro, no los 33 de costos/logro_educativo_analisis.md. En 5 hogares la brecha es de 1 año y en 3 de ellos el adulto que falta (15–17 años) asiste a la escuela, así que no es elegible a CLEI. No se pudo confirmar qué regla dio el 33; probablemente el análisis contó a esos jóvenes. **Se deja 32** porque respeta que quien ya estudia no se matricula en CLEI (el CLEI cuenta como asistencia, D2). El 33 del análisis queda como cota superior no reproducida.
- **u_ij imputados:** 219 de 2,592 filas de hogares pobres (218 en desempleo de larga duración, 1 en empleo formal). Son hogares sin adulto identificable en el caso, y se les asigna 1 persona con el aporte a pensión (COSTO_APORTE_PENSION, fuente aún pendiente).
- **Pregunta pendiente:** 14 hogares pobres sin ocupados con desocupados (posible doble conteo en el caso 3 de empleo).

## D7. Caso 3 de empleo formal: los desocupados no pagan el aporte a pensión (DECIDIDO por Martín, 6-nov)

- **Problema:** en un hogar sin ocupados (caso 3), el 05 cobraba el aporte a pensión ($2,733,120) a todo adulto sin cobertura. Eso incluía a los desocupados, que además pagan su costo de formalización (EpV, informe §6.5) dentro de empleo formal. El mismo adulto pagaba dos veces.
- **Decisión:** `n_caso3` cuenta solo a los adultos de 15 años o más sin cobertura que no son desocupados (`n_sin_cob_no_desoc`). El desocupado queda cubierto con su EpV.
- **Efecto:** no cambia qué hogares están privados, así que la validación contra el DANE queda igual (empleo 99.666 %). Cambia 66 hogares en total, de los cuales 14 son pobres. En los 14 pobres se quitan 16 personas y el costo con factor de expansión baja unos $40,507 millones.
- **Dónde:** `empleo_por_hogar()` en `Modelos/05_conteo_personas.py` (nueva columna `n_sin_cob_no_desoc`).

## P10. Paso 3.4: datos_modelo.py

- **Qué hace:** `cargar_datos(escenario)` lee los CSV del 03 y del 05 y devuelve un objeto `Datos` con los conjuntos y parámetros de la formulación (I, J_i, c_ij, A_i, M_i, Sev0, K, N, estrategias, c_ks, coef_ks, E-7, Renta Ciudadana, adultos y déficit D_i). No resuelve nada. Modelo 1 y Modelo 2 solo leen este objeto.
- **Por qué un solo objeto:** el MILP no repite lecturas ni cálculos y los dos modelos usan exactamente los mismos números.
- **Costos:** los indicadores simples (vivienda, salud, atención integral, trabajo infantil) se recalculan con `tabla_epf(escenario)` por u_ij y HW, para que las sensibilidades (acueducto BID, trabajo infantil psicosocial) cambien el costo. Empleo formal y desempleo toman el costo por persona del 05.
- **`quitable[(i, j)]`:** marca las privaciones que no se pueden quitar este año. Así el modelo ni crea esas variables x. Logro: solo si los años que ganan los adultos elegibles cubren D_i (32 hogares). Analfabetismo: solo si todos los analfabetas del hogar ganan algo con un ciclo (305 de 315). Rezago: ninguno (formulación (10b)). Inasistencia: 38 de 39.
- **Hogar 8419308_1:** el DANE lo marca con inasistencia y el 05 no identifica a ningún niño que no asista. Como no se sabe a quién pagar, no es quitable. Es parte de la brecha de 0.031 % de la validación de inasistencia.
- **Escenario u = 1:** `cargar_datos` lanza `NotImplementedError`. Se programa en el paso 3.7 (barridos).
- **Rango de B:** no se calcula aquí. Necesita resolver el MILP (costo mínimo de sacar a los hogares), así que va en 3.6/3.7.
- **Regresión (caso base):** 523 pobres, M0 = 0.038684, Sev0 = 117,908, SevEdu = 21,562, 4.96 privaciones por hogar, 6,571 puntos de tangente, 215 niños en 149 hogares, 29 con E-7, ningún par con d_ks > b_k.

## P11. Paso 3.5a: clase madre ModeloIPMBase (modelo_base.py)

- **Qué hace:** reúne lo que comparten los Modelos 1 y 2: variables (x, y, z, t, v), la regla de salida (2), las reglas educativas (E-2, E-3, E-7, 10a, Inas, 11, 12), `costo_total()`, `agregar_sevedu()`, `resolver()`, `solucion()` y `recalcular()`. `construir()` es la plantilla: llama a los pasos comunes y a tres ganchos que escribe cada hija (`sentido`, `agregar_restricciones_propias`, `definir_objetivo`). La madre no agrega presupuesto ni objetivo.
- **Variables fijas:** x existe para toda privación del hogar. Si no es quitable queda como entera con cotas 0..0, porque en PuLP `cat="Binary"` ignora `upBound` (hallazgo del hilo del Modelo 2, F3-9). Así los nombres de las variables no cambian entre escenarios.
- **z solo donde hay elegibilidad:** E-1 (legalidad) queda implícita en que la variable no existe. t_i solo en hogares donde algún niño puede volver con E1.
- **`costo_total()` en pesos:** el Modelo 1 lo usa tal cual en el presupuesto; el Modelo 2 lo divide entre 1e6 en su objetivo (F2-1).
- **`recalcular()` es una cuenta independiente:** no lee y_i del MILP; vuelve a calcular el puntaje de cada hogar con las x y aplica la regla del DANE. Así detecta un modelo mal formulado. Da H, M0 (de todo Antioquia, con los 3,732 hogares), severidad, SevEdu y costo, por zona y total. Para eso `Datos` guarda ahora `todos` (p, c0, P3 de los 3,732 hogares).
- **Solver:** `pulp.HiGHS(msg, gapRel, timeLimit)` con PuLP 3.3.2. Tolerancia por defecto 1e-4 y 300 s; cada hija pasa la suya (el Modelo 2 usa 1e-6).
- **Prueba:** `Modelo_1/prueba_3_5a.py` usa una hija mínima (max personas que salen con B = $300 mil millones). Resultado: 2,592 x (631 fijas en 0), 523 y, 56 z, 894 v, 38 t; 523 Sal, 29 E7, 49 E3 (Renta), 5 E2, 49 Inas, 32 Log, 362 Analf. El MILP resuelve en 0.5 s y `recalcular()` coincide con el MILP en personas que salen (497,142), hogares (278) y costo ($299,999,996,337). Se corrió en el contenedor de la nube con PuLP 3.3.2 porque la máquina virtual del PC no tiene PuLP ni acceso a PyPI.

## P12. Paso 3.5b-1: Modelo1, capa 1 (presupuesto y max H)

- **Qué hace:** `Modelo_1/modelo1.py` define `Modelo1(ModeloIPMBase)` con solo dos cosas propias: el presupuesto (1), `costo_total() <= B`, y el objetivo `max sum p_i y_i`. Las capas 2 a 5 (equidad, severidad, SevEdu, dos etapas) se activan con los argumentos `r`, `rho`, `rho_e` y `etapa`. Mientras no estén programadas, pedirlas lanza `NotImplementedError`, para que nadie las use creyendo que ya existen.
- **Por qué por capas:** si una capa falla, se sabe cuál. Cada capa se prueba contra un cálculo hecho por otro camino antes de agregar la siguiente (Fase 2, orden de capas).
- **Prueba contra enumeración exacta:** en 50 hogares al azar, con solo las privaciones simples quitables y sin E-7, el óptimo se calcula sin MILP: por hogar, el subconjunto más barato de privaciones que lo deja en 0.33 o menos, y una mochila 0/1 entre hogares con costos redondeados hacia arriba y hacia abajo (cota inferior y superior de H). Resultado: en 3 muestras y 2 presupuestos cada una, el MILP coincide con las dos cotas (6 de 6 OK).
- **Herramienta nueva:** `datos_modelo.subconjunto(datos, ids)` devuelve una copia con solo esos hogares (niños, adultos, costos y reglas incluidos). Sirve para probar cada capa en instancias pequeñas.

## P13. Paso 3.5b-2: Modelo1, capa 2 (equidad por zona)

- **Qué hace:** con `r > 0`, `Modelo1` agrega una restricción `Eq_<zona>` por cada zona P3: `sum_{i en zona} p_i y_i >= r * Pobres_zona`. Con `r = 0` no agrega nada. Es la restricción (4) de la formulación.
- **Por qué por zona y con y_i:** que ninguna zona, sobre todo el rural disperso (el más caro), quede abandonada. Cuenta personas que salen, no hogares.
- **Prueba contra enumeración total:** con 18 hogares (6 por zona) se enumeran los 2^18 conjuntos de hogares que salen, cada uno pagando su costo mínimo de salida (solo privaciones simples). Se compara el mejor H que cumple presupuesto y equidad con el MILP. En 3 muestras y 4 combinaciones de (r, B) cada una (12 casos), el MILP coincide con la enumeración: 7 casos óptimos con el mismo valor y 5 infactibles en los dos (r imposible con ese B).
- **Qué no prueba:** la combinación con las reglas educativas reales (E-7, Inas, 11, 12), que ya se probaron en 3.5a. La capa 2 solo depende de y_i y de `pobres_zona`.

## P14. Paso 3.5b-3: Modelo1, capa 3 (severidad: q, tangentes y techo)

- **Qué hace:** con `rho` distinto de None, agrega q_i >= 0 por hogar, las tangentes (7) `q_i >= 2a*s_i - a^2` para cada a en A_i, y el techo (8) `sum p_i q_i <= (1 - rho) * Sev0`.
- **Por qué las tangentes son exactas:** s_i solo toma valores en A_i (sumas de pesos de subconjuntos de sus privaciones) y s^2 es convexa. En cada valor alcanzable, el máximo de las tangentes vale exactamente s_i^2. El techo empuja q hacia abajo hasta ese máximo. Son 6,571 filas en total para los 523 hogares.
- **Nombre de las filas:** `Tan_<hogar>_<centésimas>` (por ejemplo `Tan_8422901_1_34`), sin puntos decimales.
- **Prueba contra enumeración:** 9 hogares por muestra y solo privaciones simples quitables. Cada hogar elige un puntaje final con su costo mínimo; se combinan con poda por presupuesto y por techo y se toma el mayor H. En 3 muestras y 8 combinaciones de (rho, B), 24 casos, el MILP coincide en todos: 21 óptimos con el mismo valor y 3 infactibles en los dos (rho = 0.6). En un caso el techo recorta H de 13,067.8 a 12,046.6 con el mismo presupuesto, así que la restricción sí discrimina. También se verificó que q_i >= s_i^2 en todos los hogares de una solución.
- **Primera versión de la prueba:** no discriminaba (presupuestos muy holgados, el techo nunca mordía). Se rehizo con presupuestos medidos contra el costo mínimo de salida y rho hasta el límite factible.

## P15. Paso 3.5b-4: Modelo1, capa 4 (techo de SevEdu)

- **Qué hace:** con `rho_e` distinto de None, `Modelo1` llama a `agregar_sevedu(rho_e)` de la clase madre: `sum coef_ks z_ks >= rho_e * SevEdu^N`. La restricción vive en la madre porque el Modelo 2 también la usa como sensibilidad (F2-4); cada hija decide si la llama.
- **Prueba contra enumeración:** hogares con niños que pueden recibir E1 o E2; solo las privaciones simples quedan quitables, para que la educación entre al modelo por tres vías: E-7, el gasto (cupo o ciclo, más la Renta Ciudadana una vez por hogar) y el techo de SevEdu. Exacto sin MILP: se enumeran las estrategias de los niños de cada hogar respetando E-7, se combinan los hogares guardando los planes con SevEdu suficiente, y lo que sobra del presupuesto se gasta en sacar hogares (mochila con costos redondeados hacia arriba y hacia abajo). En 3 muestras y 9 combinaciones de (rho_e, B), 27 casos, el MILP quedó siempre entre las dos cotas y la infactibilidad coincidió.
- **El techo sí muerde:** en la muestra 2, con B = $150.2 mil millones, H pasa de 18,602.0 (rho_e = 0.2) a 17,621.1 (rho_e = 0.3): para cumplir el techo hay que gastar más en educación y sobra menos para sacar hogares.
- **Cuándo falla por diseño:** rho_e muy alto es infactible (por ejemplo 0.9 o 0.4 en la muestra 2): los niños con estrategia elegible no alcanzan a reducir tanto SevEdu. En el caso real, el 14 % del caso base se alcanza con E-7 más el cupo de los no asistentes (decisión de Martín, 2-nov).

## P16. Paso 3.5b-5: Modelo1, capa 5 (dos etapas, D1)

- **Qué hace:** `Modelo1(etapa=1)` maximiza H. `Modelo1(etapa=2, H_star=H*)` minimiza `sum p_i q_i` con `sum p_i y_i >= H* (1 - 1e-6)` (restricción `H_min`), con el mismo presupuesto, equidad y techos. `resolver_dos_etapas(datos, B, ...)` corre las dos y devuelve el modelo de la etapa 2 y un diccionario con la información de cada etapa y H*.
- **Por qué dos etapas y no un λ pequeño (D1, Martín, 4-nov):** con λ el desempate cuesta unas 35 personas, y la tolerancia de HiGHS (gap 1e-4) equivale a unas 68; el solver puede "comerse" el desempate. En dos etapas la tolerancia no afecta el segundo objetivo. H* es el valor de la solución incumbente de la etapa 1.
- **q en la etapa 2:** se crea aunque no haya techo (`rho = None`), porque el objetivo la necesita. El techo (8) solo se agrega si hay `rho`.
- **Prueba contra enumeración:** en las 3 instancias de 9 hogares y 5 combinaciones de (rho, B) (15 casos): el MILP en dos etapas coincide con la enumeración tanto en H como en la severidad mínima entre los planes con ese H. En la muestra 3 la etapa 1 sola dejaba severidad 1,201.6 y la etapa 2 la baja a 893.4 con el mismo H, así que el desempate sí hace algo.
- **Regresión:** las pruebas de las capas 1 a 4 y la de la clase madre se volvieron a correr después del cambio y siguen en OK.

## P17. Paso 3.6: 08_modelo1.py y rango de B

- **Qué hace:** `08_modelo1.py` corre el Modelo 1 con los 523 hogares reales: carga los datos del escenario, calcula el rango útil de B, resuelve en dos etapas, recalcula con la cuenta independiente del DANE y guarda CSV en `data/processed/modelo1/` (`resumen`, `plan_hogar`, `plan_nino`, `plan_adulto`). Argumentos: `--B` (en mil millones de pesos), `--r`, `--rho`, `--rho-e`, `--sin-sevedu`, `--una-etapa`, `--escenario`, `--gap`, `--tiempo`. Sin `--B` usa el punto medio del rango.
- **Rango de B (`rango_B` en modelo1.py):** B_min es el gasto forzoso (cobertura obligatoria E-7 más el techo de SevEdu); por debajo el modelo es infactible. B_max es el menor B con el que sale todo lo que puede salir (H máximo), por bisección con tolerancia de 0.1 %. Se calcula sin equidad ni techo de severidad. Con los costos nuevos y el caso base (rho_e = 14 %): **de $105.9 a $662.5 mil millones, H máximo = 683,406 personas** (todos los pobres: los 523 hogares pueden salir).
- **Chequeo con un número anterior:** el gasto forzoso de $105.9 mil millones coincide con el "ρ_e 14 % ($105.8 mm)" que quedó en la memoria del proyecto el 2-nov (cobertura 6–15 más 14 %). Un buen indicio de que el 05 y datos_modelo no cambiaron ese costo.
- **Tiempos con los 523 hogares reales:** una corrida típica (B = $384 mil millones, r = 0.2, rho = 0.1, rho_e = 0.14) tarda 1.8 s la etapa 1 y 2.5 s la etapa 2, con gap menor a 1e-4. El caso más duro probado (rho = 0.5) tarda 6 s y 13 s.
- **Resultado de ejemplo (no es un resultado final del proyecto):** con B = $384.2 mil millones, r = 20 %, rho = 10 % y rho_e = 14 % salen 564,440 personas (361 hogares), M0 baja de 0.0387 a 0.0073 (−81 %), la severidad baja 41.7 % y SevEdu 14.0 %. Todos los chequeos del script dan OK. Los números definitivos salen del barrido de 3.7.
- **Dónde se corrió:** en el contenedor de la nube con PuLP 3.3.2 (la máquina virtual del PC no tiene PuLP). Martín debe correrlo en PyCharm con su `.venv`.

## P18. Paso 3.7: 08_modelo1_barridos.py

- **Qué hace:** barre B, rho, r, rho_e y las sensibilidades, cada fila en dos etapas con los 523 hogares, y guarda CSV en `data/processed/modelo1/` (copia de los agregados en `/mnt/project-files/modelo1/resultados/`). Tarda unos 4 a 8 minutos en total.
- **MALLA_B:** 8 puntos entre B_min × 1.02 y B_max (el 2 % evita el borde infactible). `MALLA_B` en `parametros.py` queda en None y se calcula con `rango_B()`. Con los costos del 4-nov: B_min $105.9 y B_max $662.5 mil millones.
- **Hallazgo 1, rho (B de referencia $384.2 mil millones):** maximizar H ya baja la severidad 41.7 %. Exigir menos que eso no cambia nada. El techo empieza a morder desde 41.7 % y el máximo posible con ese B es 48.0 %; entre ambos H baja de 564,443 a 518,616 personas. El codo (Kneedle, solo en ese tramo) cae en rho = 46.3 % (550,519 personas). Una primera versión del barrido tomaba la malla desde 0 con gap 1e-4 y daba un codo falso en 11.9 % porque la curva es plana y el gap equivale a unas 56 personas; se corrigió empezando la malla en 41.7 % y usando gap 1e-6 en este barrido.
- **Hallazgo 2, r:** con B de referencia, exigir que salga 5 %, 10 %, 15 % o 20 % en cada zona no cambia nada, porque el óptimo ya saca 70 % o más de cada zona. Solo muerde desde r = 0.7 y r = 0.9 es infactible. La MALLA_R de parametros (hasta 20 %) no es informativa con este B; se prolongó con 0.3, 0.5, 0.7, 0.8 y 0.9. Para ver el efecto de la equidad hace falta un B más bajo o r más alto.
- **Hallazgo 3, rho_e:** de 0 a 11.8 % da el mismo H (la cobertura obligatoria E-7 ya reduce SevEdu 11.8 %, igual que la nota del 1-nov); subir a 14 % cuesta 1,142 personas (0.2 %). Sin E3, rho_e de 17 % o más es infactible (el costo mínimo de 16 % es $159.4 mil millones). Con E3 sí es factible hasta 21 % y falla en 21.2 %, igual que la nota del 1-nov ("máximo 21.2 % con reglas oficiales"). Es una coincidencia independiente con un cálculo anterior.
- **Hallazgo 4, sensibilidades:** más cumplimiento de Renta Ciudadana sube H (p = 0.50: 576,975; p = 0.75: 588,501 personas, contra 564,443 del caso base). Con E3 y rho_e = 20 %: 591,356. Trabajo infantil psicosocial: 568,349. El acueducto rural de BID no cambia nada porque el óptimo no quita el acueducto rural en ningún hogar, ni con el costo base ni con 22 % de ese costo (comprobado). La sensibilidad u = 1 sigue sin programar.
- **Pendiente para la auditoría:** el "salen_personas" recalculado puede superar en unas pocas personas al objetivo del MILP, porque un hogar con y_i = 0 puede quedar igual en 0.33 o menos al quitar otras privaciones.

## D8. Desempleo de larga duración sin desocupado identificado: no se quita en el caso base (DECIDIDO por Martín, 7-nov, consejo del auditor H5)

- **Problema:** en 218 de los 226 hogares pobres privados en desempleo de larga duración, el 05 no identifica a ningún desocupado y imputa una persona con la tarifa más alta de Empleos para la Vida (30 %, $5.12 M). La tarifa tiene fuente (Decreto 533 de 2024); la persona no.
- **Decisión:** si no se sabe a quién pagar, la privación no se quita, igual que inasistencia (P10, hogar 8419308_1). En `datos_modelo.py`, `quitable[(i, "desempleo_larga_duracion")]` es False cuando el u_ij está imputado y `esc["desempleo_imputado"]` es False. Quedan quitables 8 de 226.
- **Sensibilidad:** `desempleo_imputado` en `parametros.SENSIBILIDADES` (`desempleo_imputado = True`) conserva la imputación anterior.
- **Efecto medido (gap 1e-6, rho_e = 14 %):** sin cambio con B hasta $266 mil millones; con $384.2 mil millones sale H = 563,505.7 (363 hogares) en vez de 564,439.1; con $504 mil millones, 628,855.2 en vez de 636,582.4 (−1.2 %). El H máximo no cambia (683,406), pero el B para lograrlo sube de $662.5 a $742.1 mil millones. B_min sigue en $105.9.
- **Por qué:** la regla de Martín de usar solo información 100 % segura, y coherencia interna: una privación con persona desconocida no se puede quitar en inasistencia pero sí en desempleo.
- **Lo que queda sin verificar:** por qué el DANE marca 226 hogares y el 05 ve desocupados en 8; puede ser que la definición del indicador en la ECV 2025 sea distinta de la del 05. Empleo formal tiene 1 hogar con u_ij imputado, que no se tocó porque la decisión fue solo sobre desempleo.
- **Dónde:** `parametros.py` (CASO_BASE y SENSIBILIDADES), `datos_modelo.py` (campo `imputados` y regla de `quitable`; el chequeo de regresión espera 8 quitables).

## P19 — Fase A de la auditoría: estado del solver y gap por defecto (7-nov-2026, luz verde de Martín)
- **H1.** PuLP devolvía "Optimal" aunque HiGHS se cortara por tiempo (sol_status 2 = factible, no probado). Ahora `resolver()` reporta estado **"Cortado"** cuando status=Optimal pero sol_status ≠ óptimo; `resolver_dos_etapas` no pasa un H* sin demostrar a la etapa 2. Evidencia: ρ=0.47, límite 1 s → "Cortado", gap 7.6 %.
- **H2.** Gap relativo por defecto 1e-4 → **1e-6** (`ModeloIPMBase.GAP_REL`). Con 1e-4 la tolerancia equivalía a ~56 personas de ruido. Evidencia: H con r=0, 0.05 y 0.5 (no muerde) = 563,505.7 en los tres.
- 08_modelo1.py y 08_modelo1_barridos.py: `--gap` por defecto 1e-6; el barrido aborta si no puede calcular ρ máximo.
- Prueba nueva: Modelo_1/prueba_faseA.py. Pruebas 3.5a y 3.5b1–b5 siguen sin fallas.

## P20 — Fase B de la auditoría: A, regla de la brecha y equidad donde muerde (7-nov-2026, luz verde de Martín)
- **H4.** `recalcular()` ahora devuelve también A0; los barridos guardan A, A0 y `brecha_no_crece` (A ≤ A0). El barrido de ρ imprime la regla de la brecha (criterio principal) y el codo Kneedle (contraste). Con B de referencia = $424.0 mil millones (punto medio del rango tras D8: $105.9–$742.1): sin techo A = 0.436 > A0 = 0.409; la regla se cumple desde **ρ = 47.5 %** (582,187 personas, A = 0.4083); codo en 48.2 % (577,347). Ambos criterios caen en la misma zona. ρ libre (sin exigir nada) = 44.9 %.
- **H3.** El barrido de r se repite con B de referencia y tres B bajos (1.2·B_min = $127.1, $130 y $187 mil millones), con r hasta 0.25, 0.30 y 0.50. Con B de referencia r no muerde (H igual para todo r). Con B bajo sí: en $127.1, r = 0.20 cuesta 578 personas (0.27 %) y r = 0.25 cuesta 11,115 (5.2 %); r ≥ 0.30 infactible. En $130: r = 0.20 cuesta 58 personas y r = 0.25 cuesta 5,591. En $187: r ≤ 0.30 casi gratis, r = 0.50 infactible.
- Todos los barridos se re-corrieron con D8 y gap 1e-6 (resultados en modelo1/resultados/).
- **Pendiente de decisión de Martín:** fijar ρ y r en el caso base (no se hizo; ρ depende de B).

## P21 — ρ del caso base por la regla de la brecha; codo y "sin penalizaciones" como sensibilidades (9-nov-2026, decisión de Martín)
- **Decisión de Martín (9-nov):** el techo de severidad ρ del caso base es el menor ρ con A ≤ A0 (regla de la brecha: quienes siguen pobres no quedan, en promedio, más pobres que hoy). El codo Kneedle queda como sensibilidad. También queda como sensibilidad el modelo "sin penalizaciones" (ρ = 0, r = 0 y sin techo de SevEdu; aclarado por Martín el 9-nov) para comparar con lo que se obtendría sin lo que el proyecto propuso. La decisión de r sigue PENDIENTE (caso base r = 0 provisional; propuesta 0.20).
- **Implementación:** `rho_regla_brecha()` en Modelo_1/modelo1.py (bisección con tolerancia 0.001 entre el ρ "libre" y el máximo posible; devuelve None si no se alcanza). `parametros.CASO_BASE`: `rho = "brecha"`, `r = 0.0`; `parametros.POLITICAS`: rho_codo y sin_penalizaciones (ρ = 0, r = 0, ρ_e = ninguno; queda solo E-7). `08_modelo1.py`: `--rho` acepta número, `brecha` o `ninguno`.
- **Prueba (`Modelo_1/prueba_faseB.py`):** con B = $424 mil millones, ρ = 47.43 %: A = 0.4076 ≤ A0 = 0.4094; con ρ − 0.003, A = 0.4126 > A0. Cada sensibilidad de datos recalcula su propio ρ.
- **Resultados (B = $424 mil millones, `barrido_sensibilidades.csv`):** base 582,604 personas (ρ 47.4 %); codo ρ 48.2 % → 577,343 (A = 0.396); sin penalizaciones (también sin techo de SevEdu) 592,196 (A = 0.4399 > A0, la brecha crece; SevEdu baja 11.8 %). Costo de la regla frente a H puro: 9,592 personas (1.6 %).

## P22 — Barrido fino de r para hallar el codo (9-nov-2026, pedido de Martín)
- **Por qué:** la malla de r era gruesa (0.20, 0.25, 0.30) justo donde H empieza a caer. Se corrió r de 0.15 a 0.30 de a 0.01 con tres presupuestos bajos (script nuevo `08_modelo1_barrido_r_fino.py`; CSV `barrido_r_fino.csv`).
- **Resultados:** codo (Kneedle) en r = 0.21 con B = $127.1 mil millones (cuesta 1,159 personas, 0.5 %) y r = 0.22 con B = $130 mil millones (cuesta 639, 0.3 %). Con B = $187 mil millones r no muerde (todas las zonas ya salen ≥ 40 %), la curva es plana y el "codo" (0.27) no significa nada. r factible máximo: 0.26 ($127.1), 0.28 ($130), > 0.30 ($187).
- **Lectura:** hasta r = 0.20 la equidad cuesta menos de 600 personas (0.3 %) en ambos presupuestos; desde 0.21–0.22 el costo se acelera (a r = 0.25 cuesta 11,100 con $127.1 y 5,600 con $130). Con r activo, la zona rural queda exactamente en r.
- **Pendiente de decisión de Martín:** valor de r del caso base (propuesta 0.20, por debajo de ambos codos).

## P23 — r = 0.20 en el caso base (9-nov-2026, decisión de Martín; justificación pedida por Martín)
**Qué es r:** piso de equidad territorial. En cada una de las 3 zonas (cabecera, centro poblado, rural disperso) debe salir de pobreza al menos el 20 % de sus pobres iniciales: Σ_{i∈zona} p_i y_i ≥ 0.20 · Pobres_zona (restricción (4)).

**Por qué 0.20 (evidencia: `barrido_r.csv`, `barrido_r_fino.csv`, P20 y P22):**
1. **Se mide donde r actúa.** Con B de referencia ($424 mil millones) r no cambia el resultado (todas las zonas ya superan 79 %); por eso se barrió con presupuestos bajos ($127.1, $130 y $187 mil millones), donde sin r el rural queda abandonado (16.3 % de sus pobres frente a 44.8 % en cabecera con $130).
2. **Casi gratis hasta 0.20.** Con r = 0.20 H baja 578 personas (0.27 %) con $127.1 mil millones y 58 (0.03 %) con $130. Con r ≤ 0.16 no cambia nada.
3. **Después el costo se acelera.** r = 0.21 → 1,159 / 92; r = 0.22 → 2,785 / 639; r = 0.25 → 11,115 / 5,591 personas (5.2 % / 2.5 % de H).
4. **Antes de los codos.** El codo (Kneedle) de H contra r cae en 0.21 ($127.1) y 0.22 ($130); 0.20 es el último valor redondo antes de la caída. Con $187 mil millones la curva es plana (r no actúa) y no hay codo.
5. **Garantía real de que el rural sale.** Con r activo, la zona rural queda exactamente en r (20 %), frente a 16.3 % sin él. A r = 0.20 el rural pasa de 16.3 % a 20.0 % con $130 mil millones.
6. **Margen de factibilidad.** El máximo factible es r = 0.26 ($127.1) y 0.28 ($130); 0.20 deja margen de 6 a 8 puntos. Valores ≥ 0.30 son infactibles con presupuestos bajos.
7. **Es un número simple y defendible:** "ninguna zona queda con menos de 1 de cada 5 de sus pobres fuera de pobreza".

**Limitación declarada (verificada el 9-nov):** r = 0.20 es **infactible con B menor que ≈ $119.2 mil millones** (rango útil de B: $105.9–$742.1). Con B = $120 mil millones sí es factible pero baja H de 187,157 a 162,353 personas (13 %); con $125 mil millones baja 2,295 (1.1 %). Es decir, en el tramo más bajo del rango (B entre $105.9 y $125 mil millones) r = 0.20 se vuelve una restricción que muerde fuerte o hace el problema infactible. En el resto del rango (B ≥ $127 mil millones) es casi gratis. Los barridos de B (`barrido_B.csv`) se corren sin equidad; el caso base con r = 0.20 solo es válido para B ≥ $119.2 mil millones.

**Qué no es r:** no reparte el presupuesto por zonas ni iguala resultados; solo fija un mínimo. Sensibilidades de r propuestas: 0.10 y 0.25.

**Verificación:** caso base con B = $424 mil millones, r = 0.20 y ρ por la regla de la brecha (47.4 %): 582,604 personas, igual que con r = 0; zonas 89.0 %, 87.4 %, 79.2 % ≥ 20 % OK.

## P24 — r del caso base = codo de la curva H contra r de cada corrida (9-nov-2026, decisión de Martín)
- **Decisión de Martín (9-nov):** r no es un número fijo (se descarta r = 0.20, P23): es el codo de la curva H contra r para el B de la corrida. Los casos de presupuesto alto, donde el codo es débil, quedan en `mejoras/mejoras_modelo.md` §11. Criterio: ningún parámetro sin respaldo calculado de los datos.
- **Rango (todo sale de los datos):** inicio = piso libre (el menor % de pobres que sale en una zona con r = 0; por debajo de ese r la restricción no actúa); fin = el mayor r factible (bisección, tolerancia 0.005). Entre ambos, 12 puntos de r (sin techo de severidad) y codo Kneedle de H contra r.
- **Orden de cálculo en la corrida base:** primero r (curva sin techo de severidad), luego ρ por la regla de la brecha usando ese r, luego la corrida en dos etapas. Implementación: `r_codo()` y `resolver_r()` en Modelo_1/modelo1.py; `CASO_BASE["r"] = "codo"`; `08_modelo1.py --r` acepta número o `codo`.
- **Resultados de la corrida base (`08_modelo1.py`, todos los chequeos OK):**

| B (mil millones) | Piso libre | r máx factible | r (codo) | ρ (regla de la brecha) | Personas que salen |
|---|---|---|---|---|---|
| $127.1 | 16.3 % | 26.1 % | 0.234 | no se alcanza (A ≤ A0 imposible a este B); se corre sin techo | 206,452 |
| $187 | 40.4 % | 49.7 % | 0.438 | 27.2 % | 332,582 |
| $424 | 80.7 % | 85.5 % | 0.833 | 47.4 % | 581,452 |

- **Costo de aplicar r y ρ a B = $424 mil millones:** 581,452 personas frente a 592,196 sin penalizaciones (10,744, 1.8 %); sin r (solo ρ) eran 582,604.
- **Limitaciones declaradas:** (i) el codo cambia con B (0.23 / 0.44 / 0.83) y con el tramo evaluado (con una malla que arrancaba en 0.15 daba 0.21 a B = $127.1); (ii) con presupuestos altos la curva es casi lineal y el codo está poco marcado (mejoras §11); (iii) a B = $127.1 la regla de la brecha no es alcanzable con r = 0.234.
- Las sensibilidades (`08_modelo1_barridos.py --solo sens`) calculan su propio r y ρ para cada escenario; hay que re-correrlas (tardan unos 50 minutos) y no se hizo.

### P24 (resultado, 10-nov): sensibilidades re-corridas con r (codo) y ρ (regla de la brecha) propios, B = $424 mil millones
(`modelo1/resultados/barrido_sensibilidades.csv`; cada escenario calcula su propio r y ρ)

| Escenario | r (codo) | ρ | Personas que salen | A (A0 = 0.409) | ¿Brecha no crece? |
|---|---|---|---|---|---|
| **base** | 0.833 | 47.4 % | 581,452 | 0.409 | sí |
| p = 0.50 | 0.850 | 48.2 % | 591,545 | 0.409 | sí |
| p = 0.75 | 0.872 | 48.9 % | 599,928 | 0.408 | sí |
| con E3 (ρ_e 20 %) | 0.871 | 49.5 % | 602,112 | 0.408 | sí |
| sin E-7 | 0.838 | 48.1 % | 587,683 | 0.409 | sí |
| desempleo imputado | 0.839 | 47.2 % | 585,762 | 0.409 | sí |
| TI psicosocial | 0.839 | 47.7 % | 585,073 | 0.408 | sí |
| acueducto BID | 0.832 | 47.4 % | 582,078 | 0.409 | sí |
| ρ por el codo (no por la regla) | 0.833 | 46.9 % | 584,201 | 0.413 | **no** |
| **sin penalizaciones** (ρ = 0, r = 0, sin techo SevEdu) | 0 | — | 592,196 | 0.440 | **no** |

- Con el r del caso base (0.833), el codo de ρ cae en 46.9 %, por debajo del umbral de la regla (47.4 %): ese ρ **no** cumple A ≤ A0 (0.413 > 0.409). Antes, con r = 0, el codo daba 48.2 % y sí cumplía. El contraste entre ρ por la regla y ρ por el codo depende del r con el que se calcule.
- Las ocho sensibilidades de datos cumplen la regla de la brecha, con ρ entre 47.2 % y 49.5 % y r entre 0.832 y 0.872. La regla cuesta entre 7,000 y 10,800 personas respecto a «sin penalizaciones».
