# -*- coding: utf-8 -*-
"""
m34_costos_reales.py — Costos "reales" PROVISIONALES para M3/M4 (4-nov-2026).

Por que existe: M3/M4 llevan desde el 2-nov con u = 1 (un beneficiario por hogar) porque
`05_conteo_personas.py` / `conteo_pares.csv` de Martin no han llegado. Este modulo reconstruye
u_ij con las reglas que Martin describio en CONTEXTO_DATOS.md §2.6, §3 y §4, y las VALIDA contra
la bandera del DANE en los 87.060 hogares (mismo criterio que uso Martin):

  indicador                 u_ij (personas)                                  acuerdo con DANE
  analfabetismo             >= 15 anios y P6160 == 2 (no sabe leer/escribir)  100,00 %
  logro_educativo           >= 15 anios con < 9 anios de educacion            privado => u >= 1 en 99,5 %
  aseguramiento_salud       >= 6 anios y P6090 != 1 (no afiliado / no sabe)   100,00 %
  barreras_acceso_salud     P5665 == 1 y P8563 >= 3 (enfermo y no fue a medico ni promotor)  100,00 %
  atencion_integral         ninios de 0 a 5 anios (aproximacion de Martin)   privado => u >= 1 en 100 %
  desempleo_larga_duracion  desocupados del hogar, minimo 1                   86,5 % (= Martin)
  empleo_formal             ocupados sin pension + desocupados (o adultos sin cobertura si no hay ocupados)
  resto (vivienda, servicios, inasistencia, trabajo infantil, rezago)  u = 1 (unidad = hogar)

Si la regla da 0 pero el DANE marca la privacion: u = 1 y `u_imputado = 1` (regla de Martin).

Costo del par (millones de $ 2025, tabla §4):  K_ij = costo_hogar_ij * HW_i,  costo_hogar = EpF_j^zona * u_ij
  excepto empleo y desempleo (formula de Martin, §4):
    empleo_formal  = 2,73 * ocupados_sin_pension + sum EpV(desocupados)          si hay ocupados
                   = 2,73 * adultos_sin_cobertura + sum EpV(desocupados)         si no hay ocupados
    desempleo      = sum EpV(desocupados)  (imputado: 5,12, igual que la sensibilidad u = 1)
    EpV: 18-28 -> 5,12; mujeres 29-56 -> 3,42; hombres 29-61 -> 2,56; mujeres >= 57 y hombres >= 62 -> 2,73
Cobertura (Trampa 1: misma unidad arriba y abajo): V_ij = u_ij * HW_i (personas reales afectadas).

FUENTE DE COSTOS (auditoria 4-nov, hallazgo 2): `cargar_costos` usa la reconstruccion provisional
por defecto. El conteo de Martin (`data/processed/conteo_pares.csv`) solo se usa si se pide
explicitamente con fuente="martin". Antes el cambio era automatico y ese archivo trae u_ij = 0 en
logro educativo (se paga por v, no por x): Den = 0, sin cortes y el MILP queda infactible en
silencio. Con fuente="martin" se valida que ningun par privado quede con cobertura 0.

Uso (validacion): python3 m34_costos_reales.py <raiz_DEPARTAMENTAL>
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import m34_datos as D
from m34_montecarlo import EPF

LLAVE = ["DIRECTORIO", "SECUENCIA_P"]
PENSION = 2.73


def _personas(raiz):
    p = pd.read_csv(D._csv(raiz, "PERSONAS (DEPARTAMENTAL) 2025"), encoding="utf-8-sig", low_memory=False)
    return p


def _epv(sexo, edad):
    """Empleos para la Vida (Decreto 533 de 2024) / aporte a pension, millones de $."""
    return np.select([edad <= 28,
                      (sexo == 2) & (edad <= 56), (sexo == 1) & (edad <= 61)],
                     [5.12, 3.42, 2.56], PENSION)


def conteos_personas(p):
    """Cuenta por hogar (todas las filas de PERSONAS). Devuelve DataFrame con LLAVE + conteos + costos."""
    e = p.P6040
    ocup = (p.P6240 == 1) | (p.P6250 == 1) | (p.P6260 == 1) | (p.P6270 == 1)
    desoc = (~ocup) & (p.P6351 == 1)           # buscaron trabajo y no estan ocupados
    nivel, g = p.P8587, p.P8587S1.fillna(0)
    anios = np.select([nivel.isin([1, 2]), nivel == 3, nivel == 4, nivel == 5, nivel >= 6],
                      [0, g.clip(0, 5), g.clip(5, 9), g.clip(9, 11), 11], np.nan)
    epv = pd.Series(_epv(p.P6020.to_numpy(), e.to_numpy()), index=p.index)
    c = pd.DataFrame({
        "analfabetismo": (e >= 15) & (p.P6160 == 2),
        "logro_educativo": (e >= 15) & (anios < 9),
        "aseguramiento_salud": (e >= 6) & (p.P6090 != 1),
        "barreras_acceso_salud": (p.P5665 == 1) & (p.P8563 >= 3),
        "atencion_integral": e <= 5,
        "n_ocup": ocup,
        "n_ocup_sin_pension": ocup & (p.P6920 == 2),
        "n_desoc": desoc,
        "n_adultos_sin_cobertura": (~ocup) & (e >= 18) & (p.P6920 == 2),
    }).astype(int)
    c["epv_desoc"] = np.where(desoc, epv, 0.0)
    c[LLAVE] = p[LLAVE]
    return c.groupby(LLAVE).sum().reset_index()


def reconstruir(hog, raiz):
    """Matrices n x J alineadas con `hog`: U (personas), Kh (millones de $ por hogar, sin HW), imputado."""
    a = hog[LLAVE].merge(conteos_personas(_personas(raiz)), on=LLAVE, how="left").fillna(0)
    assert len(a) == len(hog)
    M = hog[D.IND].to_numpy(float)
    rural = hog.P3.to_numpy() != 1
    n, J = M.shape
    U = np.ones((n, J))
    Kh = np.column_stack([np.where(rural, EPF[j][1], EPF[j][0]) for j in D.IND])
    for j in ["analfabetismo", "logro_educativo", "aseguramiento_salud", "barreras_acceso_salud",
              "atencion_integral"]:
        jj = D.IND.index(j)
        U[:, jj] = a[j].to_numpy()
        Kh[:, jj] = Kh[:, jj] * np.maximum(U[:, jj], 1)
    # desempleo de larga duracion
    jj = D.IND.index("desempleo_larga_duracion")
    U[:, jj] = a.n_desoc.to_numpy()
    Kh[:, jj] = np.where(U[:, jj] > 0, a.epv_desoc.to_numpy(), EPF["desempleo_larga_duracion"][0])
    # empleo formal (formula de Martin)
    jj = D.IND.index("empleo_formal")
    hay_ocup = a.n_ocup.to_numpy() > 0
    base = np.where(hay_ocup, a.n_ocup_sin_pension.to_numpy(), a.n_adultos_sin_cobertura.to_numpy())
    U[:, jj] = base + a.n_desoc.to_numpy()
    Kh[:, jj] = PENSION * base + a.epv_desoc.to_numpy()
    Kh[:, jj] = np.where(U[:, jj] > 0, Kh[:, jj], PENSION)
    imput = (U < 1) & (M == 1)
    U = np.where(M == 1, np.maximum(U, 1), 0)
    return U, Kh, imput


def cargar_costos(hog, raiz, fuente="provisional", ruta_martin="data/processed/conteo_pares.csv"):
    """V (cobertura) y K (pesos) n x J.

    fuente="provisional" (defecto): reconstruccion de este modulo.
    fuente="martin": conteo de Martin; solo si se pide explicitamente (hallazgo 2 del 4-nov).
    """
    HW = hog.FEX_C.to_numpy(float)
    if fuente not in ("provisional", "martin"):
        raise ValueError(f"fuente desconocida: {fuente!r}")
    if fuente == "martin":
        if not Path(ruta_martin).exists():
            raise FileNotFoundError(f"fuente='martin' pero no existe {ruta_martin}")
        cp = pd.read_csv(ruta_martin)
        print(f"[m34_costos_reales] usando {ruta_martin} (Martin)", flush=True)
        idx = {k: n for n, k in enumerate(hog.DIRECTORIO.astype(str) + "_" + hog.SECUENCIA_P.astype(str))}
        U = np.zeros((len(hog), len(D.IND)))
        for r in cp.itertuples():
            U[idx[r.ID_HOGAR], D.IND.index(r.indicador)] = r.u_ij
        rural = hog.P3.to_numpy() != 1
        Kh = np.column_stack([np.where(rural, EPF[j][1], EPF[j][0]) for j in D.IND]) * np.maximum(U, 1)
        # Nota: si Martin entrega costo_ij (incluye la formula de empleo) hay que leerlo aqui.
        # Validacion: todo par privado debe tener cobertura > 0; si no, Den = 0 en enumerar_cortes.
        Mpriv = D.matrices(hog)[0] == 1
        malos = Mpriv & (U <= 0)
        if malos.any():
            js = sorted({D.IND[j] for j in np.where(malos)[1]})
            raise ValueError(f"conteo de Martin: {int(malos.sum())} pares privados con u_ij = 0 en {js}. "
                             "Construir V de esos indicadores (p. ej. logro con adultos_clei.csv) antes de usarlo.")
    else:
        U, Kh, _ = reconstruir(hog, raiz)
    V = U * HW[:, None]
    K = Kh * HW[:, None]
    return V, K, fuente


def main():
    raiz = sys.argv[1]
    hog = D.cargar(raiz)
    b = D.verificar_linea_base(hog)
    M, HS, HW, w = D.matrices(hog)
    U, Kh, imput = reconstruir(hog, raiz)
    from m34_montecarlo import precios_u1
    K1 = precios_u1(hog)
    K = Kh * HW[:, None]
    filas = []
    for jj, j in enumerate(D.IND):
        m = M[:, jj] == 1
        if not m.any():
            continue
        pob = m & (b["pobre0"] == 1)
        filas.append(dict(indicador=j, hogares_privados=int(m.sum()), u_medio=U[m, jj].mean(),
                          u_max=int(U[m, jj].max()), imputados=int(imput[m, jj].sum()),
                          costo_u1_milmill=(K1[m, jj].sum()) / 1e3, costo_real_milmill=K[m, jj].sum() / 1e3,
                          razon_real_u1=K[m, jj].sum() / K1[m, jj].sum(),
                          costo_real_pobres_milmill=K[pob, jj].sum() / 1e3))
    t = pd.DataFrame(filas)
    pd.set_option("display.width", 200)
    print(t.round(3).to_string(index=False))
    print(f"\nTotal: u1 = {K1[M == 1].sum() / 1e3:,.1f} mil millones; real = {K[M == 1].sum() / 1e3:,.1f} mil millones;"
          f" pobres (real) = {K[(M == 1) & (b['pobre0'][:, None] == 1)].sum() / 1e3:,.1f} mil millones")
    if len(sys.argv) > 2:
        t.to_csv(sys.argv[2], index=False)


if __name__ == "__main__":
    main()
