"""
05_conteo_personas.py
Cuenta PERSONAS afectadas por privación (u_ij) y arma las tablas que necesitan los
modelos. Las reglas están en docs/reglas_conteo_personas.md y se validan aquí contra
la base de HOGARES del DANE: el conteo de un hogar debe ser > 0 exactamente donde el
DANE marca la privación (87,060 hogares del país).

Entrada : PERSONAS y HOGARES (DEPARTAMENTAL) 2025 + data/processed/hogares_antioquia.csv
Salida  : data/processed/
  conteo_pares.csv        una fila por (hogar, indicador privado): u_ij y su costo
  ninos.csv               niños rezagados (cohorte SevEdu) y no asistentes de 6 a 16 años
  adultos_clei.csv        adultos de 15 años o más de hogares pobres (logro y analfabetismo)
  logro_hogar.csv         n_i, suma de años y déficit D_i de cada hogar pobre
  empleo_componentes.csv  piezas del costo de empleo_formal y desempleo por hogar

Uso: python Modelos/05_conteo_personas.py
"""
import numpy as np
import pandas as pd

import parametros as P
from utils_dane import leer, a_numero, OUT

COLS_PER = ["DIRECTORIO", "SECUENCIA_P", "ORDEN", "P6020", "P6040", "P6090", "P5665",
            "P8563", "P6160", "P8587", "P8587S1", "P1088", "P1088S1", "P6240", "P6250",
            "P6260", "P6270", "P6351", "P6920", "P8586"]


# ==================================================================
# 1. Personas con las variables auxiliares (docs/reglas_conteo_personas.md)
# ==================================================================
def anios_aprobados(per):
    """Años de educación aprobados. Quien estudia usa P1088 (nivel actual); quien no, P8587."""
    n_no, g_no = per.P8587, per.P8587S1
    n_si, g_si = per.P1088, per.P1088S1
    a_no = np.select([n_no.isin([1, 2]), n_no.isin([3, 4, 5]),
                      n_no.between(6, 11), n_no.between(12, 13)],
                     [0, g_no, 11 + g_no, 16 + g_no], default=np.nan)
    a_si = np.select([n_si == 1, n_si.isin([2, 3, 4]),
                      n_si.between(5, 7), n_si == 8],
                     [0, g_si - 1, 11 + g_si - 1, 16 + g_si - 1], default=np.nan)
    return np.where(per.P8586 == 1, a_si, a_no)


def cargar_personas():
    per = leer("PERSONAS (DEPARTAMENTAL) 2025", columnas=COLS_PER)
    for c in COLS_PER:
        per[c] = a_numero(per[c])
    per["ID_HOGAR"] = (per.DIRECTORIO.astype(int).astype(str) + "_"
                       + per.SECUENCIA_P.astype(int).astype(str))
    per["ID_PERSONA"] = per.ID_HOGAR + "_" + per.ORDEN.astype(int).astype(str)
    per["anios"] = anios_aprobados(per)
    per["ocupado"] = (per.P6240 == 1) | (per.P6250 == 1) | (per.P6260 == 1) | (per.P6270 == 1)
    per["desocupado"] = ~per.ocupado & (per.P6351 == 1)
    per["asiste"] = per.P8586 == 1
    return per


def privaciones_persona(per):
    """Para cada indicador "por persona": qué personas están privadas (reglas validadas)."""
    e = per.P6040
    return {
        "aseguramiento_salud":   (e >= 6) & per.P6090.isin([2, 9]),
        "barreras_acceso_salud": (per.P5665 == 1) & ~per.P8563.isin([1, 2]),
        "trabajo_infantil":      e.between(12, 17) & per.ocupado,
        "rezago_escolar":        e.between(7, 17) & (per.anios < e - 6),
        "analfabetismo":         (e >= 15) & (per.P6160 == 2),
        "inasistencia_escolar":  e.between(6, 16) & (per.P8586 == 2),
        "atencion_integral":     e <= 5,      # supuesto: no replicable (docs, 96.5 %)
    }


