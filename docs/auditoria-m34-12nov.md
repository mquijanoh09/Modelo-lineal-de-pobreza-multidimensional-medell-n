# Auditoría de los Modelos 3 y 4 — 12-nov-2026

Alcance: formulación, implementación (`m34_*.py`, rama `Modelo3`), solver, resultados congelados
(`datos-finales-10nov`, commit `796ca18`) y su reporte en el paper (`paper/` en `main`). Tipo de problema:
MILP (min costo s.a. meta de M0; max personas que salen s.a. presupuesto) con un mecanismo estocástico
(sorteo R) evaluado por Monte Carlo, y *clustering* (k-medias) como insumo del M4.
No se auditan el M1 ni el M2 de Martín; solo su interfaz con M3/M4.

## 1. Resumen ejecutivo

**Los resultados de M3/M4 son correctos y reproducibles.** Todo lo que se pudo verificar ejecutando
código pasó, con evidencia independiente del modelo:
- 120/120 soluciones de costo y 45/45 de equidad cumplen la regla del sorteo hogar por hogar, la meta o el
  presupuesto con Alkire–Foster recalculado desde cero, y reproducen al peso los datos congelados.
- 40/40 instancias pequeñas tienen el mismo óptimo que la fuerza bruta.
- En 475 pares, la lista de cortes coincide con la definición.

Los tres hallazgos principales:
1. **(Medio, corregido en el paper)** El paper atribuía a la falta de información la infactibilidad del
   techo de severidad con B ≤ $10 mm. Con B = $2 mm también es infactible con información perfecta; con B
   = 5 y 10 sí es atribuible a la falta de información.
2. **(Medio, corregido)** No había un archivo de versiones exactas en el repo: `requirements.txt` solo da
   rangos. Se agregó `requirements-lock.txt`, con el que los resultados se reproducen al peso.
3. **(Bajo)** Las restricciones de PuLP no tienen nombre (`_C1`, `_C2`…), lo que dificulta depurar el
   `.lp`. No se cambia porque los modelos están congelados.

## 2. Modelo reconstruido (desde el código)

Datos: hogares i, indicadores j, celda g(i, j) (zona en M3; zona o tipo en M4), M_ij ∈ {0,1},
V_ij = u_ij·HW_i, K_ij = c_ij·HW_i, R_ij ~ U[0,1] fijo, pers_i = HS_i·HW_i, I⁰ = pobres iniciales,
s_i⁰ = round(Σ_j w_j M_ij, 2). Para cada par (j, g): privados ordenados por R; F_jg = {c : R_(c) ≤ cumV(c)/Den ≤ R_(c+1) − ε}.

**Criterio del paper (`resolver_paper`)**

```
min  Σ_(j,g) Σ_{c∈F} cumK_jg(c) z_jgc
s.a. Σ_{c∈F} z_jgc = 1                                         ∀(j,g)                 [42 en M3]
     s_i = Σ_j w_j M_ij − Σ_{j interv.} w_j Σ_{c ≥ rank_ij} z_jgc   (lo no intervenible es constante)
     C_i + pers_i b1_i ≥ pers_i s_i                            ∀i ∈ I⁰  (Lin 1)
     C_i − pers_i b1_i ≤ pers_i s_i                            ∀i ∈ I⁰  (Lin 2)
     s_i − (1 − b1_i) ≤ 0,33                                   ∀i ∈ I⁰  (Lin 3)
     Σ_{i∈I⁰} C_i ≤ M0⁰ (1 − r) Σ_i pers_i
     z, b1 binarias; C ≥ 0
Etapa 2: min Σ cumNP·z  s.a.  costo ≤ E*(1 + 1e-6)          (desempate: mínima inclusión)
```

**Criterio de equidad (`m34_equidad.resolver`)**: etapa 1 max Σ pers_i y_i s.a. Σ cumK z ≤ B,
s_i ≤ 0,33 + (s_i⁰ − 0,33)(1 − y_i), [Σ_{i∈d} pers_i y_i ≥ r·Pobres_d], [Σ pers_i q_i ≤ (1 − ρ)Sev0];
etapa 2 min Σ pers_i q_i s.a. Σ pers_i y_i ≥ H*(1 − 1e-7), con q_i ≥ 2a s_i − a² para todo valor
alcanzable a > 0.

Coincide con el paper (`secciones/06_modelo_3.tex`, `07_modelo_4.tex` y Apéndice A) y con Hamie et al.
(2024, Apéndice 1). Lin 1–10 se contrastaron con el PDF original el 12-nov.

## 3. Hallazgos

