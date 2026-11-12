# Especificación: cómo se corren y se comparan los 4 modelos

*Proyecto IPM Antioquia, Optimización 1 (EAFIT). Martín y Jerónimo. 12-nov-2026.*
*Estado: propuesta de Martín (12-nov), pendiente de su confirmación final. **Falta el acuerdo de Jerónimo.***

## 1. Idea central

En el paper hay dos tipos de resultados, y cada uno usa una versión distinta del M1 y el M2:

1. **Resultados propios del M1 y el M2.** Responden qué hace el Estado con información perfecta **y** con las obligaciones legales. Se corren con todo lo que ya está decidido.
2. **Comparación de los 4 modelos (el precio de la información).** Los modelos solo pueden diferir en **qué sabe el planificador**. Todo lo demás (datos, costos, reglas de qué se puede quitar en un año y restricciones de equidad) tiene que ser igual en los cuatro.

Hoy, la comparación iguala los modelos **quitándole** al M1 todas sus restricciones de equidad (r = 0, sin techo de severidad). Esta especificación los iguala por el otro lado: el M3 y el M4 **ganan** las restricciones de equidad que sí pueden representar.

## 2. Resultados propios del M1 y el M2 (sin cambios)

| Modelo | Restricciones del caso base | Fuente |
|---|---|---|
| M1 | E-7 (art. 67), SevEdu con ρ_e = 14 %, r por el codo de H contra r, ρ por la regla de la brecha (A ≤ A₀), dos etapas | `modelo1/formulacion_modelo1.md` |
| M2 | E-7 y meta de M0 **en cada zona** (M-d). Sin r ni ρ: la meta por zona hace el papel de r, y el techo de severidad se descartó (D-M2-2). SevEdu solo como sensibilidad | `modelo2/formulacion_modelo2.md` |

## 3. Comparación de los 4 modelos

### 3.1 Qué entra y qué no

| Restricción | M1 / M2 en la comparación | M3 / M4 | Por qué |
|---|---|---|---|
| E-7 (cobertura escolar obligatoria) | **No** | No | Exige saber qué niño concreto no asiste. En M3 y M4 eso lo decide el sorteo |
| SevEdu (techo de severidad educativa) | **No** | No | Igual: exige decisiones niño por niño |
| r (fracción mínima que sale en cada zona) | **Sí** (criterio de presupuesto) | **Sí, se agrega** | Es lineal en b1_i y no depende de saber quién es quién |
| ρ (techo de severidad) | **Sí, como sensibilidad** | **Sí, como sensibilidad** | Lineal con tangentes. No va en el caso principal porque, en las corridas de Jerónimo, con ρ = 10 % y B ≤ $10 mm ya aparecen réplicas infactibles en M3 y M4 |
| Meta de M0 por zona | **Sí** (criterio de costo) | **Sí, reemplaza la meta global** | Es la versión de equidad territorial que usa el M2 |

El texto del paper debe decir en una línea por qué el E-7 y SevEdu quedan fuera de la comparación.

### 3.2 Los dos criterios

| Criterio | Información perfecta | Pregunta | Precio de la información |
|---|---|---|---|
| Presupuesto fijo B | M1 sin E-7 ni SevEdu, con r (y ρ en la sensibilidad) | ¿Cuántas personas salen con B? | H_X(B) / H_M1(B) |
| Meta de M0 | M2 sin E-7, con meta en cada zona | ¿Cuánto cuesta bajar M0 un m % en cada zona? | E_X(m) / E_M2(m) |

**Nombre:** en el paper, el criterio de presupuesto fijo **no** se llama "criterio de equidad". Maximizar las personas que salen es un criterio de cobertura (H). "Equidad" queda reservado para r, ρ y SevEdu.

### 3.3 Tres reglas para que la comparación sea válida

1. **Los mismos valores de r y ρ en los cuatro modelos.** Para cada B, r y ρ se calculan **una sola vez** con el M1 de la comparación (sin E-7 ni SevEdu) y se imponen iguales al M3 y al M4. No se recalculan por modelo. Si cada modelo calibrara los suyos, la diferencia mediría parámetros distintos y no solo la información.
2. **La infactibilidad es un resultado, no un dato que se descarta.** Para cada configuración se reporta la fracción de réplicas factibles. Las medianas e intervalos se calculan sobre las factibles y se dice cuántas son. Si se descartaran en silencio, la muestra quedaría sesgada hacia los sorteos favorables.
3. **La misma tolerancia en todos.** Gap relativo de 1e-6 en las dos etapas de todos los modelos. Hoy, la segunda etapa del criterio de presupuesto en M3 y M4 usa 1e-4.

## 4. Lo que Jerónimo tiene que agregar al M3 y al M4

Notación de esta sección: p_i = HS_i·HW_i (personas que representa el hogar); I⁰ = hogares pobres de la línea base; d(i) = zona P3 del hogar. **En el M4 la zona sigue siendo la de P3**, aunque las celdas de focalización de los bienes privados sean tipos de hogar.

### 4.1 Criterio de presupuesto fijo: tasa mínima de salida por zona (caso principal)

Para cada zona d ∈ {cabecera, centro poblado, rural disperso}:

```
Σ_{i ∈ I⁰, d(i) = d}  p_i · b1_i  ≥  r_B · Pobres_d⁰ ,     Pobres_d⁰ = Σ_{i ∈ I⁰, d(i) = d} p_i
```

