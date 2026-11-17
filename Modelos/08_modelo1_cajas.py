"""Diagrama de caja y bigotes: puntaje de privación de los hogares pobres, antes y después de la intervención.

Lee la corrida guardada por 08_modelo1.py (data/processed/modelo1/plan_hogar.csv) y NO resuelve el MILP.
Puntaje final del hogar = puntaje inicial - suma de los pesos w_j de las privaciones quitadas (columna
`quitadas`), la misma cuenta de ModeloIPMBase.recalcular. Cada hogar pesa por sus personas (p = FEX_C * PERSONAS),
así que las cajas describen a las personas, no a los 523 hogares de la muestra.
Uso: .venv\\Scripts\\python.exe Modelos\\08_modelo1_cajas.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import parametros as P
from utils_dane import OUT

SALIDA = OUT / "modelo1"


def cuantil_ponderado(x, w, q):
    """Cuantil q (0-1) de x donde cada valor cuenta w veces (personas)."""
    o = np.argsort(x)
    x, w = np.asarray(x)[o], np.asarray(w)[o]
    acum = (np.cumsum(w) - 0.5 * w) / w.sum()
    return float(np.interp(q, acum, x))


def caja(x, w, etiqueta):
    q1, med, q3 = (cuantil_ponderado(x, w, q) for q in (0.25, 0.5, 0.75))
    iqr = q3 - q1
    x = np.asarray(x)
    dentro = x[(x >= q1 - 1.5 * iqr) & (x <= q3 + 1.5 * iqr)]
    return {"label": etiqueta, "q1": q1, "med": med, "q3": q3,
            "whislo": dentro.min(), "whishi": dentro.max(), "fliers": []}


def main():
    hog = pd.read_csv(OUT / "hogares_antioquia.csv")
    hog["ID_HOGAR"] = hog.ID_HOGAR.astype(str)
    plan = pd.read_csv(SALIDA / "plan_hogar.csv")
    plan["ID_HOGAR"] = plan.ID_HOGAR.astype(str)
    w = np.array([P.PESOS[j] for j in P.INDICADORES])
    hog["c0"] = np.round(hog[P.INDICADORES].to_numpy() @ w, 2)

    d = plan.merge(hog[["ID_HOGAR", "c0"]], on="ID_HOGAR", how="left")
    quita = d.quitadas.fillna("").map(lambda s: sum(P.PESOS[j] for j in s.split(",") if j))
    d["final"] = np.round(d.c0 - quita, 2)
    d["sale_rec"] = d.final < P.K - 1e-9
    assert (d.sale_rec.astype(int) == d.sale).all(), "El puntaje recalculado no coincide con 'sale' del plan"
    print(f"Hogares pobres: {len(d)} | salen (personas): {(d.p * d.sale_rec).sum():,.0f} | "
          f"puntaje final recalculado coincide con el modelo: OK")

    paneles = [("Antioquia (total)", pd.Series(True, index=d.index))] + \
              [(nombre, d.P3 == z) for z, nombre in P.ZONAS.items()]
    fig, ejes = plt.subplots(1, 4, figsize=(15, 5.5), sharey=True)
    filas = []
    for ax, (titulo, m) in zip(ejes, paneles):
        s = d[m]
        sigue = s[~s.sale_rec]
        cajas = [caja(s.c0, s.p, "Antes\n(todos)"),
                 caja(s.final, s.p, "Después\n(todos)"),
                 caja(sigue.final, sigue.p, "Después\n(siguen\npobres)")]
        ax.bxp(cajas, showfliers=False, patch_artist=True,
               boxprops=dict(facecolor="#9ecae1"), medianprops=dict(color="#08306b", linewidth=2))
        ax.axhline(0.335, color="crimson", linestyle="--", linewidth=1)
        ax.set_title(f"{titulo}\nsalen {s.p[s.sale_rec].sum() / s.p.sum():.1%} de los pobres", fontsize=10)
        ax.tick_params(axis="x", labelsize=8)
        ax.grid(axis="y", alpha=0.3)
        for c in cajas:
            filas.append({"panel": titulo, "caja": c["label"].replace("\n", " "), **{k: c[k] for k in ("whislo", "q1", "med", "q3", "whishi")}})
    ejes[0].set_ylabel("Puntaje de privación (pobre si >= 0.34)")
    ejes[-1].text(1.02, 0.335, "pobre si\n>= 0.34", color="crimson", transform=ejes[-1].get_yaxis_transform(), va="center", fontsize=8)
    fig.suptitle("Modelo 1: puntaje de privación de los hogares pobres antes y después de la intervención "
                 "(cajas ponderadas por personas)", fontsize=11)
    fig.tight_layout()
    fig.savefig(SALIDA / "cajas_antes_despues.png", dpi=150)
    tabla = pd.DataFrame(filas)
    tabla.to_csv(SALIDA / "cajas_antes_despues.csv", index=False)
    pd.set_option("display.width", 200)
    print(tabla.round(2).to_string(index=False))
    print(f"\nGuardado en {SALIDA}")


if __name__ == "__main__":
    main()
