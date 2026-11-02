# Modelo 3 — focalización geográfica estocástica (rama `Modelo3`)

> Actualizado: 2-nov-2026, con los archivos `m34_*`. Responsable: Jerónimo Vélez.
> Sustentación: noviembre de 2026. Responder en español, paso a paso y revisando con rigor
> los Big-M y el Monte Carlo. El panorama de los 4 modelos está en el `CLAUDE.md` de la rama
> `Contexto`.

## 1. Qué modela

Adaptación del Modelo 3 de Hamie, Hlasny & Jouni (2024, ERF WP 1742). El Estado solo ve
agregados por zona: decide **cuánto** cubrir en cada par (indicador j, zona d) y un sorteo
decide **a quién** le llega.

Los errores de inclusión y de exclusión son el resultado de política, no un defecto del
modelo: simulan la capacidad real del Estado para focalizar. Hay que preservar esa narrativa.

## 2. Datos: hechos de regresión (no re-derivarlos)

Microdato IPM 2025 del DANE (catálogo 903), versión departamental, en `data/DANE/`.
Escenario: **Antioquia completa** (`DEPARTAMENTO == 5`), con D = las 3 clases de `P3`.

| Zona | Hogares | Pobres | Personas pobres | H0 | A0 | M0 |
|---|---|---|---|---|---|---|
| Cabecera | 1.670 | 127 | 363.286 | 6,21 % | 40,58 % | 0,0252 |
| Centro poblado | 613 | 103 | 69.089 | 17,91 % | 38,56 % | 0,0691 |
| Rural disperso | 1.449 | 293 | 251.031 | 25,18 % | 42,11 % | 0,1060 |
| **Total** | **3.732** | **523** | **683.406** | **9,45 %** | **40,94 %** | **0,038684** |

- Población total: 7.231.754 personas. Sev0 = 117.908.
- Llave de hogar: `(DIRECTORIO, SECUENCIA_P)`. `FEXP = FEX_C * PERSONAS` = HS_i × HW_i.
- Pobre ⇔ puntaje ≥ 1/3 (sale ⇔ puntaje ≤ 0,33). Pares activos M_ij = 1: 8.602 sobre 45 pares (j, d).
- No hay municipio: Medellín no se puede aislar.
- Pesos: educación y trabajo 0,10 por indicador; salud 0,10; niñez 0,05; vivienda 0,04.

## 3. Archivos

| Archivo | Rol |
|---|---|
| `00_verificar_base.py` | 7 chequeos de que la base sirve para M3/M4 |
| `05_modelo3.py` | MILP directo; carga, sorteo y constantes (`IND`, `W`, `EPS`, `sortear_R`). Control de equivalencia |
| `06_modelo3_cortes.py` | **Objetivo del paper** por cortes: min esfuerzo s.a. meta de M0 |
| `cortes.py` | **Mecanismo separado del objetivo**, con cobertura `V` y costo `K` distintos y elegibilidad `elig`. También sirve para el Modelo 4 |
| `modelo3_equidad.py` | **Objetivo de equidad** del Modelo 1: max personas que salen s.a. presupuesto, en dos etapas |
| `costos_provisionales.py` | PROVISIONAL: sensibilidad u = 1 con la tabla de Martín. Se borra cuando exista `parametros.py` |
| `test_cortes.py` | T1 regresión contra 06, T2 prefijo con pesos arbitrarios, T3 elegibilidad |
| `correr_m3_equidad.py` | Pruebas por capas: `capa0` a `capa3` |
| `extremos_m3.py` | Diagnóstico de `rho_max` y `r_max` para un B dado (fijo en $500 mm) |
| `07_clusters.py` | Clústeres del Modelo 4 (fuera del alcance de este archivo) |
| `m34_datos.py` | Carga + línea base con asserts + sorteo R (idéntico a 05). Autocontenido: no importa 05/06/07 |
| `m34_mecanismo.py` | Cortes con `grupo` **matriz n×J** (sirve para M3 y M4), MILP del paper, métricas |
| `m34_clusters.py` | k-means idéntico a 07 (reproduce 1.389/1.038/849/456) |
| `m34_montecarlo.py` | MC: réplicas × metas {5, 10, 20 %} × costos {pp, u1}, para `m3` o `m4` |
| `m34_optimos_alternos.py` | Rango del error de inclusión entre óptimos alternos |
| `m34_test_regresion.py`, `m34_resumen_mc.py` | Regresión contra 06 (630 cortes, 153,0) y tabla/gráficas del MC |

