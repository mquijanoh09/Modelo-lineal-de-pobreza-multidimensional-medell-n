# -*- coding: utf-8 -*-
"""
m34_barrido_metas_v2.py — Curva costo-meta de M3 y M4 (objetivo del paper), 3-nov-2026.

Reemplaza a m34_barrido_sensibilidad.py (2-nov), cuyas filas `no_intervenible` NO sirven
(Trampa 14: el mecanismo de entonces no tenia `excluir` y el rezago se "curaba" gratis).
Cambios: mecanismo del 3-nov, desempate lexicografico (Trampa 13), solo el caso base
(rezago no intervenible) y reintento sin presolve (Trampa 15, ya dentro de resolver_paper).

Salida: una fila por (modelo, variante, replica, meta) con costo, inclusion, exclusion y
gasto por dimension y por zona. Sirve para la grafica "cuanto cuesta cada punto de M0".

Uso: python3 m34_barrido_metas_v2.py <raiz_DEPARTAMENTAL> <n_replicas> <dir_salida>
"""
import sys
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import pandas as pd

import m34_clusters as CL
import m34_datos as D
import m34_mecanismo as X
from m34_montecarlo import matriz_grupo, precios_u1

METAS = [round(x, 2) for x in np.arange(0.02, 0.301, 0.02)]
G_ = {}


def preparar(raiz):
    hog = D.cargar(raiz)
    b = D.verificar_linea_base(hog)
    M, HS, HW, w = D.matrices(hog)
    etq, _ = CL.clusters(hog, raiz)
    assert sorted(np.bincount(etq)) == [456, 849, 1038, 1389]
    Kp = precios_u1(hog)
    HWm = np.repeat(HW[:, None], 15, 1)
    G_.update(hog=hog, b=b, M=M, HS=HS, HW=HW, w=w, Kp=Kp, zona=hog.CELDA.to_numpy(),
              G={"m3": matriz_grupo(hog, "m3"), "m4": matriz_grupo(hog, "m4", etq)},
              var={"u1": (HWm, Kp)})   # variante "pp" (V = K = HS) retirada: auditoria 4-nov, h12


def tarea(args):
    modelo, var, rep = args
    g = G_
    R = D.sortear_R(g["hog"], rep)
    V, Kc = g["var"][var]
    info = X.enumerar_cortes(g["M"], R, V, Kc, g["G"][modelo], excluir=(D.IND.index("rezago_escolar"),),
                             pobre0=g["b"]["pobre0"])
    filas = []
    for meta in METAS:
        res = X.resolver_paper(g["M"], g["w"], g["b"]["pers"], g["b"]["pobre0"], g["b"]["M0"], info, meta,
                               solver="highs", gap=1e-6, tmax=180, desempate=True)
        f = dict(modelo=modelo, variante=var, replica=rep, meta=meta, estado=res["estado"],
                 objetivo=res["obj"], segundos=res["segundos"],
                 estado_highs=res.get("estado_highs"), gap=res.get("gap"))
        if res["estado"] == "Optimal":
            cub, N1 = X.reconstruir(info, res["corte"], g["M"])
            f.update(X.metricas(cub, N1, g["M"], g["w"], g["HS"], g["HW"], g["b"]["pobre0"], g["zona"],
                                Kpesos=g["Kp"]))
            gasto = (g["Kp"] * cub)
            for dim, js in D.DIMS.items():
                f[f"gasto_{dim}"] = float(gasto[:, [D.IND.index(j) for j in js]].sum())
            for d in np.unique(g["zona"]):
                f[f"gasto_{d}"] = float(gasto[g["zona"] == d].sum())
            # pendiente #5: cuanto del costo cae en pares con muestra chica (n < 10 hogares
            # privados), donde el corte equivale casi a escoger hogar por hogar
            f["costo_pares_n_lt10"] = float(sum(info[k]["cumK"][c] for k, c in res["corte"].items()
                                                if info[k]["n"] < 10))
        filas.append(f)
    return filas


def main():
    raiz, nrep, out = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    preparar(raiz)
    tareas = [(m, v, rep) for rep in range(nrep) for m in ["m3", "m4"] for v in ["u1"]]
    hechas = {p.stem for p in out.glob("*.csv")}
    tareas = [t for t in tareas if f"{t[0]}_{t[1]}_{t[2]}" not in hechas]
    print(len(tareas), "tareas", flush=True)
    # fork: las tareas heredan G_ del proceso padre; con spawn (defecto en macOS) llega vacio
    with get_context("fork").Pool(2) as pool:
        for filas in pool.imap_unordered(tarea, tareas):
            f0 = filas[0]
            pd.DataFrame(filas).to_csv(out / f"{f0['modelo']}_{f0['variante']}_{f0['replica']}.csv", index=False)
            print(time.strftime("%H:%M:%S"), f0["modelo"], f0["variante"], f0["replica"],
                  round(sum(x["segundos"] for x in filas), 1), flush=True)


if __name__ == "__main__":
    main()
