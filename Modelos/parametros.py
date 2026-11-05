"""
parametros.py
Parámetros compartidos por los 4 modelos (IPM, costos, escenarios).

Reglas del proyecto:
  - Cada costo lleva su fuente oficial en el comentario (informe §6).
  - Ningún modelo escribe números a mano: todos los leen de aquí.
  - Los costos son por UNIDAD (por hogar, por persona, por niño...). El costo
    real de un hogar es c_ij = EpF_j(zona) * u_ij * HW_i y se arma en el 05.

Lo que depende de los datos (Sev0, A_i, M_i, SevEdu^N_1,sin, rango de B) NO
vive aquí: se calcula en datos_modelo.py a partir de la ECV.
"""

# ==================================================================
# 1. IPM oficial (DANE): indicadores, pesos y umbral
# ==================================================================
DIMENSIONES = {
    "Educación":        ["logro_educativo", "analfabetismo"],
    "Niñez y juventud": ["inasistencia_escolar", "rezago_escolar",
                         "atencion_integral", "trabajo_infantil"],
    "Trabajo":          ["desempleo_larga_duracion", "empleo_formal"],
    "Salud":            ["aseguramiento_salud", "barreras_acceso_salud"],
    "Vivienda":         ["acueducto", "alcantarillado", "pisos",
                         "paredes", "hacinamiento"],
}
# Cada dimensión pesa 0.2 y se reparte por igual entre sus indicadores.
PESOS = {ind: 0.2 / len(inds) for inds in DIMENSIONES.values() for ind in inds}
INDICADORES = list(PESOS)        # mismo orden que IND de m34_datos.py
K = 1 / 3                        # pobre <=> puntaje >= 1/3
K_GRID = 0.33                    # "< 1/3" se escribe "<= 0.33" (pesos múltiplos de 0.01)

ZONAS = {1: "Cabecera", 2: "Centro poblado", 3: "Rural disperso"}
SEMILLA = 2026                   # misma semilla de Jerónimo (m34_datos.py)


def zona_costo(p3):
    """Zona de costo: urbano = cabecera (P3 = 1); rural = P3 2 o 3 (informe §6)."""
    return "urbano" if p3 == 1 else "rural"


# ==================================================================
# 2. Valores de referencia 2025
# ==================================================================
SMMLV_2025 = 1_423_500           # Decreto 1572 de 2024
UPC_SUBSIDIADO_2025 = 1_323_403.20   # Res. Minsalud 2717 de 2024
IPC_2022_A_2025 = 1.26           # factor usado en el informe §6.4 para llevar obras de 2022 a 2025


# ==================================================================
# 3. Vivienda y servicios (por hogar)
# ==================================================================
# Pisos y paredes urbano: tope del mejoramiento locativo, 18 SMMLV
#   (Decreto 0413 de 2025, art. 2.1.1.7.10, categoría A).
# Pisos y paredes rural: promedio de 416 subsidios rurales de Fonvivienda 2025
#   (Res. 0383, 0440, 0588, 0794, 1059, 1240 y 1284), informe §6.3.
COSTO_PISOS_PAREDES = {"urbano": 18 * SMMLV_2025, "rural": 35_200_000}

# Hacinamiento: mejoramiento modular, 22 SMMLV (Decreto 0413 de 2025, cat. E).
COSTO_HACINAMIENTO = {"urbano": 22 * SMMLV_2025, "rural": 22 * SMMLV_2025}

# Acueducto y alcantarillado urbanos: PCI, 8.23 SMMLV (Decreto 1275 de 2021); cubre ambos.
_PCI_URBANO = 8.23 * SMMLV_2025
# Acueducto rural: acueducto veredal de Minvivienda en Alpujarra (2022):
#   $5,789 M / 551 personas x 3.3 personas por hogar, llevado a 2025.
_ACUEDUCTO_RURAL = 5_789e6 / 551 * 3.3 * IPC_2022_A_2025
# Alcantarillado rural: unidad sanitaria con pozo séptico de Minvivienda
#   (La Cruz y Los Andes, Nariño, 2022): $5,700 M / 470 unidades, llevado a 2025.
_ALCANTARILLADO_RURAL = 5_700e6 / 470 * IPC_2022_A_2025

COSTO_ACUEDUCTO = {"urbano": _PCI_URBANO, "rural": _ACUEDUCTO_RURAL}
COSTO_ALCANTARILLADO = {"urbano": _PCI_URBANO, "rural": _ALCANTARILLADO_RURAL}


