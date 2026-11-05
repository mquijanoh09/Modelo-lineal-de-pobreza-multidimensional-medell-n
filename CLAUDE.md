# Optimización 1 (EAFIT) — MILP contra la pobreza multidimensional (IPM)

Proyecto final de Martín. Modelo MILP en Python que asigna inversión pública para reducir el IPM (Alkire-Foster / IPM-Colombia) en **Antioquia**, con microdatos **IPM 2025 del DANE**. Se replican y comparan los 4 modelos de Hamie et al. (2024).
Equipo: Modelos 1-2 (Tomás, hogar por hogar) · Modelos 3-4 (Jerónimo, por zona).

## Cómo trabajar conmigo
- **Regla 1:** al responderme, siempre menciona mi nombre: Martín.
- Responde en **español**. Martín debe poder **defender cada línea** ante la profesora: explica el porqué matemático de cada decisión.
- Avanza **paso a paso**: una función o un bloque por vez, nada de scripts enormes de una sola vez.
- **La formulación manda:** traduce a PuLP lo que está en `docs/`; no inventes restricciones. Si algo falta o se contradice, **pregunta** antes de programar.
- Cierra cada explicación con una pregunta corta que compruebe que Martín la entendió.

## Fuentes de contexto (lee solo lo que la tarea necesite)
| Archivo | Cuándo leerlo |
|---|---|
| `docs/resumen_proyecto_ipm.md` | **Fuente de verdad**: decisiones, parámetros, costos, pendientes. Antes de cualquier tarea de modelación. |
| `docs/reglas_conteo_personas.md` | Reglas validadas para contar personas afectadas ($u_{ij}$) y decisiones de costeo por indicador. Antes de escribir 05. |
| `docs/informe_modelo1.md` | Formulación completa del Modelo 1, supuestos y plan de experimentos. Antes de escribir 08. |
| `docs/paper_modelos.md` | Ecuaciones de los Modelos 1-4 y linealización. **Usa esto en vez del PDF.** |
| `graphify-out/GRAPH_REPORT.md` | Mapa de cómo se conectan código, paper y decisiones. Solo para preguntas de arquitectura. |
| `referencias/*.pdf` | Solo si piden una página concreta del paper. |

## Mapa del código
Todo el código vive en `Modelos/` (decisión de Martín, 5-nov-2026). Los datos siguen en `data/` y los documentos en `docs/`, en la raíz.
```
Modelos/                       lo común a los Modelos 1 y 2
  parametros.py                pesos, k, costos con fuente, escenarios (sección 10: Modelo 2)
  utils_dane.py                leer, a_numero, puntaje, resumen_ipm, rutas RAIZ/RAIZ_DEP/RAIZ_NAC/OUT
  02_validar_ipm.py            valida pesos w_j, umbral k, FEX_C (base completa DANE, lento)
  03_preparar_antioquia.py     pruebas A/B de P3 → genera data/processed/hogares_antioquia.csv
  04_linea_base.py             H0, A0, M0, contribuciones, distancia al umbral, por zona
  05_conteo_personas.py        (por hacer) u_ij, tablas de niños y adultos
  datos_modelo.py              (por hacer) datos del MILP: A_i, M_i, Sev0, SevEdu
  modelo_base.py               (por hacer) clase ModeloIPMBase (reglas comunes M1/M2)
  Modelo_1/                    modelo1.py (clase Modelo1), 08_modelo1.py, 08_modelo1_barridos.py
  Modelo_2/                    modelo2.py (clase Modelo2), 09_modelo2.py, 09_modelo2_barridos.py
```
`Modelo_1/` y `Modelo_2/` no llevan espacio (cambio de Martín, 5-nov), así que sus módulos se importan como paquete
desde `Modelos/` (`from Modelo_1.modelo1 import Modelo1`). Los scripts numerados de esas carpetas igual empiezan con
`sys.path.insert(0, str(Path(__file__).resolve().parents[1]))`, para poder correrlos directamente (`python Modelos/Modelo_1/08_modelo1.py`).
Las rutas a `data/` salen de `utils_dane` (desde `__file__`), así que los scripts corren desde cualquier carpeta.

