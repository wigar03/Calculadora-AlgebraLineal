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

## Actualización: revisión cruzada R1–R3 (2026-11-23)

Rama `orca/jacobi` rebasada sobre `main` 046f720, sin repetir los commits ya integrados.
Esta actualización sustituye los pendientes de integración iniciales anteriores para el área asignada.
Se modificaron únicamente `entrada.py`, `matriz.py`, `jacobi.py`, sus dos archivos de pruebas y esta evidencia.
No se editaron `resolver.py`, `convergencia.py`, Gauss-Seidel, analizador de texto ni archivos web.

- R1: antes de corregir se ejecutaron tres regresiones y se observaron siete fallos/subcasos.
  El caso mínimo `residuo([[1e-200]],[0.0],[1e-200])` pasó de relativo 0 a **1**, como exige
  la razón independiente calculada con Fraction de los mismos floats binarios.
- El respaldo racional del residuo ahora recalcula numerador y escala si el absoluto es cero/subnormal,
  existen productos subnormales, o la escala subdesborda/desborda. No reconstruye la razón de un absoluto redondeado.
  También se cubre una escala subdesbordada aunque los productos particulares Ax sean todos cero.
- Jacobi conserva los productos subnormales mediante un respaldo racional del paso con redondeo final a float;
  siempre utiliza la tupla anterior. La vía ordinaria sigue usando doble y las referencias del banco no cambian.
- R1 por HTTP: A diagonal `1e-200`, fuera de diagonal `5e-201`, b=`[5e-324,5e-324]` ahora converge en **22 pasos**,
  x=`[3.293770186978782e-124,3.293770186978782e-124]`, residuo relativo **1.192093037759159e-7**.
  La prueba verifica esa razón independientemente con Fraction de la A, b y x devueltas.
- R2/R3: tres pruebas de regresión produjeron nueve fallos/subcasos antes de corregir.
  La lectura comprueba magnitudes mediante umbrales racionales de IEEE-754, antes de diagnósticos y permutaciones.
  `sistema_float` sigue siendo la única conversión de celdas a float; el triple leído conserva Fraction exactos.
- Se comprueban los umbrales de empate a cero/infinito, incluido un racional que redondea al máximo finito
  aunque sea algo mayor que este. Los errores siguen indicando cómo corregir la magnitud.
- R2 por HTTP: `A=[[1,0],[1e400,1]]` identifica **fila 2, columna 1**, sin error interno en inglés.
- R3 por HTTP con reordenar: `A=[[0,1],[1,1e-400]]` identifica **fila 2, columna 2** del editor original.

Validación final: **31 pruebas del área OK**, incluidas siete nuevas; batería completa
`python -m unittest discover tests -v`: **407 pruebas OK, 14.985 s**;
bucle completo `node --test` por archivo: **58 pruebas OK**. `git diff 046f720 --check` sin errores.
Comprobación de rendimiento con 20 variables en bloques [[1,0.9999],[0.9999,1]], tolerancia 1e-12 y
máximo 10000: ambos consumen las 10000 iteraciones; Jacobi **2.848 s**, Gauss-Seidel **5.839 s** (llamada directa).

| Hash | Mensaje | Añadidas + eliminadas |
|---|---|---:|
| d2ef468 | fix(iterativos): preservar el residuo relativo ante subdesbordamiento | 59 |
| e121ede | fix(jacobi): conservar los productos subnormales en cada barrido | 42 |
| 15e5e13 | fix(iterativos): validar magnitudes en las celdas originales | 66 |

Pendiente del integrador: revisar y unir estas correcciones con la verificación final exacta de Codex 2
en `resolver.py`. Los dos P2 de la auditoría del analizador de texto se entregan aparte, sin corregir archivos ajenos,
en `%TEMP%/orca_texto_audit_task_fa36e0a61ef6/HALLAZGOS.md`.
