# Contexto de datos para los 4 modelos

Actualizado: 30-oct-2026 · Autor: Martín (Modelos 1 y 2) · Para: Jerónimo (Modelos 3 y 4)

Este archivo dice qué datos tengo, qué concluí de ellos y qué falta acordar para que los 4 modelos usen las mismas bases.
Jerónimo: si algo está mal o te falta, escríbelo en la sección **Notas de Jerónimo** al final (o en un archivo `NOTAS_JERONIMO.md` en esta branch).

---

## 1. Lo que ya está hecho y validado

| Pieza | Estado | Dónde |
|---|---|---|
| Microdatos IPM 2025 del DANE, versión departamental | En el repo | `data/DANE/` |
| Validación de pesos, umbral y factor de expansión | Hecho | `02_validar_ipm.py` |
| Universo de Antioquia con las 3 zonas de `P3` | Hecho (sin commit todavía) | `03_preparar_antioquia.py` → `data/processed/hogares_antioquia.csv` |
| Línea base por zona (H, A, M0, contribuciones) | Hecho | `04_linea_base.py` |
| Reglas para contar personas afectadas (u_ij) | Validadas contra HOGARES en los 87.060 hogares del país | `docs/reglas_conteo_personas.md` (sin commit todavía) |
| Costos EpF_j urbanos y rurales con fuentes | Cerrados el 21-oct-2026 | sección 4 de este archivo |
| Conteo u_ij (`05_conteo_personas.py`) | **Por hacer** | — |
| Parámetros compartidos (`parametros.py`) | **Por hacer** | — |

### Parámetros validados

| Símbolo | Columna | Resultado |
|---|---|---|
| M_ij | 15 columnas de privación de HOGARES (1 = privado) | — |
| w_j | 0,2 por dimensión: 0,10 / 0,05 / 0,04 | Reproduce `IPM` al 100 % |
| k | Pobre ⇔ puntaje ≥ 0,34 (en el modelo, "sale" ⇔ puntaje ≤ 0,33) | Reproduce `POBRE` al 100 % |
| HS_i | `PERSONAS` | — |
| HW_i | `FEX_C` (`FEXP` = `FEX_C` × `PERSONAS`) | — |
| Zona d | `P3` de VIVIENDAS: 1 cabecera, 2 centro poblado, 3 rural disperso | Replica al DANE: 9,91 / 6,30 / 22,44 % |
| ID del hogar | `ID_HOGAR = DIRECTORIO + "_" + SECUENCIA_P` | Igual que `ID` en `05_modelo3.py` de la branch Modelo3 |

### Línea base de Antioquia

| Zona | Hogares | Pobres | Personas | H₀ | A₀ | M0 |
|---|---|---|---|---|---|---|
| Cabecera | 1.670 | 127 | 5,85 M | 6,21 % | 40,58 % | 0,0252 |
| Centro poblado | 613 | 103 | 0,39 M | 17,91 % | 38,56 % | 0,0691 |
| Rural disperso | 1.449 | 293 | 1,00 M | 25,18 % | 42,11 % | 0,1060 |
| **Total** | **3.732** | **523** | **7,23 M** | **9,45 %** | **40,94 %** | **0,0387** |

Severidad inicial (sobre los pobres, sin censurar): Sev₀ ≈ 117.908. Severidad educativa inicial: SevEdu₀ ≈ 1.291.034 (215 niños rezagados en hogares pobres).

---

## 2. Lo que concluí de los datos

