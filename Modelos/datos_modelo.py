"""
datos_modelo.py
Arma TODOS los datos que necesita el MILP del Modelo 1 (y del Modelo 2) a partir de:
  - data/processed/hogares_antioquia.csv   (03: hogares, indicadores, factor de expansión)
  - data/processed/conteo_pares.csv        (05: u_ij y costo por hogar/indicador)
  - data/processed/ninos.csv, adultos_clei.csv, logro_hogar.csv   (05)
  - parametros.py                          (costos, escenarios)

No resuelve nada: solo convierte tablas en diccionarios con los nombres de la
formulación (formulacion_modelo1.md §1-§2). Los modelos solo leen este objeto.

Convención de índices (acordada con el hilo del Modelo 2):
    i = ID_HOGAR (DIRECTORIO_SECUENCIA_P)      k, a = ID_PERSONA (ID_HOGAR_ORDEN)
    j = nombre del indicador                    s = "E1" | "E2" | "E3"

Uso:
    from datos_modelo import cargar_datos
    d = cargar_datos()                   # caso base
    d = cargar_datos("p_050")            # una sensibilidad de parametros.SENSIBILIDADES
"""
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parametros as P
from utils_dane import OUT, resumen_ipm

# Indicadores cuya privación se quita pagando x_ij con costo propio c_ij (formulación §2.2).
# Los otros cuatro (rezago, inasistencia, logro, analfabetismo) NO tienen costo propio: se
# pagan por niño (z), por hogar (t) o por adulto (v).
INDICADORES_SIMPLES = [j for j in P.INDICADORES if j not in P.INDICADORES_POR_PERSONA_O_NINO]
ESTRATEGIAS = ("E1", "E2", "E3")


@dataclass
class Datos:
    esc: dict
    # ---- hogares pobres (conjunto I) -------------------------------------------------
    hogares: pd.DataFrame            # índice i: HW, HS, p, P3, zona_costo, c0, M
    J: dict                          # i -> [indicadores con M_ij = 1]
    c: dict                          # (i, j) -> costo c_ij en pesos (ya multiplicado por HW_i)
    quitable: dict                   # (i, j) -> False si la privación NO se puede quitar este año
    A: dict                          # i -> valores que puede tomar el puntaje s_i (tangentes)
    pobres_zona: pd.Series           # Pobres_d^0: personas pobres iniciales por zona P3
    Sev0: float
    # ---- niños: K (cohorte de rezago) y N (no asisten, 6 a 16) ----------------------
    ninos: pd.DataFrame              # índice k: HW, edad, e_k, atraso, asiste, b, hogar i
    K: list
    N: list
    K_i: dict                        # i -> [k de la cohorte]
    N_i: dict                        # i -> [k que no asisten]
    S_k: dict                        # k -> [estrategias elegibles]
    c_ks: dict                       # (k, s) -> costo en pesos (ya con HW_k)
    d_ks: dict                       # (k, s) -> grados que quita la estrategia
    coef_ks: dict                    # (k, s) -> cuánto baja SevEdu
    obligatorios: list               # k con E-7 (art. 67)
    sevedu_sin: float                # SevEdu^N_{1,sin}
    C_RC: dict                       # i -> Renta Ciudadana del hogar (pesos)
    # ---- adultos: logro y analfabetismo ----------------------------------------------
    adultos: pd.DataFrame            # índice a: HW, edad, anios, g_a, hogar i, analfabeta
    L_i: dict                        # i -> [a elegibles a CLEI]
    c_v: dict                        # a -> costo del ciclo (pesos, con HW)
    g_a: dict                        # a -> años que gana
    D_i: dict                        # i -> déficit de años para promedio 9
    analfabetas_i: dict              # i -> [a analfabetas del hogar]
    linea_base: tuple                # (H0, A0, M0) de TODO Antioquia, sobre los 3,732 hogares
    todos: pd.DataFrame = None       # los 3,732 hogares (índice i: p, c0, P3): para recalcular M0 de todo Antioquia
    imputados: set = field(default_factory=set)   # (i, j) cuyo u_ij fue imputado en el 05 (no se ve a quién pagar)
    notas: list = field(default_factory=list)