# ==================================================================
# 4. Salud (por persona)
# ==================================================================
# Aseguramiento: UPC del régimen subsidiado 2025 (Res. 2717 de 2024).
COSTO_ASEGURAMIENTO = {"urbano": UPC_SUBSIDIADO_2025, "rural": UPC_SUBSIDIADO_2025}

# Barreras de acceso (informe §6.2, decidido por Martín el 4-nov-2026):
# 1 consulta de medicina general, tarifa SOAT 2025, código 39141:
#   4,51 UVB = $52,100 (Circular Externa 25 de 2024, Minsalud, p. 34).
# Rural: + prima adicional por dispersión geográfica, 11.47 % x UPC-S (Res. 2717 de 2024).
CONSULTA_MEDICINA_GENERAL = 52_100
PRIMA_DISPERSION = 0.1147
COSTO_BARRERAS_SALUD = {
    "urbano": CONSULTA_MEDICINA_GENERAL,
    "rural": CONSULTA_MEDICINA_GENERAL + round(PRIMA_DISPERSION * UPC_SUBSIDIADO_2025),
}


# ==================================================================
# 5. Trabajo (empleo formal y desempleo de larga duración)
# ==================================================================
# Aporte a pensión: 16 % del IBC (Ley 797 de 2003, art. 7) x 12 meses de 1 SMMLV.
COSTO_APORTE_PENSION = 0.16 * 12 * SMMLV_2025          # 2,733,120 por persona

# Empleos para la Vida (Decreto 533 de 2024, art. 2.2.6.1.10.3): % mensual de
# 1 SMMLV pagado al empleador por 12 meses, según el perfil del desocupado.
EPV_PORCENTAJE = {"joven_18_28": 0.30, "mujer_29_56": 0.20, "hombre_29_61": 0.15}
COSTO_EPV = {perfil: pct * 12 * SMMLV_2025 for perfil, pct in EPV_PORCENTAJE.items()}
# Mujer >= 57 u hombre >= 62 (edad de pensión): aporte a pensión (informe §6.5).
EDAD_PENSION = {"mujer": 57, "hombre": 62}
# Hogar privado en desempleo sin desocupado identificable: la tarifa más alta (30 %),
# supuesto conservador (docs/reglas_conteo_personas.md).
COSTO_DESEMPLEO_SIN_IDENTIFICAR = COSTO_EPV["joven_18_28"]


def costo_desocupado(edad, mujer):
    """EpV_h: costo de formalizar a un desocupado según su perfil (informe §6.5)."""
    if edad >= (EDAD_PENSION["mujer"] if mujer else EDAD_PENSION["hombre"]):
        return COSTO_APORTE_PENSION
    if edad <= 28:
        return COSTO_EPV["joven_18_28"]
    return COSTO_EPV["mujer_29_56"] if mujer else COSTO_EPV["hombre_29_61"]


# ==================================================================
# 6. Niñez y juventud
# ==================================================================
# Atención integral: CDI institucional tipo A, por niño de 0 a 5 años
#   (ICBF, Res. 5288 de 2025, Anexo 7), mismo valor en las tres zonas.
COSTO_ATENCION_INTEGRAL = {"urbano": 5_210_277, "rural": 5_210_277}

# Trabajo infantil (informe §6.7b, decidido por Martín el 4-nov-2026)
# Externado de media jornada del ICBF (SIM 420212), 4 h diarias en contrajornada.
# Fuente: Res. ICBF 0001 de 2025, ficha I-12-122, actualizada por la
#         Res. 0296 del 31-ene-2025 (costo cupo mes, febrero a diciembre).
# Cada cupo opera 6 meses y atiende a 2 niños al año -> 6 meses por niño.
# Unidad: por niño de 12 a 17 años que trabaja, mismo valor urbano y rural.
# Supuesto declarado: los 6 meses bastan para eliminar la privación.
TI_COSTO_CUPO_MES_EXTERNADO = 886_058      # SIM 420212
TI_COSTO_CUPO_MES_PSICOSOCIAL = 554_907    # SIM 420213 (sensibilidad baja)
TI_MESES_POR_NINO = 6
COSTO_TRABAJO_INFANTIL = TI_COSTO_CUPO_MES_EXTERNADO * TI_MESES_POR_NINO             # 5,316,348
COSTO_TRABAJO_INFANTIL_SENS_BAJA = TI_COSTO_CUPO_MES_PSICOSOCIAL * TI_MESES_POR_NINO  # 3,329,442

