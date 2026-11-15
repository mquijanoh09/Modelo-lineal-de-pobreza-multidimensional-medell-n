# Modelos 3 y 4 para integrar al borrador del paper

Entrega de Jerónimo Vélez según `PLAN_INTEGRACION_M3_M4.md` (rama `Contexto`, 14-nov), ajustada al borrador de Martín (`paper_borrador/borrador_paper_2026-11-14.md`, revisión 856).

**Cómo usar este archivo.** Cada bloque empieza con una línea en cursiva que dice dónde se pega en el borrador. La numeración ya continúa la del borrador: Tabla 1 (reemplazo con cuatro columnas), Tablas 3 a 9 y Figuras 10 a 12 en el cuerpo, Tablas A2 y A3 (los huecos que el Apéndice 1 dejó para los Modelos 3 y 4) y Tablas A9 a A14 en los apéndices. Las ecuaciones siguen la convención del borrador: OBJ 3 y OBJ 4, Restricción₃ n y Restricción₄ n. Todas las cifras salen de los CSV de `datos_m34/`; `cifras_m34.csv` dice el archivo y la columna de cada una. Los valores de r\_B, ρ\_B y del Modelo 2 con meta por zona son provisionales hasta que Martín los confirme (§6 del plan).

---

## Resumen

*Se agrega al final del Resumen, antes de «Los resultados muestran estabilidad…».*

Los Modelos 3 y 4 retiran el supuesto de información perfecta: el Estado solo conoce agregados por zona o por tipo de hogar, y un sorteo decide a qué hogares llega cada programa. Con metas de reducción de M0 de hasta el 10 % en cada zona, focalizar solo por zona cuesta entre 5.5 y 12.9 veces lo que costaría con información perfecta, y con un presupuesto fijo ninguna réplica del sorteo garantiza en cada zona la tasa mínima de salida del Modelo 1.

---

## 1. Motivación

*Se agrega después del párrafo que termina en «…una distribución de las intervenciones que atiende también la intensidad de las privaciones».*

Los Modelos 1 y 2 suponen que el Estado conoce las privaciones de cada hogar y puede intervenirlas de manera individual. Ningún programa social opera así: los recursos se asignan con estadísticas territoriales o con registros como el SISBÉN, y la ejecución llega a algunos hogares privados y no a otros. Por eso la pregunta de política no es solo cuánto cuesta reducir la pobreza, sino cuánto cuesta reducirla sin saber con exactitud quién es pobre. Los Modelos 3 y 4, que replican los modelos de focalización imperfecta de Hamie et al. (2024), responden esa pregunta. La diferencia de costo frente a los Modelos 1 y 2 es el precio de la información: lo máximo que valdría la pena invertir en mejorar los sistemas de focalización antes de ampliar el presupuesto de un programa.

*Se agrega a la lista «Dos formulaciones complementarias la responden» (que pasa a «Cuatro formulaciones»).*

- **Modelo 3 (focalización por zona).** El Estado conoce cuántas personas están privadas en cada indicador y zona, pero no quiénes son. Decide qué fracción de la población privada de cada zona cubre cada programa, y un sorteo decide a qué hogares llega.
- **Modelo 4 (focalización por zona y tipo de hogar).** Como el Modelo 3, pero los bienes privados se focalizan por tipo de hogar, construido con rasgos demográficos que el Estado observa.

---

## 2. Escenarios de política modelados

### Supuestos y salvedades de los modelos

*Se agrega al final de la lista de supuestos (después del 11).*

Los Modelos 3 y 4 comparten los supuestos 1, 4, 5, 6, 8 y 9. Cuatro supuestos de los Modelos 1 y 2 no se mantienen en ellos. Sin el supuesto 3, la cobertura llega a hogares privados que no son pobres; ese es el error de inclusión. Sin el supuesto 7, se modelan los 3,732 hogares de la muestra, no solo los 523 pobres, porque el programa llega a cualquier hogar privado de la celda. El supuesto 10 (cobertura obligatoria) no se incluye, porque exige saber qué niño concreto no asiste. Del supuesto 2 se pierde una dependencia: un ciclo CLEI no quita a la vez el logro educativo y el analfabetismo, porque cada par (hogar, indicador) se costea por separado. El supuesto 11 no aplica, porque no usan la severidad educativa. Agregan tres supuestos propios:

12. **El sorteo.** Cada par (hogar, indicador) recibe un número aleatorio Rᵢⱼ, uniforme entre 0 y 1 y fijado antes de optimizar. El hogar sale de la privación si su número queda por debajo de la cobertura que el Estado compró en su celda. Dentro de una celda, cualquier hogar privado tiene la misma probabilidad de ser atendido, sea pobre o no.
13. **Las celdas de focalización.** Una celda es el grupo de hogares al que el Estado puede asignar una cobertura distinta. En el Modelo 3 son las tres zonas de P3. En el Modelo 4 son las zonas para los bienes públicos y cuatro tipos de hogar para los bienes privados. Como la base no identifica municipios, no hay celdas geográficas más finas.
14. **Las réplicas.** Como el resultado depende del sorteo, cada configuración se resuelve con 100 sorteos distintos (30 en algunas corridas del criterio de presupuesto fijo) y se reporta la mediana con su intervalo. El Modelo 3, el Modelo 4 y el placebo comparten el sorteo de cada réplica, así que sus diferencias son pareadas.

Como en el original, el modelo elige la cobertura conociendo el sorteo de la réplica, lo que hace optimistas sus cifras. Además, los sorteos de un mismo hogar son independientes entre indicadores, aunque en la práctica un hogar que no aparece en los registros suele quedar fuera de varios programas a la vez.

### Modelo 3: modelo por zona con focalización imperfecta

*Se agrega después de la subsección del Modelo 2.*

El Modelo 3 representa la forma en que suele operar la política social: el Estado conoce, para cada zona, cuántas personas están privadas en cada indicador y cuánto cuesta atenderlas, pero no sabe quiénes son. Su decisión es la cobertura de cada programa en cada zona, es decir, la fracción de la población privada que va a atender. A qué hogares llega esa cobertura lo decide un sorteo, que representa los errores de la focalización real: el programa atiende a algunos hogares privados y no a otros, sin distinguir si son pobres.

Como en el Modelo 2 de Hamie et al. (2024), el modelo busca el costo mínimo de reducir M0 en un porcentaje dado, y la meta se exige en cada zona, igual que en nuestro Modelo 2. Lo fijo son los costos por hogar e indicador, las reglas de qué se puede quitar en un año, el sorteo de cada réplica y la meta. La misma estructura admite el objetivo del Modelo 1: con un presupuesto B, maximizar las personas que salen de la pobreza con la tasa mínima de salida por zona del Modelo 1.

A diferencia de los Modelos 1 y 2, aquí sí hay errores de focalización. El error de inclusión es el gasto que llega a hogares privados que no son pobres; el error de exclusión, las personas pobres que no reciben ninguna intervención. Los dos son el resultado de focalizar sin información individual y no un defecto del modelo.

### Modelo 4: modelo mixto por zona y tipo de hogar

El Modelo 4 agrega una fuente de información: el tipo de hogar, construido con rasgos demográficos que registra el SISBÉN (tamaño, edades de los integrantes y características del jefe), sin usar ninguna privación. El Estado sigue sin saber quién está privado en qué. Siguiendo a Hamie et al. (2024), los indicadores se dividen en bienes públicos, que se proveen con infraestructura y solo pueden focalizarse por territorio (acueducto y alcantarillado), y bienes privados, que se entregan a personas u hogares (los otros 13). Los primeros se focalizan por zona y los segundos por tipo de hogar.

El Modelo 4 cambia dos cosas a la vez frente al Modelo 3: usa información demográfica y reparte los bienes privados en cuatro celdas en lugar de tres. Una partición más fina focaliza mejor aunque no tenga contenido. Para separar los dos efectos se resuelve un placebo: el Modelo 4 con los tipos de hogar permutados al azar, que conserva el número y el tamaño de las celdas pero no su relación con las privaciones.

### Comparación de los modelos

*Reemplaza la Tabla 1 y la frase que la presenta. Las columnas de los Modelos 1 y 2 son las del borrador, sin cambios.*

La Tabla 1 compara las características de los cuatro modelos. Las ocho primeras filas son las mismas de la Tabla 1 de Hamie et al. (2024); las tres últimas corresponden a las restricciones de equidad que agregamos. Los Modelos 1 y 2 comparten el supuesto de información completa sobre cada hogar. Los Modelos 3 y 4 lo retiran, y por eso son los únicos con desperdicio en hogares no pobres.

**Tabla 1. Comparación de las características de los modelos**