- r_B es el valor que entrega Martín para cada B (sección 5). Es la misma ecuación (4) del M1.
- No cambia el mecanismo de cortes: la restricción solo usa b1_i, que ya existe.
- La condición de salida se mantiene como ya está en la implementación: s_i ≤ 0,33 + (s_i⁰ − 0,33)(1 − b1_i).

### 4.2 Criterio de presupuesto fijo: techo de severidad (solo en la sensibilidad)

Su código ya tiene las tangentes de q_i para el desempate de la segunda etapa. Solo falta el techo:

```
q_i ≥ 2a · s_i − a²          para todo i ∈ I⁰ y todo a ∈ A_i   (ya existe)
Σ_{i ∈ I⁰}  p_i · q_i  ≤  (1 − ρ_B) · Sev₀ ,     Sev₀ = Σ_{i ∈ I⁰} p_i (c_i⁰)²
```

- s_i es el puntaje final **completo**: incluye como constantes las privaciones que no se pueden quitar en un año (rezago, logro que excede un ciclo, analfabetismo sin ganancia y desempleo sin desocupado identificable).
- A_i son los valores que puede tomar s_i, igual que en el M1.
- Sev₀ ≈ 117,908, con la misma convención del M1: sin censurar y sobre los 523 hogares pobres iniciales, incluidos los que salen.
- ρ_B es el valor que entrega Martín para cada B (sección 5).

### 4.3 Criterio de costo: meta de M0 en cada zona (reemplaza la meta global)

Para cada zona d:

```
Σ_{i ∈ I⁰, d(i) = d}  C_i  ≤  (1 − m) · Σ_{i ∈ I⁰, d(i) = d}  p_i · c_i⁰
```

- El lado derecho es M0_d⁰ · Pob_d (la población de la zona se cancela al pasar de M0 a contribuciones), igual que la (M-d) del M2.
- Las tres metas por zona implican la meta global.
- La meta global queda como sensibilidad: sirve para medir el costo de la equidad territorial en los 4 modelos.

### 4.4 Validaciones que hay que repetir

1. **Granularidad máxima con r.** Con un hogar por celda, el M3 con r_B debe sacar las mismas personas que el M1 de la comparación con r_B.
2. **Granularidad máxima con meta por zona.** Con un hogar por celda, el M3 con meta por zona debe costar lo mismo que el M2 sin E-7 con meta por zona. La única diferencia admitida es la ya declarada: el ciclo CLEI que quita a la vez logro y analfabetismo.
3. **Factibilidad.** Reportar cuántas réplicas son factibles en cada B (con r y con r + ρ) y en cada meta.

### 4.5 Corridas y entregables

- **Criterio de presupuesto:** B = 2, 5, 10, 25, 50 y 100 mm. Dos escenarios: (a) con r_B (caso principal) y (b) con r_B y ρ_B (sensibilidad). Réplicas: las mismas reglas de hoy (100 con B ≤ 10 y 30 con B ≥ 25).
- **Criterio de costo:** las mismas 15 metas de hoy, del 2 al 30 %, con meta por zona; 100 réplicas. Meta global como sensibilidad.
- **M3, M4 y placebo** con el mismo sorteo R por réplica (comparación pareada, como hoy).
- **Entregar:** los CSV de resultados, las tablas regeneradas con `m34_tablas_paper.py`, las cifras actualizadas en `cifras.tex` y la validación de la sección 4.4.

## 5. Lo que Martín tiene que entregar

1. **r_B y ρ_B para cada B** (2, 5, 10, 25, 50 y 100 mm) en un CSV (`r_rho_comparacion.csv`). Se calculan con el M1 de la comparación: sin E-7 ni SevEdu, r por el codo y ρ por la regla de la brecha, con el mismo procedimiento del caso base.
   - Si con algún B la regla de la brecha no es alcanzable, ese B va sin ρ en la sensibilidad y se declara.
   - La decisión R1 de la auditoría (A ≤ A₀ como restricción exacta en vez de ρ) quedó como mejora futura (Martín, 12-nov; `mejoras/mejoras_modelo.md` §12). Se mantiene ρ por la regla de la brecha.
2. **El techo de información perfecta con meta por zona:** el M2 sin E-7 con meta en cada zona, para las mismas 15 metas. Hoy solo existe la versión sin E-7 con meta **global** (0.35 / 1.32 / 6.47 mm con 5 / 10 / 20 %).
3. **El techo del criterio de presupuesto:** las personas que saca el M1 de la comparación con r_B (y con r_B y ρ_B) en cada B.

## 6. Notación en el paper

Para que no choque con el M1:

| Símbolo | Uso único |
|---|---|
| m | Meta de reducción de M0 (hoy, en el LaTeX, es r) |
| r | Fracción mínima de personas pobres que sale en cada zona |
| ρ | Reducción mínima de la severidad |
| θ (u otra letra) | Cobertura de un par (indicador, celda) (hoy, en el LaTeX, es p) |
| p_i | Personas que representa el hogar, HS_i·HW_i |

Las demás colisiones (k, K, c_ij, C, M, b1_i/y_i) están en la observación BM2 del informe de revisión.

## 7. Pendientes

- [ ] Acuerdo de Jerónimo con esta especificación.
- [x] Decisión de Martín sobre R1: queda como mejora; se mantiene ρ (12-nov).
- [ ] Martín: `r_rho_comparacion.csv`, M2 sin E-7 con meta por zona y techo del M1 con r_B (sección 5).
- [ ] Jerónimo: restricciones 4.1–4.3, validaciones 4.4 y corridas 4.5.
- [ ] Actualizar la §3.6 (diseño experimental) y las secciones de resultados del paper.
