# -*- coding: utf-8 -*-
"""
m34_montecarlo_lex.py — Monte Carlo de M3 y M4 con DESEMPATE LEXICOGRAFICO (3-nov-2026).

Cambios frente a m34_montecarlo.py (que se conserva como version del 2-nov):
  1. Segunda etapa: min error de inclusion s.a. costo <= E*(1 + 1e-6) (Trampa 13).
     El error de inclusion deja de depender de cual optimo alterno devuelva el solver.
  2. Rezago en dos versiones:
       intervenible     -> como el 2-nov (el programa cura el rezago)
       no_intervenible  -> caso base nuevo: decision de Martin del 2-nov (ningun nino sale
                           del rezago en un año). elig = 0 <=> excluir el par del MILP.
Paraleliza por tarea (modelo, variante, rezago, replica) con Pool(2); reanuda si se corta.

Uso: python3 m34_montecarlo_lex.py <raiz_DEPARTAMENTAL> <n_replicas> <dir_salida> [rep_ini]
"""
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

import m34_datos as D
import m34_mecanismo as X
from m34_montecarlo import METAS, matriz_grupo, precios_u1

G_ = {}


def preparar(raiz):
    hog = D.cargar(raiz)
    b = D.verificar_linea_base(hog)
    M, HS, HW, w = D.matrices(hog)
    import m34_clusters as K
    etq, _ = K.clusters(hog, raiz)
    assert sorted(np.bincount(etq)) == [456, 849, 1038, 1389], "clusters no reproducen 07"
    Kpes = precios_u1(hog)
    HSm = np.repeat(HS[:, None], 15, 1)
    HWm = np.repeat(HW[:, None], 15, 1)
    G_.update(hog=hog, b=b, M=M, HS=HS, HW=HW, w=w, Kpes=Kpes, celda=hog.CELDA.to_numpy(),
              G={"m3": matriz_grupo(hog, "m3"), "m4": matriz_grupo(hog, "m4", etq)},
              var={"pp": (HSm, HSm), "u1": (HWm, Kpes)})


def tarea(args):
    modelo, var, rez, rep = args
    g = G_
    R = D.sortear_R(g["hog"], rep)
    V, Kc = g["var"][var]
    excl = () if rez == "intervenible" else (D.IND.index("rezago_escolar"),)
    info = X.enumerar_cortes(g["M"], R, V, Kc, g["G"][modelo], excluir=excl, pobre0=g["b"]["pobre0"])
    filas = []
    for meta in METAS:
        res = X.resolver_paper(g["M"], g["w"], g["b"]["pers"], g["b"]["pobre0"], g["b"]["M0"],
                               info, meta, solver="highs", gap=1e-6, tmax=180, desempate=True)
        f = dict(modelo=modelo, variante=var, rezago=rez, replica=rep, meta=meta,
                 estado=res["estado"], objetivo=res["obj"], objetivo_etapa1=res["obj_etapa1"],
                 segundos=res["segundos"], n_cortes=res["n_cortes"], pares=len(info))
        if res["estado"] == "Optimal":
            cub, N1 = X.reconstruir(info, res["corte"], g["M"])
            f.update(X.metricas(cub, N1, g["M"], g["w"], g["HS"], g["HW"], g["b"]["pobre0"],
                                g["celda"], Kpesos=g["Kpes"]))
            act = {k: c for k, c in res["corte"].items() if c > 0}
            f["cortes"] = ";".join(f"{D.IND[jj]}|{gg}|{c}/{info[(jj, gg)]['n']}"
                                   for (jj, gg), c in sorted(act.items(), key=lambda t: (t[0][0], str(t[0][1]))))
        filas.append(f)
    return filas


def main():
    raiz, nrep, out = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3])
    r0 = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    out.mkdir(parents=True, exist_ok=True)
    preparar(raiz)
    tareas = [(m, v, r, rep) for rep in range(r0, nrep) for r in ["no_intervenible", "intervenible"]
              for m in ["m3", "m4"] for v in ["pp", "u1"]]
    hechas = {p.stem for p in out.glob("*.csv")}
    tareas = [t for t in tareas if "_".join(map(str, t)) not in hechas]
    print(len(tareas), "tareas", flush=True)
    with Pool(2) as pool:
        for filas in pool.imap_unordered(tarea, tareas):
            f0 = filas[0]
            nom = f"{f0['modelo']}_{f0['variante']}_{f0['rezago']}_{f0['replica']}"
            pd.DataFrame(filas).to_csv(out / f"{nom}.csv", index=False)
            print(time.strftime("%H:%M:%S"), nom, round(sum(x["segundos"] for x in filas), 1), flush=True)


if __name__ == "__main__":
    main()
