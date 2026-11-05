# -*- coding: utf-8 -*-
"""
m34_info_perfecta_comun.py — Referencia de INFORMACION PERFECTA del escenario comun (5-nov, bitacora §6.4).

Es el Modelo 2 de Martin (min costo s.a. meta de M0) con meta GLOBAL y sin E-7 ni SevEdu, en las mismas
metas del barrido de M3/M4. Asi el "precio de no tener informacion" = costo M3 (o M4) / costo M2, con la
misma tabla de costos y el mismo alcance; lo unico que cambia es la informacion.

Modo equidad: Modelo 1 de Martin (max personas que salen con presupuesto B, luego min severidad) sin E-7
ni SevEdu (rho_e = 0), en los mismos B que `m34_equidad_comun.py`.

No reimplementa nada: importa `modelo1.py`, `modelo2.py` y `datos_modelo.py` de Martin.
Uso: python3 m34_info_perfecta_comun.py <carpeta Modelos/ de Martin> [salida.csv]
     python3 m34_info_perfecta_comun.py <carpeta Modelos/ de Martin> --equidad <salida.csv> <B1> <B2> ...
"""
import sys
import time
import warnings
from pathlib import Path

warnings.simplefilter("ignore")
METAS = [round(0.02 * k, 2) for k in range(1, 16)]          # 2 %..30 %, como m34_barrido_metas_v2


def equidad(dm, salida, Bs):
    sys.path[:0] = [str(dm), str(dm / "Modelo_1")]
    import pandas as pd
    import parametros as P
    from datos_modelo import cargar_datos
    from modelo1 import Modelo1
    D1 = cargar_datos(dict(P.escenario(), cobertura_art67=False, rho_e=0.0))
    filas = []
    for B in Bs:
        t0 = time.time()
        m = Modelo1(D1, B=B * 1e9, rho_e=0.0).construir()
        e = m.resolver()
        r = m.recalcular()["total"]
        filas.append(dict(modelo="M1_info_perfecta", escenario="comun", B=B, estado=e["estado"], gap=e["gap"],
                          personas_salen=r["personas_salen"], costo_mm=r["costo"] / 1e9,
                          segundos=round(time.time() - t0, 1)))
        print(filas[-1], flush=True)
        Path(salida).parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(filas).to_csv(salida, index=False)


def main():
    dm = Path(sys.argv[1]).resolve()
    if len(sys.argv) > 2 and sys.argv[2] == "--equidad":
        return equidad(dm, sys.argv[3], [float(x) for x in sys.argv[4:]])
    salida = Path(sys.argv[2] if len(sys.argv) > 2 else "resultados/m34/info_perfecta_comun.csv")
    sys.path[:0] = [str(dm), str(dm / "Modelo_2")]
    import pandas as pd
    import parametros as P
    from datos_modelo import cargar_datos
    from modelo2 import Modelo2
    esc = P.escenario_m2("base", "meta_global")
    esc.update({"cobertura_art67": False, "rho_e": 0.0, "usar_sevedu": False})
    assert esc["meta_por_zona"] is False
    D = cargar_datos(esc)
    filas = []
    for m in METAS:
        t0 = time.time()
        e = Modelo2(D, meta_m=m).construir().resolver()
        filas.append(dict(modelo="M2_info_perfecta", escenario="comun", meta=m, estado=e["estado"],
                          gap=e["gap"], costo_mm=e.get("costo", float("nan")) / 1e9,
                          segundos=round(time.time() - t0, 1)))
        print(filas[-1], flush=True)
        salida.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(filas).to_csv(salida, index=False)


if __name__ == "__main__":
    main()
