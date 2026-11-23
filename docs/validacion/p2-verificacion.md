# P2: verificación independiente de exportaciones

Fecha: 2026-11-23. Rama: `orca/p2-verificacion`, desde `main` `d8131ba`.
Solo se añaden pruebas, herramientas de verificación y este informe; ningún cambio en `src/`, UX o referencias.
Entorno: Windows, Python 3.12.10, Node v26.13.0; KaTeX local, sin dependencias nuevas.
Biblioteca examinada: `src/ui/web/exportar.js`, SHA-256
`e0ffb9fa3731efc13955f67d2b7d40ea2c20ac3ea2ea01d6faf2deaf56896457`.

## Alcance y oráculos

- Se consultan las 43 entradas golden por HTTP real y se comparan también sus campos congelados.
- Las 33 respuestas que tienen adaptador producen `procedimiento`; se exportan todas, de los 11 módulos.
- Se añaden tres respuestas largas reales y un procedimiento adversario: 37 procedimientos, 46 consultas HTTP.
- CSV se relee con `csv.reader(strict=True)`, separador `;`: cada fila/celda contra la respuesta original.
  Los flotantes se comparan por `float.hex()` (incluye el signo de cero); enteros/cadenas con `Decimal`.
  Fracciones y protección de texto tienen oráculos literales; se comprueban BOM, CRLF y campos escapados.
- Se verifican anidación de entornos, delimitadores, paquetes, secciones, tablas completas y `longtable`.
  Los fragmentos originales deben seguir presentes. KaTeX usa `throwOnError: true`, `strict: 'error'` y `trust: false`.
  Se inspeccionaron 267 421 apariciones; se renderizaron 56 841 fragmentos distintos dentro de cada documento.
- No se encontraron `pdflatex`, `lualatex`, `xelatex`, `tectonic` ni `latex`: compilación real omitida expresamente.
  La prueba la ejecutará automáticamente si encuentra uno, con shell escape deshabilitado.
- Las dimensiones, iteraciones y presupuestos se importan de `src/core/limites.py`; no se alteran sus límites.

## Casos largos y mediciones

Jacobi: `A[i,i]=1`, `A[i,(i+1) mod 20]=-0.9999`, resto cero; `b=[1]*20`, método `jacobi`,
`tolerancia="1e-300"`, `max_iteraciones=10000`. API: HTTP 400 en 3184.14 ms, respuesta exacta
`{"error":"La respuesta supera el tamaño máximo permitido.","tipo":"limite","codigo":"respuesta_grande"}`.
La prueba obtiene entonces el resultado del motor real y su adaptador sin transporte HTTP: 2894.78 ms,
10 000 filas, motivo `max_iteraciones`. No se afirma que esa respuesta completa pueda descargarse desde la API.

Bisección: `funcion="x-1e-300"`, `a="0"`, `b="1e100"`, `criterio="residuo"`,
`tolerancia="1e-320"`, `max_iteraciones=1000`: HTTP 200 en 85.30 ms, 1000 filas, `max_iteraciones`.
Regla falsa: `funcion="x^30-1"`, `xl="0"`, `xu="2"`, `tolerancia="1e-300"`,
`max_iteraciones=1000`: HTTP 200 en 74.14 ms, 1000 filas, `max_iteraciones`.

| Caso | Filas | Exportación antes / repetición final (ms) | RSS final (MiB) | Incremento heap (MiB) | Bytes LaTeX + CSV |
|---|---:|---:|---:|---:|---:|
| Jacobi 20×20 | 10 000 | 152.51 / 152.45 | 180.90 | 60.97 | 10 107 628 |
| Bisección | 1000 | 4.03 / 3.82 | 229.02 | 4.72 | 212 153 |
| Regla falsa | 1000 | 7.31 / 7.29 | 230.41 | 8.25 | 261 196 |
| Adversario | 25 | 0.33 / 0.34 | 230.82 | 0.12 | 3020 |

Antes y después se examina el mismo SHA: no se ha corregido la implementación en esta rama.
Tiempo: documento + CSV de todas las tablas + tablas LaTeX individuales, sin incluir KaTeX.
Memoria: proceso Node compartido por el corpus; RSS no es memoria exclusiva de cada caso, pico final 235.50 MiB.
Las tres tablas largas pasan los presupuestos centrales de 10 s y 512 MiB; ninguna fila numérica se trunca.

## Incumplimientos reproducidos para asignar a la implementación

1. Todos los CSV carecen de BOM. Científica usa `e-7`, etc., en vez del formato contractual `E-07`.
2. Texto y cabeceras `=cmd|' /C calc'!A0`, `@SUM(1+1)`, `+SUM(A1)`, `-SUM(A1)`, tabulación y retorno
   iniciales quedan sin prefijo `'`. La prueba también distingue `=1/2` y `-1/2;=cmd|x` de fracciones válidas.
3. `1/2`, `-17/19`, `0003/0007` salen literales, sin la fórmula fija de texto `="p/q"`.
4. `  bordes  ` sale sin comillas. La última fila nula de una tabla de una columna desaparece al releer el CSV
   (25 registros en lugar de 26 contando cabecera); comillas, `;` y salto interno sí se escapan correctamente.
5. `-0.0` se convierte en `0`. `NaN` e infinitos numéricos se borran silenciosamente; la cadena `NaN` sí se conserva.
   `1e-300`, dobles de 17 cifras y cadenas de enteros/decimales de más de 20 cifras mantienen su valor al releerlos.
6. Los 37 documentos omiten `\usepackage[spanish]{babel}`. Las tres tablas largas usan `tabular` sin paginación
   ni encabezado repetido. Los conteos LaTeX sí incluyen 10 000/1000/1000 filas completas.
7. Los 33 procedimientos golden y los tres largos pasan KaTeX estricto. El adversario encuentra dos errores:
   etiqueta `Unicode: ñ á Ω 你好` queda con Unicode incompatible en `\text{...}`; etiqueta `\input{ajeno}`
   queda como comando sin escapar. No se ejecuta ese comando en estas pruebas de KaTeX.

El adversario aplica los textos a etiquetas de entrada, pasos, verificación, avisos, cabecera y celdas.
Incluye comillas, `;`, saltos, espacios extremos, Unicode, fracciones falsas, cero negativo y magnitudes extremas.
Su exportación final tarda 0.34 ms; la entrada íntegra reproducible está en `adversario()` de la prueba Python.

## Reproducción y resultado de la batería

`python -m unittest tests.test_golden_api`: 1 prueba OK (las 43 respuestas).
`python -m unittest discover tests -v`: 467 pruebas; 56 fallos de subpruebas P2, 1 omitida por falta de motor.
Las 457 pruebas Python anteriores pasan; las 10 nuevas tienen 4 métodos OK, 5 con fallos y 1 omitido.
`tests/*.cjs`, ejecutados individualmente con `node --test`: 72 pruebas, 67 OK y 5 fallidas (todas nuevas).
Las 66 pruebas Node anteriores pasan. No se declara P2 validado; estos fallos son la entrega solicitada.
`python -m tests.test_exportacion_modulos --informe ruta.json` genera tiempos, entradas largas y diagnósticos.
`P2_EXPORTAR_JS` puede apuntar al `exportar.js` de otra rama para repetir sin editar `src/`.
