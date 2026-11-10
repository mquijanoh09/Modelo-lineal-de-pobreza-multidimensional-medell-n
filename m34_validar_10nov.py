# -*- coding: utf-8 -*-
"""
m34_validar_10nov.py — Compatibilidad de M3/M4 con el M1/M2 de Martín de main (10-nov).

Reemplaza a m34_validar_escenario_comun.py (5-nov), que usaba la API de modelos-1-2. Comprueba que,
en el escenario común (sin E-7 ni SevEdu, meta global, desempleo no imputado), lo único que cambia
entre la información perfecta y M3/M4 es la información.

V1  Línea base idéntica: mismos 523 pobres, mismas privaciones, M0, Sev0 y población.
V2  Par por par (hogares pobres): intervenible en costos_comunes == quitable del M1, y para los
    indicadores que el M1 paga por par (d.c) el costo es el mismo.
V4  Rezago: cuántos pares el M1 podría quitar (en M3/M4 es fijo por decisión del 2-nov).
V5  Granularidad máxima: M3 con UN grupo por hogar = M2 (objetivo del paper) y = M1 (equidad),
    salvo la desviación declarada (CLEI compartido entre logro y analfabetismo).
Uso: python3 m34_validar_10nov.py <carpeta Modelos/ de Martín> [salida.csv]
"""
import sys
import time
import warnings

import numpy as np
import pandas as pd

import m34_compat_martin as CM
import m34_costos_reales as CR
import m34_datos as D3
import m34_equidad as E
import m34_mecanismo as X

warnings.simplefilter("ignore")
RAIZ = "data/DANE/DEPARTAMENTAL"
METAS_V5 = [0.02, 0.06, 0.10, 0.20, 0.30]
B_V5 = [2.0, 10.0, 50.0]
FILAS = []


def registrar(prueba, ok, detalle):
    FILAS.append(dict(prueba=prueba, ok=bool(ok), detalle=detalle))
    print(("OK   " if ok else "FALLA"), prueba, "|", detalle, flush=True)


