# -*- coding: utf-8 -*-
"""
m34_base_paper_15nov.py — CSV de origen de las cifras de contexto de M34_para_paper.md que no salen de las corridas:
línea base por zona, tipos de hogar del Modelo 4 (k = 4) y razón de discriminación de cada privación entre zonas
y entre tipos de hogar. Solo lee datos; no resuelve modelos.

Uso: python3 m34_base_paper_15nov.py <data/DANE/DEPARTAMENTAL> <datos_m34/>
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import m34_clusters as CL
import m34_datos as D

ZONA = {1: "Cabeceras", 2: "Centros poblados", 3: "Rural disperso"}


def main(raiz, out):
    out = Path(out)
    hog = D.cargar(raiz)
    M, HS, HW, w = D.matrices(hog)
    b = D.verificar_linea_base(hog)
    pers = HS * HW
    score = np.round(M @ w, 2)
    pobre = (score >= 1 / 3).astype(int)
    zona = hog.P3.map(ZONA).to_numpy()
    filas = []
    for z in ["Total Antioquia"] + list(ZONA.values()):
        s = np.ones(len(hog), bool) if z == "Total Antioquia" else zona == z
        pob = pers[s].sum()
        pp = (pers[s] * pobre[s]).sum()
        filas.append(dict(zona=z, hogares=int(s.sum()), hogares_pobres=int(pobre[s].sum()), poblacion=pob,
                          personas_pobres=pp, H0=pp / pob, A0=(pers[s] * pobre[s] * score[s]).sum() / pp,
                          M0=(pers[s] * pobre[s] * score[s]).sum() / pob,
                          pares_privados=int(M[s].sum())))
    t = pd.DataFrame(filas)
    assert abs(t.M0.iloc[0] - b["M0"]) < 1e-12
    t.to_csv(out / "linea_base.csv", index=False)

    etq, r = CL.clusters(hog, raiz)
    nom = CL.nombrar(r, etq)
    tipo = np.array([nom[e] for e in etq])
    filas = []
    for n in ["Adultos sin dependientes", "Adultos mayores", "Con hijos escolares", "Primera infancia"]:
        s = tipo == n
        filas.append(dict(tipo=n, hogares=int(s.sum()), H0=(pers[s] * pobre[s]).sum() / pers[s].sum()))
    tt = pd.DataFrame(filas)
    tt.to_csv(out / "tipos_hogar.csv", index=False)

    # razón entre la incidencia de la privación (personas expandidas) en la celda más y menos privada
    filas = []
    for j, ind in enumerate(D.IND):
        fila = dict(indicador=ind)
        for nombre, part in [("zonas", zona), ("tipos", tipo)]:
            inc = [(pers[part == c] * M[part == c, j]).sum() / pers[part == c].sum() for c in np.unique(part)]
            fila[f"razon_{nombre}"] = max(inc) / min(inc) if min(inc) > 0 else np.inf
        filas.append(fila)
    pd.DataFrame(filas).to_csv(out / "discriminacion_privaciones.csv", index=False)
    print(t.round(4).to_string(), tt.round(4).to_string(), sep="\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
