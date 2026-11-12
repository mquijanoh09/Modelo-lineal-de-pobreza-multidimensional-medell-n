# -*- coding: utf-8 -*-
"""
m34_rmax_12nov.py — Diagnóstico de la infactibilidad del piso por zona (12-nov).

Con el r_B del M1 (especificación de Martín, §4.1) M3, M4 y placebo son infactibles en TODAS las réplicas y
presupuestos. Para medir cuánta equidad territorial puede garantizar el Estado sin información individual, se
resuelve por réplica y B:
    max t   s.a.   sum_{i in I0, d(i)=d} p_i b1_i >= t * Pobres_d^0   para cada zona d,
                   presupuesto B, mecanismo de cortes y condición de salida (los de m34_equidad).
t* es el mayor piso r factible; se compara con r_B. Con información perfecta (un hogar por celda) t* >= r_B.
Uso: python3 m34_rmax_12nov.py <raiz> <n_rep> <r_rho.csv> <salida.csv>
"""
import sys
import time

import numpy as np
import pandas as pd
import pulp

import m34_corridas_costos_reales as CC
import m34_datos as D
import m34_equidad as E
import m34_mecanismo as X
from m34_montecarlo import matriz_grupo
from m34_placebo import etiquetas_placebo


def r_max(info, dat, B, tiempo=180):
    for opciones in [{}, {"presolve": "off"}]:
        m, z = E.construir(info, dat, B * 1e3, r=0.0, rho=0.0, etapa=1)
        v = m.variablesDict()
        t = pulp.LpVariable("t_piso", lowBound=0, upBound=1)
        for d in dat["zonas"]:
            m += (pulp.lpSum(dat["p"][i] * v[f"y_{i}"] for i in dat["pobres"] if dat["zona"][i] == d)
                  >= t * dat["Pobres_d"][d]), f"PISO_{str(d).replace(' ', '_')}"
        m.setObjective(t)
        m.sense = pulp.LpMaximize
        m.solve(pulp.HiGHS(msg=False, timeLimit=tiempo, gapRel=1e-6, **opciones))
        est, _, gap = X.estado_real(m, pulp.LpStatus[m.status])
        if est == "Optimal":
            return float(t.value()), gap
    return np.nan, np.nan


def main(raiz, nrep, tabla, salida):
    rr = pd.read_csv(tabla).set_index("B")
    CC.FUENTE = "comun"
    CC._preparar_equidad(raiz, list(rr.index))
    g = CC.EQ
    import m34_clusters as CL
    etq, _ = CL.clusters(g["hog"], raiz)
    filas = []
    for rep in range(nrep):
        R = D.sortear_R(g["hog"], rep)
        for mod in ["m3", "m4", "m4p"]:
            G = g["G"][mod] if mod != "m4p" else matriz_grupo(g["hog"], "m4", etiquetas_placebo(etq, rep))
            info = X.enumerar_cortes(g["M"], R, g["V"], g["K"], G, excluir=(D.IND.index("rezago_escolar"),),
                                     pobre0=g["dat"]["pobre0"], fijos=g["fijos"])
            for B in rr.index:
                t0 = time.time()
                t, gap = r_max(info, g["dat"], B)
                filas.append(dict(modelo=mod, replica=rep, B=B, r_max=t, r_B=rr.loc[B, "r_B"], gap=gap,
                                  segundos=round(time.time() - t0, 2)))
        pd.DataFrame(filas).to_csv(salida, index=False)
        print(time.strftime("%H:%M:%S"), "réplica", rep, flush=True)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4])
