# Modelos 3 y 4 para el paper

Entrega de Jerónimo Vélez para integrar al borrador de Martín Quijano, según `PLAN_INTEGRACION_M3_M4.md` (rama `Contexto`, 14 de noviembre de 2026).

Cada bloque lleva el título de la sección del borrador donde se pega. Tablas, figuras y ecuaciones tienen numeración provisional (Tabla M34-1, Figura M34-1, ecuación M3.1). Todas las cifras del texto salen de los CSV de `datos_m34/`, y `cifras_m34.csv` indica para cada una el archivo y la columna de origen. Los valores de r_B, ρ_B y del Modelo 2 con meta por zona se tratan como provisionales hasta que Martín los confirme por escrito (sección 6 del plan).

---

## Resumen

Sin información individual, el Estado paga caro por focalizar. Con metas de reducción de M0 de hasta el 10 % en cada zona, focalizar solo por zona (Modelo 3) cuesta entre {{m3_ip_baja}} veces lo que costaría con información perfecta, y focalizar por zona y tipo de hogar (Modelo 4) cuesta casi lo mismo. Con un presupuesto fijo, ninguna réplica del sorteo permite garantizar en cada zona la tasa mínima de salida que el Modelo 1 cumple con información perfecta.

---

## 1. Motivación

Los Modelos 1 y 2 suponen que el Estado sabe qué privaciones tiene cada hogar. Ningún programa social trabaja así: se asigna con estadísticas territoriales o con registros como el SISBÉN, y la ejecución llega a algunos hogares privados y no a otros. Por eso la pregunta de política no es solo cuánto cuesta reducir la pobreza, sino cuánto cuesta reducirla sin saber exactamente quién es pobre. Los Modelos 3 y 4 responden esa pregunta. El Estado decide cuánta cobertura comprar en cada zona o tipo de hogar, y un sorteo decide a qué hogares les llega. La diferencia de costo frente a los Modelos 1 y 2 es el precio de la información: lo máximo que valdría la pena invertir en mejorar los sistemas de focalización antes de ampliar el presupuesto de un programa.

---

## 2. Escenarios de política modelados

### Supuestos y salvedades propios de los Modelos 3 y 4

Los Modelos 3 y 4 comparten con los Modelos 1 y 2 los datos, los costos, las reglas de qué privación se puede quitar en un año y las restricciones de equidad territorial. Agregan tres supuestos propios.

1. **El sorteo R.** Cada par (hogar, indicador) recibe un número Rᵢⱼ uniforme entre 0 y 1, fijado antes de optimizar. El hogar sale de la privación si su número queda por debajo de la cobertura que el Estado compró en su celda. Así se representan los errores de focalización: dentro de una celda, cualquier hogar privado tiene la misma probabilidad de ser atendido, sea pobre o no.
2. **Las celdas de focalización.** Una celda es el grupo de hogares al que el Estado le puede asignar una cobertura distinta. En el Modelo 3 son las tres zonas de P3 (cabeceras, centros poblados y rural disperso). En el Modelo 4 son las zonas para los bienes públicos y cuatro tipos de hogar para los bienes privados. La base del IPM no identifica municipios, así que no hay celdas geográficas más finas.
3. **Las réplicas de Monte Carlo.** Como el resultado depende del sorteo, cada configuración se resuelve con muchos sorteos distintos (100 o 30, según el criterio) y se reporta la mediana con su intervalo. El Modelo 3, el Modelo 4 y el placebo usan el mismo sorteo en cada réplica, de modo que sus diferencias son pareadas.

Dos salvedades acompañan estos supuestos. Primero, como en el paper original, el modelo elige la cobertura conociendo el resultado del sorteo de esa réplica, lo que hace optimistas las cifras de los Modelos 3 y 4. Segundo, los sorteos de un mismo hogar son independientes entre indicadores; en la práctica, un hogar que no aparece en los registros suele quedar fuera de varios programas a la vez.

### Modelo 3

**Qué sabe el Estado.** Para cada zona y cada indicador, cuántas personas están privadas y cuánto cuesta atenderlas. No sabe quiénes son.

**Qué decide.** La cobertura θ(j, d) de cada par (indicador, zona): la fracción de la población privada de la zona que el programa va a atender. El sorteo decide qué hogares reciben esa cobertura.

**Qué se fija.** Los costos por hogar e indicador, las reglas de qué se puede quitar en un año, el sorteo de cada réplica y, según el criterio, la meta m de reducción de M0 en cada zona o el presupuesto B con la tasa mínima de salida r_B en cada zona.

### Modelo 4

**Qué sabe el Estado.** Lo mismo que en el Modelo 3 y, además, el tipo de hogar, construido con rasgos demográficos que registra el SISBÉN (tamaño, edades, jefatura). Sigue sin saber quién está privado en qué.

**Qué decide.** La cobertura de cada par (indicador, celda). Los dos bienes públicos (acueducto y alcantarillado) se focalizan por zona; los otros 13 indicadores, por tipo de hogar.

**Qué se fija.** Lo mismo que en el Modelo 3, más la partición en cuatro tipos de hogar (k = 4), que se calcula una vez y no cambia entre réplicas.

### Columnas de los Modelos 3 y 4 para la Tabla 1

> **Pendiente de alinear.** No tuve acceso al borrador de Martín, así que no conozco las 11 filas exactas de su Tabla 1. Las filas de abajo son las características que distinguen a los cuatro modelos. Al integrar, cada valor se pasa a la fila del borrador que corresponda.

