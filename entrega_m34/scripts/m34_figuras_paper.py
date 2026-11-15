# -*- coding: utf-8 -*-
"""
m34_figuras_paper.py — Figuras de M34_para_paper.md, en PNG a 300 dpi, desde los CSV de datos_m34/.

  Figura M34-1  costo contra meta (meta de M0 en cada zona): Modelo 2, Modelo 3, Modelo 4 y placebo
  Figura M34-2  piso por zona máximo garantizable (r_max) contra el presupuesto, con el r_B del Modelo 1
  Figura M34-3  incidencia H final por zona contra la meta (Modelo 2, Modelo 3, Modelo 4 y placebo)

Colores: Modelo 1 azul #2a78d6 y Modelo 2 naranja #eb6834, como en la Figura 9 del borrador de Martín. Modelo 3,
Modelo 4 y placebo usan las ranuras 3 a 5 de la misma paleta categórica (aqua, amarillo, magenta), validada con
validate_palette.js: pasa la separación para daltonismo. Su contraste con el fondo es bajo, así que cada serie
lleva además marcador propio y etiqueta directa al final de la línea.

Uso: python3 m34_figuras_paper.py <datos_m34/> <figuras_m34/>
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

COL = {"Modelo 1": "#2a78d6", "Modelo 2": "#eb6834", "Modelo 3": "#1baf7a", "Modelo 4": "#eda100",
       "Placebo": "#e87ba4"}
MARK = {"Modelo 1": "s", "Modelo 2": "o", "Modelo 3": "^", "Modelo 4": "D", "Placebo": "v"}
TINTA, TINTA2, REJILLA = "#1f1f1e", "#5d5c57", "#e4e3de"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": TINTA2, "axes.labelcolor": TINTA, "xtick.color": TINTA2,
                     "ytick.color": TINTA2, "axes.spines.top": False, "axes.spines.right": False,
                     "font.family": "DejaVu Sans"})


def miles(x, _):
    return f"{x:,.0f}" if x >= 1 else f"{x:.1f}"


def pct(x, _):
    return f"{x:.0f} %"


def _etiqueta(ax, x, y, texto, color_serie, dy=0):
    ax.annotate(texto, (x, y), xytext=(6, dy), textcoords="offset points", va="center", fontsize=8.5, color=TINTA)
    ax.plot([], [])  # la identidad la da el marcador del mismo color al final de la línea


def _rejilla(ax):
    ax.grid(axis="y", color=REJILLA, linewidth=0.8)
    ax.set_axisbelow(True)


def figura_costo(D, F):
    t = pd.read_csv(D / "costo_meta_zona.csv")
    x = 100 * t.meta
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    series = [("Modelo 2", t.costo_M2_mm, None, None), ("Modelo 3", t.costo_m3_mediana_mm, t.costo_m3_ic95_inf,
              t.costo_m3_ic95_sup), ("Modelo 4", t.costo_m4_mediana_mm, t.costo_m4_ic95_inf, t.costo_m4_ic95_sup),
              ("Placebo", t.costo_m4p_mediana_mm, t.costo_m4p_ic95_inf, t.costo_m4p_ic95_sup)]
    dy = {"Modelo 2": 0, "Modelo 3": -6, "Modelo 4": 3, "Placebo": 5}
    for nombre, y, lo, hi in series:
        if lo is not None:
            ax.fill_between(x, lo, hi, color=COL[nombre], alpha=0.18, linewidth=0)
        ax.plot(x, y, color=COL[nombre], linewidth=2, marker=MARK[nombre], markersize=5,
                markeredgecolor="white", markeredgewidth=1, label=nombre)
        _etiqueta(ax, x.iloc[-1], y.iloc[-1], nombre if nombre != "Modelo 2" else "Modelo 2 (referencia)",
                  COL[nombre], dy[nombre])
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(FuncFormatter(miles))
    ax.set_xlabel("Meta de reducción de M0 en cada zona (m)")
    ax.set_ylabel("Costo (mil millones de pesos de 2025, escala log.)")
    ax.xaxis.set_major_formatter(FuncFormatter(pct))
    ax.set_xticks(range(2, 31, 4))
    ax.set_xlim(1, 38)
    _rejilla(ax)
    ax.legend(frameon=False, loc="upper left", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(F / "figura_M34-1_costo_contra_meta.png", dpi=300)
    plt.close(fig)


def figura_rmax(D, F):
    t = pd.read_csv(D / "rmax_piso_garantizable.csv")
    x = range(len(t))
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    ax.plot(x, 100 * t.r_B, color=COL["Modelo 1"], linewidth=0, marker="_", markersize=22, markeredgewidth=2.5,
            label="r_B exigido por el Modelo 1 (marca horizontal)")
    ax.plot(x, 100 * t.IP_max, color=COL["Modelo 1"], linewidth=2, marker=MARK["Modelo 1"], markersize=5,
            markeredgecolor="white", label="Información perfecta")
    for nombre, k in [("Modelo 3", "m3"), ("Modelo 4", "m4"), ("Placebo", "m4p")]:
        ax.fill_between(x, 100 * t[f"{k}_ic_inf"], 100 * t[f"{k}_ic_sup"], color=COL[nombre], alpha=0.18, lw=0)
        ax.plot(x, 100 * t[k], color=COL[nombre], linewidth=2, marker=MARK[nombre], markersize=5,
                markeredgecolor="white", markeredgewidth=1, label=nombre)
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"{b:,}" for b in t.B])
    ax.set_xlabel("Presupuesto B (mil millones de pesos de 2025)")
    ax.set_ylabel("Piso por zona garantizable (% de los pobres de cada zona)")
    ax.yaxis.set_major_formatter(FuncFormatter(pct))
    _rejilla(ax)
    ax.legend(frameon=False, loc="upper left", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(F / "figura_M34-2_piso_garantizable.png", dpi=300)
    plt.close(fig)


def figura_H_zonas(D, F):
    f = D / "H_A_M0_por_zona.csv"
    if not f.exists():
        print("AVISO: falta H_A_M0_por_zona.csv; no se genera la Figura M34-3")
        return
    t = pd.read_csv(f)
    zonas = ["Cabeceras", "Centros poblados", "Rural disperso"]
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 3.3), sharey=False)
    for ax, z in zip(axs, zonas):
        for nombre in ["Modelo 2", "Modelo 3", "Modelo 4", "Placebo"]:
            g = t[(t.zona == z) & (t.modelo == nombre)].sort_values("meta")
            ax.plot(100 * g.meta, 100 * g.H, color=COL[nombre], linewidth=2, marker=MARK[nombre], markersize=3.5,
                    markeredgecolor="white", markeredgewidth=0.6, label=nombre)
        h0 = t[t.zona == z].H0.iloc[0]
        ax.axhline(100 * h0, color=TINTA2, linewidth=0.8, linestyle=":")
        ax.set_title(z, fontsize=9, color=TINTA)
        ax.set_xticks([2, 10, 20, 30])
        ax.xaxis.set_major_formatter(FuncFormatter(pct))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _, z=z: f"{v:.1f} %" if z == "Cabeceras" else f"{v:.0f} %"))
        _rejilla(ax)
    axs[0].set_ylabel("Incidencia H final")
    axs[1].set_xlabel("Meta de reducción de M0 en cada zona (m)")
    axs[0].legend(frameon=False, fontsize=7.5, loc="lower left")
    fig.tight_layout()
    fig.savefig(F / "figura_M34-3_H_por_zona.png", dpi=300)
    plt.close(fig)


def main(D, F):
    D, F = Path(D), Path(F)
    F.mkdir(parents=True, exist_ok=True)
    figura_costo(D, F)
    figura_rmax(D, F)
    figura_H_zonas(D, F)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
