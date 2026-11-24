# -*- coding: utf-8 -*-
"""IC bootstrap del Monte Carlo de M3/M4 (escenario común) y justificación del número de réplicas.

Cierra el hallazgo 7 de la auditoría del 3-nov: con n = 100 los p5/p95 son el 5.º y el 95.º estadístico
de orden (ruidosos); lo que sí se estabiliza es la MEDIANA y la diferencia PAREADA M4 vs M3 (misma R).

Uso:
    python m34_bootstrap_ic.py resultados/m34/barrido_comun_crudo.csv resultados/m34/equidad_comun_crudo.csv \
        resultados/m34/info_perfecta_comun.csv resultados/m34/info_perfecta_equidad_comun.csv resultados/m34

Salidas (en la carpeta del último argumento):
    ic_bootstrap_costos.csv   mediana del costo por meta y modelo con IC 95 %, M4/M3 pareado, n por TLC
    ic_bootstrap_equidad.csv  lo mismo para personas que salen con presupuesto B (rho = 0)
    convergencia_n.csv        semiancho relativo del IC de la mediana con n = 10, 30, 50, 100
    convergencia_n.png        gráfica de lo anterior

Número de réplicas por TLC (ec. 8 del paper): para que el IC 95 % de la MEDIA tenga semiancho
relativo E, n >= (z * s / (E * media))^2 = (z * CV / E)^2. Se reporta con E = 5 % y E = 10 %.
El bootstrap es de percentiles, B = 5.000 remuestreos, semilla fija; se remuestrean RÉPLICAS (no filas),
así la comparación pareada conserva que M3, M4 y el placebo comparten el mismo sorteo R.
"""
import os
import sys

import numpy as np
import pandas as pd

Z = 1.959964
B_BOOT = 5000
RNG = np.random.default_rng(20261106)


def ic_mediana(x, rng=RNG, b=B_BOOT):
    x = np.asarray(x, float)
    idx = rng.integers(0, len(x), size=(b, len(x)))
    meds = np.median(x[idx], axis=1)
    return np.median(x), np.quantile(meds, .025), np.quantile(meds, .975)


def ic_pareado(a, b_, rng=RNG, b=B_BOOT):
    """Mediana de a/b_ réplica a réplica y su IC; a y b_ alineados por réplica."""
    r = np.asarray(a, float) / np.asarray(b_, float)
    return ic_mediana(r, rng, b)


def n_tlc(x, e):
    x = np.asarray(x, float)
    cv = x.std(ddof=1) / x.mean()
    return int(np.ceil((Z * cv / e) ** 2)), cv


