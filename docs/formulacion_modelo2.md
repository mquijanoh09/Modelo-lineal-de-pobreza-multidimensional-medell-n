# Modelo 2: formulación para programar

*Versión del 5 de noviembre de 2026, actualizada el 9-nov (meta por zona como caso base, prueba cruzada hecha, regla de desempleo). Basada en:*
- *el Modelo 2 del paper (Hamie, Hlasny y Jouni, 2024, p. 14; resumen en `docs/paper_modelos.md` §4);*
- *las mismas reglas de intervención y costos del Modelo 1 (`modelo1/formulacion_modelo1.md`).*

**La pregunta del Modelo 2:** ¿cuál es el **mínimo presupuesto** necesario para cumplir una meta de reducción de la pobreza fijada por el gobierno, por ejemplo bajar el M0 de Antioquia un 10 %?

Es la pregunta "al revés" del Modelo 1:
- **Modelo 1:** el presupuesto $B$ está fijo y se maximiza el número de personas que salen.
- **Modelo 2:** la meta está fija y se minimiza el costo.

Es el "first best": el Estado sabe exactamente quién es pobre y en qué está privado. Por eso sirve de referencia para medir cuánto más caros son los Modelos 3 y 4, que focalizan por zona.

> **Decisiones de Martín (5-nov-2026):**
> - **D-M2-1:** la meta es sobre **M0**. Es lo que usa el paper, lo que propone Jerónimo y lo que hace comparables los Modelos 2, 3 y 4.
> - **D-M2-2:** se mantiene la cobertura del art. 67 (E-7); el techo de SevEdu va solo como sensibilidad; no hay techo de severidad.
> - **D-M2-3 (5-nov):** la meta se exige en cada zona P3 (caso base); solo global es sensibilidad.
> - **D-M2-4 (5-nov):** el CLEI cuenta como asistencia: $x_{i,inas} \le \sum_s z_{ks}$.
> - **Regla de desempleo (7-nov, común con el Modelo 1):** el desempleo de larga duración sin persona identificada no es quitable. Efecto: la meta de 100 % cuesta $740.37 mil millones (con la regla anterior, $660.64); las metas de 5, 10 y 20 % no cambian.

---

## 1. Conjuntos

Son los mismos del Modelo 1: $I$ (523 hogares pobres), $J$, $J_i$, $D$ (3 zonas), $K$ (215 niños rezagados), $N$ (niños de 6 a 16 años que no asisten), $S$ (E1, E2), $L_i$ y $L_i^C$ (adultos) y $A_i$ (solo si se usa el techo de severidad).

**Por qué solo los pobres:** los hogares no pobres tienen $C_i = 0$ y, por el supuesto del paper, no se vuelven pobres. No cambian M0 ni H, así que excluirlos no cambia el óptimo (reducción exacta).

---

## 2. Parámetros

Todos los del Modelo 1 (pesos, $HW_i$, $HS_i$, $p_i$, costos, $M_i$, parámetros de educación), **excepto $B$**, que en este modelo se vuelve resultado. Se agregan:

| Símbolo | Significado | Valor / fuente |
|---|---|---|
| $\text{Pob}$, $\text{Pob}_d$ | Población total de Antioquia y de cada zona (pobres y no pobres), $\sum HW_i HS_i$ | Línea base (`04_linea_base.py`) |
| $M0^0$, $M0_d^0$ | M0 inicial, total y por zona | ≈ 0.0387 total |
| $m$ | Meta de reducción relativa de M0 ($MPI_r$ en el paper) | Escenarios: 5 %, 10 %, 20 % (los mismos de Jerónimo) |
| $m_d$ | Meta por zona (si se usa) | Escenario; por defecto $m_d = m$ |
| $U_i = p_i \cdot c_i^0$ | Contribución máxima del hogar al numerador de M0 (big-M ajustado) | Derivado |
| $l_j$, $u_j$ | Gasto mínimo y máximo por indicador (Con 5–6 del paper) | Opcional; por defecto sin límites |

