"""
modelo1.py  --  Modelo 1: presupuesto fijo B, max personas que salen de la pobreza (H)
sin abandonar a los más pobres (formulacion_modelo1.md).

Lo propio del Modelo 1 (lo común está en modelo_base.ModeloIPMBase):
    (1) Presupuesto     costo_total <= B                                   [Con 1-2 del paper, en $]
    (4) Equidad         sum_{i in d} p_i y_i >= r * Pobres_d^0   para cada zona d
    (7) Tangentes       q_i >= 2 a s_i - a^2   para cada a en A_i          (q_i = s_i^2 exacto)
    (8) Severidad       sum_i p_i q_i <= (1 - rho) * Sev0                   (ε-restricción)
    (E-5) SevEdu        sum coef_ks z_ks >= rho_e * SevEdu^N_{1,sin}        (rho_e = 14 % caso base)
Objetivo en dos etapas (D1, Martín 4-nov-2026):
    etapa 1: max sum_i p_i y_i                    -> H* (la incumbente)
    etapa 2: min sum_i p_i q_i  s.a. sum_i p_i y_i >= H*

Auxiliares para escoger B, r y rho (formulacion_modelo1.md §7):
    modo="sev_min"   min severidad con B y r fijos -> rho_max(B) = 1 - Sev_min / Sev0
    modo="r_max"     max r con B fijo (r como variable)
    modo="costo_H"   min costo s.a. sum p_i y_i >= H_meta (B que alcanza un H dado)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # ...\Modelos

import pulp

import parametros as P
from modelo_base import ModeloIPMBase


class Modelo1(ModeloIPMBase):
    nombre = "Modelo1"

    def __init__(self, datos, B=None, r=0.0, rho=0.0, rho_e=None, modo="H", H_meta=None, fijos_cero=()):
        """B en pesos (None = sin presupuesto). rho_e None = el del escenario (0.14)."""
        super().__init__(datos, fijos_cero)
        self.B, self.r, self.rho = B, r, rho
        self.rho_e = datos.esc["rho_e"] if rho_e is None else rho_e
        self.modo, self.H_meta = modo, H_meta
        self.sentido = pulp.LpMinimize if modo in ("sev_min", "costo_H") else pulp.LpMaximize

    # ------------------------------------------------------------------
    def agregar_restricciones_propias(self):
        D, prob = self.D, self.prob
        hog = D.hog
        self.personas_salen = pulp.lpSum(r.p * self.y[r.ID_HOGAR] for r in hog.itertuples())
        self.costo = self.costo_total()

        # (1) Presupuesto (en millones para que los coeficientes queden en escalas parecidas)
        if self.B is not None and self.modo != "costo_H":
            prob += self.costo / P.ESCALA_COSTO <= self.B / P.ESCALA_COSTO, "Presupuesto1"

        # (4) Equidad por zona; en modo r_max, r es una variable que se maximiza
        if self.modo == "r_max":
            self.r_var = pulp.LpVariable("r", lowBound=0, upBound=1)
        for d, g in hog.groupby("zona"):
            lado = pulp.lpSum(rr.p * self.y[rr.ID_HOGAR] for rr in g.itertuples())
            r = self.r_var if self.modo == "r_max" else self.r
            prob += lado >= r * D.Pobres_d[d], f"Equidad4_{d}"

        # (7) Tangentes: q_i >= 2 a s_i - a^2 para cada valor alcanzable a de s_i.
        # Como s_i solo toma valores en A_i, la envolvente de tangentes coincide con s_i^2
        # en esos puntos: q_i = s_i^2 exacto en el óptimo de la severidad.
        self.q = {i: pulp.LpVariable(f"q_{i}", lowBound=0) for i in hog.ID_HOGAR}
        for i, vals in D.A.items():
            for n, a in enumerate(vals):
                if a > 0:                                  # a = 0 da q_i >= 0, ya está en la cota
                    prob += self.q[i] >= 2 * a * self.s[i] - a * a, f"Tang7_{i}_{n}"
        self.severidad = pulp.lpSum(r.p * self.q[r.ID_HOGAR] for r in hog.itertuples())

        # (8) Techo de severidad (ε-restricción). Con rho = 0 no aprieta, pero se deja para la etapa 2.
        prob += self.severidad <= (1 - self.rho) * D.Sev0, "Severidad8"

        # (E-5) Techo de SevEdu (Modelo 1: restricción fija, rho_e = 14 %)
        if self.rho_e:
            self.agregar_sevedu(self.rho_e)

        if self.modo == "costo_H":
            prob += self.personas_salen >= self.H_meta, "MetaH"

    def definir_objetivo(self):
        if self.modo == "H":
            self.prob += self.personas_salen, "Etapa1_personas_salen"
        elif self.modo == "sev_min":
            self.prob += self.severidad, "Severidad_min"
        elif self.modo == "r_max":
            self.prob += self.r_var, "r_max"
        elif self.modo == "costo_H":
            self.prob += self.costo / P.ESCALA_COSTO, "Costo_min"

    # ------------------------------------------------------------------
    def resolver(self, gap_rel=None, time_limit=None, dos_etapas=True):
        """Resuelve. En modo "H" hace las dos etapas de D1 y devuelve el estado de ambas."""
        gap_rel = P.SOLVER_M1["gap_rel"] if gap_rel is None else gap_rel
        time_limit = P.SOLVER_M1["time_limit"] if time_limit is None else time_limit
        e1 = self._resolver(self.prob, gap_rel, time_limit)
        self.info["etapa1"] = e1
        if self.modo != "H" or not dos_etapas or e1["estado"] != "Optimal":
            return e1
        # Etapa 2: H* = valor de la incumbente (no la cota), así la restricción es factible
        H_star = sum(r.p * round(self.y[r.ID_HOGAR].value()) for r in self.D.hog.itertuples())
        self.info["H_star"] = H_star
        self.prob += self.personas_salen >= H_star * (1 - P.TOL_H_ETAPA2), "Etapa2_mantener_H"
        self.prob.sense = pulp.LpMinimize
        self.prob.setObjective(self.severidad)
        e2 = self._resolver(self.prob, gap_rel, time_limit)
        self.info["etapa2"] = e2
        return {"estado": e2["estado"], "objetivo": H_star, "gap": e1["gap"],
                "segundos": e1["segundos"] + e2["segundos"], "gap_etapa2": e2["gap"],
                "severidad_etapa2": e2["objetivo"]}


def correr(D, B, r=0.0, rho=0.0, rho_e=None, **kw):
    """Construye, resuelve en dos etapas y recalcula. Devuelve (modelo, estado, resultados)."""
    m = Modelo1(D, B=B, r=r, rho=rho, rho_e=rho_e, **kw).construir()
    est = m.resolver()
    rec = m.recalcular() if est["estado"] == "Optimal" else None
    return m, est, rec
