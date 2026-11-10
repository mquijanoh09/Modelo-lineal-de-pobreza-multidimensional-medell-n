# Datos finales de M3/M4 (10-nov-2026) — CONGELADOS

Etiqueta git: `datos-finales-10nov`. Son las cifras que usa el paper (`paper/` en `main`). No se vuelven a correr.

Escenario común contra el M1/M2 de Martín en `main` (commits del 10-nov), validado 18/18
(`validacion_10nov.csv`, `m34_validar_10nov.py`): sin E-7 ni SevEdu, meta global de M0, tabla de costos común
con las reglas del M1 (desempleo no imputado, analfabetismo con g_a > 0), rezago no intervenible, k = 4.

| Archivo | Qué es |
|---|---|
| `info_perfecta_comun_10nov.csv` | M2 de Martín (sin_E7, meta global): costo mínimo por meta (2–30 %) |
| `info_perfecta_equidad_comun_10nov.csv` | M1 de Martín (sin_E7, r = 0, sin techos): personas que salen con B = 2–100 mm |
| `barrido_comun_crudo_10nov.csv` | M3, M4 y placebo, 100 réplicas × 15 metas (4.500 MILP, todos óptimos, gap ≤ 9,5e-7) |
| `equidad_comun_crudo_10nov.csv` | M3, M4 y placebo; 100 réplicas con B ≤ 10 y 30 con B ≥ 25; ρ = 0 y 0,10 |
| `ic_bootstrap_costos_10nov.csv`, `ic_bootstrap_equidad_10nov.csv` | medianas, IC 95 % bootstrap, cocientes pareados (`m34_bootstrap_ic.py`) |
| `convergencia_n_10nov.csv/.png` | semiancho del IC según el número de réplicas |
| `precio_informacion.pdf/.png` | figura central del paper (`m34_grafica_precio_info.py`) |

Las tablas LaTeX del paper salen de los dos `ic_bootstrap_*` con `m34_tablas_paper.py`.
