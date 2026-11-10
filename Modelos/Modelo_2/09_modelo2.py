"""
09_modelo2.py  --  Modelo 2, caso base: costo mínimo para reducir M0 un 5 %, 10 % y 20 %.

Qué hace, en orden:
  1. Carga los datos y comprueba la línea base (523 pobres, M0 = 0.038684).
  2. Validaciones del modelo:
       a. meta 0 %: el costo es el piso de E-7, igual a una cuenta independiente;
       b. el costo del MILP coincide con el que recalcula la base desde las x, z, t y v;
       c. cada zona cumple su meta de M0 (caso base: meta en cada zona);
       d. el costo no baja al subir la meta.
  3. Resuelve cada meta del caso base (parametros.METAS_M2) con HiGHS y guarda en
     Modelos/Modelo_2/resultados/caso_base/ la tabla común, el gasto por rubro y los planes.
  4. Escribe resultados/caso_base/resumen_caso_base.csv con una fila por meta.

Correr:  python Modelos/Modelo_2/09_modelo2.py
Escenario: parametros.escenario_m2("base", "base"). Decisiones: docs/justificacion_decisiones_modelo2.md
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # ...\Modelos

import pandas as pd
import pulp

import parametros as P
from datos_modelo import cargar_datos
from modelo2 import Modelo2

CARPETA = Path(__file__).resolve().parent / "resultados" / "caso_base"


def ok(c):
    return "OK   " if c else "FALLA"


def resolver(d, esc, m):
    mod = Modelo2(d, esc, meta_m=m).construir()
    mod.resolver(**P.SOLVER_M2)
    return mod


def main():
    d, esc = cargar_datos(), P.escenario_m2()
    H0, A0, M0 = d.linea_base
    zonas = [P.ZONAS[z] for z in sorted(P.ZONAS)]
    todo = True

    print("=" * 76, "\n MODELO 2 · caso base · meta de M0 en cada zona\n", "=" * 76, sep="")
    base_ok = len(d.hogares) == 523 and abs(M0 - 0.038684) < 5e-7
    todo &= base_ok
    print(f"{ok(base_ok)} línea base: {len(d.hogares)} hogares pobres, M0 = {M0:.6f}, H = {H0:.4%}, A = {A0:.4f}")

    print("\n-- Validaciones")
    mod0 = resolver(d, esc, 0.0)
    costo0, piso = pulp.value(mod0.costo_total()), Modelo2.piso_e7(d)
    v_a = mod0.info["estado"] == "Optimal" and abs(costo0 - piso) <= 1e-6 * piso
    todo &= v_a
    print(f"{ok(v_a)} (a) meta 0 %: costo {costo0 / 1e9:,.2f} mil millones = piso E-7 independiente {piso / 1e9:,.2f}")

    filas, previo = [], costo0
    for m in P.METAS_M2:
        mod = resolver(d, esc, m)
        info = mod.info
        costo = pulp.value(mod.costo_total())
        tabla = mod.tabla_comun()
        v_b = abs(tabla.at["total", "costo"] - costo) <= 1
        v_c = all(tabla.at[z, "reduccion_M0"] >= m - 1e-6 for z in zonas)
        v_d = costo >= previo - 1
        previo = costo
        todo &= info["estado"] == "Optimal" and v_b and v_c and v_d
        print(f"{ok(info['estado'] == 'Optimal')} m = {m:.0%}: {info['estado']}, gap {info['gap']:.1e}, {info['segundos']} s")
        print(f"      {ok(v_b)} (b) costo recalculado = MILP   {ok(v_c)} (c) cada zona cumple   {ok(v_d)} (d) costo no baja")
        nombre = f"m{int(round(m * 100)):02d}"
        mod.guardar(CARPETA, nombre)
        filas.append(mod.resumen())

        print(f"\n   Resultados con meta {m:.0%} (costo en pesos):")
        mostrar = tabla[["salen_personas", "H", "A", "M0", "reduccion_M0", "severidad", "sevedu", "costo"]]
        print("   " + mostrar.to_string(float_format=lambda v: f"{v:,.4f}" if abs(v) < 100 else f"{v:,.0f}")
              .replace("\n", "\n   "))
        g = mod.gasto_por_indicador()
        print("\n   Gasto por rubro (mil millones de pesos):")
        print("   " + (g[["total"]] / 1e9).round(2).to_string(float_format=lambda v: f"{v:,.2f}")
              .replace("\n", "\n   "))
        print()

    resumen = pd.DataFrame(filas)
    resumen.to_csv(CARPETA / "resumen_caso_base.csv", index=False, encoding="utf-8-sig")
    print("-- Resumen del caso base")
    print(resumen[["meta_m", "estado", "gap", "costo_mil_millones", "piso_E7_mil_millones", "costo_sobre_piso_E7_mil_millones", "reduccion_M0", "salen_hogares", "A", "A_inicial"]]
          .to_string(index=False, float_format=lambda v: f"{v:,.4f}"))
    print(f"\nArchivos en {CARPETA}")
    print("\nTODO OK" if todo else "\nFALLÓ ALGO: revisar las líneas FALLA")
    return todo


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
