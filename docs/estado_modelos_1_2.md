# Estado de los Modelos 1 y 2 — programación completada (5-nov-2026)

*Martín no pudo terminar la programación de los Modelos 1 y 2. Jerónimo la completó a partir del último commit de
Martín (`0389805`, 4-nov), siguiendo sin cambios `docs/formulacion_modelo1.md`, `docs/formulacion_modelo2.md`, las
decisiones D1–D5, P1–P8, D-M2-1 a D-M2-4 y F2-1 a F2-5, y el grafo `graphify-out/perspectiva_equidad`. Lo que se
decidió al programar está en `justificacion_decisiones.md` (P9–P13) y `justificacion_decisiones_modelo2.md` (F3-1 a F3-4).
**Este documento es para auditar:** resultados, verificaciones y puntos abiertos.*

## 1. Qué se programó

| Archivo | Qué hace |
|---|---|
| `Modelos/datos_modelo.py` | Arma los datos del MILP desde lo que dejó el 05: 523 hogares pobres, $J_i$, $c_{ij}$ por escenario, niños ($K \cup N$) con $d_{ks}$, $b_k$ y $\text{coef}_{ks}$, adultos CLEI con $g_a$, $D_i$, $A_i$, $\text{Sev}_0$ y $\text{SevEdu}^N_{1,\text{sin}}$ |
| `Modelos/modelo_base.py` | Clase `ModeloIPMBase` (P7/F2-4): variables x, y, z, t, v; reglas (2), E-1, E-2, E-3, E-7, (10a)/(10b), (Inas), (11), (12); `costo_total()`, `agregar_sevedu()`, `recalcular()` desde x |
| `Modelos/Modelo_1/modelo1.py` | Clase `Modelo1`: (1), (4), (7), (8), (E-5) y las dos etapas de D1. Modos auxiliares: `sev_min`, `r_max`, `costo_H` |
| `Modelos/Modelo_1/08_modelo1.py` | Rango de B y caso base |
| `Modelos/Modelo_1/08_modelo1_barridos.py` | Curva B → H; barridos de r y ρ con codo y regla de la brecha; sensibilidades |
| `Modelos/Modelo_2/modelo2.py` | El núcleo de Martín (3.2/3.3) intacto, más `fijos_cero`, `meta_maxima()` y la clase `Modelo2` |
| `Modelos/Modelo_2/09_modelo2.py` | Meta máxima y metas 5/10/20 % (base, meta_global, con_sevedu) |
| `Modelos/Modelo_2/09_modelo2_barridos.py` | Curva costo vs. meta, sensibilidades y validación cruzada con el M1 |
| `Modelos/prueba_modelos_1_2.py` | Pruebas de regresión (todas pasan) |

Las pruebas de Martín `prueba_3_2.py` y `prueba_3_3.py` siguen pasando contra sus algoritmos exactos.

## 2. Verificaciones que pasan

- **Valores de control:** 523 pobres, M0 = 0.038684, Sev₀ = 117,908, SevEdu_sin = 21,562, 6,571 tangentes, 215 niños en la cohorte, 29 con E-7.
- **(2) big-M $M_i = c_i^0 - 0.33$:** válido, porque $s_i \le c_i^0$ siempre; con $y_i = 0$ el lado derecho es $c_i^0 \ge s_i$. Es el más ajustado posible. En todas las corridas, $y_i = 1$ solo si el hogar sale al recalcular desde x.
- **(3) censura con $U_i = p_i c_i^0$:** con $y_i = 1$ el lado derecho es $p_i(s_i - c_i^0) \le 0$. Se verificó que $\sum C_i$ es igual al numerador de M0 recalculado.
- **(7) tangentes:** en la etapa 2, $q_i = s_i^2$ con error máximo de 8×10⁻¹⁴. Las tangentes son exactas porque $s_i$ solo toma valores en $A_i$.
- **D1 dos etapas:** H* sale de la incumbente; la etapa 2 nunca fue infactible.
- **Costos:** el costo recalculado hogar por hogar nunca supera B.
- **Piso de E-7 + SevEdu 14 %:** $105.9 mil millones. Coincide con los "$105.8 mm" del grafo (decisión del 2-nov).

## 3. Resultados del Modelo 1 (caso base: p = 0.369, sin E3, ρ_e = 14 %, E-7)

