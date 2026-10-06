"""
02_validar_ipm.py
Valida que los 15 indicadores de la base IPM 2025 (DANE), combinados con los
pesos anidados oficiales, reproducen las columnas IPM y POBRE del DANE.

Si la validación pasa, la matriz M_ij, el tamaño HS_i y el factor HW_i
pueden tomarse directamente de esta base para el modelo MILP.
"""
import numpy as np
import pandas as pd

from utils_dane import leer, a_numero

# ------------------------------------------------------------------
# Pesos oficiales del IPM-Colombia: 5 dimensiones de 0.2 cada una,
# repartidas en partes iguales entre sus indicadores.
# ------------------------------------------------------------------
DIMENSIONES = {
    "Educación":          ["logro_educativo", "analfabetismo"],
    "Niñez y juventud":   ["inasistencia_escolar", "rezago_escolar",
                           "atencion_integral", "trabajo_infantil"],
    "Trabajo":            ["desempleo_larga_duracion", "empleo_formal"],
    "Salud":              ["aseguramiento_salud", "barreras_acceso_salud"],
    "Vivienda":           ["acueducto", "alcantarillado", "pisos",
                           "paredes", "hacinamiento"],
}
PESOS = {ind: 0.2 / len(inds) for inds in DIMENSIONES.values() for ind in inds}
INDICADORES = list(PESOS)
K = 1 / 3  # umbral de pobreza

assert len(INDICADORES) == 15 #Verificación de que en total sean 15
assert abs(sum(PESOS.values()) - 1) < 1e-12 #verificación de que los pesos sumen 1

# ------------------------------------------------------------------
# 1. Cargar HOGARES (departamental)
# ------------------------------------------------------------------
hog = leer("HOGARES (DEPARTAMENTAL) 2025")
for c in INDICADORES + ["IPM", "POBRE", "PERSONAS", "FEX_C", "FEXP", "DEPARTAMENTO"]:
    hog[c] = a_numero(hog[c])

# ------------------------------------------------------------------
# 2. ¿Cómo están codificados los indicadores?
# ------------------------------------------------------------------
print("\n=== 1. Valores de cada indicador (conteo de hogares) ===")
for dim, inds in DIMENSIONES.items():
    print(f"\n[{dim}]")
    for ind in inds:
        conteo = hog[ind].value_counts(dropna=False).sort_index().to_dict()
        print(f"   {ind:<26} peso={PESOS[ind]:.2f}  valores={conteo}")

print("\nIPM:   min =", hog["IPM"].min(), "| max =", hog["IPM"].max())
print("POBRE:", hog["POBRE"].value_counts(dropna=False).sort_index().to_dict())

# ------------------------------------------------------------------
# 3. Recalcular el puntaje de privación y comparar con IPM del DANE
# ------------------------------------------------------------------
M = hog[INDICADORES].to_numpy(dtype=float)
w = np.array([PESOS[i] for i in INDICADORES])
puntaje = np.round(M @ w, 2)          # múltiplos de 0.01: redondeo exacto

escala = 100 if hog["IPM"].max() > 1.0 else 1  # por si el DANE lo da en %
ipm_dane = np.round(hog["IPM"].to_numpy() / escala, 2)

coincide = np.isclose(puntaje, ipm_dane, atol=1e-9)
print("\n=== 2. Puntaje recalculado vs. columna IPM ===")
print(f"Escala detectada de IPM: {'0-100' if escala == 100 else '0-1'}")
print(f"Hogares donde coincide: {coincide.mean():.2%}")
if not coincide.all():
    muestra = hog.loc[~coincide, ["DIRECTORIO", "IPM"]].head(5).copy()
    muestra["puntaje_recalculado"] = puntaje[~coincide][:5]
    print("Ejemplos que NO coinciden:\n", muestra.to_string(index=False))

# ------------------------------------------------------------------
# 4. Recalcular POBRE con el umbral k y comparar
# ------------------------------------------------------------------
pobre_calc = (puntaje >= K).astype(int)
pobre_dane = hog["POBRE"].to_numpy()
print("\n=== 3. Pobreza recalculada (puntaje >= 1/3) vs. columna POBRE ===")
print(f"Hogares donde coincide: {(pobre_calc == pobre_dane).mean():.2%}")
print("Puntajes distintos observados alrededor del umbral:",
      sorted(set(puntaje[(puntaje > 0.25) & (puntaje < 0.40)])))

# ------------------------------------------------------------------
# 5. Factores de expansión: ¿cuál es HW_i?
#    Personas representadas = sum(HW_i * HS_i). Colombia ~ 52-53 millones.
# ------------------------------------------------------------------
print("\n=== 4. Factores de expansión ===")
for f in ("FEX_C", "FEXP"):
    hogares = hog[f].sum()
    personas = (hog[f] * hog["PERSONAS"]).sum()
    print(f"{f:<6}: hogares representados = {hogares:>14,.0f} | "
          f"personas representadas = {personas:>14,.0f} | nulos = {hog[f].isna().sum()}")

# ------------------------------------------------------------------
# 6. Incidencia (H) nacional y de Antioquia con cada factor
#    H = sum(HW_i * HS_i * POBRE_i) / sum(HW_i * HS_i)
# ------------------------------------------------------------------
print("\n=== 5. Incidencia H (% de personas en pobreza multidimensional) ===")
ant = hog["DEPARTAMENTO"] == 5
for f in ("FEX_C", "FEXP"):
    peso = hog[f] * hog["PERSONAS"]
    h_nal = (peso * hog["POBRE"]).sum() / peso.sum()
    h_ant = (peso[ant] * hog.loc[ant, "POBRE"]).sum() / peso[ant].sum()
    print(f"{f:<6}: H Colombia = {h_nal:.2%} | H Antioquia (total) = {h_ant:.2%}")

print(f"\nHogares de Antioquia en la muestra: {ant.sum():,}")