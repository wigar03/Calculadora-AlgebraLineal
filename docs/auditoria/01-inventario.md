# Auditoría 1/4 — Qué hace hoy la calculadora (estado final: v1.0.0-rc.4)

Fecha: 2026-11-23. Método: lectura de código, pruebas y sondeo HTTP real (`servidor_local()`), sin modificar nada.
Los hallazgos con evidencia (archivo:línea, mediciones) están en `02-limitaciones.md`.

## Módulos
| # | Módulo | Números | Límite UI | Límite API | Procedimiento y verificación |
|---|---|---|---|---|---|
| 01 | Vectores (suma, resta, k·u, producto punto) | Fraction | n ≤ 20 | ninguno | desglose por componente; sin verificación |
| 02 | Combinación lineal (b ∈ gen{v}) | Fraction | 15 × 10 | ninguno | pasos de Gauss y sustitución |
| 03 | Matrices (A±B, kA, AB, Aᵀ) | Fraction | 8 × 8 | ninguno | pasos del producto; propiedades de Aᵀ |
| 04 | Inversa (2×2 por fórmula, Gauss-Jordan) | Fraction | 2 ≤ n ≤ 6 | ninguno | pasos, A·A⁻¹ = I y A⁻¹·A = I |
| 05 | Ecuaciones Ax = b (Gauss, Gauss-Jordan) | Fraction | 10 × 10 | ninguno | SCD/SCI/SI, rango, familia paramétrica, sustitución |
| 06 | Determinante (cofactores, LU con PA = LU) | Fraction | n ≤ 8 | ninguno | pasos LU; cofactores como texto; comparación n! frente a n³ |
| 07 | Bisección | float | f ≤ 500 car. | ≤ 1000 iter. | tabla, gráfica con zoom, certificación por cambio de signo |
| 08 | Regla falsa (4 pasos) | float | ídem | ídem | continuidad, intervalos candidatos, tabla, gráfica |
| 09 | Newton-Raphson | float | ídem | ídem | derivada simbólica, gráfica, tabla, certificación |
| 10 | Secante | float | ídem | ídem | rectas secantes, tabla, certificación |
| 11 | Jacobi y Gauss-Seidel (nuevo) | float, análisis exacto | 2 ≤ n ≤ 10 | n ≤ 20 | ver `docs/contratos/iterativos.md` |

## Piezas reutilizables
- **Aritmética exacta** (`src/core/arithmetic.py`): `parse_number` a `Fraction` (enteros, decimales, `a/b`,
  notación científica). No acepta `sqrt(2)`, `pi` ni expresiones.
- **Gauss exacto** (`src/solver/gauss_solver.py`): rango, clasificación, solución particular y base del núcleo.
- **Analizador de f(x)** (`src/biseccion/expresiones.py` + normalizador, diagnósticos, dominio): AST con lista
  blanca (sin `eval`), igualdades, `sen`, `e^x`, diagnósticos específicos. Solo la variable `x`.
- **Derivación simbólica** (`src/derivadas/motor.py`): primer orden, regla de la cadena, sin simplificación.
- **Certificación de raíces** (`src/regla_falsa/certificacion.py`, `intervalos.py`): cambio de signo en un intervalo
  continuo, dominio con aritmética racional.
- **Espectro exacto** (`src/iterativos/convergencia.py`): polinomio característico de Faddeev-LeVerrier, prueba de
  Schur-Cohn y radio certificado por bisección racional. Base directa para valores propios.
- **Gráficas** (`grafica-funciones.js`): escalas, marcas 1-2-5, curvas en SVG y navegación. Bisección y regla falsa
  tienen además sus propias implementaciones con rueda y arrastre.
- **KaTeX local** con pruebas estrictas (`throwOnError`) en Node, sin dependencias.

## Lo que no existe
Exportar, imprimir o copiar LaTeX; historial o guardado; visualización en álgebra lineal; valores propios;
LU/QR/Cholesky como módulo; mínimos cuadrados; interpolación; integración o diferenciación numéricas; EDO;
funciones de varias variables; expresiones en celdas de matrices; elección del pivote; distribución fuera de
Windows.

## Calidad medida
- Pruebas: 322 Python y 52 Node antes del módulo 11; **420 Python y 58 Node en el estado final** (v1.0.0-rc.4).
  CI de Windows con compilación e instalación real.
- Analizador: sin `eval` ni `exec` en `src/` (solo `re.compile`). Lista blanca estricta.
- Accesibilidad: `lang="es"`, `aria-live` en resultados y foco visible. Faltan `role="tab"` y `aria-selected`,
  etiquetas en las celdas de matrices y `prefers-reduced-motion` fuera de la barra lateral.
- Modo oscuro manual, que no sigue `prefers-color-scheme`. Media queries en todos los CSS.
