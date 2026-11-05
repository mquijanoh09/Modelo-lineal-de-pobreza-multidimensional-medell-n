"""
modelo_base.py
Clase madre de los Modelos 1 y 2 (decisión P7 / F2-4 de Martín, 5-nov-2026).

Patrón *template method*: construir() llama siempre en el mismo orden a
    crear_variables()               x, y, z, t, v
    agregar_reglas_intervencion()   (2) salida, E-1, E-2, E-3, E-7, (10a)/(10b), (Inas), (11), (12)
    agregar_restricciones_propias() lo de cada modelo (la hija lo escribe)
    definir_objetivo()              lo de cada modelo (la hija lo escribe)

Las reglas comunes son las de formulacion_modelo1.md §5 y formulacion_modelo2.md §5.2.
Los números de las restricciones son los de esas formulaciones; entre corchetes, la
ecuación del paper (docs/paper_modelos.md) cuando existe.
"""
import time

import numpy as np
import pulp

import parametros as P


class ModeloIPMBase:
    sentido = pulp.LpMaximize
    nombre = "ModeloIPM"

    def __init__(self, datos, fijos_cero=()):
        """datos: DatosIPM (datos_modelo.cargar_datos). fijos_cero: indicadores que no se pueden quitar."""
        self.D = datos
        self.esc = datos.esc
        self.fijos_cero = set(fijos_cero)
        self.prob = None
        self.info = {}

    # ==============================================================
    # Plantilla
    # ==============================================================
    def construir(self):
        self.prob = pulp.LpProblem(self.nombre, self.sentido)
        self.crear_variables()
        self.agregar_reglas_intervencion()
        self.agregar_restricciones_propias()
        self.definir_objetivo()
        n_var = len(self.prob.variables())
        n_res = len(self.prob.constraints)
        print(f"[{self.nombre}] {len(self.D.hog)} hogares pobres · {n_var:,} variables · {n_res:,} restricciones")
        return self

    def agregar_restricciones_propias(self):
        raise NotImplementedError

    def definir_objetivo(self):
        raise NotImplementedError

    # ==============================================================
    # Variables (formulacion_modelo1.md §3)
    # ==============================================================
    def crear_variables(self):
        D = self.D
        # x_ij: solo donde hay privación (j ∈ J_i)
        self.x = {(i, j): pulp.LpVariable(f"x_{i}_{j}", cat="Binary")
                  for i, js in D.priv.items() for j in js}
        # y_i = 1 si el hogar SALE de la pobreza (convención acordada con Jerónimo)
        self.y = {i: pulp.LpVariable(f"y_{i}", cat="Binary") for i in D.hog.ID_HOGAR}
        # z_ks: solo las estrategias legales del niño -> (E-1) z_ks <= elig_ks se cumple por construcción
        self.z = {}
        for r in D.ninos.itertuples():
            for s in D.estrategias:
                if getattr(r, f"elig_{s}"):
                    self.z[(r.ID_PERSONA, s)] = pulp.LpVariable(f"z_{r.ID_PERSONA}_{s}", cat="Binary")
        # t_i: Renta Ciudadana del hogar (solo hogares con algún niño elegible a E1)
        hog_e1 = {r.ID_HOGAR for r in D.ninos.itertuples() if (r.ID_PERSONA, "E1") in self.z}
        self.t = {i: pulp.LpVariable(f"t_{i}", cat="Binary") for i in sorted(hog_e1)}
        # v_a: el adulto elegible hace su siguiente ciclo CLEI (como máximo uno en el año)
        self.v = {r.ID_PERSONA: pulp.LpVariable(f"v_{r.ID_PERSONA}", cat="Binary")
                  for r in D.adultos.itertuples()}
        # puntaje después de intervenir: s_i = sum_{j ∈ J_i} w_j (1 - x_ij)
        self.s = {i: pulp.lpSum(P.PESOS[j] * (1 - self.x[(i, j)]) for j in js)
                  for i, js in D.priv.items()}

    # ==============================================================
    # Reglas de intervención (idénticas en los Modelos 1 y 2)
    # ==============================================================
    def agregar_reglas_intervencion(self):
        D, prob, x, z = self.D, self.prob, self.x, self.z
        hog = D.hog.set_index("ID_HOGAR")

        # (2) Salida de la pobreza [Lin 3]: s_i <= 0.33 + M_i (1 - y_i), M_i = c_i^0 - 0.33
        for i, r in hog.iterrows():
            prob += self.s[i] <= P.K_GRID + r.Mbig * (1 - self.y[i]), f"Sal_{i}"

        # indicadores que la prueba declara no removibles
        for (i, j), var in x.items():
            if j in self.fijos_cero:
                prob += var == 0, f"Fijo_{i}_{j}"

        ninos = D.ninos
        z_de = {k: [z[(k, s)] for s in D.estrategias if (k, s) in z] for k in ninos.ID_PERSONA}
        for r in ninos.itertuples():
            k = r.ID_PERSONA
            if z_de[k]:
                # (E-2) Una estrategia por niño
                prob += pulp.lpSum(z_de[k]) <= 1, f"E2_{k}"
            if (k, "E1") in z:
                # (E-3) Renta Ciudadana una vez por hogar
                prob += z[(k, "E1")] <= self.t[r.ID_HOGAR], f"E3_{k}"
            if r.obligatorio_E7:
                # (E-7) Cobertura obligatoria (Constitución, art. 67): 6 a 15 años que no asiste
                prob += pulp.lpSum(z_de[k]) == 1, f"E7_{k}"

        por_hogar = {i: g for i, g in ninos.groupby("ID_HOGAR")}
        self.info["rezago_no_eliminable"] = 0
        for i, js in D.priv.items():
            g = por_hogar.get(i)
            # (10a)/(10b) Rezago: el hogar lo quita solo si TODOS sus niños rezagados quedan sin atraso
            if "rezago_escolar" in js:
                cohorte = g[g.en_cohorte_sevedu] if g is not None else []
                eliminable = len(cohorte) > 0
                for rk in (cohorte.itertuples() if eliminable else []):
                    nivelan = [z[(rk.ID_PERSONA, s)] for s in D.estrategias
                               if (rk.ID_PERSONA, s) in z and getattr(rk, f"d_{s}") >= rk.atraso + 1]
                    if not nivelan:
                        eliminable = False
                        break
                    prob += x[(i, "rezago_escolar")] <= pulp.lpSum(nivelan), f"Rez10a_{i}_{rk.ID_PERSONA}"
                if not eliminable:
                    prob += x[(i, "rezago_escolar")] == 0, f"Rez10b_{i}"
                    self.info["rezago_no_eliminable"] += 1
            # (Inas) la inasistencia se quita solo si vuelven TODOS los no asistentes (E1 o CLEI, D2)
            if "inasistencia_escolar" in js:
                na = g[g.no_asiste_6_16] if g is not None else []
                if len(na) == 0 or any(not z_de[k] for k in na.ID_PERSONA):
                    prob += x[(i, "inasistencia_escolar")] == 0, f"Inas0_{i}"
                else:
                    for k in na.ID_PERSONA:
                        prob += x[(i, "inasistencia_escolar")] <= pulp.lpSum(z_de[k]), f"Inas_{i}_{k}"

        adultos = {i: g for i, g in D.adultos.groupby("ID_HOGAR")}
        for i, js in D.priv.items():
            a = adultos.get(i)
            # (11) Logro educativo: sum_a g_a v_a >= D_i x_i,logro (un ciclo por adulto en el año)
            if "logro_educativo" in js:
                gan = pulp.lpSum(r.g_a * self.v[r.ID_PERSONA] for r in a.itertuples()) if a is not None else 0
                prob += gan >= D.logro[i] * x[(i, "logro_educativo")], f"Logro11_{i}"
            # (12) Analfabetismo: x_i,analf <= v_a para cada adulto analfabeta del hogar
            if "analfabetismo" in js:
                for k in D.analfabetas.get(i, []):
                    if k in self.v:
                        prob += x[(i, "analfabetismo")] <= self.v[k], f"Analf12_{i}_{k}"
                    else:
                        prob += x[(i, "analfabetismo")] == 0, f"Analf12_{i}_{k}"

    # ==============================================================
    # Costo y capa SevEdu (la usan los dos modelos)
    # ==============================================================
    def costo_total(self):
        """Lado izquierdo de (1) del Modelo 1 = objetivo del Modelo 2. Cada programa se paga una vez."""
        D = self.D
        cz = {}
        for r in D.ninos.itertuples():
            for s in D.estrategias:
                if (r.ID_PERSONA, s) in self.z:
                    cz[(r.ID_PERSONA, s)] = getattr(r, f"costo_{s}")
        hw = D.hog.set_index("ID_HOGAR").HW
        rc = {i: hw[i] * P.RENTA_CIUDADANA_ANUAL / self.esc["p"] for i in self.t}
        cv = D.adultos.set_index("ID_PERSONA").costo_v
        return (pulp.lpSum(D.costo_x[k] * v for k, v in self.x.items() if k in D.costo_x)
                + pulp.lpSum(cz[k] * v for k, v in self.z.items())
                + pulp.lpSum(rc[i] * v for i, v in self.t.items())
                + pulp.lpSum(cv[a] * v for a, v in self.v.items()))

    def reduccion_sevedu(self):
        """sum_ks coef_ks z_ks: cuánto baja SevEdu al final del año frente a no intervenir."""
        D = self.D
        return pulp.lpSum(getattr(r, f"coef_{s}") * self.z[(r.ID_PERSONA, s)]
                          for r in D.ninos.itertuples() for s in D.estrategias
                          if (r.ID_PERSONA, s) in self.z)

    def agregar_sevedu(self, rho_e):
        """(E-5) Techo de SevEdu: sum coef z >= rho_e * SevEdu^N_{1,sin}."""
        self.prob += self.reduccion_sevedu() >= rho_e * self.D.SevEdu_sin, "E5_SevEdu"

    # ==============================================================
    # Resolver y recalcular
    # ==============================================================
    @staticmethod
    def _resolver(prob, gap_rel, time_limit):
        t0 = time.time()
        solver = pulp.HiGHS(msg=False, gapRel=gap_rel, timeLimit=time_limit)
        prob.solve(solver)
        gap = None
        try:
            gap = float(prob.solverModel.getInfo().mip_gap)
        except Exception:
            pass
        return {"estado": pulp.LpStatus[prob.status], "objetivo": pulp.value(prob.objective),
                "gap": gap, "segundos": round(time.time() - t0, 1)}

    def valores(self):
        def val(d):
            return {k: int(round(v.value() or 0)) for k, v in d.items()}
        return {"x": val(self.x), "y": val(self.y), "z": val(self.z), "t": val(self.t), "v": val(self.v)}

    def recalcular(self, sol=None):
        """H, A, M0, severidad, SevEdu y costo recalculados desde x (no desde y ni C_i).

        H y M0 usan toda la población de Antioquia (los no pobres no cambian: supuesto del paper).
        Devuelve {"total": {...}, zona: {...}} y la verificación de que y_i = 1 solo si sale.
        """
        D = self.D
        sol = sol or self.valores()
        x, z = sol["x"], sol["z"]
        h = D.hog.copy()
        h["s1"] = [round(sum(P.PESOS[j] for j in D.priv[i] if not x[(i, j)]), 2) for i in h.ID_HOGAR]
        h["pobre1"] = h.s1 >= P.K - 1e-9
        h["sale"] = ~h.pobre1
        y_ok = all(sol["y"][i] <= s for i, s in zip(h.ID_HOGAR, h.sale))

        k = D.ninos[D.ninos.en_cohorte_sevedu]
        red = {kid: sum(getattr(r, f"d_{s}") * z.get((kid, s), 0) for s in D.estrategias)
               for kid, r in zip(k.ID_PERSONA, k.itertuples())}
        k = k.assign(b1=[r.b_k - red[r.ID_PERSONA] for r in k.itertuples()])
        sevedu_k = k.HW * (k.b1 / (k.e_k + 1)) ** 2

        cz = {(r.ID_PERSONA, s): getattr(r, f"costo_{s}") for r in D.ninos.itertuples() for s in D.estrategias}
        hw = h.set_index("ID_HOGAR").HW
        cv = D.adultos.set_index("ID_PERSONA").costo_v
        costo_por_hogar = {i: 0.0 for i in h.ID_HOGAR}
        for (i, j), v in x.items():
            costo_por_hogar[i] += D.costo_x.get((i, j), 0.0) * v
        hog_de_nino = D.ninos.set_index("ID_PERSONA").ID_HOGAR
        for kz, v in z.items():
            costo_por_hogar[hog_de_nino[kz[0]]] += cz[kz] * v
        for i, v in sol["t"].items():
            costo_por_hogar[i] += hw[i] * P.RENTA_CIUDADANA_ANUAL / self.esc["p"] * v
        hog_de_adulto = D.adultos.set_index("ID_PERSONA").ID_HOGAR
        for a, v in sol["v"].items():
            costo_por_hogar[hog_de_adulto[a]] += cv[a] * v
        h["costo"] = h.ID_HOGAR.map(costo_por_hogar)

        def fila(g, pob, gk):
            pob_pobre = float((g.p * g.pobre1).sum())
            num = float((g.p * g.pobre1 * g.s1).sum())
            return {"hogares_pobres_0": len(g), "hogares_salen": int(g.sale.sum()),
                    "personas_salen": float((g.p * g.sale).sum()),
                    "H": pob_pobre / pob, "A": num / pob_pobre if pob_pobre else 0.0, "M0": num / pob,
                    "severidad": float((g.p * g.s1 ** 2).sum()),
                    "SevEdu": float(gk.sum()), "costo": float(g.costo.sum())}

        out = {"total": fila(h, D.Pob, sevedu_k)}
        zk = k.P3.values
        for d in sorted(h.zona.unique()):
            out[d] = fila(h[h.zona == d], D.Pob_d[d], sevedu_k[zk == d])
        out["y_consistente"] = y_ok
        self.hog_resultado = h
        return out


