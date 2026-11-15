# -*- coding: utf-8 -*-
"""
m34_datos_paper.py — Genera los CSV de origen de cada tabla y figura de M34_para_paper.md
(PLAN_INTEGRACION_M3_M4.md de Martín, §2 y §5). Solo lee resultados ya corridos; no resuelve ningún modelo.

Entradas (rama Modelo3, resultados/m34/ y las corridas del 15-nov):
  costo_meta_zona_crudo_12nov.csv, ic_costo_meta_zona_12nov.csv, info_perfecta_meta_zona_12nov.csv,
  cobertura_rB_crudo_12nov.csv, ic_rmax_12nov.csv, rmax_12nov.csv, r_rho_comparacion_12nov.csv,
  validacion_12nov.csv, equidad_comun_crudo_10nov.csv, info_perfecta_equidad_comun_10nov.csv,
  ic_bootstrap_costos_10nov.csv, ic_bootstrap_equidad_10nov.csv,
  costo_zonas_crudo_15nov.csv (H, A y M0 por zona) e ip_zonas_15nov.csv (Modelo 2 por zona).

Uso: python3 m34_datos_paper.py <resultados/m34/> <datos_m34/>
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

MOD = {"m3": "Modelo 3", "m4": "Modelo 4", "m4p": "Placebo"}
ZONAS = {"Cabecera": "Cabeceras", "Centro poblado": "Centros poblados", "Rural disperso": "Rural disperso",
         "total": "Total Antioquia"}
B_LISTA = [2, 5, 10, 25, 50, 100]


def p(x, q):
    return float(np.percentile(x, q))


def costo_meta_zona(R, out):
    """Tabla M34-2 y Figura M34-1: costo por meta, M2 de referencia, M3, M4 y placebo."""
    ic = pd.read_csv(R / "ic_costo_meta_zona_12nov.csv")
    cr = pd.read_csv(R / "costo_meta_zona_crudo_12nov.csv")
    assert (cr.estado == "Optimal").all() and len(cr) == 4500
    cr["costo_mm"] = cr.costo_pesos / 1e3          # costo_pesos está en millones de pesos
    filas = []
    for m, g in cr.groupby("meta"):
        w = g.pivot(index="replica", columns="modelo", values="costo_mm")
        f = ic.loc[np.isclose(ic.meta, m)].iloc[0]
        fila = dict(meta=m, replicas=len(w), costo_M2_mm=f.IP)
        for k in ["m3", "m4", "m4p"]:
            fila.update({f"costo_{k}_mediana_mm": f[k], f"costo_{k}_ic95_inf": f[f"{k}_ic_inf"],
                         f"costo_{k}_ic95_sup": f[f"{k}_ic_sup"], f"costo_{k}_p5_mm": p(w[k], 5),
                         f"costo_{k}_p95_mm": p(w[k], 95), f"precio_info_{k}": f[f"{k}_sobre_IP"],
                         f"inclusion_{k}": f[f"{k}_inclusion"], f"exclusion_{k}": f[f"{k}_exclusion"]})
        fila.update(M4_sobre_M3=f.M4_sobre_M3, M4_sobre_M3_ic95_inf=f.M4_sobre_M3_ic_inf,
                    M4_sobre_M3_ic95_sup=f.M4_sobre_M3_ic_sup, M4_sobre_placebo=f.M4_sobre_placebo,
                    M4_sobre_placebo_ic95_inf=f.M4_sobre_placebo_ic_inf,
                    M4_sobre_placebo_ic95_sup=f.M4_sobre_placebo_ic_sup,
                    pct_replicas_M4_menor_M3=100 * float((w.m4 < w.m3).mean()),
                    pct_replicas_M4_menor_placebo=100 * float((w.m4 < w.m4p).mean()))
        filas.append(fila)
    t = pd.DataFrame(filas)
    t.to_csv(out / "costo_meta_zona.csv", index=False)
    # gasto por zona y por dimensión (Tabla M34-4): promedio de la participación en las 100 réplicas
    filas = []
    for (m, k), g in cr.groupby(["meta", "modelo"]):
        tot = g.costo_pesos
        f = dict(meta=m, modelo=MOD[k])
        for z in ["Cabecera", "Centro poblado", "Rural disperso"]:
            f[f"pct_gasto_{ZONAS[z]}"] = 100 * float((g[f"gasto_{z}"] / tot).mean())
        for s in ["Salud", "Educacion", "Trabajo", "Ninez", "Vivienda"]:
            f[f"pct_gasto_{s}"] = 100 * float((g[f"gasto_{s}"] / tot).mean())
        filas.append(f)
    pd.DataFrame(filas).to_csv(out / "gasto_por_zona_y_dimension.csv", index=False)
    return t


def zonas_HAM0(R, out):
    """Tabla M34-3: H, A y M0 finales por zona (mediana de réplicas) y referencia del Modelo 2."""
    ipz = pd.read_csv(R / "ip_zonas_15nov.csv")
    cz = pd.read_csv(R / "costo_zonas_crudo_15nov.csv")
    assert (cz.estado == "Optimal").all()
    # las corridas del 15-nov deben ser las mismas soluciones del 12-nov: mismo costo en cada corrida
    v = pd.read_csv(R / "costo_meta_zona_crudo_12nov.csv")
    mm = cz.merge(v, on=["modelo", "replica", "meta"], suffixes=("", "_12nov"))
    assert len(mm) == len(cz), "hay corridas del 15-nov sin pareja en el 12-nov"
    dif = (mm.costo_pesos - mm.costo_pesos_12nov).abs().max()
    assert dif < 1e-6 and (mm.H1 - mm.H1_12nov).abs().max() < 1e-12, dif
    print(f"costo_zonas_crudo_15nov: {len(mm)} corridas idénticas al 12-nov (diferencia máxima {dif:.1e})")
    filas = []
    for _, f in ipz.iterrows():
        filas.append(dict(meta=f.meta, modelo="Modelo 2", zona=ZONAS[f.zona], replicas=1, H0=f.H0, A0=f.A0,
                          M0_inicial=f.M0_inicial, H=f.H, A=f.A, M0=f.M0, gasto_mm=f.costo_mm))
    base = ipz[np.isclose(ipz.meta, 0.02)].set_index("zona")
    pers = None
    for (m, k), g in cz.groupby(["meta", "modelo"]):
        for z in ["total", "Cabecera", "Centro poblado", "Rural disperso"]:
            sfx = "" if z == "total" else f"_{z}"
            gasto = g.costo_pesos / 1e3 if z == "total" else g[f"gasto_{z}"] / 1e3
            filas.append(dict(meta=m, modelo=MOD[k], zona=ZONAS[z], replicas=len(g), H0=base.at[z, "H0"],
                              A0=base.at[z, "A0"], M0_inicial=base.at[z, "M0_inicial"],
                              H=float(g[f"H1{sfx}"].median()), A=float(g[f"A1{sfx}"].median()),
                              M0=float(g[f"M01{sfx}"].median()), gasto_mm=float(gasto.median()),
                              H_p5=p(g[f"H1{sfx}"], 5), H_p95=p(g[f"H1{sfx}"], 95)))
    t = pd.DataFrame(filas)
    t["reduccion_H_pct"] = 100 * (1 - t.H / t.H0)
    t["reduccion_M0_pct"] = 100 * (1 - t.M0 / t.M0_inicial)
    t.to_csv(out / "H_A_M0_por_zona.csv", index=False)
    return t


def cobertura(R, out):
    """Tabla M34-5: fracción de réplicas factibles con r_B y con r_B + rho_B."""
    c = pd.read_csv(R / "cobertura_rB_crudo_12nov.csv")
    rr = pd.read_csv(R / "r_rho_comparacion_12nov.csv").set_index("B")
    filas = []
    for (B, k, esc), g in c.groupby(["B", "modelo", "escenario"]):
        if (g.estado == "sin_rho").all():
            continue
        filas.append(dict(B=int(B), modelo=MOD[k], escenario="r_B" if esc == "r" else "r_B y rho_B",
                          r_B=rr.at[int(B), "r_B"], rho_B=rr.at[int(B), "rho_B"] if esc != "r" else np.nan,
                          replicas=len(g), factibles=int((g.estado == "Optimal").sum()),
                          pct_factibles=100 * float((g.estado == "Optimal").mean())))
    t = pd.DataFrame(filas).sort_values(["escenario", "B", "modelo"])
    t.to_csv(out / "factibilidad_cobertura_rB.csv", index=False)
    rr.reset_index().to_csv(out / "r_rho_referencias_M1.csv", index=False)
    return t


def rmax(R, out):
    """Tabla M34-6 y Figura M34-2: piso máximo garantizable."""
    t = pd.read_csv(R / "ic_rmax_12nov.csv")
    t["M3_sobre_IP"] = t.m3 / t.IP_max
    t["M4_sobre_IP"] = t.m4 / t.IP_max
    t["placebo_sobre_IP"] = t.m4p / t.IP_max
    t.to_csv(out / "rmax_piso_garantizable.csv", index=False)
    return t


def sens_r0(R, out):
    """Tabla M34-7: personas que salen con r = 0 (sensibilidad, datos congelados del 10-nov)."""
    e = pd.read_csv(R / "ic_bootstrap_equidad_10nov.csv")
    ip = pd.read_csv(R / "info_perfecta_equidad_comun_10nov.csv")
    e.to_csv(out / "sens_r0_personas_que_salen.csv", index=False)
    ip.to_csv(out / "sens_r0_info_perfecta_M1.csv", index=False)
    c = pd.read_csv(R / "ic_bootstrap_costos_10nov.csv")
    c.to_csv(out / "sens_meta_global_costos.csv", index=False)
    return e


def validacion(R, out):
    v = pd.read_csv(R / "validacion_12nov.csv")
    v.to_csv(out / "validacion_granularidad_maxima.csv", index=False)
    return v


def main(R, out):
    R, out = Path(R), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    costo_meta_zona(R, out)
    if (R / "costo_zonas_crudo_15nov.csv").exists():
        zonas_HAM0(R, out)
    else:
        print("AVISO: falta costo_zonas_crudo_15nov.csv; no se genera H_A_M0_por_zona.csv")
    cobertura(R, out)
    rmax(R, out)
    sens_r0(R, out)
    validacion(R, out)
    for f in sorted(out.glob("*.csv")):
        print(f.name, pd.read_csv(f).shape)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
