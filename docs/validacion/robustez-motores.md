# Robustez de los motores lineales y sus procedimientos

Rama: `orca/robustez-motores`, desde `main` a642912; 23 de noviembre de 2026.
Entorno medido: Windows, Python 3.12.10, Node v26.13.0; matrices densas de
`scripts/medir_robustez.py:matriz`, semilla 1, enteros aleatorios de 1 a 9.
Se incorporaron las constantes aprobadas por el integrador: COFACTORES_MAX=6
(070e5b2) y EXPONENTE_MAX=1000 (0f1d59b); DIGITOS_MAX sigue siendo 64.

## Decisión y comprobación matemática

Se rechaza explícitamente cofactores para n>6 con `LimiteExcedido` y recomendación de LU.
El presupuesto elegido es 1 s y 1 MiB de salida estimada, derivado de
`RESPUESTA_MAX_BYTES // 4`; n=7 ya excedía el tamaño. Para n=6 también se estima
el coste textual antes de crear pasos: `ops_cofactores * (DIGITOS_MAX + 8*n*ancho)`,
donde ancho es la máxima longitud de una celda normalizada. Es una estimación
conservadora, no una garantía del tamaño serializado: la barrera final de 4 MiB
corresponde al supervisor del servidor. Para n<=5 el desarrollo permanece intacto.

Bareiss elimina denominadores por fila mediante mcm y opera con enteros en O(n³),
con pivoteo y signo de intercambios. LU y cofactores comparan internamente su valor
exacto con Bareiss, sin añadir ni modificar pasos. La prueba independiente suma
permutaciones con Fraction en 25 matrices racionales de órdenes 1 a 5; incluye además
pivote nulo, matriz singular y orden 8. Se verifica que una discrepancia se detecta.

## Mediciones de cofactores por HTTP

Antes: medición en esta máquina antes de modificar motores; después: rama final.
Los tiempos son de una petición local, incluyen serialización y pueden variar.

| n | Antes HTTP | Antes s | Antes bytes | Después HTTP | Después s | Después bytes |
|---|---:|---:|---:|---:|---:|---:|
| 5 | 200 | 0.02 | 28 965 | 200 | 0.018491 | 28 965 |
| 6 | 200 | 0.01 | 187 858 | 200 | 0.015546 | 187 858 |
| 7 | 200 | 0.08 | 1 453 042 | 400 | 0.000783 | 91 |
| 8 | 200 | 0.62 | 12 692 563 | 400 | 0.000641 | 91 |

La respuesta de rechazo es `{"error":"El desarrollo por cofactores admite orden hasta 6. Usa descomposición LU."}`.
Las mediciones usan el servidor de esta rama, que todavía no añade `procedimiento` ni
clasifica `tipo`; la integración del servidor es de Codex 2. El motor sí lanza
`LimiteExcedido`, que permite clasificarlo como `tipo=limite`.
Con tracemalloc (sobrecarga incluida), los motores registraron respectivamente
n=5: 0.018929 s/59 748 bytes pico; n=6: 0.113902 s/300 965 bytes;
n=7: 0.000131 s/5 490 bytes; n=8: 0.000148 s/6 184 bytes.

## Casos adversos por la vía de usuario

La línea base de los casos grandes procede de `robustez-antes.md`.
Todas las respuestas de rechazo son mensajes españoles bajo la clave `error`.

| Entrada/ruta | Antes s / bytes | Después HTTP / s / bytes | Respuesta obtenida |
|---|---|---|---|
| Cofactores n=9 | 5.77 / 124 685 561 | 400 / 0.000670 / 91 | Orden hasta 6; usar LU |
| LU n=60 | 0.88 / 11 230 152 | 400 / 0.000725 / 75 | Filas entre 1 y 8 |
| Inversa n=30 | 2.93 / 32 724 007 | 400 / 0.000636 / 75 | Filas entre 1 y 6 |
| Ecuaciones 40x40, b=1 | 4.78 / 51 483 783 | 400 / 0.000621 / 76 | Filas entre 1 y 10 |
| Eficiencia n=5000 | 0.01 / 130 | 400 / 0.000564 / 89 | Orden entre 1 y 100 |
| Suma, u=[1e5000000], v=[1] | 2.4 / 130 | 400 / 0.000570 / 56 | Exponente entre -1000 y 1000 |
| Suma, u=[2/0], v=[1] | ZeroDivisionError interno | 400 / 0.000588 / 104 | Denominador no puede ser cero |
| Eficiencia n=100 | Sin medir | 200 / 0.000609 / 718 | ops_cofactores="2.740584e+158" |
| Cofactores n=6, todas las celdas 1e1000 | Sin medir | 400 / 0.001991 / 111 | Excede presupuesto estimado; usar LU |
| LU n=8, diagonal 1e1000 | Sin medir | 200 / 0.018139 / 82 831 | Exacto: 10^8000; decimal: 1.000000e+8000 |

