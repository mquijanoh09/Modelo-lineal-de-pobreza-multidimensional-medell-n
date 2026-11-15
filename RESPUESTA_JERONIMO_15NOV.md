# Respuesta de Jerónimo al plan de integración (15-nov-2026)

De: Jerónimo (Modelos 3 y 4) · Para: Martín (Modelos 1 y 2)
Responde a `PLAN_INTEGRACION_M3_M4.md` (14-nov) y al borrador `paper_borrador/borrador_paper_2026-11-14.md` (revisión 856).

> **Martín: por favor responde en este mismo archivo**, en las líneas «Respuesta de Martín» de la sección 3,
> y haz commit y push a la rama `Contexto`. Si algo de lo que hice no te parece, escríbelo ahí aunque no esté
> en las preguntas. Esta sección 3 reemplaza la sección 6 de `RESPUESTA_JERONIMO_12NOV.md`.

## 1. Qué se entregó

Todo está en la rama **`entrega-m34-15nov`**, carpeta `entrega_m34/`. Empieza por `entrega_m34/LEEME.md`.

| Archivo | Contenido |
| --- | --- |
| `M34_para_paper.md` | Texto de los Modelos 3 y 4 para pegar en tu borrador. Cada bloque dice en cursiva dónde va |
| `figuras_m34/` | Figuras 10 a 12, PNG a 300 dpi, con el script que las genera |
| `datos_m34/` | Un CSV de origen por cada tabla y figura |
| `cifras_m34.csv` | Una fila por cifra del texto, con su archivo y columna de origen |
| `scripts/`, `scripts_modelo3/`, `crudo/` | Cómo se generó todo y las salidas crudas de las corridas nuevas |

Cómo sigue tu plan:

- **Formato:** Markdown, con notación Unicode, punto decimal, coma de miles y dinero en «mil millones».
- **Estructura:** los títulos y el orden de tu borrador, con los rótulos *Cómo se lee*, *Qué se observa* e *Interpretación* en las figuras.
- **Notación de tu borrador:** I = 523 hogares pobres, Ī = 3,732 hogares, cᵢⱼ el costo, Gᵢ la contribución censurada (como en tu Modelo 2) y A como decimal (0.409). Ecuaciones: OBJ 3, OBJ 4, Restricción₃ 1 a 10 y Restricción₄ 1 a 10.
- **Cifras:** ninguna escrita a mano. El texto se genera desde los CSV, y `scripts/m34_verificar_entrega.py` comprueba 126 de 126 cosas: cada cifra aparece en el texto, coincide con el paper auditado del 14-nov y con las referencias de la §6 del 12-nov, y existen las figuras y los CSV citados.

Corridas nuevas, sin cambiar ningún modelo:

1. **H, A y M0 finales por zona** (tu §5.4). Se repitieron las 4,500 corridas de costo guardando esos valores. Son idénticas a las del 12-nov: el costo y H coinciden corrida por corrida.
2. **El Modelo 2 por zona**, con tu `recalcular()`. El costo total coincide con el del 12-nov.
3. **El puente con el caso base (B = $424 mil millones)**, explicado en la decisión D1.

## 2. Decisiones que tomé y que puedes objetar

**D1. Cómo se conecta la comparación con el caso base (tu §6.3).** Tomé la opción B (dejar el rango y explicar en una frase por qué la comparación usa otra versión del Modelo 1) con un puente: agregué B = 424 solo a las corridas que son factibles con información imperfecta.

- *Por qué no solo la opción A.* Con r\_B, M3 y M4 ya son infactibles desde B = 2. Con B = 424 también lo serían, así que esa corrida sola no aporta información nueva. Además, ni con 424 sería tu caso base, porque la comparación no lleva E-7 ni SevEdu.
- *Lo que se corrió con B = 424.* Las referencias, con tus funciones sin cambiarlas y sin E-7 ni SevEdu, en `crudo/ref424.csv`:

  | Referencia con B = 424 | Valor |
  | --- | --- |
  | r\_B (codo) | 0.896. En tu caso base, con E-7 y SevEdu, es 0.833 |
  | ρ\_B (regla de la brecha) | 0.509. La regla se alcanza: A = 0.405 ≤ A₀ |
  | Personas que salen con el M1 y r\_B | 629,203 |
  | Personas que salen con el M1 y r = 0 | 629,400 |

  Además, el piso máximo garantizable con 100 réplicas (Tabla 9 y Figura 12) y la sensibilidad con r = 0 con 30 réplicas (Tabla A13). Todas las corridas son óptimas.
- *Qué dice.* Con B = 424, sin información individual el Estado solo puede garantizar que salga el 51.2 % de los pobres de cada zona con M3 y el 44.8 % con M4, frente al 91.7 % con información perfecta y al 89.6 % que exige r\_B. Ninguna réplica alcanza r\_B. Con r = 0, M3 saca a 389,359 personas y M4 a 392,921, frente a 629,400 del Modelo 1: alrededor del 62 %.
- *Criterio de costo.* Se queda con metas del 2 al 30 %. Una meta del 85 %, como la de tu Tabla 2, obliga a atender a casi todos y no es el rango donde la información importa.
- *Frase para el paper.* Al inicio de la comparación, en la sección 4, se dice que las cifras de M1 y M2 de la comparación no son las de la Tabla 2 porque no llevan E-7 ni SevEdu, y que B = 424 se incluye como puente con el caso base.

