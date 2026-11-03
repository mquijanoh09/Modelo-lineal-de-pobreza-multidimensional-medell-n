# -*- coding: utf-8 -*-
"""Grafica M3 vs M4 vs informacion perfecta (objetivo de equidad, rho = 0, costos u = 1)."""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

eq, ip, salida = pd.read_csv(sys.argv[1]), pd.read_csv(sys.argv[2]), sys.argv[3]
eq = eq[(eq.rho == 0) & (eq.estado == "Optimal")]
ip = ip[ip.rho == 0]
COL = {"info_perfecta": "#2a78d6", "m4": "#eb6834", "m3": "#1baf7a"}
NOM = {"info_perfecta": "Información perfecta (referencia)", "m4": "M4 zona + clúster", "m3": "M3 solo zona"}
plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#52514e", "axes.labelcolor": "#0b0b0b",
                     "xtick.color": "#52514e", "ytick.color": "#52514e"})
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2), facecolor="#fcfcfb")
for a in ax:
    a.set_facecolor("#fcfcfb"); a.grid(axis="y", color="#e6e5e1", lw=0.8); a.set_axisbelow(True)
    for s in ["top", "right"]:
        a.spines[s].set_visible(False)
ax[0].plot(ip.B, ip.personas_salen / 1e3, color=COL["info_perfecta"], lw=2, marker="o", ms=5)
ax[0].annotate(NOM["info_perfecta"], (ip.B.iloc[-1], ip.personas_salen.iloc[-1] / 1e3), xytext=(-10, -2), va="top",
               textcoords="offset points", ha="right", color="#0b0b0b")
for mod in ["m4", "m3"]:
    g = eq[eq.modelo == mod].groupby("B")
    med, lo, hi = g.personas_salen.median() / 1e3, g.personas_salen.quantile(.05) / 1e3, g.personas_salen.quantile(.95) / 1e3
    ax[0].fill_between(med.index, lo, hi, color=COL[mod], alpha=.18, lw=0)
    ax[0].plot(med.index, med, color=COL[mod], lw=2, marker="o", ms=5, label=NOM[mod])
    gi = g.inclusion_pesos
    ax[1].fill_between(med.index, gi.quantile(.05) * 100, gi.quantile(.95) * 100, color=COL[mod], alpha=.18, lw=0)
    ax[1].plot(med.index, gi.median() * 100, color=COL[mod], lw=2, marker="o", ms=5, label=NOM[mod])
ax[0].set_xscale("log"); ax[1].set_xscale("log")
for a in ax:
    a.set_xticks([10, 25, 50, 100, 200]); a.set_xticklabels(["10", "25", "50", "100", "200"])
    a.set_xlabel("Presupuesto B (mil millones de $ 2025, u = 1)")
ax[0].set_ylabel("Personas que salen de la pobreza (miles)")
ax[0].set_title("Personas que salen: mediana y p5–p95 de 30 réplicas", loc="left", fontsize=10.5)
ax[1].set_ylabel("Error de inclusión (% del gasto en no pobres)")
ax[1].set_title("Error de inclusión (información perfecta = 0 %)", loc="left", fontsize=10.5)
ax[1].set_ylim(0, 100)
ax[0].legend(frameon=False, loc="lower right"); ax[1].legend(frameon=False, loc="upper right")
fig.tight_layout(); fig.savefig(salida, dpi=150, facecolor=fig.get_facecolor())
