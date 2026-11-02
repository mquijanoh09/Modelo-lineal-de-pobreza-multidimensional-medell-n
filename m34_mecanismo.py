# -*- coding: utf-8 -*-
"""
m34_mecanismo.py — Mecanismo de cortes de prefijo y el MILP del paper (min esfuerzo
s.a. meta de M0), comun a los Modelos 3 y 4.

Unica diferencia entre M3 y M4: la columna de agrupacion de cada indicador.
    Modelo 3: g(i, j) = zona P3 del hogar                  para todo j
    Modelo 4: g(i, j) = zona P3       si j en V (publicos)
              g(i, j) = cluster k-means si j en U (privados)
Por eso `grupo` es una MATRIZ (n_hogares x n_indicadores), no un vector.

La propiedad de prefijo vale dentro de cualquier grupo: el hogar se cura <=> R_ij <= p_jg
y p_jg es UN numero para todo el grupo. Solo usa el orden de los R.
"""
import time

import numpy as np
import pulp

from m34_datos import EPS, K_GRID


def enumerar_cortes(M, R, V, K, grupo, eps=EPS):
    """Para cada (j, g) con privados: orden por R y cortes auto-consistentes.

    R_(c) <= p(c) <= R_(c+1) - eps,  p(c) = cumV(c) / Den_jg
    (version vectorizada de cortes.enumerar_cortes; mismo resultado).
    """
    n, J = M.shape
    info = {}
    for jj in range(J):
        col = grupo[:, jj]
        for g in sorted(np.unique(col)):
            idx = np.where((col == g) & (M[:, jj] == 1))[0]
            if idx.size == 0:
                continue
            orden = idx[np.argsort(R[idx, jj], kind="stable")]
            Rs = R[orden, jj]
            cumV = np.concatenate([[0.0], np.cumsum(V[orden, jj])])
            cumK = np.concatenate([[0.0], np.cumsum(K[orden, jj])])
            Den = cumV[-1]
            m = orden.size
            p = cumV / Den
            c = np.arange(m + 1)
            ok_abajo = np.ones(m + 1, bool)
            ok_abajo[1:] = Rs <= p[1:]
            ok_arriba = np.ones(m + 1, bool)
            ok_arriba[:-1] = p[:-1] <= Rs - eps
            F = c[ok_abajo & ok_arriba].tolist()
            info[(jj, g)] = dict(orden=orden, Den=Den, cumV=cumV, cumK=cumK, F=F, n=m)
    return info


def resolver_paper(M, w, pers, pobre0, M0, info, mpi_r, solver="highs", gap=1e-6, tmax=300):
    """min sum Costo_jg  s.a.  corte unico, censura AF (Big-M por hogar), meta de M0.

    Big-M de R4/R5 = pers_i = HS_i*HW_i (indexado por hogar, NUNCA global).
    C_i >= 0 obligatorio: si C es libre la meta se cumple trivialmente.
    """
    J = M.shape[1]
    pobres = np.where(pobre0 == 1)[0]
    m = pulp.LpProblem("M34_paper", pulp.LpMinimize)
    z = {(jj, g, c): pulp.LpVariable(f"z_{jj}_{str(g).replace(' ', '')}_{c}", cat="Binary")
         for (jj, g), v in info.items() for c in v["F"]}
    for (jj, g), v in info.items():
        m += pulp.lpSum(z[(jj, g, c)] for c in v["F"]) == 1
    # N_ij = 1 - sum_{c >= rank} z  -> se usa sum_{c>=k} z como "curado"
    cur = {}
    for (jj, g), v in info.items():
        for k, i in enumerate(v["orden"], start=1):
            if pobre0[i]:
                cur[(i, jj)] = pulp.lpSum(z[(jj, g, c)] for c in v["F"] if c >= k)
    b1 = {i: pulp.LpVariable(f"b1_{i}", cat="Binary") for i in pobres}
    C = {i: pulp.LpVariable(f"C_{i}", lowBound=0) for i in pobres}
    for i in pobres:
        s = pulp.lpSum(w[jj] * (1 - cur[(i, jj)]) for jj in range(J) if (i, jj) in cur)
        Mi = pers[i]
        m += C[i] + Mi * b1[i] >= Mi * s
        m += C[i] - Mi * b1[i] <= Mi * s
        m += s - (1 - b1[i]) <= K_GRID
    m += pulp.lpSum(C.values()) <= M0 * (1 - mpi_r) * pers.sum()
    m += pulp.lpSum(v["cumK"][c] * z[(jj, g, c)] for (jj, g), v in info.items() for c in v["F"])
    if solver == "highs":
        sv = pulp.HiGHS(msg=False, gapRel=gap, timeLimit=tmax)
    else:
        sv = pulp.PULP_CBC_CMD(msg=0, gapRel=gap, timeLimit=tmax)
    t0 = time.time()
    m.solve(sv)
    dt = time.time() - t0
    estado = pulp.LpStatus[m.status]
    corte = {}
    if estado == "Optimal":
        for (jj, g), v in info.items():
            corte[(jj, g)] = next(c for c in v["F"] if round(z[(jj, g, c)].value()) == 1)
    return dict(estado=estado, obj=pulp.value(m.objective), segundos=dt, corte=corte,
                n_bin=len(z) + len(b1), n_cortes=len(z))


def reconstruir(info, corte, M):
    cub = np.zeros_like(M)
    for (jj, g), v in info.items():
        c = corte[(jj, g)]
        cub[v["orden"][:c], jj] = 1
    return cub, M - cub          # cubiertos (todos elegibles en el caso base), N final


def metricas(cub, N1, M, w, HS, HW, pobre0, celda, Kpesos=None):
    """Todo se recalcula desde los cortes elegidos: no se confia en b1 ni en C."""
    pers = HS * HW
    score1 = np.round(N1 @ w, 2)
    pobre1 = (score1 >= 1 / 3).astype(int)
    pob = pers.sum()
    out = dict(H1=(pers * pobre1).sum() / pob, M01=(pers * pobre1 * score1).sum() / pob,
               privaciones_resueltas=int(cub.sum()),
               hogares_que_salen=int(((pobre0 == 1) & (pobre1 == 0)).sum()))
    # error de inclusion: fraccion del esfuerzo (personas-privacion) en hogares NO pobres
    esf_h = (HS[:, None] * cub).sum(1)
    out["inclusion_personas"] = esf_h[pobre0 == 0].sum() / esf_h.sum() if esf_h.sum() else np.nan
    if Kpesos is not None:
        gasto_h = (Kpesos * cub).sum(1)
        out["costo_pesos"] = gasto_h.sum()
        out["inclusion_pesos"] = gasto_h[pobre0 == 0].sum() / gasto_h.sum() if gasto_h.sum() else np.nan
    # error de exclusion: personas pobres que no reciben NINGUNA intervencion
    tocado = cub.sum(1) > 0
    pp = pers * pobre0
    out["exclusion"] = pp[~tocado].sum() / pp.sum()
    # entre los hogares beneficiados, que fraccion era pobre (precision de la focalizacion)
    out["benef_hogares"] = int(tocado.sum())
    out["benef_pobres"] = int((tocado & (pobre0 == 1)).sum())
    for d in np.unique(celda):
        s = celda == d
        out[f"H1_{d}"] = (pers[s] * pobre1[s]).sum() / pers[s].sum()
    return out
