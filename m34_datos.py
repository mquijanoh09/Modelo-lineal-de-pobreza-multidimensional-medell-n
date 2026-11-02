# -*- coding: utf-8 -*-
"""
m34_datos.py — Carga del universo de los Modelos 3 y 4 (Antioquia completa, D = P3)
y sorteo R_ij. Autocontenido: no importa nada de los scripts 05/06, pero reproduce
exactamente sus convenciones (mismos IND, W, K_GRID, EPS y semilla por hogar).

Pruebas de regresion (deben pasar SIEMPRE, ver verificar_linea_base):
    3.732 hogares | 523 pobres | H0 = 0,0945 | M0 = 0,038684 | 7.231.754 personas
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEMILLA = 2026
EPS = 1e-6           # mismo eps de 05 y de la enumeracion de cortes: si cambia uno, cambia el otro
K_GRID = 0.33        # 'puntaje < 1/3' <=> 'puntaje <= 0.33' (pesos multiplos de 0.01)

IND = ["logro_educativo", "analfabetismo",
       "inasistencia_escolar", "rezago_escolar", "atencion_integral", "trabajo_infantil",
       "desempleo_larga_duracion", "empleo_formal",
       "aseguramiento_salud", "barreras_acceso_salud",
       "acueducto", "alcantarillado", "pisos", "paredes", "hacinamiento"]
DIMS = {"Educacion": IND[0:2], "Ninez": IND[2:6], "Trabajo": IND[6:8],
        "Salud": IND[8:10], "Vivienda": IND[10:15]}
W = {j: 0.2 / len(js) for js in DIMS.values() for j in js}
NOM_CLASE = {1: "Cabecera", 2: "Centro poblado", 3: "Rural disperso"}

# Particion del Modelo 4 (validada empiricamente el 22-oct: discriminacion por zona > por cluster)
V_PUBLICOS = ["acueducto", "alcantarillado"]
U_PRIVADOS = [j for j in IND if j not in V_PUBLICOS]


def _csv(raiz, sub):
    archivos = sorted((Path(raiz) / sub).glob("*.csv"))
    assert len(archivos) == 1, archivos
    return archivos[0]


def cargar(raiz_dep, depto=5):
    """Hogares del departamento con P3 (clase) y la celda D."""
    hog = pd.read_csv(_csv(raiz_dep, "HOGARES (DEPARTAMENTAL) 2025"), encoding="utf-8-sig",
                      low_memory=False)
    viv = pd.read_csv(_csv(raiz_dep, "VIVIENDAS (DEPARTAMENTAL) 2025"), encoding="utf-8-sig",
                      usecols=["DIRECTORIO", "P3"])
    hog = hog.merge(viv, on="DIRECTORIO", how="left", validate="many_to_one")
    for c in IND + ["PERSONAS", "FEX_C", "IPM", "POBRE", "DEPARTAMENTO", "P3"]:
        hog[c] = pd.to_numeric(hog[c].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    hog = hog[hog.DEPARTAMENTO == depto].reset_index(drop=True)
    hog["ID"] = hog.DIRECTORIO.astype(str) + "_" + hog.SECUENCIA_P.astype(str)
    hog["CELDA"] = hog.P3.map(NOM_CLASE)
    assert hog.ID.is_unique
    return hog


def matrices(hog):
    M = hog[IND].to_numpy(float)
    HS = hog.PERSONAS.to_numpy(float)
    HW = hog.FEX_C.to_numpy(float)
    w = np.array([W[j] for j in IND])
    return M, HS, HW, w


def linea_base(hog):
    M, HS, HW, w = matrices(hog)
    pers = HS * HW
    score0 = np.round(M @ w, 2)
    pobre0 = (score0 >= 1 / 3).astype(int)
    H0 = (pers * pobre0).sum() / pers.sum()
    M0 = (pers * pobre0 * score0).sum() / pers.sum()
    return dict(score0=score0, pobre0=pobre0, H0=H0, M0=M0, pers=pers,
                A0=M0 / H0, poblacion=pers.sum())


def verificar_linea_base(hog):
    b = linea_base(hog)
    assert len(hog) == 3732, len(hog)
    assert int(b["pobre0"].sum()) == 523, b["pobre0"].sum()
    assert abs(b["M0"] - 0.038684) < 5e-7, b["M0"]
    assert (b["pobre0"] == hog.POBRE.to_numpy()).all(), "POBRE del DANE no coincide"
    assert hog.CELDA.nunique() >= 2, "|D| < 2: sin focalizacion geografica no hay Modelo 3"
    return b


def sortear_R(hog, replica):
    """R_ij ~ U[0,1] con semilla derivada del ID del hogar (identica a 05_modelo3.sortear_R)."""
    R = np.empty((len(hog), len(IND)))
    for n, (d, s) in enumerate(zip(hog.DIRECTORIO, hog.SECUENCIA_P)):
        ss = np.random.SeedSequence([SEMILLA, replica, int(d), int(s)])
        R[n] = np.random.default_rng(ss).random(len(IND))
    return R
