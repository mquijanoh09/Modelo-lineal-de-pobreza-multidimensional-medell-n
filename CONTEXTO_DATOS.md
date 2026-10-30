# Contexto de datos para los 4 modelos

Actualizado: 30-oct-2026 · Autor: Martín (Modelos 1 y 2) · Para: Jerónimo (Modelos 3 y 4)

Este archivo dice qué datos tengo, qué concluí de ellos y qué falta acordar para que los 4 modelos usen las mismas bases.
Jerónimo: si algo está mal o te falta, escríbelo en la sección **Notas de Jerónimo** al final (o en un archivo `NOTAS_JERONIMO.md` en esta branch).

**Grafo de conocimiento:** `graphify-out/perspectiva_equidad/` (101 nodos, 139 relaciones, 10 comunidades). Lee primero
"Contexto en 60 segundos" de `GRAPH_REPORT.md`; para verlo, abre `graph.html` en el navegador (doble clic en un nodo de
simulador abre su enlace). La sección 7 de este archivo resume qué hay en cada comunidad.

---

## 1. Lo que ya está hecho y validado

| Pieza | Estado | Dónde |
|---|---|---|
| Microdatos IPM 2025 del DANE, versión departamental | En el repo | `data/DANE/` |
| Validación de pesos, umbral y factor de expansión | Hecho | `02_validar_ipm.py` |
| Universo de Antioquia con las 3 zonas de `P3` | Hecho (por subir a `main`) | `03_preparar_antioquia.py` → `data/processed/hogares_antioquia.csv` |
| Línea base por zona (H, A, M0, contribuciones) | Hecho | `04_linea_base.py` |
| Reglas para contar personas afectadas (u_ij) | Validadas contra HOGARES en los 87.060 hogares del país | `docs/reglas_conteo_personas.md` (por subir) |
| Costos EpF_j con fuente oficial | Verificados el 30-oct-2026 | sección 4 |
| Estrategia de rezago (brecha normalizada) | Adoptada el 30-oct-2026 | sección 5 |
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

Severidad inicial (sobre los pobres, sin censurar): Sev₀ ≈ 117.908 (0,0163 por persona).

---

## 2. Lo que concluí de los datos

1. **El 100 % de los pobres es informal** (privación de `empleo_formal`), en las tres zonas.
2. **Educación y trabajo explican ~65 % de la pobreza** en las tres zonas. Vivienda pesa el doble en lo rural (19 % contra 10 %).
3. **Los pobres están pegados al umbral:** el 49 % de los hogares pobres está a 0,05 o menos, 135 hogares están justo en 0,34 y el 77,6 % sale con una sola intervención. Un modelo de H puro gasta en los "menos pobres"; por eso el Modelo 1 tiene techo de severidad.
4. **El 53 % de las personas pobres vive en la cabecera**, aunque la incidencia es mucho mayor en lo rural.
5. **No hay municipio en la base:** Medellín no se puede aislar. El universo es Antioquia completa para los 4 modelos.
6. **Las reglas de conteo valen para pobres y no pobres,** porque se validaron con todos los hogares del país. Dos indicadores son aproximaciones: `atencion_integral` (96,5 %; se cuentan los niños de 0 a 5 años) y `desempleo_larga_duracion` (86,5 %; desocupados del hogar, mínimo 1).
7. **Rezago escolar:** 215 niños rezagados en 149 hogares pobres. 83 tienen 1 año de atraso, 47 tienen 2, 27 tienen 3, 26 tienen 4 y 32 tienen 5 o más. 49 de los 132 con 2 años o más no asisten.
8. **La entropía de Shannon no sirve para identificar pobres:** con privaciones binarias premia la rareza (correlación −0,94 con la prevalencia) y bajaría H de 9,5 % a 2,2 %. Se mantienen los pesos oficiales y k = 1/3.
9. **El rango de presupuesto hay que recalcularlo** con los costos corregidos (sección 4). Con los costos viejos era ≈ $0,50 billones (sacar a los 523 hogares) y ≈ $7,29 billones (quitar todo lo intervenible); el acueducto rural nuevo lo sube bastante.

---

## 3. Cómo se van a compartir los datos (propuesta)

La idea: **el 05 cuenta y `parametros.py` pone los precios.** El 05 se corre una sola vez; las sensibilidades solo cambian el escenario.

### Salidas de `05_conteo_personas.py` (en `data/processed/`), para los 3.732 hogares

