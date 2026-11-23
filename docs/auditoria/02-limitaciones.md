# Auditoría 2/4 — Problemas y limitaciones verificados

Severidad: **A** = puede bloquear o engañar al usuario; **M** = calidad o mantenimiento; **B** = menor.
Todas las mediciones se hicieron en esta máquina con `servidor_local()` y HTTP real.

## Problemas del producto (no requieren decisión de UX)
| ID | Sev. | Problema | Evidencia |
|---|---|---|---|
| AU-01 | A | Cofactores sin límite en la API: el tiempo crece como n! | n = 8: 0.62 s y 12.7 MB (integrador); n = 10: 56 s y 1.35 GB |
| AU-02 | A | Servidor de un solo hilo y sin tiempos de espera: un cálculo largo o un socket incompleto congela la app | `HTTPServer` en `web_server.py:628,641`; otra petición agotó 15 s |
| AU-03 | A | Los límites de la UI (n ≤ 8, ≤ 10…) no se validan en Python | inversa n = 30: 3 s y 32 MB; sistema 40×40: 4.5 s y 51 MB |
| AU-04 | M | JSON inválido se convierte en `{}` y produce mensajes engañosos | `except Exception: body = {}` en `web_server.py:95`; `{no json` da «Operación vectorial desconocida: ''» |
| AU-05 | M | Se filtran textos de Python sin traducir | `'list' object has no attribute 'get'`, `invalid literal for int()`, `Exceeds the limit (4300 digits)` |
| AU-06 | M | `?v=` de 10 de 13 recursos desactualizados y sin `Cache-Control`: la app de escritorio puede usar JS viejo | `tests/test_recursos_version.py`; **se corrige en esta etapa** |
| AU-07 | M | Errores mostrados con `innerHTML` sin escapar (autoinyección de HTML) | `app.js:411,1410` y otros 4: `<p>${err.message}</p>`; el servidor repite la entrada |
| AU-08 | B | `Fraction("1e5000000")` construye un entero enorme antes de fallar (2.5 s de CPU) | sondeo HTTP |
| AU-09 | B | Listado de directorios en estáticos y CORS `*` (solo afecta a 127.0.0.1) | `GET /vendor/` = 200; `Access-Control-Allow-Origin: *` |
| AU-10 | B | Respuestas enormes: cada paso serializa la matriz completa | LU 60×60: 11.5 MB |

## Limitaciones académicas (funciones ausentes)
1. Álgebra lineal solo con racionales: `sqrt(2)`, `pi` y `e` no se aceptan en celdas.
2. Sin valores ni vectores propios, LU/QR/Cholesky como módulo, normas matriciales ni número de condición.
3. Sin rango, núcleo, espacio columna, independencia ni base como operaciones propias.
4. Vectores sin norma, ángulo, proyección, producto cruzado ni Gram-Schmidt.
5. Métodos numéricos de una sola variable `x`: sin sistemas no lineales, EDO, interpolación, integración ni
   diferenciación numérica.
6. Derivada solo de primer orden, sin simplificar y sin pasos.
7. Sin exportar, imprimir ni copiar el procedimiento; sin historial (recargar borra todo).
8. Cofactores mostrados como bloque de texto (3 pasos para una 4×4).
9. Pivote elegido siempre por máximo |a|: con [[1,2],[3,4]] el primer paso intercambia F1 y F2, y el estudiante
   no reproduce a mano el procedimiento mostrado.
10. Sin visualización en los módulos de álgebra lineal.

## Arquitectura (resumen; detalle en `04-arquitectura.md`)
- `web_server.py` enruta con una cadena de `if/elif` e importa más de 20 símbolos; cada módulo nuevo lo modifica.
- No hay un formato común de procedimiento: `Step`, `PasoDeterminante`, listas de cadenas y dicts usan nombres
  distintos (`step_number`/`numero`, `matrix_state`/`matriz_estado`). Exportar o guardar historial exige adaptadores.
- Duplicaciones: dos `dominio.py` con funciones distintas, `OPERACIONES` repetido y tres copias de
  `formatear`/`numeroLatex` en JS.
- `app.js` tiene 2143 líneas con seis módulos y 75 manejadores en línea en `index.html`.
- `src/solver/anterior_programa.py` contiene funciones muertas con rutas fijas de otra máquina; solo se usa su envoltorio.
- CI solo en Windows; sin linters, cobertura ni pruebas de carga o seguridad del servidor.
