# Rezago escolar: hasta dónde contar el atraso y cómo medirlo

*Propuesta para el Modelo 1 (y los 4 modelos) · 30 de octubre de 2026 · preparado para Martín*

## 1. Recomendación

1. **No poner tope al atraso.** Los niños con 5 a 11 años de atraso se quedan en el modelo. Cortarlos es abandonar a los más rezagados, que es justo lo que el enfoque de equidad quiere evitar.
2. **Medir la severidad con la brecha normalizada de Alkire-Foster**, en vez de los años de atraso brutos:

   $$g_k = \frac{a_k}{e_k}, \qquad e_k = \text{edad}_k - 6 \quad (\text{años de escuela que debería tener})$$

   y usar $g_k^2$ en lugar de $a_k^2$. Así cada niño queda entre 0 (sin atraso) y 1 (nunca ha estudiado), y ninguno se dispara.
3. **Permitir que un año de intervención nivele más de un grado** cuando existe un programa que lo hace (CLEI para 13 años o más, Aceleración del Aprendizaje en primaria). En el caso base se nivela 1 grado, como hoy; el programa acelerado entra como sensibilidad.
4. **Condición de pago (decidida 30-oct):** en la primera corrida no hay condición; desde la segunda solo se le vuelve a pagar el año a quien lo ganó (sección 4.4). No se exige asistencia.
5. **Reportar aparte a los niños con $g_k = 1$** (nunca han aprobado un año): son el núcleo duro de la exclusión educativa.

## 2. El problema con medir en años brutos

Hoy la severidad educativa es

$$\text{SevEdu} = \sum_k HW_k\,(a_k^0 - z_k)^2 .$$

**¿Qué es un atraso de 11?** Con la regla del DANE (rezagado si los años aprobados son menos que edad − 6), un atraso de 11 solo es posible a los 17 años y con cero años aprobados. No es un niño "un poco atrasado": es un joven que nunca estudió.

**Pesa demasiado.** Al cuadrado, $11^2 = 121$. Un solo joven con 11 años de atraso pesa en SevEdu₀ lo mismo que 121 niños con 1 año. Nivelarle un año baja la severidad en $2a - 1 = 21$, mientras que nivelar a un niño de 1 año la baja en 1. El solver gastaría primero en esos pocos casos extremos, aunque un año de clase regular casi no cambie su situación.

**No compara bien entre edades.** Un niño de 8 años con 2 años de atraso nunca ha ido al colegio; uno de 17 con 2 años de atraso está casi al día. En años brutos los dos pesan igual (4).

## 3. Justificación

### 3.1 Es la forma estándar en Alkire-Foster

Para indicadores cardinales, Alkire y Foster (2011) miden la privación como **brecha normalizada**, $g = (z - y)/z$, que siempre está entre 0 y 1, y la elevan a la potencia α. Aquí el umbral es $z = e_k$ (años esperados) y el logro es $y = e_k - a_k$ (años aprobados), así que $g_k = a_k / e_k$. No inventamos una medida nueva: aplicamos la de la metodología al atraso escolar.

### 3.2 α = 2 sigue priorizando al más rezagado

Con $g_k^2$ se mantiene la propiedad que ya defendimos: el que está más lejos pesa más que proporcionalmente. Lo que cambia es la escala: "más lejos" se mide frente a lo que debería llevar a su edad, no en años sueltos (Datt, 2019, sobre medidas sensibles a la distribución).

### 3.3 Los atrasos grandes sí se pueden recuperar más rápido

En Colombia existen programas que avanzan varios grados en un año:

- **CLEI** (Decreto 1075 de 2015, art. 2.3.3.5.3.4.7): para personas de 13 años o más. Cuatro ciclos de 40 semanas: el 1.º cubre los grados 1.º a 3.º, y el 2.º, 3.º y 4.º cubren dos grados cada uno.
- **Aceleración del Aprendizaje** (Ministerio de Educación): para estudiantes en extraedad que ya leen y escriben; completan la primaria en un año escolar.
- **Evidencia experimental:** un programa acelerado para 1,723 niños de 9 a 14 años fuera del colegio en Nigeria mejoró lectura y matemáticas con £66 por niño en 7 meses (Diazgranados Ferráns y otros, 2022). No es Colombia, así que sirve de apoyo, no de parámetro.

