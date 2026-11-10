# Modelo lineal de pobreza multidimensional (IPM, Antioquia 2025)

MILP en Python (PuLP + HiGHS) para la asignación óptima de inversión pública que reduce el IPM,
con los microdatos oficiales del DANE (catálogo 903, versión departamental). Adaptación a Colombia de
Hamie, Hlasny & Jouni (2024), ERF WP 1742. Universo común: Antioquia, 3.732 hogares, 523 pobres.

| Modelo | Información | Qué hace | Responsable |
|---|---|---|---|
| 1 | perfecta | maximiza personas que salen de la pobreza con presupuesto B | Martín |
| 2 | perfecta | minimiza el costo para reducir M0 en una meta | Martín |
| 3 | imperfecta (zona) | focalización geográfica estocástica | Jerónimo (rama `Modelo3`) |
| 4 | imperfecta (zona + clúster) | focalización mixta | Jerónimo (rama `Modelo3`) |

## Instalación

```bash
python -m venv .venv && .venv\Scripts\activate      # Windows (en Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
```
Solver único: HiGHS (viene con `highspy`). No usar PuLP 4.x.

## Cómo correr (siempre desde la raíz del repo)

```bash
python Modelos/02_validar_ipm.py                  # valida que la base reproduce el IPM del DANE
python Modelos/03_preparar_antioquia.py           # subconjunto Antioquia -> data/processed/hogares_antioquia.csv
python Modelos/04_linea_base.py                   # línea base: H0, A0, M0
python Modelos/05_conteo_personas.py              # u_ij y costos por hogar -> conteo_pares.csv y demás tablas
python Modelos/08_modelo1.py                      # Modelo 1, caso base (opciones: --B --r --rho --escenario --sin-sevedu)
python Modelos/08_modelo1_barridos.py             # barridos de B, rho, ...
python Modelos/08_modelo1_barrido_r_fino.py       # barrido fino de r (codo)
python Modelos/Modelo_2/09_modelo2.py             # Modelo 2, caso base: metas 5, 10 y 20 % de M0
python Modelos/Modelo_2/09_modelo2_barridos.py    # curva costo-meta y sensibilidades
```
Las pruebas de cada fase están en `Modelos/Modelo_1/prueba_*.py` y `Modelos/Modelo_2/prueba_*.py`.
Resultados: `data/processed/modelo1/` (M1) y `Modelos/Modelo_2/resultados/` (M2).

## Estructura

- `Modelos/parametros.py`: único lugar de pesos, k, costos, escenarios, mallas de B/r/ρ y metas del M2.
- `Modelos/datos_modelo.py`: carga la base y arma los conjuntos y costos de un escenario.
- `Modelos/modelo_base.py`: clase madre `ModeloIPMBase`; `Modelo_1/modelo1.py` y `Modelo_2/modelo2.py` heredan.
- `Modelos/utils_dane.py`: lectura y validación del microdato.
- `docs/`: formulaciones (`formulacion_modelo1.md`, `formulacion_modelo2.md`), justificación de decisiones y reglas de conteo.
- `graphify-out/perspectiva_equidad/`: grafo de conocimiento del proyecto.
- Modelos 3 y 4: rama `Modelo3` (`m34_*`), ver su `CLAUDE.md`.

## Datos

`data/DANE/` trae el microdato oficial. `data/processed/` guarda los derivados del conteo.
Todo costo usado en los modelos debe tener fuente oficial (ver `docs/justificacion_decisiones.md`).
