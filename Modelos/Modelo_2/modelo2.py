"""
modelo2.py  --  Modelo 2: mínimo costo para cumplir una meta de reducción de M0.

Hereda de ModeloIPMBase (modelo_base.py): variables x, y, z, t, v, la salida de la
pobreza (2) y todas las reglas de intervención (E-2, E-3, E-7, 10a, Inas, 11, 12) ya
vienen de la madre. Aquí solo está lo propio del Modelo 2 (formulacion_modelo2.md):

    C_i >= 0                                          contribución censurada a M0
    Cen_<i>:   C_i >= p_i s_i - p_i c0_i y_i          (3)
    Meta_<d>:  sum_{i en d} C_i <= (1 - m) sum_{i en d} p_i c0_i     meta en cada zona (caso base)
    Meta:      sum_i C_i       <= (1 - m) sum_i p_i c0_i             solo global (sensibilidad)
    SevEdu     solo si esc["usar_sevedu"] (sensibilidad, D-M2-2)
    objetivo:  min costo_total() en MILLONES de pesos

Nota: M0^0 * Pob = sum p_i c0_i, así que la población total no hace falta.
Resultados (subfase 3.5): gasto_por_indicador(), tabla_comun(), guardar().
Escenario: parametros.escenario_m2(comun, m2). Uso:
    d = cargar_datos(); esc = P.escenario_m2()
    m = Modelo2(d, esc, meta_m=0.10).construir(); m.resolver(**P.SOLVER_M2)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # ...\Modelos

import pandas as pd
import itertools

import pulp

import parametros as P
from modelo_base import ModeloIPMBase, _val


class Modelo2(ModeloIPMBase):
    GAP_REL = P.SOLVER_M2["gap_rel"]          # 1e-6: con costos de ~1e11 el 1e-4 dejaría ~$10 M de holgura
    TIME_LIMIT = P.SOLVER_M2["time_limit"]

    def __init__(self, datos, esc, meta_m=None, objetivo="costo"):
        """meta_m: reducción relativa de M0 exigida (0.10 = 10 %); None = sin meta.
        objetivo: "costo" (el modelo) o "contribucion" (min sum C_i; solo lo usa meta_maxima)."""
        super().__init__(datos, esc)
        self.meta_m = meta_m
        self.objetivo = objetivo
        self.C = {}

    def sentido(self):
        return pulp.LpMinimize

    def agregar_restricciones_propias(self):
        h = self.datos.hogares                                   # índice i: p, c0, P3
        for i, r in h.iterrows():
            self.C[i] = pulp.LpVariable(f"C_{i}", lowBound=0)
            self.prob += self.C[i] >= r.p * self.s[i] - r.p * r.c0 * self.y[i], f"Cen_{i}"
        if self.meta_m is not None:
            techo = 1 - self.meta_m
            if self.esc.get("meta_por_zona", True):
                for d, g in h.groupby("P3"):
                    self.prob += (pulp.lpSum(self.C[i] for i in g.index)
                                  <= techo * float((g.p * g.c0).sum()), f"Meta_{d}")
            else:
                self.prob += (pulp.lpSum(self.C.values())
                              <= techo * float((h.p * h.c0).sum()), "Meta")
        if self.esc.get("usar_sevedu", False):
            self.agregar_sevedu(self.esc["rho_e"])                # E-5 como sensibilidad

    def definir_objetivo(self):
        if self.objetivo == "costo":
            self.prob += self.costo_total() / P.ESCALA_COSTO, "Costo_total"
        else:
            self.prob += pulp.lpSum(self.C.values()), "Contribucion_minima"

    @classmethod
    def meta_maxima(cls, datos, esc):
        """Mayor reducción de M0 por zona (y total) con TODAS las reglas y sin meta.

        Un solo problema que minimiza sum C_i. Como las zonas no comparten nada, minimizar el
        total minimiza cada zona. Una meta mayor que la menor de las tres deja el caso base
        infactible. Devuelve {P3: reducción, ..., "total": reducción}.
        """
        m = cls(datos, esc, meta_m=None, objetivo="contribucion").construir()
        info = m.resolver(gap_rel=1e-9)
        if info["estado"] != "Optimal":
            raise RuntimeError(f"meta_maxima no es óptima: {info}")
        h, out = datos.hogares, {}
        for d, g in h.groupby("P3"):
            out[d] = 1 - sum(m.C[i].value() for i in g.index) / float((g.p * g.c0).sum())
        out["total"] = 1 - sum(v.value() for v in m.C.values()) / float((h.p * h.c0).sum())
        return out

    # ------------------------------------------------------------------ resultados (3.5)
    def gasto_por_indicador(self):
        """Gasto en pesos por rubro y zona (el E_j del paper). Suma exactamente el costo total.

        Los 11 indicadores simples se pagan con x_ij. Los programas de educación se pagan por
        niño o adulto y no se pueden repartir entre rezago e inasistencia (un mismo z sirve a los
        dos), así que van en dos rubros: "educacion_ninos" (z y Renta Ciudadana t) y
        "educacion_adultos" (ciclos CLEI v, que sirven a logro y analfabetismo).
        Devuelve un DataFrame: filas = rubros, columnas = zonas, "total" y "participacion".
        """
        d = self.datos
        zona = d.hogares.P3
        gasto = {}

        def sumar(rubro, i, valor):
            if valor:
                fila = gasto.setdefault(rubro, {z: 0.0 for z in P.ZONAS})
                fila[int(zona[i])] += valor

        for (i, j), c in d.c.items():
            sumar(j, i, c * _val(self.x[(i, j)]))
        for (k, s), var in self.z.items():
            sumar("educacion_ninos", d.ninos.at[k, "hogar"], d.c_ks[(k, s)] * _val(var))
        for i, var in self.t.items():
            sumar("educacion_ninos", i, d.C_RC[i] * _val(var))
        for a, var in self.v.items():
            sumar("educacion_adultos", d.adultos.at[a, "hogar"], d.c_v[a] * _val(var))
        tabla = pd.DataFrame(gasto).T.reindex(columns=list(P.ZONAS)).fillna(0.0)
        tabla.columns = [P.ZONAS[z] for z in tabla.columns]
        tabla["total"] = tabla.sum(axis=1)
        tabla["participacion"] = tabla.total / tabla.total.sum() if tabla.total.sum() else 0.0
        return tabla.sort_values("total", ascending=False)

    def tabla_comun(self):
        """Tabla común de los 4 modelos (agenda de Jerónimo, punto 10): H, A, M0, severidad,
        SevEdu y costo en pesos, por zona y total, más lo que mide el cumplimiento de la meta."""
        rec = self.recalcular()
        cols = ["salen_personas", "salen_hogares", "H0", "H", "A", "M0_inicial", "M0", "reduccion_M0",
                "severidad", "severidad_inicial", "sevedu", "sevedu_inicial", "costo"]
        return rec[cols]

    @staticmethod
    def piso_e7(datos):
        """Costo mínimo de cumplir E-7 (art. 67), en pesos, sin usar el MILP (auditoría M2-H3).

        Por hogar con niños obligados se prueba cada combinación de estrategias y se toma la más
        barata; si alguna usa E1 se suma la Renta Ciudadana del hogar una sola vez.
        Es 0 si el escenario no exige E-7 (cobertura_art67 = False).
        """
        por_hogar = {}
        for k in datos.obligatorios:
            por_hogar.setdefault(datos.ninos.at[k, "hogar"], []).append(k)
        total = 0.0
        for i, ks in por_hogar.items():
            mejor = float("inf")
            for combo in itertools.product(*[datos.S_k[k] for k in ks]):
                c = sum(datos.c_ks[(k, s)] for k, s in zip(ks, combo))
                if "E1" in combo:
                    c += datos.C_RC[i]
                mejor = min(mejor, c)
            total += mejor
        return total

    def resumen(self):
        """Una fila con lo esencial de la corrida (para armar la curva costo vs. meta).

        Incluye el piso de E-7, el costo incremental de la meta sobre ese piso y la brecha A
        inicial, para comparar con la A de los que siguen pobres (auditoría M2-H3 y M2-H4)."""
        t = self.tabla_comun()
        fila = {"meta_m": self.meta_m, "escenario": self.esc.get("nombre"), **self.info}
        for k in ("salen_personas", "salen_hogares", "H", "A", "M0", "reduccion_M0", "severidad", "sevedu", "costo"):
            fila[k] = float(t.at["total", k])
        fila["A_inicial"] = float(self.datos.linea_base[1])
        fila["piso_E7"] = self.piso_e7(self.datos)
        # Solo vale si E-7 es la única obligación (caso base: lo valida 09_modelo2.py con meta 0 %).
        # Con SevEdu u otras reglas obligatorias, el piso es el costo del mismo escenario con meta 0 %
        # (ver 09_modelo2_barridos.py, auditoría N1). Por eso la columna se llama costo_sobre_piso_E7 (B1).
        fila["costo_mil_millones"] = fila["costo"] / 1e9
        fila["piso_E7_mil_millones"] = fila["piso_E7"] / 1e9
        fila["costo_sobre_piso_E7_mil_millones"] = (fila["costo"] - fila["piso_E7"]) / 1e9
        for zona in P.ZONAS.values():
            fila[f"reduccion_M0_{zona}"] = float(t.at[zona, "reduccion_M0"])
        return fila

    def guardar(self, carpeta, nombre):
        """Escribe en `carpeta` los CSV de esta corrida: tabla común, gasto y los tres planes."""
        carpeta = Path(carpeta)
        carpeta.mkdir(parents=True, exist_ok=True)
        plan_hogar, plan_nino, plan_adulto = self.solucion()
        salidas = {"tabla_comun": self.tabla_comun(), "gasto": self.gasto_por_indicador(),
                   "plan_hogar": plan_hogar, "plan_nino": plan_nino, "plan_adulto": plan_adulto}
        for sufijo, df in salidas.items():
            ruta = carpeta / f"{nombre}_{sufijo}.csv"
            df.to_csv(ruta, index=sufijo in ("tabla_comun", "gasto"), encoding="utf-8-sig")
        return carpeta