# Cupo escolar: asignación por alumno SGP 2025, ETC Antioquia
#   (DNP, Anexo 1 DD SGP-96-2025, fila "05 ANTIOQUIA"). Se usa en E1 (regreso).
CUPO_SGP = {
    "urbano": {"primaria": 2_709_038, "secundaria": 3_047_670, "media": 3_216_987},
    "rural":  {"primaria": 3_521_752, "secundaria": 3_961_971, "media": 4_182_081},
}


def nivel_grado(grado):
    """Nivel educativo del grado que cursaría el niño (1-5 primaria, 6-9 secundaria, 10-11 media)."""
    if grado <= 5:
        return "primaria"
    return "secundaria" if grado <= 9 else "media"


# Renta Ciudadana (E1): $500,000 por ciclo x 6 ciclos en 2025 (Prosperidad Social),
# pagada una vez por hogar. p = cumplimiento del ciclo 4 de 2025 (Prosperidad Social).
RENTA_CIUDADANA_ANUAL = 500_000 * 6       # 3,000,000 por hogar
P_CUMPLIMIENTO = 0.369


# ==================================================================
# 7. Logro educativo y analfabetismo (informe §6.9, decidido por Martín el 4-nov-2026)
# ==================================================================
# CLEI: asignación por alumno por ciclo, SGP 2025 Antioquia (DNP, Anexo 1 DD SGP-96-2025).
# Cada ciclo dura al menos 40 semanas (Decreto 1075/2015, art. 2.3.3.5.3.4.4):
# como máximo UN ciclo por adulto en el año (variable v_a). También se usa en E2.
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


# ==================================================================
# 8. Tabla EpF por indicador "simple" (informe §6.8)
#    Rezago, inasistencia, logro y analfabetismo NO están aquí: se pagan por
#    niño o por adulto con las variables z, t y v (formulación §5).
# ==================================================================
UNIDAD = {   # qué cuenta u_ij (docs/reglas_conteo_personas.md)
    "pisos": "hogar", "paredes": "hogar", "hacinamiento": "hogar",
    "acueducto": "hogar", "alcantarillado": "hogar",
    "aseguramiento_salud": "persona", "barreras_acceso_salud": "persona",
    "atencion_integral": "niño 0-5", "trabajo_infantil": "niño 12-17 que trabaja",
    "empleo_formal": "costo por hogar (3 casos)", "desempleo_larga_duracion": "desocupado",
}
EPF_BASE = {
    "pisos": COSTO_PISOS_PAREDES,
    "paredes": COSTO_PISOS_PAREDES,
    "hacinamiento": COSTO_HACINAMIENTO,
    "acueducto": COSTO_ACUEDUCTO,
    "alcantarillado": COSTO_ALCANTARILLADO,
    "aseguramiento_salud": COSTO_ASEGURAMIENTO,
    "barreras_acceso_salud": COSTO_BARRERAS_SALUD,
    "atencion_integral": COSTO_ATENCION_INTEGRAL,
    "trabajo_infantil": {"urbano": COSTO_TRABAJO_INFANTIL, "rural": COSTO_TRABAJO_INFANTIL},
    # empleo_formal y desempleo se costean persona por persona en el 05
    # (COSTO_APORTE_PENSION y costo_desocupado), por eso no tienen EpF fijo.
}
INDICADORES_POR_PERSONA_O_NINO = ["logro_educativo", "analfabetismo",
                                  "inasistencia_escolar", "rezago_escolar"]


# ==================================================================
# 9. Escenarios (caso base y sensibilidades)
# ==================================================================
CASO_BASE = {
    "nombre": "base",
    "p": P_CUMPLIMIENTO,          # cumplimiento de Renta Ciudadana
    "usar_E3": False,             # CLEI de secundaria fuera (no hay años por fuera en la ECV)
    "u_igual_1": False,           # True = una intervención por hogar (versión del paper)
    "rho_e": 0.14,                # techo de SevEdu (decidido 2-nov) + cobertura art. 67 (E-7)
    "cobertura_art67": True,
    "ap": 1.0,                    # probabilidad de aprobar si asiste (pendiente MEN)
    "costo_trabajo_infantil": COSTO_TRABAJO_INFANTIL,
    "acueducto_rural": _ACUEDUCTO_RURAL,
}

