# Compilación LaTeX real y rendimiento de respuestas grandes

Fecha: 2026-11-23. Rama: `orca/consolidacion-latex-rendimiento`, base `60c6d0c`.
Entorno: Windows 11 10.0.26200, Python 3.12.10, Node 26.13.0, AMD64 Family 25 Model 80.
Biblioteca inicial: `src/ui/web/exportar.js`, SHA-256 `3ef92d0bb4fc0e5b65842d765d5dce1029ff4e4a1bf88951537fcb7b95a474fc`.
No se modificaron archivos de producción, golden, UX, límites ni referencias matemáticas.

## Herramientas y reproducción

Se extrajo TinyTeX Windows v2026.11 mediante 7zr en `%TEMP%/orca-latex-rendimiento-9r1w7eur`.
Se actualizó su gestor y se añadió `babel-spanish`, siempre dentro de esa carpeta temporal.
Motor: pdfTeX 3.141592653-2.6-1.40.29, TeX Live 2026; sin instalación de sistema ni privilegios.
También se extrajo Chrome for Testing 158.0.8127.88 en la misma carpeta temporal.
Los navegadores instalados terminaban con código 0 antes de abrir CDP; Chrome portátil pasó el flujo real.

```powershell
$texBin = "$env:TEMP\orca-latex-rendimiento-9r1w7eur\portable\TinyTeX\bin\windows"
$env:PATH = "$texBin;$env:PATH"
$env:REQUIERE_EXTERNOS = '1'
$env:P2_LATEX_ARTEFACTOS = "$env:TEMP\orca-latex-rendimiento-9r1w7eur\artefactos-base"
python -m unittest tests.test_externo_latex -v
python scripts/medir_robustez.py --concurrencia-grande
python scripts/medir_exportaciones.py
```

Las pruebas externas consultan 43 respuestas golden y tres límites reales por HTTP, sin mocks.
Se exportan vía Node los 33 procedimientos golden de los 11 módulos y tres casos largos:
Jacobi 20×20 con 10 000 filas, bisección con 1000 y regla falsa con 1000.
Se añade un adversario con matrices, acentos UTF-8 y `% & _ # { } ~ ^ \` en todos los campos textuales.
Cada documento se compila con `-no-shell-escape -halt-on-error -interaction=nonstopmode -file-line-error`.
Se exigen dos pasadas, PDF real, ausencia de caracteres perdidos y más de una página en tablas largas.
El integrador fijó el máximo de `Overfull hbox` en **1 pt**; `vbox` grave significa más de 10 pt.
Cada fuente, PDF y log de ambas pasadas queda en `P2_LATEX_ARTEFACTOS` si se configura.
Sin `pdflatex`/Node, se omite con motivo; con `REQUIERE_EXTERNOS=1`, falla la preparación de la clase.
Ambos modos se comprobaron vaciando PATH en un subproceso: omisión explícita frente a error explícito.

## Defectos iniciales reproducidos, pendientes de Antigravity

| Documento | Resultado observado con exportar.js inicial |
|---|---|
| `jacobi_20x20_10000` | Aborta: `Extra alignment tab has been changed to cr`, entrada A, línea 11 |
| `regla_falsa[3]`, `regla_falsa_1000` | Abortan: `Incompatible glue units`, porcentaje precedido de espacio matemático |
| `biseccion[0]`, `biseccion[1]` | Desbordamiento horizontal máximo 281,62985 / 270,67984 pt; 2 páginas cada uno |
| `biseccion_1000` | Desbordamiento 293,46843 pt; 25 páginas, sin truncar la tabla |
| `iterativos[0]`, `[1]`, `[2]` | Desbordamiento 670,64570 / 663,32454 / 670,64570 pt; 4 / 4 / 7 páginas |
| `newton[2]`, `secante[1]` | Desbordamiento 288,59023 / 403,40697 pt; 2 páginas cada uno |
| `ecuaciones[0]`, `[1]` | Desbordamiento 5,83472 pt; 4 / 3 páginas; excede el criterio final de 1 pt |
| Adversario UTF-8 | Compila en 2 páginas, pero barra inversa imprime llaves adicionales por doble escape |

Correcciones necesarias en `exportar.js`, asignadas por el integrador a Antigravity:

1. Elevar `MaxMatrixCols` de amsmath para admitir matrices de 20 columnas.
2. Desactivar la redefinición porcentual de Babel español sin cambiar los fragmentos de la respuesta.
3. Ajustar fórmulas/tablas al ancho conservando todas las filas, cifras y paginación.
4. Escapar texto en una sola pasada para evitar reescapar las llaves generadas por la barra inversa.

Inicialmente hubo 12 fallos con umbral 10 pt; al aplicar 1 pt se añadieron dos ecuaciones.
Por instrucción del integrador, los **14 defectos** están aislados con `expectedFailure` y motivo explícito.
La prueba restante compila los otros 23 procedimientos: resultado **15 pruebas, 14 fallos esperados, sin fallos inesperados**.
Estas marcas deben retirarse después de revalidar la biblioteca corregida con `P2_EXPORTAR_JS`.

## Cuatro respuestas Jacobi concurrentes, límite de 16 MiB

Servidor en proceso independiente del cliente; dos trabajadores persistentes originales, sin modificar P1.
Misma entrada circular de `entradas_largas()`: diagonal 1, siguiente columna -0,9999, b=1 y tolerancia 1e-300.
Cuatro POST arrancan con barrera; consultas ligeras a `/api/biseccion/preview` continúan durante la carga.
El monitor consulta cada 20 ms los máximos del SO: RSS y memoria comprometida en Windows, virtual en Linux.

| Medida | Resultado |
|---|---|
| Respuestas grandes | 4 HTTP 200; 10 332 983 bytes cada una, menos de 16 777 216; 10 000 iteraciones cada una |
| HTTP total, incluye JSON y transporte | 5,927 / 10,008 / 10,205 / 5,728 s |
| Supervisor, incluye cola y cálculo | 4,071 / 4,308 / 8,340 / 8,618 s; todos menores que los 10 s de P1 |
| 68 consultas ligeras | Todas HTTP 200; mediana 0,002 s, p95 0,304 s, máximo 0,567 s |
| RSS máximo servidor | 103,49 MiB; memoria comprometida máxima 95,96 MiB |
| Trabajadores: RSS máximo | 65,97 / 65,02 MiB |
| Trabajadores: comprometida máxima | 57,34 / 56,31 MiB; inferiores al límite de 512 MiB |
| Recuperación posterior | Suma vectorial HTTP 200 en 0,002 s; cierre limpio, sin errores de muestreo |

La cota de P1 limita el cálculo supervisado, no la latencia HTTP completa: se informa la diferencia expresamente.
La medición retorna código 0 solo con filas completas, respuestas acotadas, memoria/tiempo supervisados válidos y recuperación.

## Cuatro exportaciones Node simultáneas

Tres exportaciones Jacobi de 10 000 filas y una bisección de 1000, desde procedimientos HTTP reales.
Jacobi: 188,05 / 192,91 / 189,46 ms para LaTeX+CSV; RSS máximo 141,41 / 141,78 / 141,00 MiB.
Cada una produjo 5 563 755 bytes LaTeX y 4 544 394 bytes CSV, con las 10 000 filas y sin mutar la respuesta.
Bisección: 12,48 ms; RSS máximo 54,32 MiB; 134 994 bytes LaTeX, 77 433 bytes CSV, 1000 filas completas.
El tiempo total por proceso, incluido inicio/lectura, fue 0,329–0,336 s para Jacobi y 0,075 s para bisección.
