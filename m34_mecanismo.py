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


def info_highs(m):
    """(estado del modelo segun HiGHS, mip_gap). Auditoria 4-nov, hallazgo 9: PuLP reporta
    "Optimal" aunque HiGHS pare por tiempo con una solucion factible; esto lo distingue."""
    try:
        h = m.solverModel
        return h.modelStatusToString(h.getModelStatus()), float(h.getInfo().mip_gap)
    except Exception:
        return None, None


def estado_real(m, estado_pulp):
    """Baja el "Optimal" de PuLP a "NoOptimo:<motivo>" si HiGHS no certifico optimalidad."""
    st, gap = info_highs(m)
    if estado_pulp == "Optimal" and st is not None and st != "Optimal":
        estado_pulp = f"NoOptimo:{st}"
    return estado_pulp, st, gap


def enumerar_cortes(M, R, V, K, grupo, eps=EPS, excluir=(), pobre0=None):
    """Para cada (j, g) con privados: orden por R y cortes auto-consistentes.

    R_(c) <= p(c) <= R_(c+1) - eps,  p(c) = cumV(c) / Den_jg
    (version vectorizada de cortes.enumerar_cortes; mismo resultado).

    excluir: indices de indicadores NO intervenibles (no llevan variable; la privacion
             queda fija). Caso base 3-nov: rezago (decision de Martin del 2-nov: ningun
             nino sale del rezago en un año; elig = 0 equivale a excluirlo, porque pagar
             sin curar nunca es optimo).
    pobre0: si se pasa, guarda cumNP = costo acumulado en hogares NO pobres (desempate).
    """
    n, J = M.shape
    info = {}
    for jj in range(J):
        if jj in excluir:
            continue
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
            # Auditoria 4-nov (hallazgo 2): con Den = 0 la cobertura es 0/0, F queda vacio y el
            # MILP es infactible sin ningun error visible. Se corta aqui.
            assert Den > 0, f"Den = 0 en el par (indicador {jj}, grupo {g}): cobertura V nula en sus privados"
            m = orden.size
            p = cumV / Den
            c = np.arange(m + 1)
            ok_abajo = np.ones(m + 1, bool)
            ok_abajo[1:] = Rs <= p[1:]
            ok_arriba = np.ones(m + 1, bool)
            ok_arriba[:-1] = p[:-1] <= Rs - eps
            F = c[ok_abajo & ok_arriba].tolist()
            info[(jj, g)] = dict(orden=orden, Den=Den, cumV=cumV, cumK=cumK, F=F, n=m)
            if pobre0 is not None:
                info[(jj, g)]["cumNP"] = np.concatenate(
                    [[0.0], np.cumsum(K[orden, jj] * (1 - pobre0[orden]))])
    return info


def resolver_paper(M, w, pers, pobre0, M0, info, mpi_r, solver="highs", gap=1e-6, tmax=300,
                   desempate=False, tol_lex=1e-6):
    """min sum Costo_jg  s.a.  corte unico, censura AF (Big-M por hogar), meta de M0.

    Big-M de R4/R5 = pers_i = HS_i*HW_i (indexado por hogar, NUNCA global).
    C_i >= 0 obligatorio: si C es libre la meta se cumple trivialmente.

    desempate=True (Trampa 13, optimos alternos): segunda etapa lexicografica
        min  sum cumNP(c) z      (costo en hogares NO pobres = error de inclusion)
        s.a. costo <= E* (1 + tol_lex)
    Requiere info con cumNP (enumerar_cortes(..., pobre0=pobre0)). Interpretacion: entre
    todas las politicas igual de baratas, el Estado escoge la que menos se filtra a no
    pobres. Sin esto, el error de inclusion reportado depende del solver.
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
        # s_i = sum_j w_j M_ij - sum_{j intervenible} w_j cur_ij. Las privaciones NO
        # intervenibles (excluir) quedan como constante: si solo se sumaran los pares con
        # variable, excluir un indicador "curaria" gratis su peso (bug detectado el 3-nov:
        # M4 cumplia metas de 5-10 % con costo 0).
        s = float(w @ M[i]) - pulp.lpSum(w[jj] * cur[(i, jj)] for jj in range(J) if (i, jj) in cur)
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
    st_h, gap_h = None, None
    if solver == "highs":
        estado, st_h, gap_h = estado_real(m, estado)
    obj1 = pulp.value(m.objective)
    if desempate and estado == "Optimal":
        costo = pulp.lpSum(v["cumK"][c] * z[(jj, g, c)] for (jj, g), v in info.items() for c in v["F"])
        m += costo <= obj1 * (1 + tol_lex) + 1e-9, "LEX_costo"
        m.setObjective(pulp.lpSum(v["cumNP"][c] * z[(jj, g, c)]
                                  for (jj, g), v in info.items() for c in v["F"]))
        m.solve(sv)
        estado = pulp.LpStatus[m.status]
        if estado != "Optimal" and solver == "highs":
            # Falso infactible del presolve de HiGHS (visto el 3-nov en 12 de 2.400 corridas:
            # la solucion de la etapa 1 cumple "costo <= E*" por construccion). Reintento
            # sin presolve, que si encuentra el optimo.
            m.solve(pulp.HiGHS(msg=False, gapRel=gap, timeLimit=tmax, presolve="off"))
            estado = pulp.LpStatus[m.status]
        if solver == "highs":
            estado, st_h, gap_h = estado_real(m, estado)
        dt = time.time() - t0
    corte = {}
    if estado == "Optimal":
        for (jj, g), v in info.items():
            corte[(jj, g)] = next(c for c in v["F"] if round(z[(jj, g, c)].value()) == 1)
    obj = sum(info[k]["cumK"][c] for k, c in corte.items()) if corte else obj1
    return dict(estado=estado, obj=obj, obj_etapa1=obj1, segundos=dt, corte=corte,
                n_bin=len(z) + len(b1), n_cortes=len(z), estado_highs=st_h, gap=gap_h)


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
    # error de inclusion: fraccion del esfuerzo (personas-privacion) en hogares NO pobres.
    # Personas expandidas HS*HW (auditoria 3-nov h2 / 4-nov h12); antes era HS sin expandir.
    esf_h = (pers[:, None] * cub).sum(1)
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
