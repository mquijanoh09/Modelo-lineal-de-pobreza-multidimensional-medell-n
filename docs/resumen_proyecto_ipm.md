# Resumen del proyecto — Optimización 1 (EAFIT)

## Proyecto

Modelo MILP para asignar inversión pública que minimice la pobreza multidimensional (IPM, metodología Alkire-Foster / IPM-Colombia).

- **Modelos 1 y 2 (Tomás):** información perfecta, decisión hogar por hogar.
- **Modelos 3 y 4 (Jerónimo):** focalización por zona.
- Los cuatro modelos se comparan en el paper.

## Decisiones tomadas

- **Datos:** base de microdatos **IPM 2025 del DANE**, versión **DEPARTAMENTAL**. Las 15 privaciones vienen ya calculadas.
- **Universo:** **Antioquia completa** (`DEPARTAMENTO == 5`), con las 3 zonas de `P3`. Es el mismo universo para los 4 modelos, por requisito de los Modelos 3 y 4.
- **No hay municipio** en la base: Medellín no es aislable.
- **Lenguaje:** Python + PuLP + HiGHS.
- **Costos:** en **pesos reales con fuentes**.

## Parámetros validados

| Símbolo | Fuente | Estado |
|---|---|---|
| $M_{ij}$ | 15 columnas de HOGARES | ✅ 1 = privado (incluido `empleo_formal`) |
| $w_j$ | 0.2 por dimensión, repartido: 0.1 / 0.05 / 0.04 | ✅ Reproduce `IPM` al 100% |
| $k$ | 1/3 (en la práctica, puntaje ≥ 0.34) | ✅ Reproduce `POBRE` al 100% |
| $HS_i$ | `PERSONAS` | ✅ |
| $HW_i$ | `FEX_C` (`FEXP` = `FEX_C` × `PERSONAS`) | ✅ |
| Zona $d$ | `P3` de VIVIENDAS (1 cabecera, 2 centro poblado, 3 rural disperso) | ✅ Replica el DANE: 9.91 / 6.30 / 22.44% |

## Línea base de Antioquia

Coincide con la calculada de forma independiente para los Modelos 3 y 4.

| Zona | Hogares | Pobres | Personas | H₀ | M0 |
|---|---|---|---|---|---|
| Cabecera | 1,670 | 127 | 5.85 M | 6.21% | 0.0252 |
| Centro poblado | 613 | 103 | 0.39 M | 17.91% | 0.0691 |
| Rural disperso | 1,449 | 293 | 1.00 M | 25.18% | 0.1060 |
| **Total** | **3,732** | **523** | **7.23 M** | **9.45%** | **0.0387** |

### Hallazgos clave

- El **100% de los pobres** tiene la privación de informalidad, en todas las zonas.
- Educación y trabajo explican el ~65% de la pobreza en las tres zonas. Vivienda pesa el doble en lo rural (19% contra 10%).
- El 77.6% de los hogares pobres sale con una sola intervención.
- El 53% de las personas pobres vive en la cabecera.

## Archivos del proyecto

```
utils_dane.py               funciones de lectura (leer, leer_cabecera, a_numero...)
02_validar_ipm.py           valida pesos, umbral y FEX_C
03_preparar_antioquia.py    pruebas A/B de P3 y genera data/processed/hogares_antioquia.csv
04_linea_base.py            H, A, M0, contribuciones y distancia al umbral, por zona
docs/reglas_conteo_personas.md  reglas validadas para contar personas afectadas (u_ij)
docs/informe_modelo1.md     informe del Modelo 1 (formulación, parámetros, supuestos, plan)
```

## Costos $EpF_j$ (2025, SMMLV = $1,423,500) — cerrados el 21-oct-2026

Zona urbana = `P3` 1 (cabecera). Zona rural = `P3` 2 o 3 (centro poblado y rural disperso).

