"""
10_cajas_modelo2.py  --  Diagramas de caja y bigotes del puntaje de privación de los hogares pobres,
antes y después de la intervención del Modelo 2 (caso base, metas 5, 10 y 20 %).

Qué dibuja: para los 523 hogares pobres iniciales, el puntaje de privación c_i (0 a 1; pobre si >= 1/3).
Cada caja pondera por personas (p_i = HW_i * HS_i), así que representa a la población, no a la muestra.
  - caja: cuartiles 25 %, 50 % (mediana) y 75 %;  bigotes: último dato dentro de 1.5 x rango intercuartil;
  - rombo: promedio ponderado (con los pobres iniciales; los que salen cuentan con su nuevo puntaje < 1/3);
  - línea punteada: umbral de pobreza 1/3.
Salidas en Modelos/Modelo_2/resultados/graficos/: caja_<caso>.png (una por caso), estadisticas_cajas_casos.csv y resumen_cajas_casos.csv

Correr:  python Modelos/Modelo_2/10_cajas_modelo2.py     (necesita matplotlib)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pulp

import parametros as P
from datos_modelo import cargar_datos
from modelo2 import Modelo2
from modelo_base import _val

CARPETA = Path(__file__).resolve().parent / "resultados" / "graficos"
AZUL, NARANJA, GRIS, TEXTO, TEXTO2, FONDO = "#2a78d6", "#eb6834", "#a9a8a2", "#0b0b0b", "#52514e", "#fcfcfb"


def cuantil_ponderado(x, w, q):
    o = np.argsort(x)
    x, w = np.asarray(x)[o], np.asarray(w)[o]
    c = (np.cumsum(w) - 0.5 * w) / w.sum()
    return float(np.interp(q, c, x))


def estadisticas(x, w):
    q1, med, q3 = (cuantil_ponderado(x, w, q) for q in (0.25, 0.5, 0.75))
    iqr = q3 - q1
    dentro = np.asarray(x)[(np.asarray(x) >= q1 - 1.5 * iqr) & (np.asarray(x) <= q3 + 1.5 * iqr)]
    return {"q1": q1, "mediana": med, "q3": q3, "bigote_inf": float(dentro.min()), "bigote_sup": float(dentro.max()),
            "promedio": float(np.average(x, weights=w)), "minimo": float(np.min(x)), "maximo": float(np.max(x)),
            "pct_bajo_umbral": float(w[np.asarray(x) < P.K - 1e-9].sum() / w.sum())}


def puntaje_final(mod, d):
    """Puntaje de cada hogar pobre inicial después de intervenir (misma cuenta que recalcular())."""
    return pd.Series({i: round(d.hogares.at[i, "c0"] - sum(P.PESOS[j] for j in d.J[i] if _val(mod.x[(i, j)])), 2)
                      for i in d.hogares.index})


def graficar(d, esc, titulo, archivo, etiqueta):
    """Corre las metas 5, 10 y 20 % del escenario `esc` y dibuja las cajas. Devuelve la tabla de estadísticas."""
    h = d.hogares
    grupos = [("Antes", h.c0)]
    resumen = []
    for m in P.METAS_M2:
        mod = Modelo2(d, esc, meta_m=m).construir()
        mod.resolver(**P.SOLVER_M2)
        assert mod.info["estado"] == "Optimal", (etiqueta, m, mod.info)
        f = puntaje_final(mod, d)
        grupos.append((f"Meta {m:.0%}", f))
        t = mod.recalcular().loc["total"]
        resumen.append({"caso": etiqueta, "meta_m": m, "costo_mil_millones": pulp.value(mod.costo_total()) / 1e9,
                        "salen_hogares": t.salen_hogares, "salen_personas": t.salen_personas, "H": t.H, "A": t.A,
                        "A_inicial": d.linea_base[1], "reduccion_M0": t.reduccion_M0,
                        "reduccion_severidad": 1 - t.severidad / t.severidad_inicial})

    zonas = [("Antioquia (total)", None)] + [(P.ZONAS[z], z) for z in sorted(P.ZONAS)]
    filas = []
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": "#c9c8c2"})
    fig, axes = plt.subplots(1, 4, figsize=(15, 5.6), sharey=True, facecolor=FONDO)
    for ax, (nombre, z) in zip(axes, zonas):
        ax.set_facecolor(FONDO)
        sel = h.index if z is None else h.index[h.P3 == z]
        w = h.loc[sel, "p"].to_numpy()
        for pos, (etq, serie) in enumerate(grupos):
            x = serie.loc[sel].to_numpy()
            st = estadisticas(x, w)
            filas.append({"caso": etiqueta, "zona": nombre, "grupo": etq, **st})
            color = GRIS if etq == "Antes" else (AZUL if pos == 1 else NARANJA if pos == 2 else "#1baf7a")
            ax.bxp([{"med": st["mediana"], "q1": st["q1"], "q3": st["q3"], "whislo": st["bigote_inf"],
                     "whishi": st["bigote_sup"], "fliers": []}], positions=[pos], widths=0.55, showfliers=False,
                   patch_artist=True, boxprops=dict(facecolor=color, alpha=0.35, edgecolor=color, linewidth=1.2),
                   medianprops=dict(color=color, linewidth=2.2), whiskerprops=dict(color=color, linewidth=1.2),
                   capprops=dict(color=color, linewidth=1.2))
            ax.plot(pos, st["promedio"], marker="D", markersize=6, color=color, markeredgecolor=FONDO, markeredgewidth=1.5)
        ax.axhline(P.K, color=TEXTO2, linestyle=(0, (4, 3)), linewidth=1)
        ax.set_ylim(0.2, 0.7)
        ax.set_xticks(range(len(grupos)))
        ax.set_xticklabels([g[0] for g in grupos], fontsize=10, color=TEXTO2)
        ax.set_title(nombre, fontsize=12, color=TEXTO, loc="left", fontweight="bold")
        ax.grid(axis="y", color="#e7e6e1", linewidth=0.8); ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.tick_params(colors=TEXTO2)
    axes[0].set_ylabel("Puntaje de privación (0 a 1)", color=TEXTO2, fontsize=11)
    fig.suptitle(titulo, x=0.01, ha="left", fontsize=15, fontweight="bold", color=TEXTO)
    fig.text(0.01, 0.905, "Hogares pobres iniciales (523), ponderados por personas. Caja = cuartiles; línea gruesa = mediana; "
             "rombo = promedio; bigotes = 1.5 x rango intercuartil; línea punteada = umbral de pobreza (1/3).", fontsize=9.5, color=TEXTO2)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    CARPETA.mkdir(parents=True, exist_ok=True)
    fig.savefig(CARPETA / archivo, dpi=150, facecolor=FONDO)
    plt.close(fig)
    return pd.DataFrame(filas), pd.DataFrame(resumen)


# (clave, título, escenario común, opciones del M2, opciones extra)
CASOS = [
    ("base", "Caso base (p = 0.369, E-7, meta en cada zona)", "base", "base", {}),
    ("p050", "Sensibilidad: cumplimiento de Renta Ciudadana p = 0.50", "p_050", "base", {}),
    ("p075", "Sensibilidad: cumplimiento de Renta Ciudadana p = 0.75", "p_075", "base", {}),
    ("sevedu14", "Sensibilidad: SevEdu activa (rho_e = 14 %)", "base", "con_sevedu", {}),
    ("e3_sevedu20", "Sensibilidad: E3 + SevEdu (rho_e = 20 %)", "con_E3", "con_sevedu", {}),
    ("desempleo", "Sensibilidad: desempleo imputado quitable", "desempleo_imputado", "base", {}),
    ("meta_global", "Sensibilidad: meta solo global (con E-7)", "base", "meta_global", {}),
    ("sin_E7_global", "Versión comparable con M3/M4: sin E-7, meta global", "sin_E7", "meta_global", {}),
    ("severidad", "Escenario aparte: con techo de severidad (rho = meta)", "base", "base", {"usar_severidad": True, "rho_sev": None}),
]


def main():
    todas, resumenes = [], []
    for clave, titulo, comun, m2, extra in CASOS:
        d = cargar_datos(comun)
        esc = {**P.escenario_m2(comun, m2), **extra}
        est, res = graficar(d, esc, titulo, f"caja_{clave}.png", clave)
        todas.append(est); resumenes.append(res)
        print(f"{clave}: listo", flush=True)
    CARPETA.mkdir(parents=True, exist_ok=True)
    pd.concat(todas).to_csv(CARPETA / "estadisticas_cajas_casos.csv", index=False, encoding="utf-8-sig")
    pd.concat(resumenes).to_csv(CARPETA / "resumen_cajas_casos.csv", index=False, encoding="utf-8-sig")
    print(f"\nArchivos en {CARPETA}")


if __name__ == "__main__":
    main()
