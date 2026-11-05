---
paths:
  - "Modelos/05_*.py"
  - "Modelos/datos_modelo.py"
  - "Modelos/modelo_base.py"
  - "Modelos/Modelo_1/**"
  - "Modelos/Modelo_2/**"
---

# Reglas para los scripts de modelación (05 en adelante)

- Antes de escribir un modelo, muestra la formulación (conjuntos, parámetros, variables, objetivo, restricciones) y pide confirmación. Cita la ecuación de `docs/paper_modelos.md` (p. ej. "Con 4", "Lin 3") en un comentario sobre cada restricción.
- Pon nombre a cada restricción en PuLP (`prob += expr, "Con4_<j>"`) para poder rastrearla y explicarla.
- Trabaja solo con los hogares pobres ($P_i = 1$); los no pobres no cambian H ni M0. Deja el número de hogares y de variables impreso al construir el modelo.
- bigM ajustado por hogar: $M_i = c_i^0 - 0.33$ en la restricción de salida del Modelo 1 (en los demás modelos, la más ajustada posible; $HS_i \cdot HW_i$ en las de $C_i$ si se usan). Nunca uses 1e9.
- Severidad (Modelo 1): $q_i \ge 2a\,s_i - a^2$ para cada valor alcanzable $a$ de $s_i$ (sumas de pesos de subconjuntos de $J_i$), con $s_i$ sin censurar; techo $\sum p_iq_i \le (1-\rho)\,\text{Sev}_0$. Si el desempate va con $\lambda$, usa `mip_rel_gap = 0`; si no, dos etapas.
- Escribe "< k" como "<= 0.33" (puntajes en múltiplos de 0.01).
- Después de resolver:
  1. imprime el estado y el valor objetivo;
  2. recalcula H, A, M0 y severidad desde $N_{ij}$ con la misma fórmula de `resumen()` en `04_linea_base.py`, sin confiar en $C_i$. Como `04_linea_base.py` es un script y no se puede importar, propón mover esa función a `utils_dane.py`;
  3. reporta por zona (P3).
- Lee los parámetros de `Modelos/parametros.py`; no escribas números a mano en los modelos.
- Prueba primero con una muestra pequeña (p. ej. 50 hogares pobres) y solo después con los 523.
