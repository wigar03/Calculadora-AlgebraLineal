# Consolidación de `src/ui/web/exportar.js` (LaTeX y CSV con herramientas reales)

Rama: `orca/consolidacion-chrome` (rebasada sobre `main` `69dac10`). Hash final: `exportar.js?v=a0a3d589eec5` (SHA-256 LF).
Sin cambios de UX, sin funciones nuevas y sin editar oráculos ajenos (`tests/test_exportacion_modulos.py`, `tests/exportacion_verificar.cjs`).

## Correcciones aplicadas

### A. LaTeX (`6b608cc`)
1. **`MaxMatrixCols` (`jacobi_20x20_10000`):** `\setcounter{MaxMatrixCols}{32}` (`>= ITERATIVOS_MAX = 20`), resolviendo `Extra alignment tab` en matrices 20×20.
2. **Porcentaje con `babel-spanish` (`regla_falsa[3]`, `regla_falsa_1000`):** se conserva `\usepackage[spanish]{babel}` literal y se añade `\spanishplainpercent` para desactivar `\es@sppercent` sin alterar fragmentos matemáticos (`\,\%`). Además `esMathSeguro` admite `\;` para que `\varepsilon_a\;(\%)` se emita en modo matemático.
3. **Ajuste al ancho sin perder filas, columnas ni cifras (`Overfull \hbox <= 1 pt`):**
   - `\usepackage[a4paper,margin=1.2cm]{geometry}`, `\sloppy`, `\emergencystretch=3em`, `\subsubsection*` (en lugar de `\paragraph` en línea).
   - Ecuaciones `\[ ... \]` redefinidas vía `\@namedef{[}` / `\@namedef{]}` (sin `$` ni `\begin`/`\end` en el preámbulo, conservando intactos los fragmentos `\[...\]` para KaTeX) con escalado automático solo si exceden `\linewidth`.
   - Fórmulas en línea largas con `\left` envueltas fuera de `$...$` con `\ajm{...}` (`0.98\linewidth`), resolviendo los vectores 20D de `jacobi_20x20_10000`.
   - Tablas cortas (`tabular`): `\footnotesize`, `\tabcolsep=4pt` y `\resizebox{\ifdim\width>\linewidth\linewidth\else\width\fi}{!}{...}`.
   - Tablas largas (`longtable` > 30 filas): apaisado (`pdflscape`) si `>= 8` columnas, tipo de columna `C{...}` (`array` + `graphicx`) y tamaños `\footnotesize`/`\scriptsize`/`\tiny` según anchura.
4. **Escape en una sola pasada:** `escaparTextoLatex` reemplaza `\`, `{`, `}`, `&`, `$`, `%`, `#`, `_`, `^`, `~` y símbolos Unicode en un único `replace(RE_ESCAPE_LATEX, ...)`, emitiendo `\textbackslash{}` sin llaves espurias `\textbackslash\{\}`.

### B. CSV (`619898b`, ajustes finales en `6b608cc` y commit posterior)
- **Prioridad alta — inyección con espacios/controles iniciales:** `PREFIJO_FORMULA = /^(?:[\t\r]|[\s\p{Z}\p{Cc}\uFEFF]*[=+\-@])/u` protege celdas, cabeceras y títulos con `LF`, espacio, `\t`, `\r`, `\v`, `NBSP (U+00A0)`, `U+2003`, `U+3000` o `BOM (U+FEFF)` antes de `= + - @`, conservando el texto original intacto.
- **Punto 5 (`1/0`, `1/000`):** `FRACCION_EXACTA = /^-?\d+\/0*[1-9]\d*$/` exige denominador `q != 0`; `1/0` y `1/000` van como texto normal y `-1/0` se prefija con `'`.
- **Punto 6 (enteros > 15 cifras significativas):** `ENTERO_LARGO = /^[+-]?0*[1-9]\d{15,}$/` ignora ceros iniciales (`000123456789012345` sigue numérico con 15 cifras; `0001234567890123456` y `9007199254740993123456789` van como `="n"` en celdas y cabeceras) sin afectar flotantes `number` de `biseccion_1000` ni decimales largos.
- **Punto 7 (cero en cualquier forma):** `CERO_NUMERICO` exporta `-0`, `-0.0`, `-0.00`, `-0e8`, `0e8`, `-0.0e-5` como `0` numérico sin signo ni notación exponencial.
- **Puntos 8 y 9 (racionales en cabeceras y `1/2\n`):** racionales exactos (`1/2`, `-1/2`, `-17/19`, `0003/0007`) y enteros largos en cabeceras/títulos van como `="p/q"` / `="n"` (sin apóstrofo visible en Calc y sin fecha en Gnumeric STF); `"1/2\n"` y `" 1/2 "` llevan `'` contra conversión a fecha. Nota: el importador CSV de Calc recorta el `\n` final de `"texto\n"`.

## Verificación reproducida

| Verificación | Herramienta / Alcance | Resultado |
|---|---|---|
| `node --test tests/test_*.cjs` | 15 archivos (incluye `test_exportar.cjs` 7/7 y navegador real Chrome) | **70 / 70 OK** |
| `node --test tests/exportacion_verificar.cjs` | Oráculo Node independiente de Codex 2 (sin editar) | **10 / 10 OK** |
| `CSV_EXIGIR_PENDIENTES=1 python -m unittest tests.test_exportacion_modulos` | Oráculo Python independiente de Codex 2 (sin editar) | **23 / 23 OK** (`skipped=1` `pdflatex`) |
| `tests/test_recursos_version.py` + `tests/test_golden_api.py` | Hash `exportar.js?v=a0a3d589eec5` y 43 respuestas congeladas | **3 / 3 OK** |
| `pdflatex 1.40.29` (TinyTeX 2026), doble pasada `-no-shell-escape` | 36 procedimientos reales (incl. `jacobi_20x20_10000` 143 pág., `biseccion_1000`, `regla_falsa_1000`) + `especiales_utf8` | **37 / 37 OK** (`0.00 pt` Overfull hbox/vbox, 0 `Missing character`) |
| `test_externo_csv.py` (`P2_EXPORTAR_JS`) | Gnumeric `1.12.62` (STF) + LibreOffice Calc `26.2.4` (`especiales=false` y `especiales=true`), 35 libros × importado/guardado/reabierto | **5 / 5 OK** (0 errores) |

## Commits de la rama (`60c6d0c..HEAD`)
- `0e7a461` `fix(test): evitar auto-de-elevacion de Chrome y Edge en Windows en test_p2_browser` (`+15/-5`)
- `872b2a5` `docs(validacion): diagnosticar auto-de-elevacion de Chrome y Edge en Windows local` (`+58`)
- `619898b` `fix(exportar): endurecer CSV contra inyeccion con espacios, 1/0, enteros largos, -0 y racionales en cabeceras` (`+38/-8`)
- `6b608cc` `fix(exportar): ajustar LaTeX (MaxMatrixCols, babel %, 1 pasada, ancho) y limitar enteros largos a cadenas` (`+63/-19`)
