# -*- coding: utf-8 -*-
"""
m34_referencias_comparacion.py — Lo que la especificación del 12-nov (Martín, rama Contexto, §5) pide que entregue
Martín, calculado con SUS funciones de main (sin cambiarlas), para no bloquear las corridas de M3/M4.
PROVISIONAL hasta que Martín lo confirme.

1. r_rho_comparacion.csv: para B = 2, 5, 10, 25, 50, 100 mm, r_B = codo de H contra r (Modelo_1.r_codo) y
   rho_B = regla de la brecha con r_B (Modelo_1.rho_regla_brecha); M1 sin E-7 ni SevEdu (escenario sin_E7, rho_e=None).
   Además, el techo del criterio de presupuesto: personas que salen con r_B y con r_B + rho_B.
2. info_perfecta_meta_zona.csv: M2 sin E-7 con meta de M0 en cada zona (escenario_m2("sin_E7", "base")), 15 metas.
Uso: python3 m34_referencias_comparacion.py <Modelos/> <carpeta salida>
"""
import sys
import time
from pathlib import Path

import pandas as pd

import m34_compat_martin as CM

METAS = [round(0.02 * k, 2) for k in range(1, 16)]
BS = [2, 5, 10, 25, 50, 100]


def main(dm, out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    P, _, _, resolver_dos_etapas, Modelo2 = CM.cargar(dm)
    from Modelo_1.modelo1 import resolver_r, rho_regla_brecha
    d = CM.datos_comun(dm)
    # --- 2. M2 con meta por zona (rápido) ---
    esc = P.escenario_m2("sin_E7", "base")
    assert esc["meta_por_zona"] is True and esc["usar_sevedu"] is False and esc["cobertura_art67"] is False
    filas = []
    for m in METAS:
        t0 = time.time()
        mod = Modelo2(d, esc, meta_m=m).construir()
        inf = mod.resolver(gap_rel=1e-6, time_limit=600)
        costo = float(mod.recalcular().loc["total", "costo"]) / 1e9 if inf["estado"] == "Optimal" else float("nan")
        filas.append(dict(meta=m, estado=inf["estado"], gap=inf["gap"], costo_mm=costo, segundos=round(time.time() - t0, 1)))
        print("M2 zona", filas[-1], flush=True)
        pd.DataFrame(filas).to_csv(out / "info_perfecta_meta_zona.csv", index=False)
    # --- 1. r_B, rho_B y techo del M1 ---
    filas = []
    for B in BS:
        t0 = time.time()
        r, inf_r = resolver_r(d, B * 1e9, "codo", rho_e=None, gap_rel=1e-6, time_limit=300)
        rho, inf_rho = (rho_regla_brecha(d, B * 1e9, r=r, rho_e=None, gap_rel=1e-6, time_limit=300)
                        if r is not None else (None, {"motivo": "sin r"}))
        f = dict(B=B, r_B=r, rho_B=rho, nota_rho=str(inf_rho.get("motivo", inf_rho.get("nota", ""))))
        for etiqueta, rr in [("r", None), ("r_rho", rho)]:
            if etiqueta == "r_rho" and rho is None:
                f["M1_salen_r_rho"], f["M1_estado_r_rho"] = float("nan"), "sin rho"
                continue
            m, info = resolver_dos_etapas(d, B * 1e9, r=r, rho=rr, rho_e=None, gap_rel=1e-6, time_limit=300)
            ok = info["etapa2"] is not None and info["etapa2"]["estado"] == "Optimal"
            f[f"M1_salen_{etiqueta}"] = float(m.recalcular().loc["total", "salen_personas"]) if ok else float("nan")
            f[f"M1_estado_{etiqueta}"] = "Optimal" if ok else info["etapa1"]["estado"]
        f["segundos"] = round(time.time() - t0, 1)
        filas.append(f)
        print("M1", f, flush=True)
        pd.DataFrame(filas).to_csv(out / "r_rho_comparacion.csv", index=False)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