| Característica | Modelo 3 | Modelo 4 |
|---|---|---|
| Información hogar por hogar | N. El Estado solo conoce agregados por zona. | N. Conoce agregados por zona y el tipo de hogar, no las privaciones. |
| Unidad de focalización | Parcial. Zona: 3 celdas para los 15 indicadores. | Parcial. Zona para los 2 bienes públicos y 4 tipos de hogar para los 13 privados. |
| Componente estocástico | S. El sorteo Rᵢⱼ decide qué hogares reciben la cobertura. | S. El mismo sorteo, con las mismas réplicas que el Modelo 3. |
| Errores de inclusión y exclusión | S. Se miden en cada réplica. | S. Se miden en cada réplica. |
| Meta de reducción de M0 en cada zona | S. Criterio de costo. | S. Criterio de costo. |
| Tasa mínima de salida por zona r | S. Criterio de presupuesto fijo, con el r_B del Modelo 1. | S. Igual que el Modelo 3. |
| Techo de severidad ρ | Parcial. Solo en la sensibilidad, con el ρ_B del Modelo 1. | Parcial. Igual que el Modelo 3. |
| Cobertura escolar obligatoria (E-7) | N. Exige saber qué niño no asiste; aquí lo decide el sorteo. | N. Igual que el Modelo 3. |
| Techo de severidad educativa (SevEdu) | N. Exige decisiones niño por niño. | N. Igual que el Modelo 3. |
| Privaciones que no se quitan en un año | S. Entran como constante en el puntaje, con las reglas del Modelo 1. | S. Igual que el Modelo 3. |
| Clustering demográfico | N. | S. k-medias sobre ocho rasgos, sin usar privaciones. |

---

## 3. Métodos empíricos

### Modelo 3: formulación

**Conjuntos.**

- I: los {{hogares}} hogares de Antioquia; I⁰ ⊆ I: los {{hogares_pobres}} hogares pobres de la línea base.
- J: los 15 indicadores del IPM.
- D: las tres zonas de P3; d(i) es la zona del hogar i.
- Para cada par (j, d), los hogares privados ordenados por su sorteo: R₍₁₎ < R₍₂₎ < … < R₍ₙ₎, con n = n(j, d).
- F(j, d): los cortes admisibles del par (j, d), definidos en la ecuación M3.8.

**Parámetros.**

- Mᵢⱼ ∈ {0, 1}: privación inicial; wⱼ: peso del indicador; k = 1/3: umbral de pobreza.
- pᵢ = HSᵢ · HWᵢ: personas que representa el hogar; cᵢ⁰ = Σⱼ wⱼ Mᵢⱼ: puntaje inicial.
- uᵢⱼ: personas del hogar que hay que atender para quitar la privación; eᵢⱼ: costo de quitarla en el hogar de la muestra.
- Vᵢⱼ = uᵢⱼ · HWᵢ: población que atiende el par; Kᵢⱼ = eᵢⱼ · HWᵢ: gasto que exige el par en la población.
- Den(j, d) = Σ_{i en d} Vᵢⱼ Mᵢⱼ: población privada en el indicador j dentro de la zona d.
- Rᵢⱼ ∈ [0, 1]: sorteo del par, distinto en cada réplica.
- m: meta de reducción de M0; B: presupuesto; r_B y ρ_B: los parámetros de equidad del Modelo 1 para ese presupuesto.

**Variables.**

- xᵢⱼ ∈ {0, 1}: 1 si se quita la privación j del hogar i.
- sᵢ: puntaje final del hogar.
- yᵢ ∈ {0, 1}: 1 si el hogar sale de la pobreza (en el código, b1ᵢ).
- Cᵢ ≥ 0: contribución del hogar al M0 final (solo en el criterio de costo).
- θ(j, d) ∈ [0, 1]: cobertura del par (indicador, zona).
- E(j, d) ≥ 0: gasto en el indicador j dentro de la zona d.

**Mecanismo de cobertura.** El gasto y la cobertura de cada par son

(M3.1) E(j, d) = Σ_{i en d} Kᵢⱼ · xᵢⱼ

(M3.2) θ(j, d) = (1 / Den(j, d)) · Σ_{i en d} Vᵢⱼ · xᵢⱼ

y el sorteo decide a quién llega la cobertura:

(M3.3) xᵢⱼ = Mᵢⱼ si Rᵢⱼ ≤ θ(j, d(i)), y xᵢⱼ = 0 si Rᵢⱼ > θ(j, d(i)).

Numerador y denominador de M3.2 se miden en la misma unidad, personas de la población. En el paper original el numerador está ponderado por HWᵢ y el denominador cuenta hogares de la muestra; con esa definición la cobertura llega a {{cob_paper}} en nuestros datos, todo hogar privado se cura y el Modelo 3 se reduce al Modelo 1 sin que el solver lo advierta.

**Función objetivo (criterio de costo).**

(M3.4) min Σⱼ Σ_d E(j, d)

**Restricciones (criterio de costo).** El puntaje final es

(M3.5) sᵢ = cᵢ⁰ − Σ_{j intervenible} wⱼ · xᵢⱼ

donde las privaciones que no se pueden quitar en un año quedan como constante. Para cada hogar pobre i ∈ I⁰, la censura de Alkire y Foster se linealiza con Big-M:

(M3.6a) Cᵢ + pᵢ · yᵢ ≥ pᵢ · sᵢ

(M3.6b) Cᵢ − pᵢ · yᵢ ≤ pᵢ · sᵢ

(M3.6c) sᵢ − (1 − yᵢ) ≤ 0.33

y la meta se exige en cada zona:

(M3.7) Σ_{i ∈ I⁰, d(i) = d} Cᵢ ≤ (1 − m) · Σ_{i ∈ I⁰, d(i) = d} pᵢ · cᵢ⁰ para cada zona d.

El lado derecho de M3.7 es la contribución inicial de la zona a M0, reducida en la meta; es la misma restricción (M-d) del Modelo 2. Las tres metas por zona implican la meta global, así que cumplir la meta en cada zona nunca cuesta menos que cumplirla en el total.

**Criterio de presupuesto fijo.** El mismo mecanismo admite el objetivo del Modelo 1. Se reemplazan M3.4, M3.6 y M3.7 por

max Σ_{i ∈ I⁰} pᵢ · yᵢ

sujeto a Σⱼ Σ_d E(j, d) ≤ B, a la condición de salida sᵢ ≤ 0.33 + (cᵢ⁰ − 0.33)(1 − yᵢ) y a la tasa mínima de salida en cada zona,

