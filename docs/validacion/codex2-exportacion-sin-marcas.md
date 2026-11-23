# Revalidación independiente tras retirar las 19 marcas

Fecha: 2026-11-23. Rama `orca/consolidacion-latex-rendimiento`, rebasada sobre
`orca/integracion-exportar` `e11d33e`; no se editaron `src/`, golden ni otros motores.
Biblioteca integrada: SHA-256 `2c6acff322f27e17fd3bbed79b1d48774450e4966d07445ba3a5d27560bd3cec`.
Este informe sustituye el estado pendiente de los informes anteriores de esta área.

Se eliminaron las cinco marcas CSV de Python/Node y los catorce `expectedFailure` LaTeX.
Los 36 procedimientos reales y el adversario se ejecutan completos, sin lista de excepciones.
No se definieron `P2_EXPORTAR_JS` ni `CSV_EXIGIR_PENDIENTES`; se usó el archivo integrado directamente.

## Herramientas reales y resultados

Windows 11, Python 3.12.10 y Node 26.13.0; herramientas portátiles previamente extraídas en TEMP.

- pdfTeX 1.40.29, TeX Live 2026: **37 PDF y 74 pasadas correctas**, `-halt-on-error` y `-no-shell-escape`.
  Cero errores, caracteres perdidos, `Overfull hbox` o desbordamientos verticales graves en ambos logs.
  El máximo horizontal observado es **0 pt**, inferior al criterio de 1 pt.
  Jacobi 20×20/10 000 iteraciones: **143 páginas**; bisección/1000: **14**;
  regla falsa/1000: **20**; adversario UTF-8, símbolos escapados y matrices: **2**.
  Prueba dedicada: dos métodos, OK, 83,938 s; los 37 documentos se compilan dentro de esos métodos.
- LibreOffice Calc **26.2.4.2**: **22/22 etapas conformes**, CSV → XLSX → ODS → XLSX.
- Gnumeric/ssconvert **1.12.62**: **22/22 etapas conformes**, mismos bytes con detector STF y locale español,
  TXT → ODS → Gnumeric → ODS. Se verificaron tipos, valores y fórmulas con ZIP/XML estándar.
- Node: **81/81 pruebas aprobadas**, sin omisiones ni fallos, incluido Chrome portátil real; 5,046 s.
  El oráculo independiente CSV aporta diez pruebas activas, todas aprobadas.

Las etapas de hoja de cálculo abarcan todas las tablas golden y los adversarios; se activó
`CSV_TEXTO_RACIONAL_EXACTO=1` para rechazar apóstrofos visibles en racionales completos.
Se conservaron CSV, libros y resultados en `%TEMP%/orca-latex-rendimiento-9r1w7eur/csv-integrado/`.
Los PDF, fuentes y logs están en `%TEMP%/orca-latex-rendimiento-9r1w7eur/artefactos-integrados/`.

## Reapertura adicional de las cabeceras corregidas

Se exportaron con el archivo integrado las cabeceras `1/2`, `-17/19`, `0003/0007` y
`9007199254740993123456789`, conservando BOM y CRLF originales del proceso Node.
Calc y Gnumeric conservan exactamente esos cuatro textos en importación y reapertura:
sin apóstrofo visible, sin fecha, sin pérdida de cifras, con constantes de texto validadas.
En Calc, `quotePrefix=0` y la constante de A1 es `"1/2"`, cuyo valor mostrado es `1/2`.
El caso textual no racional ` 1/2` conserva un apóstrofo visible en Calc: es el coste aprobado expresamente
por el integrador; Gnumeric conserva el espacio inicial sin apóstrofo.
Artefactos adicionales: `%TEMP%/csv-reapertura-qo4w9jza/informe.json` y sus libros de ambas etapas.

## Exportaciones simultáneas del archivo integrado

Tres Jacobi de 10 000 filas y una bisección de 1000, cuatro procesos Node simultáneos:
162,83–175,55 ms para cada Jacobi, 11,88 ms para bisección; RSS máximo por proceso **165,34 MiB**.
Todas las filas están presentes, sin mutar los procedimientos; salida de la medición: código 0.

## Único fallo adicional de la batería completa

Con `REQUIERE_EXTERNOS=1`, motor LaTeX en PATH, Calc y Gnumeric configurados, la batería completa ejecutó
**497 pruebas en 180,021 s, un fallo, cero omisiones y ninguna marca esperada ni éxito inesperado**.
Falla `TestExportacionModulos.test_compilacion_real_si_hay_motor_instalado`, subcaso `adversario`:
el fixture CSV contiene `Unicode: ñ á Ω 你好` y pdfLaTeX aborta con
`Unicode character Ω (U+03A9) not set up for use with LaTeX`.
No es uno de los 37 PDF del contrato (su adversario exige acentos latinos y caracteres especiales).
No se ha retirado ni debilitado esa prueba adicional; el bloqueo se comunica al integrador para resolver
el alcance del fixture o asignar el soporte Unicode de `exportar.js`, que no se edita en esta rama.
