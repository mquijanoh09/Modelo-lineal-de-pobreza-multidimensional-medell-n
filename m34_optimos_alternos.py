# -*- coding: utf-8 -*-
"""
m34_optimos_alternos.py — ¿El error de inclusion esta determinado por el optimo?

Con esfuerzo en personas-privacion (valores enteros pequeños) hay MUCHOS cortes con el
mismo costo total: el MILP tiene optimos alternos y cada solver devuelve uno distinto.
Prueba: fijar el esfuerzo en su optimo E* y resolver en segunda etapa
    min / max  sum_{(j,g)} sum_c cumNP(c) z[j,g,c]      (esfuerzo en hogares NO pobres)
Si min != max, el error de inclusion reportado depende del solver y hay que fijar una
regla de desempate (recomendada: la mas favorable para el Estado = min inclusion,
o reportar el intervalo).

Uso: python3 m34_optimos_alternos.py <raiz> <m3|m4> <n_replicas>
"""
import sys

import numpy as np
import pandas as pd
import pulp

import m34_datos as D
import m34_mecanismo as X
from m34_datos import K_GRID
from m34_montecarlo import matriz_grupo


def modelo(M, w, pers, pobre0, M0, info, meta, HS):
    pobres = np.where(pobre0 == 1)[0]
    m = pulp.LpProblem("alt", pulp.LpMinimize)
    z = {(jj, g, c): pulp.LpVariable(f"z_{jj}_{str(g).replace(' ', '')}_{c}", cat="Binary")
         for (jj, g), v in info.items() for c in v["F"]}
    for (jj, g), v in info.items():
        m += pulp.lpSum(z[(jj, g, c)] for c in v["F"]) == 1
    cur = {}
    for (jj, g), v in info.items():
        for k, i in enumerate(v["orden"], start=1):
            if pobre0[i]:
                cur[(i, jj)] = pulp.lpSum(z[(jj, g, c)] for c in v["F"] if c >= k)
    b1 = {i: pulp.LpVariable(f"b1_{i}", cat="Binary") for i in pobres}
    C = {i: pulp.LpVariable(f"C_{i}", lowBound=0) for i in pobres}
    for i in pobres:
        s = pulp.lpSum(w[jj] * (1 - cur[(i, jj)]) for jj in range(M.shape[1]) if (i, jj) in cur)
        m += C[i] + pers[i] * b1[i] >= pers[i] * s
        m += C[i] - pers[i] * b1[i] <= pers[i] * s
        m += s - (1 - b1[i]) <= K_GRID
    m += pulp.lpSum(C.values()) <= M0 * (1 - meta) * pers.sum()
    costo = pulp.lpSum(v["cumK"][c] * z[(jj, g, c)] for (jj, g), v in info.items() for c in v["F"])
    np_ = {}
    for (jj, g), v in info.items():
        x = HS[v["orden"]] * (1 - pobre0[v["orden"]])
        cum = np.concatenate([[0.0], np.cumsum(x)])
        np_[(jj, g)] = cum
    incl = pulp.lpSum(np_[(jj, g)][c] * z[(jj, g, c)] for (jj, g), v in info.items() for c in v["F"])
    return m, costo, incl


def main():
    raiz, mod, nrep = sys.argv[1], sys.argv[2], int(sys.argv[3])
    hog = D.cargar(raiz)
    b = D.verificar_linea_base(hog)
    M, HS, HW, w = D.matrices(hog)
    etq = None
    if mod == "m4":
        import m34_clusters as K
        etq, _ = K.clusters(hog, raiz)
    G = matriz_grupo(hog, mod, etq)
    HSm = np.repeat(HS[:, None], 15, 1)
    filas = []
    for rep in range(nrep):
        R = D.sortear_R(hog, rep)
        info = X.enumerar_cortes(M, R, HSm, HSm, G)
        for meta in [0.05, 0.10, 0.20]:
            m, costo, incl = modelo(M, w, b["pers"], b["pobre0"], b["M0"], info, meta, HS)
            m.setObjective(costo)
            m.solve(pulp.HiGHS(msg=False, gapRel=1e-9))
            E = pulp.value(costo)
            m += costo <= E + 1e-6
            res = {}
            for sentido in ["min", "max"]:
                m.sense = pulp.LpMinimize if sentido == "min" else pulp.LpMaximize
                m.setObjective(incl)
                m.solve(pulp.HiGHS(msg=False, gapRel=1e-9))
                res[sentido] = pulp.value(incl) / E
            filas.append(dict(modelo=mod, replica=rep, meta=meta, esfuerzo=E,
                              inclusion_min=res["min"], inclusion_max=res["max"]))
            print(filas[-1], flush=True)
    pd.DataFrame(filas).to_csv(f"out/optimos_alternos_{mod}.csv", index=False)


if __name__ == "__main__":
    main()
