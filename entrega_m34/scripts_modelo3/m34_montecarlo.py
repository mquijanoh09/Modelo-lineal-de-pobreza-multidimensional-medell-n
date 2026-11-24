# -*- coding: utf-8 -*-
"""
m34_montecarlo.py — Monte Carlo de los Modelos 3 y 4 (objetivo del paper).

Por cada replica r: se sortea R^(r) (semilla por hogar), se enumeran los cortes y se
resuelve el MILP para cada meta. Se guarda una fila por (replica, meta, variante).

Lo que importa NO es el promedio sino la DISTRIBUCION: la dispersion entre replicas es
cuanto depende el desempeño del Estado del azar de a quien le llega el programa.

Variantes de costo:
  pp  : V = K = HS (personas-privacion; reproduce 06: 153,0 con meta 10 %, replica 0)
  u1  : V = HW (hogares representados), K = EpF_j^zona * HW en millones de pesos
        (sensibilidad u = 1 acordada con Martin; tabla de CONTEXTO_DATOS.md §4)

Uso: python3 m34_montecarlo.py <raiz_DEPARTAMENTAL> <m3|m4> <rep_ini> <rep_fin> <salida.csv>
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

import m34_datos as D
import m34_mecanismo as X

METAS = [0.05, 0.10, 0.20]
P_INASISTENCIA = 0.369
EPF = {  # (urbano, rural), millones de pesos de 2025 — CONTEXTO_DATOS.md §4 (Martin, 30-oct)
    "logro_educativo": (2.88, 3.86), "analfabetismo": (0.96, 1.29),
    "inasistencia_escolar": (3.0 / P_INASISTENCIA, 3.0 / P_INASISTENCIA),
    "rezago_escolar": (3.05, 3.96), "atencion_integral": (5.21, 5.21),
    "trabajo_infantil": (3.0, 3.0), "desempleo_larga_duracion": (5.12, 5.12),
    "empleo_formal": (2.73, 2.73), "aseguramiento_salud": (1.32, 1.32),
    "barreras_acceso_salud": (0.21, 0.36), "acueducto": (11.72, 43.7),
    "alcantarillado": (11.72, 15.3), "pisos": (25.62, 35.2), "paredes": (25.62, 35.2),
    "hacinamiento": (31.32, 31.32)}


def precios_u1(hog):
    rural = hog.P3.to_numpy() != 1
    P = np.column_stack([np.where(rural, EPF[j][1], EPF[j][0]) for j in D.IND])
    return P * hog.FEX_C.to_numpy(float)[:, None]          # millones de pesos por par (i, j)


def matriz_grupo(hog, modelo, etq=None):
    zona = hog.CELDA.to_numpy()
    G = np.repeat(zona[:, None], len(D.IND), 1).astype(object)
    if modelo == "m4":
        for jj, j in enumerate(D.IND):
            if j in D.U_PRIVADOS:
                G[:, jj] = np.array([f"T{e}" for e in etq], dtype=object)
    return G


def main():
    raiz, modelo, r0, r1, salida = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    hog = D.cargar(raiz)
    b = D.verificar_linea_base(hog)
    M, HS, HW, w = D.matrices(hog)
    celda = hog.CELDA.to_numpy()
    etq = None
    if modelo == "m4":
        import m34_clusters as K
        etq, _ = K.clusters(hog, raiz)
        assert sorted(np.bincount(etq)) == [456, 849, 1038, 1389], "clusters no reproducen 07"
    G = matriz_grupo(hog, modelo, etq)
    Kpes = precios_u1(hog)
    HSm = np.repeat(HS[:, None], 15, 1)
    HWm = np.repeat(HW[:, None], 15, 1)
    variantes = {"pp": (HSm, HSm), "u1": (HWm, Kpes)}

    hechas = set()
    if Path(salida).exists():
        prev = pd.read_csv(salida)
        hechas = set(zip(prev.replica, prev.meta, prev.variante))
    for rep in range(r0, r1):
        R = D.sortear_R(hog, rep)
        for var, (V, Kc) in variantes.items():
            info = X.enumerar_cortes(M, R, V, Kc, G)
            for meta in METAS:
                if (rep, meta, var) in hechas:
                    continue
                res = X.resolver_paper(M, w, b["pers"], b["pobre0"], b["M0"], info, meta,
                                       solver="highs", gap=1e-6, tmax=180)
                fila = dict(modelo=modelo, replica=rep, meta=meta, variante=var,
                            estado=res["estado"], objetivo=res["obj"], segundos=res["segundos"],
                            n_cortes=res["n_cortes"], n_bin=res["n_bin"], pares=len(info))
                if res["estado"] == "Optimal":
                    cub, N1 = X.reconstruir(info, res["corte"], M)
                    fila.update(X.metricas(cub, N1, M, w, HS, HW, b["pobre0"], celda, Kpesos=Kpes))
                    # cuantos pares (j, g) reciben esfuerzo y donde
                    act = {k: c for k, c in res["corte"].items() if c > 0}
                    fila["pares_activos"] = len(act)
                    fila["cortes"] = ";".join(f"{D.IND[jj]}|{g}|{c}/{info[(jj, g)]['n']}"
                                              for (jj, g), c in sorted(act.items(), key=lambda t: (t[0][0], str(t[0][1]))))
                pd.DataFrame([fila]).to_csv(salida, mode="a", header=not Path(salida).exists(), index=False)
        print(f"{modelo} replica {rep} lista ({time.strftime('%H:%M:%S')})", flush=True)


if __name__ == "__main__":
    main()
