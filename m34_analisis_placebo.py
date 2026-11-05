# -*- coding: utf-8 -*-
"""
m34_analisis_placebo.py — Lectura del placebo de M4 (escenario comun). Solo replicas con las tres
variantes (M3, M4, M4 placebo) y todas Optimal: comparacion pareada por replica (mismo sorteo R).

Por meta: costos medianos; razones pareadas M4/M3 y M4p/M3; "parte de la ventaja de M4 que logra
el placebo" = mediana(M3 - M4p) / mediana(M3 - M4); % de replicas con M4 < M4p; IC 95 % bootstrap
(2.000 remuestreos de replicas) de la razon pareada M4/M4p.

Uso: python3 m34_analisis_placebo.py [carpeta=out/barrido_comun] [salida=resultados/m34/placebo_comun.csv]
"""
import glob
import sys

import numpy as np
import pandas as pd

carpeta = sys.argv[1] if len(sys.argv) > 1 else "out/barrido_comun"
salida = sys.argv[2] if len(sys.argv) > 2 else "resultados/m34/placebo_comun.csv"
d = pd.concat([pd.read_csv(f) for f in glob.glob(f"{carpeta}/*.csv")])
assert (d.estado == "Optimal").all(), d.estado.value_counts()
c = d.pivot_table(index=["meta", "replica"], columns="modelo", values="costo_pesos") / 1e3
c = c.dropna()
reps = c.reset_index().replica.nunique()
rng = np.random.default_rng(2026)
filas = []
for meta, g in c.groupby(level="meta"):
    g = g.droplevel("meta")
    r = (g.m4 / g.m4p).to_numpy()
    boot = [np.median(rng.choice(r, r.size)) for _ in range(2000)]
    dif4, difp = (g.m3 - g.m4).median(), (g.m3 - g.m4p).median()
    filas.append(dict(meta=meta, replicas=len(g), M3=g.m3.median(), M4=g.m4.median(), M4_placebo=g.m4p.median(),
                      M4_sobre_M3=(g.m4 / g.m3).median(), placebo_sobre_M3=(g.m4p / g.m3).median(),
                      ventaja_que_logra_placebo=difp / dif4 if dif4 > 0 else np.nan,
                      M4_sobre_placebo=np.median(r), IC95_inf=np.percentile(boot, 2.5), IC95_sup=np.percentile(boot, 97.5),
                      pct_M4_menor_placebo=100 * (g.m4 < g.m4p).mean(),
                      pct_M4_menor_M3=100 * (g.m4 < g.m3).mean()))
t = pd.DataFrame(filas)
pd.set_option("display.width", 250)
print(f"{reps} replicas pareadas; costos en miles de millones de $ 2025")
print(t.round(3).to_string(index=False))
t.round(5).to_csv(salida, index=False)
print("->", salida)
