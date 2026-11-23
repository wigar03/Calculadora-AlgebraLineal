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