| Característica | Modelo 1: por hogar, presupuesto fijo | Modelo 2: por hogar, costo mínimo (*first best*) | Modelo 3: por zona, focalización imperfecta | Modelo 4: por zona y tipo de hogar |
| --- | --- | --- | --- | --- |
| Se puede intervenir cualquier hogar con privaciones | N: solo los hogares pobres | N: solo los hogares pobres | S: cualquier hogar privado de la zona, pobre o no | S: cualquier hogar privado de la celda, pobre o no |
| Desperdicio por ayuda a hogares sin privaciones | N | N | N: la cobertura del indicador j solo llega a hogares privados en j | N: igual que el Modelo 3 |
| Los hogares en pobreza multidimensional se focalizan con precisión | S | S | N: el Estado solo conoce agregados por zona | N: conoce agregados por zona y el tipo de hogar |
| Gasto en hogares pobres que no salen de la pobreza (sin efecto en H) | S, a propósito: el techo de severidad y la escolarización obligatoria invierten en hogares que no salen; no cambia H, pero sí la severidad | S, a propósito: la meta de M0 premia reducir privaciones de quien sigue pobre, y la escolarización obligatoria se paga aunque el hogar no salga | S: el sorteo reparte la cobertura entre los pobres sin mirar cuánto les falta para salir | S: igual que el Modelo 3 |
| Desperdicio por ayuda a hogares con privaciones pero no pobres (sin efecto en A ni en H) | N | N | S: error de inclusión, entre el 26 y 55 % del gasto según la meta | S: entre el 18 y 50 % del gasto |
| Se distinguen privaciones de bienes privados y públicos | N | N | N | S: acueducto y alcantarillado por zona; los otros 13 por tipo de hogar |
| El Estado ajusta las transferencias según el patrón de consumo del hogar | N | N | N | N: la base no trae ingreso ni gasto |
| Desperdicio en transferencias por riesgo moral (el hogar usa la ayuda en otra cosa) | Parcial: casi todas las intervenciones son en especie; en la única transferencia (Renta Ciudadana) el incumplimiento se cobra con p = 0.369 | Parcial: igual que el Modelo 1 | Parcial: igual que el Modelo 1 | Parcial: igual que el Modelo 1 |
| Techo de severidad (FGT α = 2) | S: ρ es el menor valor con A ≤ A₀ | N: la meta sobre M0 atenúa el sesgo, pero A sube levemente (sección 4) | Solo como sensibilidad, con el ρ\_B del Modelo 1 | Solo como sensibilidad, igual que el Modelo 3 |
| Equidad territorial | S: tasa mínima de salida r en cada zona | S: meta de M0 en cada zona | S: meta de M0 en cada zona; con presupuesto fijo, la tasa r\_B del Modelo 1 es infactible | S: igual que el Modelo 3 |
| Techo de severidad educativa (SevEdu) | S: ρ\_e = 14 % | Solo como sensibilidad | N: exige decisiones niño por niño | N: igual que el Modelo 3 |

*S = sí; N = no. Fuente: elaboración propia con base en la Tabla 1 de Hamie et al. (2024). Las columnas de sus Modelos 1a y 1b (sin costos) no se incluyen.*

---

## 3. Métodos empíricos

### Modelo 3: modelo por zona con focalización imperfecta

*Se agrega después de la subsección del Modelo 2 y antes de «Resolución y verificación de los modelos».*

**Conjuntos.** Los del Modelo 1, con tres cambios:

- **Ī ⊇ I**: los 3,732 hogares de la muestra. I sigue siendo el de los 523 hogares pobres. El mecanismo de cobertura actúa sobre Ī, porque un programa puede llegar a un hogar privado que no es pobre; la salida de la pobreza y la meta se miden sobre I.
- **J**: los 15 indicadores; **Jᴵ ⊆ J**, los intervenibles en un año, con las reglas de los Modelos 1 y 2 (supuesto 4).
- **D**: las tres zonas de P3, con d(i) la zona del hogar i. En cada par (j, d), los hogares privados se ordenan por su sorteo, R₍₁₎ < R₍₂₎ < … < R₍ₙ₎, con n = n(j, d), y **F(j, d)** es el conjunto de cortes admisibles definido abajo.

**Parámetros de entrada.**

- **Originales:** los del Modelo 1 (wⱼ, Mᵢⱼ, HWᵢ, HSᵢ y los costos unitarios por zona de la Tabla A6), ahora para todos los hogares de Ī; la meta m.
- **Calculados:**
  - cᵢ⁰, pᵢ, uᵢⱼ y el costo cᵢⱼ = costo unitario de la zona × uᵢⱼ × HWᵢ, como en el Modelo 1;
  - Vᵢⱼ = uᵢⱼ · HWᵢ, la población que atiende el par (i, j);
  - Den(j, d) = Σᵢ∈Ī(d) Vᵢⱼ Mᵢⱼ, la población privada en el indicador j dentro de la zona d;
  - Rᵢⱼ ∈ [0, 1], el sorteo del par, distinto en cada réplica;
  - Pob\_d y M0\_d⁰, como en el Modelo 2.

**Variables de decisión.**

- **Externas:** θ(j, d) ∈ [0, 1], la cobertura del indicador j en la zona d.
- **Internas:** xᵢⱼ ∈ {0, 1}, igual a 1 si al hogar i se le quita la privación j; yᵢ ∈ {0, 1}, igual a 1 si el hogar pobre i sale de la pobreza; Gᵢ ≥ 0, la contribución censurada del hogar i al numerador de M0, como en el Modelo 2; E(j, d) ≥ 0, el gasto en el indicador j dentro de la zona d.
- **Expresión auxiliar:** el puntaje final sᵢ = cᵢ⁰ − Σⱼ∈Jᴵ wⱼ xᵢⱼ. Las privaciones que no se pueden quitar en un año quedan como constante.

A diferencia de los Modelos 1 y 2, xᵢⱼ no es una decisión del Estado: la determinan la cobertura θ y el sorteo.

**Función objetivo.** Se minimiza el gasto total:

min Σⱼ Σ\_d E(j, d)  (OBJ 3)

**Restricciones.** *Mecanismo de cobertura.* El gasto y la cobertura de cada par se calculan con los hogares que efectivamente reciben la intervención:

E(j, d) = Σᵢ∈Ī(d) cᵢⱼ xᵢⱼ  para todo j y toda zona d  (Restricción₃ 1)

θ(j, d) = Σᵢ∈Ī(d) Vᵢⱼ xᵢⱼ / Den(j, d)  para todo j y toda zona d  (Restricción₃ 2)

y el sorteo decide a quién llega la cobertura:

xᵢⱼ = Mᵢⱼ si Rᵢⱼ ≤ θ(j, d(i)), y xᵢⱼ = 0 si Rᵢⱼ > θ(j, d(i))  para todo i ∈ Ī y j ∈ Jᴵ  (Restricción₃ 3)

Numerador y denominador de Restricción₃ 2 se miden en la misma unidad, personas de la población. En el original, el numerador está ponderado por HWᵢ y el denominador cuenta hogares de la muestra; con esa definición la cobertura llega a 4.81 en nuestros datos, todo hogar privado se cura y el Modelo 3 se reduce al Modelo 1 sin que el solver lo advierta.

*Salida de la pobreza y censura.* Para cada hogar pobre i ∈ I, la censura de Alkire y Foster se escribe con las restricciones Lin 1 a Lin 3 de Hamie et al. (2024, Apéndice 1):

Gᵢ ≥ pᵢ sᵢ − pᵢ yᵢ  para todo i ∈ I  (Restricción₃ 4)

Gᵢ ≤ pᵢ sᵢ + pᵢ yᵢ  para todo i ∈ I  (Restricción₃ 5)

sᵢ ≤ 0.33 + (1 − yᵢ)  para todo i ∈ I  (Restricción₃ 6)

Restricción₃ 4 es la Restricción₂ 2 con big-M pᵢ en lugar de Uᵢ = pᵢ cᵢ⁰, y Restricción₃ 6 es la Restricción₂ 1 con big-M 1 en lugar de Mᵢ. Restricción₃ 5 es redundante cuando se minimiza el costo, pero la conservamos para que el Modelo 3 sea la formulación del original.

*Meta sobre M0.* Igual que en el Modelo 2, el M0 final de cada zona debe bajar al menos un porcentaje m:

Σᵢ∈I(d) Gᵢ ≤ (1 − m) · M0\_d⁰ · Pob\_d  para toda zona d ∈ D  (Restricción₃ 7)

Las tres metas por zona implican la meta global, así que cumplir la meta en cada zona nunca cuesta menos que cumplirla en el total.

**Reformulación exacta por cortes.** Escrito con las restricciones Lin 6 a Lin 10 del original, el Modelo 3 no se resuelve en un tiempo razonable: en una versión inicial con meta del 10 %, HiGHS no cerraba la brecha en más de 200 segundos. La razón es también la idea central del modelo. Como θ(j, d) es un solo número para toda la zona, Restricción₃ 3 cura exactamente a los hogares con Rᵢⱼ ≤ θ(j, d), y ese conjunto es siempre un prefijo del orden por R: si se cura el hogar en la posición c, se curan todos los anteriores. **El Estado elige cuántos hogares atiende, no cuáles.** La solución de cada par queda descrita por un corte c entre 0 y n. No todo corte es admisible, porque la cobertura que resulta de curar a los c primeros tiene que curar a esos c y a ninguno más:

F(j, d) = { c : R₍c₎ ≤ θ(j, d)(c) ≤ R₍c₊₁₎ − ε },  con ε = 10⁻⁶,

donde θ(j, d)(c) es la cobertura de los c primeros. F(j, d) depende solo de los datos y del sorteo, así que se enumera antes de optimizar. Con una binaria z(j, d, c) por corte admisible, el gasto del par es E(j, d) = Σ\_c∈F(j, d) gasto(j, d, c) · z(j, d, c), y Restricción₃ 1 a Restricción₃ 3 se reemplazan por

Σ\_c∈F(j, d) z(j, d, c) = 1  para todo par (j, d)  (Restricción₃ 8)

xᵢⱼ = Σ\_c∈F(j, d(i)), c ≥ posición de i z(j, d(i), c)  para todo par privado (i, j)  (Restricción₃ 9)

*Dominios.*

z(j, d, c), yᵢ ∈ {0, 1};  Gᵢ, E(j, d) ≥ 0  (Restricción₃ 10)

Las dos formulaciones tienen las mismas soluciones factibles con el mismo gasto, así que tienen el mismo óptimo (Apéndice 1). La reformulación se resuelve en unos 2 segundos con la base completa.

