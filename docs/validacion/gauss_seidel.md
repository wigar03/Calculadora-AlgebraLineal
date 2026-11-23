# Evidencia de Gauss-Seidel, convergencia y API

Fecha: 2026-11-23. Rama entregada: `orca/gauss-seidel`, base `fd597c3` de main.
Se modificaron únicamente los tres módulos asignados de `src/iterativos/`,
el bloque de tres rutas en `web_server.py`, las tres pruebas y esta evidencia.
No se editaron entrada, matriz, Jacobi, referencias, vista ni otros handlers.

## Resultado y reproducción

Integración temporal autorizada con `orca/jacobi` en `ee1806034c33cf26ba93dde42cc6a7ecfe09c692`.
HEAD probado: `db8561acc0396ae3d67ce976545dac93897492eb` de `tmp-integracion`.
La rama temporal se eliminó tras comprobar los resultados; no forma parte de la entrega.
La rama entregada requiere integrar también la rama de Codex 1 para ejecutar el resolvedor.

- `python -m unittest discover tests -v`: **376 pruebas, OK**, 12.772 segundos.
- `Get-ChildItem tests -Filter *.cjs | ForEach-Object { node --test $_.FullName }`:
  **52 pruebas en 9 archivos, 52 aprobadas, 0 fallos**.
- **30 pruebas propias**: pasos GS, análisis exacto, resolvedor y HTTP real con `servidor_local()`.
- `git diff --check fd597c3..orca/gauss-seidel`: sin errores.
- Logs completos de la ejecución: `%TEMP%/gauss-seidel-python-tests.log` y
  `%TEMP%/gauss-seidel-node-tests.log` (evidencia local, no versionada).

## Cobertura independiente

Los 17 casos de `banco_iterativos.py` pasaron por HTTP con ambos métodos (34 resoluciones).
Se contrastaron rangos y diagonal nula con `referencias_iterativos.json`.
En los 15 casos sin diagonal nula se contrastaron los tres primeros barridos GS
en Fraction exacto, y radios y decisiones estrictas de estabilidad para ambos métodos.
También se contrastaron los tres primeros vectores flotantes por HTTP cuando procede iterar.

Casos: `principal`, `principal_x0_unos`, `practica`, `dd_2x2`, `decimales_3x3`,
`fracciones_3x3`, `tridiagonal_5x5`, `spd_no_dominante`, `jacobi_si_gs_no`,
`diverge_ambos`, `reordenable`, `diagonal_nula_reordenable`,
`diagonal_nula_sin_arreglo`, `singular_infinitas`, `singular_incompatible`,
`hilbert_4x4` y `dd_10x10`.

Las ocho familias convergentes ordinarias (incluidos x0 distinto y 10x10)
coinciden con la solución independiente a 1e-10 con tolerancia exigida 1e-12.
Se cubren los nueve motivos de parada, los tres criterios, reordenamiento informado,
convergencia demostrada/observada/no asegurada, n=20, límite de 10000 iteraciones,
errores HTTP 400, no finitos sin NaN/Infinity JSON y escala de residuo desbordada.
Una prueba explícita falla si GS consume los valores viejos como Jacobi.
Otra impide diagnosticar divergencia por transitorios crecientes nilpotentes estables.

## Decisiones matemáticas y límites

