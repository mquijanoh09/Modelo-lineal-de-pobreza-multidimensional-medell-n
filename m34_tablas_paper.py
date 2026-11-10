# -*- coding: utf-8 -*-
"""
m34_tablas_paper.py — Tablas LaTeX del paper desde las salidas de m34_bootstrap_ic.py (10-nov).
Los números del paper salen de aquí; no se escriben a mano.
Uso: python3 m34_tablas_paper.py <ic_bootstrap_costos.csv> <ic_bootstrap_equidad.csv> <carpeta tablas/>
"""
import sys
from pathlib import Path

import pandas as pd

METAS = [0.02, 0.06, 0.10, 0.14, 0.18, 0.20, 0.24, 0.30]


def f2(x):
    return f"{x:.2f}".replace(".", ",")


def miles(x):
    return f"{x:,.0f}".replace(",", ".")


def main(costos, equidad, carpeta):
    out = Path(carpeta)
    out.mkdir(parents=True, exist_ok=True)
    c = pd.read_csv(costos)
    filas = []
    for meta in METAS:
        r = c[(c.meta - meta).abs() < 1e-9].iloc[0]
        filas.append(
            f"{round(meta * 100)}\\,\\% & {f2(r.IP_M2)} & {f2(r.m3_mediana)} & {f2(r.m4_mediana)} & "
            f"{f2(r.m4p_mediana)} & {f2(r.m3_sobre_IP)} & {f2(r.m4_sobre_IP)} & "
            f"{f2(r.M4_sobre_placebo)} ({f2(r.M4_sobre_placebo_ic_inf)}--{f2(r.M4_sobre_placebo_ic_sup)}) & "
            f"{round(100 * r.m3_inclusion_pesos)} / {round(100 * r.m4_inclusion_pesos)}\\,\\% \\\\")
    (out / "costos.tex").write_text("\n".join(filas) + "\n", encoding="utf-8")

    e = pd.read_csv(equidad)
    filas = []
    for _, r in e.sort_values("B").iterrows():
        filas.append(
            f"{r.B:g} & {miles(r.IP_M1)} & {miles(r.m3_mediana)} & {miles(r.m4_mediana)} & {miles(r.m4p_mediana)} & "
            f"{round(r.m3_pct_IP)}\\,\\% & {round(r.m4_pct_IP)}\\,\\% & "
            f"{f2(r.M4_sobre_M3)} ({f2(r.M4_sobre_M3_ic_inf)}--{f2(r.M4_sobre_M3_ic_sup)}) & "
            f"{f2(r.M4_sobre_placebo)} ({f2(r.M4_sobre_placebo_ic_inf)}--{f2(r.M4_sobre_placebo_ic_sup)}) \\\\")
    (out / "equidad.tex").write_text("\n".join(filas) + "\n", encoding="utf-8")
    print((out / "costos.tex").read_text(encoding="utf-8"))
    print((out / "equidad.tex").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main(*sys.argv[1:4])
