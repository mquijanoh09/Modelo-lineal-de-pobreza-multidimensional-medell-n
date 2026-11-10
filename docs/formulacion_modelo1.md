# Modelo 1: formulación para programar

*Versión del 4 de noviembre de 2026, actualizada el 9 de noviembre (ver «Cambios del 9-nov» al final de esta sección). Junta en un solo lugar:*
- *el informe (`docs/informe_modelo1.md` §4);*
- *la síntesis de rezago, inasistencia y SevEdu (`rezago/rezago_inasistencia_sevedu_documento.md` §5);*
- *las decisiones de costos del 4 de noviembre: trabajo infantil, logro educativo con un ciclo por año y barreras de salud.*

**La pregunta del Modelo 1:** con un presupuesto fijo $B$ para un año, ¿a qué hogares pobres de Antioquia intervenir, y en qué privaciones, para que salga de la pobreza el mayor número de personas posible sin abandonar a los más pobres?

---

## 1. Conjuntos (índices)

| Símbolo | Qué es | Tamaño (Antioquia) | Para qué sirve |
|---|---|---|---|
| $I$ | Hogares pobres al inicio (puntaje $c_i^0 \ge 1/3$) | 523 | Los no pobres no cambian H ni M0, así que solo se modelan los pobres (reducción exacta) |
| $J$ | Los 15 indicadores del IPM | 15 | — |
| $J_i \subseteq J$ | Privaciones que tiene el hogar $i$ ($M_{ij} = 1$) | 4.96 en promedio | Solo se crea $x_{ij}$ donde hay privación |
| $D$ | Zonas (`P3`): cabecera, centro poblado, rural disperso | 3 | Restricción de equidad por zona |
| $K$ | Niños de 7 a 17 años con rezago escolar (cohorte fija) | 215 | Capa SevEdu |
| $N$ | Niños de 6 a 16 años que no asisten, con o sin rezago | — (sale del 05) | Ligadura de inasistencia |
| $K(i)$, $N(i)$ | Niños rezagados y no asistentes del hogar $i$ | — | Ligar las decisiones por niño con el hogar |
| $S$ | Estrategias educativas: E1 regreso al colegio, E2 CLEI de primaria (E3 solo en sensibilidad) | 2 | Capa SevEdu |
| $L_i$ | Personas de 15 años o más del hogar $i$; $n_i = |L_i|$ | — | Logro educativo (promedio del hogar) |
| $L_i^{C} \subseteq L_i$ | Adultos elegibles a un ciclo CLEI: no asisten y tienen 8 años aprobados o menos | — | Logro y analfabetismo |
| $A_i$ | Valores que puede tomar el puntaje $s_i$ (sumas de pesos de subconjuntos de $J_i$) | 6,571 en total | Linealizar $s_i^2$ con tangentes |

---

## 2. Parámetros (datos que entran al modelo)

### 2.1 IPM y población

| Símbolo | Significado | Fuente |
|---|---|---|
| $w_j$ | Peso del indicador $j$ (0.10, 0.05 o 0.04) | DANE, reproduce `IPM` al 100 % |
| $M_{ij}$ | 1 si el hogar $i$ está privado en $j$ | HOGARES (DANE) |
| $c_i^0 = \sum_j w_j M_{ij}$ | Puntaje de privación inicial | Derivado |
| $HW_i$ | Factor de expansión del hogar (`FEX_C`) | HOGARES |
| $HS_i$ | Personas del hogar (`PERSONAS`) | HOGARES |
| $p_i = HW_i \cdot HS_i$ | Personas que representa el hogar | Derivado |
| $\text{Pobres}_d^0 = \sum_{i \in d} p_i$ | Personas pobres iniciales en la zona $d$ | Línea base |

### 2.2 Costos (todos con fuente oficial)

