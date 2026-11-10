# -*- coding: utf-8 -*-
"""Verifica contra los CSV congelados (datos-finales-10nov) cada cifra de M3/M4 que afirma el paper."""
import numpy as np
import pandas as pd

R = "resultados/m34/"
c = pd.read_csv(R + "ic_bootstrap_costos_10nov.csv")
e = pd.read_csv(R + "ic_bootstrap_equidad_10nov.csv")
b = pd.read_csv(R + "barrido_comun_crudo_10nov.csv")
q = pd.read_csv(R + "equidad_comun_crudo_10nov.csv")
v = pd.read_csv(R + "validacion_10nov.csv")
res = []


def chk(nombre, ok, valor):
    res.append(ok)
    print(("OK   " if ok else "FALLA"), nombre, "|", valor)


baja, alta = c[c.meta <= 0.101], c[c.meta >= 0.199]
chk("M3/IP metas <=10 %: 6 a 17", round(baja.m3_sobre_IP.min()) == 6 and round(baja.m3_sobre_IP.max()) == 17,
    baja.m3_sobre_IP.round(2).tolist())
chk("M3/IP metas >=20 %: 3,5 a 3,9", round(alta.m3_sobre_IP.min(), 1) == 3.5 and round(alta.m3_sobre_IP.max(), 1) == 3.9,
    alta.m3_sobre_IP.round(2).tolist())
p22 = c[c.meta >= 0.219].M4_sobre_placebo
chk("M4 vs placebo metas >=22 %: 14 a 31 % menos", round(100 * (1 - p22.max())) == 14 and round(100 * (1 - p22.min())) == 31,
    p22.round(3).tolist())
med = b.groupby(["meta", "modelo"]).costo_pesos.median().unstack()
caro = med.index[med.m4 >= med.m3].round(2).tolist()
chk("M4 mediana más barata que M3 salvo 16 %", caro == [0.16], caro)
chk("IC M4/M3 < 1 en 13 de 15 metas", (c.M4_sobre_M3_ic_sup < 1).sum() == 13, (c.M4_sobre_M3_ic_sup < 1).sum())
b18 = c[c.meta <= 0.181]
cont = (b18.M4_sobre_placebo_ic_inf <= 1) & (b18.M4_sobre_placebo_ic_sup >= 1)
chk("IC M4/placebo contiene 1 en 6 de 9 metas <=18 %", cont.sum() == 6,
    b18.loc[~cont, ["meta", "M4_sobre_placebo"]].round(2).values.tolist())
inc = pd.concat([c.m3_inclusion_pesos, c.m4_inclusion_pesos])
chk("inclusión 25-69 %", round(100 * inc.min()) == 25 and round(100 * inc.max()) == 69, (inc.min(), inc.max()))
ex = b.groupby(["meta", "modelo"]).exclusion.median()
chk("exclusión M3 97 % (2 %) y 58 % (30 %)", round(100 * ex[(0.02, "m3")]) == 97 and round(100 * ex[(0.30, "m3")]) == 58,
    (ex[(0.02, "m3")], ex[(0.30, "m3")], ex[(0.02, "m4")], ex[(0.30, "m4")]))
chk("4.500 corridas óptimas, gap < 1e-6", len(b) == 4500 and (b.estado == "Optimal").all() and b.gap.max() < 1e-6, (len(b), b.gap.max()))
sa = pd.concat([(c.m3_ic_sup - c.m3_ic_inf) / 2 / c.m3_mediana, (c.m4_ic_sup - c.m4_ic_inf) / 2 / c.m4_mediana], axis=1).max(axis=1)
chk("IC mediana <= ±10 % en todas las metas", (sa <= 0.105).all(), sa.round(3).tolist())
chk("IC mediana <= ±5 % desde 12 %", (sa[c.meta >= 0.119] <= 0.05).all(), sa[c.meta >= 0.119].round(3).tolist())
chk("CV M3 máx 0,46", round(c.m3_cv.max(), 2) == 0.46, c.m3_cv.max())
chk("equidad M3 13-65 %", round(e.m3_pct_IP.min()) == 13 and round(e.m3_pct_IP.max()) == 65, e.m3_pct_IP.round(1).tolist())
chk("equidad M4 19-67 %", round(e.m4_pct_IP.min()) == 19 and round(e.m4_pct_IP.max()) == 67, e.m4_pct_IP.round(1).tolist())
r = e.set_index("B")
chk("B=2: M4/M3 no significativo", r.loc[2, "M4_sobre_M3_ic_inf"] < 1 < r.loc[2, "M4_sobre_M3_ic_sup"], r.loc[2, ["M4_sobre_M3_ic_inf", "M4_sobre_M3_ic_sup"]].tolist())
chk("B=5: M4/M3 1,86 y placebo igual", round(r.loc[5, "M4_sobre_M3"], 2) == 1.86 and r.loc[5, "M4_sobre_placebo_ic_inf"] < 1 < r.loc[5, "M4_sobre_placebo_ic_sup"],
    (r.loc[5, "M4_sobre_M3"], r.loc[5, "M4_sobre_placebo_ic_inf"], r.loc[5, "M4_sobre_placebo_ic_sup"]))
