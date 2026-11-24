# -*- coding: utf-8 -*-
"""
m34_equidad.py — Modelos 3 y 4 con el objetivo de EQUIDAD del Modelo 1 (3-nov-2026).

Generaliza modelo3_equidad.py (que usa cortes.py con grupo = zona) al mecanismo de
m34_mecanismo, donde `grupo` es una matriz n x J. Asi el MISMO codigo sirve para:
    M3: grupo = zona P3 para todo j
    M4: grupo = zona para V = {acueducto, alcantarillado}, cluster para U
y la unica diferencia entre los dos es la informacion que el Estado usa para focalizar.

Formulacion (numeracion del Modelo 1 de Martin, CONTEXTO_DATOS.md §6)
  z[j,g,c] binaria, C1 sum_c z = 1                 (corte unico por par (j, g))
  cur_ij = sum_{c >= rank_ij} z[j,g,c]             (el hogar i queda cubierto en j)
  s_i    = sum_j w_j M_ij - sum_j w_j cur_ij       (puntaje sin censurar, i pobre)
  p_i    = HS_i * HW_i
  (1) sum cumK(c) z <= B                           presupuesto (incluye a los NO pobres)
  (2) s_i <= 0,33 + (s0_i - 0,33)(1 - y_i)         salida; bigM por hogar = s0_i - 0,33
  (4) sum_{i en d} p_i y_i >= r * Pobres_d^0       equidad por zona P3 (opcional)
  (7) q_i >= 2 a s_i - a^2, a en A_i               q_i = s_i^2 por tangentes (exacto en A_i)
  (8) sum p_i q_i <= (1 - rho) Sev_0               techo de severidad (opcional)
  Etapa 1: max sum p_i y_i     Etapa 2: min sum p_i q_i  s.a.  sum p_i y_i >= H*(1 - 1e-7)

Gaps de HiGHS: 1e-6 en la etapa 1 (personas) y 1e-4 en la etapa 2 (severidad), Trampa 11.
"""
import time

import numpy as np
import pulp

from m34_datos import K_GRID
from m34_mecanismo import estado_real


def valores_alcanzables(pesos_cent):
    sumas = {0}
    for p in pesos_cent:
        sumas |= {s + p for s in sumas}
    return sorted(s / 100 for s in sumas)


def preparar(M, w, HS, HW, celda):
    p = HS * HW
    s0 = np.round(M @ w, 2)
    pobre0 = (s0 >= 1 / 3).astype(int)
    pobres = np.where(pobre0 == 1)[0]
    wc = np.round(w * 100).astype(int)
    A = {i: valores_alcanzables(wc[M[i] == 1]) for i in pobres}
    zonas = sorted(np.unique(celda))
    return dict(M=M, w=w, p=p, s0=s0, pobre0=pobre0, pobres=pobres, A=A, zona=celda, zonas=zonas,
                Sev0=float((p[pobres] * s0[pobres] ** 2).sum()),
                Pobres_d={d: float(p[pobres][celda[pobres] == d].sum()) for d in zonas})


