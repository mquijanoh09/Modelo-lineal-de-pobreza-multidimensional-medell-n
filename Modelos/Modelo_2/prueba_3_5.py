"""
prueba_3_5.py  --  Prueba de la subfase 3.5 (gasto por indicador, tabla común y guardado).

Se resuelve el caso base con meta 10 % y se comprueba:
  1. El gasto por rubro suma exactamente el costo total, y por zona coincide con el costo
     por zona que recalcula la base (cuenta independiente).
  2. Cada rubro simple gasta lo que dicen sus x (c_ij * x_ij sumado a mano).
  3. La tabla común trae total y las 3 zonas, y su M0 final es el de recalcular().
  4. guardar() escribe los 5 CSV y al leerlos de nuevo dan lo mismo.
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # ...\\Modelos

import pandas as pd
import pulp

import parametros as P
from datos_modelo import cargar_datos
from modelo2 import Modelo2
from modelo_base import _val


def ok(c):
    return "OK   " if c else "FALLA"


def main():
    d, esc = cargar_datos(), P.escenario_m2()
    m = Modelo2(d, esc, meta_m=0.10).construir()
    info = m.resolver()
    print(f"Corrida: {info}\n")
    todo = info["estado"] == "Optimal"
    costo = pulp.value(m.costo_total())
    zonas = [P.ZONAS[z] for z in sorted(P.ZONAS)]

    g = m.gasto_por_indicador()
    mostrar = g.copy()
    mostrar.loc[:, mostrar.columns != "participacion"] /= 1e9
    print(mostrar.to_string(float_format=lambda v: f"{v:,.2f}"),
          "\n(gasto en mil millones de pesos; participación = fracción del total)\n")
    suma = abs(g.total.sum() - costo) <= 1
    rec = m.tabla_comun()
    por_zona = all(abs(g[z].sum() - rec.at[z, "costo"]) <= 1 for z in zonas)
    todo &= suma and por_zona
    print(f"{ok(suma)} el gasto por rubro suma el costo total: {g.total.sum():,.0f} = {costo:,.0f}")
    print(f"{ok(por_zona)} el gasto por zona coincide con el costo por zona de recalcular()")

    # 2. un rubro simple a mano
    mano = sum(d.c[(i, j)] * _val(m.x[(i, j)]) for (i, j) in d.c if j == "empleo_formal")
    if "empleo_formal" in g.index:
        rub = abs(g.at["empleo_formal", "total"] - mano) <= 1
    else:
        rub = mano == 0
    todo &= rub
    print(f"{ok(rub)} empleo_formal: tabla {g.total.get('empleo_formal', 0):,.0f} = suma a mano {mano:,.0f}")

    # 3. tabla común
    filas = set(rec.index) == {"total", *zonas}
    m0 = abs(rec.at["total", "M0"] - (1 - rec.at["total", "reduccion_M0"]) * rec.at["total", "M0_inicial"]) < 1e-12
    todo &= filas and m0
    print(f"{ok(filas)} la tabla común tiene total y las 3 zonas")
    print(f"{ok(m0)} M0 final = (1 - reducción) * M0 inicial")
    print((rec[["salen_personas", "H", "A", "M0", "reduccion_M0", "severidad", "sevedu", "costo"]]
           .to_string(float_format=lambda v: f"{v:,.4f}" if abs(v) < 100 else f"{v:,.0f}")))

    # 4. guardar y volver a leer
    with tempfile.TemporaryDirectory() as tmp:
        m.guardar(tmp, "m10")
        archivos = sorted(p.name for p in Path(tmp).iterdir())
        esperados = sorted(f"m10_{s}.csv" for s in ("tabla_comun", "gasto", "plan_hogar", "plan_nino", "plan_adulto"))
        leido = pd.read_csv(Path(tmp) / "m10_tabla_comun.csv", index_col=0)
        igual = abs(leido.at["total", "costo"] - rec.at["total", "costo"]) <= 1
        sale = pd.read_csv(Path(tmp) / "m10_plan_hogar.csv").sale.sum()
        todo &= archivos == esperados and igual and sale == rec.at["total", "salen_hogares"]
        print(f"\n{ok(archivos == esperados)} guardar() escribió {len(archivos)} archivos")
        print(f"{ok(igual)} el costo leído del CSV coincide; {ok(sale == rec.at['total', 'salen_hogares'])} hogares que salen en plan_hogar = {sale}")

    r = m.resumen()
    print(f"\nresumen(): {{meta {r['meta_m']}, costo {r['costo'] / 1e9:,.1f} mil M, reducción {r['reduccion_M0']:.1%}, gap {r['gap']}}}")
    print("\nTODO OK" if todo else "\nFALLÓ ALGO")
    return todo


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