g = r.loc[[50, 100]]
chk("B>=50: M4/placebo 9-10 %, IC sin 1", (g.M4_sobre_placebo_ic_inf > 1).all() and round(100 * (g.M4_sobre_placebo.min() - 1)) == 9 and round(100 * (g.M4_sobre_placebo.max() - 1)) == 10,
    g.M4_sobre_placebo.round(3).tolist())
chk("B>=50: M3 en torno al 60 % del techo", ((g.m3_pct_IP > 57) & (g.m3_pct_IP < 61)).all(), g.m3_pct_IP.round(1).tolist())
chk("CV equidad B<=10 entre 0,32 y 0,55 (M3)", round(r.loc[[2, 5, 10], "m3_cv"].min(), 2) == 0.32 and round(r.loc[[2, 5, 10], "m3_cv"].max(), 2) == 0.55, r.m3_cv.round(3).tolist())
chk("CV equidad B>=25 <= 0,05 y TLC pide < 5 réplicas", (r.loc[[25, 50, 100], ["m3_cv", "m4_cv", "m4p_cv"]].round(2) <= 0.05).all().all() and (r.loc[[25, 50, 100], ["m3_n_tlc_5pct", "m4_n_tlc_5pct", "m4p_n_tlc_5pct"]] < 5).all().all(), r.loc[[25, 50, 100], ["m3_cv", "m4_cv"]].round(3).values.tolist())
rho = q[q.rho == 0.1]
chk("rho 0,10 infactible en 900 corridas con B <= 10", (rho[rho.B <= 10].estado != "Optimal").sum() == 900, (rho[rho.B <= 10].estado != "Optimal").sum())
chk("rho 0,10 factible en todas con B >= 25", (rho[rho.B >= 25].estado == "Optimal").all(), (rho[rho.B >= 25].estado == "Optimal").sum())
chk("validación 18/18", v.ok.all() and len(v) == 18, int(v.ok.sum()))
d5 = v[v.prueba.str.contains("meta 20|meta 30")].detalle.tolist()
chk("V5 exceso 5,9 % (20 %) y 2,7 % (30 %)", "5.90" in d5[0] and "2.73" in d5[1], d5)
for k in ["Salud", "Educacion", "Cabecera", "Trabajo", "Ninez", "Vivienda"]:
    b[k] = b[f"gasto_{k}"] / b.costo_pesos
t = b.groupby(["meta", "modelo"])[["Salud", "Educacion", "Cabecera", "Trabajo", "Ninez", "Vivienda"]].mean()
s18 = t.loc[[m for m in t.index if m[0] <= 0.181]].Salud
chk("salud 97-100 % hasta 18 %", round(100 * s18.min()) == 97, round(s18.min(), 3))
e30 = t.loc[0.30].Educacion
chk("educación 68-81 % con 30 %", round(100 * e30.min()) == 68 and round(100 * e30.max()) == 81, e30.round(3).tolist())
cab = t.Cabecera.unstack()
mid = cab.loc[[0.06, 0.10, 0.14]]
chk("cabecera M3 84-97 %, M4/placebo 58-73 % (6-14 %)", round(100 * mid.m3.min()) == 84 and round(100 * mid.m3.max()) == 97
    and round(100 * mid[["m4", "m4p"]].min().min()) == 58 and round(100 * mid[["m4", "m4p"]].max().max()) == 73, mid.round(3).values.tolist())
chk("niñez+vivienda <= 2 %, trabajo <= 13 %", (t.Ninez + t.Vivienda).max() <= 0.02 and round(100 * t.Trabajo.max()) <= 13, ((t.Ninez + t.Vivienda).max(), t.Trabajo.max()))
ip = c.set_index("meta").IP_M2
m3_6 = c.set_index("meta").m3_mediana
chk("discusión: meta 6 %: M3 5,66 vs IP 0,51 (dif ~5)", round(m3_6[0.06], 2) == 5.66 and round(ip[0.06], 2) == 0.51, (m3_6[0.06], ip[0.06]))
print(f"\n{sum(res)}/{len(res)} cifras verificadas")
