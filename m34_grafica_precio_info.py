# -*- coding: utf-8 -*-
"""
m34_grafica_precio_info.py — Figura central del paper: el precio de la información (escenario común, 10-nov).

Panel A: costo de cumplir la meta relativo a la información perfecta (M2), por meta de reducción de M0.
Panel B: personas que salen de la pobreza como % del techo del M1, por presupuesto B.
Mediana de las réplicas con IC 95 % bootstrap (sombreado). M3, M4 y el placebo de M4.
Dos paneles separados (no doble eje). Identidad por color + marcador + etiqueta directa.
Uso: python3 m34_grafica_precio_info.py <ic_bootstrap_costos.csv> <ic_bootstrap_equidad.csv> <salida.pdf>
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

SERIES = [("m3", "Modelo 3 (zona)", "#2a78d6", "o"),
          ("m4", "Modelo 4 (zona + tipo)", "#eb6834", "s"),
          ("m4p", "Placebo de M4", "#1baf7a", "^")]
TXT, TXT2, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def estilo(ax):
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color(TXT2)
    ax.tick_params(colors=TXT2, labelsize=8)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def main(costos, equidad, salida):
    c = pd.read_csv(costos).sort_values("meta")
    e = pd.read_csv(equidad).sort_values("B")
    plt.rcParams.update({"font.family": "serif", "font.size": 9})
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 3.1))

    x = 100 * c.meta
    a.axhline(1, color=TXT, lw=1, ls="--")
    a.text(x.iloc[-1], 1.06, "información perfecta (M2)", ha="right", va="bottom", fontsize=7.5, color=TXT)
    for m, nombre, col, mk in SERIES:
        y, lo, hi = c[f"{m}_mediana"] / c.IP_M2, c[f"{m}_ic_inf"] / c.IP_M2, c[f"{m}_ic_sup"] / c.IP_M2
        a.fill_between(x, lo, hi, color=col, alpha=0.15, lw=0)
        a.plot(x, y, color=col, lw=2, marker=mk, ms=4, label=nombre)
    a.set_yscale("log")
    a.set_yticks([1, 2, 5, 10, 20])
    a.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}×"))
    a.set_xlabel("meta de reducción de $M_0$ (%)", color=TXT2)
    a.set_ylabel("costo / costo con información perfecta", color=TXT2)
    a.set_title("A. Precio de la información (costo)", loc="left", fontsize=9, color=TXT)
    estilo(a)

    xb = e.B
    b.axhline(100, color=TXT, lw=1, ls="--")
    b.text(xb.iloc[-1], 101.5, "información perfecta (M1)", ha="right", va="bottom", fontsize=7.5, color=TXT)
    for m, nombre, col, mk in SERIES:
        y = e[f"{m}_pct_IP"]
        lo, hi = 100 * e[f"{m}_ic_inf"] / e.IP_M1, 100 * e[f"{m}_ic_sup"] / e.IP_M1
        b.fill_between(xb, lo, hi, color=col, alpha=0.15, lw=0)
        b.plot(xb, y, color=col, lw=2, marker=mk, ms=4, label=nombre)
    b.set_xscale("log")
    b.set_xticks(list(xb))
    b.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
    b.set_ylim(0, 110)
    b.set_xlabel("presupuesto $B$ (miles de millones de \\$ de 2025)", color=TXT2)
    b.set_ylabel("personas que salen (% del techo)", color=TXT2)
    b.set_title("B. Personas que salen de la pobreza", loc="left", fontsize=9, color=TXT)
    estilo(b)

    h, l = a.get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, frameon=False, fontsize=8, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(salida, bbox_inches="tight")
    fig.savefig(salida.replace(".pdf", ".png"), dpi=200, bbox_inches="tight")


if __name__ == "__main__":
    main(*sys.argv[1:4])
