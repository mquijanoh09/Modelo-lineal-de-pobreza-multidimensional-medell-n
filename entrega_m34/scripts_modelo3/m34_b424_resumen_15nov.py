# -*- coding: utf-8 -*-
"""
m34_b424_resumen_15nov.py — Resume las corridas de B = $424 mil millones (m34_b424_15nov.py y m34_equidad_comun.py)
con el mismo formato e intervalos bootstrap de las tablas del 10 y 12-nov, para agregarlas como una fila más.

Uso: python3 m34_b424_resumen_15nov.py <out424/> <salida/>
  entrada: ref424.csv, ipmax.csv, rmax424.csv, equidad_424_crudo.csv
  salida:  r_rho_424_15nov.csv, ip_rmax_15nov.csv, ic_rmax_424_15nov.csv, ic_bootstrap_equidad_424_15nov.csv
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from m34_bootstrap_ic import ic_mediana, ic_pareado


def main(entrada, salida):
    e, s = Path(entrada), Path(salida)
    ref = pd.read_csv(e / "ref424.csv")
    assert (ref.M1_estado_r == "Optimal").all() and (ref.M1_estado_r0 == "Optimal").all()
    ref.to_csv(s / "r_rho_424_15nov.csv", index=False)
    ip = pd.read_csv(e / "ipmax.csv")
    assert (ip.gap.abs() < 1e-6).all()
    ip.to_csv(s / "ip_rmax_15nov.csv", index=False)
    rB = float(ref.r_B.iloc[0])

    d = pd.read_csv(e / "rmax424.csv")
    w = d.pivot(index="replica", columns="modelo", values="r_max")
    assert len(w) == 100 and w.notna().all().all()
    r = dict(B=424, n=len(w), r_B=rB, IP_max=float(ip.loc[ip.B == 424, "IP_max"].iloc[0]))
    for m in ["m3", "m4", "m4p"]:
        r[m], r[m + "_ic_inf"], r[m + "_ic_sup"] = ic_mediana(w[m])
        r[m + "_mejor"] = w[m].max()
        r[m + "_pct_factible_rB"] = 100 * float((w[m] >= rB).mean())
    pd.DataFrame([r]).to_csv(s / "ic_rmax_424_15nov.csv", index=False)

    q = pd.read_csv(e / "equidad_424_crudo.csv")
    q = q[q.rho == 0]
    assert (q.estado == "Optimal").all()
    w = q.pivot(index="replica", columns="modelo", values="personas_salen")
    ipm1 = float(ref.M1_salen_r0.iloc[0])
    f = dict(B=424.0, n=len(w), IP_M1=ipm1)
    for m in ["m3", "m4", "m4p"]:
        f[m + "_mediana"], f[m + "_ic_inf"], f[m + "_ic_sup"] = ic_mediana(w[m])
        f[m + "_cv"] = float(w[m].std() / w[m].mean())
        f[m + "_pct_IP"] = 100 * f[m + "_mediana"] / ipm1
    f["M4_sobre_M3"], f["M4_sobre_M3_ic_inf"], f["M4_sobre_M3_ic_sup"] = ic_pareado(w.m4, w.m3)
    f["pct_M4_mayor_M3"] = 100 * float((w.m4 > w.m3).mean())
    f["M4_sobre_placebo"], f["M4_sobre_placebo_ic_inf"], f["M4_sobre_placebo_ic_sup"] = ic_pareado(w.m4, w.m4p)
    pd.DataFrame([f]).to_csv(s / "ic_bootstrap_equidad_424_15nov.csv", index=False)
    print(pd.DataFrame([r]).round(4).T, pd.DataFrame([f]).round(3).T, sep="\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
