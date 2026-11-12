# -*- coding: utf-8 -*-
"""
m34_auditoria_12nov.py — Verificación INDEPENDIENTE de soluciones de M3/M4 (auditoría del 12-nov).

Del modelo solo se toma la matriz `cub` (qué pares (i, j) se curaron). Todo lo demás se recalcula desde
los datos crudos sin usar `info`, `cumK`, `b1` ni `C`:
  V1  regla del sorteo: dentro de cada par (j, g), p = sum V(curados) / sum V(privados) y
      curado <=> R <= p - (tolerancia de empate eps), hogar por hogar (no se supone el prefijo)
  V2  solo se curan pares privados, intervenibles (ni rezago ni pares fijos)
  V3  M0 final con Alkire-Foster escrito aparte (puntaje redondeado a 0,01, censura en 1/3)
      y meta M0_final <= M0_0 (1 - r) (+1e-9)
  V4  costo = sum K de los curados = objetivo reportado; y = costo de la fila congelada del 10-nov
Uso: python3 m34_auditoria_12nov.py <n_replicas> <salida.csv>
"""
import sys
import time

import numpy as np
import pandas as pd

import m34_barrido_metas_v2 as BV
import m34_clusters as CL
import m34_corridas_costos_reales as CC
import m34_datos as D
import m34_mecanismo as X
from m34_montecarlo import matriz_grupo
from m34_placebo import etiquetas_placebo

RAIZ = "data/DANE/DEPARTAMENTAL"
METAS = [0.02, 0.10, 0.20, 0.30]


def m0_af(N, w, pers):
    """M0 de Alkire-Foster escrito de cero: puntaje en la grilla de 0,01, pobre si >= 1/3."""
    s = np.round(N @ w, 2)
    pobre = s >= 1 / 3
    return float((pers * s * pobre).sum() / pers.sum())


def verificar(cub, R, M, V, K, G, w, pers, M0_0, meta, fijos, rezago, obj, eps=D.EPS):
    fallas = []
    J = M.shape[1]
    # V2
    if (cub > M).any():
        fallas.append("cura un par sin privación")
    if cub[:, rezago].any():
        fallas.append("cura rezago (no intervenible)")
    if fijos is not None and (cub.astype(bool) & fijos).any():
        fallas.append("cura un par fijo")
    # V1: regla R <= p hogar por hogar
    peor = 0.0
    for j in range(J):
        if j == rezago:
            continue
        for g in np.unique(G[:, j]):
            priv = (G[:, j] == g) & (M[:, j] == 1)
            if fijos is not None:
                priv &= ~fijos[:, j]
            if not priv.any():
                continue
            den = V[priv, j].sum()
            p = V[priv & (cub[:, j] == 1), j].sum() / den
            cur = cub[priv, j] == 1
            r = R[priv, j]
            # curado => R <= p ; no curado => p <= R - eps
            v1 = np.maximum(r[cur] - p, 0).max() if cur.any() else 0.0
            v2 = np.maximum(p - (r[~cur] - eps), 0).max() if (~cur).any() else 0.0
            peor = max(peor, v1, v2)
    if peor > 1e-9:
        fallas.append(f"regla del sorteo violada ({peor:.2e})")
    # V3
    N1 = M - cub
    m0f = m0_af(N1, w, pers)
    if m0f > M0_0 * (1 - meta) + 1e-9:
        fallas.append(f"meta incumplida: M0 {m0f:.6f} > {M0_0 * (1 - meta):.6f}")
    # V4
    costo = float((K * cub).sum())
    if abs(costo - obj) > 1e-6 * max(1.0, abs(obj)):
        fallas.append(f"costo {costo} != objetivo {obj}")
    return fallas, peor, m0f, costo


