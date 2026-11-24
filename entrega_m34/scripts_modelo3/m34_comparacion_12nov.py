# -*- coding: utf-8 -*-
"""
m34_comparacion_12nov.py — Corridas de M3, M4 y placebo según la especificación de Martín del 12-nov
(rama Contexto, ESPECIFICACION_COMPARACION_4_MODELOS.md, §4).

  costo      Meta de M0 EN CADA ZONA (§4.3), 15 metas del 2 al 30 %, desempate lexicográfico, gap 1e-6.
             (La meta global queda como sensibilidad: son los datos congelados del 10-nov.)
  cobertura  Max personas que salen con presupuesto B (§4.1-4.2), con el piso por zona r_B (caso principal)
             y con r_B + rho_B (sensibilidad), r_B y rho_B del M1 (r_rho_comparacion.csv), los MISMOS en los
             tres modelos. Gap 1e-6 en las dos etapas (§3.3). Las infactibles se guardan (§3.3, regla 2).
M3, M4 y placebo con el mismo sorteo R por réplica (pareado). Costos y reglas: tabla común (10-nov).

Uso:
  python3 m34_comparacion_12nov.py costo     <raiz> <n_rep> <salida/> <procesos>
  python3 m34_comparacion_12nov.py cobertura <raiz> <n_rep> <salida/> <procesos> <r_rho.csv> B1 B2 ...
"""
import sys
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import pandas as pd

import m34_barrido_metas_v2 as BV
import m34_corridas_costos_reales as CC
import m34_datos as D
import m34_equidad as E
import m34_mecanismo as X
from m34_montecarlo import matriz_grupo
from m34_placebo import etiquetas_placebo
from m34_placebo import tarea as tarea_costo

PAR = {}


def _ejecutar(tareas, fn, out, nombre, procesos):
    hechas = {p.stem for p in out.glob("*.csv")}
    tareas = [t for t in tareas if nombre(t) not in hechas]
    print(len(tareas), "tareas,", procesos, "procesos", flush=True)
    with get_context("fork").Pool(procesos) as pool:
        for filas in pool.imap_unordered(fn, tareas):
            n = nombre(filas[0], de_fila=True)
            tmp = out / f".{n}.tmp"
            pd.DataFrame(filas).to_csv(tmp, index=False)
            tmp.rename(out / f"{n}.csv")
            print(time.strftime("%H:%M:%S"), n, flush=True)


def tarea_cobertura(args):
    mod, rep = args
    g = CC.EQ
    G = g["G"][mod] if mod != "m4p" else matriz_grupo(g["hog"], "m4", etiquetas_placebo(g["etq"], rep))
    R = D.sortear_R(g["hog"], rep)
    info = X.enumerar_cortes(g["M"], R, g["V"], g["K"], G, excluir=(D.IND.index("rezago_escolar"),),
                             pobre0=g["dat"]["pobre0"], fijos=g["fijos"])
    filas = []
    for B in g["Bs"]:
        rr = PAR["tabla"].loc[B]
        for esc, rho in [("r", 0.0), ("r_rho", rr.rho_B)]:
            base = dict(modelo=mod, replica=rep, B=B, escenario=esc, r=rr.r_B,
                        rho=rho if pd.notna(rho) else np.nan)
            if pd.isna(rho):
                filas.append(dict(base, estado="sin_rho"))      # la regla de la brecha no se alcanza con este B
                continue
            s = E.resolver(info, g["dat"], B=B * 1e3, r=float(rr.r_B), rho=float(rho), gap2=1e-6)
            f = dict(base, estado=s["estado"], segundos=s["segundos"], estado_highs=s.get("estado_highs"),
                     gap_etapa1=s.get("gap_etapa1"), gap_etapa2=s.get("gap_etapa2"))
            if s["estado"] == "Optimal":
                cub, N1 = X.reconstruir(info, s["corte"], g["M"])
                f.update(X.metricas(cub, N1, g["M"], g["w"], g["HS"], g["HW"], g["b"]["pobre0"], g["celda"],
                                    Kpesos=g["K"]))
                f["personas_salen"] = s["H_star"]
                f["sev_reduccion"] = E.severidad(N1, g["dat"])
                f["presolve_off"] = s["presolve_off"]
            filas.append(f)
    return filas


def main():
    modo, raiz, nrep, out, procesos = sys.argv[1], sys.argv[2], int(sys.argv[3]), Path(sys.argv[4]), int(sys.argv[5])
    out.mkdir(parents=True, exist_ok=True)
    CC.FUENTE = "comun"
    import m34_clusters as CL
    if modo == "costo":
        BV.META_ZONA = True                     # heredado por los procesos (fork)
        CC._preparar_barrido(raiz)
        etq, _ = CL.clusters(BV.G_["hog"], raiz)
        assert sorted(np.bincount(etq)) == [456, 849, 1038, 1389]
        BV.G_["etq"] = etq
        tareas = [(m, "comun", r) for r in range(nrep) for m in ["m3", "m4", "m4p"]]
        nombre = lambda t, de_fila=False: (f"{t['modelo']}_{t['variante']}_{t['replica']}" if de_fila
                                           else f"{t[0]}_{t[1]}_{t[2]}")
        _ejecutar(tareas, tarea_costo, out, nombre, procesos)
    elif modo == "cobertura":
        tabla = pd.read_csv(sys.argv[6]).set_index("B")
        Bs = [float(x) for x in sys.argv[7:]]
        PAR["tabla"] = tabla
        CC._preparar_equidad(raiz, Bs)
        CC.EQ["etq"], _ = CL.clusters(CC.EQ["hog"], raiz)
        tareas = [(m, r) for r in range(nrep) for m in ["m3", "m4", "m4p"]]
        sufijo = "_".join(f"{b:g}" for b in Bs)
        nombre = lambda t, de_fila=False: (f"{t['modelo']}_{t['replica']}_B{sufijo}" if de_fila
                                           else f"{t[0]}_{t[1]}_B{sufijo}")
        _ejecutar(tareas, tarea_cobertura, out, nombre, procesos)


if __name__ == "__main__":
    main()
