# Asignación óptima de la inversión pública para reducir la pobreza multidimensional en Antioquia (borrador)

10 de noviembre de 2026 · Martín Quijano Hoyos

## Resumen

Este estudio desarrolla dos modelos de programación lineal entera mixta para orientar la asignación de inversión pública destinada a reducir la pobreza multidimensional en Antioquia. Para ello, utiliza los microdatos del IPM 2025 del DANE y costos unitarios respaldados por fuentes oficiales. El Modelo 1, inspirado en los modelos de Hamie et al. (2024), maximiza el número de personas que salen de la pobreza bajo un presupuesto fijo e incorpora tres condiciones de equidad: un techo de severidad, una tasa mínima de salida en cada zona y un techo de severidad educativa. El Modelo 2, por su parte, determina el costo mínimo de alcanzar una meta de reducción del índice ajustado M0 en cada zona, considerando la cobertura escolar obligatoria como piso de gasto. Con $424 mil millones, el Modelo 1 permite que 581,452 personas salgan de la pobreza (85.1 % de la población pobre), reduce la incidencia del 9.45 % al 1.41 % y disminuye la severidad un 47.4 %. La intensidad media de quienes permanecen pobres no aumenta en el agregado departamental, aunque sí lo hace en el rural disperso. Por su parte, el Modelo 2 alcanza una reducción de M0 del 85 % con $420.3 mil millones. Excepto con presupuestos muy bajos, ambos mecanismos producen reducciones de M0 similares para un mismo gasto; por ello, su elección depende principalmente de las garantías distributivas que se busque establecer. En los dos casos, la inversión se concentra en educación de adultos, trabajo informal y educación de niños. Los resultados muestran estabilidad ante los supuestos de costo evaluados.

**Palabras clave:** pobreza multidimensional, método Alkire-Foster, optimización entera mixta, asignación del gasto público, equidad territorial, Antioquia.

**Clasificación JEL:** I32, I38, H53, C61.

## 1. Motivación

*Replica la §1 de Hamie et al. (2024). Por ahora solo está la pregunta de investigación; el resto se escribe párrafo por párrafo. El marco de política (asignación según necesidad vs presupuesto por desempeño) viene del OPHI Briefing 63.*

