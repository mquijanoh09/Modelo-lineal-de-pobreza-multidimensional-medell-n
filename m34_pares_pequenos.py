# -*- coding: utf-8 -*-
"""
m34_pares_pequenos.py — Pares (j, g) con pocos hogares privados (pendiente #5, 3-nov-2026).

Problema: si un par (j, g) tiene 1-3 hogares privados en la muestra, p_jg salta a 0 o 1 de
golpe y el resultado depende de un solo R. Esto no es un error del modelo sino del tamaño de
muestra de la ECV; hay que (a) listarlos, (b) medir cuanto pesan y (c) declarar una regla.
Uso: python3 m34_pares_pequenos.py <raiz_DEPARTAMENTAL> <salida.csv>
"""
import sys

import numpy as np
import pandas as pd

import m34_clusters as CL
import m34_datos as D
from m34_montecarlo import matriz_grupo

raiz, salida = sys.argv[1], sys.argv[2]
hog = D.cargar(raiz)
b = D.verificar_linea_base(hog)
M, HS, HW, w = D.matrices(hog)
etq, _ = CL.clusters(hog, raiz)
filas = []
for mod, G in [("m3", matriz_grupo(hog, "m3")), ("m4", matriz_grupo(hog, "m4", etq))]:
    for jj, j in enumerate(D.IND):
        for g in sorted(np.unique(G[:, jj])):
            s = (G[:, jj] == g) & (M[:, jj] == 1)
            if not s.any():
                continue
            filas.append(dict(modelo=mod, indicador=j, grupo=g, n_hogares=int(s.sum()),
                              n_pobres=int((s & (b["pobre0"] == 1)).sum()),
                              personas_rep=float((HS * HW)[s].sum()),
                              personas_pobres_rep=float((HS * HW * b["pobre0"])[s].sum())))
df = pd.DataFrame(filas)
df.to_csv(salida, index=False)
for mod in ["m3", "m4"]:
    d = df[df.modelo == mod]
    print(f"\n{mod}: {len(d)} pares; con n < 5: {(d.n_hogares < 5).sum()}, n < 10: {(d.n_hogares < 10).sum()}, "
          f"n < 30: {(d.n_hogares < 30).sum()}")
    print(d[d.n_hogares < 10].sort_values("n_hogares").to_string(index=False))
