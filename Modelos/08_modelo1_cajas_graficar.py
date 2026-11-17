"""Cajas y bigotes (antes/después) de cada escenario de data/processed/modelo1/sens/ (lo deja 08_modelo1_cajas_sens.py).
Cajas ponderadas por personas (p = FEX_C * PERSONAS). Puntaje final = c0 - pesos de las privaciones quitadas."""
import importlib.util, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RAIZ_M = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ_M))
import parametros as P
from utils_dane import OUT

spec = importlib.util.spec_from_file_location("cajas", RAIZ_M / "08_modelo1_cajas.py")
cajas_mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(cajas_mod)
caja = cajas_mod.caja
SENS = OUT / "modelo1" / "sens"
ORDEN = ["base", "p_050", "p_075", "con_E3", "sin_E7", "desempleo_imputado", "ti_psicosocial",
         "acueducto_bid", "rho_codo", "sin_penalizaciones"]


def final_por_hogar(nombre, hog):
    plan = pd.read_csv(SENS / f"{nombre}_plan_hogar.csv")
    plan["ID_HOGAR"] = plan.ID_HOGAR.astype(str)
    d = plan.merge(hog[["ID_HOGAR", "c0"]], on="ID_HOGAR")
    q = d.quitadas.fillna("").map(lambda s: sum(P.PESOS[j] for j in s.split(",") if j))
    d["final"] = np.round(d.c0 - q, 2)
    d["sale_rec"] = d.final < P.K - 1e-9
    assert (d.sale_rec.astype(int) == d.sale).all(), nombre
    return d


def main():
    hog = pd.read_csv(OUT / "hogares_antioquia.csv"); hog["ID_HOGAR"] = hog.ID_HOGAR.astype(str)
    hog["c0"] = np.round(hog[P.INDICADORES].to_numpy() @ np.array([P.PESOS[j] for j in P.INDICADORES]), 2)
    resumen = pd.read_csv(SENS / "resumen_sens.csv").set_index("escenario")
    filas = []
    fig, ejes = plt.subplots(2, 5, figsize=(20, 9), sharey=True)
    for ax, n in zip(ejes.ravel(), ORDEN):
        d = final_por_hogar(n, hog)
        sigue = d[~d.sale_rec]
        cs = [caja(d.c0, d.p, "Antes"), caja(d.final, d.p, "Después\n(todos)"), caja(sigue.final, sigue.p, "Después\n(siguen\npobres)")]
        ax.bxp(cs, showfliers=False, patch_artist=True, boxprops=dict(facecolor="#9ecae1"),
               medianprops=dict(color="#08306b", linewidth=2))
        ax.axhline(0.335, color="crimson", linestyle="--", linewidth=1)
        ax.set_title(f"{n}\nsalen {resumen.at[n, 'salen_personas']:,.0f} ({d.p[d.sale_rec].sum() / d.p.sum():.1%})", fontsize=10)
        ax.grid(axis="y", alpha=0.3)
        for zona, zn in [(None, "Total")] + list(P.ZONAS.items()):
            s = d if zona is None else d[d.P3 == zona]
            sg = s[~s.sale_rec]
            for etiqueta, x, w in [("Antes", s.c0, s.p), ("Después (todos)", s.final, s.p), ("Después (siguen pobres)", sg.final, sg.p)]:
                c = caja(x, w, etiqueta)
                filas.append({"escenario": n, "zona": zn, "caja": etiqueta, "bigote_inf": c["whislo"], "Q1": c["q1"],
                              "mediana": c["med"], "Q3": c["q3"], "bigote_sup": c["whishi"]})
    ejes[0, 0].set_ylabel("Puntaje de privación"); ejes[1, 0].set_ylabel("Puntaje de privación")
    fig.suptitle("Modelo 1, B = $424 mil millones: puntaje de los pobres antes y después, por escenario (cajas por personas; línea roja = umbral de pobreza)")
    fig.tight_layout()
    fig.savefig(OUT / "modelo1" / "cajas_sensibilidades.png", dpi=130)
    t = pd.DataFrame(filas); t.to_csv(OUT / "modelo1" / "cajas_sensibilidades.csv", index=False)
    print(t[t.zona == "Total"].round(2).to_string(index=False))
    print(resumen.round(4).T.to_string())


main()