---

## 3. Variables de decisión

Las mismas del Modelo 1: $x_{ij}$, $y_i$, $z_{ks}$, $t_i$, $v_a$ (y $q_i$ solo si se usa el techo de severidad). Se agrega una:

| Variable | Tipo | Significado |
|---|---|---|
| $C_i$ | Continua ≥ 0 | Contribución **censurada** del hogar $i$ al numerador de M0: $p_i s_i$ si sigue pobre y 0 si sale |

Recuerda que $s_i = \sum_{j \in J_i} w_j (1 - x_{ij})$ es el puntaje después de intervenir.

---

## 4. Función objetivo

$$\min \; \text{Costo} = \sum_i \sum_{j \in J_i^{simple}} c_{ij} x_{ij} + \sum_{k,s} c_{ks} z_{ks} + \sum_i C^{RC}_i t_i + \sum_i \sum_{a \in L_i^C} c^{C}_{d(i)} HW_i\, v_a$$

Es exactamente el lado izquierdo de la restricción de presupuesto (1) del Modelo 1. En el paper, $\min \sum_j E_j$ es lo mismo, agrupado por indicador. Cada programa se paga una sola vez: rezago, inasistencia, logro y analfabetismo se pagan por niño o por adulto.

---

## 5. Restricciones

### 5.1 Las que definen M0 (nuevas frente al Modelo 1)

| # | Ecuación | Para qué sirve |
|---|---|---|
| **(2) Salida de la pobreza** | $s_i \le 0.33 + M_i (1 - y_i) \quad \forall i$ | Igual que en el Modelo 1. Si $y_i = 1$, el hogar queda debajo del umbral. Es la Lin 3 del paper, con $\le 0.33$ en vez de $< k$, porque los puntajes son múltiplos de 0.01 y los solvers no aceptan $<$ |
| **(3) Contribución censurada** | $C_i \ge p_i\, s_i - U_i\, y_i \quad \forall i$ | Si el hogar sigue pobre ($y_i = 0$), obliga a $C_i \ge p_i s_i$: su privación cuenta en M0. Si sale ($y_i = 1$), el lado derecho es ≤ 0 y $C_i$ puede ser 0. Reemplaza las Lin 1, 2, 4 y 5 del paper con **una** sola desigualdad, porque al minimizar el costo y exigir un M0 bajo, el solver nunca tiene interés en inflar $C_i$ |
| **(M) Meta de M0** (decidido) | $\sum_i C_i \le (1 - m)\, M0^0 \cdot \text{Pob}$ | La meta política (Con 6 del paper): el M0 final, que es $\sum C_i / \text{Pob}$, debe bajar al menos un $m$ %. Ojo: el denominador es **toda** la población, no solo los pobres |
| **(M-d) Meta por zona** (caso base, D-M2-3; solo global es sensibilidad) | $\sum_{i \in d} C_i \le (1 - m_d)\, M0_d^0 \cdot \text{Pob}_d \quad \forall d$ | La versión de equidad territorial ("metas por zona" del plan original): obliga a cumplir la meta también en la zona rural dispersa, donde todo es más caro. Es el análogo de la restricción (4) del Modelo 1 |

**Si la meta fuera sobre H** (alternativa de D-M2-1): se quita $C_i$ y la (3), y la meta queda como $\sum_i p_i\, y_i \ge m_H \cdot \sum_i p_i$. El modelo se vuelve más simple, pero premia sacar a los que están cerca del umbral, que es justo lo que criticamos del objetivo H en el Modelo 1. Con M0, bajar privaciones a un hogar que sigue pobre **también** ayuda a la meta. Por eso M0 encaja mejor con el enfoque de equidad.

### 5.2 Las reglas de intervención (idénticas al Modelo 1)

No son decisiones de diseño: definen qué se puede hacer legalmente en un año y cuándo desaparece una privación. Se copian tal cual:

