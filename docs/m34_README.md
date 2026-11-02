# m34 — Monte Carlo del Modelo 3 y MILP + Monte Carlo del Modelo 4 (2-nov-2026)

Código autocontenido (no importa 05/06/07; reproduce sus convenciones y resultados).
Pensado para entrar al repo con el prefijo `m34_` propuesto a Martín.

| Archivo | Qué hace |
|---|---|
| `m34_datos.py` | Carga Antioquia completa + P3, línea base con asserts de regresión (3.732 / 523 / M0 = 0,038684), sorteo R por hogar idéntico a `05_modelo3.sortear_R` |
| `m34_mecanismo.py` | Enumeración de cortes (vectorizada) con `grupo` como **matriz** n×J (M3: zona para todo j; M4: zona para V, clúster para U), MILP del paper (min esfuerzo s.a. meta M0, Big-M por hogar), métricas ex post |
| `m34_clusters.py` | k-means k = 4 idéntico a `07_clusters.py` (reproduce 1.389 / 1.038 / 849 / 456) |
| `m34_test_regresion.py` | Reproduce 06: 45 pares, 630 cortes, 153,0, error de inclusión 62,1 % (HiGHS y CBC) |
| `m34_montecarlo.py` | 100 réplicas × metas {5, 10, 20 %} × variantes {pp, u1} para `m3` o `m4`; guarda por fila y reanuda si se corta |
| `m34_optimos_alternos.py` | Fija el esfuerzo óptimo y mide min/max del error de inclusión (detecta óptimos alternos) |
| `m34_resumen_mc.py` | Tabla de mediana [p5; p95] y boxplots M3 vs M4 |

```bash
R="data/DANE/DEPARTAMENTAL"
python3 m34_test_regresion.py "$R"
python3 m34_montecarlo.py "$R" m3 0 100 out/mc_m3.csv     # ~40 min con 2 núcleos ocupados
python3 m34_montecarlo.py "$R" m4 0 100 out/mc_m4.csv     # ~30 min
python3 m34_resumen_mc.py out/mc_m3.csv out/mc_m4.csv
```
Requiere `pulp` con HiGHS (`highspy`) o CBC; probado con PuLP 3.3.2 + highspy, Python 3.13.
Variantes: `pp` = V = K = HS (personas-privación, la del paper/06); `u1` = V = HW, K = EpF_j^zona·HW
(millones de pesos 2025, tabla de Martín §4, sensibilidad u = 1).
