# -*- coding: utf-8 -*-
"""
m34_analisis_12nov.py — IC bootstrap de las corridas de la especificación del 12-nov, con la regla de
factibilidad (§3.3, regla 2): por configuración se reporta la fracción de réplicas factibles; medianas e IC
sobre las factibles; los cocientes pareados, solo en las réplicas donde los dos modelos son factibles.
Uso: python3 m34_analisis_12nov.py <costo_crudo.csv> <cobertura_crudo.csv> <ref/> <salida/>
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from m34_bootstrap_ic import ic_mediana, n_tlc

MODS = ["m3", "m4", "m4p"]


def _pareado(w, a, b):
    ok = w[[a, b]].dropna()
    if len(ok) < 5:
        return np.nan, np.nan, np.nan, len(ok)
    r, lo, hi = ic_mediana(ok[a] / ok[b])
    return r, lo, hi, len(ok)


def resumir(d, clave, valor, ref, ref_col):
    filas = []
    for k, g in d.groupby(clave):
        w = g.pivot(index="replica", columns="modelo", values=valor)
        est = g.pivot(index="replica", columns="modelo", values="estado")
        f = dict(zip(clave if isinstance(clave, list) else [clave], k if isinstance(k, tuple) else [k]))
        f["n"] = len(w)
        f["IP"] = ref(f)
        for m in MODS:
            x = w.loc[est[m] == "Optimal", m]
            f[f"{m}_factibles"] = int(len(x))
            f[f"{m}_frac_factible"] = len(x) / len(w)
            if len(x) >= 5:
                med, lo, hi = ic_mediana(x)
                f.update({f"{m}_mediana": med, f"{m}_ic_inf": lo, f"{m}_ic_sup": hi,
                          f"{m}_cv": n_tlc(x, .05)[1], f"{m}_n_tlc_5pct": n_tlc(x, .05)[0],
                          f"{m}_sobre_IP": med / f["IP"] if f["IP"] else np.nan})
        wf = w.where(est == "Optimal")
        for a, b, n in [("m4", "m3", "M4_sobre_M3"), ("m4", "m4p", "M4_sobre_placebo")]:
            r, lo, hi, npar = _pareado(wf, a, b)
            f.update({n: r, f"{n}_ic_inf": lo, f"{n}_ic_sup": hi, f"{n}_n_pares": npar})
        filas.append(f)
    return pd.DataFrame(filas)


def main(costo, cobertura, ref, salida):
    salida = Path(salida); salida.mkdir(parents=True, exist_ok=True)
    c = pd.read_csv(costo)
    c["costo_mm"] = c.costo_pesos / 1000.0
    ipc = pd.read_csv(Path(ref) / "info_perfecta_meta_zona.csv").set_index("meta").costo_mm
    tc = resumir(c, "meta", "costo_mm", lambda f: ipc.get(round(f["meta"], 2), np.nan), None)
    for m in MODS:
        inc = c[c.estado == "Optimal"].groupby(["meta", "modelo"]).inclusion_pesos.median().unstack()
        tc[f"{m}_inclusion_pesos"] = tc.meta.map(inc[m])
        exc = c[c.estado == "Optimal"].groupby(["meta", "modelo"]).exclusion.median().unstack()
        tc[f"{m}_exclusion"] = tc.meta.map(exc[m])
    tc.to_csv(salida / "ic_costo_meta_zona.csv", index=False)
    e = pd.read_csv(cobertura)
    e = e[e.estado != "sin_rho"]
    rb = pd.read_csv(Path(ref) / "r_rho_comparacion.csv").set_index("B")
    te = resumir(e, ["escenario", "B"], "personas_salen",
                 lambda f: rb.loc[f["B"], "M1_salen_r" if f["escenario"] == "r" else "M1_salen_r_rho"], None)
    for m in MODS:
        te[f"{m}_pct_IP"] = 100 * te[f"{m}_mediana"] / te.IP if f"{m}_mediana" in te else np.nan
    te.to_csv(salida / "ic_cobertura_r.csv", index=False)
    pd.set_option("display.width", 250)
    print(tc[["meta", "n", "IP"] + [f"{m}_frac_factible" for m in MODS] + ["m3_sobre_IP", "m4_sobre_IP", "M4_sobre_M3",
             "M4_sobre_placebo", "M4_sobre_placebo_ic_inf", "M4_sobre_placebo_ic_sup"]].round(3).to_string(index=False))
    print(te[["escenario", "B", "n", "IP"] + [f"{m}_frac_factible" for m in MODS] + [c for c in ["m3_pct_IP", "m4_pct_IP", "m4p_pct_IP"] if c in te]
             + ["M4_sobre_M3", "M4_sobre_placebo", "M4_sobre_placebo_ic_inf", "M4_sobre_placebo_ic_sup"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main(*sys.argv[1:5])