En Colombia, la desigualdad del ingreso y de la riqueza sigue siendo elevada. En 2025, el coeficiente de Gini del ingreso fue de 0,531 ([DANE, 2026](https://www.dane.gov.co/files/operaciones/PM/bol-PM-2025.pdf)), mientras que las estimaciones basadas en datos administrativos tributarios sitúan la participación del 1 % más rico entre el 37 % y el 40,6 % de la riqueza nacional ([Carranza, De Rosa y Flores, 2023](https://publications.iadb.org/publications/english/document/Wealth-Inequality-in-Latin-America.pdf), con datos de Londoño-Vélez y Ávila-Mahecha, 2021). Estas diferencias también se manifiestan entre territorios. Según los microdatos IPM 2025 del DANE, la incidencia de la pobreza multidimensional en Antioquia alcanza el 6.21 % en las cabeceras y el 25.18 % en el rural disperso. La distancia se mantiene al considerar el IPM ajustado: en el rural disperso llega a 0.1060, un valor 4.2 veces superior al de las cabeceras (0.0252).

En este contexto, la forma en que el Estado distribuye los recursos entre programas, hogares y territorios es decisiva para la reducción de la pobreza. Conconi et al. ([2025](https://ophi.org.uk/sites/default/files/2025-11/B63_Budget_Allocation_2025.pdf), p. 4–7) distinguen dos mecanismos de asignación basados en un IPM nacional. El primero, la asignación según necesidad, distribuye los recursos escasos atendiendo a las condiciones específicas de cada región y grupo poblacional. El segundo, el presupuesto por desempeño, establece la reducción del IPM como prioridad y la traduce en metas concretas para los programas. A partir de esta distinción, el estudio plantea dos modelos de optimización complementarios: el Modelo 1 distribuye un presupuesto fijo entre los hogares pobres, garantizando una tasa mínima de salida en cada zona; el Modelo 2 determina el costo mínimo de alcanzar una meta de reducción de M0 en cada zona.

Sin embargo, maximizar únicamente el número de personas que salen de la pobreza introduce un sesgo en la asignación. Cuando el presupuesto es fijo, resulta menos costoso atender a los hogares próximos al umbral, pues suele ser suficiente eliminar una o dos privaciones. En Antioquia, el 49 % de los hogares pobres de la muestra, que representan el 44 % de las personas pobres, se encuentra a 0.05 o menos del umbral k = 1/3. La consecuencia se observa al resolver el modelo sin restricciones de equidad: con $424 mil millones (cifra justificada en «Presupuesto de referencia», sección 3), el 49 % de los hogares con puntaje inicial de 0.45 o más no recibe ninguna intervención (Figura 2B). Aunque el plan reduce la incidencia, la intensidad entre quienes permanecen en pobreza aumenta de A₀ = 0.409 a A = 0.440. Por tanto, el problema no consiste en que aumenten las privaciones de esos hogares, sino en que el modelo concentra las salidas entre quienes ya estaban más cerca del umbral, mientras deja sin atención a una parte considerable de los más privados.

&#91;image: Figura 1. Distribución del puntaje de privación de los hogares pobres de Antioquia\]

*Figura 1. Personas en hogares pobres según el puntaje de privación del hogar, Antioquia, 2025. La línea continua marca el umbral de pobreza (k = 1/3) y la discontinua, la intensidad inicial (A₀ = 0.409). En naranja, los hogares a 0.05 o menos del umbral: son los más baratos de sacar de la pobreza y los que un modelo que maximiza H atiende primero. Fuente: cálculos propios con los microdatos IPM 2025 del DANE (523 hogares pobres, ponderados por factor de expansión y tamaño del hogar).*

&#91;image: Figura 2. Puntaje de privación de cada hogar pobre antes y después de intervenir\]

*Figura 2. Puntaje de privación de los 523 hogares pobres de Antioquia, ordenados por su puntaje inicial (cada hogar ocupa la misma posición en los tres paneles), con un presupuesto de $424 mil millones. A: antes de intervenir. B: después del plan que maximiza H sin restricciones de equidad (592,196 personas salen de la pobreza). C: después del Modelo 1, con techo de severidad, equidad por zona y techo de SevEdu (581,452 personas). La línea horizontal es el umbral de pobreza k = 1/3. De los hogares con puntaje inicial ≥ 0.45, el 49 % no recibe ninguna intervención en B y el 32 % en C (porcentajes sobre hogares de la muestra, sin ponderar). Fuente: cálculos propios con los microdatos IPM 2025 del DANE.*

Para mitigar ese sesgo, incorporamos a la formulación de Hamie et al. (2024) tres condiciones: un techo de severidad de la pobreza, una tasa mínima de salida en cada zona y un techo de severidad educativa. Con ellas, la intensidad de quienes permanecen en pobreza no aumenta (A ≤ A₀) y la severidad disminuye un 47.4 %. Este resultado implica una compensación respecto al modelo sin restricciones: salen de la pobreza 10,744 personas menos, una diferencia del 1.8 %, a cambio de una distribución de las intervenciones que atiende también la intensidad de las privaciones.

**Pregunta de investigación.** ¿Cuál es la asignación óptima de intervenciones públicas que reduce la incidencia de la pobreza multidimensional (H) en Antioquia? (Aprobada por Martín, 11-nov-2026.)

Dos formulaciones complementarias la responden:

- **Modelo 1 (presupuesto fijo).** Dado un presupuesto anual B, maximizar el número de personas que salen de la pobreza, sujeto a un techo de severidad y a una tasa mínima de salida en cada zona.
- **Modelo 2 (meta).** Dada una meta de reducción del IPM ajustado M0 en cada zona, minimizar el costo anual total.

**Medidas que se reportan en cada solución:** incidencia H, intensidad A, IPM ajustado M0 = H × A, severidad (FGT α = 2 sobre el puntaje sin censurar) y severidad educativa (SevEdu), en total y por zona.

*\[Párrafo de hallazgos principales: se escribe después de la sección 4.\]*

El resto del documento se organiza así. La sección 2 presenta la lógica de los dos escenarios de política modelados y sus supuestos. La sección 3 desarrolla sus formulaciones matemáticas y su aplicación a los microdatos de Antioquia. La sección 4 presenta los resultados principales. La sección 5 discute los hallazgos y ofrece recomendaciones de política.

**Nota para el texto.** H es el objetivo del Modelo 1 y un resultado del Modelo 2, cuyo objetivo es el costo mínimo sujeto a una meta de M0. El texto debe decirlo explícitamente. Si más adelante entran los Modelos 3 y 4, hay que verificar que H también baje en sus resultados.

## 2. Escenarios de política modelados

*Replica la §2 de Hamie et al.: la narrativa de cada modelo, sin ecuaciones.*

### Supuestos y salvedades de los modelos

Los modelos de este estudio se basan en los siguientes supuestos. Los supuestos 1 a 7 adaptan los de Hamie et al. (2024); los supuestos 8 a 11 son propios.

1. Los supuestos normativos del IPM se mantienen constantes durante el horizonte de la intervención: pesos oficiales del DANE y umbral de pobreza k = 1/3.
2. Los indicadores son independientes, salvo las dependencias que se modelan de forma explícita: un ciclo CLEI cuenta como asistencia escolar; las decisiones por niño ligan el rezago escolar, la inasistencia y la transferencia de Renta Ciudadana; y un ciclo CLEI de un adulto puede eliminar a la vez las privaciones de logro educativo y de analfabetismo del hogar.
3. Solo cambia la situación de los hogares intervenidos. Los demás hogares no se ven afectados, es decir, no hay error de inclusión en la focalización.
4. No todas las privaciones son intervenibles en el horizonte del modelo. Con las reglas oficiales, la privación de rezago escolar no se elimina en un año, y el desempleo de larga duración no se interviene cuando la encuesta no identifica a la persona desocupada.
5. El costo de eliminar una privación es constante por unidad (costo marginal constante) y corresponde a valores oficiales de 2025 (Tabla A6). Cada privación se paga por separado, aunque una sola obra pudiera eliminar varias.
6. Los parámetros de política están dados en cada corrida: el presupuesto B en el Modelo 1 y la meta de reducción de M0 en el Modelo 2. En cada caso se evalúa su factibilidad.
7. Los hogares no pobres no pasan a ser pobres. Por eso solo se modelan los 523 hogares pobres de la línea base.
8. El horizonte de planeación es de un año.
9. La transferencia de Renta Ciudadana logra el regreso escolar con una tasa de cumplimiento p = 0.369, la proporción de hogares que cumplió todas las corresponsabilidades en el ciclo 4 de 2025 (\[Prosperidad Social\](https://prosperidadsocial.gov.co/Noticias/sobre-las-corresponsabilidades-de-renta-ciudadana-en-el-cuarto-ciclo-de-2025/)). Por eso el costo esperado de un regreso logrado es $3.0 M / p.
10. Por el artículo 67 de la Constitución, el Estado está obligado a brindar educación a todos los niños entre los 5 y los 15 años. El DANE mide el rezago escolar solo a partir de los 7 años, así que, por falta de información, el modelo solo obliga a escolarizar a los niños de 7 a 15 años con rezago escolar que no asisten al colegio. Los que no asisten y no tienen rezago no están obligados, aunque el modelo puede intervenirlos si le conviene. Este vacío de información se tendrá en cuenta en las mejoras del modelo (sección 5).
11. En la severidad educativa (SevEdu), la cohorte de 215 niños con rezago se mantiene fija, aunque alguno cumpla 18 años durante el horizonte.

### Modelo 1: modelo por hogar con presupuesto fijo y techo de severidad

El Modelo 1 parte de una situación habitual para la gestión pública: se dispone de un presupuesto anual B y es necesario decidir qué hogares pobres atender y qué privaciones eliminar para conseguir que salga de la pobreza el mayor número posible de personas. Al igual que el Modelo 2 de Hamie et al. (2024), supone que el Estado conoce las privaciones de cada hogar pobre y puede intervenirlas de manera individual. Por ello, sus resultados representan un techo teórico de lo alcanzable bajo información perfecta. Los microdatos del IPM 2025 del DANE permiten identificar cuáles de los 15 indicadores afectan a cada hogar de la muestra, y el factor de expansión (FEX\_C) establece cuántos hogares de Antioquia representa. Sin embargo, al tratarse de una muestra anonimizada, esos datos permiten caracterizar perfiles de privación, pero no localizar a los hogares. Para ejecutar las intervenciones, el Estado requeriría un registro nominal que identificara las mismas privaciones. El costo de cada intervención depende del indicador, de la zona y del número de personas afectadas dentro del hogar.

El objetivo de maximizar las salidas favorece, por su menor costo de atención, a los hogares situados cerca del umbral de pobreza (Figura 1). Para evitar que esta ventaja determine por completo la asignación, el modelo incorpora tres condiciones de equidad. La primera es un techo de severidad: exige reducir al menos una fracción ρ de la suma ponderada de los cuadrados de los puntajes de los hogares pobres. Al elevar los puntajes al cuadrado, las privaciones más intensas adquieren mayor peso, de modo que también se incentivan intervenciones en hogares que no alcanzan a salir de la pobreza. La segunda condición impone una tasa mínima de salida r en cada zona, mientras que la tercera establece un techo de severidad educativa orientado a atender a los niños con mayor rezago escolar.

Los valores de ρ y r se determinan en cada corrida a partir de los datos, mediante dos criterios establecidos por los autores: la regla de la brecha para ρ y el criterio del codo para r (sección 3). La primera identifica el menor valor de ρ para el cual la intensidad de quienes siguen pobres no supera la inicial (A ≤ A₀). Si ninguno de los valores evaluados satisface esta condición, se adopta el techo de severidad más exigente entre ellos. El segundo criterio localiza el codo de la curva que relaciona las personas que salen de la pobreza con la tasa mínima r. Una vez fijados ambos parámetros, el problema se resuelve en dos etapas: primero se maximiza el número de personas que salen de la pobreza y, entre los planes que alcanzan ese resultado, se selecciona el que produce la menor severidad.

Esta formulación requiere una capacidad estatal considerable: identificar las privaciones de cada hogar, entregar exactamente la intervención correspondiente y limitar la focalización a la población pobre. Bajo estos supuestos, no se presentan errores de inclusión ni de exclusión. Ningún hogar no pobre recibe recursos (error de inclusión), y todos los hogares que el modelo selecciona efectivamente reciben la intervención (error de exclusión). Por tanto, cuando un hogar pobre queda sin atender, ello responde a la decisión óptima bajo el presupuesto disponible y no a una falla de focalización.

### Modelo 2: modelo por hogar de costo mínimo (*first best*)

El Modelo 2 invierte la pregunta de asignación. En lugar de partir de un presupuesto disponible, el gobierno define una meta —por ejemplo, reducir en un 10 % el IPM ajustado M0 de Antioquia— y busca el costo mínimo necesario para alcanzarla. Esta formulación replica el Modelo 2 de Hamie et al. (2024) y conserva los hogares, las reglas de intervención y los costos oficiales del Modelo 1. La diferencia central es, por tanto, la relación entre los parámetros y el objetivo: el presupuesto, que en el primer modelo es un límite, aquí se convierte en el resultado de la optimización.

La elección de M0, en vez de H, como indicador de la meta responde a la información que aporta cada medida. Dado que M0 = H × A, puede disminuir tanto cuando un hogar sale de la pobreza como cuando uno que continúa siendo pobre reduce sus privaciones. Una meta basada únicamente en H reconocería solo la primera mejora y reproduciría el incentivo a concentrar las intervenciones cerca del umbral descrito en la sección 1. Aunque M0 incorpora las dos vías de reducción, no otorga prioridad adicional a los hogares más privados: al ser lineal en el puntaje censurado (equivalente a α = 1), una reducción de 0.10 en un hogar con puntaje 0.60 cuenta lo mismo que en uno con 0.45, siempre que ambos sigan siendo pobres. Esto ayuda a interpretar los resultados del Modelo 2: con metas del 5 % al 20 %, la intensidad entre quienes permanecen pobres aumenta ligeramente, de A₀ = 0.409 a valores entre 0.410 y 0.419 (sección 4). En contraste, el techo de severidad del Modelo 1 mantiene A ≤ A₀ en el total de Antioquia, aunque no necesariamente en cada zona (sección 4). La elección de M0 también permite conservar la medida utilizada por Hamie et al. (2024) y comparar posteriormente este escenario con sus Modelos 3 y 4. Aunque H no constituye el objetivo del Modelo 2, se informa en cada solución por su relación directa con la pregunta de investigación.

Para incorporar la dimensión territorial, la meta de M0 debe cumplirse en cada una de las tres zonas de Antioquia, y no únicamente en el agregado departamental. Esta condición cumple una función análoga a la tasa mínima de salida por zona del Modelo 1. Sin ella, el modelo podría alcanzar el objetivo global concentrando recursos en las cabeceras, donde las intervenciones resultan menos costosas, y producir pocos cambios en el rural disperso. Comparar el costo de la meta territorial con el de una meta exclusivamente global permite cuantificar el precio de esa exigencia de equidad (sección 4). Asimismo, el modelo mantiene la obligación de escolarizar a los niños de 7 a 15 años con rezago escolar que no asisten, según el supuesto 10. El techo de severidad educativa se reserva para el análisis de sensibilidad.

Hamie et al. (2024) denominan *first best* (primer mejor) al escenario en el que el Estado identifica a cada hogar pobre, conoce sus privaciones y entrega únicamente las intervenciones necesarias, sin desperdicio ni errores de focalización. Bajo estas condiciones, el costo obtenido funciona como referencia inferior: un escenario de información imperfecta, sujeto a las mismas restricciones, no puede ser menos costoso que el de información perfecta. Esta comparación, sin embargo, exige cuidar la equivalencia de las condiciones. En el caso base, la escolarización obligatoria (E-7) representa $104.41 de los $105.58 mil millones que cuesta alcanzar la meta del 5 % (99 %), y requiere identificar al niño concreto que no asiste, algo que los escenarios de información imperfecta no observan. Por esta razón, la comparación con los Modelos 3 y 4 utiliza una versión del Modelo 2 sin E-7.

### Comparación de los modelos

La Tabla 1 compara las características de los dos modelos. Las ocho primeras filas son las mismas de la Tabla 1 de Hamie et al. (2024); las tres últimas corresponden a las restricciones de equidad que agregamos. Los dos modelos comparten el supuesto de información completa sobre cada hogar, así que se diferencian sobre todo en qué se fija (el presupuesto o la meta) y en cómo protegen a los hogares más privados.

*Pendiente (Martín, 12-nov): la Tabla 1 se rehace cuando Jerónimo termine los Modelos 3 y 4; esta versión con solo los Modelos 1 y 2 es provisional.*

**Tabla 1. Comparación de las características de los modelos**

| Característica | Modelo 1: por hogar, presupuesto fijo | Modelo 2: por hogar, costo mínimo (*first best*) |
| --- | --- | --- |
| Se puede intervenir cualquier hogar con privaciones | N: solo los hogares pobres | N: solo los hogares pobres |
| Desperdicio por ayuda a hogares sin privaciones | N | N |
| Los hogares en pobreza multidimensional se focalizan con precisión | S | S |
| Gasto en hogares pobres que no salen de la pobreza (sin efecto en H) | S, a propósito: el techo de severidad y la escolarización obligatoria invierten en hogares que no salen; no cambia H, pero sí la severidad | S, a propósito: la meta de M0 premia reducir privaciones de quien sigue pobre, y la escolarización obligatoria se paga aunque el hogar no salga |
| Desperdicio por ayuda a hogares con privaciones pero no pobres (sin efecto en A ni en H) | N | N |
| Se distinguen privaciones de bienes privados y públicos | N | N |
| El Estado ajusta las transferencias según el patrón de consumo del hogar | N | N |
| Desperdicio en transferencias por riesgo moral (el hogar usa la ayuda en otra cosa) | Parcial: casi todas las intervenciones son en especie; en la única transferencia (Renta Ciudadana) el incumplimiento se cobra con p = 0.369 | Parcial: igual que el Modelo 1 |
| Techo de severidad (FGT α = 2) | S: ρ es el menor valor con A ≤ A₀ | N: la meta sobre M0 atenúa el sesgo, pero A sube levemente (sección 4) |
| Equidad territorial | S: tasa mínima de salida r en cada zona | S: meta de M0 en cada zona |
| Techo de severidad educativa (SevEdu) | S: ρ\_e = 14 % | Solo como sensibilidad |

*S = sí; N = no. Fuente: elaboración propia con base en la Tabla 1 de Hamie et al. (2024). Las columnas de sus Modelos 1a y 1b (sin costos), 3 y 4 no se incluyen.*

## 3. Métodos empíricos

*Replica la §3 de Hamie et al.: primero las formulaciones, luego la aplicación y los datos.*

### Modelo 1: modelo por hogar con presupuesto fijo

*Borrador de los bloques 1 y 2 (conjuntos, parámetros y variables). La función objetivo y las restricciones vienen después.*

**Conjuntos.** El modelo trabaja con los siguientes conjuntos:

- **I**: los 523 hogares pobres de la línea base, es decir, con puntaje inicial ≥ 1/3. Solo se modelan los pobres porque, por el supuesto 7, los no pobres no cambian H ni M0; dejarlos fuera no cambia la solución óptima.
- **J**: los 15 indicadores del IPM. **Jᵢ ⊆ J** son las privaciones del hogar i (4.96 en promedio). Solo se crea una decisión donde el hogar está privado.
- **D**: las tres zonas de P3 (cabecera, centro poblado y rural disperso).
- **K**: los 215 niños de 7 a 17 años con rezago escolar (cohorte fija, supuesto 11). **N**: los niños de 6 a 16 años que no asisten al colegio. Las decisiones educativas se definen para cada niño de K ∪ N.
- **S**: las estrategias educativas que el modelo puede asignar a cada niño en el caso base: E1, regreso al colegio, y E2, un ciclo CLEI de primaria. E0 (no intervenir) corresponde a zₖₛ = 0 para toda s, y E3 (CLEI de secundaria) solo entra en el análisis de sensibilidad.
- **Lᵢᶜ**: los adultos del hogar i que pueden hacer un ciclo CLEI (no asisten y tienen 8 años aprobados o menos).
- **Aᵢ**: los valores que puede tomar el puntaje final del hogar i (6,571 en total). Se usan para linealizar la severidad (Apéndice 1).

**Parámetros de entrada.** Como Hamie et al. (2024), los dividimos en originales, que vienen de los datos o de fuentes oficiales, y calculados, que se obtienen antes de optimizar. La Tabla A1 trae la definición completa de cada uno.

- **Originales:** el peso wⱼ de cada indicador (0.10, 0.05 o 0.04, del DANE); Mᵢⱼ = 1 si el hogar i está privado en el indicador j; el factor de expansión HWᵢ (FEX\_C); el número de personas del hogar HSᵢ; el costo unitario oficial de cada indicador en cada zona (Tabla A6); el presupuesto anual B, y la tasa de cumplimiento de Renta Ciudadana p = 0.369 (supuesto 9).
- **Calculados:**
  - el puntaje inicial cᵢ⁰ = Σⱼ wⱼ Mᵢⱼ;
  - las personas que representa el hogar, pᵢ = HWᵢ · HSᵢ. Por eso el objetivo cuenta personas de Antioquia y no hogares de la muestra;
  - las personas afectadas uᵢⱼ, porque muchas intervenciones se pagan por persona y no por hogar;
  - el costo de quitar la privación j al hogar i: costo unitario de su zona × uᵢⱼ × HWᵢ;
  - el costo de Renta Ciudadana por hogar, HWᵢ · $3.0 millones / p;
  - la severidad inicial Sev₀ = Σᵢ pᵢ (cᵢ⁰)² ≈ 117,908, y la severidad educativa sin intervenir ≈ 21,562;
  - el big-M de cada hogar, Mᵢ = cᵢ⁰ − 0.33. Es el menor valor que deja inactiva la restricción de salida cuando el hogar no sale, porque el puntaje final nunca supera al inicial. Un big-M ajustado por hogar hace más ajustada la relajación lineal y el modelo se resuelve más rápido;
  - los parámetros de equidad: ρ y r se calculan en cada corrida (ver Calibración), y ρ\_e = 14 %.

**Variables de decisión.** También siguiendo a Hamie et al. (2024), separamos las externas, que son el plan que observa el gestor, de las internas, que solo sirven para escribir el modelo de forma lineal.

- **Externas (todas binarias):**
  - xᵢⱼ = 1 si se elimina la privación j del hogar i;
  - yᵢ = 1 si el hogar i sale de la pobreza;
  - zₖₛ = 1 si el niño k ∈ K ∪ N recibe la estrategia s;
  - tᵢ = 1 si el hogar i recibe Renta Ciudadana;
  - vₐ = 1 si el adulto a hace su siguiente ciclo CLEI en el año (como máximo uno).
- **Interna:** qᵢ ≥ 0 (continua) representa el cuadrado del puntaje final del hogar y permite escribir la severidad sin términos cuadráticos (Apéndice 1).
- **Expresión auxiliar** (no es variable): el puntaje final del hogar, sᵢ = Σⱼ∈Jᵢ wⱼ (1 − xᵢⱼ). Cada privación que se elimina le resta su peso al puntaje.

**Severidad.** El Modelo 1 usa dos medidas de severidad. Las dos pertenecen a la familia FGT con α = 2 (Foster, Greer y Thorbecke, 1984), pero miden cosas distintas: la severidad del IPM (Sev) mide qué tan alto es el puntaje de privación de cada hogar pobre, y la severidad educativa (SevEdu) mide qué tan atrasado está cada niño frente a los grados que debería llevar.

*Severidad del IPM: qué es.* Sev = Σᵢ∈I pᵢ sᵢ². Para cada uno de los 523 hogares pobres iniciales, suma el cuadrado de su puntaje final, ponderado por las personas que representa. El puntaje no se censura: el hogar sigue contando aunque baje del umbral, así que bajar de 0.60 a 0.35 cuenta como mejora aunque el hogar siga pobre, y bajar de 0.40 a 0.30 también cuenta. En la línea base, Sev₀ = Σᵢ pᵢ (cᵢ⁰)² ≈ 117,908. Alkire y Foster (2011) definen sus medidas Mα con α ≥ 1 solo para indicadores cardinales; con indicadores binarios, como los del IPM colombiano, solo existe M0. Por eso Sev es una extensión FGT propia de este trabajo y no una medida oficial.

*Cómo funciona.* El cuadrado pesa más a quien tiene el puntaje más alto. Bajar el puntaje en 0.10 a un hogar que está en 0.60 reduce su término en 0.11 (de 0.36 a 0.25); bajarlo en 0.10 a un hogar en 0.35 lo reduce en 0.06 (de 0.1225 a 0.0625). Con α = 1 las dos mejoras valdrían lo mismo; α = 2 es el menor exponente entero que prioriza al más privado. Un término cuadrático no cabe en un modelo lineal, así que se reemplaza por la variable qᵢ y por las rectas tangentes a la parábola en cada valor que puede tomar el puntaje del hogar (el conjunto Aᵢ). Como el puntaje solo toma esos valores, el techo de severidad admite exactamente los mismos planes que si se usara sᵢ²: no es una aproximación (Apéndice 1).

*Para qué la usamos.* Un objetivo de H premia sacar a quien está cerca del umbral, y en Antioquia el 49 % de los hogares pobres de la muestra (44 % de las personas pobres) está a 0.05 o menos de él. Para no dejar atrás a los más pobres, la severidad entra de dos maneras. Primero, como techo: la severidad final debe ser a lo sumo (1 − ρ) Sev₀. Es una ε-restricción (Haimes, Lasdon y Wismer, 1971): se optimiza H y el segundo objetivo se convierte en restricción. El valor de ρ es el menor con el que quienes siguen pobres no quedan, en promedio, más pobres que hoy (A ≤ A₀); con B = $424 mil millones, ρ = 47.4 %. Segundo, como criterio de desempate en la segunda etapa del objetivo.

*Severidad educativa (SevEdu): qué es.* SevEdu aplica la misma idea FGT con α = 2 a los niños y no a los hogares. Su población es la cohorte fija de los 215 niños de 7 a 17 años que hoy tienen rezago escolar. Para cada niño k, eₖ = edadₖ − 6 son los grados que debería llevar, su atraso aₖ es la diferencia entre esos grados y los que aprobó, y su brecha normalizada es aₖ / eₖ, que vale entre 0 y 1. SevEdu suma, ponderado por el factor de expansión, el cuadrado de esa brecha, así que un niño muy atrasado pesa más que uno con poco atraso. Sin ninguna intervención, al final del año valdría ≈ 21,562.

*Para qué sirve.* Con las reglas oficiales, ningún niño rezagado puede salir del rezago escolar binario en un año: tendría que aprobar más grados que su atraso actual, y ninguna estrategia con norma y costo oficial lo permite. Sin una medida de cuánto atraso tiene cada niño, el modelo no tendría nada que mejorar en rezago y abandonaría a los más atrasados, porque atenderlos es caro y el indicador binario no se mueve. SevEdu es una segunda capa: el IPM binario queda intacto, para que la cifra sea comparable con la del DANE, y SevEdu registra las mejoras parciales. Un niño que pasa de 6 a 4 años de atraso cuenta como mejora aunque siga rezagado. SevEdu no saca a ningún niño del rezago binario ni cambia H: solo obliga al modelo a atender el rezago.

*Cómo funciona.* Cuatro decisiones de diseño la hacen funcionar:

1. **Brecha normalizada.** Sin normalizar, un joven de 17 años que nunca estudió (11 años de atraso) valdría 11² = 121 y pesaría lo mismo que 121 niños con un año de atraso. Con la brecha normalizada cada niño vale entre 0 y 1, quien nunca estudió vale 1 sea cual sea su edad, y un año de atraso pesa más a los 8 años que a los 17. No se pone tope al atraso: cortar a los más atrasados sería abandonar a quienes se quiere atender.
2. **Escenario sin intervenir.** La intervención dura un año y todos los niños cumplen un año más. Por eso SevEdu se mide al final del año contra lo que pasaría sin intervenir, y no contra la foto inicial: sin ayuda, el atraso de quien no asiste sube un grado y el de quien asiste y aprueba se mantiene. Llamamos bₖ a ese atraso final sin intervenir y dₖₛ a los grados que la estrategia s le quita. Un año escolar regular no baja el atraso, pero evita que crezca. La cohorte se mantiene fija aunque algún joven cumpla 18 años, para que nadie salga del indicador «gratis».
3. **Linealización exacta.** Como cada niño recibe a lo sumo una estrategia y las decisiones zₖₛ son binarias, el cuadrado se desarrolla exactamente como una suma lineal: SevEdu₁ = SevEdu₁,sin − Σₖ,ₛ coefₖₛ zₖₛ, con coefₖₛ = HWₖ (2 bₖ dₖₛ − dₖₛ²) / (eₖ + 1)². Los coeficientes se calculan antes de resolver, así que aquí no hacen falta tangentes.
4. **Una sola decisión, un solo cobro.** La misma decisión zₖₛ alimenta tres cosas: la severidad educativa, la privación de inasistencia del hogar (que se quita solo si todos sus niños no asistentes vuelven a estudiar) y la privación de rezago del hogar. El costo se cobra una sola vez.

Las estrategias disponibles para cada niño son las que tienen norma y costo oficial:

| Código | Estrategia | Para quién | Grados que gana | Costo 2025 |
| --- | --- | --- | --- | --- |
| E0 | Ninguna | Quien ya asiste (su cupo ya lo paga el SGP) | 0 | $0 |
| E1 | Regreso al colegio: Renta Ciudadana y cupo del SGP | De 6 a 16 años que no asisten | 1 | $3.0 millones / p por hogar, más el cupo del SGP por niño que vuelve |
| E2 | Ciclo CLEI de primaria | 13 años o más que no asisten, con 3 grados aprobados o menos | 3 − g si g ≤ 2; 2 si g = 3 | $958,431 urbano / $1,286,194 rural por ciclo |
| E3 | Ciclo CLEI de secundaria | 15 años o más, primaria terminada y 2 años o más por fuera del colegio | 1 o 2 | Igual que E2 |

*g = grados aprobados. E3 queda fuera del caso base: la norma exige dos años por fuera del colegio y la encuesta no trae esa variable. Entra solo como análisis de sensibilidad.*

*Para qué la usamos.* Para que el modelo atienda a los niños más atrasados aunque eso no mueva H este año, con dos restricciones. Primero, la cobertura obligatoria: todo niño de 7 a 15 años de la cohorte que no asiste recibe E1 o E2 (artículo 67 de la Constitución). Segundo, un techo: SevEdu debe bajar al menos una fracción ρ\_e frente al escenario sin intervenir, Σₖ,ₛ coefₖₛ zₖₛ ≥ ρ\_e · SevEdu₁,sin.

*Cómo se escoge ρ\_e.* Se aplicaron cuatro criterios, en este orden:

1. **Factibilidad.** Con las reglas oficiales hay un máximo de reducción que ningún plan supera: 16.9 % sin E3 y 21.2 % con E3.
2. **El codo de la curva de costo.** Con la regla de la máxima distancia a la cuerda, inspirada en el método Kneedle (Satopää et al., 2011) sobre la curva de costo contra ρ\_e, el codo está en 11.5 % ($31.2 mil millones). Hasta ahí la reducción se compra con ciclos CLEI de primaria, que son baratos; después hay que usar el regreso al colegio con transferencia, unas diez veces más caro por niño.
3. **Lo que obliga la ley.** El codo deja sin atender a niños pequeños que no asisten. La cobertura obligatoria de los niños de 7 a 15 años con rezago que no asisten ya logra 11.8 % ($104.2 mil millones).
4. **El costo de subir un poco más.** Pasar de 11.8 % a 14 % cuesta solo $1.6 mil millones más (dos jóvenes de 17 años con un ciclo CLEI de primaria). Después el costo se dispara: 15 % ya cuesta $142.3 mil millones.

No se adopta el máximo porque exigiría realizar todas las intervenciones posibles y haría que el modelo se volviera infactible ante cualquier cambio en los datos. Ninguna fórmula da 14 % por sí sola: la factibilidad y la ley son límites objetivos, y dentro de ese rango 14 % es una elección de los autores, apoyada en el costo marginal. El modelo solo encuentra la forma más barata de cumplirla.

| Punto | Reducción de SevEdu | Costo (mil millones) |
| --- | --- | --- |
| Codo (máxima distancia) | 11.5 % | $31.2 |
| Cobertura obligatoria | 11.8 % | $104.2 |
| **Caso base (cobertura + ρ\_e)** | **14 %** | **$105.8** |
| 15 % | 15 % | $142.3 |
| Máximo factible | 16.9 % | $201.6 |
| Sensibilidad con E3 (cobertura + 20 %) | 20 % | $77.9 |

*Costos del plan educativo mínimo que logra cada reducción, sin E3 salvo en la última fila.*

*Por qué la sensibilidad con E3 cuesta menos que el caso base.* Con E3 disponible, parte de los jóvenes de 15 años o más que no asisten pueden cubrirse con un ciclo CLEI de secundaria ($958,431 urbano o $1,286,194 rural) en vez de E1, que cuesta $3.0 millones / p ≈ $8.1 millones por hogar más el cupo del SGP. Por eso, con E3, la cobertura obligatoria más el 14 % cuesta $64.7 mil millones, frente a $105.8 mil millones en el caso base, y el ahorro alcanza para exigir un 20 % ($77.9 mil millones). No es que exigir más cueste menos: es que E3 abre una estrategia mucho más barata. E3 no entra en el caso base porque la encuesta no permite verificar los dos años por fuera del colegio que exige la norma.

*Simulador interactivo.* El [Simulador de severidades](https://claude.ai/artifact/CQxrVZrLLwP97KP3d6bVtw) permite explorar la severidad del IPM, la severidad educativa y la comparación de los planes con y sin las restricciones de severidad (material suplementario, Apéndice 2).

**Función objetivo.** El modelo se resuelve en dos etapas, con las mismas restricciones en ambas.

En la primera etapa se maximiza el número de personas que salen de la pobreza:

max Σᵢ∈I pᵢ yᵢ  (OBJ 1a)

El valor de esta función objetivo corresponde al número de personas que dejan de ser pobres. Como H final = (pobres iniciales − Σᵢ pᵢ yᵢ) / población total, y el numerador inicial y la población son fijos, maximizar (OBJ 1a) es lo mismo que minimizar H. Así el modelo responde directamente la pregunta de investigación. Llamamos P\* al valor óptimo de esta etapa.

En la segunda etapa, entre todos los planes que sacan a esas mismas P\* personas, se escoge el que deja la menor severidad:

min Σᵢ∈I pᵢ qᵢ  sujeto a  Σᵢ∈I pᵢ yᵢ ≥ P\* (1 − 10⁻⁶)  (OBJ 1b)

La segunda etapa es un criterio de desempate: nunca sacrifica una persona que sale para bajar la severidad. La tolerancia de 10⁻⁶ es la misma tolerancia relativa del solver, y evita que la etapa 2 resulte infactible por redondeo.

Usamos dos etapas en vez de un solo objetivo ponderado del tipo Σ pᵢ yᵢ − λ Σ pᵢ qᵢ. Para que λ solo desempate, tendría que ser tan pequeño que la tolerancia del solver podría absorberlo. Con dos etapas, la prioridad de H sobre la severidad es exacta y no depende de escoger un λ.

**Restricciones.** Las dos etapas comparten las restricciones Restricción₁ 1 a Restricción₁ 16. Cada una lleva el número del modelo en subíndice y su número de orden (Restricción₁ 3 es la tercera del Modelo 1), y las agrupamos por su función: presupuesto, salida de la pobreza, equidad, educación y dominios.

*Presupuesto.* El costo total de las intervenciones realizadas durante el año no puede superar el presupuesto B:

Σᵢ Σⱼ∈Jᵢ cᵢⱼ xᵢⱼ + Σₖ,ₛ cₖₛ zₖₛ + Σᵢ Cᵢᴿᶜ tᵢ + Σᵢ Σₐ∈Lᵢᶜ cᶜ\_d(i) HWᵢ vₐ ≤ B  (Restricción₁ 1)

El primer término paga las privaciones que se quitan con una intervención por hogar o por persona (vivienda, servicios, salud, empleo, trabajo infantil y atención integral), con cᵢⱼ = costo unitario de la zona × uᵢⱼ × HWᵢ. Los otros tres pagan los programas educativos por niño o por adulto: cₖₛ es el cupo escolar (E1) o el ciclo CLEI (E2) del niño k, ya multiplicado por su factor de expansión; Cᵢᴿᶜ = HWᵢ · $3.0 millones / p es la Renta Ciudadana del hogar, y cᶜ\_d es un ciclo CLEI para adultos en la zona d. Así cada programa se cobra una sola vez, aunque quite varias privaciones (por ejemplo, un ciclo CLEI puede quitar el logro educativo y el analfabetismo del mismo hogar).

*Salida de la pobreza.* El hogar solo cuenta como que sale si su puntaje final queda por debajo del umbral:

sᵢ ≤ 0.33 + Mᵢ (1 − yᵢ)  para todo i ∈ I  (Restricción₁ 2)

Dado que los pesos son múltiplos de 0.01, el puntaje también lo es, y «menor que 1/3» equivale a «menor o igual que 0.33». Si yᵢ = 1, la restricción exige sᵢ ≤ 0.33. Si yᵢ = 0, el lado derecho vale cᵢ⁰ y la restricción no limita nada, porque el puntaje final nunca supera al inicial. Esta es la versión lineal de la condición lógica «si el hogar sale, su puntaje queda bajo el umbral» (Apéndice 1).

*Equidad.* Tres restricciones evitan que el modelo abandone a los más pobres. La primera es una tasa mínima de salida en cada zona:

Σᵢ∈I(d) pᵢ yᵢ ≥ r · Pobres⁰\_d  para toda zona d ∈ D  (Restricción₁ 3)

donde Pobres⁰\_d = Σᵢ∈I(d) pᵢ son las personas pobres iniciales de la zona d. Con presupuestos bajos, sin ella el modelo concentraría la inversión en las cabeceras, donde quitar privaciones cuesta menos, y casi abandonaría la zona rural dispersa: con B = $108.0 mil millones y r = 0 sale el 27.9 % de las personas pobres de las cabeceras, el 3.6 % de las de los centros poblados y solo el 1.1 % de las del rural disperso (cifras exactas para ese B: cerca del presupuesto mínimo la salida por zona es muy sensible, y con $108.041 mil millones el rural disperso sale 1.5 %; el total de personas es estable). Con presupuestos altos casi no actúa: con $424 mil millones, sin exigir nada, ya sale el 81 % de los pobres del rural disperso (ver Calibración). r se calcula en cada corrida como el codo de la curva de personas que salen contra r (ver Calibración); con B = $424 mil millones, r = 0.833.

La segunda define la severidad de cada hogar sin términos cuadráticos. Para cada valor a que puede tomar el puntaje final:

qᵢ ≥ 2a sᵢ − a²  para todo i ∈ I y todo a ∈ Aᵢ  (Restricción₁ 4)

Cada recta es tangente a la parábola s² en el punto a, así que qᵢ queda por encima de sᵢ² y, como sᵢ solo toma valores de Aᵢ, la mayor de las tangentes coincide con sᵢ². Por eso un plan cumple Restricción₁ 4 y Restricción₁ 5 si y solo si su severidad con sᵢ² cumple el techo. En la primera etapa qᵢ puede quedar por encima de sᵢ² sin cambiar la solución; lo exacto es el conjunto de planes factibles (derivación en el Apéndice 1).

La tercera es el techo de severidad, una ε-restricción (Haimes, Lasdon y Wismer, 1971):

Σᵢ∈I pᵢ qᵢ ≤ (1 − ρ) Sev₀  (Restricción₁ 5)

La restricción exige que la severidad total de los 523 hogares inicialmente pobres disminuya al menos una fracción ρ, independientemente de que cada hogar salga o no de la pobreza. Se trata, por tanto, de un límite agregado y no de una exigencia individual. El parámetro ρ se selecciona como el menor valor evaluado con el que la intensidad de quienes siguen pobres no supera la inicial (A ≤ A₀). Si ninguno lo consigue, se utiliza el techo más exigente evaluado y se deja constancia de que la condición no se cumple (véase «Calibración»). Para B = $424 mil millones, ρ = 47.4 %.

*Educación.* Estas restricciones ligan las decisiones por niño y por adulto con las privaciones del hogar. Primero, solo se asignan estrategias que la norma permite y como máximo una por niño:

zₖₛ ≤ elegₖₛ  para todo k y todo s  (Restricción₁ 6)

Σₛ zₖₛ ≤ 1  para todo k  (Restricción₁ 7)

donde elegₖₛ = 1 si el niño cumple los requisitos legales de la estrategia: E1 si no asiste y tiene 16 años o menos; E2 si tiene 13 años o más, no asiste y tiene a lo sumo 3 grados aprobados. Restricción₁ 7 es la que hace exacta y lineal la fórmula de SevEdu (sección Severidad). La Renta Ciudadana se paga una vez por hogar, aunque vuelvan varios niños:

zₖ,E1 ≤ tᵢ₍ₖ₎  para todo k  (Restricción₁ 8)

El techo de severidad educativa y la cobertura obligatoria son:

Σₖ,ₛ coefₖₛ zₖₛ ≥ ρₑ · SevEdu₁,sin  (Restricción₁ 9)

Σₛ zₖₛ = 1  para todo niño k de 7 a 15 años de la cohorte que no asiste  (Restricción₁ 10)

Restricción₁ 9 exige reducir al menos un 14 % el atraso de los niños rezagados frente al escenario sin intervención. Restricción₁ 10 traduce el artículo 67 de la Constitución, que hace obligatoria la educación hasta los 15 años (supuesto 10).

La privación de rezago del hogar se quita solo si ningún niño del hogar queda atrasado. Si mₖₛ son los grados que gana el niño k con la estrategia s y aₖ⁰ su atraso inicial:

xᵢ,rez ≤ Σₛ: mₖₛ ≥ aₖ⁰ + 1 zₖₛ  para todo k ∈ K(i)  (Restricción₁ 11)

xᵢ,rez = 0  si algún k ∈ K(i) tiene mₖₛ < aₖ⁰ + 1 para toda s  (Restricción₁ 12)

El «+ 1» aparece porque el niño cumple un año más durante el periodo. Con las estrategias que tienen norma y costo oficial, ningún niño de la cohorte cumple mₖₛ ≥ aₖ⁰ + 1 con ninguna estrategia, así que Restricción₁ 12 fija xᵢ,rez = 0 en todos los hogares. Por eso el modelo necesita SevEdu (Restricción₁ 9): sin ella no tendría nada que mejorar en rezago.

La inasistencia del hogar se quita solo si vuelven a estudiar todos sus niños que no asisten, con E1 o con E2:

xᵢ,inas ≤ Σₛ zₖₛ  para todo k ∈ N(i)  (Restricción₁ 13)

El ciclo CLEI cuenta como asistencia porque así lo define la ECV 2025 en la pregunta de asistencia (P8586), que incluye los programas de educación por ciclos.

Para los adultos, el logro educativo del hogar se quita solo si los años que ganan con un ciclo cubren lo que le falta al hogar para un promedio de 9 años:

Σₐ∈Lᵢᶜ gₐ vₐ ≥ Dᵢ xᵢ,logro  para todo i ∈ I  (Restricción₁ 14)

donde gₐ son los años que gana el adulto a con su siguiente ciclo y Dᵢ = 9 nᵢ − Σₐ ℓₐ es el déficit del hogar (nᵢ personas de 15 años o más, ℓₐ años aprobados). En 470 hogares un ciclo por adulto no alcanza y Restricción₁ 14 fija xᵢ,logro = 0. El analfabetismo se quita si cada adulto analfabeta hace su ciclo, que alfabetiza:

xᵢ,analf ≤ vₐ  para todo i ∈ I y todo adulto analfabeta a ∈ Lᵢᶜ  (Restricción₁ 15)

*Dominios.*

xᵢⱼ, yᵢ, zₖₛ, tᵢ, vₐ ∈ {0, 1};  qᵢ ≥ 0  (Restricción₁ 16)

**Calibración: el codo de una curva.** Varios parámetros del modelo se fijan con el mismo criterio, el codo. Lo definimos aquí una sola vez.

*Qué es.* Cuando dos objetivos compiten, la curva que los relaciona muestra cuánto se pierde de uno por cada unidad que se gana del otro. El codo es el punto donde esa relación cambia: antes del codo, mejorar el segundo objetivo cuesta poco del primero; después, cuesta mucho. En el caso de r, la curva es el número de personas que salen de la pobreza contra el piso r exigido en cada zona. Subir r al principio casi no reduce las personas que salen, pero a partir de cierto valor cada punto adicional de r sacrifica muchas.

*Cómo se calcula.* Usamos la regla de la máxima distancia a la cuerda, inspirada en el método Kneedle (Satopää et al., 2011). Primero se normalizan los dos ejes a \[0, 1\], para que el resultado no dependa de las unidades. Después se traza la recta, llamada cuerda, que une el primer y el último punto de la curva. El codo es el punto de la curva más alejado de esa cuerda, es decir, donde la curva más se separa de una relación proporcional entre los dos objetivos.

*Para qué lo usamos.* El codo cumple tres papeles en el Modelo 1. (1) Fija r en el caso base. En cada corrida se resuelve primero con r = 0 y se mide el piso libre, el menor porcentaje de pobres que sale en una zona sin exigir nada; por debajo de ese valor la restricción Restricción₁ 3 no actúa. Luego se busca por bisección el mayor r factible. La bisección se detiene cuando el intervalo mide menos de 0.005. Entre esos dos extremos se evalúan 12 valores de r igualmente espaciados. Doce es la resolución que escogimos para la curva, y el resultado no depende de ella: con B = $424 mil millones, el codo vale r = 0.8345 con 8 puntos, 0.8332 con 12 y 0.8321 con 24, es decir, cambia menos de 0.002 (segunda auditoría del Modelo 1). Cada punto es una corrida completa del Modelo 1 en dos etapas, con la cobertura obligatoria (Restricción₁ 10) y el techo de SevEdu (Restricción₁ 9), pero sin el techo de severidad (Restricción₁ 5), porque ρ se calcula después con el r ya fijado. r es el codo de esa curva. Con B = $127.1, $187 y $424 mil millones se obtiene r = 0.234, 0.438 y 0.833. (2) Es uno de los cuatro criterios con los que se escogió ρₑ (sección Severidad), aplicado a la curva de costo contra ρₑ. (3) Para ρ es solo un contraste: ρ se fija con la regla A ≤ A₀, y el codo de la curva de personas que salen contra severidad se reporta como sensibilidad. El orden en la corrida base es: primero r, luego ρ con ese r, y por último las dos etapas del objetivo.

*Límite.* El codo depende del tramo de la curva que se evalúe, y con presupuestos altos la curva es casi recta, así que el codo queda poco marcado. Con $424 mil millones, r = 0.833 está cerca de lo que ya sale sin exigir nada en cada zona (Sección 5).

&#91;image: Figura 3. Calibración de r con el codo de la curva de personas que salen contra r\]

*Figura 3. Calibración de la tasa mínima de salida por zona r con el codo, para tres presupuestos. Cada punto azul es una corrida del Modelo 1 con un valor distinto de r, entre el piso libre (el menor porcentaje de pobres que sale en una zona cuando r = 0) y el mayor r factible. La línea gris es la cuerda entre los extremos de la curva, y el codo (naranja) es el punto más alejado de la cuerda, medido con los dos ejes normalizados a \[0, 1\]. Con B = $127.1 mil millones el codo está bien marcado: a partir de r = 0.234 cada punto adicional de r sacrifica muchas personas. Con B = $424 mil millones la curva es casi recta y el codo apenas se separa de la cuerda (limitación discutida en la sección 5). Cada panel tiene su propia escala vertical, que no arranca en cero. Las personas que salen en el codo se calculan sin techo de severidad, porque así se calibra r; el caso base final, con el techo ρ, saca 581,452 personas con B = $424 mil millones. Fuente: cálculos propios con los microdatos IPM 2025 del DANE.*

**Calibración de ρ: la regla de la brecha.** Para seleccionar ρ se busca el menor valor que permita mantener la intensidad de quienes siguen pobres por debajo o al nivel de la inicial (A ≤ A₀). El procedimiento comienza con una bisección, con tolerancia de 0.001, en el intervalo comprendido entre la reducción de severidad obtenida sin techo y el 99.5 % de la máxima reducción posible con el presupuesto B. Sin embargo, como A no varía de manera monótona respecto de ρ, la bisección puede pasar por alto valores que sí cumplen la condición. Por eso, cuando no encuentra ninguno, se evalúan 15 valores igualmente espaciados en el mismo intervalo y se selecciona el menor que la satisfaga. Si tampoco se encuentra uno en esa rejilla, se adopta el techo más exigente evaluado y se informa que la regla no se alcanzó. Con B = $424 mil millones se obtiene ρ = 47.4 %. En los 11 presupuestos de la Figura 9, la condición se cumple en 5.

**Presupuesto de referencia.** En el Modelo 1 el presupuesto B es un parámetro de política, no un dato observado: no existe un presupuesto oficial destinado a reducir el IPM de Antioquia con la mezcla de programas del modelo. Por eso el caso base se reporta con un presupuesto de referencia, B = $424 mil millones, que debe leerse como un punto de la frontera H(B) y no como el presupuesto del departamento.

*Cómo se escogió.* Es el punto medio del rango útil que calcula el propio modelo: (105.9 + 742.1) / 2 = 424.0 mil millones de pesos. El extremo inferior, B\_min = $105.9 mil millones, es el gasto forzoso: la cobertura educativa obligatoria de los niños de 7 a 15 años con rezago que no asisten (Restricción₁ 10, artículo 67 de la Constitución) más el techo de SevEdu con ρₑ = 14 %. La tabla de ρₑ muestra $105.8 mil millones para el mismo gasto porque viene de un cálculo anterior (2 de noviembre); la diferencia es de $0.1 mil millones. Con menos dinero el modelo es infactible. El extremo superior, B\_max = $742.1 mil millones, es el menor presupuesto con el que sale todo lo que puede salir (683,406 personas, el H máximo). Se obtiene por bisección, con tolerancia de 0.1 %, sin la equidad por zona ni el techo de severidad. Con un B mayor el modelo no saca a nadie más.

*Por qué el punto medio.* Necesitábamos un valor intermedio para calibrar ρ y r y para reportar el caso base. Cerca de B\_min casi todo el gasto es forzoso y el modelo tiene poco que decidir; cerca de B\_max el presupuesto deja de ser escaso y la pregunta de a quién priorizar pierde sentido. El punto medio queda lejos de ambos extremos, es reproducible (el código lo usa cuando no se le da otro valor) y no favorece ningún escenario. Los resultados para otros presupuestos se reportan en la Sección 4.

*Cómo se compara con el gasto real.* Para anclar el rango a una escala conocida, lo comparamos con la inversión que la Gobernación de Antioquia ejecutó en 2025 en la Línea 2 de su Plan de Desarrollo, «Cohesión desde lo social» (salud, educación, inclusión social y superación de la pobreza): $1,510.7 mil millones ([Gobernación de Antioquia, Rendición de Cuentas 2025](https://www.antioquia.gov.co/images/rendicion-de-cuentas/2026/preguntas-y-respuestas-para-la-rendicion-de-cuentas.pdf)). El presupuesto de referencia equivale al 28 % de esa línea, y el rango útil va del 7 % (B\_min) al 49 % (B\_max). Además, B\_min es del orden de lo que Renta Ciudadana y la Devolución del IVA transfieren en Antioquia en un año, unos $101.6 mil millones (cálculo propio: promedio de tres ciclos oficiales de Prosperidad Social en 2025, multiplicado por los seis ciclos del año). La comparación es solo de escala. La línea social incluye gasto recurrente, como la nómina docente y la salud, y varios programas del modelo (Renta Ciudadana, Fonvivienda y la UPC) son nacionales y no los ejecuta la Gobernación.

*Trabajo futuro.* Revisar qué presupuestos se destinan en Antioquia a estos programas y reemplazar el punto medio por un monto anclado en el gasto real (Sección 5).

### Modelo 2: modelo por hogar con meta de reducción de M0

El Modelo 2 responde la pregunta inversa del Modelo 1: ¿cuál es el presupuesto mínimo para que el M0 de Antioquia baje al menos un porcentaje fijado por el gobierno? En el Modelo 1 el presupuesto B está fijo y se maximiza el número de personas que salen de la pobreza; aquí la meta está fija y se minimiza el costo. Como el Estado sabe exactamente qué hogar es pobre y en qué está privado, este modelo es el «first best» (Hamie et al., 2024) y sirve de referencia para medir cuánto más cuestan los Modelos 3 y 4, que no observan a cada hogar: el Modelo 3 focaliza por zona y el Modelo 4 por tipo de hogar.

**Conjuntos, parámetros y variables.** Son los del Modelo 1, con una diferencia: el presupuesto B deja de ser un dato y se vuelve el resultado del modelo. Se trabaja otra vez solo con los 523 hogares pobres, porque los hogares no pobres no aportan al numerador de M0 y, por el supuesto de que ningún hogar cae en la pobreza durante el año, excluirlos no cambia el óptimo. Las variables qᵢ del Modelo 1 no se usan, porque este modelo no lleva techo de severidad. Se agregan:

- Pob y Pob\_d: población total de Antioquia y de cada zona d, contando pobres y no pobres (Σᵢ HWᵢ HSᵢ sobre todos los hogares).
- M0⁰ y M0\_d⁰: el M0 inicial, total y de cada zona.
- m\_d: la meta de reducción relativa de M0 en la zona d. Se corren tres de las 15 metas que usan los Modelos 3 y 4, que van del 2 % al 30 %: 5 %, 10 % y 20 %.
- Uᵢ = pᵢ cᵢ⁰: la mayor contribución posible del hogar i al numerador de M0, que se alcanza si no se le quita ninguna privación.
- Gᵢ ≥ 0 (variable continua): contribución censurada del hogar i al numerador de M0. Vale pᵢ sᵢ si el hogar sigue pobre y 0 si sale.

**Función objetivo.** Se minimiza el costo total del plan:

min  Σᵢ Σⱼ∈Jᵢ cᵢⱼ xᵢⱼ + Σₖ,ₛ cₖₛ zₖₛ + Σᵢ Cᵢᴿᶜ tᵢ + Σᵢ Σₐ∈Lᵢᶜ cᶜ\_d(i) HWᵢ vₐ  (OBJ 2)

La expresión coincide con el lado izquierdo de la restricción presupuestaria del Modelo 1 (Restricción₁ 1): lo que allá era el gasto que debía caber en B, aquí es lo que se quiere hacer lo más pequeño posible. Cada programa se cobra una sola vez, igual que en el Modelo 1. El paper original escribe la misma suma agrupada por indicador, como min Σⱼ Eⱼ.

**Restricciones.** El Modelo 2 tiene trece restricciones, de Restricción₂ 1 a Restricción₂ 13. Tres son nuevas o distintas frente al Modelo 1: la salida de la pobreza, la censura y la meta sobre M0. Las otras diez son las reglas de intervención del Modelo 1 y la naturaleza de las variables, sin cambios salvo que Gᵢ ≥ 0 ocupa el lugar de qᵢ ≥ 0, porque describen qué se puede hacer legalmente en un año y cuándo desaparece una privación, y eso no depende de cuál sea el objetivo.

*Salida de la pobreza.* Igual que en el Modelo 1, el hogar solo cuenta como que sale si su puntaje final queda por debajo del umbral:

sᵢ ≤ 0.33 + Mᵢ (1 − yᵢ)  para todo i ∈ I  (Restricción₂ 1)

Es la misma desigualdad que la Restricción₁ 2, con el mismo Mᵢ = cᵢ⁰ − 0.33 y la misma razón: si yᵢ = 1 exige sᵢ ≤ 0.33, y si yᵢ = 0 no limita nada.

*Contribución censurada.* El numerador de M0 solo cuenta los hogares que siguen pobres:

Gᵢ ≥ pᵢ sᵢ − Uᵢ yᵢ  para todo i ∈ I  (Restricción₂ 2)

Si el hogar sigue pobre (yᵢ = 0), la restricción exige Gᵢ ≥ pᵢ sᵢ: sus privaciones cuentan en M0. Si sale (yᵢ = 1), el lado derecho vale pᵢ (sᵢ − cᵢ⁰), que es menor o igual que cero porque el puntaje final nunca supera al inicial, y Gᵢ puede ser 0. Basta una sola desigualdad, y no las cuatro que usa el paper original para esta censura, porque el modelo minimiza el costo con un M0 máximo permitido: nunca le conviene dejar a Gᵢ por encima de lo que exige la desigualdad.

*Meta sobre M0.* El M0 final de cada zona debe bajar al menos un porcentaje m\_d:

Σᵢ∈I(d) Gᵢ ≤ (1 − m\_d) · M0\_d⁰ · Pob\_d  para toda zona d ∈ D  (Restricción₂ 3)

El M0 final de la zona d es ΣGᵢ / Pob\_d, así que el lado derecho es el numerador inicial reducido en m\_d. El denominador es toda la población de la zona, pobres y no pobres, como en el cálculo del DANE. Exigir la meta en cada zona, y no solo en Antioquia, es el caso base: obliga a cumplir la meta también en la zona rural dispersa, donde todo es más caro, y juega el papel que la Restricción₁ 3 juega en el Modelo 1. La meta solo global, ΣᵢGᵢ ≤ (1 − m) · M0⁰ · Pob, se reporta como sensibilidad.

*Reglas de intervención.* Son las del Modelo 1 con otra numeración. Elegibilidad y una estrategia por niño:

zₖₛ ≤ elegₖₛ  para todo k y todo s  (Restricción₂ 4)

Σₛ zₖₛ ≤ 1  para todo k  (Restricción₂ 5)

La Renta Ciudadana se paga una vez por hogar:

zₖ,E1 ≤ tᵢ₍ₖ₎  para todo k  (Restricción₂ 6)

Cobertura obligatoria del artículo 67 (supuesto 10):

Σₛ zₖₛ = 1  para todo niño k de 7 a 15 años de la cohorte que no asiste  (Restricción₂ 7)

Rezago escolar:

xᵢ,rez ≤ Σₛ: mₖₛ ≥ aₖ⁰ + 1 zₖₛ  para todo k ∈ K(i)  (Restricción₂ 8)

xᵢ,rez = 0  si algún k ∈ K(i) tiene mₖₛ < aₖ⁰ + 1 para toda s  (Restricción₂ 9)

Inasistencia, logro educativo y analfabetismo:

xᵢ,inas ≤ Σₛ zₖₛ  para todo k ∈ N(i)  (Restricción₂ 10)

Σₐ∈Lᵢᶜ gₐ vₐ ≥ Dᵢ xᵢ,logro  para todo i ∈ I  (Restricción₂ 11)

xᵢ,analf ≤ vₐ  para todo i ∈ I y todo adulto analfabeta a ∈ Lᵢᶜ  (Restricción₂ 12)

Naturaleza de las variables:

xᵢⱼ, yᵢ, zₖₛ, tᵢ, vₐ ∈ {0, 1};  Gᵢ ≥ 0  (Restricción₂ 13)

elegₖₛ, mₖₛ, gₐ y Dᵢ se definen como en el Modelo 1. Frente a ese modelo no hay restricción de presupuesto (Restricción₁ 1), porque el gasto es el objetivo. Tampoco hay techo de severidad (Restricción₁ 4 y Restricción₁ 5): M0 ya premia bajar privaciones a un hogar que sigue pobre, y la severidad se reporta después de resolver. El techo de SevEdu (Restricción₁ 9) pasa a ser solo una sensibilidad, porque el rezago binario no se mueve en un año y el modelo no invertiría en él por la meta sobre M0. La cobertura del artículo 67 (Restricción₂ 7) sí se mantiene: es una obligación constitucional, y sin ella el modelo ahorraría incumpliendo la ley. Frente al Modelo 1 se agregan 523 variables continuas Gᵢ y 523 restricciones de censura, y se quitan las variables qᵢ y las 6,571 tangentes, así que el problema es más pequeño.

### Resolución y verificación de los modelos

*Resolución.* Los dos modelos se resuelven con HiGHS a través de PuLP, con un gap relativo de 10⁻⁶ (en el Modelo 1, en cada una de las dos etapas). Cuando el solver se detiene por tiempo sin demostrar el óptimo, la corrida se reporta como cortada y no como óptima. El Modelo 1 se corre con las calibraciones descritas arriba: primero r por el codo, luego ρ por la regla de la brecha y por último las dos etapas del objetivo. El Modelo 2 se resuelve una sola vez por cada meta m y cada escenario, porque su único parámetro de política es la meta: no hay r, ni ρ, ni segunda etapa de desempate.

*Verificación independiente.* Para cada modelo, un verificador que no usa los objetos del modelo recalcula el puntaje de cada hogar a partir de las decisiones, aplica la regla del DANE (pobre si el puntaje es ≥ 0.34) y revisa las restricciones y el valor del objetivo. En el Modelo 1 no hubo violaciones con B = $187 y $424 mil millones: el H y la severidad recalculados coincidieron con los del solver, y el caso base se reprodujo exacto (332,582 y 581,452 personas). En el Modelo 2 no hubo violaciones en diez corridas y el costo recalculado coincidió con el objetivo (diferencia de 0 pesos). Si una restricción estuviera mal escrita, por ejemplo una censura o un big-M flojos, el recalculo no cumpliría la meta o el presupuesto y aparecería como violación.

*Prueba cruzada entre los modelos.* Si el Modelo 2 cumple la meta m con costo B\*, su plan también es factible para el Modelo 1 con presupuesto B = B\*, sin el techo de SevEdu y con r = 0. Como el Modelo 1 maximiza justamente el número de personas que salen, con ese mismo dinero debe sacar al menos tantas como el plan del Modelo 2. Esto se cumplió en los seis casos probados (metas de 10, 20 y 50 %, por zona y global). Con meta por zona, por ejemplo, el plan del Modelo 2 saca a 73,919 personas con la meta de 10 % y el Modelo 1 saca a 139,014 con el mismo presupuesto, porque este último no exige reducir M0 en cada zona. La diferencia es el precio de no dejar sin atender a la zona rural dispersa.

### Aplicación empírica a Antioquia

Los dos modelos se aplican al Índice de Pobreza Multidimensional (IPM) colombiano, calculado por el DANE mediante el método de Alkire y Foster (2011). Este índice evalúa quince indicadores binarios agrupados en cinco dimensiones: educación (logro educativo y analfabetismo); condiciones de la niñez y la juventud (inasistencia escolar, rezago escolar, acceso a servicios para el cuidado de la primera infancia y trabajo infantil); trabajo (desempleo de larga duración y trabajo informal); salud (sin aseguramiento en salud y barreras de acceso a servicios de salud); y vivienda y servicios públicos (acceso a fuente de agua mejorada, eliminación de excretas, material de pisos, material de paredes exteriores y hacinamiento crítico). Cada dimensión recibe un peso de 0.20, distribuido por igual entre sus indicadores: 0.10 por indicador en educación, trabajo y salud; 0.05 en niñez y juventud; y 0.04 en vivienda. El puntaje inicial de privación de un hogar, cᵢ⁰ = Σⱼ wⱼ Mᵢⱼ, suma los pesos de todos los indicadores en que presenta privación. Se considera pobre al hogar cuyo puntaje cumple cᵢ⁰ ≥ k = 1/3, y todas las personas que lo integran se contabilizan como pobres. Conservar los pesos y el umbral oficiales permite comparar nuestros resultados con los publicados por el DANE.

Después de identificar los hogares pobres, el método resume la pobreza mediante tres medidas complementarias. Sea pᵢ = HWᵢ · HSᵢ el número de personas que representa el hogar i, calculado como el producto del factor de expansión por el tamaño del hogar, y sea Pob la población total. La **incidencia**, H = Σᵢ pobre pᵢ / Pob, expresa la proporción de personas en situación de pobreza. La **intensidad**, A = Σᵢ pobre pᵢ cᵢ⁰ / Σᵢ pobre pᵢ, indica el puntaje de privación promedio de esa población. Ambas se integran en el **índice ajustado**, M0 = H × A = Σᵢ pobre pᵢ cᵢ⁰ / Pob. Esta última medida permite registrar dos tipos de mejora: la salida de un hogar de la pobreza y la reducción de privaciones de un hogar que sigue siendo pobre. La incidencia H, en cambio, solo disminuye en el primer caso. Para Antioquia, 523 de los 3,732 hogares de la muestra son pobres en la línea base; mediante los factores de expansión representan 683,406 personas de una población de 7,231,754. De allí se obtienen H₀ = 9.45 %, A₀ = 0.409 y M0₀ = 0.0387 (cálculos propios con los microdatos IPM 2025 del DANE).

El análisis distingue las tres zonas que identifica la variable P3 del DANE —cabecera municipal, centro poblado y rural disperso—, de acuerdo con el enfoque de área de estudio de Muñetón-Santa y Manrique-Ruiz (2023). Las diferencias son marcadas. Las cabeceras concentran el 81 % de la población, pero registran una incidencia de pobreza del 6.2 % (A = 0.406, M0 = 0.025). En los centros poblados, la incidencia alcanza el 17.9 % y la intensidad es la menor de las tres zonas (A = 0.386, M0 = 0.069). Por su parte, el rural disperso reúne el 14 % de la población y el 37 % de las personas pobres; allí la incidencia es del 25.2 %, cuatro veces la de las cabeceras, y la intensidad alcanza su valor más alto (A = 0.421, M0 = 0.106). A estas diferencias se suman mayores costos rurales en intervenciones como acueducto, pisos, paredes, ciclos CLEI y atención en salud (Tabla A6). En consecuencia, los modelos incorporan condiciones territoriales específicas: una tasa mínima de salida por zona en el Modelo 1 (Restricción₁ 3) y metas de M0 por zona en el Modelo 2 (Restricción₂ 3). Su finalidad es evitar que la menor inversión requerida en las cabeceras concentre la asignación de recursos.

Como ejercicio alternativo a la ponderación oficial, evaluamos pesos basados en la entropía de Shannon, wⱼ = (1 − eⱼ) / Σⱼ (1 − eⱼ), donde eⱼ representa la entropía del indicador j calculada a partir de la distribución ponderada de las privaciones entre hogares. Sin embargo, descartamos estos pesos para identificar a la población pobre. En el caso de indicadores binarios, la entropía mide la distribución de una privación y no necesariamente su gravedad, por lo que puede asignar mayor importancia a privaciones menos frecuentes. En Antioquia, la correlación de rangos entre la prevalencia de los indicadores y sus pesos por entropía es de −0.94. Además, si se conservara el umbral k = 1/3, la incidencia estimada pasaría de 9.45 % a 2.2 % y cambiaría la clasificación de 462 hogares de la muestra. Esta diferencia dificultaría la comparación directa con el IPM oficial (cálculos propios con prevalencias ponderadas por personas).

La distribución de las privaciones por zona se presenta en la Figura 4. El trabajo informal es el indicador más frecuente en las tres áreas, con prevalencias del 63.5 % en las cabeceras y del 84.6 % en el rural disperso. Las mayores diferencias territoriales aparecen en el acceso al acueducto —2.7 % en las cabeceras frente a 38.7 % en el rural disperso—, así como en el alcantarillado, la calidad de pisos y el logro educativo. En contraste, las barreras de acceso a la salud, la falta de aseguramiento y el desempleo de larga duración son más frecuentes en las cabeceras.

&#91;image: Tasas de privación por indicador y zona, Antioquia\]

*Figura 4. Porcentaje de personas privadas en cada indicador del IPM, por zona (P3), Antioquia. Incluye a todos los hogares, pobres y no pobres, ponderados por FEX\_C × PERSONAS. El 0.0 % de paredes en los centros poblados corresponde a la muestra. Fuente: cálculos propios con los microdatos IPM 2025 del DANE.*

La Figura 1 permite examinar la distancia que separa a los hogares pobres del umbral. El 49 % de ellos (44 % de las personas pobres) está a 0.05 o menos de k = 1/3, de modo que basta quitarles una o dos privaciones para que salgan de la pobreza; los demás se reparten hasta un puntaje de 0.65, el máximo de la muestra.

### Datos

La aplicación empírica utiliza los microdatos departamentales del IPM 2025 publicados por el DANE, elaborados a partir de la Encuesta Nacional de Calidad de Vida (ECV) del mismo año. Para cada hogar, la base identifica las 15 privaciones que componen el índice (Mᵢⱼ), el número de integrantes (HSᵢ) y el factor de expansión (HWᵢ). La clasificación territorial (P3) se obtiene del archivo de viviendas. La muestra de Antioquia comprende 3,732 hogares, que representan aproximadamente 7.23 millones de personas. Antes de formular los modelos, verificamos que la aplicación de los pesos oficiales y del umbral k = 1/3 reproduce el puntaje y la clasificación de pobreza publicados por el DANE en el 100 % de los hogares. Como la base pública no identifica el municipio, no es posible aislar a Medellín. Por tanto, los resultados corresponden a la totalidad de Antioquia, universo común a los cuatro modelos.

Aunque el IPM registra las privaciones a nivel del hogar, varias intervenciones se financian por persona. Para calcular el número de beneficiarios potenciales de cada intervención (uᵢⱼ), utilizamos el archivo de personas de la ECV e identificamos a los integrantes que cumplen la condición asociada a cada indicador. Por ejemplo, para el aseguramiento en salud contamos a las personas de 6 años o más que no están afiliadas. Estas reglas se validaron con los 87,060 hogares de la muestra nacional: en los indicadores cuyo costo se determina por persona, la clasificación obtenida coincide con la privación reportada por el DANE en al menos el 99.67 % de los hogares. Las excepciones son la atención integral a la primera infancia, con una coincidencia del 96.5 % al contar a los niños de 0 a 5 años, y el desempleo de larga duración, con un 86.5 % al contar a las personas desocupadas del hogar. En ambos casos se trata de aproximaciones. Cuando la regla no identifica a ninguna persona afectada, pero el DANE registra la privación, se establece uᵢⱼ = 1.

### Costos de intervención

Los costos incorporados al modelo corresponden a los valores que, de acuerdo con la normativa y las fuentes oficiales, paga el Estado colombiano por intervenciones capaces de eliminar las privaciones medidas por el DANE. Cuando existe un tope normativo expresado en salarios mínimos, se adopta ese tope; cuando se dispone de asignaciones efectivas publicadas, se utiliza su promedio. No se incluyen intervenciones sin una fuente oficial de costos. Todos los valores corresponden a 2025 y distinguen entre zona urbana (cabecera) y zona rural (centro poblado y rural disperso). La Tabla A6 reúne las cifras y sus fundamentos normativos.

Mientras que Hamie et al. (2024) asignan a cada indicador un costo por hogar, en este estudio el costo se ajusta por el número de unidades afectadas dentro del hogar (uᵢⱼ). Esta distinción es necesaria porque varios programas se financian por beneficiario y no por vivienda o grupo familiar: por ejemplo, afiliar a cinco personas al sistema de salud cuesta cinco veces lo que cuesta afiliar a una. La unidad de costeo se establece a partir de la definición del indicador del DANE y de las reglas de financiación de cada programa:

- **Vivienda (por hogar).** Pisos y paredes se eliminan con un mejoramiento de vivienda: en lo urbano, el tope del mejoramiento locativo (18 salarios mínimos, Decreto 0413 de 2025); en lo rural, el promedio de los subsidios de Fonvivienda asignados en 2025. El hacinamiento se elimina con un mejoramiento modular (22 salarios mínimos, mismo decreto). Se paga por hogar porque la obra beneficia a toda la vivienda. Por el supuesto 5, cada privación se paga por separado, aunque una sola obra pudiera arreglar pisos y paredes.
- **Agua y saneamiento (por hogar).** En lo urbano, las Conexiones Intradomiciliarias (Decreto 1275 de 2021). En lo rural, un acueducto veredal para el agua y una unidad sanitaria con pozo séptico para el saneamiento, con costos de obras de Minvivienda actualizados por IPC. Se escogieron porque el DANE no marca privación en un hogar rural con acueducto o con inodoro conectado a pozo séptico.
- **Salud (por persona).** El aseguramiento se elimina afiliando al régimen subsidiado, que cuesta la UPC por persona (Resolución 2717 de 2024). Las barreras de acceso se eliminan con una consulta de medicina general por persona afectada (tarifa del código 39141, Circular Externa 25 de 2024 de Minsalud), porque la privación es no haber sido atendido por un profesional. En lo rural se suma la prima de dispersión de la UPC, como aproximación al costo de llegar al paciente.
- **Educación de adultos (por adulto).** El analfabetismo y el bajo logro educativo se atienden con un ciclo del CLEI, la educación por ciclos para jóvenes y adultos, a la asignación del SGP 2025 para Antioquia. Cada ciclo dura al menos 40 semanas (Decreto 1075 de 2015), así que en un año cabe uno por adulto. El ciclo 1 alfabetiza y además suma años de estudio, por eso se paga una sola vez aunque sirva para las dos privaciones.
- **Educación de niños (por niño y por hogar).** La inasistencia se elimina con el regreso al colegio: el cupo del SGP del nivel por cada niño que vuelve, más Renta Ciudadana para el hogar ($500,000 por ciclo, seis ciclos en 2025). Renta Ciudadana exige la matrícula de los niños de 5 a 17 años (Resolución 652 de 2025), pero solo el 36.9 % de los hogares cumplió todas sus condiciones en el ciclo 4 de 2025. Por eso el costo esperado de un regreso logrado es $3.0 millones / p (supuesto 9). A los jóvenes de 13 años o más también se les puede ofrecer un ciclo CLEI. El rezago escolar se costea con la asignación del SGP por alumno, aunque con las reglas oficiales no se puede eliminar en un año y solo cuenta para la severidad educativa.
- **Trabajo (por persona).** El empleo formal se costea con el aporte a pensión de un año, 16 % de 12 salarios mínimos (Ley 100 de 1993, modificada por la Ley 797 de 2003). El desempleo de larga duración se costea con el incentivo de Empleos para la Vida (Decreto 533 de 2024), entre el 15 % y el 30 % del salario mínimo durante 12 meses según el perfil del trabajador, y solo se paga cuando la encuesta identifica a la persona desocupada.
- **Niñez (por niño).** El trabajo infantil se atiende con el externado de media jornada del ICBF, que ocupa al niño en las horas en que trabajaría, durante 6 meses (Resolución ICBF 0001 de 2025, actualizada por la 0296 de 2025). La falta de atención integral a la primera infancia se elimina con un cupo en un Centro de Desarrollo Infantil institucional (Resolución ICBF 5288 de 2025), la modalidad que cubre salud, nutrición y cuidado, los tres componentes que mide el DANE.

*Pendiente antes de entregar: (1) el empleo formal supone que el Estado paga el 100 % del aporte a pensión, pero el subsidio oficial análogo (Fondo de Solidaridad Pensional) paga solo una parte, y ese porcentaje no está verificado; (2) los seis ciclos de Renta Ciudadana vienen de prensa y falta la resolución de Prosperidad Social. Fuente de esta subsección: costos/justificacion\_costos.md.*

## 4. Resultados principales

*Replica la §4 de Hamie et al. Todas las cifras salen de los CSV de resultados de los Modelos 1 y 2.*

- **Línea base:** H = 9.45 %, A = 0.4094, M0 = 0.03868, en total y por zona.
- **Modelo 1:** personas que salen contra el presupuesto B, por zona; H contra ρ con el punto donde A = A0.
- **Modelo 2:** costo contra meta de M0 (curva convexa); precio de la equidad territorial; gasto por rubro.
- **Tabla 2. Resultados de los modelos:** H, A, M0, severidad, SevEdu y costo, en total y por zona (equivale a la Tabla 2 del original).
- **Diagramas de cajas (decisión de Martín del 14-nov).** Una figura de cajas del caso base de cada modelo, antes y después de intervenir, para mostrar si baja la caja y, sobre todo, el bigote superior (los más privados). Las cajas de las sensibilidades van en el Apéndice 2, y la explicación de cómo leer una caja va en el pie de figura. Fuentes: informe\_cajas\_sensibilidades.md (Modelo 1), modelo2/informe\_cajas\_modelo2.md y cajas/como\_leer\_las\_cajas.md (Modelo 2). En el Modelo 2, decir que cuatro sensibilidades cambian el costo pero no las cajas (mejora 16).
- **Contribución de cada indicador** antes y después del plan óptimo (equivale a la Figura 8 del original).

La Tabla 2 presenta los resultados de ambos modelos y permite compararlos con la línea base descrita en la sección 3. Antes de cualquier intervención, 683,406 de los 7,231,754 habitantes representados por la muestra se encuentran en pobreza multidimensional, equivalentes al 9.45 % de la población de Antioquia. La intensidad inicial es de 0.409 y el M0 alcanza 0.0387. Esta situación presenta diferencias territoriales importantes: la incidencia es del 6.21 % en las cabeceras, del 17.91 % en los centros poblados y del 25.18 % en el rural disperso. Aunque esta última zona reúne apenas el 14 % de la población, concentra el 37 % de las personas pobres. En la línea base, la severidad asciende a 117,908 y la severidad educativa a 21,562.

Con un presupuesto de $424 mil millones, el Modelo 1 permite que 581,452 personas salgan de la pobreza, lo que equivale al 85.1 % de la población inicialmente pobre. En consecuencia, la incidencia disminuye del 9.45 % al 1.41 %. La reducción de M0 es del 85.1 %, mientras que la severidad baja un 47.4 % y la severidad educativa un 14.0 %; estas dos últimas cifras corresponden a los mínimos establecidos por ρ y ρₑ. La condición de equidad territorial también se satisface: sale de la pobreza el 86.3 % de las personas pobres de las cabeceras, el 84.8 % de las de los centros poblados y el 83.3 % de las del rural disperso, porcentajes que cumplen r = 0.833. Aun así, persiste una brecha territorial: la incidencia final del rural disperso es del 4.20 %, frente al 0.85 % de las cabeceras.

Para contrastar ambos mecanismos a partir de resultados semejantes, resolvimos el Modelo 2 con una meta de reducción de M0 del 85 % en cada zona, próxima al resultado alcanzado por el Modelo 1. El costo mínimo es de $420.3 mil millones, es decir, $3.7 mil millones menos que el presupuesto del Modelo 1, y permite que 580,029 personas salgan de la pobreza, 1,423 menos. Aunque la incidencia final resulta muy similar (1.43 %), la severidad disminuye un 46.0 % y la severidad educativa un 11.8 %, porcentaje que se alcanza únicamente con la cobertura obligatoria del artículo 67. La distribución del gasto también cambia: el Modelo 2 asigna $236.0 mil millones al rural disperso, frente a $223.6 mil millones del Modelo 1, y reduce la incidencia de esa zona al 3.53 %, en lugar del 4.20 %. Estas diferencias deben interpretarse teniendo en cuenta que las restricciones no son idénticas. El Modelo 1 incorpora el piso territorial r, el techo de severidad ρ y el techo educativo ρₑ (14 %), mientras que el Modelo 2 exige la meta por zona y la cobertura escolar obligatoria, sin los tres límites anteriores. Por ello, las diferencias de costo y severidad no pueden atribuirse exclusivamente a la elección entre presupuesto fijo y meta de reducción.

Las metas de reducción del 5, 10 y 20 % permiten observar cómo responde el Modelo 2 ante objetivos más moderados. Los costos se sitúan entre $105.6 y $118.9 mil millones y están determinados en gran medida por la cobertura escolar obligatoria, cuyo costo asciende a $104.4 mil millones. Según la meta, salen de la pobreza entre 35,650 y 149,325 personas. Sin embargo, la intensidad de quienes permanecen pobres aumenta de 0.409 a 0.410, 0.413 y 0.419, respectivamente, un comportamiento consistente con la forma en que M0 censura el puntaje de los hogares que cruzan el umbral (sección 3).

**Tabla 2.** Resultados de los Modelos 1 y 2, en total y por zona. Severidad y SevEdu en niveles; entre paréntesis, la reducción frente a la línea base.

| Escenario | Zona | Personas que salen | H | A | M0 | Severidad | SevEdu | Costo (mil millones) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Línea base | Total | — | 9.45 % | 0.409 | 0.0387 | 117,908 | 21,562 | — |
|  | Cabecera | — | 6.21 % | 0.406 | 0.0252 | 61,548 | 9,440 | — |
|  | Centro poblado | — | 17.91 % | 0.386 | 0.0691 | 10,430 | 1,799 | — |
|  | Rural disperso | — | 25.18 % | 0.421 | 0.1060 | 45,931 | 10,323 | — |
| Modelo 1 (B = $424 mil millones) | Total | 581,452 | 1.41 % | 0.409 | 0.0058 (−85.1 %) | 62,006 (−47.4 %) | 18,543 (−14.0 %) | 424.0 |
|  | Cabecera | 313,678 | 0.85 % | 0.386 | 0.0033 (−87.0 %) | 31,074 | 8,498 | 151.2 |
|  | Centro poblado | 58,569 | 2.73 % | 0.377 | 0.0103 (−85.1 %) | 5,975 | 1,383 | 49.2 |
|  | Rural disperso | 209,205 | 4.20 % | 0.445 | 0.0187 (−82.4 %) | 24,956 | 8,662 | 223.6 |
| Modelo 2 (meta 85 %) | Total | 580,029 | 1.43 % | 0.406 | 0.0058 (−85.0 %) | 63,718 (−46.0 %) | 19,015 (−11.8 %) | 420.3 |
|  | Cabecera | 305,755 | 0.98 % | 0.384 | 0.0038 (−85.0 %) | 33,138 | 8,970 | 135.3 |
|  | Centro poblado | 58,437 | 2.76 % | 0.375 | 0.0104 (−85.0 %) | 5,977 | 1,383 | 49.0 |
|  | Rural disperso | 215,837 | 3.53 % | 0.451 | 0.0159 (−85.0 %) | 24,604 | 8,662 | 236.0 |
| Modelo 2 (meta 5 %) | Total | 35,650 | 8.96 % | 0.410 | 0.0367 (−5.0 %) | 114,580 | 19,015 | 105.6 |
| Modelo 2 (meta 10 %) | Total | 73,919 | 8.43 % | 0.413 | 0.0348 (−10.1 %) | 112,072 | 19,015 | 108.7 |
| Modelo 2 (meta 20 %) | Total | 149,325 | 7.39 % | 0.419 | 0.0309 (−20.1 %) | 107,182 | 19,015 | 118.9 |

*Fuente: cálculos propios con los microdatos del IPM 2025 (DANE). Línea base y metas del 5, 10 y 20 %: modelo2/resultados/caso\_base/. Modelo 1: auditoria/datos\_v2/run424.log y A por zona recalculada de base\_plan\_hogar.csv. Modelo 2 al 85 %: paper/datos\_tabla2/m85\_tabla\_comun.csv (Optimal, gap 8.9 × 10⁻⁷).*

Aunque la regla de la brecha se cumple para Antioquia en su conjunto, el comportamiento de la intensidad no es uniforme entre zonas. En el Modelo 1, la intensidad agregada de quienes siguen pobres se mantiene en 0.409, mientras que desciende de 0.406 a 0.386 en las cabeceras y de 0.386 a 0.377 en los centros poblados. En el rural disperso, por el contrario, aumenta de 0.421 a 0.445. Esto es compatible con el diseño del modelo: ρ se calibra a partir de la intensidad departamental y no de la intensidad de cada zona, por lo que las mejoras en las cabeceras, que concentran el 81 % de la población, pueden compensar el aumento rural. El resultado no significa que algún hogar experimente más privaciones; refleja un efecto de composición, pues los hogares rurales que salen de la pobreza tenían puntajes iniciales más bajos que quienes permanecen en ella. El Modelo 2 tampoco impone la regla de la brecha: con metas del 5, 10 y 20 %, la intensidad total alcanza 0.410, 0.413 y 0.419, respectivamente. Cuando se exige una reducción de M0 del 85 %, comparable con la del Modelo 1, la intensidad del rural disperso también aumenta, hasta 0.451 (Figura 8).

**Figura 5.** Modelo 1 (B = $424 mil millones): puntaje de privación de los hogares pobres antes y después de la intervención, por zona.

&#91;image: Figura 5. Cajas del Modelo 1 antes y después de la intervención\]

*Cómo se lee.* Cada panel muestra Antioquia o una de sus zonas. Las cajas sintetizan la distribución del puntaje de privación de los 523 hogares inicialmente pobres, ponderados por las personas que representan (FEX\_C × PERSONAS). Por tanto, los resultados describen a las personas y no simplemente el número de hogares de la muestra. Los límites de cada caja corresponden a los cuartiles del 25 % y del 75 %, y la línea central representa la mediana. Los bigotes se extienden hasta el último valor comprendido dentro de 1.5 veces el rango intercuartílico; los valores más extremos no aparecen dibujados. La línea discontinua señala el umbral de pobreza (0.34). Se presentan tres distribuciones: el puntaje inicial («Antes»), el puntaje final de todos los hogares inicialmente pobres («Después, todos») y el puntaje final de quienes permanecen pobres («Después, siguen pobres»). Un desplazamiento hacia abajo de la caja, especialmente de su extremo superior, indica una reducción de las privaciones más elevadas.

*Qué se observa.* Para Antioquia, la mediana del puntaje pasa de 0.39 a 0.29, y el cuartil superior de «Después, todos» se ubica en 0.31, por debajo del umbral. Este cambio es consistente con la salida del 85.1 % de las personas pobres. En cambio, entre quienes permanecen pobres, la mediana sigue en 0.39 y el bigote superior alcanza 0.58, frente a 0.57 en la situación inicial. En las cabeceras y los centros poblados, las medianas de quienes siguen pobres son de 0.37 y 0.34, respectivamente. El rural disperso presenta un patrón distinto: su caja se desplaza de 0.42 a 0.47 y la mediana aumenta de 0.40 a 0.45. El bigote superior de esta última distribución llega a 0.52, aunque no incluye dos hogares que continúan pobres con puntajes entre 0.55 y 0.58. Con todo, el puntaje máximo rural disminuye de 0.65 a 0.58.

*Interpretación.* Aunque el Modelo 1 logra que la mayoría de las personas pobres supere el umbral, la mejora no es equivalente para quienes permanecen en esa situación. Como las intervenciones únicamente eliminan privaciones, ningún hogar empeora su puntaje. El desplazamiento hacia arriba de la distribución de quienes siguen pobres responde, en cambio, a un efecto de composición: quienes salen suelen tener puntajes iniciales menores. En el rural disperso, este mecanismo ayuda a explicar que la intensidad aumente de 0.421 a 0.445 (Tabla 2), una limitación que se retoma en la sección 5.

**Figura 6.** Modelo 2: puntaje de privación de los hogares pobres antes y después de la intervención, con metas de reducción de M0 del 5, 10 y 20 % en cada zona.

&#91;image: Figura 6. Cajas del Modelo 2 antes y después de la intervención\]

*Cómo se lee.* La Figura 6 mantiene las convenciones de la Figura 5: cajas ponderadas por personas, cuartiles, mediana, bigotes definidos por 1.5 veces el rango intercuartílico y umbral de pobreza en 0.34. El rombo añade el promedio del puntaje. La caja gris representa la línea base y las otras tres corresponden a los planes de costo mínimo para las metas del 5, 10 y 20 %. A diferencia de la Figura 5, todas las cajas incluyen a los hogares inicialmente pobres, independientemente de si salen o no de la pobreza tras la intervención.

*Qué se observa.* Los cambios más notorios en Antioquia se concentran en la parte inferior de la distribución: el bigote inferior pasa de 0.34 a 0.24, mientras que la proporción de personas por debajo del umbral aumenta a 5.2 %, 10.8 % y 21.9 %, según la meta. La parte superior, en cambio, muestra pocas variaciones: el cuartil superior permanece en 0.44, el bigote superior pasa de 0.57 a 0.58 y el máximo continúa en 0.65. El aumento del bigote no supone un empeoramiento de los hogares; se debe a que el cuartil inferior baja de 0.35 a 0.34, amplía el rango intercuartílico y modifica el límite utilizado para definir el bigote. Al mismo tiempo, la mediana disminuye de 0.39 a 0.38 y el promedio de 0.409 a 0.386. Los centros poblados registran la mayor mejora de la distribución, con una mediana que pasa de 0.38 a 0.35 y un bigote superior que se reduce de 0.49 a 0.45. En el rural disperso, el bigote superior aumenta de 0.62 a 0.65 por el mismo efecto estadístico, sin que ningún hogar empeore: el máximo de esa zona permanece en 0.65 antes y después.

*Interpretación.* Cuando se minimiza el costo sujeto a una meta de M0, las intervenciones tienden a concentrarse en los hogares próximos al umbral, mientras que los puntajes de los más privados presentan pocos cambios. La censura de M0 ayuda a entender este resultado: cuando un hogar deja de ser pobre, su contribución al índice desaparece por completo; si permanece pobre, solo se descuenta el peso de las privaciones eliminadas. No obstante, las metas aquí representadas son considerablemente menores que la reducción de M0 del 85.1 % obtenida con el Modelo 1. Por esta razón, la comparación entre mecanismos se realiza con resultados de magnitud semejante en la Tabla 2.

*Fuente: cálculos propios. Figura 5: cajas\_sensibilidades.csv (escenario base) y base\_plan\_hogar.csv. Figura 6: modelo2/graficos/estadisticas\_cajas\_casos.csv.*

**Figura 7.** Gasto por rubro del Modelo 1 (B = $424 mil millones) y del Modelo 2 con meta de reducción de M0 del 85 %.

&#91;image: Figura 7. Gasto por rubro de los Modelos 1 y 2\]

*Cómo se lee.* Cada grupo de dos barras representa un rubro de intervención, medido en miles de millones de pesos: la barra azul corresponde al Modelo 1 y la naranja al Modelo 2. Los rubros aparecen ordenados según el gasto del Modelo 1, de mayor a menor. La categoría «educación de niños» incluye la cobertura obligatoria del artículo 67 (E-7), los programas de nivelación y la transferencia condicionada, que pueden atender simultáneamente el rezago y la inasistencia escolar. «Educación de adultos» agrupa los ciclos CLEI vinculados al logro educativo y al analfabetismo. No se muestran los rubros sin gasto en ambos modelos.

*Qué se observa.* La composición del gasto es semejante en los dos modelos. En el Modelo 1, la educación de adultos ($134.4 mil millones), el trabajo informal ($133.6 mil millones) y la educación de niños ($105.9 mil millones) reúnen el 88 % del presupuesto. En ambos modelos, el gasto en educación de niños responde principalmente a la cobertura escolar obligatoria, cuyo costo alcanza $104.4 mil millones. También coinciden los montos destinados al aseguramiento en salud, las barreras de acceso a servicios de salud y el desempleo de larga duración. Las principales diferencias aparecen en la educación de adultos, a la que el Modelo 1 asigna $9.5 mil millones más, y en la primera infancia y el trabajo infantil, a los que el Modelo 2 destina $3.9 y $2.5 mil millones adicionales, respectivamente. Ningún modelo asigna gasto a los cinco indicadores de vivienda.

*Interpretación.* Al alcanzar reducciones de M0 muy similares, ambos mecanismos coinciden en sus principales prioridades presupuestarias: educación de adultos, trabajo informal y educación de niños concentran el 88 % del gasto en el Modelo 1 y el 86.5 % en el Modelo 2. Las diferencias de composición se explican principalmente por las asignaciones adicionales del Modelo 1 a educación de adultos ($9.5 mil millones) y del Modelo 2 a primera infancia ($3.9 mil millones) y trabajo infantil ($2.5 mil millones). Aunque esta figura no desagrega el gasto territorial, la Tabla 2 muestra que el Modelo 2 asigna $236.0 mil millones al rural disperso, frente a $223.6 mil millones del Modelo 1. La ausencia de gasto en vivienda resulta coherente con el menor peso de sus indicadores (0.04 cada uno, frente a 0.10 en educación, trabajo y salud) y con sus costos unitarios relativamente elevados (Tabla A6).

*Fuente: cálculos propios. paper/datos\_tabla2/m1\_base\_gasto.csv y m85\_gasto.csv.*

**Figura 8.** Intensidad de la pobreza (A) de quienes siguen pobres, antes y después de la intervención, por zona.

&#91;image: Figura 8. Intensidad A por zona antes y después\]

*Cómo se lee.* Los grupos de barras representan a Antioquia y sus tres zonas. La barra gris muestra la intensidad inicial (A₀); la azul, el resultado del Modelo 1; y la naranja, el del Modelo 2 con una meta de reducción de M0 del 85 %. La intensidad A corresponde al puntaje promedio de privación de quienes permanecen en pobreza. Por ello, una barra de menor altura indica una intensidad más baja entre las personas que siguen pobres.

*Qué se observa.* En Antioquia, la intensidad agregada prácticamente no cambia con el Modelo 1 (0.409) y se reduce ligeramente con el Modelo 2 (0.406). Ambos modelos también disminuyen la intensidad en las cabeceras, de 0.406 a 0.386 y 0.384, y en los centros poblados, de 0.386 a 0.377 y 0.375, respectivamente. En el rural disperso sucede lo contrario: la intensidad aumenta de 0.421 a 0.445 con el Modelo 1 y a 0.451 con el Modelo 2.

*Interpretación.* En el rural disperso, que parte de la mayor incidencia de pobreza, las personas que continúan pobres presentan, en promedio, una intensidad de privación mayor que en la línea base. Esto no implica que algún hogar haya empeorado: el aumento responde al efecto de composición producido cuando los hogares que salen tenían puntajes iniciales menores que los de aquellos que permanecen pobres. La presencia de este patrón en ambos modelos es compatible con la hipótesis de que el problema no depende únicamente del mecanismo de asignación, sino también de la ausencia de un control de intensidad por zona. Sin embargo, esta interpretación todavía requiere una prueba específica: resolver el Modelo 1 con la restricción de que la intensidad de cada zona no supere su valor inicial y evaluar sus resultados (sección 5).

*Fuente: cálculos propios. A₀ y Modelo 1: recálculo con base\_plan\_hogar.csv (reproduce run424.log); Modelo 2: paper/datos\_tabla2/m85\_tabla\_comun.csv.*

**Figura 9.** Reducción de M0 según el gasto en los Modelos 1 y 2, Antioquia, 2025.

&#91;image: Figura 9. Reducción de M0 según el gasto\]

*Cómo se lee.* Los puntos azules representan corridas del Modelo 1 con distintos presupuestos B y su configuración base: r calibrado mediante el codo, ρₑ = 14 % y ρ seleccionado por la regla de la brecha en una rejilla de 15 valores. Los puntos azules vacíos identifican presupuestos para los cuales ninguno de los valores de ρ evaluados permite satisfacer A ≤ A₀; en esos casos se utiliza el techo más exigente de la rejilla. Los puntos naranjas corresponden al Modelo 2 y muestran el costo mínimo de distintas metas de reducción de M0, entre el 5 % y el 100 %. En el eje horizontal aparece el gasto, expresado en miles de millones de pesos, y en el vertical la reducción de M0 respecto de la línea base. La línea punteada señala B = $424 mil millones.

*Qué se observa.* A partir de $150 mil millones, las curvas de ambos modelos prácticamente coinciden, con diferencias inferiores a un punto porcentual. En cambio, con gastos menores, el Modelo 1 consigue reducciones de M0 entre 2.8 y 3.6 puntos porcentuales mayores: 15.2 % frente a 11.6 % con $110 mil millones, y 28.4 % frente a 25.6 % con $127.1 mil millones. En el Modelo 1, la reducción alcanza 48.7 % con $187 mil millones y 85.1 % con $424 mil millones. El Modelo 2 logra una reducción del 50 % con $193.6 mil millones y del 85 % con $420.3 mil millones. Ambos modelos eliminan por completo la pobreza multidimensional con un gasto cercano a $740 mil millones. La pendiente de las curvas disminuye a medida que aumenta el gasto: entre $110 y $250 mil millones se obtienen 47 puntos porcentuales adicionales de reducción de M0, mientras que entre $424 y $742 mil millones la mejora adicional es de solo 15 puntos.

*Interpretación.* La cercanía entre las curvas indica que, por encima de $150 mil millones, partir de un presupuesto disponible o de una meta de reducción conduce prácticamente al mismo resultado agregado en M0. Las diferencias entre los modelos se encuentran, entonces, en la distribución de las intervenciones entre hogares y zonas (Tabla 2 y Figuras 5 a 8). Los rendimientos decrecientes también son consistentes con una secuencia en la que primero se atiende a los hogares cercanos al umbral, mientras que las reducciones posteriores requieren intervenir privaciones más numerosas o costosas. Por otra parte, la regla de la brecha se cumple en 5 de los 11 presupuestos analizados (150, 187, 300, 350 y 424 mil millones). En los restantes, incluso el techo de severidad más exigente evaluado deja A por encima de A₀, una limitación que se retoma en la sección 5.

*Fuente: cálculos propios con los microdatos del IPM 2025 (DANE). Modelo 1: paper/datos\_curvas/curva\_B\_m1\_final.csv (bisección y rejilla de ρ). Modelo 2: modelo2/resultados/barridos/curva\_costo\_meta.csv.*

La sensibilidad de los resultados a los supuestos de costo es reducida. Con B = $424 mil millones, el Modelo 1 permite que salgan de la pobreza entre 581,452 y 602,112 personas, con disminuciones de M0 comprendidas entre 85.1 % y 88.1 %. Este rango se obtiene al modificar la proporción de hogares que cumplen las condiciones de Renta Ciudadana (p = 0.50 y 0.75, frente a 0.369), la medición del rezago mediante E3, la cobertura obligatoria del artículo 67, la imputación del desempleo de larga duración y los costos del trabajo infantil y del acueducto rural. En todos los escenarios evaluados se mantiene A ≤ A₀. El Apéndice 2 presenta estos resultados y las sensibilidades correspondientes al Modelo 2.

## 5. Discusión

Los resultados muestran que, con $424 mil millones, el Modelo 1 permite que 581,452 personas salgan de la pobreza multidimensional en Antioquia, equivalentes al 85.1 % de la población inicialmente pobre. La incidencia disminuye del 9.45 % al 1.41 %, mientras que la severidad se reduce un 47.4 % y se cumple el piso de equidad en las tres zonas. Con una meta de reducción del 85 %, el Modelo 2 obtiene un resultado agregado semejante a un costo de $420.3 mil millones. Desde $150 mil millones, ambos modelos logran prácticamente la misma reducción de M0 para un mismo gasto y concentran la inversión en educación de adultos, trabajo informal y educación de niños, sin destinar recursos a vivienda. No obstante, la distribución territorial y el efecto sobre la severidad difieren. El Modelo 2 asigna más recursos al rural disperso y reduce allí la incidencia al 3.53 %, frente al 4.20 % del Modelo 1. Este último consigue mayores disminuciones de la severidad y de la severidad educativa, en consonancia con sus restricciones de equidad. Pese a estas mejoras, en ambos modelos aumenta la intensidad media de quienes siguen pobres en el rural disperso, debido a un efecto de composición.

Estos hallazgos permiten comparar los dos mecanismos de asignación descritos por Conconi et al. (2025). El Modelo 1 se aproxima a la asignación según necesidad, pues distribuye un presupuesto dado y utiliza el piso r para evitar que alguna zona quede rezagada en las salidas de la pobreza. El Modelo 2, en cambio, responde al presupuesto por desempeño: estima el gasto necesario para cumplir una meta de reducción de M0 en cada zona. Así, reducir el índice a la mitad requiere alrededor de $194 mil millones, mientras que una reducción del 85 % cuesta $420.3 mil millones. Dado que las curvas casi coinciden desde $150 mil millones (Figura 9), la elección entre modelos se relaciona menos con la reducción agregada de M0 que con las garantías distributivas: una tasa mínima de salida por zona acompañada de un techo de severidad en el Modelo 1, o una meta exigible en cada zona en el Modelo 2. La concentración del gasto en educación y trabajo, sin inversión en vivienda, es consistente con la hipótesis de que el presupuesto resulta más eficaz para reducir el IPM cuando se dirige a privaciones con pesos de 0.10, frente a las de vivienda, que pesan 0.04 y presentan costos unitarios más altos.

El análisis también revela limitaciones. En primer lugar, ninguno de los modelos impone un límite a la intensidad de la pobreza en cada zona. Como la regla de la brecha del Modelo 1 se aplica al agregado de Antioquia, la intensidad puede aumentar en el rural disperso, precisamente donde la incidencia inicial es mayor. Una extensión sería exigir A\_d ≤ A\_d⁰ en cada zona y cuantificar su costo en términos de personas que salen de la pobreza. En segundo lugar, la regla de la brecha se implementa mediante ρ, que también limita la severidad de los hogares que dejan de ser pobres. Si A ≤ A₀ se impusiera directamente como restricción, con B = $424 mil millones podrían salir unas 4,800 personas adicionales (0.8 %). Además, la regla solo se cumple en 5 de los 11 presupuestos analizados (150, 187, 300, 350 y 424 mil millones); en los demás, ni siquiera el techo de severidad más exigente evaluado consigue mantener A ≤ A₀. Dado que A no es monótona en ρ, la bisección puede omitir valores que satisfacen la condición, razón por la cual se complementó con una búsqueda en rejilla.

Una tercera limitación es que el presupuesto de referencia se definió como el punto medio del rango útil del modelo, no a partir de una asignación presupuestal oficial. Sería conveniente contrastarlo, en trabajos posteriores, con los recursos que efectivamente se destinan a estos programas en Antioquia. Finalmente, aunque el artículo 67 de la Constitución establece la obligatoriedad de la educación entre los 5 y los 15 años, el modelo exige la escolarización únicamente de los niños de 7 a 15 años con rezago que no asisten (29 niños). Esta diferencia responde a que el IPM no mide la inasistencia a los 5 años ni el rezago antes de los 7, y a que la obligación todavía no se extiende en el modelo a los niños que no asisten pero no presentan rezago.

## Referencias

## Apéndice 1

Equivalentes lineales de las restricciones lógicas (big-M por hogar, linealización con tangentes).

*Plan (13-nov):* aquí va la derivación completa de las tangentes de la severidad (fuente: severidad/tangentes\_severidad.md). Incluye: la restricción qᵢ ≥ 2a sᵢ − a² para cada a ∈ Aᵢ; la identidad s² − (2as − a²) = (s − a)² ≥ 0, que prueba que cada tangente es un piso válido; por qué es exacta (sᵢ solo toma los valores de Aᵢ, así que el máximo de las tangentes es sᵢ²); por qué qᵢ termina igual a sᵢ² (el techo es ≤ y la etapa 2 minimiza Σ pᵢ qᵢ); por qué no se usan alternativas, y la verificación de la auditoría. Una figura con la parábola y sus tangentes. En la §3 queda solo una frase con la restricción y la referencia a este apéndice. No citar el conteo de filas de Jerónimo hasta que lo confirme.

- **Tabla A1.** Nomenclatura de los Modelos 1 y 2 (las Tablas A2 y A3 del original, de los Modelos 3 y 4, no se incluyen).
- **Tabla A4.** Marco del IPM colombiano: dimensiones, indicadores y pesos.
- **Tabla A5.** Encuesta usada (ECV/IPM 2025).
- **Tabla A6.** Costos unitarios con la fuente oficial de cada uno.

**Tabla A6.** Costos unitarios por indicador y fuente oficial (pesos de 2025). Urbano = cabeceras; rural = centros poblados y rural disperso.

| Indicador | Intervención | Unidad | Urbano | Rural | Fuente |
| --- | --- | --- | --- | --- | --- |
| Analfabetismo | Ciclo 1 del CLEI | adulto | $958,431 | $1,286,194 | DNP, Anexo 1 DD SGP-96-2025 |
| Logro educativo | Un ciclo del CLEI por año | adulto | $958,431 | $1,286,194 | DNP, Anexo 1 DD SGP-96-2025; Decreto 1075 de 2015 |
| Inasistencia escolar | Cupo SGP del nivel + Renta Ciudadana / p | niño y hogar | $2.71–3.22 M + $3.0 M / p | $3.52–4.18 M + $3.0 M / p | DNP, SGP-96-2025; Res. 652 de 2025; Prosperidad Social, res. 00730 a 03013 de 2025 (p = 0.369) |
| Rezago escolar | Asignación SGP por alumno, según nivel | niño | $2.71–3.22 M | $3.52–4.18 M | DNP, Anexo 1 DD SGP-96-2025 |
| Atención a la primera infancia | Cupo en CDI institucional | niño de 0 a 5 años | $5,210,277 | $5,210,277 | Res. ICBF 5288 de 2025 |
| Trabajo infantil | Externado de media jornada, 6 meses | niño | $5,316,348 | $5,316,348 | Res. ICBF 0001 y 0296 de 2025 |
| Desempleo de larga duración | Empleos para la Vida, 12 meses | desocupado | $2.56–5.12 M | $2.56–5.12 M | Decreto 533 de 2024 |
| Trabajo informal | Aporte a pensión, 16 % × 12 SMMLV | persona | $2,733,120 | $2,733,120 | Ley 100 de 1993, mod. Ley 797 de 2003; Decreto 1572 de 2024 |
| Sin aseguramiento en salud | UPC del régimen subsidiado | persona | $1,323,403 | $1,323,403 | Res. Minsalud 2717 de 2024 |
| Barreras de acceso a salud | Consulta de medicina general (+ prima de dispersión en lo rural) | persona | $52,100 | $203,894 | Circular Externa 25 de 2024; Res. 2717 de 2024 |
| Fuente de agua | Conexión intradomiciliaria / acueducto veredal | hogar | $11,715,405 | $43,685,412 | Decreto 1275 de 2021; Minvivienda (Alpujarra, 2022), IPC |
| Eliminación de excretas | Conexión intradomiciliaria / unidad sanitaria con pozo séptico | hogar | $11,715,405 | $15,280,851 | Decreto 1275 de 2021; Minvivienda (Nariño, 2022), IPC |
| Pisos | Mejoramiento locativo / subsidio rural Fonvivienda | hogar | $25,623,000 | $35,200,000 | Decreto 0413 de 2025; res. Fonvivienda 2025 |
| Paredes | Mejoramiento locativo / subsidio rural Fonvivienda | hogar | $25,623,000 | $35,200,000 | Decreto 0413 de 2025; res. Fonvivienda 2025 |
| Hacinamiento | Mejoramiento modular, 22 SMMLV | hogar | $31,317,000 | $31,317,000 | Decreto 0413 de 2025 |

*Nota: el aporte a pensión supone que el Estado paga el 100 %. Es una cota alta del costo, porque el porcentaje oficial del subsidio (CONPES 4175 de 2025) aún no se ha verificado. Fuente: costos/justificacion\_costos.md.*

## Apéndice 2: resultados adicionales

El apéndice examina la sensibilidad de ambos modelos ante supuestos de costo y de política que no quedan plenamente establecidos por las fuentes oficiales. Para aislar el efecto de cada uno, se modifica un supuesto a la vez y se mantienen constantes los demás elementos de la especificación base. Así, cada resultado puede compararse directamente con el caso de referencia.

**Tabla A7.** Sensibilidad del Modelo 1 ante los supuestos de costo y de política (B = $424 mil millones).

La Tabla A7 reúne diez corridas del Modelo 1 con el presupuesto de referencia de $424 mil millones. Cada fila presenta un escenario y muestra los parámetros de equidad r y ρ obtenidos, respectivamente, mediante el criterio del codo y la regla de la brecha. El número de personas que salen de la pobreza y la reducción de M0 permiten comparar el alcance de las soluciones. La última columna recoge la intensidad media A de quienes permanecen pobres, cuyo valor de referencia es A₀ = 0.4094. Si A ≤ A₀, la asignación no deja más pobres a quienes permanecen en la pobreza. Los ocho primeros escenarios modifican supuestos de costo; los dos últimos evalúan decisiones de política: calibrar ρ mediante el codo en lugar de la regla de la brecha y eliminar simultáneamente r y ρ.

| Escenario | r | ρ | Personas que salen | Reducción de M0 | A |
| --- | --- | --- | --- | --- | --- |
| Caso base | 0.833 | 0.474 | 581,452 | 85.1 % | 0.4091 |
| p = 0.50 | 0.850 | 0.482 | 591,545 | 86.6 % | 0.4087 |
| p = 0.75 | 0.872 | 0.489 | 599,928 | 87.8 % | 0.4083 |
| Rezago con E3 (ρₑ = 20 %) | 0.871 | 0.495 | 602,112 | 88.1 % | 0.4081 |
| Sin cobertura del artículo 67 | 0.838 | 0.481 | 587,683 | 86.0 % | 0.4090 |
| Desempleo imputado | 0.839 | 0.472 | 585,762 | 85.7 % | 0.4087 |
| Trabajo infantil con atención psicosocial | 0.839 | 0.477 | 585,073 | 85.6 % | 0.4083 |
| Acueducto rural con costo BID | 0.832 | 0.474 | 582,078 | 85.2 % | 0.4087 |
| Contraste: ρ por el codo | 0.833 | 0.469 | 584,201 | 85.4 % | 0.4127 |
| Contraste: sin r ni ρ | 0 | No aplica | 592,196 | 85.7 % | 0.4399 |

*Nota: p es la proporción de hogares que cumple las condiciones de Renta Ciudadana (0.369 en el caso base). A₀ = 0.4094. Fuente: modelo1/resultados/barrido\_sensibilidades.csv.*

Los cambios en los supuestos de costo no modifican la conclusión central del caso base. Según el escenario, salen de la pobreza entre 581,452 y 602,112 personas y, en ninguno de ellos, la intensidad A supera A₀. Una mayor proporción de cumplimiento p y la inclusión de E3 abaratan determinadas intervenciones, liberan recursos y elevan los valores calibrados de r y ρ. Las dos variantes de política, en cambio, incumplen A ≤ A₀. Al eliminar r y ρ, salen 10,744 personas adicionales respecto del caso base, pero A aumenta a 0.440 y la proporción de personas pobres que sale en el rural disperso disminuye del 83.3 % al 79.9 %. El contraste muestra que las restricciones de equidad tienen un costo relativamente pequeño en cobertura y evitan una mayor concentración de las salidas entre los hogares próximos al umbral.

**Figura A1.** Puntaje de privación de los hogares pobres antes y después del Modelo 1, por escenario de sensibilidad (B = $424 mil millones).

&#91;image: Figura A1. Cajas del Modelo 1 por escenario de sensibilidad\]

*Cómo se lee.* Cada panel corresponde a uno de los diez escenarios de la Tabla A7. En ellos se comparan tres distribuciones del puntaje de los 523 hogares inicialmente pobres, ponderadas por personas: la situación anterior a la intervención, la posterior para todos los hogares y la posterior para quienes siguen pobres. Las cajas abarcan del primer al tercer cuartil; la línea gruesa marca la mediana y los bigotes se extienden hasta 1.5 veces el rango intercuartílico. La línea roja identifica el umbral k = 1/3, por debajo del cual los hogares dejan de ser pobres.

*Qué se observa.* En los ocho escenarios de costo, la mediana del puntaje entre los hogares inicialmente pobres pasa de 0.39 a 0.28 o 0.29. Entre quienes permanecen pobres, la mediana se mantiene en 0.39 y el bigote superior varía entre 0.53 y 0.58. En contraste, al eliminar r y ρ, la mediana de quienes siguen pobres aumenta a 0.44 y el bigote superior alcanza 0.65.

*Interpretación.* Las modificaciones de costo cambian el número de personas que salen de la pobreza, pero apenas alteran la distribución de los puntajes. La eliminación de r y ρ produce un efecto distinto: deja relativamente más hogares con privaciones elevadas entre quienes permanecen pobres, en consonancia con el aumento de A a 0.440 registrado en la Tabla A7.

*Fuente: cálculos propios, cajas\_sensibilidades.csv y cajas\_sensibilidades.png (informe\_cajas\_sensibilidades.md). El panel del desempleo imputado proviene de una corrida del 12 de noviembre que arrojó 583,731 personas, frente a las 585,762 de la Tabla A7 (corrida del 10 de noviembre); esa diferencia no se ha verificado, por lo que en el texto se usa la cifra de la tabla.*

**Tabla A8.** Sensibilidad del Modelo 2 ante los supuestos de costo (meta de reducción de M0 de 20 % en cada zona).

La Tabla A8 separa el costo mínimo del Modelo 2 en dos componentes. El primero es el piso de gasto asociado al artículo 67, necesario para garantizar la cobertura educativa obligatoria de los niños de 7 a 15 años, independientemente de la meta. El segundo corresponde al costo adicional requerido para reducir M0 un 20 % en cada zona. La suma de ambos constituye el costo total. Cada fila modifica un supuesto del caso base, y las dos últimas incorporan además la restricción de severidad educativa (SevEdu).

| Escenario | Piso del artículo 67 ($ mil millones) | Costo adicional ($ mil millones) | Costo total ($ mil millones) |
| --- | --- | --- | --- |
| Caso base | 104.41 | 14.45 | 118.86 |
| p = 0.50 | 87.73 | 14.45 | 102.19 |
| p = 0.75 | 72.07 | 14.45 | 86.53 |
| Desempleo imputado | 104.41 | 14.45 | 118.86 |
| Con SevEdu | 105.92 | 14.45 | 120.38 |
| Con SevEdu y E3 | 78.04 | 12.96 | 91.00 |

*Nota: con SevEdu, el piso incluye el costo de cumplir ρₑ. Fuente: modelo2/resultados/barridos/sensibilidades.csv y curva\_costo\_meta.csv.*

Los supuestos de costo modifican principalmente el piso asociado al artículo 67, mientras que el gasto adicional necesario para cumplir la meta permanece casi constante. Al aumentar la proporción de cumplimiento p, disminuye el costo de la transferencia condicionada vinculada al regreso escolar: con p = 0.75, el piso baja de $104.41 a $72.07 mil millones. En cambio, el costo adicional de la meta sigue en $14.45 mil millones, lo que sugiere que esa reducción de M0 se logra mediante intervenciones diferentes de la transferencia. La estrategia E3 es la única que modifica también el costo adicional, al cambiar las posibilidades de intervención sobre el rezago. La imputación del desempleo no altera el costo de la meta del 20 %, pero sí influye en metas más exigentes: con una reducción del 90 %, el costo total pasa de $481.4 a $467.8 mil millones.

**Figura A2.** Puntaje de privación de los hogares pobres antes y con metas de reducción de M0 de 5, 10 y 20 % en el Modelo 2, por escenario de sensibilidad (Antioquia).

&#91;image: Figura A2. Cajas del Modelo 2 por escenario de sensibilidad\]

*Cómo se lee.* Cada panel muestra un escenario del Modelo 2 y compara cuatro distribuciones de los puntajes de los 523 hogares inicialmente pobres, ponderadas por personas: antes de intervenir y después de alcanzar metas de reducción de M0 del 5, 10 y 20 % en cada zona. Las cajas abarcan del primer al tercer cuartil, la línea gruesa identifica la mediana, el rombo señala el promedio y los bigotes se extienden hasta 1.5 veces el rango intercuartílico. La línea roja marca el umbral k = 1/3. Además de los escenarios de la Tabla A8, se incluyen la meta definida solo para el total departamental, una variante con meta global sin la cobertura del artículo 67 y un escenario con techo de severidad.

*Qué se observa.* Cuatro escenarios (p = 0.50, p = 0.75, SevEdu de 14 % y desempleo imputado) presentan distribuciones idénticas a la del caso base, pues los mismos hogares salen de la pobreza. En el caso base, con una meta del 20 %, la mediana disminuye de 0.39 a 0.38, mientras que el bigote superior permanece en 0.58. Solo el escenario con techo de severidad modifica claramente la parte alta de la distribución: para la misma meta, el tercer cuartil baja de 0.44 a 0.41 y el bigote superior de 0.58 a 0.52.

*Interpretación.* Los cambios en los supuestos de costo afectan cuánto se necesita gastar para cumplir la meta, pero no necesariamente qué hogares reciben las intervenciones, como muestra la Tabla A8. Por sí sola, una meta de M0 tiende a favorecer a los hogares cercanos al umbral; para mejorar la situación de los más privados se requiere una restricción explícita sobre la severidad, análoga a ρ en el Modelo 1.

*Fuente: cálculos propios a partir de modelo2/graficos/estadisticas\_cajas\_casos.csv (informe\_cajas\_modelo2.md); figura en paper/figuras/figuraA2\_cajas\_m2.png.*

Por último, se estimó el costo de la equidad territorial en el Modelo 2 como la diferencia entre el gasto mínimo necesario para cumplir la meta en cada zona y el requerido para cumplirla únicamente en el conjunto departamental. Este costo alcanza un máximo de $9.9 mil millones con una meta del 25 % y es de $7.8 mil millones con una meta del 85 %. Su mayor participación relativa es del 8.2 % del costo total, para la meta del 20 %. Los resultados indican que exigir la reducción de M0 también en el rural disperso y en los centros poblados incrementa relativamente poco el costo de la intervención (fuente: modelo2/resultados/barridos/costo\_equidad\_territorial.csv).

**Material suplementario.** Los tres simuladores HTML con los que se escogieron los parámetros (26-oct, 28-oct y 1-nov), con una línea sobre qué muestra cada uno y qué decisión salió de él, y el simulador de severidades enlazado en la §3. Los enlaces de claude.ai no son una referencia permanente, así que la versión final debe dar una ubicación estable. Se agrega al cerrar la §3.

## Glosario EN–ES (para la versión en inglés; se quita antes de entregar)

| English term | Español | Use in context |
| --- | --- | --- |
| headcount ratio (H) | incidencia | *The headcount ratio fell from 9.45 % to …* |
| intensity (A) | intensidad / brecha | *Intensity is the average deprivation score among the poor.* |
| adjusted headcount ratio (M0) | IPM ajustado | *M0 is the product of H and A.* |
| poverty cutoff (k) | umbral de pobreza | *A household is poor if its score is at least the cutoff k = 1/3.* |
| uncensored score | puntaje sin censurar | *Severity is computed on the uncensored score.* |
| to exit poverty | salir de la pobreza | *Households near the cutoff exit poverty first.* |
| severity ceiling | techo de severidad | *The severity ceiling is an ε-constraint.* |
| to be left behind | quedar rezagado / abandonado | *No zone is left behind.* |
| composition effect | efecto composición | *A rises through a composition effect, not because anyone becomes poorer.* |
| tie-breaking | desempate | *Severity acts as a tie-breaking criterion in the second stage.* |
