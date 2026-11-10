# -*- coding: utf-8 -*-
"""
m34_costos_comunes.py — Costos del ESCENARIO COMUN para M3/M4 (propuesta del 5-nov, bitacora §6.4).

Una sola tabla de costos para los cuatro modelos: `parametros.py` + reglas de `05_conteo_personas.py`
de Martin. Este script NO escribe ningun precio: importa los modulos de Martin.

Por par (hogar, indicador privado) se guarda u (personas que recibe el programa), el costo del hogar
en pesos (sin HW) y si el par es intervenible en un año. M3/M4 lo leen con
`m34_costos_reales.cargar_costos(..., fuente="comun")`: V = u*HW, K = costo_hogar*HW/1e6.

Reglas:
- 11 indicadores "simples" (pago por x en M1): u y costo_hogar de `conteo_pares.csv`, tal cual.
- Educacion (en M1 se paga por niño/adulto con z, t, v): las tablas `tabla_ninos` y `tabla_adultos`
  de Martin se aplican a TODOS los hogares (en M1 solo a los pobres, porque M1 solo interviene pobres;
  M3/M4 necesitan el costo de los no pobres para los errores de inclusion). El costo del par es el
  minimo que en M1 quita esa privacion:
    * logro: menor numero de ciclos CLEI (adultos elegibles, mayor g_a primero) con sum g_a >= D_i
      (ec. 11). Si ni con todos se llega: no intervenible en un año (M1 fija x = 0).
    * analfabetismo: un ciclo por cada analfabeta (ec. 12); si alguno no es elegible: no intervenible.
    * inasistencia: cada no asistente de 6-16 vuelve por E1 (cupo SGP, + Renta Ciudadana/p una vez
      por hogar, E-3) o E2 si es elegible (ciclo CLEI); se toma la combinacion mas barata (D2: deben
      volver TODOS). Sin no asistentes identificados: no intervenible (M1: Inas0).
    * rezago: no intervenible (decision del 2-nov, igual que hasta ahora).
- Desviaciones declaradas frente a M1: (a) cada par se costea por separado, asi que un adulto que sirve
  a logro y a analfabetismo se paga en los dos pares si se cubren ambos; (b) sin E-7 ni SevEdu
  (escenario comun).

Uso: python3 m34_costos_comunes.py <carpeta Modelos/ de Martin>
Salida: data/processed/costos_comunes_m34.csv
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RUTA_SALIDA = Path("data/processed/costos_comunes_m34.csv")


def construir(dir_modelos):
    sys.path.insert(0, str(Path(dir_modelos).resolve()))
    import importlib
    import parametros as P
    c05 = importlib.import_module("05_conteo_personas")
    per = c05.cargar_personas()
    hog = c05.cargar_hogares()
    emp = c05.empleo_por_hogar(per)
    pares = c05.conteo_pares(per, emp, hog)
    todos = hog.assign(POBRE=1)                    # las tablas de educacion para todos los hogares
    ninos = c05.tabla_ninos(per, todos)
    adultos, logro = c05.tabla_adultos(per, todos)
    zona = hog.set_index("ID_HOGAR").zona_costo
    ciclo = {i: P.COSTO_CICLO_CLEI[z] for i, z in zona.items()}
    rc = P.RENTA_CIUDADANA_ANUAL / P.escenario()["p"]

    filas = []
    simples = pares[pares.pago == "x"]
    # Regla de Martin (7-nov, datos_modelo.py): desempleo sin desocupado identificado (u imputado) NO es
    # quitable en el caso base. Se replica aqui para que M3/M4 no curen lo que M1/M2 no pueden (10-nov).
    imputar = P.escenario().get("desempleo_imputado", True)
    for r in simples.itertuples(index=False):
        if r.indicador == "desempleo_larga_duracion" and bool(r.u_imputado) and not imputar:
            filas.append((r.ID_HOGAR, r.indicador, r.u_ij, np.nan, False, "desempleo sin desocupado identificado (7-nov)"))
        else:
            filas.append((r.ID_HOGAR, r.indicador, r.u_ij, r.costo_hogar, True, "conteo_pares"))

    D = logro.set_index("ID_HOGAR").D_i
    el = adultos[adultos.elegible_clei].groupby("ID_HOGAR").g_a.apply(lambda s: np.sort(s.to_numpy())[::-1])
    # Regla del M1 (datos_modelo.py, 10-nov): el analfabeta tiene que ser elegible a CLEI Y ganar años con el
    # ciclo (g_a > 0). Antes solo se pedía elegible: 10 pares pobres quedaban quitables aquí y no en el M1.
    an = (adultos[adultos.analfabeta].assign(ok=lambda a: a.elegible_clei & (a.g_a > 0))
          .groupby("ID_HOGAR").ok.agg(["size", "all"]))
    noas = ninos[ninos.no_asiste_6_16].groupby("ID_HOGAR")
    for r in pares[pares.pago != "x"].itertuples(index=False):
        i, j = r.ID_HOGAR, r.indicador
        if j == "rezago_escolar":
            filas.append((i, j, r.u_ij, np.nan, False, "rezago no intervenible (2-nov)"))
        elif j == "logro_educativo":
            g = el.get(i, np.array([]))
            cum = np.cumsum(g)
            d = D.get(i, np.nan)
            if not d > 0:
                # Caso limite (1 hogar no pobre, 8380201_1): promedio exactamente 9 con los años de
                # Martin y el DANE lo marca privado. Se exige 1 año mas (un ciclo basta).
                if not d == 0:
                    raise ValueError(f"{i}: DANE marca logro pero D_i = {d}")
                d = 1.0
            if cum.size and cum[-1] >= d:
                k = int(np.searchsorted(cum, d) + 1)
                filas.append((i, j, k, k * ciclo[i], True, f"{k} ciclo(s) CLEI, ec. 11"))
            else:
                filas.append((i, j, 0, np.nan, False, "deficit > un ciclo por adulto"))
        elif j == "analfabetismo":
            if i in an.index and an.loc[i, "all"]:
                n = int(an.loc[i, "size"])
                filas.append((i, j, n, n * ciclo[i], True, "un ciclo por analfabeta, ec. 12"))
            else:
                filas.append((i, j, 0, np.nan, False, "analfabeta no elegible o no identificado"))
        elif j == "inasistencia_escolar":
            if i not in noas.groups:
                filas.append((i, j, 0, np.nan, False, "sin no asistentes identificados"))
                continue
            k = noas.get_group(i)
            e1 = k.precio_E1_cupo.to_numpy(float)
            e2 = np.where(k.elig_E2, k.precio_E2_E3_ciclo, np.inf)
            if np.isfinite(e2).all():              # todos pueden ir por CLEI: comparar con pagar RC
                costo = min(e2.sum(), np.minimum(e1, e2).sum() + rc)
            else:
                costo = np.minimum(e1, e2).sum() + rc
            filas.append((i, j, len(k), costo, True, "E1/E2 mas barato + RC/p si hay E1"))
    t = pd.DataFrame(filas, columns=["ID_HOGAR", "indicador", "u", "costo_hogar", "intervenible", "regla"])
    t = t.merge(hog[["ID_HOGAR", "FEX_C", "P3", "POBRE"]], on="ID_HOGAR")
    assert len(t) == len(pares), (len(t), len(pares))
    assert (t[t.intervenible].u > 0).all() and t[t.intervenible].costo_hogar.notna().all()
    return t


def main():
    t = construir(sys.argv[1])
    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(RUTA_SALIDA, index=False)
    t["costo_ij_mm"] = t.costo_hogar * t.FEX_C / 1e9
    r = t.groupby("indicador").agg(pares=("u", "size"), no_interv=("intervenible", lambda s: (~s).sum()),
                                   pobres=("POBRE", "sum"), u_medio=("u", "mean"),
                                   costo_mm=("costo_ij_mm", "sum"))
    print(r.round(2).to_string())
    print(f"\nTotal: {len(t)} pares, {int((~t.intervenible).sum())} no intervenibles, "
          f"${t.costo_ij_mm.sum():,.1f} mil millones; pobres ${t[t.POBRE == 1].costo_ij_mm.sum():,.1f}")
    print("->", RUTA_SALIDA)


if __name__ == "__main__":
    main()
