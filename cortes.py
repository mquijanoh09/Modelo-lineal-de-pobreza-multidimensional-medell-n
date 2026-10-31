# -*- coding: utf-8 -*-
"""
cortes.py — El mecanismo de focalizacion por cortes de prefijo, SEPARADO del objetivo.

Por que existe este archivo
---------------------------
En 06_modelo3_cortes.py el mecanismo (sorteo -> orden -> cortes factibles) y el
modelo del paper (min esfuerzo s.a. meta de M0) estaban mezclados, y un mismo
numero, HS_i, hacia dos trabajos a la vez:
    1. medir la COBERTURA  p_jd = cum(c) / Den_jd
    2. medir el ESFUERZO   E_jd = EF_j * cum(c)
Con los costos de Martin esos dos trabajos se separan:
    v_ij = u_ij * HW_i     personas reales afectadas  -> cobertura
    k_ij = costo_ij        pesos (EpF_j^zona * u_ij * HW_i, o la formula de empleo) -> costo
En empleo formal o rezago el costo por persona cambia de un hogar a otro, asi que
no se puede seguir usando un solo numero.

Aqui solo vive el mecanismo. El objetivo (paper: min costo s.a. M0; o equidad:
max salidas s.a. presupuesto y techos) se arma afuera con las expresiones que
devuelve `expresiones_lineales`. Asi el mismo mecanismo sirve para los dos
objetivos y para el Modelo 4 (se cambia la columna de agrupacion: zona o cluster).

Por que la propiedad de prefijo no depende de los pesos
-------------------------------------------------------
Dentro de una celda, el hogar i se cura  <=>  R_ij <= p_jd, y p_jd es UN numero.
Eso solo usa el ORDEN de los R, no los pesos. Los pesos solo cambian cuanto sube
p con cada hogar que entra al corte: si v_ij > 0, cum_v(c) es estrictamente
creciente y la condicion de auto-consistencia
    R_(c) <= p(c) <= R_(c+1) - eps,     p(c) = cum_v(c) / Den_jd
sigue siendo verificable de antemano, corte por corte.
"""
import sys

import numpy as np
import pulp


def enumerar_cortes(M, R, V, K, grupo, elig=None, eps=1e-6, minimo_grupos=2):
    """Para cada (indicador j, grupo g) con privados: orden por R y cortes factibles.

    M, R, V, K, elig : arrays (n_hogares, n_indicadores)
        M    privacion inicial 0/1
        R    sorteo U[0,1] (fijo dentro de una corrida de Monte Carlo)
        V    peso de COBERTURA (u_ij * HW_i); solo se lee donde M = 1
        K    peso de COSTO en pesos (costo_ij); solo se lee donde M = 1
        elig 1 si cubrir al hogar SI le quita la privacion; 0 si el Estado paga
             pero la privacion sigue (rezago no nivelable este año). Por defecto 1.
    grupo : array (n_hogares,) con la celda (zona P3) o el cluster.

    Devuelve dict {(jj, g): {orden, Den, cumV, cumK, F, n, elig}}.
    """
    M = np.asarray(M, float)
    n, J = M.shape
    V = np.asarray(V, float)
    K = np.asarray(K, float)
    elig = np.ones_like(M) if elig is None else np.asarray(elig, float)
    grupo = np.asarray(grupo)

    grupos = sorted(np.unique(grupo))
    if len(grupos) < minimo_grupos:
        sys.exit(f"\n*** {len(grupos)} grupo(s): sin focalizacion por grupo no hay Modelo 3/4.\n")

    act = M == 1
    # Un peso de cobertura 0 haria que dos cortes tengan la misma p: el prefijo
    # quedaria ambiguo. Un costo negativo no tiene sentido. Mejor fallar aqui.
    if np.any(V[act] <= 0):
        raise ValueError(f"{int((V[act] <= 0).sum())} pares privados con peso de cobertura <= 0")
    if np.any(K[act] < 0):
        raise ValueError(f"{int((K[act] < 0).sum())} pares privados con costo negativo")

    info = {}
    for jj in range(J):
        for g in grupos:
            idx = np.where((grupo == g) & act[:, jj])[0]
            if idx.size == 0:
                continue                                   # nadie privado en j dentro de g
            orden = idx[np.argsort(R[idx, jj], kind="stable")]
            Rs = R[orden, jj]
            if np.any(np.diff(Rs) == 0):
                print(f"    aviso: empate exacto en R (j={jj}, g={g}): prefijo ambiguo")

            v = V[orden, jj]
            cumV = np.concatenate([[0.0], np.cumsum(v)])  # cobertura acumulada, c = 0..n
            cumK = np.concatenate([[0.0], np.cumsum(K[orden, jj])])  # costo acumulado
            Den = cumV[-1]
            m = orden.size

            F = []
            for c in range(m + 1):
                p = cumV[c] / Den
                ok_abajo = (c == 0) or (Rs[c - 1] <= p)          # el ultimo cubierto: R <= p
                ok_arriba = (c == m) or (p <= Rs[c] - eps)        # el primero no cubierto: p < R
                if ok_abajo and ok_arriba:
                    F.append(c)
            info[(jj, g)] = dict(orden=orden, Den=Den, cumV=cumV, cumK=cumK,
                                 F=F, n=m, elig=elig[orden, jj])
    return info