Para un joven de 15 a 17 años con mucho atraso, lo realista es un CLEI, no un año regular (el costo de $6.3 M que usa el informe no tiene fuente oficial).

### 3.4 Por qué no poner tope

- Un tope (por ejemplo, contar como máximo 5 años) iguala a todos los que están por encima y quita el incentivo a atenderlos.
- Estar en extraedad es de los factores más ligados a la deserción en secundaria en Colombia (Sánchez y otros, Uniandes, 2016). Son los niños con más riesgo de salir del sistema.
- Con la brecha normalizada el tope ya no hace falta: el peso máximo por niño es 1.

### 3.5 Hueco en la literatura

En Scopus, la búsqueda de pobreza multidimensional junto con rezago o atraso escolar arrojó 8 documentos y ninguno trata el atraso en años dentro del IPM. Medir la severidad del rezago es un aporte propio del proyecto, y por eso conviene que use la regla general de Alkire-Foster y no una escala inventada.

## 4. Cómo funciona en el modelo

### 4.1 Datos por niño

De `ninos_rezago.csv` (215 niños de 7 a 17 años en hogares pobres): edad, atraso $a_k^0$, $HW_k$ (`FEX_C`), si asiste hoy, hogar y zona. Se agregan:

| Símbolo | Qué es |
|---|---|
| $e_k = \text{edad}_k - 6$ | Años de escuela esperados |
| $g_k^0 = a_k^0 / e_k$ | Brecha normalizada inicial, entre 0 y 1 |
| $m_k$ | Grados que nivela un año de intervención: 1 en el caso base; 2 en la sensibilidad CLEI (13 años o más con $a_k^0 \ge 2$); nunca más que $a_k^0$ |
| $c_k$ | Costo de esa intervención. CLEI: $958,431 urbano y $1,286,194 rural por estudiante y ciclo (asignación por alumno 2025, Anexo 1 del DD SGP-96-2025, DNP). El año regular se verifica aparte. |

### 4.2 Severidad normalizada y techo

Con $z_k = 1$ si se interviene al niño:

$$\text{SevEdu}^N = \sum_k HW_k \left(\frac{a_k^0 - m_k z_k}{e_k}\right)^2 = \text{SevEdu}^N_0 - \sum_k HW_k\,\frac{2a_k^0 m_k - m_k^2}{e_k^2}\, z_k$$

Como $z_k$ es binaria ($z_k^2 = z_k$), sigue siendo **lineal y exacta**, igual que hoy. El techo (9) queda:

$$\sum_k HW_k\,\frac{2a_k^0 m_k - m_k^2}{e_k^2}\, z_k \;\ge\; \rho_e \cdot \text{SevEdu}^N_0$$

Con $m_k = 1$, la reducción por niño es $(2a_k^0 - 1)/e_k^2$: el mismo término de hoy, dividido por $e_k^2$.

### 4.3 Ejemplos (cuánto baja la severidad por niño intervenido)

| Niño | Edad | Atraso | $g^0$ | Hoy ($a^2$) | Normalizada, $m = 1$ | Normalizada, CLEI ($m = 3$) |
|---|---|---|---|---|---|---|
| A | 8 | 1 | 0.50 | 1 | 0.25 | — |
| B | 8 | 2 (nunca ha estudiado) | 1.00 | 3 | 0.75 | — |
| C | 12 | 3 | 0.50 | 5 | 0.14 | — |
| D | 17 | 1 | 0.09 | 1 | 0.008 | — |
| E | 17 | 11 (nunca ha estudiado) | 1.00 | 21 | 0.17 | 0.47 |

Lo que cambia:

- **Hoy** el solver va primero por E (21), aunque un año regular casi no le cambie la situación.
- **Normalizada con $m = 1$**, el orden es B, A, E, C, D. Un año pesa más para un niño de 8 que para uno de 17, porque es una parte más grande de lo que debería llevar. Eso es coherente con que intervenir temprano rinde más.
- **Con CLEI**, E sube a 0.47, el segundo lugar. Para los jóvenes de 13 a 17 años con mucho atraso, la intervención correcta es la que los vuelve prioritarios.

### 4.4 Condición de pago (decidido por Martín, 30-oct)

Martín descartó las opciones A y B de asistencia. La regla es:

- **Corrida 1:** se puede intervenir a cualquier niño rezagado, sin condición de asistencia.
- **Corridas siguientes:** el **único requisito** para volver a pagarle el año a un niño es que **haya ganado el año** ($ap_k = 1$). No se exige un porcentaje de asistencia.

