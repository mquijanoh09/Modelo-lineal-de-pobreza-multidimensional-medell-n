# -*- coding: utf-8 -*-
"""
07_clusters.py — FASE PREVIA del Modelo 4: construir el conjunto T de clusteres.

El Modelo 4 parte los 15 indicadores en dos:
  V = bienes publicos  -> se focalizan por ZONA geografica (igual que el Modelo 3)
  U = bienes privados  -> se focalizan por CLUSTER de hogares

Este archivo construye esos clusteres. NO optimiza nada: la pertenencia de un
hogar a un cluster es DATO DE ENTRADA del MILP, no variable de decision. Se
calcula una sola vez, antes de optimizar, y queda fija.

DECISION METODOLOGICA CENTRAL — por que la demografia y no las privaciones
-------------------------------------------------------------------------
El PDF de seleccion de variables proponia agrupar por el vector de privacion en
U mas una proxy de ingreso. Dos razones para no hacerlo:

1. No se puede: la base del IPM 2025 no trae ninguna variable de ingreso ni de
   gasto. Se verifico columna por columna.

2. No se debe: los Modelos 3 y 4 asumen que el Estado NO observa las privaciones
   del hogar. Si los clusteres se construyen sobre esas mismas privaciones, se
   le esta devolviendo al planificador justo la informacion que el modelo dice
   que no tiene, y el supuesto de informacion imperfecta se vuelve incoherente.

Por eso agrupamos por variables que el Estado SI observa: composicion
demografica del hogar y caracteristicas del jefe. Es lo que hay en cualquier
registro administrativo tipo Sisben, y es lo que de hecho usan los programas
sociales colombianos para focalizar. El cluster representa un TIPO DE HOGAR,
no un tipo de carencia.

Salida: data/processed/hogares_con_cluster.csv
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from utils_dane import leer, a_numero, OUT

FILTRO  = {"DEPARTAMENTO": [5]}     # mismo escenario que el Modelo 3
SEMILLA = 2026
K_RANGO = range(2, 11)              # valores de k a evaluar
K_ELEGIDO = 4                       # elegido con el codo + la viabilidad del mecanismo (ver abajo)

IND = ["logro_educativo", "analfabetismo",
       "inasistencia_escolar", "rezago_escolar", "atencion_integral", "trabajo_infantil",
       "desempleo_larga_duracion", "empleo_formal",
       "aseguramiento_salud", "barreras_acceso_salud",
       "acueducto", "alcantarillado", "pisos", "paredes", "hacinamiento"]

# Particion J = U union V.  V = solo los que exigen infraestructura de red:
# un hogar solo no puede resolverlos sin inversion que beneficia a toda la zona.
V_PUBLICOS = ["acueducto", "alcantarillado"]
U_PRIVADOS = [j for j in IND if j not in V_PUBLICOS]

# Variables que alimentan k-means. Todas OBSERVABLES por el Estado.
RASGOS = ["n_personas", "n_menores5", "n_5a17", "n_mayores65",
          "tasa_dependencia", "edad_jefe", "jefe_mujer", "educ_jefe"]


# =============================================================================
# 1. CONSTRUIR LOS RASGOS DEL HOGAR
# =============================================================================
def construir_rasgos():
    hog = leer("HOGARES (DEPARTAMENTAL) 2025")
    viv = leer("VIVIENDAS (DEPARTAMENTAL) 2025", columnas=["DIRECTORIO", "P3"])
    hog = hog.merge(viv, on="DIRECTORIO", how="left", validate="many_to_one")
    for c in IND + ["PERSONAS", "FEX_C", "POBRE", "DEPARTAMENTO", "P3"]:
        hog[c] = a_numero(hog[c])
    for col, vals in FILTRO.items():
        hog = hog[hog[col].isin(vals)]
    hog = hog.reset_index(drop=True)

    per = leer("PERSONAS (DEPARTAMENTAL) 2025",
               columnas=["DIRECTORIO", "SECUENCIA_P", "ORDEN", "P6020", "P6040", "P6051", "P8587"])
    for c in ["P6020", "P6040", "P6051", "P8587"]:
        per[c] = a_numero(per[c])
    llave = ["DIRECTORIO", "SECUENCIA_P"]
    per = per.merge(hog[llave], on=llave, how="inner")   # solo los hogares del filtro

    # --- composicion por edades -------------------------------------------
    per["m5"]   = (per.P6040 < 5).astype(int)
    per["e5a17"]= ((per.P6040 >= 5) & (per.P6040 <= 17)).astype(int)
    per["adu"]  = ((per.P6040 >= 15) & (per.P6040 < 65)).astype(int)
    per["m65"]  = (per.P6040 >= 65).astype(int)
    per["dep"]  = ((per.P6040 < 15) | (per.P6040 >= 65)).astype(int)

    comp = per.groupby(llave).agg(
        n_menores5=("m5", "sum"), n_5a17=("e5a17", "sum"),
        n_adultos=("adu", "sum"), n_mayores65=("m65", "sum"),
        n_dependientes=("dep", "sum")).reset_index()

    # --- el jefe de hogar --------------------------------------------------
    # P6051 == 1 es el jefe. Verificado: hay exactamente uno por hogar (100%).
    jefe = per[per.P6051 == 1].groupby(llave).agg(
        edad_jefe=("P6040", "first"),
        sexo_jefe=("P6020", "first"),
        educ_jefe=("P8587", "first")).reset_index()

    r = hog.merge(comp, on=llave, how="left").merge(jefe, on=llave, how="left")
    r["n_personas"] = r.PERSONAS
    r["jefe_mujer"] = (r.sexo_jefe == 2).astype(int)

    # Tasa de dependencia: dependientes por adulto en edad de trabajar.
    # El max(...,1) evita dividir por cero en hogares sin adultos 15-64.
    r["tasa_dependencia"] = r.n_dependientes / r.n_adultos.clip(lower=1)

    # educ_jefe nula = el jefe no declaro nivel educativo. Se imputa la mediana
    # en vez de borrar el hogar: borrarlo cambiaria la poblacion representada y
    # por lo tanto la linea base del IPM.
    faltan = r.educ_jefe.isna().sum()
    r["educ_jefe"] = r.educ_jefe.fillna(r.educ_jefe.median())
    if faltan:
        print(f"  educ_jefe imputada con la mediana en {faltan} hogares de {len(r)}")

    assert r[RASGOS].notna().all().all(), "quedaron nulos en los rasgos"
    return r


# =============================================================================
# 2. ELEGIR k  (metodo del codo + coeficiente de silueta)
# =============================================================================
def diagnosticar_k(X, pesos):
    """Corre k-means para varios k y reporta inercia y silueta.

    INERCIA (metodo del codo): suma de distancias al cuadrado de cada hogar a su
    centroide. Siempre baja al subir k, asi que no se busca el minimo sino el
    'codo': el punto donde agregar un cluster mas deja de pagar.

    SILUETA: por cada hogar, que tan cerca esta de su propio cluster comparado
    con el cluster vecino mas cercano. Va de -1 a 1; por encima de 0,25 ya se
    considera estructura util, y a diferencia de la inercia SI tiene optimo
    interior, asi que es el criterio mas decisivo de los dos.
    """
    filas = []
    for k in K_RANGO:
        km = KMeans(n_clusters=k, random_state=SEMILLA, n_init=10)
        etq = km.fit_predict(X, sample_weight=pesos)
        sil = silhouette_score(X, etq) if k > 1 else np.nan
        tam = pd.Series(etq).value_counts()
        filas.append(dict(k=k, inercia=km.inertia_, silueta=sil,
                          min_hogares=tam.min(), max_hogares=tam.max()))
    d = pd.DataFrame(filas)
    d["caida_inercia"] = -d.inercia.diff() / d.inercia.shift() * 100
    return d


# =============================================================================
# 3. PERFILAR LOS CLUSTERES
# =============================================================================
def perfilar(r, etiquetas):
    r = r.assign(CLUSTER=etiquetas)
    pers = r.PERSONAS * r.FEX_C
    perfil = r.groupby("CLUSTER").apply(lambda g: pd.Series({
        "hogares": len(g),
        "personas_repr": (g.PERSONAS * g.FEX_C).sum(),
        **{c: g[c].mean() for c in RASGOS},
        "H (%)": 100 * np.average(g.POBRE, weights=g.PERSONAS * g.FEX_C),
    }), include_groups=False)
    return perfil.round(2)


if __name__ == "__main__":
    print("\n=== 1. RASGOS ===")
    r = construir_rasgos()
    print(f"  {len(r):,} hogares, {len(RASGOS)} rasgos observables")
    print(r[RASGOS].describe().round(2).to_string())

    # ESTANDARIZAR es obligatorio: k-means usa distancia euclidiana, asi que sin
    # estandarizar la variable de mayor rango (aqui educ_jefe, que va de 1 a 13)
    # domina sobre jefe_mujer, que solo vale 0 o 1. Se centra en 0 y se escala a
    # desviacion 1 para que todas pesen igual.
    X = StandardScaler().fit_transform(r[RASGOS].to_numpy(float))

    # PONDERAR por el factor de expansion: sin esto los clusteres describen la
    # MUESTRA, no la poblacion. sklearn lo acepta via sample_weight.
    pesos = r.FEX_C.to_numpy(float)

    print("\n=== 2. DIAGNOSTICO DE k ===")
    d = diagnosticar_k(X, pesos)
    print(d.round(3).to_string(index=False))
    print("\n  'caida_inercia' = cuanto baja la inercia respecto a k-1, en %.")
    print("  El codo esta donde esa caida se aplana. La silueta se lee aparte:")
    print(f"  mejor silueta en k = {int(d.loc[d.silueta.idxmax(), 'k'])}")

    if K_ELEGIDO is None:
        print("\n  K_ELEGIDO esta en None: mira el diagnostico, fijalo arriba y vuelve a correr.")
    else:
        km = KMeans(n_clusters=K_ELEGIDO, random_state=SEMILLA, n_init=10)
        etq = km.fit_predict(X, sample_weight=pesos)
        print(f"\n=== 3. PERFIL DE LOS {K_ELEGIDO} CLUSTERES ===")
        print(perfilar(r, etq).to_string())
        r["CLUSTER"] = etq
        salida = OUT / "hogares_con_cluster.csv"
        r.to_csv(salida, index=False)
        print(f"\nGuardado: {salida}")
