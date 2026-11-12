# -*- coding: utf-8 -*-
"""Tamaño del MILP por cortes y datos del Modelo 4 en el escenario final (datos-finales-10nov). Solo lee datos."""
import sys
import numpy as np
import pandas as pd
import m34_barrido_metas_v2 as BV
import m34_corridas_costos_reales as CC
import m34_datos as D
import m34_mecanismo as X
from m34_montecarlo import matriz_grupo
import m34_clusters as CL

raiz = "data/DANE/DEPARTAMENTAL"
CC.FUENTE = "comun"
CC._preparar_barrido(raiz)
g = BV.G_
V, Kc = g["var"]["comun"]
etq, _ = CL.clusters(g["hog"], raiz)
G4 = matriz_grupo(g["hog"], "m4", etq)
filas = []
for rep in range(100):
    R = D.sortear_R(g["hog"], rep)
    for mod, G in [("m3", g["G"]["m3"]), ("m4", G4)]:
        info = X.enumerar_cortes(g["M"], R, V, Kc, G, excluir=(D.IND.index("rezago_escolar"),),
                                 pobre0=g["b"]["pobre0"], fijos=g.get("fijos"))
        filas.append(dict(modelo=mod, replica=rep, pares=len(info), cortes=sum(len(v["F"]) if "F" in v else len(v["cortes"]) for v in info.values())))
t = pd.DataFrame(filas)
t["binarias"] = t.cortes + int(g["b"]["pobre0"].sum())
print(t.groupby("modelo")[["pares", "cortes", "binarias"]].agg(["min", "median", "max"]))
b = pd.read_csv("resultados/m34/barrido_comun_crudo_10nov.csv")
print("segundos por MILP (incluye desempate):", b.groupby("modelo").segundos.describe(percentiles=[.5, .95]).round(2))
# Modelo 4: tipos de hogar y discriminacion
hog = g["hog"]; pers = g["b"]["pers"]; pobre = g["b"]["pobre0"]
for k in range(4):
    s = etq == k
    print("tipo", k, "hogares", s.sum(), "H", round(100 * (pers[s] * pobre[s]).sum() / pers[s].sum(), 1))
M = g["M"]
for j in ["acueducto", "alcantarillado", "inasistencia_escolar", "aseguramiento_salud", "barreras_acceso_salud"]:
    jj = D.IND.index(j)
    def razon(lbl):
        tasas = [(pers[lbl == v] * M[lbl == v, jj]).sum() / pers[lbl == v].sum() for v in np.unique(lbl)]
        tasas = [x for x in tasas]
        return round(max(tasas) / min(tasas), 1) if min(tasas) > 0 else float("inf")
    print(j, "zona", razon(g["zona"]), "tipo", razon(etq))

# --- Verificación de las cifras que cita el paper (secciones 3.4, 3.5 y Tabla de discriminación) ---
def razon(lbl, j):
    jj = D.IND.index(j)
    tasas = [(pers[lbl == v] * M[lbl == v, jj]).sum() / pers[lbl == v].sum() for v in np.unique(lbl)]
    return round(max(tasas) / min(tasas), 1) if min(tasas) > 0 else None

esperado = {"acueducto": (14.5, 4.1), "alcantarillado": (4.7, 3.2), "inasistencia_escolar": (4.8, 51.7),
            "hacinamiento": (2.7, 26.6), "aseguramiento_salud": (1.9, 1.9), "barreras_acceso_salud": (2.7, 1.8),
            "atencion_integral": (2.2, None)}
ok = []
for j, (z, t_) in esperado.items():
    ok.append(razon(g["zona"], j) == z and razon(etq, j) == t_)
    print("OK   " if ok[-1] else "FALLA", j, razon(g["zona"], j), razon(etq, j))
q3, q4 = t[t.modelo == "m3"], t[t.modelo == "m4"]
for nombre, cond in [("M3: 42 pares, cortes 318-542, binarias 841-1065",
                      (q3.pares == 42).all() and q3.cortes.min() == 318 and q3.cortes.max() == 542 and q3.binarias.min() == 841 and q3.binarias.max() == 1065),
                     ("M4: 53 pares, cortes 324-524", (q4.pares == 53).all() and q4.cortes.min() == 324 and q4.cortes.max() == 524),
                     ("M3: mediana 1 s, máximo 22 s", round(b[b.modelo == "m3"].segundos.median()) == 1 and round(b[b.modelo == "m3"].segundos.max()) == 22),
                     ("tipos de hogar 1389/1038/849/456 con H 3,7/11,8/9,1/16,1",
                      [int((etq == k).sum()) for k in range(4)] == [1389, 1038, 849, 456]
                      and [round(100 * (pers[etq == k] * pobre[etq == k]).sum() / pers[etq == k].sum(), 1) for k in range(4)] == [3.7, 11.8, 9.1, 16.1])]:
    ok.append(cond)
    print("OK   " if cond else "FALLA", nombre)
print(f"\n{sum(ok)}/{len(ok)} cifras verificadas")
