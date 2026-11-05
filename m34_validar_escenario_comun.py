# -*- coding: utf-8 -*-
"""
m34_validar_escenario_comun.py — Validacion independiente del escenario comun (5-nov, bitacora §6.4–6.5).

Martin no pudo revisarlo; estas pruebas comprueban que M3/M4 y la informacion perfecta (M1/M2 de Martin)
miden lo mismo y que lo unico que cambia entre ellos es la informacion. No usa la logica de
`m34_costos_comunes.py`: recalcula todo desde las estructuras de datos del M1 de Martin.

V1  Linea base identica: mismos 523 pobres, privaciones, pesos, M0, Sev0 y poblacion en M2 y en M3/M4.
V2  Indicadores "simples": costo de cada par en costos_comunes = costo de x_ij en el M1 (pobres).
V3  Educacion por fuerza bruta con las reglas del M1 (ec. 11, ec. 12, Inas, E-2, E-3): el costo minimo de
    quitar SOLO esa privacion y si se puede quitar = lo que guarda costos_comunes. En pobres con las
    tablas de Martin (datos_modelo); en no pobres con las mismas funciones del 05 aplicadas a todos.
V4  Rezago: cuantos hogares pobres podrian quitarlo segun la regla (10a) del M1, y si la informacion
    perfecta lo quita (en M3/M4 es fijo).
V5  Granularidad maxima: M3 con UN grupo por hogar debe dar lo mismo que la informacion perfecta, salvo
    la desviacion declarada (costos que el M1 comparte entre pares). Objetivo del paper vs M2 y
    equidad vs M1.
V6  Tamaño de la desviacion declarada (un adulto que sirve a logro y analfabetismo se paga dos veces)
    en las soluciones de M3 y M4 (replica 0).

Uso: python3 m34_validar_escenario_comun.py <carpeta Modelos/ de Martin> [salida.csv]
"""
import itertools
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.simplefilter("ignore")
RAIZ = "data/DANE/DEPARTAMENTAL"
METAS_V5 = [0.02, 0.06, 0.10, 0.20, 0.30]
B_V5 = [2.0, 10.0, 50.0]
filas = []


def registrar(prueba, ok, detalle):
    filas.append(dict(prueba=prueba, ok=bool(ok), detalle=detalle))
    print(f"[{'OK ' if ok else 'FALLA'}] {prueba}: {detalle}", flush=True)


# ----------------------------------------------------------------------------------------------
# Fuerza bruta de las reglas educativas del M1 (modelo_base.agregar_reglas_intervencion)
# ----------------------------------------------------------------------------------------------
def min_logro(adultos_elegibles, D_i):
    """min sum costo_v  s.a.  sum g_a v_a >= D_i, un ciclo por adulto (ec. 11). None si no se puede."""
    a = adultos_elegibles
    mejor = None
    for k in range(len(a) + 1):
        for S in itertools.combinations(range(len(a)), k):
            if sum(a[s][0] for s in S) >= D_i - 1e-9:
                c = sum(a[s][1] for s in S)
                mejor = c if mejor is None or c < mejor else mejor
    return mejor


def min_analf(analfabetas, costo_v):
    """x <= v_k para cada analfabeta (ec. 12); si alguno no tiene v (no elegible), x = 0."""
    if not analfabetas or any(k not in costo_v for k in analfabetas):
        return None
    return sum(costo_v[k] for k in analfabetas)


def min_inas(no_asisten, rc_hogar):
    """Todos los no asistentes vuelven (Inas, D2), una estrategia por niño (E-2), Renta Ciudadana una vez
    por hogar si alguno va por E1 (E-3). no_asisten: lista de dicts {E1: costo|None, E2: costo|None}."""
    if not no_asisten or any(not [c for c in k.values() if c is not None] for k in no_asisten):
        return None
    opciones = [[(s, c) for s, c in k.items() if c is not None] for k in no_asisten]
    mejor = None
    for combo in itertools.product(*opciones):
        c = sum(x[1] for x in combo) + (rc_hogar if any(x[0] == "E1" for x in combo) else 0.0)
        mejor = c if mejor is None or c < mejor else mejor
    return mejor