Σ_{i ∈ I⁰, d(i) = d} pᵢ · yᵢ ≥ r_B · Σ_{i ∈ I⁰, d(i) = d} pᵢ,

que es la restricción (4) del Modelo 1. En la sensibilidad se agrega el techo de severidad del Modelo 1, con las mismas tangentes: qᵢ ≥ 2a · sᵢ − a² para cada valor posible a, y Σᵢ pᵢ · qᵢ ≤ (1 − ρ_B) · Sev₀. Los empates se resuelven en una segunda etapa que minimiza la severidad, como en el Modelo 1.

**Reformulación exacta por cortes.** Escrito literalmente, con la linealización del Apéndice 1 del paper, el Modelo 3 no se resuelve: en una versión inicial con meta del 10 %, HiGHS no cerraba la brecha en más de {{t_directa}} segundos. La razón también es la idea central del modelo. Como la cobertura θ(j, d) es un solo número para toda la zona, M3.3 cura exactamente a los hogares con Rᵢⱼ ≤ θ(j, d), y ese conjunto es siempre un prefijo del orden por R: si se cura el hogar en la posición c, se curan todos los anteriores. **El Estado elige cuántos hogares atiende, no cuáles.** La solución de cada par queda descrita por un corte c entre 0 y n. No todo corte es admisible, porque la cobertura que resulta de curar los c primeros tiene que curar a esos c y a ninguno más:

(M3.8) F(j, d) = { c : R₍c₎ ≤ θ(j, d)(c) ≤ R₍c₊₁₎ − ε }, con ε = 10⁻⁶,

donde θ(j, d)(c) es la cobertura de los c primeros. F(j, d) depende solo de los datos y del sorteo, así que se enumera antes de optimizar. Con una binaria z(j, d, c) por corte admisible, el modelo queda

(M3.9) min Σ_{(j, d)} Σ_{c ∈ F(j, d)} gasto(j, d, c) · z(j, d, c)

(M3.10) Σ_{c ∈ F(j, d)} z(j, d, c) = 1 para cada par (j, d)

(M3.11) xᵢⱼ = Σ_{c ∈ F(j, d(i)), c ≥ posición de i} z(j, d(i), c) para cada par privado (i, j)

más M3.5 a M3.7. Las dos formulaciones tienen las mismas soluciones factibles y el mismo gasto en cada una, así que tienen el mismo óptimo (Apéndice 1). En la base completa, la reformulación se resuelve en unos {{t_cortes}} segundos.

**Errores de focalización.** El error de inclusión es la fracción del gasto que llega a hogares que no eran pobres. El error de exclusión es la fracción de las personas pobres que no reciben ninguna intervención. Como el objetivo puede tener óptimos alternos con el mismo gasto y errores distintos, una segunda etapa elige, entre las soluciones con gasto a lo sumo E* · (1 + 10⁻⁶), la que menos gasta en hogares no pobres. Así el error reportado no depende del solver.

### Modelo 4: formulación

El Modelo 4 es el Modelo 3 con otra regla para asignar cada par a su celda:

(M4.1) g(i, j) = d(i) si j es un bien público, y g(i, j) = t(i) si j es un bien privado,

donde t(i) es el tipo del hogar. Los conjuntos, parámetros y variables son los del Modelo 3, con la celda g en lugar de la zona d. La función objetivo es

(M4.2) min Σ_{j privado} Σ_t E(j, t) + Σ_{j público} Σ_d E(j, d).

Las restricciones M3.5 a M3.7 no cambian, porque el puntaje sᵢ depende de todos los indicadores sin importar cómo se focalizó cada uno, y la meta y la tasa r_B se siguen exigiendo por zona de P3. La propiedad de prefijo solo usa que la cobertura es común dentro de una celda, así que la reformulación por cortes se aplica igual dentro de un tipo de hogar.

**Bienes públicos y privados.** Los bienes públicos son acueducto y alcantarillado, que se proveen con infraestructura y solo pueden focalizarse por territorio. Los otros 13 indicadores son bienes privados. Los datos apoyan la partición: el acueducto es {{disc_acu_z}} veces más frecuente en la zona más privada que en la menos privada, y solo {{disc_acu_t}} veces entre tipos de hogar. La inasistencia escolar y el hacinamiento varían mucho más entre tipos ({{disc_inas_t}} y {{disc_hac_t}} veces) que entre zonas ({{disc_inas_z}} y {{disc_hac_z}}). El detalle está en el Apéndice 1.

**Tipos de hogar.** Se obtienen con k-medias sobre ocho rasgos que el Estado observa sin una encuesta de privaciones: número de personas, número de menores de 5 años, de personas de 5 a 17 y de mayores de 65, tasa de dependencia y edad, sexo y nivel educativo del jefe. Ninguna privación del IPM entra en el clustering: si entrara, el Estado usaría justo la información que el modelo supone que no tiene. Con k = 4 los tipos separan la pobreza sin haberla usado: la incidencia del tipo más pobre es {{separa_pobreza}} veces la del menos pobre.

**Placebo.** El Modelo 4 cambia dos cosas a la vez frente al Modelo 3: usa información demográfica y reparte los bienes privados en cuatro celdas en vez de tres. Una partición más fina focaliza mejor aunque no tenga contenido. Para separar los dos efectos se resuelve un placebo: el Modelo 4 con las etiquetas de tipo permutadas al azar entre los hogares. Conserva el número y el tamaño de las celdas, pero no la relación entre el tipo y las privaciones.

### Diseño de la comparación de los cuatro modelos

Los cuatro modelos solo pueden diferir en qué sabe el Estado. Todo lo demás es común: los mismos {{hogares}} hogares y la misma línea base (H₀ = {{H0}}, A₀ = {{A0}}, M₀ = {{M0}}), una sola tabla de costos y de reglas de qué se puede quitar en un año, y las mismas restricciones de equidad territorial. En vez de quitarle al Modelo 1 sus restricciones de equidad, se las agregamos a los Modelos 3 y 4, que pueden representarlas porque solo dependen de cuántas personas salen o de cuánto baja M0 en cada zona.