| Archivo | Una fila por | Columnas |
|---|---|---|
| `conteo_pares.csv` | Par hogar-indicador con M_ij = 1 | ID_HOGAR, P3, zona_costo, pobre, FEX_C, PERSONAS, indicador, u_ij, u_imputado, intervenible |
| `empleo_componentes.csv` | Hogar privado en empleo formal o desempleo | ID_HOGAR, tiene_ocupados, n_ocup_sin_pension, n_desoc_18_28, n_desoc_mujer_29_56, n_desoc_hombre_29_61, n_desoc_pension, n_adultos_sin_cobertura |
| `ninos_rezago.csv` | Niño de 7 a 17 años rezagado | ID_HOGAR, P3, pobre, FEX_C, edad, e_k = edad − 6, atraso a_k⁰, asiste, nivel (primaria/secundaria/media) |

- **u_ij solo existe donde M_ij = 1.** Si la regla da 0 personas pero el DANE marca la privación, u_ij = 1 y `u_imputado = 1`.
- `zona_costo`: urbano = `P3` 1; rural = `P3` 2 o 3. La equidad y los reportes usan las 3 zonas de `P3`.
- El nivel educativo de cada niño se necesita porque el costo del rezago cambia entre primaria, secundaria y media.

### Qué vive en `parametros.py` (no `06_parametros.py`: Python no importa módulos cuyo nombre empieza por número)

- `DIMENSIONES`, `PESOS`, `INDICADORES`, umbral k.
- `SMMLV`, tabla `EPF[indicador] = (urbano, rural)`, tarifas de Empleos para la Vida y costos del rezago por zona y nivel.
- `ESCENARIOS` (base, u_ij = 1, p = 0,369 / 0,50 / 0,75, acueducto rural BID, empleo ×0,5 / ×2, caso 3 opción B, CLEI acelerado).
- `tabla_costos(escenario)`: devuelve la tabla larga (ID_HOGAR, indicador, u_ij, costo_ij) con costo_ij = EpF_j^zona · u_ij · HW_i.
- Malla de B, r, ρ, ρ_e y la semilla del sorteo.

---

## 4. Costos EpF_j verificados (2025, SMMLV = $1.423.500, Decreto 1572 de 2024)

