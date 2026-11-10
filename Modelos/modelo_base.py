"""
modelo_base.py
Clase madre de los Modelos 1 y 2: lo que los dos comparten.

    Modelo 1:  max personas que salen de la pobreza s.a. presupuesto B
    Modelo 2:  min costo s.a. meta de reducción de M0

Lo común es: las variables (x, y, z, t, v), la regla de salida de la pobreza (2) y las
reglas de intervención (E-2, E-3, E-7, 10a, Inas, 11, 12), el costo total, el resolver
y la recalculación de H, A, M0, severidad y costo a partir de la solución.

Lo propio de cada modelo lo escribe cada hija (patrón "template method"):
    construir() llama, en este orden, a
        crear_variables()                  [madre]
        agregar_salida_pobreza()           [madre]  restricción (2)
        agregar_reglas_intervencion()      [madre]  E-2, E-3, E-7, 10a, Inas, 11, 12
        agregar_restricciones_propias()    [hija]   presupuesto, equidad, censura, meta...
        definir_objetivo()                 [hija]

Nombres (acordados con el hilo del Modelo 2):
    self.datos, self.esc, self.prob
    self.x[(i, j)]  self.y[i]  self.z[(k, s)]  self.t[i]  self.v[a]   (variables)
    self.s[i]       puntaje del hogar después de intervenir (expresión lineal)
    i = ID_HOGAR, k y a = ID_PERSONA, s in {"E1", "E2", "E3"}, j = indicador

Versión de PuLP: 3.3.2 (la del .venv). No actualizar sin avisar: en 4.x cambia LpVariable.
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pulp

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parametros as P
from utils_dane import resumen_ipm

# Indicadores educativos que tienen reglas propias (no tienen costo propio c_ij)
REZ, INAS, LOGRO, ANALF = "rezago_escolar", "inasistencia_escolar", "logro_educativo", "analfabetismo"


def _val(var):
    """Valor 0/1 de una variable ya resuelta (None -> 0)."""
    v = var.value()
    return 0 if v is None else int(round(v))


class ModeloIPMBase:
    GAP_REL = 1e-6          # tolerancia por defecto de HiGHS (auditoría H2: con 1e-4 el ruido es de ~56 personas)
    TIME_LIMIT = 300        # segundos

    def __init__(self, datos, esc=None):
        self.datos = datos
        self.esc = datos.esc if esc is None else esc
        self.prob = None
        self.x, self.y, self.z, self.t, self.v, self.s = {}, {}, {}, {}, {}, {}
        self.info = {}      # estado, objetivo, gap, tiempo de la última resolución

    # ------------------------------------------------------------------ plantilla
    def construir(self):
        """Arma el problema completo. Las hijas no la reescriben: llenan los dos ganchos."""
        self.prob = pulp.LpProblem(self.__class__.__name__, self.sentido())
        self.crear_variables()
        self.agregar_salida_pobreza()
        self.agregar_reglas_intervencion()
        self.agregar_restricciones_propias()
        self.definir_objetivo()
        return self

    def sentido(self):
        """pulp.LpMaximize o pulp.LpMinimize: lo decide la hija."""
        raise NotImplementedError

    def agregar_restricciones_propias(self):
        raise NotImplementedError

    def definir_objetivo(self):
        raise NotImplementedError

    # ------------------------------------------------------------------ variables
    def crear_variables(self):
        d = self.datos
        # x_ij: una por cada privación del hogar. Si no se puede quitar este año, queda fija en 0.
        # OJO PuLP: cat="Binary" ignora upBound; por eso las fijas se declaran enteras con cotas 0..0.
        for i in d.hogares.index:
            for j in d.J[i]:
                nombre = f"x_{i}_{j}"
                if d.quitable[(i, j)]:
                    self.x[(i, j)] = pulp.LpVariable(nombre, cat="Binary")
                else:
                    self.x[(i, j)] = pulp.LpVariable(nombre, lowBound=0, upBound=0, cat="Integer")
        # y_i: el hogar sale de la pobreza
        for i in d.hogares.index:
            self.y[i] = pulp.LpVariable(f"y_{i}", cat="Binary")
        # z_ks: solo existe donde la estrategia es legalmente elegible (E-1 queda implícita)
        for k, estrategias in d.S_k.items():
            for s in estrategias:
                self.z[(k, s)] = pulp.LpVariable(f"z_{k}_{s}", cat="Binary")
        # t_i: Renta Ciudadana, solo en hogares donde algún niño puede volver con E1
        for (k, s) in self.z:
            if s == "E1":
                i = d.ninos.at[k, "hogar"]
                if i not in self.t:
                    self.t[i] = pulp.LpVariable(f"t_{i}", cat="Binary")
        # v_a: el adulto elegible hace su siguiente ciclo CLEI
        for a in d.c_v:
            self.v[a] = pulp.LpVariable(f"v_{a}", cat="Binary")

    # ------------------------------------------------------------------ (2) salida de la pobreza
    def agregar_salida_pobreza(self):
        d = self.datos
        for i in d.hogares.index:
            self.s[i] = pulp.lpSum(P.PESOS[j] * (1 - self.x[(i, j)]) for j in d.J[i])
            M_i = float(d.hogares.at[i, "M"])
            self.prob += self.s[i] <= P.K_GRID + M_i * (1 - self.y[i]), f"Sal_{i}"

    # ------------------------------------------------------------------ reglas de intervención
    def _suma_z(self, k, solo=None):
        """Suma de z_ks del niño k (todas sus estrategias, o solo las de `solo`)."""
        return pulp.lpSum(self.z[(k, s)] for s in self.datos.S_k[k] if solo is None or s in solo)

    def agregar_reglas_intervencion(self):
        d = self.datos
        # (E-2) una estrategia por niño (si tiene una sola, el binario ya lo garantiza)
        for k, estrategias in d.S_k.items():
            if len(estrategias) > 1:
                self.prob += self._suma_z(k) <= 1, f"E2_{k}"
        # (E-3) Renta Ciudadana una vez por hogar: el regreso con E1 exige t_i = 1
        for (k, s), var in self.z.items():
            if s == "E1":
                self.prob += var <= self.t[d.ninos.at[k, "hogar"]], f"E3_{k}"
        # (E-7) cobertura obligatoria (art. 67)
        for k in d.obligatorios:
            self.prob += self._suma_z(k) == 1, f"E7_{k}"
        for i in d.hogares.index:
            for j in d.J[i]:
                if not d.quitable[(i, j)]:
                    continue
                x = self.x[(i, j)]
                if j == REZ:       # (10a) todos los niños rezagados deben quedar sin atraso
                    for k in d.K_i.get(i, []):
                        buenas = [s for s in d.S_k[k] if d.d_ks[(k, s)] >= d.ninos.at[k, "atraso"] + 1]
                        self.prob += x <= pulp.lpSum(self.z[(k, s)] for s in buenas), f"Rez_{i}_{k}"
                elif j == INAS:    # (Inas) todos los niños que no asisten deben volver (E1 o CLEI)
                    for k in d.N_i[i]:
                        self.prob += x <= self._suma_z(k), f"Inas_{i}_{k}"
                elif j == LOGRO:   # (11) los años que ganan los adultos deben cubrir el déficit
                    self.prob += (pulp.lpSum(d.g_a[a] * self.v[a] for a in d.L_i.get(i, []))
                                  >= d.D_i[i] * x), f"Log_{i}"
                elif j == ANALF:   # (12) todo adulto analfabeta debe hacer el ciclo 1
                    for a in d.analfabetas_i[i]:
                        self.prob += x <= self.v[a], f"Analf_{i}_{a}"

    # ------------------------------------------------------------------ costo y SevEdu
    def costo_total(self):
        """Todo lo que se gasta en el año, en pesos (expresión lineal)."""
        d = self.datos
        return (pulp.lpSum(d.c[(i, j)] * self.x[(i, j)] for (i, j) in d.c)
                + pulp.lpSum(d.c_ks[ks] * var for ks, var in self.z.items())
                + pulp.lpSum(d.C_RC[i] * var for i, var in self.t.items())
                + pulp.lpSum(d.c_v[a] * var for a, var in self.v.items()))

    def agregar_sevedu(self, rho_e):
        """(E-5) Reducción mínima de SevEdu. Cada hija decide si la llama."""
        d = self.datos
        self.prob += (pulp.lpSum(d.coef_ks[ks] * var for ks, var in self.z.items())
                      >= rho_e * d.sevedu_sin), "SevEdu"

    # ------------------------------------------------------------------ resolver
    def resolver(self, gap_rel=None, time_limit=None, msg=False):
        gap_rel = self.GAP_REL if gap_rel is None else gap_rel
        time_limit = self.TIME_LIMIT if time_limit is None else time_limit
        t0 = time.time()
        self.prob.solve(pulp.HiGHS(msg=msg, gapRel=gap_rel, timeLimit=time_limit))
        gap = None
        try:                                    # gap real que reporta HiGHS (None si no hay)
            gap = float(self.prob.solverModel.getInfo().mip_gap)
        except Exception:
            pass
        estado = pulp.LpStatus[self.prob.status]
        # Auditoría H1: PuLP 3.3.2 traduce "límite de tiempo" de HiGHS como "Optimal". La señal
        # confiable es sol_status: 1 = óptimo demostrado, 2 = solución factible sin demostración.
        cortado = estado == "Optimal" and self.prob.sol_status != pulp.LpSolutionOptimal
        if cortado:
            estado = "Cortado"          # nunca se trata como óptimo (ni se pasa H* a la etapa 2)
        self.info = {"estado": estado,
                     "objetivo": pulp.value(self.prob.objective),
                     "gap": gap, "segundos": round(time.time() - t0, 2)}
        return self.info

    # ------------------------------------------------------------------ solución
    def solucion(self):
        """Tres tablas: qué se hizo en cada hogar, en cada niño y en cada adulto."""
        d = self.datos
        filas = []
        for i in d.hogares.index:
            quitadas = [j for j in d.J[i] if _val(self.x[(i, j)])]
            filas.append({"ID_HOGAR": i, "P3": d.hogares.at[i, "P3"], "p": d.hogares.at[i, "p"],
                          "sale": _val(self.y[i]), "t_renta": _val(self.t[i]) if i in self.t else 0,
                          "quitadas": ",".join(quitadas)})
        plan_hogar = pd.DataFrame(filas)
        plan_nino = pd.DataFrame(
            [{"ID_PERSONA": k, "ID_HOGAR": d.ninos.at[k, "hogar"], "estrategia": s}
             for (k, s), var in self.z.items() if _val(var)],
            columns=["ID_PERSONA", "ID_HOGAR", "estrategia"])
        plan_adulto = pd.DataFrame(
            [{"ID_PERSONA": a, "ID_HOGAR": d.adultos.at[a, "hogar"]} for a, var in self.v.items() if _val(var)],
            columns=["ID_PERSONA", "ID_HOGAR"])
        return plan_hogar, plan_nino, plan_adulto

    # ------------------------------------------------------------------ recalcular
    def recalcular(self):
        """H, A, M0, severidad, SevEdu y costo reales, por zona y total, a partir de la solución.

        No usa y_i del MILP: vuelve a calcular el puntaje de cada hogar con las privaciones
        quitadas (x) y aplica la regla del DANE (pobre si puntaje >= 1/3). Así comprueba al
        modelo con una cuenta independiente.
        """
        d = self.datos
        final = d.todos.c0.copy()                       # puntaje final de los 3,732 hogares
        for i in d.hogares.index:
            final[i] = round(d.hogares.at[i, "c0"] - sum(P.PESOS[j] for j in d.J[i] if _val(self.x[(i, j)])), 2)
        h = d.hogares.copy()
        h["final"] = final.reindex(h.index)
        h["sale"] = h.final < P.K - 1e-9
        costo_h = pd.Series(0.0, index=h.index)
        for (i, j) in d.c:
            costo_h[i] += d.c[(i, j)] * _val(self.x[(i, j)])
        for (k, s), var in self.z.items():
            costo_h[d.ninos.at[k, "hogar"]] += d.c_ks[(k, s)] * _val(var)
        for i, var in self.t.items():
            costo_h[i] += d.C_RC[i] * _val(var)
        for a, var in self.v.items():
            costo_h[d.adultos.at[a, "hogar"]] += d.c_v[a] * _val(var)
        h["costo"] = costo_h
        h["sev"] = h.p * h.final ** 2
        # SevEdu al final del año: cada niño de la cohorte con su atraso b_k menos lo que quita su estrategia
        coh = d.ninos.loc[d.K].copy()
        quita = {k: 0.0 for k in d.K}
        for (k, s), var in self.z.items():
            if k in quita and _val(var):
                quita[k] = d.d_ks[(k, s)]
        coh["sev_edu"] = coh.HW * ((coh.b - pd.Series(quita)) / (coh.e_k + 1)) ** 2
        coh["P3"] = coh.P3

        def resumen(mask_zona):
            todos = d.todos[mask_zona(d.todos.P3)]
            sub = h[mask_zona(h.P3)]
            pf = todos.c0.copy()
            pf.loc[sub.index] = sub.final
            H0, A0, M00 = resumen_ipm(todos.p, todos.c0, P.K)
            H, A, M0 = resumen_ipm(todos.p, pf, P.K)
            c = coh[mask_zona(coh.P3)]
            return {"salen_personas": float((sub.p * sub.sale).sum()),
                    "salen_hogares": int(sub.sale.sum()),
                    "H0": H0, "H": H, "A0": A0, "A": A, "M0_inicial": M00, "M0": M0,
                    "reduccion_M0": 1 - M0 / M00 if M00 > 0 else 0.0,
                    "severidad": float(sub.sev.sum()), "severidad_inicial": float((sub.p * sub.c0 ** 2).sum()),
                    "sevedu": float(c.sev_edu.sum()), "sevedu_inicial": float(
                        (c.HW * (c.b / (c.e_k + 1)) ** 2).sum()),
                    "costo": float(sub.costo.sum())}

        salida = {"total": resumen(lambda z: pd.Series(True, index=z.index))}
        for zona, nombre in P.ZONAS.items():
            salida[nombre] = resumen(lambda z, zona=zona: z == zona)
        return pd.DataFrame(salida).T