**Errores de focalización y desempate.** El error de inclusión es la fracción del gasto que llega a hogares no pobres; el de exclusión, la fracción de las personas pobres que no reciben ninguna intervención. Como OBJ 3 puede tener óptimos alternos con el mismo gasto y errores distintos, una segunda etapa elige, entre las soluciones con gasto a lo sumo E\* · (1 + 10⁻⁶), la que menos gasta en hogares no pobres. Así el error reportado no depende del solver.

**Criterio de presupuesto fijo.** El mismo mecanismo admite el objetivo del Modelo 1. Se usan OBJ 1a y OBJ 1b con Restricción₁ 2, Restricción₁ 3 y, en la sensibilidad, Restricción₁ 4 y Restricción₁ 5, sobre los xᵢⱼ que determinan el sorteo y la cobertura, y la Restricción₁ 1 se reemplaza por Σⱼ Σ\_d E(j, d) ≤ B. La tasa r y el techo ρ se fijan con los valores r\_B y ρ\_B que calcula el Modelo 1 para ese presupuesto.

### Modelo 4: modelo mixto por zona y tipo de hogar

**Conjuntos, parámetros y variables.** Los del Modelo 3, con la celda g en lugar de la zona d. Se agregan el conjunto **T** de los cuatro tipos de hogar, el tipo t(i) de cada hogar y la partición de los indicadores en **V** = {acueducto, alcantarillado} (bienes públicos) y **U** = J \ V (bienes privados). La celda del par (i, j) es

g(i, j) = d(i) si j ∈ V, y g(i, j) = t(i) si j ∈ U.

**Función objetivo.**

min Σⱼ∈U Σₜ∈T E(j, t) + Σⱼ∈V Σ\_d E(j, d)  (OBJ 4)

**Restricciones.** Restricción₄ 1 a Restricción₄ 10 son Restricción₃ 1 a Restricción₃ 10 con la celda g(i, j) en lugar de d(i). Las de censura y meta (Restricción₄ 4 a Restricción₄ 7) no cambian, porque el puntaje sᵢ depende de todos los indicadores sin importar cómo se focalizó cada uno, y la meta y la tasa r\_B se siguen exigiendo por zona de P3. La propiedad de prefijo solo usa que la cobertura es común dentro de una celda, así que la reformulación por cortes vale igual dentro de un tipo de hogar.

**Bienes públicos y privados.** Los datos apoyan la partición (Tabla A9): el acueducto es 14.5 veces más frecuente en la zona más privada que en la menos privada, y solo 4.1 veces entre tipos de hogar. La inasistencia escolar y el hacinamiento varían mucho más entre tipos (51.7 y 26.6 veces) que entre zonas (4.8 y 2.7).

**Tipos de hogar.** Se obtienen con k-medias sobre ocho rasgos que el Estado observa sin una encuesta de privaciones: número de personas, número de menores de 5 años, de personas de 5 a 17 y de mayores de 65, tasa de dependencia y edad, sexo y nivel educativo del jefe. Ninguna privación entra en el clustering, porque si entrara el Estado usaría justo la información que el modelo supone que no tiene. Con k = 4 los tipos separan la pobreza sin haberla usado: la incidencia del tipo más pobre es 4.3 veces la del menos pobre (Tabla A10). La elección de k se explica en el Apéndice 2.

### Diseño de la comparación de los cuatro modelos

*Se agrega antes de «Resolución y verificación de los modelos».*

Para que la comparación mida solo el efecto de la información, los cuatro modelos comparten los mismos 3,732 hogares y la línea base (H₀ = 9.45 %, A₀ = 0.409, M0⁰ = 0.0387), una sola tabla de costos y de reglas de qué se puede quitar en un año, y las mismas restricciones de equidad territorial. En lugar de quitarle al Modelo 1 sus restricciones de equidad, se agregan a los Modelos 3 y 4 las que pueden representar, que son las que solo dependen de cuántas personas salen o de cuánto baja M0 en cada zona. Las que exigen decisiones sobre un niño concreto quedan fuera de los cuatro.

| Restricción | Modelos 1 y 2 en la comparación | Modelos 3 y 4 | Por qué |
| --- | --- | --- | --- |
| Cobertura obligatoria (Restricción₁ 10, Restricción₂ 7) | No | No | Exige saber qué niño concreto no asiste |
| Techo de SevEdu (Restricción₁ 9) | No | No | Exige decisiones niño por niño |
| Tasa mínima de salida por zona (Restricción₁ 3) | Sí, en el criterio de presupuesto fijo | Sí, se agrega | Es lineal en yᵢ y no exige saber quién es quién |
| Techo de severidad (Restricción₁ 5) | Sí, como sensibilidad | Sí, como sensibilidad | Lineal con tangentes |
| Meta de M0 en cada zona (Restricción₂ 3) | Sí, en el criterio de costo | Sí, Restricción₃ 7 y Restricción₄ 7 | Es la equidad territorial del Modelo 2 |

*Fuente: especificación de la comparación (rama Contexto, ESPECIFICACION\_COMPARACION\_4\_MODELOS.md, secciones 3.1 y 3.3). Los resultados de la sección 4 con E-7 y SevEdu son los del caso base de los Modelos 1 y 2, no los de la comparación.*

La comparación usa dos criterios. En el **criterio de costo**, la pregunta es cuánto cuesta reducir M0 un m % en cada zona; la referencia de información perfecta es el Modelo 2 sin E-7, y el precio de la información de un modelo X es su costo dividido por el del Modelo 2. En el **criterio de presupuesto fijo**, la pregunta es cuántas personas salen de la pobreza con un presupuesto B si en cada zona debe salir al menos una fracción r\_B de los pobres; la referencia es el Modelo 1 sin E-7 ni SevEdu.

Tres reglas protegen la comparación. Primera, los mismos r y ρ en los cuatro modelos: para cada B, r\_B y ρ\_B se calculan una sola vez con el Modelo 1 (r por el codo y ρ por la regla de la brecha) y se imponen iguales a los Modelos 3 y 4; si cada modelo calibrara los suyos, la diferencia mediría parámetros distintos y no información. Segunda, la infactibilidad es un resultado: se reporta la fracción de réplicas factibles y las medianas se calculan sobre las factibles. Tercera, la misma tolerancia: brecha relativa de 10⁻⁶ en todas las etapas de los cuatro modelos.

En el criterio de costo se usan 100 réplicas por meta para el Modelo 3, el Modelo 4 y el placebo, con el mismo sorteo en cada réplica (4,500 corridas). En el de presupuesto fijo, 100 réplicas con B ≤ $10 mil millones y 30 con B ≥ $25 mil millones (1,350 corridas), y 100 réplicas para el piso máximo garantizable (1,800 corridas). El número de réplicas cumple la condición del teorema del límite central de Hamie et al. (2024, ec. 8), n ≥ (1.96 · CV / e)², y se reporta el intervalo de confianza del 95 % de la mediana por bootstrap.

### Resolución y verificación de los modelos

*Se agrega a la subsección compartida, después de «Prueba cruzada entre los modelos».*

*Resolución de los Modelos 3 y 4.* Se resuelven con HiGHS a través de PuLP, con brecha relativa de 10⁻⁶ en las dos etapas, y solo se cuentan las corridas con optimalidad demostrada. Las 4,500 corridas del criterio de costo terminaron todas con optimalidad demostrada. Las del criterio de presupuesto fijo con r\_B son todas infactibles; para confirmar que la infactibilidad es real y no numérica, cada una se resolvió de nuevo sin el preprocesamiento del solver.

*Prueba de granularidad máxima.* Si cada hogar es su propia celda, el sorteo no tiene a quién más asignar la cobertura y el Modelo 3 debe reproducir la información perfecta. Con las restricciones de equidad territorial pasan 11/11 pruebas (Tabla A11). Con la meta en cada zona, el Modelo 3 reproduce el costo del Modelo 2 hasta el centavo con metas del 2 al 20 % y difiere en 0.38 % con la del 30 %. Con el piso r\_B saca exactamente a las mismas personas que el Modelo 1 con B ≤ $10 mil millones y difiere entre 0.32 % y 0.97 % con presupuestos mayores. La única diferencia es la del supuesto 2: el Modelo 1 puede usar un mismo ciclo CLEI para quitar a la vez el logro educativo y el analfabetismo de un adulto, mientras que en los Modelos 3 y 4 cada par se costea por separado.

*Verificación independiente de los Modelos 3 y 4.* Una auditoría del 14 de noviembre re-resolvió 144 soluciones y las verificó con la regla directa del sorteo (Rᵢⱼ ≤ θ) y con la meta en cada zona, sin violaciones. Comparó la reformulación por cortes con la enumeración exhaustiva en 40 instancias pequeñas de cada criterio (40 de 40) y comprobó la frontera del piso máximo garantizable en 72 de 72 casos.

---

## 4. Resultados principales

### Comparación de los cuatro modelos

*Se agrega al final de la sección 4, después del párrafo de sensibilidades.*

Esta subsección compara los cuatro modelos en el escenario común de la sección 3: sin cobertura obligatoria ni SevEdu, con la meta de M0 en cada zona en el criterio de costo y con la tasa mínima de salida r\_B en cada zona en el de presupuesto fijo. Por eso sus cifras de los Modelos 1 y 2 no son las de la Tabla 2. El Modelo 1 no aparece en el criterio de costo, porque fija el presupuesto y maximiza las personas que salen.

#### Criterio de costo

