# Validación — Área `p2-ui` (Etapa 4 / P2 Exportar e Imprimir)

Rama: `orca/p2-ui` (desde `main` `d8131ba`). Entorno: Windows 11, Python 3.12, Node.js v26.13.0, Chrome headless (CDP).

## Alcance entregado
1. **Componente único reutilizable** (`src/ui/web/exportar-ui.js`): inyecta un botón «Exportar» (`btn-clear` + iconos lucide) y menú («Copiar LaTeX», «Exportar CSV» solo con tablas, «Imprimir o guardar como PDF») en las cabeceras de los 11 módulos (excluido `tab-inicio`). API mínima `ExportarUI.registrar(id, resp)` y `ExportarUI.limpiar(id)`. Deshabilitado (`disabled` y `aria-disabled`) sin resultado, tras error, al limpiar o al modificar entradas. Teclado (Enter/Espacio, flechas, Home/End, Escape con devolución de foco), `aria-haspopup`/`aria-expanded`/`role="menu"`/`menuitem`, confirmación «Copiado» en `aria-live="polite"`. Móvil (`<= 680 px`): ancho completo bajo la descripción, áreas táctiles `>= 44 px`, sin desbordamiento.
2. **Exportación CSV y LaTeX** (`src/ui/web/exportar.js`): CSV UTF-8 con BOM (`\uFEFF`), `;`, coma decimal, CRLF, RFC 4180 + espacios extremos entrecomillados, precisión completa y científica `1,5E-07`, fracciones exactas `^-?\d+/\d+$` como `="p/q"` (`"=""p/q"""`), prefijo `'` contra inyección (`=`, `+`, `-`, `@`, `\t`, `\r`), y `tablasACSV` para todas las filas de todas las tablas. LaTeX compilable con `\usepackage[spanish]{babel}`, `amsmath,amssymb`, `longtable` (tablas > 30 filas) y símbolos Unicode completos.
3. **Impresión / PDF** (`src/ui/web/impresion.css`, `media="print"`): imprime solo el módulo activo en papel blanco; oculta barra lateral, cabecera, controles, teclados y botones; `thead` `table-header-group`, `break-inside: avoid` en filas/fórmulas/matrices/gráficas; KaTeX vectorial sin alterar pantalla.
4. **Carga y subtítulo** (`src/ui/web/index.html`): carga `impresion.css`, `exportar.js`, `exportar-ui.js` y actualiza el subtítulo aprobado «Álgebra lineal y métodos numéricos con procedimientos paso a paso». `HUELLA_SIN_MODULO_11` en `tests/test_iterativos_ui.cjs` se mantiene intacta tras normalizar únicamente esas 4 líneas autorizadas.
5. **Conexión de los 11 módulos**: llamadas de una línea en `app.js` (6 lineales), `biseccion.js`, `regla-falsa.js`, `newton-raphson.js`, `secante.js` e `iterativos.js`.

## Mediciones antes / después

| Indicador | Antes (`main` `d8131ba`) | Después (`orca/p2-ui`) |
|---|---|---|
| Módulos con botón «Exportar» reutilizable | 0 / 11 | 11 / 11 (0 en `tab-inicio`) |
| `tests/test_golden_api.py` (43 respuestas congeladas) | 1 / 1 OK | 1 / 1 OK |
| `tests/test_recursos_offline.py` (0 peticiones externas) | 2 / 2 OK | 2 / 2 OK |
| Pruebas Python (`unittest discover tests`) | 457 / 457 OK | 456 / 457 OK (1 test con 6 subfallos esperados de `?v=`) |
| Pruebas Node (`tests/*.cjs`) | 66 / 66 (13 archivos) | 68 / 68 (15 archivos, incluye navegador real) |
| Desbordamiento horizontal móvil (390 px, menú abierto) | N/A | 0 px (`scrollWidth == clientWidth`, botón `>= 44 px`, ítems `53.9 px`) |

> Nota `?v=` para el integrador (no se tocaron los `?v=` existentes): actualizar `app.js?v=af40e286ed7e`, `biseccion.js?v=1fc78816cd53`, `regla-falsa.js?v=743cb5307335`, `newton-raphson.js?v=fae04e17fb73`, `secante.js?v=2fd3642db817` e `iterativos.js?v=bd6c5a95a4ba`. Los 3 recursos nuevos ya llevan su SHA-256 real (`impresion.css?v=698245902f23`, `exportar.js?v=3588dae8aa3f`, `exportar-ui.js?v=8665d7db6b6a`).

## Verificación cruzada contra batería independiente de Codex 2 (`orca/p2-verificacion`)
Ejecutada en rama temporal con `78ee467` (`RESPUESTA_MAX_BYTES = 16 MB`) y los 8 commits de `orca/p2-verificacion` (`a0eacbc..4a6a748`):
- `node --test tests/exportacion_verificar.cjs`: **6 / 6 OK** (89 ms) — BOM, oráculo KaTeX, inyección en cabeceras/celdas, fracciones validadas, rechazo explícito de `NaN`/`Infinity`, preservación de `-0.0`.
- `python -m unittest tests.test_exportacion_modulos -v`: **9 / 9 OK, 1 skipped** (`pdflatex` no instalado) en **9.05 s** — 43 golden + Jacobi 20×20 10 000 iteraciones + Bisección 1000 + Regla Falsa 1000 + caso adversario (`\input{ajeno}`, Unicode, fila nula final, precisión `float.hex()`/`Decimal`, `longtable` con conteo exacto de `\\`, tiempo y memoria dentro de límites).

