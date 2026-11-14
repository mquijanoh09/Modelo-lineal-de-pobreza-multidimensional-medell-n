# -*- coding: utf-8 -*-
"""Auditoría 14-nov. r_max: (a) valores de información perfecta (un hogar por celda), que en m34_tablas_12nov.py
están escritos a mano; (b) prueba de frontera: con r = r_max - 1e-5 la cobertura es factible y con r_max + 1e-4 no;
(c) verificación independiente del piso logrado a partir de los cortes."""
import numpy as np, pandas as pd, pulp
import m34_corridas_costos_reales as CC, m34_datos as D, m34_equidad as E, m34_mecanismo as X, m34_clusters as CL
import m34_rmax_12nov as RM
from m34_montecarlo import matriz_grupo
from m34_placebo import etiquetas_placebo
rr = pd.read_csv("resultados/m34/r_rho_comparacion_12nov.csv").set_index("B")
CC.FUENTE = "comun"; CC._preparar_equidad("data/DANE/DEPARTAMENTAL", list(rr.index)); g = CC.EQ; dat = g["dat"]
etq, _ = CL.clusters(g["hog"], "data/DANE/DEPARTAMENTAL")
jrez = D.IND.index("rezago_escolar")
# (a) información perfecta
Gip = np.repeat(np.arange(len(g["hog"]))[:, None], 15, 1)
info = X.enumerar_cortes(g["M"], D.sortear_R(g["hog"], 0), g["V"], g["K"], Gip, excluir=(jrez,), pobre0=dat["pobre0"], fijos=g["fijos"])
escrito = {2: .0585, 5: .1071, 10: .1649, 25: .2844, 50: .3913, 100: .5362}
for B in rr.index:
    t, gap = RM.r_max(info, dat, B, tiempo=600)
    print(f"IP  B={B:g}: r_max = {t:.6f} (gap {gap:.1e}) | escrito a mano {escrito[int(B)]} | r_B = {rr.loc[B,'r_B']:.6f} | r_max >= r_B: {t >= rr.loc[B,'r_B']}", flush=True)
# (b) y (c) frontera en una muestra
guard = pd.read_csv("resultados/m34/rmax_12nov.csv").set_index(["modelo", "replica", "B"]).r_max
def factible(info, B, r):
    for op in [{}, {"presolve": "off"}]:
        m, z = E.construir(info, dat, B * 1e3, r=r, rho=0.0, etapa=1)
        m.solve(pulp.HiGHS(msg=False, timeLimit=180, gapRel=1e-6, **op))
        est, _, _ = X.estado_real(m, pulp.LpStatus[m.status])
        if est == "Optimal":
            corte = {k: next(c for c in v["F"] if round(z[(k[0], k[1], c)].value()) == 1) for k, v in info.items()}
            return True, corte
    return False, None
malas = 0; n = 0
for rep in [7, 31, 66, 92]:
    R = D.sortear_R(g["hog"], rep)
    for mod in ["m3", "m4", "m4p"]:
        G = g["G"][mod] if mod != "m4p" else matriz_grupo(g["hog"], "m4", etiquetas_placebo(etq, rep))
        info = X.enumerar_cortes(g["M"], R, g["V"], g["K"], G, excluir=(jrez,), pobre0=dat["pobre0"], fijos=g["fijos"])
        for B in rr.index:
            t = guard[(mod, rep, B)]; n += 1
            ok_abajo, corte = factible(info, B, max(t - 1e-5, 0)) if t > 1e-5 else (True, None)
            ok_arriba, _ = factible(info, B, t + 1e-4)
            piso = np.nan
            if corte is not None:   # piso logrado, recalculado desde los cortes
                cub, N1 = X.reconstruir(info, corte, g["M"]); s1 = np.round(N1 @ g["w"], 2)
                sale = (dat["pobre0"] == 1) & (s1 < 1 / 3); p = dat["p"]; z = g["celda"]
                piso = min((p[sale & (z == d)].sum() / p[(dat["pobre0"] == 1) & (z == d)].sum()) for d in np.unique(z))
                costo = (g["K"] * cub).sum()
                assert costo <= B * 1e3 * (1 + 1e-9)
            mal = (not ok_abajo) or ok_arriba or (corte is not None and piso < t - 1e-5 - 1e-9)
            malas += mal
            if mal: print("FALLA", mod, rep, B, t, ok_abajo, ok_arriba, piso, flush=True)
    print("réplica", rep, "lista", flush=True)
print(f"frontera de r_max: {n - malas}/{n} casos correctos")
