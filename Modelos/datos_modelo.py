"""
datos_modelo.py
Datos que necesitan los MILP de los Modelos 1 y 2, armados a partir de lo que
genera el 05 (data/processed/) y de parametros.py. No resuelve nada: solo arma
conjuntos y parámetros (formulacion_modelo1.md §1-§2).

    from datos_modelo import cargar_datos
    D = cargar_datos(P.escenario("base"))

Contenido de D (un objeto DatosIPM):
  hog         DataFrame de los 523 hogares pobres: ID_HOGAR, zona (P3), zona_costo,
              HW, HS, p = HW*HS, c0, Mbig = c0 - 0.33
  priv        {i: [j con M_ij = 1]}                       (J_i)
  costo_x     {(i, j): $} costo de x_ij para los indicadores "simples" (pago por x)
  ninos       DataFrame de niños (K ∪ N) con elegibilidad, d_ks, coef_ks, costos
  adultos     DataFrame de adultos elegibles a un ciclo CLEI (L_i^C) con g_a y costo
  logro       {i: D_i}
  analfabetas {i: [ID_PERSONA de los analfabetas del hogar]}
  A           {i: [valores alcanzables de s_i]}           (A_i, tangentes de (7))
  Sev0, SevEdu_sin, Pobres_d, Pob, Pob_d, M0_0, M0_d
"""
import itertools
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

import parametros as P
from utils_dane import OUT

# Estrategias educativas: E1 regreso, E2 CLEI de primaria, E3 CLEI de secundaria (solo sensibilidad)
ESTRATEGIAS = ["E1", "E2", "E3"]
INDICADORES_SIMPLES = list(P.EPF_BASE) + ["empleo_formal", "desempleo_larga_duracion"]


@dataclass
class DatosIPM:
    esc: dict
    hog: pd.DataFrame
    priv: dict
    costo_x: dict
    ninos: pd.DataFrame
    adultos: pd.DataFrame
    logro: dict
    analfabetas: dict
    A: dict
    Sev0: float
    SevEdu_sin: float
    Pobres_d: dict
    Pob: float
    Pob_d: dict
    M0_0: float
    M0_d: dict
    estrategias: list = field(default_factory=list)

    def resumen(self):
        n_x = sum(len(v) for v in self.priv.values())
        n_tang = sum(len(v) for v in self.A.values())
        k = self.ninos
        return (f"{len(self.hog)} hogares pobres · {n_x} pares (i, j) · {len(k)} niños "
                f"({int(k.en_cohorte_sevedu.sum())} en la cohorte SevEdu, "
                f"{int(k.obligatorio_E7.sum())} con E-7) · {len(self.adultos)} adultos CLEI · "
                f"{n_tang} tangentes · Sev0 = {self.Sev0:,.0f} · SevEdu_sin = {self.SevEdu_sin:,.0f} · "
                f"estrategias {self.estrategias}")


# ------------------------------------------------------------------
# Hogares pobres y privaciones
# ------------------------------------------------------------------
def _hogares():
    h = pd.read_csv(OUT / "hogares_antioquia.csv")
    h["HW"], h["HS"] = h.FEX_C, h.PERSONAS
    h["p"] = h.HW * h.HS
    h["c0"] = np.round(sum(P.PESOS[j] * h[j] for j in P.INDICADORES), 2)
    assert np.allclose(h.c0, h.IPM), "el puntaje recalculado no coincide con IPM del DANE"
    h["zona"] = h.P3
    h["zona_costo"] = h.P3.map(P.zona_costo)
    return h


def _costos_x(pobres, esc):
    """c_ij = EpF_j(zona) * u_ij * HW_i para los indicadores pagados por x_ij.

    Vivienda, salud, atención integral y trabajo infantil se recalculan con la tabla
    EpF del escenario (así funcionan las sensibilidades de acueducto y trabajo infantil).
    Empleo y desempleo se toman del 05, que los costea persona por persona (P4).
    Con u_igual_1 (versión del paper) se paga una unidad por hogar.
    """
    pares = pd.read_csv(OUT / "conteo_pares.csv")
    pares = pares[pares.ID_HOGAR.isin(pobres.ID_HOGAR) & (pares.pago == "x")]
    epf = P.tabla_epf(esc)
    zc = pobres.set_index("ID_HOGAR").zona_costo
    costo = {}
    for r in pares.itertuples(index=False):
        u = 1 if esc["u_igual_1"] else r.u_ij
        if r.indicador in epf:
            unit = epf[r.indicador][zc[r.ID_HOGAR]]
            if P.UNIDAD[r.indicador] == "hogar":
                u = 1
        else:                                       # empleo_formal / desempleo: costo del hogar del 05
            unit = r.costo_hogar / max(r.u_ij, 1)
        costo[(r.ID_HOGAR, r.indicador)] = float(unit * u * r.HW)
    return costo


def _valores_alcanzables(js):
    """A_i: todas las sumas de pesos de subconjuntos de J_i (redondeadas a 0.01)."""
    w = [P.PESOS[j] for j in js]
    vals = set()
    for k in range(len(w) + 1):
        for comb in itertools.combinations(w, k):
            vals.add(round(sum(comb), 2))
    return sorted(vals)


