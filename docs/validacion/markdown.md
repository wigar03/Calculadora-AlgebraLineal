# Validación del Markdown público

Fecha: 2026-11-23. Rama: `orca/docs-publicas`; base: `d8131ba` (main local actualizado).

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

## Archivos auditados y renderizado final

Cada archivo se envió al endpoint `/markdown` de GitHub; se compararon sus fragmentos con los recibidos en
`math-renderer`, decodificando las entidades HTML. Ningún fragmento matemático quedó fuera del renderizador.

| Archivo | Expresiones | Bloques math | Petición (s) |
|---|---:|---:|---:|
| `README.md` | 1 | 0 | 0,5042 |
| `CHANGELOG.md` | 2 | 0 | 0,4583 |
| `docs/guia-matematica.md` | 274 | 29 | 0,9469 |
| `docs/distribucion.md` | 0 | 0 | 0,4445 |
| `docs/firma-codigo.md` | 0 | 0 | 0,4793 |
| `src/ui/web/vendor/README.md` | 0 | 0 | 0,4345 |
| `docs/notas-v1.0.0-rc.1.md` | 0 | 0 | 0,4458 |
| `docs/notas-v1.0.0-rc.2.md` | 1 | 0 | 0,4235 |
| `docs/notas-v1.0.0-rc.4.md` | 9 | 0 | 0,4369 |
| `docs/notas-v1.0.0-rc.5.md` | 4 | 0 | 0,4246 |

Total: 291 expresiones (29 bloques); las 291 pasan además KaTeX local con `throwOnError: true, strict: 'error'`.
La guía original de la base producía diez fragmentos sueltos; después produce cero. KaTeX detectó primero un
separador inválido `\1` en la matriz del contraejemplo de Jacobi; se repararon sus filas sin cambiar sus entradas.
GitHub añadía una barra al final de las filas de la matriz aumentada: se conservaron sus separadores en una misma
línea del bloque math y se comprobó de nuevo que todos sus caracteres llegaban intactos al renderizador.

## Cambios de formato y contenido obsoleto

| Antes | Después |
|---|---|
| `R^n` en una cabecera de texto | ``$`\mathbb{R}^n`$`` en el contexto académico. |
| `Ax = b` como código en README | ``$`Ax = b`$`` como expresión matemática. |
| `A·A⁻¹ = I` en rc.2 | ``$`A\cdot A^{-1} = I`$``. |
| `n ≤ 12`, `10⁻⁶`, dimensiones con `×` | Subíndices, exponentes y desigualdades dentro de delimitadores matemáticos. |
| Fórmulas con `$…$` que GitHub dejaba parcialmente sueltas | Sintaxis ``$`…`$`` para todas las expresiones en línea. |
| Fórmulas display con `$$…$$` | Bloques con lenguaje `math` (fracciones, matrices, sumatorias y métodos iterativos). |
| Resultados de secante en comillas de código | Resultados en notación matemática; las entradas `x^3-x-2`, `1` y `2` siguen siendo código. |
| Notas históricas con primer título de nivel 3 | Título de documento de nivel 1 y apartados de nivel 2. |

README usa `/releases/latest` y resume los 11 módulos; CHANGELOG conserva el enlace a la publicación original rc.1.
Se actualizaron los conteos de módulos, la versión de Python probada y el árbol del código; se retiraron conteos
de pruebas caducados de la guía. Vendor enlaza sus archivos de licencia sin modificar atribuciones ni licencias.
Las cuatro notas históricas recuperan exactamente su texto original al revertir los cambios de formato (comparación automatizada).
Los 28 Markdown internos no recibieron tratamiento editorial; sus enlaces son válidos y no necesitaron cambios.

## Casos adversos del verificador

Cada caso incluye un título válido `# A` antes de la entrada indicada; tiempos de una ejecución local, sin red.

| Entrada | Respuesta | Tiempo (ms) |
|---|---|---:|
| `$x` | `$ sin pareja`, línea 2 | 1,251 |
| `\frac{1}{2}` | `LaTeX fuera de matemáticas`, línea 2 | 0,688 |
| Apertura de bloque Python sin cierre | `bloque sin cerrar`, línea 2 | 0,728 |
| `![x](ausente.png)` | `enlace inexistente`, línea 2 | 0,957 |
| `[x](#ausente)` | `ancla inexistente`, línea 2 | 1,133 |
| `### B` después de `# A` | `salto de título: 1 a 3`, línea 2 | 0,717 |
| `[x][ausente]` | `referencia sin definir`, línea 2 | 1,421 |
| Código literal con dólares, LaTeX y enlace inexistente | `OK` (contenido literal) | 0,927 |

También se prueban imágenes, referencias colapsadas, rutas con espacios/codificación URL y paréntesis, anclas
acentuadas y repetidas, anclas HTML, cercas de longitud distinta, dólares escapados y revisión interna solo de enlaces.

## Pruebas finales y límites de la evidencia

- `python -m unittest discover tests -v`: 466 pruebas OK en 31,235 s (457 previas y 9 nuevas).
- Cada `tests/*.cjs` con `node --test`: 66 pruebas OK en 13 archivos; suma de tiempos por archivo 1982,9121 ms.
  La línea base Node se ejecutó conjuntamente (593,747 ms); los modos de ejecución no son una comparación de rendimiento.
- `python -m unittest tests.test_golden_api`: 1 prueba OK, 43 respuestas intactas, 1,079 s.
- `python scripts/verificar_markdown.py`: 10 públicos y enlaces de 28 internos; cero problemas, 125,955 ms incluyendo proceso.
- Los cuatro saltos de títulos iniciales pasan a cero; `git diff --check` no detecta problemas.

La CI existente descubre `tests/test_markdown.py`; sus pruebas y el verificador solo usan Python estándar y no requieren red.
No se modificaron el motor, la UI, los recursos JS/CSS ni sus versiones. La inspección visual final en github.com tras
publicar corresponde al coordinador; la validación realizada aquí es estructural y sintáctica, no una inspección visual.
Queda para el integrador valorar los comentarios erróneos del motor mencionados arriba, fuera del alcance autorizado.