# ==================================================================
# 2. Empleo formal y desempleo: piezas por hogar (informe §6.5)
# ==================================================================
def costo_persona_desocupada(per):
    """EpV_h de cada persona desocupada según su perfil (parametros.costo_desocupado)."""
    c = pd.Series(0.0, index=per.index)
    d = per.desocupado
    c[d] = [P.costo_desocupado(e, s == 2) for e, s in zip(per.P6040[d], per.P6020[d])]
    return c


def empleo_por_hogar(per):
    """Una fila por hogar con las piezas de empleo_formal y desempleo_larga_duracion."""
    p = per.assign(
        ocup_sin_pension=per.ocupado & (per.P6920 == 2),
        sin_cobertura=(per.P6040 >= 15) & ~per.P6920.isin([1, 3]),
        sin_cob_no_desoc=(per.P6040 >= 15) & ~per.P6920.isin([1, 3]) & ~per.desocupado,
        costo_desoc=costo_persona_desocupada(per),
    )
    h = p.groupby("ID_HOGAR").agg(
        n_ocupados=("ocupado", "sum"), n_ocup_sin_pension=("ocup_sin_pension", "sum"),
        n_desocupados=("desocupado", "sum"), n_adultos_sin_cobertura=("sin_cobertura", "sum"),
        n_sin_cob_no_desoc=("sin_cob_no_desoc", "sum"),
        costo_desocupados=("costo_desoc", "sum"))
    sin_ocup = h.n_ocupados == 0
    # Caso 3: hogar sin ocupados -> aporte a pensión a cada adulto sin cobertura,
    # SIN contar a los desocupados: ellos ya pagan su EpV (decisión D7 de Martín, 6-nov)
    h["n_caso3"] = np.where(sin_ocup, h.n_sin_cob_no_desoc, 0)
    h["privado_pred"] = (h.n_ocup_sin_pension > 0) | (h.n_desocupados > 0) | (sin_ocup & (h.n_adultos_sin_cobertura > 0))
    h["u_empleo_formal"] = h.n_ocup_sin_pension + h.n_desocupados + h.n_caso3
    h["costo_empleo_formal"] = (P.COSTO_APORTE_PENSION * (h.n_ocup_sin_pension + h.n_caso3)
                                + h.costo_desocupados)
    return h.reset_index()


