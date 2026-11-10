"""
prueba_3_5a.py  --  Prueba del paso 3.5a (ModeloIPMBase).

Usa una hija mínima de prueba (max personas que salen con un presupuesto) solo para
poder resolver. Revisa: conteo de variables y restricciones, reglas educativas,
variables fijas, y que recalcular() (cuenta independiente) coincida con el MILP.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # ...\Modelos

import pulp

from datos_modelo import cargar_datos
from modelo_base import ModeloIPMBase, _val


class HijaPrueba(ModeloIPMBase):
    """max sum p_i y_i  s.a.  costo_total <= B  (solo para probar la madre)."""
    def __init__(self, datos, B):
        super().__init__(datos)
        self.B = B

    def sentido(self):
        return pulp.LpMaximize

    def agregar_restricciones_propias(self):
        self.prob += self.costo_total() <= self.B, "Pres"

    def definir_objetivo(self):
        d = self.datos
        self.prob += pulp.lpSum(d.hogares.at[i, "p"] * self.y[i] for i in self.y), "H"


def ok(c):
    return "OK   " if c else "FALLA"


def main():
    d = cargar_datos()
    m = HijaPrueba(d, B=3e11).construir()
    prob = m.prob
    pref = {}
    for nombre in prob.constraints:
        k = nombre.split("_")[0]
        pref[k] = pref.get(k, 0) + 1
    n_x = sum(len(v) for v in d.J.values())
    n_fijas = sum(1 for v in d.quitable.values() if not v)
    print(f"{ok(len(m.x) == n_x)} x: {len(m.x)} (privaciones {n_x}); fijas en 0: {n_fijas}")
    print(f"{ok(len(m.y) == 523)} y: {len(m.y)}")
    print(f"{ok(len(m.z) == sum(len(v) for v in d.S_k.values()))} z: {len(m.z)} (E1 {sum(1 for k in m.z if k[1]=='E1')}, E2 {sum(1 for k in m.z if k[1]=='E2')})")
    print(f"{ok(len(m.v) == 894)} v: {len(m.v)} (adultos elegibles a CLEI: 894)")
    print(f"     t: {len(m.t)} hogares con alguna opción de E1")
    print(f"{ok(pref.get('Sal') == 523)} restricciones Sal: {pref.get('Sal')}")
    print(f"{ok(pref.get('E7') == len(d.obligatorios))} restricciones E7: {pref.get('E7')} (obligatorios {len(d.obligatorios)})")
    print(f"     restricciones por tipo: {pref}")
    print(f"{ok(all(v.upBound == 0 for (i, j), v in m.x.items() if not d.quitable[(i, j)]))} las x no quitables tienen cotas 0..0")

    info = m.resolver(gap_rel=1e-4, time_limit=170)
    print("\nResolución:", info)
    plan_hogar, plan_nino, plan_adulto = m.solucion()
    rec = m.recalcular()
    pd_opts = {"display.width": 220, "display.max_columns": 30, "display.float_format": "{:,.4f}".format}
    import pandas as pd
    with pd.option_context(*[a for kv in pd_opts.items() for a in kv]):
        print(rec[["salen_personas", "salen_hogares", "H", "M0", "reduccion_M0", "severidad", "sevedu", "costo"]])

    # (a) la cuenta independiente coincide con el MILP
    salen_milp = float((plan_hogar.p * plan_hogar.sale).sum())
    print(f"\n{ok(abs(rec.at['total', 'salen_personas'] - salen_milp) < 1e-6)} personas que salen: recalculado {rec.at['total', 'salen_personas']:,.1f} = MILP {salen_milp:,.1f}")
    costo_milp = pulp.value(m.costo_total())
    print(f"{ok(abs(rec.at['total', 'costo'] - costo_milp) < 1)} costo: recalculado {rec.at['total', 'costo']:,.0f} = MILP {costo_milp:,.0f}")
    print(f"{ok(costo_milp <= m.B + 1)} costo <= B ({m.B:,.0f})")
    # (b) reglas educativas
    cubiertos = set(plan_nino.ID_PERSONA)
    print(f"{ok(all(k in cubiertos for k in d.obligatorios))} los {len(d.obligatorios)} obligatorios (E-7) tienen estrategia")
    print(f"{ok(plan_nino.ID_PERSONA.is_unique)} ningún niño tiene dos estrategias (E-2)")
    e1 = plan_nino[plan_nino.estrategia == 'E1'].ID_HOGAR.unique()
    print(f"{ok(all(_val(m.t[i]) for i in e1))} todo hogar con E1 paga Renta Ciudadana (E-3)")
    malos = []
    for i in d.hogares.index:
        for j in d.J[i]:
            if not _val(m.x[(i, j)]):
                continue
            if j == "inasistencia_escolar" and not all(k in cubiertos for k in d.N_i[i]):
                malos.append((i, j))
            if j == "logro_educativo" and sum(d.g_a[a] for a in d.L_i.get(i, []) if _val(m.v[a])) < d.D_i[i]:
                malos.append((i, j))
            if j == "analfabetismo" and not all(_val(m.v[a]) for a in d.analfabetas_i[i]):
                malos.append((i, j))
            if not d.quitable[(i, j)]:
                malos.append((i, j))
    print(f"{ok(not malos)} Inas / 11 / 12 / no quitables respetadas en la solución ({len(malos)} violaciones)")
    # (c) los que salen según el MILP salen también con la cuenta independiente
    h = plan_hogar.set_index("ID_HOGAR")
    print(f"{ok(int(h.sale.sum()) == rec.at['total', 'salen_hogares'])} hogares que salen: MILP {int(h.sale.sum())} = recalculado {rec.at['total', 'salen_hogares']}")


if __name__ == "__main__":
    main()
