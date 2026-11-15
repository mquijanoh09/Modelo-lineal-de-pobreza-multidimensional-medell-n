# -*- coding: utf-8 -*-
"""
m34_documento_paper.py — Arma M34_para_paper.md y cifras_m34.csv (PLAN_INTEGRACION_M3_M4.md de Martín, §2).

Todas las cifras del texto se calculan aquí desde los CSV de datos_m34/ y se escriben en cifras_m34.csv con su
archivo y su columna de origen. La plantilla (plantilla_M34.md) solo lleva marcas {{nombre}} para las cifras y
{{TABLA:nombre}} para las tablas. Si una marca no tiene valor, el script falla: no queda ningún número a mano.

Formato del paper de Martín: punto decimal y coma de miles (0.036, 87,034), porcentaje con espacio (85.1 %) y
dinero en pesos de 2025 y en «mil millones» ($16.1 mil millones).

Uso: python3 m34_documento_paper.py <datos_m34/> <plantilla_M34.md> <M34_para_paper.md> <cifras_m34.csv>
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

C = {}          # nombre -> (texto, valor, archivo, columna)


def n(x, d=0):
    return f"{x:,.{d}f}"


def pc(x, d=1):
    return f"{x:,.{d}f} %"


def reg(nombre, texto, valor, archivo, columna):
    assert nombre not in C, nombre
    C[nombre] = (texto, valor, archivo, columna)


def rango(nombre, a, b, fmt, archivo, columna, sep=" y "):
    reg(nombre, f"{fmt(a)}{sep}{fmt(b)}", f"{a}|{b}", archivo, columna)


def cifras(D):
    lb = pd.read_csv(D / "linea_base.csv").set_index("zona")
    t = lb.loc["Total Antioquia"]
    f = "linea_base.csv"
    reg("hogares", n(t.hogares), t.hogares, f, "hogares (Total Antioquia)")
    reg("hogares_pobres", n(t.hogares_pobres), t.hogares_pobres, f, "hogares_pobres (Total Antioquia)")
    reg("personas_pobres", n(t.personas_pobres), t.personas_pobres, f, "personas_pobres (Total Antioquia)")
    reg("poblacion", n(t.poblacion), t.poblacion, f, "poblacion (Total Antioquia)")
    reg("H0", pc(100 * t.H0, 2), t.H0, f, "H0 (Total Antioquia)")
    reg("A0", pc(100 * t.A0, 2), t.A0, f, "A0 (Total Antioquia)")
    reg("M0", n(t.M0, 4), t.M0, f, "M0 (Total Antioquia)")
    reg("pares_privados", n(t.pares_privados), t.pares_privados, f, "pares_privados (Total Antioquia)")
    for z, k in [("Cabeceras", "cab"), ("Centros poblados", "cp"), ("Rural disperso", "rd")]:
        reg(f"H0_{k}", pc(100 * lb.at[z, "H0"], 1), lb.at[z, "H0"], f, f"H0 ({z})")
    reg("pct_pobres_rural", pc(100 * lb.at["Rural disperso", "personas_pobres"] / t.personas_pobres, 0),
        lb.at["Rural disperso", "personas_pobres"] / t.personas_pobres, f, "personas_pobres rural / total")

    th = pd.read_csv(D / "tipos_hogar.csv").set_index("tipo")
    reg("separa_pobreza", n(th.H0.max() / th.H0.min(), 1), th.H0.max() / th.H0.min(), "tipos_hogar.csv",
        "max(H0) / min(H0)")
    di = pd.read_csv(D / "discriminacion_privaciones.csv").set_index("indicador")
    for ind, k in [("acueducto", "acu"), ("alcantarillado", "alc"), ("inasistencia_escolar", "inas"),
                   ("hacinamiento", "hac"), ("aseguramiento_salud", "aseg"), ("barreras_acceso_salud", "barr")]:
        reg(f"disc_{k}_z", n(di.at[ind, "razon_zonas"], 1), di.at[ind, "razon_zonas"],
            "discriminacion_privaciones.csv", f"razon_zonas ({ind})")
        reg(f"disc_{k}_t", n(di.at[ind, "razon_tipos"], 1), di.at[ind, "razon_tipos"],
            "discriminacion_privaciones.csv", f"razon_tipos ({ind})")

    # ---- criterio de costo ----
    c = pd.read_csv(D / "costo_meta_zona.csv")
    f = "costo_meta_zona.csv"
    reg("replicas_costo", n(c.replicas.iloc[0]), c.replicas.iloc[0], f, "replicas")
    reg("corridas_costo", n(3 * c.replicas.sum()), 3 * c.replicas.sum(), f, "3 x suma de replicas")
    baja, alta = c[c.meta <= 0.10 + 1e-9], c[c.meta >= 0.20 - 1e-9]
    rango("m3_ip_baja", baja.precio_info_m3.min(), baja.precio_info_m3.max(), lambda x: n(x, 1), f,
          "precio_info_m3, metas 2-10 %", " y ")
    rango("m3_ip_alta", alta.precio_info_m3.min(), alta.precio_info_m3.max(), lambda x: n(x, 1), f,
          "precio_info_m3, metas 20-30 %", " y ")
    rango("m3_ip_todas", c.precio_info_m3.min(), c.precio_info_m3.max(), lambda x: n(x, 1), f,
          "precio_info_m3, todas las metas", " y ")
    rango("m4_ip_todas", c.precio_info_m4.min(), c.precio_info_m4.max(), lambda x: n(x, 1), f,
          "precio_info_m4, todas las metas", " y ")
    menor = c[c.M4_sobre_M3_ic95_sup < 1]
    mayor = c[c.M4_sobre_M3_ic95_inf > 1]
    reg("n_m4_menor_m3", n(len(menor)), len(menor), f, "metas con M4_sobre_M3_ic95_sup < 1")
    reg("n_m4_mayor_m3", n(len(mayor)), len(mayor), f, "metas con M4_sobre_M3_ic95_inf > 1")
    reg("n_m4_igual_m3", n(15 - len(menor) - len(mayor)), 15 - len(menor) - len(mayor), f, "las demás metas")
    medio = c[(c.meta >= 0.10 - 1e-9) & (c.meta <= 0.24 + 1e-9)]
    rango("ahorro_m4_m3_medio", 100 * (1 - medio.M4_sobre_M3.max()), 100 * (1 - medio.M4_sobre_M3.min()),
          lambda x: n(x, 0), f, "1 - M4_sobre_M3, metas 10-24 %", " y ")
    rango("pct_rep_m4_menor_m3_medio", medio.pct_replicas_M4_menor_M3.min(), medio.pct_replicas_M4_menor_M3.max(),
          lambda x: n(x, 0), f, "pct_replicas_M4_menor_M3, metas 10-24 %", " y ")
    reg("m4_m3_meta2", n(c.M4_sobre_M3.iloc[0], 2), c.M4_sobre_M3.iloc[0], f, "M4_sobre_M3 (meta 2 %)")
    alto = c[c.meta >= 0.26 - 1e-9]
    rango("sobrecosto_m4_alto", 100 * (alto.M4_sobre_M3.min() - 1), 100 * (alto.M4_sobre_M3.max() - 1),
          lambda x: n(x, 0), f, "M4_sobre_M3 - 1, metas 26-30 %", " y ")
    pl = c[c.meta >= 0.06 - 1e-9]
    rango("ahorro_m4_placebo", 100 * (1 - pl.M4_sobre_placebo.max()), 100 * (1 - pl.M4_sobre_placebo.min()),
          lambda x: n(x, 0), f, "1 - M4_sobre_placebo, metas 6-30 %", " y ")
    rango("incl_m3", 100 * c.inclusion_m3.min(), 100 * c.inclusion_m3.max(), lambda x: n(x, 0), f,
          "inclusion_m3", " y ")
    rango("incl_m4", 100 * c.inclusion_m4.min(), 100 * c.inclusion_m4.max(), lambda x: n(x, 0), f,
          "inclusion_m4", " y ")
    rango("excl_m3", 100 * c.exclusion_m3.min(), 100 * c.exclusion_m3.max(), lambda x: n(x, 0), f,
          "exclusion_m3", " y ")
    s6 = c[np.isclose(c.meta, 0.06)].iloc[0]
    reg("ip_6", n(s6.costo_M2_mm, 2), s6.costo_M2_mm, f, "costo_M2_mm (meta 6 %)")
    reg("m3_6", n(s6.costo_m3_mediana_mm, 2), s6.costo_m3_mediana_mm, f, "costo_m3_mediana_mm (meta 6 %)")
    reg("dif_6", n(s6.costo_m3_mediana_mm - s6.costo_M2_mm, 0), s6.costo_m3_mediana_mm - s6.costo_M2_mm, f,
        "costo_m3_mediana_mm - costo_M2_mm (meta 6 %)")
    s10 = c[np.isclose(c.meta, 0.10)].iloc[0]
    reg("ip_10", n(s10.costo_M2_mm, 2), s10.costo_M2_mm, f, "costo_M2_mm (meta 10 %)")

    g = pd.read_csv(D / "gasto_por_zona_y_dimension.csv")
    f = "gasto_por_zona_y_dimension.csv"
    m3r = g[(g.modelo == "Modelo 3") & (g.meta >= 0.08 - 1e-9)]["pct_gasto_Rural disperso"]
    rango("m3_rural", m3r.min(), m3r.max(), lambda x: n(x, 0), f, "pct_gasto_Rural disperso, Modelo 3, metas 8-30 %")
    pcab = g[g.modelo == "Placebo"]["pct_gasto_Cabeceras"]
    rango("plac_cab", pcab.min(), pcab.max(), lambda x: n(x, 0), f, "pct_gasto_Cabeceras, Placebo", " y ")
    g10 = g[np.isclose(g.meta, 0.10)].set_index("modelo")
    for k, mod in [("m3", "Modelo 3"), ("m4", "Modelo 4"), ("plac", "Placebo")]:
        reg(f"edu10_{k}", n(g10.at[mod, "pct_gasto_Educacion"], 0), g10.at[mod, "pct_gasto_Educacion"], f,
            f"pct_gasto_Educacion ({mod}, meta 10 %)")
    g2 = g[np.isclose(g.meta, 0.02)]
    reg("salud2_min", n(g2.pct_gasto_Salud.min(), 0), g2.pct_gasto_Salud.min(), f, "min pct_gasto_Salud, meta 2 %")
    otros = g[["pct_gasto_Ninez", "pct_gasto_Vivienda", "pct_gasto_Trabajo"]].max().max()
    reg("otros_max", n(otros, 0), otros, f, "max de pct_gasto_Ninez, _Vivienda y _Trabajo")

    # ---- H, A y M0 por zona ----
    z = pd.read_csv(D / "H_A_M0_por_zona.csv")
    f = "H_A_M0_por_zona.csv"
    t10 = z[np.isclose(z.meta, 0.10) & (z.zona == "Total Antioquia")].set_index("modelo")
    for k, mod in [("m2", "Modelo 2"), ("m3", "Modelo 3"), ("m4", "Modelo 4"), ("plac", "Placebo")]:
        reg(f"H10_{k}", pc(100 * t10.at[mod, "H"], 2), t10.at[mod, "H"], f, f"H ({mod}, meta 10 %, total)")
        reg(f"redH10_{k}", pc(t10.at[mod, "reduccion_H_pct"], 1), t10.at[mod, "reduccion_H_pct"], f,
            f"reduccion_H_pct ({mod}, meta 10 %, total)")
        reg(f"A10_{k}", pc(100 * t10.at[mod, "A"], 2), t10.at[mod, "A"], f, f"A ({mod}, meta 10 %, total)")
    tot = z[z.zona == "Total Antioquia"].pivot(index="meta", columns="modelo", values="H")
    for k, mod in [("m3", "Modelo 3"), ("m4", "Modelo 4")]:
        nn = int((tot[mod] <= tot["Modelo 2"] + 1e-12).sum())
        reg(f"n_H_{k}_menor", n(nn), nn, f, f"metas con H total de {mod} <= H total del Modelo 2")
    a2 = z[(z.zona == "Total Antioquia") & (z.modelo == "Modelo 2")]
    nn = int((a2.A > a2.A0).sum())
    reg("n_A_sube_m2", n(nn), nn, f, "metas con A > A0 en el Modelo 2 (total)")
    q = z[np.isclose(z.meta, 0.10) & (z.modelo == "Modelo 3") & (z.zona == "Cabeceras")].iloc[0]
    reg("m3_10_redM0_cab", pc(q.reduccion_M0_pct, 1), q.reduccion_M0_pct, f,
        "reduccion_M0_pct (Modelo 3, meta 10 %, Cabeceras; mediana)")
    redz = z[(z.zona != "Total Antioquia") & (z.modelo != "Modelo 2")].reduccion_H_pct
    reg("redH_min_zona", pc(redz.min(), 1), redz.min(), f, "min reduccion_H_pct por zona, M3/M4/placebo")
    t30 = z[np.isclose(z.meta, 0.30) & (z.zona == "Total Antioquia")].set_index("modelo")
    for k, mod in [("m2", "Modelo 2"), ("m3", "Modelo 3"), ("m4", "Modelo 4")]:
        reg(f"redH30_{k}", pc(t30.at[mod, "reduccion_H_pct"], 1), t30.at[mod, "reduccion_H_pct"], f,
            f"reduccion_H_pct ({mod}, meta 30 %, total)")

    # ---- criterio de presupuesto ----
    fb = pd.read_csv(D / "factibilidad_cobertura_rB.csv")
    f = "factibilidad_cobertura_rB.csv"
    reg("corridas_cob", n(fb.replicas.sum()), fb.replicas.sum(), f, "suma de replicas")
    reg("pct_fact_max", pc(fb.pct_factibles.max(), 0), fb.pct_factibles.max(), f, "max pct_factibles")
    rr = pd.read_csv(D / "rmax_piso_garantizable.csv")
    f = "rmax_piso_garantizable.csv"
    reg("rmax_reps", n(rr.n.iloc[0]), rr.n.iloc[0], f, "n")
    reg("corridas_rmax", n(3 * rr.n.sum()), 3 * rr.n.sum(), f, "3 x suma de n")
    b100 = rr[rr.B == 100].iloc[0]
    reg("rmax_m3_100", pc(100 * b100.m3, 1), b100.m3, f, "m3 (B = 100)")
    reg("rmax_ip_100", pc(100 * b100.IP_max, 1), b100.IP_max, f, "IP_max (B = 100)")
    rango("rmax_frac_100", 100 * b100.M4_sobre_IP, 100 * b100.M3_sobre_IP, lambda x: n(x, 0), f,
          "M4_sobre_IP y M3_sobre_IP (B = 100)", " y ")
    b2 = rr[rr.B == 2].iloc[0]
    reg("rmax_m3_2", pc(100 * b2.m3, 1), b2.m3, f, "m3 (B = 2)")
    mejor = (rr.m3_mejor < rr.r_B).all()
    reg("mejor_bajo_rB", "ninguna" if mejor else "alguna", int(mejor), f, "m3_mejor < r_B en todos los B")

    # ---- validación y sensibilidades ----
    v = pd.read_csv(D / "validacion_granularidad_maxima.csv")
    f = "validacion_granularidad_maxima.csv"
    reg("valid_ok", f"{int(v.ok.sum())}/{len(v)}", int(v.ok.sum()), f, "ok")
    g1 = v[v.prueba.str.startswith("G1")].diferencia_pct.abs()
    reg("g1_30", pc(g1.max(), 2), g1.max(), f, "max |diferencia_pct| G1")
    g2 = v[v.prueba.str.startswith("G2") & (v.diferencia_pct.abs() > 1e-9)].diferencia_pct.abs()
    rango("g2_rango", g2.min(), g2.max(), lambda x: pc(x, 2), f, "|diferencia_pct| G2 distintas de 0", " y ")
    e = pd.read_csv(D / "sens_r0_personas_que_salen.csv")
    f = "sens_r0_personas_que_salen.csv"
    rango("r0_m3_pct", e.m3_pct_IP.min(), e.m3_pct_IP.max(), lambda x: n(x, 0), f, "m3_pct_IP", " y ")
    rango("r0_m4_pct", e.m4_pct_IP.min(), e.m4_pct_IP.max(), lambda x: n(x, 0), f, "m4_pct_IP", " y ")
    cg = pd.read_csv(D / "sens_meta_global_costos.csv")
    f = "sens_meta_global_costos.csv"
    reg("ip_global_10", n(cg[np.isclose(cg.meta, 0.10)].IP_M2.iloc[0], 2), cg[np.isclose(cg.meta, 0.10)].IP_M2.iloc[0],
        f, "IP_M2 (meta global 10 %)")
    bj = cg[cg.meta <= 0.10 + 1e-9]
    rango("glob_m3_ip_baja", bj.m3_sobre_IP.min(), bj.m3_sobre_IP.max(), lambda x: n(x, 1), f,
          "m3_sobre_IP, metas 2-10 %", " y ")
    # cifras de documentos (no de corridas de esta entrega): se citan con su documento de origen
    rev = "Project Opti1: claude/revision-formulacion-modelo3.md (7-oct, versión inicial del modelo)"
    aud = "rama Contexto: AUDITORIA_M34_14NOV.md y auditoria_14nov/verif_soluciones.csv"
    reg("cob_paper", "4.81", 4.81, rev, "cobertura máxima con las unidades del paper")
    reg("t_directa", "200", 200, rev, "segundos sin cerrar la brecha, formulación directa, meta 10 %")
    reg("t_cortes", "2", 2.1, rev, "segundos de la reformulación por cortes en la base completa")
    reg("aud_sol", "144", 144, aud, "soluciones re-resueltas y verificadas")
    reg("aud_fb", "40", 40, aud, "instancias de fuerza bruta por criterio")
    reg("aud_frontera", "72", 72, aud, "casos de la frontera de r_max")
    k = pd.read_csv(D / "sens_k_u1.csv")
    k10 = k[(k.objetivo == "equidad") & (k.B == 10)].set_index("modelo")
    for mod in ["m4_k2", "m4_k4", "m4_k5"]:
        reg(f"k_{mod}", n(k10.at[mod, "vs_M3_mediana"], 2), k10.at[mod, "vs_M3_mediana"], "sens_k_u1.csv",
            f"vs_M3_mediana ({mod}, B = 10)")


# ------------------------------------------------------------------ tablas
def md(df):
    cab = "| " + " | ".join(df.columns) + " |"
    sep = "| " + " | ".join("---" if i == 0 else "---:" for i in range(len(df.columns))) + " |"
    return "\n".join([cab, sep] + ["| " + " | ".join(str(x) for x in r) + " |" for r in df.itertuples(index=False)])


def tablas(D):
    T = {}
    c = pd.read_csv(D / "costo_meta_zona.csv")
    T["costo"] = md(pd.DataFrame({
        "Meta m": [pc(100 * x, 0) for x in c.meta],
        "Modelo 2": [n(x, 2) for x in c.costo_M2_mm],
        "Modelo 3": [f"{n(a, 2)} ({n(b, 1)} a {n(d, 1)})" for a, b, d in zip(c.costo_m3_mediana_mm, c.costo_m3_p5_mm,
                                                                           c.costo_m3_p95_mm)],
        "Modelo 4": [f"{n(a, 2)} ({n(b, 1)} a {n(d, 1)})" for a, b, d in zip(c.costo_m4_mediana_mm, c.costo_m4_p5_mm,
                                                                           c.costo_m4_p95_mm)],
        "Placebo": [f"{n(a, 2)} ({n(b, 1)} a {n(d, 1)})" for a, b, d in zip(c.costo_m4p_mediana_mm, c.costo_m4p_p5_mm,
                                                                          c.costo_m4p_p95_mm)],
        "Precio M3": [n(x, 1) for x in c.precio_info_m3], "Precio M4": [n(x, 1) for x in c.precio_info_m4],
        "M4/M3 (IC 95 %)": [f"{n(a, 2)} ({n(b, 2)} a {n(d, 2)})" for a, b, d in
                            zip(c.M4_sobre_M3, c.M4_sobre_M3_ic95_inf, c.M4_sobre_M3_ic95_sup)],
        "Réplicas con M4 < M3": [pc(x, 0) for x in c.pct_replicas_M4_menor_M3],
        "M4/placebo (IC 95 %)": [f"{n(a, 2)} ({n(b, 2)} a {n(d, 2)})" for a, b, d in
                                 zip(c.M4_sobre_placebo, c.M4_sobre_placebo_ic95_inf, c.M4_sobre_placebo_ic95_sup)]}))
    T["errores"] = md(pd.DataFrame({
        "Meta m": [pc(100 * x, 0) for x in c.meta],
        "Inclusión M3": [pc(100 * x, 0) for x in c.inclusion_m3], "Inclusión M4": [pc(100 * x, 0) for x in c.inclusion_m4],
        "Inclusión placebo": [pc(100 * x, 0) for x in c.inclusion_m4p],
        "Exclusión M3": [pc(100 * x, 0) for x in c.exclusion_m3], "Exclusión M4": [pc(100 * x, 0) for x in c.exclusion_m4],
        "Exclusión placebo": [pc(100 * x, 0) for x in c.exclusion_m4p]}))

    z = pd.read_csv(D / "H_A_M0_por_zona.csv")
    orden_z = ["Total Antioquia", "Cabeceras", "Centros poblados", "Rural disperso"]
    orden_m = ["Modelo 2", "Modelo 3", "Modelo 4", "Placebo"]
    for meta in [0.10, 0.30]:
        s = z[np.isclose(z.meta, meta)].copy()
        s["oz"] = s.zona.map(orden_z.index)
        s["om"] = s.modelo.map(orden_m.index)
        s = s.sort_values(["oz", "om"])
        T[f"zonas{int(round(100 * meta))}"] = md(pd.DataFrame({
            "Zona": s.zona, "Modelo": s.modelo, "Gasto": [n(x, 2) for x in s.gasto_mm],
            "H inicial": [pc(100 * x, 2) for x in s.H0], "H final": [pc(100 * x, 2) for x in s.H],
            "A inicial": [pc(100 * x, 2) for x in s.A0], "A final": [pc(100 * x, 2) for x in s.A],
            "M0 inicial": [n(x, 4) for x in s.M0_inicial], "M0 final": [n(x, 4) for x in s.M0]}))

    g = pd.read_csv(D / "gasto_por_zona_y_dimension.csv")
    g = g[g.meta.round(2).isin([0.02, 0.06, 0.10, 0.14, 0.20, 0.24, 0.30])]
    w = {}
    for mod, ab in [("Modelo 3", "M3"), ("Modelo 4", "M4"), ("Placebo", "Plac.")]:
        s = g[g.modelo == mod].set_index("meta")
        for col, nom in [("pct_gasto_Salud", "Salud"), ("pct_gasto_Educacion", "Educación"),
                         ("pct_gasto_Cabeceras", "Cabeceras"), ("pct_gasto_Rural disperso", "Rural disperso")]:
            w[f"{nom} {ab}"] = [n(x, 0) for x in s[col]]
    metas = sorted(g.meta.unique())
    T["gasto"] = md(pd.DataFrame({"Meta m": [pc(100 * x, 0) for x in metas], **w}))

    fb = pd.read_csv(D / "factibilidad_cobertura_rB.csv")
    rr = pd.read_csv(D / "r_rho_referencias_M1.csv")
    filas = []
    for _, r in rr.iterrows():
        a = fb[(fb.B == r.B) & (fb.escenario == "r_B")]
        b = fb[(fb.B == r.B) & (fb.escenario == "r_B y rho_B")]
        filas.append({"B": n(r.B), "r_B": n(r.r_B, 3), "ρ_B": "no se alcanza" if pd.isna(r.rho_B) else n(r.rho_B, 3),
                      "Salen con el Modelo 1 y r_B": n(r.M1_salen_r),
                      "Réplicas": n(a.replicas.iloc[0]),
                      "Factibles con r_B (M3 / M4 / placebo)": " / ".join(pc(x, 0) for x in a.sort_values("modelo").pct_factibles),
                      "Factibles con r_B y ρ_B": "no aplica" if b.empty else
                      " / ".join(pc(x, 0) for x in b.sort_values("modelo").pct_factibles)})
    T["factibilidad"] = md(pd.DataFrame(filas))

    r = pd.read_csv(D / "rmax_piso_garantizable.csv")
    f3 = lambda a, b, c_: f"{pc(100 * a, 1)} ({n(100 * b, 1)} a {n(100 * c_, 1)})"
    T["rmax"] = md(pd.DataFrame({
        "B": [n(x) for x in r.B], "r_B (Modelo 1)": [pc(100 * x, 1) for x in r.r_B],
        "Información perfecta": [pc(100 * x, 1) for x in r.IP_max],
        "Modelo 3": [f3(a, b, c_) for a, b, c_ in zip(r.m3, r.m3_ic_inf, r.m3_ic_sup)],
        "Modelo 4": [f3(a, b, c_) for a, b, c_ in zip(r.m4, r.m4_ic_inf, r.m4_ic_sup)],
        "Placebo": [f3(a, b, c_) for a, b, c_ in zip(r.m4p, r.m4p_ic_inf, r.m4p_ic_sup)],
        "Mejor réplica M3": [pc(100 * x, 1) for x in r.m3_mejor],
        "M3 / IP": [pc(100 * x, 0) for x in r.M3_sobre_IP], "M4 / IP": [pc(100 * x, 0) for x in r.M4_sobre_IP]}))

    cg = pd.read_csv(D / "sens_meta_global_costos.csv")
    cg = cg[cg.meta.round(2).isin([0.02, 0.06, 0.10, 0.14, 0.18, 0.20, 0.24, 0.30])]
    T["global"] = md(pd.DataFrame({
        "Meta m": [pc(100 * x, 0) for x in cg.meta], "Modelo 2": [n(x, 2) for x in cg.IP_M2],
        "Modelo 3": [n(x, 2) for x in cg.m3_mediana], "Modelo 4": [n(x, 2) for x in cg.m4_mediana],
        "Placebo": [n(x, 2) for x in cg.m4p_mediana], "Precio M3": [n(x, 1) for x in cg.m3_sobre_IP],
        "Precio M4": [n(x, 1) for x in cg.m4_sobre_IP],
        "M4/placebo (IC 95 %)": [f"{n(a, 2)} ({n(b, 2)} a {n(d, 2)})" for a, b, d in
                                 zip(cg.M4_sobre_placebo, cg.M4_sobre_placebo_ic_inf, cg.M4_sobre_placebo_ic_sup)]}))
    e = pd.read_csv(D / "sens_r0_personas_que_salen.csv")
    T["r0"] = md(pd.DataFrame({
        "B": [n(x) for x in e.B], "Réplicas": [n(x) for x in e.n], "Modelo 1": [n(x) for x in e.IP_M1],
        "Modelo 3": [n(x) for x in e.m3_mediana], "Modelo 4": [n(x) for x in e.m4_mediana],
        "Placebo": [n(x) for x in e.m4p_mediana], "M3 / M1": [pc(x, 0) for x in e.m3_pct_IP],
        "M4 / M1": [pc(x, 0) for x in e.m4_pct_IP],
        "M4/M3 (IC 95 %)": [f"{n(a, 2)} ({n(b, 2)} a {n(d, 2)})" for a, b, d in
                            zip(e.M4_sobre_M3, e.M4_sobre_M3_ic_inf, e.M4_sobre_M3_ic_sup)]}))
    k = pd.read_csv(D / "sens_k_u1.csv")
    k = k[k.objetivo == "equidad"]
    k = k[k.B == 10]
    nom = {"m3": "Modelo 3", "m4_k2": "k = 2", "m4_k3": "k = 3", "m4_k4": "k = 4 (caso base)", "m4_k5": "k = 5",
           "m4_k6": "k = 6", "m4_k8": "k = 8"}
    T["k"] = md(pd.DataFrame({"Partición del Modelo 4": [nom[x] for x in k.modelo],
                              "Personas que salen con B = 10": [s.replace(";", " a").split(" [")[0] for s in k.salen],
                              "Veces el Modelo 3 (mediana)": [n(x, 2) for x in k.vs_M3_mediana]}))
    th = pd.read_csv(D / "tipos_hogar.csv")
    T["tipos"] = md(pd.DataFrame({"Tipo de hogar": th.tipo, "Hogares en la muestra": [n(x) for x in th.hogares],
                                  "Incidencia H": [pc(100 * x, 1) for x in th.H0]}))
    di = pd.read_csv(D / "discriminacion_privaciones.csv")
    nombres = {"acueducto": "Acueducto (bien público)", "alcantarillado": "Alcantarillado (bien público)",
               "inasistencia_escolar": "Inasistencia escolar", "hacinamiento": "Hacinamiento",
               "atencion_integral": "Atención integral a la primera infancia",
               "aseguramiento_salud": "Aseguramiento en salud", "barreras_acceso_salud": "Barreras de acceso a salud"}
    di = di[di.indicador.isin(nombres)].set_index("indicador").loc[list(nombres)]
    T["discrimina"] = md(pd.DataFrame({
        "Privación": [nombres[i] for i in di.index], "Entre zonas": [n(x, 1) for x in di.razon_zonas],
        "Entre tipos de hogar": ["solo existe en hogares con niños" if np.isinf(x) else n(x, 1)
                                 for x in di.razon_tipos]}))
    v = pd.read_csv(D / "validacion_granularidad_maxima.csv")
    T["validacion"] = md(pd.DataFrame({
        "Prueba": v.prueba.str.replace("%", " %", regex=False),
        "Modelo 3 con un hogar por celda": [n(x, 2) if x < 1e3 else n(x) for x in v.M3_granular],
        "Información perfecta": [n(x, 2) if x < 1e3 else n(x) for x in v.info_perfecta],
        "Diferencia": [pc(x, 2) for x in v.diferencia_pct], "Resultado": ["pasa" if o else "falla" for o in v.ok]}))
    return T


def main(D, plantilla, salida, salida_cifras):
    D = Path(D)
    cifras(D)
    T = tablas(D)
    txt = Path(plantilla).read_text(encoding="utf-8")

    def sub_tabla(m):
        return T[m.group(1)]

    def sub_cifra(m):
        if m.group(1) not in C:
            raise KeyError(f"cifra sin valor: {m.group(1)}")
        return C[m.group(1)][0]
    txt = re.sub(r"\{\{TABLA:(\w+)\}\}", sub_tabla, txt)
    usadas = set(re.findall(r"\{\{(\w+)\}\}", txt))
    txt = re.sub(r"\{\{(\w+)\}\}", sub_cifra, txt)
    assert "{{" not in txt
    Path(salida).write_text(txt, encoding="utf-8")
    pd.DataFrame([dict(cifra=k, texto=v[0], valor=v[1], archivo=v[2] if ":" in v[2] else f"datos_m34/{v[2]}", columna=v[3],
                       citada_en_texto=k in usadas) for k, v in C.items()]).to_csv(salida_cifras, index=False)
    print(len(C), "cifras,", len(usadas), "citadas,", len(T), "tablas")


if __name__ == "__main__":
    main(*sys.argv[1:5])