## 4. Formulación

Notación: I hogares, J 15 indicadores, D zonas. `Den_jd` es el total de cobertura de los
privados de la celda. Cobertura: `p_jd = cum(c) / Den_jd`. Sorteo `R_ij ~ U[0,1]`: el hogar
sale de la privación ⇔ `R_ij ≤ p_jd`.

**Hallazgo central: el Estado elige cuántos, no cuáles.** Dentro de (j, d) los curados son
siempre un prefijo del orden por R_ij. Un corte c es auto-consistente si
`R_(c) ≤ p(c) ≤ R_(c+1) − ε`. Los cortes factibles se enumeran antes de optimizar. La
propiedad solo usa el orden de los R, así que vale con cualquier peso V > 0 (`cortes.py`).

```
z[j,d,c] ∈ {0,1}        ∀c ∈ F_jd
C1   Σ_c z[j,d,c] = 1
     N_ij = 1 − elig_ij · Σ_{c ≥ rank_ij} z[j,d,c]
     Costo_jd = Σ_c cumK(c) · z[j,d,c]       (incluye a los no pobres)
```

### 4.1 Objetivo del paper (`06_modelo3_cortes.py`)

`min Σ E_jd` con V = K = HS. Es equivalente a la formulación directa de `05_modelo3.py`
(R1–R7) y tiene la misma región factible.

```
C3–C5  linealización de C_i con Big-M = HS_i·HW_i por hogar y b1_i
C6     Σ_i C_i ≤ MPI_s·(1 − MPI_r)·Σ_i HS_i·HW_i
```

### 4.2 Objetivo de equidad (`modelo3_equidad.py`)

La numeración coincide con la del Modelo 1 para poder comparar. `p_i = HW_i·HS_i`;
`s_i = Σ_j w_j N_ij` para i pobre al inicio.

```
Etapa 1  max Σ p_i y_i
Etapa 2  min Σ p_i q_i   s.a. Σ p_i y_i ≥ H*·(1 − 1e-7)
(1) Σ_jd Costo_jd ≤ B
(2) s_i ≤ 0,33 + M_i(1 − y_i),   M_i = s_i^0 − 0,33
(4) Σ_{i∈d} p_i y_i ≥ r·Pobres_d^0
(7) q_i ≥ 2a·s_i − a²   ∀a ∈ A_i, a > 0
(8) Σ p_i q_i ≤ (1 − ρ)·Sev0
```

SevEdu (9) no está implementada: necesita un sorteo por niño. `metricas` recalcula todo desde
los cortes elegidos; no confía en `y` ni en `q`.

## 5. Trampas ya corregidas — NO revertirlas

1. **Unidades de p_jd:** numerador y denominador en la misma unidad. Con hogares abajo y
   personas arriba p_jd llegaba a 4,81, el sorteo quedaba inerte y M3 = M1.
2. **MPI_s es M0 (0,038684), no H0.** Con H0 el esfuerzo da 0. Nunca hardcodearlo.
3. **Desigualdades estrictas:** `< 1/3` ⇔ `≤ 0,33` exacto (pesos múltiplos de 0,01); umbral
   estocástico `≤ R − ε`, con ε = 1e-6 en 05 y en la enumeración de cortes. Si cambia uno,
   cambia el otro.
4. **Big-M ajustado por hogar.** Nada de M global: CBC no cierra el gap.
5. **N_ij ≡ b2_ij:** b2 y b3 eliminadas. Solo los pares con M_ij = 1 llevan variable.
6. **`C_i` con `lowBound=0`.** Si es libre, la meta se cumple trivialmente.
7. **No inline-ar expresiones grandes** dentro de bucles de restricciones: PuLP se colgaba.
8. **Cotas inferiores de esfuerzo:** causa #1 de infactibilidad (`paredes` en centro poblado
   tiene 1 hogar privado). Desactivadas a propósito.
9. **Semilla de R_ij derivada del hogar:**
   `np.random.SeedSequence([SEMILLA, replica, DIRECTORIO, SECUENCIA_P])`. No cambiar a
   `rng.random((n,15))`.
10. **Guarda `|D| ≥ 2`:** con una sola zona, M3 colapsa en M1. No quitar el `sys.exit`.
11. **Gap de HiGHS por etapa:** 1e-6 en personas (etapa 1) y 1e-4 en severidad (etapa 2). Con
    el mismo solver en ambas, la etapa 2 no terminó en > 150 s con B = $500 mm.
