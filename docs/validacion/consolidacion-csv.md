# Auditoría de seguridad y compatibilidad CSV

Fecha: 2026-11-23. Rama `orca/consolidacion-csv`, desde `main` `60c6d0c`.
Se revisó `src/ui/web/exportar.js` sin editarlo; SHA-256:
`3ef92d0bb4fc0e5b65842d765d5dce1029ff4e4a1bf88951537fcb7b95a474fc`.
No hay cambios de UX, motores, golden, dependencias del proyecto, push, merge ni release.

## Entorno y procedimiento independiente

- Windows, Python 3.12.10, Node 26.13.0; WSL no está instalado.
- LibreOffice Portable 26.2.4.2 y Gnumeric/ssconvert 1.12.62, extraídos únicamente en TEMP.
  Fuentes: [LibreOffice Portable](https://download.documentfoundation.org/libreoffice/portable/26.2.4/)
  y [paquetes MSYS2 UCRT64](https://repo.msys2.org/mingw/ucrt64/).
  Sus dependencias también se extrajeron en TEMP; no se ejecutaron instaladores ni se requirió administrador.
- `tests/test_externo_csv.py` consulta las 43 entradas golden por HTTP y compara los campos congelados.
  Las 33 respuestas con procedimiento abarcan los 11 módulos y 13 identificadores de adaptador.
  Nueve respuestas tienen tablas (diez tablas): bisección, eficiencia de determinantes, iterativos,
  Newton-Raphson, regla falsa y secante. Los demás resultados no ofrecen CSV; no se inventaron tablas.
- Node ejecuta `tablasACSV`, la función usada para exportar todas las tablas. Se conservan BOM y bytes UTF-8.
- Calc: CSV → XLSX → ODS → XLSX. Gnumeric: mismos bytes como TXT → ODS → Gnumeric → ODS.
  Se inspeccionan tipos, valores, todas las celdas y fórmulas del primer y del último libro, con ZIP/XML estándar.
  El oráculo también se prueba contra una fórmula con caché inocua, una fecha y un decimal redondeado.
- Fracciones: texto exacto, nunca fecha. Únicas fórmulas admitidas: constantes de texto idénticas al racional
  original con denominador distinto de cero o al entero original validado de más de 15 cifras (decisión del integrador).
  Ningún título/cabecera/texto arbitrario recibe esa excepción.
- Decimales: el integrador aprobó el límite de 15 cifras significativas de Calc/Excel y normalizar `-0` a `0`.
  Se admite como máximo media unidad de la cifra significativa 15; las fracciones/enteros largos siguen siendo exactos.
  STF recorta espacios extremos y los formatos nativos normalizan saltos/controles: esto se permite solo al comparar
  texto; nunca permite sustituirlo por número, fecha o fórmula. El CSV original conserva esos caracteres.

## Hallazgos reproducidos y correcciones solicitadas

1. **Inyección real:** `\n=1+2`, ` =1+2` y `\u00a0=1+2`, en celdas y cabeceras, producen fórmula `1+2`
   y valor numérico `3` en Gnumeric STF. `PREFIJO_FORMULA` solo mira el primer carácter.
   Proteger también después de espacios/controles Unicode, conservando el texto; no basta con entrecomillar CSV.
2. `1/0` y `1/000` pasan la expresión regular y generan `="1/0"`/`="1/000"`.
   Son constantes inocuas, pero no racionales: comprobar también denominador distinto de cero.
3. `9007199254740993123456789` se convierte en número y pierde cifras en ambos motores.
   El integrador aprobó exportarlo como texto mediante una constante fija solo después de validar el entero completo.
4. Texto `1/2` seguido de LF: Calc con especiales desactivados lo conserva como texto y recorta LF;
   con especiales activados lo convierte en fecha (serial observado `46054`). STF también lo convierte en fecha.
5. Cabecera textual `1/2`: Gnumeric la convierte en fecha. Proteger textos racionales de títulos/cabeceras
   como texto; no generar fórmulas arbitrarias para resolverlo.
6. `=cmd|'/c calc'!A1`, `=HYPERLINK("#local";"x")`, `=1+2`, `+1+2`, `-1+2`, `@SUM(1)`, tabulación y CR
   iniciales sí reciben apóstrofo y permanecen como texto. También se prueban comillas, `;`, saltos internos,
   Unicode `ñ á Ω 你好`, BOM inicial, controles, fracciones falsas y extremos numéricos.
7. `1/2`, `-17/19`, `0003/0007`, `0/5`: se conservan como texto exacto en ambos motores tras guardar/reabrir.
   No se encontró una vía para introducir comillas/comandos dentro de la constante racional de la biblioteca original.

## Configuración de importación y limitaciones

Calc usa `59,34,76,1,,3082,false,false,false,false,false,0,true`: `;`, comillas, UTF-8, español,
campos entrecomillados sin forzar texto, especiales **false** (predeterminado), sin recortar espacios y fórmulas **true**.
La evaluación de fórmulas se activa expresamente para que las constantes contractuales produzcan texto `p/q`.
`CSV_CALC_ESPECIALES=1` ejecuta el segundo perfil, con especiales **true**; no se confunden sus resultados.
Los tokens están definidos en la [documentación de LibreOffice](https://help.libreoffice.org/latest/en-US/text/shared/guide/csv_params.html).

`ssconvert --help-all` no ofrece separador de importación: `-O` configura **exportación** y el importador
`stf_assistant` exige GUI. La prueba usa **detección automática de STF, no selección explícita de ;**:
copia byte a byte con extensión `.txt` y `LC_ALL=es_ES.UTF-8`. Si falta un locale de coma decimal en Linux,
compila uno con `localedef --no-archive` en TEMP; no cambia locales del sistema. Con locale inglés, los decimales
con coma pueden causar detección incorrecta; con `.csv`, incluso `Cofactores;LU` queda como una sola celda.
En la GUI se puede elegir el separador en el asistente; no se automatizó ese diálogo.
Véanse [ssconvert](https://gnome.pages.gitlab.gnome.org/gnumeric/manual/sect-files-ssconvert.html)
y el [importador STF](https://github.com/GNOME/gnumeric/blob/master/src/stf.c).

Excel no estuvo disponible en ningún entorno usado para esta auditoría: no está en PATH, rutas habituales ni
registro de aplicaciones/COM de Windows; el job Ubuntu `externos` no proporciona Excel. No se ejecutó Excel.
Quedan sin probar su apertura por doble clic, asistente/Power Query, configuraciones regionales, advertencias DDE,
tratamiento del apóstrofo/Unicode, evaluación y reapertura de las constantes y diferencias entre versiones de Excel.
El archivo XLSX producido por Calc no constituye una prueba en Excel.

## Marcas temporales autorizadas

El integrador asignó las correcciones a Antigravity y autorizó omisiones explícitas hasta recibir su commit.
Ocho subpruebas marcadas: `33_adversarios` y `34_precision`, cada una en `importado` y `reabierto`,
para `calc` y para `gnumeric` (2 × 2 × 2). Solo se omiten errores de categorías conocidas asociados exactamente a:
`1/0`, `1/000`, `\n=1+2`, ` =1+2`, `\u00a0=1+2`, `1/2\n`, cabecera `1/2` y
`9007199254740993123456789`. Cualquier otro fallo sigue siendo fallo.
`P2_EXPORTAR_JS` o `CSV_EXIGIR_PENDIENTES=1` desactivan todas estas marcas para la revalidación estricta.
Las ausencias de herramientas se comprueban antes: con `REQUIERE_EXTERNOS=1` siempre fallan, sin omitirlas.

## Resultado por herramienta y reproducción

En ambos perfiles Calc: 18/18 etapas de respuestas reales conformes; cuatro etapas adversarias/precisión marcadas.
Gnumeric STF con locale español: 18/18 etapas reales conformes; cuatro etapas adversarias/precisión marcadas.
Ejecución externa: cuatro métodos, cero fallos no esperados, ocho omisiones explícitas; no equivale a aprobación CSV.

Ejecutar `python -m unittest tests.test_externo_csv -v`, con `SOFFICE` y `SSCONVERT` apuntando a los ejecutables
portables o instalados. `REQUIERE_EXTERNOS=1` exige ambos; sin él, las ausencias se omiten indicando motivo.
`CSV_EVIDENCIA_DIR` conserva CSV, TXT, libros y `informe.json`; `CSV_CALC_ESPECIALES=1` selecciona el segundo perfil.

## Batería y cambio adicional Markdown

`python -m unittest discover tests -v`: 481 métodos en 40.571 s, OK, tres omisiones:
motor LaTeX ausente (preexistente) y las dos herramientas CSV sin configurar en PATH.
Con ejecutables portables configurados, los cuatro métodos externos terminan OK con las ocho marcas anteriores;
con `CSV_EXIGIR_PENDIENTES=1`, esos ocho casos son fallos reproducibles. No se afirma validación final de P2.
Ausencias forzadas: `REQUIERE_EXTERNOS=0` → dos omisiones, salida 0;
`REQUIERE_EXTERNOS=1` → dos fallos, salida 1. Golden: sin modificación; las 43 consultas congeladas pasan.

Node, todos los `tests/*.cjs`: 75 pruebas, 74 pasan y una falla al arrancar Edge (salida 0 antes de CDP).
El subconjunto `tests/test_*.cjs` es 67/68 y las siete pruebas auxiliares pasan.
Es el problema de auto de elevación ya corregido por el integrador en `main` `4f9eb9b`;
no está relacionado con CSV y esta rama aún no incorpora ese cambio ajeno.

Por encargo adicional del integrador se añadió la regla del verificador Markdown: dentro de `$…$`, `$`backticks`$`,
`$$…$$` y bloques `math`, detectar `<` seguido de letra o `>` precedido de letra/`}` sin espacio.
La regresión usa los sumatorios antiguos de Gauss-Seidel, comprueba `\lt`/`\gt`, líneas y código literal.
`tests.test_markdown`: diez pruebas OK. Verificador público: 11 documentos públicos, 31 internos, cero problemas.
Se incorporó exclusivamente la corrección documental aprobada `0b04d8e` como `edae11b`;
el integrador omitirá ese duplicado al integrar. El exportador y sus referencias permanecen intactos.
