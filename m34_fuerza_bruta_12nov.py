# -*- coding: utf-8 -*-
"""Optimalidad del MILP por cortes contra enumeración exhaustiva en instancias pequeñas (auditoría 12-nov).
Submuestras aleatorias de hogares; solo 2 indicadores intervenibles (el resto queda fijo en el puntaje);
costos y cobertura de la tabla común final. Compara el costo mínimo del MILP con el de la fuerza bruta."""
import itertools
import numpy as np
import m34_barrido_metas_v2 as BV
import m34_corridas_costos_reales as CC
import m34_datos as D
import m34_mecanismo as X

CC.FUENTE = "comun"
CC._preparar_barrido("data/DANE/DEPARTAMENTAL")
g = BV.G_
M, w, persT = g["M"], g["w"], g["b"]["pers"]
V, K = g["var"]["comun"]
fijos = g.get("fijos")
rng = np.random.default_rng(20261112)
pobreT = g["b"]["pobre0"]
casos, iguales, saltados = 0, 0, 0
while casos < 40:
    pob = rng.choice(np.where(pobreT == 1)[0], 25, replace=False)
    nop = rng.choice(np.where(pobreT == 0)[0], 35, replace=False)
    idx = np.r_[pob, nop]
    Ms, Vs, Ks, ps = M[idx], V[idx], K[idx], persT[idx]
    pobre0 = (np.round(Ms @ w, 2) >= 1 / 3).astype(int)
    M0 = float((ps * np.round(Ms @ w, 2) * pobre0).sum() / ps.sum())
    js = rng.choice(np.where(Ms[pobre0 == 1].sum(0) >= 3)[0], 2, replace=False)
    excl = tuple(j for j in range(Ms.shape[1]) if j not in js)
    G = g["G"]["m3"][idx]
    R = rng.random(Ms.shape)
    info = X.enumerar_cortes(Ms, R, Vs, Ks, G, excluir=excl, pobre0=pobre0,
                             fijos=None if fijos is None else fijos[idx])
    claves = list(info)
    tam = np.prod([len(info[k]["F"]) for k in claves])
    if tam > 300_000 or tam < 20:
        saltados += 1
        continue
    meta = float(rng.choice([0.05, 0.10, 0.20, 0.30]))
    # fuerza bruta
    mejor = np.inf
    for combo in itertools.product(*[info[k]["F"] for k in claves]):
        cub = np.zeros_like(Ms)
        costo = 0.0
        for (jj, gg), c in zip(claves, combo):
            cub[info[(jj, gg)]["orden"][:c], jj] = 1
            costo += info[(jj, gg)]["cumK"][c]
        if costo >= mejor:
            continue
        s1 = np.round((Ms - cub) @ w, 2)
        if (ps * s1 * (s1 >= 1 / 3)).sum() / ps.sum() <= M0 * (1 - meta) + 1e-12:
            mejor = costo
    res = X.resolver_paper(Ms, w, ps, pobre0, M0, info, meta, solver="highs", gap=1e-9, tmax=120)
    milp = res["obj"] if res["estado"] == "Optimal" else np.inf
    ok = (np.isinf(mejor) and res["estado"] != "Optimal") or abs(milp - mejor) <= 1e-6 * max(1, mejor)
    casos += 1
    iguales += ok
    print(f"caso {casos:2d}: {tam:7d} combinaciones, meta {meta:.0%} | fuerza bruta {mejor:.4f} | MILP {milp:.4f} | {'OK' if ok else 'DIFERENTE'}", flush=True)
print(f"\n{iguales}/{casos} instancias con el mismo óptimo (saltadas por tamaño: {saltados})")