**Qué entra y qué no.** La Tabla M34-1 dice qué restricciones tienen los cuatro modelos en la comparación y por qué.

**Tabla M34-1. Restricciones de la comparación de los cuatro modelos**

| Restricción | Modelos 1 y 2 en la comparación | Modelos 3 y 4 | Por qué |
|---|---|---|---|
| Cobertura escolar obligatoria (E-7) | No | No | Exige saber qué niño concreto no asiste |
| Techo de severidad educativa (SevEdu) | No | No | Exige decisiones niño por niño |
| Tasa mínima de salida por zona r | Sí, en el criterio de presupuesto | Sí, se agrega | Es lineal en yᵢ y no exige saber quién es quién |
| Techo de severidad ρ | Sí, como sensibilidad | Sí, como sensibilidad | Lineal con tangentes |
| Meta de M0 en cada zona | Sí, en el criterio de costo | Sí, reemplaza la meta global | Es la equidad territorial del Modelo 2 |

*Nota.* Especificación de la comparación de Martín (`ESPECIFICACION_COMPARACION_4_MODELOS.md`, rama `Contexto`, secciones 3.1 y 3.3). Los resultados propios de los Modelos 1 y 2, con E-7 y SevEdu, se reportan aparte.

**Los dos criterios.**

- **Criterio de costo.** ¿Cuánto cuesta reducir M0 un m % en cada zona? La referencia de información perfecta es el Modelo 2 sin E-7, con meta en cada zona. El precio de la información de un modelo X es E_X(m) / E_M2(m).
- **Criterio de presupuesto fijo.** ¿Cuántas personas salen de la pobreza con un presupuesto B, si en cada zona debe salir al menos una fracción r_B de los pobres? La referencia es el Modelo 1 sin E-7 ni SevEdu. El precio de la información es H_X(B) / H_M1(B).

**Las tres reglas.**

1. **Los mismos r y ρ en los cuatro modelos.** Para cada B, r_B y ρ_B se calculan una sola vez con el Modelo 1 de la comparación (r por el codo y ρ por la regla de la brecha) y se imponen iguales a los Modelos 3 y 4. Si cada modelo calibrara los suyos, la diferencia mediría parámetros distintos y no información.
2. **La infactibilidad es un resultado.** Para cada configuración se reporta la fracción de réplicas factibles, y las medianas se calculan sobre las factibles. Descartarlas en silencio sesgaría la muestra hacia los sorteos favorables.
3. **La misma tolerancia.** Brecha relativa de 10⁻⁶ en todas las etapas de todos los modelos.

**Réplicas.** En el criterio de costo, {{replicas_costo}} réplicas por meta para el Modelo 3, el Modelo 4 y el placebo, todas con el mismo sorteo por réplica ({{corridas_costo}} corridas). En el criterio de presupuesto fijo, 100 réplicas con B ≤ $10 mil millones y 30 con B ≥ $25 mil millones ({{corridas_cob}} corridas), y {{rmax_reps}} réplicas en el piso máximo garantizable ({{corridas_rmax}} corridas). El número de réplicas se justifica con la condición del teorema del límite central de Hamie et al. (2024, ec. 8), n ≥ (1.96 · CV / e)², y se reporta el intervalo de confianza del 95 % de la mediana por bootstrap.

### Resolución y verificación

Todos los modelos se resuelven con HiGHS mediante PuLP, con brecha relativa de 10⁻⁶, y solo se cuentan las corridas con optimalidad demostrada. Las {{corridas_costo}} corridas del criterio de costo terminaron todas con optimalidad demostrada. Las del criterio de presupuesto fijo con r_B son todas infactibles; para confirmar que la infactibilidad es real y no un error numérico, cada una se resolvió de nuevo sin el preprocesamiento del solver.

La prueba más exigente es la de granularidad máxima: si cada hogar es su propia celda, el sorteo no tiene a quién más asignar la cobertura y el Modelo 3 debe reproducir la información perfecta. Con las restricciones de equidad territorial pasan {{valid_ok}} pruebas (Tabla M34-11 del Apéndice 1). Con la meta en cada zona, el Modelo 3 reproduce el costo del Modelo 2 hasta el centavo con metas del 2 al 20 % y difiere en {{g1_30}} con la del 30 %. Con el piso r_B, saca exactamente a las mismas personas que el Modelo 1 con B ≤ $10 mil millones y difiere entre {{g2_rango}} con presupuestos mayores. La única diferencia es la ya declarada: el Modelo 1 puede usar un mismo ciclo de educación para adultos para quitar a la vez el logro y el analfabetismo de una persona, mientras que en los Modelos 3 y 4 cada par se costea por separado.

Una auditoría independiente del 14 de noviembre no encontró hallazgos críticos. Re-resolvió {{aud_sol}} soluciones y las verificó con la regla directa del sorteo (R ≤ θ) y con la meta en cada zona, sin violaciones. Comparó el modelo por cortes con la enumeración exhaustiva en {{aud_fb}} instancias pequeñas de cada criterio ({{aud_fb}} de {{aud_fb}}) y comprobó la frontera del piso máximo garantizable en {{aud_frontera}} de {{aud_frontera}} casos. Los errores que encontró eran de redacción y ya están corregidos.

---

## 4. Resultados principales

### Comparación de los cuatro modelos

Las cifras de esta sección son del escenario común, con las restricciones de equidad territorial de los Modelos 1 y 2 tal cual: meta de reducción de M0 en cada zona en el criterio de costo y tasa mínima de salida r_B en cada zona en el criterio de presupuesto fijo. El Modelo 1 no aparece en el criterio de costo porque fija el presupuesto y maximiza las personas que salen; su referencia está en el criterio de presupuesto fijo.

#### Criterio de costo

La Tabla M34-2 muestra el costo de cumplir cada meta. Se lee de izquierda a derecha como una escalera de información: el Modelo 2 sabe quién es pobre, el Modelo 4 conoce la zona y el tipo de hogar, el Modelo 3 solo la zona, y el placebo tiene la partición del Modelo 4 sin su contenido. El precio de la información es el cociente entre el costo de cada modelo y el del Modelo 2.