| Símbolo | Significado | Valor y fuente |
|---|---|---|
| $u_{ij}$ | Personas del hogar $i$ afectadas en el indicador $j$ | `05_conteo_personas.py`, reglas validadas contra el DANE |
| $EpF_j^{d}$ | Costo unitario del indicador $j$ en la zona $d$ | Informe §6.8 |
| $c_{ij} = EpF_j^{d(i)} \cdot u_{ij} \cdot HW_i$ | Costo de quitarle la privación $j$ al hogar $i$ | Derivado. Se usa para los indicadores "simples" (vivienda, servicios, salud, empleo, trabajo infantil, atención integral) |
| Trabajo infantil | $5,316,348 por niño de 12 a 17 años que trabaja | Externado ICBF, 6 meses × $886,058 (Res. 0001/2025, ficha I-12-122, act. Res. 0296/2025) |
| Barreras de salud | $52,100 urbano / $203,894 rural por persona | 1 consulta, código 39141 (Circular 25/2024) + prima de dispersión (Res. 2717/2024) |
| $c^{C}_d$ | Un ciclo CLEI: $958,431 urbano / $1,286,194 rural | Asignación CLEI SGP 2025 Antioquia |
| $c_{ks}$ | Costo de la estrategia $s$ para el niño $k$, ya multiplicado por $HW_k$: cupo SGP del nivel (E1) o un ciclo CLEI (E2) | SGP 2025 (Anexo 1 DD SGP-96-2025) |
| $C^{RC}_i = HW_i \cdot 3.0\text{ M} / p$ | Renta Ciudadana del hogar, pagada una vez | Prosperidad Social; $p = 0.369$ (0.50 y 0.75 en sensibilidad) |
| $B$ | Presupuesto del año | Escenario. Rango útil con la tabla vigente y la regla de D8: de $105.9 a $742.1 mil millones |

### 2.3 Severidad y equidad

| Símbolo | Significado | Valor |
|---|---|---|
| $\text{Sev}_0 = \sum_{i} p_i (c_i^0)^2$ | Severidad inicial (FGT α = 2 sobre el puntaje, sin censurar) | ≈ 117,908 |
| $\rho$ | Reducción mínima de severidad exigida | **Se calcula en cada corrida:** el menor $\rho$ con $A \le A_0$ (regla de la brecha, §7). Con $B$ = $424 mil millones: 47.4 % |
| $r$ | Fracción mínima de pobres que debe salir en cada zona | **Se calcula en cada corrida:** el codo de la curva $H$ contra $r$ (§7). Con $B$ = $424 mil millones: 0.833 |
| $M_i = c_i^0 - 0.33$ | big-M de la restricción de salida, ajustada por hogar | Derivado |

### 2.4 Educación (SevEdu, logro)

| Símbolo | Significado |
|---|---|
| $a_k^0$, $e_k$ | Atraso inicial del niño $k$ y grados esperados, $e_k = \text{edad}_k - 6$ |
| $b_k = a_k^0 + 1 - q_k$ | Atraso al final del año sin intervenir ($q_k = 0$ si no asiste; $q_k = 1$ si asiste, caso base) |
| $d_{ks}$ | Grados que la estrategia $s$ le quita al atraso al final del año: E1 = 1; E2 = $3 - g$ si $g \le 2$, 2 si $g = 3$ |
| $\text{elig}_{ks} \in \{0,1\}$ | Elegibilidad legal: E1 si no asiste y tiene 16 años o menos; E2 si tiene 13 años o más, $g_k \le 3$ y no asiste; E3 = 0 en el caso base |
| $\text{coef}_{ks} = HW_k \dfrac{2 b_k d_{ks} - d_{ks}^2}{(e_k+1)^2}$ | Cuánto baja SevEdu si el niño $k$ recibe $s$ (se calcula antes de resolver) |
| $\text{SevEdu}^N_{1,\text{sin}}$ | SevEdu al final del año sin intervenir | ≈ 21,562 |
| $\rho_e$ | Reducción mínima de SevEdu | **14 %** (caso base); 20 % con E3 en sensibilidad |
| $\ell_a$ | Años aprobados del adulto $a$ | 05 (regla `anios`) |
| $g_a$ | Años que gana el adulto con su siguiente ciclo: 0→3, 1→3, 2→3, 3→5, 4→5, 5→7, 6→7, 7→9, 8→9; si es analfabeta, $\max(3-\ell_a, 0)$ | `parametros.ganancia_ciclo()` |
| $D_i = 9 n_i - \sum_{a \in L_i} \ell_a$ | Años que le faltan al hogar para un promedio de 9 | Derivado |

