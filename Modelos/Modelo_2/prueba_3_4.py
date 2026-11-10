"""
prueba_3_4.py  --  Prueba de la subfase 3.4 (Modelo2 completo, heredando de ModeloIPMBase).

1. Piso de costo (m = 0): con meta 0 el modelo solo paga lo que obliga E-7. Se compara con
   una cuenta independiente: por hogar, la combinación más barata de estrategias de sus
   niños obligatorios (E1 exige pagar Renta Ciudadana una vez).
2. Metas 5 %, 10 % y 20 % (caso base, meta en cada zona): H, M0 y costo recalculados con la
   cuenta independiente de la base; cada zona cumple su meta; el costo coincide con el MILP;
   el costo sube con la meta; exigir la meta en cada zona cuesta >= exigirla solo global.
3. meta_maxima: el tope es 100 % (todos los hogares pueden salir); m = 100 % saca a los 523 hogares.
4. Las privaciones no quitables (rezago, logro de 471 hogares...) siguen en 0.
"""
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # ...\Modelos

import pandas as pd
import pulp

import parametros as P
from datos_modelo import cargar_datos
from modelo2 import Modelo2


def ok(c):
    return "OK   " if c else "FALLA"


def piso_exacto(d):
    """Costo mínimo de cumplir E-7, calculado sin el MILP."""
    por_hogar = {}
    for k in d.obligatorios:
        por_hogar.setdefault(d.ninos.at[k, "hogar"], []).append(k)
    total = 0.0
    for i, ks in por_hogar.items():
        mejor = float("inf")
        for combo in itertools.product(*[d.S_k[k] for k in ks]):
            c = sum(d.c_ks[(k, s)] for k, s in zip(ks, combo))
            if "E1" in combo:
                c += d.C_RC[i]
            mejor = min(mejor, c)
        total += mejor
    return total


def resolver(d, esc, m):
    mod = Modelo2(d, esc, meta_m=m).construir()
    info = mod.resolver()
    return mod, info


def main():
    d = cargar_datos()
    esc = P.escenario_m2()
    esc_g = P.escenario_m2("base", "meta_global")
    todo = True
    print(f"{len(d.hogares)} hogares pobres; meta por zona = {esc['meta_por_zona']}, SevEdu = {esc['usar_sevedu']}\n")

    print("1) Piso de costo con meta 0 %")
    mod, info = resolver(d, esc, 0.0)
    piso = piso_exacto(d)
    costo = pulp.value(mod.costo_total())
    c1 = abs(costo - piso) <= 1e-6 * piso
    todo &= c1 and info["estado"] == "Optimal"
    print(f"  {ok(c1)} MILP {costo:,.0f} | cuenta independiente {piso:,.0f} | {info['estado']} gap {info['gap']}")

    print("\n2) Metas 5 %, 10 % y 20 %")
    prev = -1.0
    for m in (0.05, 0.10, 0.20):
        mod, info = resolver(d, esc, m)
        todo &= info["estado"] == "Optimal"
        rec = mod.recalcular()
        costo = pulp.value(mod.costo_total())
        zonas = [P.ZONAS[z] for z in sorted(P.ZONAS)]
        cumple = all(rec.at[z, "reduccion_M0"] >= m - 1e-6 for z in zonas)
        cost_ok = abs(rec.at["total", "costo"] - costo) <= 1
        mod_g, info_g = resolver(d, esc_g, m)
        costo_g = pulp.value(mod_g.costo_total())
        monot = costo >= prev - 1
        prev = costo
        todo &= cumple and cost_ok and monot and costo >= costo_g - 1
        red = " | ".join(f"{z[:4]} {rec.at[z, 'reduccion_M0']:.1%}" for z in zonas)
        print(f"  m={m:.0%}: {info['estado']} costo ${costo / 1e9:,.1f} mil millones (solo global ${costo_g / 1e9:,.1f}) "
              f"gap {info['gap']:.1e} {info['segundos']}s")
        print(f"        reducción de M0 por zona: {red} | total {rec.at['total', 'reduccion_M0']:.1%} | "
              f"salen {rec.at['total', 'salen_hogares']:.0f} hogares")
        print(f"        {ok(cumple)} cada zona cumple  {ok(cost_ok)} costo recalculado = MILP  "
              f"{ok(monot)} costo no baja con m  {ok(costo >= costo_g - 1)} por zona >= solo global")

    print("\n3) meta_maxima con todas las reglas")
    mm = Modelo2.meta_maxima(d, esc)
    for z in sorted(P.ZONAS):
        print(f"  {P.ZONAS[z]:<15} {mm[z]:.4%}")
    tope = min(mm[z] for z in P.ZONAS)
    print(f"  total {mm['total']:.4%}")
    # Con M0 censurado, un hogar deja de aportar en cuanto sale de la pobreza, y todos pueden
    # salir quitando privaciones intervenibles. Por eso el tope es 100 %: la meta no limita y
    # lo que acota el barrido es el costo. Se comprueba que m = 100 % saca a los 523 hogares.
    todo &= abs(tope - 1) < 1e-6
    mod, info = resolver(d, esc, 1.0)
    rec = mod.recalcular()
    salen = rec.at["total", "salen_hogares"] == len(d.hogares)
    todo &= info["estado"] == "Optimal" and salen
    print(f"  {ok(abs(tope - 1) < 1e-6)} tope = 100 %: la meta no limita (todos los hogares pueden salir)")
    print(f"  {ok(info['estado'] == 'Optimal' and salen)} m = 100 %: {info['estado']}, salen {rec.at['total', 'salen_hogares']:.0f} de {len(d.hogares)} hogares, "
          f"costo ${pulp.value(mod.costo_total()) / 1e9:,.1f} mil millones")

    print("\n4) No quitables")
    mod, _ = resolver(d, esc, 0.10)
    malas = [(i, j) for (i, j), v in mod.x.items() if not d.quitable[(i, j)] and round(v.value() or 0) != 0]
    todo &= not malas
    print(f"  {ok(not malas)} {sum(1 for v in d.quitable.values() if not v)} privaciones no quitables, {len(malas)} quitadas por error")

    print("\nTODO OK" if todo else "\nFALLÓ ALGO")
    return todo


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
