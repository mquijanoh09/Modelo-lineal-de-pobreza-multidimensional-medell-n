"""
09_modelo2.py  --  Corrida del Modelo 2 (caso base y sus dos sensibilidades propias).

1. Prueba con 50 hogares pobres (regla del proyecto) y después con los 523.
2. meta_maxima (F2-3): reducción máxima de M0 por zona con E-7 activa y sin límite de costo.
   El barrido de m se detiene en la zona que menos puede bajar (D-M2-3).
3. Metas METAS_M2 (5, 10 y 20 %, las de Jerónimo) en:
     base          meta en cada zona P3, E-7, sin SevEdu
     meta_global   meta solo global (cuánto cuesta la equidad territorial)
     con_sevedu    + techo de SevEdu rho_e = 14 % (cuánto cuesta no abandonar a los más atrasados)
Resultados: Modelos/Modelo_2/resultados/m2_metas.csv y m2_meta_maxima.csv

Uso: python Modelos/Modelo_2/09_modelo2.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # ...\Modelos
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd

import parametros as P
from datos_modelo import cargar_datos
from modelo2 import correr, meta_maxima_completa
from modelo_base import tabla_resultados

RES = Path(__file__).resolve().parent / "resultados"
RES.mkdir(exist_ok=True)


def filas(rec, extra):
    return [{**extra, "zona": "Total" if d == "total" else P.ZONAS[d], **r}
            for d, r in rec.items() if d != "y_consistente"]


def verificar(rec, D, m, por_zona):
    """La meta se cumple con el M0 recalculado desde x (no con las C_i del MILP)."""
    ok = rec["y_consistente"]
    num0 = D.hog.assign(n=D.hog.p * D.hog.c0).groupby("zona").n.sum()
    if por_zona:
        for d in num0.index:
            ok &= rec[d]["M0"] * D.Pob_d[d] <= (1 - m) * num0[d] * (1 + 1e-6)
    ok &= rec["total"]["M0"] * D.Pob <= (1 - m) * num0.sum() * (1 + 1e-6)
    return ok


def main():
    print("=" * 78 + "\n PRUEBA con 50 hogares pobres\n" + "=" * 78)
    Dm = cargar_datos(P.escenario_m2(), n_muestra=50)
    mm = meta_maxima_completa(Dm)
    m_prueba = round(0.5 * min(v for k, v in mm.items() if k != "total"), 3)
    _, est, rec = correr(Dm, m_prueba)
    print(f"Muestra: meta máxima por zona {[f'{v:.1%}' for v in mm.values()]} · m = {m_prueba:.1%}: "
          f"{est['estado']}, costo ${est['costo'] / 1e9:,.1f} mm · meta cumplida recalculando: "
          f"{verificar(rec, Dm, m_prueba, True)}")

    print("\n" + "=" * 78 + "\n 523 HOGARES POBRES\n" + "=" * 78)
    D = cargar_datos(P.escenario_m2())
    print(D.resumen())
    mm = meta_maxima_completa(D)
    tope = min(v for k, v in mm.items() if k != "total")
    print("\nMeta máxima de reducción de M0 (E-7 activa, sin límite de costo):")
    for k, v in mm.items():
        print(f"  {'Total' if k == 'total' else P.ZONAS[k]:<16}{v:.2%}")
    print(f"  -> con meta por zona, m llega hasta {tope:.2%}")
    pd.DataFrame([{"zona": "Total" if k == "total" else P.ZONAS[k], "m_max": v} for k, v in mm.items()]
                 ).to_csv(RES / "m2_meta_maxima.csv", index=False)

    todas = []
    for nombre_m2 in ["base"] + list(P.SENSIBILIDADES_M2):
        Ds = D if nombre_m2 == "base" else cargar_datos(P.escenario_m2("base", nombre_m2))
        print(f"\n--- Escenario M2 '{nombre_m2}' ({Ds.esc['nombre']}) ---")
        for m in P.METAS_M2:
            if Ds.esc["meta_por_zona"] and m > tope:
                print(f"  m = {m:.0%}: por encima de la meta máxima por zona ({tope:.2%}), se omite")
                continue
            mod, est, rec = correr(Ds, m)
            if rec is None:
                print(f"  m = {m:.0%}: {est['estado']}")
                todas.append({"escenario_m2": nombre_m2, "meta": m, "estado": est["estado"], "zona": "Total"})
                continue
            ok = verificar(rec, Ds, m, Ds.esc["meta_por_zona"])
            print(tabla_resultados(rec, Ds, f"m = {m:.0%}: {est['estado']}, costo mínimo "
                                   f"${est['costo'] / 1e9:,.1f} mm, gap {est['gap']}, {est['segundos']} s, "
                                   f"meta cumplida recalculando desde x: {ok}"))
            assert ok, "la meta no se cumple con el M0 recalculado"
            todas += filas(rec, {"escenario_m2": nombre_m2, "meta": m, "estado": est["estado"],
                                 "gap": est["gap"], "costo_objetivo": est["costo"]})
    pd.DataFrame(todas).to_csv(RES / "m2_metas.csv", index=False)
    t = pd.DataFrame([f for f in todas if f["zona"] == "Total"])
    print("\nResumen: costo mínimo ($ mil millones) por meta")
    print(t.pivot_table(index="meta", columns="escenario_m2", values="costo").div(1e9).round(1).to_string())
    print(f"\nGuardado en {RES}")


if __name__ == "__main__":
    main()
