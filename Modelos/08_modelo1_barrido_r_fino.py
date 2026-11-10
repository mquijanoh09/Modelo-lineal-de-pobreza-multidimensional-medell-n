"""
08_modelo1_barrido_r_fino.py -- Barrido fino de r (9-nov, pedido de Martin) para hallar el codo de H contra r.

r de 0.15 a 0.30 de a 0.01, con tres presupuestos bajos (donde la equidad si actua):
1.2 x B_min, $130 y $187 mil millones. Para cada B: H, % de pobres que sale por zona, costo de la
equidad respecto a r = 0 y el codo (Kneedle) de H contra r sobre los puntos factibles.
Salida: pantalla + data/processed/modelo1/barrido_r_fino.csv
Uso (desde Modelos):  python 08_modelo1_barrido_r_fino.py
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parametros as P
from datos_modelo import cargar_datos
from Modelo_1.modelo1 import rango_B, resolver_dos_etapas
from utils_dane import OUT

R_FINO = [0.0] + [round(x, 2) for x in np.arange(0.15, 0.3001, 0.01)]


def codo_decreciente(x, y):
    """Punto de mayor distancia sobre la cuerda que une el primero y el ultimo (Kneedle simplificado)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    xn, yn = (x - x.min()) / (x.max() - x.min()), (y - y.min()) / (y.max() - y.min())
    return int(np.argmax(yn - (1 - xn)))


def main():
    d = cargar_datos()
    rho_e = d.esc["rho_e"]
    B_min = rango_B(d, rho_e)["B_min"]
    filas = []
    for B in (1.2 * B_min, 130e9, 187e9):
        for r in R_FINO:
            m, info = resolver_dos_etapas(d, B, r=r, rho_e=rho_e)
            e2 = info["etapa2"]
            fila = {"B_mil_millones": round(B / 1e9, 1), "r": r, "estado": (e2 or info["etapa1"])["estado"]}
            if e2 is not None and e2["estado"] == "Optimal":
                rec = m.recalcular()
                fila["salen_personas"] = rec.at["total", "salen_personas"]
                for z, nombre in P.ZONAS.items():
                    fila[f"sale_{nombre}"] = rec.at[nombre, "salen_personas"] / d.pobres_zona[z]
            filas.append(fila)
            print(fila, flush=True)
    df = pd.DataFrame(filas)
    out = OUT / "modelo1"
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "barrido_r_fino.csv", index=False)
    print("\nCodo de H contra r (puntos factibles):")
    for B, g in df.groupby("B_mil_millones"):
        ok = g[g.estado == "Optimal"]
        k = codo_decreciente(ok.r, ok.salen_personas)
        h0 = ok.salen_personas.iloc[0]
        f = ok.iloc[k]
        print(f"  B = {B}: codo en r = {f.r:.2f} (H = {f.salen_personas:,.0f}, cuesta {h0 - f.salen_personas:,.0f} personas); "
              f"r factible maximo = {ok.r.max():.2f}")
    print(f"\nGuardado en {out}")


if __name__ == "__main__":
    main()