**Tabla M34-2. Costo de reducir M0 en cada zona, por modelo (mil millones de pesos de 2025)**

{{TABLA:costo}}

*Nota.* Modelo 2: información perfecta, una sola solución. Modelos 3 y 4 y placebo: mediana de {{replicas_costo}} réplicas, y entre paréntesis los percentiles 5 y 95 entre réplicas. Precio: costo del modelo dividido por el del Modelo 2. M4/M3 y M4/placebo: mediana del cociente pareado réplica a réplica, con su intervalo de confianza del 95 % por bootstrap. Fuente: `datos_m34/costo_meta_zona.csv`.

**Figura M34-1. Costo de reducir M0 en cada zona según la información del Estado**

![Figura M34-1](figuras_m34/figura_M34-1_costo_contra_meta.png)

**Cómo se lee.** Cada línea es el costo de cumplir la meta del eje horizontal en las tres zonas a la vez. El eje vertical está en escala logarítmica, así que la distancia vertical entre dos líneas es el cociente de sus costos, es decir, el precio de la información. Las bandas son el intervalo de confianza del 95 % de la mediana.

**Qué se observa.** Con metas de hasta el 10 %, el Modelo 3 cuesta entre {{m3_ip_baja}} veces lo que costaría con información perfecta, y con metas del 20 al 30 %, entre {{m3_ip_alta}} veces. El Modelo 4 cuesta entre {{m4_ip_todas}} veces la información perfecta y casi lo mismo que el Modelo 3. El placebo es el más caro desde la meta del 6 %.

**Interpretación.** La información vale más con metas modestas, que son las de los programas reales: elige a quién atender primero, y pierde valor cuando hay que atender a casi todos los pobres de todas formas.

*Fuente:* `datos_m34/costo_meta_zona.csv`.

Cuatro resultados se destacan.

**No saber quién es pobre es caro.** Con la meta del 6 %, por ejemplo, focalizar solo por zona cuesta ${{m3_6}} mil millones y con información perfecta ${{ip_6}} mil millones. Un sistema que permitiera identificar hogar por hogar a quién atender, como un registro social actualizado, pagaría su costo mientras costara menos que la diferencia, unos ${{dif_6}} mil millones para ese solo programa.

**Con la meta en cada zona, el tipo de hogar apenas mejora a la zona.** El intervalo del cociente M4/M3 queda por debajo de 1 en {{n_m4_menor_m3}} de las 15 metas, contiene el 1 en {{n_m4_igual_m3}} y queda por encima en {{n_m4_mayor_m3}}. Con metas del 10 al 24 %, el Modelo 4 cuesta entre un {{ahorro_m4_m3_medio}} % menos que el Modelo 3, pero esas cifras son medianas: el Modelo 4 es más barato en entre el {{pct_rep_m4_menor_m3_medio}} % de las réplicas, no en todas. Con metas del 26 al 30 %, cuesta entre un {{sobrecosto_m4_alto}} % más.

**Pero la demografía sí reemplaza a la geografía.** Desde la meta del 6 %, el Modelo 4 cuesta entre un {{ahorro_m4_placebo}} % menos que el placebo. La razón es que la meta se exige en cada zona. El Modelo 3 puede dirigir la cobertura al rural disperso, donde la incidencia es la más alta ({{H0_rd}}), y lo hace: desde la meta del 8 % pone allí entre el {{m3_rural}} % del gasto (Tabla M34-5). Las celdas del placebo mezclan las tres zonas, así que entre el {{plac_cab}} % de su gasto cae en las cabeceras, y para cumplir la meta rural tiene que comprar cobertura en todas partes. Los tipos del Modelo 4 también mezclan zonas, pero se relacionan con las privaciones, sobre todo con las educativas, y eso le permite llegar a los pobres sin saber dónde viven.

**Los errores de focalización son grandes.** Según la meta, la mediana del error de inclusión está entre el {{incl_m3}} % en el Modelo 3 y entre el {{incl_m4}} % en el Modelo 4. Entre el {{excl_m3}} % de las personas pobres no recibe ninguna intervención en el Modelo 3 (Tabla M34-6).

La Tabla M34-3 responde la pregunta de investigación, que es sobre la incidencia H. Aunque los Modelos 3 y 4 minimizan el costo de una meta sobre M0, la incidencia también baja en las tres zonas. Con la meta del 10 %, H pasa de {{H0}} a {{H10_m2}} con información perfecta, a {{H10_m3}} con el Modelo 3 y a {{H10_m4}} con el Modelo 4.

**Tabla M34-3. Valores finales de H, A y M0 por zona con la meta del 10 %**

La tabla da, para el total de Antioquia y cada zona, el gasto y los valores inicial y final de la incidencia H, la intensidad A y M0. Para los Modelos 3 y 4 y el placebo, cada cifra es la mediana de las réplicas.

{{TABLA:zonas10}}

*Nota.* Gasto en mil millones de pesos de 2025. M0 final cumple la meta en cada zona en todos los modelos; los Modelos 3 y 4 y el placebo la sobrepasan en algunas zonas. Fuente: `datos_m34/H_A_M0_por_zona.csv`, que trae también las otras 14 metas y los percentiles 5 y 95 de H.

