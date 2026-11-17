"""
09_modelo2_severidad.py  --  Modelo 2 con techo de severidad (escenario aparte, decidido por Martín el 10-nov).

Qué hace:
  1. Caso con rho = meta (severidad baja al menos lo mismo que M0), para m = 5, 10 y 20 %,
     comparado con el caso base (sin techo de severidad): costo, personas, A, severidad, SevEdu.
  2. Barrido de rho (de 0 de 5 en 5 % hasta que el problema es infactible) para cada meta:
     costo, A y si la brecha no crece (A <= A0), la regla de equidad del Modelo 1.
  3. Validaciones: la reducción de severidad recalculada desde las x cumple rho; costo = recalculado.
Guarda en Modelos/Modelo_2/resultados/severidad/: comparacion_rho_meta.csv y barrido_rho.csv.

Correr:  python Modelos/Modelo_2/09_modelo2_severidad.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import pulp

import parametros as P
from datos_modelo import cargar_datos
from modelo2 import Modelo2

CARPETA = Path(__file__).resolve().parent / "resultados" / "severidad"


def correr(d, esc, m):
    mod = Modelo2(d, esc, meta_m=m).construir()
    mod.resolver(**P.SOLVER_M2)
    if mod.info["estado"] != "Optimal":
        return {"estado": mod.info["estado"], "meta_m": m, "rho": esc.get("rho_sev") if esc.get("usar_severidad") else None}, mod
    t = mod.recalcular().loc["total"]
    costo = pulp.value(mod.costo_total())
    return {"estado": "Optimal", "meta_m": m, "rho": esc.get("rho_sev") if esc.get("usar_severidad") else None,
            "costo_mil_millones": costo / 1e9, "costo_recalculado_ok": abs(float(t.costo) - costo) <= 1,
            "salen_hogares": t.salen_hogares, "salen_personas": t.salen_personas, "H": t.H, "A": t.A,
            "A_inicial": d.linea_base[1], "brecha_no_crece": bool(t.A <= d.linea_base[1] + 1e-9),
            "reduccion_M0": t.reduccion_M0, "reduccion_severidad": 1 - t.severidad / t.severidad_inicial,
            "sevedu": t.sevedu, "gap": mod.info["gap"], "segundos": mod.info["segundos"]}, mod


def main():
    CARPETA.mkdir(parents=True, exist_ok=True)
    d = cargar_datos()
    base = P.escenario_m2()
    ok = True

    # 1. rho = meta
    filas = []
    for m in P.METAS_M2:
        fb, _ = correr(d, base, m)
        fb["escenario"] = "base (sin techo de severidad)"
        fs, _ = correr(d, {**base, "usar_severidad": True, "rho_sev": m}, m)
        fs["escenario"] = "con severidad (rho = meta)"
        v = fs["estado"] == "Optimal" and fs["reduccion_severidad"] >= m - 1e-6 and fs["costo_recalculado_ok"]
        ok &= v and fb["estado"] == "Optimal"
        filas += [fb, fs]
        print(f"m = {m:.0%}: base {fb['costo_mil_millones']:.2f} mm, A {fb['A']:.4f}, sev -{fb['reduccion_severidad']:.1%} | "
              f"con severidad {fs['costo_mil_millones']:.2f} mm, A {fs['A']:.4f}, sev -{fs['reduccion_severidad']:.1%}  "
              f"[{'OK' if v else 'FALLA'}]", flush=True)
    pd.DataFrame(filas).to_csv(CARPETA / "comparacion_rho_meta.csv", index=False, encoding="utf-8-sig")

    # 2. barrido de rho
    filas = []
    for m in P.METAS_M2:
        rho = 0.0
        while rho < 0.95:
            f, _ = correr(d, {**base, "usar_severidad": True, "rho_sev": round(rho, 4)}, m)
            filas.append(f)
            if f["estado"] != "Optimal":
                print(f"m = {m:.0%}, rho = {rho:.0%}: {f['estado']} (fin del barrido)", flush=True)
                break
            print(f"m = {m:.0%}, rho = {rho:4.0%}: costo {f['costo_mil_millones']:7.2f} mm, A {f['A']:.4f} "
                  f"({'no crece' if f['brecha_no_crece'] else 'crece'}), salen {f['salen_hogares']:.0f}, {f['segundos']} s", flush=True)
            rho += 0.05
    barrido = pd.DataFrame(filas)
    barrido.to_csv(CARPETA / "barrido_rho.csv", index=False, encoding="utf-8-sig")
    for m, g in barrido[barrido.estado == "Optimal"].groupby("meta_m"):
        buenos = g[g.brecha_no_crece]
        if len(buenos):
            r = buenos.iloc[0]
            print(f"m = {m:.0%}: menor rho de la malla con A <= A0: {r.rho:.0%} (costo {r.costo_mil_millones:.2f} mm)")
        else:
            print(f"m = {m:.0%}: ningún rho de la malla deja A <= A0")
    ok &= bool((barrido[barrido.estado == "Optimal"].costo_recalculado_ok).all())
    print(f"\nArchivos en {CARPETA}")
    print("TODO OK" if ok else "FALLÓ ALGO: revisar")
    return ok


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
