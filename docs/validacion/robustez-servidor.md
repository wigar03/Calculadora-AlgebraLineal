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

## Validación final y empaquetado

- `python -m unittest discover tests -v`: **435 pruebas OK**, 30.569 s; 14 pruebas nuevas de este trabajo.
- Cada `tests/*.cjs` con `node --test`: **58 pruebas OK**.
- `python -m unittest tests.test_golden_api`: **43 respuestas congeladas intactas** (una prueba con subcasos).
- `git diff a642912 --check`: sin errores. Cada commit respeta el máximo de 100 líneas añadidas + eliminadas.
- Primero se reprodujeron los fallos HTTP y la ausencia de supervisor; después se implementaron las correcciones.
  Una comprobación intermedia detectó fracciones no serializables; `8e8e5a3` restauró el formato original.

En Orca Browser se comprobaron los scripts locales, 348 fórmulas KaTeX, Outfit cargada, cero recursos externos
y cero errores de consola. La navegación y el botón existente de suma funcionaron: (2,-3,4)+(5,1,-2)=(7,-2,2).
La CSP admite los manejadores y estilos inline que ya utiliza la página, sin autorizar orígenes externos.

PyInstaller 6.22.3 compiló dos veces con `packaging/calculadora.spec`, usando `.venv-release` existente.
El primer ejecutable pasó `--diagnostico`: salida 0, `ok=true`, 11 módulos, 346 fórmulas, KaTeX/fuentes disponibles,
cero recursos externos y raíz de Newton 1.5213797068045751. Tras los cambios finales de trazas/cierre/JSON,
la recompilación fue correcta, pero Windows impidió iniciar el nuevo binario con el mensaje literal:

> An Application Control policy has blocked this file.

El código fuente final sí pasó `desktop.py --diagnostico` mediante `.venv-release`, con los mismos resultados.
No se cambió ni eludió Application Control. El coordinador aceptó esta entrega y fijó como criterio definitivo
la CI de Windows: `scripts/test_windows_package.ps1` sobre versión portable, instalada y reinstalada al integrar.
El diagnóstico definitivo del binario final queda pendiente de esa CI; la ruta POSIX de RLIMIT_AS también
queda para CI de Linux (este equipo no tiene WSL). No se modifica versión, no se publica ni se fusiona main.

Los JSON y logs locales de comprobación están en `%TEMP%/robustez-servidor-*`; no son artefactos de release.
La evidencia de commits siguiente incluye las dependencias prestadas, que el integrador ya conoce en main
o en la rama de motores; evita aplicar dos veces esos cambios al integrar.

## Commits de implementación y pruebas

Líneas = añadidas + eliminadas; los commits de esta evidencia se identifican con `git log` de la rama.

| Hash | Mensaje | Líneas |
|---|---|---:|
| 43dff49 | test(servidor): reproducir fallos de aislamiento y entrada HTTP | 85 |
| 3a4b5ef | feat(ejecucion): definir protocolo acotado y errores controlados | 83 |
| 696a853 | feat(ejecucion): limitar memoria con Job Object en Windows | 41 |
| 8ee2ae3 | feat(ejecucion): supervisar procesos spawn persistentes | 59 |
| 199720e | feat(ejecucion): cancelar reemplazar y acotar tareas aisladas | 49 |
| 2d8d06c | refactor(servidor): separar calculo y adjuntar procedimiento una vez | 68 |
| 98239e7 | test(servidor): exigir aislamiento HTTP y cabeceras seguras | 45 |
| 499878f | fix(servidor): limitar lectura y restringir acceso al origen local | 69 |
| 8e8e5a3 | fix(ejecucion): conservar fracciones en la salida JSON | 2 |
| 346ac41 | test(servidor): exigir limites antes de invocar cada motor | 27 |
| 1c7902e | feat(servidor): validar literales antes de construir fracciones | 45 |
| ce47f21 | feat(servidor): aplicar limites comunes al inicio de cada ruta | 59 |
| 0e0143c | test(servidor): comprobar concurrencia durante calculo aislado | 33 |
| 4cf394e | feat(servidor): aislar calculos y habilitar spawn empaquetado | 19 |
| c03ea82 | test(servidor): inyectar fallo en frontera del supervisor | 2 |
| e8542bb | fix(robustez): admitir todo el rango de los dobles en el exponente (0f1d59b) | 4 |
| a2a72b4 | feat(robustez): limitar la expansion por cofactores a orden seis (070e5b2) | 1 |
| 4409a90 | fix(servidor): conservar diagnosticos y anticipar coste de cofactores | 21 |
| 89f0891 | test(ejecucion): exigir cierre activo y registro de fallos remotos | 31 |
| da81e77 | fix(ejecucion): registrar trazas remotas y sincronizar cierre | 18 |
| e241efc | fix(ejecucion): retirar cada proceso una sola vez al cerrar | 16 |
| 11e819b | test(servidor): verificar cancelacion HTTP y procedimiento unico | 29 |
| ee22335 | test(servidor): cubrir JSON no estandar y anidamiento hostil | 9 |
| 6ff2552 | fix(servidor): rechazar constantes y JSON demasiado anidado | 9 |
| ff2d3bc | test(lineal): verificar subindices largos sin superar limites de entrada (403a8d5) | 13 |
| 166d9e8 | docs(robustez): registrar mediciones y casos adversos del servidor | 67 |
