# Indicaciones para Jerónimo: qué subir y qué no (17-nov-2026)

De: Martín · Para: Jerónimo (Modelos 3 y 4)

Esta rama es **`entrega-m34-15nov`**. Úsala para subir todo lo de los Modelos 3 y 4 que va al paper. No la borres, no la reescribas y no hagas `git push --force`.

## 1. Qué debes subir (en la carpeta `entrega_m34/`)

1. **Cualquier cambio posterior al 15-nov** en `M34_para_paper.md`, `figuras_m34/`, `datos_m34/`, `cifras_m34.csv` o `scripts/`. Regenera todo con los scripts (no a mano) y vuelve a correr `scripts/m34_verificar_entrega.py`; debe dar todo en verde (126 de 126 al 15-nov).
2. **`requirements-lock.txt`**: el `LEEME.md` dice que se reproduce con esas versiones, pero el archivo solo está en la rama `Modelo3`. Cópialo a `entrega_m34/` para que la entrega se pueda reproducir desde esta rama.
3. **Los scripts `m34_*` que se usan para generar cifras** y que todavía no están en `entrega_m34/scripts_modelo3/` (hoy hay cinco: `m34_b424_15nov.py`, `m34_b424_resumen_15nov.py`, `m34_base_paper_15nov.py`, `m34_ip_zonas_15nov.py`, `m34_zonas_costo_15nov.py`). Si `m34_datos_paper.py` o los otros scripts de `scripts/` importan otro `m34_*.py`, cópialo ahí también, para que `LEEME.md` no mande a otra rama.
4. **Tu respuesta a lo que Martín conteste** en `RESPUESTA_JERONIMO_15NOV.md` va en la rama `Contexto`, no aquí.

Sube solo lo que sea resultado agregado (por zona, por réplica, por B) o código.

## 2. Qué NO debes subir

- **Microdatos del DANE** (`data/DANE/**`: `.csv`, `.dta`, `.sav`). Ya están en el historial por un commit viejo (`0389805`); no agregues más ni los modifiques. Martín decide aparte qué hacer con ese historial; no lo reescribas tú.
- **Tablas a nivel de persona** o con identificadores de persona (columnas como `ID_PERSONA`): por ejemplo `plan_adulto.csv`, `plan_nino.csv`, `ninos.csv`, `adultos_clei.csv`, `logro_hogar.csv`. Si necesitas una cifra que sale de ellas, sube el agregado (por zona o por hogar-tipo), no la tabla.
- **Paquetes y respaldos**: `.bundle`, `.tgz`, `.zip`, `.pdf` y copias `*.bak_*` (ya están en `.gitignore`; no los fuerces con `git add -f`).
- **El grafo** (`graphify-out/`, `graph.json`, `GRAPH_REPORT.md`): lo regenera Martín; si lo tocas se pisan las versiones.
- **El paper en `main`** (`paper/**`) y el código de los Modelos 1 y 2 (`Modelos/`): no los edites desde tu rama. Martín integra tu texto desde `entrega_m34/M34_para_paper.md`.

## 3. Cómo subirlo sin errores

Esta rama tiene otra estructura que `main` (los archivos viven en la raíz, no en `Modelos/`). Por eso **no hagas merge de `main` en esta rama**: haría conflictos grandes y no aporta nada a la entrega.

```bash
git fetch origin
git checkout entrega-m34-15nov
git pull --ff-only origin entrega-m34-15nov     # si falla, no fuerces: avisa a Martín

# agrega SOLO lo que quieres subir, nunca "git add ." ni "git add -A"
git add entrega_m34/
git status                                      # revisa la lista completa
git diff --cached --stat                        # revisa tamaños: nada de decenas de MB

git commit -m "Entrega M3/M4: <qué cambió>"
git push origin entrega-m34-15nov               # sin -f
```

## 4. Cómo verificar que quedó perfecto

1. Antes del commit: ningún archivo de `data/DANE/` en `git diff --cached --name-only`:
   `git diff --cached --name-only | grep -E 'data/DANE|\.(dta|sav|zip|tgz|bundle)$'` no debe imprimir nada.
2. Ninguna columna de persona en los CSV nuevos:
   `git diff --cached --name-only | grep '\.csv$' | xargs -I{} sh -c 'head -1 "{}" | grep -l ID_PERSONA && echo "{}"'` no debe imprimir nada.
3. Corre `python3 entrega_m34/scripts/m34_verificar_entrega.py entrega_m34/ <paper/cifras.tex>`. Para la comparación usa el `cifras.tex` de la rama **`paper-12nov`** (tiene la auditoría del 14-nov y todavía no está en `main`).
4. Después del push: abre `https://github.com/mquijanoh09/modelo-lineal-de-pobreza-multidimensional-medell-n/tree/entrega-m34-15nov/entrega_m34` y confirma que están `LEEME.md`, `M34_para_paper.md`, `figuras_m34/`, `datos_m34/`, `cifras_m34.csv`, `scripts/`, `scripts_modelo3/` y `requirements-lock.txt`.
5. Escríbele a Martín el hash del commit.

## 5. Dónde queda cada cosa (para no perderse)

| Rama | Qué tiene |
| --- | --- |
| `main` | Paper en LaTeX (`paper/`), Modelos 1 y 2 (`Modelos/`), documentos de decisiones |
| `paper-12nov` | Correcciones del paper del 12 y 14-nov, aún sin pasar a `main` |
| `entrega-m34-15nov` | **Tu entrega** (`entrega_m34/`) y la auditoría del 14-nov |
| `Modelo3` | Todo el código de M3/M4 (`m34_*.py`) |
| `Contexto` | Plan de integración, borrador del paper y las respuestas entre los dos |
| `claude/project-thread-0az49u` | Trabajo nuevo de Martín (cajas del Modelo 1, techo de severidad del Modelo 2); no necesitas tocarla |

Si algo de esto no coincide con lo que ves en tu computador, no lo arregles con `--force`: escríbele a Martín.
