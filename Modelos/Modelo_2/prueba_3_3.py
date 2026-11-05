"""
prueba_3_3.py  --  Prueba de la subfase 3.3 (meta por zona y meta_maxima).

1. Meta por zona: el MILP debe costar lo mismo que la suma, por zona, del algoritmo
   exacto de la prueba 3.2 (cada zona tiene su propia meta, así que no se mezclan).
2. meta_maxima: con 6 indicadores NO removibles (caso conocido), el máximo por zona
   debe coincidir con la enumeración exacta; una meta apenas por encima es infactible
   y una apenas por debajo es factible.
Los costos son sintéticos (u = 1), solo prueban la lógica.
"""
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # ...\Modelos

import parametros as P
from modelo2 import construir_nucleo, meta_maxima, resolver
from prueba_3_2 import cargar_pobres, costos_sinteticos, minimo_exacto, recalcular

N_HOGARES = 60
METAS = [0.10, 0.30]
FIJOS = ("empleo_formal", "logro_educativo", "analfabetismo", "desempleo_larga_duracion",
         "barreras_acceso_salud", "rezago_escolar")   # no removibles en esta prueba (caso extremo)


def min_contribucion_exacta(g, priv):
    """Menor sum C posible de un grupo de hogares (cada uno elige sus privaciones libres)."""
    tot = 0.0
    for r in g.itertuples():
        libres = [j for j in priv[r.ID_HOGAR] if j not in FIJOS]
        fijas = sum(P.PESOS[j] for j in priv[r.ID_HOGAR] if j in FIJOS)
        mejor = float("inf")
        for k in range(len(libres) + 1):
            for q in itertools.combinations(libres, k):
                s = fijas + sum(P.PESOS[j] for j in libres if j not in q)
                mejor = min(mejor, r.p * s if s > P.K_GRID + 1e-9 else 0.0)
        tot += mejor
    return tot


def main():
    hog, priv = cargar_pobres(N_HOGARES)
    costo = costos_sinteticos(hog, priv)
    zonas = sorted(hog.zona.unique())
    print(f"{len(hog)} hogares; por zona: " + ", ".join(
        f"{P.ZONAS[d]} {int((hog.zona == d).sum())}" for d in zonas))
    ok = True

    print("\n1) Meta por zona vs. suma de exactos por zona")
    for m in METAS:
        prob, x, y, C = construir_nucleo(hog, priv, costo, m, por_zona=True)
        milp = resolver(prob)["objetivo_millones"] * P.ESCALA_COSTO
        exacto = 0.0
        for d in zonas:
            g = hog[hog.zona == d].reset_index(drop=True)
            e, _ = minimo_exacto(g, {i: priv[i] for i in g.ID_HOGAR}, costo, m)
            exacto += e
        # cada zona cumple su meta (recalculado desde x, sin usar las C del MILP)
        xv = {k: round(v.value()) for k, v in x.items()}
        zona_ok = True
        for d in zonas:
            g = hog[hog.zona == d]
            num, _ = recalcular(g, priv, xv)
            zona_ok &= num <= (1 - m) * float((g.p * g.c0).sum()) + 1e-4
        # la meta por zona implica la global: cuesta igual o más que solo global
        pg, *_ = construir_nucleo(hog, priv, costo, m, por_zona=False)
        glob = resolver(pg)["objetivo_millones"] * P.ESCALA_COSTO
        igual = abs(milp - exacto) <= 1e-6 * max(1, exacto)
        ok &= igual and zona_ok and milp >= glob - 1e-3
        print(f"  m={m:.0%}: MILP {milp:,.0f} | suma exactos {exacto:,.0f} | "
              f"solo global {glob:,.0f} | cada zona cumple={zona_ok} iguales={igual} "
              f"por_zona>=global={milp >= glob - 1e-3}")

    print("\n2) meta_maxima con 6 indicadores no removibles (caso extremo)")
    mm = meta_maxima(hog, priv, fijos_cero=FIJOS)
    for d in zonas:
        g = hog[hog.zona == d]
        exacto = 1 - min_contribucion_exacta(g, priv) / float((g.p * g.c0).sum())
        coincide = abs(mm[d] - exacto) < 1e-9
        ok &= coincide
        print(f"  {P.ZONAS[d]:<15} MILP {mm[d]:.4%} | exacto {exacto:.4%} | coincide={coincide}")
    tope = min(mm[d] for d in zonas)
    print(f"  total {mm['total']:.4%}; el barrido de m llega hasta {tope:.4%} (zona que menos baja)")
    p_ok, *_ = construir_nucleo(hog, priv, costo, tope - 1e-4, por_zona=True, fijos_cero=FIJOS)
    p_mal, *_ = construir_nucleo(hog, priv, costo, tope + 1e-3, por_zona=True, fijos_cero=FIJOS)
    e_ok, e_mal = resolver(p_ok)["estado"], resolver(p_mal)["estado"]
    ok &= e_ok == "Optimal" and e_mal == "Infeasible"
    print(f"  meta justo debajo del tope: {e_ok} | justo encima: {e_mal}")
    print("\nTODO OK" if ok else "\nFALLÓ ALGO")
    return ok


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
