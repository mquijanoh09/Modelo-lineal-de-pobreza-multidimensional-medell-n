# -*- coding: utf-8 -*-
"""Resumen de la distribucion del Monte Carlo (M3 vs M4) y graficas."""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

d = pd.concat([pd.read_csv(f) for f in sys.argv[1:]], ignore_index=True)
print("estados:", d.groupby(["modelo", "variante", "estado"]).size().to_dict())
d = d[d.estado == "Optimal"]
cols = ["objetivo", "costo_pesos", "inclusion_personas", "inclusion_pesos", "exclusion",
        "H1", "M01", "privaciones_resueltas", "hogares_que_salen", "pares_activos", "segundos"]


def q(s):
    return f"{s.median():.4g} [{s.quantile(.05):.4g}; {s.quantile(.95):.4g}]"


filas = []
for (m, v, meta), g in d.groupby(["modelo", "variante", "meta"]):
    f = dict(modelo=m, variante=v, meta=meta, n=len(g))
    for c in cols:
        f[c] = q(g[c])
    f["cv_objetivo"] = f"{g.objetivo.std() / g.objetivo.mean():.1%}"
    filas.append(f)
tab = pd.DataFrame(filas)
tab.to_csv("out/resumen_mc.csv", index=False)
pd.set_option("display.width", 250)
print(tab.to_string(index=False))

# Frecuencia con que cada (indicador, grupo) recibe esfuerzo, meta 10 %, variante pp
for m in d.modelo.unique():
    g = d[(d.modelo == m) & (d.meta == 0.10) & (d.variante == "pp")]
    pares = g.cortes.fillna("").str.split(";").explode()
    pares = pares[pares != ""].str.rsplit("|", n=1).str[0]
    print(f"\n{m}: pares (indicador|grupo) intervenidos con meta 10 % (% de replicas)")
    print((pares.value_counts() / len(g) * 100).round(0).head(12).to_string())

fig, ax = plt.subplots(2, 2, figsize=(11, 8))
for k, (var, met, tit) in enumerate([("pp", "objetivo", "Esfuerzo (personas-privación)"),
                                     ("u1", "costo_pesos", "Costo u=1 (millones de pesos)"),
                                     ("pp", "inclusion_personas", "Error de inclusión (pp)"),
                                     ("pp", "exclusion", "Error de exclusión (pp)")]):
    a = ax.flat[k]
    datos, etq = [], []
    for meta in [0.05, 0.10, 0.20]:
        for m in ["m3", "m4"]:
            datos.append(d[(d.modelo == m) & (d.variante == var) & (d.meta == meta)][met].values)
            etq.append(f"{m.upper()}\n{int(meta*100)}%")
    bp = a.boxplot(datos, tick_labels=etq, patch_artist=True)
    for i, p in enumerate(bp["boxes"]):
        p.set_facecolor("#4C78A8" if i % 2 == 0 else "#F58518")
    a.set_title(tit, fontsize=10)
    a.grid(alpha=.3)
fig.suptitle("Monte Carlo, 100 réplicas del sorteo R — Modelo 3 (azul) vs Modelo 4 (naranja)")
fig.tight_layout()
fig.savefig("out/mc_m3_vs_m4.png", dpi=130)
print("\ngrafica: out/mc_m3_vs_m4.png")
