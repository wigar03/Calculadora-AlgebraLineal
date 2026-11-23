# Validación del Markdown público

Fecha: 2026-11-23. Rama: `orca/docs-publicas`; base: `9266219` (main local actualizado).

## Alcance y línea base

Se auditan README, CHANGELOG, guía matemática, distribución, firma, cuatro notas históricas y README de vendor.
Los documentos internos solo se comprueban por sus enlaces; se preservan autorías, referencias y licencias.
Antes de corregir: 457 pruebas Python (31,664 s), 66 Node (593,747 ms) y golden (43 respuestas, 1 prueba) OK.
La prueba nueva falló primero por ausencia del verificador y después detectó cuatro saltos de títulos históricos.

## Errores matemáticos verificados antes de corregir

Comprobaciones independientes con SymPy 1.14.0, sin importar el motor de la calculadora:

- `diag(-2, 3).det()` devuelve −6; su valor absoluto es 6. `diag(-2, 3, 4).det()` devuelve −24; su valor absoluto es 24.
  Por tanto, el valor absoluto representa área/volumen sin orientación; el signo del determinante recoge la orientación.
- La expansión por una fila de una matriz de orden cuatro tiene cuatro menores inmediatos de orden tres, no 24.
  `factorial(4)` vale 24, pero cuenta términos de la fórmula de Leibniz, no esos menores.
  Se retiran las tablas que confundían productos, menores y operaciones; se conservan las complejidades factorial y cúbica.
- La suma simbólica `summation(j*(2*j+1), (j, 1, n-1)) + n-1` da 4, 15, 37, 74 y 315 para órdenes 2, 3, 4, 5 y 8.
  Las antiguas cifras 2, 14, 36, 75 y 320 no eran un conteo reproducible bajo ese modelo; se sustituirán por el orden asintótico.
- Para la matriz del contraejemplo Jacobi/Gauss-Seidel, `(-D.inv()*(L+U)).eigenvals()` da `{0: 3}` y
  `(-(D+L).inv()*U).eigenvals()` da `{2: 2, 0: 1}`. Los radios 0 y 2 de la guía son correctos y se conservan.

Los comentarios matemáticos de `src/matrices/determinante.py` repiten algunos errores; quedan fuera del área autorizada.

Comprobaciones complementarias: `solve((x-1)*(x-2)*(x-3), x)` da tres raíces (1, 2, 3), aunque en 0 y 4 los
signos sean opuestos (−6, 6). La guía no debe prometer una sola raíz a partir del muestreo. La traza de una matriz
rectangular (`zeros(2, 3).trace()`) lanza `NonSquareMatrixError`: la propiedad se restringirá a matrices cuadradas.
Las normas de cambio y residuo escritas en la guía son absolutas; se aclarará que los criterios usan sus versiones
relativas (por ejemplo, cambio absoluto 2 y relativo 1 al pasar de 0 a 2), conservando las expresiones.

## Renderizado y formato

GitHub recibe el contenido con `gh api -X POST /markdown -f mode=gfm -f context=wigar03/Calculadora-AlgebraLineal -F text=@archivo`.
La opción `-f text=@archivo` de la tarea se probó: produce un párrafo con el nombre literal, sin leer el archivo.
Una sonda confirmó que las fórmulas en línea con delimitadores de dólar y comillas invertidas internas se reconocen completas;
los bloques con lenguaje `math` producen `math-renderer`. Se conservará el código de entrada como código.

## Resultados finales

Pendientes de completar al terminar la corrección y ejecutar la batería completa.
