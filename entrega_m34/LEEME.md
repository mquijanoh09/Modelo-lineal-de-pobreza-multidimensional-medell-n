# Entrega de los Modelos 3 y 4 para el paper

Jerónimo Vélez, 15 de noviembre de 2026. Responde a `PLAN_INTEGRACION_M3_M4.md` de Martín (rama `Contexto`, 14-nov).

| Archivo | Contenido | Sección del plan |
| --- | --- | --- |
| `M34_para_paper.md` | Todo el texto de los Modelos 3 y 4, en Markdown, con los títulos de la sección 3 del plan | §2 y §3 |
| `figuras_m34/*.png` | Figuras M34-1 a M34-3 a 300 dpi | §2 |
| `scripts/m34_figuras_paper.py` | Script que genera las tres figuras desde `datos_m34/` | §2 |
| `datos_m34/*.csv` | CSV de origen de cada tabla y figura | §2 y §5 |
| `cifras_m34.csv` | Una fila por cifra: texto, valor, archivo y columna de origen, y si se cita en el texto | §2 |
| `scripts/` | Cómo se generó todo (ver abajo) | |

## Qué hay que saber al integrar

1. **Tabla 1.** No tuve acceso al borrador (el enlace no está compartido conmigo), así que no conozco sus 11 filas. Las columnas de los Modelos 3 y 4 están en la sección 2 con las filas que distinguen a los cuatro modelos; al integrar hay que pasarlas a las filas del borrador.
2. **Referencias provisionales.** r_B, ρ_B y el Modelo 2 con meta por zona se calcularon con las funciones de Martín sin cambiarlas. Coinciden con la sección 6 de `RESPUESTA_JERONIMO_12NOV.md`; siguen siendo provisionales hasta que Martín lo confirme por escrito.
3. **Caso base y comparación (§6.3 del plan).** La comparación llega hasta B = $100 mil millones y se corre sin E-7 ni SevEdu. La decisión de cómo conectarla con el caso base (B = $424 mil millones) es de Martín; el texto no la toma.
4. **Colores.** Modelo 3 aqua #1baf7a, Modelo 4 amarillo #eda100 y placebo magenta #e87ba4: las ranuras 3 a 5 de la misma paleta categórica de la Figura 9, validadas para daltonismo. Como su contraste con el fondo es bajo, cada serie lleva marcador propio y etiqueta o leyenda.
5. **Numeración provisional.** Tablas M34-1 a M34-14, Figuras M34-1 a M34-3, ecuaciones M3.1 a M3.11 y M4.1 a M4.2.

## Qué es nuevo frente a lo que ya estaba corrido

Todo el criterio de costo, el de presupuesto fijo, el piso máximo garantizable y la validación son las corridas del 12-nov (rama `Modelo3`, commit `a88de3c`), auditadas el 14-nov. Lo único nuevo son dos cosas que pedía la sección 5 del plan:

- **H, A y M0 finales por zona** para el Modelo 3, el Modelo 4 y el placebo. Se repitieron las 4,500 corridas de costo guardando además esos valores (`m34_zonas_costo_15nov.py`). Las soluciones son idénticas a las del 12-nov: el costo y H de cada corrida coinciden al peso, y el script de datos lo comprueba.
- **La misma información para el Modelo 2**, con su propia función `recalcular()` (`m34_ip_zonas_15nov.py`). El costo total coincide con `info_perfecta_meta_zona_12nov.csv`.

## Cómo se reproduce

Desde la raíz de la rama `Modelo3`, con las versiones de `requirements-lock.txt`:

```bash
python3 m34_zonas_costo_15nov.py data/DANE/DEPARTAMENTAL 100 out15/costo 2      # unas 3 horas con 2 núcleos
python3 m34_ip_zonas_15nov.py <Modelos/ de main> out15/ip_zonas.csv              # 1 minuto
python3 m34_base_paper_15nov.py data/DANE/DEPARTAMENTAL datos_m34/                # segundos
# con resultados/m34/ más costo_zonas_crudo_15nov.csv e ip_zonas_15nov.csv en una carpeta R/:
python3 scripts/m34_datos_paper.py R/ datos_m34/
python3 scripts/m34_figuras_paper.py datos_m34/ figuras_m34/
python3 scripts/m34_documento_paper.py datos_m34/ scripts/plantilla_M34.md M34_para_paper.md cifras_m34.csv
python3 scripts/m34_verificar_entrega.py . <paper/cifras.tex de paper-12nov>
```

`m34_documento_paper.py` llena la plantilla con las cifras y las tablas calculadas desde los CSV. Si una cifra no tiene valor, falla: no hay números escritos a mano. `m34_verificar_entrega.py` comprueba que cada cifra citada aparezca en el texto, que coincida con el paper de la rama `paper-12nov` (ya verificado 16/16 y 29/29) y con la sección 6 de `RESPUESTA_JERONIMO_12NOV.md`, que existan las figuras y los CSV citados, y que no haya guiones largos ni flechas.
