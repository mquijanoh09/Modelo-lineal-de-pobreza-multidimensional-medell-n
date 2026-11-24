# Entrega de los Modelos 3 y 4 para el paper

Jerónimo Vélez, 15 de noviembre de 2026. Responde a `PLAN_INTEGRACION_M3_M4.md` de Martín (rama `Contexto`, 14-nov).

| Archivo | Contenido | Sección del plan |
| --- | --- | --- |
| `M34_para_paper.md` | Todo el texto de los Modelos 3 y 4, en Markdown, con los títulos y la numeración del borrador | §2 y §3 |
| `figuras_m34/*.png` | Figuras 10 a 12 a 300 dpi (los archivos se llaman M34-1 a M34-3) | §2 |
| `scripts/m34_figuras_paper.py` | Script que genera las tres figuras desde `datos_m34/` | §2 |
| `datos_m34/*.csv` | CSV de origen de cada tabla y figura | §2 y §5 |
| `cifras_m34.csv` | Una fila por cifra: texto, valor, archivo y columna de origen, y si se cita en el texto | §2 |
| `scripts/` | Cómo se generó todo (ver abajo) | |
| `scripts_modelo3/` | Los scripts de las corridas y todos los módulos `m34_*` que importan, copiados de la rama `Modelo3` (commit `4e7eefc`) para que la entrega se reproduzca desde esta rama | §5 |
| `crudo/` | Salidas crudas por réplica y por B que leen los scripts de `scripts/` (las del 10 y 12-nov, auditadas el 14-nov, y las del 15-nov) | §5 |
| `requirements-lock.txt` | Versiones exactas de Python y de las librerías con las que se reprodujeron las cifras | §5 |

## Qué hay que saber al integrar

1. **Ajustada al borrador de Martín** (`paper_borrador/borrador_paper_2026-11-14.md`, rama `Contexto`, revisión 856). Cada bloque de `M34_para_paper.md` empieza con una línea en cursiva que dice dónde se pega.
2. **Numeración que continúa la del borrador.** Tabla 1 (reemplazo con cuatro columnas y las mismas 11 filas), Tablas 3 a 9 y Figuras 10 a 12 en el cuerpo, Tablas A2 y A3 (nomenclatura de los Modelos 3 y 4, el hueco que dejó el Apéndice 1) y Tablas A9 a A14 en los apéndices. Ecuaciones: OBJ 3, OBJ 4, Restricción₃ 1 a 10 y Restricción₄ 1 a 10. La tabla de restricciones de la comparación va sin número, como las tablas de la §3 del borrador.
3. **Notación del borrador.** I son los 523 hogares pobres y Ī los 3,732 hogares; cᵢⱼ es el costo, Gᵢ la contribución censurada (como en el Modelo 2) y A se reporta como decimal (0.409).
4. **Supuestos.** Los Modelos 3 y 4 no cumplen los supuestos 3 y 7 del borrador (hay error de inclusión y se modelan todos los hogares), ni el 10 (E-7). Se agregan los supuestos 12 a 14.
5. **Referencias provisionales.** r_B, ρ_B y el Modelo 2 con meta por zona se calcularon con las funciones de Martín sin cambiarlas. Coinciden con la sección 6 de `RESPUESTA_JERONIMO_12NOV.md`; siguen siendo provisionales hasta que Martín lo confirme por escrito.
6. **Caso base y comparación (§6.3 del plan): decisión del 15-nov.** Se tomó la opción B (dejar el rango de la comparación y explicar en una frase por qué usa otra versión del Modelo 1) con un puente: B = $424 mil millones se agregó al piso máximo garantizable (Tabla 9, Figura 12; 300 corridas) y a la sensibilidad con r = 0 (Tabla A13; 90 corridas). r_B y ρ_B con B = 424 salen de las funciones de Martín, sin E-7 ni SevEdu (`crudo/ref424.csv`). Martín puede objetar esta decisión en `RESPUESTA_JERONIMO_15NOV.md` (rama `Contexto`).
7. **Colores.** Modelo 3 aqua #1baf7a, Modelo 4 amarillo #eda100 y placebo magenta #e87ba4, las ranuras 3 a 5 de la paleta de la Figura 9, validadas para daltonismo. Como su contraste con el fondo es bajo, cada serie lleva marcador propio y etiqueta o leyenda.

## Qué es nuevo frente a lo que ya estaba corrido

Todo el criterio de costo, el de presupuesto fijo, el piso máximo garantizable y la validación son las corridas del 12-nov (rama `Modelo3`, commit `a88de3c`), auditadas el 14-nov. Lo único nuevo son dos cosas que pedía la sección 5 del plan:

