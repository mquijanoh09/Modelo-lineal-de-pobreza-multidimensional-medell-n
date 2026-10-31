# -*- coding: utf-8 -*-
"""
costos_provisionales.py — PROVISIONAL. Se borra cuando exista parametros.py de Martin.

Implementa SOLO la sensibilidad u_ij = 1 acordada por los dos ("caso base y u_ij = 1"),
porque es la unica que no necesita el conteo de personas (05_conteo_personas.py):
una intervencion por hogar privado, al precio EpF_j de su zona.

    V_ij = HW_i                 cobertura: hogares reales (u = 1)
    K_ij = EpF_j^zona * HW_i    costo en pesos

Tabla: CONTEXTO_DATOS.md de Martin, seccion 4 (30-oct-2026), pesos de 2025.
Zona de costo: urbano = P3 1 (cabecera); rural = P3 2 o 3.

Avisos que hay que tener presentes al leer resultados con esta tabla:
  * u = 1 SUBESTIMA los indicadores por persona (salud, analfabetismo, logro, CDI).
  * empleo_formal y desempleo a $2,73 M y $5,12 M por hogar: propuesta de Martin
    para u = 1 (pregunta 3 de su seccion 8).
  * rezago: precio de secundaria (año regular) y elegible para todos. Es un
    marcador de posicion: con las reglas nuevas de Martin un año regular no
    quita la privacion; elig_ij real sale de ninos_rezago.csv.
  * acueducto rural $43,7 M es la base de Martin; tu nota del 30-oct lo deja
    "a confirmar" con la fuente. Se puede cambiar con el argumento.
"""
import numpy as np

MILLON = 1e6
P_INASISTENCIA = 0.369          # cumplimiento del ciclo 4 de 2025 (Renta Ciudadana)

EPF = {                         # (urbano, rural) en millones de pesos de 2025
    "logro_educativo":          (2.88, 3.86),
    "analfabetismo":            (0.96, 1.29),
    "inasistencia_escolar":     (3.0 / P_INASISTENCIA, 3.0 / P_INASISTENCIA),
    "rezago_escolar":           (3.05, 3.96),     # PROVISIONAL (ver arriba)
    "atencion_integral":        (5.21, 5.21),
    "trabajo_infantil":         (3.0, 3.0),
    "desempleo_larga_duracion": (5.12, 5.12),
    "empleo_formal":            (2.73, 2.73),
    "aseguramiento_salud":      (1.32, 1.32),
    "barreras_acceso_salud":    (0.21, 0.36),
    "acueducto":                (11.72, 43.7),
    "alcantarillado":           (11.72, 15.3),
    "pisos":                    (25.62, 35.2),
    "paredes":                  (25.62, 35.2),
    "hacinamiento":             (31.32, 31.32),
}


def pesos_u1(hog, IND, acueducto_rural=None):
    """Devuelve (V, K, elig) con la sensibilidad u = 1."""
    HW = hog.FEX_C.to_numpy(float)
    rural = hog.P3.to_numpy() != 1
    epf = {j: list(v) for j, v in EPF.items()}
    if acueducto_rural is not None:
        epf["acueducto"][1] = acueducto_rural
    precio = np.column_stack([np.where(rural, epf[j][1], epf[j][0]) for j in IND]) * MILLON
    V = np.repeat(HW[:, None], len(IND), axis=1)
    K = precio * HW[:, None]
    elig = np.ones_like(K)
    return V, K, elig
