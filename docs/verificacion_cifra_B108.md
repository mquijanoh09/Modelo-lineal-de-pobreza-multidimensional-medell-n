# Verificación de la cifra del paper: B = $108 mil millones, r = 0 (14-nov-2026)

**Cifra verificada (Modelo 1, ρ_e = 0.14, sin equidad r = 0 y sin techo de severidad):**
cabecera **27.9 %**, centro poblado **3.6 %** (3.55), rural disperso **1.1 %** (1.108).

## Procedencia
- Corrida del 14-nov-2026 en el PC de Martín, PuLP 3.3.2 + HiGHS, gap 1e-6, `.venv` del proyecto.
- Código: commit `9731943`; `Modelos/Modelo_1/`, `parametros.py`, `datos_modelo.py`, `modelo_base.py` y `05_conteo_personas.py` sin cambios frente a ese commit (`git status` limpio). Datos: `data/processed/*.csv` del 6-nov-2026 (`hogares_antioquia.csv` del 15-oct).
- Costos y reglas vigentes: caso base (D8: el desempleo sin desocupado identificado no se paga; p = 0.369; sin E3; ρ_e = 0.14 con E-7).
- Estado: Optimal en las dos etapas, gap ≤ 5e-16. El costo es $107.9998 mil millones. H* = 106,666 personas.

## Resultado exacto y denominadores

| Zona | Hogares pobres (muestra) | Personas pobres (denominador) | Hogares que salen | Personas que salen | % |
|---|---|---|---|---|---|
| Cabecera | 127 | 363,286 | 14 | 101,431 | 27.920 % |
| Centro poblado | 103 | 69,089 | 2 | 2,454 | 3.551 % |
| Rural disperso | 293 | 251,031 | 3 | 2,781 | 1.108 % |
| Total | 523 | 683,406 | 19 | 106,666 | 15.6 % |

El 1.1 % **no es redondeo de un entero de hogares**: son 3 hogares de la muestra con factores de expansión de 135.9, 209.0 y 436.7, que suman 2,781 personas de 251,031. Cada hogar de la muestra representa muchas personas.

## Por qué antes salía 1.5 % en el rural
El barrido de B no usa B = 108.000 sino su primer punto de la malla, **B = 108.041** (= 1.02 × B_min, con B_min = 105.92). Con costos y código vigentes, ese punto da cabecera 27.92 %, centro poblado 3.55 % y **rural 1.48 %** (2 hogares rurales, 3,721 personas). Es decir, el 1.5 % no venía solo de los costos viejos: es la cifra de B = $108.04 mil millones y sigue saliendo en el `barrido_B.csv` regenerado hoy.

## La cifra por zona es frágil cerca del mínimo
Con r = 0 el modelo maximiza el total y la zona solo cambia según qué pocos hogares compra el presupuesto. Corridas con los costos vigentes:

| B (mil millones) | Personas que salen | Cabecera | Centro poblado | Rural disperso |
|---|---|---|---|---|
| 107.0 | 76,337 | 20.16 % | 3.55 % | 0.25 % |
| 107.5 | 92,773 | 24.69 % | 3.55 % | 0.25 % |
| **108.0** | **106,666** | **27.92 %** | **3.55 %** | **1.11 %** |
| 108.041 | 107,606 | 27.92 % | 3.55 % | 1.48 % |
| 108.5 | 119,300 | 31.73 % | 4.91 % | 0.25 % |
| 109.0 | 128,795 | 32.16 % | 7.56 % | 2.68 % |
| 110.0 | 138,072 | 32.16 % | 14.83 % | 4.38 % |

La cifra total sí es estable y única (H* = 106,666 con etapa 1 sola o con las dos etapas, y la misma repartición por zona). Pero el reparto por zona cambia de un presupuesto a otro. En el paper conviene citar **el B exacto** de cada cifra ($108.0 mil millones para 27.9 / 3.6 / 1.1) y decir que cerca del presupuesto mínimo la salida por zona es muy sensible.

## Archivos (en `data/processed/modelo1/`)
- `verif_B108_r0.csv`: la corrida exacta con B = 108 (hogares, personas y % por zona).
- `verif_B_cerca_108.csv`: la tabla de sensibilidad de B de arriba.
- `barrido_B.csv`: barrido regenerado el 14-nov-2026 con los costos vigentes (8 puntos de B = 108.04 a 742.09, sin equidad ni techo de severidad).
- `verif_B108_log.txt`: salida completa de la corrida.
