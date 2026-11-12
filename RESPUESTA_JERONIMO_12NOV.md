# Respuesta de Jerónimo a la especificación del 12-nov: resultados y propuesta

Fecha: 12-nov-2026 · De: Jerónimo (Modelos 3 y 4) · Para: Martín (Modelos 1 y 2)
Responde a `ESPECIFICACION_COMPARACION_4_MODELOS.md` y `CONTEXTO_COMPARACION_12NOV.md`.
**Necesito tu opinión en la sección 4 antes de reescribir los resultados del paper.**

## 1. Qué se implementó (rama `Modelo3`)

| Especificación | Estado | Dónde |
|---|---|---|
| §4.1 Piso por zona r_B (cobertura) | Hecho | `m34_equidad.construir` (P4), con el r_B del M1 |
| §4.2 Techo de severidad ρ_B (sensibilidad) | Hecho | `m34_equidad.construir` (P8) |
| §4.3 Meta de M0 en cada zona (costo) | Hecho | `m34_mecanismo.resolver_paper(zona=...)` |
| §3.3 Gap 1e-6 en las dos etapas | Hecho | `m34_equidad.resolver(gap2=1e-6)` |
| §3.3 Reportar la fracción de réplicas factibles | Hecho | `m34_analisis_12nov.py` |
| §4.4 Validaciones de granularidad máxima | **11/11** | `m34_validar_12nov.py`, `resultados/m34/validacion_12nov.csv` |
| §4.5 Corridas | Cobertura: hechas. Costo: en curso (30 réplicas hoy; 100 después) | `m34_comparacion_12nov.py` |

Además, en la etapa 1 de equidad, cualquier resultado infactible ahora se confirma sin *presolve*, porque la
infactibilidad pasó a ser un resultado que se reporta.

**Tus entregables (§5) los calculé con TUS funciones** para no frenar las corridas, sin cambiarlas: `r_codo` y
`rho_regla_brecha` sobre el M1 con `sin_E7` y `rho_e = None`, y el M2 con `escenario_m2("sin_E7", "base")`.
Están en `resultados/m34/r_rho_comparacion_12nov.csv` e `info_perfecta_meta_zona_12nov.csv`
(script `m34_referencias_comparacion.py`). **Por favor confirma que te dan lo mismo.**

| B ($ mm) | r_B | ρ_B | M1 con r_B (personas) | M1 con r_B y ρ_B |
|---|---|---|---|---|
| 2 | 0,036 | no se alcanza | 87.034 | — |
| 5 | 0,073 | no se alcanza | 129.294 | — |
| 10 | 0,146 | no se alcanza | 154.347 | — |
| 25 | 0,238 | 0,165 | 214.879 | 193.047 |
| 50 | 0,344 | 0,215 | 281.588 | 259.931 |
| 100 | 0,522 | no se alcanza | 369.940 | — |

Así que la sensibilidad con ρ solo existe para B = 25 y 50.

**Validación de granularidad máxima (§4.4), un hogar por celda:**
- Con meta por zona, M3 = tu M2 al centavo con metas del 2, 6, 10 y 20 %; con 30 % es 0,4 % más caro (CLEI).
- Con r_B, M3 = tu M1 exactamente con B = 2, 5 y 10; con B ≥ 25 saca entre 0,3 y 1,0 % menos (CLEI).

## 2. El resultado: con r_B, M3 y M4 son infactibles en el 100 % de las réplicas

En las **1.350 corridas** de cobertura (M3, M4 y placebo; 100 réplicas con B ≤ 10 y 30 con B ≥ 25; 1.170 con r_B y
180 con r_B + ρ_B en B = 25 y 50), ninguna es factible (`resultados/m34/cobertura_rB_crudo_12nov.csv`).

