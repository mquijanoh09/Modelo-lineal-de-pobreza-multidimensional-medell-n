# -*- coding: utf-8 -*-
"""
05_modelo3.py — Modelo 3: focalizacion geografica estocastica (MILP).

PRINCIPIO DE DISENO: el modelo NO sabe como filtraste los datos.
Todo lo que depende de la muestra (MPI_s, los denominadores de celda, el
conjunto activo, que hogares existen) se calcula en tiempo de ejecucion a
partir del DataFrame que le pases. Cambiar el filtro geografico es cambiar
el diccionario FILTRO de abajo; no se toca ni una linea del modelo.

Formulacion: ver `revision-formulacion-modelo3.md` en el proyecto.
Incluye las correcciones de unidades de p_jd y de MPI_s = M0.

Uso:  python3 05_modelo3.py
"""
import sys
import numpy as np
import pandas as pd
import pulp 

from utils_dane import leer, a_numero

# =============================================================================
# CONFIGURACION — lo unico que cambias al cambiar de escenario
# =============================================================================
FILTRO  = {"DEPARTAMENTO": [5]}   # Antioquia completa. {} = nacional.
COL_CELDA = "P3"                  # la variable que define el conjunto D
MPI_R   = 0.00                    # meta de reduccion. Capa 1: 0.00 (verificado: da esfuerzo 0)
EPS     = 1e-6                    # rompe empates en p_jd == R_ij
SEMILLA = 2026
REPLICA = 0                       # indice de la corrida de Monte Carlo
N_POR_CELDA = 200                 # None = toda la base. Un entero = muestra de
                                  # desarrollo con ese numero de hogares POR CELDA.
USAR_CORTES_PREFIJO = True        # R3c: desigualdades validas (ver nota abajo)
TIEMPO_MAX = 120                  # segundos

# TODO-EF: costo por persona de resolver una privacion en j. En 1.0 el objetivo
# mide "personas-privacion resueltas". Calibrar con costos unitarios DNP/DPS.
# TODO-COTAS: E_min_j y E_max_j. Se dejan desactivadas en la capa 1 — las cotas
# INFERIORES son la causa #1 de infactibilidad (ver paso 4 de la revision).
USAR_COTAS = False

IND = ["logro_educativo", "analfabetismo",
       "inasistencia_escolar", "rezago_escolar", "atencion_integral", "trabajo_infantil",
       "desempleo_larga_duracion", "empleo_formal",
       "aseguramiento_salud", "barreras_acceso_salud",
       "acueducto", "alcantarillado", "pisos", "paredes", "hacinamiento"]
DIMS = {"Educacion": IND[0:2], "Ninez": IND[2:6], "Trabajo": IND[6:8],
        "Salud": IND[8:10], "Vivienda": IND[10:15]}
W = {j: 0.2 / len(js) for js in DIMS.values() for j in js}
K_GRID = 0.33   # 'puntaje < 1/3' es exactamente 'puntaje <= 0.33' (pesos multiplos de 0.01)
NOM_CLASE = {1: "Cabecera", 2: "Centro poblado", 3: "Rural disperso"}


# =============================================================================
# 1. DATOS — todo parametrizado, nada hardcodeado
# =============================================================================
def cargar():
    hog = leer("HOGARES (DEPARTAMENTAL) 2025")
    viv = leer("VIVIENDAS (DEPARTAMENTAL) 2025", columnas=["DIRECTORIO", "P3"])
    hog = hog.merge(viv, on="DIRECTORIO", how="left", validate="many_to_one")
    for c in IND + ["PERSONAS", "FEX_C", "IPM", "POBRE", "DEPARTAMENTO", "P3"]:
        hog[c] = a_numero(hog[c])
    for col, vals in FILTRO.items():
        hog = hog[hog[col].isin(vals)]
    hog = hog.reset_index(drop=True)
    hog["ID"] = hog.DIRECTORIO.astype(str) + "_" + hog.SECUENCIA_P.astype(str)
    hog["CELDA"] = hog[COL_CELDA].map(NOM_CLASE) if COL_CELDA == "P3" else hog[COL_CELDA].astype(str)
    if N_POR_CELDA:
        hog = muestra_desarrollo(hog, N_POR_CELDA)
    return hog


