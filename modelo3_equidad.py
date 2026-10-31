# -*- coding: utf-8 -*-
"""
modelo3_equidad.py — Modelo 3 con el objetivo de equidad del Modelo 1.

Misma pregunta que el Modelo 1 de Martin, pero el Estado NO sabe quien es quien:
decide cuanto cubrir en cada (indicador, zona) y el sorteo decide a quien le llega.

Formulacion (numeracion igual a la del Modelo 1 para poder compararlos)
-----------------------------------------------------------------------
  Conjuntos: I todos los hogares (pagan), I^P pobres al inicio (cuentan), D zonas P3.
  Decision : z[j,d,c] (cortes.py).  N_ij = 1 - elig_ij * sum_{c>=rank} z.
  s_i = sum_j w_j N_ij  puntaje SIN censurar despues de intervenir, i en I^P.
  p_i = HW_i * HS_i     personas reales que representa el hogar.

  Etapa 1:  max  sum_{i in I^P} p_i y_i                     (personas que salen)
  Etapa 2:  min  sum_{i in I^P} p_i q_i   s.a.  sum p_i y_i >= H*   (desempate)

  C1  sum_c z[j,d,c] = 1                                   cortes.py
  (1) sum_{j,d} sum_c cumK(c) z[j,d,c] <= B                presupuesto (incluye no pobres)
  (2) s_i <= 0.33 + M_i (1 - y_i),  M_i = s_i^0 - 0.33     salida (Lin 3, bigM por hogar)
  (4) sum_{i in I^P, d} p_i y_i >= r * Pobres_d^0           equidad entre zonas
  (7) q_i >= 2 a s_i - a^2   para todo a en A_i             q_i = s_i^2 (tangentes)
  (8) sum_{i in I^P} p_i q_i <= (1 - rho) * Sev_0           equidad entre pobres

  (9) SevEdu queda para despues: necesita el sorteo por niño.

Por que (2) con M_i = s_i^0 - 0.33 y no M = 1: si y_i = 0 la restriccion debe ser
holgada, y s_i <= s_i^0 siempre (intervenir solo quita). Ese es el menor M valido;
uno mas grande da el mismo optimo pero una relajacion lineal mas floja.

Por que las tangentes (7) son exactas: s^2 - (2as - a^2) = (s - a)^2 >= 0, y s_i solo
puede valer sumas de pesos de subconjuntos de J_i (A_i). En el optimo q_i = s_i^2
porque (8) y la etapa 2 empujan q hacia abajo.
"""
import time

import numpy as np
import pulp

import cortes

K_GRID = 0.33


def valores_alcanzables(pesos_cent):
    """A_i: todas las sumas de subconjuntos de los pesos (en centesimas), como fraccion."""
    sumas = {0}
    for p in pesos_cent:
        sumas |= {s + p for s in sumas}
    return sorted(s / 100 for s in sumas)


def preparar(hog, IND, W):
    M = hog[IND].to_numpy(float)
    w = np.array([W[j] for j in IND])
    HS = hog.PERSONAS.to_numpy(float)
    HW = hog.FEX_C.to_numpy(float)
    p = HS * HW
    s0 = np.round(M @ w, 2)
    pobre0 = s0 >= 1 / 3
    zona = hog.CELDA.to_numpy()
    pobres = np.where(pobre0)[0]
    wc = np.round(w * 100).astype(int)
    A = {i: valores_alcanzables(wc[M[i] == 1]) for i in pobres}
    Sev0 = float((p[pobres] * s0[pobres] ** 2).sum())
    zonas = sorted(np.unique(zona))
    Pobres_d = {d: float(p[pobres][zona[pobres] == d].sum()) for d in zonas}
    return dict(M=M, w=w, HS=HS, HW=HW, p=p, s0=s0, pobre0=pobre0, pobres=pobres,
                zona=zona, zonas=zonas, A=A, Sev0=Sev0, Pobres_d=Pobres_d)


