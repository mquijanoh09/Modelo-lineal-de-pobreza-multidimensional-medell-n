"""
modelo1.py  --  Modelo 1: max personas que salen de la pobreza s.a. presupuesto B.

Hereda de ModeloIPMBase (variables, salida de la pobreza y reglas educativas).
Aquí solo va lo propio del Modelo 1, por capas (se agregan de a una y cada una se prueba):

    capa 1  presupuesto (1) y objetivo max sum p_i y_i                [este archivo, paso 3.5b-1]
    capa 2  equidad por zona (4): sum_{i en d} p_i y_i >= r * Pobres_d     [paso 3.5b-2]
    capa 3  severidad: q_i, tangentes (7) y techo (8)                  [paso 3.5b-3]
    capa 4  SevEdu (E-5) con rho_e                                       [paso 3.5b-4]
    capa 5  desempate en dos etapas (D1)                                 [paso 3.5b-5]

Las capas 2 a 5 se activan con los argumentos r, rho, rho_e y etapa; mientras no estén
programadas, pedirlas lanza NotImplementedError (así no se usan por error).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # ...\Modelos

import numpy as np
import pulp

import parametros as P
from modelo_base import ModeloIPMBase


class Modelo1(ModeloIPMBase):
    TOL_H = 1e-6            # holgura relativa de H en la etapa 2

    def __init__(self, datos, B, r=0.0, rho=None, rho_e=None, etapa=1, H_star=None):
        super().__init__(datos)
        self.B = B                  # presupuesto del año, en pesos
        self.r = r                  # fracción mínima de pobres que debe salir en cada zona
        self.rho = rho              # reducción mínima de severidad (None = sin techo)
        self.rho_e = rho_e          # reducción mínima de SevEdu (None = sin techo)
        self.etapa = etapa          # 1: max H;  2: min severidad con H >= H*
        self.H_star = H_star
        if etapa == 2 and H_star is None:
            raise ValueError("La etapa 2 necesita H_star, el H óptimo de la etapa 1.")
        self.q = {}                 # q_i >= s_i^2, solo si hay techo de severidad

    def sentido(self):
        return pulp.LpMaximize if self.etapa == 1 else pulp.LpMinimize

    def agregar_restricciones_propias(self):
        # (1) Presupuesto: todo lo que se gasta en el año cabe en B
        self.prob += self.costo_total() <= self.B, "Pres"
        if self.r > 0:
            self.agregar_equidad()
        if self.rho is not None or self.etapa == 2:
            self.agregar_severidad()            # la etapa 2 minimiza severidad: necesita q aunque no haya techo
        if self.etapa == 2:
            # (D1) la etapa 2 no puede perder personas respecto a la etapa 1 (tolerancia 1e-6)
            self.prob += (pulp.lpSum(self.datos.hogares.at[i, "p"] * self.y[i] for i in self.y)
                          >= self.H_star * (1 - self.TOL_H)), "H_min"
        if self.rho_e is not None:
            # (E-5) techo de SevEdu: lo calcula la madre con coef_ks y SevEdu^N (datos_modelo)
            self.agregar_sevedu(self.rho_e)

    def agregar_equidad(self):
        """(4) Equidad: en cada zona P3 debe salir al menos la fracción r de sus personas pobres."""
        d = self.datos
        for zona, g in d.hogares.groupby("P3"):
            self.prob += (pulp.lpSum(d.hogares.at[i, "p"] * self.y[i] for i in g.index)
                          >= self.r * d.pobres_zona[zona]), f"Eq_{zona}"

    def definir_objetivo(self):
        d = self.datos
        if self.etapa == 1:
            # H: personas que salen de la pobreza = sum p_i y_i
            self.prob += pulp.lpSum(d.hogares.at[i, "p"] * self.y[i] for i in self.y), "H"
        else:
            # Etapa 2: entre los planes con ese H, el de menor severidad
            self.prob += pulp.lpSum(d.hogares.at[i, "p"] * self.q[i] for i in self.q), "Severidad"

    def agregar_severidad(self):
        """(7) q_i >= s_i^2 con tangentes y (8) techo: sum p_i q_i <= (1 - rho) * Sev0.

        s_i solo toma valores en A_i (sumas de pesos de subconjuntos de sus privaciones), y la
        parábola s^2 es convexa: las tangentes en esos puntos, q >= 2a*s - a^2, obligan a
        q_i >= s_i^2 de forma EXACTA en cada valor alcanzable. Con q libre hacia arriba, el
        techo (8) empuja q hacia abajo hasta el máximo de las tangentes.
        """
        d = self.datos
        for i in d.hogares.index:
            self.q[i] = pulp.LpVariable(f"q_{i}", lowBound=0)
            for a in d.A[i]:
                self.prob += self.q[i] >= 2 * a * self.s[i] - a * a, f"Tan_{i}_{int(round(a * 100))}"
        if self.rho is not None:
            self.prob += (pulp.lpSum(d.hogares.at[i, "p"] * self.q[i] for i in self.q)
                          <= (1 - self.rho) * d.Sev0), "Sev"


def resolver_dos_etapas(datos, B, r=0.0, rho=None, rho_e=None, gap_rel=ModeloIPMBase.GAP_REL, time_limit=300):
    """D1 (Martín, 4-nov): primero max H; luego min severidad con H >= H*.

    Devuelve (modelo_etapa2, info) con info = {"etapa1": ..., "etapa2": ..., "H_star": ...}.
    Con una sola corrida y un lambda pequeño, la tolerancia de HiGHS (gap 1e-4, unas 68
    personas) puede comerse el desempate; en dos etapas no.
    """
    m1 = Modelo1(datos, B, r=r, rho=rho, rho_e=rho_e, etapa=1).construir()
    info1 = m1.resolver(gap_rel=gap_rel, time_limit=time_limit)
    if info1["estado"] != "Optimal":
        return m1, {"etapa1": info1, "etapa2": None, "H_star": None}
    H_star = info1["objetivo"]
    m2 = Modelo1(datos, B, r=r, rho=rho, rho_e=rho_e, etapa=2, H_star=H_star).construir()
    info2 = m2.resolver(gap_rel=gap_rel, time_limit=time_limit)
    return m2, {"etapa1": info1, "etapa2": info2, "H_star": H_star}


def _evaluar(datos, B, r, rho, rho_e, gap_rel, time_limit):
    """Una corrida en dos etapas con techo rho. Devuelve la fila 'total' recalculada, o None si no es Optimal."""
    m, info = resolver_dos_etapas(datos, B, r=r, rho=rho, rho_e=rho_e, gap_rel=gap_rel, time_limit=time_limit)
    if info["etapa2"] is None or info["etapa2"]["estado"] != "Optimal":
        return None
    return m.recalcular().loc["total"]


def rho_maximo(datos, B, r=0.0, rho_e=None, gap_rel=ModeloIPMBase.GAP_REL, time_limit=300):
    """Mayor reduccion de severidad posible con el presupuesto B (min severidad sin exigir H). None si no es Optimal."""
    m = Modelo1(datos, B, r=r, rho_e=rho_e, etapa=2, H_star=0.0).construir()
    info = m.resolver(gap_rel=gap_rel, time_limit=time_limit)
    if info["estado"] != "Optimal":
        return None
    return 1 - info["objetivo"] / datos.Sev0


def rho_regla_brecha(datos, B, r=0.0, rho_e=None, tol=0.001, gap_rel=ModeloIPMBase.GAP_REL, time_limit=300):
    """Regla de la brecha (Martin, 9-nov): el MENOR rho con el que A (intensidad de quienes siguen pobres)
    no supera A0 (la de hoy). Biseccion sobre rho entre el nivel que se baja 'gratis' al maximizar H y el
    maximo posible. Devuelve (rho, info); rho = None si la regla no se alcanza con este B."""
    libre = _evaluar(datos, B, r, 0.0, rho_e, gap_rel, time_limit)
    if libre is None:
        return None, {"motivo": "sin solucion con rho = 0"}
    A0 = libre.A0
    if libre.A <= A0 + 1e-9:
        return 0.0, {"A0": A0, "A": libre.A, "H": libre.salen_personas, "nota": "se cumple sin techo"}
    lo = 1 - libre.severidad / libre.severidad_inicial          # no cumple aqui
    rmax = rho_maximo(datos, B, r, rho_e, gap_rel, time_limit)
    if rmax is None:
        return None, {"motivo": "no se pudo calcular el rho maximo"}
    hi = rmax * 0.995
    f_hi = _evaluar(datos, B, r, hi, rho_e, gap_rel, time_limit)
    if f_hi is None or f_hi.A > A0 + 1e-9:
        return None, {"A0": A0, "motivo": "la regla no se alcanza ni con el rho maximo"}
    mejor = f_hi
    while hi - lo > tol:
        mid = (lo + hi) / 2
        f = _evaluar(datos, B, r, mid, rho_e, gap_rel, time_limit)
        if f is not None and f.A <= A0 + 1e-9:
            hi, mejor = mid, f
        else:
            lo = mid
    return hi, {"A0": A0, "A": mejor.A, "H": mejor.salen_personas}


def _codo_decreciente(x, y):
    """Codo (Kneedle simplificado) de una curva decreciente: el punto mas alejado de la cuerda entre sus extremos."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or x.max() == x.min() or y.max() == y.min():
        return 0
    xn, yn = (x - x.min()) / (x.max() - x.min()), (y - y.min()) / (y.max() - y.min())
    return int(np.argmax(yn - (1 - xn)))