| # | Severidad | Área | Hallazgo | Evidencia | Corrección |
|---|---|---|---|---|---|
| 1 | Medio | Informe | "El techo ρ = 0,10 es infactible con B ≤ 10 por falta de información" era cierto solo para B = 5 y 10: con B = 2 el M1 (información perfecta) también es infactible | M1 de Martín (`sin_E7`, r = 0, ρ = 0,10): B = 2 Infeasible; B = 5 Optimal (131.858 personas); B = 10 Optimal (160.841) | **Corregido** en las secciones 4.2, 4.3 y 6 del paper |
| 2 | Medio | Reproducibilidad | `requirements.txt` solo da rangos (`pulp>=2.9,<4`, `pandas>=2.3.3`…); el lock exacto solo estaba en el Project | `requirements.txt` | **Corregido**: `requirements-lock.txt` con las versiones con las que se reprodujeron 165/165 soluciones |
| 3 | Bajo | Informe | El paper no decía que la equidad de M3/M4 también desempata por severidad ni cómo se escribe la condición de salida | `m34_equidad.construir` (etapa 2, P2) | **Corregido** en la sección 3.4 |
| 4 | Bajo | Supuestos | Sorteos independientes entre indicadores del mismo hogar (supuesto del paper, no declarado); los errores de focalización reales suelen estar correlacionados | `m34_datos.sortear_R` (un `random(15)` independiente por hogar) | **Declarado** en las limitaciones (sección 5) |
| 5 | Bajo | Implementación | Restricciones sin nombre en PuLP | `out12/m3_rep0_meta10.lp`: `_C1` … `_C1612` | Opcional: `m += expr, f"R4_{i}"`. No se aplica (modelos congelados) |
| 6 | Bajo | Clustering | `educ_jefe` (P8587, códigos 1–13) entra como numérica; faltantes imputados con la mediana | `m34_clusters.rasgos` | Aceptable: la variable es ordinal. Ya estaba en la auditoría del 3-nov (h9) |
| 7 | Bajo | Solver | En equidad, el reintento sin *presolve* existe solo para la etapa 2; en la etapa 1 un falso infactible no se reintentaría | `m34_equidad.resolver` | Verificado que no ocurrió: 24/24 infactibles con ρ = 0,10 siguen infactibles sin *presolve*. Opcional: reintentar también la etapa 1 |
| 8 | Bajo (mejora) | Big-M | Lin 1–2 usan M = pers_i; M = pers_i·s_i⁰ sería algo más ajustado | `resolver_paper` | No necesario: todas las corridas cierran con gap ≤ 9,5e-7 en ≤ 29 s |

No se encontraron hallazgos críticos ni altos.

## 4. Verificación independiente (scripts y salidas)

| Prueba | Script | Resultado |
|---|---|---|
| Factibilidad, meta, costo y reproducción, criterio del paper (10 réplicas × M3/M4/placebo × metas 2/10/20/30 %) | `m34_auditoria_12nov.py 10 …` | **120/120**; holgura mínima de la meta 3,8e-7; peor violación de la regla 0; costos idénticos a `barrido_comun_crudo_10nov.csv` |
| Lo mismo para equidad (5 réplicas × 3 modelos × B = 2/10/50) | `m34_auditoria_12nov.equidad(5, …)` | **45/45**; personas que salen = H* del solver = datos congelados |
| Optimalidad contra fuerza bruta (submuestras de 60 hogares, 2 indicadores intervenibles, metas al azar) | `m34_fuerza_bruta_12nov.py` | **40/40** con el mismo óptimo (8 casos infactibles en ambos) |
| Completitud de la enumeración de cortes (regla completa, todos los hogares de la celda) | en línea, réplicas 0–4, M3 y M4 | **475/475** pares |
| Conteo de variables y restricciones contra la formulación (M3, réplica 0, meta 10 %) | `.lp` exportado | 1.480 variables (957 binarias = 434 cortes + 523 b1), 1.612 restricciones: **coincide** |
| Estados del solver de los datos congelados | lectura de los CSV | 4.500/4.500 de costo y 1.170/1.170 de equidad (ρ = 0) Optimal certificadas por HiGHS; gap máx. 9,5e-7 (costo), 1e-15 y 9,6e-5 (equidad, etapas 1 y 2); tiempo máx. 28,6 s (límite 180) |
| Infactibilidad con ρ = 0,10 | re-solución sin *presolve* | 24/24 siguen infactibles (es real) |
| Compatibilidad con M1/M2 | `m34_validar_10nov.py` (10-nov) | 18/18 |
| Cifras del paper | `m34_verificar_cifras_paper.py`, `m34_tamano_modelo.py` | 29/29 y 11/11 |

Salidas: `resultados/m34/auditoria12_verificacion_costos.csv` y `auditoria12_verificacion_equidad.csv`.

## 5. Lo que no se pudo verificar

- **Costos de los hogares no pobres.** Salen de las mismas funciones del M1 (`m34_costos_comunes.py`), pero
  el M1 no los usa, así que no hay contra qué compararlos. Solo los pares de hogares pobres se validaron par
  por par (V2).
- **Las cifras de la versión inicial del modelo** (9.125 binarias, más de 200 s, 22,6 veces más rápida en la
  muestra) vienen de `docs_proyecto/revision-formulacion-modelo3.md` (7-oct) y no se re-ejecutaron. El
  paper ya las presenta como de la versión inicial.
- **La sensibilidad a k** se calculó con costos u = 1 y no se repitió; el paper la presenta como cualitativa.
- **El M1 y el M2** quedan fuera del alcance, salvo su interfaz y la prueba de ρ = 0,10 del hallazgo 1.

## 6. Próximos pasos (opcionales; los modelos están congelados)

1. Si se vuelve a tocar el código, nombrar las restricciones y reintentar sin *presolve* también en la
   etapa 1 de equidad (hallazgos 5 y 7).
2. Si hay tiempo después de la entrega: sensibilidad con sorteos correlacionados entre indicadores
   (hallazgo 4).