SENSIBILIDADES = {
    "p_050": {"p": 0.50},
    "p_075": {"p": 0.75},
    "con_E3": {"usar_E3": True, "rho_e": 0.20},          # supuesto: atraso >= 2 => 2 años por fuera
    "u_1": {"u_igual_1": True},
    "ti_psicosocial": {"costo_trabajo_infantil": COSTO_TRABAJO_INFANTIL_SENS_BAJA},
    # Acueducto rural bajo: aljibe propio con bomba manual, piloto BID Guachené 2015
    # (x1.65 a 2025; fuente técnica no gubernamental), informe §6.4.
    "acueducto_bid": {"acueducto_rural": 9_700_000},
}


def escenario(nombre="base"):
    """Devuelve el diccionario del escenario: el caso base con los cambios de la sensibilidad."""
    if nombre == "base":
        return dict(CASO_BASE)
    return {**CASO_BASE, **SENSIBILIDADES[nombre], "nombre": nombre}


def tabla_epf(esc):
    """EpF_j por zona para un escenario: {indicador: {"urbano": $, "rural": $}}."""
    tabla = {j: dict(v) for j, v in EPF_BASE.items()}
    tabla["trabajo_infantil"] = {"urbano": esc["costo_trabajo_infantil"],
                                 "rural": esc["costo_trabajo_infantil"]}
    tabla["acueducto"]["rural"] = esc["acueducto_rural"]
    return tabla


# Mallas de los barridos. B se fija DESPUÉS de calcular, con los datos, el costo
# mínimo de sacar a los 523 hogares (validación 2 de la sección 5 del plan).
MALLA_R = [0.0, 0.05, 0.10, 0.15, 0.20]
MALLA_RHO_E = [0.0, 0.05, 0.10, 0.118, 0.14]     # 0.20 solo con E3
MALLA_B = None                                   # pendiente: depende del rango de B


# ==================================================================
# 10. Modelo 2: min costo s.a. meta de M0 (modelo2/formulacion_modelo2.md)
#     Decisiones en docs/justificacion_decisiones_modelo2.md
# ==================================================================
# Metas de reducción relativa de M0 (m = MPI_r del paper): las mismas de
# Jerónimo en M3/M4, para que los modelos 2 a 4 se comparen igual.
METAS_M2 = [0.05, 0.10, 0.20]
PASO_MALLA_M2 = 0.025            # paso del barrido fino de la curva costo vs. meta

# Opciones propias del Modelo 2 (se suman al escenario común de la sección 9).
CASO_BASE_M2 = {
    "meta_por_zona": True,       # D-M2-3: la meta se exige en cada zona P3 (implica la global)
    "usar_sevedu": False,        # D-M2-2: SevEdu (E-5) solo como sensibilidad; E-7 siempre activa
}
SENSIBILIDADES_M2 = {
    "meta_global": {"meta_por_zona": False},   # cuánto cuesta la equidad territorial
    "con_sevedu": {"usar_sevedu": True},       # usa esc["rho_e"] (0.14; 0.20 con E3)
}

# Solver (F2-2): una sola etapa. Con un costo de ~$100 mil millones, gap 1e-4
# deja ~$10 M de holgura (un hogar); 1e-6 la baja a ~$0.1 M (igual que M3/M4).
SOLVER_M2 = {"gap_rel": 1e-6, "time_limit": 300}
# Barridos: metas intermedias (30-80 %) pueden tardar minutos en cerrar el gap 1e-6.
# En los barridos se corta a 60 s y se reporta el gap alcanzado de cada punto.
SOLVER_M2_BARRIDO = {"gap_rel": 1e-6, "time_limit": 60}

# F2-1: el objetivo se escribe en millones de pesos para que los coeficientes
# del MILP queden en escalas parecidas; los resultados se reportan en pesos.
ESCALA_COSTO = 1e6


def escenario_m2(nombre_comun="base", nombre_m2="base"):
    """Escenario del Modelo 2 = escenario común (p, E3, u = 1, ...) + opciones del M2.

    Así se combinan, por ejemplo, p = 0.50 con la meta solo global:
    escenario_m2("p_050", "meta_global").
    """
    esc = escenario(nombre_comun)
    esc.update(CASO_BASE_M2)
    if nombre_m2 != "base":
        esc.update(SENSIBILIDADES_M2[nombre_m2])
    esc["nombre"] = f"{esc['nombre']}|m2_{nombre_m2}"
    return esc


