# -*- coding: utf-8 -*-
"""
00_verificar_base.py — Chequeo de que la base cumple lo que los Modelos 3 y 4
necesitan. Correr esto ANTES de pasarle la base a Jeronimo.

Si todo sale OK, los modelos 3 y 4 corren. Si algo sale MAL, el mensaje dice
que es y por que importa.

Uso:  python3 00_verificar_base.py
"""
import sys
import numpy as np
import pandas as pd
from utils_dane import leer, a_numero

# EL FILTRO QUE SE VA A USAR. Cambiarlo aqui y volver a correr.
FILTRO = {"DEPARTAMENTO": [5]}        # Antioquia completa
COL_ZONA = "P3"
DEN_MINIMO = 10                       # personas privadas minimas por (indicador, zona)

IND = ["logro_educativo", "analfabetismo", "inasistencia_escolar", "rezago_escolar",
       "atencion_integral", "trabajo_infantil", "desempleo_larga_duracion",
       "empleo_formal", "aseguramiento_salud", "barreras_acceso_salud",
       "acueducto", "alcantarillado", "pisos", "paredes", "hacinamiento"]
W = {**{j: 0.10 for j in IND[:2]}, **{j: 0.05 for j in IND[2:6]},
     **{j: 0.10 for j in IND[6:10]}, **{j: 0.04 for j in IND[10:]}}

fallos = []
def chequeo(ok, titulo, detalle=""):
    print(f"  [{'OK ' if ok else 'MAL'}] {titulo}")
    if detalle:
        print(f"         {detalle}")
    if not ok:
        fallos.append(titulo)

print("\n=== VERIFICACION DE LA BASE PARA LOS MODELOS 3 Y 4 ===")

hog = leer("HOGARES (DEPARTAMENTAL) 2025")
viv = leer("VIVIENDAS (DEPARTAMENTAL) 2025", columnas=["DIRECTORIO", "P3"])
hog = hog.merge(viv, on="DIRECTORIO", how="left", validate="many_to_one")
for c in IND + ["PERSONAS", "FEX_C", "IPM", "POBRE", "DEPARTAMENTO", "P3"]:
    hog[c] = a_numero(hog[c])
for col, vals in FILTRO.items():
    hog = hog[hog[col].isin(vals)]
hog = hog.reset_index(drop=True)
print(f"\nFiltro aplicado: {FILTRO}  ->  {len(hog):,} hogares\n")

# --- 1. columnas presentes ---------------------------------------------------
faltan = [c for c in IND + ["PERSONAS", "FEX_C", "P3", "DIRECTORIO", "SECUENCIA_P"]
          if c not in hog.columns]
chequeo(not faltan, "Estan todas las columnas que el modelo lee",
        f"faltan: {faltan}" if faltan else "15 indicadores + PERSONAS + FEX_C + P3")

# --- 2. llave unica ----------------------------------------------------------
dup = hog.duplicated(["DIRECTORIO", "SECUENCIA_P"]).sum()
chequeo(dup == 0, "La llave DIRECTORIO + SECUENCIA_P es unica por hogar",
        f"{dup} duplicados" if dup else "")

# --- 3. sin nulos en lo que importa -----------------------------------------
nulos = hog[IND + ["PERSONAS", "FEX_C", "P3"]].isna().sum()
chequeo(nulos.sum() == 0, "No hay nulos en indicadores, PERSONAS, FEX_C ni P3",
        f"{nulos[nulos > 0].to_dict()}" if nulos.sum() else "")

# --- 4. AL MENOS DOS ZONAS  (el critico) ------------------------------------
zonas = sorted(hog[COL_ZONA].dropna().unique())
chequeo(len(zonas) >= 2,
        f"Hay al menos 2 zonas en {COL_ZONA}  <-- SIN ESTO NO HAY MODELO 3",
        f"zonas encontradas: {zonas}. Con una sola, E_jd colapsa a E_j y "
        f"desaparece la focalizacion geografica." if len(zonas) < 2
        else f"{len(zonas)} zonas: {zonas}")

# --- 5. los pesos y el umbral siguen cuadrando ------------------------------
w = np.array([W[j] for j in IND])
calc = np.round(hog[IND].to_numpy(float) @ w, 2)
chequeo(np.allclose(calc, hog.IPM, atol=1e-9),
        "La columna IPM se reconstruye con los pesos oficiales")
chequeo(((calc >= 1/3).astype(int) == hog.POBRE).all(),
        "La columna POBRE coincide con IPM >= 1/3 (umbral k = 0,333)")

# --- 6. denominadores por (indicador, zona) ---------------------------------
HS = hog.PERSONAS.to_numpy(float)
flacos = []
for j in IND:
    m = hog[j].to_numpy(float)
    for z in zonas:
        sel = (hog[COL_ZONA].to_numpy() == z)
        den = (HS[sel] * m[sel]).sum()
        if 0 < den < DEN_MINIMO:
            flacos.append((j, z, int(den)))
chequeo(len(flacos) <= 3,
        f"Pocos pares (indicador, zona) con denominador menor a {DEN_MINIMO}",
        f"{len(flacos)} pares flacos: {flacos[:5]}" if flacos else "ninguno")

# --- 7. hay pobres suficientes para que la meta signifique algo -------------
n_pobres = int(hog.POBRE.sum())
chequeo(n_pobres >= 100, "Hay al menos 100 hogares pobres en la muestra",
        f"{n_pobres} hogares pobres")

# --- resumen ----------------------------------------------------------------
pers = hog.PERSONAS * hog.FEX_C
score = calc
H = (pers * hog.POBRE).sum() / pers.sum()
M0 = (pers * hog.POBRE * score).sum() / pers.sum()
print(f"\nLinea base con este filtro:")
print(f"  hogares={len(hog):,}  pobres={n_pobres}  zonas={len(zonas)}")
print(f"  H0={H:.4f}   M0={M0:.6f}  <- M0 es el que restringe el modelo, no H0")
print(f"  pares activos (i,j) con M_ij=1: {int(hog[IND].to_numpy().sum()):,}")

print("\n" + "="*60)
if fallos:
    print(f"HAY {len(fallos)} PROBLEMA(S):")
    for f in fallos:
        print(f"  - {f}")
    sys.exit(1)
print("TODO OK: la base sirve para los Modelos 3 y 4.")
