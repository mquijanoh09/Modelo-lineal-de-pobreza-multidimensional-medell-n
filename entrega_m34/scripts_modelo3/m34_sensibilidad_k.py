# -*- coding: utf-8 -*-
"""
m34_sensibilidad_k.py — ¿Depende la ventaja del Modelo 4 del numero de clusteres k? (3-nov-2026)

Pregunta de sustentacion esperada: "¿por que k = 4?". Dos respuestas complementarias:
  (a) Calidad estadistica del k-means: inercia (codo), silueta y Calinski-Harabasz.
  (b) Lo que importa para POLITICA: cuanto separan los clusteres a pobres de no pobres
      (eta^2 de la pobreza entre clusteres) y, sobre todo, el resultado del MILP.
Un k "bueno" para el k-means no es necesariamente el mejor para focalizar.

Para cada k en K_LISTA se resuelven, con las MISMAS replicas R (comparacion pareada):
  - objetivo de equidad (el del M1), B en {10, 25} mil millones, rho = 0, u = 1
  - objetivo del paper con desempate, meta 10 %, variante u1
Rezago no intervenible (caso base). M3 (k irrelevante) se corre una vez como referencia.

Uso: python3 m34_sensibilidad_k.py <raiz_DEPARTAMENTAL> <n_replicas> <dir_salida>
"""
import sys
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import calinski_harabasz_score, silhouette_score
from sklearn.preprocessing import StandardScaler

import m34_clusters as CL
import m34_datos as D
import m34_equidad as E
import m34_mecanismo as X
from m34_montecarlo import matriz_grupo, precios_u1

K_LISTA = [2, 3, 4, 5, 6, 8]
BS = [10, 25]               # mil millones de $
META_PAPER = 0.10
G_ = {}


def calidad_k(hog, raiz):
    """Metricas del k-means y de separacion de la pobreza para cada k."""
    r = CL.rasgos(hog, raiz)
    X_ = StandardScaler().fit_transform(r[CL.RASGOS].to_numpy(float))
    fw = r.FEX_C.to_numpy(float)
    b = D.linea_base(hog)
    pers, pobre = b["pers"], b["pobre0"]
    filas, etqs = [], {}
    rng = np.random.default_rng(D.SEMILLA)
    sub = rng.choice(len(X_), size=min(3000, len(X_)), replace=False)
    for k in K_LISTA:
        km = KMeans(n_clusters=k, random_state=D.SEMILLA, n_init=10).fit(X_, sample_weight=fw)
        e = km.labels_
        etqs[k] = e
        # eta^2 ponderado por personas: varianza ENTRE clusteres de la pobreza / varianza total
        H = (pers * pobre).sum() / pers.sum()
        Hc = np.array([(pers[e == c] * pobre[e == c]).sum() / pers[e == c].sum() for c in range(k)])
        Pc = np.array([pers[e == c].sum() for c in range(k)])
        eta2 = (Pc * (Hc - H) ** 2).sum() / (pers * (pobre - H) ** 2).sum()
        filas.append(dict(k=k, inercia=km.inertia_, silueta=silhouette_score(X_[sub], e[sub]),
                          calinski=calinski_harabasz_score(X_, e), eta2_pobreza=eta2,
                          H_min=Hc.min(), H_max=Hc.max(), tam_min=int(np.bincount(e).min()),
                          tamanos="/".join(map(str, sorted(np.bincount(e), reverse=True)))))
    assert sorted(np.bincount(etqs[4])) == [456, 849, 1038, 1389], "k = 4 no reproduce 07"
    return pd.DataFrame(filas), etqs


def preparar(raiz):
    hog = D.cargar(raiz)
    b = D.verificar_linea_base(hog)
    M, HS, HW, w = D.matrices(hog)
    calidad, etqs = calidad_k(hog, raiz)
    Kp = precios_u1(hog)
    G = {"m3": matriz_grupo(hog, "m3")}
    for k, e in etqs.items():
        G[f"m4_k{k}"] = matriz_grupo(hog, "m4", e)
    G_.update(hog=hog, b=b, M=M, HS=HS, HW=HW, w=w, Kp=Kp, G=G, celda=hog.CELDA.to_numpy(),
              HWm=np.repeat(HW[:, None], 15, 1), dat=E.preparar(M, w, HS, HW, hog.CELDA.to_numpy()))
    return calidad


def tarea(args):
    mod, rep = args
    g = G_
    R = D.sortear_R(g["hog"], rep)
    excl = (D.IND.index("rezago_escolar"),)
    info = X.enumerar_cortes(g["M"], R, g["HWm"], g["Kp"], g["G"][mod], excluir=excl,
                             pobre0=g["b"]["pobre0"])
    filas = []
    for B in BS:
        s = E.resolver(info, g["dat"], B=B * 1e3)
        f = dict(modelo=mod, replica=rep, objetivo="equidad", B=B, estado=s["estado"], segundos=s["segundos"],
                 pares=len(info))
        if s["estado"] == "Optimal":
            cub, N1 = X.reconstruir(info, s["corte"], g["M"])
            f.update(X.metricas(cub, N1, g["M"], g["w"], g["HS"], g["HW"], g["b"]["pobre0"], g["celda"],
                                Kpesos=g["Kp"]))
            f["personas_salen"] = s["H_star"]
            f["sev_reduccion"] = E.severidad(N1, g["dat"])
        filas.append(f)
    res = X.resolver_paper(g["M"], g["w"], g["b"]["pers"], g["b"]["pobre0"], g["b"]["M0"], info, META_PAPER,
                           solver="highs", gap=1e-6, tmax=180, desempate=True)
    f = dict(modelo=mod, replica=rep, objetivo="paper", meta=META_PAPER, estado=res["estado"],
             segundos=res["segundos"], pares=len(info))
    if res["estado"] == "Optimal":
        cub, N1 = X.reconstruir(info, res["corte"], g["M"])
        f.update(X.metricas(cub, N1, g["M"], g["w"], g["HS"], g["HW"], g["b"]["pobre0"], g["celda"],
                            Kpesos=g["Kp"]))
    filas.append(f)
    return filas


def main():
    raiz, nrep, out = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    calidad = preparar(raiz)
    calidad.to_csv(out / "calidad_k.csv", index=False)
    print(calidad.round(4).to_string(index=False), flush=True)
    tareas = [(m, rep) for rep in range(nrep) for m in G_["G"]]
    hechas = {p.stem for p in out.glob("t_*.csv")}
    tareas = [t for t in tareas if f"t_{t[0]}_{t[1]}" not in hechas]
    print(len(tareas), "tareas", flush=True)
    # fork: las tareas heredan G_ del proceso padre; con spawn (defecto en macOS) llega vacio
    with get_context("fork").Pool(2) as pool:
        for filas in pool.imap_unordered(tarea, tareas):
            f0 = filas[0]
            pd.DataFrame(filas).to_csv(out / f"t_{f0['modelo']}_{f0['replica']}.csv", index=False)
            print(time.strftime("%H:%M:%S"), f0["modelo"], f0["replica"],
                  round(sum(x["segundos"] for x in filas), 1), flush=True)


if __name__ == "__main__":
    main()
