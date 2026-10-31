# -*- coding: utf-8 -*-
"""
test_cortes.py — Tres pruebas del bloque 1 (cortes.py) antes de tocar el objetivo.

  T1  Regresion: con V = K = HS (lo que hacia 06) el modelo del paper debe dar
      EXACTAMENTE lo mismo que 06_modelo3_cortes.py: 153,0 con meta 10 %, mismos cortes.
  T2  Propiedad de prefijo con pesos arbitrarios: con V aleatorio > 0, cada corte
      factible debe ser auto-consistente y c = 0 y c = n deben estar siempre.
  T3  Elegibilidad: un par con elig = 0 se cubre (y se paga) pero N sigue en 1.

Uso: python3 test_cortes.py
"""
import importlib.util

import numpy as np
import pulp

import cortes

spec = importlib.util.spec_from_file_location("m6", "06_modelo3_cortes.py")
m6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m6)
m3 = m6.m3
m3.N_POR_CELDA = None                     # base completa

hog = m3.cargar()
R = m3.sortear_R(hog, m3.REPLICA)
IND, W = m3.IND, m3.W
M = hog[IND].to_numpy(float)
HS = hog.PERSONAS.to_numpy(float)
HW = hog.FEX_C.to_numpy(float)
w = np.array([W[j] for j in IND])
grupo = hog.CELDA.to_numpy()
HSmat = np.repeat(HS[:, None], len(IND), axis=1)


def modelo_paper(info, mpi_r=0.10):
    """El modelo del paper (min esfuerzo s.a. M0), armado SOLO con piezas de cortes.py."""
    pers = HS * HW
    score0 = np.round(M @ w, 2)
    pobre0 = (score0 >= 1 / 3).astype(int)
    MPI_S = (pers * pobre0 * score0).sum() / pers.sum()
    pobres = np.where(pobre0 == 1)[0]

    m = pulp.LpProblem("M3_paper", pulp.LpMinimize)
    z = cortes.variables_z(info)
    cortes.restricciones_corte_unico(m, info, z)
    Nexp, Kexp = cortes.expresiones_lineales(info, z)
    b1 = {i: pulp.LpVariable(f"b1_{i}", cat="Binary") for i in pobres}
    C = {i: pulp.LpVariable(f"C_{i}", lowBound=0) for i in pobres}
    for i in pobres:
        s = pulp.lpSum(w[jj] * Nexp[(i, jj)] for jj in range(len(IND)) if (i, jj) in Nexp)
        Mi = pers[i]
        m += C[i] + Mi * b1[i] >= Mi * s, f"R4_{i}"
        m += C[i] - Mi * b1[i] <= Mi * s, f"R5_{i}"
        m += s - (1 - b1[i]) <= m3.K_GRID, f"R6_{i}"
    m += pulp.lpSum(C.values()) <= MPI_S * (1 - mpi_r) * pers.sum(), "R7_meta"
    m += pulp.lpSum(Kexp.values())
    m.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=150))
    return m, z


# ---------------------------------------------------------------- T1
print("\nT1  regresion contra 06 (V = K = HS, meta 10 %)")
info = cortes.enumerar_cortes(M, R, HSmat, HSmat, grupo, eps=m3.EPS)
n_c = sum(len(v["F"]) for v in info.values())
m, z = modelo_paper(info)
obj = pulp.value(m.objective)
corte_nuevo, cub, Npost = cortes.reconstruir(info, z, M)

info_viejo = m6.enumerar_cortes(hog, R)[3]
mismos_F = all(info[(jj, d)]["F"] == info_viejo[(jj, d)]["F"] for (jj, d) in info_viejo)
print(f"    pares = {len(info)}, cortes = {n_c}, mismos cortes factibles que 06: {mismos_F}")
print(f"    estado = {pulp.LpStatus[m.status]}, objetivo = {obj:.1f}  (06 dio 153.0)")
assert len(info) == len(info_viejo) and mismos_F
assert abs(obj - 153.0) < 1e-6, "*** no reproduce 06"
print("    OK")

# ---------------------------------------------------------------- T2
print("\nT2  prefijo con pesos arbitrarios (V ~ U[0.1, 50] * HW)")
rng = np.random.default_rng(7)
Vr = rng.uniform(0.1, 50, M.shape) * HW[:, None]
info_r = cortes.enumerar_cortes(M, R, Vr, Vr, grupo, eps=m3.EPS)
malos = 0
for (jj, g), v in info_r.items():
    assert v["F"][0] == 0 and v["F"][-1] == v["n"], "faltan c = 0 o c = n"
    Rs = R[v["orden"], jj]
    for c in v["F"]:
        p = v["cumV"][c] / v["Den"]
        if (c > 0 and Rs[c - 1] > p) or (c < v["n"] and p > Rs[c] - m3.EPS):
            malos += 1
print(f"    cortes = {sum(len(v['F']) for v in info_r.values())}, inconsistentes = {malos}")
assert malos == 0
print("    OK")

# ---------------------------------------------------------------- T3
print("\nT3  elegibilidad: rezago no nivelable -> se paga, la privacion sigue")
jr = IND.index("rezago_escolar")
elig = np.ones_like(M)
elig[:, jr] = 0                                   # caso extremo: ningun rezago es nivelable
info_e = cortes.enumerar_cortes(M, R, HSmat, HSmat, grupo, elig=elig, eps=m3.EPS)
mt = pulp.LpProblem("t3", pulp.LpMinimize)
ze = cortes.variables_z(info_e)
cortes.restricciones_corte_unico(mt, info_e, ze)
Ne, Ke = cortes.expresiones_lineales(info_e, ze)
gr = next(g for (jj, g) in info_e if jj == jr)
v = info_e[(jr, gr)]
c_max = v["F"][-1]
for c in v["F"]:                                   # forzar a cubrir a todos en esa celda
    ze[(jr, gr, c)].setInitialValue(0)
mt += ze[(jr, gr, c_max)] == 1
mt += pulp.lpSum(Ke.values())
mt.solve(pulp.PULP_CBC_CMD(msg=0))
_, cub_e, N_e = cortes.reconstruir(info_e, ze, M)
filas = v["orden"]
print(f"    celda {gr}: cubiertos = {int(cub_e[filas, jr].sum())}/{v['n']}, "
      f"siguen privados = {int(N_e[filas, jr].sum())}, costo pagado = {pulp.value(mt.objective):.0f}")
assert cub_e[filas, jr].sum() == v["n"] and N_e[filas, jr].sum() == v["n"]
assert abs(pulp.value(mt.objective) - v["cumK"][-1]) < 1e-6
print("    OK\n")
