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

| Bloque | VALIDADO | MOTOR OK | FALLA | INCOMPLETO |
|---|---|---|---|---|
| Parte I (19) | 0 | 19 | 0 | 0 |
| Parte II (10) | 0 | 10 | 0 | 0 |
| Parte III (15) | 0 | 15 (solo sintaxis explícita) | 15 (notación del documento) | 0 |
| Parte IV (5) | 0 | 3 (solo sintaxis explícita) | 3 (notación del documento) | 2 |

Detalle por área: `docs/validacion/lineal.md`, `docs/validacion/numerico.md`, `docs/validacion/expresiones.md`.