def _sumas_posibles(pesos):
    """Valores que puede tomar sum_j w_j (1 - x_ij): sumas de todos los subconjuntos, a 0.01."""
    vals = {0}
    for w in pesos:                       # w en centésimas para evitar errores de punto flotante
        w = int(round(w * 100))
        vals |= {v + w for v in vals}
    return sorted(v / 100 for v in vals)


def cargar_datos(nombre_escenario="base", verbose=False):
    esc = P.escenario(nombre_escenario)
    if esc["u_igual_1"]:
        raise NotImplementedError("El escenario u = 1 se programa en el paso 3.7 (barridos).")
    notas = []

    # ------------------------------------------------------------------ hogares pobres
    hog = pd.read_csv(OUT / "hogares_antioquia.csv")
    hog["ID_HOGAR"] = hog.ID_HOGAR.astype(str)
    w = np.array([P.PESOS[j] for j in P.INDICADORES])
    hog["c0"] = np.round(hog[P.INDICADORES].to_numpy() @ w, 2)
    hog["p"] = hog.FEX_C * hog.PERSONAS
    H0, A0, M0 = resumen_ipm(hog.p, hog.c0, P.K)          # M0 de TODO Antioquia (regresión)

    todos = hog.set_index("ID_HOGAR")[["p", "c0", "P3"]]
    pob = hog[hog.c0 >= P.K - 1e-9].set_index("ID_HOGAR")
    pob["HW"] = pob.FEX_C
    pob["HS"] = pob.PERSONAS
    pob["zona_costo"] = pob.P3.map(P.zona_costo)
    pob["M"] = np.round(pob.c0 - P.K_GRID, 2)               # big-M de la restricción de salida
    hogares = pob[["HW", "HS", "p", "P3", "zona_costo", "c0", "M"]]
    ids = set(hogares.index)

    J = {i: [j for j in P.INDICADORES if pob.at[i, j] == 1] for i in hogares.index}
    A = {i: _sumas_posibles([P.PESOS[j] for j in J[i]]) for i in hogares.index}
    pobres_zona = hogares.groupby("P3").p.sum()
    Sev0 = float((hogares.p * hogares.c0 ** 2).sum())

    # ------------------------------------------------------------------ costos c_ij
    pares = pd.read_csv(OUT / "conteo_pares.csv")
    pares["ID_HOGAR"] = pares.ID_HOGAR.astype(str)
    pares = pares[pares.ID_HOGAR.isin(ids)].set_index(["ID_HOGAR", "indicador"])
    epf = P.tabla_epf(esc)
    c, quitable, imputados = {}, {}, set()
    for i in hogares.index:
        z, hw = hogares.at[i, "zona_costo"], hogares.at[i, "HW"]
        for j in J[i]:
            if j in epf:                                 # vivienda, salud, atención, trabajo infantil
                c[(i, j)] = epf[j][z] * pares.at[(i, j), "u_ij"] * hw
            elif j in ("empleo_formal", "desempleo_larga_duracion"):
                c[(i, j)] = pares.at[(i, j), "costo_hogar"] * hw    # persona por persona (05)
            quitable[(i, j)] = True
            if bool(pares.at[(i, j), "u_imputado"]):
                imputados.add((i, j))
                # Desempleo de larga duración sin desocupado identificado: no se sabe a quién pagar (7-nov,
                # consejo del auditor, igual que inasistencia). La sensibilidad "desempleo_imputado" lo permite.
                if j == "desempleo_larga_duracion" and not esc["desempleo_imputado"]:
                    quitable[(i, j)] = False

    # ------------------------------------------------------------------ niños (K y N)
    ni = pd.read_csv(OUT / "ninos.csv")
    ni["ID_HOGAR"] = ni.ID_HOGAR.astype(str)
    ni = ni[ni.ID_HOGAR.isin(ids)].set_index("ID_PERSONA")
    ni["hogar"] = ni.ID_HOGAR
    # Atraso al final del año sin intervenir: b = a0 + 1 - ap * asiste   (formulación §2.4)
    ni["b"] = ni.atraso + 1 - esc["ap"] * ni.asiste.astype(float)
    elig = {"E1": ni.elig_E1, "E2": ni.elig_E2, "E3": ni.elig_E3_sens & esc["usar_E3"]}
    precio = {"E1": ni.precio_E1_cupo, "E2": ni.precio_E2_E3_ciclo, "E3": ni.precio_E2_E3_ciclo}
    m = {"E1": ni.m_E1, "E2": ni.m_E2, "E3": ni.m_E3}

    K = list(ni.index[ni.en_cohorte_sevedu])
    N = list(ni.index[ni.no_asiste_6_16])
    K_i, N_i = {}, {}
    for k in K:
        K_i.setdefault(ni.at[k, "hogar"], []).append(k)
    for k in N:
        N_i.setdefault(ni.at[k, "hogar"], []).append(k)

    S_k, c_ks, d_ks, coef_ks = {}, {}, {}, {}
    for k, r in ni.iterrows():
        S_k[k] = [s for s in ESTRATEGIAS if bool(elig[s][k])]
        for s in S_k[k]:
            c_ks[(k, s)] = float(precio[s][k]) * r.HW
            d_ks[(k, s)] = float(m[s][k])
            # D3: los no asistentes SIN rezago solo aportan a H (coeficiente de SevEdu = 0)
            if r.en_cohorte_sevedu:
                d = d_ks[(k, s)]
                coef_ks[(k, s)] = r.HW * (2 * r.b * d - d * d) / (r.e_k + 1) ** 2
            else:
                coef_ks[(k, s)] = 0.0
    obligatorios = list(ni.index[ni.obligatorio_E7]) if esc["cobertura_art67"] else []
    cohorte = ni[ni.en_cohorte_sevedu]
    sevedu_sin = float((cohorte.HW * (cohorte.b / (cohorte.e_k + 1)) ** 2).sum())

    # Renta Ciudadana: se paga una vez por hogar, dividida entre p (cumplimiento)
    C_RC = {i: P.RENTA_CIUDADANA_ANUAL * hogares.at[i, "HW"] / esc["p"] for i in hogares.index}

    # ------------------------------------------------------------------ adultos (logro y analfabetismo)
    ad = pd.read_csv(OUT / "adultos_clei.csv")
    ad["ID_HOGAR"] = ad.ID_HOGAR.astype(str)
    ad = ad[ad.ID_HOGAR.isin(ids)].set_index("ID_PERSONA")
    ad["hogar"] = ad.ID_HOGAR
    elegibles = ad[ad.elegible_clei]
    L_i = {}
    for a, r in elegibles.iterrows():
        L_i.setdefault(r.hogar, []).append(a)
    c_v = {a: float(r.precio_ciclo) * r.HW for a, r in elegibles.iterrows()}
    g_a = {a: int(r.g_a) for a, r in elegibles.iterrows()}
    lg = pd.read_csv(OUT / "logro_hogar.csv")
    lg["ID_HOGAR"] = lg.ID_HOGAR.astype(str)
    D_i = dict(zip(lg.ID_HOGAR, lg.D_i))
    analfabetas_i = {}
    for a, r in ad[ad.analfabeta].iterrows():
        analfabetas_i.setdefault(r.hogar, []).append(a)

    # ------------------------------------------------------------------ ¿qué privaciones sí se pueden quitar este año?
    # logro: solo si los años que ganan los adultos elegibles cubren el déficit (restricción 11)
    # analfabetismo: solo si TODOS los analfabetas del hogar son elegibles a CLEI (restricción 12)
    # inasistencia: solo si a cada niño de N(i) se le puede ofrecer alguna estrategia (Inas)
    # rezago: solo si cada niño de K(i) tiene una estrategia que le quite todo el atraso (10a/10b)
    for i in hogares.index:
        for j in J[i]:
            if j == "logro_educativo":
                quitable[(i, j)] = sum(g_a[a] for a in L_i.get(i, [])) >= D_i[i]
            elif j == "analfabetismo":
                quitable[(i, j)] = bool(analfabetas_i.get(i)) and all(a in g_a and g_a[a] > 0 for a in analfabetas_i[i])
            elif j == "inasistencia_escolar":
                # si el DANE marca el hogar y el 05 no identifica a ningún niño, no se sabe a quién pagar: no se quita
                quitable[(i, j)] = bool(N_i.get(i)) and all(len(S_k[k]) > 0 for k in N_i[i])
            elif j == "rezago_escolar":
                quitable[(i, j)] = bool(K_i.get(i)) and all(
                    any(d_ks[(k, s)] >= ni.at[k, "atraso"] + 1 for s in S_k[k]) for k in K_i[i])

    return Datos(esc=esc, hogares=hogares, J=J, c=c, quitable=quitable, A=A,
                 pobres_zona=pobres_zona, Sev0=Sev0, ninos=ni, K=K, N=N, K_i=K_i, N_i=N_i,
                 S_k=S_k, c_ks=c_ks, d_ks=d_ks, coef_ks=coef_ks, obligatorios=obligatorios,
                 sevedu_sin=sevedu_sin, C_RC=C_RC, adultos=ad, L_i=L_i, c_v=c_v, g_a=g_a,
                 D_i=D_i, analfabetas_i=analfabetas_i, linea_base=(H0, A0, M0), todos=todos, imputados=imputados, notas=notas)


