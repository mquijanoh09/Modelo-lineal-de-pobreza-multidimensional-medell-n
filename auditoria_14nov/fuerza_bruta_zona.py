# -*- coding: utf-8 -*-
"""Auditoría 14-nov. Fuerza bruta en instancias pequeñas para lo NUEVO del 12-nov:
(1) costo mínimo con meta de M0 en cada zona; (2) piso máximo garantizable r_max con presupuesto B.
Agrupación mixta (un indicador por zona y otro por clúster, como el M4)."""
import itertools
import numpy as np
import m34_barrido_metas_v2 as BV, m34_corridas_costos_reales as CC, m34_datos as D, m34_mecanismo as X, m34_equidad as E, m34_clusters as CL
import m34_rmax_12nov as RM
CC.FUENTE = "comun"; CC._preparar_barrido("data/DANE/DEPARTAMENTAL"); g = BV.G_
M, w, persT, zonaT, HS, HW = g["M"], g["w"], g["b"]["pers"], g["zona"], g["HS"], g["HW"]
V, K = g["var"]["comun"]; fijos = g["fijos"]; pobreT = g["b"]["pobre0"]
etq, _ = CL.clusters(g["hog"], "data/DANE/DEPARTAMENTAL")
rng = np.random.default_rng(20261114)
casos = ok1 = ok2 = salt = 0
while casos < 40:
    idx = np.r_[rng.choice(np.where(pobreT == 1)[0], 27, replace=False), rng.choice(np.where(pobreT == 0)[0], 33, replace=False)]
    Ms, Vs, Ks, ps, zs = M[idx], V[idx], K[idx], persT[idx], zonaT[idx]
    s0 = np.round(Ms @ w, 2); pobre0 = (s0 >= 1 / 3).astype(int)
    if min((pobre0[zs == d]).sum() for d in np.unique(zonaT)) < 3 or len(np.unique(zs)) < 3: continue
    cand = np.where((Ms[pobre0 == 1] * ~fijos[idx][pobre0 == 1]).sum(0) >= 3)[0]
    cand = cand[cand != D.IND.index("rezago_escolar")]
    js = rng.choice(cand, 2, replace=False)
    excl = tuple(j for j in range(15) if j not in js)
    G = np.repeat(zs[:, None], 15, 1).astype(object)
    G[:, js[1]] = np.array([f"T{e}" for e in etq[idx]], dtype=object)       # segundo indicador por clúster
    R = rng.random(Ms.shape)
    info = X.enumerar_cortes(Ms, R, Vs, Ks, G, excluir=excl, pobre0=pobre0, fijos=fijos[idx])
    claves = list(info); tam = int(np.prod([len(info[k]["F"]) for k in claves]))
    if tam > 200_000 or tam < 30: salt += 1; continue
    meta = float(rng.choice([0.03, 0.05, 0.10, 0.20]))
    todo = sum(info[k]["cumK"][-1] for k in claves); B = float(rng.choice([0.15, 0.3, 0.5])) * todo
    mejor = np.inf; mejor_t = 0.0
    Pd = {d: ps[(pobre0 == 1) & (zs == d)].sum() for d in np.unique(zs)}
    rhs = {d: (1 - meta) * (ps * s0 * pobre0)[zs == d].sum() for d in Pd}
    for combo in itertools.product(*[info[k]["F"] for k in claves]):
        cub = np.zeros_like(Ms); costo = 0.0
        for k, c in zip(claves, combo):
            cub[info[k]["orden"][:c], k[0]] = 1; costo += info[k]["cumK"][c]
        s1 = np.round((Ms - cub) @ w, 2); pob1 = s1 >= 1 / 3
        if costo < mejor and all((ps * s1 * pob1)[zs == d].sum() <= rhs[d] + 1e-9 for d in Pd): mejor = costo
        if costo <= B + 1e-9:
            t = min(ps[(pobre0 == 1) & ~pob1 & (zs == d)].sum() / Pd[d] for d in Pd)
            mejor_t = max(mejor_t, t)
    M0 = float((ps * s0 * pobre0).sum() / ps.sum())
    res = X.resolver_paper(Ms, w, ps, pobre0, M0, info, meta, gap=1e-9, tmax=120, zona=zs)
    milp = res["obj"] if res["estado"] == "Optimal" else np.inf
    a = (np.isinf(mejor) and res["estado"] != "Optimal") or abs(milp - mejor) <= 1e-6 * max(1, mejor)
    dat = E.preparar(Ms, w, HS[idx], HW[idx], zs)
    t_milp, _ = RM.r_max(info, dat, B / 1e3)
    b = abs(t_milp - mejor_t) <= 2e-6
    casos += 1; ok1 += a; ok2 += b
    print(f"caso {casos:2d}: {tam:6d} comb., meta {meta:.0%} | costo FB {mejor:.4f} MILP {milp:.4f} {'OK' if a else 'DIF'} | r_max FB {mejor_t:.6f} MILP {t_milp:.6f} {'OK' if b else 'DIF'}", flush=True)
print(f"\ncosto con meta por zona: {ok1}/{casos} | r_max: {ok2}/{casos} (saltadas por tamaño: {salt})")
