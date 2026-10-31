# -*- coding: utf-8 -*-
"""
06_modelo3_cortes.py — Modelo 3 reformulado por PUNTOS DE CORTE.

Mismo modelo matematico que 05_modelo3.py, misma region factible, mismo optimo.
Lo unico que cambia es COMO se describe la decision.

LA IDEA
-------
En 05_modelo3.py hay una binaria N_ij por cada hogar privado (8.602 en Antioquia
completa). Pero el mecanismo estocastico no permite 2^8602 combinaciones. Fija
una celda d y un indicador j: un hogar sale de la privacion si y solo si
R_ij <= p_jd, y p_jd es UN numero para toda la celda. Entonces, si ordenas los
hogares privados de la celda por R_ij ascendente, los curados son siempre un
PREFIJO de ese orden. El optimizador no puede escoger un hogar si y el siguiente
no: solo puede mover el punto de corte.

Y no cualquier corte vale. Si cortas en c, la cobertura resultante es
    p(c) = cum(c) / Den_jd,   cum(c) = suma de HS de los c primeros
y para que sea auto-consistente hace falta que el ultimo curado efectivamente
cumpla R <= p y el primero no curado cumpla R > p:
    R_(c) <= p(c) <= R_(c+1) - eps
Eso deja un punado de cortes factibles por celda-indicador, enumerables de
antemano porque solo dependen de los datos y del sorteo R, no de la decision.

Medido sobre Antioquia completa: 631 cortes factibles en total sobre los 45
pares (indicador, celda). El Modelo 3 tiene 45 decisiones, no 8.602.

ESTO ES, LITERALMENTE, LA NARRATIVA DEL PROYECTO: el Estado decide cuanto pone
en cada celda, pero no a quien le llega. La identidad de los beneficiarios la
fija el sorteo. Los errores de inclusion son los hogares con R bajo que no eran
prioritarios; los de exclusion, los de R alto que si lo eran.

LA REFORMULACION
----------------
Variables:  z[j,d,c] = 1 si la celda d corta en c para el indicador j
            sum_{c in F_jd} z[j,d,c] = 1                 (escoge exactamente uno)

Todo lo demas sale lineal en z:
    N_ij  = 1 - sum_{c in F_jd, c >= rank_ij} z[j,d,c]
    E_jd  = EF_j * sum_{c in F_jd} cum(c) * z[j,d,c]

R4-R7 (censura Alkire-Foster y meta de IPM) no cambian en nada.

Uso:  python3 06_modelo3_cortes.py            # resuelve y compara con 05
      python3 06_modelo3_cortes.py 0.10       # con esa meta
      python3 06_modelo3_cortes.py 0.10 solo  # sin comparar (mas rapido)
"""
import importlib.util
import sys
import time
from pathlib import Path

import numpy as np
import pulp

# Reutilizamos la carga de datos, el sorteo de R y las constantes de 05_modelo3.
# Se hace con importlib porque el nombre empieza por digito y no se puede importar.
_ruta = Path(__file__).resolve().parent / "05_modelo3.py"
_spec = importlib.util.spec_from_file_location("m3", _ruta)
m3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m3)

IND, W, EPS = m3.IND, m3.W, m3.EPS
K_GRID = m3.K_GRID
EF = {j: 1.0 for j in IND}       # TODO-EF: igual que en 05


# =============================================================================
# 1. ENUMERAR LOS CORTES FACTIBLES  (puro preproceso, sin solver)
# =============================================================================
def enumerar_cortes(hog, R):
    """Para cada (indicador, celda) devuelve el orden por R y los cortes validos."""
    M  = hog[IND].to_numpy(float)
    HS = hog.PERSONAS.to_numpy(float)
    celdas = sorted(hog.CELDA.unique())
    if len(celdas) < 2:
        sys.exit("\n*** |D| < 2: sin focalizacion geografica no hay Modelo 3.\n")
    idx_celda = {d: np.where(hog.CELDA.values == d)[0] for d in celdas}

    info = {}
    for jj in range(len(IND)):
        for d in celdas:
            act = [i for i in idx_celda[d] if M[i, jj] == 1]
            if not act:
                continue                      # celda sin privacion en j
            orden = sorted(act, key=lambda i: R[i, jj])
            Rs  = np.array([R[i, jj] for i in orden])
            hs  = np.array([HS[i] for i in orden])
            Den = hs.sum()
            cum = np.concatenate([[0.0], np.cumsum(hs)])     # cum[c], c = 0..n
            n   = len(orden)

            if np.any(np.diff(Rs) == 0):
                print(f"    aviso: empate exacto en R para j={IND[jj]} d={d}; "
                      f"el prefijo queda ambiguo (probabilidad cero con R continua)")

            F = []
            for c in range(n + 1):
                p = cum[c] / Den
                # el ultimo curado tiene que cumplir R <= p
                ok_abajo  = (c == 0) or (Rs[c - 1] <= p)
                # el primer NO curado tiene que cumplir p <= R - eps
                ok_arriba = (c == n) or (p <= Rs[c] - EPS)
                if ok_abajo and ok_arriba:
                    F.append(c)
            # c=0 (no hacer nada) y c=n (cubrir a todos) son siempre factibles
            info[(jj, d)] = dict(orden=orden, Den=Den, cum=cum, F=F, n=n)
    return M, HS, celdas, info


