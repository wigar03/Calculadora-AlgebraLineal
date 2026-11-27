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

## 2026-11-23 — etapa 5: consolidación con herramientas reales
| Origen | Motivo | Archivos principales |
|---|---|---|
| integrador | job `externos` (TeX Live, Calc, Gnumeric); auditoría visual GitHub; fórmula de Gauss-Seidel; firma | `.github/workflows/windows-release.yml`, `docs/guia-matematica.md`, `docs/firma-opciones.md` |
| `orca/consolidacion-latex-rendimiento` (Codex 2) | compilación pdflatex real; oráculo CSV revisado; mediciones 16 MiB | `tests/test_externo_latex.py`, `tests/test_exportacion_modulos.py`, `scripts/medir_*.py` |
| `orca/consolidacion-csv` (Codex 1) | abrir/guardar/reabrir con Calc y Gnumeric; regla `<`/`>` en Markdown | `tests/test_externo_csv.py`, `scripts/verificar_markdown.py` |
| `orca/consolidacion-chrome` (Antigravity) | diagnóstico Chrome; INC-024 a INC-027 en la exportación | `tests/test_p2_browser.cjs`, `src/ui/web/exportar.js`, `index.html` |
| integrador | rutas personales sustituidas por `%TEMP%`; incidencias, estado y release | `docs/validacion/*`, `docs/INCIDENCIAS.md`, `docs/ORCA-ESTADO.md` |

## 2026-11-24 — etapa final: v1.0.0
| Origen | Motivo | Archivos principales |
|---|---|---|
| integrador | INC-031: tiempos del diagnóstico, espera 120 s, flujo de estabilidad en 5 máquinas limpias | `desktop.py`, `src/ui/diagnostico.py`, `scripts/*windows*.ps1`, `.github/workflows/windows-estabilidad.yml` |
| `orca/consolidacion-csv` (Codex 1) | README, distribución, CHANGELOG y notas de v1.0.0 | `README.md`, `docs/distribucion.md`, `CHANGELOG.md`, `docs/notas-v1.0.0.md` |
| integrador | versión 1.0.0; Excel para la Web; releases | `src/core/version.py`, `docs/validacion/excel-web.md`, `docs/RELEASES.md` |

## 2026-11-27 — Dev-Carbon y mejoras para el banco final
| Origen | Motivo | Archivos principales |
|---|---|---|
| Carbon, Codex 1, Codex 2 (`Dev-Carbon`) | auditoría de coherencia C-01…C-21, banco final 50-64, independencia lineal, «Usar resultado como A» (INC-032) | `docs/auditoria/carbon-coherencia.md`, `src/**`, `tests/validacion/banco_final.py` |
| `orca/final-lineal` (Codex 1) | forma A·X = B y verificación algebraica de dependencia | `src/ecuaciones`, `src/vectores`, `src/procedimientos/lineal.py`, `app.js` |
| `orca/final-numerico` (Codex 2) | orden de convergencia observado; selector de condición y recomendación de método (INC-033) | `src/raices/`, métodos de raíces, `web_server.py`, vistas 07-10 |

