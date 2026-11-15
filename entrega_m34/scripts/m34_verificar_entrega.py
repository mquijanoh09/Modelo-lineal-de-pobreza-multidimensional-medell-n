# -*- coding: utf-8 -*-
"""
m34_verificar_entrega.py — Comprueba la entrega de los Modelos 3 y 4 antes de mandarla a Martín.

1. Cada cifra de cifras_m34.csv marcada como citada aparece tal cual en M34_para_paper.md, y no queda ninguna marca
   {{...}} sin reemplazar.
2. Las cifras que ya estaban en el paper de la rama paper-12nov (cifras.tex, verificadas 16/16 y 29/29 el 14-nov)
   coinciden con las de esta entrega, salvo el formato (coma decimal allá, punto acá).
3. Las referencias provisionales (r_B, rho_B y Modelo 2 por zona) son las mismas de la sección 6 de
   RESPUESTA_JERONIMO_12NOV.md.
4. El documento no usa guiones largos ni flechas, y las figuras citadas existen.

Uso: python3 m34_verificar_entrega.py <carpeta de la entrega> <paper/cifras.tex de paper-12nov>
"""
import re
import sys
from pathlib import Path

import pandas as pd


def latex_a_punto(s):
    s = s.replace("\\%", "%").replace("\\,", " ").replace("$", "").replace("{", "").replace("}", "")
    s = s.replace(".", "")            # miles con punto en el LaTeX
    return s.replace(",", ".")        # coma decimal -> punto


def main(raiz, cifras_tex):
    raiz = Path(raiz)
    doc = (raiz / "M34_para_paper.md").read_text(encoding="utf-8")
    c = pd.read_csv(raiz / "cifras_m34.csv")
    ok, total = 0, 0

    def check(cond, msg):
        nonlocal ok, total
        total += 1
        ok += bool(cond)
        print("OK   " if cond else "FALLA", msg)

    check("{{" not in doc, "no quedan marcas sin reemplazar")
    for _, f in c[c.citada_en_texto].iterrows():
        check(str(f.texto) in doc, f"cifra {f.cifra} = '{f.texto}' aparece en el texto")
    check("—" not in doc.replace("| — |", "|  |") and "→" not in doc, "sin guiones largos ni flechas (salvo «—» como celda vacía, como en la Tabla 2 del borrador)")
    for img in re.findall(r"\]\((figuras_m34/[^)]+)\)", doc):
        check((raiz / img).exists(), f"existe {img}")
    for csv in set(re.findall(r"`(datos_m34/[^`]+\.csv)`", doc)):
        check((raiz / csv).exists(), f"existe {csv}")

    tex = Path(cifras_tex).read_text(encoding="utf-8")
    mac = dict(re.findall(r"\\newcommand\{\\(\w+)\}\{(.+?)\}\s*(?:%.*)?$", tex, flags=re.M))
    v = dict(zip(c.cifra, c.texto.astype(str)))
    pares = [("zMtresIPbaja", "m3_ip_baja", " a ", " y "), ("zMtresIPalta", "m3_ip_alta", " a ", " y "),
             ("zMcuatroIPmin", "m4_ip_todas", None, None), ("zMcuatroIPmax", "m4_ip_todas", None, None),
             ("zMcuatroMtresMenor", "n_m4_menor_m3", None, None), ("zMcuatroMtresMayor", "n_m4_mayor_m3", None, None),
             ("zMcuatroMtresIgual", "n_m4_igual_m3", None, None), ("zIPzonaDiez", "ip_10", None, None),
             ("cIPglobalDiez", "ip_global_10", None, None), ("zCorridas", "corridas_costo", None, None),
             ("zCorridasCob", "corridas_cob", None, None),
             ("cHogares", "hogares", None, None), ("cPobresHog", "hogares_pobres", None, None),
             ("cSeparaPobreza", "separa_pobreza", None, None), ("cDiscAcuZona", "disc_acu_z", None, None),
             ("cDiscAcuClu", "disc_acu_t", None, None), ("cDiscInasClu", "disc_inas_t", None, None)]
    for m, k, a, b in pares:
        lt = latex_a_punto(mac[m]).replace(" %", "").strip()
        nuevo = v[k].replace(",", "").replace(" %", "")
        if a:
            lt = lt.replace(a, b)
        check(lt in nuevo or nuevo in lt, f"{m} = {mac[m]} (paper-12nov) frente a {k} = {v[k]}")
    for m, k in [("zPlacMin", "ahorro_m4_placebo"), ("zPlacMax", "ahorro_m4_placebo"),
                 ("zInclMtres", "incl_m3"), ("zInclMcuatro", "incl_m4"), ("zExclMtres", "excl_m3")]:
        lt = latex_a_punto(mac[m]).replace(" %", "").strip()
        check(lt.split(" y ")[0] in v[k].split(" y "), f"{m} = {mac[m]} (paper-12nov) frente a {k} = {v[k]}")

    # r_max: las 1,800 corridas del 12-nov más 300 de B = 424 (15-nov)
    check(latex_a_punto(mac["zCorridasRmax"]) == "1800" and v["corridas_rmax"] == "2,100",
          f"zCorridasRmax = {mac['zCorridasRmax']} (paper-12nov) + 300 de B = 424 = {v['corridas_rmax']}")
    rr = pd.read_csv(raiz / "datos_m34/r_rho_referencias_M1.csv").set_index("B")
    esperado = {2: (0.0365, 87034), 5: (0.0730, 129294), 10: (0.1462, 154347), 25: (0.2382, 214879),
                50: (0.3442, 281588), 100: (0.5219, 369940)}
    for B, (r, s) in esperado.items():
        check(abs(rr.at[B, "r_B"] - r) < 6e-5 and abs(rr.at[B, "M1_salen_r"] - s) < 1,
              f"r_B y personas del M1 con B = {B} iguales a RESPUESTA_JERONIMO_12NOV.md §6")
    cm = pd.read_csv(raiz / "datos_m34/costo_meta_zona.csv")
    for m, e in {0.02: 0.47, 0.06: 2.30, 0.10: 5.17, 0.20: 16.11, 0.30: 32.37}.items():
        val = cm.loc[(cm.meta - m).abs() < 1e-9, "costo_M2_mm"].iloc[0]
        check(abs(val - e) < 0.005, f"Modelo 2 por zona con meta {m:.0%} = {val:.2f} (RESPUESTA §6: {e})")
    z = pd.read_csv(raiz / "datos_m34/H_A_M0_por_zona.csv")
    for (meta, mod), g in z[z.modelo != "Modelo 2"].groupby(["meta", "modelo"]):
        pass
    check(set(z[z.modelo != "Modelo 2"].replicas) == {100}, "H, A y M0 por zona con 100 réplicas en todas las metas")
    m2 = z[(z.modelo == "Modelo 2") & (z.zona != "Total Antioquia")]
    check(((m2.reduccion_M0_pct + 1e-6) >= 100 * m2.meta).all(), "el Modelo 2 cumple la meta en cada zona")
    otros = z[(z.modelo != "Modelo 2") & (z.zona != "Total Antioquia")]
    check(((otros.reduccion_M0_pct + 1e-6) >= 100 * otros.meta).all(),
          "la mediana de M3, M4 y placebo cumple la meta en cada zona")
    print(f"\n{ok}/{total} comprobaciones")
    sys.exit(0 if ok == total else 1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