# =============================================================================
# 2. MODELO
# =============================================================================
def construir_y_resolver(hog, R, mpi_r, tiempo_max=300):
    M, HS, celdas, info = enumerar_cortes(hog, R)
    HW = hog.FEX_C.to_numpy(float)
    pers = HS * HW
    w = np.array([W[j] for j in IND])

    score0 = np.round(M @ w, 2)
    pobre0 = (score0 >= 1 / 3).astype(int)
    MPI_S  = (pers * pobre0 * score0).sum() / pers.sum()
    pobres_idx = np.where(pobre0 == 1)[0]

    n_cortes = sum(len(v["F"]) for v in info.values())
    print(f"\n  |I| = {len(hog):,} | |D| = {len(celdas)} | pares (j,d) activos = {len(info)}")
    print(f"  cortes factibles = {n_cortes:,}  (media {n_cortes/len(info):.1f} por par)")
    print(f"  binarias: z={n_cortes:,} + b1={len(pobres_idx):,} = {n_cortes+len(pobres_idx):,}")
    print(f"  MPI_s = M0 = {MPI_S:.6f}  ->  meta <= {MPI_S*(1-mpi_r):.6f}")

    m = pulp.LpProblem("Modelo3_cortes", pulp.LpMinimize)
    z = {(jj, d, c): pulp.LpVariable(f"z_{jj}_{d}_{c}", cat="Binary")
         for (jj, d), v in info.items() for c in v["F"]}
    b1 = {i: pulp.LpVariable(f"b1_{i}", cat="Binary") for i in pobres_idx}
    C  = {i: pulp.LpVariable(f"C_{i}", lowBound=0) for i in pobres_idx}  # lowBound=0 OBLIGATORIO

    # --- una sola eleccion de corte por (indicador, celda) ------------------
    for (jj, d), v in info.items():
        m += pulp.lpSum(z[(jj, d, c)] for c in v["F"]) == 1, f"corte_unico_{jj}_{d}"

    # --- N_ij como expresion lineal en z ------------------------------------
    # el hogar de rango k (1-indexado) se cura si y solo si el corte c >= k
    Nexp = {}
    for (jj, d), v in info.items():
        for k, i in enumerate(v["orden"], start=1):
            Nexp[(i, jj)] = 1 - pulp.lpSum(z[(jj, d, c)] for c in v["F"] if c >= k)

    # --- esfuerzo: tambien lineal en z --------------------------------------
    Eexp = {(jj, d): EF[IND[jj]] * pulp.lpSum(v["cum"][c] * z[(jj, d, c)] for c in v["F"])
            for (jj, d), v in info.items()}

    # --- R4-R6: censura Alkire-Foster (identicas a 05) ----------------------
    for i in pobres_idx:
        score_post = pulp.lpSum(w[jj] * Nexp[(i, jj)]
                                for jj in range(len(IND)) if (i, jj) in Nexp)
        Mi = pers[i]
        m += C[i] + Mi * b1[i] >= Mi * score_post, f"R4_{i}"
        m += C[i] - Mi * b1[i] <= Mi * score_post, f"R5_{i}"
        m += score_post - (1 - b1[i]) <= K_GRID,   f"R6_{i}"

    # --- R7: meta de reduccion ---------------------------------------------
    m += pulp.lpSum(C.values()) <= MPI_S * (1 - mpi_r) * pers.sum(), "R7_meta"

    m += pulp.lpSum(Eexp.values())

    print(f"  restricciones: {len(m.constraints):,}")
    t0 = time.time()
    m.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=tiempo_max))
    dt = time.time() - t0

    ctx = dict(celdas=celdas, info=info, M=M, HS=HS, pers=pers, w=w,
               score0=score0, pobre0=pobre0, MPI_S=MPI_S, z=z, segundos=dt)
    return m, ctx