- **H, A y M0 finales por zona** para el Modelo 3, el Modelo 4 y el placebo. Se repitieron las 4,500 corridas de costo guardando además esos valores (`m34_zonas_costo_15nov.py`). Las soluciones son idénticas a las del 12-nov: el costo y H de cada corrida coinciden al peso, y el script de datos lo comprueba.
- **La misma información para el Modelo 2**, con su propia función `recalcular()` (`m34_ip_zonas_15nov.py`). El costo total coincide con `info_perfecta_meta_zona_12nov.csv`.

## Cómo se reproduce

Todo corre **desde la raíz de esta rama** (`entrega-m34-15nov`), con las versiones de `entrega_m34/requirements-lock.txt` (`pip install -r entrega_m34/requirements-lock.txt`). Python agrega la carpeta de cada script a la ruta de importación, así que los módulos `m34_*` de `scripts_modelo3/` se encuentran solos.

Hacen falta dos cosas que no están en `entrega_m34/`:

- **Los microdatos del IPM 2025 del DANE** en `data/DANE/DEPARTAMENTAL/` (en esta rama ya están en la raíz; no se copian a la entrega).
- **El código de los Modelos 1 y 2 de Martín**, la carpeta `Modelos/` de `main` (commit `c741f50`). Se pasa como argumento (`<Modelos/ de main>`), por ejemplo desde un `git worktree add ../main main`. Lo usan `m34_costos_comunes.py`, `m34_ip_zonas_15nov.py`, `m34_b424_15nov.py ref` y las corridas de la comparación, a través de `m34_compat_martin.py`. No se copia, porque es código de Martín.

```bash
S=entrega_m34/scripts_modelo3
R=data/DANE/DEPARTAMENTAL
# 0. Tabla de costos común a los cuatro modelos (se escribe en data/processed/; no se sube)
python3 $S/m34_costos_comunes.py <Modelos/ de main>                                   # 1 minuto
# 1. Corridas del 15-nov
python3 $S/m34_zonas_costo_15nov.py $R 100 out15/costo 2                               # unas 3 horas con 2 núcleos
python3 $S/m34_ip_zonas_15nov.py <Modelos/ de main> out15/ip_zonas.csv                 # 1 minuto
python3 $S/m34_base_paper_15nov.py $R entrega_m34/datos_m34/                           # segundos
# 2. Puente con el caso base (B = 424)
python3 $S/m34_b424_15nov.py ref <Modelos/ de main> out424/ref424.csv                  # ~8 minutos
python3 $S/m34_b424_15nov.py ipmax out424/ipmax.csv                                    # segundos
python3 $S/m34_b424_15nov.py rmax 100 out424/ref424.csv out424/rmax424.csv             # ~4 minutos
python3 $S/m34_equidad_comun.py $R 30 out424/eq 2 424                                  # ~15 minutos
python3 $S/m34_b424_resumen_15nov.py out424/ entrega_m34/crudo/
# 3. Datos, figuras, texto y verificación (desde los CSV de crudo/)
cd entrega_m34
python3 scripts/m34_datos_paper.py crudo/ datos_m34/
python3 scripts/m34_figuras_paper.py datos_m34/ figuras_m34/
python3 scripts/m34_documento_paper.py datos_m34/ scripts/plantilla_M34.md M34_para_paper.md cifras_m34.csv
python3 scripts/m34_verificar_entrega.py . <paper/cifras.tex de paper-12nov>            # 126/126
```

Las salidas crudas del 10 y 12-nov que están en `crudo/` salen de `m34_comparacion_12nov.py` (costo y cobertura con r\_B), `m34_rmax_12nov.py` (piso máximo), `m34_equidad_comun.py` (r = 0), `m34_tablas_12nov.py` y `m34_bootstrap_ic.py` (intervalos), todos en `scripts_modelo3/`; volver a correrlas toma unas 10 horas con 2 núcleos, y la auditoría del 14-nov ya las verificó. `datos_m34/sens_k_u1.csv` es una copia de `resumen_k.csv` (3-nov), que producen `m34_sensibilidad_k.py` y `m34_resumen_k.py`.

**Comprobado el 24-nov desde esta rama:** `m34_costos_comunes.py` reproduce la tabla de costos de `Modelo3` (8,602 pares, idéntica), `m34_b424_15nov.py ipmax` reproduce `crudo/ipmax.csv` exactamente, `m34_base_paper_15nov.py` reproduce los tres CSV de contexto y `m34_datos_paper.py crudo/` reproduce byte a byte los 11 CSV de `datos_m34/` que produce.

`m34_documento_paper.py` llena la plantilla con las cifras y las tablas calculadas desde los CSV. Si una cifra no tiene valor, falla: no hay números escritos a mano. `m34_verificar_entrega.py` comprueba que cada cifra citada aparezca en el texto, que coincida con el paper de la rama `paper-12nov` (ya verificado 16/16 y 29/29) y con la sección 6 de `RESPUESTA_JERONIMO_12NOV.md`, que existan las figuras y los CSV citados, y que no haya guiones largos (salvo «—» en celdas vacías, como en la Tabla 2 del borrador) ni flechas.
