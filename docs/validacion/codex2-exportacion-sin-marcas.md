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

## Único fallo adicional de la batería completa (histórico)

Con `REQUIERE_EXTERNOS=1`, motor LaTeX en PATH, Calc y Gnumeric configurados, la batería completa ejecutó
**497 pruebas en 180,021 s, un fallo, cero omisiones y ninguna marca esperada ni éxito inesperado**.
Falla `TestExportacionModulos.test_compilacion_real_si_hay_motor_instalado`, subcaso `adversario`:
el fixture CSV contiene `Unicode: ñ á Ω 你好` y pdfLaTeX aborta con
`Unicode character Ω (U+03A9) not set up for use with LaTeX`.
No es uno de los 37 PDF del contrato (su adversario exige acentos latinos y caracteres especiales).
No se ha retirado ni debilitado esa prueba adicional; el bloqueo se comunica al integrador para resolver
el alcance del fixture o asignar el soporte Unicode de `exportar.js`, que no se edita en esta rama.

## Revalidación final desde main 5ec2154: Unicode corregido

La rama se rebasó sobre `main` `5ec2154`, que integra la corrección Unicode de Antigravity
(`1ec825c`, incorporada como `35cd3cb`); esta revalidación no modifica código, pruebas ni golden.
SHA-256 actual de `exportar.js`: `4fdaf33e838b154e1793dbe1bc12876f6d51baade4d99a317c4be0a80cb5672e`.
Se usó `REQUIERE_EXTERNOS=1`; se eliminaron `P2_EXPORTAR_JS`, `CSV_EXIGIR_PENDIENTES` y
`CSV_TEXTO_RACIONAL_EXACTO` del entorno. Los oráculos funcionan sin excepciones y conservan la exigencia
predeterminada de texto racional exacto. Los perfiles de importación no alteran los bytes exportados.

| Herramienta / perfil | Resultado independiente |
|---|---|
| Python completo, herramientas obligatorias | **497/497 pruebas aprobadas**, 178,737 s, cero omisiones o marcas |
| `test_compilacion_real_si_hay_motor_instalado` | Pasa también el adversario original `ñ á Ω 你好` |
| `test_externo_latex` | 37 PDF, 74 pasadas correctas; cero `Overfull hbox`, máximo 0 pt |
| LibreOffice Calc, especiales desactivados | 22/22 etapas correctas, cero errores |
| LibreOffice Calc, especiales activados | 22/22 etapas correctas, cero errores; prueba adicional 10,987 s |
| Gnumeric STF, locale español | 22/22 etapas correctas, cero errores |
| Node, incluidos auxiliares y Chrome portátil real | 81/81 pruebas aprobadas, cero omisiones; 5,509 s |

Los libros se importaron, guardaron y reabrieron; valores, tipos, fórmulas y cabeceras racionales se
comprobaron con los oráculos independientes existentes, sin retirar el adversario `ñ á Ω 你好`.

### Comprobación del texto visible del PDF

Se exportó un procedimiento cuyo único texto de muestra es `ñ á Ω 你好`, sin escribir los códigos
de respaldo en la entrada, y se compiló dos veces con el mismo `exportar.js` de main y pdfLaTeX.
El PDF tiene una página, sin errores, caracteres perdidos ni desbordamientos mayores de 1 pt.

Se extrajo el texto con **pypdf y PyMuPDF**, de forma independiente de los formateadores:

```text
Comprobación Unicode: Ω [U+4F60][U+597D]
Texto original del usuario
ñ á Ω [U+4F60][U+597D]
```

Ambos extractores devuelven para el glifo griego `Ω` (U+2126), canónicamente equivalente a `Ω` (U+03A9);
la normalización **NFC** de ambos textos confirma `Ω`. No se confunde el respaldo con un literal añadido
por la prueba: `你` produce `[U+4F60]` y `好` produce `[U+597D]` en la salida real.
También se renderizó la página a PNG con PyMuPDF a escala 2 y se inspeccionó la imagen: se ve la letra
griega Ω, los dos códigos entre corchetes, los acentos y la ñ; sin recortes, solapamientos ni glifos vacíos.

Evidencia local bajo `%TEMP%/orca-latex-rendimiento-9r1w7eur/unicode-main-5ec2154/`:
`visible/documento.pdf`, `visible/pagina-1.png`, dos textos extraídos e `informe.json`;
`csv-predeterminado/{calc,gnumeric}/informe.json` y `csv-especiales/calc/informe.json` conservan los 66
resultados de etapas y los libros. El script de comprobación está en `scratch/verificar_unicode_pdf.py`.

La compilación conserva la paginación de los casos largos: Jacobi 143 páginas, bisección 14 y regla falsa 20.
El único fallo Unicode histórico queda resuelto; no hay fallos, omisiones, marcas ni éxitos inesperados
en la batería completa actual. Se mantiene íntegro el fixture que permitió descubrirlo.
