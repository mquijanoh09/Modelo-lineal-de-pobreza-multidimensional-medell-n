# -*- coding: utf-8 -*-
"""m34_resumen_3nov.py — Tablas del MC lexicografico y de M3/M4 con objetivo de equidad.

Uso: python3 m34_resumen_3nov.py <dir_mc_lex> <equidad.csv> <info_perfecta.csv> <mc_viejo_m3.csv> <mc_viejo_m4.csv>
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def q(s):
    s = s.dropna()
    return f"{s.median():.3g} [{s.quantile(.05):.3g}; {s.quantile(.95):.3g}]"


def main():
    d = pd.concat([pd.read_csv(p) for p in Path(sys.argv[1]).glob("*.csv")], ignore_index=True)
    eq, ip = pd.read_csv(sys.argv[2]), pd.read_csv(sys.argv[3])
    viejo = pd.concat([pd.read_csv(sys.argv[4]), pd.read_csv(sys.argv[5])])
    print("MC lex: filas", len(d), "| estados", d.estado.value_counts().to_dict(),
          "| replicas", d.groupby(["modelo", "variante", "rezago"]).replica.nunique().min())
    d["incl"] = np.where(d.variante == "pp", d.inclusion_personas, d.inclusion_pesos)
    d["obj_rep"] = np.where(d.variante == "pp", d.objetivo, d.objetivo / 1e3)
    filas = []
    for (rez, var, meta, mod), g in d.groupby(["rezago", "variante", "meta", "modelo"]):
        filas.append(dict(rezago=rez, variante=var, meta=meta, modelo=mod, n=len(g),
                          objetivo=q(g.obj_rep), inclusion=q(g.incl), exclusion=q(g.exclusion),
                          H1=f"{g.H1.median():.4f}"))
    t = pd.DataFrame(filas)
    print(t.to_string(index=False))
    t.to_csv("out/resumen_mc_lex.csv", index=False)

    print("\nPareado M4 vs M3 (misma replica):")
    for (rez, var, meta), g in d.groupby(["rezago", "variante", "meta"]):
        p = g.pivot_table(index="replica", columns="modelo", values=["objetivo", "incl"])
        ah = 1 - p["objetivo"]["m4"] / p["objetivo"]["m3"]
        print(f"  {rez:<16}{var} meta {meta:.2f}: M4 mas barato {(ah > 0).mean():.0%}, ahorro mediano "
              f"{ah.median():.0%}; M4 menos inclusion {(p['incl']['m4'] < p['incl']['m3']).mean():.0%} "
              f"(mediana {p['incl']['m3'].median():.0%} -> {p['incl']['m4'].median():.0%})")

    print("\nEfecto del desempate (rezago intervenible, mismas replicas que el 2-nov):")
    viejo["incl"] = np.where(viejo.variante == "pp", viejo.inclusion_personas, viejo.inclusion_pesos)
    lx = d[d.rezago == "intervenible"]
    mm = lx.merge(viejo, on=["modelo", "replica", "meta", "variante"], suffixes=("", "_v"))
    for (mod, var, meta), g in mm.groupby(["modelo", "variante", "meta"]):
        dif = g.incl_v - g.incl
        print(f"  {mod} {var} {meta:.2f}: n={len(g)}, mismo costo {np.isclose(g.objetivo, g.objetivo_v, rtol=1e-5).mean():.0%}, "
              f"inclusion baja en {(dif > 1e-6).mean():.0%} de replicas, mediana {g.incl_v.median():.0%} -> {g.incl.median():.0%}")

    print("\nEfecto de rezago no intervenible (lex):")
    for (mod, var, meta), g in d.groupby(["modelo", "variante", "meta"]):
        p = g.pivot_table(index="replica", columns="rezago", values="objetivo")
        print(f"  {mod} {var} {meta:.2f}: costo sube en {(p.no_intervenible > p.intervenible * (1 + 1e-6)).mean():.0%} "
              f"de replicas; mediana +{(p.no_intervenible / p.intervenible - 1).median():.1%}")

    print("\nEquidad (objetivo del M1), costos u = 1, rezago no intervenible:")
    filas = []
    for (rho, B, mod), g in eq.groupby(["rho", "B", "modelo"]):
        ok = g[g.estado == "Optimal"]
        ref = ip[(ip.B == B) & (ip.rho == rho)].personas_salen.iloc[0]
        filas.append(dict(rho=rho, B=B, modelo=mod, factible=f"{len(ok)}/{len(g)}",
                          salen=q(ok.personas_salen), pct_info_perfecta=q(ok.personas_salen / ref * 100),
                          inclusion_pesos=q(ok.inclusion_pesos), sev_red=q(ok.sev_reduccion * 100),
                          exclusion=q(ok.exclusion), ref_IP=f"{ref:,.0f}"))
    t2 = pd.DataFrame(filas)
    print(t2.to_string(index=False))
    t2.to_csv("out/resumen_equidad.csv", index=False)
    print("\nPareado equidad M4/M3 (rho = 0):")
    for B, g in eq[(eq.rho == 0) & (eq.estado == "Optimal")].groupby("B"):
        p = g.pivot_table(index="replica", columns="modelo", values=["personas_salen", "inclusion_pesos"])
        r = p["personas_salen"]["m4"] / p["personas_salen"]["m3"]
        print(f"  B={B:>5}: M4 saca mas en {(r > 1).mean():.0%}; razon mediana {r.median():.2f}; "
              f"inclusion {p['inclusion_pesos']['m3'].median():.0%} -> {p['inclusion_pesos']['m4'].median():.0%}")


if __name__ == "__main__":
    main()
