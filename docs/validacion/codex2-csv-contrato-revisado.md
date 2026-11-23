# Oráculos CSV revisados y comprobación independiente de 619898b

Fecha: 2026-11-23. Rama `orca/consolidacion-latex-rendimiento`, desde `main` `5ddb6cc`.
Se actualizaron únicamente pruebas; `src/` y los golden no se modificaron.

## Contrato exigido

- Cero negativo, decimal o científico: salida canónica `0`, sin signo ni exponente.
- Enteros con más de 15 cifras significativas: constante de texto validada `="n"`.
  Los ceros iniciales no cuentan; los dígitos originales del texto se conservan.
- Fracciones: constante `="p/q"` solo con denominador distinto de cero.
- Fórmulas tras espacios/controles: prefijo `'` antes del texto original completo, también en cabeceras.
- Decisión posterior del integrador: cabeceras racionales completas o enteras largas usan la constante
  de texto validada, **sin apóstrofo**; se exige el texto original exacto.
- El apóstrofo para fórmulas y textos no racionales con aspecto de fecha puede resultar visible en Calc;
  el integrador acepta expresamente ese coste, sin extenderlo a racionales completos.

El oráculo usa `csv`, `Decimal`, igualdad binaria de flotantes y expresiones propias; no importa formateadores.
Admite un entero flotante protegido si la constante entera validada reimporta exactamente el mismo `double`.
Rechaza fórmulas arbitrarias, denominadores cero, redondeo y recorte de espacios o controles del CSV.
Nueve pruebas del propio oráculo comprueban tanto ejemplos conformes como corrupciones deliberadas.

## Revalidación estricta de la biblioteca candidata

Se extrajo con `git show 619898b:src/ui/web/exportar.js` a `%TEMP%/exportar-619898b.js` conservando bytes.
Se ejecutaron las pruebas con `P2_EXPORTAR_JS` apuntando a ese archivo y `CSV_EXIGIR_PENDIENTES=1`.
Ambas variables desactivan las marcas CSV para la ejecución estricta; las marcas permanecen en la rama.

| Caso | Resultado en 619898b |
|---|---|
| Enteros de 16 y 25 cifras, negativos y con ceros iniciales | Pasa: texto validado, sin pérdida de dígitos |
| Denominadores 0, 000; positivos, negativos y 0/0 | Pasa: no produce constante racional |
| 14 prefijos × 4 operadores, en cabeceras y celdas | Pasa: texto completo y protección contra fórmulas |
| Corpus real de 11 módulos y tres casos largos | Pasa CSV: todas las filas y valores preservados |
| Número -0.0 y cadena -0 | Pasan: `0` |
| Cadenas -0.00 y -0e8 | Fallan normalización canónica: `0,00` y `0E+08` |
| 000123456789012345, 15 cifras significativas | Falla límite: cuenta ceros iniciales y produce constante de texto |
| Cabecera racional/entera larga exacta | Falla: introduce apóstrofo en lugar de constante validada |

Python: **23 pruebas, 3 fallos estrictos y 1 omisión** del motor LaTeX fuera de PATH.
Node independiente: **10 pruebas, 8 aprobadas y 2 fallos estrictos**, sin omisiones.
La omisión LaTeX no aprueba los 14 defectos previos; las correcciones LaTeX siguen asignadas a Antigravity.

## Reapertura real: apóstrofo en cabeceras

Herramientas portátiles existentes en `%TEMP%/auditoria-csv-mg7o8ewu`: LibreOffice y ssconvert/Gnumeric.
CSV exportado por Node conservando exactamente BOM UTF-8 y CRLF, sin convertir los saltos al capturar stdout.
Cabeceras y primera fila: `1/2`, `-17/19`, `0003/0007`, `9007199254740993123456789` y ` 1/2`.

- Calc: CSV → XLSX → ODS → XLSX; filtro
  `59,34,76,1,,3082,false,false,false,false,false,0,true` y perfil privado temporal.
  En importación y reapertura, A1 almacena **`'1/2`**, tipo `s`, sin fórmula, `quotePrefix=0`.
  El apóstrofo forma parte del texto visible; B1–E1 tienen el mismo defecto.
- Gnumeric: mismos bytes como TXT, detector STF y `LC_ALL=es_ES.UTF-8`;
  TXT → ODS → Gnumeric → ODS. A1 conserva **`1/2`**, tipo string y sin fórmula, en ambas etapas.
  B1–E1 también conservan el texto exacto, incluido el espacio inicial de E1.
- Las fracciones/enteros de la fila de datos usan constantes y preservan los dígitos en ambos motores.

Se leyeron valores, tipos y fórmulas con ZIP/XML estándar; en ODS se reconstruyeron espacios `text:s`.
Artefactos locales: `C:/Users/wigar/AppData/Local/Temp/csv-619898b-reapertura-zwaif0wf/`:
CSV, XLSX/ODS/Gnumeric de ambas etapas e `informe.json`, sin modificar el sistema.
El script local reproducible queda en `scratch/reabrir_csv_619898b.py` (no se publica como dependencia).

## Estado

Contra la biblioteca de `main`, solo las cinco regresiones CSV tienen `expectedFailure` Python o `skip` Node,
con motivo explícito; el resto sigue siendo estricto, incluidos los límites de 15 cifras y el texto inocuo.
La batería completa local termina **489 Python, OK** (dos omisiones de motor y cinco fallos esperados),
41,937 s; **79 Node, 74 aprobadas y cinco omisiones autorizadas**, 5,412 s, con Chrome portátil real.
Pendiente por instrucción del integrador: **esperar el siguiente commit y revalidar LaTeX y CSV juntos**.
No se retiran las marcas hasta que el integrador incorpore `exportar.js`.
