# Validación de ejercicios

Referencia independiente: `tests/validacion/referencias.json`, generada con SymPy (aritmética racional exacta) y
mpmath (50 dígitos) por `tests/validacion/generar_referencias.py`, sin importar código de `src/`.
Tolerancias: lineales y matrices, igualdad exacta de fracciones; raíces, |x − r| ≤ 10⁻⁶ más el residuo |f(x)|.
Estados: **VALIDADO** (motor + vía de la página + revisión del integrador), **MOTOR OK** (la API coincide, pero falta
la validación completa por la vía del usuario o del procedimiento), **FALLA**, **INCOMPLETO** (fuente).

## Línea base — `main` 7a241ad (2026-11-23, sonda HTTP del integrador)
| Bloque | Resultado | Notas |
|---|---|---|
| I-1…I-19 (API `/api/ecuaciones/resolver`) | 19/19 MOTOR OK | I-14 clasificado SCI (infinitas), coincide con rango 3 |
| II-1…II-10 det (API) | 10/10 MOTOR OK | det exacto igual a la referencia |
| II-1…II-10 inversa (API) | 10/10 responde | comprobación A·A⁻¹ = I pendiente en prueba automática |
| III/IV con sintaxis explícita, semillas a ±0.05 | 72/72 MOTOR OK | 18 ecuaciones × 4 métodos; prueba débil (INC-003) |
| III/IV con la notación del documento | 0/72 | «Función inválida» (INC-002) |
| IV-2, IV-5 | INCOMPLETO | INC-001 |

## Estado por ejercicio
Se actualiza al integrar cada rama, con el commit que lo valida.

| Bloque | VALIDADO | MOTOR OK | FALLA | INCOMPLETO | Evidencia |
|---|---|---|---|---|---|
| Parte I (19) | 19 | — | 0 | 0 | rama `orca/lineal` integrada en `main` (a9d2a2b) |
| Parte II (10) | 10 | — | 0 | 0 | ídem |
| Parte III (15) | 15 | — | 0 | 0 | ramas `orca/numerico` (910c90a) y `orca/expresiones` (e26bb99) |
| Parte IV (5) | 3 | — | 0 | 2 | ídem; IV-2 e IV-5 en INC-001 |

### Partes I y II — VALIDADO (29/29)
- Motor (Codex 1): Gauss con sustitución regresiva fallaba en los 18 sistemas con solución única al elegir
  «Eliminación Gaussiana + Sustitución Regresiva» (la sonda inicial solo usó Gauss-Jordan). Corregido (2a26e67→).
  I-14 muestra ahora la familia paramétrica exacta y la verifica fila a fila para todo t ∈ ℝ.
- Página (Codex 1): 78 resoluciones en el navegador (19 sistemas × 2 métodos, 10 matrices × 4 métodos), 5×5 y
  celdas `1/3`, `0.75`, `181/60`, sin errores KaTeX. Detalle: `docs/validacion/lineal.md`.
- Independiente (integrador): `tests/test_validacion_ejercicios.py` compara por HTTP con `referencias.json` y
  sustituye con `Fraction` (A·X = B, A·A⁻¹ = I). Revisión del diff del motor: sin hallazgos bloqueantes.

### Partes III y IV — VALIDADO (18/18); IV-2 e IV-5 INCOMPLETOS
- Motor (Codex 2): 18 ecuaciones × 4 métodos con datos iniciales realistas, |x − r| ≤ 10⁻⁶ y residuo verificado.
  Corregido: polos y continuidad antes de encerrar raíces, pasos diminutos sin mejora declarados como convergencia,
  dominio de f′ en Newton, estancamiento unilateral en falsa posición, condición `positiva_no_nula` (III-10).
  Detalle: `docs/validacion/numerico.md`.
- Independiente (integrador): la prueba de aceptación detectó que mi intervalo de IV-3 [1.4, 1.7] contenía π/2,
  donde tan(x) no está definida; el rechazo de la calculadora es correcto y la prueba usa ahora [1.4, 1.55].
- Analizador (Antigravity): las ecuaciones se aceptan con la notación del documento (`=`, `sen`, `e^(−x)`, `·`,
  `−`, `x³`). Los 6 productos implícitos del documento (III-1, III-2, III-5, III-13, III-14, IV-3) se diagnostican
  («falta el operador de multiplicación entre 4 y x»), sin corrección silenciosa. Detalle: `docs/validacion/expresiones.md`.
- Independiente (integrador): `test_raices_escritas_como_en_el_documento` resuelve las 18 ecuaciones en notación del
  documento con los 4 métodos (72 casos) y `test_producto_implicito_del_documento_se_diagnostica` los 6 productos.
- Página (integrador, navegador): Bisección con las 18 ecuaciones del documento; Secante III-12 y III-15;
  Newton-Raphson III-13 e IV-3. Todas con |x − r| ≤ 10⁻⁶ y 0 errores KaTeX.
- Revisión cruzada (Codex 1): 7 hallazgos fuera de los datos del banco, en corrección (INC-010). La
  validación del banco se repetirá tras integrarlos.
- Batería tras integrar las tres ramas: 305 pruebas Python OK y 46 pruebas Node OK (8 archivos).

Detalle por área: `docs/validacion/lineal.md`, `docs/validacion/numerico.md`, `docs/validacion/expresiones.md`.
