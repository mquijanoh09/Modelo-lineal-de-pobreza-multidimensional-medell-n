"""
09_modelo2_barridos.py  --  Modelo 2: curva costo-meta y sensibilidades.

Qué hace:
  1. Curva costo vs. meta de M0 (0 % a 100 %, de 5 en 5 %) con la meta en cada zona (caso base)
     y con la meta solo global. La diferencia es lo que cuesta la equidad territorial.
  2. Sensibilidades en las metas del caso base (5, 10 y 20 %):
       p = 0.50 y p = 0.75 (cumplimiento de Renta Ciudadana), E3 con rho_e = 0.20 + SevEdu,
       SevEdu activa (rho_e = 0.14), desempleo imputado (vuelve a ser quitable), y la versión comparable con M3/M4 de Jerónimo
       (sin E-7 y con meta global).
  3. Guarda todo en Modelos/Modelo_2/resultados/barridos/.
No se incluye u = 1 (datos_modelo aún no lo implementa) ni la prueba cruzada con el Modelo 1.

Correr:  python Modelos/Modelo_2/09_modelo2_barridos.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import pulp

import parametros as P
from datos_modelo import cargar_datos
from modelo2 import Modelo2

CARPETA = Path(__file__).resolve().parent / "resultados" / "barridos"
MALLA = [round(0.05 * i, 2) for i in range(21)]          # 0 %, 5 %, ..., 100 %


def correr(d, esc, m, piso=0.0):
    """Resuelve una meta. `piso` = costo (mil millones) del mismo escenario con meta 0 %:
    costo_incremental = costo - piso es lo que cuesta la meta, con las mismas obligaciones
    (E-7, y SevEdu si el escenario la activa). Auditoría N1."""
    mod = Modelo2(d, esc, meta_m=m).construir()
    mod.resolver(**P.SOLVER_M2)
    tabla = mod.tabla_comun()
    return {"escenario": esc["nombre"], "meta_m": m, "estado": mod.info["estado"],
            "gap": mod.info["gap"], "segundos": mod.info["segundos"],
            "costo_mil_millones": pulp.value(mod.costo_total()) / 1e9,
            "reduccion_M0": tabla.at["total", "reduccion_M0"],
            "salen_hogares": tabla.at["total", "salen_hogares"],
            "H": tabla.at["total", "H"], "A": tabla.at["total", "A"], "A_inicial": d.linea_base[1],
            "piso_E7_mil_millones": Modelo2.piso_e7(d) / 1e9,      # solo E-7, cuenta independiente
            "piso_escenario_mil_millones": piso,                    # costo con meta 0 % del escenario
            "costo_incremental_mil_millones": pulp.value(mod.costo_total()) / 1e9 - piso,
            "sevedu": tabla.at["total", "sevedu"]}


def main():
    CARPETA.mkdir(parents=True, exist_ok=True)
    d = cargar_datos()
    ok = True

    # 1. Curva costo-meta
    filas = []
    for nombre in ("base", "meta_global"):
        esc = P.escenario_m2("base", nombre)
        piso = correr(d, esc, 0.0)["costo_mil_millones"]
        for m in MALLA:
            f = correr(d, esc, m, piso)
            f["meta_zona"] = nombre == "base"
            filas.append(f)
            print(f"{nombre:<12} m={m:4.0%} {f['estado']:<8} costo {f['costo_mil_millones']:8.2f}  "
                  f"salen {f['salen_hogares']:6.0f}  gap {f['gap']:.1e}  {f['segundos']} s", flush=True)
    curva = pd.DataFrame(filas)
    curva.to_csv(CARPETA / "curva_costo_meta.csv", index=False, encoding="utf-8-sig")
    ok &= bool((curva.estado == "Optimal").all())
    for nombre, g in curva.groupby("meta_zona"):
        ok &= bool(g.costo_mil_millones.is_monotonic_increasing)     # el costo no baja al subir la meta
    pz = curva[curva.meta_zona].set_index("meta_m").costo_mil_millones
    pg = curva[~curva.meta_zona].set_index("meta_m").costo_mil_millones
    ok &= bool((pz >= pg - 1e-6).all())                                # exigir más no cuesta menos
    costo_equidad = (pz - pg).rename("costo_equidad_mil_millones")
    costo_equidad.to_csv(CARPETA / "costo_equidad_territorial.csv", encoding="utf-8-sig")
    print("\nCosto de la equidad territorial (zona - global, mil millones):")
    print(costo_equidad.round(2).to_string())

    # 2. Sensibilidades
    casos = [("sin_E7", "meta_global"), ("p_050", "base"), ("p_075", "base"), ("base", "con_sevedu"),
             ("con_E3", "con_sevedu"), ("desempleo_imputado", "base")]
    metas_extra = {"desempleo_imputado": [0.80, 0.90, 0.95, 1.00]}   # N2: donde cambia el costo
    filas = []
    for com, m2 in casos:
        esc = P.escenario_m2(com, m2)
        dd = cargar_datos(com)
        piso = correr(dd, esc, 0.0)["costo_mil_millones"]
        for m in P.METAS_M2 + metas_extra.get(com, []):
            f = correr(dd, esc, m, piso)
            filas.append(f)
            print(f"{esc['nombre']:<22} m={m:4.0%} {f['estado']:<8} costo {f['costo_mil_millones']:8.2f}  "
                  f"salen {f['salen_hogares']:4.0f}  SevEdu {f['sevedu']:,.0f}", flush=True)
    sens = pd.DataFrame(filas)
    sens.to_csv(CARPETA / "sensibilidades.csv", index=False, encoding="utf-8-sig")
    ok &= bool((sens.estado == "Optimal").all())
    print(f"\nArchivos en {CARPETA}")
    print("TODO OK" if ok else "FALLÓ ALGO: revisar")
    return ok


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