En todas las metas y zonas, la incidencia baja al menos un {{redH_min_zona}} en los Modelos 3 y 4 y el placebo. Con la misma meta, los Modelos 3 y 4 suelen bajar H tanto o más que el Modelo 2: el Modelo 3 deja una incidencia total menor o igual que la del Modelo 2 en {{n_H_m3_menor}} de las 15 metas, y el Modelo 4 en {{n_H_m4_menor}}. No es una ventaja, es el reflejo del costo. Sin saber quién es pobre, la cobertura avanza a saltos y no se puede parar justo en la meta, así que en algunas zonas se reduce M0 más de lo exigido. Con la meta del 10 %, por ejemplo, el Modelo 3 reduce M0 un {{m3_10_redM0_cab}} en las cabeceras, cuando la meta es del 10 %. El Modelo 2, en cambio, cumple la meta casi exactamente en cada zona y gasta lo mínimo. Por la misma razón, la intensidad A se comporta distinto: con información perfecta sube en {{n_A_sube_m2}} de las 15 metas, porque el Modelo 2 saca primero a los hogares más cerca del umbral y los que quedan son más intensamente pobres; en los Modelos 3 y 4 el sorteo no distingue esa cercanía, y A cambia poco o incluso baja. Con la meta del 30 %, H baja un {{redH30_m2}} con información perfecta, un {{redH30_m3}} con el Modelo 3 y un {{redH30_m4}} con el Modelo 4 (Tabla M34-4).

**Tabla M34-4. Valores finales de H, A y M0 por zona con la meta del 30 %**

{{TABLA:zonas30}}

*Nota.* Igual que la Tabla M34-3. Fuente: `datos_m34/H_A_M0_por_zona.csv`.

**Figura M34-3. Incidencia final por zona según la meta**

![Figura M34-3](figuras_m34/figura_M34-3_H_por_zona.png)

**Cómo se lee.** Cada panel es una zona. Las líneas muestran la incidencia H final (mediana de las réplicas en los Modelos 3 y 4 y el placebo) para cada meta de reducción de M0. La línea punteada es la incidencia inicial de la zona.

**Qué se observa.** En las tres zonas, H baja con la meta en los cuatro modelos. En el rural disperso, que parte de la incidencia más alta ({{H0_rd}}), el Modelo 2 baja H más que los demás desde las metas intermedias. En las cabeceras y los centros poblados ocurre lo contrario: los Modelos 3 y 4 y el placebo bajan H igual o más que el Modelo 2.

**Interpretación.** En el rural disperso la meta obliga a los cuatro modelos a reducir M0 casi lo mismo, pero el Modelo 2 lo logra sacando de la pobreza a los hogares más cerca del umbral, así que con la misma reducción de M0 baja más la incidencia. En las otras zonas, los Modelos 3 y 4 sobrepasan la meta porque no pueden detener la cobertura justo donde haría falta. La información imperfecta no reduce menos la pobreza en total: la reduce de forma menos dirigida y mucho más cara.

*Fuente:* `datos_m34/H_A_M0_por_zona.csv`.

**Tabla M34-5. En qué se gasta: participación de la salud, la educación y dos zonas en el gasto (%)**

La tabla muestra, para algunas metas, qué parte del gasto va a cada dimensión y a cada zona. Explica por qué el placebo es caro con metas por zona.

{{TABLA:gasto}}

*Nota.* Promedio de la participación en las {{replicas_costo}} réplicas. La salud incluye aseguramiento y barreras de acceso; los centros poblados completan el 100 % de las zonas. Ninguna corrida gasta más del {{otros_max}} % en niñez, vivienda o trabajo. Fuente: `datos_m34/gasto_por_zona_y_dimension.csv`.

La meta por zona adelanta la entrada de la educación. Con la meta del 2 %, los tres modelos gastan al menos el {{salud2_min}} % en salud. Con la del 10 %, el Modelo 4 ya gasta el {{edu10_m4}} % en educación, el placebo el {{edu10_plac}} % y el Modelo 3 el {{edu10_m3}} %.

**Tabla M34-6. Errores de focalización por meta**

La inclusión es la fracción del gasto que llega a hogares no pobres. La exclusión es la fracción de las personas pobres que no recibe ninguna intervención.

{{TABLA:errores}}

*Nota.* Mediana de {{replicas_costo}} réplicas. Fuente: `datos_m34/costo_meta_zona.csv`.

#### Criterio de presupuesto fijo

**Tabla M34-7. Factibilidad con la tasa mínima de salida del Modelo 1**

Para cada presupuesto, la tabla da r_B y ρ_B, las personas que saca de la pobreza el Modelo 1 con r_B y la fracción de réplicas en que los Modelos 3 y 4 y el placebo pueden cumplir r_B en las tres zonas.

{{TABLA:factibilidad}}

*Nota.* B en mil millones de pesos de 2025. r_B y ρ_B se calcularon con las funciones del Modelo 1 (r por el codo y ρ por la regla de la brecha); son provisionales hasta la confirmación de Martín. Con B = 2, 5, 10 y 100, la regla de la brecha no se alcanza y no hay ρ_B. Fuente: `datos_m34/factibilidad_cobertura_rB.csv` y `datos_m34/r_rho_referencias_M1.csv`.

Con información imperfecta, la tasa mínima de salida del Modelo 1 no se puede cumplir: en las {{corridas_cob}} corridas, la fracción de réplicas factibles es del {{pct_fact_max}} en todos los presupuestos. Lo reportamos como resultado. La razón cambia con el presupuesto. Con B ≥ $25 mil millones, r_B exige sacar a más personas de las que el Modelo 3 o el Modelo 4 logran sacar en total. Con B ≤ $10 mil millones el total sí alcanzaría, pero no su reparto: el sorteo no permite asegurar la fracción exigida en las tres zonas a la vez.

Para medir cuánta equidad territorial sí puede garantizar el Estado sin información individual, resolvimos en cada réplica el piso máximo garantizable,

r_max = max t sujeto a Σ_{i ∈ I⁰, d(i) = d} pᵢ · yᵢ ≥ t · Σ_{i ∈ I⁰, d(i) = d} pᵢ para cada zona d,

con el presupuesto B y el mismo mecanismo. Con información perfecta, r_max es el extremo superior del rango en el que el Modelo 1 busca el codo, y por eso siempre es al menos r_B.

**Tabla M34-8. Piso por zona máximo garantizable (% de los pobres de cada zona)**

{{TABLA:rmax}}

*Nota.* B en mil millones de pesos de 2025. Información perfecta: un hogar por celda. Modelos 3 y 4 y placebo: mediana de {{rmax_reps}} réplicas con su intervalo de confianza del 95 % por bootstrap. La última columna del Modelo 3 es su mejor réplica. Fuente: `datos_m34/rmax_piso_garantizable.csv`.

