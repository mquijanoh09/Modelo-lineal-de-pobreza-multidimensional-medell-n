"""
prueba_3_5b5.py  --  Capa 5 del Modelo 1 (dos etapas, D1) contra enumeración.

Misma instancia y mismas opciones por hogar que la prueba de severidad (3.5b-3). Exacto sin MILP:
  1) H_max = mayor H con presupuesto (y techo de severidad, si hay rho);
  2) entre los planes con H >= H_max (1 - 1e-6), la menor severidad.
El MILP en dos etapas debe dar el mismo H y la misma severidad mínima. También se muestra
que la etapa 1 sola puede dejar una severidad mayor (el desempate sí hace algo).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # ...\Modelos

import parametros as P
from datos_modelo import cargar_datos
from Modelo_1.modelo1 import Modelo1, resolver_dos_etapas
from Modelo_1.prueba_3_5b3 import instancia, opciones, salida_minima


def enumeracion(s, B, rho):
    techo = np.inf if rho is None else (1 - rho) * s.Sev0
    ops = []
    for i in s.hogares.index:
        p = s.hogares.at[i, "p"]
        o = opciones(s, i)
        ops.append(np.array([(c, p * sc * sc, p if sc <= P.K_GRID + 1e-9 else 0.0) for sc, c in o.items()]))
    min_c = [o[:, 0].min() for o in ops]
    resto_c = np.cumsum(min_c[::-1])[::-1].tolist() + [0]
    est = np.zeros((1, 3))
    for n, o in enumerate(ops):
        est = (est[:, None, :] + o[None, :, :]).reshape(-1, 3)
        est = est[est[:, 0] + resto_c[n + 1] <= B + 1e-6]
    est = est[est[:, 1] <= techo + 1e-6]
    if len(est) == 0:
        return None, None
    H = est[:, 2].max()
    cand = est[est[:, 2] >= H * (1 - 1e-6)]
    return H, cand[:, 1].min()


def severidad_real(m):
    d = m.datos
    return float(sum(d.hogares.at[i, "p"] * m.s[i].value() ** 2 for i in d.hogares.index))


def main():
    d = cargar_datos()
    todo_ok = True
    hubo_desempate = False
    print(f"{'semilla':>7}{'rho':>6}{'B (mil mill.)':>15}{'H etapa 2':>12}{'H exacto':>12}{'Sev etapa 2':>14}{'Sev exacta':>12}{'Sev etapa 1':>13}  resultado")
    for semilla in (1, 2, 3):
        s = instancia(d, semilla)
        total = sum(salida_minima(s, i) for i in s.hogares.index)
        for rho, frac in ((None, 0.3), (None, 0.6), (0.0, 0.6), (0.3, 0.6), (0.4, 1.0)):
            B = frac * total
            m2, info = resolver_dos_etapas(s, B, rho=rho, gap_rel=1e-9, time_limit=60)
            H_ex, sev_ex = enumeracion(s, B, rho)
            if info["etapa2"] is None or info["etapa2"]["estado"] != "Optimal":
                ok = H_ex is None
                print(f"{semilla:>7}{str(rho):>6}{B / 1e9:>15,.1f}{'infactible':>12}{'infactible' if ok else H_ex:>12}  {'OK' if ok else 'FALLA'}")
                todo_ok &= ok
                continue
            H2 = sum(s.hogares.at[i, "p"] * round(m2.y[i].value()) for i in m2.y)
            sev2 = severidad_real(m2)
            # severidad que deja la etapa 1 sola (sin desempate)
            m1 = Modelo1(s, B, rho=rho).construir()
            m1.resolver(gap_rel=1e-9, time_limit=60)
            sev1 = severidad_real(m1)
            ok = (H_ex is not None and abs(H2 - H_ex) < 1e-4 * H_ex and abs(sev2 - sev_ex) < 1e-4 * max(sev_ex, 1)
                  and sev2 <= sev1 + 1e-6)
            hubo_desempate |= sev1 > sev2 + 1e-6
            todo_ok &= ok
            print(f"{semilla:>7}{str(rho):>6}{B / 1e9:>15,.1f}{H2:>12,.1f}{H_ex:>12,.1f}{sev2:>14,.1f}{sev_ex:>12,.1f}{sev1:>13,.1f}  {'OK' if ok else 'FALLA'}")
    print(f"\nEl desempate redujo la severidad respecto a la etapa 1 sola en algún caso: {'sí' if hubo_desempate else 'NO (la prueba no discrimina)'}")
    print("CAPA 5:", "OK en todas las instancias" if todo_ok and hubo_desempate else "HAY FALLAS")


if __name__ == "__main__":
    main()
