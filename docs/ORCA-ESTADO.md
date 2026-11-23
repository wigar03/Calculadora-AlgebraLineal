# Estado operativo de Orca

Última actualización: 2026-11-23 (integrador: Claude Business, Opus 5.5).

## Resumen para el propietario
- **47/47 ejercicios definidos VALIDADOS** (I 19, II 10, III 15, IV 3), por API, página y referencias independientes.
- **2 incompletos en la fuente** (IV-2, IV-5): esperan tu respuesta (INC-001).
- Release **v1.0.0-rc.2** preparada (ver `docs/RELEASES.md`). Batería: 322 Python OK y 52 Node OK.
- Incidencias abiertas: solo INC-001 (fuente). INC-002…INC-011 cerradas.

## Agentes (Run `run_e96b75f55a83`)
| Agente | Cuenta / modelo | Rama | Entregado e integrado | Estado |
|---|---|---|---|---|
| Codex 1 | Codex «Personal (Plus)» · gpt-6.1-sol xhigh | `orca/lineal` | Partes I y II, revisión cruzada numérica, INC-008 | terminado |
| Codex 2 | Codex «Team» (sistema) · gpt-6.1-sol xhigh | `orca/numerico` | Partes III y IV, revisión cruzada lineal, INC-010 | terminado |
| Antigravity | Antigravity · gemini-4-neon-high | `orca/expresiones` | analizador, diagnósticos, KaTeX, INC-009, INC-011 | terminado |
| Claude Business | Claude Business (sistema) · Opus 5.5 | `main` | referencias, aceptación, integración, documentación, release | activo |

Claude Pro individual: **no usado** (la cuenta personal gestionada no está seleccionada: `activeAccountId: null`).
Integración: `cherry-pick` de cada commit de 100 líneas o menos sobre `main` y batería completa después de cada entrega.
Revisión cruzada: Codex 1 revisó la rama numérica (7 hallazgos) y Codex 2 la lineal (2 hallazgos de LaTeX).

## Pruebas (`main`)
- Línea base (7a241ad): 169 Python OK y 5 archivos Node OK.
- Final: 322 Python OK y 52 Node OK en 9 archivos.
- Aceptación independiente: `tests/test_validacion_ejercicios.py` (189 llamadas HTTP contra SymPy/mpmath).
- Navegador (`main` final): 18 ecuaciones del documento, Secante, Newton, sistemas I-11, I-12, I-14, mensaje
  `no_certificada`; 0 errores KaTeX; consola sin errores salvo `favicon.ico` 404 (preexistente).

## Pendiente del propietario
- INC-001: igualdad completa de IV-2 `√(2x³/(x−3))` y de IV-5 `√((x+4)/(x−1))`.