La Tabla 3 presenta el costo de cumplir cada meta en los cuatro escenarios de información: el Modelo 2 sabe quién es pobre, el Modelo 4 conoce la zona y el tipo de hogar, el Modelo 3 solo la zona, y el placebo tiene la partición del Modelo 4 sin su contenido. El precio de la información es el cociente entre el costo de cada modelo y el del Modelo 2.

**Tabla 3.** Costo de reducir M0 en cada zona según la información del Estado (mil millones de pesos de 2025).

| Meta m | Modelo 2 | Modelo 3 | Modelo 4 | Placebo | Precio M3 | Precio M4 | M4/M3 (IC 95 %) | Réplicas con M4 < M3 | M4/placebo (IC 95 %) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 % | 0.47 | 6.10 (3.6 a 13.2) | 4.15 (2.7 a 5.4) | 4.00 (2.7 a 5.7) | 12.9 | 8.8 | 0.64 (0.59 a 0.72) | 83 % | 1.00 (0.92 a 1.11) |
| 4 % | 1.31 | 8.09 (5.1 a 14.6) | 9.18 (6.5 a 11.0) | 8.72 (6.5 a 11.5) | 6.2 | 7.0 | 1.14 (0.98 a 1.25) | 42 % | 1.01 (0.95 a 1.05) |
| 6 % | 2.30 | 14.16 (9.7 a 30.6) | 15.34 (10.9 a 22.2) | 18.33 (12.7 a 26.7) | 6.1 | 6.7 | 1.04 (0.96 a 1.11) | 48 % | 0.83 (0.76 a 0.90) |
| 8 % | 3.62 | 21.96 (14.6 a 35.5) | 21.35 (16.0 a 26.9) | 27.62 (20.8 a 36.8) | 6.1 | 5.9 | 0.97 (0.88 a 1.02) | 54 % | 0.75 (0.72 a 0.79) |
| 10 % | 5.17 | 28.67 (20.2 a 38.6) | 26.91 (20.9 a 29.5) | 38.09 (29.0 a 49.1) | 5.5 | 5.2 | 0.90 (0.83 a 0.97) | 65 % | 0.70 (0.66 a 0.73) |
| 12 % | 7.06 | 36.39 (24.7 a 42.4) | 32.27 (27.7 a 35.5) | 48.62 (38.7 a 60.9) | 5.2 | 4.6 | 0.89 (0.87 a 0.92) | 71 % | 0.67 (0.65 a 0.69) |
| 14 % | 8.97 | 42.61 (30.6 a 73.4) | 40.44 (34.6 a 45.9) | 57.43 (48.3 a 72.1) | 4.8 | 4.5 | 0.96 (0.93 a 1.00) | 61 % | 0.69 (0.68 a 0.72) |
| 16 % | 11.19 | 50.07 (36.9 a 86.5) | 47.90 (39.9 a 52.6) | 69.07 (56.2 a 83.5) | 4.5 | 4.3 | 0.93 (0.87 a 0.97) | 64 % | 0.66 (0.65 a 0.69) |
| 18 % | 13.56 | 59.33 (45.4 a 89.1) | 53.95 (46.2 a 62.0) | 81.65 (66.2 a 93.1) | 4.4 | 4.0 | 0.92 (0.86 a 0.97) | 68 % | 0.66 (0.64 a 0.68) |
| 20 % | 16.11 | 65.41 (50.9 a 94.0) | 60.79 (54.1 a 68.2) | 93.33 (78.9 a 104.3) | 4.1 | 3.8 | 0.92 (0.87 a 0.97) | 70 % | 0.65 (0.64 a 0.67) |
| 22 % | 19.02 | 74.96 (59.8 a 97.6) | 67.38 (62.6 a 71.4) | 105.29 (87.8 a 116.6) | 3.9 | 3.5 | 0.90 (0.89 a 0.94) | 72 % | 0.64 (0.63 a 0.65) |
| 24 % | 22.04 | 80.65 (65.1 a 101.4) | 74.99 (70.9 a 77.4) | 117.73 (99.0 a 131.3) | 3.7 | 3.4 | 0.92 (0.90 a 0.95) | 68 % | 0.62 (0.62 a 0.64) |
| 26 % | 25.22 | 84.75 (70.7 a 105.4) | 90.29 (81.7 a 100.2) | 132.09 (110.9 a 145.1) | 3.4 | 3.6 | 1.07 (1.02 a 1.09) | 35 % | 0.68 (0.67 a 0.70) |
| 28 % | 28.46 | 89.28 (75.8 a 107.9) | 113.07 (97.9 a 125.3) | 146.91 (126.5 a 157.7) | 3.1 | 4.0 | 1.24 (1.20 a 1.29) | 4 % | 0.77 (0.76 a 0.78) |
| 30 % | 32.37 | 105.34 (89.5 a 125.8) | 138.61 (115.9 a 155.9) | 160.24 (140.0 a 173.5) | 3.3 | 4.3 | 1.30 (1.28 a 1.37) | 4 % | 0.86 (0.84 a 0.88) |

*Modelo 2: información perfecta, una sola solución. Modelos 3 y 4 y placebo: mediana de 100 réplicas y, entre paréntesis, los percentiles 5 y 95 entre réplicas. Precio: costo del modelo dividido por el del Modelo 2. M4/M3 y M4/placebo: mediana del cociente pareado réplica a réplica, con su intervalo de confianza del 95 % por bootstrap. Fuente: cálculos propios con los microdatos del IPM 2025 (DANE); entrega\_m34/datos\_m34/costo\_meta\_zona.csv.*

**Figura 10.** Costo de reducir M0 en cada zona según la información del Estado.

![Figura 10](figuras_m34/figura_M34-1_costo_contra_meta.png)

*Cómo se lee.* Cada línea es el costo de cumplir la meta del eje horizontal en las tres zonas a la vez. El eje vertical está en escala logarítmica, de modo que la distancia vertical entre dos líneas es el cociente de sus costos, es decir, el precio de la información. Las bandas son el intervalo de confianza del 95 % de la mediana.

*Qué se observa.* Con metas de hasta el 10 %, el Modelo 3 cuesta entre 5.5 y 12.9 veces lo que costaría con información perfecta, y con metas del 20 al 30 %, entre 3.1 y 4.1 veces. El Modelo 4 cuesta entre 3.4 y 8.8 veces la información perfecta y casi lo mismo que el Modelo 3. El placebo es el más caro desde la meta del 6 %.

*Interpretación.* La información vale más con metas modestas, que son las de los programas reales, porque permite elegir a quién atender primero. Pierde valor cuando hay que atender a casi todos los pobres de todas formas.

*Fuente: cálculos propios con los microdatos del IPM 2025 (DANE); entrega\_m34/datos\_m34/costo\_meta\_zona.csv y scripts/m34\_figuras\_paper.py.*

Cuatro resultados se destacan. El primero es que no saber quién es pobre resulta caro. Con la meta del 6 %, focalizar solo por zona cuesta $14.16 mil millones y con información perfecta $2.30 mil millones. Un sistema que permitiera identificar a quién atender, como un registro social actualizado, pagaría su costo mientras costara menos que la diferencia, unos $12 mil millones para ese solo programa.

El segundo es que, con la meta en cada zona, el tipo de hogar apenas mejora a la zona. El intervalo del cociente M4/M3 queda por debajo de 1 en 9 de las 15 metas, contiene el 1 en 3 y queda por encima en 3. Con metas del 10 al 24 %, el Modelo 4 cuesta entre un 4 y 11 % menos que el Modelo 3, pero esas cifras son medianas: el Modelo 4 es más barato en entre el 61 y 72 % de las réplicas, no en todas. Con metas del 26 al 30 % cuesta entre un 7 y 30 % más.

El tercero es que la demografía sí reemplaza a la geografía. Desde la meta del 6 %, el Modelo 4 cuesta entre un 14 y 38 % menos que el placebo. La razón es que la meta se exige en cada zona. El Modelo 3 puede dirigir la cobertura al rural disperso, donde la incidencia es la más alta (25.2 %), y lo hace: desde la meta del 8 % pone allí entre el 65 y 79 % del gasto (Tabla 6). Las celdas del placebo mezclan las tres zonas, así que entre el 50 y 62 % de su gasto cae en las cabeceras, y para cumplir la meta rural tiene que comprar cobertura en todas partes. Los tipos del Modelo 4 también mezclan zonas, pero se relacionan con las privaciones, sobre todo con las educativas, y eso le permite llegar a los pobres sin saber dónde viven.

El cuarto es que los errores de focalización son grandes. Según la meta, la mediana del error de inclusión está entre el 26 y 55 % en el Modelo 3 y entre el 18 y 50 % en el Modelo 4, y entre el 56 y 93 % de las personas pobres no recibe ninguna intervención en el Modelo 3 (Tabla 7).

La pregunta de investigación es sobre la incidencia H, que no es el objetivo de los Modelos 3 y 4. La Tabla 4 muestra que también baja en las tres zonas: con la meta del 10 %, H pasa de 9.45 % a 8.38 % con información perfecta, a 8.15 % con el Modelo 3 y a 8.15 % con el Modelo 4.

**Tabla 4.** Resultados de los Modelos 2, 3 y 4 y del placebo con la meta de reducción de M0 del 10 % en cada zona, en total y por zona.