**Figura M34-2. Piso por zona garantizable según el presupuesto**

![Figura M34-2](figuras_m34/figura_M34-2_piso_garantizable.png)

**Cómo se lee.** Para cada presupuesto, la figura muestra la mayor fracción de los pobres de cada zona que el Estado puede asegurar que sale de la pobreza en las tres zonas a la vez. Las marcas horizontales son el r_B que exige el Modelo 1.

**Qué se observa.** Con información perfecta el piso garantizable siempre supera a r_B. Sin información individual queda siempre por debajo: va de {{rmax_m3_2}} con B = $2 mil millones a {{rmax_m3_100}} con B = $100 mil millones en el Modelo 3, frente a {{rmax_ip_100}} con información perfecta. Ni la mejor réplica del Modelo 3 alcanza r_B en ningún presupuesto.

**Interpretación.** La falta de información no solo encarece la reducción de la pobreza: también limita cuánta equidad territorial puede prometer el Estado. Con B = $100 mil millones, los Modelos 3 y 4 garantizan entre el {{rmax_frac_100}} % del piso que garantizaría la información perfecta.

*Fuente:* `datos_m34/rmax_piso_garantizable.csv`.

---

## 5. Discusión

El precio de la información se puede leer como lo máximo que valdría la pena invertir en información para un programa. Como la brecha relativa es mayor con metas modestas y presupuestos pequeños, el argumento pesa más para los programas acotados. El error de inclusión pide una lectura cuidadosa: que buena parte del gasto llegue a hogares no pobres no significa que se pierda, porque esos hogares sí tenían la privación que se les quita. Lo que se pierde es eficacia frente al objetivo de reducir la pobreza multidimensional. Un programa evaluado por su cobertura puede verse exitoso y mover poco el IPM.

El Modelo 4 y su placebo separan dos fuentes de mejora que en la práctica se confunden: la granularidad, que ayuda aunque las celdas no signifiquen nada, y el contenido de la partición, que solo ayuda si se relaciona con la privación. Con metas por zona, la granularidad sin contenido estorba, porque las celdas al azar mezclan las zonas. Antes de focalizar un programa por tipo de hogar hay que comprobar que esos tipos discriminan la privación que el programa ataca.

**Limitaciones de los Modelos 3 y 4.** La base del IPM no identifica municipios, así que la focalización geográfica solo distingue tres zonas; con celdas municipales el Modelo 3 se acercaría a la información perfecta, y nuestro precio de la información es una cota superior. El sorteo supone que, dentro de una celda, cualquier hogar privado tiene la misma probabilidad de ser atendido, y que los sorteos de un hogar son independientes entre indicadores. El modelo elige la cobertura conociendo el sorteo de cada réplica, como en el paper original, así que las cifras son optimistas. Los dos sesgos van en sentidos opuestos: las celdas gruesas inflan el precio de la información y conocer el sorteo lo reduce. Algunas celdas tienen menos de 10 hogares privados en la muestra, y en ellas la cobertura avanza a saltos. La severidad que se reporta, como en el Modelo 1, no está censurada.

---

## Apéndice 1. Linealización y parámetros de los Modelos 3 y 4

### Censura de Alkire y Foster

Hamie et al. (2024, Apéndice 1) linealizan la censura con dos binarias por hogar y cinco restricciones (Lin 1 a Lin 5). En los Modelos 3 y 4 bastan Lin 1 a Lin 3, escritas como M3.6a a M3.6c, con Big-M igual a pᵢ en las dos primeras e igual a 1 en la tercera, y con sᵢ < k escrito como sᵢ ≤ 0.33. La conversión es exacta porque todos los pesos son múltiplos de 0.01. Omitir Lin 4 y Lin 5 no cambia el óptimo: si se toma una solución factible sin ellas y se redefine yᵢ como 1 exactamente cuando sᵢ < k, la contribución Cᵢ no aumenta, la meta se sigue cumpliendo y el gasto es el mismo. El Big-M pᵢ es el más ajustado posible, porque sᵢ ≤ 1; con una constante global la relajación lineal se afloja y el solver no cierra la brecha. La cota Cᵢ ≥ 0 es indispensable: sin ella la meta se cumple con contribuciones negativas.

### Mecanismo de cobertura

Para cada par privado, el paper introduce dos binarias y escribe M3.3 como Lin 6 a Lin 10. La verificamos rama por rama: si la primera binaria vale 0, el hogar sale de la privación y Rᵢⱼ ≤ θ; si vale 1, sigue privado y θ ≤ Rᵢⱼ − ε. Las dos ramas cubren todos los casos sin solaparse. Como todas las cantidades están entre 0 y 1, basta Big-M igual a 1, y con ese valor la binaria coincide con xᵢⱼ, así que las dos binarias se eliminan. La desigualdad estricta θ < R se escribe θ ≤ R − ε con ε = 10⁻⁶, el mismo valor de M3.8: si cambia uno, tiene que cambiar el otro.

### Equivalencia de la reformulación por cortes

Tomemos una solución factible de la formulación directa y un par (j, d). Por M3.3, los hogares curados son los que tienen Rᵢⱼ ≤ θ(j, d), un prefijo del orden de tamaño c. Por M3.2, θ(j, d) es la cobertura de esos c primeros. El último curado cumple R₍c₎ ≤ θ y el primero no curado cumple θ ≤ R₍c₊₁₎ − ε, así que c pertenece a F(j, d), y con z(j, d, c) = 1 la ecuación M3.11 reproduce las mismas xᵢⱼ con el mismo gasto. Recíprocamente, si c pertenece a F(j, d), curar los c primeros y fijar θ como su cobertura cumple M3.2 y M3.3 por la definición de F(j, d). Las restricciones M3.5 a M3.7 dependen solo de xᵢⱼ, así que se cumplen en las dos formulaciones a la vez.

### Tangentes de la severidad

