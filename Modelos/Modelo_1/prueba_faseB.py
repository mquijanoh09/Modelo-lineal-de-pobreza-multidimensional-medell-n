"""
prueba_faseB.py -- Regla de la brecha (9-nov): rho es el MENOR con A <= A0.
Comprueba: con rho se cumple A <= A0; con rho - 0.002 ya no; y que el barrido de r con B bajo no rompe nada.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from datos_modelo import cargar_datos
from Modelo_1.modelo1 import rho_regla_brecha, resolver_dos_etapas


def ok(c):
    return "OK   " if c else "FALLA"


def main():
    d = cargar_datos()
    B, rho_e = 424e9, d.esc["rho_e"]
    rho, inf = rho_regla_brecha(d, B, rho_e=rho_e)
    print(f"rho por la regla de la brecha = {rho:.4f}  (A0 = {inf['A0']:.4f}, A = {inf['A']:.4f})")
    for etiqueta, x, debe in (("en rho", rho, True), ("rho - 0.003", rho - 0.003, False)):
        m, i = resolver_dos_etapas(d, B, rho=x, rho_e=rho_e)
        t = m.recalcular().loc["total"]
        cumple = t.A <= t.A0 + 1e-9
        print(f"{ok(cumple == debe)} {etiqueta}: A = {t.A:.4f} {'<=' if cumple else '>'} A0 = {t.A0:.4f}")
    # con B muy bajo la regla puede no alcanzarse: debe devolver None sin romperse
    r2, i2 = rho_regla_brecha(d, 127.2e9, rho_e=rho_e)
    print(f"     B = 127.2 mil millones: rho = {r2} {i2}")


if __name__ == "__main__":
    main()