def variables_z(info, nombre="z"):
    """Una binaria por corte factible."""
    return {(jj, g, c): pulp.LpVariable(f"{nombre}_{jj}_{g}_{c}".replace(" ", ""), cat="Binary")
            for (jj, g), v in info.items() for c in v["F"]}


def restricciones_corte_unico(modelo, info, z, prefijo="C1"):
    """C1: cada (indicador, grupo) escoge exactamente un corte (c = 0 es 'no hacer nada')."""
    for (jj, g), v in info.items():
        modelo += pulp.lpSum(z[(jj, g, c)] for c in v["F"]) == 1, f"{prefijo}_{jj}_{g}".replace(" ", "")


def expresiones_lineales(info, z):
    """N_ij y costo por (j, g) como expresiones lineales en z.

    N_ij = 1 - elig_ij * sum_{c >= rank_ij} z[j,g,c]
        El hogar de rango k queda cubierto si el corte es c >= k. Si no es elegible,
        queda cubierto (y se paga) pero N_ij = 1: la privacion sigue.
    Costo_jg = sum_c cumK(c) * z[j,g,c]
        Incluye a TODOS los cubiertos, pobres y no pobres: ahi esta el error de inclusion.
    """
    Nexp, Kexp = {}, {}
    for (jj, g), v in info.items():
        for k, i in enumerate(v["orden"], start=1):
            if v["elig"][k - 1] == 1:
                Nexp[(i, jj)] = 1 - pulp.lpSum(z[(jj, g, c)] for c in v["F"] if c >= k)
            else:
                Nexp[(i, jj)] = 1
        Kexp[(jj, g)] = pulp.lpSum(v["cumK"][c] * z[(jj, g, c)] for c in v["F"])
    return Nexp, Kexp


def reconstruir(info, z, M):
    """Despues de resolver: cortes elegidos, matriz de cubiertos y N final."""
    cubierto = np.zeros_like(M, dtype=float)
    Npost = np.asarray(M, float).copy()
    corte = {}
    for (jj, g), v in info.items():
        c_sel = next(c for c in v["F"] if round(z[(jj, g, c)].value()) == 1)
        corte[(jj, g)] = c_sel
        for k, i in enumerate(v["orden"], start=1):
            if c_sel >= k:
                cubierto[i, jj] = 1
                if v["elig"][k - 1] == 1:
                    Npost[i, jj] = 0
    return corte, cubierto, Npost