def muestra_desarrollo(hog, n_por_celda):
    """Muestra de desarrollo ESTRATIFICADA POR CELDA x CONDICION DE POBREZA.

    Cuatro cosas que no se pueden hacer de otra forma:

    1. Estratificar por celda, no muestrear al azar sobre toda la tabla. Un
       muestreo simple te deja las celdas chicas (Centro poblado) con 20 hogares
       y las grandes intactas: |D| sobrevive pero los denominadores Den_jd de las
       celdas chicas se vuelven 1 o 2 y el mecanismo estocastico deja de ser
       informativo justo donde ya era fragil.

    2. Estratificar TAMBIEN por condicion de pobreza. Solo el 14% de los hogares
       es pobre, asi que un muestreo aleatorio dentro de la celda te deja ~14
       pobres por celda y M0 queda altisimamente ruidoso: medido, la meta
       MPI_s*(1-MPI_r) saltaba entre 0.031 y 0.070 segun el tamano, cuando el
       valor real de la base completa es 0.0387. Fijando la proporcion de pobres
       dentro de cada celda, M0 queda casi identico al real y las metas de
       reduccion que pruebes significan lo mismo que en la corrida final.

    3. Recalibrar el factor de expansion dentro de cada estrato. FEX_C esta
       calibrado para la muestra completa; si te quedas con la mitad de los
       hogares y no reescalas, la poblacion representada se cae a la mitad.
       Se reescala por (celda, pobre) para preservar el peso relativo de cada
       estrato, que es lo que determina el IPM agregado.

    4. NO tocar la semilla de R_ij. Como se deriva del ID del hogar (ver
       sortear_R), cada hogar conserva su mismo R en la muestra y en la base
       completa, asi que las dos corridas son comparables.

    OJO: aun con esto, la muestra sirve para DEPURAR Y MEDIR TIEMPOS. Los
    resultados de politica (que celda recibe cuanto esfuerzo) se reportan solo
    con la base completa.
    """
    w = np.array([W[j] for j in IND])
    pobre = (np.round(hog[IND].to_numpy(float) @ w, 2) >= 1/3).astype(int)
    hog = hog.assign(_POBRE0=pobre)
    estrato = ["CELDA", "_POBRE0"]

    pers_full = (hog.PERSONAS * hog.FEX_C).groupby([hog.CELDA, hog._POBRE0]).sum()

    partes = []
    for (d, pb), g in hog.groupby(estrato):
        # cuota proporcional del estrato dentro de su celda, con minimo de 1
        en_celda = (hog.CELDA == d).sum()
        cuota = max(1, int(round(n_por_celda * len(g) / en_celda)))
        partes.append(g.sample(min(len(g), cuota), random_state=SEMILLA))
    sub = pd.concat(partes).reset_index(drop=True)

    # recalibracion por post-estratificacion, dentro de cada (celda, pobre)
    pers_sub = (sub.PERSONAS * sub.FEX_C).groupby([sub.CELDA, sub._POBRE0]).sum()
    factor = (pers_full / pers_sub)
    sub["FEX_C"] = sub.FEX_C * pd.MultiIndex.from_arrays(
        [sub.CELDA, sub._POBRE0]).map(factor).to_numpy()

    tasa_full = (hog.PERSONAS * hog.FEX_C * hog._POBRE0).sum() / (hog.PERSONAS * hog.FEX_C).sum()
    tasa_sub = (sub.PERSONAS * sub.FEX_C * sub._POBRE0).sum() / (sub.PERSONAS * sub.FEX_C).sum()
    print(f"\n  MUESTRA DE DESARROLLO: {len(sub):,} hogares de {len(hog):,} "
          f"(~{n_por_celda} por celda), estratificada por celda x pobreza")
    print(f"    pobres en muestra: {int(sub._POBRE0.sum())} de {int(hog._POBRE0.sum())}"
          f" | H0 completa={tasa_full:.4f} vs muestra={tasa_sub:.4f}")
    return sub.drop(columns=["_POBRE0"])


