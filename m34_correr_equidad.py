# -*- coding: utf-8 -*-
"""
m34_correr_equidad.py — M3 vs M4 con el objetivo de equidad del Modelo 1 (costos u = 1).

Capas de prueba (deben pasar antes de mirar resultados):
  capa 0  linea base: 523 pobres, H0 = 9,45 %, Sev0 ~ 117.908 (Martin)
  capa 1  B = 0 -> nadie sale, severidad intacta
  barrido B (mil millones de $) x replicas, r = rho = 0 y con techo rho

Uso: python3 m34_correr_equidad.py <raiz> <rep_ini> <rep_fin> <salida.csv> [B1 B2 ...]
Rezago no intervenible (caso base del 3-nov). Costos en millones de $ 2025 (u = 1).
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

import m34_datos as D
import m34_equidad as E
import m34_mecanismo as X
from m34_montecarlo import matriz_grupo, precios_u1

MIL_MILLONES = 1e3       # K esta en millones de pesos


def main():
    raiz, r0, r1, salida = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    Bs = [float(x) for x in sys.argv[5:]] or [10, 25, 50, 100]
    hog = D.cargar(raiz)
    b = D.verificar_linea_base(hog)
    M, HS, HW, w = D.matrices(hog)
    celda = hog.CELDA.to_numpy()
    import m34_clusters as K
    etq, _ = K.clusters(hog, raiz)
    G = {"m3": matriz_grupo(hog, "m3"), "m4": matriz_grupo(hog, "m4", etq)}
    Kp = precios_u1(hog)
    HWm = np.repeat(HW[:, None], 15, 1)
    dat = E.preparar(M, w, HS, HW, celda)
    # capa 0
    print(f"capa 0: pobres={len(dat['pobres'])}, Sev0={dat['Sev0']:,.0f} (Martin ~117.908), "
          f"tangentes={sum(sum(1 for a in dat['A'][i] if a > 0) for i in dat['pobres']):,}")
    excl = (D.IND.index("rezago_escolar"),)
    hechas = set()
    if Path(salida).exists():
        prev = pd.read_csv(salida)
        hechas = set(zip(prev.modelo, prev.replica, prev.B, prev.rho))
    for rep in range(r0, r1):
        R = D.sortear_R(hog, rep)
        for mod in ["m3", "m4"]:
            info = X.enumerar_cortes(M, R, HWm, Kp, G[mod], excluir=excl, pobre0=dat["pobre0"])
            if rep == r0:
                s = E.resolver(info, dat, B=0.0)
                print(f"capa 1 {mod}: B=0 -> {s['estado']}, salen={s['H_star']:.0f}")
            for B in Bs:
                for rho in [0.0, 0.10]:
                    if (mod, rep, B, rho) in hechas:
                        continue
                    s = E.resolver(info, dat, B=B * MIL_MILLONES, rho=rho)
                    f = dict(modelo=mod, replica=rep, B=B, rho=rho, estado=s["estado"],
                             segundos=s["segundos"])
                    if s["estado"] == "Optimal":
                        cub, N1 = X.reconstruir(info, s["corte"], M)
                        f.update(X.metricas(cub, N1, M, w, HS, HW, b["pobre0"], celda, Kpesos=Kp))
                        f["personas_salen"] = s["H_star"]
                        f["sev_reduccion"] = E.severidad(N1, dat)
                        gasto = (Kp * cub).sum(0)
                        for dim, js in D.DIMS.items():
                            f[f"gasto_{dim}"] = sum(gasto[D.IND.index(j)] for j in js)
                    pd.DataFrame([f]).to_csv(salida, mode="a", header=not Path(salida).exists(), index=False)
                    print(time.strftime("%H:%M:%S"), mod, rep, B, rho, s["estado"],
                          f"{f.get('personas_salen', 0):,.0f}", f"{f.get('inclusion_pesos', 0):.2f}",
                          f"{s['segundos']:.0f}s", flush=True)


if __name__ == "__main__":
    main()
