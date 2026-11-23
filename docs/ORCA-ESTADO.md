# Estado operativo de Orca

Última actualización: 2026-11-23 (integrador: Claude Business, Opus 5.5).

## Resumen para el propietario
- **47/47 ejercicios definidos VALIDADOS** (I 19, II 10, III 15, IV 3), por API, página e independientemente.
- **2 incompletos en la fuente** (IV-2, IV-5): esperan tu respuesta (INC-001).
- `main`: 305 pruebas Python OK, 46 pruebas Node OK. Sin push ni release todavía (ver «Próximos pasos»).

## Agentes (Run `run_e96b75f55a83`)
| Agente | Cuenta / modelo | Rama | Entregado e integrado | Tarea actual |
|---|---|---|---|---|
| Codex 1 | Codex «Personal (Plus)» · gpt-6.1-sol xhigh | `orca/lineal` | Partes I y II (14 commits) | revisión cruzada de la rama numérica; luego INC-008 |
| Codex 2 | Codex «Team» (sistema) · gpt-6.1-sol xhigh | `orca/numerico` | Partes III y IV (13 commits) | revisión cruzada de la rama lineal: entregada (INC-008) |
| Antigravity | Antigravity · gemini-4-neon-high | `orca/expresiones` | analizador y diagnósticos (11 commits) | INC-009: proponer la expresión completa corregida |
| Claude Business | Claude Business (sistema) · Opus 5.5 | `main` | referencias, aceptación, integración, documentación | supervisión e integración |

Claude Pro individual: **no usado** (la cuenta personal gestionada no está seleccionada: `activeAccountId: null`).
Integración: `cherry-pick` de cada commit de 100 líneas o menos sobre `main` y batería completa después de cada rama.

## Pruebas (`main`)
- Línea base (7a241ad): 169 Python OK y 5 archivos Node OK.
- Tras integrar las tres ramas: 305 Python OK y 46 Node OK en 8 archivos.
- Aceptación independiente `tests/test_validacion_ejercicios.py`: 189 llamadas HTTP contra `referencias.json`.
- Navegador: 18 ecuaciones del documento en Bisección, más Secante (III-12, III-15) y Newton (III-13, IV-3), sin
  errores de KaTeX; 7 diagnósticos de entrada visibles; consola sin errores salvo `favicon.ico` 404 (preexistente).

## Pendiente del propietario
- INC-001: igualdad completa de IV-2 `√(2x³/(x−3))` y de IV-5 `√((x+4)/(x−1))`.

## Próximos pasos
1. Integrar INC-008 e INC-009 y la revisión cruzada de la rama numérica.
2. Release `v1.1.0` (nuevas capacidades compatibles: analizador, diagnósticos y métodos robustos), con notas que
   declaren IV-2 e IV-5 como incompletos en la fuente.