def sortear_R(hog, replica):
    """R_ij ~ U[0,1], reproducible y ESTABLE ante filtros.

    La semilla de cada hogar se deriva de su ID, no de su posicion en la tabla.
    Asi el hogar 8369550_1 recibe el mismo R tanto si corres Antioquia completa
    como si corres solo cabecera: los escenarios quedan comparables.
    """
    R = np.empty((len(hog), len(IND)))
    for n, (d, s) in enumerate(zip(hog.DIRECTORIO, hog.SECUENCIA_P)):
        ss = np.random.SeedSequence([SEMILLA, replica, int(d), int(s)])
        R[n] = np.random.default_rng(ss).random(len(IND))
    return R


# =============================================================================
# 2. MODELO
# =============================================================================
def construir_y_resolver(hog, R, mpi_r):
    M  = hog[IND].to_numpy(float)
    HS = hog.PERSONAS.to_numpy(float)
    HW = hog.FEX_C.to_numpy(float)
    pers = HS * HW                      # personas representadas por el hogar
    w  = np.array([W[j] for j in IND])
    nI, nJ = M.shape

    # --- Linea base, calculada de ESTOS datos (nunca hardcodeada) -----------
    score0 = np.round(M @ w, 2)
    pobre0 = (score0 >= 1/3).astype(int)
    H0 = (pers * pobre0).sum() / pers.sum()
    A0 = (pers * pobre0 * score0).sum() / (pers * pobre0).sum()
    MPI_S = (pers * pobre0 * score0).sum() / pers.sum()      # M0 = H0 * A0

    celdas = sorted(hog.CELDA.unique())
    if len(celdas) < 2:
        sys.exit(f"\n*** |D| = {len(celdas)}. Con una sola celda E_jd colapsa a E_j "
                 f"y el mecanismo de focalizacion geografica desaparece: esto ya no "
                 f"es el Modelo 3. Revisa FILTRO / COL_CELDA.\n")
    idx_celda = {d: np.where(hog.CELDA.values == d)[0] for d in celdas}

    # Den_jd = personas privadas en j dentro de la celda d  (CORRECCION DE UNIDADES:
    # numerador y denominador de p_jd van ambos en personas, no personas/hogares)
    Den = {(j, d): float((HS[idx_celda[d]] * M[idx_celda[d], jj]).sum())
           for jj, j in enumerate(IND) for d in celdas}

    # Conjunto activo: si M_ij = 0 entonces N_ij = 0 por construccion
    A = [(i, jj) for i in range(nI) for jj in range(nJ) if M[i, jj] == 1]
    # Solo los hogares POBRES hoy pueden aportar a C_i: el puntaje solo puede bajar
    # (N <= M), asi que un hogar no pobre hoy nunca se vuelve pobre.
    pobres_idx = np.where(pobre0 == 1)[0]

    print(f"\n  |I| = {nI:,} hogares | |D| = {len(celdas)} celdas | |A| = {len(A):,} pares activos")
    print(f"  binarias: N={len(A):,} + b1={len(pobres_idx):,} = {len(A)+len(pobres_idx):,}")
    print(f"  H0={H0:.4f}  A0={A0:.4f}  MPI_s=M0={MPI_S:.6f}  ->  meta <= {MPI_S*(1-mpi_r):.6f}")

    # --- Variables ----------------------------------------------------------
    m = pulp.LpProblem("Modelo3", pulp.LpMinimize)
    N  = {(i, jj): pulp.LpVariable(f"N_{i}_{jj}", cat="Binary") for i, jj in A}
    b1 = {i: pulp.LpVariable(f"b1_{i}", cat="Binary") for i in pobres_idx}
    C  = {i: pulp.LpVariable(f"C_{i}", lowBound=0) for i in pobres_idx}  # lowBound=0 es OBLIGATORIO
    E  = {(j, d): pulp.LpVariable(f"E_{j}_{d}", lowBound=0) for j in IND for d in celdas}

    def priv_resueltas(jj, d):
        """Personas cuya privacion en j SE RESOLVIO en la celda d.
        Es sum_i HS_i*(M_ij - N_ij); con M_ij=1 queda sum_i HS_i*(1 - N_ij)."""
        return pulp.lpSum(HS[i] * (1 - N[(i, jj)]) for i in idx_celda[d] if (i, jj) in N)

    # --- R1: esfuerzo por celda --------------------------------------------
    EF = {j: 1.0 for j in IND}   # TODO-EF
    for jj, j in enumerate(IND):
        for d in celdas:
            m += E[(j, d)] == EF[j] * priv_resueltas(jj, d), f"R1_{jj}_{d}"

    # --- R2: cotas de esfuerzo (desactivadas en la capa 1) ------------------
    if USAR_COTAS:
        pass  # TODO-COTAS

    # --- R3: mecanismo estocastico linealizado ------------------------------
    # p_jd = priv_resueltas / Den_jd  in [0,1].  Big-M = 1 y 2, no una constante grande.
    n_cortes = 0
    for jj, j in enumerate(IND):
        for d in celdas:
            if Den[(j, d)] == 0:
                continue                      # celda sin privacion en j: nada que decidir
            # p_jd se escribe usando la variable E ya definida en R1:
            #   p_jd = E_jd / (EF_j * Den_jd)
            # TIP: NO inline-ar aqui la suma de ~1000 terminos de priv_resueltas().
            # Si lo haces, cada una de las ~1000 restricciones de abajo copia esa
            # suma entera y terminas con millones de terminos: PuLP se cuelga antes
            # de llamar al solver. Referenciar una sola variable deja 2 terminos.
            # Se multiplica por el inverso en vez de dividir: en PuLP 2.x una
            # LpVariable no soporta '/' (TypeError), solo '*' por una constante.
            p = (1.0 / (EF[j] * Den[(j, d)])) * E[(j, d)]
            activos_d = [i for i in idx_celda[d] if (i, jj) in N]
            for i in activos_d:
                m += p >= R[i, jj] - N[(i, jj)],                  f"R3a_{i}_{jj}"
                m += p <= R[i, jj] - EPS + 2 * (1 - N[(i, jj)]),  f"R3b_{i}_{jj}"
            # R3c: los curados son siempre un PREFIJO del orden de R. Implicito en
            # el modelo, invisible para el solver: agregarlo aprieta la relajacion.
            if USAR_CORTES_PREFIJO and len(activos_d) > 1:
                orden = sorted(activos_d, key=lambda i: R[i, jj])
                for a, b in zip(orden, orden[1:]):
                    m += N[(a, jj)] <= N[(b, jj)], f"R3c_{a}_{b}_{jj}"
                    n_cortes += 1

    # --- R4-R6: censura Alkire-Foster post-intervencion ---------------------
    # Big-M indexado por hogar (HS_i*HW_i), no global.
    for i in pobres_idx:
        score_post = pulp.lpSum(w[jj] * N[(i, jj)] for jj in range(nJ) if (i, jj) in N)
        Mi = pers[i]
        m += C[i] + Mi * b1[i] >= Mi * score_post, f"R4_{i}"
        m += C[i] - Mi * b1[i] <= Mi * score_post, f"R5_{i}"
        m += score_post - (1 - b1[i]) <= K_GRID,   f"R6_{i}"

    # --- R7: meta de reduccion del IPM (sobre M0, no sobre H) ---------------
    m += pulp.lpSum(C.values()) <= MPI_S * (1 - mpi_r) * pers.sum(), "R7_meta"

    # --- Objetivo -----------------------------------------------------------
    m += pulp.lpSum(E.values())

    print(f"  restricciones: {len(m.constraints):,} (de las cuales {n_cortes:,} son cortes de prefijo)")
    m.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=TIEMPO_MAX))
    return m, N, C, E, dict(celdas=celdas, M=M, HS=HS, pers=pers, w=w,
                            score0=score0, pobre0=pobre0, MPI_S=MPI_S, Den=Den)