## Datos
- **Entrada de los modelos:** `data/processed/hogares_antioquia.csv`, con 3,732 hogares y 24 columnas: `ID_HOGAR, DIRECTORIO, SECUENCIA_P, DEPARTAMENTO, P3`, las 15 privaciones, `PERSONAS, FEX_C, IPM, POBRE`.
- **Mapeo:** $M_{ij}$ = 15 columnas de privación · $HS_i$ = `PERSONAS` · $HW_i$ = `FEX_C` · zona $d$ = `P3` (1 cabecera, 2 centro poblado, 3 rural disperso).
- **No leas los CSV con la herramienta de lectura** (están bloqueados en `.claude/settings.json`). Inspecciónalos con pandas: `df.head()`, `df.shape`, `df.describe()`.
- `data/DANE/` (~330 MB) es la base cruda: nunca la cargues completa; usa `leer(..., columnas=[...])`.
- **No cambies el universo** (Antioquia, 3 zonas de P3) ni agregues filtros: los 4 modelos deben compartirlo.

## Convenciones técnicas
- Python 3.13 en `.venv`. En Windows: `.venv\Scripts\python.exe <script>.py`. Librerías: pandas 3, numpy 2, **PuLP 3.3 + HiGHS** (`highspy`), matplotlib.
- Solver: `pulp.HiGHS(msg=False)`. Reporta el estado de la solución y el gap.
- Los parámetros (pesos, k, costos) viven en `Modelos/parametros.py`. El 04 ya los importa; 02 y 03 aún tienen copias de `DIMENSIONES`/`PESOS`/`INDICADORES`: no las dupliques otra vez.
- Puntajes en múltiplos de 0.01: pobre ⇔ puntaje ≥ 0.34. Una desigualdad estricta $< k$ se programa como $\le 0.33$.
- Reporta **siempre** los resultados por zona (P3) además del total.

## Decisiones abiertas (no las tomes tú: pregúntale a Martín)
1. Desempate del Modelo 1: con $\lambda$ en una corrida o en **dos etapas** (max H; luego min $\sum p_iq_i$ con $\sum p_iy_i \ge H^*$). Recomendado: dos etapas.
2. Acuerdo con Jerónimo sobre $u_{ij}$, $HW_i$, tabla de costos compartida y convención $y_i = 1$ ⇔ el hogar **sale** de la pobreza.

Ya decidido (21-oct-2026): todos los costos $EpF_j$ urbanos y rurales, unidades $u_{ij}$ por persona afectada,
empleo_formal por hogar (3 casos), rezago opción C, inasistencia como transferencia condicionada con $p$, CDI en todas las zonas.
Decidido 26/27-oct-2026 (perspectiva de equidad): objetivo H con techo de severidad $\sum p_iq_i \le (1-\rho)\text{Sev}_0$ y severidad como desempate;
bigM por hogar $M_i = c_i^0 - 0.33$; sin $C_i$; desocupados costeados por perfil (Decreto 533/2024) y aporte a pensión para mujeres ≥ 57 y hombres ≥ 62.
Contexto: `graphify-out/perspectiva_equidad/GRAPH_REPORT.md`; formulación: `docs/informe_modelo1.md` §3.4 y §4.
Propuesto 28-oct-2026 (pendiente de acordar con Jerónimo): severidad educativa del rezago en los 4 modelos (§3.5, restricciones 9 y 10).
Fuente: `docs/resumen_proyecto_ipm.md` y `docs/reglas_conteo_personas.md`.

## Al terminar una tarea
- Si se tomó o cambió una decisión, **actualiza `docs/resumen_proyecto_ipm.md`** (sección correspondiente) y avísale a Martín para que sincronice la copia del proyecto en Claude.
- Si aparecen resultados nuevos (H, M0, costos óptimos), agrégalos al resumen con la fecha.
