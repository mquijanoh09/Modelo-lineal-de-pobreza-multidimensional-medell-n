# -*- coding: utf-8 -*-
"""
m34_analisis_equidad_comun.py — Lectura del objetivo de equidad en el escenario comun.

rho = 0 (solo max personas que salen; la severidad es desempate). Por presupuesto B: personas que salen
(mediana de replicas) de M3, M4 y placebo; % del techo de informacion perfecta (M1 de Martin sin E-7);
razones pareadas M4/M3 y M4/placebo con IC 95 % bootstrap; reduccion de severidad e inclusion.
Con rho = 0,10 se reporta la factibilidad (exigir 10 % menos de severidad).

Uso: python3 m34_analisis_equidad_comun.py   (lee out/equidad_comun y resultados/m34/info_perfecta_equidad_comun.csv)
"""
import glob

import numpy as np
import pandas as pd

d = pd.concat([pd.read_csv(f) for f in glob.glob("out/equidad_comun/*.csv")])
ip = pd.read_csv("resultados/m34/info_perfecta_equidad_comun.csv").set_index("B")
assert (ip.estado == "Optimal").all()
print("estados:", d.groupby(["rho", "estado"]).size().to_dict())
e = d[(d.rho == 0) & (d.estado == "Optimal")]
assert e.groupby("B").size().eq(90).all(), "faltan replicas optimas con rho = 0"
p = e.pivot_table(index=["B", "replica"], columns="modelo", values="personas_salen")
rng = np.random.default_rng(2026)


def ic(x):
    b = [np.median(rng.choice(x, x.size)) for _ in range(2000)]
    return f"{np.median(x):.2f} ({np.percentile(b, 2.5):.2f}-{np.percentile(b, 97.5):.2f})"


filas = []
for B, g in p.groupby(level="B"):
    g = g.droplevel("B"); techo = ip.loc[B, "personas_salen"]
    s = e[e.B == B].groupby("modelo")
    filas.append({"B": B, "IP (M1)": round(techo), "M3": round(g.m3.median()), "M4": round(g.m4.median()),
                  "placebo": round(g.m4p.median()),
                  "M3 %IP": 100 * g.m3.median() / techo, "M4 %IP": 100 * g.m4.median() / techo,
                  "placebo %IP": 100 * g.m4p.median() / techo,
                  "M4/M3 (IC)": ic((g.m4 / g.m3).to_numpy()), "M4/placebo (IC)": ic((g.m4 / g.m4p).to_numpy()),
                  "%rep M4>placebo": 100 * (g.m4 > g.m4p).mean(),
                  "sev M3 %": 100 * s.sev_reduccion.median()["m3"], "sev M4 %": 100 * s.sev_reduccion.median()["m4"],
                  "incl M3 %": 100 * s.inclusion_pesos.median()["m3"], "incl M4 %": 100 * s.inclusion_pesos.median()["m4"]})
t = pd.DataFrame(filas)
pd.set_option("display.width", 300)
print(t.round(1).to_string(index=False))
f10 = d[d.rho == 0.10].assign(ok=lambda x: x.estado == "Optimal").groupby(["B", "modelo"]).ok.mean().unstack() * 100
print("\nrho = 0,10: % replicas factibles"); print(f10.round(0).to_string())
t.to_csv("resultados/m34/equidad_comun_resumen.csv", index=False)
print("-> resultados/m34/equidad_comun_resumen.csv")
