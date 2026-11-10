"""
prueba_3_2.py  --  Prueba de la subfase 3.2 (censura + meta global).

El MILP (modelo2.construir_nucleo) se compara contra un algoritmo EXACTO distinto:
  1. Por hogar se enumeran los 2^n subconjuntos de privaciones que se pueden quitar.
  2. Se conserva solo lo no dominado (menos costo y menos contribución a M0).
  3. Se combinan los hogares uno a uno, conservando la frontera (costo, contribución).
  4. La respuesta es el menor costo cuya contribución total cumple la meta.
Los costos son SINTÉTICOS (u = 1, solo para probar la lógica), no son los del modelo.
"""
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # ...\Modelos

import numpy as np
import pandas as pd

import parametros as P
from nucleo_pruebas import construir_nucleo, resolver
from utils_dane import OUT

N_HOGARES = 50
METAS = [0.10, 0.30, 0.50]


def cargar_pobres(n, semilla=P.SEMILLA):
    d = pd.read_csv(OUT / "hogares_antioquia.csv")
    d = d[d.POBRE == 1].copy()
    d["p"] = d.FEX_C * d.PERSONAS
    d["c0"] = sum(P.PESOS[j] * d[j] for j in P.INDICADORES)
    assert np.allclose(d.c0, d.IPM), "el puntaje recalculado no coincide con IPM"
    d["zona"] = d.P3
    d = d.sample(n=n, random_state=semilla).sort_values("ID_HOGAR")
    priv = {r.ID_HOGAR: [j for j in P.INDICADORES if getattr(r, j) == 1]
            for r in d.itertuples()}
    return d.reset_index(drop=True), priv


def costos_sinteticos(hog, priv):
    """EpF por hogar (u = 1) con placeholders donde aún no hay u_ij; solo para esta prueba."""
    epf = P.tabla_epf(P.escenario())
    otros = {"empleo_formal": P.COSTO_APORTE_PENSION,
             "desempleo_larga_duracion": P.COSTO_EPV["joven_18_28"],
             "logro_educativo": P.COSTO_CICLO_CLEI["urbano"],
             "analfabetismo": P.COSTO_CICLO_CLEI["urbano"],
             "inasistencia_escolar": P.RENTA_CIUDADANA_ANUAL,
             "rezago_escolar": P.CUPO_SGP["urbano"]["primaria"]}
    costo = {}
    for r in hog.itertuples():
        zc = P.zona_costo(r.zona)
        for j in priv[r.ID_HOGAR]:
            c = epf[j][zc] if j in epf else otros[j]
            costo[(r.ID_HOGAR, j)] = c * r.FEX_C
    return costo


def opciones_hogar(r, js, costo):
    """(costo, contribución C) de cada subconjunto de privaciones que se quita."""
    ops = []
    for k in range(len(js) + 1):
        for q in itertools.combinations(js, k):
            s = sum(P.PESOS[j] for j in js if j not in q)
            ops.append((sum(costo[(r.ID_HOGAR, j)] for j in q),
                        r.p * s if s > P.K_GRID + 1e-9 else 0.0))
    return ops


def pareto(pares):
    pares = sorted(set(pares))
    out, mejor_c = [], float("inf")
    for cost, c in pares:
        if c < mejor_c - 1e-9:
            out.append((cost, c)); mejor_c = c
    return out


def minimo_exacto(hog, priv, costo, meta):
    techo = (1 - meta) * float((hog.p * hog.c0).sum())
    frontera = [(0.0, 0.0)]
    for r in hog.itertuples():
        ops = pareto(opciones_hogar(r, priv[r.ID_HOGAR], costo))
        frontera = pareto([(a + b, c + d) for a, c in frontera for b, d in ops
                           if c + d <= techo + 1e-9])
    return min((c for c, v in frontera if v <= techo + 1e-9), default=None), len(frontera)


def recalcular(hog, priv, x_val):
    """M0 (numerador) recalculado desde x, con la regla de censura, sin usar las C del MILP."""
    tot, sale = 0.0, {}
    for r in hog.itertuples():
        s = sum(P.PESOS[j] for j in priv[r.ID_HOGAR] if not x_val[(r.ID_HOGAR, j)])
        sale[r.ID_HOGAR] = s <= P.K_GRID + 1e-9
        tot += 0.0 if sale[r.ID_HOGAR] else r.p * s
    return tot, sale


def main():
    hog, priv = cargar_pobres(N_HOGARES)
    costo = costos_sinteticos(hog, priv)
    num0 = float((hog.p * hog.c0).sum())
    print(f"{len(hog)} hogares pobres; privaciones por hogar: {np.mean([len(v) for v in priv.values()]):.2f}; "
          f"{sum(len(v) for v in priv.values())} variables x")
    ok = True
    for m in METAS:
        prob, x, y, C = construir_nucleo(hog, priv, costo, m)
        res = resolver(prob)
        milp = res["objetivo_millones"] * P.ESCALA_COSTO
        exacto, tam = minimo_exacto(hog, priv, costo, m)
        xv = {k: round(v.value()) for k, v in x.items()}
        num, sale = recalcular(hog, priv, xv)
        y_ok = all(round(y[i].value()) <= sale[i] for i in sale)      # y = 1 solo si sale de verdad
        c_ok = sum(v.value() for v in C.values()) >= num - 1e-4         # las C del MILP cubren la regla
        meta_ok = num <= (1 - m) * num0 + 1e-4
        igual = exacto is not None and abs(milp - exacto) <= 1e-6 * max(1, exacto)
        ok &= igual and y_ok and c_ok and meta_ok
        print(f"m={m:.0%}: MILP {milp:,.0f} | exacto {exacto:,.0f} (frontera {tam}) | "
              f"M0 reducido {1 - num / num0:.1%} | iguales={igual} y_ok={y_ok} C_ok={c_ok} meta_ok={meta_ok}")
    print("\nTODO OK" if ok else "\nFALLÓ ALGO")
    return ok


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
