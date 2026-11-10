"""
prueba_faseA.py  --  Auditoría H1 y H2 (7-nov): estado del solver y gap por defecto.

H1: una corrida cortada por tiempo NO puede reportarse como "Optimal", y la etapa 2 no debe
    recibir un H* sin demostrar.
H2: con el gap por defecto (1e-6), pedir una equidad que no muerde (r = 0.05) no debe cambiar H
    respecto a r = 0 (con gap 1e-4 daba una diferencia de ~31 personas que era solo ruido).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # ...\Modelos

from datos_modelo import cargar_datos
from modelo_base import ModeloIPMBase
from Modelo_1.modelo1 import Modelo1, resolver_dos_etapas


def ok(c):
    return "OK   " if c else "FALLA"


def main():
    d = cargar_datos()
    B = 384.2e9
    print(f"{ok(ModeloIPMBase.GAP_REL == 1e-6)} gap por defecto de la clase madre: {ModeloIPMBase.GAP_REL}")

    # H1: límite de tiempo muy corto con un problema difícil (rho alto)
    m = Modelo1(d, B, rho=0.47, rho_e=0.14).construir()
    info = m.resolver(time_limit=1)
    print(f"{ok(info['estado'] == 'Cortado')} corrida con 1 s de límite: estado = {info['estado']}, gap = {info['gap']}")
    m2, info2 = resolver_dos_etapas(d, B, rho=0.47, rho_e=0.14, time_limit=1)
    print(f"{ok(info2['etapa2'] is None and info2['H_star'] is None)} dos etapas cortadas: no pasa H* a la etapa 2 (etapa 2 = {info2['etapa2']})")

    # el caso normal sigue siendo óptimo
    info = Modelo1(d, B, rho_e=0.14).construir().resolver(time_limit=120)
    print(f"{ok(info['estado'] == 'Optimal')} corrida normal: estado = {info['estado']}, gap = {info['gap']:.2e}")

    # H2: r que no muerde no cambia H
    H = []
    for r in (0.0, 0.05, 0.5):
        mm, ii = resolver_dos_etapas(d, B, r=r, rho_e=0.14, time_limit=120)
        H.append(mm.recalcular().at["total", "salen_personas"])
    print(f"{ok(max(H) - min(H) < 1)} H con r = 0, 0.05 y 0.5 (no muerde): " + ", ".join(f"{h:,.1f}" for h in H))


if __name__ == "__main__":
    main()
