# -*- coding: utf-8 -*-
"""
m34_clusters.py — Conjunto T del Modelo 4 (k-means, k = 4), reimplementacion fiel de
07_clusters.py: rasgos que el Estado SI observa (tipo Sisben), estandarizados,
ponderados por FEX_C, random_state = 2026, n_init = 10.

Regresion esperada (22-oct): tamaños {1389, 1038, 849, 456}.
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from m34_datos import SEMILLA, _csv

RASGOS = ["n_personas", "n_menores5", "n_5a17", "n_mayores65",
          "tasa_dependencia", "edad_jefe", "jefe_mujer", "educ_jefe"]


def rasgos(hog, raiz_dep):
    per = pd.read_csv(_csv(raiz_dep, "PERSONAS (DEPARTAMENTAL) 2025"), encoding="utf-8-sig",
                      usecols=["DIRECTORIO", "SECUENCIA_P", "ORDEN", "P6020", "P6040", "P6051", "P8587"])
    for c in ["P6020", "P6040", "P6051", "P8587"]:
        per[c] = pd.to_numeric(per[c], errors="coerce")
    llave = ["DIRECTORIO", "SECUENCIA_P"]
    per = per.merge(hog[llave], on=llave, how="inner")
    per["m5"] = (per.P6040 < 5).astype(int)
    per["e5a17"] = ((per.P6040 >= 5) & (per.P6040 <= 17)).astype(int)
    per["adu"] = ((per.P6040 >= 15) & (per.P6040 < 65)).astype(int)
    per["m65"] = (per.P6040 >= 65).astype(int)
    per["dep"] = ((per.P6040 < 15) | (per.P6040 >= 65)).astype(int)
    comp = per.groupby(llave).agg(n_menores5=("m5", "sum"), n_5a17=("e5a17", "sum"),
                                  n_adultos=("adu", "sum"), n_mayores65=("m65", "sum"),
                                  n_dependientes=("dep", "sum")).reset_index()
    jefe = per[per.P6051 == 1].groupby(llave).agg(edad_jefe=("P6040", "first"),
                                                  sexo_jefe=("P6020", "first"),
                                                  educ_jefe=("P8587", "first")).reset_index()
    r = hog[llave + ["PERSONAS", "FEX_C"]].merge(comp, on=llave, how="left").merge(jefe, on=llave, how="left")
    r["n_personas"] = r.PERSONAS
    r["jefe_mujer"] = (r.sexo_jefe == 2).astype(int)
    r["tasa_dependencia"] = r.n_dependientes / r.n_adultos.clip(lower=1)
    r["educ_jefe"] = r.educ_jefe.fillna(r.educ_jefe.median())
    assert r[RASGOS].notna().all().all()
    assert len(r) == len(hog)
    return r


def clusters(hog, raiz_dep, k=4):
    r = rasgos(hog, raiz_dep)
    X = StandardScaler().fit_transform(r[RASGOS].to_numpy(float))
    etq = KMeans(n_clusters=k, random_state=SEMILLA, n_init=10).fit_predict(
        X, sample_weight=r.FEX_C.to_numpy(float))
    # mismo orden de filas que hog (merge left conserva el orden)
    return etq, r


def nombrar(r, etq):
    """Nombre interpretable por el rasgo dominante del centroide."""
    g = r.assign(CL=etq).groupby("CL")[RASGOS].mean()
    nombres = {}
    for c, f in g.iterrows():
        if f.n_menores5 >= 0.8:
            nombres[c] = "Primera infancia"
        elif f.n_mayores65 >= 0.8:
            nombres[c] = "Adultos mayores"
        elif f.n_5a17 >= 1.0:
            nombres[c] = "Con hijos escolares"
        else:
            nombres[c] = "Adultos sin dependientes"
    return nombres
