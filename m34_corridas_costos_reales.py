# -*- coding: utf-8 -*-
"""
m34_corridas_costos_reales.py — Repite las corridas clave de M3/M4 con costos reales (4-nov-2026).

Costos: `m34_costos_reales.cargar_costos` con fuente="provisional" (reconstruccion validada contra
el DANE). El conteo de Martin solo entra si se pide fuente="martin" (auditoria 4-nov, hallazgo 2). V = u*HW (cobertura), K = costo_hogar*HW (pesos).
Todo lo demas es identico a las corridas u1 del 3-nov (mismo sorteo R, mismos clusters k = 4,
desempate, rezago no intervenible, reintento sin presolve), para que la comparacion u1 vs real
sea pareada replica por replica.

Modos:
  barrido  curva costo-meta 2-30 % (como m34_barrido_metas_v2), variante "real"
  equidad  objetivo de equidad del M1 (como m34_correr_equidad), B en mil millones, rho {0, 0,10}
  ip       referencia con informacion perfecta (como m34_referencia_info_perfecta)

Uso:
  python3 m34_corridas_costos_reales.py barrido <raiz> <n_rep> <dir_salida>
  python3 m34_corridas_costos_reales.py equidad <raiz> <n_rep> <salida.csv> B1 B2 ...
  python3 m34_corridas_costos_reales.py ip      <raiz> <salida.csv> B1 B2 ...
"""
import sys
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import pandas as pd

import m34_barrido_metas_v2 as BV
import m34_costos_reales as CR
import m34_datos as D
import m34_equidad as E
import m34_mecanismo as X

EQ = {}


def _preparar_barrido(raiz):
    BV.preparar(raiz)
    V, K, fuente = CR.cargar_costos(BV.G_["hog"], raiz)
    BV.G_["Kp"] = K                      # metricas y gasto por dimension en pesos reales
    BV.G_["var"]["real"] = (V, K)
    print("fuente de costos:", fuente, flush=True)


def barrido(raiz, nrep, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    _preparar_barrido(raiz)
    tareas = [(m, "real", rep) for rep in range(nrep) for m in ["m3", "m4"]]
    hechas = {p.stem for p in out.glob("*.csv")}
    tareas = [t for t in tareas if f"{t[0]}_{t[1]}_{t[2]}" not in hechas]
    print(len(tareas), "tareas", flush=True)
    # fork: las tareas heredan G_ (o EQ) del proceso padre; con spawn (defecto en macOS) llegan vacios
    with get_context("fork").Pool(2) as pool:
        for filas in pool.imap_unordered(BV.tarea, tareas):
            f0 = filas[0]
            pd.DataFrame(filas).to_csv(out / f"{f0['modelo']}_{f0['variante']}_{f0['replica']}.csv", index=False)
            print(time.strftime("%H:%M:%S"), f0["modelo"], f0["replica"],
                  round(sum(x["segundos"] for x in filas), 1), flush=True)


def _preparar_equidad(raiz, Bs):
    import m34_clusters as CL
    from m34_montecarlo import matriz_grupo
    hog = D.cargar(raiz)
    b = D.verificar_linea_base(hog)
    M, HS, HW, w = D.matrices(hog)
    etq, _ = CL.clusters(hog, raiz)
    assert sorted(np.bincount(etq)) == [456, 849, 1038, 1389]
    V, K, fuente = CR.cargar_costos(hog, raiz)
    EQ.update(hog=hog, b=b, M=M, HS=HS, HW=HW, w=w, V=V, K=K, Bs=Bs, celda=hog.CELDA.to_numpy(),
              G={"m3": matriz_grupo(hog, "m3"), "m4": matriz_grupo(hog, "m4", etq)},
              dat=E.preparar(M, w, HS, HW, hog.CELDA.to_numpy()))
    print("fuente de costos:", fuente, flush=True)


def tarea_equidad(args):
    mod, rep = args
    g = EQ
    R = D.sortear_R(g["hog"], rep)
    info = X.enumerar_cortes(g["M"], R, g["V"], g["K"], g["G"][mod], excluir=(D.IND.index("rezago_escolar"),),
                             pobre0=g["dat"]["pobre0"])
    filas = []
    for B in g["Bs"]:
        for rho in [0.0, 0.10]:
            s = E.resolver(info, g["dat"], B=B * 1e3, rho=rho)
            f = dict(modelo=mod, replica=rep, B=B, rho=rho, estado=s["estado"], segundos=s["segundos"],
                     costos="real", estado_highs=s.get("estado_highs"),
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


def equidad(raiz, nrep, salida, Bs):
    _preparar_equidad(raiz, Bs)
    tareas = [(m, r) for r in range(nrep) for m in ["m3", "m4"]]
    # fork: las tareas heredan G_ (o EQ) del proceso padre; con spawn (defecto en macOS) llegan vacios
    with get_context("fork").Pool(2) as pool:
        for filas in pool.imap_unordered(tarea_equidad, tareas):
            pd.DataFrame(filas).to_csv(salida, mode="a", header=not Path(salida).exists(), index=False)
            print(time.strftime("%H:%M:%S"), filas[0]["modelo"], filas[0]["replica"],
                  [round(f.get("personas_salen", 0)) for f in filas], flush=True)


def ip(raiz, salida, Bs):
    import m34_referencia_info_perfecta as IP
    hog = D.cargar(raiz)
    D.verificar_linea_base(hog)
    M, HS, HW, w = D.matrices(hog)
    dat = E.preparar(M, w, HS, HW, hog.CELDA.to_numpy())
    _, K, fuente = CR.cargar_costos(hog, raiz)
    intervenible = np.array([j != "rezago_escolar" for j in D.IND])
    filas = []
    for B in Bs:
        for rho in [0.0, 0.10]:
            r = IP.resolver(dat, K, B * 1e3, rho, intervenible)
            filas.append(dict(modelo="info_perfecta", B=B, rho=rho, costos="real", **r))
            print(filas[-1], flush=True)
    pd.DataFrame(filas).to_csv(salida, index=False)


if __name__ == "__main__":
    modo = sys.argv[1]
    if modo == "barrido":
        barrido(sys.argv[2], int(sys.argv[3]), sys.argv[4])
    elif modo == "equidad":
        equidad(sys.argv[2], int(sys.argv[3]), sys.argv[4], [float(x) for x in sys.argv[5:]])
    elif modo == "ip":
        ip(sys.argv[2], sys.argv[3], [float(x) for x in sys.argv[4:]])
