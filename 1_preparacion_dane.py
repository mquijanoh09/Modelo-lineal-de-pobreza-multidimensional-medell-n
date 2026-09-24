import pandas as pd
import os

# 1. DEFINIR RUTAS DE LOS ARCHIVOS
# Esto asegura que Python encuentre los archivos sin importar dónde estés ejecutando
ruta_viviendas = 'datos/viviendas_2014.txt'
ruta_hogares = 'datos/hogares_2014.txt'
ruta_factores = 'datos/factores_2014'

# Nota: Si al descomprimir los ZIP del DANE resultaron ser archivos .txt en lugar de .csv,
# simplemente cambia la extensión arriba (ej. 'datos/Viviendas.txt')

print("1. Cargando bases de datos del DANE...")
# El DANE utiliza punto y coma (;) para separar columnas y 'latin-1' para tildes y eñes
try:
    df_viviendas = pd.read_csv(ruta_viviendas, sep=';', encoding='latin-1')
    df_hogares = pd.read_csv(ruta_hogares, sep=';', encoding='latin-1')
    df_factores = pd.read_csv(ruta_factores, sep=';', encoding='latin-1')
    print("   ¡Archivos cargados con éxito!")
except FileNotFoundError as e:
    print(f"   Error: No se encontró el archivo {e.filename}. Revisa los nombres en la carpeta 'datos'.")
    exit()

print("\n2. Cruzando las bases de datos...")
# Unimos Viviendas con Hogares usando la llave maestra: DIRECTORIO (ID de la casa)
# Usamos 'inner' para mantener solo las casas que tienen información en ambos archivos
df_fusion = pd.merge(df_viviendas, df_hogares, on='DIRECTORIO', how='inner')

# Ahora le pegamos el Factor de Expansión (HW_i)
# Ojo: Una casa puede tener varias familias. Usamos DIRECTORIO + SECUENCIA_P para identificar la familia exacta
df_fusion = pd.merge(df_fusion, df_factores, on=['DIRECTORIO', 'SECUENCIA_P'], how='inner')
print(f"   Total de hogares a nivel nacional tras el cruce: {len(df_fusion)}")

print("\n3. Filtrando geográficamente (Medellín)...")
# Buscamos la columna del municipio. A veces el DANE la llama U_MPIO, MPIO, o DPMP.
# Asumimos que se llama MPIO y que Medellín es 5001.
# Si sale error aquí, imprimiremos las columnas para buscar el nombre real.
try:
    df_medellin = df_fusion[df_fusion['MPIO'] == 5001].copy()
    # Si la columna viene como texto ('05001'), descomenta la siguiente línea y borra la anterior:
    # df_medellin = df_fusion[df_fusion['MPIO'] == '05001'].copy()

    print(f"   Total de hogares aislados en Medellín: {len(df_medellin)}")
except KeyError:
    print("   Error: No se encontró la columna 'MPIO'. Estas son las columnas disponibles en Vivienda:")
    print("  ", list(df_viviendas.columns)[:15])  # Imprime las primeras 15 para buscarla
    exit()

print("\n4. Guardando el archivo maestro...")
# Guardamos la base limpia en la misma carpeta de datos
ruta_salida = 'datos/medellin_base.csv'
df_medellin.to_csv(ruta_salida, index=False, sep=';', encoding='latin-1')
print(f"   ¡Proceso terminado! Archivo guardado en: {ruta_salida}")