def construir(info, dat, B, r=0.0, rho=0.0, etapa=1, H_star=None):
    M, w, p, s0, zona = dat["M"], dat["w"], dat["p"], dat["s0"], dat["zona"]
    pobres = dat["pobres"]
    sentido = pulp.LpMaximize if etapa == 1 else pulp.LpMinimize
    m = pulp.LpProblem(f"M3_equidad_e{etapa}", sentido)

    z = cortes.variables_z(info)
    cortes.restricciones_corte_unico(m, info, z)
    Nexp, Kexp = cortes.expresiones_lineales(info, z)
    y = {i: pulp.LpVariable(f"y_{i}", cat="Binary") for i in pobres}
    q = {i: pulp.LpVariable(f"q_{i}", lowBound=0) for i in pobres}

    m += pulp.lpSum(Kexp.values()) <= B, "P1_presupuesto"

    # q_i solo importa si hay techo (8) o si es la etapa 2. En la etapa 1 sin techo,
    # las 6.048 tangentes no cambian el optimo y solo le estorban al solver.
    usar_q = rho > 0 or etapa == 2
    for i in pobres:
        s = pulp.lpSum(w[jj] * Nexp[(i, jj)] for jj in range(M.shape[1]) if (i, jj) in Nexp)
        Mi = s0[i] - K_GRID
        m += s <= K_GRID + Mi * (1 - y[i]), f"P2_salida_{i}"
        if usar_q:
            for k, a in enumerate(dat["A"][i]):
                if a > 0:
                    m += q[i] >= 2 * a * s - a * a, f"P7_tang_{i}_{k}"

    for d in dat["zonas"]:
        if r > 0:
            m += (pulp.lpSum(p[i] * y[i] for i in pobres if zona[i] == d)
                  >= r * dat["Pobres_d"][d]), f"P4_equidad_{d}".replace(" ", "")

    sev = pulp.lpSum(p[i] * q[i] for i in pobres)
    if rho > 0:
        m += sev <= (1 - rho) * dat["Sev0"], "P8_techo_severidad"

    salen = pulp.lpSum(p[i] * y[i] for i in pobres)
    if etapa == 1:
        m += salen
    else:
        m += salen >= H_star * (1 - 1e-7), "E2_mantener_salidas"
        m += sev
    return m, z, y, q


def resolver(info, dat, B, r=0.0, rho=0.0, dos_etapas=True, tiempo=150):
    t0 = time.time()
    # HiGHS, como Martin. gapRel pequeño: con p_i de cientos de personas, el gap por
    # defecto (1e-4) equivale a decenas de personas y arruina la etapa 2.
    # Etapa 2: el gap se mide en SEVERIDAD, no en personas; 1e-4 basta y con 1e-6
    # HiGHS se queda puliendo decimales (medido: 6 s contra > 150 s con B = $500 mm).
    m, z, y, q = construir(info, dat, B, r, rho, etapa=1)
    m.solve(pulp.HiGHS(msg=False, timeLimit=tiempo, gapRel=1e-6))
    est = pulp.LpStatus[m.status]
    if est != "Optimal":
        return dict(estado=est, segundos=time.time() - t0)
    H_star = pulp.value(m.objective)
    if dos_etapas:
        m, z, y, q = construir(info, dat, B, r, rho, etapa=2, H_star=H_star)
        m.solve(pulp.HiGHS(msg=False, timeLimit=tiempo, gapRel=1e-4))
        est = pulp.LpStatus[m.status]
    return dict(estado=est, z=z, H_star=H_star, segundos=time.time() - t0,
                n_restr=len(m.constraints), n_var=len(m.variables()))


def metricas(info, dat, sol, K):
    """Todo se RECALCULA desde los cortes elegidos; no se confia en y ni en q."""
    M, w, p, zona, pobre0 = dat["M"], dat["w"], dat["p"], dat["zona"], dat["pobre0"]
    corte, cubierto, Npost = cortes.reconstruir(info, sol["z"], M)
    s1 = np.round(Npost @ w, 2)
    pobre1 = s1 >= 1 / 3
    gasto_hogar = (cubierto * K).sum(axis=1)

    def bloque(mask):
        P = p[mask].sum()
        pob = mask & pobre1
        H = p[pob].sum() / P
        A = (p[pob] * s1[pob]).sum() / p[pob].sum() if p[pob].sum() > 0 else 0.0
        ini = mask & pobre0
        sev = (p[ini] * s1[ini] ** 2).sum()
        sev0 = (p[ini] * dat["s0"][ini] ** 2).sum()
        H0 = p[ini].sum() / P
        A0 = (p[ini] * dat["s0"][ini]).sum() / p[ini].sum()
        g = gasto_hogar[mask].sum()
        incl = gasto_hogar[mask & ~pobre0].sum() / g if g > 0 else 0.0
        return dict(H0=H0, H=H, A0=A0, A=A, M0_0=H0 * A0, M0=H * A,
                    sev_red=1 - sev / sev0, gasto=g, inclusion=incl,
                    salen=p[ini & ~pobre1].sum())

    out = {"Total": bloque(np.ones(len(p), bool))}
    for d in dat["zonas"]:
        out[d] = bloque(zona == d)
    return out, corte


def imprimir(res):
    print(f"    {'zona':<16}{'H0':>7}{'H':>7}{'A0':>7}{'A':>7}{'M0':>8}{'sev -':>7}"
          f"{'gasto $mm':>11}{'inclus.':>8}{'salen':>9}")
    for d, b in res.items():
        print(f"    {d:<16}{b['H0']:7.2%}{b['H']:7.2%}{b['A0']:7.1%}{b['A']:7.1%}"
              f"{b['M0']:8.4f}{b['sev_red']:7.1%}{b['gasto']/1e9:11.1f}"
              f"{b['inclusion']:8.1%}{b['salen']:9,.0f}")
