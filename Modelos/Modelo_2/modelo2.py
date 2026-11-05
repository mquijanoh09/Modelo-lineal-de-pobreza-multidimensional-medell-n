"""
modelo2.py  --  Modelo 2: min costo total s.a. meta de M0 (subfase 3.2).

En esta subfase solo existe el NUCLEO del modelo (censura + meta global), armado
sobre las variables x (quitar privación) e y (el hogar sale de la pobreza).
Todavía no hay educación, logro ni clase madre: eso llega en 3.3 a 3.5.

Fórmulas (modelo2/formulacion_modelo2.md):
    (2)  s_i <= 0.33 + (c0_i - 0.33)(1 - y_i)          el hogar sale si queda <= 0.33
    (3)  C_i >= p_i s_i - U_i y_i,   C_i >= 0           contribución censurada a M0
    (M)  sum_i C_i <= (1 - m) * sum_i p_i c0_i          meta de reducción de M0
con p_i = HW_i * HS_i, U_i = p_i c0_i y s_i = sum_j w_j (1 - x_ij).

Nota: M0^0 * Pob = sum_i p_i c0_i (el numerador de M0), así que la población
total Pob se cancela y la meta no necesita saberla.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # ...\Modelos

import pulp

from parametros import K_GRID, PESOS, SOLVER_M2, ESCALA_COSTO


def agregar_censura_y_meta(prob, hog, privaciones, x, y, meta_m, por_zona=False):
    """Agrega C_i, (2), (3) y la meta (global o por zona) al problema `prob`.

    hog          DataFrame de hogares pobres con columnas ID_HOGAR, p, c0, zona.
    privaciones  {ID_HOGAR: [indicadores con M_ij = 1]}
    x, y         dicts de variables binarias: x[(i, j)], y[i].
    meta_m       reducción relativa exigida de M0 (0.10 = 10 %).
    Devuelve el dict C[i] de variables continuas.
    """
    C, s = {}, {}
    for r in hog.itertuples():
        i = r.ID_HOGAR
        s[i] = pulp.lpSum(PESOS[j] * (1 - x[(i, j)]) for j in privaciones[i])
        C[i] = pulp.LpVariable(f"C_{i}", lowBound=0)
        # (2) salida de la pobreza
        prob += s[i] <= K_GRID + (r.c0 - K_GRID) * (1 - y[i]), f"Sal_{i}"
        # (3) contribución censurada
        prob += C[i] >= r.p * s[i] - (r.p * r.c0) * y[i], f"Cen_{i}"

    if por_zona:
        for d, g in hog.groupby("zona"):
            prob += (pulp.lpSum(C[i] for i in g.ID_HOGAR)
                     <= (1 - meta_m) * float((g.p * g.c0).sum()), f"Meta_{d}")
    else:
        prob += (pulp.lpSum(C.values())
                 <= (1 - meta_m) * float((hog.p * hog.c0).sum()), "Meta")
    return C


def construir_nucleo(hog, privaciones, costo, meta_m, por_zona=False):
    """Núcleo 3.2: min costo (en millones) s.a. censura y meta. Devuelve (prob, x, y, C)."""
    prob = pulp.LpProblem("Modelo2_nucleo", pulp.LpMinimize)
    x = {(i, j): pulp.LpVariable(f"x_{i}_{j}", cat="Binary")
         for i, js in privaciones.items() for j in js}
    y = {i: pulp.LpVariable(f"y_{i}", cat="Binary") for i in hog.ID_HOGAR}
    C = agregar_censura_y_meta(prob, hog, privaciones, x, y, meta_m, por_zona)
    prob += pulp.lpSum(costo[k] * v for k, v in x.items()) / ESCALA_COSTO, "Costo_total"
    return prob, x, y, C


def resolver(prob, gap_rel=None, time_limit=None):
    """Resuelve con HiGHS y devuelve estado, objetivo y gap. gap/tiempo salen de parametros."""
    gap_rel = SOLVER_M2["gap_rel"] if gap_rel is None else gap_rel
    time_limit = SOLVER_M2["time_limit"] if time_limit is None else time_limit
    prob.solve(pulp.HiGHS(msg=False, gapRel=gap_rel, timeLimit=time_limit))
    return {"estado": pulp.LpStatus[prob.status],
            "objetivo_millones": pulp.value(prob.objective)}
