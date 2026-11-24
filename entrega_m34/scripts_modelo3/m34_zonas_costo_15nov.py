# -*- coding: utf-8 -*-
"""
m34_zonas_costo_15nov.py — Repite las corridas de costo del 12-nov (meta de M0 en cada zona) para guardar, además
de lo de siempre, los valores finales de H, A y M0 POR ZONA (PLAN_INTEGRACION_M3_M4.md de Martín, §5, punto 4).

No cambia ningún modelo: solo agrega columnas a X.metricas antes de lanzar m34_comparacion_12nov (modo costo).
El sorteo R se deriva del hogar y de la réplica, así que las soluciones son las mismas del 12-nov; el script
scripts/m34_datos_paper.py comprueba que el costo de cada corrida coincide con costo_meta_zona_crudo_12nov.csv.

Uso: python3 m34_zonas_costo_15nov.py <raiz> <n_rep> <salida/> <procesos>
"""
import sys

import numpy as np

import m34_comparacion_12nov as C
import m34_mecanismo as X

_metricas = X.metricas


def metricas_zona(cub, N1, M, w, HS, HW, pobre0, celda, Kpesos=None):
    out = _metricas(cub, N1, M, w, HS, HW, pobre0, celda, Kpesos=Kpesos)
    pers = HS * HW
    score1 = np.round(N1 @ w, 2)
    pobre1 = (score1 >= 1 / 3).astype(int)
    out["A1"] = (pers * pobre1 * score1).sum() / (pers * pobre1).sum()
    for d in np.unique(celda):
        s = celda == d
        pob = pers[s].sum()
        Hd = (pers[s] * pobre1[s]).sum() / pob
        M0d = (pers[s] * pobre1[s] * score1[s]).sum() / pob
        out[f"M01_{d}"] = M0d
        out[f"A1_{d}"] = M0d / Hd if Hd > 0 else np.nan
    return out


X.metricas = metricas_zona

if __name__ == "__main__":
    sys.argv = [sys.argv[0], "costo"] + sys.argv[1:]
    C.main()