def subconjunto(d, ids):
    """Copia de `d` con solo los hogares `ids` (para probar el MILP en instancias pequeñas).

    Se queda con los niños, adultos, costos y reglas de esos hogares. `todos` (los 3,732
    hogares) y `linea_base` no se tocan: recalcular() los usa para M0 de todo Antioquia.
    """
    ids = list(ids)
    S = set(ids)
    ni = d.ninos[d.ninos.hogar.isin(S)]
    ad = d.adultos[d.adultos.hogar.isin(S)]
    ks, As = set(ni.index), set(ad.index)
    hog = d.hogares.loc[ids]
    coh = ni[ni.en_cohorte_sevedu]
    return replace(
        d, hogares=hog, J={i: d.J[i] for i in ids}, A={i: d.A[i] for i in ids},
        c={k: v for k, v in d.c.items() if k[0] in S}, quitable={k: v for k, v in d.quitable.items() if k[0] in S},
        pobres_zona=hog.groupby("P3").p.sum(), Sev0=float((hog.p * hog.c0 ** 2).sum()),
        ninos=ni, K=[k for k in d.K if k in ks], N=[k for k in d.N if k in ks],
        K_i={i: v for i, v in d.K_i.items() if i in S}, N_i={i: v for i, v in d.N_i.items() if i in S},
        S_k={k: v for k, v in d.S_k.items() if k in ks},
        c_ks={k: v for k, v in d.c_ks.items() if k[0] in ks}, d_ks={k: v for k, v in d.d_ks.items() if k[0] in ks},
        coef_ks={k: v for k, v in d.coef_ks.items() if k[0] in ks},
        obligatorios=[k for k in d.obligatorios if k in ks],
        sevedu_sin=float((coh.HW * (coh.b / (coh.e_k + 1)) ** 2).sum()),
        C_RC={i: d.C_RC[i] for i in ids}, adultos=ad,
        L_i={i: v for i, v in d.L_i.items() if i in S}, c_v={a: v for a, v in d.c_v.items() if a in As},
        g_a={a: v for a, v in d.g_a.items() if a in As}, D_i={i: d.D_i[i] for i in ids},
        analfabetas_i={i: v for i, v in d.analfabetas_i.items() if i in S},
        imputados={k for k in d.imputados if k[0] in S})


