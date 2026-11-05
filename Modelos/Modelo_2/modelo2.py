"""
modelo2.py  --  Modelo 2: min costo total del año s.a. meta de M0 (formulacion_modelo2.md).

Dos niveles en este archivo:
  * Núcleo (subfases 3.2 y 3.3, escrito por Martín): construir_nucleo() y meta_maxima() con
    costos dados por par (i, j). Lo usan prueba_3_2.py y prueba_3_3.py contra algoritmos exactos.
  * Clase Modelo2(ModeloIPMBase) (subfases 3.4 a 3.5): el modelo completo con las reglas de
    intervención comunes (modelo_base.py), E-7 siempre, SevEdu como sensibilidad (D-M2-2) y la
    meta en cada zona P3 (D-M2-3).

Fórmulas propias del Modelo 2:
    (2)  s_i <= 0.33 + (c0_i - 0.33)(1 - y_i)          el hogar sale si queda <= 0.33   [Lin 3]
    (3)  C_i >= p_i s_i - U_i y_i,   C_i >= 0           contribución censurada a M0      [Lin 1, 2, 4, 5]
    (M)  sum_i C_i <= (1 - m) * sum_i p_i c0_i          meta de reducción de M0          [Con 6]
    (M-d) lo mismo en cada zona d (caso base; implica la global)
con p_i = HW_i * HS_i, U_i = p_i c0_i y s_i = sum_j w_j (1 - x_ij).

Por qué basta una desigualdad en (3): al minimizar el costo con un techo sobre sum C_i, el solver
nunca gana nada inflando C_i, así que C_i = max(p_i s_i - U_i y_i, 0) en el óptimo. U_i = p_i c0_i es
el big-M más ajustado: es el mayor valor que puede tomar p_i s_i (s_i <= c0_i).

Nota: M0^0 * Pob = sum_i p_i c0_i (el numerador de M0), así que la población total Pob se cancela y
la meta no necesita saberla.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # ...\Modelos

import pulp

import parametros as P
from parametros import K_GRID, PESOS, SOLVER_M2, ESCALA_COSTO
from modelo_base import ModeloIPMBase


# ======================================================================
# Núcleo (subfases 3.2 y 3.3)
# ======================================================================
def agregar_censura(prob, hog, s, y):
    """(3) C_i >= p_i s_i - U_i y_i con U_i = p_i c0_i. Devuelve el dict C[i]."""
    C = {}
    for r in hog.itertuples():
        i = r.ID_HOGAR
        C[i] = pulp.LpVariable(f"C_{i}", lowBound=0)
        prob += C[i] >= r.p * s[i] - (r.p * r.c0) * y[i], f"Cen_{i}"
    return C


def agregar_meta(prob, hog, C, meta_m, por_zona):
    """(M) meta global, o (M-d) una por zona P3 (que implica la global)."""
    if por_zona:
        for d, g in hog.groupby("zona"):
            prob += (pulp.lpSum(C[i] for i in g.ID_HOGAR)
                     <= (1 - meta_m) * float((g.p * g.c0).sum()), f"Meta_{d}")
    else:
        prob += (pulp.lpSum(C.values())
                 <= (1 - meta_m) * float((hog.p * hog.c0).sum()), "Meta")


def agregar_censura_y_meta(prob, hog, privaciones, x, y, meta_m, por_zona=False):
    """Agrega (2), C_i, (3) y la meta (global o por zona) al problema `prob`.

    hog          DataFrame de hogares pobres con columnas ID_HOGAR, p, c0, zona.
    privaciones  {ID_HOGAR: [indicadores con M_ij = 1]}
    x, y         dicts de variables binarias: x[(i, j)], y[i].
    meta_m       reducción relativa exigida de M0 (0.10 = 10 %); None = sin meta.
    Devuelve el dict C[i] de variables continuas.
    """
    s = {}
    for r in hog.itertuples():
        i = r.ID_HOGAR
        s[i] = pulp.lpSum(PESOS[j] * (1 - x[(i, j)]) for j in privaciones[i])
        # (2) salida de la pobreza
        prob += s[i] <= K_GRID + (r.c0 - K_GRID) * (1 - y[i]), f"Sal_{i}"
    C = agregar_censura(prob, hog, s, y)
    if meta_m is not None:
        agregar_meta(prob, hog, C, meta_m, por_zona)
    return C


def _variables_nucleo(prob, hog, privaciones, fijos_cero):
    x = {(i, j): pulp.LpVariable(f"x_{i}_{j}", cat="Binary")
         for i, js in privaciones.items() for j in js}
    y = {i: pulp.LpVariable(f"y_{i}", cat="Binary") for i in hog.ID_HOGAR}
    for (i, j), v in x.items():
        if j in fijos_cero:
            prob += v == 0, f"Fijo_{i}_{j}"
    return x, y


def construir_nucleo(hog, privaciones, costo, meta_m, por_zona=False, fijos_cero=()):
    """Núcleo 3.2/3.3: min costo (en millones) s.a. censura y meta. Devuelve (prob, x, y, C).
    fijos_cero: indicadores que no se pueden quitar (x_ij = 0), para las pruebas."""
    prob = pulp.LpProblem("Modelo2_nucleo", pulp.LpMinimize)
    x, y = _variables_nucleo(prob, hog, privaciones, fijos_cero)
    C = agregar_censura_y_meta(prob, hog, privaciones, x, y, meta_m, por_zona)
    prob += pulp.lpSum(costo[k] * v for k, v in x.items()) / ESCALA_COSTO, "Costo_total"
    return prob, x, y, C


def meta_maxima(hog, privaciones, fijos_cero=()):
    """Reducción máxima de M0 por zona sin límite de costo (F2-3, versión núcleo).

    min sum_i C_i sin meta. Las restricciones son por hogar, así que el problema se separa:
    cada hogar llega a su menor C_i y la suma por zona es la menor posible en esa zona.
    Devuelve {zona: m_max_d, "total": m_max}.
    """
    prob = pulp.LpProblem("Modelo2_meta_max", pulp.LpMinimize)
    x, y = _variables_nucleo(prob, hog, privaciones, fijos_cero)
    C = agregar_censura_y_meta(prob, hog, privaciones, x, y, None)
    prob += pulp.lpSum(C.values()), "Min_contribucion"
    resolver(prob)
    return _reduccion_por_zona(hog, {i: C[i].value() for i in C})


def _reduccion_por_zona(hog, Cval):
    out = {}
    for d, g in hog.groupby("zona"):
        out[d] = 1 - sum(Cval[i] for i in g.ID_HOGAR) / float((g.p * g.c0).sum())
    out["total"] = 1 - sum(Cval.values()) / float((hog.p * hog.c0).sum())
    return out


def resolver(prob, gap_rel=None, time_limit=None):
    """Resuelve con HiGHS y devuelve estado, objetivo y gap. gap/tiempo salen de parametros."""
    gap_rel = SOLVER_M2["gap_rel"] if gap_rel is None else gap_rel
    time_limit = SOLVER_M2["time_limit"] if time_limit is None else time_limit
    prob.solve(pulp.HiGHS(msg=False, gapRel=gap_rel, timeLimit=time_limit))
    return {"estado": pulp.LpStatus[prob.status],
            "objetivo_millones": pulp.value(prob.objective)}


# ======================================================================
# Modelo completo (subfases 3.4 y 3.5)
# ======================================================================
class Modelo2(ModeloIPMBase):
    """min costo_total s.a. reglas comunes + (3) + meta de M0.

    meta_m        reducción relativa de M0 exigida (None con modo="meta_max")
    modo          "costo" (el Modelo 2) o "meta_max" (F2-3: min sum C_i, sin meta ni costo)
    El escenario (P.escenario_m2) trae meta_por_zona, usar_sevedu y rho_e.
    """
    sentido = pulp.LpMinimize
    nombre = "Modelo2"

    def __init__(self, datos, meta_m=None, modo="costo", fijos_cero=()):
        super().__init__(datos, fijos_cero)
        self.meta_m, self.modo = meta_m, modo
        self.por_zona = datos.esc.get("meta_por_zona", True)
        self.usar_sevedu = datos.esc.get("usar_sevedu", False)

    def agregar_restricciones_propias(self):
        # (2) ya está en las reglas comunes; aquí van (3) y la meta
        self.C = agregar_censura(self.prob, self.D.hog, self.s, self.y)
        if self.modo == "costo":
            agregar_meta(self.prob, self.D.hog, self.C, self.meta_m, self.por_zona)
        # (E-5) SevEdu solo en la sensibilidad "con_sevedu" (D-M2-2); E-7 va siempre en las reglas comunes
        if self.usar_sevedu:
            self.agregar_sevedu(self.esc["rho_e"])

    def definir_objetivo(self):
        if self.modo == "costo":
            self.prob += self.costo_total() / ESCALA_COSTO, "Costo_total"
        else:
            self.prob += pulp.lpSum(self.C.values()), "Min_contribucion"

    def resolver(self, gap_rel=None, time_limit=None):
        gap_rel = SOLVER_M2["gap_rel"] if gap_rel is None else gap_rel
        time_limit = SOLVER_M2["time_limit"] if time_limit is None else time_limit
        est = self._resolver(self.prob, gap_rel, time_limit)
        if est["estado"] == "Optimal" and self.modo == "costo":
            est["costo"] = est["objetivo"] * ESCALA_COSTO
        self.info["solver"] = est
        return est

    def meta_maxima(self):
        """{zona: m_max_d, "total": m_max} a partir de la solución en modo meta_max."""
        return _reduccion_por_zona(self.D.hog, {i: v.value() for i, v in self.C.items()})


def meta_maxima_completa(D):
    """F2-3 con el modelo completo (E-7 activa, reglas de intervención, sin costo)."""
    m = Modelo2(D, modo="meta_max").construir()
    est = m.resolver()
    if est["estado"] != "Optimal":
        raise RuntimeError(f"meta_maxima: {est['estado']}")
    return m.meta_maxima()


def correr(D, meta_m, time_limit=None):
    """Construye, resuelve y recalcula. Devuelve (modelo, estado, resultados o None)."""
    m = Modelo2(D, meta_m=meta_m).construir()
    est = m.resolver(time_limit=time_limit)
    rec = m.recalcular() if est["estado"] == "Optimal" else None
    return m, est, rec