def r_codo(datos, B, rho_e=None, n_puntos=12, tol=0.005, gap_rel=ModeloIPMBase.GAP_REL, time_limit=300):
    """r del caso base (Martin, 9-nov): el codo de la curva H contra r para este B.

    Rango, todo sacado de los datos (nada inventado):
      - inicio = piso libre: el menor % de pobres que sale en una zona cuando r = 0 (por debajo de ese r la
        restriccion no actua);
      - fin    = el mayor r factible (biseccion con tolerancia tol).
    Entre ambos se evaluan n_puntos de r (sin techo de severidad) y se toma el codo de H contra r.
    Devuelve (r, info); r = None si no hay solucion con r = 0.
    """
    def corre(r):
        m, info = resolver_dos_etapas(datos, B, r=r, rho_e=rho_e, gap_rel=gap_rel, time_limit=time_limit)
        if info["etapa2"] is None or info["etapa2"]["estado"] != "Optimal":
            return None
        rec = m.recalcular()
        fr = [rec.at[nombre, "salen_personas"] / datos.pobres_zona[z] for z, nombre in P.ZONAS.items()]
        return rec.at["total", "salen_personas"], min(fr)

    libre = corre(0.0)
    if libre is None:
        return None, {"motivo": "sin solucion con r = 0"}
    H0, piso = libre
    lo, hi = piso, 1.0
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if corre(mid) is None:
            hi = mid
        else:
            lo = mid
    r_max = lo
    if r_max - piso < 1e-3:
        return float(piso), {"piso_libre": piso, "r_max": r_max, "H0": H0, "nota": "rango degenerado"}
    grilla = np.linspace(piso, r_max, n_puntos)
    H = []
    for r in grilla:
        c = corre(float(r))
        H.append(np.nan if c is None else c[0])
    ok = ~np.isnan(H)
    k = _codo_decreciente(grilla[ok], np.asarray(H)[ok])
    r = float(grilla[ok][k])
    return r, {"piso_libre": piso, "r_max": r_max, "H0": H0, "H_codo": float(np.asarray(H)[ok][k])}


