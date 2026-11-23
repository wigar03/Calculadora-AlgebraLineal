# Validación del área `expresiones` (rama `orca/expresiones`)

## Alcance verificado
- Normalización de notación (`src/biseccion/normalizador.py`): igualdades `izquierda = derecha` convertidas a `izquierda - (derecha)` (simplificando `= 0`), alias `sen`→`sin`, `e^x`/`e^(...)`→`exp(...)`, `·`/`×`→`*`, `−`/`–`→`-`, superíndices `²`/`³`/`⁴`→`^2`/`^3`/`^4`.
- Diagnósticos específicos de sintaxis (`src/biseccion/diagnosticos.py`, `src/biseccion/expresiones.py`): multiplicación omitida sin corrección silenciosa, paréntesis sin cerrar/sobrantes con posición, operadores consecutivos, potencias mal escritas, funciones desconocidas con sugerencias (`sinn`→`sin`, `lg`→`ln`/`log`), argumentos vacíos o múltiples, variables no reconocidas, expresiones incompletas e igualdades mal formadas.
- Diagnósticos de dominio (`src/biseccion/dominio.py`): `ln`/`log` no positivo, `sqrt` negativo, `asin`/`acos` fuera de `[-1, 1]`, `tan` en polos (`|cos(u)| < 1e-12`), división por cero, potencia real de base negativa con exponente no entero y desbordamientos.
- Renderizado KaTeX estricto (`throwOnError: true`, `vendor/katex/katex.min.js`) y visualización de diagnósticos en los cuatro métodos sin cambios de UX (`biseccion.js`, `regla-falsa.js`, `secante.js`, `newton-raphson.js`, `formula-keyboard.js`).

## Evidencia por ejercicio del banco (`tests/validacion/banco_raices.py`)
Referencia independiente: `tests/validacion/referencias.json` (SymPy/mpmath) y `funcion` en 50 puntos del dominio.

| ID | Entrada `ecuacion` | Comportamiento directo | Variante explícita (`*`) vs `funcion` (50 pts) | Máx. `\|f(r_ref)\|` | KaTeX (`f` y `f'`) | Estado |
|---|---|---|---|---|---|---|
| III-1 | `x^3 − 4x − 9 = 0` | Diagnóstico `4*x` | `0.00e+00` | `1.78e-15` | OK | VALIDADO |
| III-2 | `e^x − 3x^2 = 0` | Diagnóstico `3*x` | `0.00e+00` | `7.11e-15` | OK | VALIDADO |
| III-3 | `cos(x) − x·e^x = 0` | Aceptada | `0.00e+00` | `1.11e-16` | OK | VALIDADO |
| III-4 | `x·ln(x) − 1 = 0` | Aceptada | `0.00e+00` | `2.22e-16` | OK | VALIDADO |
| III-5 | `x^4 − 3x^2 − 3 = 0` | Diagnóstico `3*x` | `0.00e+00` | `0.00e+00` | OK | VALIDADO |
| III-6 | `ln(x+2) + x^2 − 2 = 0` | Aceptada | `0.00e+00` | `0.00e+00` | OK | VALIDADO |
| III-7 | `e^(−x) − x^2 + 0.5 = 0` | Aceptada | `0.00e+00` | `0.00e+00` | OK | VALIDADO |
| III-8 | `x^3 + x − 1 = 0` | Aceptada | `0.00e+00` | `1.11e-16` | OK | VALIDADO |
| III-9 | `x·e^(−x) − 0.2 = 0` | Aceptada | `0.00e+00` | `0.00e+00` | OK | VALIDADO |
| III-10 | `x^2 − 5·sin(x) = 0` | Aceptada | `0.00e+00` | `1.78e-15` | OK | VALIDADO |
| III-11 | `ln(x) + sen(x) = 1.2` | Aceptada | `0.00e+00` | `2.22e-16` | OK | VALIDADO |
| III-12 | `e^(−x) + cos(x) = 0.5` | Aceptada | `0.00e+00` | `3.33e-16` | OK | VALIDADO |
| III-13 | `x^2 − 3 sen(x) − ln(x + 2) = 0` | Diagnóstico `3*sen(...)` | `0.00e+00` | `2.22e-16` | OK | VALIDADO |
| III-14 | `e^(x/2) + sen(2x) = 3` | Diagnóstico `2*x` | `0.00e+00` | `4.44e-16` | OK | VALIDADO |
| III-15 | `ln(x + 3) + cos(x) = x/2` | Aceptada | `0.00e+00` | `4.44e-16` | OK | VALIDADO |
| IV-1 | `sen(x) / ln(x) = 1` | Aceptada | `0.00e+00` | `2.22e-16` | OK | VALIDADO |
| IV-3 | `e^(1/x) + 2x / tan(x) = 2` | Diagnóstico `2*x` | `0.00e+00` | `4.88e-15` | OK | VALIDADO |
| IV-4 | `ln(x + 1) / (x^2 − 4) = −0.1` | Aceptada | `0.00e+00` | `0.00e+00` | OK | VALIDADO |