# =============================================================================
# 3. REPORTE
# =============================================================================
def reportar(m, N, C, E, ctx, mpi_r):
    # LpStatus solo dice si CBC termino; sol_status dice QUE devolvio. Si CBC
    # corta por timeLimit con una solucion entera en mano, LpStatus puede decir
    # "Optimal" aunque el gap no este cerrado: eso es una cota, no el optimo.
    sol = pulp.LpSolution.get(m.sol_status, str(m.sol_status))
    print(f"\n  estado: {pulp.LpStatus[m.status]} | solucion: {sol}")
    if m.sol_status not in (pulp.LpSolutionOptimal, pulp.LpSolutionIntegerFeasible):
        return
    if m.sol_status != pulp.LpSolutionOptimal:
        print("  OJO: solucion factible SIN probar optimalidad (gap abierto). "
              "El esfuerzo reportado es una cota superior.")
    M, HS, pers, w = ctx["M"], ctx["HS"], ctx["pers"], ctx["w"]
    score0, pobre0 = ctx["score0"], ctx["pobre0"]
    Npost = M.copy()
    for (i, jj), v in N.items():
        Npost[i, jj] = round(v.value())
    score1 = np.round(Npost @ w, 2)
    pobre1 = (score1 >= 1/3).astype(int)
    H1 = (pers * pobre1).sum() / pers.sum()
    M1 = (pers * pobre1 * score1).sum() / pers.sum()

    print(f"  esfuerzo total (objetivo) = {pulp.value(m.objective):,.1f} personas-privacion")
    print(f"  M0: {ctx['MPI_S']:.6f} -> {M1:.6f}   (meta <= {ctx['MPI_S']*(1-mpi_r):.6f})")
    print(f"  H : {(pers*pobre0).sum()/pers.sum():.4f} -> {H1:.4f}")

    curadas = (M - Npost)
    if curadas.sum() > 0:
        # ERROR DE INCLUSION: esfuerzo gastado en hogares que NO eran pobres.
        # El mecanismo los arrastra porque su R cayo bajo el umbral de la celda.
        esf = (HS[:, None] * curadas).sum(axis=1)
        incl = esf[pobre0 == 0].sum() / esf.sum()
        print(f"  privaciones resueltas: {int(curadas.sum()):,}")
        print(f"  ERROR DE INCLUSION: {incl:.1%} del esfuerzo cayo en hogares no pobres")
        print("\n  esfuerzo por celda e indicador (solo lo no nulo):")
        for (j, d), v in E.items():
            if v.value() and v.value() > 1e-6:
                print(f"    {d:<16} {j:<26} {v.value():10,.1f}")


if __name__ == "__main__":
    # Permite barrer metas sin editar el archivo:  python3 05_modelo3.py 0.10
    if len(sys.argv) > 1:
        MPI_R = float(sys.argv[1])
    hog = cargar()
    R = sortear_R(hog, REPLICA)
    print(f"\n{'='*70}\n MODELO 3 — filtro={FILTRO} celda={COL_CELDA} MPI_r={MPI_R}\n{'='*70}")
    m, N, C, E, ctx = construir_y_resolver(hog, R, MPI_R)
    reportar(m, N, C, E, ctx, MPI_R)
