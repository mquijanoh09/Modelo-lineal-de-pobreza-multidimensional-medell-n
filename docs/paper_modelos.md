# Paper condensado — formulaciones de los 4 modelos

Fuente: Hamie, Hlasny & Jouni (2024), *Multidimensional Poverty Alleviation: Policy Optimization and Impact Simulation*, ERF Working Paper 1742. PDF completo en `referencias/` (49 págs.). **Este archivo reemplaza leer el PDF**: tiene las ecuaciones de las págs. 12-16 y los apéndices 1 y A1-A3. Las páginas del paper se citan como (p. N) con la numeración impresa.

> Las secciones "Nota de implementación" son del equipo / asesor, **no** del paper.

---

## 1. Nomenclatura (Tabla A1, p. 34)

| Símbolo | Tipo | Significado | En nuestro proyecto |
|---|---|---|---|
| $I$, $J$ | conjunto | hogares, indicadores | 3,732 hogares de Antioquia; 15 indicadores |
| $k$ | parámetro | umbral de pobreza | 1/3 (puntaje ≥ 0.34, múltiplos de 0.01) |
| $w_j$ | parámetro | peso del indicador, $\sum_j w_j = 1$ | 0.1 / 0.05 / 0.04 |
| $M_{ij}$ | binario | privación inicial (1 = privado) | 15 columnas de HOGARES |
| $HS_i$ | parámetro | tamaño del hogar | `PERSONAS` |
| $HW_i$ | parámetro | peso estadístico (expansión) | `FEX_C` |
| $EpF_j$ | parámetro | esfuerzo (costo) para quitar una privación | costos en pesos (ver resumen) |
| $l_j, u_j$ | parámetro | cotas inferior/superior de esfuerzo por indicador | — |
| $MPI_s$ | parámetro | MPI inicial | M0 = 0.0387 |
| $MPI_r$ | parámetro | reducción exigida, en $[0,1]$ | — |
| $P_i$ | binario calculado | 1 si el hogar es pobre al inicio | `POBRE` |
| $N_{ij}$ | **variable** binaria | matriz de privaciones después de intervenir | — |
| $E_j$ | **variable** | esfuerzo en el indicador $j$ | — |
| $C_i$ | **variable** continua ≥ 0 | contribución del hogar al MPI final | — |

Modelo 3 (Tabla A2): $D$ = celdas geográficas, $d_i$ = celda del hogar, $I[d]$ = hogares de la celda $d$, $R_{ij} \sim U[0,1]$ fija, variable $E_{jd}$.
Modelo 4 (Tabla A3): $T$ = tipos de hogar (de clustering), $t_i$, $I[t]$, variable $E_{jt}$.

## 2. Medidas Alkire-Foster (p. 12)

$$P_i = 1 \iff \sum_j M_{ij} w_j \ge k \qquad\qquad C_i = \begin{cases}\sum_j M_{ij} w_j \cdot HS_i \cdot HW_i & P_i = 1\\ 0 & P_i = 0\end{cases}$$

$$MPI = \frac{\sum_i C_i}{\sum_i HS_i HW_i} \qquad H = \frac{\sum_i HS_i HW_i P_i}{\sum_i HS_i HW_i} \qquad I = MPI / H$$

$$UH_j = \frac{\sum_i M_{ij} HW_i HS_i}{\sum_i HW_i HS_i} \qquad MPI\_Cont_j = \frac{w_j \sum_i M_{ij} HW_i HS_i P_i}{\sum_i HW_i HS_i}$$

Ya implementadas en `04_linea_base.py` (`resumen()`, `contribuciones()`).

## 3. Modelo 1 — hogar, sin costo (p. 12-13). **No es un MILP**

Heurística iterativa: en cada iteración se elige el indicador con mayor $MPI\_Cont_j$ y se quitan privaciones hasta cumplir

$$\frac{\sum_i C_i}{\sum_i HS_i HW_i} \le MPI_s (1 - MPI_r) \tag{7}$$

- **1a determinístico:** dentro del indicador elegido atiende primero a los hogares con mayor $C_i$.
- **1b probabilístico:** elige hogares al azar entre los privados → Monte Carlo; número de corridas $n$ por el TLC (p. 13).

> ⚠️ **Nota:** nuestro `07_modelo1.py` (presupuesto fijo + equidad) **no** es el Modelo 1 del paper. Hay que justificar ese cambio en el informe.

## 4. Modelo 2 — hogar, minimiza costo, MILP (p. 14)

$$\min \sum_j E_j \tag{OBJ 2}$$

| Restricción | Ecuación |
|---|---|
| Con 1 | $N_{ij} \le M_{ij} \quad \forall i,j$ (solo se quitan privaciones) |
| Con 2 | $\sum_j N_{ij} w_j \ge k \Rightarrow C_i = \sum_j N_{ij} w_j HS_i HW_i$ |
| Con 3 | $\sum_j N_{ij} w_j < k \Rightarrow C_i = 0$ |
| Con 4 | $E_j = EpF_j \sum_i HW_i (M_{ij} - N_{ij}) \quad \forall j$ |
| Con 5-6 | $l_j \le E_j \le u_j \quad \forall j$ |
| Con 6 (meta) | $\dfrac{\sum_i C_i}{\sum_i HS_i HW_i} \le MPI_s (1 - MPI_r)$ |

Nota: la meta y la contribución $C_i$ usan **M0** (no H). Con 4 multiplica por $HW_i$, no por $HS_i$.

