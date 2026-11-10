# -*- coding: utf-8 -*-
"""
m34_tabla_gasto.py — Tabla LaTeX "en qué se gasta" (datos congelados del 10-nov, 100 réplicas).
Participación PROMEDIO de cada dimensión y de la cabecera en el gasto, por meta y modelo.
Uso: python3 m34_tabla_gasto.py resultados/m34/barrido_comun_crudo_10nov.csv <salida.tex>
"""
import sys

import pandas as pd

METAS = [0.06, 0.10, 0.18, 0.20, 0.24, 0.30]
MODELOS = [("m3", "M3"), ("m4", "M4"), ("m4p", "Placebo")]


def pct(x):
    return f"{round(100 * x)}"


def main(crudo, salida):
    d = pd.read_csv(crudo)
    for c in ["Salud", "Educacion", "Trabajo", "Ninez", "Vivienda", "Cabecera"]:
        d[c] = d[f"gasto_{c}"] / d.costo_pesos
    t = d.groupby(["meta", "modelo"])[["Salud", "Educacion", "Trabajo", "Ninez", "Vivienda", "Cabecera"]].mean()
    filas = []
    for meta in METAS:
        celdas = []
        for clave in ["Salud", "Educacion", "Cabecera"]:
            celdas += [pct(t.loc[(meta, m), clave]) for m, _ in MODELOS]
        filas.append(f"{round(100 * meta)}\\,\\% & " + " & ".join(celdas) + " \\\\")
    with open(salida, "w", encoding="utf-8") as f:
        f.write("\n".join(filas) + "\n")
    print("\n".join(filas))
    print("máximo de niñez + vivienda:", round((t.Ninez + t.Vivienda).max(), 3), "| trabajo máx:", round(t.Trabajo.max(), 3))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