def construir(info, dat, B, r=0.0, rho=0.0, etapa=1, H_star=None):
    M, w, p, s0, zona, pobres = dat["M"], dat["w"], dat["p"], dat["s0"], dat["zona"], dat["pobres"]
    J = M.shape[1]
    m = pulp.LpProblem(f"M34_equidad_e{etapa}", pulp.LpMaximize if etapa == 1 else pulp.LpMinimize)
    z = {(jj, g, c): pulp.LpVariable(f"z_{jj}_{str(g).replace(' ', '')}_{c}", cat="Binary")
         for (jj, g), v in info.items() for c in v["F"]}
    for (jj, g), v in info.items():
        m += pulp.lpSum(z[(jj, g, c)] for c in v["F"]) == 1
    es_pobre = dat["pobre0"]
    cur = {}
    for (jj, g), v in info.items():
        for k, i in enumerate(v["orden"], start=1):
            if es_pobre[i]:
                cur[(i, jj)] = pulp.lpSum(z[(jj, g, c)] for c in v["F"] if c >= k)
    m += pulp.lpSum(v["cumK"][c] * z[(jj, g, c)] for (jj, g), v in info.items() for c in v["F"]) <= B, "P1"
    y = {i: pulp.LpVariable(f"y_{i}", cat="Binary") for i in pobres}
    q = {i: pulp.LpVariable(f"q_{i}", lowBound=0) for i in pobres}
    usar_q = rho > 0 or etapa == 2
    for i in pobres:
        s = float(w @ M[i]) - pulp.lpSum(w[jj] * cur[(i, jj)] for jj in range(J) if (i, jj) in cur)
        m += s <= K_GRID + (s0[i] - K_GRID) * (1 - y[i]), f"P2_{i}"
        if usar_q:
            for k, a in enumerate(dat["A"][i]):
                if a > 0:
                    m += q[i] >= 2 * a * s - a * a, f"P7_{i}_{k}"
    if r > 0:
        for d in dat["zonas"]:
            m += pulp.lpSum(p[i] * y[i] for i in pobres if zona[i] == d) >= r * dat["Pobres_d"][d], \
                f"P4_{d}".replace(" ", "")
    sev = pulp.lpSum(p[i] * q[i] for i in pobres)
    if rho > 0:
        m += sev <= (1 - rho) * dat["Sev0"], "P8"
    salen = pulp.lpSum(p[i] * y[i] for i in pobres)
    if etapa == 1:
        m += salen
    else:
        m += salen >= H_star * (1 - 1e-7), "E2"
        m += sev
    return m, z


def resolver(info, dat, B, r=0.0, rho=0.0, tiempo=180, gap2=1e-4):
    """gap2: brecha de la etapa 2. 1e-4 reproduce los datos congelados del 10-nov; la especificación del
    12-nov (Martín, §3.3) pide 1e-6 en las dos etapas de los cuatro modelos."""
    t0 = time.time()
    # Etapa 1. Auditoría 12-nov (h7): si HiGHS declara infactible, se confirma sin presolve, porque la
    # infactibilidad es ahora un RESULTADO que se reporta (fracción de réplicas factibles).
    for opciones1 in [{}, {"presolve": "off"}]:
        m, z = construir(info, dat, B, r, rho, etapa=1)
        m.solve(pulp.HiGHS(msg=False, timeLimit=tiempo, gapRel=1e-6, **opciones1))
        est, st_h, gap1 = estado_real(m, pulp.LpStatus[m.status])
        if est == "Optimal":
            break
    if est != "Optimal":
        return dict(estado=est + "_etapa1", segundos=time.time() - t0, estado_highs=st_h, gap_etapa1=gap1)
    H_star = pulp.value(m.objective)
    # Etapa 2. En 2 de 300 corridas (3-nov) el presolve de HiGHS declara infactible
    # "salen >= H*" aunque la solucion de la etapa 1 la cumple (verificado: gasto 49.024 <=
    # 50.000 y las mismas personas salen al reconstruir). Es un falso infactible del
    # presolve: se reintenta con presolve="off", que da el optimo. Se registra en la salida.
    for opciones in [{}, {"presolve": "off"}]:
        m, z = construir(info, dat, B, r, rho, etapa=2, H_star=H_star)
        m.solve(pulp.HiGHS(msg=False, timeLimit=tiempo, gapRel=gap2, **opciones))
        est, st_h, gap2 = estado_real(m, pulp.LpStatus[m.status])
        if est == "Optimal":
            break
    corte = {}
    if est == "Optimal":
        for (jj, g), v in info.items():
            corte[(jj, g)] = next(c for c in v["F"] if round(z[(jj, g, c)].value()) == 1)
    return dict(estado=est, H_star=H_star, corte=corte, presolve_off=bool(opciones), segundos=time.time() - t0,
                estado_highs=st_h, gap_etapa1=gap1, gap_etapa2=gap2)


def severidad(N1, dat):
    s1 = np.round(N1 @ dat["w"], 2)
    pb = dat["pobres"]
    return 1 - (dat["p"][pb] * s1[pb] ** 2).sum() / dat["Sev0"]