| Escenario | Zona | Personas que salen | H | A | M0 | Costo (mil millones) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Línea base | Total | — | 9.45 % | 0.409 | 0.0387 | — |
|  | Cabecera | — | 6.21 % | 0.406 | 0.0252 | — |
|  | Centro poblado | — | 17.91 % | 0.386 | 0.0691 | — |
|  | Rural disperso | — | 25.18 % | 0.421 | 0.1060 | — |
| Modelo 2 | Total | 77,578 | 8.38 % | 0.415 | 0.0348 (−10.1 %) | 5.2 |
|  | Cabecera | 42,633 | 5.48 % | 0.413 | 0.0227 (−10.1 %) | 0.4 |
|  | Centro poblado | 7,228 | 16.04 % | 0.386 | 0.0619 (−10.4 %) | 0.4 |
|  | Rural disperso | 27,717 | 22.40 % | 0.426 | 0.0954 (−10.0 %) | 4.4 |
| Modelo 3 | Total | 94,311 | 8.15 % | 0.411 | 0.0334 (−13.6 %) | 28.7 |
|  | Cabecera | 60,168 | 5.18 % | 0.409 | 0.0211 (−16.2 %) | 6.0 |
|  | Centro poblado | 9,701 | 15.40 % | 0.386 | 0.0595 (−13.9 %) | 1.4 |
|  | Rural disperso | 25,918 | 22.58 % | 0.421 | 0.0952 (−10.3 %) | 20.6 |
| Modelo 4 | Total | 93,800 | 8.15 % | 0.405 | 0.0331 (−14.5 %) | 26.9 |
|  | Cabecera | 63,550 | 5.12 % | 0.403 | 0.0207 (−17.8 %) | 10.1 |
|  | Centro poblado | 9,213 | 15.52 % | 0.383 | 0.0598 (−13.4 %) | 3.3 |
|  | Rural disperso | 21,720 | 23.00 % | 0.414 | 0.0954 (−10.1 %) | 13.5 |
| Placebo | Total | 112,865 | 7.89 % | 0.410 | 0.0324 (−16.3 %) | 38.1 |
|  | Cabecera | 77,148 | 4.89 % | 0.407 | 0.0198 (−21.3 %) | 19.8 |
|  | Centro poblado | 9,388 | 15.48 % | 0.386 | 0.0596 (−13.6 %) | 4.4 |
|  | Rural disperso | 25,235 | 22.65 % | 0.420 | 0.0954 (−10.1 %) | 14.3 |

*Modelo 2 sin E-7, una sola solución. Modelos 3 y 4 y placebo: mediana de 100 réplicas en cada columna. Entre paréntesis, la reducción de M0 frente a la línea base. Las personas que salen son la diferencia entre las personas pobres iniciales y las finales. Fuente: cálculos propios con los microdatos del IPM 2025 (DANE); entrega\_m34/datos\_m34/H\_A\_M0\_por\_zona.csv, que trae las 15 metas y los percentiles 5 y 95 de H.*

En todas las metas y zonas, la incidencia baja al menos un 2.0 % en los Modelos 3 y 4 y en el placebo. Con la misma meta, los Modelos 3 y 4 suelen bajar H tanto o más que el Modelo 2: el Modelo 3 deja una incidencia total menor o igual que la del Modelo 2 en 13 de las 15 metas, y el Modelo 4 en 12. No es una ventaja, es el reflejo del costo. Sin saber quién es pobre, la cobertura avanza a saltos y no se puede detener justo en la meta, así que en algunas zonas M0 baja más de lo exigido. Con la meta del 10 %, por ejemplo, el Modelo 3 reduce M0 un 16.2 % en las cabeceras. El Modelo 2, en cambio, cumple la meta casi exactamente en cada zona y gasta lo mínimo. Por la misma razón, la intensidad se comporta distinto: con información perfecta, A sube en 15 de las 15 metas, porque el Modelo 2 saca primero a los hogares más cercanos al umbral, como se discutió en la sección 3; en los Modelos 3 y 4 el sorteo no distingue esa cercanía, y A cambia poco o incluso baja. Con la meta del 30 %, H baja un 31.6 % con información perfecta, un 30.5 % con el Modelo 3 y un 34.9 % con el Modelo 4 (Tabla 5).

**Tabla 5.** Resultados de los Modelos 2, 3 y 4 y del placebo con la meta de reducción de M0 del 30 % en cada zona, en total y por zona.

| Escenario | Zona | Personas que salen | H | A | M0 | Costo (mil millones) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Línea base | Total | — | 9.45 % | 0.409 | 0.0387 | — |
|  | Cabecera | — | 6.21 % | 0.406 | 0.0252 | — |
|  | Centro poblado | — | 17.91 % | 0.386 | 0.0691 | — |
|  | Rural disperso | — | 25.18 % | 0.421 | 0.1060 | — |
| Modelo 2 | Total | 216,136 | 6.46 % | 0.419 | 0.0270 (−30.1 %) | 32.4 |
|  | Cabecera | 114,499 | 4.25 % | 0.414 | 0.0176 (−30.2 %) | 3.3 |
|  | Centro poblado | 21,114 | 12.44 % | 0.389 | 0.0483 (−30.0 %) | 3.9 |
|  | Rural disperso | 80,523 | 17.10 % | 0.434 | 0.0742 (−30.0 %) | 25.1 |
| Modelo 3 | Total | 208,215 | 6.57 % | 0.406 | 0.0266 (−31.2 %) | 105.3 |
|  | Cabecera | 112,941 | 4.28 % | 0.409 | 0.0175 (−30.5 %) | 16.5 |
|  | Centro poblado | 21,093 | 12.44 % | 0.381 | 0.0476 (−31.0 %) | 17.7 |
|  | Rural disperso | 72,085 | 17.95 % | 0.407 | 0.0734 (−30.7 %) | 68.4 |
| Modelo 4 | Total | 238,662 | 6.15 % | 0.397 | 0.0244 (−36.8 %) | 138.6 |
|  | Cabecera | 143,214 | 3.76 % | 0.391 | 0.0147 (−41.6 %) | 72.0 |
|  | Centro poblado | 26,988 | 10.92 % | 0.385 | 0.0421 (−39.1 %) | 15.8 |
|  | Rural disperso | 69,342 | 18.23 % | 0.407 | 0.0742 (−30.0 %) | 50.0 |
| Placebo | Total | 236,053 | 6.19 % | 0.402 | 0.0249 (−35.6 %) | 160.2 |
|  | Cabecera | 139,635 | 3.82 % | 0.399 | 0.0154 (−39.0 %) | 82.7 |
|  | Centro poblado | 25,165 | 11.39 % | 0.381 | 0.0437 (−36.7 %) | 19.5 |
|  | Rural disperso | 71,155 | 18.04 % | 0.411 | 0.0742 (−30.1 %) | 58.3 |

*Igual que la Tabla 4. Fuente: cálculos propios con los microdatos del IPM 2025 (DANE); entrega\_m34/datos\_m34/H\_A\_M0\_por\_zona.csv.*

**Figura 11.** Incidencia final por zona según la meta de reducción de M0, Modelos 2, 3 y 4 y placebo.

![Figura 11](figuras_m34/figura_M34-3_H_por_zona.png)

*Cómo se lee.* Cada panel corresponde a una zona. Las líneas muestran la incidencia H final para cada meta de reducción de M0: la solución del Modelo 2 y la mediana de las réplicas en los Modelos 3 y 4 y el placebo. La línea punteada es la incidencia inicial de la zona.

*Qué se observa.* En las tres zonas, H baja con la meta en los cuatro escenarios. En el rural disperso, que parte de la incidencia más alta (25.2 %), el Modelo 2 baja H más que los demás desde las metas intermedias. En las cabeceras y los centros poblados ocurre lo contrario: los Modelos 3 y 4 y el placebo bajan H igual o más que el Modelo 2.

*Interpretación.* En el rural disperso, la meta obliga a los cuatro escenarios a reducir M0 casi lo mismo, pero el Modelo 2 lo logra sacando de la pobreza a los hogares más cercanos al umbral, así que con la misma reducción de M0 baja más la incidencia. En las otras zonas, los Modelos 3 y 4 sobrepasan la meta porque no pueden detener la cobertura justo donde haría falta. La información imperfecta no reduce menos la pobreza en total: la reduce de forma menos dirigida y mucho más cara.

*Fuente: cálculos propios con los microdatos del IPM 2025 (DANE); entrega\_m34/datos\_m34/H\_A\_M0\_por\_zona.csv y scripts/m34\_figuras\_paper.py.*

La Tabla 6 muestra en qué se gasta. Explica por qué el placebo es caro con metas por zona y cómo la meta por zona adelanta la entrada de la educación.

**Tabla 6.** Participación de la salud, la educación, las cabeceras y el rural disperso en el gasto de los Modelos 3 y 4 y del placebo (%).

| Meta m | Salud M3 | Educación M3 | Cabeceras M3 | Rural disperso M3 | Salud M4 | Educación M4 | Cabeceras M4 | Rural disperso M4 | Salud Plac. | Educación Plac. | Cabeceras Plac. | Rural disperso Plac. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 % | 93 | 6 | 50 | 37 | 91 | 8 | 52 | 35 | 95 | 4 | 62 | 27 |
| 6 % | 75 | 22 | 34 | 59 | 46 | 53 | 46 | 43 | 51 | 46 | 52 | 36 |
| 10 % | 67 | 32 | 23 | 73 | 24 | 75 | 38 | 50 | 27 | 72 | 50 | 38 |
| 14 % | 48 | 49 | 18 | 79 | 20 | 79 | 43 | 45 | 18 | 81 | 50 | 38 |
| 20 % | 27 | 70 | 13 | 73 | 13 | 87 | 44 | 44 | 13 | 86 | 50 | 38 |
| 24 % | 27 | 72 | 12 | 71 | 14 | 86 | 45 | 43 | 10 | 89 | 50 | 38 |
| 30 % | 19 | 77 | 18 | 65 | 22 | 75 | 52 | 37 | 8 | 91 | 51 | 37 |