$$z_k^{t} \le 1 - z_k^{t-1}\,(1 - ap_k^{t-1})$$

Si al niño se le pagó y perdió el año, no se le paga el siguiente; si ganó, o no se le pagó, sigue siendo elegible. Como $z_k^{t-1}$ y $ap_k^{t-1}$ son datos de la corrida anterior, la restricción es lineal. $ap_k$ se simula con Monte Carlo usando la probabilidad de aprobar el año (fuente oficial del MEN, pendiente).

Ejemplo: María y Tomás tienen 2 años de atraso y se les paga el año. María gana el año y sigue siendo elegible. Tomás pierde (aunque haya asistido al 100 %) y no se le paga el año siguiente.

Para los jóvenes de 13 años o más con mucho atraso, la intervención es el CLEI ($m_k = 2$ o 3), que además resuelve el regreso de los que hoy no asisten (49 de los 132 con 2 años o más).

### 4.5 Enlace con el IPM oficial (restricción 10)

El indicador binario del DANE no cambia. La privación del hogar solo desaparece si todos sus niños quedan con atraso 0, y con $m_k$ eso pasa cuando $a_k^0 \le m_k$:

- **(10a)** $x_{i,\text{rez}} \le z_k$ para todo niño $k$ del hogar $i$ con $a_k^0 \le m_k$
- **(10b)** $x_{i,\text{rez}} = 0$ si algún niño del hogar tiene $a_k^0 > m_k$

Con $m_k = 1$ es exactamente la (10a)/(10b) corregida el 30 de octubre.

### 4.6 El paso del tiempo: el niño cumple un año (decidido por Martín, 30-oct)

Durante el año que dura la intervención **todos los niños envejecen un año**. El modelo lo debe tomar así:

**Nueva definición de $m_k$:** grados que el niño **aprueba** en el año. Un año regular aprobado da $m_k = 1$. La promoción anticipada da 2. Un ciclo CLEI da 2 o 3. Aceleración del Aprendizaje da lo que le falte de primaria. La nivelación neta es $m_k - 1$.

**Datos al final del año:**
- Años esperados: $e_k^1 = e_k + 1$.
- Atraso **sin** intervenir (contrafactual): $b_k = a_k^0 + 1 - \text{asiste}_k \cdot ap_k$. Si asiste y gana el año, el atraso se queda igual. Si no asiste o pierde, crece en 1.
- Atraso **con** intervención: $a_k^1 = a_k^0 + 1 - m_k$.
- Efecto de intervenir: $d_k = b_k - a_k^1 = m_k - \text{asiste}_k \cdot ap_k$.

**Severidad al final del año** (sigue lineal porque $z_k$ es binaria):

$$\text{SevEdu}^N_1 = \sum_k HW_k\left(\frac{b_k - d_k z_k}{e_k+1}\right)^2 = \text{SevEdu}^{N}_{1,\text{sin}} - \sum_k HW_k\,\frac{2b_k d_k - d_k^2}{(e_k+1)^2}\,z_k$$

**El techo se mide contra el contrafactual, no contra la foto inicial:** $\text{SevEdu}^N_1 \le (1-\rho_e)\,\text{SevEdu}^N_{1,\text{sin}}$. Así el simple paso del tiempo no cuenta como logro del modelo.

**Los que cumplen 18 (cohorte fija):** un joven de 17 años sale del rango de 7 a 17 del indicador al cumplir 18. Esa salida pasaría "gratis", sin gastar un peso. Por eso la población se fija en t = 0: los 215 niños siguen en la suma y en la privación de su hogar aunque cumplan 18. Si no se hiciera, el modelo mostraría reducciones de H y de severidad que no vienen de ninguna intervención.

**Consecuencia para la restricción (10):** para que el niño quede sin atraso hace falta $a_k^1 = 0$, o sea $m_k \ge a_k^0 + 1$. Queda:
- (10a) $x_{i,\text{rez}} \le z_k$ para cada niño del hogar con $a_k^0 + 1 \le m_k$.
- (10b) $x_{i,\text{rez}} = 0$ si algún niño tiene $a_k^0 + 1 > m_k$.

Un año regular ($m_k = 1$) ya **no** quita la privación a nadie. Al de 1 año de atraso se la quita la promoción anticipada ($m_k = 2$). A los demás, los programas acelerados.

