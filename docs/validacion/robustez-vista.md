# Validación — Área `robustez-vista` (Etapa 3 / P1 + base P2)

Rama: `orca/robustez-vista` (desde `main` `5bbdb7e`). Entorno: Windows 11, Python 3.12, Node.js v26.13.0.

## Alcance entregado
1. **Adaptadores numéricos** (`src/procedimientos/numerico.py`): 7 rutas registradas con `@registrar` (`/api/biseccion/resolver`, `/api/regla-falsa/resolver`, `/api/newton-raphson/resolver`, `/api/secante/resolver`, `/api/derivadas/derivar`, `/api/iterativos/resolver`, `/api/iterativos/comparar`), funciones puras sin recálculo, tablas completas sin redondear y verificación equivalente a cada vista.
2. **Seguridad de la vista** (`src/ui/web/app.js`): sustitución de los 6 bloques `innerHTML` con `<p>${err.message}</p>` por `mostrarErrorResultado()` basado en `textContent` con estructura DOM, clases y estilos idénticos. Verificación estática de que ningún otro JS propio usa `innerHTML`/`outerHTML`/`insertAdjacentHTML`.
3. **Base de exportación P2 sin cargar** (`src/ui/web/exportar.js`): `procedimientoALatex(p)`, `tablaALatex(t)`, `tablaACSV(t, {separador, decimal})` (RFC 4180 + Excel ES) y `textoPlano(p)`. No se modificó `index.html` ni ningún CSS.

## Mediciones antes / después

| Indicador | Antes (`main` `5bbdb7e`) | Después (`orca/robustez-vista`) |
|---|---|---|
| Inserciones `innerHTML` con `err.message` en `app.js` | 6 (inyecta `<img onerror=...>` como HTML) | 0 (100 % `textContent`, texto plano) |
| Adaptadores numéricos registrados (`ADAPTADORES`) | 0 / 7 | 7 / 7 (9 casos golden válidos + KaTeX estricto) |
| `tests/test_golden_api.py` (43 respuestas congeladas) | 1 / 1 OK | 1 / 1 OK (0.158 s) |
| Pruebas Python (`unittest discover tests`) | 421 / 421 OK | 423 / 424 OK (1 fallo esperado por `?v=` de `app.js`) |
| Pruebas Node (`tests/*.cjs`) | 58 / 58 OK (10 archivos) | 65 / 65 OK (12 archivos) |

> Nota sobre `?v=`: conforme a las reglas, no se tocó `index.html`. El integrador debe actualizar `app.js?v=c6c606a23f95` (antes `2ee884e695c6`) al fusionar.

## Tiempos de adaptadores numéricos (corpus golden)

| Ruta | Tiempo | Tablas | Filas | KaTeX estricto |
|---|---:|---:|---|---|
| `/api/biseccion/resolver` (intervalo) | 0.084 ms | 1 | `[21]` | OK |
| `/api/biseccion/resolver` (residuo) | 0.050 ms | 1 | `[19]` | OK |
| `/api/regla-falsa/resolver` | 0.067 ms | 1 | `[6]` | OK |
| `/api/newton-raphson/resolver` | 0.098 ms | 1 | `[4]` | OK |
| `/api/secante/resolver` | 0.087 ms | 1 | `[4]` | OK |
| `/api/derivadas/derivar` | 0.020 ms | 0 | `[]` | OK |
| `/api/iterativos/resolver` (Jacobi) | 0.304 ms | 1 | `[18]` | OK |
| `/api/iterativos/resolver` (Gauss-Seidel) | 0.129 ms | 1 | `[8]` | OK |
| `/api/iterativos/comparar` | 0.170 ms | 2 | `[18, 8]` | OK |

## Casos adversos probados

| Caso adverso | Entrada | Respuesta / resultado observado | Tiempo |
|---|---|---|---:|
| XSS en error del servidor (6 vistas de `app.js`) | `{"error": "<img src=x onerror=\"alert(1)\"><script>xss()</script>&<b>texto</b>"}` | Antes: `innerHTML` inyectaba `<img ...>`. Después: `<p>.textContent` literal, 0 etiquetas inyectadas | 7.67 ms |
| Bisección hasta agotamiento de precisión | `x^2 - 2`, `[1, 2]`, `tol=1e-300`, `max=1000` | `motivo="precision_agotada"`, procedimiento válido, 53 filas sin redondeo | 0.56 ms |
| Sistema singular en iterativos | `A=[[1,2],[2,4]]`, `b=[3,6]`, Jacobi | `motivo="singular"`, procedimiento válido, tabla con 0 filas, KaTeX estricto OK | 2.87 ms |
| Regla falsa con estancamiento | `x^10 - 1`, `[0, 1.3]`, `max=20` | Procedimiento válido, aviso de estancamiento con `$x_l$`/`$x_u$`, 20 filas | < 1 ms |
| CSV RFC 4180 Excel ES (1000 filas) | 1000 filas con `;`, `"`, decimales y `1e-7` | 59 740 bytes, comillas duplicadas `""`, coma decimal `,`, CRLF `\r\n` | 2.59 ms |
| LaTeX tabla + caracteres especiales (1000 filas) | 1000 filas con `_`, `%`, `#`, `&`, `←`, `✓`, `≈` | 82 989 bytes, escapes `\_`, `\%`, `\#`, `\&`, `$\leftarrow$`, compilable con `pdflatex` | 3.38 ms |

## Commits de la rama (`main..HEAD`)

| Hash | Mensaje | Líneas (`+`/`-`) |
|---|---|---:|
| `eb067fb` | `test(ui): exigir escape seguro de errores HTML en la vista` | 80 (`+80/-0`) |
| `0713e09` | `fix(ui): insertar mensajes de error con textContent en app.js` | 58 (`+22/-36`) |
| `983442a` | `test(procedimientos): añadir pruebas de adaptadores numéricos y KaTeX` | 91 (`+91/-0`) |
| `e4fba10` | `feat(procedimientos): añadir base y adaptadores de bisección y derivadas` | 100 (`+100/-0`) |
| `f1d99e3` | `feat(procedimientos): añadir adaptador de regla falsa y verificación abierta` | 77 (`+77/-0`) |
| `46fad12` | `feat(procedimientos): añadir adaptadores de Newton-Raphson y secante` | 76 (`+76/-0`) |
| `968fc31` | `feat(procedimientos): añadir adaptadores de métodos iterativos` | 98 (`+98/-0`) |
| `25e3c21` | `test(procedimientos): añadir casos borde y no convergencia numéricos` | 21 (`+21/-0`) |
| `18e35a4` | `test(exportar): añadir pruebas de exportación LaTeX, CSV y texto plano` | 96 (`+96/-0`) |
| `4c3e123` | `feat(exportar): añadir tablaACSV (RFC 4180) y textoPlano en exportar.js` | 91 (`+91/-0`) |
| `b53055b` | `feat(exportar): añadir tablaALatex y procedimientoALatex compilables` | 89 (`+88/-1`) |
