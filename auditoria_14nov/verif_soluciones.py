# -*- coding: utf-8 -*-
"""Auditoría 14-nov. Verificador independiente del criterio de costo con meta por zona.
Re-resuelve una muestra, y comprueba cada solución SIN usar el mecanismo de cortes:
regla directa R_ij <= p_jg, metas de M0 por zona censuradas, costo, y lo compara con el CSV guardado."""
import sys, time
import numpy as np, pandas as pd
import m34_barrido_metas_v2 as BV, m34_corridas_costos_reales as CC, m34_datos as D, m34_mecanismo as X, m34_clusters as CL
from m34_montecarlo import matriz_grupo
from m34_placebo import etiquetas_placebo

reps = [int(x) for x in sys.argv[1].split(",")]; metas = [float(x) for x in sys.argv[2].split(",")]; salida = sys.argv[3]
CC.FUENTE = "comun"; CC._preparar_barrido("data/DANE/DEPARTAMENTAL"); g = BV.G_
etq, _ = CL.clusters(g["hog"], "data/DANE/DEPARTAMENTAL")
M, w, pers, pobre0, zona = g["M"], g["w"], g["b"]["pers"], g["b"]["pobre0"], g["zona"]
V, K = g["var"]["comun"]; fijos = g["fijos"]; jrez = D.IND.index("rezago_escolar")
ref = pd.read_csv("resultados/m34/costo_meta_zona_crudo_12nov.csv").set_index(["modelo", "replica", "meta"])
s0 = np.round(M @ w, 2)
# estructura de grupos (independiente): M3 todo zona; M4 zona en acueducto/alcantarillado, clúster en el resto
pub = [D.IND.index(j) for j in D.IND if j not in D.U_PRIVADOS]
print("indicadores públicos:", [D.IND[j] for j in pub], "| fijos:", int(fijos.sum()), "pares", flush=True)
filas = []
for rep in reps:
    R = D.sortear_R(g["hog"], rep)
    for mod in ["m3", "m4", "m4p"]:
        G = g["G"][mod] if mod != "m4p" else matriz_grupo(g["hog"], "m4", etiquetas_placebo(etq, rep))
        if mod == "m3": assert all((G[:, j] == zona).all() for j in range(15))
        else:
            assert all((G[:, j] == zona).all() for j in pub)
            tam = sorted(pd.Series(G[:, [j for j in range(15) if j not in pub][0]]).value_counts().tolist())
            assert tam == [456, 849, 1038, 1389], tam
        info = X.enumerar_cortes(M, R, V, K, G, excluir=(jrez,), pobre0=pobre0, fijos=fijos)
        for meta in metas:
            t0 = time.time()
            r1 = X.resolver_paper(M, w, pers, pobre0, g["b"]["M0"], info, meta, gap=1e-6, tmax=180, desempate=False, zona=zona)
            r2 = X.resolver_paper(M, w, pers, pobre0, g["b"]["M0"], info, meta, gap=1e-6, tmax=180, desempate=True, zona=zona)
            cub, _ = X.reconstruir(info, r2["corte"], M)
            # ---- verificación independiente ----
            viol_sorteo = 0; costo = 0.0
            for j in range(15):
                if j == jrez: assert cub[:, j].sum() == 0; continue
                for gg in np.unique(G[:, j]):
                    priv = (G[:, j] == gg) & (M[:, j] == 1) & ~fijos[:, j]
                    if not priv.any(): continue
                    cz = cub[:, j].astype(bool) & priv
                    p = V[cz, j].sum() / V[priv, j].sum()
                    viol_sorteo += int((R[cz, j] > p).sum()) + int((R[priv & ~cz, j] < p + D.EPS - 1e-15).sum())
                    costo += K[cz, j].sum()
            assert (cub[~((M == 1) & ~fijos)] == 0).all()            # no se cubre a quien no está privado ni a pares fijos
            s1 = np.round((M - cub) @ w, 2); pobre1 = s1 >= 1 / 3
            holg = []
            for d in np.unique(zona):
                z = zona == d
                lhs = (pers[z] * s1[z] * pobre1[z]).sum(); rhs = (1 - meta) * (pers[z] * s0[z] * (pobre0[z] == 1)).sum()
                holg.append((rhs - lhs) / rhs)
            fr = ref.loc[(mod, rep, round(meta, 2))]
            filas.append(dict(modelo=mod, replica=rep, meta=meta, viol_sorteo=viol_sorteo, holgura_min_zona=min(holg),
                              costo=costo, dif_csv=abs(costo - fr.objetivo) / fr.objetivo, dif_H1=abs((pers * pobre1).sum() / pers.sum() - fr.H1),
                              dif_M01=abs((pers * pobre1 * s1).sum() / pers.sum() - fr.M01),
                              gap_etapa1=r1["gap"], obj1=r1["obj"], exceso_lex=costo / r1["obj"] - 1, estado1=r1["estado"], estado2=r2["estado"],
                              segundos=round(time.time() - t0, 1)))
        pd.DataFrame(filas).to_csv(salida, index=False); print(time.strftime("%H:%M:%S"), rep, mod, flush=True)
t = pd.DataFrame(filas)
print(len(t), "soluciones | violaciones del sorteo:", t.viol_sorteo.sum(), "| holgura mínima de la meta por zona:", t.holgura_min_zona.min(),
      "| dif. máx con el CSV:", t.dif_csv.max(), "| dif H1/M01:", t.dif_H1.max(), t.dif_M01.max(),
      "| gap etapa 1 máx:", t.gap_etapa1.max(), "| exceso lex máx:", t.exceso_lex.max(), "| estados:", set(t.estado1) | set(t.estado2))
