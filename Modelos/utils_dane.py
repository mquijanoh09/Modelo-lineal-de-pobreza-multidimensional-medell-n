"""
utils_dane.py
Funciones reutilizables para leer los CSV de la base del IPM 2025 (DANE).

Uso desde Modelos/ (o desde Modelos/Modelo_1 y Modelo_2 agregando Modelos/ al path):
    from utils_dane import leer, leer_cabecera, RAIZ_DEP, RAIZ_NAC, OUT
"""
import csv
from pathlib import Path

import numpy as np
import pandas as pd

# ------------------------------------------------------------------
# Rutas del proyecto. Este archivo vive en Optimizacion_1_S4/Modelos/ y los
# datos siguen en la raíz: Optimizacion_1_S4/data/ (decisión de Martín, 5-nov).
# ------------------------------------------------------------------
RAIZ = Path(__file__).resolve().parents[1]          # Optimizacion_1_S4/
MODELOS = RAIZ / "Modelos"
BASE = RAIZ / "data"
DANE = BASE / "DANE"
RAIZ_DEP = DANE / "DEPARTAMENTAL"
RAIZ_NAC = DANE / "NACIONAL"
OUT = BASE / "processed"
OUT.mkdir(parents=True, exist_ok=True)


def detectar_separador(cabecera, requeridas, ruta):
    """Devuelve el separador cuya cabecera contiene las columnas requeridas."""
    opciones = []
    for sep in (";", ",", "\t", "|"):
        nombres = [n.strip().lstrip("\ufeff")
                   for n in next(csv.reader([cabecera], delimiter=sep))]
        opciones.append((sep, nombres))

    if requeridas:
        validas = [(s, n) for s, n in opciones if requeridas.issubset(n)]
        if not validas:
            raise ValueError(f"{ruta.name}: no están {sorted(requeridas)}. "
                             f"Cabeceras por separador: {opciones}")
        return validas[0][0]

    sep, nombres = max(opciones, key=lambda o: len(o[1]))
    if len(nombres) == 1:
        raise ValueError(f"{ruta.name}: no se pudo identificar el separador.")
    return sep


def ruta_csv(carpeta):
    """Devuelve el único CSV dentro de `carpeta`."""
    archivos = sorted(Path(carpeta).glob("*.csv"))
    if len(archivos) != 1:
        raise FileNotFoundError(f"Se esperaba 1 CSV en {carpeta}; "
                                f"hay {[p.name for p in archivos]}")
    return archivos[0]


def leer_cabecera(ruta):
    """Lee solo los nombres de columna (instantáneo, no carga los datos)."""
    with Path(ruta).open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        cabecera = f.readline()
    sep = detectar_separador(cabecera, set(), Path(ruta))
    return [n.strip().lstrip("\ufeff")
            for n in next(csv.reader([cabecera], delimiter=sep))]


def leer(sub, columnas=None, raiz=RAIZ_DEP):
    """Lee el único CSV de la subcarpeta `sub`, detectando separador y codificación."""
    ruta = ruta_csv(Path(raiz) / sub)
    requeridas = set(columnas or ())

    # latin-1 nunca falla al decodificar, así que actúa como red de seguridad
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            with ruta.open("r", encoding=encoding, newline="") as f:
                cabecera = f.readline()
            sep = detectar_separador(cabecera, requeridas, ruta)
            datos = pd.read_csv(
                ruta, sep=sep, encoding=encoding, low_memory=False,
                usecols=(lambda n: n.strip().lstrip("\ufeff") in requeridas)
                        if columnas else None,
            )
            break  # solo sale si leyó TODO el archivo sin errores
        except UnicodeDecodeError:
            continue

    datos.columns = datos.columns.str.strip().str.lstrip("\ufeff")
    print(f"Leído: {ruta.name} (sep={sep!r}, encoding={encoding}, "
          f"{len(datos):,} filas)")
    return datos


def a_numero(serie):
    """Convierte a número aceptando coma decimal (formato DANE)."""
    return pd.to_numeric(serie.astype(str).str.strip().str.replace(",", ".", regex=False),
                         errors="coerce")


# ------------------------------------------------------------------
# Indicadores Alkire-Foster (antes vivían dentro de 04_linea_base.py,
# que no se puede importar porque su nombre empieza por un dígito)
# ------------------------------------------------------------------
def puntaje(M, w):
    """Puntaje de privación de cada hogar: sum_j w_j * M_ij, redondeado a 0.01.
    El redondeo evita errores de punto flotante (0.1 + 0.2 + 0.04 = 0.34000000000000002):
    todos los pesos son múltiplos de 0.01, así que el puntaje real también lo es."""
    return np.round(np.asarray(M, dtype=float) @ np.asarray(w, dtype=float), 2)


def resumen_ipm(p, puntaje_hogar, k=1 / 3):
    """H, A y M0 de un conjunto de hogares.

    p              personas que representa cada hogar (HW_i * HS_i)
    puntaje_hogar  puntaje de privación de cada hogar (antes o después de intervenir)
    k              umbral: el hogar es pobre si su puntaje es >= k

    H  = personas pobres / personas totales
    A  = puntaje promedio de los pobres (ponderado por personas)
    M0 = H * A
    Se usa igual para la línea base (04) y para recalcular después de resolver
    un modelo (08): así ambos números salen de la misma fórmula.
    """
    p = np.asarray(p, dtype=float)
    s = np.asarray(puntaje_hogar, dtype=float)
    pobre = s >= k
    H = (p * pobre).sum() / p.sum()
    A = (p * pobre * s).sum() / (p * pobre).sum() if pobre.any() else 0.0
    return H, A, H * A