**Rango de B (pendiente P5, recalculado con los costos verificados):**

| | Valor |
|---|---|
| $B_{piso}$ (H = 0; E-7 + SevEdu) | $105.9 mil millones |
| H máximo factible | 683,406 personas: **los 523 hogares pueden salir** |
| $B_{sat}$ (mínimo para sacar a todos) | **$658.9 mil millones** (antes ≈ $0.50 billones) |
| Quitar todas las privaciones simples | $8.26 billones (antes ≈ $7.29 billones) |

**Curva B → H** (r = 0, ρ = 0; B = $B_{piso}$ + f·($B_{sat}$ − $B_{piso}$)):

| f | B ($ mm) | Personas que salen | H | A | M0 | Severidad |
|---|---|---|---|---|---|---|
| 0 | 105.9 | 7,663 | 9.34 % | 40.81 % | 0.0381 | 116,328 |
| 0.10 | 161.2 | 302,491 | 5.27 % | 42.98 % | 0.0226 | 95,499 |
| 0.30 | 271.8 | 467,764 | 2.98 % | 43.86 % | 0.0131 | 79,521 |
| 0.50 | 382.4 | 565,014 | 1.64 % | 44.25 % | 0.0072 | 68,470 |
| 1.00 | 658.9 | 683,406 | 0.00 % | — | 0 | 53,692 |

**Caso base en $B_{ref}$ = $271.8 mm (f = 0.30, provisional):** salen 258 de 523 hogares (467,764 personas); H baja de 9.45 % a 2.98 % y M0 de 0.0387 a 0.0131. Por zona, H queda en 1.68 % en cabecera, 4.60 % en centro poblado y 10.01 % en rural disperso.

**Hallazgo para la narrativa:** con ρ = 0, **A sube** de 40.94 % a 43.86 %. Maximizar H saca primero a los que están cerca del umbral, y los que quedan son más pobres en promedio. Es justo la crítica al objetivo H que motivó el techo de severidad.

**Barrido de ρ en $B_{ref}$:** ρ_max = 39.86 %.
- Hasta ρ ≈ 27 % el techo no cuesta ninguna persona.
- El codo está en ρ ≈ 33 %: se pierden 166 personas y A baja a 43.27 %.
- La regla "la brecha no crece" (A ≤ A₀) solo se cumple en ρ_max: con 388,757 personas (−17 %), A queda en 38.44 %.

**Barrido de r en $B_{ref}$:** la equidad por zona (4) no aprieta hasta r ≈ 60 %, porque todas las zonas ya superan esa fracción. r_max = 67.1 %: cuesta unas 9,000 personas y desplaza ~17,000 personas hacia el rural disperso.

**Sensibilidades en $B_{ref}$** (personas que salen): base 467,764 · p = 0.50: 485,780 · p = 0.75: 502,117 · con E3: 503,865 · u = 1: 506,436 · TI psicosocial: 468,124 · acueducto BID: 467,764 (sin cambio: aun a $9.7 M, el acueducto rural pesa 0.04 y no es costo-efectivo).

## 4. Resultados del Modelo 2

**Meta máxima (E-7, sin límite de costo): 100 % en las tres zonas.** Es coherente con el M1: todos los hogares pueden salir.

**Costo mínimo** ($ mil millones):

| Meta m | base (meta por zona) | meta_global | con_sevedu |
|---|---|---|---|
| 5 % | 105.6 | 104.7 | 107.1 |
| 10 % | 108.7 | 105.4 | 110.2 |
| 20 % | 118.6 | 109.1 | 120.1 |

Casi todo es el piso de E-7: unos $104 mm aunque m = 0, en su mayor parte en rural disperso. La meta por zona encarece la de 20 % en $9.5 mm frente a la global, porque obliga a gastar en rural disperso (37 hogares salen allí, contra 10 con meta global). Ese es el costo de la equidad territorial.

**Curva costo vs. meta** (`09_modelo2_barridos.py 0.1`; gap máximo 9.5×10⁻⁷ en todos los puntos):