*Promedio de la participación en las 100 réplicas. La salud incluye aseguramiento y barreras de acceso; los centros poblados completan el 100 % de las zonas. Ninguna corrida gasta más del 3 % en niñez, vivienda o trabajo. Fuente: cálculos propios con los microdatos del IPM 2025 (DANE); entrega\_m34/datos\_m34/gasto\_por\_zona\_y\_dimension.csv.*

Con la meta del 2 %, los tres escenarios gastan al menos el 91 % en salud. Con la del 10 %, el Modelo 4 ya gasta el 75 % en educación, el placebo el 72 % y el Modelo 3 el 32 %. A diferencia de los Modelos 1 y 2 (Figura 7), que concentran la inversión en educación de adultos y trabajo informal, los Modelos 3 y 4 casi no invierten en trabajo. Una explicación posible es que, sin saber quién es pobre, el aporte a pensión llegaría sobre todo a trabajadores informales de hogares no pobres, que son la mayoría de los informales.

**Tabla 7.** Errores de focalización de los Modelos 3 y 4 y del placebo según la meta.

| Meta m | Inclusión M3 | Inclusión M4 | Inclusión placebo | Exclusión M3 | Exclusión M4 | Exclusión placebo |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 % | 54 % | 46 % | 55 % | 93 % | 91 % | 94 % |
| 4 % | 55 % | 50 % | 55 % | 90 % | 86 % | 87 % |
| 6 % | 44 % | 32 % | 44 % | 86 % | 85 % | 84 % |
| 8 % | 38 % | 25 % | 40 % | 84 % | 81 % | 81 % |
| 10 % | 37 % | 18 % | 38 % | 81 % | 78 % | 78 % |
| 12 % | 37 % | 23 % | 36 % | 78 % | 72 % | 76 % |
| 14 % | 33 % | 28 % | 37 % | 75 % | 74 % | 73 % |
| 16 % | 30 % | 30 % | 36 % | 71 % | 71 % | 70 % |
| 18 % | 28 % | 28 % | 35 % | 68 % | 68 % | 68 % |
| 20 % | 27 % | 27 % | 35 % | 66 % | 65 % | 65 % |
| 22 % | 28 % | 26 % | 35 % | 64 % | 63 % | 62 % |
| 24 % | 26 % | 28 % | 35 % | 62 % | 57 % | 59 % |
| 26 % | 27 % | 31 % | 35 % | 60 % | 53 % | 56 % |
| 28 % | 27 % | 35 % | 34 % | 59 % | 50 % | 53 % |
| 30 % | 27 % | 37 % | 35 % | 56 % | 47 % | 50 % |

*Inclusión: fracción del gasto que llega a hogares no pobres. Exclusión: fracción de las personas pobres que no recibe ninguna intervención. Mediana de 100 réplicas. Fuente: cálculos propios con los microdatos del IPM 2025 (DANE); entrega\_m34/datos\_m34/costo\_meta\_zona.csv.*

#### Criterio de presupuesto fijo

La Tabla 8 presenta, para cada presupuesto, los parámetros de equidad que calcula el Modelo 1, las personas que saca de la pobreza con ellos y la fracción de réplicas en que los Modelos 3 y 4 y el placebo pueden cumplir r\_B en las tres zonas.

**Tabla 8.** Factibilidad de la tasa mínima de salida del Modelo 1 con información imperfecta.

| B | r_B | ρ_B | Salen con el Modelo 1 y r_B | Réplicas | Factibles con r_B (M3 / M4 / placebo) | Factibles con r_B y ρ_B |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 0.036 | no se alcanza | 87,034 | 100 | 0 % / 0 % / 0 % | no aplica |
| 5 | 0.073 | no se alcanza | 129,294 | 100 | 0 % / 0 % / 0 % | no aplica |
| 10 | 0.146 | no se alcanza | 154,347 | 100 | 0 % / 0 % / 0 % | no aplica |
| 25 | 0.238 | 0.165 | 214,879 | 30 | 0 % / 0 % / 0 % | 0 % / 0 % / 0 % |
| 50 | 0.344 | 0.215 | 281,588 | 30 | 0 % / 0 % / 0 % | 0 % / 0 % / 0 % |
| 100 | 0.522 | no se alcanza | 369,940 | 30 | 0 % / 0 % / 0 % | no aplica |

*B en mil millones de pesos de 2025. r\_B y ρ\_B se calcularon con las funciones del Modelo 1 (r por el codo y ρ por la regla de la brecha), sin E-7 ni SevEdu; son provisionales hasta la confirmación de los autores del Modelo 1. Con B = 2, 5, 10 y 100 la regla de la brecha no se alcanza y no hay ρ\_B. Fuente: cálculos propios con los microdatos del IPM 2025 (DANE); entrega\_m34/datos\_m34/factibilidad\_cobertura\_rB.csv y r\_rho\_referencias\_M1.csv.*

Con información imperfecta, la tasa mínima de salida del Modelo 1 no se puede cumplir: en las 1,350 corridas, la fracción de réplicas factibles es del 0 % en todos los presupuestos. Lo reportamos como resultado. La razón cambia con el presupuesto. Con B ≥ $25 mil millones, r\_B exige sacar de la pobreza a más personas de las que el Modelo 3 o el Modelo 4 logran sacar en total. Con B ≤ $10 mil millones el total sí alcanzaría, pero no su reparto: el sorteo no permite asegurar la fracción exigida en las tres zonas a la vez.

Para medir cuánta equidad territorial sí puede garantizar el Estado sin información individual, resolvimos en cada réplica el piso máximo garantizable, r\_max = max t sujeto a Σᵢ∈I(d) pᵢ yᵢ ≥ t · Pobres⁰\_d en cada zona d, con el presupuesto B y el mismo mecanismo de cobertura. Con información perfecta, r\_max es el extremo superior del rango en el que el Modelo 1 busca el codo, y por eso siempre es al menos r\_B.

**Tabla 9.** Piso por zona máximo garantizable según la información del Estado (% de los pobres de cada zona).

| B | r_B (Modelo 1) | Información perfecta | Modelo 3 | Modelo 4 | Placebo | Mejor réplica M3 | M3 / IP | M4 / IP |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 3.6 % | 5.9 % | 0.0 % (0.0 a 0.1) | 0.8 % (0.7 a 0.9) | 0.6 % (0.4 a 0.8) | 1.6 % | 0 % | 13 % |
| 5 | 7.3 % | 10.7 % | 1.5 % (1.1 a 1.7) | 2.4 % (2.3 a 2.5) | 2.7 % (2.5 a 2.8) | 4.9 % | 14 % | 22 % |
| 10 | 14.6 % | 16.5 % | 4.9 % (4.8 a 5.1) | 4.3 % (4.2 a 4.4) | 4.5 % (4.4 a 4.5) | 8.3 % | 30 % | 26 % |
| 25 | 23.8 % | 28.4 % | 8.8 % (8.4 a 9.3) | 8.7 % (8.2 a 9.0) | 7.4 % (7.2 a 7.7) | 13.1 % | 31 % | 30 % |
| 50 | 34.4 % | 39.1 % | 15.7 % (15.1 a 16.3) | 15.3 % (15.1 a 15.7) | 12.1 % (11.7 a 12.5) | 20.8 % | 40 % | 39 % |
| 100 | 52.2 % | 53.6 % | 29.9 % (28.9 a 30.4) | 24.3 % (24.1 a 24.5) | 20.3 % (20.0 a 20.6) | 32.2 % | 56 % | 45 % |

*B en mil millones de pesos de 2025. Información perfecta: un hogar por celda. Modelos 3 y 4 y placebo: mediana de 100 réplicas, con su intervalo de confianza del 95 % por bootstrap; también se reporta la mejor réplica del Modelo 3. Fuente: cálculos propios con los microdatos del IPM 2025 (DANE); entrega\_m34/datos\_m34/rmax\_piso\_garantizable.csv.*

**Figura 12.** Piso por zona máximo garantizable según el presupuesto y la información del Estado.

![Figura 12](figuras_m34/figura_M34-2_piso_garantizable.png)

*Cómo se lee.* Para cada presupuesto, la figura muestra la mayor fracción de los pobres de cada zona que el Estado puede asegurar que salga de la pobreza en las tres zonas a la vez. Las marcas horizontales son el r\_B que exige el Modelo 1.

*Qué se observa.* Con información perfecta, el piso garantizable siempre supera a r\_B. Sin información individual, siempre queda por debajo: en el Modelo 3 va de 0.0 % con B = $2 mil millones a 29.9 % con B = $100 mil millones, frente a 53.6 % con información perfecta. Ni la mejor réplica del Modelo 3 alcanza r\_B en ningún presupuesto.

*Interpretación.* La falta de información no solo encarece la reducción de la pobreza: también limita cuánta equidad territorial puede prometer el Estado. Con B = $100 mil millones, los Modelos 3 y 4 garantizan entre el 45 y 56 % del piso que garantizaría la información perfecta.

*Fuente: cálculos propios con los microdatos del IPM 2025 (DANE); entrega\_m34/datos\_m34/rmax\_piso\_garantizable.csv y scripts/m34\_figuras\_paper.py.*

---

## 5. Discusión

*Se agregan después del segundo párrafo de la sección 5 (implicaciones de política) y antes de los de limitaciones.*