def malla_m2(m_max, paso=PASO_MALLA_M2):
    """Metas del barrido fino: 0, paso, 2*paso, ... sin pasar de m_max.

    m_max sale de Modelo2.meta_maxima() (la zona que menos puede bajar M0),
    porque una meta mayor deja el caso base infactible.
    """
    n = int(m_max / paso + 1e-9)
    return [round(i * paso, 6) for i in range(n + 1)]


# ==================================================================
# 11. Modelo 1: presupuesto fijo, max H en dos etapas (D1)
#     Decisiones en docs/justificacion_decisiones.md
# ==================================================================
# D1: dos etapas. Etapa 1 max sum p_i y_i; etapa 2 min sum p_i q_i con sum p_i y_i >= H*.
# Con ~683 mil pobres, gap 1e-4 dejaría ~68 personas de holgura; 1e-6 la baja a < 1.
SOLVER_M1 = {"gap_rel": 1e-6, "time_limit": 300}
# Tolerancia relativa al fijar H* en la etapa 2 (H* es la incumbente de la etapa 1, así que es factible;
# el margen solo evita que el redondeo de HiGHS la vuelva infactible).
TOL_H_ETAPA2 = 1e-9
# Malla de r (equidad por zona) y de rho (techo de severidad): se barren entre sus extremos.
# MALLA_B se arma en 08_modelo1_barridos.py como B = B_piso + f (B_sat - B_piso), porque depende
# de los datos (P5): B_piso = costo con H = 0 (E-7 + SevEdu) y B_sat = mínimo para el H máximo.
FRACCIONES_B = [0.0, 0.05, 0.10, 0.20, 0.30, 0.50, 0.75, 1.00]
PASOS_RHO = 5                    # puntos interiores del barrido de rho entre 0 y rho_max(B)
# B de referencia para los barridos de r y rho y las sensibilidades: fracción del rango B_piso-B_sat.
# PROVISIONAL (5-nov-2026, al completar el código): no hay decisión de Martín sobre el B
# del caso base; 0.30 queda en la zona de la curva B -> H donde todavía hay rendimientos
# decrecientes claros. Cambiar aquí si se acuerda otro valor.
FRACCION_B_REF = 0.30


# ==================================================================
# Prueba rápida: python parametros.py
# ==================================================================
if __name__ == "__main__":
    assert abs(sum(PESOS.values()) - 1) < 1e-12, "los pesos no suman 1"
    assert len(INDICADORES) == 15
    print(f"Pesos: suman {sum(PESOS.values()):.2f}, {len(INDICADORES)} indicadores, k = {K:.4f}")
    print(f"\n{'Indicador':<26}{'Urbano':>14}{'Rural':>14}   Unidad")
    for j, v in tabla_epf(escenario()).items():
        print(f"{j:<26}{v['urbano']:>14,.0f}{v['rural']:>14,.0f}   {UNIDAD[j]}")
    print(f"\nAporte a pensión:         {COSTO_APORTE_PENSION:>14,.0f} por persona")
    for perfil, c in COSTO_EPV.items():
        print(f"Empleos para la Vida {perfil:<12}{c:>10,.0f} por desocupado")
    print(f"Renta Ciudadana / p:      {RENTA_CIUDADANA_ANUAL / P_CUMPLIMIENTO:>14,.0f} por hogar (p = {P_CUMPLIMIENTO})")
    print(f"Ciclo CLEI:               {COSTO_CICLO_CLEI['urbano']:>14,.0f} urbano / {COSTO_CICLO_CLEI['rural']:,.0f} rural")
    print(f"\nEscenarios: base + {list(SENSIBILIDADES)}")
    e2 = escenario_m2("p_050", "meta_global")
    assert e2["p"] == 0.50 and e2["meta_por_zona"] is False and e2["usar_sevedu"] is False
    assert escenario_m2()["meta_por_zona"] is True
    assert malla_m2(0.10) == [0.0, 0.025, 0.05, 0.075, 0.1]
    print(f"Modelo 2: metas {METAS_M2}, opciones {CASO_BASE_M2}, solver {SOLVER_M2}")
