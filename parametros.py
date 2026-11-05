"""
parametros.py
Parámetros compartidos por los 4 modelos (costos, severidad, presupuesto).

Regla del proyecto: cada costo lleva su fuente oficial en el comentario.
Se construye por partes; hoy tiene trabajo infantil, logro educativo (CLEI) y barreras de salud.
Pendiente: resto de la tabla de costos (informe §6.8), Sev0, A_i, lambda, SevEdu^N_0.
"""

# ------------------------------------------------------------------
# Trabajo infantil (informe §6.7b, decidido por Martín el 4-nov-2026)
# Externado de media jornada del ICBF (SIM 420212), 4 h diarias en contrajornada.
# Fuente: Res. ICBF 0001 de 2025, ficha I-12-122, actualizada por la
#         Res. 0296 del 31-ene-2025 (costo cupo mes, febrero a diciembre).
# Cada cupo opera 6 meses y atiende a 2 niños al año -> 6 meses por niño.
# Unidad: por niño de 12 a 17 años que trabaja (u_ij), mismo valor urbano y rural.
# Supuesto declarado: los 6 meses bastan para eliminar la privación.
# ------------------------------------------------------------------
TI_COSTO_CUPO_MES_EXTERNADO = 886_058      # SIM 420212
TI_COSTO_CUPO_MES_PSICOSOCIAL = 554_907    # SIM 420213 (sensibilidad baja)
TI_MESES_POR_NINO = 6

COSTO_TRABAJO_INFANTIL = TI_COSTO_CUPO_MES_EXTERNADO * TI_MESES_POR_NINO           # 5,316,348
COSTO_TRABAJO_INFANTIL_SENS_BAJA = TI_COSTO_CUPO_MES_PSICOSOCIAL * TI_MESES_POR_NINO  # 3,329,442

if __name__ == "__main__":
    print(f"Trabajo infantil (caso base): ${COSTO_TRABAJO_INFANTIL:,.0f} por niño")
    print(f"Trabajo infantil (sens. baja): ${COSTO_TRABAJO_INFANTIL_SENS_BAJA:,.0f} por niño")

# ------------------------------------------------------------------
# Logro educativo y analfabetismo (informe §6.9, decidido por Martín el 4-nov-2026)
# CLEI: asignación por alumno por ciclo, SGP 2025 Antioquia (DNP, Anexo 1 DD SGP-96-2025).
# Cada ciclo dura al menos 40 semanas (Decreto 1075/2015, art. 2.3.3.5.3.4.4):
# como máximo UN ciclo por adulto en el año (variable v_a).
# ------------------------------------------------------------------
COSTO_CICLO_CLEI = {"urbano": 958_431, "rural": 1_286_194}

# Años aprobados al terminar el siguiente ciclo (art. 2.3.3.5.3.4.7):
# ciclo 1 = 1.º-3.º, ciclo 2 = 4.º-5.º, ciclo 3 = 6.º-7.º, ciclo 4 = 8.º-9.º
FIN_SIGUIENTE_CICLO = {0: 3, 1: 3, 2: 3, 3: 5, 4: 5, 5: 7, 6: 7, 7: 9, 8: 9}
LOGRO_META_PROMEDIO = 9     # DANE: privado si el promedio de años de los >= 15 es < 9


def ganancia_ciclo(anios, analfabeta=False):
    """Años que gana un adulto con su siguiente ciclo CLEI (g_a).
    Un analfabeta hace el ciclo 1: gana max(3 - anios, 0)."""
    if analfabeta:
        return max(3 - anios, 0)
    return FIN_SIGUIENTE_CICLO.get(anios, 0) - anios if anios <= 8 else 0

# ------------------------------------------------------------------
# Barreras de acceso a salud (informe §6.2, decidido por Martín el 4-nov-2026)
# 1 consulta ambulatoria de medicina general, tarifa SOAT 2025, código 39141:
#   4,51 UVB = $52,100 (Circular Externa 25 de 2024, Minsalud, p. 34).
# Rural: + prima adicional por dispersión geográfica de la UPC,
#   11.47 % x UPC-S $1,323,403.20 (Res. 2717 de 2024), aproximación al transporte.
# Unidad: por persona con necesidad no atendida.
# ------------------------------------------------------------------
CONSULTA_MEDICINA_GENERAL = 52_100
UPC_SUBSIDIADO_2025 = 1_323_403.20
PRIMA_DISPERSION = 0.1147

COSTO_BARRERAS_SALUD = {
    "urbano": CONSULTA_MEDICINA_GENERAL,
    "rural": CONSULTA_MEDICINA_GENERAL + round(PRIMA_DISPERSION * UPC_SUBSIDIADO_2025),
}