12. **Submuestras solo para depurar,** nunca para resultados.
13. **Óptimos alternos (2-nov):** con esfuerzo en personas-privación hay empates; en la réplica 0,
    meta 5 %, el error de inclusión va de 41,7 % a 61,7 % con el mismo esfuerzo (60,0). Reportar con
    desempate lexicográfico (min inclusión s.a. esfuerzo ≤ E*) o como intervalo. El 41,7 % histórico
    era uno de esos óptimos, no un error.

## 6. Estado y resultados

### Verificado el 1-nov-2026 (`origin/Modelo3`, entorno `opti1`, CBC)

| Prueba | Resultado |
|---|---|
| `test_cortes.py` T1 | 45 pares, 630 cortes, mismos cortes que 06, objetivo 153,0 |
| `test_cortes.py` T2 | 511 cortes con pesos aleatorios, 0 inconsistentes |
| `test_cortes.py` T3 | Celda Cabecera: 243/243 cubiertos, 243 siguen privados, costo 953 |
| `correr_m3_equidad.py capa0` | 523 pobres, H0 = 9,45 %, Sev0 = 117.908, 518 cortes con u = 1 |
| Costo de cubrir todo (u = 1) | $29.358 mm, de los cuales $8.946 mm en hogares pobres |

**Tangentes:** el código da 6.048 y Martín reporta 6.571. La diferencia es exactamente 523, el
número de hogares pobres, y el código omite a = 0 en cada hogar. Es muy probable que esa sea
la causa; falta confirmarlo con Martín.

### Objetivo del paper: réplica 0, esfuerzo en personas-privación

Es una sola réplica: para resultados, usar el Monte Carlo de abajo. Estas cifras vienen de corridas
anteriores; de ellas se reprodujo el 153,0.

| MPI_r | Esfuerzo | Privaciones resueltas | M0 final | H final | Error de inclusión |
|---|---|---|---|---|---|
| 0,05 | 60,0 | 19 | 0,036730 | 0,0903 | 41,7 % |
| 0,10 | 153,0 | 47 | 0,034779 | 0,0854 | 62,1 % |
| 0,20 | 349,0 | 104 | 0,030866 | 0,0756 | 68,5 % |

**Corrección:** la tendencia 42→62→69 % del error de inclusión era de una réplica. En el Monte Carlo
la mediana de M3 es plana (~60 %): lo robusto es el nivel alto, no la tendencia.

### Monte Carlo M3 y M4: objetivo del paper (2-nov)

1.200 MILP (100 réplicas × 3 metas × 2 costos × 2 modelos), todos óptimos. Mediana [p5; p95]; archivos
en `resultados/m34/`.

| Meta | Modelo | Esfuerzo pp | Costo u=1 (mil millones $) | Inclusión (pp) | Exclusión | H final |
|---|---|---|---|---|---|---|
| 5 % | M3 | 83 [41; 124] | 12,2 [6,4; 17,4] | 59 % [32; 76] | 94 % | 0,0894 |
| 5 % | M4 | 57 [30; 79] | 6,0 [3,2; 6,6] | 41 % [16; 64] | 94 % | 0,0892 |
| 10 % | M3 | 164 [115; 223] | 23,5 [15,0; 32,9] | 64 % [44; 79] | 88 % | 0,0843 |
| 10 % | M4 | 133 [92; 162] | 13,4 [10,3; 16,9] | 45 % [23; 57] | 88 % | 0,0844 |
| 20 % | M3 | 365 [303; 420] | 44,2 [40,5; 47,8] | 62 % [45; 69] | 74 % | 0,0753 |
| 20 % | M4 | 345 [290; 383] | 38,3 [33,5; 41,9] | 35 % [27; 51] | 72 % | 0,0763 |

Pareado (misma R), por meta de 5 / 10 / 20 %:

- **Costo:** con u = 1, M4 es más barato en 97–99 % de las réplicas (ahorro mediano 53 / 43 / 13 %).
  Con `pp`, su esfuerzo es menor en 83 / 85 / 75 % (ahorro mediano 36 / 19 / 6 %).
- **Inclusión:** con `pp`, M4 tiene menos en 78 / 92 / 98 % de las réplicas. Con u = 1, en 33 / 76 / 92 %:
  con meta 5 % la mediana **sube** de 49 % a 60 %, así que no se puede afirmar que M4 siempre la reduzca.

### Objetivo de equidad: SIN VERIFICAR