En el criterio de presupuesto fijo, la severidad qᵢ = sᵢ² se representa, como en el Modelo 1, con una tangente por cada valor posible a del puntaje: qᵢ ≥ 2a · sᵢ − a². Como sᵢ solo toma valores discretos, el máximo de las tangentes coincide con sᵢ² en esos valores. La implementación omite la tangente en a = 0, que es redundante con qᵢ ≥ 0.

### Parámetros del Modelo 4

**Tabla M34-9. Razón entre la incidencia de la privación en la celda más privada y en la menos privada**

La tabla compara qué tanto varía cada privación entre zonas y entre tipos de hogar. Una razón alta significa que la partición discrimina bien esa privación.

{{TABLA:discrimina}}

*Nota.* Personas expandidas, k = 4. La atención integral a la primera infancia solo puede existir en hogares con niños menores de 5 años. Fuente: `datos_m34/discriminacion_privaciones.csv`.

**Tabla M34-10. Tipos de hogar del Modelo 4 (k = 4)**

{{TABLA:tipos}}

*Nota.* k-medias ponderado por el factor de expansión, semilla fija. Fuente: `datos_m34/tipos_hogar.csv`.

### Validación de granularidad máxima

**Tabla M34-11. Modelo 3 con un hogar por celda frente a la información perfecta**

G1 compara el costo con meta en cada zona contra el Modelo 2 (mil millones de pesos de 2025). G2 compara las personas que salen con r_B contra el Modelo 1.

{{TABLA:validacion}}

*Nota.* La diferencia admitida es la del ciclo de educación para adultos. Fuente: `datos_m34/validacion_granularidad_maxima.csv`.

---

## Apéndice 2. Sensibilidades de los Modelos 3 y 4

### Sin equidad territorial: meta global y r = 0

Como sensibilidad, repetimos la comparación sin restricciones de equidad territorial: con la meta de M0 global y con r = 0. Miden cuánto cuesta la equidad territorial en cada modelo. Con la meta global del 10 %, la información perfecta cuesta ${{ip_global_10}} mil millones, y con la misma meta en cada zona, ${{ip_10}} mil millones. Con meta global, el Modelo 3 cuesta entre {{glob_m3_ip_baja}} veces la información perfecta con metas de hasta el 10 %. El Modelo 4 es más barato que el Modelo 3, pero hasta la meta del 18 % cuesta lo mismo que el placebo: sin la exigencia por zona, cualquier partición más fina ayuda.

**Tabla M34-12. Costo de reducir M0 con una meta global (mil millones de pesos de 2025)**

{{TABLA:global}}

*Nota.* Mediana de 100 réplicas. Datos congelados del 10 de noviembre. Fuente: `datos_m34/sens_meta_global_costos.csv`.

**Tabla M34-13. Personas que salen de la pobreza con r = 0**

Esta tabla permite comparar H en los cuatro modelos, porque sin piso por zona los Modelos 3 y 4 sí son factibles.

{{TABLA:r0}}

*Nota.* B en mil millones de pesos de 2025. Modelo 1 con r = 0, sin E-7 ni SevEdu. Mediana de las réplicas, con su intervalo de confianza del 95 % para el cociente pareado. Datos congelados del 10 de noviembre. Fuente: `datos_m34/sens_r0_personas_que_salen.csv` y `datos_m34/sens_r0_info_perfecta_M1.csv`.

Con r = 0, el Modelo 3 saca de la pobreza entre el {{r0_m3_pct}} % de las personas que saldrían con el Modelo 1, y el Modelo 4 entre el {{r0_m4_pct}} %.

### Número de tipos de hogar k y costos simplificados (u = 1)

La elección de k se apoyó en un análisis con 50 réplicas pareadas para k de 2 a 8, hecho con una versión simplificada de los costos (una intervención por hogar, uᵢⱼ = 1) y sin equidad territorial, así que se lee por su forma y no por sus cifras. Con k = 2, el Modelo 4 saca de la pobreza {{k_m4_k2}} veces las personas del Modelo 3: la partición separa los hogares por tamaño, que casi no se relaciona con la pobreza. De k = 3 a k = 4 la ganancia es grande, y desde ahí se aplana ({{k_m4_k4}} veces con k = 4 y {{k_m4_k5}} con k = 5). Con k = 8 hay celdas con menos de 10 hogares privados, donde el sorteo deja de representar una focalización por tipo. Elegimos k = 4 con dos criterios: que menos del 15 % de los pares (indicador, celda) tenga menos de 10 hogares privados, y que al pasar a k + 1 la ganancia sea marginal.

**Tabla M34-14. Personas que salen con B = $10 mil millones según el número de tipos de hogar**

{{TABLA:k}}

*Nota.* Costos simplificados (uᵢⱼ = 1), sin equidad territorial, 50 réplicas pareadas. Fuente: `datos_m34/sens_k_u1.csv`.

---

## Referencias

- Alkire, S., y Foster, J. (2011). Counting and multidimensional poverty measurement. *Journal of Public Economics*, 95(7-8), 476-487. https://doi.org/10.1016/j.jpubeco.2010.11.006
- DANE (2026). *Medida de Pobreza Multidimensional 2025: microdatos departamentales* (catálogo 903). Departamento Administrativo Nacional de Estadística. https://microdatos.dane.gov.co/index.php/catalog/903
- Hamie, C., Hlasny, V., y Jouni, M. (2024). *Multidimensional poverty alleviation: Policy optimization and impact simulation* (Working Paper 1742). Economic Research Forum. https://erf.org.eg/publications/multidimensional-poverty-alleviation-policy-optimization-and-impact-simulation/
- Huangfu, Q., y Hall, J. A. J. (2018). Parallelizing the dual revised simplex method. *Mathematical Programming Computation*, 10(1), 119-142. https://doi.org/10.1007/s12532-017-0130-5
- Mitchell, S., O'Sullivan, M., y Dunning, I. (2011). PuLP: A linear programming toolkit for Python. University of Auckland. https://optimization-online.org/2011/09/3178/
- Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, 12, 2825-2830. https://jmlr.org/papers/v12/pedregosa11a.html