1. **El 100 % de los pobres es informal** (privación de `empleo_formal`), en las tres zonas.
2. **Educación y trabajo explican ~65 % de la pobreza** en las tres zonas. Vivienda pesa el doble en lo rural (19 % contra 10 %).
3. **El 77,6 % de los hogares pobres sale con una sola intervención** y 135 hogares están justo en 0,34. Un modelo de H puro gasta en los "menos pobres"; por eso el Modelo 1 tiene techo de severidad.
4. **El 53 % de las personas pobres vive en la cabecera**, aunque la incidencia es mucho mayor en lo rural.
5. **No hay municipio en la base:** Medellín no se puede aislar. El universo es Antioquia completa para los 4 modelos.
6. **Las reglas de conteo valen para pobres y no pobres,** porque se validaron con todos los hogares del país. Dos indicadores son aproximaciones: `atencion_integral` (96,5 % de coincidencia; se cuentan los niños de 0 a 5 años) y `desempleo_larga_duracion` (86,5 %; desocupados del hogar, mínimo 1).
7. **Rezago escolar:** de 215 niños rezagados en hogares pobres, 83 tienen 1 año de atraso, 47 tienen 2, 27 tienen 3, 26 tienen 4 y 32 tienen 5 o más. En un año solo se nivela a los de 1 año de atraso.
8. **Rango de presupuesto** (costos base, p = 0,5): sacar de la pobreza a los 523 hogares pobres cuesta como mínimo ≈ $0,50 billones; quitar todas las privaciones intervenibles cuesta ≈ $7,29 billones.

---

## 3. Cómo se van a compartir los datos (propuesta)

La idea: **el 05 cuenta y `parametros.py` pone los precios.** El 05 se corre una sola vez; las sensibilidades solo cambian el escenario.

### Salidas de `05_conteo_personas.py` (en `data/processed/`), para los 3.732 hogares

| Archivo | Una fila por | Columnas |
|---|---|---|
| `conteo_pares.csv` | Par hogar-indicador con M_ij = 1 | ID_HOGAR, P3, zona_costo, pobre, FEX_C, PERSONAS, indicador, u_ij, u_imputado, intervenible |
| `empleo_componentes.csv` | Hogar privado en empleo formal o desempleo | ID_HOGAR, tiene_ocupados, n_ocup_sin_pension, n_desoc_18_28, n_desoc_mujer_29_56, n_desoc_hombre_29_61, n_desoc_pension, n_adultos_sin_cobertura |
| `ninos_rezago.csv` | Niño de 7 a 17 años rezagado | ID_HOGAR, P3, pobre, FEX_C, edad, atraso |

- **u_ij solo existe donde M_ij = 1.** Si la regla da 0 personas pero el DANE marca la privación, u_ij = 1 y `u_imputado = 1`.
- `intervenible = 0` en rezago si algún niño del hogar tiene 2 o más años de atraso (opción C). En el modelo: (10a) x_i,rez ≤ z_k para cada niño con a_k⁰ = 1 y (10b) x_i,rez = 0 si algún niño tiene a_k⁰ ≥ 2. El rezago se paga por niño nivelado, $6,3 M × HW_k, y SevEdu usa α = 2.
- `zona_costo`: urbano = `P3` 1; rural = `P3` 2 o 3. La equidad y los reportes usan las 3 zonas de `P3`.

### Qué vive en `parametros.py` (no `06_parametros.py`: Python no importa módulos cuyo nombre empieza por número)

- `DIMENSIONES`, `PESOS`, `INDICADORES`, umbral k.
- `SMMLV`, tabla `EPF[indicador] = (urbano, rural)` y tarifas de Empleos para la Vida.
- `ESCENARIOS` (base, u_ij = 1, p = 0,37 / 0,75, rezago A / B, empleo ×0,5 / ×2, caso 3 opción B).
- `tabla_costos(escenario)`: devuelve la tabla larga (ID_HOGAR, indicador, u_ij, costo_ij) con costo_ij = EpF_j^zona · u_ij · HW_i.
- Malla de B, r, ρ, ρ_e y la semilla del sorteo.

---

## 4. Costos EpF_j (2025, SMMLV = $1.423.500)

