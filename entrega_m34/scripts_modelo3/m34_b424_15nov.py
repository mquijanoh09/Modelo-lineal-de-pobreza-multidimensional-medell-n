# -*- coding: utf-8 -*-
"""
m34_b424_15nov.py — Puente entre la comparación de los cuatro modelos y el caso base del paper (B = $424 mil
millones), decidido por Jerónimo el 15-nov (opción B del PLAN_INTEGRACION_M3_M4.md, §6.3, con un puente).

No cambia ningún modelo: agrega B = 424 a las dos corridas que sí son factibles con información imperfecta.

  ref   Referencias de información perfecta con las funciones de Martín (main, sin cambiarlas), en el escenario de
        la comparación (sin E-7 ni SevEdu): r_B por el codo, rho_B por la regla de la brecha, personas que salen
        con el M1 con r_B y con r = 0.
  ipmax Piso máximo garantizable con información perfecta: M3 con un hogar por celda (como m34_tablas_12nov).
  rmax  Piso máximo garantizable de M3, M4 y placebo, 100 réplicas (m34_rmax_12nov.main con B = 424).
La sensibilidad con r = 0 de M3, M4 y placebo se corre con m34_equidad_comun.py (30 réplicas, B = 424).

Uso:
  python3 m34_b424_15nov.py ref   <Modelos/ de main> <salida.csv>
  python3 m34_b424_15nov.py ipmax <salida.csv>
  python3 m34_b424_15nov.py rmax  <n_rep> <r_rho_424.csv> <salida.csv>
"""
import sys
import time

import numpy as np
import pandas as pd

B = 424.0
RAIZ = "data/DANE/DEPARTAMENTAL"


def ref(dm, salida):
    import m34_compat_martin as CM
    P, _, _, resolver_dos_etapas, _ = CM.cargar(dm)
    from Modelo_1.modelo1 import resolver_r, rho_regla_brecha
    d = CM.datos_comun(dm)
    t0 = time.time()
    r, _ = resolver_r(d, B * 1e9, "codo", rho_e=None, gap_rel=1e-6, time_limit=600)
    print("r_B", r, round(time.time() - t0), "s", flush=True)
    rho, inf_rho = (rho_regla_brecha(d, B * 1e9, r=r, rho_e=None, gap_rel=1e-6, time_limit=600)
                    if r is not None else (None, {"motivo": "sin r"}))
    print("rho_B", rho, inf_rho, round(time.time() - t0), "s", flush=True)
    f = dict(B=B, r_B=r, rho_B=rho, nota_rho=str(inf_rho.get("motivo", inf_rho.get("nota", ""))))
    for etiqueta, rr, rh in [("r", r, None), ("r0", 0.0, None)]:
        m, info = resolver_dos_etapas(d, B * 1e9, r=rr, rho=rh, rho_e=None, gap_rel=1e-6, time_limit=600)
        ok = info["etapa2"] is not None and info["etapa2"]["estado"] == "Optimal"
        f[f"M1_salen_{etiqueta}"] = float(m.recalcular().loc["total", "salen_personas"]) if ok else float("nan")
        f[f"M1_estado_{etiqueta}"] = "Optimal" if ok else info["etapa1"]["estado"]
        print(etiqueta, f[f"M1_salen_{etiqueta}"], f[f"M1_estado_{etiqueta}"], flush=True)
    f["segundos"] = round(time.time() - t0, 1)
    pd.DataFrame([f]).to_csv(salida, index=False)
    print(f, flush=True)


def ipmax(salida):
    import m34_costos_reales as CR
    import m34_datos as D
    import m34_equidad as E
    import m34_mecanismo as X
    from m34_rmax_12nov import r_max
    hog = D.cargar(RAIZ)
    b = D.verificar_linea_base(hog)
    M, HS, HW, w = D.matrices(hog)
    V, K, _ = CR.cargar_costos(hog, RAIZ, fuente="comun")
    F = CR.pares_fijos(hog, "comun")
    G = np.repeat(np.arange(len(hog))[:, None], len(D.IND), 1)          # un hogar por celda
    info = X.enumerar_cortes(M, D.sortear_R(hog, 0), V, K, G, excluir=(D.IND.index("rezago_escolar"),),
                             pobre0=b["pobre0"], fijos=F)
    dat = E.preparar(M, w, HS, HW, hog.CELDA.to_numpy())
    filas = []
    for BB in [2, 5, 10, 25, 50, 100, B]:                              # 2 a 100 reproducen los del 12-nov
        t0 = time.time()
        t, gap = r_max(info, dat, BB, tiempo=600)
        filas.append(dict(B=BB, IP_max=t, gap=gap, segundos=round(time.time() - t0, 1)))
        print(filas[-1], flush=True)
        pd.DataFrame(filas).to_csv(salida, index=False)


if __name__ == "__main__":
    modo = sys.argv[1]
    if modo == "ref":
        ref(sys.argv[2], sys.argv[3])
    elif modo == "ipmax":
        ipmax(sys.argv[2])
    elif modo == "rmax":
        import m34_rmax_12nov as RM
        RM.main(RAIZ, int(sys.argv[2]), sys.argv[3], sys.argv[4])