**No es un error:**
1. Con un hogar por celda, la misma restricción reproduce tu M1 (validación anterior), así que está bien escrita.
2. Cada infactible se confirmó sin *presolve*.
3. Es aritmética: el piso calibrado con información perfecta exige sacar a más personas de las que M3/M4 sacan
   en total. Con B = 2, r_B = 3,6 % exige unas 25.000 personas entre las tres zonas, y M3 sin piso saca unas
   12.400; con B = 100, r_B = 52 % exige unas 357.000, y M3 saca unas 222.000.

**Diagnóstico: el piso máximo que cada modelo puede garantizar** en las tres zonas a la vez
(max t s.a. Σ_{i∈I⁰,d} p_i b1_i ≥ t·Pobres_d⁰ en cada zona y presupuesto B; `m34_rmax_12nov.py`,
`resultados/m34/rmax_12nov.csv`, 100 réplicas, mediana):

| B ($ mm) | r_B del M1 | Máximo con información perfecta | M3 | M4 | Placebo | Mejor réplica de M3 |
|---|---|---|---|---|---|---|
| 2 | 3,6 % | 5,9 % | 0,0 % | 0,8 % | 0,6 % | 1,6 % |
| 5 | 7,3 % | 10,7 % | 1,5 % | 2,4 % | 2,7 % | 4,9 % |
| 10 | 14,6 % | 16,5 % | 4,9 % | 4,3 % | 4,5 % | 8,3 % |
| 25 | 23,8 % | 28,4 % | 8,8 % | 8,7 % | 7,4 % | 13,1 % |
| 50 | 34,4 % | 39,1 % | 15,7 % | 15,3 % | 12,1 % | 20,8 % |
| 100 | 52,2 % | 53,6 % | 29,9 % | 24,3 % | 20,3 % | 32,2 % |

El "máximo con información perfecta" es el mismo extremo superior del rango que usa tu `r_codo` (el mayor r
factible), y siempre queda ≥ r_B, como debe ser. **Lectura:** sin información individual, el Estado puede
garantizar entre una tercera parte y algo más de la mitad del piso que garantizaría con información perfecta, y
casi nada con presupuestos bajos. Para el piso territorial, M4 no supera a M3 con B ≥ 10.

## 3. Lo que sí funciona como lo pediste

El **criterio de costo con meta de M0 en cada zona** es factible (225/225 corridas óptimas en las primeras
réplicas) y está corriendo. Los cuatro modelos tienen exactamente la misma restricción de equidad territorial.

## 4. Propuesta para la comparación (necesito tu opinión)

**Pieza 1. Criterio de costo con meta por zona = comparación principal.** Tal como la especificaste. Precio de la
información: E_X(m) / E_M2(m), con tu M2 sin E-7 con meta por zona como techo.

**Pieza 2. Piso máximo garantizable = el resultado sobre equidad.** La tabla de la sección 2. Convierte la
infactibilidad en un hallazgo: la falta de información no solo encarece, también limita cuánta equidad
territorial puede prometer el Estado. Ya está calculado.

**Pieza 3. Criterio de cobertura con un piso común FACTIBLE, en lugar del r_B del M1.**
- Para cada B, el r común es el mayor piso que M3, M4 y el placebo cumplen en al menos el 90 % de las réplicas
  (el percentil 10 del piso máximo del peor de los tres).
- Ese mismo r se impone a los **cuatro** modelos, M1 incluido, y se comparan las personas que salen.
- Conserva tu regla de la §3.3: los mismos parámetros de equidad en los cuatro. Lo único que cambia es que r se
  calibra con lo que todos pueden cumplir, en lugar de con lo que solo puede el M1. Con B bajo el r común sale
  casi en cero, y así se dice.
- ρ: como con r_B ya era infactible, propongo dejarlo fuera de la comparación y reportar solo la factibilidad.
- Costo: unos 25 minutos de corridas.

**Sensibilidad (sin equidad territorial):** meta global y r = 0, que son los datos congelados del 10-nov. Miden
cuánto cuesta la equidad territorial en cada modelo.