| Indicador | Urbano | Rural | Unidad u_ij | Intervención |
|---|---|---|---|---|
| pisos, paredes | $20,5 M | $35,2 M | hogar | Cambia Mi Casa / mejoramiento rural Fonvivienda |
| hacinamiento | $31,3 M | $31,3 M | hogar | Mejoramiento modular (22 SMMLV) |
| acueducto | $9,7 M | $9,7 M | hogar | PCI / aljibe con bomba manual |
| alcantarillado | $9,7 M | $12,1 M | hogar | PCI / unidad sanitaria con pozo séptico |
| aseguramiento_salud | $1,32 M | $1,32 M | persona ≥ 6 años no afiliada | UPC subsidiada |
| barreras_acceso_salud | $0,21 M | $0,36 M | persona con necesidad no atendida | 4 consultas + prima de dispersión rural |
| analfabetismo | $0,78 M | $0,78 M | persona ≥ 15 años | Programa Nacional de Alfabetización |
| logro_educativo | $2,35 M | $2,35 M | adulto ≥ 15 con < 9 años | 3 ciclos CLEI |
| empleo_formal | por hogar | por hogar | fórmula | $2,73 M × ocupados sin pensión + Σ EpV_h desocupados + $2,73 M × adultos sin cobertura (solo si no hay ocupados) |
| desempleo_larga_duracion | EpV_h | EpV_h | desocupado (mín. 1) | Empleos para la Vida (Decreto 533/2024): 30 % 18–28, 20 % mujeres 29–56, 15 % hombres 29–61; pensión a mujeres ≥ 57 y hombres ≥ 62 |
| trabajo_infantil | $3,0 M | $3,0 M | hogar | Renta Ciudadana |
| inasistencia_escolar | $3,0 M / p | $3,0 M / p | hogar | Transferencia condicionada; p ∈ {0,37; 0,50; 0,75} |
| atencion_integral | $5,21 M | $5,21 M | niño de 0 a 5 años | CDI institucional (ICBF) |
| rezago_escolar | $6,3 M | $6,3 M | niño rezagado | Solo intervenible con 1 año de atraso (opción C) |

---

## 5. Convenciones acordadas

- y_i = 1 ⇔ el hogar **sale** de la pobreza (igual que b1_i del paper).
- HW_i siempre multiplica el costo; HS_i nunca, porque las personas ya están en u_ij.
- Reportamos H, A, M0 y severidad, siempre por zona (`P3`) y total. Severidad sobre los pobres iniciales y sin censurar.
- Desempate en dos etapas: (1) max personas que salen; (2) min severidad s.a. personas que salen ≥ H*.
- Sensibilidades mínimas que corremos los dos: caso base y u_ij = 1.

---

## 6. Pendientes y preguntas para Jerónimo

1. **Severidad educativa en los 4 modelos.** ¿La adoptamos? Propuesta: K = los 215 niños de hogares pobres, ρ_e = 29 % como caso central. Si sí, el sorteo de rezago debería ser por niño, porque pagar a un niño con 3 años de atraso no cambia H pero sí baja SevEdu.
2. **u_ij = 1 en empleo formal y desempleo.** Propuesta: $2,73 M por hogar en empleo formal y $5,12 M en desempleo.
3. **Inasistencia (3,0/p) con el sorteo.** Sugerencia: en la optimización el sorteo queda fijo y el costo es 3,0/p; el cumplimiento entra solo en el Monte Carlo de evaluación. Tú decides.
4. **Conteo de los no pobres:** lo programo yo en el mismo 05 (es el mismo código sin filtrar por `pobre`). Te pido revisarlo cuando lo suba.
5. **Branch Modelo3:** `05_modelo3.py` define sus propios `IND`, `W` y `SEMILLA = 2026`. Cuando exista `parametros.py`, habría que importarlos de ahí. Además el nombre `05_` choca con `05_conteo_personas.py`; ¿lo renumeramos?

---

## Notas de Jerónimo

_(Escribe aquí lo que necesites que agregue, cambie o corrija.)_
