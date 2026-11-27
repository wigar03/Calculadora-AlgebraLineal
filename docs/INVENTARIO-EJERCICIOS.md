# Inventario de ejercicios

Fuentes (adjuntas por el propietario, revisadas el 2026-11-23 sobre el XML del .docx, incluido OMML):
- **A** = banco ampliado (49 ejercicios: I 1–19, II 1–10, III 1–15, IV 1–5).
- **B** = banco corto (30 ejercicios: I 1–10, II 1–10, III 1–10). Los 30 son idénticos a los de A (mismos
  coeficientes, matrices y ecuaciones); B solo añade instrucciones de informe. Sin diferencias matemáticas.
- **C** = banco final (2026-11-27, 64 ejercicios): 1–49 son los de A con numeración corrida (el 45 añade la forma
  `sen(x)/ln(x) − 1 = 0`; el 46 y el 49 siguen sin igualdad, INC-001) y 50–64 son nuevos (Partes V–VII, abajo).

Datos exactos: `tests/validacion/banco_*.py`. Referencias: `tests/validacion/referencias.json`.
Estado: ver `docs/VALIDACION-EJERCICIOS.md`.

## Parte I — Sistemas lineales (A·X = B, Gauss/Gauss-Jordan exacto)
| ID | Fuente | Incógnitas | Coeficientes | Clasificación (ref.) | Capacidad necesaria |
|---|---|---|---|---|---|
| I-1…I-10 | A, B | x, y, z, w | enteros | única | sistema 4×4 entero |
| I-11 | A | x1…x5 | enteros | única [2, −1, 3, 1, −2] | sistema 5×5, variables indexadas |
| I-12 | A | x, y, z, w | decimales y fracciones OMML (1/3, 181/60, 253/120) | única, racional | aritmética exacta |
| I-13 | A | x, y, z, w | enteros (mal condicionado, tipo Hilbert) | única [1, −2, 3, −1] | exactitud con `Fraction` |
| I-14 | A | x, y, z, w | enteros | **infinitas** (rango 3) | no forzar solución única; forma paramétrica |
| I-15 | A | x₁…x₄ | fraccionarios | única | entrada de fracciones |
| I-16, I-18 | A | x₁…x₄ | decimales | única, racional | entrada decimal exacta |
| I-17, I-19 | A | x₁…x₄ | fracciones propias/impropias | única, racional | entrada de fracciones |

## Parte II — Determinante e inversa (4×4 enteras)
| ID | Fuente | det (ref.) | Inversa | Capacidad necesaria |
|---|---|---|---|---|
| II-1 | A, B | −146 | existe | det + inversa + A·A⁻¹ = I₄ |
| II-2 | A, B | −54 | existe | ídem |
| II-3 | A, B | 348 | existe | ídem |
| II-4 | A, B | −99 | existe | ídem |
| II-5 | A, B | 342 | existe | ídem |
| II-6 | A, B | 844 | existe | ídem |
| II-7 | A, B | 728 | existe | ídem |
| II-8 | A, B | 75 | existe | ídem |
| II-9 | A, B | 55 | existe | ídem |
| II-10 | A, B | −654 | existe | ídem |

Ninguna matriz del banco es singular; el caso singular se cubre con pruebas sintéticas.

