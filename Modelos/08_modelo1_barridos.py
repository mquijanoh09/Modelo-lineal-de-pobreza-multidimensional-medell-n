"""
08_modelo1_barridos.py  --  Barridos del Modelo 1 (formulación §7: cómo se escogen B, rho, r y rho_e).

Qué barre (cada fila = una corrida completa en dos etapas con los 523 hogares):
  1. B       : MALLA de presupuestos entre B_min y B_max (rango_B), sin equidad ni techo de severidad.
  2. rho     : de 0 al máximo posible con B_REF (frontera H vs severidad) + el codo (Kneedle).
  3. r       : parametros.MALLA_R (+ EXTRA_R) con B_REF.
  4. rho_e   : parametros.MALLA_RHO_E (+ EXTRA_RHO_E) con B_REF.
  5. sensibilidades de parametros.SENSIBILIDADES con B_REF (u_1 todavía no está programada).

Uso (desde Modelos):
    python 08_modelo1_barridos.py                  # todo, B_REF = punto medio del rango
    python 08_modelo1_barridos.py --B-ref 300      # B_REF en MIL MILLONES de pesos
    python 08_modelo1_barridos.py --solo B rho     # solo algunos barridos
Salida: pantalla + CSV en data/processed/modelo1/ (barrido_B.csv, barrido_rho.csv, ...).
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parametros as P
from datos_modelo import cargar_datos
from Modelo_1.modelo1 import Modelo1, rango_B, resolver_dos_etapas, resolver_r, rho_regla_brecha
from utils_dane import OUT

SALIDA = OUT / "modelo1"
N_B = 8                      # puntos de la malla de B
N_RHO = 9                    # puntos del barrido de rho
EXTRA_R = [0.25, 0.30, 0.50]                     # MALLA_R (hasta 20 %) no muerde con B de referencia: se prolonga
B_BAJOS = [None, 130e9, 187e9]                   # H3: presupuestos del tercio bajo donde r sí muerde (None = 1.2 x B_min)
EXTRA_RHO_E = [0.17, 0.20, 0.21, 0.22]           # para ver dónde se vuelve infactible rho_e sin E3


def corrida(d, B, r=0.0, rho=None, rho_e=None, gap=1e-6, tiempo=300, **etiquetas):
    """Una corrida en dos etapas y su recálculo independiente. Devuelve un dict (una fila)."""
    t0 = time.time()
    m, info = resolver_dos_etapas(d, B, r=r, rho=rho, rho_e=rho_e, gap_rel=gap, time_limit=tiempo)
    fila = {**etiquetas, "B_mil_millones": B / 1e9, "r": r, "rho": rho, "rho_e": rho_e}
    e2 = info["etapa2"]
    if e2 is None or e2["estado"] != "Optimal":
        fila.update(estado=(e2 or info["etapa1"])["estado"])
        return fila
    t = m.recalcular().loc["total"]
    fila.update(estado="Optimal", salen_personas=t.salen_personas, salen_hogares=int(t.salen_hogares),
                H=t.H, reduccion_M0=t.reduccion_M0,
                reduccion_severidad=1 - t.severidad / t.severidad_inicial,
                reduccion_sevedu=1 - t.sevedu / t.sevedu_inicial, A0=t.A0, A=t.A,
                brecha_no_crece=bool(t.A <= t.A0 + 1e-9), costo_mil_millones=t.costo / 1e9,
                segundos=round(time.time() - t0, 1))
    zonas = m.recalcular()
    for z, nombre in P.ZONAS.items():
        fila[f"sale_{nombre}"] = zonas.at[nombre, "salen_personas"] / m.datos.pobres_zona[z]
    return fila


def rho_maximo(d, B, rho_e, r=0.0):
    """Mayor reducción de severidad posible con el presupuesto B: min severidad sin exigir H."""
    m = Modelo1(d, B, r=r, rho_e=rho_e, etapa=2, H_star=0.0).construir()
    info = m.resolver(gap_rel=1e-6, time_limit=300)
    if info["estado"] != "Optimal":
        return None
    return 1 - info["objetivo"] / d.Sev0


def codo(x, y):
    """Codo (Kneedle simplificado) de una curva decreciente y(x): mayor brecha sobre la cuerda."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or x.max() == x.min() or y.max() == y.min():
        return None
    xn, yn = (x - x.min()) / (x.max() - x.min()), (y - y.min()) / (y.max() - y.min())
    return int(np.argmax(yn - (1 - xn)))