def main():
    nrep, salida = int(sys.argv[1]), sys.argv[2]
    CC.FUENTE = "comun"
    CC._preparar_barrido(RAIZ)
    g = BV.G_
    M, w, pers = g["M"], g["w"], g["b"]["pers"]
    V, K = g["var"]["comun"]
    fijos = g.get("fijos")
    rezago = D.IND.index("rezago_escolar")
    etq, _ = CL.clusters(g["hog"], RAIZ)
    congelado = pd.read_csv("resultados/m34/barrido_comun_crudo_10nov.csv")
    filas = []
    for rep in range(nrep):
        R = D.sortear_R(g["hog"], rep)
        grupos = {"m3": g["G"]["m3"], "m4": matriz_grupo(g["hog"], "m4", etq),
                  "m4p": matriz_grupo(g["hog"], "m4", etiquetas_placebo(etq, rep))}
        for mod, G in grupos.items():
            info = X.enumerar_cortes(M, R, V, K, G, excluir=(rezago,), pobre0=g["b"]["pobre0"], fijos=fijos)
            for meta in METAS:
                t0 = time.time()
                res = X.resolver_paper(M, w, pers, g["b"]["pobre0"], g["b"]["M0"], info, meta,
                                       solver="highs", gap=1e-6, tmax=180, desempate=True)
                assert res["estado"] == "Optimal", res["estado"]
                cub, _ = X.reconstruir(info, res["corte"], M)
                fallas, peor, m0f, costo = verificar(cub, R, M, V, K, G, w, pers, g["b"]["M0"], meta,
                                                    fijos, rezago, res["obj"])
                fila_c = congelado[(congelado.modelo == mod) & (congelado.replica == rep)
                                   & np.isclose(congelado.meta, meta)]
                c10 = float(fila_c.costo_pesos.iloc[0])
                # costo_pesos del CSV está en millones de $; K en pesos expandidos/1e6 (misma escala)
                repro = abs(costo - c10) <= 1e-6 * max(1.0, c10)
                filas.append(dict(modelo=mod, replica=rep, meta=meta, ok=not fallas and repro,
                                  fallas="; ".join(fallas) + ("" if repro else f"; no reproduce 10-nov ({costo} vs {c10})"),
                                  peor_regla=peor, M0_final=m0f, M0_meta=g["b"]["M0"] * (1 - meta),
                                  costo=costo, costo_10nov=c10, gap=res["gap"], seg=round(time.time() - t0, 2)))
                print(mod, rep, meta, "OK" if filas[-1]["ok"] else "FALLA " + filas[-1]["fallas"], flush=True)
    t = pd.DataFrame(filas)
    t.to_csv(salida, index=False)
    print(f"\n{t.ok.sum()}/{len(t)} soluciones verificadas | holgura mínima de la meta "
          f"{(t.M0_meta - t.M0_final).min():.2e} | peor violación de la regla {t.peor_regla.max():.1e}")


if __name__ == "__main__":
    main()


def equidad(nrep, salida, Bs=(2, 10, 50)):
    """Verificación independiente del objetivo de equidad (rho = 0): presupuesto, regla del sorteo,
    personas que salen recalculadas con AF propio == H* del solver == fila congelada del 10-nov."""
    import m34_equidad as E
    CC.FUENTE = "comun"
    CC._preparar_barrido(RAIZ)
    g = BV.G_
    M, w, pers = g["M"], g["w"], g["b"]["pers"]
    V, K = g["var"]["comun"]
    fijos, rezago = g.get("fijos"), D.IND.index("rezago_escolar")
    pobre0 = g["b"]["pobre0"]
    dat = E.preparar(M, w, g["HS"], g["HW"], g["zona"])
    etq, _ = CL.clusters(g["hog"], RAIZ)
    cong = pd.read_csv("resultados/m34/equidad_comun_crudo_10nov.csv")
    filas = []
    for rep in range(nrep):
        R = D.sortear_R(g["hog"], rep)
        grupos = {"m3": g["G"]["m3"], "m4": matriz_grupo(g["hog"], "m4", etq),
                  "m4p": matriz_grupo(g["hog"], "m4", etiquetas_placebo(etq, rep))}
        for mod, G in grupos.items():
            info = X.enumerar_cortes(M, R, V, K, G, excluir=(rezago,), pobre0=pobre0, fijos=fijos)
            for B in Bs:
                s = E.resolver(info, dat, B=B * 1e3, rho=0.0, tiempo=180)
                assert s["estado"] == "Optimal", s["estado"]
                cub, _ = X.reconstruir(info, s["corte"], M)
                fallas, peor, _, costo = verificar(cub, R, M, V, K, G, w, pers, 1.0, 0.0, fijos, rezago,
                                                   float((K * cub).sum()))
                if costo > B * 1e3 * (1 + 1e-9):
                    fallas.append(f"presupuesto excedido {costo} > {B * 1e3}")
                s1 = np.round((M - cub) @ w, 2)
                salen = float((pers * ((pobre0 == 1) & (s1 < 1 / 3))).sum())
                if not (s["H_star"] * (1 - 1e-6) <= salen <= s["H_star"] * (1 + 1e-6)):
                    fallas.append(f"salen {salen} != H* {s['H_star']}")
                fc = cong[(cong.modelo == mod) & (cong.replica == rep) & (cong.B == B) & (cong.rho == 0)]
                c10 = float(fc.personas_salen.iloc[0])
                if abs(salen - c10) > 1e-6 * c10:
                    fallas.append(f"no reproduce 10-nov ({salen} vs {c10})")
                filas.append(dict(modelo=mod, replica=rep, B=B, ok=not fallas, fallas="; ".join(fallas),
                                  costo=costo, salen=salen, H_star=s["H_star"], salen_10nov=c10, peor_regla=peor))
                print(mod, rep, B, "OK" if not fallas else "FALLA " + "; ".join(fallas), flush=True)
    t = pd.DataFrame(filas)
    t.to_csv(salida, index=False)
    print(f"\n{t.ok.sum()}/{len(t)} soluciones de equidad verificadas")


if __name__ == "__main__" and len(sys.argv) > 3 and sys.argv[3] == "equidad":
    pass