**D2. Numeración y ubicación.** La Tabla 1 se reemplaza por una con cuatro columnas y tus mismas 11 filas; las columnas de M1 y M2 quedan sin cambios. En el cuerpo van las Tablas 3 a 9 y las Figuras 10 a 12; en los apéndices, las Tablas A2 y A3 (la nomenclatura de M3 y M4, el hueco que dejó tu Apéndice 1) y las Tablas A9 a A14. La tabla de restricciones de la comparación no lleva número, como las de tu §3.

**D3. Supuestos.** M3 y M4 no cumplen tus supuestos 3 (no hay error de inclusión) ni 7 (solo se modelan los pobres), y no llevan el 10 (E-7). Del supuesto 2 se pierde que un ciclo CLEI quite a la vez logro y analfabetismo. Agregué los supuestos 12 (el sorteo), 13 (las celdas) y 14 (las réplicas).

**D4. Columnas de M3 y M4 en la Tabla 1.** Las cuatro filas que más cambian son estas:
- Se puede intervenir cualquier hogar con privaciones: S en M3 y M4.
- Focalización precisa: N en M3 y M4.
- Desperdicio en hogares privados pero no pobres: S, con el error de inclusión.
- Bienes públicos y privados: S solo en M4.

**D5. Colores de las figuras.** M3 aqua #1baf7a, M4 amarillo #eda100 y placebo magenta #e87ba4: las ranuras 3 a 5 de la paleta de tu Figura 9, validadas para daltonismo. M1 y M2 conservan tu azul y tu naranja.

**D6. Cómo se presenta H en M3 y M4.** Con la misma meta de M0, M3 y M4 bajan H tanto o más que el M2 en 12 o 13 de las 15 metas, porque gastan varias veces más y sobrepasan la meta en algunas zonas. El texto lo presenta como reflejo del costo, no como ventaja. En el rural disperso pasa lo contrario: el M2 baja más H, porque saca primero a los hogares cercanos al umbral.

## 3. Preguntas para Martín (responde aquí)

**P1. Referencias del 12-nov.** Tu plan dice que el 13-nov verificaste en tu computador que r\_B, ρ\_B y el Modelo 2 con meta por zona coinciden. Los valores de r\_B son 0.036 / 0.073 / 0.146 / 0.238 / 0.344 / 0.522 para B = 2 / 5 / 10 / 25 / 50 / 100; ρ\_B vale 0.165 con B = 25 y 0.215 con B = 50; el M2 por zona cuesta 0.47 / 2.30 / 5.17 / 16.11 / 32.37 mil millones con metas del 2 / 6 / 10 / 20 / 30 %. ¿Lo confirmas por escrito y estás de acuerdo con que el paper los use?

**Respuesta de Martín:** _(escribe aquí)_

**P2. Referencias nuevas de B = 424.** r\_B = 0.896, ρ\_B = 0.509, 629,203 personas con r\_B y 629,400 con r = 0, sin E-7 ni SevEdu. ¿Te dan lo mismo con tu código? Se reproducen con `python3 m34_b424_15nov.py ref <Modelos/ de main> ref424.csv`, en unos 8 minutos.

**Respuesta de Martín:** _(escribe aquí)_

**P3. Decisión D1.** ¿Estás de acuerdo con la opción B con el puente de B = 424? Si prefieres otra cosa, dime cuál.

**Respuesta de Martín:** _(escribe aquí)_

**P4. Tabla 1 (D4).** ¿Cambiarías algo de las columnas de M3 y M4?

**Respuesta de Martín:** _(escribe aquí)_

**P5. Las demás decisiones (D2, D3, D5 y D6).** ¿Algo que no te parezca?

**Respuesta de Martín:** _(escribe aquí)_

**P6. Conteo de privaciones.** El 10-nov entendí que habías subido un cambio que cuenta varias personas privadas por hogar en los Modelos 1 y 2, y no lo encontré en ninguna rama. ¿Existe? ¿En qué rama está? Si cambia el conteo de personas, cambian los costos de los cuatro modelos.

**Respuesta de Martín:** _(escribe aquí)_

**Cualquier otra cosa que no te parezca:** _(escribe aquí)_

## 4. Cómo revisarlo

```bash
git fetch origin
git checkout entrega-m34-15nov          # entrega completa en entrega_m34/
python3 entrega_m34/scripts/m34_verificar_entrega.py entrega_m34 <paper/cifras.tex de paper-12nov>   # 126/126
```

Mientras no respondas P1 y P2, los valores de referencia siguen marcados como provisionales en el texto. Si alguno cambia, en el criterio de costo solo cambia la columna de información perfecta; la factibilidad, r\_max y la sensibilidad con r = 0 sí hay que repetirlas, en menos de una hora.
