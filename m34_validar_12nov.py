# -*- coding: utf-8 -*-
"""
m34_validar_12nov.py — Validaciones de granularidad máxima de la especificación del 12-nov (§4.4).

Con UN grupo por hogar el sorteo no tiene a quién más asignar la cobertura, así que M3 debe reproducir la
información perfecta con las MISMAS restricciones nuevas:
  G1  M3 con meta de M0 en cada zona  ==  M2 sin E-7 con meta por zona (info_perfecta_meta_zona.csv)
  G2  M3 con piso por zona r_B         ==  M1 sin E-7 ni SevEdu con r_B (r_rho_comparacion.csv)
Diferencia admitida (declarada): el ciclo CLEI que en el M1 quita a la vez logro y analfabetismo; en M3/M4
cada par se costea por separado, así que M3 puede salir algo más caro (G1) o sacar algo menos (G2), nunca al revés.
Uso: python3 m34_validar_12nov.py <carpeta con r_rho_comparacion.csv e info_perfecta_meta_zona.csv> <salida.csv>
"""
import sys

import numpy as np
import pandas as pd

import m34_costos_reales as CR
import m34_datos as D
import m34_equidad as E
import m34_mecanismo as X

RAIZ = "data/DANE/DEPARTAMENTAL"


def main(carpeta, salida):
    ref_m = pd.read_csv(f"{carpeta}/info_perfecta_meta_zona.csv").set_index("meta")
    ref_b = pd.read_csv(f"{carpeta}/r_rho_comparacion.csv").set_index("B")
    hog = D.cargar(RAIZ)
    b = D.verificar_linea_base(hog)
    M, HS, HW, w = D.matrices(hog)
    V, K, _ = CR.cargar_costos(hog, RAIZ, fuente="comun")
    F = CR.pares_fijos(hog, "comun")
    G = np.repeat(np.arange(len(hog))[:, None], len(D.IND), 1)
    info = X.enumerar_cortes(M, D.sortear_R(hog, 0), V, K, G, excluir=(D.IND.index("rezago_escolar"),),
                             pobre0=b["pobre0"], fijos=F)
    zona = hog.CELDA.to_numpy()
    filas = []
    for meta in [0.02, 0.06, 0.10, 0.20, 0.30]:
        r = X.resolver_paper(M, w, b["pers"], b["pobre0"], b["M0"], info, meta, tmax=600, zona=zona)
        g3, ip = r["obj"] / 1e3, ref_m.loc[round(meta, 2), "costo_mm"]
        exceso = 100 * (g3 / ip - 1)
        filas.append(dict(prueba=f"G1 meta por zona {meta:.0%}", ok=r["estado"] == "Optimal" and exceso >= -1e-4,
                          M3_granular=g3, info_perfecta=ip, diferencia_pct=exceso))
        print(filas[-1], flush=True)
    dat = E.preparar(M, w, HS, HW, zona)
    for B, rr in ref_b.iterrows():
        s = E.resolver(info, dat, B=B * 1e3, r=float(rr.r_B), rho=0.0, tiempo=600, gap2=1e-6)
        h1 = rr.M1_salen_r
        dif = 100 * (s["H_star"] / h1 - 1) if s["estado"] == "Optimal" else np.nan
        filas.append(dict(prueba=f"G2 piso por zona r_B, B = {B:g}", ok=s["estado"] == "Optimal" and dif <= 1e-4,
                          M3_granular=s.get("H_star"), info_perfecta=h1, diferencia_pct=dif))
        print(filas[-1], flush=True)
    t = pd.DataFrame(filas)
    t.to_csv(salida, index=False)
    print(f"\n{int(t.ok.sum())}/{len(t)} validaciones OK")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