| # | Ecuación | Para qué sirve |
|---|---|---|
| (E-1) | $z_{ks} \le \text{elig}_{ks}$ | Solo estrategias legales |
| (E-2) | $\sum_s z_{ks} \le 1$ | Una estrategia por niño |
| (E-3) | $z_{k,E1} \le t_{i(k)}$ | Renta Ciudadana una vez por hogar |
| (10a)/(10b) | $x_{i,\text{rez}} \le z_k$ con $m_k \ge a_k^0 + 1$; $x_{i,\text{rez}} = 0$ si algún niño no se puede nivelar | El rezago binario no se quita en un año con las reglas oficiales |
| (Inas) | $x_{i,\text{inas}} \le \sum_{s} z_{ks} \quad \forall k \in N(i)$ | La inasistencia se quita solo si vuelven todos los niños, con E1 o con E2: el CLEI cuenta como asistencia (D2 del Modelo 1, nota de P8586 de la ECV 2025; decidido por Martín el 5-nov) |
| (11) | $\sum_{a \in L_i^C} g_a v_a \ge D_i\, x_{i,\text{logro}}$ | Logro con un ciclo CLEI por adulto en el año |
| (12) | $x_{i,\text{analf}} \le v_a$ por cada adulto analfabeta | El ciclo 1 se paga una sola vez |
| (6) | $x, y, z, t, v \in \{0,1\}$, $C_i \ge 0$ | — |

### 5.3 Capas de equidad del Modelo 1 (decidido)

| # | Ecuación | Recomendación para el Modelo 2 |
|---|---|---|
| (E-7) Cobertura art. 67 | $\sum_s z_{ks} = 1$ para cada niño de 6 a 15 años que no asiste | **Sí (caso base).** Es una obligación constitucional, no una preferencia. Si se quita, el Modelo 2 "ahorra" incumpliendo la ley |
| (E-5) Techo de SevEdu | $\sum \text{coef}_{ks} z_{ks} \ge \rho_e\, \text{SevEdu}^N_{1,\text{sin}}$ | **Sensibilidad.** Con meta sobre M0, el rezago binario no se mueve en un año, así que el modelo no invierte en él. Con $\rho_e = 14 %$ se mide cuánto cuesta no abandonar a los niños más atrasados |
| (7)+(8) Techo de severidad | $q_i \ge 2a s_i - a^2$; $\sum p_i q_i \le (1-\rho)\text{Sev}_0$ | **No en el caso base.** M0 ya premia bajar privaciones de quien sigue pobre. Se puede reportar la severidad después de resolver |
| (4) Equidad por zona | Se reemplaza por (M-d) | La meta por zona cumple ese papel |

---

## 6. Después de resolver

Reportar, total y por zona: **costo mínimo**, H, A, M0, severidad y SevEdu. Usar la misma tabla común de los 4 modelos (punto 10 de la agenda de Jerónimo). Reportar también el gap de HiGHS de cada corrida.

**Conexión con el Modelo 1 (útil para la sustentación; prueba HECHA en la auditoría del 7-nov, 6 de 6 casos):** si el Modelo 2 dice que la meta $m$ cuesta $B^*$, el Modelo 1 con $B = B^*$ debería sacar **al menos** tantas personas como saca el plan del Modelo 2. La razón es que el Modelo 1 maximiza justamente eso. Es una validación cruzada sencilla entre los dos códigos.

## 7. Por qué es un MILP pequeño

Comparado con el Modelo 1, se agregan 523 variables continuas $C_i$ y 523 restricciones (3). Se quitan $q_i$ y las 6,571 tangentes. HiGHS lo debería resolver en segundos para cada meta.

## 8. Pendientes antes de programar

- **Metas $m$** a correr (5 / 10 / 20 % como Jerónimo): decidido; (M-d) se usa en el caso base (D-M2-3).
- **Lo mismo que el Modelo 1:** el conteo `05_conteo_personas.py` y las decisiones D1 a D5 que aplican aquí (D2: si E2 quita la inasistencia; D3: E1 para no asistentes sin rezago).
