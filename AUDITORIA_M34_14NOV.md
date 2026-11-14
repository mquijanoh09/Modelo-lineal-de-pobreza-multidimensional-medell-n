# Auditoría de M3/M4 y del paper — 14-nov-2026 (resumen)

Alcance: corridas del 12-nov de la rama `Modelo3` (commit `a88de3c`) y paper de la rama `paper-12nov`. El informe completo está en el Project "Opti1" de Jerónimo (`claude/auditoria-m34-14nov.md`). Los scripts de verificación están en `auditoria_14nov/` y se corren desde la raíz de `Modelo3` con `PYTHONPATH=.`.

**Conclusión:** los modelos y los resultados se sostienen; no hay hallazgos críticos. Los errores eran de redacción del paper y ya están corregidos en `paper-12nov` (commit `049a1ee`).

## Verificación independiente

| Prueba | Resultado |
|---|---|
| 144 soluciones re-resueltas y comprobadas con la regla directa R ≤ p, la meta censurada por zona y el costo (`verif_soluciones.py`) | 0 violaciones; meta cumplida en las 3 zonas; costo igual al guardado |
| Fuerza bruta en 40 instancias pequeñas: costo con meta por zona y r_max (`fuerza_bruta_zona.py`) | 40/40 y 40/40 |
| Frontera de r_max: factible con r_max − 10⁻⁵, infactible con r_max + 10⁻⁴ (`rmax_check.py`) | 72/72 |
| Invariantes de las 4.500 corridas de costo | Todas óptimas; costo no decreciente en la meta; ninguna por debajo de la información perfecta; meta por zona ≥ meta global en las 4.500 parejas |
| 1.350 corridas con r_B | Infactibles también sin presolve; ni la mejor réplica de r_max alcanza r_B |
| Granularidad máxima | 11/11 |

## Hallazgos y estado

| # | Severidad | Hallazgo | Estado |
|---|---|---|---|
| 1 | Alto | El paper decía que la infactibilidad de r_B "es aritmética". Solo vale con B ≥ 25; con B ≤ 10 el total de personas alcanza, pero no su reparto por zona. | Corregido |
| 2 | Alto | r_B, ρ_B y el costo del M2 por zona son provisionales: los calculó Jerónimo con el código de Martín (`main`, `bb51532`). | **Abierto: Martín debe confirmar** (`RESPUESTA_JERONIMO_12NOV.md` §6) |
| 3 | Alto | El paper tiene 16 marcas `\pendiente` en las secciones 1, 2, 3, 5 y 9, el resumen y las conclusiones. | **Abierto: Martín** |
| 4 | Medio | La meta de M0 en cada zona no estaba escrita como ecuación para M3/M4. | Corregido (`eq:m3-meta-zona`) |
| 5 | Medio | Cifra vieja en la Discusión ($14,09 mm; es $14,16 mm). | Corregido |
| 6 | Medio | "M4 cuesta 4–11 % menos que M3" es una mediana: gana en el 61–72 % de las réplicas. | Corregido |
| 7 | Medio | Gasto en celdas con menos de 10 hogares privados sin reportar (M3: 17,5 % de las corridas, hasta 27 % del costo). | Corregido |
| 8, 12 | Bajo | Matices de redacción (precisión de los IC, "exactamente", "ningún sorteo", placebo con B = 5). | Corregidos |
| 9 | Bajo | La brecha guardada es la de la etapa de desempate; la de la etapa 1 no se guarda (en la muestra fue ≤ 3×10⁻¹⁶). | Aclarado en el texto; código abierto |
| 10 | Bajo | El bootstrap usa un generador global: los IC cambian en el último decimal según el orden de las llamadas. | Abierto (no cambia conclusiones: estables en 30 semillas) |
| 11 | Bajo | Los r_max de información perfecta están escritos a mano en `m34_tablas_12nov.py`. Reproducidos: 0,0585 / 0,1071 / 0,1649 / 0,2844 / 0,3913 / 0,5362. | Abierto |
| 13 | Bajo | `docs/m34_README.md` no explica los scripts del 12-nov. | Abierto |

## No verificado

- El interior del M1 y el M2 (codo de r, regla de la brecha): solo se usaron sus funciones.
- Las otras 4.356 soluciones de costo: solo pasan los invariantes.
- La repetición de las corridas del 12-nov en una segunda máquina.
