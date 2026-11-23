# Robustez del servidor y ejecución aislada

2026-11-23 · Windows 11 · Python 3.12.10 · rama `orca/robustez-servidor`, base `a642912`.
Solo biblioteca estándar en producción; se conserva la interfaz. Dependencias autorizadas del integrador:
`070e5b2` (COFACTORES_MAX=6), `0f1d59b` (EXPONENTE_MAX=1000) y `403a8d5` (pruebas de subíndices dentro del límite).
La única modificación propia fuera del reparto inicial es la aserción 413 de `test_iterativos_texto.py`, autorizada por Orca.

## Medición antes/después

Antes: [robustez-antes.md](robustez-antes.md). Después: `python -X utf8 scripts/medir_robustez.py`.
`-X utf8` evita que la consola cp1252 falle al imprimir «≤». Tiempos redondeados a centésimas por el script.

| Caso | HTTP antes | s antes | bytes antes | HTTP después | s después | bytes después |
|---|---:|---:|---:|---:|---:|---:|
| Cofactores n=8 | 200 | 0.65 | 12692563 | 400 | 0.02 | 129 |
| Cofactores n=9 | 200 | 5.77 | 124685561 | 400 | 0.00 | 129 |
| LU n=60 | 200 | 0.88 | 11230152 | 400 | 0.00 | 99 |
| Inversa n=30 | 200 | 2.93 | 32724007 | 400 | 0.00 | 99 |
| Ecuaciones 40x40 | 200 | 4.78 | 51483783 | 400 | 0.02 | 100 |
| Eficiencia n=5000 | 400 | 0.01 | 130 | 400 | 0.00 | 112 |
| Número 1e5000000 | 400 | 2.40 | 130 | 400 | 0.00 | 110 |
| JSON `{no json` | 400 | 0.00 | 53 | 400 | 0.00 | 111 |
| Cuerpo `[1,2]` | 400 | 0.00 | 49 | 400 | 0.00 | 115 |
| Host/Origin ajenos | 200 | 0.00 | 255 | 403 | 0.00 | 115 |
| Suma durante cofactores n=9 | 200 | 5.36 | 255 | 200 | 0.02 | 255 |
| Suma con socket lento abierto | sin respuesta | 15.01 | 0 | 200 | 0.00 | 255 |

Los casos fuera de dimensión/coste se rechazan antes de enviar trabajo; cofactores recomienda LU.
El caso n=9 del script ahora mide el rechazo temprano. La prueba de concurrencia adicional mantiene ocupado
un trabajador durante 1 s, verifica que la vista previa tarda menos de 0.5 s y recibe después el cálculo correcto.

## Coste del supervisor y decisión de rutas

Mediana de 100 llamadas por caso, motor directo frente al mismo resultado por IPC, con procesos persistentes:

| Entrada | Directo (ms) | Trabajador (ms) | Sobrecoste (ms) |
|---|---:|---:|---:|
| Suma R3 | 0.015 | 0.136 | 0.121 |
| Vista previa x^3-x-2 | 0.068 | 0.172 | 0.104 |
| Muestreo 401 puntos, [1,2] | 1.388 | 3.771 | 2.383 |
| Sistema textual 2x2 | 0.108 | 0.221 | 0.113 |

Arranque de dos procesos: 164.294 ms; primera importación del motor: 48.549 ms (fuera de las medianas).
Se aíslan todas las rutas de cálculo, incluidas derivadas, análisis y preparación de Newton. Permanecen en los
hilos únicamente las dos vistas previas, `iterativos/texto`, `biseccion/muestrear`, `regla-falsa/graficar` y
`secante/graficar`, con función/literales/puntos acotados antes de trabajar. Su tamaño limita también el coste.
El supervisor usa `spawn`, dos procesos, 512 MB por proceso y 10 s por defecto; cada instancia de HTTPServer
permite sobrescribir el plazo mediante `tiempos_calculo[ruta]`. La espera por un trabajador también tiene plazo.
La cancelación termina y recoge el proceso antes de reemplazarlo; el cierre concurrente no deja reemplazos vivos.

## Casos adversos adicionales

| Entrada/prueba | HTTP o estado | tipo / codigo | s medidos |
|---|---|---|---:|
| 262145 bytes | 413 | limite / cuerpo_grande | 0.0165 |
| `{no json` | 400 | entrada / json_invalido | 0.0010 |
| `[1,2]` | 400 | entrada / datos_invalidos | 0.0010 |
| Origin http://evil.example | 403 | entrada / origen_no_permitido | 0.0009 |
| Content-Length: 1000, un byte, Host local; lectura configurada a 0.15 s | 503 | tiempo / tiempo_lectura | 0.1629 |
| Función de 30 s, plazo de 0.1 s | 503 | tiempo / tiempo_agotado | 0.1875 |
| Reservar 256 MB con Job Object de 128 MB | 400 | limite / limite_calculo | 0.0153 |
| Cadena de 4 MB (JSON excede el máximo) | 400 | limite / respuesta_grande | 0.0076 |

Después de tiempo, memoria y salida excesiva, `os:getpid` vuelve a funcionar; tras tiempo cambia el PID y el
proceso anterior está terminado. Errores inesperados devuelven 500 genérico; la traza remota llega al log padre.
También se prueban límites de todas las rutas, enteros enormes, NaN/UTF-8/anidamiento inválidos, listado 404,
Host y Origin ajenos, cabeceras y un único `adjuntar(ruta, respuesta, cuerpo)` antes de serializar.
