"""
prueba_3_5b4.py  --  Capa 4 del Modelo 1 (techo de SevEdu) contra enumeración.

Instancia: hogares con niños que pueden recibir E1 o E2. Se dejan quitables las privaciones
simples (para que haya H) y NO las educativas, de modo que la educación afecta al modelo solo
por tres vías: la cobertura obligatoria E-7, el gasto (cupo/ciclo + Renta Ciudadana una vez por
hogar) y el techo de SevEdu. Exacto sin MILP:
   1) por hogar se enumeran las opciones de sus niños (nada, E1, E2) respetando E-7;
   2) se combinan los hogares y se guardan los planes con SevEdu suficiente;
   3) para cada plan, lo que sobra del presupuesto se gasta en sacar hogares (mochila, con
      costos redondeados arriba/abajo = cotas inferior/superior de H).
"""
import itertools
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # ...\Modelos

import parametros as P
from datos_modelo import cargar_datos, subconjunto, INDICADORES_SIMPLES
from Modelo_1.modelo1 import Modelo1
from Modelo_1.prueba_3_5b1 import costo_minimo_de_salir, ESCALA

N_HOGARES = 8


def instancia(d, semilla):
    rng = np.random.default_rng(semilla)
    con_nino = sorted({d.ninos.at[k, "hogar"] for k, ss in d.S_k.items() if ss and k in d.K})
    ids = list(rng.choice(con_nino, size=min(N_HOGARES, len(con_nino)), replace=False))
    s = subconjunto(d, ids)
    for (i, j) in list(s.quitable):
        if j not in INDICADORES_SIMPLES:
            s.quitable[(i, j)] = False
    return s


def planes_hogar(s, i):
    """Lista de (costo, coef) de las combinaciones de estrategias de los niños del hogar i."""
    ninos = [k for k in s.S_k if s.ninos.at[k, "hogar"] == i and s.S_k[k]]
    opc = [[None] + s.S_k[k] for k in ninos]
    planes = []
    for combo in itertools.product(*opc):
        if any(k in s.obligatorios and e is None for k, e in zip(ninos, combo)):
            continue
        costo = sum(s.c_ks[(k, e)] for k, e in zip(ninos, combo) if e)
        if any(e == "E1" for e in combo):
            costo += s.C_RC[i]
        coef = sum(s.coef_ks[(k, e)] for k, e in zip(ninos, combo) if e)
        planes.append((costo, coef))
    return planes


def dp_mochila(items, cap, redondeo):
    f = np.ceil if redondeo == "arriba" else np.floor
    dp = np.zeros(cap + 1)
    for costo, p in items:
        w = int(f(costo / ESCALA))
        if 0 < w <= cap:
            dp[w:] = np.maximum(dp[w:], dp[:cap + 1 - w] + p)
        elif w == 0:
            dp += p
    return dp


def cotas(s, B, rho_e):
    ids = list(s.hogares.index)
    items = []
    for i in ids:
        c = costo_minimo_de_salir(s, i)
        if c is not None:
            items.append((c, float(s.hogares.at[i, "p"])))
    # combinar los planes educativos de los hogares con poda por presupuesto
    est = np.zeros((1, 2))
    for i in ids:
        pl = np.array(planes_hogar(s, i))
        est = (est[:, None, :] + pl[None, :, :]).reshape(-1, 2)
        est = est[est[:, 0] <= B + 1e-6]
        if len(est) == 0:
            return None, None
    est = est[est[:, 1] >= rho_e * s.sevedu_sin - 1e-9]
    if len(est) == 0:
        return None, None
    cap_max = int(np.ceil(B / ESCALA))
    dp_lo, dp_hi = dp_mochila(items, cap_max, "arriba"), dp_mochila(items, cap_max, "abajo")
    resto = B - est[:, 0]
    lo = dp_lo[np.floor(resto / ESCALA).astype(int)].max()
    hi = dp_hi[np.minimum(np.ceil(resto / ESCALA).astype(int), cap_max)].max()
    return lo, hi


def main():
    d = cargar_datos()
    todo_ok = True
    print(f"{'semilla':>7}{'rho_e':>7}{'B (mil mill.)':>15}{'MILP':>14}{'cota inf':>12}{'cota sup':>12}  resultado")
    for semilla in (1, 2, 3):
        s = instancia(d, semilla)
        c_edu_forzado = sum(min(p[0] for p in planes_hogar(s, i)) for i in s.hogares.index)
        total_salir = sum(c for c in (costo_minimo_de_salir(s, i) for i in s.hogares.index) if c is not None)
        for rho_e, frac in ((0.0, 0.5), (0.1, 0.5), (0.2, 0.5), (0.3, 0.5), (0.4, 0.5), (0.0, 1.0), (0.2, 1.0), (0.3, 1.0), (0.9, 1.0)):
            B = c_edu_forzado + frac * total_salir
            m = Modelo1(s, B, rho_e=rho_e).construir()
            info = m.resolver(gap_rel=1e-9, time_limit=60)
            milp = info["objetivo"] if info["estado"] == "Optimal" else None
            lo, hi = cotas(s, B, rho_e)
            if milp is None:
                ok = lo is None
            else:
                ok = lo is not None and lo - 1e-6 <= milp <= hi + 1e-6
            todo_ok &= ok
            f = lambda v: "infactible" if v is None else f"{v:,.1f}"
            print(f"{semilla:>7}{rho_e:>7}{B / 1e9:>15,.1f}{f(milp):>14}{f(lo):>12}{f(hi):>12}  {'OK' if ok else 'FALLA'}  [{info['estado']}]")
    print("\nCAPA 4:", "OK en todas las instancias" if todo_ok else "HAY FALLAS")


if __name__ == "__main__":
    main()
