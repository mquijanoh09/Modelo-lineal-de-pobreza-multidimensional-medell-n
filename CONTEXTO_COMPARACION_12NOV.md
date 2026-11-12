# Qué está pasando con la comparación de los 4 modelos y qué tiene que agregar Jerónimo

Actualizado: 12-nov-2026 · Autor: Martín (Modelos 1 y 2) · Para: Jerónimo (Modelos 3 y 4)
Complementa a `CONTEXTO_DATOS.md`. La especificación completa, con las ecuaciones, está en
`ESPECIFICACION_COMPARACION_4_MODELOS.md` (propuesta de Martín del 12-nov; **falta tu acuerdo**).

## 1. Qué está pasando

- El paper ya tiene escritas tus secciones de M3/M4 y la comparación (rama `main`, carpeta `paper/`). Quedan por escribir
  las de Martín (M1/M2) y cerrar la comparación.
- Los Modelos 1 y 2 ya están en `main` (commits del 10-nov) y pasaron tres rondas de auditoría con verificador
  independiente: cumplen su función (0 violaciones). El M1 es el techo de información perfecta con presupuesto fijo B,
  y el M2 el techo con meta de M0.
- **R1 está resuelto (12-nov):** no se implementa «A ≤ A₀ como restricción exacta»; queda como mejora futura. Se mantiene
  ρ por la regla de la brecha. Por eso la especificación sigue en pie tal como está escrita.

## 2. El problema: hoy la comparación no iguala los modelos

El precio de la información (M3 y M4 frente a M1 y M2) solo mide información si los modelos difieren **únicamente en qué
sabe el planificador**. Hoy los igualamos quitándole al M1 sus restricciones de equidad (r = 0, sin techo de severidad) y
dándole al M2 solo una meta global. Pero el M3 y el M4 sí pueden representar esas restricciones. Si no las tienen, la
brecha M1/M2 contra M3/M4 mezcla dos cosas: la falta de información y la falta de equidad. Además, M1/M2 son más
exigentes de lo que parecen en el paper: con equidad por zona el techo de personas que salen baja.

La propuesta los iguala por el otro lado: M3 y M4 **ganan** las restricciones de equidad que sí pueden expresar.
E-7 y SevEdu quedan fuera de la comparación para los cuatro, porque exigen saber qué niño concreto es quién, y en M3/M4
eso lo decide el sorteo.

## 3. Qué tienes que agregar al M3 y al M4, y por qué

| # | Qué agregar | Por qué |
|---|---|---|
| 1 | **Piso por zona** con r_B: `Σ_{i∈I⁰, d(i)=d} p_i·b1_i ≥ r_B · Pobres_d⁰` (caso principal del criterio de presupuesto) | Es la ecuación (4) del M1 y es lineal en `b1_i`: no toca tu mecanismo de cortes. Sin ella, M3/M4 pueden concentrar la salida en la zona más barata y parecer mejores que el M1 con equidad. En el M4 la zona sigue siendo la de P3 |
| 2 | **Techo de severidad** `Σ p_i·q_i ≤ (1−ρ_B)·Sev₀` (solo en la sensibilidad) | Tus tangentes de `q_i` ya existen. Solo falta el techo. No va en el caso principal porque con ρ = 10 % y B ≤ $10 mm ya aparecen réplicas infactibles |
| 3 | **Meta de M0 en cada zona** en lugar de la global: `Σ_{i∈I⁰, d(i)=d} C_i ≤ (1−m)·Σ p_i·c_i⁰` | Es la (M-d) del M2. Con meta global, M3/M4 pueden cumplir la meta bajando M0 donde es barato, y el M2 por zona no; la comparación quedaría sesgada. La meta global queda como sensibilidad |
| 4 | **Mismos valores de r_B y ρ_B** que el M1 (los calcula Martín una sola vez) | Si cada modelo calibra los suyos, la diferencia mide parámetros distintos y no información |
| 5 | **Gap relativo 1e-6 en las dos etapas** (hoy tu segunda etapa de presupuesto usa 1e-4) | La auditoría del M1 mostró que con 1e-4 aparece ruido de ~31 personas. Debe ser la misma tolerancia en los cuatro |
| 6 | **Reportar la fracción de réplicas factibles** en cada B y cada meta, y calcular medianas e IC sobre las factibles | La infactibilidad es un resultado, no un dato que se descarta: si se descarta en silencio, la muestra queda sesgada hacia los sorteos favorables |
| 7 | **Repetir las validaciones de granularidad máxima** (un hogar por celda): M3 con r_B = M1 con r_B; M3 con meta por zona = M2 sin E-7 con meta por zona | Prueba que el M3/M4 modificado converge al techo cuando la información es perfecta. La única diferencia admitida es la ya declarada: el ciclo CLEI que quita a la vez logro y analfabetismo |

**Corridas (sección 4.5 de la especificación):** B = 2, 5, 10, 25, 50 y 100 mm con r_B, y con r_B + ρ_B como sensibilidad
(100 réplicas con B ≤ 10 y 30 con B ≥ 25); las 15 metas del 2 al 30 % con meta por zona (100 réplicas), con la global
como sensibilidad; M3, M4 y placebo con el mismo sorteo por réplica. Entregar los CSV, las tablas regeneradas con
`m34_tablas_paper.py`, las cifras actualizadas en `cifras.tex` y las validaciones.

## 4. Qué entrega Martín

1. `r_rho_comparacion.csv`: r_B y ρ_B para cada B, calculados con el M1 sin E-7 ni SevEdu (r por el codo, ρ por la regla de
   la brecha). Si con algún B la regla de la brecha no es alcanzable, ese B va sin ρ en la sensibilidad y se declara.
2. El M2 sin E-7 con meta por zona, para las mismas 15 metas (hoy solo existe con meta global: 0,35 / 1,32 / 6,47 mil
   millones con 5 / 10 / 20 %).
3. El techo del criterio de presupuesto: personas que saca el M1 con r_B (y con r_B y ρ_B) en cada B.

## 5. Notación y nombres en el paper

- «Criterio de equidad» queda reservado para r, ρ y SevEdu; el criterio de presupuesto fijo se llama criterio de cobertura.
- m = meta de reducción de M0, r = fracción mínima que sale por zona, ρ = reducción mínima de severidad,
  p_i = HS_i·HW_i. En el LaTeX hoy `r` se usa para la meta y `p` para la cobertura: hay que cambiarlos
  (detalle en la sección 6 de la especificación).

## 6. Qué necesito de ti

- Tu acuerdo (o tus objeciones) a la especificación, y cuánto te toma el punto 3 de la sección 3.
- Si algo del M3/M4 no se puede expresar así, dímelo antes de correr nada.
