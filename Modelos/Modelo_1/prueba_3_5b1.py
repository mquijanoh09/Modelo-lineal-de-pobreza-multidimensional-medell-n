"""
prueba_3_5b1.py  --  Capa 1 del Modelo 1 (presupuesto + max H) contra una enumeración exacta.

Instancia de prueba: N hogares pobres al azar, donde SOLO se pueden quitar las privaciones
simples (las educativas se fijan en 0 y no hay cobertura obligatoria). Así el óptimo se
calcula por otro camino, sin MILP:
   1) por hogar: de todos los subconjuntos de privaciones, el más barato que lo deja <= 0.33;
   2) mochila 0/1 entre hogares (programación dinámica) con costos redondeados hacia
      arriba (cota inferior de H) y hacia abajo (cota superior de H).
El MILP debe quedar entre las dos cotas (y casi siempre igualarlas).
"""
import itertools
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # ...\Modelos

import parametros as P
from datos_modelo import cargar_datos, subconjunto, INDICADORES_SIMPLES
from Modelo_1.modelo1 import Modelo1

ESCALA = 1e5                  # pesos por casilla de la mochila


def instancia(d, n, semilla):
    rng = np.random.default_rng(semilla)
    ids = list(rng.choice(list(d.hogares.index), size=n, replace=False))
    s = subconjunto(d, ids)
    for (i, j) in list(s.quitable):
        if j not in INDICADORES_SIMPLES:
            s.quitable[(i, j)] = False          # lo educativo no se puede quitar en la prueba
    s.obligatorios = []                         # sin E-7: no hay gasto forzoso
    return s


def costo_minimo_de_salir(s, i):
    """(costo, ¿puede salir?) del subconjunto más barato de privaciones que deja al hogar <= 0.33."""
    libres = [j for j in s.J[i] if s.quitable[(i, j)]]
    c0 = s.hogares.at[i, "c0"]
    mejor = None
    for k in range(len(libres) + 1):
        for q in itertools.combinations(libres, k):
            if round(c0 - sum(P.PESOS[j] for j in q), 2) <= P.K_GRID + 1e-9:
                costo = sum(s.c[(i, j)] for j in q)
                if mejor is None or costo < mejor:
                    mejor = costo
    return mejor


def mochila(items, B, redondeo):
    """max sum p s.a. sum costo <= B, con costos en casillas de ESCALA pesos."""
    f = np.ceil if redondeo == "arriba" else np.floor
    cap = int(np.floor(B / ESCALA)) if redondeo == "arriba" else int(np.ceil(B / ESCALA))
    dp = np.zeros(cap + 1)
    for costo, p in items:
        w = int(f(costo / ESCALA))
        if w <= cap:
            dp[w:] = np.maximum(dp[w:], dp[:cap + 1 - w] + p) if w > 0 else dp + p
    return dp[cap]


def main():
    d = cargar_datos()
    ok_total = True
    print(f"{'semilla':>7}{'n':>4}{'B (mil mill.)':>15}{'MILP':>14}{'cota inf':>14}{'cota sup':>14}  resultado")
    for semilla in (1, 2, 3):
        s = instancia(d, 50, semilla)
        items = []
        for i in s.hogares.index:
            c = costo_minimo_de_salir(s, i)
            if c is not None:
                items.append((c, float(s.hogares.at[i, "p"])))
        total = sum(c for c, _ in items)
        for frac in (0.25, 0.5):
            B = frac * total
            m = Modelo1(s, B).construir()
            info = m.resolver(gap_rel=1e-9, time_limit=120)
            milp = info["objetivo"]
            lo, hi = mochila(items, B, "arriba"), mochila(items, B, "abajo")
            ok = info["estado"] == "Optimal" and lo - 1e-6 <= milp <= hi + 1e-6
            ok_total &= ok
            print(f"{semilla:>7}{len(s.hogares):>4}{B / 1e9:>15,.1f}{milp:>14,.1f}{lo:>14,.1f}{hi:>14,.1f}  {'OK' if ok else 'FALLA'}"
                  f"{'  (cotas iguales)' if abs(hi - lo) < 1e-6 else ''}")
    print("\nCAPA 1:", "OK en todas las instancias" if ok_total else "HAY FALLAS")


if __name__ == "__main__":
    main()