Al retirar el supuesto de información perfecta, el panorama cambia más en el costo que en el resultado. Con la meta en cada zona, focalizar solo por zona cuesta entre 3.1 y 12.9 veces lo que cuesta con información perfecta, y focalizar también por tipo de hogar apenas reduce ese múltiplo. En los términos de Conconi et al. (2025), el presupuesto por desempeño tiene un costo oculto: la meta de M0 se puede cumplir sin información individual, pero a un costo varias veces mayor y con buena parte del gasto en hogares no pobres. Ese gasto no se pierde, porque esos hogares sí tenían la privación que se les quita, pero no mueve el IPM. Un programa evaluado por su cobertura puede verse exitoso y reducir poco la pobreza multidimensional. Con presupuesto fijo el efecto es más fuerte: la tasa mínima de salida por zona que el Modelo 1 cumple con información perfecta no la cumple ninguna réplica de los Modelos 3 y 4, y el piso que sí pueden garantizar con B = $100 mil millones es apenas entre el 45 y 56 % del que garantizaría la información perfecta. La asignación según necesidad, con garantías por zona, depende más de la información que el presupuesto por desempeño.

El precio de la información también puede leerse como el valor máximo de mejorar la focalización. Como la diferencia relativa es mayor con metas modestas y presupuestos pequeños, el argumento pesa más para los programas acotados. El Modelo 4 y su placebo separan dos fuentes de mejora que en la práctica se confunden: la granularidad, que ayuda aunque las celdas no signifiquen nada, y el contenido de la partición, que solo ayuda si se relaciona con la privación. Con metas por zona, la granularidad sin contenido estorba, porque las celdas al azar mezclan las zonas. Antes de focalizar un programa por tipo de hogar hay que comprobar que esos tipos discriminan la privación que el programa ataca.

*Se agrega al final de los párrafos de limitaciones.*

Los Modelos 3 y 4 tienen limitaciones propias. La base no identifica municipios, así que la focalización geográfica solo distingue tres zonas; con celdas municipales, el Modelo 3 se acercaría a la información perfecta. El modelo elige la cobertura conociendo el sorteo de cada réplica, como en Hamie et al. (2024), lo que hace optimistas sus cifras. Los dos sesgos van en sentidos opuestos: las celdas gruesas inflan el precio de la información y conocer el sorteo lo reduce. Además, los sorteos de un hogar son independientes entre indicadores, algunas celdas tienen menos de 10 hogares privados en la muestra, y la comparación se hace sin la cobertura obligatoria ni la severidad educativa, que los Modelos 3 y 4 no pueden representar.

---

## Referencias

*Se agregan a la lista de referencias.*

- Alkire, S., y Foster, J. (2011). Counting and multidimensional poverty measurement. *Journal of Public Economics*, 95(7-8), 476-487. https://doi.org/10.1016/j.jpubeco.2010.11.006
- Hamie, C., Hlasny, V., y Jouni, M. (2024). *Multidimensional poverty alleviation: Policy optimization and impact simulation* (Working Paper 1742). Economic Research Forum. https://erf.org.eg/publications/multidimensional-poverty-alleviation-policy-optimization-and-impact-simulation/
- Huangfu, Q., y Hall, J. A. J. (2018). Parallelizing the dual revised simplex method. *Mathematical Programming Computation*, 10(1), 119-142. https://doi.org/10.1007/s12532-017-0130-5
- Mitchell, S., O'Sullivan, M., y Dunning, I. (2011). PuLP: A linear programming toolkit for Python. University of Auckland. https://optimization-online.org/2011/09/3178/
- Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, 12, 2825-2830. https://jmlr.org/papers/v12/pedregosa11a.html

---

## Apéndice 1

*Las Tablas A2 y A3 ocupan el lugar que el Apéndice 1 dejó para los Modelos 3 y 4 («las Tablas A2 y A3 del original, de los Modelos 3 y 4, no se incluyen»). La derivación y las Tablas A9 a A11 se agregan al final del apéndice.*

**Tabla A2.** Nomenclatura del Modelo 3.

| Símbolo | Tipo | Definición |
| --- | --- | --- |
| Ī, I | Conjunto | Todos los hogares de la muestra (3,732) y los hogares pobres de la línea base (523) |
| J, Jᴵ | Conjunto | Los 15 indicadores y los intervenibles en un año |
| D | Conjunto | Las tres zonas de P3; d(i) es la zona del hogar i |
| F(j, d) | Conjunto | Cortes admisibles del par (j, d) |
| wⱼ, Mᵢⱼ, HWᵢ, HSᵢ, pᵢ, cᵢ⁰ | Parámetro original o calculado | Como en el Modelo 1 |
| cᵢⱼ | Parámetro calculado | Costo de quitar la privación j al hogar i: costo unitario de la zona × uᵢⱼ × HWᵢ |
| Vᵢⱼ | Parámetro calculado | Población que atiende el par (i, j): uᵢⱼ · HWᵢ |
| Den(j, d) | Parámetro calculado | Población privada en el indicador j dentro de la zona d |
| Rᵢⱼ | Parámetro calculado | Sorteo uniforme del par (i, j), distinto en cada réplica |
| m, Pob\_d, M0\_d⁰ | Parámetro | Meta de reducción de M0; población y M0 inicial de la zona d |
| θ(j, d) | Variable externa | Cobertura del indicador j en la zona d |
| xᵢⱼ, yᵢ | Variable interna binaria | Se quita la privación j al hogar i; el hogar pobre i sale de la pobreza |
| Gᵢ, E(j, d) | Variable interna continua | Contribución censurada del hogar i a M0; gasto en el indicador j dentro de la zona d |
| z(j, d, c) | Variable interna binaria | Se elige el corte c en el par (j, d) |

*Fuente: elaboración propia con base en la Tabla A2 de Hamie et al. (2024).*

**Tabla A3.** Nomenclatura del Modelo 4 (además de la del Modelo 3).

| Símbolo | Tipo | Definición |
| --- | --- | --- |
| T, t(i) | Conjunto | Los cuatro tipos de hogar y el tipo del hogar i |
| V, U | Conjunto | Bienes públicos (acueducto y alcantarillado) y bienes privados (los otros 13 indicadores) |
| g(i, j) | Parámetro calculado | Celda del par (i, j): d(i) si j ∈ V y t(i) si j ∈ U |
| θ(j, g), E(j, g), z(j, g, c) | Variable | Como en el Modelo 3, por celda g |

*Fuente: elaboración propia con base en la Tabla A3 de Hamie et al. (2024).*

**Censura de Alkire y Foster.** El original linealiza la censura con dos binarias por hogar y cinco restricciones (Lin 1 a Lin 5). En los Modelos 3 y 4 bastan Lin 1 a Lin 3 (Restricción₃ 4 a Restricción₃ 6), con sᵢ < k escrito como sᵢ ≤ 0.33, que es exacto porque todos los pesos son múltiplos de 0.01. Omitir Lin 4 y Lin 5 no cambia el óptimo: si se toma una solución factible sin ellas y se redefine yᵢ como 1 exactamente cuando sᵢ ≤ 0.33, Gᵢ no aumenta, la meta se sigue cumpliendo y el gasto es el mismo. El big-M pᵢ basta porque sᵢ ≤ 1; con una constante global la relajación lineal se afloja y el solver no cierra la brecha. La cota Gᵢ ≥ 0 es indispensable: sin ella la meta se cumple con contribuciones negativas.

**Mecanismo de cobertura.** Para cada par privado, el original introduce dos binarias y escribe Restricción₃ 3 como Lin 6 a Lin 10. Las verificamos rama por rama: si la primera binaria vale 0, el hogar sale de la privación y Rᵢⱼ ≤ θ; si vale 1, sigue privado y θ ≤ Rᵢⱼ − ε. Las dos ramas cubren todos los casos sin solaparse. Como todas las cantidades están entre 0 y 1, basta big-M igual a 1, y con ese valor la binaria coincide con 1 − xᵢⱼ, así que las dos binarias se eliminan. La desigualdad estricta θ < R se escribe θ ≤ R − ε con ε = 10⁻⁶, el mismo valor de la definición de F(j, d).

**Equivalencia de la reformulación por cortes.** Tomemos una solución factible de la formulación directa y un par (j, d). Por Restricción₃ 3, los hogares curados son los que tienen Rᵢⱼ ≤ θ(j, d), un prefijo del orden de tamaño c. Por Restricción₃ 2, θ(j, d) es la cobertura de esos c primeros. El último curado cumple R₍c₎ ≤ θ y el primero no curado cumple θ ≤ R₍c₊₁₎ − ε, así que c ∈ F(j, d), y con z(j, d, c) = 1 la Restricción₃ 9 reproduce las mismas xᵢⱼ con el mismo gasto. Recíprocamente, si c ∈ F(j, d), curar a los c primeros y fijar θ como su cobertura cumple Restricción₃ 2 y Restricción₃ 3 por la definición de F(j, d). Las restricciones de censura y meta dependen solo de xᵢⱼ, así que se cumplen en las dos formulaciones a la vez.

**Tabla A9.** Razón entre la incidencia de cada privación en la celda más privada y en la menos privada, entre zonas y entre tipos de hogar.

| Privación | Entre zonas | Entre tipos de hogar |
| --- | ---: | ---: |
| Acueducto (bien público) | 14.5 | 4.1 |
| Alcantarillado (bien público) | 4.7 | 3.2 |
| Inasistencia escolar | 4.8 | 51.7 |
| Hacinamiento | 2.7 | 26.6 |
| Atención integral a la primera infancia | 2.2 | solo existe en hogares con niños |
| Aseguramiento en salud | 1.9 | 1.9 |
| Barreras de acceso a salud | 2.7 | 1.8 |

