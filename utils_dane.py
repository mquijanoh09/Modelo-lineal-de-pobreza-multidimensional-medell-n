"""
utils_dane.py
Funciones reutilizables para leer los CSV de la base del IPM 2025 (DANE).

Uso desde cualquier script en la raíz del proyecto:
    from utils_dane import leer, leer_cabecera, RAIZ_DEP, RAIZ_NAC, OUT
"""
import csv
from pathlib import Path

import pandas as pd

# ------------------------------------------------------------------
# Rutas del proyecto (este archivo vive en la raíz: Optimizacion_1_S4/)
# ------------------------------------------------------------------
BASE = Path(__file__).resolve().parent / "data"
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