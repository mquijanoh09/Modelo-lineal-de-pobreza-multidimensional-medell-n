# -*- coding: utf-8 -*-
"""Grafica de m34_sensibilidad_k: personas que salen (equidad) vs k, con M3 como referencia.
Uso: python3 m34_grafica_k.py <dir_sens_k> <salida.png>"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

d = Path(sys.argv[1])
df = pd.concat([pd.read_csv(p) for p in d.glob("t_*.csv")], ignore_index=True)
e = df[df.objetivo == "equidad"]
fig, ax = plt.subplots(figsize=(6.5, 4.2))
for B, col in [(10, "#9bbb59"), (25, "#4f81bd")]:
    s = e[(e.B == B) & (e.modelo != "m3")].copy()
    s["k"] = s.modelo.str.extract(r"k(\d+)").astype(int)
    g = s.groupby("k").personas_salen
    ks = sorted(s.k.unique())
    ax.plot(ks, g.median() / 1e3, "-o", color=col, label=f"M4, B = {B} mil mill.")
    ax.fill_between(ks, g.quantile(.05) / 1e3, g.quantile(.95) / 1e3, color=col, alpha=.15)
    m3 = e[(e.B == B) & (e.modelo == "m3")].personas_salen.median() / 1e3
    ax.axhline(m3, color=col, ls="--", lw=1)
    ax.text(ks[-1], m3, f" M3 ({B})", va="bottom", ha="right", color=col, fontsize=8)
ax.axvline(4, color="grey", ls=":", lw=1)
ax.set(xlabel="Número de clústeres k (información demográfica del Estado)",
       ylabel="Personas que salen de la pobreza (miles)", title="Modelo 4: sensibilidad a k (50 réplicas)")
ax.grid(alpha=.3); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(sys.argv[2], dpi=150)