## Casos adversos y rendimiento

| Caso probado | Entrada | Resultado observado | Tiempo |
|---|---|---|---:|
| Navegador real (11 módulos + impresión + 390 px + offline) | Ejercicios reales en los 11 módulos en Chrome CDP | 11/11 LaTeX compilable + «Copiado», 5/5 CSV con bytes BOM `EF BB BF` + `;` + CRLF, impresión limpia, 0 px overflow a 390 px, 0 peticiones externas, 0 excepciones JS | 3.62 s |
| 33 procedimientos golden en `procedimientoALatex` | Corpus completo `tests/validacion/golden/*.json` | 33/33 entornos `\begin`/`\end` equilibrados y KaTeX `strict: 'error'` en todos los bloques y fragmentos inline | 270.7 ms |
| Inyección de fórmulas y fracciones CSV | `=SUM(A1:A5)`, `+cmd\|calc`, `-2+3`, `@SUM(1,2)`, `\t=1`, `\r=2`, `1/2+A1`, `-12.75`, `5/2`, `-3/4` | Cabeceras y fórmulas prefijadas con `'`; `5/2` y `-3/4` como `"=""5/2"""` y `"=""-3/4"""`; `-12.75` como `-12,75`; `1/2+A1` sin envolver en `="..."` | 0.12 ms |
| Tabla larga Jacobi (10 000 iteraciones) — CSV | 10 000 filas con decimales, científica y `181/60` | 755 286 bytes, 10 000 filas completas sin truncar, BOM UTF-8, `;`, coma decimal, CRLF | 22.86 ms |
| Tabla larga Jacobi (10 000 iteraciones) — LaTeX | 10 000 filas | 985 487 bytes con `\begin{longtable}` y encabezados repetidos | 21.58 ms |
| Error dimensional en `tab-matrices` + edición de entrada | Suma en matrices 2×3 y 3×2; luego edición en `.card-input` | Exportar permanece/vuelve a `disabled` y `aria-disabled="true"` | < 10 ms |

## Capturas en navegador real
- Escritorio (menú Exportar abierto y subtítulo aprobado): `docs/validacion/p2-ui/escritorio-menu.png`
- Impresión emulada (`media="print"`, solo módulo activo, sin barra lateral ni botones): `docs/validacion/p2-ui/impresion-emulada.png`
- Móvil 390 px (botón a todo el ancho bajo la descripción, menú en línea, 0 px desbordamiento): `docs/validacion/p2-ui/movil-390-menu.png`

## Commits de la rama (`main..HEAD`)

| Hash | Mensaje | Líneas (`+`/`-`) |
|---|---|---:|
| `d3f781e` | `test(exportar): exigir contrato CSV y LaTeX P2 en exportar.js` | 94 (`+47/-47`) |
| `75c828e` | `test(exportar): añadir pruebas del componente exportar-ui` | 95 (`+95/-0`) |
| `f48260b` | `feat(impresion): añadir hoja de estilos media=print en impresion.css` | 88 (`+88/-0`) |
| `7ca5d8a` | `feat(exportar): crear base y estilos del componente exportar-ui.js` | 75 (`+75/-0`) |
| `3addea9` | `feat(exportar): ajustar CSV al contrato P2 (BOM, ;, fracciones e inyección)` | 75 (`+54/-21`) |
| `f82a417` | `feat(exportar): añadir gestión de estado y acciones en exportar-ui.js` | 93 (`+92/-1`) |
| `f0e77a6` | `feat(exportar): añadir babel spanish y longtable en exportar.js` | 43 (`+32/-11`) |
| `0f62e6b` | `feat(exportar): montar componente en 11 módulos con teclado y ARIA` | 66 (`+65/-1`) |
| `e32fa97` | `feat(ui): cargar P2 y actualizar subtítulo aprobado en index.html` | 16 (`+13/-3`) |
| `8198627` | `feat(ui): conectar exportar-ui en los 6 módulos lineales de app.js` | 25 (`+25/-0`) |
| `22d8747` | `feat(ui): conectar exportar-ui en los 5 módulos numéricos` | 21 (`+16/-5`) |
| `2275f02` | `fix(ui): ajustar transición táctil móvil en exportar-ui e impresión de steppers` | 10 (`+6/-4`) |
| `cedcaaa` | `test(exportar): añadir prueba en navegador real para 11 módulos, impresión y móvil` | 92 (`+92/-0`) |
| `28c552c` | `docs(validacion): registrar evidencia, capturas y mediciones de p2-ui` | 57 (`+57/-0`) |
| `78fbd3b` | `test(exportar): cubrir -0.0, no finitos, fila nula, longtable y etiquetas adversarias` | 11 (`+9/-2`) |
| `0b77034` | `fix(exportar): preservar -0, rechazar no finitos, fila nula, longtable y escape adversario` | 43 (`+29/-14`) |