def tabla_resultados(rec, D, titulo=""):
    """Texto con la tabla de resultados total y por zona (regla: siempre por P3)."""
    lin = [f"\n{titulo}", f"{'Zona':<16}{'salen':>7}{'personas':>11}{'H':>8}{'A':>8}{'M0':>9}"
           f"{'Sev':>10}{'SevEdu':>9}{'costo ($ mm)':>15}"]
    for d in [k for k in rec if k not in ("total", "y_consistente")] + ["total"]:
        r = rec[d]
        nom = "Total" if d == "total" else P.ZONAS[d]
        lin.append(f"{nom:<16}{r['hogares_salen']:>4}/{r['hogares_pobres_0']:<3}{r['personas_salen']:>10,.0f}"
                   f"{r['H']:>8.2%}{r['A']:>8.2%}{r['M0']:>9.5f}{r['severidad']:>10,.0f}{r['SevEdu']:>9,.0f}"
                   f"{r['costo'] / 1e9:>15,.1f}")
    lin.append(f"Línea base: H = {sum(D.Pobres_d.values()) / D.Pob:.2%}, M0 = {D.M0_0:.6f}, "
               f"Sev0 = {D.Sev0:,.0f}, SevEdu_sin = {D.SevEdu_sin:,.0f} · y consistente: {rec['y_consistente']}")
    return "\n".join(lin)