def main(barrido, equidad, ip_costos, ip_equidad, salida):
    os.makedirs(salida, exist_ok=True)
    d = pd.read_csv(barrido)
    assert (d.estado == "Optimal").all(), "hay corridas no óptimas en el barrido"
    d["costo_mm"] = d.costo_pesos / 1000.0          # millones -> miles de millones de $ 2025
    ip = pd.read_csv(ip_costos).set_index("meta").costo_mm

    filas = []
    for meta, g in d.groupby("meta"):
        w = g.pivot(index="replica", columns="modelo", values="costo_mm").dropna()
        inc = g.pivot(index="replica", columns="modelo", values="inclusion_pesos").loc[w.index]
        f = dict(meta=meta, n=len(w), IP_M2=ip.get(meta, np.nan))
        for m in ["m3", "m4", "m4p"]:
            med, lo, hi = ic_mediana(w[m])
            f[f"{m}_mediana"], f[f"{m}_ic_inf"], f[f"{m}_ic_sup"] = med, lo, hi
            f[f"{m}_p5"], f[f"{m}_p95"] = w[m].quantile(.05), w[m].quantile(.95)
            n5, cv = n_tlc(w[m], .05)
            f[f"{m}_cv"], f[f"{m}_n_tlc_5pct"], f[f"{m}_n_tlc_10pct"] = cv, n5, n_tlc(w[m], .10)[0]
            mi, li, hi_ = ic_mediana(inc[m])
            f[f"{m}_inclusion_pesos"], f[f"{m}_inc_ic_inf"], f[f"{m}_inc_ic_sup"] = mi, li, hi_
            # precio de la información: costo del modelo / costo con información perfecta
            f[f"{m}_sobre_IP"] = med / f["IP_M2"]
            f[f"{m}_sobre_IP_ic"] = f"{lo / f['IP_M2']:.2f}-{hi / f['IP_M2']:.2f}"
        r, rl, rh = ic_pareado(w.m4, w.m3)
        f.update(M4_sobre_M3=r, M4_sobre_M3_ic_inf=rl, M4_sobre_M3_ic_sup=rh,
                 pct_M4_menor_M3=100 * (w.m4 < w.m3).mean())
        r, rl, rh = ic_pareado(w.m4, w.m4p)
        f.update(M4_sobre_placebo=r, M4_sobre_placebo_ic_inf=rl, M4_sobre_placebo_ic_sup=rh)
        filas.append(f)
    tab = pd.DataFrame(filas)
    tab.to_csv(os.path.join(salida, "ic_bootstrap_costos.csv"), index=False)

    # Convergencia: semiancho relativo del IC de la mediana usando las primeras n réplicas
    conv = []
    for meta, g in d.groupby("meta"):
        for m in ["m3", "m4"]:
            x = g[g.modelo == m].sort_values("replica").costo_mm.values
            for n in [10, 30, 50, 100]:
                if n > len(x):
                    continue
                med, lo, hi = ic_mediana(x[:n])
                conv.append(dict(meta=meta, modelo=m, n=n, mediana=med, semiancho_rel=(hi - lo) / 2 / med))
    conv = pd.DataFrame(conv)
    conv.to_csv(os.path.join(salida, "convergencia_n.csv"), index=False)

    # Equidad (rho = 0; rho = 0,10 es infactible con B <= 10 y se reporta aparte)
    e = pd.read_csv(equidad)
    e = e[(e.rho == 0) & (e.estado == "Optimal")]
    ipe = pd.read_csv(ip_equidad).set_index("B").personas_salen
    filas = []
    for B, g in e.groupby("B"):
        w = g.pivot(index="replica", columns="modelo", values="personas_salen").dropna()
        f = dict(B=B, n=len(w), IP_M1=ipe.get(B, np.nan))
        for m in ["m3", "m4", "m4p"]:
            med, lo, hi = ic_mediana(w[m])
            n5, cv = n_tlc(w[m], .05)
            f.update({f"{m}_mediana": med, f"{m}_ic_inf": lo, f"{m}_ic_sup": hi, f"{m}_cv": cv,
                      f"{m}_n_tlc_5pct": n5, f"{m}_pct_IP": 100 * med / f["IP_M1"]})
        r, rl, rh = ic_pareado(w.m4, w.m3)
        f.update(M4_sobre_M3=r, M4_sobre_M3_ic_inf=rl, M4_sobre_M3_ic_sup=rh,
                 pct_M4_mayor_M3=100 * (w.m4 > w.m3).mean())
        r, rl, rh = ic_pareado(w.m4, w.m4p)
        f.update(M4_sobre_placebo=r, M4_sobre_placebo_ic_inf=rl, M4_sobre_placebo_ic_sup=rh)
        filas.append(f)
    pd.DataFrame(filas).to_csv(os.path.join(salida, "ic_bootstrap_equidad.csv"), index=False)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
        for a, m, tit in [(ax[0], "m3", "Modelo 3"), (ax[1], "m4", "Modelo 4")]:
            for meta in [0.04, 0.10, 0.20, 0.30]:
                c = conv[(conv.modelo == m) & np.isclose(conv.meta, meta)]
                a.plot(c.n, 100 * c.semiancho_rel, marker="o", label=f"meta {meta:.0%}")
            a.axhline(5, color="gray", ls="--", lw=.8)
            a.set_title(tit); a.set_xlabel("réplicas n"); a.grid(alpha=.3)
        ax[0].set_ylabel("semiancho del IC 95 % de la mediana (% de la mediana)")
        ax[1].legend()
        fig.suptitle("Convergencia del Monte Carlo (escenario común, bootstrap de réplicas)")
        fig.tight_layout()
        fig.savefig(os.path.join(salida, "convergencia_n.png"), dpi=130)
    except ImportError:
        print("sin matplotlib: no se genera la gráfica")

    pd.set_option("display.width", 250)
    cols = ["meta", "n", "IP_M2", "m3_mediana", "m3_ic_inf", "m3_ic_sup", "m4_mediana", "m4_ic_inf",
            "m4_ic_sup", "M4_sobre_M3", "M4_sobre_M3_ic_inf", "M4_sobre_M3_ic_sup", "pct_M4_menor_M3",
            "m3_cv", "m3_n_tlc_5pct", "m4_cv", "m4_n_tlc_5pct"]
    print(tab[cols].round(3).to_string(index=False))
    print(conv.pivot_table(index=["modelo", "meta"], columns="n", values="semiancho_rel").round(3).to_string())


if __name__ == "__main__":
    main(*sys.argv[1:6])
