# Estado operativo de Orca

Última actualización: 2026-11-27, tras publicar v1.3.0 (integrador: Claude Business, Opus 5.5).

## Resumen para el propietario
- **Versión estable publicada:** v1.3.0 (`latest`), con setup, portable y `SHA256SUMS.txt` verificados tras la CI y
  tras la descarga pública. Historial: v1.0.0 → v1.1.0 → v1.2.0 → v1.3.0 (`docs/RELEASES.md`).
- **Ejercicios:** banco A (49; 47 resueltos, IV-2/IV-5 incompletos en la fuente) y banco final (64; los 15 nuevos,
  50-64, validados contra SymPy; 46 y 49 siguen sin igualdad). `docs/VALIDACION-EJERCICIOS.md`.
- **Auditoría de coherencia (Carbon):** C-01…C-28 cerrados. Correcciones sin cambio de UX en v1.1.0; propuestas de UX
  aprobadas en INC-032 a INC-035 y publicadas en v1.1.0-v1.3.0. `docs/auditoria/carbon-coherencia.md`.
- **CI:** Linux, Windows (ejecutable empaquetado) y `externos` (pdflatex, LibreOffice Calc, Gnumeric reales, con
  caché de paquetes), más el flujo manual `windows-estabilidad.yml` (5 máquinas limpias) que cerró INC-031.
- **Etapa 5 y v1.0.0:** evidencia de exportaciones, rendimiento, Chrome local e INC-031 en `docs/validacion/`.

## Pendiente (requiere decisión o recursos del propietario)
- Enunciados completos de los ejercicios 46 y 49 (INC-001).
- Firma digital de los ejecutables (`docs/firma-opciones.md`); antes, una licencia OSI para SignPath Foundation.
  En el equipo del integrador, Windows Application Control bloqueó el ejecutable sin firma de v1.2.0.
- Prueba con Microsoft Excel (escritorio o web) con una cuenta o licencia autorizada (`docs/validacion/excel-web.md`).
- Prueba en Windows 10 real; pruebas con estudiantes y docentes; lector de pantalla.
- Limpieza de ramas de trabajo ya integradas (borrarlas es irreversible).

## Agentes (Run `run_e96b75f55a83`)
| Agente | Cuenta / modelo | Área |
|---|---|---|
| Codex 1 | Codex «Personal (Plus)» · gpt-6.1-sol xhigh | álgebra lineal, vistas 01-06, Markdown público |
| Codex 2 | Codex «Team» (sistema) · gpt-6.1-sol xhigh | métodos numéricos, vistas 07-11, núcleo |
| Antigravity | Antigravity · gemini-4-neon-high | analizador y CSS/UI; con la cuota agotada se reasigna a los Codex |
| Gemini Carbon | sesión del propietario | auditoría de coherencia en la rama `Dev-Carbon` (integrada) |
| Claude Business | Claude Business (sistema) · Opus 5.5 | plan, revisión, CI, validación, integración y releases |

Claude Pro individual: **no usado**. Ningún commit supera 100 líneas ni lleva coautores; cada rama se revisa commit a
commit y se integra con `cherry-pick` o avance rápido, sin reescribir historial publicado.