## Enunciados incompletos (`INCOMPLETOS`)
| ID | Expresión | Resultado | Estado |
|---|---|---|---|
| IV-2 | `sqrt(2x^3/(x-3))` | Diagnóstico de producto implícito `2*x`; versión `sqrt(2*x^3/(x-3))` respeta dominio (`x=3` división por cero, `x=1` radicando negativo) y renderiza en KaTeX. Sin `=`, no se resuelve como ecuación. | PENDIENTE (enunciado incompleto) |
| IV-5 | `sqrt((x+4)/(x-1))` | Aceptada como `f(x)` con respeto de dominio (`x=1` división por cero, `x=0` radicando negativo) y renderizado KaTeX. Sin `=`, no se resuelve como ecuación. | PENDIENTE (enunciado incompleto) |

## Incidencias encontradas y resueltas
1. **Vista previa ocultaba el diagnóstico específico**:
   - *Síntoma*: `biseccion.js` y `regla-falsa.js` reemplazaban cualquier `datos.error` en `/preview` por `"Complete la expresión para actualizar la vista matemática."`.
   - *Causa*: manejo genérico del error HTTP 400 en `actualizarPreview()`.
   - *Corrección*: mostrar `datos.error` (o `error.message` de respuesta HTTP) en el mismo elemento `#bis-preview-status` / `#rf-preview-status` sin cambiar UX (`39c9c2d`).
   - *Prueba*: `tests/test_raices_errores_ui.cjs`.
2. **`tan(x)` en polos no lanzaba error de dominio en IEEE 754**:
   - *Síntoma*: `math.tan(math.pi/2)` devolvía `~1.63e16` en lugar de fallar por polo.
   - *Causa*: `math.cos(math.pi/2)` es `6.12e-17` y no cero exacto.
   - *Corrección*: comprobar `abs(math.cos(u)) < 1e-12` en `src/biseccion/dominio.py` (`e08d2c2`), verificado sin regresiones en detección de asíntotas de `test_regla_falsa_continuidad.py`.
   - *Prueba*: `tests/test_expresiones_diagnosticos.py` (`TestDiagnosticosDominio`).
3. **Contrato de producto implícito en `banco_raices.py`**:
   - *Síntoma*: 6 de las 18 `ecuacion` (`III-1`, `III-2`, `III-5`, `III-13`, `III-14`, `IV-3`) y `IV-2` contienen producto implícito mientras Objetivo A prohíbe corregirlo en silencio.
   - *Resolución*: confirmado por el coordinador (`msg_54fbcb6ae3ff`): se mantiene prohibida la multiplicación implícita, se diagnostican los 6 + `IV-2`, se aceptan las 12 explícitas tal cual y se validan las 18 con `*` explícito en 50 puntos y KaTeX.

## Batería ejecutada y commits
- `python -m unittest discover tests -v`: **182 OK** (línea base 169 + 13 pruebas nuevas).
- `tests/*.cjs` (`node --test`): **7 archivos / 37 pruebas OK** (línea base 5 / 31 + `test_katex_render.cjs` y `test_raices_errores_ui.cjs`).
- Commits en `orca/expresiones`: `f9c3708`, `81a361e`, `e08d2c2`, `52a239a`, `39c9c2d`, `bc265ef`, `415bcbe`, `e7899c5`, `87a4708`, `8a240b2`.