---

## 3. Variables de decisión

| Variable | Tipo | Significado |
|---|---|---|
| $x_{ij}$, $j \in J_i$ | Binaria | 1 si se elimina la privación $j$ del hogar $i$ |
| $y_i$ | Binaria | 1 si el hogar $i$ **sale** de la pobreza |
| $q_i$ | Continua ≥ 0 | Representa $s_i^2$ (severidad del hogar) |
| $z_{ks}$, $k \in K \cup N$, $s \in S$ | Binaria | 1 si el niño $k$ recibe la estrategia $s$ |
| $t_i$ | Binaria | 1 si el hogar $i$ recibe Renta Ciudadana |
| $v_a$, $a \in L_i^{C}$ | Binaria | 1 si el adulto $a$ hace su siguiente ciclo CLEI en el año (como máximo uno) |

Expresión auxiliar (no es variable): puntaje después de intervenir, $s_i = \sum_{j \in J_i} w_j (1 - x_{ij})$.

---

## 4. Función objetivo

Se resuelve en **dos etapas** (decisión D1 de Martín, 4-nov), sin $\lambda$:

1. **Etapa 1:** $\max \sum_{i \in I} p_i\, y_i$ sujeto a las restricciones de la sección 5. Da $H^*$ (personas que salen).
2. **Etapa 2:** $\min \sum_{i \in I} p_i\, q_i$ sujeto a las mismas restricciones y a $\sum_i p_i y_i \ge H^* (1 - 10^{-6})$.

- **Etapa 1:** el objetivo principal es el numerador de H.
- **Etapa 2:** desempate. Entre planes que sacan a las mismas personas, escoge el que deja menos severidad. Nunca sacrifica una persona por bajar severidad.
- **Por qué dos etapas y no un $\lambda$ pequeño:** la tolerancia del solver podía "comerse" un $\lambda$ tan chico. Con el gap por defecto de 1e-6 (auditoría H2, 7-nov) el ruido es menor que una persona. Justificación: `modelo1/justificacion_decisiones.md` (D1, P19).
- **Estado del solver:** si HiGHS se corta por tiempo sin probar optimalidad, el estado es «Cortado» (no «Optimal») y la etapa 2 no arranca (auditoría H1).

---

## 5. Restricciones

