# -*- coding: utf-8 -*-
"""
m34_compat_martin.py — Puente único entre los m34_* y el M1/M2 de Martín (versión de main del 10-nov).

Fija en UN solo lugar el escenario de información perfecta comparable con M3/M4:
  datos   : cargar_datos("sin_E7")  -> sensibilidad de Martín "versión comparable con M3/M4" (sin E-7)
  M2      : escenario_m2("sin_E7", "meta_global"), sin SevEdu (usar_sevedu = False)
  M1      : dos etapas (D1) con r = 0, rho = None (sin techo de severidad), rho_e = None (sin SevEdu)
Desempleo sin desocupado identificado: no quitable (caso base de Martín, 7-nov), igual que en
costos_comunes_m34.csv desde el 10-nov.

OJO (10-nov): en la API nueva rho_e = 0.0 NO desactiva SevEdu (activa el techo "no subir"); la
desactivación es rho_e = None. La versión de modelos-1-2 (5-nov) usaba `if self.rho_e:`.
"""
import sys
from pathlib import Path


def cargar(dir_modelos):
    """Agrega Modelos/ al path y devuelve (P, cargar_datos, Modelo1, resolver_dos_etapas, Modelo2)."""
    dm = str(Path(dir_modelos).resolve())
    if dm not in sys.path:
        sys.path.insert(0, dm)
    import parametros as P
    from datos_modelo import cargar_datos
    from Modelo_1.modelo1 import Modelo1, resolver_dos_etapas
    from Modelo_2.modelo2 import Modelo2
    return P, cargar_datos, Modelo1, resolver_dos_etapas, Modelo2


def datos_comun(dir_modelos):
    P, cargar_datos, *_ = cargar(dir_modelos)
    d = cargar_datos("sin_E7")
    assert d.esc["cobertura_art67"] is False, "el escenario comun no lleva E-7"
    assert d.esc.get("desempleo_imputado", False) is False, "caso base de Martin: desempleo no imputado"
    return d


def esc_m2(dir_modelos):
    P, *_ = cargar(dir_modelos)
    esc = P.escenario_m2("sin_E7", "meta_global")
    esc["usar_sevedu"] = False
    assert esc["meta_por_zona"] is False and esc["cobertura_art67"] is False
    return esc


def m2_costo(dir_modelos, d, meta, gap_rel=1e-6, time_limit=600):
    """Costo mínimo (pesos) del M2 de Martín con meta global de M0, sin E-7 ni SevEdu."""
    *_, Modelo2 = cargar(dir_modelos)
    m = Modelo2(d, esc_m2(dir_modelos), meta_m=meta).construir()
    info = m.resolver(gap_rel=gap_rel, time_limit=time_limit)
    costo = float(m.recalcular().loc["total", "costo"]) if info["estado"] == "Optimal" else float("nan")
    return dict(estado=info["estado"], gap=info["gap"], costo=costo, segundos=info["segundos"])


def m1_personas(dir_modelos, d, B, gap_rel=1e-6, time_limit=600):
    """Personas que salen con el M1 de Martín (max H; desempate severidad), B en pesos, sin techos."""
    _, _, _, resolver_dos_etapas, _ = cargar(dir_modelos)
    m, info = resolver_dos_etapas(d, B, r=0.0, rho=None, rho_e=None, gap_rel=gap_rel, time_limit=time_limit)
    e1 = info["etapa1"]
    ok = e1["estado"] == "Optimal" and info["etapa2"] is not None and info["etapa2"]["estado"] == "Optimal"
    rec = m.recalcular().loc["total"] if ok else None
    return dict(estado=e1["estado"] if not ok else "Optimal", gap=e1["gap"],
                personas_salen=float(rec["salen_personas"]) if ok else float("nan"),
                costo=float(rec["costo"]) if ok else float("nan"), H_star=info["H_star"])