# =============================================================================
# 3. REPORTE
# =============================================================================
def reportar(m, ctx, mpi_r):
    print(f"\n  estado: {pulp.LpStatus[m.status]}   ({ctx['segundos']:.1f} s)")
    if pulp.LpStatus[m.status] != "Optimal":
        return None
    M, HS, pers, w = ctx["M"], ctx["HS"], ctx["pers"], ctx["w"]
    info, z = ctx["info"], ctx["z"]

    # reconstruir N desde los cortes elegidos
    Npost = M.copy()
    corte = {}
    for (jj, d), v in info.items():
        c_sel = next(c for c in v["F"] if round(z[(jj, d, c)].value()) == 1)
        corte[(jj, d)] = c_sel
        for k, i in enumerate(v["orden"], start=1):
            Npost[i, jj] = 0 if c_sel >= k else 1

    score1 = np.round(Npost @ w, 2)
    pobre1 = (score1 >= 1 / 3).astype(int)
    obj = pulp.value(m.objective)
    M1 = (pers * pobre1 * score1).sum() / pers.sum()
    print(f"  esfuerzo total = {obj:,.1f} personas-privacion")
    print(f"  M0: {ctx['MPI_S']:.6f} -> {M1:.6f}  (meta <= {ctx['MPI_S']*(1-mpi_r):.6f})")
    print(f"  H : {(pers*ctx['pobre0']).sum()/pers.sum():.4f} -> "
          f"{(pers*pobre1).sum()/pers.sum():.4f}")

    curadas = M - Npost
    if curadas.sum() > 0:
        esf = (HS[:, None] * curadas).sum(axis=1)
        incl = esf[ctx["pobre0"] == 0].sum() / esf.sum()
        print(f"  privaciones resueltas: {int(curadas.sum()):,}")
        print(f"  ERROR DE INCLUSION: {incl:.1%} del esfuerzo cayo en hogares no pobres")
        print("\n  cortes elegidos (solo los no nulos):")
        for (jj, d), c in sorted(corte.items(), key=lambda kv: -kv[1]):
            if c > 0:
                v = info[(jj, d)]
                print(f"    {d:<16} {IND[jj]:<26} corte {c}/{v['n']}  "
                      f"cobertura p={v['cum'][c]/v['Den']:.3f}  esfuerzo={v['cum'][c]:,.0f}")
    return obj


# =============================================================================
if __name__ == "__main__":
    mpi_r = float(sys.argv[1]) if len(sys.argv) > 1 else 0.10
    comparar = not (len(sys.argv) > 2 and sys.argv[2] == "solo")

    hog = m3.cargar()
    R = m3.sortear_R(hog, m3.REPLICA)

    print(f"\n{'='*72}\n FORMULACION POR CORTES — MPI_r = {mpi_r}\n{'='*72}")
    m_new, ctx = construir_y_resolver(hog, R, mpi_r)
    obj_new = reportar(m_new, ctx, mpi_r)

    if comparar:
        print(f"\n{'='*72}\n CONTROL: formulacion original de 05_modelo3.py\n{'='*72}")
        t0 = time.time()
        m_old, N, C, E, ctx_old = m3.construir_y_resolver(hog, R, mpi_r)
        dt_old = time.time() - t0
        print(f"  estado: {pulp.LpStatus[m_old.status]}   ({dt_old:.1f} s)")
        obj_old = pulp.value(m_old.objective) if pulp.LpStatus[m_old.status] == "Optimal" else None

        print(f"\n{'='*72}\n EQUIVALENCIA\n{'='*72}")
        print(f"  objetivo por cortes   = {obj_new}")
        print(f"  objetivo original     = {obj_old}")
        if obj_old is not None and obj_new is not None:
            igual = abs(obj_new - obj_old) < 1e-6
            print(f"  {'OK: mismo optimo' if igual else '*** DIFIEREN: revisar la enumeracion de cortes'}")
            print(f"  velocidad: {dt_old/ctx['segundos']:.1f}x mas rapido")
