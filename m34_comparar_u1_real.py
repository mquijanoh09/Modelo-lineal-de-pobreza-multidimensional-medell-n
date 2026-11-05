# -*- coding: utf-8 -*-
"""
m34_comparar_u1_real.py — Compara u = 1 (3-nov) contra costos reales (4-nov), pareado por replica.

Pregunta: ¿los hallazgos de M3/M4 sobreviven al cambio de costos? (ahorro de M4, campana de la
inclusion, convexidad, precio de la informacion, pares chicos).

Uso: python3 m34_comparar_u1_real.py <barrido_v2_crudo.csv> <dir_barrido_real> <equidad_u1.csv>
        <equidad_real.csv> <info_perfecta_u1.csv> <info_perfecta_real.csv> <dir_salida>
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

bu1, dreal, eu1, ereal, ipu1, ipreal, out = sys.argv[1:8]
out = Path(out)
out.mkdir(parents=True, exist_ok=True)
pd.set_option("display.width", 250)

# ---------- 1. curva costo-meta ----------
a = pd.read_csv(bu1)
a = a[(a.variante == "u1")]
b = pd.concat([pd.read_csv(p) for p in Path(dreal).glob("*.csv")], ignore_index=True)
print("estados real:", b.groupby("modelo").estado.value_counts().to_dict())
df = pd.concat([a.assign(costos="u1"), b.assign(costos="real")], ignore_index=True)
df = df[df.estado == "Optimal"].copy()
reps = set(b.replica)
df = df[df.replica.isin(reps)]
df["costo_mm"] = df.objetivo / 1e3
df["frac_chicos"] = df.costo_pares_n_lt10 / df.objetivo
agg = df.groupby(["costos", "meta", "modelo"]).agg(
    costo=("costo_mm", "median"), p5=("costo_mm", lambda s: s.quantile(.05)),
    p95=("costo_mm", lambda s: s.quantile(.95)), inclusion=("inclusion_pesos", "median"),
    exclusion=("exclusion", "median"), frac_chicos=("frac_chicos", "max"), n=("replica", "nunique")).reset_index()
p = df.pivot_table(index=["costos", "meta", "replica"], columns="modelo", values="costo_mm").dropna()
ah = (1 - p.m4 / p.m3).groupby(["costos", "meta"]).median().rename("ahorro_m4")
gana = (p.m4 < p.m3).groupby(["costos", "meta"]).mean().rename("m4_mas_barato")
t = agg.pivot_table(index=["meta"], columns=["costos", "modelo"],
                    values=["costo", "inclusion", "exclusion"]).round(3)
t.columns = [f"{x}_{c}_{m}" for x, c, m in t.columns]
t = t.join(ah.unstack(0).add_prefix("ahorro_m4_").round(3)).join(gana.unstack(0).add_prefix("m4_barato_").round(2))
for m in ["m3", "m4"]:
    t[f"razon_real_u1_{m}"] = (t[f"costo_real_{m}"] / t[f"costo_u1_{m}"]).round(3)
t.to_csv(out / "comparacion_barrido_u1_real.csv")
cols = ["costo_u1_m3", "costo_real_m3", "costo_u1_m4", "costo_real_m4", "razon_real_u1_m3", "razon_real_u1_m4",
        "ahorro_m4_u1", "ahorro_m4_real", "m4_barato_real", "inclusion_u1_m3", "inclusion_real_m3",
        "inclusion_u1_m4", "inclusion_real_m4"]
print(t[cols].to_string())
print("max fraccion del costo en pares con n < 10 (real):",
      agg[agg.costos == "real"].groupby("modelo").frac_chicos.max().to_dict())

# gasto por dimension con meta 10 %
dims = [c for c in df.columns if c.startswith("gasto_") and c[6:] in
        ["Educacion", "Ninez", "Trabajo", "Salud", "Vivienda"]]
g = df[df.meta == 0.10].groupby(["costos", "modelo"])[dims].median()
g = g.div(g.sum(1), axis=0).round(3)
g.to_csv(out / "gasto_dimension_meta10_u1_real.csv")
print("\nReparto del gasto por dimension (meta 10 %, mediana, fraccion):\n", g.to_string())

# ---------- 2. equidad + informacion perfecta ----------
e = pd.concat([pd.read_csv(eu1).assign(costos="u1"), pd.read_csv(ereal).assign(costos="real")], ignore_index=True)
e = e[e.replica.isin(set(pd.read_csv(ereal).replica))]
ip = pd.concat([pd.read_csv(ipu1).assign(costos="u1"), pd.read_csv(ipreal).assign(costos="real")])
eo = e[(e.estado == "Optimal") & (e.rho == 0)]
q = eo.groupby(["costos", "B", "modelo"]).agg(salen=("personas_salen", "median"),
                                             inclusion=("inclusion_pesos", "median"),
                                             sev=("sev_reduccion", "median")).reset_index()
ipo = ip[ip.rho == 0].set_index(["costos", "B"]).personas_salen
q["ip"] = [ipo.get((c, bb)) for c, bb in zip(q.costos, q.B)]
q["frac_ip"] = (q.salen / q.ip).round(3)
pr = eo.pivot_table(index=["costos", "B", "replica"], columns="modelo", values="personas_salen").dropna()
raz = (pr.m4 / pr.m3).groupby(["costos", "B"]).median().rename("m4_sobre_m3")
fact = e[e.rho == 0.10].assign(ok=lambda x: x.estado == "Optimal").groupby(["costos", "B", "modelo"]).ok.mean()
qt = q.pivot_table(index="B", columns=["costos", "modelo"], values=["salen", "frac_ip", "inclusion"]).round(3)
qt.columns = [f"{x}_{c}_{m}" for x, c, m in qt.columns]
qt = qt.join(raz.unstack(0).add_prefix("m4_sobre_m3_").round(2))
qt = qt.join(ipo.unstack(0).add_prefix("ip_").round(0))
qt.to_csv(out / "comparacion_equidad_u1_real.csv")
print("\nEquidad (rho = 0, mediana):\n", qt.to_string())
print("\nFactible con rho = 10 % (fraccion de replicas):\n", fact.unstack([0, 2]).round(2).to_string())
print("\nInfo perfecta:\n", ip.pivot_table(index="B", columns=["costos", "rho"], values="personas_salen").round(0).to_string())

# ---------- 3. grafica ----------
fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.3))
col = {"m3": "#c0504d", "m4": "#4f81bd"}
nom = {"m3": "M3", "m4": "M4"}
for (c, ls) in [("u1", "--"), ("real", "-")]:
    for m in ["m3", "m4"]:
        s = agg[(agg.costos == c) & (agg.modelo == m)]
        ax[0].plot(s.meta * 100, s.costo, ls, color=col[m], label=f"{nom[m]} ({'u = 1' if c == 'u1' else 'costos reales'})")
        if c == "real":
            ax[0].fill_between(s.meta * 100, s.p5, s.p95, color=col[m], alpha=.12)
        ax[1].plot(s.meta * 100, s.inclusion * 100, ls, color=col[m], label=f"{nom[m]} ({c})")
ax[0].set(xlabel="Meta de reducción de M0 (%)", ylabel="Costo (mil millones de $ 2025)",
          title="Costo de la meta: u = 1 vs costos reales")
ax[1].set(xlabel="Meta de reducción de M0 (%)", ylabel="Error de inclusión en pesos (%)",
          title="Fracción del gasto en hogares no pobres")
for a_ in ax:
    a_.grid(alpha=.3)
    a_.legend(fontsize=8)
fig.tight_layout()
fig.savefig(out / "u1_vs_real.png", dpi=150)
