"""
09_modelo2_barridos.py  --  Barridos del Modelo 2.

1. Curva costo mínimo vs. meta m (malla_m2 hasta la meta máxima), con meta por zona (caso base)
   y solo global. m = 0 da el piso de costo de E-7 (D-M2-2): se reporta aparte y se reporta
   también el costo incremental sobre ese piso.
2. Sensibilidades comunes (parametros.SENSIBILIDADES) en m = 10 %.
3. Validación cruzada con el Modelo 1 (formulacion_modelo2.md §6): con B = costo del plan del
   Modelo 2 (con SevEdu, para que el plan sea factible en el Modelo 1), el Modelo 1 debe sacar
   al menos tantas personas como ese plan.
Resultados: Modelos/Modelo_2/resultados/m2_barrido_meta.csv, m2_sensibilidades.csv, m2_validacion_m1.csv

Uso: python Modelos/Modelo_2/09_modelo2_barridos.py [paso]     (paso por defecto PASO_MALLA_M2)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # ...\Modelos
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Modelo_1"))

import pandas as pd

import parametros as P
from datos_modelo import cargar_datos
from modelo2 import correr, meta_maxima_completa
import modelo1

RES = Path(__file__).resolve().parent / "resultados"
RES.mkdir(exist_ok=True)


def total(rec, extra):
    return {**extra, **rec["total"]}


def main(paso=P.PASO_MALLA_M2):
    D = cargar_datos(P.escenario_m2())
    mm = meta_maxima_completa(D)
    tope = min(v for k, v in mm.items() if k != "total")
    malla = P.malla_m2(tope, paso)
    print(f"Meta máxima por zona {tope:.2%}; malla de {len(malla)} metas con paso {paso}")

    # 1. Curva costo vs. meta
    filas = []
    for nombre_m2 in ["base", "meta_global"]:
        Ds = D if nombre_m2 == "base" else cargar_datos(P.escenario_m2("base", nombre_m2))
        for m in malla:
            _, est, rec = correr(Ds, m, time_limit=P.SOLVER_M2_BARRIDO["time_limit"])
            if rec is None:
                filas.append({"escenario_m2": nombre_m2, "meta": m, "estado": est["estado"]})
                continue
            filas.append(total(rec, {"escenario_m2": nombre_m2, "meta": m, "estado": est["estado"],
                                     "gap": est["gap"], "segundos": est["segundos"]}))
    df = pd.DataFrame(filas)
    piso = df[df.meta == 0].set_index("escenario_m2").costo
    df["costo_sobre_piso"] = df.costo - df.escenario_m2.map(piso)
    df.to_csv(RES / "m2_barrido_meta.csv", index=False)
    print(f"\n1) Piso de costo por E-7 (m = 0): ${piso['base'] / 1e9:,.1f} mm")
    tab = df.pivot_table(index="meta", columns="escenario_m2", values="costo").div(1e9).round(1)
    tab["equidad_territorial"] = (tab["base"] - tab["meta_global"]).round(1)
    print("   Costo mínimo ($ mil millones):")
    print(tab.to_string())
    print(f"   Gap máximo de la curva: {df.gap.max():.2e} (puntos con gap > 1e-6: {int((df.gap > 1e-6).sum())})")

    # 2. Sensibilidades comunes en m = 10 %
    filas = []
    for nombre in ["base"] + list(P.SENSIBILIDADES):
        Ds = cargar_datos(P.escenario_m2(nombre))
        _, est, rec = correr(Ds, 0.10)
        filas.append(total(rec, {"escenario": nombre, "estado": est["estado"]}) if rec
                     else {"escenario": nombre, "estado": est["estado"]})
    s = pd.DataFrame(filas)
    s.to_csv(RES / "m2_sensibilidades.csv", index=False)
    print("\n2) Sensibilidades en m = 10 %")
    print(s[["escenario", "estado", "costo", "personas_salen", "H", "M0", "severidad", "SevEdu"]].to_string(
        index=False, formatters={"costo": lambda v: f"{v / 1e9:,.1f}", "H": "{:.2%}".format}))

    # 3. Validación cruzada con el Modelo 1
    Dsev = cargar_datos(P.escenario_m2("base", "con_sevedu"))
    D1 = cargar_datos(P.escenario())
    filas = []
    for m in P.METAS_M2:
        _, est2, rec2 = correr(Dsev, m)
        B = est2["costo"] * (1 + 1e-9)
        _, est1, rec1 = modelo1.correr(D1, B=B)
        ok = rec1["total"]["personas_salen"] >= rec2["total"]["personas_salen"] - 1e-6
        filas.append({"meta": m, "B_modelo2": B, "personas_M2": rec2["total"]["personas_salen"],
                      "personas_M1": rec1["total"]["personas_salen"], "M1_>=_M2": ok})
        assert ok, "el Modelo 1 saca menos personas que el plan del Modelo 2 con el mismo B"
    v = pd.DataFrame(filas)
    v.to_csv(RES / "m2_validacion_m1.csv", index=False)
    print("\n3) Validación cruzada M1 >= M2 con el mismo B")
    print(v.to_string(index=False, formatters={"B_modelo2": lambda x: f"{x / 1e9:,.1f}"}))
    print(f"\nGuardado en {RES}")


if __name__ == "__main__":
    main(float(sys.argv[1]) if len(sys.argv) > 1 else P.PASO_MALLA_M2)
