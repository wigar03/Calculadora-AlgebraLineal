# Estado operativo de Orca

Última actualización: 2026-11-24, etapa final v1.0.0 (integrador: Claude Business, Opus 5.5).

## Resumen para el propietario
- **Etapa final:** v1.0.0 estable autorizada sin firma y sin Excel. INC-031 cerrada (entorno de CI; 15 máquinas
  limpias, `docs/validacion/inc031-windows.md`). Excel para la Web no disponible (`docs/validacion/excel-web.md`).
- **Etapa 5 (consolidación) completa:** exportaciones validadas con herramientas reales y auditoría visual en GitHub.
  Sin módulos nuevos ni cambios de UX. Hallazgos y limitaciones: INC-023 a INC-029 en `docs/INCIDENCIAS.md`.
- **LaTeX:** 37 documentos reales compilados con pdflatex en dos pasadas, 0 desbordes > 1 pt, incluido un adversario
  con `ñ á Ω 你好`. Evidencia: `docs/validacion/codex2-latex-rendimiento.md`, `codex2-exportacion-sin-marcas.md`.
- **CSV:** abrir, guardar y reabrir con LibreOffice Calc (dos perfiles) y Gnumeric, 22/22 etapas cada uno; inyección
  con espacios iniciales corregida. Excel no disponible. Evidencia: `docs/validacion/consolidacion-csv.md`,
  `csv-integrado-e11d33e.md`.
- **Rendimiento:** 4 respuestas Jacobi de 10,3 MB simultáneas bajo el límite de 16 MiB; cálculo ≤ 8,6 s; servidor
  103 MiB; consultas ligeras atendidas durante la carga.
- **GitHub:** README y guías sin LaTeX expuesto (escritorio, móvil, oscuro); capturas en `docs/validacion/github/`.
- **Chrome local:** causa de entorno (Orca elevado), no de la aplicación: `docs/validacion/chrome-local.md`.
- **Firma de Windows:** opciones reales en `docs/firma-opciones.md`. No se adquirió nada.
- La CI tiene un job `externos` con TeX Live, LibreOffice y Gnumeric, además de Linux y Windows.

## Agentes (Run `run_e96b75f55a83`)
| Agente | Cuenta / modelo | Rama | Entregado e integrado en la etapa 5 |
|---|---|---|---|
| Codex 1 | Codex «Personal (Plus)» · gpt-6.1-sol xhigh | `orca/consolidacion-csv` | auditoría CSV con Calc y Gnumeric; regla Markdown `<`/`>` |
| Codex 2 | Codex «Team» (sistema) · gpt-6.1-sol xhigh | `orca/consolidacion-latex-rendimiento` | pdflatex real; oráculo CSV; rendimiento 16 MiB |
| Antigravity | Antigravity · gemini-4-neon-high | `orca/consolidacion-chrome` | diagnóstico Chrome; correcciones de `exportar.js` |
| Claude Business | Claude Business (sistema) · Opus 5.5 | `main` | auditoría visual GitHub, firma, CI, decisiones, integración |

Claude Pro individual: **no usado**. Ningún commit supera 100 líneas ni lleva coautores.
Quien implementó `exportar.js` no modificó los oráculos: Codex 1 y Codex 2 revalidaron de forma independiente.

## Pendiente tras v1.0.0
- Firma digital de los ejecutables (decisión y gasto del propietario; ver `docs/firma-opciones.md`).
- Prueba con Microsoft Excel real (no disponible en los entornos autorizados).
- IV-2 e IV-5: limitación del enunciado original (INC-001), no bloquea.
