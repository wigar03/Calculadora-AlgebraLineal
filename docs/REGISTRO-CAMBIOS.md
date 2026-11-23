# Registro de cambios (orquestación Orca)

Registro cronológico de modificaciones, motivo, archivos y commits. Las versiones publicadas están en
`CHANGELOG.md` y `docs/RELEASES.md`.

## 2026-11-23
| Commit | Motivo | Archivos |
|---|---|---|
| 5af9c78 | Instrucciones permanentes para los agentes | `AGENTS.md` |
| 3dd10f1 | Banco de datos exacto de las Partes I y II | `tests/validacion/banco_lineales.py`, `banco_matrices.py` |
| e100363 | Ecuaciones de las Partes III y IV e incompletos IV-2/IV-5 | `tests/validacion/banco_raices.py` |
| 7a241ad | Referencias independientes (SymPy/mpmath) | `tests/validacion/generar_referencias.py`, `referencias.json` |

Configuración local (no versionada): ganchos `.git/hooks/pre-commit` (≤ 100 líneas por commit) y
`.git/hooks/commit-msg` (rechaza `Co-authored-by` y direcciones de asistentes), compartidos por todos los worktrees.

## 2026-11-23 — integración de ramas (cherry-pick, autoría conservada)
| Rango en `main` | Origen | Motivo | Archivos principales |
|---|---|---|---|
| …→a9d2a2b (14) | `orca/lineal` (Codex 1) | Gauss con sustitución regresiva exacta, SCI paramétrico verificado, procedimiento visible | `src/solver`, `src/ecuaciones`, `app.js`, `tests/test_banco_lineal.py` |
| …→910c90a (13) | `orca/numerico` (Codex 2) | dominio y polos, continuidad, parada honesta, raíz no nula | `src/regla_falsa/dominio.py`, métodos, `tests/test_banco_raices.py` |
| …→e26bb99 (11) | `orca/expresiones` (Antigravity) | igualdades, alias, diagnósticos de sintaxis y dominio, KaTeX | `src/biseccion/{normalizador,diagnosticos,dominio}.py` |
| 1060aa4 | integrador | intervalo de IV-3 sin el polo π/2 | `tests/validacion/funciones_independientes.py` |
| 7196bbd, 9a5fb83 | integrador | INC-005 (la prueba entró en el commit anterior a la corrección) | `src/ui/web_server.py`, `tests/test_servidor_local.py` |
| 580bcb5 | integrador | INC-007, salida de Python en UTF-8 en pruebas Node | `tests/test_raices_errores_ui.cjs`, `test_katex_render.cjs` |
| f9a79b4, c6fdf36 | integrador | aceptación con la notación del documento | `tests/test_validacion_ejercicios.py` |
