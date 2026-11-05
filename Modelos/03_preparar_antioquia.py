"""
03_preparar_antioquia.py
1. Valida que P3 (VIVIENDAS) es la variable de clase:
   1 = cabecera, 2 = centro poblado, 3 = rural disperso.
     Prueba A: H por clase con la base NACIONAL vs. cifras oficiales DANE 2025
               (nacional 9.9%, cabeceras 6.3%, centros poblados y rural disperso 22.4%).
     Prueba B: en hogares urbanos, las privaciones de acueducto y alcantarillado
               deben coincidir exactamente con "no tiene el servicio".
2. Construye la base COMÚN de los cuatro modelos del proyecto:
   Antioquia completa (base DEPARTAMENTAL, DEPARTAMENTO == 5), las tres zonas de P3.

   Esta base la usan:
     - Modelos 1 y 2 (información perfecta, focalización hogar por hogar)
     - Modelos 3 y 4 (focalización por zona; requieren al menos 2 zonas en P3)
   NO agregar filtros adicionales sin coordinarlo: cualquier filtro cambia el
   universo de los cuatro modelos y rompe la comparación entre ellos.

Requiere utils_dane.py en la raíz del proyecto.
Salida: data/processed/hogares_antioquia.csv
"""
from utils_dane import leer, a_numero, RAIZ_DEP, RAIZ_NAC, OUT

INDICADORES = [
    "logro_educativo", "analfabetismo",
    "inasistencia_escolar", "rezago_escolar", "atencion_integral", "trabajo_infantil",
    "desempleo_larga_duracion", "empleo_formal",
    "aseguramiento_salud", "barreras_acceso_salud",
    "acueducto", "alcantarillado", "pisos", "paredes", "hacinamiento",
]
CABECERA = 1
ZONAS = {1: "Cabecera", 2: "Centro poblado", 3: "Rural disperso"}
OFICIAL = {"Nacional": 9.9, "Cabeceras": 6.3, "Centros poblados y rural disperso": 22.4}


def cargar_con_p3(version, raiz):
    """Lee HOGARES de una versión y le pega P3 y los servicios desde VIVIENDAS."""
    hog = leer(f"HOGARES ({version}) 2025", raiz=raiz)
    viv = leer(f"VIVIENDAS ({version}) 2025", raiz=raiz,
               columnas=["DIRECTORIO", "P3", "P8520S3", "P8520S5"])

    if viv["DIRECTORIO"].duplicated().any():
        raise ValueError(f"VIVIENDAS ({version}): DIRECTORIO repetido.")
    hog = hog.merge(viv, on="DIRECTORIO", how="left", validate="many_to_one")
    if hog["P3"].isna().any():
        raise ValueError(f"{hog['P3'].isna().sum()} hogares sin P3 en {version}.")

    numericas = INDICADORES + ["PERSONAS", "FEX_C", "IPM", "POBRE",
                               "P3", "P8520S3", "P8520S5"]
    if "DEPARTAMENTO" in hog.columns:
        numericas.append("DEPARTAMENTO")
    for c in numericas:
        hog[c] = a_numero(hog[c])
    return hog


def incidencia(df):
    """H = sum(HW_i * HS_i * POBRE_i) / sum(HW_i * HS_i), en porcentaje."""
    peso = df["FEX_C"] * df["PERSONAS"]
    return 100 * (peso * df["POBRE"]).sum() / peso.sum()


# ==================================================================
# PRUEBA A: replicar las cifras oficiales por clase (base NACIONAL)
# ==================================================================
nac = cargar_con_p3("NACIONAL", RAIZ_NAC)
urbano = nac["P3"] == CABECERA

calculado = {
    "Nacional": incidencia(nac),
    "Cabeceras": incidencia(nac[urbano]),
    "Centros poblados y rural disperso": incidencia(nac[~urbano]),
}
print("\n===== PRUEBA A: H calculado vs. oficial DANE 2025 =====")
for dominio, h in calculado.items():
    print(f"   {dominio:<36} calculado = {h:5.2f}%   oficial = {OFICIAL[dominio]:4.1f}%   "
          f"diferencia = {h - OFICIAL[dominio]:+.2f} p.p.")

# ==================================================================
# PRUEBA B: consistencia de acueducto y alcantarillado en lo urbano
#   P8520S5 = acueducto (1 sí, 2 no) | P8520S3 = alcantarillado (1 sí, 2 no)
# ==================================================================
print("\n===== PRUEBA B: privación vs. 'no tiene el servicio' =====")
for ind, servicio in (("acueducto", "P8520S5"), ("alcantarillado", "P8520S3")):
    sin_servicio = (nac[servicio] == 2).astype(int)
    coincide = nac[ind] == sin_servicio
    print(f"   {ind:<15} urbano: {coincide[urbano].mean():7.2%} coincide | "
          f"rural: {coincide[~urbano].mean():7.2%} coincide")

# ==================================================================
# CONSTRUCCIÓN: Antioquia completa (base DEPARTAMENTAL)
# ==================================================================
dep = cargar_con_p3("DEPARTAMENTAL", RAIZ_DEP)

if dep.duplicated(["DIRECTORIO", "SECUENCIA_P"]).any():
    raise ValueError("La llave DIRECTORIO + SECUENCIA_P no es única por hogar.")

ant = dep[dep["DEPARTAMENTO"] == 5].copy()
ant["P3"] = ant["P3"].astype(int)
ant["ID_HOGAR"] = ant["DIRECTORIO"].astype(str) + "_" + ant["SECUENCIA_P"].astype(str)

if ant["P3"].nunique() < 2:
    raise ValueError("La base tiene menos de 2 zonas en P3: los Modelos 3 y 4 no corren.")

# Tabla por zona
print("\n===== Antioquia completa por zona (base DEPARTAMENTAL) =====")
print(f"   {'Zona':<18}{'Hogares':>9}{'Pobres':>8}{'H':>9}{'Personas repr.':>17}")
for p3, nombre in ZONAS.items():
    z = ant[ant["P3"] == p3]
    print(f"   {p3} {nombre:<16}{len(z):>9,}{int(z['POBRE'].sum()):>8,}"
          f"{incidencia(z):>8.2f}%{(z['FEX_C'] * z['PERSONAS']).sum():>17,.0f}")
print(f"   {'Total':<18}{len(ant):>9,}{int(ant['POBRE'].sum()):>8,}"
      f"{incidencia(ant):>8.2f}%{(ant['FEX_C'] * ant['PERSONAS']).sum():>17,.0f}")

# Tamaño esperado del modelo
M = ant[INDICADORES].to_numpy()
pobres = ant["POBRE"].to_numpy() == 1
print("\n===== Tamaño esperado del MILP (Modelos 1 y 2) =====")
print(f"   Hogares totales:                          {len(ant):,}")
print(f"   Privaciones M_ij = 1 (todas):             {int(M.sum()):,}")
print(f"   Hogares pobres (los únicos relevantes):   {pobres.sum():,}")
print(f"   Privaciones M_ij = 1 en hogares pobres:   {int(M[pobres].sum()):,}")

# Guardar: columnas que necesitan los cuatro modelos
columnas = (["ID_HOGAR", "DIRECTORIO", "SECUENCIA_P", "DEPARTAMENTO", "P3"]
            + INDICADORES + ["PERSONAS", "FEX_C", "IPM", "POBRE"])
salida = OUT / "hogares_antioquia.csv"
ant[columnas].to_csv(salida, index=False)
print(f"\nGuardado: {salida}  ({len(ant):,} hogares, {len(columnas)} columnas)")