*Personas expandidas, k = 4. La atención integral a la primera infancia solo puede existir en hogares con niños menores de 5 años. Fuente: cálculos propios con los microdatos del IPM 2025 (DANE); entrega\_m34/datos\_m34/discriminacion\_privaciones.csv.*

**Tabla A10.** Tipos de hogar del Modelo 4 (k = 4).

| Tipo de hogar | Hogares en la muestra | Incidencia H |
| --- | ---: | ---: |
| Adultos sin dependientes | 1,389 | 3.7 % |
| Adultos mayores | 1,038 | 11.8 % |
| Con hijos escolares | 849 | 9.1 % |
| Primera infancia | 456 | 16.1 % |

*k-medias ponderado por el factor de expansión, con semilla fija. Fuente: cálculos propios con los microdatos del IPM 2025 (DANE); entrega\_m34/datos\_m34/tipos\_hogar.csv.*

**Tabla A11.** Prueba de granularidad máxima: Modelo 3 con un hogar por celda frente a la información perfecta.

| Prueba | Modelo 3 con un hogar por celda | Información perfecta | Diferencia | Resultado |
| --- | ---: | ---: | ---: | ---: |
| G1 meta por zona 2 % | 0.47 | 0.47 | 0.00 % | pasa |
| G1 meta por zona 6 % | 2.30 | 2.30 | 0.00 % | pasa |
| G1 meta por zona 10 % | 5.17 | 5.17 | 0.00 % | pasa |
| G1 meta por zona 20 % | 16.11 | 16.11 | 0.00 % | pasa |
| G1 meta por zona 30 % | 32.49 | 32.37 | 0.38 % | pasa |
| G2 piso por zona r_B, B = 2 | 87,034 | 87,034 | 0.00 % | pasa |
| G2 piso por zona r_B, B = 5 | 129,294 | 129,294 | 0.00 % | pasa |
| G2 piso por zona r_B, B = 10 | 154,347 | 154,347 | 0.00 % | pasa |
| G2 piso por zona r_B, B = 25 | 212,791 | 214,879 | -0.97 % | pasa |
| G2 piso por zona r_B, B = 50 | 279,498 | 281,588 | -0.74 % | pasa |
| G2 piso por zona r_B, B = 100 | 368,751 | 369,940 | -0.32 % | pasa |

*G1 compara el costo con meta en cada zona contra el Modelo 2 (mil millones de pesos de 2025). G2 compara las personas que salen con r\_B contra el Modelo 1. La diferencia admitida es la del supuesto 2 (ciclo CLEI). Fuente: cálculos propios con los microdatos del IPM 2025 (DANE); entrega\_m34/datos\_m34/validacion\_granularidad\_maxima.csv.*

---

## Apéndice 2: resultados adicionales

*Se agrega al final del Apéndice 2, después de la Tabla A8 y del párrafo del costo de la equidad territorial.*

**Sin equidad territorial: meta global y r = 0.** Como sensibilidad de los Modelos 3 y 4, repetimos la comparación sin restricciones de equidad territorial: con la meta de M0 global y con r = 0. Con la meta global del 10 %, la información perfecta cuesta $1.32 mil millones, y con la misma meta en cada zona, $5.17 mil millones. Con meta global, el Modelo 3 cuesta entre 6.2 y 16.9 veces la información perfecta con metas de hasta el 10 %. El Modelo 4 es más barato que el Modelo 3, pero hasta la meta del 18 % cuesta lo mismo que el placebo: sin la exigencia por zona, cualquier partición más fina ayuda.

**Tabla A12.** Costo de reducir M0 con una meta global según la información del Estado (mil millones de pesos de 2025).

| Meta m | Modelo 2 | Modelo 3 | Modelo 4 | Placebo | Precio M3 | Precio M4 | M4/placebo (IC 95 %) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 % | 0.18 | 2.22 | 1.57 | 1.58 | 12.0 | 8.5 | 1.11 (0.94 a 1.25) |
| 6 % | 0.51 | 5.66 | 3.24 | 3.44 | 11.2 | 6.4 | 0.90 (0.85 a 0.95) |
| 10 % | 1.32 | 8.27 | 6.16 | 6.01 | 6.2 | 4.7 | 1.02 (0.98 a 1.08) |
| 14 % | 2.37 | 10.12 | 9.25 | 9.17 | 4.3 | 3.9 | 1.01 (0.98 a 1.04) |
| 18 % | 4.26 | 14.22 | 14.18 | 13.69 | 3.3 | 3.3 | 1.04 (1.00 a 1.06) |
| 20 % | 6.47 | 22.83 | 20.73 | 21.75 | 3.5 | 3.2 | 0.93 (0.89 a 0.96) |
| 24 % | 12.49 | 48.74 | 34.48 | 45.16 | 3.9 | 2.8 | 0.75 (0.72 a 0.77) |
| 30 % | 24.40 | 84.36 | 61.08 | 82.77 | 3.5 | 2.5 | 0.74 (0.72 a 0.76) |

*Mediana de 100 réplicas. Corridas del 10 de noviembre, sin E-7 ni SevEdu. Fuente: cálculos propios con los microdatos del IPM 2025 (DANE); entrega\_m34/datos\_m34/sens\_meta\_global\_costos.csv.*

**Tabla A13.** Personas que salen de la pobreza con presupuesto fijo y r = 0 según la información del Estado.

| B | Réplicas | Modelo 1 | Modelo 3 | Modelo 4 | Placebo | M3 / M1 | M4 / M1 | M4/M3 (IC 95 %) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 100 | 97,286 | 12,424 | 18,173 | 19,805 | 13 % | 19 % | 1.14 (0.96 a 1.22) |
| 5 | 100 | 135,908 | 33,736 | 61,269 | 63,457 | 25 % | 45 % | 1.86 (1.64 a 2.04) |
| 10 | 100 | 161,254 | 95,607 | 103,679 | 105,663 | 59 % | 64 % | 1.10 (1.04 a 1.30) |
| 25 | 30 | 217,910 | 141,688 | 146,118 | 144,737 | 65 % | 67 % | 1.03 (1.02 a 1.04) |
| 50 | 30 | 284,099 | 166,850 | 186,268 | 170,098 | 59 % | 66 % | 1.12 (1.11 a 1.12) |
| 100 | 30 | 370,508 | 218,204 | 242,657 | 222,610 | 59 % | 65 % | 1.11 (1.10 a 1.12) |

*B en mil millones de pesos de 2025. Modelo 1 con r = 0, sin E-7 ni SevEdu. Mediana de las réplicas, con el intervalo de confianza del 95 % del cociente pareado. Corridas del 10 de noviembre. Fuente: cálculos propios con los microdatos del IPM 2025 (DANE); entrega\_m34/datos\_m34/sens\_r0\_personas\_que\_salen.csv y sens\_r0\_info\_perfecta\_M1.csv.*

Sin piso por zona, los Modelos 3 y 4 sí son factibles. El Modelo 3 saca de la pobreza entre el 13 y 65 % de las personas que saldrían con el Modelo 1, y el Modelo 4 entre el 19 y 67 %.

**Número de tipos de hogar.** La elección de k se apoyó en un análisis con 50 réplicas pareadas para k de 2 a 8. Se hizo con una versión simplificada de los costos (una intervención por hogar, uᵢⱼ = 1) y sin equidad territorial, así que se lee por su forma y no por sus cifras. Con k = 2, el Modelo 4 saca de la pobreza 0.71 veces las personas del Modelo 3: la partición separa los hogares por tamaño, que casi no se relaciona con la pobreza. De k = 3 a k = 4 la ganancia es grande, y desde ahí se aplana (1.92 veces con k = 4 y 1.93 con k = 5). Con k = 8 hay celdas con menos de 10 hogares privados, donde el sorteo deja de representar una focalización por tipo. Elegimos k = 4 con dos criterios: que menos del 15 % de los pares (indicador, celda) tenga menos de 10 hogares privados, y que al pasar a k + 1 la ganancia sea marginal.

**Tabla A14.** Personas que salen de la pobreza con B = $10 mil millones según el número de tipos de hogar del Modelo 4.

| Partición del Modelo 4 | Personas que salen con B = 10 | Veces el Modelo 3 (mediana) |
| --- | ---: | ---: |
| Modelo 3 | 31,066 | 1.00 |
| k = 2 | 21,836 | 0.71 |
| k = 3 | 44,626 | 1.19 |
| k = 4 (caso base) | 61,232 | 1.92 |
| k = 5 | 61,427 | 1.93 |
| k = 6 | 64,677 | 1.99 |
| k = 8 | 76,248 | 2.44 |

*Costos simplificados (uᵢⱼ = 1), sin equidad territorial, 50 réplicas pareadas. Fuente: cálculos propios con los microdatos del IPM 2025 (DANE); entrega\_m34/datos\_m34/sens\_k\_u1.csv.*

---

## Glosario EN–ES

*Se agregan a la tabla del glosario.*

| English term | Español | Use in context |
| --- | --- | --- |
| price of information | precio de la información | *The price of information is the cost ratio against the first best.* |
| coverage | cobertura | *The State chooses coverage by zone, not which households are served.* |
| random draw | sorteo | *A random draw decides which deprived households are served.* |
| inclusion error | error de inclusión | *The inclusion error is the share of spending on non-poor households.* |
| exclusion error | error de exclusión | *The exclusion error is the share of poor people who receive nothing.* |
| targeting cell | celda de focalización | *Model 4 targets private goods by household type.* |
| placebo partition | partición placebo | *A placebo with shuffled household types keeps the cells but not their content.* |
| maximum guaranteed floor | piso máximo garantizable | *Without household data, the guaranteed floor stays below r_B.* |
