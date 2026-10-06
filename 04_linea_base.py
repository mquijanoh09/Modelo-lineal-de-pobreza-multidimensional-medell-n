"""
04_linea_base.py
Línea base (situación ANTES de intervenir) de Antioquia urbana, metodología
Alkire-Foster / IPM-Colombia:
  - H0  : incidencia (% de personas en pobreza multidimensional)
  - A0  : intensidad (puntaje promedio de los pobres)
  - M0  : tasa ajustada = H0 * A0
  - Tasas de privación por indicador (sin censurar y censuradas a los pobres)
  - Contribución de cada indicador y dimensión a M0
  - Distancia de los hogares pobres al umbral

Entrada: data/processed/hogares_antioquia_urbana.csv  (generado por 03_...py)
"""
from pathlib import Path

import numpy as np
import pandas as pd

ARCHIVO = Path(__file__).resolve().parent / "data" / "processed" / "hogares_antioquia_urbana.csv"

DIMENSIONES = {
    "Educación":        ["logro_educativo", "analfabetismo"],
    "Niñez y juventud": ["inasistencia_escolar", "rezago_escolar",
                         "atencion_integral", "trabajo_infantil"],
    "Trabajo":          ["desempleo_larga_duracion", "empleo_formal"],
    "Salud":            ["aseguramiento_salud", "barreras_acceso_salud"],
    "Vivienda":         ["acueducto", "alcantarillado", "pisos",
                         "paredes", "hacinamiento"],
}
PESOS = {ind: 0.2 / len(inds) for inds in DIMENSIONES.values() for ind in inds}
INDICADORES = list(PESOS)
K = 1 / 3

# ------------------------------------------------------------------
# Datos y peso poblacional de cada hogar: p_i = HW_i * HS_i
# ------------------------------------------------------------------
df = pd.read_csv(ARCHIVO)
M = df[INDICADORES].to_numpy(dtype=float)
w = np.array([PESOS[i] for i in INDICADORES])
puntaje = np.round(M @ w, 2)
pobre = (puntaje >= K).astype(int)
assert (pobre == df["POBRE"].to_numpy()).all(), "POBRE no coincide con el puntaje"

p = (df["FEX_C"] * df["PERSONAS"]).to_numpy()   # personas representadas por hogar
P = p.sum()                                     # total de personas

# ------------------------------------------------------------------
# 1. H0, A0, M0
# ------------------------------------------------------------------
H0 = (p * pobre).sum() / P
A0 = (p * pobre * puntaje).sum() / (p * pobre).sum()
M0 = (p * pobre * puntaje).sum() / P

print("=" * 66)
print(" LÍNEA BASE — ANTIOQUIA URBANA (IPM 2025)")
print("=" * 66)
print(f" Hogares en la muestra:          {len(df):,}")
print(f" Hogares pobres en la muestra:   {pobre.sum():,}")
print(f" Personas representadas:         {P:,.0f}")
print(f" Personas en pobreza:            {(p * pobre).sum():,.0f}")
print(f"\n H0 (incidencia)     = {H0:.2%}")
print(f" A0 (intensidad)     = {A0:.2%}   (puntaje promedio de los pobres)")
print(f" M0 = H0 x A0        = {M0:.4f}")

# ------------------------------------------------------------------
# 2. Tasas de privación por indicador y contribución a M0
#    - Sin censurar: % de TODAS las personas con la privación
#    - Censurada:    % de personas que tienen la privación Y son pobres
#    - Contribución: w_j * censurada_j / M0  (las contribuciones suman 100%)
# ------------------------------------------------------------------
print("\n" + "-" * 66)
print(f" {'Indicador':<26}{'peso':>6}{'sin cens.':>11}{'censurada':>11}{'contrib.':>11}")
print("-" * 66)
contrib_dim = {}
for dim, inds in DIMENSIONES.items():
    print(f" [{dim}]")
    contrib_dim[dim] = 0.0
    for ind in inds:
        j = INDICADORES.index(ind)
        sin_cens = (p * M[:, j]).sum() / P
        censurada = (p * M[:, j] * pobre).sum() / P
        contrib = PESOS[ind] * censurada / M0
        contrib_dim[dim] += contrib
        print(f"   {ind:<24}{PESOS[ind]:>6.2f}{sin_cens:>11.2%}{censurada:>11.2%}{contrib:>11.2%}")

print("-" * 66)
print(" Contribución por dimensión:")
for dim, c in sorted(contrib_dim.items(), key=lambda x: -x[1]):
    print(f"   {dim:<20} {c:7.2%}  {'█' * int(round(c * 50))}")

# ------------------------------------------------------------------
# 3. Distancia de los hogares pobres al umbral
#    ¿Cuánto puntaje tiene que bajar cada hogar pobre para salir (< 1/3)?
#    Como los puntajes son múltiplos de 0.01, salir = quedar en <= 0.33.
# ------------------------------------------------------------------
pob = df[pobre == 1].copy()
pob["puntaje"] = puntaje[pobre == 1]
pob["reduccion_necesaria"] = np.round(pob["puntaje"] - 0.33, 2)
pob["n_privaciones"] = M[pobre == 1].sum(axis=1)

# Peso máximo entre las privaciones que tiene cada hogar
Mp = M[pobre == 1]
pob["peso_max_disponible"] = (Mp * w).max(axis=1)
pob["sale_con_1"] = pob["peso_max_disponible"] >= pob["reduccion_necesaria"]

print("\n" + "-" * 66)
print(" Distancia al umbral de los hogares pobres")
print("-" * 66)
print(" Puntaje de los hogares pobres:")
print(pob["puntaje"].value_counts().sort_index().to_string())
print(f"\n Privaciones promedio de un hogar pobre: {pob['n_privaciones'].mean():.2f}")
print(f" Hogares pobres que salen eliminando UNA sola privación: "
      f"{pob['sale_con_1'].sum()} de {len(pob)} "
      f"({pob['sale_con_1'].mean():.1%})")
print(f" Hogares reales representados: {df['FEX_C'].sum():,.0f} "
      f"(promedio por hogar encuestado: {df['FEX_C'].mean():,.0f})")