| m | 0 | 10 % | 20 % | 30 % | 40 % | 50 % | 60 % | 70 % | 80 % | 90 % | 100 % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Por zona ($ mm) | 104.4 | 108.7 | 118.6 | 133.3 | 157.2 | 192.3 | 237.9 | 295.0 | 370.2 | 465.4 | 657.4 |
| Global ($ mm) | 104.4 | 105.4 | 109.1 | 125.4 | 152.0 | 188.4 | 232.7 | 289.0 | 362.1 | 460.6 | 657.4 |

- **El piso de E-7 es $104.4 mm.** Las metas bajas casi no cuestan más que cumplir el art. 67; la curva es convexa y se dispara después del 80 %.
- **m = 100 % cuesta $657.4 mm.** Coincide con el $B_{sat}$ del M1 ($658.9 mm); la diferencia de $1.5 mm es el techo de SevEdu que el M1 lleva fijo.

**Sensibilidades en m = 10 %:**
- p = 0.50 cuesta $92.0 mm y p = 0.75 cuesta $76.3 mm, con el mismo plan. Solo cambia lo que cuesta la Renta Ciudadana de E-7.
- Con E3 cuesta $70.1 mm, porque el CLEI de secundaria es más barato que E1 para cumplir E-7.
- u = 1 cuesta $108.4 mm.
- Trabajo infantil psicosocial y acueducto BID no cambian nada.

**Validación cruzada (formulación §6), cumple en las tres metas.** Con el mismo B, el M1 saca a más personas que el plan del M2:

| Meta | M2 | M1 |
|---|---|---|
| 5 % | 35,650 | 79,835 |
| 10 % | 73,919 | 139,014 |
| 20 % | 149,416 | 187,454 |

Así debe ser: el M1 maximiza personas y el M2 minimiza costo para una meta de M0.

## 5. Puntos abiertos para auditar (no se decidieron al programar)

1. **B del caso base del M1:** `FRACCION_B_REF = 0.30` es provisional (P11). Hay que acordarlo en el equipo, por ejemplo usando el B* del M2 en m = 10 % para comparar los modelos con el mismo presupuesto.
2. **Objeción 3 (sigue abierta):** el codo de ρ_e debe tomarse sobre H vs. SevEdu, no sobre el costo. ρ_e sigue fijo en 14 % (decisión del 2-nov).
3. **Jóvenes de 15 a 17 años que están en las dos tablas:** 88 personas aparecen en `ninos.csv` y en `adultos_clei.csv`; 40 de ellas son elegibles a CLEI como adultos. El modelo podría pagarles un $z_{k,E2}$ y un $v_a$ (dos ciclos CLEI), y un $v_a$ no quita su inasistencia. La formulación no lo trata. Propuesta: $z_{k,E2} + v_a \le 1$, o excluir de `adultos_clei` a los menores de 18 que están en `ninos`. **No se agregó** porque sería una restricción que no está en `docs/`.
4. **Un hogar** marcado con inasistencia por el DANE no tiene en `ninos.csv` ningún no asistente de 6 a 16 años; su $x_{inas}$ queda en 0 (P10).
5. **Severidad en el M2:** el M2 no la controla (D-M2-2); se reporta después de resolver.
6. **Gap en los barridos del M2:** las metas intermedias pueden tardar más de 60 s; en los barridos se corta a 60 s y se guarda el gap de cada punto en `m2_barrido_meta.csv`.
7. **Comunicar a Martín** los cambios en `parametros.py`: sección 11 (`SOLVER_M1`, `TOL_H_ETAPA2`, `FRACCIONES_B`, `FRACCION_B_REF`) y `SOLVER_M2_BARRIDO`.

## 6. Cómo correr todo

```
python Modelos/datos_modelo.py
python Modelos/prueba_modelos_1_2.py
python Modelos/Modelo_2/prueba_3_2.py ; python Modelos/Modelo_2/prueba_3_3.py
python Modelos/Modelo_1/08_modelo1.py            # rango de B y caso base (~30 s)
python Modelos/Modelo_1/08_modelo1_barridos.py   # ~2 min
python Modelos/Modelo_2/09_modelo2.py            # ~1 min
python Modelos/Modelo_2/09_modelo2_barridos.py 0.1   # ~25 min con paso 0.1 (60 s máx. por punto)
```
Los resultados quedan en `Modelos/Modelo_1/resultados/` y `Modelos/Modelo_2/resultados/`.
