# Evidencia de entrada, matriz y Jacobi

Fecha: 2026-11-23. Rama: `orca/jacobi`, creada desde `main` en `fd597c3`.
Firmas confirmadas por el integrador mediante Orca y documentadas en `main` (`5843c3f`).
Esta evidencia valida las funciones y pruebas del área; la aceptación del módulo completo corresponde al integrador.

## Implementación y decisiones

- `leer_sistema(A,b,x0)` devuelve tres copias `Fraction`; `sistema_float` convierte ese triple una sola vez.
- Se aceptan enteros, decimales y fracciones; n=1 y n=20 están cubiertos. Las celdas inválidas nombran fila y columna
  en base 1 y explican la corrección. Se rechazan celdas vacías, booleanos, no finitos y fracciones con denominador 0.
- La conversión rechaza desbordamiento y números no nulos que se convertirían silenciosamente en cero.
- Los diagnósticos comparan valores exactos cuando reciben `Fraction`; diagonal y suma se informan como `float`
  para JSON. `cumple` significa dominancia estricta; `no_estricta`, la desigualdad no estricta.
- Índices Python/JSON base 0; las variables del LaTeX usan base 1. `permutacion[k]` es la fila original situada en k.
- Reordenamiento: primero asignación dominante estricta; después, si hace falta, asignación diagonal no nula.
  Siempre se permutan conjuntamente las ecuaciones y b; no se permutan incógnitas. Las entradas no se mutan.
- Hasta n=8: backtracking exhaustivo podado, máximo 109601 nodos. Para n>8: preferencia heurística por
  `|a_ij|/suma(|fila|)` y caminos aumentantes (O(n³)); la preferencia elige una solución sin perder factibilidad.
  Si no existe dominancia estricta ni es necesario corregir ceros, se conserva el orden original.
- Rangos y singularidad reutilizan `solve_gaussian_elimination` con aritmética exacta, sin sustituir Jacobi.
- Cada componente de Jacobi usa exclusivamente una tupla del vector anterior; `usa_nuevos` siempre está vacío.
- Residuo `b−Ax`, norma infinito por filas y escala `‖b‖∞+‖A‖∞‖x‖∞`; escala cero devuelve `residuo_inf`.
  Si la escala desborda con residuo finito, su cociente se calcula racionalmente para evitar un falso cero.
  Los residuos no finitos informan normas infinitas para que resolver pueda detener la iteración.

## Resultados reproducibles

- `python -m unittest tests.test_iterativos_jacobi tests.test_iterativos_matriz -v`: **24 pruebas OK**.
- `python -m unittest discover tests -v`: **346 pruebas OK**, 10.947 s (322 anteriores + 24 nuevas).
- Bucle PowerShell equivalente a `for f in tests/*.cjs; do node --test "$f"; done`: **52 pruebas OK**, 9 archivos.
- KaTeX local con `throwOnError: true, strict: 'error'`: **324 fórmulas/sustituciones renderizadas sin errores**,
  obtenidas de los tres pasos de todos los casos sin diagonal nula.
- `git diff fd597c3 --check`: sin errores de espacios.

Referencias independientes sin modificar: `tests/validacion/banco_iterativos.py` y `referencias_iterativos.json`.
Las comparaciones cubren 45 vectores y 162 componentes, error relativo ≤1e-12; si la referencia es cero, absoluto ≤1e-12.
Se verifican los rangos de los 17 casos y residuos relativos ≤1e-15 en las 14 soluciones únicas de referencia.
Los dos sistemas reordenables conservan su solución exacta y obtienen permutación `[1,0,2]` estrictamente dominante.

| Caso | Pasos Jacobi 1–3 | Diagnóstico adicional |
|---|---|---|
| principal | OK | Diferencia explícita con x₂ de Gauss-Seidel en k=1 |
| principal_x0_unos | OK | Vector inicial no nulo y no mutación |
| practica | OK | Rango y residuo de la solución |
| dd_2x2 | OK | Rango y residuo de la solución |
| decimales_3x3 | OK | Entrada decimal exacta |
| fracciones_3x3 | OK | Entrada fraccionaria exacta |
| tridiagonal_5x5 | OK | Rango y residuo de la solución |
| spd_no_dominante | OK | Dominancia no estricta; no se afirma garantía de Jacobi |
| jacobi_si_gs_no | OK | Esquema Jacobi contra referencia, sin estimar autovalores |
| diverge_ambos | OK | Tres pasos válidos aunque la sucesión diverja |
| reordenable | OK | Permutación dominante y solución exacta preservada |
| diagonal_nula_reordenable | Rechazo esperado | Reordenamiento dominante, misma solución exacta |
| diagonal_nula_sin_arreglo | Rechazo esperado | Imposibilidad de asignación, rango A=1, aumentada=1 |
| singular_infinitas | OK | Rango A=1, aumentada=1, singular |
| singular_incompatible | OK | Rango A=1, aumentada=2, singular |
| hilbert_4x4 | OK | Rango y residuo de la solución |
| dd_10x10 | OK | Índices LaTeX de dos cifras |

Además: todas las 512 matrices binarias 3×3 se contrastan contra sus seis permutaciones independientes;
hay casos de caminos aumentantes, imposibilidad con columnas no nulas, límites n=8/9/20, escala extrema y no finitos.

## Commits del área (líneas añadidas + eliminadas)

| Hash | Mensaje | Líneas |
|---|---|---:|
| 1b5e0ad | feat(iterativos): leer sistemas exactos y convertir a float | 68 |
| e14fc32 | feat(iterativos): diagnosticar dominancia rangos y residuo | 54 |
| 5ee7ec2 | feat(iterativos): buscar asignaciones de ecuaciones completas | 57 |
| 0a89e41 | feat(iterativos): reordenar filas y explicar la permutacion | 39 |
| d5db9d2 | feat(iterativos): calcular Jacobi con componentes anteriores | 56 |
| 901b9b8 | test(iterativos): contrastar Jacobi con todo el banco exacto | 83 |
| b745bd1 | test(iterativos): validar entradas exactas y errores por celda | 58 |
| 947712f | test(iterativos): verificar dominancia rangos y reordenamientos | 87 |
| d969ed5 | test(iterativos): cubrir asignaciones exhaustivas y heuristicas | 60 |
| dae38a4 | fix(iterativos): conservar residuo relativo con escalas extremas | 50 |

## Pendientes e incidencias

Sin pendientes funcionales ni decisiones para el propietario dentro del área asignada; sin cambios de UX.
Pendientes de integración: Gauss-Seidel, convergencia, resolver, API e interfaz a cargo de las otras áreas;
esta rama no declara validada su convergencia ni el recorrido del usuario del módulo nuevo.
El integrador debe unir las exportaciones de `__init__.py`, revisar y ejecutar la batería sobre el conjunto integrado.
