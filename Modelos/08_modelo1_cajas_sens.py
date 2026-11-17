"""Corre el caso base y cada sensibilidad del Modelo 1 (B = 424 mil millones) y guarda el plan por hogar.

Para cada escenario: r por el codo, rho por la regla de la brecha (o el que defina la política), dos etapas,
recálculo independiente. Guarda en data/processed/modelo1/sens/:
  <escenario>_plan_hogar.csv   plan por hogar (sale, quitadas)
  resumen_sens.csv             una fila por escenario (H, A, A0, r, rho, costo, salida por zona)
Es reanudable: si <escenario>_plan_hogar.csv ya existe, lo salta (borra el archivo para repetirlo).
Uso: .venv\\Scripts\\python.exe Modelos\\08_modelo1_cajas_sens.py [--B 424] [--solo base p_050 ...]
"""
import argparse
import importlib.util
import sys
import time
from pathlib import Path

import pandas as pd

RAIZ_M = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ_M))
import parametros as P
from datos_modelo import cargar_datos
from Modelo_1.modelo1 import resolver_dos_etapas, resolver_r, rho_regla_brecha
from utils_dane import OUT

spec = importlib.util.spec_from_file_location("barridos", RAIZ_M / "08_modelo1_barridos.py")
barridos = importlib.util.module_from_spec(spec)
spec.loader.exec_module(barridos)

SALIDA = OUT / "modelo1" / "sens"
GAP, TIEMPO = 1e-6, 300


def correr(nombre, B):
    pol = P.POLITICAS.get(nombre)
    d = cargar_datos("base" if pol else nombre)
    rho_e = pol.get("rho_e", d.esc["rho_e"]) if pol and "rho_e" in pol else d.esc["rho_e"]
    r_pedido = pol.get("r", d.esc["r"]) if pol else d.esc["r"]
    r, _ = resolver_r(d, B, r_pedido, rho_e=rho_e, gap_rel=GAP, time_limit=TIEMPO)
    rho = pol["rho"] if pol else "brecha"
    if rho == "brecha":
        rho, _ = rho_regla_brecha(d, B, r=r, rho_e=rho_e, gap_rel=GAP, time_limit=TIEMPO)
    elif rho == "codo":
        rho = barridos.rho_codo(d, B, rho_e, GAP, TIEMPO, r)
    m, info = resolver_dos_etapas(d, B, r=r, rho=rho, rho_e=rho_e, gap_rel=GAP, time_limit=TIEMPO)
    if info["etapa2"] is None or info["etapa2"]["estado"] != "Optimal":
        raise RuntimeError(f"{nombre}: sin solución óptima ({info})")
    plan, _, _ = m.solucion()
    rec = m.recalcular()
    t = rec.loc["total"]
    fila = {"escenario": nombre, "B_mil_millones": B / 1e9, "r": r, "rho": rho, "rho_e": rho_e,
            "salen_personas": t.salen_personas, "H0": t.H0, "H": t.H, "A0": t.A0, "A": t.A,
            "reduccion_M0": t.reduccion_M0, "reduccion_severidad": 1 - t.severidad / t.severidad_inicial,
            "costo_mil_millones": t.costo / 1e9}
    for z, zn in P.ZONAS.items():
        fila[f"sale_{zn}"] = rec.at[zn, "salen_personas"] / d.pobres_zona[z]
    return plan, fila


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=float, default=424.0)
    ap.add_argument("--solo", nargs="+", default=None)
    a = ap.parse_args()
    SALIDA.mkdir(parents=True, exist_ok=True)
    nombres = ["base"] + [n for n in P.SENSIBILIDADES if n != "u_1"] + list(P.POLITICAS)
    for n in (a.solo or nombres):
        ruta = SALIDA / f"{n}_plan_hogar.csv"
        if ruta.exists():
            print(f"{n}: ya existe, se salta")
            continue
        t0 = time.time()
        plan, fila = correr(n, a.B * 1e9)
        plan.to_csv(ruta, index=False)
        pd.DataFrame([fila]).to_csv(SALIDA / f"{n}_resumen.csv", index=False)
        print(f"{n}: {fila['salen_personas']:,.0f} personas, r={fila['r']:.3f}, rho={fila['rho']}, "
              f"A={fila['A']:.4f} (A0={fila['A0']:.4f}) en {time.time() - t0:.0f} s", flush=True)
    filas = [pd.read_csv(p) for p in sorted(SALIDA.glob("*_resumen.csv"))]
    pd.concat(filas).to_csv(SALIDA / "resumen_sens.csv", index=False)


if __name__ == "__main__":
    main()
