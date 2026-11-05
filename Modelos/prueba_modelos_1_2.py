"""
prueba_modelos_1_2.py  --  Pruebas de regresión de los Modelos 1 y 2 (correr antes de cada commit).

1. Datos: 523 pobres, M0 = 0.038684, Sev0 ≈ 117,908, SevEdu_sin ≈ 21,562, 6,571 tangentes, 215 niños
   en la cohorte y 29 con E-7 (valores de control de Martín).
2. Modelo 1 en B_ref:
   - (2) big-M: todo hogar con y_i = 1 sale de verdad (s_i <= 0.33 recalculado desde x);
   - (7) tangentes: en la etapa 2, q_i = s_i^2 exacto en cada hogar (las tangentes no dejan holgura);
   - (1) el costo recalculado no supera B;  (E-7) los 29 niños obligatorios reciben una estrategia;
   - (E-5) SevEdu baja al menos rho_e.
3. Modelo 2 con m = 10 %: (3) censura: sum C_i >= M0 recalculado; la meta se cumple en cada zona.
Uso: python Modelos/prueba_modelos_1_2.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "Modelo_1"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "Modelo_2"))

import parametros as P
from datos_modelo import cargar_datos
import modelo1
import modelo2


def check(nombre, cond):
    print(f"  [{'OK' if cond else 'FALLA'}] {nombre}")
    return bool(cond)


def main():
    ok = True
    print("1) Datos")
    D = cargar_datos()
    ok &= check("523 hogares pobres", len(D.hog) == 523)
    ok &= check(f"M0 = {D.M0_0:.6f}", abs(D.M0_0 - 0.038684) < 1e-6)
    ok &= check(f"Sev0 = {D.Sev0:,.0f}", abs(D.Sev0 - 117_908) < 1)
    ok &= check(f"SevEdu_sin = {D.SevEdu_sin:,.0f}", abs(D.SevEdu_sin - 21_562) < 1)
    ok &= check("6,571 tangentes", sum(len(v) for v in D.A.values()) == 6571)
    ok &= check("215 niños en la cohorte, 29 con E-7",
                D.ninos.en_cohorte_sevedu.sum() == 215 and D.ninos.obligatorio_E7.sum() == 29)

    print("2) Modelo 1")
    m08 = __import__("importlib").import_module("08_modelo1")
    piso, H_max, B_sat = m08.rango_B(D)
    B = m08.B_de(piso, B_sat, P.FRACCION_B_REF)
    m, est, rec = modelo1.correr(D, B=B)
    ok &= check(f"dos etapas óptimas ({m.info['etapa1']['estado']}, {m.info['etapa2']['estado']})",
                est["estado"] == "Optimal")
    ok &= check("(2) y_i = 1 solo si el hogar sale", rec["y_consistente"])
    h = m.hog_resultado.set_index("ID_HOGAR")
    err_q = max(abs(m.q[i].value() - h.s1[i] ** 2) for i in h.index)
    ok &= check(f"(7) q_i = s_i^2 exacto en la etapa 2 (error máx {err_q:.1e})", err_q < 1e-6)
    ok &= check(f"(1) costo {rec['total']['costo'] / 1e9:,.1f} <= B {B / 1e9:,.1f}", rec["total"]["costo"] <= B * (1 + 1e-9))
    z = m.valores()["z"]
    oblig = D.ninos[D.ninos.obligatorio_E7].ID_PERSONA
    ok &= check("(E-7) cada niño obligatorio recibe exactamente una estrategia",
                all(sum(z.get((k, s), 0) for s in D.estrategias) == 1 for k in oblig))
    ok &= check(f"(E-5) SevEdu {rec['total']['SevEdu']:,.0f} <= (1 - rho_e) SevEdu_sin",
                rec["total"]["SevEdu"] <= (1 - D.esc["rho_e"]) * D.SevEdu_sin + 1e-6)
    ok &= check(f"H* = personas que salen recalculadas ({m.info['H_star']:,.0f})",
                abs(m.info["H_star"] - rec["total"]["personas_salen"]) < 1)

    print("3) Modelo 2")
    D2 = cargar_datos(P.escenario_m2())
    m2, est2, rec2 = modelo2.correr(D2, 0.10)
    ok &= check(f"m = 10 %: {est2['estado']}", est2["estado"] == "Optimal")
    num = rec2["total"]["M0"] * D2.Pob
    sumC = sum(v.value() for v in m2.C.values())
    ok &= check(f"(3) sum C_i ({sumC:,.1f}) >= numerador de M0 recalculado ({num:,.1f})", sumC >= num - 1e-4)
    num0 = D2.hog.assign(n=D2.hog.p * D2.hog.c0).groupby("zona").n.sum()
    ok &= check("(M-d) la meta se cumple en cada zona recalculando desde x",
                all(rec2[d]["M0"] * D2.Pob_d[d] <= 0.9 * num0[d] + 1e-4 for d in num0.index))
    print("\nTODO OK" if ok else "\nFALLÓ ALGO")
    return ok


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
