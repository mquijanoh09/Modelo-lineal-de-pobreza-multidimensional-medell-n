# -*- coding: utf-8 -*-
"""
m34_referencia_info_perfecta.py — Techo de referencia con INFORMACION PERFECTA (3-nov-2026).

NO reemplaza el Modelo 1 de Martin: es el mismo objetivo de m34_equidad (etapa 1 y 2,
mismo B, mismos costos u = 1, rezago no intervenible) pero el Estado elige hogar por hogar
(x_ij solo en pobres -> error de inclusion = 0, sin sorteo). Sirve para medir el
"precio de no tener informacion": personas que salen en M3/M4 divididas por las de aqui.
Cuando exista el M1 oficial con los mismos supuestos, se reemplaza por ese.

Uso: python3 m34_referencia_info_perfecta.py <raiz> <salida.csv> B1 B2 ...
"""
import sys

import numpy as np
import pandas as pd
import pulp

import m34_datos as D
import m34_equidad as E
from m34_datos import K_GRID
from m34_montecarlo import precios_u1


def resolver(dat, Kp, B, rho, intervenible):
    M, w, p, s0, pobres = dat["M"], dat["w"], dat["p"], dat["s0"], dat["pobres"]
    sol = None
    for etapa in [1, 2]:
        m = pulp.LpProblem("IP", pulp.LpMaximize if etapa == 1 else pulp.LpMinimize)
        x = {(i, j): pulp.LpVariable(f"x_{i}_{j}", cat="Binary")
             for i in pobres for j in range(M.shape[1]) if M[i, j] == 1 and intervenible[j]}
        y = {i: pulp.LpVariable(f"y_{i}", cat="Binary") for i in pobres}
        q = {i: pulp.LpVariable(f"q_{i}", lowBound=0) for i in pobres}
        m += pulp.lpSum(Kp[i, j] * v for (i, j), v in x.items()) <= B
        for i in pobres:
            s = float(s0[i]) - pulp.lpSum(w[j] * x[(i, j)] for j in range(M.shape[1]) if (i, j) in x)
            m += s <= K_GRID + (s0[i] - K_GRID) * (1 - y[i])
            if rho > 0 or etapa == 2:
                for a in dat["A"][i]:
                    if a > 0:
                        m += q[i] >= 2 * a * s - a * a
        sev = pulp.lpSum(p[i] * q[i] for i in pobres)
        if rho > 0:
            m += sev <= (1 - rho) * dat["Sev0"]
        salen = pulp.lpSum(p[i] * y[i] for i in pobres)
        if etapa == 1:
            m += salen
        else:
            m += salen >= H * (1 - 1e-7)
            m += sev
        m.solve(pulp.HiGHS(msg=False, gapRel=1e-6 if etapa == 1 else 1e-4, timeLimit=180))
        est = pulp.LpStatus[m.status]
        if est != "Optimal":
            return dict(estado=est)
        if etapa == 1:
            H = pulp.value(m.objective)
    N1 = M.copy()
    for (i, j), v in x.items():
        if round(v.value()) == 1:
            N1[i, j] = 0
    return dict(estado=est, personas_salen=H, sev_reduccion=E.severidad(N1, dat),
                gasto=sum(Kp[i, j] for (i, j), v in x.items() if round(v.value()) == 1))


def main():
    raiz, salida = sys.argv[1], sys.argv[2]
    Bs = [float(b) for b in sys.argv[3:]]
    hog = D.cargar(raiz)
    D.verificar_linea_base(hog)
    M, HS, HW, w = D.matrices(hog)
    dat = E.preparar(M, w, HS, HW, hog.CELDA.to_numpy())
    Kp = precios_u1(hog)
    intervenible = np.array([j != "rezago_escolar" for j in D.IND])
    filas = []
    for B in Bs:
        for rho in [0.0, 0.10]:
            r = resolver(dat, Kp, B * 1e3, rho, intervenible)
            filas.append(dict(modelo="info_perfecta", B=B, rho=rho, **r))
            print(filas[-1], flush=True)
    pd.DataFrame(filas).to_csv(salida, index=False)


if __name__ == "__main__":
    main()
