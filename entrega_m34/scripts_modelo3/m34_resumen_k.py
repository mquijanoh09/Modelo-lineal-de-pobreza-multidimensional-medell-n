# -*- coding: utf-8 -*-
"""Tabla de m34_sensibilidad_k: mediana [p5; p95] por k y comparacion pareada con k = 4 y con M3.
Uso: python3 m34_resumen_k.py <dir_sens_k> <salida.csv>"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

d = Path(sys.argv[1])
df = pd.concat([pd.read_csv(p) for p in d.glob("t_*.csv")], ignore_index=True)
cal = pd.read_csv(d / "calidad_k.csv")
print("estados:", df.estado.value_counts().to_dict(), "| replicas:", df.replica.nunique())
q = lambda s: f"{s.median():,.0f} [{s.quantile(.05):,.0f}; {s.quantile(.95):,.0f}]"
qp = lambda s: f"{100*s.median():.0f} %"
filas = []
for (obj, B), g in df.groupby(["objetivo", df.B.fillna(-1)]):
    base3 = g[g.modelo == "m3"].set_index("replica").sort_index()
    base4 = g[g.modelo == "m4_k4"].set_index("replica").sort_index()
    for mod, h in g.groupby("modelo"):
        h = h.set_index("replica").sort_index()
        f = dict(objetivo=obj, B=None if B < 0 else B, modelo=mod)
        if obj == "equidad":
            f["salen"] = q(h.personas_salen)
            f["vs_M3_mediana"] = round((h.personas_salen / base3.personas_salen).median(), 2)
            f["gana_a_M3"] = f"{100*(h.personas_salen > base3.personas_salen).mean():.0f} %"
            f["vs_k4_mediana"] = round((h.personas_salen / base4.personas_salen).median(), 2)
            f["sev_red"] = qp(h.sev_reduccion)
        else:
            f["costo_mm"] = f"{h.costo_pesos.median()/1e3:.1f} [{h.costo_pesos.quantile(.05)/1e3:.1f}; {h.costo_pesos.quantile(.95)/1e3:.1f}]"
            f["vs_M3_mediana"] = round((h.costo_pesos / base3.costo_pesos).median(), 2)
            f["gana_a_M3"] = f"{100*(h.costo_pesos < base3.costo_pesos).mean():.0f} %"
            f["vs_k4_mediana"] = round((h.costo_pesos / base4.costo_pesos).median(), 2)
        f["inclusion_pesos"] = qp(h.inclusion_pesos)
        f["exclusion"] = qp(h.exclusion)
        filas.append(f)
res = pd.DataFrame(filas)
res.to_csv(sys.argv[2], index=False)
pd.set_option("display.width", 250)
print(cal.round(4).to_string(index=False))
print(res.to_string(index=False))
