# -*- coding: utf-8 -*-
"""Tabla y grafica de m34_barrido_metas_v2: costo (u1, mil millones de $) y errores por meta.
Uso: python3 m34_resumen_barrido_v2.py <dir_barrido_v2> <salida.csv> <grafica.png>"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

d = Path(sys.argv[1])
df = pd.concat([pd.read_csv(p) for p in d.glob("*.csv")], ignore_index=True)
print("estados:", df.groupby(["modelo", "variante"]).estado.value_counts().to_dict())
print("replicas por modelo/variante:", df.groupby(["modelo", "variante"]).replica.nunique().to_dict())
u = df[(df.variante == "u1") & (df.estado == "Optimal")].copy()
u["costo_mm"] = u.objetivo / 1e3
u["frac_pares_chicos"] = u.costo_pares_n_lt10 / u.objetivo
agg = u.groupby(["meta", "modelo"]).agg(
    costo_med=("costo_mm", "median"), costo_p5=("costo_mm", lambda s: s.quantile(.05)),
    costo_p95=("costo_mm", lambda s: s.quantile(.95)), inclusion=("inclusion_pesos", "median"),
    exclusion=("exclusion", "median"), frac_pares_chicos=("frac_pares_chicos", "median"),
    n=("replica", "nunique")).reset_index()
p = u.pivot_table(index=["meta", "replica"], columns="modelo", values="costo_mm").dropna()
ahorro = (1 - p.m4 / p.m3).groupby("meta").median().rename("ahorro_m4_mediano")
gana = (p.m4 < p.m3).groupby("meta").mean().rename("m4_mas_barato")
tab = agg.pivot(index="meta", columns="modelo").round(3)
tab.columns = [f"{a}_{b}" for a, b in tab.columns]
tab = tab.join(ahorro.round(3)).join(gana.round(3))
tab.to_csv(sys.argv[2])
pd.set_option("display.width", 250)
print(tab[["costo_med_m3", "costo_med_m4", "ahorro_m4_mediano", "m4_mas_barato", "inclusion_m3", "inclusion_m4",
           "exclusion_m3", "exclusion_m4", "frac_pares_chicos_m3", "frac_pares_chicos_m4", "n_m3", "n_m4"]].to_string())
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
for mod, col, nom in [("m3", "#c0504d", "M3 (solo zona)"), ("m4", "#4f81bd", "M4 (zona + clúster)")]:
    a = agg[agg.modelo == mod]
    ax[0].plot(a.meta * 100, a.costo_med, "-o", color=col, label=nom, ms=3)
    ax[0].fill_between(a.meta * 100, a.costo_p5, a.costo_p95, color=col, alpha=.15)
    ax[1].plot(a.meta * 100, a.inclusion * 100, "-o", color=col, label=nom, ms=3)
ax[0].set(xlabel="Meta de reducción de M0 (%)", ylabel="Costo (mil millones de $ 2025, u = 1)",
          title="Costo de la meta: mediana y p5–p95")
ax[1].set(xlabel="Meta de reducción de M0 (%)", ylabel="Error de inclusión en pesos (%)",
          title="Fracción del gasto en hogares no pobres")
for a_ in ax:
    a_.grid(alpha=.3); a_.legend()
fig.tight_layout(); fig.savefig(sys.argv[3], dpi=150)
