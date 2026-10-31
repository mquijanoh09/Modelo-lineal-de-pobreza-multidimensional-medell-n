# -*- coding: utf-8 -*-
"""
correr_m3_equidad.py — Pruebas por capas del Modelo 3 de equidad (costos u = 1).

  capa 0  linea base: H0, Sev0 y pobres por zona deben coincidir con Martin
  capa 1  B = 0: nadie sale, severidad intacta
  capa 2  barrido de B con r = rho = 0 (curva B -> personas que salen)
  capa 3  un B con techo de severidad rho > 0 y equidad r > 0

Uso: python3 correr_m3_equidad.py capa0|capa1|capa2|capa3 [B en mil millones ...]
"""
import importlib.util
import sys

import numpy as np

import cortes
import costos_provisionales as cp
import modelo3_equidad as me

spec = importlib.util.spec_from_file_location("m3", "05_modelo3.py")
m3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m3)
m3.N_POR_CELDA = None

hog = m3.cargar()
R = m3.sortear_R(hog, m3.REPLICA)
dat = me.preparar(hog, m3.IND, m3.W)
V, K, elig = cp.pesos_u1(hog, m3.IND)
info = cortes.enumerar_cortes(dat["M"], R, V, K, dat["zona"], elig=elig, eps=m3.EPS)
capa = sys.argv[1] if len(sys.argv) > 1 else "capa0"
MM = 1e9

if capa == "capa0":
    p, pob = dat["p"], dat["pobres"]
    print(f"\n  hogares = {len(hog):,}, pobres = {len(pob)}, H0 = {p[pob].sum()/p.sum():.4%}"
          f"   (Martin: 523, 9,45 %)")
    print(f"  Sev0 = {dat['Sev0']:,.0f}   (Martin: ~117.908)")
    for d, v in dat["Pobres_d"].items():
        print(f"    pobres {d:<16} {v:12,.0f} personas")
    n_tang = sum(sum(1 for a in dat["A"][i] if a > 0) for i in pob)
    print(f"  tangentes (7) = {n_tang:,}   (Martin: 6.571)")
    n_c = sum(len(v["F"]) for v in info.values())
    tot = sum(v["cumK"][-1] for v in info.values())
    tot_p = sum((K[v["orden"], jj] * dat["pobre0"][v["orden"]]).sum() for (jj, g), v in info.items())
    print(f"  pares = {len(info)}, cortes factibles = {n_c:,} (con u = 1)")
    print(f"  cubrir TODO lo privado cuesta ${tot/MM:,.0f} mm, de eso ${tot_p/MM:,.0f} mm en pobres")

elif capa == "capa1":
    sol = me.resolver(info, dat, B=0.0)
    print(f"\n  B = 0 -> {sol['estado']}, salen = {sol['H_star']:.0f} personas ({sol['segundos']:.1f} s)")
    res, _ = me.metricas(info, dat, sol, K)
    me.imprimir(res)

elif capa == "capa2":
    for Bmm in [float(x) for x in sys.argv[2:]]:
        sol = me.resolver(info, dat, B=Bmm * MM)
        print(f"\n  B = ${Bmm:,.0f} mm -> {sol['estado']}  ({sol['segundos']:.1f} s)")
        if sol["estado"] == "Optimal":
            res, corte = me.metricas(info, dat, sol, K)
            me.imprimir(res)

elif capa == "capa3":
    Bmm, r, rho = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
    sol = me.resolver(info, dat, B=Bmm * MM, r=r, rho=rho)
    print(f"\n  B = ${Bmm:,.0f} mm, r = {r}, rho = {rho} -> {sol['estado']}  ({sol['segundos']:.1f} s)")
    if sol["estado"] == "Optimal":
        res, corte = me.metricas(info, dat, sol, K)
        me.imprimir(res)
        print("\n    cortes no nulos:")
        for (jj, g), c in sorted(corte.items(), key=lambda kv: -info[kv[0]]["cumK"][kv[1]]):
            if c > 0:
                v = info[(jj, g)]
                print(f"      {g:<16}{m3.IND[jj]:<26} {c:>4}/{v['n']:<4} p={v['cumV'][c]/v['Den']:.2f}"
                      f"  ${v['cumK'][c]/MM:8,.1f} mm")