# ------------------------------------------------------------------
# Niños: SevEdu, rezago e inasistencia (formulacion_modelo1.md §2.4)
# ------------------------------------------------------------------
def _ninos(esc):
    n = pd.read_csv(OUT / "ninos.csv")
    n["elig_E3"] = n.elig_E3_sens & bool(esc["usar_E3"])
    n = n.rename(columns={"m_E1": "d_E1", "m_E2": "d_E2", "m_E3": "d_E3"})
    # b_k: atraso al final del año sin intervenir; q_k = 1 si asiste (aprueba con prob. ap = 1)
    q = n.asiste.astype(float) * esc["ap"]
    n["b_k"] = np.where(n.en_cohorte_sevedu, n.atraso + 1 - q, 0.0)
    den = (n.e_k + 1) ** 2
    for s in ESTRATEGIAS:
        d = n[f"d_{s}"].astype(float)
        # coef_ks = HW_k (2 b_k d_ks - d_ks^2) / (e_k + 1)^2 (solo la cohorte aporta a SevEdu)
        n[f"coef_{s}"] = np.where(n.en_cohorte_sevedu, n.HW * (2 * n.b_k * d - d ** 2) / den, 0.0)
    # Costos ya multiplicados por HW_k: E1 = cupo SGP (la Renta Ciudadana va por hogar con t_i);
    # E2 y E3 = un ciclo CLEI.
    n["costo_E1"] = n.precio_E1_cupo * n.HW
    n["costo_E2"] = n.precio_E2_E3_ciclo * n.HW
    n["costo_E3"] = n.precio_E2_E3_ciclo * n.HW
    n["obligatorio_E7"] = n.obligatorio_E7 & bool(esc["cobertura_art67"])
    return n


def cargar_datos(esc=None, n_muestra=None, semilla=P.SEMILLA):
    """Arma todos los datos del MILP para un escenario.

    n_muestra: si se da, toma una muestra de hogares pobres (pruebas rápidas, regla del proyecto:
    primero 50 hogares y luego los 523). Pob y M0 se calculan siempre sobre toda Antioquia.
    """
    esc = P.escenario() if esc is None else esc
    h = _hogares()
    pob_d = h.groupby("zona").p.sum().to_dict()
    pobres = h[h.c0 >= P.K - 1e-9].copy()
    num_d = (pobres.p * pobres.c0).groupby(pobres.zona).sum().to_dict()
    Pob = float(h.p.sum())
    M0_0 = float((pobres.p * pobres.c0).sum()) / Pob
    M0_d = {d: num_d.get(d, 0.0) / pob_d[d] for d in pob_d}
    if n_muestra is not None:
        pobres = pobres.sample(n=n_muestra, random_state=semilla)
    pobres = pobres.sort_values("ID_HOGAR").reset_index(drop=True)
    pobres["Mbig"] = pobres.c0 - P.K_GRID                 # M_i = c_i^0 - 0.33 (big-M ajustado)
    ids = set(pobres.ID_HOGAR)

    priv = {r.ID_HOGAR: [j for j in P.INDICADORES if getattr(r, j) == 1] for r in pobres.itertuples()}
    costo_x = _costos_x(pobres, esc)

    ninos = _ninos(esc)
    ninos = ninos[ninos.ID_HOGAR.isin(ids)].reset_index(drop=True)
    estr = ["E1", "E2"] + (["E3"] if esc["usar_E3"] else [])
    k = ninos[ninos.en_cohorte_sevedu]
    SevEdu_sin = float((k.HW * (k.b_k / (k.e_k + 1)) ** 2).sum())

    a = pd.read_csv(OUT / "adultos_clei.csv")
    a = a[a.ID_HOGAR.isin(ids)]
    analf = a[a.analfabeta].groupby("ID_HOGAR").ID_PERSONA.apply(list).to_dict()
    adultos = a[a.elegible_clei].copy()
    adultos["costo_v"] = adultos.precio_ciclo * adultos.HW
    lg = pd.read_csv(OUT / "logro_hogar.csv").set_index("ID_HOGAR").D_i.to_dict()

    return DatosIPM(
        esc=esc, hog=pobres, priv=priv, costo_x=costo_x, ninos=ninos,
        adultos=adultos.reset_index(drop=True), logro={i: lg.get(i, 0.0) for i in ids},
        analfabetas=analf, A={i: _valores_alcanzables(js) for i, js in priv.items()},
        Sev0=float((pobres.p * pobres.c0 ** 2).sum()), SevEdu_sin=SevEdu_sin,
        Pobres_d=pobres.groupby("zona").p.sum().to_dict(), Pob=Pob, Pob_d=pob_d,
        M0_0=M0_0, M0_d=M0_d, estrategias=estr)


if __name__ == "__main__":
    D = cargar_datos()
    print(D.resumen())
    print(f"M0 = {D.M0_0:.6f} (esperado 0.038684) · por zona "
          + ", ".join(f"{P.ZONAS[d]} {v:.4f}" for d, v in D.M0_d.items()))
    print(f"Personas pobres por zona: " + ", ".join(f"{P.ZONAS[d]} {v:,.0f}" for d, v in D.Pobres_d.items()))
    assert len(D.hog) == 523 and abs(D.Sev0 - 117_908) < 1 and abs(D.M0_0 - 0.038684) < 1e-6
    print(f"Costo de quitar TODAS las privaciones simples: ${sum(D.costo_x.values()) / 1e12:,.3f} billones")
