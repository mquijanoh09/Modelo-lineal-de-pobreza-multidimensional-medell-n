# Modelo 2: resultados, significado y análisis

*Proyecto IPM Antioquia, Optimización 1 (EAFIT). Para Martín. 10-nov-2026. Todas las cifras salen de `Modelos\Modelo_2\resultados\` (caso base en `caso_base\`, curva y sensibilidades en `barridos\`), corridas del 9-nov con HiGHS (gap ≤ 1e-6, todas `Optimal`) y verificadas por el auditor sin violaciones.*

**La pregunta del Modelo 2:** ¿cuál es el costo mínimo de reducir M0 (el IPM ajustado) de Antioquia un 5 %, 10 % o 20 %, exigiendo esa reducción en cada una de las tres zonas (cabecera, centro poblado y rural disperso)? Es el "first best": el Estado conoce a cada hogar pobre y qué privaciones tiene.

**Cómo leer las unidades.** Los costos van en **mil millones de pesos** (mm). Cada hogar de la muestra representa a varios hogares reales (factor de expansión), así que "19 hogares salen" son 19 hogares de la muestra, equivalentes a 35,650 personas.

---

## 1. Qué significa cada resultado

| Resultado | Qué es | Cómo leerlo |
|---|---|---|
| **Costo** | Gasto anual total de las intervenciones del plan (es lo que el modelo minimiza) | Presupuesto mínimo que cumple la meta, con las reglas legales (E-7) y los costos oficiales |
| **Piso de E-7** | Costo de escolarizar a los niños de 6 a 15 años que no asisten (art. 67 de la Constitución), con meta 0 % | Se paga con o sin meta. Es $104.41 mm |
| **Costo de la meta** | Costo con meta menos costo con meta 0 % del mismo escenario | Lo que cuesta de verdad bajar M0, sin la obligación constitucional |
| **Hogares / personas que salen** | Hogares que dejan de ser pobres (puntaje de privación bajo 1/3) y personas en ellos | Impacto en cobertura |
| **H** (incidencia) | Proporción de personas pobres | Cuántos siguen pobres |
| **A** (brecha) | Privación promedio de quienes siguen pobres | Qué tan pobres quedan los que no salen |
| **M0 = H × A** | IPM ajustado, la medida que fija la meta | La reducción de M0 es la que se exige por zona |
| **Reducción de M0** | 1 − M0 final / M0 inicial | Debe ser ≥ meta en cada zona; en la zona más difícil queda en la meta exacta |
| **Severidad** | Promedio del cuadrado del puntaje de privación (a quienes siguen pobres) | Si baja, mejoran también los más privados |
| **SevEdu** | Severidad educativa (rezago e inasistencia ponderados por qué tan atrasado está el niño) | Mide si la educación mejora más allá de cruzar el umbral |
| **Gasto por rubro** | Costo dividido por tipo de intervención y zona | Qué compra el plan |
| **Costo de la equidad territorial** | Costo con meta en cada zona menos costo con meta solo global | Precio de no abandonar a la zona rural |
| **Gap / estado** | Cercanía a la solución óptima probada por HiGHS | `Optimal` con gap ≤ 1e-6: el costo es el mínimo real |

Línea base de Antioquia (sin intervenir): **H = 9.45 %, A = 0.4094, M0 = 0.03868**, severidad 117,908, SevEdu 21,562. Por zona: M0 de 0.0252 (cabecera), 0.0691 (centro poblado) y 0.1060 (rural disperso).

---

## 2. Resultados del caso base

Supuestos: cumplimiento de Renta Ciudadana p = 0.369, sin E3, E-7 siempre activa, meta en cada zona, SevEdu solo como sensibilidad, desempleo de larga duración sin persona identificada no quitable.

### 2.1 Tabla principal

| Meta M0 | Costo (mm) | Piso E-7 (mm) | Costo de la meta (mm) | Hogares que salen | Personas que salen | H final | A final | M0 final |
|---|---|---|---|---|---|---|---|---|
| 0 % | 104.41 | 104.41 | 0.00 | 3 | n/d | 9.34% | 0.408 | n/d |
| **5 %** | **105.58** | 104.41 | **1.17** | 19 | 35,650 | 8.96 % | 0.4101 | 0.03673 |
| **10 %** | **108.66** | 104.41 | **4.25** | 29 | 73,919 | 8.43 % | 0.4125 | 0.03477 |
| **20 %** | **118.86** | 104.41 | **14.45** | 65 | 149,325 | 7.39 % | 0.4186 | 0.03091 |

### 2.2 Por zona

| Meta | Zona | Reducción de M0 | H final (inicial) | Hogares que salen | Costo (mm) |
|---|---|---|---|---|---|
| 5 % | Cabecera | 5.01 % | 5.85 % (6.21 %) | 3 | 13.94 |
| 5 % | Centro poblado | 5.36 % | 17.09 % (17.91 %) | 3 | 20.16 |
| 5 % | Rural disperso | 5.01 % | 24.02 % (25.18 %) | 13 | 71.48 |
| 10 % | Cabecera | 10.22 % | 5.48 % | 4 | 14.09 |
| 10 % | Centro poblado | 10.11 % | 16.26 % | 6 | 20.36 |
| 10 % | Rural disperso | 10.00 % | 22.71 % | 19 | 74.21 |
| 20 % | Cabecera | 20.12 % | 4.80 % | 12 | 15.05 |
| 20 % | Centro poblado | 20.26 % | 14.35 % | 12 | 21.61 |
| 20 % | Rural disperso | 20.00 % | 19.89 % | 41 | 82.20 |

### 2.3 En qué se gasta (mm)

| Rubro | 5 % | 10 % | 20 % |
|---|---|---|---|
| Educación de niños (E-7: cupo escolar y Renta Ciudadana) | 104.41 | 104.41 | 104.41 |
| Educación de adultos (ciclos CLEI, logro y analfabetismo) | 0.00 | 2.60 | 10.50 |
| Barreras de acceso a salud | 1.17 | 1.65 | 3.30 |
| Aseguramiento en salud | 0.00 | 0.00 | 0.66 |

Con 20 %, los CLEI se concentran en el rural disperso (9.68 de 10.50). Los demás indicadores no se compran en estas metas.

### 2.4 Qué se puede analizar

1. **El costo es casi todo obligación constitucional.** El piso de E-7 es el 98.9 %, 96.1 % y 87.8 % del costo con metas de 5 %, 10 % y 20 %. Para la defensa: de los $108.7 mm de la meta de 10 %, $104.4 son escolarizar a los niños de 6 a 15 años, y bajar M0 cuesta $4.3 mm.
2. **Bajar M0 es barato al principio y se encarece.** Los primeros hogares salen con una consulta médica por persona ($52,100 urbano; $203,894 rural) o con un ciclo CLEI. Costo por hogar adicional que sale: unos $73 millones entre 0 % y 5 %, unos $283 millones entre 10 % y 20 % y más de $1,000 millones entre 50 % y 80 % (ver §3).
3. **La meta por zona se cumple al décimo.** La zona más difícil (rural disperso) queda exactamente en la meta (5.01 %, 10.00 %, 20.00 %); las otras pasan un poco. Eso indica que la restricción de equidad territorial es la que manda.
4. **La brecha de los que siguen pobres casi no crece** (A de 0.4094 a 0.410–0.419). Con una meta sobre M0 el modelo no solo saca hogares del umbral, también reduce privaciones de quienes siguen pobres. Con H puro (Modelo 1) la brecha llega a 0.445. Es el argumento a favor de haber elegido M0 (D-M2-1).
5. **SevEdu mejora solo por E-7.** Baja de 21,562 a 19,015 (−11.8 %) y no cambia con la meta: una meta de M0 no mueve el rezago educativo más allá de lo que ya obliga el art. 67.
6. **Efecto en pobres.** Con 20 % salen 65 hogares (149 mil personas) y H baja de 9.45 % a 7.39 %. Con 10 %, 74 mil personas.

---

## 3. Curva costo-meta (0 % a 100 %)

| Meta | Costo con meta por zona (mm) | Hogares que salen | A final | Costo con meta solo global (mm) | Costo de la equidad territorial (mm) |
|---|---|---|---|---|---|
| 0 % | 104.41 | 3 | 0.408 | 104.41 | 0.00 |
| 5 % | 105.58 | 19 | 0.410 | 104.67 | 0.91 |
| 10 % | 108.66 | 29 | 0.413 | 105.43 | 3.23 |
| 15 % | 113.15 | 46 | 0.415 | 106.64 | 6.51 |
| 20 % | 118.86 | 65 | 0.419 | 109.14 | 9.72 |
| 25 % | 126.06 | 85 | 0.421 | 116.19 | 9.86 |
| 30 % | 134.19 | 99 | 0.418 | 125.59 | 8.60 |
| 40 % | 158.26 | 130 | 0.416 | 152.69 | 5.57 |
| 50 % | 193.56 | 174 | 0.411 | 189.75 | 3.81 |
| 60 % | 239.34 | 224 | 0.415 | 234.41 | 4.93 |
| 70 % | 296.81 | 274 | 0.415 | 291.41 | 5.41 |
| 80 % | 373.53 | 346 | 0.406 | 365.06 | 8.48 |
| 90 % | 481.43 | 414 | 0.394 | 474.83 | 6.60 |
| 95 % | 574.30 | 480 | 0.414 | 573.34 | 0.95 |
| 100 % | 740.37 | 523 | n/a | 740.37 | 0.00 |

*(Tabla completa de 5 en 5 % en `barridos\curva_costo_meta.csv`.)*

**Qué se puede analizar**
- **La meta máxima es 100 %.** Los 523 hogares pobres pueden salir con intervenciones que sí son posibles, y cuesta $740.37 mm (con la regla anterior de desempleo, $660.64 mm).
- **La curva es convexa:** cada punto adicional de reducción cuesta más. De 0 % a 20 % cuesta $14.5 mm; de 20 % a 50 % cuesta $74.7 mm; de 50 % a 80 % cuesta $180 mm; de 80 % a 100 % cuesta $367 mm. Los últimos hogares tienen muchas privaciones difíciles de quitar.
- **El costo de la equidad territorial no es monótono, y no es un error.** Sube hasta $9.86 mm (meta de 25 %), baja a $3.8 mm (50 %) y vuelve a 0 en 100 %. Con metas pequeñas, una meta global se cumple casi solo en las cabeceras (con 10 %: cabecera 17.9 %, rural 1.1 %); exigirla por zona obliga a llegar al campo. Con metas altas la meta global ya obliga a entrar a todas las zonas, y en 100 % salen todos.
- **Pregunta de política:** exigir la meta en cada zona cuesta entre 0.9 y 9.9 mm más que exigirla solo en total, es decir, entre 1 % y 9 % más. Es el precio de no dejar sin reducir la pobreza a la zona rural dispersa.

---

## 4. Análisis de sensibilidad

El costo de la meta se mide contra el costo del **mismo escenario** con meta 0 % (columna "Costo de la meta"), para no mezclar obligaciones que el escenario agrega (SevEdu). Metas de 5 %, 10 % y 20 %.

| Escenario | Costo 5 % | Costo 10 % | Costo 20 % | Piso del escenario | Costo de la meta (5 / 10 / 20 %) | Hogares que salen |
|---|---|---|---|---|---|---|
| **Caso base** (p = 0.369) | 105.58 | 108.66 | 118.86 | 104.41 | 1.17 / 4.25 / 14.45 | 19 / 29 / 65 |
| Cumplimiento p = 0.50 | 88.90 | 91.98 | 102.19 | 87.73 | 1.17 / 4.25 / 14.45 | 19 / 29 / 65 |
| Cumplimiento p = 0.75 | 73.24 | 76.32 | 86.53 | 72.07 | 1.17 / 4.25 / 14.45 | 19 / 29 / 65 |
| SevEdu activa (ρ_e = 14 %) | 107.09 | 110.18 | 120.38 | 105.92 | 1.17 / 4.25 / 14.45 | 19 / 29 / 65 |
| E3 + SevEdu (ρ_e = 20 %) | 78.71 | 81.35 | 91.00 | 78.04 | 0.68 / 3.31 / 12.96 | 15 / 26 / 62 |
| Desempleo imputado quitable | 105.58 | 108.66 | 118.86 | 104.41 | 1.17 / 4.25 / 14.45 | 19 / 29 / 65 |
| Sin E-7, meta solo global (comparable con M3/M4) | 0.35 | 1.32 | 6.47 | 0.00 | 0.35 / 1.32 / 6.47 | 3 / 12 / 43 |

*Desempleo imputado quitable en metas altas: 80 % = 371.76, 90 % = 467.84, 95 % = 540.43, 100 % = 660.64 mm (caso base actual: 373.53, 481.43, 574.30, 740.37).*

**Qué se puede analizar, escenario por escenario**
1. **Cumplimiento de Renta Ciudadana (p).** Mueve el costo total pero no el costo de la meta. Renta Ciudadana cuesta $3.0 M por hogar dividido por p, así que con p más alto cuesta menos y el piso de E-7 baja: de 104.4 a 87.7 (p = 0.50) y a 72.1 (p = 0.75). El costo de bajar M0 sigue en 1.17 / 4.25 / 14.45. Conclusión: la incertidumbre sobre p afecta el presupuesto de E-7, no la dificultad de reducir M0. Es el supuesto que más mueve el costo total.
2. **SevEdu activa (14 %).** Sube el piso en $1.5 mm (de 104.4 a 105.9) porque obliga a atender también a los niños más atrasados; el costo de la meta no cambia. SevEdu baja a 18,543 (−14 %) frente a 19,015 solo con E-7.
3. **E3 + SevEdu (20 %).** Es el escenario más barato: el piso baja a 78.0 mm. La razón probable es que E3 (CLEI de secundaria, $958,431 por ciclo urbano) cuesta menos que el año regular (~$3.0 M), pero no lo verifiqué por rubro. Menos hogares salen (15/26/62) porque parte del presupuesto va a la educación. SevEdu baja a 17,248 (−20 %). Hay que decidir si E3 es aceptable (el supuesto es que los niños con atraso ≥ 2 años estuvieron 2 años por fuera).
4. **Desempleo imputado quitable.** No cambia las metas de 5 %, 10 % ni 20 %. Cambia las metas altas: con la regla vigente (no quitar si no se identifica a la persona) la meta de 100 % cuesta $740.37 mm, y $660.64 mm si se permite quitarlo. La regla vigente es la prudente: 218 de 226 hogares con desempleo de larga duración no tienen un desocupado identificable en la encuesta.
5. **Sin E-7 y meta solo global (comparable con M3/M4).** Es el Modelo 2 puro, como lo usa Jerónimo de referencia de información perfecta: 0.35 / 1.32 / 6.47 mm. Frente a eso, el caso base cuesta 300 veces más con 5 % y 18 veces con 20 %, casi todo por E-7. Por eso no se deben comparar los costos del caso base con los de M3 y M4 sin aclarar esta diferencia. **Pendiente:** acuerdo escrito con Jerónimo.

**No hay sensibilidad** en el escenario u = 1 (una intervención por hogar; `datos_modelo` aún no lo implementa), ni en trabajo infantil con costo psicosocial ni en acueducto rural bajo (solo cambian costos de indicadores que estas metas no compran).

---

## 5. Validaciones que respaldan los resultados

- **Costo del modelo = costo recalculado** de forma independiente (diferencia de 0 pesos) en 10 corridas.
- **Piso de E-7** calculado aparte, por hogar y con la combinación más barata: coincide con el del modelo ($104.41 mm).
- **Meta cumplida en cada zona** y costo que no baja al subir la meta.
- **Verificador independiente del auditor:** 0 violaciones en 10 corridas y los barridos reproducidos con diferencia 0.0.
- **Prueba cruzada con el Modelo 1:** con el mismo presupuesto, el Modelo 1 saca al menos tantas personas como el plan del Modelo 2 en los 6 casos.

---

## 6. Límites que conviene decir en la defensa

- **Costos oficiales:** cupo SGP del DNP (CLEI $958,431 urbano / $1,286,194 rural), consulta SOAT $52,100, Renta Ciudadana $3.0 M por hogar dividida por p. Quedan pendientes verificar el porcentaje del aporte a pensión y el factor de IPC.
- **Un solo año:** el modelo no mide el efecto del tiempo; la cohorte se fija.
- **H binario** con la regla del DANE (pobre si el puntaje es ≥ 1/3): hogares justo por debajo salen "baratos".
- **p = 0.369** es un supuesto de cumplimiento, no una medición.
- **La muestra expande:** 523 hogares pobres representan toda la población pobre de Antioquia.
- **Sin u = 1** todavía.

---

## 7. Qué decidir con estos resultados

1. Si se reporta el caso base (con E-7) como respuesta principal, mostrar siempre las tres cifras: costo total, costo de la meta y versión comparable con M3/M4.
2. Si E3 entra al caso base (con SevEdu de 20 %, el piso baja unos 26 mm).
3. Cuál es la meta de política: 5 %, 10 % o 20 % (con $1.2, $4.3 o $14.5 mm sobre el piso).

---

*Archivos: `Modelos\Modelo_2\resultados\caso_base\` (por meta: tabla común, gasto por rubro y planes por hogar, niño y adulto), `barridos\curva_costo_meta.csv`, `costo_equidad_territorial.csv`, `sensibilidades.csv`. Decisiones en `docs\justificacion_decisiones_modelo2.md`.*