## Parte III — Ecuaciones no lineales (tolerancia 10⁻⁶, ≥ 8 cifras)
| ID | Fuente | Ecuación (notación del documento) | Raíz pedida (ref., 10 cifras) | Método | Observaciones |
|---|---|---|---|---|---|
| III-1 | A, B | x³ − 4x − 9 = 0 | 2.7065279545 | a elegir | única raíz real |
| III-2 | A, B | eˣ − 3x² = 0 | 0.9100075725 o 3.7330790286 | a elegir | dos raíces positivas |
| III-3 | A, B | cos(x) − x·eˣ = 0 | 0.5177573637 | a elegir | raíces negativas adicionales |
| III-4 | A, B | x·ln(x) − 1 = 0 | 1.7632228344 | a elegir | dominio x > 0 |
| III-5 | A, B | x⁴ − 3x² − 3 = 0 | 1.9471229667 | a elegir | simétrica (±) |
| III-6 | A, B | ln(x+2) + x² − 2 = 0 | 0.9569892367 | a elegir | dominio x > −2 |
| III-7 | A, B | e^(−x) − x² + 0.5 = 0 | 0.9430917183 | a elegir | superíndice en texto |
| III-8 | A, B | x³ + x − 1 = 0 | 0.6823278038 | a elegir | única raíz real |
| III-9 | A, B | x·e^(−x) − 0.2 = 0 | 0.2591711018 o 2.5426413578 | a elegir | indicar cuál se aproxima |
| III-10 | A, B | x² − 5·sin(x) = 0 | 2.0859345838 | a elegir | excluir x = 0 (trivial) |
| III-11 | A | ln(x) + sen(x) = 1.2 | 1.2754495801 (también 3.0598…, 5.7100…) | bisección / falsa posición | `sen`, igualdad ≠ 0 |
| III-12 | A | e^(−x) + cos(x) = 0.5 | 1.3323901986 (también 5.2298…, 7.3311…) | secante | |
| III-13 | A | x² − 3 sen(x) − ln(x + 2) = 0 | 2.0226001972 (también −0.1875880093) | Newton-Raphson | |
| III-14 | A | e^(x/2) + sen(2x) = 3 | 2.6730630411 | bisección / falsa posición | |
| III-15 | A | ln(x + 3) + cos(x) = x/2 | 2.1646088424 (también −2.3734…, 5.2556…, 6.4626…) | secante | |

## Parte IV — Ecuaciones fraccionarias y compuestas
| ID | Fuente | Ecuación | Raíz (ref.) | Método | Dominio / observaciones |
|---|---|---|---|---|---|
| IV-1 | A | sen(x) / ln(x) = 1 | 2.2191071489 | bisección | x > 0, x ≠ 1 |
| IV-2 | A | √(2x³/(x−3)) — **sin igualdad** | — | falsa posición | **INCOMPLETO** (INC-001) |
| IV-3 | A | e^(1/x) + 2x / tan(x) = 2 | 1.5423960061 (también 4.6306…, …) | Newton | x ≠ 0, tan(x) ≠ 0, polos |
| IV-4 | A | ln(x + 1) / (x² − 4) = −0.1 | 0.4605194803 | bisección | x > −1, x ≠ 2 |
| IV-5 | A | √((x+4)/(x−1)) — **sin igualdad** | — | bisección | **INCOMPLETO** (INC-001) |

Total: 49 ejercicios (47 matemáticamente definidos + 2 incompletos en la fuente).

## Partes V–VII — Banco final (C), ejercicios 50–64
Datos: `tests/validacion/banco_final.py`. Referencias SymPy: `tests/validacion/referencias_final.json`.
| ID | Tipo | Datos | Referencia | Capacidad necesaria |
|---|---|---|---|---|
| V-50, V-52, V-54 | sistema rectangular 3×4, 4×5, 3×5 | enteros | SCI con 1, 1 y 2 variables libres | Ecuaciones Ax = b con m ≠ n, solución paramétrica |
| V-51, V-53 | sistema rectangular 5×4, 6×4 | enteros | incompatible (rg A = 4, rg [A\|b] = 5) | identificar la contradicción |
| VI-55 … VI-59 | A ± B, kA ± B, A + B + C (2×3 a 4×2) | enteros | matrices exactas | Matrices: suma, resta y escalar encadenados |
| VII-60 … VII-64 | independencia de 3 a 5 vectores en R³ y R⁴ | enteros | todos dependientes; núcleo de dimensión 1 | Combinación lineal con b = 0 |