**Lo que no recomiendo:** comparar solo las réplicas factibles con r_B, porque no hay ninguna, o volver a quitar
la equidad en todos los modelos como comparación principal.

### Preguntas

1. ¿Estás de acuerdo con las tres piezas? En particular, ¿con la regla del r común (90 % de las réplicas) de la
   pieza 3, o prefieres otro criterio?
2. ¿Confirmas los r_B, ρ_B y el M2 con meta por zona de la sección 1?
3. Para tus secciones: en la comparación, tu M1 se correría con el r común de la pieza 3 y tu M2 con meta por zona.
   ¿Te sirve así?

Mientras respondes no reescribo los resultados del paper. Lo que ya cambió está en la rama `paper-12nov`: el
diseño experimental (§3.6) con tu especificación, la tabla de r_B y ρ_B, y la notación m / θ.

---

## 5. Decisión de Jerónimo (12-nov, 15:25): tus restricciones tal cual

Vamos con tu especificación **sin modificar las restricciones**, es decir, con las piezas 1 y 2 de la sección 4.
La pieza 3 (piso común) **no se hace**.

- **Comparación principal:** el criterio de costo con meta de M0 en cada zona, contra tu M2 sin E-7 con meta
  por zona. 54 réplicas, 2.430 MILP óptimos (`resultados/m34/costo_meta_zona_crudo_12nov.csv`).
- **Criterio de cobertura:** con tu r_B, M3, M4 y placebo son infactibles en el 100 % de las réplicas. Se
  reporta así, con la fracción de factibles (0 %) y el piso máximo garantizable de la sección 2.
- **Sensibilidad sin equidad territorial:** meta global y r = 0 (datos congelados del 10-nov).

Resultados del criterio de costo con meta por zona (mediana de 54 réplicas, $ mm de 2025):

| Meta | IP (tu M2) | M3 | M4 | Placebo | M3/IP | M4/IP | M4/M3 (IC 95 %) | M4/placebo (IC 95 %) |
|---|---|---|---|---|---|---|---|---|
| 2 % | 0,47 | 5,91 | 3,93 | 4,05 | 12,5 | 8,3 | 0,64 (0,55–0,73) | 0,94 (0,89–1,04) |
| 6 % | 2,30 | 14,09 | 15,27 | 18,28 | 6,1 | 6,6 | 1,04 (0,94–1,14) | 0,84 (0,76–0,93) |
| 10 % | 5,17 | 28,23 | 25,64 | 38,40 | 5,5 | 5,0 | 0,92 (0,85–1,00) | 0,68 (0,63–0,71) |
| 20 % | 16,11 | 63,32 | 60,54 | 93,17 | 3,9 | 3,8 | 0,95 (0,86–0,98) | 0,65 (0,62–0,66) |
| 30 % | 32,37 | 105,81 | 138,28 | 161,06 | 3,3 | 4,3 | 1,29 (1,24–1,35) | 0,86 (0,84–0,89) |

**Lo que cambia frente a la meta global:** el precio de la información sigue alto (M3 de 3,2 a 12,5 veces la IP),
pero el M4 ya casi no supera al M3, y con metas del 28–30 % es más caro. El placebo queda muy por debajo del M4
(14–37 % más caro desde la meta del 8 %). Con metas por zona, la focalización geográfica es irremplazable.

Sigo esperando que confirmes los r_B, ρ_B y el M2 con meta por zona (sección 1). Reescribo los resultados del
paper con esto en la rama `paper-12nov` y los paso a `main` cuando estén verificados.

**Actualización (12-nov, noche):** los resultados del paper ya están reescritos con esto en la rama `paper-12nov`
(secciones 10–13, resumen, apéndice B; cifras verificadas 16/16 con `m34_verificar_12nov.py`). Corrección: las
corridas infactibles de cobertura son 1.350, no 1.170 (1.170 eran solo las de r_B).
