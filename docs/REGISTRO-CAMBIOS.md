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

## 2026-11-23 — etapa 2: módulo 11 (Jacobi y Gauss-Seidel)
| Origen | Motivo | Archivos principales |
|---|---|---|
| integrador | contrato, firmas, casos y referencias exactas; AGENTS.md | `docs/contratos/iterativos.md`, `tests/validacion/*iterativos*` |
| `orca/jacobi` (Codex 1) | entrada exacta, dominancia, reordenamiento, rango, residuo, Jacobi; R1-R3 | `src/iterativos/{entrada,matriz,jacobi}.py` |
| `orca/gauss-seidel` (Codex 2) | Gauss-Seidel, espectro exacto (Schur-Cohn), parada, resolvedor, API; INC-015/017/018 | `src/iterativos/{gauss_seidel,convergencia,resolver}.py`, `web_server.py` |
| `orca/iterativos-ui` (Antigravity) | lector de texto, vista, gráficas, KaTeX, 10 cifras, motivos, robustez | `src/iterativos/sistema_texto.py`, `src/ui/web/iterativos.{js,css}`, `index.html` |
| integrador | ruta `/texto`, exportaciones, `?v=` por contenido, regresión por huella, aceptación HTTP | `web_server.py`, `index.html`, `tests/test_validacion_iterativos.py` |
| integrador | auditoría y roadmap; README y guía matemática; release rc.3 | `docs/auditoria/*`, `README.md`, `docs/guia-matematica.md` |

Todos los commits de agentes se integraron con `cherry-pick` (autoría del propietario conservada) y ≤ 100 líneas.
