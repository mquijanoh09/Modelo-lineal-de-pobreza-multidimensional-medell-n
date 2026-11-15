# -*- coding: utf-8 -*-
"""
m34_ip_zonas_15nov.py — Referencia de información perfecta del criterio de costo, por zona (PLAN_INTEGRACION_M3_M4.md
de Martín, §5, punto 4): Modelo 2 de Martín sin E-7 ni SevEdu, con la meta de M0 en cada zona, 15 metas.
Guarda costo, H, A y M0 finales del total y de cada zona, con la función recalcular() de Martín (sin cambiarla).
Es el mismo escenario de info_perfecta_meta_zona_12nov.csv; el costo total debe coincidir.

Uso: python3 m34_ip_zonas_15nov.py <Modelos/ de main> <salida.csv>
"""
import sys
import time

import pandas as pd

import m34_compat_martin as CM

METAS = [round(0.02 * k, 2) for k in range(1, 16)]


def main(dm, salida):
    P, _, _, _, Modelo2 = CM.cargar(dm)
    d = CM.datos_comun(dm)
    esc = P.escenario_m2("sin_E7", "base")
    assert esc["meta_por_zona"] is True and esc["usar_sevedu"] is False and esc["cobertura_art67"] is False
    filas = []
    for m in METAS:
        t0 = time.time()
        mod = Modelo2(d, esc, meta_m=m).construir()
        inf = mod.resolver(gap_rel=1e-6, time_limit=600)
        assert inf["estado"] == "Optimal", (m, inf)
        tab = mod.recalcular()
        for zona, f in tab.iterrows():
            filas.append(dict(meta=m, zona=zona, estado=inf["estado"], gap=inf["gap"], costo_mm=f.costo / 1e9,
                              H0=f.H0, H=f.H, A0=f.A0, A=f.A, M0_inicial=f.M0_inicial, M0=f.M0,
                              reduccion_M0=f.reduccion_M0, salen_personas=f.salen_personas))
        print(m, round(time.time() - t0, 1), "s", flush=True)
        pd.DataFrame(filas).to_csv(salida, index=False)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