| # | Ecuación | Para qué sirve |
|---|---|---|
| **(1) Presupuesto** | $\sum_i \sum_{j \in J_i^{simple}} c_{ij} x_{ij} + \sum_{k,s} c_{ks} z_{ks} + \sum_i C^{RC}_i t_i + \sum_i \sum_{a \in L_i^C} c^{C}_{d(i)} HW_i\, v_a \le B$ | Todo lo que se gasta en el año cabe en $B$. Cada programa se paga **una sola vez**: rezago, inasistencia, logro y analfabetismo se pagan por niño o por adulto ($z$, $t$, $v$), no por $x_{ij}$ |
| **(2) Salida de la pobreza** | $s_i \le 0.33 + M_i (1 - y_i) \quad \forall i$ | Si $y_i = 1$, el puntaje final tiene que quedar por debajo del umbral. Si $y_i = 0$, la restricción se relaja |
| **(4) Equidad por zona** | $\sum_{i \in d} p_i\, y_i \ge r \cdot \text{Pobres}_d^0 \quad \forall d$ | Que ninguna zona (sobre todo la rural dispersa, la más cara) quede abandonada |
| **(7) Linealización de $s_i^2$** | $q_i \ge 2a\, s_i - a^2 \quad \forall i,\ \forall a \in A_i$ | Tangentes a la parábola: obligan a $q_i \ge s_i^2$ de forma exacta, porque $s_i$ solo toma valores en $A_i$ |
| **(8) Techo de severidad** | $\sum_i p_i\, q_i \le (1 - \rho)\, \text{Sev}_0$ | ε-restricción: obliga a reducir la severidad de **todos** los pobres, no solo a sacar a los que están cerca del umbral |
| **(E-1) Legalidad** | $z_{ks} \le \text{elig}_{ks}$ | Solo estrategias que la norma permite (edad, grado, asistencia) |
| **(E-2) Una estrategia por niño** | $\sum_s z_{ks} \le 1 \quad \forall k$ | Hace exacta y lineal la fórmula de SevEdu |
| **(E-3) Renta Ciudadana por hogar** | $z_{k,E1} \le t_{i(k)} \quad \forall k$ | La transferencia se paga una vez por hogar, aunque vuelvan varios niños |
| **(E-5) Techo de SevEdu** | $\sum_{k,s} \text{coef}_{ks}\, z_{ks} \ge \rho_e \cdot \text{SevEdu}^N_{1,\text{sin}}$ | ε-restricción educativa: reducir el atraso de los niños más rezagados, aunque eso no mueva el H binario este año |
| **(E-7) Cobertura obligatoria** | $\sum_s z_{ks} = 1 \quad \forall k \in K$ con 6 a 15 años que no asiste | Constitución, art. 67. Hoy solo cubre a los rezagados de la cohorte (ampliarla es la mejora 4) |
| **(10a) Rezago del hogar** | $x_{i,\text{rez}} \le z_k \quad \forall k \in K(i)$ con $m_k \ge a_k^0 + 1$ | La privación del hogar se quita solo si **todos** sus niños quedan sin atraso |
| **(10b) Rezago no eliminable** | $x_{i,\text{rez}} = 0$ si algún $k \in K(i)$ tiene $a_k^0 + 1 > m_k$ | Con las reglas oficiales aplica a todos: ningún hogar quita el rezago binario en un año |
| **(Inas) Inasistencia del hogar** | $x_{i,\text{inas}} \le \sum_{s} z_{ks} \quad \forall k \in N(i)$ | La privación se quita solo si **todos** los niños que no asisten vuelven a estudiar, con E1 o con E2. **D2 (Martín, 5-nov):** el CLEI cuenta como asistencia (nota de P8586, ECV 2025: "se consideran asistiendo... programas para jóvenes y adultos por ciclos") |
| **(11) Logro educativo** | $\sum_{a \in L_i^C} g_a\, v_a \ge D_i\, x_{i,\text{logro}} \quad \forall i$ | Un ciclo por adulto en el año. La privación (promedio < 9) se quita solo si los años ganados cubren el déficit. En los 470 hogares donde no alcanza, obliga sola a $x_{i,\text{logro}} = 0$ |
| **(12) Analfabetismo** | $x_{i,\text{analf}} \le v_a \quad \forall i,\ \forall a \in L_i$ analfabeta | El ciclo 1 alfabetiza y suma años: se paga una sola vez |
| **(6) Dominios** | $x, y, z, t, v \in \{0,1\}$, $q_i \ge 0$ | — |

Se conservan los números del informe. La (3) y la variable $C_i$ se quitaron: M0 se recalcula después de resolver.

---

## 6. Después de resolver (no es parte del MILP)

Reportar siempre, total y por zona: **H, A, M0, severidad, SevEdu y costo**. Se recalculan a partir de $x_{ij}$ con las reglas del DANE: el H binario usa la regla oficial (quien cumple 18 sale del indicador), y la cohorte fija se usa **solo** en SevEdu.

**Decisión D4 (Martín, 5-nov-2026): H es la foto inicial (lectura a).** H se calcula con las edades de hoy y nadie cumple años dentro de H. El puntaje final es el de hoy menos las privaciones que el modelo pagó. Así no hay salidas "gratis" por el paso del tiempo (por ejemplo, el joven de 17 años que cumple 18) ni entradas nuevas (el niño que cumple 6 sin matrícula). H mide el impacto de la política, no la pobreza proyectada a un año. El paso del tiempo se modela solo en SevEdu (contrafactual $b_k$ y cohorte fija). Se descartó envejecer a los niños dentro de H, porque inflaría H con salidas que nadie pagó.

## 7. Cómo se escogen $\rho$, $r$ y $\rho_e$

