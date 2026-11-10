"""
nucleo_pruebas.py  --  Núcleo aislado del Modelo 2 (subfases 3.2 y 3.3).

NO es el modelo: solo x, y, C_i y la meta, sin educación. Sirve para validar la censura
y la meta contra un algoritmo exacto (prueba_3_2.py, prueba_3_3.py). El modelo completo
es modelo2.py, que hereda de modelo_base.py.

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


def crear_x(privaciones, fijos_cero=()):
    """Variables x[(i, j)] binarias. Las privaciones fijas (no removibles) quedan en x = 0.

    Ojo: en PuLP una variable con cat="Binary" ignora upBound y vuelve a ser 0..1,
    así que las fijas se declaran enteras con cotas 0..0.
    """
    x = {}
    for i, js in privaciones.items():
        for j in js:
            if j in fijos_cero or (i, j) in fijos_cero:
                x[(i, j)] = pulp.LpVariable(f"x_{i}_{j}", 0, 0, cat="Integer")
            else:
                x[(i, j)] = pulp.LpVariable(f"x_{i}_{j}", cat="Binary")
    return x


def agregar_censura_y_meta(prob, hog, privaciones, x, y, meta_m, por_zona=False):
    """Agrega C_i, (2), (3) y la meta (global o por zona) al problema `prob`.

    hog          DataFrame de hogares pobres con columnas ID_HOGAR, p, c0, zona.
    privaciones  {ID_HOGAR: [indicadores con M_ij = 1]}
    x, y         dicts de variables binarias: x[(i, j)], y[i].
    meta_m       reducción relativa exigida de M0 (0.10 = 10 %); None = sin meta.
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

    if meta_m is None:                       # sin meta: lo usa meta_maxima()
        return C
    if por_zona:
        for d, g in hog.groupby("zona"):
            prob += (pulp.lpSum(C[i] for i in g.ID_HOGAR)
                     <= (1 - meta_m) * float((g.p * g.c0).sum()), f"Meta_{d}")
    else:
        prob += (pulp.lpSum(C.values())
                 <= (1 - meta_m) * float((hog.p * hog.c0).sum()), "Meta")
    return C


def construir_nucleo(hog, privaciones, costo, meta_m, por_zona=False, fijos_cero=()):
    """Núcleo: min costo (en millones) s.a. censura y meta. Devuelve (prob, x, y, C).

    fijos_cero: pares (i, j) o indicadores j cuya privación NO se puede quitar (x = 0).
    En 3.4 esto lo hacen las reglas de intervención (rezago, logro...); aquí sirve
    para probar meta_maxima() con un caso conocido.
    """
    prob = pulp.LpProblem("Modelo2_nucleo", pulp.LpMinimize)
    x = crear_x(privaciones, fijos_cero)
    y = {i: pulp.LpVariable(f"y_{i}", cat="Binary") for i in hog.ID_HOGAR}
    C = agregar_censura_y_meta(prob, hog, privaciones, x, y, meta_m, por_zona)
    prob += pulp.lpSum(costo[k] * v for k, v in x.items()) / ESCALA_COSTO, "Costo_total"
    return prob, x, y, C


def meta_maxima(hog, privaciones, fijos_cero=()):
    """Mayor reducción relativa de M0 que se puede lograr en cada zona (y en total).

    Se resuelve UN problema sin meta que minimiza sum C_i. Como las zonas no se
    tocan entre sí, minimizar el total minimiza también cada zona. Una meta m mayor
    que este valor deja el caso base infactible.
    Devuelve {zona: reducción, "total": reducción}.
    """
    prob = pulp.LpProblem("Modelo2_meta_maxima", pulp.LpMinimize)
    x = crear_x(privaciones, fijos_cero)
    y = {i: pulp.LpVariable(f"y_{i}", cat="Binary") for i in hog.ID_HOGAR}
    C = agregar_censura_y_meta(prob, hog, privaciones, x, y, None)
    prob += pulp.lpSum(C.values()), "Contribucion_minima"
    res = resolver(prob)
    if res["estado"] != "Optimal":
        raise RuntimeError(f"meta_maxima no es óptima: {res['estado']}")
    out = {}
    for d, g in hog.groupby("zona"):
        num0 = float((g.p * g.c0).sum())
        out[d] = 1 - sum(C[i].value() for i in g.ID_HOGAR) / num0
    out["total"] = 1 - sum(v.value() for v in C.values()) / float((hog.p * hog.c0).sum())
    return out


def resolver(prob, gap_rel=None, time_limit=None):
    """Resuelve con HiGHS y devuelve estado, objetivo y gap. gap/tiempo salen de parametros."""
    gap_rel = SOLVER_M2["gap_rel"] if gap_rel is None else gap_rel
    time_limit = SOLVER_M2["time_limit"] if time_limit is None else time_limit
    prob.solve(pulp.HiGHS(msg=False, gapRel=gap_rel, timeLimit=time_limit))
    return {"estado": pulp.LpStatus[prob.status],
            "objetivo_millones": pulp.value(prob.objective)}
