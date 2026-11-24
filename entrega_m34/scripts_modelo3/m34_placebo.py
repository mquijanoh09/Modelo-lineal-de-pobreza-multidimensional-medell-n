# -*- coding: utf-8 -*-
"""
m34_placebo.py — Placebo del Modelo 4 (auditoria 4-nov, hallazgo 6), escenario comun.

Pregunta: ¿la ventaja de M4 sobre M3 viene de la informacion demografica de los clusters o solo de
cambiar la particion (3 zonas -> 4 grupos)? El placebo "m4p" es M4 con las etiquetas de cluster
PERMUTADAS al azar: mismos 4 grupos y mismos tamaños (456/849/1.038/1.389), pero sin demografia.
Cada replica usa su propia permutacion (semilla [2026, 4, replica]) y el MISMO sorteo R que M3 y M4
en esa replica, asi la comparacion es pareada.

Las tareas de M3/M4 son las de siempre (BV.tarea con --fuente comun); este script solo agrega m4p
y corre en paralelo con escritura atomica, retomando lo ya hecho.

Uso: python3 m34_placebo.py <raiz_DEPARTAMENTAL> <n_replicas> <salida> [procesos=4] [modelos=m3,m4,m4p]
"""
import sys
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import pandas as pd

import m34_barrido_metas_v2 as BV
import m34_corridas_costos_reales as CC
from m34_montecarlo import matriz_grupo

SEMILLA_PLACEBO = 4


def etiquetas_placebo(etq, replica):
    rng = np.random.default_rng([2026, SEMILLA_PLACEBO, replica])
    return rng.permutation(etq)


def tarea(args):
    modelo, var, rep = args
    if modelo == "m4p":
        # cada proceso trabaja una tarea a la vez sobre su copia de G_ (fork): es seguro fijar aqui
        BV.G_["G"]["m4p"] = matriz_grupo(BV.G_["hog"], "m4", etiquetas_placebo(BV.G_["etq"], rep))
    return BV.tarea(args)


def main():
    raiz, nrep, out = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3])
    procesos = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    modelos = sys.argv[5].split(",") if len(sys.argv) > 5 else ["m3", "m4", "m4p"]
    out.mkdir(parents=True, exist_ok=True)
    CC.FUENTE = "comun"
    CC._preparar_barrido(raiz)
    import m34_clusters as CL
    etq, _ = CL.clusters(BV.G_["hog"], raiz)
    assert sorted(np.bincount(etq)) == [456, 849, 1038, 1389]
    BV.G_["etq"] = etq
    tareas = [(m, "comun", r) for r in range(nrep) for m in modelos]
    hechas = {p.stem for p in out.glob("*.csv")}
    tareas = [t for t in tareas if f"{t[0]}_{t[1]}_{t[2]}" not in hechas]
    print(len(tareas), "tareas,", procesos, "procesos", flush=True)
    with get_context("fork").Pool(procesos) as pool:
        for filas in pool.imap_unordered(tarea, tareas):
            f0 = filas[0]
            nombre = f"{f0['modelo']}_{f0['variante']}_{f0['replica']}"
            tmp = out / f".{nombre}.tmp"
            pd.DataFrame(filas).to_csv(tmp, index=False)
            tmp.rename(out / f"{nombre}.csv")          # atomico: un corte a mitad no deja archivos a medias
            print(time.strftime("%H:%M:%S"), nombre, round(sum(x["segundos"] for x in filas), 1), flush=True)


if __name__ == "__main__":
    main()
