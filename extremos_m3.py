# -*- coding: utf-8 -*-
"""
extremos_m3.py — Extremos de la frontera del Modelo 3 de equidad para un B dado
(diagnostico; se va a convertir en funciones de modelo3_equidad.py):
  rho_max = minima severidad alcanzable con B, sin exigir salidas
  r_max   = maximin de la fraccion de pobres que sale en cada zona
Con B = $500 mm y costos u = 1 dio rho_max = 40,7 % y r_max = 59,8 %.
"""
import importlib.util, time, pulp, numpy as np, sys
import cortes, costos_provisionales as cp, modelo3_equidad as me
spec = importlib.util.spec_from_file_location("m3", "05_modelo3.py"); m3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(m3)
m3.N_POR_CELDA=None; hog=m3.cargar(); R=m3.sortear_R(hog,0)
dat=me.preparar(hog,m3.IND,m3.W); V,K,el=cp.pesos_u1(hog,m3.IND)
info=cortes.enumerar_cortes(dat["M"],R,V,K,dat["zona"],elig=el,eps=m3.EPS)
B=500e9
# extremo 1: minima severidad alcanzable con B (sin exigir salidas)
m,z,y,q=me.construir(info,dat,B,etapa=2,H_star=0.0)
m.solve(pulp.HiGHS(msg=False,timeLimit=60,gapRel=1e-4))
print("min sev:",pulp.LpStatus[m.status],"rho_max =",f"{1-pulp.value(m.objective)/dat['Sev0']:.1%}")
# extremo 2: r_max por zona = max t s.a. salidas_d >= t*Pobres_d (maximin)
m=pulp.LpProblem("rmax",pulp.LpMaximize); z=cortes.variables_z(info); cortes.restricciones_corte_unico(m,info,z)
N,Kx=cortes.expresiones_lineales(info,z); t=pulp.LpVariable("t",0,1)
y={i:pulp.LpVariable(f"y_{i}",cat="Binary") for i in dat["pobres"]}
m+=pulp.lpSum(Kx.values())<=B
for i in dat["pobres"]:
    s=pulp.lpSum(dat["w"][jj]*N[(i,jj)] for jj in range(15) if (i,jj) in N)
    m+= s<=0.33+(dat["s0"][i]-0.33)*(1-y[i])
for d in dat["zonas"]:
    m+= pulp.lpSum(dat["p"][i]*y[i] for i in dat["pobres"] if dat["zona"][i]==d) >= t*dat["Pobres_d"][d]
m+=t; m.solve(pulp.HiGHS(msg=False,timeLimit=80,gapRel=1e-4))
print("r_max:",pulp.LpStatus[m.status],f"{t.value():.1%}")
