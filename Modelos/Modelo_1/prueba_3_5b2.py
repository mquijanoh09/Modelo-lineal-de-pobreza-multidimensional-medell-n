"""
prueba_3_5b2.py  --  Capa 2 del Modelo 1 (equidad por zona) contra enumeración total.

Con 18 hogares (6 por zona) se enumeran los 2^18 conjuntos de hogares que salen. Cada hogar
que sale paga su costo mínimo de salida (solo privaciones simples, ver prueba_3_5b1). Se
calcula el mejor H que cumple presupuesto y equidad por zona, y se compara con el MILP.
También se prueba que una r imposible dé infactible en los dos.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # ...\Modelos

from datos_modelo import cargar_datos, subconjunto, INDICADORES_SIMPLES
from Modelo_1.modelo1 import Modelo1
from Modelo_1.prueba_3_5b1 import costo_minimo_de_salir

N_POR_ZONA = 6


def instancia(d, semilla):
    rng = np.random.default_rng(semilla)
    ids = []
    for zona, g in d.hogares.groupby("P3"):
        ids += list(rng.choice(list(g.index), size=N_POR_ZONA, replace=False))
    s = subconjunto(d, ids)
    for (i, j) in list(s.quitable):
        if j not in INDICADORES_SIMPLES:
            s.quitable[(i, j)] = False
    s.obligatorios = []
    return s


def enumeracion(s, B, r):
    ids = list(s.hogares.index)
    n = len(ids)
    costo = np.array([costo_minimo_de_salir(s, i) if costo_minimo_de_salir(s, i) is not None else np.inf for i in ids])
    p = s.hogares.p.to_numpy()
    zonas = s.hogares.P3.to_numpy()
    mask = ((np.arange(2 ** n)[:, None] >> np.arange(n)) & 1).astype(bool)      # (2^n, n)
    c = np.where(mask, costo, 0).sum(1)
    H = (mask * p).sum(1)
    ok = c <= B + 1e-6
    for z in np.unique(zonas):
        ok &= (mask[:, zonas == z] * p[zonas == z]).sum(1) >= r * s.pobres_zona[z] - 1e-9
    return H[ok].max() if ok.any() else None


def main():
    d = cargar_datos()
    todo_ok = True
    print(f"{'semilla':>7}{'r':>6}{'B (mil mill.)':>15}{'MILP':>14}{'enumeración':>14}  resultado")
    for semilla in (1, 2, 3):
        s = instancia(d, semilla)
        costos = [costo_minimo_de_salir(s, i) for i in s.hogares.index]
        total = sum(c for c in costos if c is not None)
        for r, frac in ((0.0, 0.4), (0.3, 0.4), (0.6, 0.6), (0.95, 0.3)):
            B = frac * total
            m = Modelo1(s, B, r=r).construir()
            info = m.resolver(gap_rel=1e-9, time_limit=60)
            milp = info["objetivo"] if info["estado"] == "Optimal" else None
            ex = enumeracion(s, B, r)
            ok = (milp is None and ex is None) or (milp is not None and ex is not None and abs(milp - ex) < 1e-4 * max(ex, 1))
            todo_ok &= ok
            f = lambda v: "infactible" if v is None else f"{v:,.1f}"
            print(f"{semilla:>7}{r:>6}{B / 1e9:>15,.1f}{f(milp):>14}{f(ex):>14}  {'OK' if ok else 'FALLA'}  [{info['estado']}]")
    print("\nCAPA 2:", "OK en todas las instancias" if todo_ok else "HAY FALLAS")


if __name__ == "__main__":
    main()