Matrices T y polinomio por Faddeev-LeVerrier en Fraction; Schur-Cohn exacto decide rho<1.
Se rechaza la frontera exactamente, incluso diferencias de 2^-300, sin epsilon flotante.
Para mostrar rho se quitan multiplicidades con gcd(p,p') racional y se biseca r:
las raíces de p(r*z) están en el disco unidad si y solo si rho<r.
Se utiliza así el criterio exacto para acotar el máximo módulo, evitando resolver
raíces complejas mal condicionadas. Error absoluto <= max(1,2*rho)*2^-38.
Base del criterio recursivo: [Garza, Martínez y Romero, Algorithm 1](https://www.mdpi.com/2227-7390/8/8/1322).
En el caso general con n>12 o diagonal nula los radios son null y se informa «No calculado».
La revisión posterior añadió la excepción triangular exacta para n>12, descrita abajo.
Dominancia estricta y SPD para GS pueden seguir proporcionando garantía.
SPD se verifica por simetría y eliminación LDL racional con pivotes positivos.

La parada usa cambio relativo en norma infinito; además exige residuo relativo
escalado <= tolerancia y valores finitos en todos los criterios.
La divergencia por crecimiento es heurística y nunca anula una garantía exacta;
los ciclos se reconocen por repetición exacta y el estancamiento por falta de progreso.
Reordenar devuelve A y b en el orden usado y la permutación de filas originales.
Ningún solucionador directo sustituye los pasos iterativos.

Hilbert 4x4: verificados barridos, radios, garantía SPD de GS y parada por máximo
con 100 iteraciones y tol=1e-12; no se declara alcanzada esa precisión en ese límite.
No hay cambios de UX, decisiones pendientes del propietario, push, merge a main ni release.
Quedan revisión independiente e integración por el coordinador, incluidos Jacobi y la vista.

## Commits entregados (añadidas + eliminadas)

| Hash | Mensaje | Líneas |
|---|---|---:|
| 3d3e0e1 | feat(iterativos): implementar barrido secuencial de Gauss-Seidel | 34 |
| 24a4814 | feat(iterativos): calcular polinomio y estabilidad racional exacta | 72 |
| 4dee78c | feat(iterativos): acotar radios sin autovalores flotantes | 73 |
| b85fae2 | feat(iterativos): comprobar garantias y motivos de parada | 74 |
| 372a36a | feat(iterativos): preparar analisis y validar opciones del resolvedor | 63 |
| 9486f05 | feat(iterativos): resolver con residuo y diagnosticos de parada | 74 |
| a41cc2e | feat(api): exponer resolver comparar y analizar iterativos | 42 |
| 7e3cf6f | test(iterativos): contrastar barridos exactos de Gauss-Seidel | 60 |
| 3c45a7c | test(iterativos): validar espectros y fronteras exactas del banco | 81 |
| c7e5c47 | test(iterativos): exigir residuo y diagnosticar paradas | 23 |
| f3330d0 | test(iterativos): verificar soluciones y clasificar convergencia | 74 |
| 97647af | fix(iterativos): formatear LaTeX y rechazar escalas no finitas | 38 |
| be92441 | test(iterativos): cubrir limites redondeo y convergencia observada | 60 |
| d8c2f9a | test(api): comprobar contrato iterativo por HTTP real | 69 |
| 6aa5aef | test(api): contrastar todo el banco y diagnosticos por HTTP | 58 |
| fbafe18 | fix(iterativos): respetar estabilidad exacta ante transitorios crecientes | 17 |

El commit documental que contiene este informe completa la entrega; cada commit es <=100 líneas.

## Revisión cruzada e integración de controles HTML (2026-11-23)

Rama `orca/gauss-seidel` rebasada sobre main `a9627f8`, sin tocar entrada, matriz,
Jacobi, vista ni handlers; el bloque API existente ya pasa los parámetros al resolvedor.

INC-015 reproducida y corregida: `max_iteraciones: "100"` devuelve HTTP 200,
con `max_iteraciones` entero en la respuesta, en vez del error que bloqueaba Resolver.
Se admiten enteros decimales ASCII en texto, espacios exteriores y ceros iniciales:
`"1"`, `"100"`, `" 100 "`, `"000100"`, `"10000"`.
Se rechazan exponentes, signos y decimales (`"1e2"`, `"+100"`, `"10.5"`), texto
inválido, booleanos, 0, negativos y valores mayores de 10000, con mensaje reparable.
La tolerancia admite `"1e-6"` y `"0.000001"`; sigue exigiendo un valor positivo finito.
`reordenar` admite el booleano real que envía `.checked` y también `"true"`/`"false"`
(sin distinguir mayúsculas ni espacios exteriores); otros textos se rechazan.
Se prueba el cuerpo exacto de `iterativos.js:490–493`: celdas A/b/x0 en texto,
tolerancia/máximo/criterio en texto y checkbox booleano; se prueban además todos los
escalares en texto para `/resolver`, `/comparar` y `/analizar`.
`/analizar` conserva su contrato: analiza A/b/x0 y reordenamiento sin usar controles de parada.

Tres regresiones adversarias de Codex 1 se comprobaron fallando antes del arreglo:

- Meseta nilpotente n=9: ambos métodos daban estancamiento pese a cambio infinito 1.
  La meseta de residuo exige ahora cambio nulo; alcanzan tolerancia en k=10 con x=unos.
- Transitorio n=20, A=I−100N: se demostraba indebidamente ninguna garantía y se cortaba
  por crecimiento en k=7; se reconoce triangularidad y T^n=0 exactamente aun con n>12.
  Ambos métodos superiores alcanzan x=unos y tolerancia en k=21; se prueba también la
  versión inferior (Jacobi k=21, GS k=2). La garantía es demostrada y ambos radios son 0.
- A=[[1e308]], b=[1e308], x0=[1]: se sobrescribía el residuo robusto con infinito.
  Se conserva ahora el cociente protegido de matriz.residuo: un paso, residuo relativo 0,
  tolerancia satisfecha. Los valores realmente no finitos siguen provocando parada.

Las tres entradas pasan también por HTTP para ambos métodos, comparar y analizar,
con controles HTML en texto; no se sustituyó ninguna iteración por solución directa.

Ejecución final, antes del cambio puramente documental:

- `python -m unittest discover tests -v`: **400 pruebas, OK**, 13.308 segundos.
- Los 10 archivos `tests/*.cjs` con `node --test`: **57 pruebas, 57 OK, 0 fallos**.
- Las tres pruebas propias suman **38 tests**; API+convergencia: 33 tests OK.
- `git diff --check a9627f8..HEAD`: sin errores.
- Logs locales: `%TEMP%/gauss-seidel-revision-python.log` y `gauss-seidel-revision-node.log`.

Auditoría de lectura de los archivos de Codex 1: 2912 emparejamientos frente a flujo
máximo independiente, 600 permutaciones con solución preservada, 208 rangos contra SymPy,
288 errores de celda y 2428 fórmulas KaTeX estrictas sin fallos en esas comprobaciones.
Hallazgos reproducidos pendientes: P1 de residuo/iteración subnormal (API informa relativo 0
con razón racional real 0.2), P2 de magnitud sin celda y P2 de celda tras reordenar.
Detalles y correcciones sugeridas en
`C:/Users/wigar/AppData/Local/Temp/revision_iterativos_codex1_task_36b5663b4c45.md`.
La auditoría no cambió los módulos de Codex 1; los P2 son fallos de integración de la preparación.

Commits de esta revisión (líneas añadidas + eliminadas):

| Hash | Mensaje | Líneas |
|---|---|---:|
| c500a51 | fix(iterativos): aceptar los valores de los controles HTML | 23 |
| e6778c1 | test(api): cubrir el cuerpo de texto del editor iterativo | 56 |
| e1ed070 | test(api): rechazar opciones de texto invalidas con mensajes claros | 18 |
| 9ccbe2a | fix(iterativos): exigir falta de cambio para detectar estancamiento | 17 |
| 6d976b6 | fix(iterativos): demostrar nilpotencia triangular hasta orden veinte | 33 |
| e1a2f3d | fix(iterativos): conservar el residuo robusto con escalas grandes | 23 |
| 010339a | test(api): reproducir regresiones adversarias con controles HTML | 26 |

Quedan revisión e integración del coordinador y asignación de los hallazgos de la auditoría;
no se hizo push, merge a main ni release y no se requiere decisión del propietario.

## Verificación exacta final de R1 (2026-11-23)

Rama `orca/gauss-seidel` rebasada sobre main `bd3107f` (incluye el motivo y texto
de vista integrados por el coordinador). No se modificaron matriz.py, jacobi.py ni la vista.

Antes de aceptar convergencia se calcula una sola vez el residuo de la x final
con `Fraction(float)` de A, b y x: se preserva exactamente el racional binario
que realmente usó la iteración, sin reinterpretarlo como decimal.
Ax, b−Ax, norma infinita y escala se calculan racionalmente; la comparación
`residuo_rel_exacto <= Fraction(tolerancia)` precede a cualquier redondeo para JSON.
Esa comprobación proporciona también todos los campos de `verificacion`.
Las iteraciones siguen usando la primitiva existente; no se añadió este cálculo
exacto dentro del bucle. Una prueba con espía demuestra una llamada final por
resolución, tanto con parada por tolerancia como por máximo de iteraciones.

Si una candidata por tolerancia flotante no pasa la verificación final, se devuelve
`convergio=false`, `verificacion.cumple=false` y `motivo=precision_insuficiente`.
Texto: «La verificación exacta final no cumple la tolerancia; la precisión flotante
es insuficiente». Se avisó al coordinador, que actualizó contrato y vista en main.
Si la primitiva de residuo robusto detiene antes por estancamiento, se conserva ese motivo.
Los números JSON se muestran redondeados a doble, pero `cumple` se decide racionalmente;
un residuo absoluto subnormal puede redondearse a cero sin perder su razón relativa.

R1 por HTTP: A=[[1e-200,5e-201],[5e-201,1e-200]], b=[5e-324,5e-324], x0=0.
La regresión falló primero en seis subcasos (ambos métodos y los tres criterios).
Ahora informa residuo relativo final 0.19999999999999998 y rechaza convergencia;
se contrasta con Fraction independiente de los mismos floats de la respuesta.
También se verifica `/comparar`; no se sustituye la iteración por una solución directa.
Otra prueba usa la razón exacta 1/(2^53+1), ligeramente mayor que su float redondeado:
la verificación rechaza ese umbral aun cuando la presentación JSON coincida con él.
Se cubre además la escala nula; se mantienen las regresiones de nilpotencia y 1e308.

Ejecución completa sobre la base actualizada, antes del cambio documental:

- `python -m unittest discover tests -v`: **403 pruebas, OK**, 12.803 segundos.
- Los 10 archivos `tests/*.cjs` con `node --test`: **58 pruebas, 58 OK, 0 fallos**.
- `git diff --check bd3107f..HEAD`: sin errores.
- Logs: `%TEMP%/gauss-seidel-final-exacto-python.log` y `gauss-seidel-final-exacto-node.log`.
- La primera pasada detectó una huella web antigua; se incorporó el arreglo ya
  disponible en main `bd3107f` y la repetición completa pasó.

Commits (añadidas + eliminadas): `2260479` — fix(iterativos): exigir residuo racional
exacto al finalizar, 58 líneas; `ef62e96` — test(iterativos): verificar una vez y comparar
el umbral exacto, 36 líneas; este registro añade el commit documental, todos <=100 líneas.
Queda revisión e integración del coordinador; el cambio paralelo en matriz.residuo
es independiente de esta barrera final y no forma parte de esta rama.

## Barrido GS normalizado para R1 (2026-11-23)

Rama `orca/gauss-seidel` rebasada sobre main `d6b8209`, con los arreglos de Codex 1
y la verificación exacta final ya integrados. Solo se modificó Gauss-Seidel, sus pruebas
y esta evidencia; no se tocaron Jacobi, matriz, resolvedor, vista ni referencias.

El barrido calcula ahora `b_i/a_ii - sum((a_ij/a_ii)*x_j)` usando inmediatamente
las componentes anteriores nuevas. Así no redondea a cero a_ij*x_j antes de dividir.
Si la normalización produce un cociente no representable o pierde uno no nulo a cero,
se conserva la ecuación original racionalmente, evitando infinito por cero y pérdida
del cociente. Este respaldo se prueba con coeficientes 1e-308 y 1e308.
Las fórmulas y sustituciones LaTeX conservan el procedimiento y los índices originales.

Primero fallaron dos regresiones: R1 por HTTP devolvía estancamiento, y el segundo
componente del primer barrido era el doble de la referencia racional por perder
el término que usa x_1 nuevo. Tras el arreglo ambas pasan.
Con A=[[1e-200,5e-201],[5e-201,1e-200]], b=[5e-324,5e-324], x0=0 y tol=1e-6,
GS alcanza tolerancia en **12 iteraciones**, con residuo relativo exacto
**2.9802320600738147e-8**, verificado independientemente por HTTP con Fraction
de los mismos floats A/b/x y sin reemplazar las iteraciones por solución directa.

Se preservan los tres primeros barridos exactos Fraction de los 15 casos sin diagonal
nula; los tres barridos flotantes se contrastan a `1e-12*max(1,abs(referencia))`.
Se renderizaron las fórmulas y sustituciones de esos barridos y R1: **336 fórmulas**,
KaTeX local con `throwOnError:true`, `strict:"error"`, **cero errores**.

- `python -m unittest discover tests -v`: **414 pruebas, OK**, 14.703 segundos.
- Los 10 archivos `tests/*.cjs` con `node --test`: **58 pruebas, 58 OK, 0 fallos**.
- `git diff --check d6b8209..HEAD`: sin errores.
- Logs: `%TEMP%/gauss-seidel-normalizado-python.log` y `gauss-seidel-normalizado-node.log`.
- `be851b7` — fix(iterativos): normalizar el barrido de Gauss-Seidel por su diagonal,
  **42 líneas**; `09bbb6a` — test(iterativos): contrastar los barridos normalizados
  y sus extremos, **26 líneas**; este registro completa los commits, todos <=100 líneas.

Queda revisión e integración del coordinador; no hay decisiones para el propietario.
