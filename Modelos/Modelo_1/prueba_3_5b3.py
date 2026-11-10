"""
prueba_3_5b3.py  --  Capa 3 del Modelo 1 (severidad: q, tangentes y techo) contra enumeración.

Instancia: pocos hogares, solo privaciones simples quitables. Cada hogar elige un subconjunto de
privaciones; lo único que importa es (costo, puntaje final s). Para cada puntaje alcanzable
se guarda el costo mínimo. Se combinan los hogares con poda por presupuesto y por techo de
severidad, y se busca el mayor H. El MILP debe dar lo mismo, y también la misma
infactibilidad.
"""
import itertools
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # ...\Modelos

import parametros as P
from datos_modelo import cargar_datos, subconjunto, INDICADORES_SIMPLES
from Modelo_1.modelo1 import Modelo1

N_HOGARES = 9


def instancia(d, semilla):
    rng = np.random.default_rng(semilla)
    # hogares con pocas privaciones quitables, para que la enumeración sea corta
    cand = [i for i in d.hogares.index if 2 <= sum(1 for j in d.J[i] if j in INDICADORES_SIMPLES) <= 6]
    ids = list(rng.choice(cand, size=N_HOGARES, replace=False))
    s = subconjunto(d, ids)
    for (i, j) in list(s.quitable):
        if j not in INDICADORES_SIMPLES:
            s.quitable[(i, j)] = False
    s.obligatorios = []
    return s


def opciones(s, i):
    """{puntaje final: costo mínimo} para el hogar i."""
    libres = [j for j in s.J[i] if s.quitable[(i, j)]]
    c0 = s.hogares.at[i, "c0"]
    mejor = {}
    for k in range(len(libres) + 1):
        for q in itertools.combinations(libres, k):
            sc = round(c0 - sum(P.PESOS[j] for j in q), 2)
            c = sum(s.c[(i, j)] for j in q)
            if sc not in mejor or c < mejor[sc]:
                mejor[sc] = c
    return mejor


def salida_minima(s, i):
    """Costo mínimo de dejar al hogar i en <= 0.33 (0 si no puede salir)."""
    c = [c for sc, c in opciones(s, i).items() if sc <= P.K_GRID + 1e-9]
    return min(c) if c else 0.0


def enumeracion(s, B, rho):
    ids = list(s.hogares.index)
    techo = (1 - rho) * s.Sev0
    ops = []
    for i in ids:
        p = s.hogares.at[i, "p"]
        o = opciones(s, i)
        ops.append(np.array([(c, p * sc * sc, p if sc <= P.K_GRID + 1e-9 else 0.0) for sc, c in o.items()]))
    # mínimos que aún pueden sumar los hogares que faltan (para podar)
    min_c = [o[:, 0].min() for o in ops]
    min_s = [o[:, 1].min() for o in ops]
    resto_c = np.cumsum(min_c[::-1])[::-1].tolist() + [0]
    resto_s = np.cumsum(min_s[::-1])[::-1].tolist() + [0]
    est = np.zeros((1, 3))
    for n, o in enumerate(ops):
        nuevo = (est[:, None, :] + o[None, :, :]).reshape(-1, 3)
        ok = (nuevo[:, 0] + resto_c[n + 1] <= B + 1e-6) & (nuevo[:, 1] + resto_s[n + 1] <= techo + 1e-6)
        est = nuevo[ok]
        if len(est) == 0:
            return None
    return est[:, 2].max()


def main():
    d = cargar_datos()
    todo_ok = True
    print(f"{'semilla':>7}{'rho':>6}{'B (mil mill.)':>15}{'MILP':>14}{'enumeración':>14}  resultado")
    for semilla in (1, 2, 3):
        s = instancia(d, semilla)
        total = sum(salida_minima(s, i) for i in s.hogares.index)    # costo de sacar a todos los que pueden salir
        for rho, frac in ((0.0, 0.4), (0.2, 0.4), (0.3, 0.6), (0.35, 0.6), (0.4, 1.0), (0.45, 1.0), (0.5, 1.0), (0.6, 1.0)):
            B = frac * total
            m = Modelo1(s, B, rho=rho).construir()
            info = m.resolver(gap_rel=1e-9, time_limit=60)
            milp = info["objetivo"] if info["estado"] == "Optimal" else None
            ex = enumeracion(s, B, rho)
            ok = (milp is None and ex is None) or (milp is not None and ex is not None and abs(milp - ex) < 1e-4 * max(ex, 1))
            todo_ok &= ok
            f = lambda v: "infactible" if v is None else f"{v:,.1f}"
            print(f"{semilla:>7}{rho:>6}{B / 1e9:>15,.1f}{f(milp):>14}{f(ex):>14}  {'OK' if ok else 'FALLA'}  [{info['estado']}]")
    # q_i debe valer exactamente s_i^2 donde importa: se revisa en una solución
    s = instancia(d, 1)
    m = Modelo1(s, 0.4 * sum(salida_minima(s, i) for i in s.hogares.index), rho=0.2).construir()
    m.resolver(gap_rel=1e-9, time_limit=60)
    mal = [(i, m.q[i].value(), m.s[i].value() ** 2) for i in s.hogares.index if m.q[i].value() + 1e-6 < m.s[i].value() ** 2]
    print(f"\nq_i >= s_i^2 en todos los hogares de la solución: {'OK' if not mal else 'FALLA ' + str(mal)}")
    todo_ok &= not mal
    print("CAPA 3:", "OK en todas las instancias" if todo_ok else "HAY FALLAS")


if __name__ == "__main__":
    main()