**Ejemplo:** un joven de 17 años con 6 de atraso que no asiste entra al ciclo 3 del CLEI ($m_k = 2$). Sin intervenir, $b_k = 7$. Con CLEI, $a_k^1 = 5$, así que $d_k = 2$. La reducción es $(2\cdot7\cdot2 - 4)/12^2 = 24/144 \approx 0.167$. Si el joven asistiera y ganara el año, $b_k = 6$, $d_k = 1$ y la reducción sería $(12-1)/144 \approx 0.076$.

### 4.7 Qué hay que recalcular

1. $\text{SevEdu}^N_0$, en total y por zona (el valor actual de 1,291,034 está en años al cuadrado y deja de servir).
2. El rango de $\rho_e$: el máximo alcanzable en un año, el valor sin techo y los codos. El 29 % propuesto se calculó con años brutos y hay que volver a escogerlo.
3. El simulador de severidad educativa, para mostrar las dos escalas lado a lado.
4. Los Modelos 3 y 4: la fórmula es la misma niño por niño, así que se reproduce igual con el sorteo. Hay que contárselo a Jerónimo.

## 5. Qué decir en la defensa

- **"¿Tiene sentido contar 11 años de atraso?"** Sí, son los más excluidos. Pero medidos frente a lo esperado para su edad: valen 1, el máximo, no 121.
- **"¿Por qué normalizar?"** Porque así define Alkire-Foster la privación para variables cardinales. Un año de atraso no significa lo mismo a los 8 que a los 17.
- **"¿Por qué un año nivela 3 grados para algunos?"** Porque así está diseñado el CLEI en la norma colombiana. En el caso base usamos 1 grado y el CLEI va como sensibilidad.
- **"¿Y si no asisten o pierden?"** En la primera corrida se les puede intervenir igual (para los de 13 años o más, con CLEI). Desde la segunda, solo se le vuelve a pagar a quien ganó el año.

## 6. Pendientes

- Con §4.6: recalcular $b_k$, $\text{SevEdu}^N_{1,\text{sin}}$ y $\rho_e$; contar cuántos de los 215 tienen 17 años; acordarlo con Jerónimo para los 4 modelos; ajustar los ejemplos de §4.3, que aún son de foto fija.

- ~~Decidir entre A y B para la asistencia~~ Decidido: único requisito de pago es ganar el año (§4.4). Falta la probabilidad oficial de aprobar.
- ~~Confirmar el costo del CLEI~~ Confirmado: $958,431 urbano y $1,286,194 rural por ciclo (Anexo 1, DD SGP-96-2025, DNP). Falta reemplazar el $6.3 M del año regular por el valor oficial.
- Recalcular $\text{SevEdu}^N_0$ y $\rho_e$ con `ninos_rezago.csv`.

## Fuentes

- Alkire, S. y Foster, J. (2011). Counting and multidimensional poverty measurement. *Journal of Public Economics*, 95(7–8), 476–487. https://doi.org/10.1016/j.jpubeco.2010.11.006 (verificado en Scopus).
- Angulo, R., Díaz, Y. y Pardo, R. (2016). The Colombian Multidimensional Poverty Index: Measuring Poverty in a Public Policy Context. *Social Indicators Research*, 127(1), 1–38 (verificado en Scopus).
- Datt, G. (2019). Distribution-Sensitive Multidimensional Poverty Measures. *World Bank Economic Review*, 33(3), 551–572 (verificado en Scopus).
- Diazgranados Ferráns, S. y otros (2022). The Cost-Effectiveness of an Accelerated Learning Program… Northeast Nigeria. *Journal of Research on Educational Effectiveness*, 15(4), 655–686 (verificado en Scopus).
- Decreto 1075 de 2015, arts. 2.3.3.5.3.4.2 a 2.3.3.5.3.4.7 (educación de adultos, CLEI): https://normativa.colpensiones.gov.co/colpens/docs/decreto_1075_2015_pr017.htm
- Ministerio de Educación Nacional. Aceleración del Aprendizaje: https://www.mineducacion.gov.co/1759/w3-printer-340092.html
- Sánchez, F., Velasco, T., Ayala, M. C. y Pulido, X. (2016). Trayectorias de permanencia, deserción y repitencia en la educación secundaria colombiana. Documento de trabajo n.º 36, Universidad de los Andes: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2927172