# ==================================================================
# Prueba de regresión: python datos_modelo.py
# ==================================================================
def _verificar(d):
    H0, A0, M0 = d.linea_base
    ok = lambda cond: "OK " if cond else "FALLA"
    print("=" * 72, "\n REGRESIÓN DE datos_modelo.py (caso base)\n", "=" * 72, sep="")
    print(f"{ok(len(d.hogares) == 523)} hogares pobres: {len(d.hogares)} (esperado 523)")
    print(f"{ok(abs(M0 - 0.038684) < 5e-7)} M0 de Antioquia = {M0:.6f} (esperado 0.038684) · H = {H0:.4%} · A = {A0:.4f}")
    print(f"{ok(abs(d.Sev0 - 117908) < 50)} Sev0 = {d.Sev0:,.0f} (esperado ≈ 117,908)")
    print(f"{ok(abs(d.sevedu_sin - 21562) < 5)} SevEdu^N(1,sin) = {d.sevedu_sin:,.0f} (esperado ≈ 21,562)")
    n_priv = sum(len(v) for v in d.J.values())
    print(f"{ok(abs(n_priv / len(d.hogares) - 4.96) < 0.01)} privaciones por hogar: {n_priv / len(d.hogares):.2f} (esperado 4.96)")
    n_A = sum(len(v) for v in d.A.values())
    print(f"{ok(n_A == 6571)} puntos de tangente (suma de |A_i|): {n_A:,} (esperado 6,571)")
    print(f"{ok((d.hogares.M > 0).all())} M_i = c0_i - 0.33 > 0 en todos los hogares")
    coh = [k for k in d.K]
    print(f"{ok(len(d.K) == 215)} cohorte K: {len(d.K)} niños en {len(d.K_i)} hogares (esperado 215 y 149)")
    print(f"     N (no asisten 6-16): {len(d.N)} niños en {len(d.N_i)} hogares")
    print(f"{ok(len(d.obligatorios) == 29)} E-7 obligatorios: {len(d.obligatorios)} (esperado 29)")
    sin_estrategia = [k for k in d.obligatorios if not d.S_k[k]]
    print(f"{ok(not sin_estrategia)} todo obligatorio tiene alguna estrategia elegible: {len(sin_estrategia)} sin ninguna")
    for s in ESTRATEGIAS:
        n = sum(1 for k in d.S_k if s in d.S_k[k])
        print(f"     elegibles a {s}: {n}")
    d_mayor_b = [(k, s) for (k, s), dd in d.d_ks.items()
                 if k in d.K and dd > d.ninos.at[k, "b"] + 1e-9]
    print(f"     pares (k, s) con d_ks > b_k (el coeficiente premia más de lo que hay): {len(d_mayor_b)}")
    q = {j: [sum(1 for (i, jj), v in d.quitable.items() if jj == j and v),
             sum(1 for (i, jj) in d.quitable if jj == j)] for j in P.INDICADORES}
    print("\n Privaciones que SÍ se pueden quitar este año (de las que existen):")
    for j, (a, b) in q.items():
        print(f"     {j:<26}{a:>5} de {b:<5}")
    print(f"{ok(q['logro_educativo'][0] == 32)} logro quitable: {q['logro_educativo'][0]} (D6: 32)")
    print(f"{ok(q['rezago_escolar'][0] == 0)} rezago quitable: {q['rezago_escolar'][0]} (esperado 0, formulación (10b))")
    n_imp = sum(1 for (i, j) in d.imputados if j == 'desempleo_larga_duracion')
    print(f"{ok(q['desempleo_larga_duracion'][0] == 226 - n_imp == 8)} desempleo quitable: {q['desempleo_larga_duracion'][0]} "
          f"(226 menos {n_imp} imputados; esperado 8, decisión H5 del 7-nov)")
    print(f"\n Adultos elegibles a CLEI: {len(d.c_v)} en {len(d.L_i)} hogares · analfabetas: "
          f"{sum(len(v) for v in d.analfabetas_i.values())}")
    print(f" Costos: c_ij suma {sum(d.c.values()) / 1e9:,.1f} mil millones · "
          f"Renta Ciudadana de todos los hogares {sum(d.C_RC.values()) / 1e9:,.1f} mil millones")
    print(f" Personas pobres por zona: {d.pobres_zona.round(0).to_dict()}")


if __name__ == "__main__":
    _verificar(cargar_datos())
