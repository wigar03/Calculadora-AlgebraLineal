# Contrato de la etapa 3 (P1): robustez, límites, errores y seguridad

Autor: integrador (Claude Business). Cambios solo mediante el integrador. Regla absoluta: las 43 respuestas de
`tests/validacion/golden/` siguen idénticas (`tests/test_golden_api.py`); solo se admiten claves nuevas de primer nivel.

## 1. Ejecución aislada y cancelable (`src/core/ejecucion.py`, Codex 2)
- Un hilo del servidor nunca ejecuta un cálculo costoso: lo envía a un **proceso trabajador** supervisado
  (multiprocessing `spawn`, compatible con PyInstaller mediante `freeze_support()` en `desktop.py` y `main.py`).
- Tiempo máximo por operación (por defecto 10 s, configurable por ruta). Al vencer, el supervisor **termina el
  proceso**, lo reemplaza y responde 503 con `tipo = "tiempo"`. Ninguna otra petición espera a ese cálculo.
- Memoria: Windows, Job Object con `JOB_OBJECT_LIMIT_PROCESS_MEMORY` (ctypes); POSIX, `resource.RLIMIT_AS`.
  Por defecto 512 MB. Superarla equivale a fallo controlado (`tipo = "limite"`), nunca a caída del servidor.
- Salida: si la respuesta serializada supera 4 MB, se rechaza con `tipo = "limite"` (no se envían respuestas enormes).
- Rutas baratas (vista previa, muestreos pequeños, texto) pueden ejecutarse en el hilo tras la validación previa.
- Coste previo: cada ruta costosa valida dimensiones y estima el coste **antes** de crear trabajo.

## 2. Límites (`src/core/limites.py`, Codex 2; los motores los reutilizan, Codex 1)
| Ruta | Límite |
|---|---|
| vectores | n ≤ 20 · combinación: n ≤ 15, k ≤ 10 |
| matrices (operar) | filas y columnas ≤ 8 |
| inversa | 1 ≤ n ≤ 6 |
| ecuaciones | m, n ≤ 10 |
| determinante | n ≤ 8; cofactores solo si el coste estimado cabe en el presupuesto (Codex 1 mide y fija el corte; para n ≤ 5 nada cambia) |
| eficiencia-determinante | n ≤ 100, números grandes en notación científica (sin error de 4300 dígitos) |
| raíces | f ≤ 500 caracteres, iteraciones ≤ 1000, puntos ≤ 2000 (ya existentes) |
| iterativos | n ≤ 20, iteraciones ≤ 10 000 (ya existentes) |
| celdas numéricas | ≤ 64 dígitos por entero y exponente |e| ≤ 300, comprobados ANTES de construir `Fraction` |
| cuerpo HTTP | ≤ 256 KB (413) · lectura del socket con tiempo máximo de 10 s |

Los límites de la API coinciden con los de la interfaz: nada de lo que hoy hace la UI deja de funcionar.

## 3. Errores (formato único)
`{"error": "<mensaje en español>", "tipo": "entrada"|"dominio"|"limite"|"tiempo"|"interno", "codigo": "<id>"}`.
HTTP: 400 entrada/dominio/limite, 413 cuerpo grande, 503 tiempo, 500 interno. El mensaje interno nunca incluye
texto de Python (`'list' object…`, `invalid literal…`): se registra en el log y el usuario recibe un texto
genérico. JSON inválido → 400 «El cuerpo de la petición no es JSON válido»; cuerpo que no es objeto → 400.
Las claves existentes `error` y los códigos 400/404 actuales se conservan.

## 4. Seguridad del servidor
- Sin `Access-Control-Allow-Origin` (la página y la API comparten origen). POST con `Origin` ajeno → 403.
- `Host` debe ser `127.0.0.1:<puerto>` o `localhost:<puerto>` (protección contra DNS rebinding) → 403 si no.
- Sin listado de directorios (404). Cabeceras: `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`,
  `Content-Security-Policy` compatible con la página actual (scripts y estilos propios, sin orígenes externos),
  `Cache-Control: no-cache` en HTML y JSON.
- La interfaz inserta mensajes de error con `textContent` o escape HTML (sin `innerHTML` con texto del servidor).

## 5. Pruebas obligatorias (cada responsable las suyas; el integrador repite las adversarias)
Concurrencia (una petición costosa no bloquea otra), cancelación por tiempo con proceso terminado, memoria,
salida máxima, cuerpo grande, socket lento, JSON inválido, `Host`/`Origin` ajenos, listado, cabeceras, límites
de cada ruta, números enormes, `?v=` y golden. Mediciones de rendimiento antes y después en `docs/validacion/`.