def rho_codo(d, B, rho_e, gap, tiempo, r=0.0):
    """rho del codo (Kneedle) de la curva H vs severidad, con la misma malla que el barrido de rho. None si no hay codo."""
    rmax = rho_maximo(d, B, rho_e, r)
    if rmax is None:
        return None
    libre = corrida(d, B, r=r, rho=0.0, rho_e=rho_e, gap=gap, tiempo=tiempo)
    if libre["estado"] != "Optimal":
        return None
    grilla = np.linspace(libre["reduccion_severidad"], rmax * 0.995, N_RHO)
    df = pd.DataFrame([libre] + [corrida(d, B, r=r, rho=float(x), rho_e=rho_e, gap=gap, tiempo=tiempo) for x in grilla])
    ok = df[(df.estado == "Optimal") & (df.rho >= grilla[0] - 1e-9)]
    k = codo(ok.reduccion_severidad, ok.salen_personas)
    return None if k is None else float(ok.iloc[k].rho)


def mostrar(titulo, df, columnas):
    print("\n" + "=" * 100 + f"\n {titulo}\n" + "=" * 100)
    cols = [c for c in columnas if c in df.columns]
    with pd.option_context("display.width", 220, "display.max_columns", 30, "display.float_format", "{:,.3f}".format):
        print(df[cols].to_string(index=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--B-ref", type=float, default=None, help="B de referencia, en MIL MILLONES (por defecto el punto medio)")
    ap.add_argument("--solo", nargs="+", choices=["B", "rho", "r", "rho_e", "sens"], default=None)
    ap.add_argument("--gap", type=float, default=1e-6)
    ap.add_argument("--tiempo", type=float, default=300)
    a = ap.parse_args()
    hacer = set(a.solo or ["B", "rho", "r", "rho_e", "sens"])

    d = cargar_datos()
    rho_e = d.esc["rho_e"]
    rango = rango_B(d, rho_e)
    B_min, B_max = rango["B_min"], rango["B_max"]
    B_ref = a.B_ref * 1e9 if a.B_ref else (B_min + B_max) / 2
    print(f"Rango de B: ${B_min / 1e9:,.1f} a ${B_max / 1e9:,.1f} mil millones | H máximo {rango['H_max']:,.0f} | "
          f"B de referencia ${B_ref / 1e9:,.1f} mil millones | rho_e = {rho_e}")
    SALIDA.mkdir(parents=True, exist_ok=True)
    columnas = ["B_mil_millones", "r", "rho", "rho_e", "estado", "salen_personas", "salen_hogares", "reduccion_M0",
                "reduccion_severidad", "reduccion_sevedu", "A0", "A", "brecha_no_crece", "costo_mil_millones", "sale_Cabecera",
                "sale_Centro poblado", "sale_Rural disperso", "segundos"]
    kw = dict(gap=a.gap, tiempo=a.tiempo)

    if "B" in hacer:
        malla = np.linspace(B_min * 1.02, B_max, N_B)         # 2 % sobre B_min para no caer en el borde infactible
        df = pd.DataFrame([corrida(d, B, rho_e=rho_e, **kw) for B in malla])
        df.to_csv(SALIDA / "barrido_B.csv", index=False)
        mostrar("1. Barrido de B (sin equidad ni techo de severidad)", df, columnas)

    if "rho" in hacer:
        rmax = rho_maximo(d, B_ref, rho_e)
        if rmax is None:
            raise SystemExit("No se pudo calcular el rho máximo (¿tiempo insuficiente?): subir --tiempo.")
        print(f"\nMáxima reducción de severidad posible con B de referencia: {rmax:.1%}")
        kw_f = dict(gap=a.gap, tiempo=a.tiempo)
        libre = corrida(d, B_ref, rho=0.0, rho_e=rho_e, **kw_f)          # rho = 0: H puro con el mejor desempate
        rho_libre = libre["reduccion_severidad"]                        # severidad que se baja "gratis" al maximizar H
        print(f"Con H máximo ya se baja la severidad {rho_libre:.1%}: exigir menos que eso no cambia nada.")
        grilla = np.linspace(rho_libre, rmax * 0.995, N_RHO)
        filas = [libre] + [corrida(d, B_ref, rho=float(x), rho_e=rho_e, **kw_f) for x in grilla]
        df = pd.DataFrame(filas)
        df.to_csv(SALIDA / "barrido_rho.csv", index=False)
        mostrar("2. Barrido de rho: frontera H vs severidad (B de referencia)", df, columnas)
        ok = df[(df.estado == "Optimal") & (df.rho >= grilla[0] - 1e-9)]
        cumple = ok[ok.brecha_no_crece]
        if len(cumple):
            f = cumple.iloc[0]
            print(f"\nRegla de la brecha (A <= A0 = {f.A0:.4f}): se cumple desde rho = {f.rho:.1%} -> salen "
                  f"{f.salen_personas:,.0f} personas, A = {f.A:.4f}. (Criterio principal; el codo es el contraste.)")
        k = codo(ok.reduccion_severidad, ok.salen_personas)
        if k is not None:
            f = ok.iloc[k]
            print(f"\nCodo sugerido (Kneedle, tramo donde el techo ya muerde): rho = {f.rho:.1%} -> salen "
                  f"{f.salen_personas:,.0f} personas, severidad -{f.reduccion_severidad:.1%}. Es una sugerencia, la decisión es tuya.")

    if "r" in hacer:
        filas = []
        for Bb in [B_ref] + [1.2 * B_min if b is None else b for b in B_BAJOS]:
            filas += [corrida(d, Bb, r=r, rho_e=rho_e, **kw) for r in P.MALLA_R + EXTRA_R]
        df = pd.DataFrame(filas)
        df.to_csv(SALIDA / "barrido_r.csv", index=False)
        mostrar("3. Barrido de r: equidad por zona (B de referencia y tres B bajos)", df, columnas)
        # costo de la equidad: caída de H respecto a r = 0 con el mismo B
        for Bb, g in df.groupby("B_mil_millones"):
            base = g[(g.r == 0) & (g.estado == "Optimal")]
            if base.empty:
                continue
            h0 = base.salen_personas.iloc[0]
            for _, f in g[(g.estado == "Optimal") & (g.r > 0)].iterrows():
                if h0 - f.salen_personas >= 1:
                    print(f"  B={Bb:,.0f}: r={f.r:.2f} cuesta {h0 - f.salen_personas:,.0f} personas ({1 - f.salen_personas / h0:.2%})")

    if "rho_e" in hacer:
        df = pd.DataFrame([corrida(d, B_ref, rho_e=x, **kw) for x in P.MALLA_RHO_E + EXTRA_RHO_E])
        df.to_csv(SALIDA / "barrido_rho_e.csv", index=False)
        mostrar("4. Barrido de rho_e: techo de SevEdu (B de referencia)", df, columnas)

    if "sens" in hacer:
        # El caso base usa rho = regla de la brecha (9-nov). Cada sensibilidad de datos recalcula su propio rho.
        def con_brecha(ds, nombre):
            r_b, _ = resolver_r(ds, B_ref, ds.esc["r"], rho_e=ds.esc["rho_e"], gap_rel=a.gap, time_limit=a.tiempo)
            rho_b, inf = rho_regla_brecha(ds, B_ref, r=r_b, rho_e=ds.esc["rho_e"], gap_rel=a.gap, time_limit=a.tiempo)
            f = corrida(ds, B_ref, r=r_b, rho=rho_b, rho_e=ds.esc["rho_e"], sensibilidad=nombre, **kw)
            f["rho_regla"] = rho_b
            return f
        filas = [con_brecha(d, "base")]
        for nombre in P.SENSIBILIDADES:
            try:
                ds = cargar_datos(nombre)
            except NotImplementedError as e:
                print(f"\n(sensibilidad {nombre} omitida: {e})")
                continue
            filas.append(con_brecha(ds, nombre))
        # sensibilidades de politica (mismos datos del caso base)
        for nombre, pol in P.POLITICAS.items():
            re_ = pol.get("rho_e", rho_e) if "rho_e" in pol else rho_e
            rho_p = pol["rho"]
            r_p, _ = resolver_r(d, B_ref, pol.get("r", d.esc["r"]), rho_e=re_, gap_rel=a.gap, time_limit=a.tiempo)
            if rho_p == "codo":
                rho_p = rho_codo(d, B_ref, re_, a.gap, a.tiempo, r_p)
            f = corrida(d, B_ref, r=r_p, rho=rho_p, rho_e=re_, sensibilidad=nombre, **kw)
            f["rho_regla"] = rho_p
            filas.append(f)
        df = pd.DataFrame(filas)
        df.to_csv(SALIDA / "barrido_sensibilidades.csv", index=False)
        mostrar("5. Sensibilidades (B de referencia; base = rho por regla de la brecha)", df, ["sensibilidad"] + columnas)

    print(f"\nGuardado en {SALIDA}")


if __name__ == "__main__":
    main()