`parse_number` directo, con tracemalloc: 1e5000000 se rechaza en 0.000374 s/2 092
bytes pico; 1e-5000000 en 0.000057 s/1 126 bytes; 65 dígitos en 0.000041 s/1 031 bytes;
2/0 devuelve ValueError en 0.000035 s/680 bytes. Un constructor espía demuestra
que los casos excesivos no llegan a construir Fraction.

## Verificación final y alcance

- `python -m unittest discover tests -v`: **440 pruebas OK**, 16.851 s (base 421).
- Todos los `tests/*.cjs`, ejecutados individualmente con `node --test`: **59 OK** (base 58).
- `python -m unittest tests.test_golden_api`: **OK**, 43 respuestas sin cambios de campos existentes.
- Adaptadores: 7 rutas, 24 casos lineales del corpus, 851 bloques/inline de LaTeX
  con KaTeX local, `throwOnError: true` y `strict: 'error'`; forma `base.validar`,
  mismos títulos y cantidad de pasos, matrices/detalles iguales y entradas sin mutar.
- Las nuevas pruebas se ejecutaron en rojo antes de las correcciones correspondientes.
- Los resultados internos Fraction conservan exactitud aunque superen los límites
  de los literales; el formateo evita tanto OverflowError de float como el error de
  4300 dígitos, sin modificar `sys.set_int_max_str_digits`.
- Los límites se validan en los puntos de entrada de cada módulo; el Gauss interno
  compartido admite los sistemas de hasta 20 filas de los iterativos.
- Autorización del integrador: se ajustaron `test_banco_lineal.py` y `test_lineal_ui.cjs`
  para verificar x_11/t_11 con el formateador y conservar la cobertura sin resolver
  un sistema de 11 variables. `test_ecuaciones.py` no necesitó cambios.
- Sin cambios en UI, métodos numéricos, base/registro de procedimientos ni releases.
  No se editaron los documentos de estado ajenos al área; corresponde al integrador
  reconciliar sus resultados. Pendiente: revisión independiente e integración con
  el servidor de Codex 2, incluidos `tipo=limite`, adjuntar procedimientos y repetir
  mediciones del tamaño completo de la respuesta integrada.

## Commits entregados

Todos respetan <=100 líneas añadidas+eliminadas, ganchos e identidad configurada;
sin push, merge ni coautoría. Los dos cherry-picks autorizados se señalan por origen.
El commit final que cierra este informe se identifica en la entrega de la tarea.

| Hash | Mensaje | + / - |
|---|---|---:|
| 3874d70 | feat(robustez): limitar la expansion por cofactores a orden seis (origen 070e5b2) | 1 / 0 |
| da6fc77 | test(core): cubrir numeros excesivos antes de construir fracciones | 37 / 0 |
| bcc91c4 | fix(core): validar digitos y exponentes antes de crear fracciones | 25 / 6 |
| e6260a1 | test(lineal): exigir limites de dimensiones en cada motor | 61 / 0 |
| 2c7e1a5 | fix(core): validar dimensiones antes de normalizar matrices | 13 / 2 |
| e3db51f | fix(lineal): acotar vectores combinaciones y eliminacion gaussiana | 6 / 0 |
| 31795b1 | fix(vectores): aplicar dimensiones centrales y contexto de combinacion | 17 / 12 |
| f0607d2 | fix(matrices): acotar operaciones inversas y ecuaciones en los motores | 15 / 12 |
| 2f106f6 | test(determinante): contrastar Bareiss limites y estimaciones grandes | 47 / 0 |
| 0943fe9 | fix(determinante): comprobar con Bareiss y limitar expansion factorial | 43 / 6 |
| 05f132c | fix(matrices): acotar identidad y mostrar costes grandes en notacion cientifica | 11 / 3 |
| b0a3a29 | test(procedimientos): exigir adaptadores puros para todo el corpus lineal | 73 / 0 |
| cf54d0e | test(latex): renderizar procedimientos lineales con KaTeX estricto | 36 / 1 |
| 6c717d9 | feat(procedimientos): adaptar operaciones vectoriales y matriciales | 52 / 0 |
| 37bcaa2 | feat(procedimientos): adaptar sistemas inversas determinantes y eficiencia | 57 / 1 |
| 14488d3 | fix(robustez): admitir todo el rango de los dobles en el exponente (origen 0f1d59b) | 2 / 2 |
| 3692ca3 | fix(solver): conservar Gauss compartido sin limites propios de modulo | 6 / 9 |
| 403a8d5 | test(lineal): verificar subindices largos sin superar limites de entrada | 9 / 4 |
| 8bd82cd | test(core): cubrir resultados exactos mayores que el rango de float | 14 / 1 |
| 7f48a4b | fix(core): formatear resultados grandes sin desbordamientos ni limites globales | 29 / 6 |
| 38febf8 | test(determinante): acotar el desarrollo de celdas grandes antes de crearlo | 6 / 0 |
| 11ed9eb | fix(determinante): estimar el coste textual antes de expandir celdas grandes | 8 / 1 |
| e80cab8 | docs(validacion): registrar costes y casos adversos de motores lineales | 66 / 0 |
