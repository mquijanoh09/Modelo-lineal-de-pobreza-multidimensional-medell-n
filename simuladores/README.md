# Simuladores usados para tomar decisiones

Páginas HTML autocontenidas: se abren con doble clic en cualquier navegador, sin instalar nada.
Están en el orden en que se usaron.

| Archivo | Fecha | Qué muestra | Qué se concluyó con él |
|---|---|---|---|
| `del_lepi_a_la_severidad_26oct.html` | 26-oct | Qué hace el paper del LEPI, por qué es un método de evaluación, cómo se adapta a los datos de Antioquia y la opción C (ε-restricción). Incluye simuladores de entropía, ε y ρ. | Pasar de contar pobres a medir severidad (FGT α = 2). La opción C (ε-restricción) se descartó después (ver `docs/resumen_proyecto_ipm.md`). |
| `simulador_severidad_educativa_28oct.html` | 28-oct | Por qué el atraso escolar va al cuadrado, los 215 niños rezagados de Antioquia y cómo se escoge ρ. | Definición de la severidad educativa (SevEdu) y del método para escoger ρ_e. |
| `sevedu_paso_del_tiempo_v2_1nov.html` | 1-nov | La misma SevEdu, ahora con el paso del año (el niño solo avanza si gana el año) sobre los 215 niños. | Con las reglas oficiales, la reducción máxima alcanzable es 21.2 %, así que ρ_e = 29 % es infactible. El codo (Kneedle) queda en 13.7 %. Decisión del 2-nov: caso base sin E3 = cobertura obligatoria 6–15 + ρ_e = 14 %; sensibilidad con E3 = cobertura + 20 %. |

El detalle de las decisiones está en `docs/` y en el grafo de `graphify-out/`.