## 5. Linealización (Apéndice 1, p. 31-33)

Con 2 con binaria $b1_i$:

$$C_i + bigM\, b1_i \ge \sum_j N_{ij} w_j HS_i HW_i \tag{Lin 1}$$
$$C_i - bigM\, b1_i \le \sum_j N_{ij} w_j HS_i HW_i \tag{Lin 2}$$
$$\sum_j N_{ij} w_j - (1 - b1_i)\, bigM < k \tag{Lin 3}$$

Con 3 con binaria $b2_i$:

$$C_i - bigM\, b2_i \le 0 \tag{Lin 4}$$
$$\sum_j N_{ij} w_j + bigM (1 - b2_i) \ge k \tag{Lin 5}$$

El paper indica que se puede usar $b2_i = 1 - b1_i$ para ahorrar variables.

> ⚠️ **Convención de $b1_i$ en el paper:** $b1_i = 1$ activa Lin 3 ⇒ puntaje final $< k$ ⇒ **el hogar SALE de la pobreza**. $b1_i = 0$ ⇒ $C_i$ = su contribución (sigue pobre).
> La restricción de equidad del resumen ($\sum_{i\in d} HW_i HS_i\, b1_i \le (1-r)\,Pobres_d^0$) trata $b1_i$ como "sigue pobre". **Con la convención del paper debe escribirse con $(1 - b1_i)$.** Pendiente de decidir y de dejar escrito en el resumen.

### Nota de implementación (no del paper)
- **Desigualdad estricta en Lin 3:** los solvers no aceptan $<$. Como los puntajes son múltiplos de 0.01, usar $\le k - 0.01$, es decir $\le 0.33$.
- **bigM ajustado** (mejor que un número enorme): en las restricciones de puntaje basta $bigM = 1$ (el puntaje está en $[0,1]$); en Lin 1/2/4, $bigM_i = HS_i \cdot HW_i$ (máxima contribución posible del hogar $i$).
- **Reducción exacta:** solo los hogares con $P_i = 1$ pueden cambiar M0 o H; los no pobres se dejan fijos ($N_{ij} = M_{ij}$) o se excluyen del modelo.

## 6. Modelo 3 — focalización geográfica (p. 15)

$$\min \sum_j \sum_{d} E_{jd} \tag{OBJ 3}$$

Igual que el Modelo 2, cambiando:

$$E_{jd} = EpF_j \sum_{i \in I[d]} HW_i (M_{ij} - N_{ij}) \quad \forall j, d \tag{Con 4*}$$
$$\sum_d E_{jd} \ge l_j, \qquad \sum_d E_{jd} \le u_j \tag{Con 5*, 6*}$$

El esfuerzo $E_{jd}$ produce $E_{jd}/EpF_j$ cambios en la columna $j$ de la celda $d$. Probabilidad de que el hogar $i$ sea atendido:

$$\min\left(\frac{E_{jd}/EpF_j}{\sum_{i' \in I[d_i]} M_{i'j}},\ 1\right) \tag{9}$$

Con $R_{ij} \sim U[0,1]$ fija:

$$R_{ij} \le \frac{E_{jd}/EpF_j}{\sum_{i' \in I[d_i]} M_{i'j}} \Rightarrow N_{ij} = 0 \tag{Con 8}$$
$$R_{ij} > \frac{E_{jd}/EpF_j}{\sum_{i' \in I[d_i]} M_{i'j}} \Rightarrow N_{ij} = M_{ij} \tag{Con 9}$$

Linealización con $b2_{ij}$ y $b3_{ij} = 1 - b2_{ij}$ (Lin 6-10, p. 32-33). Aquí **sí** pueden cambiar hogares no pobres (desperdicio). En nuestro proyecto $d$ = `P3` (3 zonas).

Ratios de priorización (p. 9): Ratio 1 = P(privado en $j$ ⇒ pobre); Ratio 2 = P(sale de pobreza al quitar solo $j$).

## 7. Modelo 4 — geográfico + demográfico (p. 16)

$J = U \cup V$: $U$ = indicadores de bien privado (por tipo de hogar $t$), $V$ = de bien público (por celda $d$; p. ej. acueducto, alcantarillado).

$$\min \left[\sum_{j \in U} \sum_{t \in T} E_{jt} + \sum_{j \in V} \sum_{d \in D} E_{jd}\right] \tag{OBJ 4}$$
$$E_{jt} = EpF_{jt} \sum_{i \in I[t]} HW_i (M_{ij} - N_{ij}) \quad \forall j \in U, t \tag{Con 4**}$$

Con 10-11: mismo mecanismo estocástico de Con 8-9, pero con la celda $I[t]$. Los tipos $T$ salen de clustering (partición alrededor de medianas) sobre las privaciones privadas + un proxy de ingreso.

## 8. Supuestos del paper (p. 6-7)

1. El marco del IPM no cambia en el horizonte.
2. Indicadores independientes: intervenir uno no cambia otro.
3. Solo cambian los hogares atendidos (sin error de inclusión en los Modelos 1-2).
4. No todos los indicadores tienen que estar activos.
5. Costo marginal constante y estático.
6. Metas de reducción fijas.
7. Un hogar no pobre no puede volverse pobre.

## 9. Comparación (Tabla 1, p. 11)

Los Modelos 1-2 son los más eficientes (información perfecta). Los Modelos 3-4 son más realistas, pero desperdician recursos en hogares no pobres o en hogares que no salen de la pobreza. Comparar con **la misma reducción** de pobreza.