# ==================================================================
# 3. Validación contra HOGARES del DANE (87,060 hogares del país)
# ==================================================================
def validar(per, emp):
    hog = leer("HOGARES (DEPARTAMENTAL) 2025")
    hog["ID_HOGAR"] = (a_numero(hog.DIRECTORIO).astype(int).astype(str) + "_"
                       + a_numero(hog.SECUENCIA_P).astype(int).astype(str))
    hog = hog.set_index("ID_HOGAR")
    filas = []

    def comparar(nombre, pred):
        pred = pred.reindex(hog.index, fill_value=False).astype(bool)
        dane = a_numero(hog[nombre]) == 1
        filas.append((nombre, int(dane.sum()), 100 * (pred == dane).mean(), int((pred != dane).sum())))

    for ind, flag in privaciones_persona(per).items():
        if ind != "atencion_integral":
            comparar(ind, flag.groupby(per.ID_HOGAR).any())
    # logro_educativo: regla del HOGAR (promedio de años de los >= 15 < 9)
    adultos = per[per.P6040 >= 15]
    comparar("logro_educativo", adultos.groupby("ID_HOGAR").anios.mean() < 9)
    comparar("empleo_formal", emp.set_index("ID_HOGAR").privado_pred)
    tabla = pd.DataFrame(filas, columns=["indicador", "hogares_DANE", "coincidencia_%", "discrepancias"])
    print("\n" + "=" * 70 + "\n VALIDACIÓN contra HOGARES (87,060 hogares)\n" + "=" * 70)
    print(tabla.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
    return tabla


# ==================================================================
# 4. Universo del modelo: hogares de Antioquia (hogares_antioquia.csv)
# ==================================================================
def cargar_hogares():
    h = pd.read_csv(OUT / "hogares_antioquia.csv")
    h["zona_costo"] = h.P3.map(P.zona_costo)
    return h


# ==================================================================
# 5. conteo_pares.csv: u_ij y costo de cada privación "simple" (pago por x_ij)
# ==================================================================
PAGO_POR_NINO_O_ADULTO = {"rezago_escolar": "z (niño)", "inasistencia_escolar": "z, t (niño, hogar)",
                          "logro_educativo": "v (adulto)", "analfabetismo": "v (adulto)"}
VIVIENDA = ["pisos", "paredes", "hacinamiento", "acueducto", "alcantarillado"]


def conteo_pares(per, emp, hog):
    """Una fila por (hogar, indicador) donde el DANE marca la privación."""
    flags = privaciones_persona(per)
    por_hogar = {ind: f.groupby(per.ID_HOGAR).sum() for ind, f in flags.items()}
    emp = emp.set_index("ID_HOGAR")
    epf = P.tabla_epf(P.escenario())
    filas = []
    for r in hog.itertuples(index=False):
        z = r.zona_costo
        for ind in P.INDICADORES:
            if getattr(r, ind) != 1:
                continue
            u, costo, imputado, pago = 1, np.nan, False, "x"
            if ind in VIVIENDA:
                costo = epf[ind][z]
            elif ind in ("aseguramiento_salud", "barreras_acceso_salud", "trabajo_infantil"):
                u = int(por_hogar[ind].get(r.ID_HOGAR, 0))
                costo = epf[ind][z] * u
            elif ind == "atencion_integral":
                n = int(por_hogar[ind].get(r.ID_HOGAR, 0))
                u, imputado = max(n, 1), n == 0                  # supuesto declarado
                costo = epf[ind][z] * u
            elif ind == "empleo_formal":
                e = emp.loc[r.ID_HOGAR] if r.ID_HOGAR in emp.index else None
                u = int(e.u_empleo_formal) if e is not None else 0
                if u == 0:                                       # el DANE lo marca y no se ve a quién
                    u, imputado, costo = 1, True, P.COSTO_APORTE_PENSION
                else:
                    costo = float(e.costo_empleo_formal)
            elif ind == "desempleo_larga_duracion":
                n = int(emp.n_desocupados.get(r.ID_HOGAR, 0))
                u, imputado = max(n, 1), n == 0
                costo = float(emp.costo_desocupados.get(r.ID_HOGAR, 0)) if n else P.COSTO_DESEMPLEO_SIN_IDENTIFICAR
            else:                                                # rezago, inasistencia, logro, analfabetismo
                pago = PAGO_POR_NINO_O_ADULTO[ind]
                u = int(por_hogar[ind].get(r.ID_HOGAR, 0)) if ind in por_hogar else 0
            filas.append((r.ID_HOGAR, ind, u, costo, r.FEX_C,
                          costo * r.FEX_C if not np.isnan(costo) else np.nan,
                          r.P3, imputado, pago))
    return pd.DataFrame(filas, columns=["ID_HOGAR", "indicador", "u_ij", "costo_hogar", "HW",
                                        "costo_ij", "P3", "u_imputado", "pago"])


# ==================================================================
# 6. ninos.csv: cohorte de SevEdu (rezagados) + no asistentes de 6 a 16 años
# ==================================================================
def tabla_ninos(per, hog):
    pob = hog[hog.POBRE == 1].set_index("ID_HOGAR")
    n = per[per.ID_HOGAR.isin(pob.index) & per.P6040.between(6, 17)].copy()
    n["atraso"] = (n.P6040 - 6) - n.anios
    n["en_cohorte_sevedu"] = n.P6040.between(7, 17) & (n.atraso >= 1)
    n["no_asiste_6_16"] = n.P6040.between(6, 16) & ~n.asiste
    n = n[n.en_cohorte_sevedu | n.no_asiste_6_16].copy()
    n["atraso"] = n.atraso.clip(lower=0)
    n["P3"] = n.ID_HOGAR.map(pob.P3)
    n["zona_costo"] = n.ID_HOGAR.map(pob.zona_costo)
    n["HW"] = n.ID_HOGAR.map(pob.FEX_C)
    g = n.anios
    n["e_k"] = n.P6040 - 6
    # Grados que gana la estrategia en el año (m_s): regreso 1; CLEI primaria 3-g (2 si g = 3);
    # CLEI secundaria (solo sensibilidad) 2 si g en {5, 7}, 1 si g en {6, 8}
    n["m_E1"] = 1
    n["m_E2"] = np.where(g <= 2, 3 - g, 2)
    n["m_E3"] = np.select([g.isin([5, 7]), g.isin([6, 8])], [2, 1], default=0)
    # Elegibilidad legal (Decreto 1075 de 2015, arts. 2.3.3.5.3.4.2 y 2.3.3.5.3.4.3)
    n["elig_E1"] = ~n.asiste & (n.P6040 <= 16)
    n["elig_E2"] = ~n.asiste & (n.P6040 >= 13) & (g <= 3)
    n["elig_E3_sens"] = ~n.asiste & (n.P6040 >= 15) & g.between(5, 8) & (n.atraso >= 2)
    # Precios unitarios (por niño, sin HW): cupo SGP del nivel del grado que cursaría, y un ciclo CLEI
    nivel = (g + 1).clip(1, 11).map(P.nivel_grado)
    n["nivel_cupo"] = nivel
    n["precio_E1_cupo"] = [P.CUPO_SGP[z][v] for z, v in zip(n.zona_costo, nivel)]
    n["precio_E2_E3_ciclo"] = n.zona_costo.map(P.COSTO_CICLO_CLEI)
    # Cobertura obligatoria (art. 67, decisión del 4-nov): rezagados de 6 a 15 años que no asisten
    n["obligatorio_E7"] = n.en_cohorte_sevedu & ~n.asiste & (n.P6040 <= 15)
    cols = ["ID_HOGAR", "ID_PERSONA", "P3", "zona_costo", "HW", "P6040", "anios", "atraso",
            "asiste", "en_cohorte_sevedu", "no_asiste_6_16", "e_k", "m_E1", "m_E2", "m_E3",
            "elig_E1", "elig_E2", "elig_E3_sens", "nivel_cupo", "precio_E1_cupo",
            "precio_E2_E3_ciclo", "obligatorio_E7"]
    return n[cols].rename(columns={"P6040": "edad"}).reset_index(drop=True)


# ==================================================================
# 7. adultos_clei.csv y logro_hogar.csv: logro educativo y analfabetismo (informe §6.9)
# ==================================================================
def tabla_adultos(per, hog):
    pob = hog[hog.POBRE == 1].set_index("ID_HOGAR")
    a = per[per.ID_HOGAR.isin(pob.index) & (per.P6040 >= 15)].copy()
    a["analfabeta"] = a.P6160 == 2
    a["elegible_clei"] = ~a.asiste & (a.anios <= P.LOGRO_META_PROMEDIO - 1)    # <= 8 años aprobados
    a["g_a"] = [P.ganancia_ciclo(int(x), bool(an)) for x, an in zip(a.anios, a.analfabeta)]
    a["P3"] = a.ID_HOGAR.map(pob.P3)
    a["zona_costo"] = a.ID_HOGAR.map(pob.zona_costo)
    a["HW"] = a.ID_HOGAR.map(pob.FEX_C)
    a["precio_ciclo"] = a.zona_costo.map(P.COSTO_CICLO_CLEI)
    adultos = a[["ID_HOGAR", "ID_PERSONA", "P3", "zona_costo", "HW", "P6040", "anios", "asiste",
                 "analfabeta", "elegible_clei", "g_a", "precio_ciclo"]].rename(columns={"P6040": "edad"})
    h = a.groupby("ID_HOGAR").agg(n_adultos=("anios", "size"), suma_anios=("anios", "sum"))
    h["D_i"] = P.LOGRO_META_PROMEDIO * h.n_adultos - h.suma_anios       # déficit para llegar a un promedio de 9
    h["g_max_hogar"] = a[a.elegible_clei].groupby("ID_HOGAR").g_a.sum().reindex(h.index).fillna(0)
    return adultos.reset_index(drop=True), h.reset_index()


if __name__ == "__main__":
    per = cargar_personas()
    print(f"Personas: {len(per):,} · años aprobados sin dato en mayores de 6: "
          f"{int(per.anios[per.P6040 >= 6].isna().sum()):,}")
    emp = empleo_por_hogar(per)
    validar(per, emp)

    hog = cargar_hogares()
    pares = conteo_pares(per, emp, hog)
    ninos = tabla_ninos(per, hog)
    adultos, logro = tabla_adultos(per, hog)
    pares.to_csv(OUT / "conteo_pares.csv", index=False)
    ninos.to_csv(OUT / "ninos.csv", index=False)
    adultos.to_csv(OUT / "adultos_clei.csv", index=False)
    logro.to_csv(OUT / "logro_hogar.csv", index=False)
    emp.to_csv(OUT / "empleo_componentes.csv", index=False)

    print("\n" + "=" * 70 + "\n RESULTADOS (hogares pobres de Antioquia)\n" + "=" * 70)
    k = ninos[ninos.en_cohorte_sevedu]
    print(f"Cohorte SevEdu: {len(k)} niños (esperado 215) · hogares {k.ID_HOGAR.nunique()} (149)")
    print(f"  atraso 1/2/3/4/5+: {[int((k.atraso == a).sum()) for a in (1, 2, 3, 4)]} + {int((k.atraso >= 5).sum())} (esperado 83/47/27/26/32)")
    print(f"  asisten {int(k.asiste.sum())} (160) · no asisten {int((~k.asiste).sum())} (55) · obligatorio E-7 {int(k.obligatorio_E7.sum())} (29)")
    b = k.atraso + 1 - k.asiste.astype(int)
    sev = (k.HW * (b / (k.e_k + 1)) ** 2).sum()
    print(f"  SevEdu^N(1,sin) = {sev:,.0f} (esperado ~21,562)")
    otros = ninos[~ninos.en_cohorte_sevedu]
    print(f"No asistentes de 6 a 16 SIN rezago (D3): {len(otros)} niños en {otros.ID_HOGAR.nunique()} hogares")
    print(f"Adultos de hogares pobres: {len(adultos):,} · elegibles a CLEI: {int(adultos.elegible_clei.sum()):,}")
    p = pares[pares.ID_HOGAR.isin(hog[hog.POBRE == 1].ID_HOGAR)].merge(logro, on="ID_HOGAR", how="left")
    lg = p[p.indicador == "logro_educativo"]
    print(f"Hogares pobres con logro_educativo: {len(lg)} (esperado 503) · pueden salir con 1 ciclo por adulto: "
          f"{int((lg.g_max_hogar >= lg.D_i).sum())} (esperado 33)")
    pp = pares[pares.ID_HOGAR.isin(hog[hog.POBRE == 1].ID_HOGAR)]
    print(f"u_ij imputados (hogares pobres): {int(pp.u_imputado.sum())} de {len(pp):,} filas; por indicador: "
          f"{pp[pp.u_imputado].groupby('indicador').size().to_dict()}")
    sel = (emp.set_index('ID_HOGAR').loc[hog[hog.POBRE == 1].ID_HOGAR])
    print(f"Hogares pobres sin ocupados con desocupados (posible doble conteo en el caso 3): "
          f"{int(((sel.n_ocupados == 0) & (sel.n_desocupados > 0)).sum())}")
    print(f"\nGuardado en {OUT}")
