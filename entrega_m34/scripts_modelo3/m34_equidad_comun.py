# -*- coding: utf-8 -*-
"""
m34_equidad_comun.py — Objetivo de equidad (el del M1: max personas que salen, luego min severidad) en el
ESCENARIO COMUN (5-nov), para M3, M4 y el placebo de M4 (clusters permutados, `m34_placebo`).

Reusa `m34_corridas_costos_reales.tarea_equidad` (mismo sorteo R por replica, rho = 0 y 0,10).
Guarda un CSV por (modelo, replica) con escritura atomica y retoma lo ya hecho (auditoria 4-nov, h10:
30 replicas en lugar de 15).

Uso: python3 m34_equidad_comun.py <raiz> <n_replicas> <carpeta_salida> <procesos> <B1> <B2> ...   (B en mil millones)
"""
import sys
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import pandas as pd

import m34_corridas_costos_reales as CC
from m34_montecarlo import matriz_grupo
from m34_placebo import etiquetas_placebo


def tarea(args):
    mod, rep = args
    if mod == "m4p":
        CC.EQ["G"]["m4p"] = matriz_grupo(CC.EQ["hog"], "m4", etiquetas_placebo(CC.EQ["etq"], rep))
    return CC.tarea_equidad(args)


def main():
    raiz, nrep, out, procesos = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3]), int(sys.argv[4])
    Bs = [float(x) for x in sys.argv[5:]]
    out.mkdir(parents=True, exist_ok=True)
    CC.FUENTE = "comun"
    CC._preparar_equidad(raiz, Bs)
    import m34_clusters as CL
    etq, _ = CL.clusters(CC.EQ["hog"], raiz)
    CC.EQ["etq"] = etq
    tareas = [(m, r) for r in range(nrep) for m in ["m3", "m4", "m4p"]]
    hechas = {p.stem for p in out.glob("*.csv")}
    tareas = [t for t in tareas if f"{t[0]}_{t[1]}" not in hechas]
    print(len(tareas), "tareas, B =", Bs, flush=True)
    with get_context("fork").Pool(procesos) as pool:
        for filas in pool.imap_unordered(tarea, tareas):
            n = f"{filas[0]['modelo']}_{filas[0]['replica']}"
            tmp = out / f".{n}.tmp"
            pd.DataFrame(filas).to_csv(tmp, index=False)
            tmp.rename(out / f"{n}.csv")
            print(time.strftime("%H:%M:%S"), n, [round(f.get("personas_salen", -1)) for f in filas if f["rho"] == 0],
                  flush=True)


if __name__ == "__main__":
    main()