| Indicador | Urbano | Rural | Unidad $u_{ij}$ | Fuente / intervención |
|---|---|---|---|---|
| pisos, paredes | $25.62 M | $35.2 M | hogar | Decreto 0413 de 2025 (locativo urbano, 18 SMMLV) / promedio de 416 subsidios de mejoramiento rural, 7 resoluciones Fonvivienda 2025 |
| hacinamiento | $31.3 M | $31.3 M | hogar | Mejoramiento modular, tope 22 SMMLV |
| acueducto | $11.72 M | $43.7 M | hogar | PCI, Decreto 1275 de 2021 (8.23 SMMLV) / acueducto veredal Minvivienda (Alpujarra 2022, ajustado a 2025) |
| alcantarillado | $11.72 M | $15.3 M | hogar | PCI, Decreto 1275 de 2021 / unidad sanitaria con pozo séptico (Minvivienda, Nariño 2022, ajustado a 2025) |
| aseguramiento_salud | $1.32 M | $1.32 M | persona ≥ 6 años no afiliada | UPC subsidiada |
| barreras_acceso_salud | $52,100 | $203,894 | persona con necesidad no atendida | 1 consulta ambulatoria de medicina general (SOAT 2025, código 39141, 4,51 UVB, Circular 25/2024) + prima de dispersión UPC (11.47 % = $151,794) en lo rural. Se descartan las 4 consultas (decidido por Martín 4-nov-2026) |
| analfabetismo | $0.96 M | $1.29 M | persona ≥ 15 años | CLEI ciclo 1, asignación SGP 2025 Antioquia |
| logro_educativo | $0.96 M | $1.29 M | ciclo CLEI por adulto (máximo 1 por año) | Asignación CLEI SGP 2025 por ciclo. El hogar sale si los años ganados cubren el déficit del promedio de 9 (restricción 11); solo 33 de 503 hogares pobres pueden salir en un año. Decidido por Martín 4-nov-2026 |
| empleo_formal | por hogar | por hogar | ver fórmula | $c_i = 2.73\,n^{ocup.\,sin\,pensión} + \sum_h EpV_h + 2.73\,n^{adultos\,sin\,cobertura}$ (último término solo si no hay ocupados) |
| desempleo_larga_duracion | $EpV_h$ | $EpV_h$ | desocupado (mín. 1) | Empleos para la Vida por perfil (Decreto 533 de 2024): 30 % 18–28 años, 20 % mujeres 29–56, 15 % hombres 29–61; aporte a pensión ($2.73 M) a mujeres ≥ 57 y hombres ≥ 62 |
| trabajo_infantil | $5.32 M | $5.32 M | niño 12–17 que trabaja | Externado media jornada ICBF, 6 meses × $886,058 (Res. 0001/2025, ficha I-12-122, act. Res. 0296/2025); sensibilidad baja: apoyo psicosocial $3.33 M. Reemplaza Renta Ciudadana (sin condición sobre trabajo infantil). Decidido por Martín 4-nov-2026 |
| inasistencia_escolar | $3.0 M / p | $3.0 M / p | hogar | Transferencia condicionada (Renta Ciudadana); p ∈ {0.37, 0.50, 0.75} |
| atencion_integral | $5.21 M | $5.21 M | niño de 0 a 5 años | CDI institucional tipo A (ICBF, Res. 5288/2025, Anexo 7) |
| rezago_escolar | $2.71–3.22 M | $3.52–4.18 M | niño 7–17 rezagado (asignación por alumno SGP 2025 por nivel, DNP) | Dos capas (vigente desde el 2-nov, ver `rezago/rezago_inasistencia_sevedu_documento.md`): el IPM binario no se toca y SevEdu mide el atraso de cada niño. El costo se cobra por niño en $z_{ks}$ (E1 cupo SGP; E2 CLEI primaria $958,431 / $1,286,194 por ciclo); $x_{i,rez}$ no tiene costo propio y se liga con (10a)/(10b). Con las reglas oficiales ningún niño sale del rezago binario en un año. La Opción C quedó descartada |

Sensibilidades previstas: pisos/paredes rural $31.3–36.8 M; acueducto rural $9.7 M (BID, cota baja); empleo_formal ×0.5–×2 y caso 3 opción B ($5.12 M por hogar);
barreras de salud ×0.5–×5; inasistencia p = 0.37 / 0.50 / 0.75; rezago con E3 (CLEI secundaria, supuesto atraso ≥ 2) y ρ_e 20 %; trabajo infantil con apoyo psicosocial ($3.33 M); $u_{ij} = 1$ (como el paper).

## Decisiones de modelación acordadas

