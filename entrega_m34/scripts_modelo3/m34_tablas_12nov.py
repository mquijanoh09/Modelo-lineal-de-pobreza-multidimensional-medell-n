# -*- coding: utf-8 -*-
"""Tablas LaTeX y CSV de resumen de la comparación del 12-nov (restricciones de Martín tal cual).
Uso: python3 m34_tablas_12nov.py <carpeta tablas/>"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from m34_bootstrap_ic import ic_mediana

R = "resultados/m34/"
f2 = lambda x: f"{x:.2f}".replace(".", ",")
f1 = lambda x: f"{x:.1f}".replace(".", ",")
mi = lambda x: f"{x:,.0f}".replace(",", ".")


def costo():
    d = pd.read_csv(R + "costo_meta_zona_crudo_12nov.csv"); d["c"] = d.costo_pesos / 1000
    ip = pd.read_csv(R + "info_perfecta_meta_zona_12nov.csv").set_index("meta").costo_mm
    rows = []
    for meta, g in d.groupby("meta"):
        w = g.pivot(index="replica", columns="modelo", values="c")
        inc = g.pivot(index="replica", columns="modelo", values="inclusion_pesos")
        exc = g.pivot(index="replica", columns="modelo", values="exclusion")
        r = dict(meta=meta, n=len(w), IP=ip[round(meta, 2)])
        for m in ["m3", "m4", "m4p"]:
            r[m], r[m + "_ic_inf"], r[m + "_ic_sup"] = ic_mediana(w[m])
            r[m + "_sobre_IP"] = r[m] / r["IP"]
            r[m + "_inclusion"] = inc[m].median(); r[m + "_exclusion"] = exc[m].median()
        for a, b, n in [("m4", "m3", "M4_sobre_M3"), ("m4", "m4p", "M4_sobre_placebo")]:
            r[n], r[n + "_ic_inf"], r[n + "_ic_sup"] = ic_mediana(w[a] / w[b])
        rows.append(r)
    t = pd.DataFrame(rows); t.to_csv(R + "ic_costo_meta_zona_12nov.csv", index=False)
    return t


def rmax():
    d = pd.read_csv(R + "rmax_12nov.csv")
    ip = {2: 0.0585, 5: 0.1071, 10: 0.1649, 25: 0.2844, 50: 0.3913, 100: 0.5362}   # m34_rmax con un hogar por celda
    rows = []
    for B, g in d.groupby("B"):
        w = g.pivot(index="replica", columns="modelo", values="r_max")
        r = dict(B=B, n=len(w), r_B=g.r_B.iloc[0], IP_max=ip[int(B)])
        for m in ["m3", "m4", "m4p"]:
            r[m], r[m + "_ic_inf"], r[m + "_ic_sup"] = ic_mediana(w[m]); r[m + "_mejor"] = w[m].max()
        rows.append(r)
    t = pd.DataFrame(rows); t.to_csv(R + "ic_rmax_12nov.csv", index=False)
    return t


def main(carpeta):
    out = Path(carpeta); out.mkdir(parents=True, exist_ok=True)
    t = costo()
    sel = [0.02, 0.06, 0.10, 0.14, 0.18, 0.20, 0.24, 0.30]
    L = []
    for _, r in t[t.meta.round(2).isin(sel)].iterrows():
        L.append(f"{round(r.meta * 100)}\\,\\% & {f2(r.IP)} & {f2(r.m3)} & {f2(r.m4)} & {f2(r.m4p)} & {f1(r.m3_sobre_IP)} & "
                 f"{f1(r.m4_sobre_IP)} & {f2(r.M4_sobre_M3)} ({f2(r.M4_sobre_M3_ic_inf)}--{f2(r.M4_sobre_M3_ic_sup)}) & "
                 f"{f2(r.M4_sobre_placebo)} ({f2(r.M4_sobre_placebo_ic_inf)}--{f2(r.M4_sobre_placebo_ic_sup)}) \\\\")
    (out / "costos_zona.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
    q = rmax()
    L = []
    for _, r in q.iterrows():
        pc = lambda x: f"{100 * x:.1f}".replace(".", ",")
        L.append(f"{r.B:g} & {pc(r.r_B)} & {pc(r.IP_max)} & {pc(r.m3)} ({pc(r.m3_ic_inf)}--{pc(r.m3_ic_sup)}) & "
                 f"{pc(r.m4)} ({pc(r.m4_ic_inf)}--{pc(r.m4_ic_sup)}) & {pc(r.m4p)} & {pc(r.m3_mejor)} \\\\")
    (out / "rmax.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
    pd.set_option("display.width", 250)
    print(t[["meta", "IP", "m3", "m4", "m4p", "m3_sobre_IP", "m4_sobre_IP", "M4_sobre_M3", "M4_sobre_M3_ic_inf",
             "M4_sobre_M3_ic_sup", "M4_sobre_placebo", "M4_sobre_placebo_ic_inf", "M4_sobre_placebo_ic_sup",
             "m3_inclusion", "m4_inclusion", "m3_exclusion", "m4_exclusion"]].round(3).to_string(index=False))
    print(q.round(4).to_string(index=False))


if __name__ == "__main__":
    main(sys.argv[1])
