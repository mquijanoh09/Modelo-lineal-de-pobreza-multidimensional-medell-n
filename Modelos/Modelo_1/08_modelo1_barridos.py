"""
08_modelo1_barridos.py  --  Barridos del Modelo 1 (formulacion_modelo1.md §7 e informe §8).

1. Curva B -> H, M0 y severidad, por zona          (B = B_piso + f (B_sat - B_piso); r = rho = 0)
2. Equidad: barrido de r entre 0 y r_max(B_ref)    (rho = 0)
3. Severidad: barrido de rho entre 0 y rho_max(B_ref) (r = 0). Se reporta el codo de la frontera
   H vs. severidad y la regla "la brecha de los que siguen pobres no crece" (A <= A0).
4. Sensibilidades de parametros.SENSIBILIDADES en B_ref (con el B_ref del caso base, en pesos).
Cada punto se resuelve en dos etapas (D1) y se recalcula desde x.
Resultados: Modelos/Modelo_1/resultados/m1_barrido_*.csv

Uso: python Modelos/Modelo_1/08_modelo1_barridos.py
"""
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # ...\Modelos
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd

import parametros as P
from datos_modelo import cargar_datos
from modelo1 import Modelo1, correr

m08 = importlib.import_module("08_modelo1")          # el nombre empieza por dígito
RES = m08.RES


def punto(D, B, r=0.0, rho=0.0, **extra):
    m, est, rec = correr(D, B=B, r=r, rho=rho)
    if rec is None:
        return [{**extra, "B": B, "r": r, "rho": rho, "estado": est["estado"], "zona": "Total"}]
    return [{**extra, "B": B, "r": r, "rho": rho, "estado": est["estado"], "gap": est["gap"], **f}
            for f in m08.filas(rec, {})]


def codo(xs, ys):
    """Punto de la frontera más lejano a la recta entre sus extremos (ejes normalizados)."""
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    if len(xs) < 3:
        return 0
    xn = (xs - xs.min()) / (np.ptp(xs) or 1)
    yn = (ys - ys.min()) / (np.ptp(ys) or 1)
    a, b = np.array([xn[0], yn[0]]), np.array([xn[-1], yn[-1]])
    u = b - a
    d = np.abs(u[0] * (yn - a[1]) - u[1] * (xn - a[0])) / (np.linalg.norm(u) or 1)
    return int(d.argmax())


def tot(rows):
    return pd.DataFrame([r for r in rows if r["zona"] == "Total"])


def main():
    D = cargar_datos()
    piso, H_max, B_sat = m08.rango_B(D)
    B_ref = m08.B_de(piso, B_sat, P.FRACCION_B_REF)
    A0 = float((D.hog.p * D.hog.c0).sum() / D.hog.p.sum())
    print(f"B_piso ${piso / 1e9:,.1f} mm · B_sat ${B_sat / 1e9:,.1f} mm · B_ref ${B_ref / 1e9:,.1f} mm · A0 = {A0:.2%}")

    # 1. Curva B -> H
    filas = []
    for f in P.FRACCIONES_B:
        filas += punto(D, m08.B_de(piso, B_sat, f), fraccion_B=f)
    pd.DataFrame(filas).to_csv(RES / "m1_barrido_B.csv", index=False)
    t = tot(filas)
    print("\n1) Curva B -> H (r = 0, rho = 0)")
    print(t[["fraccion_B", "B", "personas_salen", "H", "A", "M0", "severidad", "SevEdu"]].to_string(
        index=False, formatters={"B": lambda v: f"{v / 1e9:,.1f}", "H": "{:.2%}".format, "A": "{:.2%}".format}))

    # 2. Equidad r
    mr = Modelo1(D, B=B_ref, modo="r_max").construir()
    r_max = m08._ok(mr.resolver(), "r_max")
    filas = []
    for r in sorted({x for x in P.MALLA_R if x <= r_max} | {round(r_max - 1e-6, 6)}):
        filas += punto(D, B_ref, r=r)
    pd.DataFrame(filas).to_csv(RES / "m1_barrido_r.csv", index=False)
    print(f"\n2) Equidad por zona en B_ref: r_max = {r_max:.2%}")
    df = pd.DataFrame(filas)
    piv = df[df.zona != "Total"].pivot_table(index="r", columns="zona", values="personas_salen")
    print(pd.concat([tot(filas).set_index("r")[["personas_salen", "H", "A", "severidad"]], piv], axis=1).to_string(
        float_format=lambda v: f"{v:,.4f}" if v < 1 else f"{v:,.0f}"))

    # 3. Severidad rho
    ms = Modelo1(D, B=B_ref, modo="sev_min").construir()
    sev_min = m08._ok(ms.resolver(), "severidad mínima")
    rho_max = 1 - sev_min / D.Sev0
    rhos = list(np.round(np.linspace(0, rho_max - 1e-6, P.PASOS_RHO + 2), 6))
    filas = []
    for rho in rhos:
        filas += punto(D, B_ref, rho=rho)
    t = tot(filas)
    i_codo = codo(t.severidad, t.personas_salen)
    ok_brecha = t[t.A <= A0 + 1e-12]
    t["codo"] = False
    t.loc[t.index[i_codo], "codo"] = True
    pd.DataFrame(filas).to_csv(RES / "m1_barrido_rho.csv", index=False)
    print(f"\n3) Techo de severidad en B_ref: rho_max = {rho_max:.2%} (severidad mínima {sev_min:,.0f})")
    print(t[["rho", "personas_salen", "H", "A", "M0", "severidad", "codo"]].to_string(
        index=False, formatters={"H": "{:.2%}".format, "A": "{:.2%}".format}))
    print(f"   Codo de la frontera H vs. severidad: rho = {t.rho.iloc[i_codo]:.2%}")
    print("   Regla 'la brecha no crece' (A <= A0): " +
          (f"rho >= {ok_brecha.rho.min():.2%}" if len(ok_brecha) else "ningún rho de la malla la cumple"))

    # 4. Sensibilidades
    filas = punto(D, B_ref, escenario="base")
    for nombre in P.SENSIBILIDADES:
        Ds = cargar_datos(P.escenario(nombre))
        filas += [dict(f, escenario=nombre) for f in punto(Ds, B_ref)]
    pd.DataFrame(filas).to_csv(RES / "m1_sensibilidades.csv", index=False)
    print("\n4) Sensibilidades en B_ref (mismo B en pesos)")
    print(tot(filas)[["escenario", "estado", "personas_salen", "H", "M0", "severidad", "SevEdu", "costo"]].to_string(
        index=False, formatters={"H": "{:.2%}".format, "costo": lambda v: f"{v / 1e9:,.1f}"}))
    print(f"\nGuardado en {RES}")


if __name__ == "__main__":
    main()
