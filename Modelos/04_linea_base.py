"""
04_linea_base.py
Línea base (situación ANTES de intervenir) de Antioquia completa, total y por
zona (P3: 1 cabecera, 2 centro poblado, 3 rural disperso). Metodología
Alkire-Foster / IPM-Colombia:
  - H0  : incidencia (% de personas en pobreza multidimensional)
  - A0  : intensidad (puntaje promedio de los pobres)
  - M0  : tasa ajustada = H0 * A0
  - Tasas de privación por indicador y contribución de cada indicador a M0
  - Contribución por dimensión, por zona
  - Distancia de los hogares pobres al umbral, por zona

Entrada: data/processed/hogares_antioquia.csv  (generado por 03_preparar_antioquia.py)
"""

import numpy as np
import pandas as pd


from parametros import DIMENSIONES, PESOS, INDICADORES, K, ZONAS
from utils_dane import puntaje, resumen_ipm, OUT

ARCHIVO = OUT / "hogares_antioquia.csv"   # data/processed/ en la raíz del repo

W = np.array([PESOS[i] for i in INDICADORES])

# ------------------------------------------------------------------
# Datos
# ------------------------------------------------------------------
df = pd.read_csv(ARCHIVO)
M_total = df[INDICADORES].to_numpy(dtype=float)
df["puntaje"] = puntaje(M_total, W)
df["pobre_calc"] = (df["puntaje"] >= K).astype(int)
assert (df["pobre_calc"] == df["POBRE"]).all(), "POBRE no coincide con el puntaje"
df["p"] = df["FEX_C"] * df["PERSONAS"]          # personas representadas por hogar


def resumen(d):
    """H0, A0, M0 de un subconjunto de hogares (fórmula en utils_dane.resumen_ipm)."""
    return resumen_ipm(d["p"], d["puntaje"])


def contribuciones(d):
    """Tasas sin censurar, censuradas y contribución (%) de cada indicador a M0."""
    p, pobre = d["p"].to_numpy(), d["pobre_calc"].to_numpy()
    M = d[INDICADORES].to_numpy(dtype=float)
    _, _, M0 = resumen(d)
    cens = (p[:, None] * M * pobre[:, None]).sum(axis=0) / p.sum()
    sin_cens = (p[:, None] * M).sum(axis=0) / p.sum()
    return sin_cens, cens, W * cens / M0


# ==================================================================
# 1. Resumen total y por zona
# ==================================================================
print("=" * 78)
print(" LÍNEA BASE — ANTIOQUIA COMPLETA (IPM 2025)")
print("=" * 78)
print(f" {'Zona':<20}{'Hogares':>9}{'Pobres':>8}{'Personas':>13}{'H0':>9}{'A0':>9}{'M0':>10}")
print("-" * 78)
for p3, nombre in ZONAS.items():
    z = df[df["P3"] == p3]
    H, A, M0 = resumen(z)
    print(f" {p3} {nombre:<18}{len(z):>9,}{int(z['pobre_calc'].sum()):>8,}"
          f"{z['p'].sum():>13,.0f}{H:>9.2%}{A:>9.2%}{M0:>10.4f}")
H, A, M0 = resumen(df)
print("-" * 78)
print(f" {'Total':<20}{len(df):>9,}{int(df['pobre_calc'].sum()):>8,}"
      f"{df['p'].sum():>13,.0f}{H:>9.2%}{A:>9.2%}{M0:>10.4f}")
print(f"\n Personas en pobreza (total): {(df['p'] * df['pobre_calc']).sum():,.0f}")
print(f" Hogares reales representados: {df['FEX_C'].sum():,.0f}")

# ==================================================================
# 2. Indicadores: total de Antioquia
# ==================================================================
sin_cens, cens, contrib = contribuciones(df)
print("\n" + "-" * 78)
print(" Indicadores — Antioquia completa")
print("-" * 78)
print(f" {'Indicador':<28}{'peso':>6}{'sin cens.':>11}{'censurada':>11}{'contrib.':>11}")
for dim, inds in DIMENSIONES.items():
    print(f" [{dim}]")
    for ind in inds:
        j = INDICADORES.index(ind)
        print(f"   {ind:<26}{PESOS[ind]:>6.2f}{sin_cens[j]:>11.2%}"
              f"{cens[j]:>11.2%}{contrib[j]:>11.2%}")

# ==================================================================
# 3. Contribución por dimensión, por zona (el gradiente urbano-rural)
# ==================================================================
print("\n" + "-" * 78)
print(" Contribución por dimensión a M0, por zona")
print("-" * 78)
print(f" {'Dimensión':<20}" + "".join(f"{ZONAS[z]:>18}" for z in ZONAS) + f"{'Total':>12}")
tabla = {}
for z in list(ZONAS) + ["Total"]:
    d = df if z == "Total" else df[df["P3"] == z]
    _, _, c = contribuciones(d)
    tabla[z] = {dim: sum(c[INDICADORES.index(i)] for i in inds)
                for dim, inds in DIMENSIONES.items()}
for dim in DIMENSIONES:
    fila = "".join(f"{tabla[z][dim]:>18.2%}" for z in ZONAS)
    print(f" {dim:<20}{fila}{tabla['Total'][dim]:>12.2%}")

# ==================================================================
# 4. Distancia al umbral de los hogares pobres, por zona
#    Salir de la pobreza = quedar en puntaje <= 0.33 (múltiplos de 0.01)
# ==================================================================
print("\n" + "-" * 78)
print(" Distancia al umbral de los hogares pobres")
print("-" * 78)
pob = df[df["pobre_calc"] == 1].copy()
Mp = pob[INDICADORES].to_numpy(dtype=float)
pob["reduccion_necesaria"] = np.round(pob["puntaje"] - 0.33, 2)
pob["peso_max_disponible"] = (Mp * W).max(axis=1)
pob["sale_con_1"] = pob["peso_max_disponible"] >= pob["reduccion_necesaria"]
pob["n_privaciones"] = Mp.sum(axis=1)

print(f" {'Zona':<20}{'Pobres':>8}{'Privac. prom.':>15}{'Puntaje prom.':>15}{'Salen con 1':>14}")
for z in list(ZONAS) + ["Total"]:
    d = pob if z == "Total" else pob[pob["P3"] == z]
    etiqueta = "Total" if z == "Total" else f"{z} {ZONAS[z]}"
    print(f" {etiqueta:<20}{len(d):>8}{d['n_privaciones'].mean():>15.2f}"
          f"{d['puntaje'].mean():>15.2f}{d['sale_con_1'].mean():>14.1%}")

print("\n Puntajes de los hogares pobres (Antioquia completa):")
print(pob["puntaje"].value_counts().sort_index().to_string())