def resolver_r(datos, B, r_pedido, rho_e=None, **kw):
    """Convierte el r pedido ('codo' o un numero) en el r numerico de la corrida. Devuelve (r, info)."""
    if r_pedido == "codo":
        return r_codo(datos, B, rho_e=rho_e, **kw)
    return float(r_pedido), {}


class _CostoMinimo(ModeloIPMBase):
    """Auxiliar: min costo_total sin presupuesto ni meta. Da el gasto forzoso (E-7 y, si se pide, SevEdu)."""
    def __init__(self, datos, rho_e=None):
        super().__init__(datos)
        self.rho_e = rho_e

    def sentido(self):
        return pulp.LpMinimize

    def agregar_restricciones_propias(self):
        if self.rho_e is not None:
            self.agregar_sevedu(self.rho_e)

    def definir_objetivo(self):
        self.prob += self.costo_total(), "Costo"


def rango_B(datos, rho_e=None, tol=1e-3):
    """Rango útil del presupuesto B (en pesos), sin equidad ni techo de severidad.

    B_min: el gasto forzoso. Por debajo el modelo es infactible porque la cobertura
           obligatoria (E-7) y el techo de SevEdu ya cuestan más que B.
    B_max: el menor B con el que sale de la pobreza todo lo que puede salir (H máximo);
           se encuentra por bisección. Más allá, más presupuesto no sube H.
    """
    m = _CostoMinimo(datos, rho_e).construir()
    m.resolver(gap_rel=1e-6, time_limit=60)
    B_min = pulp.value(m.costo_total())
    cota = (sum(datos.c.values()) + sum(datos.c_ks.values()) + sum(datos.C_RC.values())
            + sum(datos.c_v.values()))                       # pagar TODO lo posible
    top = Modelo1(datos, cota, rho_e=rho_e).construir()
    H_max = top.resolver(gap_rel=1e-6, time_limit=120)["objetivo"]
    lo, hi = B_min, cota
    while (hi - lo) / hi > tol:
        mid = (lo + hi) / 2
        info = Modelo1(datos, mid, rho_e=rho_e).construir().resolver(gap_rel=1e-6, time_limit=120)
        if info["estado"] == "Optimal" and info["objetivo"] >= H_max * (1 - 1e-6):
            hi = mid
        else:
            lo = mid
    return {"B_min": B_min, "B_max": hi, "H_max": H_max}
