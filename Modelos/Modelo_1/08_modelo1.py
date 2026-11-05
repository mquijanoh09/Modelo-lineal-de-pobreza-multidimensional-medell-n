"""
08_modelo1.py  --  Corrida del Modelo 1 (caso base) y cálculo del rango de B.

1. Prueba con 50 hogares pobres (regla del proyecto) y después con los 523.
2. Extremos de B (pendiente P5 y §8 del informe, con los costos verificados):
     B_piso : costo mínimo con H = 0 (lo que exigen E-7 y el techo de SevEdu aunque nadie salga)
     B_sat  : costo mínimo de alcanzar el H máximo factible (sin presupuesto)
3. Caso base en B_ref = B_piso + FRACCION_B_REF (B_sat - B_piso), con r = 0, rho = 0 y rho_e = 14 %.
Resultados: Modelos/Modelo_1/resultados/m1_caso_base.csv y m1_rango_B.csv

Uso: python Modelos/Modelo_1/08_modelo1.py [escenario]      (por defecto "base")
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # ...\Modelos
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd

import parametros as P
from datos_modelo import cargar_datos
from modelo1 import Modelo1, correr
from modelo_base import tabla_resultados

RES = Path(__file__).resolve().parent / "resultados"
RES.mkdir(exist_ok=True)


def _ok(est, que):
    if est["estado"] != "Optimal":
        raise RuntimeError(f"{que}: {est['estado']}")
    return est["objetivo"]


def B_de(piso, B_sat, f):
    """Presupuesto a una fracción f del rango útil: B_piso + f (B_sat - B_piso).
    Por debajo de B_piso el modelo es infactible (E-7 y SevEdu se pagan aunque nadie salga)."""
    return piso + f * (B_sat - piso)


def rango_B(D, rho_e=None):
    """Devuelve (B_piso, H_max, B_sat) para el escenario de D."""
    H_max = _ok(Modelo1(D, B=None, rho_e=rho_e).construir().resolver(dos_etapas=False), "H máximo")
    piso = _ok(Modelo1(D, modo="costo_H", H_meta=0, rho_e=rho_e).construir().resolver(), "B_piso")
    sat = Modelo1(D, modo="costo_H", H_meta=H_max * (1 - P.TOL_H_ETAPA2), rho_e=rho_e).construir()
    B_sat = _ok(sat.resolver(), "B_sat")
    return piso * P.ESCALA_COSTO, H_max, B_sat * P.ESCALA_COSTO


def filas(rec, extra):
    out = []
    for d, r in rec.items():
        if d == "y_consistente":
            continue
        out.append({**extra, "zona": "Total" if d == "total" else P.ZONAS[d], **r})
    return out


def main(nombre_esc="base"):
    esc = P.escenario(nombre_esc)

    print("=" * 78 + f"\n PRUEBA con 50 hogares pobres (escenario {nombre_esc})\n" + "=" * 78)
    # En la muestra se apaga E-5: con 50 hogares no hay niños suficientes para bajar SevEdu un 14 %.
    Dm = cargar_datos(esc, n_muestra=50)
    piso, H_max, B_sat = rango_B(Dm, rho_e=0)
    _, est, rec = correr(Dm, B=B_de(piso, B_sat, 0.5), rho_e=0)
    print(f"Muestra: piso ${piso / 1e9:,.1f} mm · B_sat ${B_sat / 1e9:,.1f} mm · con B a la mitad del rango: "
          f"{est['estado']}, {rec['total']['personas_salen']:,.0f} de {H_max:,.0f} personas · "
          f"y consistente {rec['y_consistente']}")

    print("\n" + "=" * 78 + "\n 523 HOGARES POBRES\n" + "=" * 78)
    D = cargar_datos(esc)
    print(D.resumen())
    piso, H_max, B_sat = rango_B(D)
    print(f"\nRango de B (costos verificados, escenario {nombre_esc}):")
    print(f"  B_piso = ${piso / 1e9:,.1f} mil millones (E-7 + SevEdu {esc['rho_e']:.0%}, H = 0)")
    print(f"  H máximo factible = {H_max:,.0f} personas ({H_max / sum(D.Pobres_d.values()):.1%} de los pobres)")
    print(f"  B_sat  = ${B_sat / 1e9:,.1f} mil millones (mínimo para alcanzar el H máximo)")
    todo = sum(D.costo_x.values())
    print(f"  Quitar todas las privaciones simples: ${todo / 1e12:,.2f} billones")
    pd.DataFrame([{"escenario": nombre_esc, "B_piso": piso, "H_max": H_max, "B_sat": B_sat,
                   "todas_las_privaciones_simples": todo}]).to_csv(RES / f"m1_rango_B_{nombre_esc}.csv", index=False)

    B_ref = B_de(piso, B_sat, P.FRACCION_B_REF)
    m, est, rec = correr(D, B=B_ref)
    print(f"\nCaso base: B = ${B_ref / 1e9:,.1f} mm ({P.FRACCION_B_REF:.0%} del rango B_piso-B_sat), r = 0, rho = 0, "
          f"rho_e = {esc['rho_e']:.0%}")
    e1, e2 = m.info["etapa1"], m.info["etapa2"]
    print(f"  Etapa 1: {e1['estado']}, H* = {m.info['H_star']:,.0f} personas, gap {e1['gap']}, {e1['segundos']} s")
    print(f"  Etapa 2: {e2['estado']}, severidad {e2['objetivo']:,.0f}, gap {e2['gap']}, {e2['segundos']} s")
    print(tabla_resultados(rec, D, "Resultados recalculados desde x (no desde y)"))
    assert rec["y_consistente"], "algún y_i = 1 no corresponde a un hogar que sale de verdad"
    assert rec["total"]["costo"] <= B_ref * (1 + 1e-9), "el costo recalculado supera el presupuesto"
    assert abs(rec["total"]["personas_salen"] - m.info["H_star"]) < 1e-3 * max(1, m.info["H_star"]) + 1
    pd.DataFrame(filas(rec, {"escenario": nombre_esc, "B": B_ref, "r": 0, "rho": 0, "rho_e": esc["rho_e"]})
                 ).to_csv(RES / f"m1_caso_base_{nombre_esc}.csv", index=False)
    print(f"\nGuardado en {RES}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "base")
