# -*- coding: utf-8 -*-
"""
m34_grafica_12nov.py — Figura central con las restricciones de equidad de Martín tal cual (12-nov).
Panel A: costo de cumplir la meta de M0 EN CADA ZONA relativo al M2 con la misma meta (log).
Panel B: piso por zona máximo garantizable (r_max) de M3, M4 y placebo como % del de la información perfecta,
con el r_B del M1 como referencia.
Uso: python3 m34_grafica_12nov.py <ic_costo_meta_zona_12nov.csv> <ic_rmax_12nov.csv> <salida.pdf>
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from m34_grafica_precio_info import SERIES, TXT, TXT2, estilo


def main(costos, rmax, salida):
    c = pd.read_csv(costos).sort_values("meta")
    e = pd.read_csv(rmax).sort_values("B")
    plt.rcParams.update({"font.family": "serif", "font.size": 9})
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 3.1))
    x = 100 * c.meta
    a.axhline(1, color=TXT, lw=1, ls="--")
    a.text(x.iloc[-1], 1.06, "información perfecta (M2)", ha="right", va="bottom", fontsize=7.5, color=TXT)
    for m, nombre, col, mk in SERIES:
        a.fill_between(x, c[f"{m}_ic_inf"] / c.IP, c[f"{m}_ic_sup"] / c.IP, color=col, alpha=0.15, lw=0)
        a.plot(x, c[m] / c.IP, color=col, lw=2, marker=mk, ms=4, label=nombre)
    a.set_yscale("log"); a.set_yticks([1, 2, 5, 10, 20])
    a.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}×"))
    a.set_xlabel("meta de reducción de $M_0$ en cada zona (%)", color=TXT2)
    a.set_ylabel("costo / costo con información perfecta", color=TXT2)
    a.set_title("A. Precio de la información (costo)", loc="left", fontsize=9, color=TXT)
    estilo(a)
    xb = e.B
    b.axhline(100, color=TXT, lw=1, ls="--")
    b.text(xb.iloc[-1], 101.5, "información perfecta", ha="right", va="bottom", fontsize=7.5, color=TXT)
    b.plot(xb, 100 * e.r_B / e.IP_max, color=TXT2, lw=1, ls=":", marker="x", ms=4, label="$r_B$ del Modelo 1")
    for m, nombre, col, mk in SERIES:
        b.fill_between(xb, 100 * e[f"{m}_ic_inf"] / e.IP_max, 100 * e[f"{m}_ic_sup"] / e.IP_max, color=col, alpha=0.15, lw=0)
        b.plot(xb, 100 * e[m] / e.IP_max, color=col, lw=2, marker=mk, ms=4)
    b.set_xscale("log"); b.set_xticks(list(xb))
    b.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
    b.set_ylim(0, 110)
    b.set_xlabel("presupuesto $B$ (miles de millones de \\$ de 2025)", color=TXT2)
    b.set_ylabel("piso por zona garantizable (% del de la IP)", color=TXT2)
    b.set_title("B. Equidad territorial garantizable", loc="left", fontsize=9, color=TXT)
    estilo(b)
    h, l = a.get_legend_handles_labels(); h2, l2 = b.get_legend_handles_labels()
    fig.legend(h + h2, l + l2, loc="lower center", ncol=4, frameon=False, fontsize=8, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(salida, bbox_inches="tight")
    fig.savefig(salida.replace(".pdf", ".png"), dpi=200, bbox_inches="tight")


if __name__ == "__main__":
    main(*sys.argv[1:4])