Reportado en el commit `16a4e4f` y en `extremos_m3.py` (u = 1, réplica 0, B = $500 mm):
419.550 personas salen, 42,6 % del gasto cae en no pobres, `rho_max` = 40,7 %, `r_max` = 59,8 %.
**No se pudo reproducir** el 1-nov porque faltaba `highspy`. Ya está instalado, pero estas corridas
no se han repetido. No citar estas cifras hasta volver a correrlas.

## 7. Decisiones abiertas

1. **¿Qué objetivo es el caso base del Modelo 3?** Hay una contradicción por resolver: el contexto
   anterior decía que M3/M4 no cambian de objetivo y se comparan ex post, pero `modelo3_equidad.py`
   ya implementa la equidad del Modelo 1. Hay que decidirlo con Martín, porque define qué se compara.
2. **Sorteo por niño para SevEdu:** rompe el prefijo por hogar. Mientras tanto, SevEdu solo como
   métrica ex post dentro del Monte Carlo.
3. **Pares no intervenibles** (columna `intervenible` de Martín): fijar N_ij = 1 y decidir si
   cuentan en `Den_jd` (contarlos deja la cobertura máxima < 1, excluirlos no).
4. **Denominador pequeño** (`paredes` en centro poblado = 1): E_jd = 0, agrupar zonas o piso.
5. **Solver único:** CBC en 05, 06 y `test_cortes.py`; HiGHS en `modelo3_equidad.py`. Martín usa
   HiGHS con `mip_rel_gap = 1e-4`. Hay que unificar o reportar los gaps.

## 8. Lo que sigue

1. Reproducir las capas 1 a 3 de equidad y `extremos_m3.py`.
2. Decidir el objetivo del caso base (sección 7, punto 1).
3. **Monte Carlo:** hecho con el objetivo del paper (`m34_montecarlo.py`). Falta el desempate de la
   trampa 13 y repetirlo con costos reales. Reportar la **distribución**: la varianza entre réplicas
   es el resultado.
4. Sustituir `costos_provisionales.py` por `parametros.py` y `conteo_pares.csv` de Martín cuando
   existan, con V = u_ij·HW_i, K = costo_ij y elig_ij reales.
5. Verificar contra el Apéndice 1 del paper el error de unidades de p_jd y actualizar
   `Seleccion_Variables_Restricciones_Modelo3.pdf` (carpeta Opti1, un nivel arriba del repo).

## 9. Entorno y cómo correrlo

Correr desde la raíz del repo: los scripts cargan `05_modelo3.py` y `06_modelo3_cortes.py` por
ruta relativa.

```bash
PY=/opt/anaconda3/envs/opti1/bin/python
$PY test_cortes.py
$PY 06_modelo3_cortes.py 0.10          # producción + control de equivalencia
$PY 06_modelo3_cortes.py 0.10 solo     # sin control
$PY 05_modelo3.py 0.10                 # formulación directa
$PY correr_m3_equidad.py capa0         # capa1 | capa2 <B> | capa3 <B> <r> <rho>; 1-3 requieren highspy
```

- `opti1`: Python 3.10.18 y PuLP 2.9.0, con CBC y HiGHS (`highspy` instalado). `requirements.txt` pide
  `pulp>=2.9,<4` y `highspy>=1.7`.
- El `python3` por defecto trae PuLP 4.0.0 sin solvers: no usarlo.
- `timeLimit` de `PULP_CBC_CMD` no es confiable: 120 s configurados llegaron a > 200 s. Este Mac no
  tiene `timeout`; usar `perl -e 'alarm 240; exec @ARGV' <comando>`.
- CSV del DANE: coma y UTF-8 con BOM. `utils_dane.leer()` lo detecta; no hardcodear.

## 10. Convenciones

- Nada derivado de los datos hardcodeado: un `0.038684` literal en el código es un bug.
- Los comentarios explican el porqué y son material de sustentación: ampliarlos, no limpiarlos.
- Los cambios metodológicos (umbral, pesos, D) se reflejan también en los PDF de selección de variables.
- Con Martín: y_i = 1 ⇔ el hogar **sale**; reportar H, A, M0 y severidad por zona `P3` y total;
  sensibilidades mínimas compartidas: caso base y u_ij = 1.
- Repo compartido: **no hacer commit ni push sin que Jerónimo lo pida.** No poner atribución de
  Claude en commits ni en PR.
- Cuando se resuelva un problema relevante, agregarlo a `docs_proyecto/bitacora-problemas-y-soluciones.md`
  (carpeta Opti1).