- **Costo real del hogar $i$ en el indicador $j$:** $EpF_j^{\,zona(i)} \cdot u_{ij} \cdot HW_i$, con $u_{ij}$ = personas afectadas
  (reglas validadas en `docs/reglas_conteo_personas.md`). Es una mejora frente al paper (Con 4 usa $u_{ij}=1$); $u_{ij}=1$ queda como sensibilidad.
- El conteo de personas se calcula una sola vez (`05_conteo_personas.py`) y lo comparten los 4 modelos.
- Solo importan los hogares pobres (reducción exacta del problema).
- Horizonte de **un año** para el presupuesto $B$.
- **Atención integral:** se mantiene el CDI en todas las zonas. Los microdatos muestran que quedarse en casa con el padre o la madre (`P51` = 2) no es privación de cuidado, pero no permiten saber qué componente (salud, nutrición o cuidado) priva a cada niño.
- **Inasistencia:** el Estado paga de enero a diciembre y el informe de asistencia decide la renovación el año siguiente.
  Optimización con costo efectivo $3.0/p$; evaluación del plan con Monte Carlo (~200 corridas, cada niño cumple con prob. $p$).
- **Equidad:** restricción de reducción mínima por zona, con $y_i = 1$ si el hogar **sale** de la pobreza:

  $$\sum_{i \in d} HW_i \, HS_i \, y_i \ge r \cdot \text{Pobres}_d^0 \qquad \forall d$$

  con $r$ como parámetro ($r = 0$ recupera el modelo base). Siempre reportar resultados por zona.
- **Rango de presupuesto (con los costos base y p = 0.5):** sacar de la pobreza a los 523 hogares pobres cuesta como mínimo ≈ **$0.50 billones**;
  quitar todas las privaciones intervenibles cuesta ≈ $7.29 billones. Los experimentos del Modelo 1 deben barrer $B$ entre 0 y ~$0.5 billones.

## Pendientes

1. ~~Decidir el objetivo~~ **Decidido (26-oct-2026).** **Objetivo del Modelo 1 (decidido 26-oct-2026, perspectiva de equidad):** H principal con techo de severidad y severidad como desempate
($\max \sum p_iy_i - \lambda \sum p_iq_i$ s.a. $\sum p_iq_i \le (1-\rho)\,\text{Sev}_0$, con $q_i = s_i^2$ linealizado por tangentes y $p_i = HW_iHS_i$).
bigM por hogar $M_i = c_i^0 - 0.33$; se quitaron $C_i$ y la restricción (3). Detalle completo en `docs/informe_modelo1.md` §3.4 y §4;
contexto de por qué en `graphify-out/perspectiva_equidad/GRAPH_REPORT.md`.
   Falta decidir si el desempate se programa con λ o en dos etapas (recomendado: dos etapas) y contárselo a Jerónimo.
   **Severidad educativa (28-oct-2026, propuesta para los 4 modelos):** techo $\sum_k HW_k(a_k^0 - z_k)^2 \le (1-\rho_e)\,\text{SevEdu}_0$ sobre los años de atraso de los 215 niños rezagados ($\text{SevEdu}_0 \approx 1{,}291{,}034$), lineal porque $z_k$ es binaria; ver `docs/informe_modelo1.md` §3.5. Pendiente de acordar con Jerónimo.
2. **Acordar con Jerónimo** la unidad $u_{ij}$, el uso de $HW_i$, la tabla de costos compartida y la convención de $y_i$ ("sale").
3. Escribir `05_conteo_personas.py` (reglas de `docs/reglas_conteo_personas.md`) y `06_parametros.py`.
4. ~~Verificar el factor de inflación 2015→2025~~ Verificado (30-oct): ×1.645 dic-2015→dic-2024 con el IPC del DANE. Costos revisados con fuente oficial el 30-oct; **recalcular** el rango de presupuesto ($0.50 y $7.29 billones) con los costos nuevos.

## Siguientes scripts

```
05_conteo_personas.py      u_ij por hogar desde el archivo de PERSONAS (validado contra HOGARES)
06_parametros.py           costos urbanos/rurales, unidades, pesos y k en un solo lugar
07_eficiencia_por_zona.py  diagnóstico HS_i / c_i por zona
08_modelo1.py              presupuesto fijo, con parámetro r de equidad
09_modelo2.py              meta política, con metas por zona
```