Ningún valor se fija a ojo (decisiones de Martín, 9-nov; P21 y P24):

- **$\rho$ (techo de severidad): regla de la brecha.** El caso base usa el **menor $\rho$** con el que $A \le A_0$: quienes siguen pobres no quedan, en promedio, más pobres que hoy. Se halla por bisección entre la reducción de severidad que se obtiene «gratis» al maximizar $H$ y el máximo posible. El **codo** de la frontera $H$ contra severidad queda como sensibilidad (`rho_codo`). Con $B$ = $424 mil millones: $\rho$ = 47.4 % (codo 48.2 %). Con presupuestos muy bajos (por ejemplo $127.1 mil millones) la regla puede no ser alcanzable; en ese caso se corre sin techo y se declara.
- **$r$ (equidad por zona): codo de $H$ contra $r$.** En cada corrida se corre primero con $r = 0$ y se mide el piso libre (el menor porcentaje de pobres que sale en una zona). Se halla el mayor $r$ factible (bisección). Entre ambos extremos se evalúan 12 valores de $r$ (sin techo de severidad) y $r$ es el codo de $H$ contra $r$. Con $B$ = $127.1 / $187 / $424 mil millones: $r$ = 0.234 / 0.438 / 0.833. Limitación declarada: con presupuestos altos la curva es casi lineal y el codo está poco marcado (`mejoras/mejoras_modelo.md` §11).
- **Orden en la corrida base:** primero $r$, luego $\rho$ (con ese $r$), luego las dos etapas.
- **$\rho_e$** está decidido: 14 %, con la cobertura E-7.
- **Sensibilidad «sin penalizaciones»:** $\rho = 0$, $r = 0$ y sin techo de SevEdu (queda solo la cobertura E-7): $H$ puro. Con $B$ = $424 mil millones salen 592,196 personas, frente a 581,452 en el caso base, y $A$ crece (0.4399 contra $A_0$ = 0.4094).

## 8. Supuestos y limitaciones que hay que declarar

Ver el informe §7 (supuestos 1 a 8) y `mejoras/mejoras_modelo.md` (mejoras 1 a 9). Las que más pesan:
- p = 0.369 se toma como cumplimiento y no como valor esperado (mejora 3);
- un ciclo CLEI por año (mejora 6);
- los 6 meses del ICBF quitan el trabajo infantil;
- los hogares que ya reciben Renta Ciudadana (mejora 9).

## 9. Pendientes antes de programar

- ~~D1 a D5~~ **Decididas (4–5 nov):** dos etapas; el CLEI (E2) sí quita la inasistencia; E1 para los no asistentes sin rezago (sin E-7); H sobre la foto inicial; el hilo de programación hace el 05 y `parametros.py`. Ver `modelo1/justificacion_decisiones.md`.
- **El conteo `05_conteo_personas.py`:** $u_{ij}$, tabla de niños ($K$, $N$) y tabla de adultos ($\ell_a$, asiste, analfabeta, $g_a$).
- ~~Recalcular el rango de $B$~~ **Hecho:** de $105.9 a $742.1 mil millones (con la regla D8 de desempleo).

---

## 10. Cambios del 9-nov (respecto a la versión del 4-nov)

- **D6 (6-nov):** logro educativo con regla estricta, 32 hogares pueden salir por logro.
- **D7 (6-nov):** en hogares sin ocupados (caso 3) no se cuenta a los desocupados como adultos sin cobertura de empleo formal (evita doble cobro con EpV).
- **D8 (7-nov):** el desempleo de larga duración sin desocupado identificado no se paga en el caso base (8 hogares quitables en vez de 226); la imputación es la sensibilidad `desempleo_imputado`.
- **Objetivo:** dos etapas, sin $\lambda$; gap 1e-6; estado «Cortado» (auditoría H1 y H2).
- **$p$ = 0.369** (no 0.37).
- **$\rho$ y $r$** se calculan en cada corrida (sección 7), no se barren a mano.
- **Auditoría:** ver `auditoria/auditoria_modelo1.md` y la bitácora `modelo1/justificacion_decisiones.md` (P19 a P24).
