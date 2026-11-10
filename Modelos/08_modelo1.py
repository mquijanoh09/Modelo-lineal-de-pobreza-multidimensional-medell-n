"""
08_modelo1.py  --  Corrida del Modelo 1 con los 523 hogares pobres de Antioquia.

    max personas que salen de la pobreza  s.a.  presupuesto B, equidad por zona (r),
    techo de severidad (rho) y techo de SevEdu (rho_e), con desempate en dos etapas (D1).

Ejemplos (desde la carpeta Modelos):
    python 08_modelo1.py                          # caso base, B = punto medio del rango
    python 08_modelo1.py --B 300 --r 0.2 --rho 0.1       # B en MIL MILLONES de pesos
    python 08_modelo1.py --escenario p_050 --B 400
    python 08_modelo1.py --sin-sevedu             # sin el techo de SevEdu

Salida: tablas en pantalla y CSV en data/processed/modelo1/.
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from datos_modelo import cargar_datos
from Modelo_1.modelo1 import resolver_r, rho_regla_brecha, Modelo1, rango_B, resolver_dos_etapas
from utils_dane import OUT
import parametros as P

SALIDA = OUT / "modelo1"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--escenario", default="base", help="base o una clave de parametros.SENSIBILIDADES")
    ap.add_argument("--B", type=float, default=None, help="presupuesto en MIL MILLONES de pesos")
    ap.add_argument("--r", default=None, help="fracción mínima de pobres que sale en cada zona (por defecto la del escenario)")
    ap.add_argument("--rho", default=None, help="techo de severidad: un número, 'brecha' (menor rho con A <= A0), "
                    "'ninguno' (sin techo). Por defecto el del escenario ('brecha')")
    ap.add_argument("--rho-e", type=float, default=None, help="reducción mínima de SevEdu (por defecto la del escenario)")
    ap.add_argument("--sin-sevedu", action="store_true", help="no exigir el techo de SevEdu")
    ap.add_argument("--una-etapa", action="store_true", help="solo la etapa 1 (max H), sin desempate")
    ap.add_argument("--gap", type=float, default=1e-6)
    ap.add_argument("--tiempo", type=float, default=300)
    a = ap.parse_args()

    d = cargar_datos(a.escenario)
    rho_e = None if a.sin_sevedu else (a.rho_e if a.rho_e is not None else d.esc["rho_e"])
    print(f"Escenario: {d.esc['nombre']} | hogares pobres {len(d.hogares)} | rho_e = {rho_e}")

    rango = rango_B(d, rho_e)
    print(f"Rango útil de B: de ${rango['B_min'] / 1e9:,.1f} a ${rango['B_max'] / 1e9:,.1f} mil millones "
          f"(H máximo = {rango['H_max']:,.0f} personas)")
    B = a.B * 1e9 if a.B is not None else (rango["B_min"] + rango["B_max"]) / 2
    r_pedido = d.esc["r"] if a.r is None else a.r
    a.r, inf_r = resolver_r(d, B, r_pedido, rho_e=rho_e, gap_rel=a.gap, time_limit=a.tiempo)
    if r_pedido == "codo":
        print(f"r por el codo de H contra r: {a.r} {inf_r}")
    pedido = d.esc["rho"] if a.rho is None else a.rho
    if pedido in ("ninguno", "none", "None"):
        pedido = None
    if pedido == "brecha":
        rho, inf = rho_regla_brecha(d, B, r=a.r, rho_e=rho_e, gap_rel=a.gap, time_limit=a.tiempo)
        print(f"Regla de la brecha: rho = {rho} {inf}")
        if rho is None:
            print("La regla de la brecha no se alcanza con este B: se corre sin techo de severidad.")
    else:
        rho = None if pedido is None else float(pedido)
    a.rho = rho
    print(f"B = ${B / 1e9:,.1f} mil millones | r = {a.r} | rho = {a.rho}")

    if a.una_etapa:
        m = Modelo1(d, B, r=a.r, rho=a.rho, rho_e=rho_e).construir()
        info = {"etapa1": m.resolver(a.gap, a.tiempo), "etapa2": None}
    else:
        m, info = resolver_dos_etapas(d, B, r=a.r, rho=a.rho, rho_e=rho_e, gap_rel=a.gap, time_limit=a.tiempo)
    print(f"Etapa 1: {info['etapa1']}")
    if not a.una_etapa:
        print(f"Etapa 2: {info['etapa2']}")
    ultima = info["etapa1"] if a.una_etapa else info["etapa2"]
    if ultima is None or ultima["estado"] != "Optimal":
        print("\nSin solución óptima. Si el estado dice Infeasible: ¿B por debajo del gasto forzoso, o equidad/techos imposibles? "
              "Si dice Cortado: HiGHS se detuvo por tiempo sin demostrar el óptimo; sube --tiempo.")
        return

    plan_hogar, plan_nino, plan_adulto = m.solucion()
    rec = m.recalcular()
    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", 30)
    pd.set_option("display.float_format", "{:,.4f}".format)
    print("\n" + "=" * 90 + "\n RESULTADO (cuenta independiente con la regla del DANE)\n" + "=" * 90)
    print(rec[["salen_personas", "salen_hogares", "H0", "H", "M0_inicial", "M0", "reduccion_M0"]])
    print(rec[["severidad_inicial", "severidad", "sevedu_inicial", "sevedu", "costo"]])

    t = rec.loc["total"]
    print("\nChequeos:")
    print(f"  costo {t.costo / 1e9:,.2f} mil millones <= B {B / 1e9:,.2f}: {'OK' if t.costo <= B + 1 else 'FALLA'}")
    print(f"  personas que salen: modelo {plan_hogar.eval('p * sale').sum():,.0f} = recalculado {t.salen_personas:,.0f}: "
          f"{'OK' if abs(plan_hogar.eval('p * sale').sum() - t.salen_personas) < 1 else 'FALLA'}")
    if rho_e is not None:
        red = 1 - t.sevedu / t.sevedu_inicial
        print(f"  reducción de SevEdu {red:.1%} >= rho_e {rho_e:.0%}: {'OK' if red >= rho_e - 1e-9 else 'FALLA'}")
    if a.rho is not None:
        red = 1 - t.severidad / t.severidad_inicial
        print(f"  reducción de severidad {red:.1%} >= rho {a.rho:.0%}: {'OK' if red >= a.rho - 1e-9 else 'FALLA'}")
    if a.r:
        for z, nombre in P.ZONAS.items():
            frac = rec.at[nombre, "salen_personas"] / (m.datos.pobres_zona[z])
            print(f"  {nombre}: sale {frac:.1%} >= r {a.r:.0%}: {'OK' if frac >= a.r - 1e-9 else 'FALLA'}")

    SALIDA.mkdir(parents=True, exist_ok=True)
    rec.to_csv(SALIDA / "resumen.csv")
    plan_hogar.to_csv(SALIDA / "plan_hogar.csv", index=False)
    plan_nino.to_csv(SALIDA / "plan_nino.csv", index=False)
    plan_adulto.to_csv(SALIDA / "plan_adulto.csv", index=False)
    print(f"\nGuardado en {SALIDA}")


if __name__ == "__main__":
    main()