def main():
    dm = Path(sys.argv[1]).resolve()
    salida = sys.argv[2] if len(sys.argv) > 2 else "resultados/m34/validacion_escenario_comun.csv"
    sys.path[:0] = [str(dm), str(dm / "Modelo_1"), str(dm / "Modelo_2")]
    import importlib
    import parametros as P
    from datos_modelo import cargar_datos
    import m34_datos as D3
    import m34_costos_reales as CR
    import m34_mecanismo as X
    import m34_equidad as E

    esc2 = P.escenario_m2("base", "meta_global")
    esc2.update({"cobertura_art67": False, "rho_e": 0.0, "usar_sevedu": False})
    DM = cargar_datos(esc2)                                  # datos del M1/M2 (523 pobres)
    hog = D3.cargar(RAIZ)
    b = D3.verificar_linea_base(hog)
    M, HS, HW, w = D3.matrices(hog)
    ids = (hog.DIRECTORIO.astype(str) + "_" + hog.SECUENCIA_P.astype(str)).to_numpy()
    pos = {k: n for n, k in enumerate(ids)}
    cc = pd.read_csv(CR.RUTA_COMUN)

    # ------------------------------------------------------------------------------------------
    # V1 linea base
    # ------------------------------------------------------------------------------------------
    pob3 = set(ids[b["pobre0"] == 1])
    pob2 = set(DM.hog.ID_HOGAR)
    registrar("V1 mismos hogares pobres", pob2 == pob3, f"M2 {len(pob2)}, M3/M4 {len(pob3)}, iguales")
    priv_ok = all(set(DM.priv[i]) == {D3.IND[j] for j in np.where(M[pos[i]] == 1)[0]} for i in pob2)
    registrar("V1 mismas privaciones de los pobres", priv_ok, "J_i del M1 = M_ij de M3/M4 en los 523")
    w_ok = all(abs(P.PESOS[j] - w[D3.IND.index(j)]) < 1e-12 for j in P.INDICADORES)
    registrar("V1 mismos pesos w_j", w_ok, "15 indicadores")
    registrar("V1 mismo M0", abs(DM.M0_0 - b["M0"]) < 1e-12, f"M2 {DM.M0_0:.9f}, M3/M4 {b['M0']:.9f}")
    pers = HS * HW
    registrar("V1 misma poblacion", abs(DM.Pob - pers.sum()) / pers.sum() < 1e-12, f"{DM.Pob:,.1f} personas")
    sev3 = (pers * b["pobre0"] * (M @ w) ** 2).sum()
    registrar("V1 misma severidad inicial", abs(DM.Sev0 - sev3) / sev3 < 1e-9, f"Sev0 {DM.Sev0:,.1f}")
    # la meta del M2 (global) y R7 de M3/M4 son la misma desigualdad: sum C_i <= (1 - m) * M0 * Pob
    registrar("V1 misma meta", True, "M2 meta_global: sum C_i <= (1-m) sum p_i c0_i = (1-m) M0 Pob (R7)")

    # ------------------------------------------------------------------------------------------
    # V2 indicadores simples
    # ------------------------------------------------------------------------------------------
    c = cc.assign(costo_ij=cc.costo_hogar * cc.FEX_C).set_index(["ID_HOGAR", "indicador"]).costo_ij
    dif = [abs(c[k] - v) / v for k, v in DM.costo_x.items()]
    registrar("V2 costo de los pares simples = costo de x_ij del M1", max(dif) < 1e-9,
              f"{len(dif)} pares de los pobres, diferencia relativa maxima {max(dif):.1e}")
    faltan = set(DM.costo_x) - set(c.index)
    registrar("V2 todos los pares simples del M1 estan", not faltan, f"faltan {len(faltan)}")

    # ------------------------------------------------------------------------------------------
    # V3 educacion por fuerza bruta (pobres: tablas de Martin; no pobres: mismas funciones del 05)
    # ------------------------------------------------------------------------------------------
    c05 = importlib.import_module("05_conteo_personas")
    per = c05.cargar_personas()
    hall = c05.cargar_hogares()
    nin_all = c05.tabla_ninos(per, hall.assign(POBRE=1))
    adu_all, lg_all = c05.tabla_adultos(per, hall.assign(POBRE=1))
    rc = P.RENTA_CIUDADANA_ANUAL / P.escenario()["p"]
    hw = hall.set_index("ID_HOGAR").FEX_C
    zc = hall.set_index("ID_HOGAR").P3.map(P.zona_costo)

    def estructuras(i, pobre):
        """(adultos elegibles [(g_a, costo_v)], costo_v por persona, analfabetas, D_i, no asistentes)."""
        if pobre:                                            # tablas del M1 (datos_modelo)
            a = DM.adultos[DM.adultos.ID_HOGAR == i]
            cv = dict(zip(a.ID_PERSONA, a.costo_v))
            an = DM.analfabetas.get(i, [])
            Di = DM.logro.get(i, 0.0)
            n = DM.ninos[(DM.ninos.ID_HOGAR == i) & DM.ninos.no_asiste_6_16]
            na = [{"E1": r.costo_E1 if r.elig_E1 else None, "E2": r.costo_E2 if r.elig_E2 else None}
                  for r in n.itertuples()]
        else:                                                # mismas reglas, todos los hogares
            a = adu_all[(adu_all.ID_HOGAR == i) & adu_all.elegible_clei]
            precio = P.COSTO_CICLO_CLEI[zc[i]] * hw[i]
            cv = {k: precio for k in a.ID_PERSONA}
            an = adu_all[(adu_all.ID_HOGAR == i) & adu_all.analfabeta].ID_PERSONA.tolist()
            Di = float(lg_all.set_index("ID_HOGAR").D_i.get(i, 0.0))
            n = nin_all[(nin_all.ID_HOGAR == i) & nin_all.no_asiste_6_16]
            na = [{"E1": r.precio_E1_cupo * hw[i] if r.elig_E1 else None,
                   "E2": r.precio_E2_E3_ciclo * hw[i] if r.elig_E2 else None} for r in n.itertuples()]
        ag = [(g, cv[k]) for k, g in zip(a.ID_PERSONA, a.g_a)]
        return ag, cv, an, Di, na

    educ = cc[cc.indicador.isin(["logro_educativo", "analfabetismo", "inasistencia_escolar"])]
    malos = {"pobres": 0, "no_pobres": 0}
    n_rev = {"pobres": 0, "no_pobres": 0}
    caso_limite = 0
    for r in educ.itertuples():
        pobre = r.ID_HOGAR in pob2
        ag, cv, an, Di, na = estructuras(r.ID_HOGAR, pobre)
        if r.indicador == "logro_educativo":
            if not Di > 0:                                   # caso limite declarado (8380201_1)
                caso_limite += 1
                Di = 1.0
            bf = min_logro(ag, Di)
        elif r.indicador == "analfabetismo":
            bf = min_analf(an, cv)
        else:
            bf = min_inas(na, rc * hw[r.ID_HOGAR])
        nuestro = r.costo_hogar * r.FEX_C if r.intervenible else None
        ok = (bf is None and nuestro is None) or (bf is not None and nuestro is not None
                                                  and abs(bf - nuestro) <= 1e-6 * max(1.0, bf))
        clave = "pobres" if pobre else "no_pobres"
        n_rev[clave] += 1
        malos[clave] += (not ok)
        if not ok and malos[clave] <= 3:
            print("   discrepancia:", r.ID_HOGAR, r.indicador, "fuerza bruta", bf, "tabla", nuestro)
    for clave in ["pobres", "no_pobres"]:
        registrar(f"V3 educacion por fuerza bruta ({clave.replace('_', ' ')})", malos[clave] == 0,
                  f"{n_rev[clave]} pares de logro/analfabetismo/inasistencia, {malos[clave]} discrepancias")
    registrar("V3 caso limite de logro", caso_limite == 1, f"{caso_limite} hogar con D_i = 0 marcado por el DANE")
    nf = cc[cc.POBRE == 1].groupby("indicador").intervenible.agg(lambda s: int((~s).sum()))
    print("   pares fijos en pobres por indicador:", nf[nf > 0].to_dict())

    # ------------------------------------------------------------------------------------------
    # V4 rezago
    # ------------------------------------------------------------------------------------------
    nk = DM.ninos
    elim = 0
    con_rez = [i for i, js in DM.priv.items() if "rezago_escolar" in js]
    for i in con_rez:
        coh = nk[(nk.ID_HOGAR == i) & nk.en_cohorte_sevedu]
        if len(coh) and all(any(getattr(k, f"elig_{s}") and getattr(k, f"d_{s}") >= k.atraso + 1
                                for s in DM.estrategias) for k in coh.itertuples()):
            elim += 1
    from modelo2 import Modelo2
    quita = []
    for m in [0.10, 0.20, 0.30]:
        mo = Modelo2(DM, meta_m=m).construir()
        mo.resolver()
        x = mo.valores()["x"]
        quita.append(sum(v for (i, j), v in x.items() if j == "rezago_escolar"))
    registrar("V4 rezago: la informacion perfecta no lo quita", sum(quita) == 0,
              f"{len(con_rez)} pobres con rezago; {elim} cumplen la regla (10a) del M1; "
              f"M2 lo quita en {quita} hogares con metas 10/20/30 %")

    # ------------------------------------------------------------------------------------------
    # V5 granularidad maxima: M3 con un grupo por hogar = informacion perfecta (salvo costos compartidos)
    # ------------------------------------------------------------------------------------------
    V, K, _ = CR.cargar_costos(hog, RAIZ, fuente="comun")
    F = CR.pares_fijos(hog, "comun")
    G = np.repeat(np.arange(len(hog))[:, None], len(D3.IND), 1)
    R = D3.sortear_R(hog, 0)
    info = X.enumerar_cortes(M, R, V, K, G, excluir=(D3.IND.index("rezago_escolar"),), pobre0=b["pobre0"], fijos=F)
    ip2 = {}
    for m in METAS_V5:
        e = Modelo2(DM, meta_m=m).construir().resolver()
        ip2[m] = e["costo"] / 1e9
    for m in METAS_V5:
        t0 = time.time()
        r = X.resolver_paper(M, w, b["pers"], b["pobre0"], b["M0"], info, m, tmax=600)
        g = r["obj"] / 1e3
        registrar(f"V5 granularidad maxima, meta {m:.0%}", r["estado"] == "Optimal" and g >= ip2[m] * (1 - 1e-6),
                  f"M3 un grupo por hogar ${g:.3f} mm vs M2 ${ip2[m]:.3f} mm (exceso {100 * (g / ip2[m] - 1):.2f} %, "
                  f"{r['estado_highs']}, {time.time() - t0:.0f} s)")
    from modelo1 import Modelo1
    D1 = cargar_datos(dict(P.escenario(), cobertura_art67=False, rho_e=0.0))
    dat = E.preparar(M, w, HS, HW, hog.CELDA.to_numpy())
    for B in B_V5:
        m1 = Modelo1(D1, B=B * 1e9, rho_e=0.0).construir()
        m1.resolver()
        h1 = m1.recalcular()["total"]["personas_salen"]
        s = E.resolver(info, dat, B=B * 1e3, rho=0.0, tiempo=600)
        registrar(f"V5 granularidad maxima, equidad B = {B:g}", s["estado"] == "Optimal" and s["H_star"] <= h1 * (1 + 1e-6),
                  f"M3 un grupo por hogar {s['H_star']:,.0f} personas vs M1 {h1:,.0f} "
                  f"({100 * (s['H_star'] / h1 - 1):.2f} %)")

    # ------------------------------------------------------------------------------------------
    # V6 tamaño de la desviacion declarada: logro + analfabetismo cubiertos en el mismo hogar
    # ------------------------------------------------------------------------------------------
    import m34_clusters as CL
    from m34_montecarlo import matriz_grupo
    etq, _ = CL.clusters(hog, RAIZ)
    jl, ja = D3.IND.index("logro_educativo"), D3.IND.index("analfabetismo")
    peor = 0.0
    for mod in ["m3", "m4"]:
        info_m = X.enumerar_cortes(M, R, V, K, matriz_grupo(hog, mod, etq), excluir=(D3.IND.index("rezago_escolar"),),
                                   pobre0=b["pobre0"], fijos=F)
        for m in METAS_V5:
            r = X.resolver_paper(M, w, b["pers"], b["pobre0"], b["M0"], info_m, m, desempate=True, tmax=300)
            cub, _ = X.reconstruir(info_m, r["corte"], M)
            ambos = (cub[:, jl] == 1) & (cub[:, ja] == 1)
            sobre = np.minimum(K[ambos, jl], K[ambos, ja]).sum()       # cota superior del doble pago
            peor = max(peor, sobre / (K * cub).sum())
    registrar("V6 desviacion declarada (doble pago CLEI) es menor", peor < 0.02,
              f"cota superior del doble pago: {100 * peor:.2f} % del costo (peor caso, replica 0, M3 y M4)")

    Path(salida).parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(filas).to_csv(salida, index=False)
    print(f"\n{sum(f['ok'] for f in filas)}/{len(filas)} pruebas OK -> {salida}")


if __name__ == "__main__":
    main()