Regla del proyecto: todo costo tiene fuente oficial (norma, resolución o documento con enlace). Detalle y enlaces:
[Verificación de costos por indicador del IPM](https://claude.ai/artifact/Tim5YJJDpGstsHKB53ofj6).

| Indicador | Urbano | Rural | Unidad u_ij | Fuente |
|---|---|---|---|---|
| pisos, paredes | $25,62 M | $35,2 M | hogar | Decreto 0413 de 2025 (18 SMMLV) / promedio de resoluciones Fonvivienda 2025 |
| hacinamiento | $31,32 M | $31,32 M | hogar | Decreto 0413 de 2025, modular (22 SMMLV) |
| acueducto | $11,72 M | $43,7 M | hogar | Decreto 1275 de 2021 (8,23 SMMLV) / Minvivienda, acueducto veredal de Alpujarra, llevado a 2025. BID $9,7 M queda como sensibilidad baja |
| alcantarillado | $11,72 M | $15,3 M | hogar | Decreto 1275 de 2021 (el subsidio urbano cubre acueducto y alcantarillado juntos) / Minvivienda Nariño 2022 × 1,26 IPC |
| aseguramiento_salud | $1,32 M | $1,32 M | persona ≥ 6 años no afiliada | UPC subsidiada, Res. 2717 de 2024 |
| barreras_acceso_salud | $0,21 M | $0,36 M | persona con necesidad no atendida | 4 consultas (4,51 UVB) + prima de dispersión 11,47 % en lo rural |
| analfabetismo | $0,96 M | $1,29 M | persona ≥ 15 años | CLEI ciclo 1, asignación por alumno SGP 2025 (Anexo 1 DD SGP-96-2025, DNP) |
| logro_educativo | $2,88 M | $3,86 M | adulto ≥ 15 con < 9 años | 3 ciclos CLEI, misma fuente |
| empleo_formal | por hogar | por hogar | fórmula | $2,73 M × ocupados sin pensión + Σ EpV_h desocupados + $2,73 M × adultos sin cobertura (solo si no hay ocupados). 16 % × 12 SMMLV, Ley 100 de 1993 |
| desempleo_larga_duracion | EpV_h | EpV_h | desocupado (mín. 1) | Decreto 533 de 2024: 30 % 18–28 ($5,12 M), 20 % mujeres 29–56 ($3,42 M), 15 % hombres 29–61 ($2,56 M); aporte a pensión ($2,73 M) a mujeres ≥ 57 y hombres ≥ 62 |
| trabajo_infantil | $3,0 M | $3,0 M | hogar | Renta Ciudadana: $500.000 × 6 ciclos en 2025 |
| inasistencia_escolar | $3,0 M / p | $3,0 M / p | hogar | Misma fuente; p = 0,369 (cumplimiento del ciclo 4 de 2025) |
| atencion_integral | $5,21 M | $5,21 M | niño de 0 a 5 años | CDI tipo A, ICBF Res. 5288 de 2025 |
| rezago_escolar (año regular) | $2,71 / 3,05 / 3,22 M | $3,52 / 3,96 / 4,18 M | niño intervenido (primaria / secundaria / media) | Asignación por alumno SGP 2025, ETC Antioquia (Anexo 1 DD SGP-96-2025) |
| rezago_escolar (CLEI) | $0,96 M por ciclo | $1,29 M por ciclo | niño ≥ 13 años | Misma fuente |

El $6,3 M que usábamos antes para el rezago ya no se usa (no tenía fuente).

---

## 5. Rezago escolar: estrategia adoptada (30-oct-2026)

Fuente de verdad: `informe_rezago_brecha_normalizada.md` (§4.4 y §4.6). El rezago va en **dos capas**:

1. **IPM oficial intacto:** la privación del hogar sí/no (peso 0,05) define H, así que H sigue siendo comparable con el DANE.
2. **Severidad educativa por niño (SevEdu) debajo,** para no abandonar a los niños con 2 o más años de atraso, que este año no cambian el IPM.

**Medida:** brecha normalizada de Alkire-Foster, g_k = a_k / e_k con e_k = edad − 6, al cuadrado (α = 2). Cada niño queda entre 0 y 1; 11 años de atraso pesan 1, no 121. **Sin tope al atraso:** cortarlo es abandonar a los más rezagados.

**m_k = grados que el niño aprueba en el año:** 1 año regular, 2 promoción anticipada o CLEI ciclos 2–4, 3 CLEI ciclo 1, y Aceleración del Aprendizaje lo que le falte de primaria.

**El año que pasa (cohorte fija):** todos los niños envejecen un año.
- Sin intervenir: b_k = a_k⁰ + 1 − asiste_k · ap_k. Con intervención: a_k¹ = a_k⁰ + 1 − m_k. Efecto: d_k = m_k − asiste_k · ap_k.
- SevEdu¹ = Σ_k HW_k ((b_k − d_k z_k) / (e_k + 1))², lineal porque z_k es binaria.
- **Techo contra el escenario sin intervención:** SevEdu¹ ≤ (1 − ρ_e) · SevEdu¹_sin. Así el paso del tiempo no cuenta como logro.
- Los 215 niños siguen en la suma y en la privación de su hogar aunque cumplan 18; si no, el modelo bajaría H gratis.

**Enlace con el IPM (restricción 10):**
- (10a) x_i,rez ≤ z_k para cada niño k del hogar con a_k⁰ + 1 ≤ m_k.
- (10b) x_i,rez = 0 si algún niño del hogar tiene a_k⁰ + 1 > m_k.

Un año regular (m_k = 1) ya no le quita la privación a nadie: solo evita que el atraso crezca. El rezago se paga por niño intervenido (Σ c_k z_k, con c_k · HW_k); x_i,rez no tiene costo propio, para no cobrar dos veces.

**Condición de pago (multiperiodo):** en la corrida 1 se puede intervenir a cualquier niño, sin condición de asistencia. Desde la corrida 2, solo se le vuelve a pagar a quien ganó el año: z_k^t ≤ 1 − z_k^(t−1) (1 − ap_k^(t−1)). ap_k se simula con Monte Carlo (falta la probabilidad oficial de aprobar, del MEN).

**Para los Modelos 3 y 4:** la fórmula es la misma niño por niño, así que se reproduce con el sorteo. El sorteo de rezago tendría que ser por niño, y nivelar a un niño de un hogar no pobre cuesta pero no baja SevEdu (error de inclusión).

**Por recalcular:** SevEdu⁰ y SevEdu¹_sin en la escala normalizada (el 1.291.034 estaba en años al cuadrado), el rango de ρ_e y sus codos (el 29 % era con años brutos), y el simulador.

---

## 6. Convenciones acordadas

- y_i = 1 ⇔ el hogar **sale** de la pobreza (igual que b1_i del paper).
- HW_i siempre multiplica el costo; HS_i nunca, porque las personas ya están en u_ij.
- Reportamos H, A, M0 y severidad, siempre por zona (`P3`) y total. Severidad sobre los pobres iniciales y sin censurar. Para el rezago, además: SevEdu, niños intervenidos por años de atraso y hogares que salen del rezago.
- Desempate en dos etapas: (1) max personas que salen; (2) min severidad s.a. personas que salen ≥ H*. Se recomienda por la tolerancia de HiGHS (mip_rel_gap 1e-4 ≈ 68 personas).
- Sensibilidades mínimas que corremos los dos: caso base y u_ij = 1.

### Formulación vigente del Modelo 1 (para comparar)

max Σ p_i y_i − λ Σ p_i q_i, con p_i = HW_i · HS_i, sujeto a:
(1) presupuesto Σ c_ij x_ij ≤ B · (2) salida s_i ≤ 0,33 + M_i (1 − y_i), M_i = c_i⁰ − 0,33 · (4) equidad por zona Σ_{i∈d} p_i y_i ≥ r · Pobres_d⁰ ·
(7) q_i ≥ 2a · s_i − a² para cada valor alcanzable a · (8) techo de severidad Σ p_i q_i ≤ (1 − ρ) · Sev₀ · (9) techo de SevEdu · (10a)/(10b) rezago.
ρ, ρ_e y r no se fijan a ojo: se calculan los extremos, se barre y se escoge con el codo o con la regla "la brecha no crece" (A de los que siguen pobres ≤ A₀).

---

## 7. Qué hay en el grafo

| Comunidad | De qué trata |
|---|---|
| 0. Paper LEPI | Análisis del paper de pobreza energética: es evaluación (MADM), no optimización |
| 1. Crítica al objetivo H | Por qué maximizar H abandona a los más pobres; definición de severidad |
| 2. Entropía | Probada y descartada para identificar pobres |
| 3. Modelo 1 reformulado | Objetivo, techo de severidad, linealización, bigM por hogar, SevEdu |
| 4. Escoger ρ y r | Barridos, codo, regla de la brecha, malla (r, ρ) |
| 5. Costos verificados | Fuentes oficiales y correcciones del 30-oct |
| 6. Limitaciones y defensa | Supuestos que hay que declarar ante la profesora |
| 7. Grafo base (21-oct) | Nodos del grafo original del repo |
| 8. Simuladores y artefactos | Enlaces a simuladores y documentos publicados |
| 9. Rezago (brecha normalizada) | Estrategia vigente del rezago |

---

## 8. Pendientes y preguntas para Jerónimo

1. **Severidad educativa en los 4 modelos.** ¿La adoptamos con la brecha normalizada? Si sí, el sorteo de rezago debería ser por niño. ρ_e se vuelve a escoger cuando recalculemos.
2. **Cambio de objetivo del Modelo 1:** H con techo de severidad y desempate en dos etapas. Cambia lo que se compara entre los 4 modelos.
3. **u_ij = 1 en empleo formal y desempleo.** Propuesta: $2,73 M por hogar en empleo formal y $5,12 M en desempleo.
4. **Inasistencia (3,0/p) con el sorteo.** Sugerencia: en la optimización el sorteo queda fijo y el costo es 3,0/p; el cumplimiento entra solo en el Monte Carlo de evaluación. Tú decides.
5. **Conteo de los no pobres:** lo programo yo en el mismo 05 (es el mismo código sin filtrar por `pobre`). Te pido revisarlo cuando lo suba.
6. **Branch Modelo3:** `05_modelo3.py` define sus propios `IND`, `W` y `SEMILLA = 2026`. Cuando exista `parametros.py`, habría que importarlos de ahí. Además el nombre `05_` choca con `05_conteo_personas.py`; ¿lo renumeramos?
7. **Decisiones de costos que siguen abiertas para ti:** logro educativo con 3 ciclos CLEI (base) o 1 ciclo por año; ¿estás de acuerdo con el acueducto rural de $43,7 M?

---

## Notas de Jerónimo

_(Escribe aquí lo que necesites que agregue, cambie o corrija.)_