def main():
    dm = sys.argv[1]
    salida = sys.argv[2] if len(sys.argv) > 2 else "resultados/m34/validacion_10nov.csv"
    d = CM.datos_comun(dm)

    hog = D3.cargar(RAIZ)
    b = D3.verificar_linea_base(hog)
    M, HS, HW, w = D3.matrices(hog)
    ids = (hog.DIRECTORIO.astype(str) + "_" + hog.SECUENCIA_P.astype(str)).to_numpy()
    pos = {k: n for n, k in enumerate(ids)}

    # V1 ----------------------------------------------------------------------------------------
    pob3 = set(ids[b["pobre0"] == 1])
    pob1 = set(d.hogares.index)
    registrar("V1 mismos hogares pobres", pob1 == pob3, f"M1/M2 {len(pob1)}, M3/M4 {len(pob3)}")
    priv_ok = all(set(d.J[i]) == {D3.IND[j] for j in np.where(M[pos[i]] == 1)[0]} for i in pob1)
    registrar("V1 mismas privaciones", priv_ok, "J_i del M1 = M_ij de M3/M4 en los 523 pobres")
    H0, A0, M0 = d.linea_base
    registrar("V1 mismo M0", abs(M0 - b["M0"]) < 1e-12, f"M1/M2 {M0:.9f}, M3/M4 {b['M0']:.9f}")
    pob_tot = float(d.todos.p.sum())
    registrar("V1 misma poblacion", abs(pob_tot - b["pers"].sum()) / pob_tot < 1e-12, f"{pob_tot:,.1f} personas")
    s0 = np.round(M @ w, 2)
    sev3 = float((b["pers"] * b["pobre0"] * s0 ** 2).sum())
    registrar("V1 misma severidad inicial", abs(d.Sev0 - sev3) / sev3 < 1e-9, f"Sev0 {d.Sev0:,.1f} vs {sev3:,.1f}")

    # V2 ----------------------------------------------------------------------------------------
    cc = pd.read_csv(CR.RUTA_COMUN, dtype={"ID_HOGAR": str})
    cc = cc[cc.ID_HOGAR.isin(pob1)].set_index(["ID_HOGAR", "indicador"])
    claves = set(d.quitable)
    registrar("V2 mismos pares privados (pobres)", claves == set(cc.index), f"{len(claves)} pares")
    for nombre, filtro in [("sin rezago", lambda j: j != "rezago_escolar"), ("rezago", lambda j: j == "rezago_escolar")]:
        ks = [k for k in claves if filtro(k[1])]
        dif = [k for k in ks if bool(cc.at[k, "intervenible"]) != bool(d.quitable[k])]
        por = pd.Series([k[1] for k in dif]).value_counts().to_dict() if dif else {}
        registrar(f"V2 mismo 'se puede quitar' ({nombre})", not dif or nombre == "rezago",
                  f"{len(ks)} pares, {len(dif)} distintos {por}")
    errs = []
    for k, c in d.c.items():
        if bool(d.quitable[k]):
            v = cc.at[k, "costo_hogar"] * d.hogares.at[k[0], "HW"]
            errs.append(abs(v - c) / c)
    registrar("V2 mismo costo en los pares que el M1 paga por par", max(errs) < 1e-9,
              f"{len(errs)} pares, error relativo máximo {max(errs):.1e}")

    # V4 ----------------------------------------------------------------------------------------
    rez = [k for k in claves if k[1] == "rezago_escolar"]
    q = sum(bool(d.quitable[k]) for k in rez)
    registrar("V4 rezago no quitable en un año", q == 0, f"el M1 podría quitar {q} de {len(rez)} pares de rezago")

    # V5 ----------------------------------------------------------------------------------------
    V, K, _ = CR.cargar_costos(hog, RAIZ, fuente="comun")
    F = CR.pares_fijos(hog, "comun")
    G = np.repeat(np.arange(len(hog))[:, None], len(D3.IND), 1)
    R = D3.sortear_R(hog, 0)
    info = X.enumerar_cortes(M, R, V, K, G, excluir=(D3.IND.index("rezago_escolar"),), pobre0=b["pobre0"], fijos=F)
    for m in METAS_V5:
        t0 = time.time()
        ip = CM.m2_costo(dm, d, m)
        r = X.resolver_paper(M, w, b["pers"], b["pobre0"], b["M0"], info, m, tmax=600)
        g, i2 = r["obj"] / 1e3, ip["costo"] / 1e9
        registrar(f"V5 granularidad maxima, meta {m:.0%}",
                  r["estado"] == "Optimal" and ip["estado"] == "Optimal" and g >= i2 * (1 - 1e-6),
                  f"M3 un grupo por hogar ${g:.3f} mm vs M2 ${i2:.3f} mm (exceso {100 * (g / i2 - 1):.2f} %, "
                  f"{time.time() - t0:.0f} s)")
    dat = E.preparar(M, w, HS, HW, hog.CELDA.to_numpy())
    for B in B_V5:
        h1 = CM.m1_personas(dm, d, B * 1e9)
        s = E.resolver(info, dat, B=B * 1e3, rho=0.0, tiempo=600)
        registrar(f"V5 granularidad maxima, equidad B = {B:g}",
                  s["estado"] == "Optimal" and h1["estado"] == "Optimal" and s["H_star"] <= h1["personas_salen"] * (1 + 1e-6),
                  f"M3 un grupo por hogar {s['H_star']:,.0f} personas vs M1 {h1['personas_salen']:,.0f} "
                  f"({100 * (s['H_star'] / h1['personas_salen'] - 1):.2f} %)")

    pd.DataFrame(FILAS).to_csv(salida, index=False)
    print(f"\n{sum(f['ok'] for f in FILAS)}/{len(FILAS)} pruebas OK -> {salida}")


if __name__ == "__main__":
    main()
