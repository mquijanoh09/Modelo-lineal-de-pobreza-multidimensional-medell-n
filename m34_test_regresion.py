# -*- coding: utf-8 -*-
"""Regresion: el codigo autocontenido reproduce 06_modelo3_cortes.py (630 cortes, 153,0)."""
import sys

import numpy as np

import m34_datos as D
import m34_mecanismo as X

raiz = sys.argv[1]
hog = D.cargar(raiz)
b = D.verificar_linea_base(hog)
print(f"linea base OK: {len(hog)} hogares, {b['pobre0'].sum()} pobres, H0={b['H0']:.4f}, M0={b['M0']:.6f}")
M, HS, HW, w = D.matrices(hog)
R = D.sortear_R(hog, 0)
HSm = np.repeat(HS[:, None], 15, 1)
grupo = np.repeat(hog.CELDA.to_numpy()[:, None], 15, 1)
info = X.enumerar_cortes(M, R, HSm, HSm, grupo)
print("pares", len(info), "cortes", sum(len(v["F"]) for v in info.values()))
for solver in ["highs", "cbc"]:
    r = X.resolver_paper(M, w, b["pers"], b["pobre0"], b["M0"], info, 0.10, solver=solver)
    cub, N1 = X.reconstruir(info, r["corte"], M)
    mt = X.metricas(cub, N1, M, w, HS, HW, b["pobre0"], hog.CELDA.to_numpy())
    print(solver, r["estado"], r["obj"], f"{r['segundos']:.1f}s", {k: round(v, 4) for k, v in mt.items()})
