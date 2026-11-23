# Validación de álgebra lineal

Fecha: 2026-11-23. Rama: orca/lineal. Base: 7a241ad.

**29/29 VALIDADO; 0 FALLA; 0 PENDIENTE.**

## Evidencia ejecutada

- python -m unittest discover tests -v: **202 pruebas OK**, incluidas las **33** de test_banco_lineal.py (29 ejercicios y 4 regresiones adicionales).
- Get-ChildItem tests/*.cjs | ForEach-Object { node --test $_.FullName }: **6 archivos OK; 40 pruebas OK** (6 + 5 + 9 + 4 + 11 + 5). Equivale al bucle solicitado en Bash.
- Las pruebas usan servidor_local(), HTTP real y referencias JSON inmutables; comprueban ambos métodos de sistemas, ambos de determinante y ambos de inversa.
- Sustitución independiente con Fraction: A·X=B, A·A⁻¹=I y A⁻¹·A=I; cada operación elemental se reproduce desde el estado anterior; las matrices LU conservan el valor absoluto del determinante calculado por permutaciones independientes.
- Navegador Orca real, servidor del worktree: los **19 sistemas × 2 métodos** y **10 matrices × 4 métodos** se introdujeron en las grillas DOM y se ejecutaron llamando las funciones de los botones de la página: **78 resoluciones sin error ni .katex-error**.
- I-11 mostró sus cinco incógnitas y 29/14 matrices intermedias con Jordan/Gauss; I-12 se repitió con 0.5, -0.75, -2.5, 0.75, 1/3 y 181/60; las celdas mantienen cadenas exactas y no pasan por parseFloat.
- I-14 mostró t∈R, x₄=t y cuatro filas de verificación válidas para cualquier t; cada inversa mostró exactamente 16 entradas Correcto en cada producto (32 en total).
- Se ejecutó el ejemplo singular visible [[2,3,4],[2,3,4],[2,3,4]]: explica ausencia de pivote, rango deficiente y por qué no existe la inversa; 0 errores KaTeX.
- tests/test_lineal_ui.cjs: **9 pruebas OK**, sin paquetes externos, con el KaTeX ya incluido en la aplicación; verifican controles hasta 5×5, entradas exactas, envío HTTP, renderizado paramétrico, procedimiento y diagnóstico singular.
- Se inspeccionó visualmente la página de sistemas tras resolver I-14; navegación, controles, colores, tipografía y flujos se conservan.

## Resultados por ejercicio

Entradas A por filas y b exactamente como en los bancos; las matrices inversas de la tabla son la respuesta HTTP completa. Referencia: tests/validacion/referencias.json, claves indicadas; Δ=0 significa igualdad racional exacta, sin tolerancias.

| Ejercicio | Entrada utilizada | Resultado de la calculadora | Referencia independiente | Diferencia | Estado | Commit de prueba |
|---|---|---|---|---|---|---|
| I-1 | A=[["-3","-1","4","5"],["3","4","-2","3"],["-4","3","-1","2"],["-2","-4","2","5"]]; b=["-6","16","-12","-12"] | SCD; rangos=4/4; X=["4","2","2","0"] | lineales.I-1: ["4","2","2","0"] | 0; A·X−b=0 | VALIDADO | df8776 / 88a074 |
| I-2 | A=[["-1","-1","3","-2"],["6","4","5","-1"],["1","-1","2","3"],["0","-3","6","-2"]]; b=["-18","21","9","-21"] | SCD; rangos=4/4; X=["5","1","-2","3"] | lineales.I-2: ["5","1","-2","3"] | 0; A·X−b=0 | VALIDADO | df8776 / 88a074 |
| I-3 | A=[["6","2","6","6"],["-2","5","-3","-1"],["-2","-3","1","4"],["-2","6","1","6"]]; b=["-18","21","-13","10"] | SCD; rangos=4/4; X=["-2","3","0","-2"] | lineales.I-3: ["-2","3","0","-2"] | 0; A·X−b=0 | VALIDADO | df8776 / 88a074 |
| I-4 | A=[["-2","2","0","-2"],["-1","-2","-4","-2"],["2","3","4","2"],["1","2","5","-2"]]; b=["-2","-25","31","6"] | SCD; rangos=4/4; X=["1","5","1","5"] | lineales.I-4: ["1","5","1","5"] | 0; A·X−b=0 | VALIDADO | df8776 / 88a074 |
| I-5 | A=[["1","4","-1","3"],["3","-2","1","3"],["-3","4","6","3"],["-1","3","4","1"]]; b=["6","22","41","22"] | SCD; rangos=4/4; X=["0","-1","5","5"] | lineales.I-5: ["0","-1","5","5"] | 0; A·X−b=0 | VALIDADO | df8776 / 88a074 |
| I-6 | A=[["3","3","5","6"],["-1","6","-4","2"],["1","-1","2","6"],["2","-2","4","0"]]; b=["8","-6","-7","10"] | SCD; rangos=4/4; X=["4","1","1","-2"] | lineales.I-6: ["4","1","1","-2"] | 0; A·X−b=0 | VALIDADO | df8776 / 88a074 |
| I-7 | A=[["-4","-3","2","-2"],["6","3","2","-3"],["-3","-1","3","-2"],["4","-1","-2","4"]]; b=["-26","21","-21","32"] | SCD; rangos=4/4; X=["5","0","0","3"] | lineales.I-7: ["5","0","0","3"] | 0; A·X−b=0 | VALIDADO | df8776 / 88a074 |
| I-8 | A=[["0","0","-2","-2"],["-2","2","-2","5"],["0","-1","-3","2"],["-4","6","-4","5"]]; b=["8","-22","-7","-26"] | SCD; rangos=4/4; X=["0","-1","0","-4"] | lineales.I-8: ["0","-1","0","-4"] | 0; A·X−b=0 | VALIDADO | df8776 / 88a074 |
| I-9 | A=[["0","0","2","4"],["6","-4","-2","5"],["-4","1","1","2"],["0","0","0","2"]]; b=["8","11","-11","2"] | SCD; rangos=4/4; X=["5","5","2","1"] | lineales.I-9: ["5","5","2","1"] | 0; A·X−b=0 | VALIDADO | df8776 / 88a074 |
| I-10 | A=[["-2","0","3","4"],["4","6","3","2"],["5","-2","3","2"],["2","-3","-2","-1"]]; b=["7","21","42","8"] | SCD; rangos=4/4; X=["5","-2","3","2"] | lineales.I-10: ["5","-2","3","2"] | 0; A·X−b=0 | VALIDADO | df8776 / 88a074 |
| I-11 | A=[["0","2","-3","1","4"],["3","0","2","-4","1"],["-2","5","0","3","-2"],["4","-1","3","0","-3"],["1","-3","-2","5","0"]]; b=["-18","6","-2","24","4"] | SCD; rangos=5/5; X=["2","-1","3","1","-2"] | lineales.I-11: ["2","-1","3","1","-2"] | 0; A·X−b=0 | VALIDADO | df8776 / 88a074 |
| I-12 | A=[["1/2","-3/4","2","-1/3"],["3/2","1","-5/2","2/3"],["-1","1/2","3/4","-2"],["2/3","-2","1/2","5/4"]]; b=["181/60","-3/4","7/30","253/120"] | SCD; rangos=4/4; X=["162683/104610","-16458/17435","96608/156915","-94081/104610"] | lineales.I-12: ["162683/104610","-16458/17435","96608/156915","-94081/104610"] | 0; A·X−b=0 | VALIDADO | df8776 / 88a074 |
| I-13 | A=[["12","6","4","3"],["30","20","15","12"],["20","15","12","10"],["105","84","70","60"]]; b=["9","23","16","87"] | SCD; rangos=4/4; X=["1","-2","3","-1"] | lineales.I-13: ["1","-2","3","-1"] | 0; A·X−b=0 | VALIDADO | df8776 / 88a074 |
| I-14 | A=[["2","-3","1","4"],["4","-1","-3","2"],["-2","8","-6","-10"],["3","2","-4","1"]]; b=["7","5","-16","4"] | SCI; rangos=3/3; X=["6 - 3t","17/5 - 8/5t","26/5 - 14/5t","t"] | lineales.I-14: infinitas; rangos 3/3 | 0; A·X−b=0 | VALIDADO | df8776 / 88a074 |
| I-15 | A=[["0","1/2","1","-1"],["2","1","-1","1/2"],["1","-1","2","1"],["1/2","2","1","-1"]]; b=["3","5","1","4"] | SCD; rangos=4/4; X=["115/32","-17/32","3/64","-103/32"] | lineales.I-15: ["115/32","-17/32","3/64","-103/32"] | 0; A·X−b=0 | VALIDADO | df8776 / 88a074 |
| I-16 | A=[["1/2","3/2","-1/2","2"],["6/5","-4/5","12/5","3/5"],["21/10","1","-13/10","1/2"],["-7/10","11/5","0","11/10"]]; b=["9/2","16/5","-17/10","13/5"] | SCD; rangos=4/4; X=["-3034/3841","-11882/19205","2871/3841","59504/19205"] | lineales.I-16: ["-3034/3841","-11882/19205","2871/3841","59504/19205"] | 0; A·X−b=0 | VALIDADO | df8776 / 88a074 |
| I-17 | A=[["2","2/3","-1/2","1"],["3/4","1","2/5","-1"],["1","-1/3","2","1/2"],["2","1","1/4","3/2"]]; b=["2","1","5","6"] | SCD; rangos=4/4; X=["-143/331","3531/1324","850/331","1569/662"] | lineales.I-17: ["-143/331","3531/1324","850/331","1569/662"] | 0; A·X−b=0 | VALIDADO | df8776 / 88a074 |
| I-18 | A=[["0","5/4","5/2","-3/4"],["1/2","-3/2","1/4","2"],["7/4","1/2","-1","1/4"],["-1","9/4","3/4","3/2"]]; b=["9/4","-3/2","3","17/4"] | SCD; rangos=4/4; X=["10138/9355","3795/1871","324/9355","928/1871"] | lineales.I-18: ["10138/9355","3795/1871","324/9355","928/1871"] | 0; A·X−b=0 | VALIDADO | df8776 / 88a074 |
| I-19 | A=[["1","3/5","1","1/2"],["1/4","-2","3/2","1"],["2","1/3","-1","2/3"],["1","-1/2","1/4","2"]]; b=["7/5","-2","3","5"] | SCD; rangos=4/4; X=["-1868/4789","8931/4789","-4646/4789","15720/4789"] | lineales.I-19: ["-1868/4789","8931/4789","-4646/4789","15720/4789"] | 0; A·X−b=0 | VALIDADO | df8776 / 88a074 |
| II-1 | A=[[-4,5,-4,5],[-3,3,-1,3],[-3,5,1,-1],[1,-4,-1,-3]] | det=-146; A⁻¹=[["17/73","-101/146","-7/146","-21/73"],["14/73","-33/73","10/73","-13/73"],["-24/73","61/146","-3/146","-9/73"],["-5/73","17/73","-14/73","-11/73"]] | matrices.II-1: det=-146; inversa exacta idéntica | 0; ambos residuos identidad=0 | VALIDADO | 88a074 |
| II-2 | A=[[3,-3,-1,4],[0,-3,0,6],[0,0,-2,2],[-3,-3,3,3]] | det=-54; A⁻¹=[["0","1/3","-1/2","-1/3"],["-2/3","1","-2/3","-2/3"],["-1/3","2/3","-5/6","-1/3"],["-1/3","2/3","-1/3","-1/3"]] | matrices.II-2: det=-54; inversa exacta idéntica | 0; ambos residuos identidad=0 | VALIDADO | 88a074 |
| II-3 | A=[[-3,-4,2,0],[1,6,-3,3],[1,2,0,5],[3,4,3,-2]] | det=348; A⁻¹=[["-12/29","-9/29","5/29","-1/29"],["19/116","79/348","-31/348","41/348"],["6/29","-1/87","7/87","16/87"],["1/58","-5/174","35/174","-7/174"]] | matrices.II-3: det=348; inversa exacta idéntica | 0; ambos residuos identidad=0 | VALIDADO | 88a074 |
| II-4 | A=[[-2,0,-4,-1],[-3,-3,-3,0],[6,-3,4,2],[-2,-3,-1,2]] | det=-99; A⁻¹=[["10/33","-5/33","2/11","-1/33"],["2/11","-14/33","-1/11","2/11"],["-16/33","8/33","-1/11","-5/33"],["1/3","-2/3","0","2/3"]] | matrices.II-4: det=-99; inversa exacta idéntica | 0; ambos residuos identidad=0 | VALIDADO | 88a074 |
| II-5 | A=[[1,-3,4,5],[2,4,4,2],[0,-3,-4,-1],[0,-3,3,-3]] | det=342; A⁻¹=[["-1/57","29/57","11/19","20/171"],["-5/57","5/114","-2/19","-14/171"],["2/57","-1/57","-3/19","17/171"],["7/57","-7/114","-1/19","-26/171"]] | matrices.II-5: det=342; inversa exacta idéntica | 0; ambos residuos identidad=0 | VALIDADO | 88a074 |
| II-6 | A=[[3,-3,2,-3],[3,3,1,5],[1,6,6,-1],[3,-2,5,1]] | det=844; A⁻¹=[["239/844","167/844","-5/844","-123/844"],["9/211","16/211","21/211","-32/211"],["-25/211","-21/211","12/211","42/211"],["-145/844","47/844","-57/844","117/844"]] | matrices.II-6: det=844; inversa exacta idéntica | 0; ambos residuos identidad=0 | VALIDADO | 88a074 |
| II-7 | A=[[5,6,-2,4],[-1,4,1,3],[1,6,3,0],[6,0,-1,6]] | det=728; A⁻¹=[["9/364","-3/14","43/364","33/364"],["81/728","1/28","23/728","-67/728"],["-3/13","0","3/13","2/13"],["-23/364","3/14","-29/364","37/364"]] | matrices.II-7: det=728; inversa exacta idéntica | 0; ambos residuos identidad=0 | VALIDADO | 88a074 |
| II-8 | A=[[5,6,1,2],[6,6,2,-1],[-3,-3,4,-2],[-3,1,3,6]] | det=75; A⁻¹=[["3","-34/15","17/15","-1"],["-3","12/5","-6/5","1"],["4/5","-8/15","7/15","-1/5"],["8/5","-19/15","8/15","-2/5"]] | matrices.II-8: det=75; inversa exacta idéntica | 0; ambos residuos identidad=0 | VALIDADO | 88a074 |
| II-9 | A=[[2,-1,-3,5],[-3,-4,0,1],[0,-3,-1,6],[5,4,1,2]] | det=55; A⁻¹=[["3/5","7/5","-1","4/5"],["-29/55","-81/55","10/11","-37/55"],["-3/11","3/11","1/11","3/11"],["-17/55","-38/55","7/11","-16/55"]] | matrices.II-9: det=55; inversa exacta idéntica | 0; ambos residuos identidad=0 | VALIDADO | 88a074 |
| II-10 | A=[[-4,-2,-4,5],[-2,2,1,4],[2,0,2,4],[5,3,-2,-4]] | det=-654; A⁻¹=[["2/109","-13/109","41/218","10/109"],["-14/327","91/327","-23/218","13/109"],["-52/327","11/327","4/109","-14/109"],["23/327","14/327","15/109","2/109"]] | matrices.II-10: det=-654; inversa exacta idéntica | 0; ambos residuos identidad=0 | VALIDADO | 88a074 |

La solución completa de I-14 es X=(6−3t, 17/5−8t/5, 26/5−14t/5, t), t∈R; particular=(6,17/5,26/5,0), base del núcleo=(-3,-8/5,-14/5,1).
La referencia de I-14 solo especifica clasificación y rangos: la familia se valida independientemente verificando A·particular=b, A·base=0 y sustituciones t=-3,0,2/3; no se inventa una solución única.

## Incidencias corregidas

| Síntoma | Causa | Corrección | Prueba |
|---|---|---|---|
| Los 18 sistemas únicos daban resultados erróneos al seleccionar Gauss, aunque Jordan funcionaba | Se devolvía directamente la columna b triangular | Sustitución regresiva exacta por pivotes | Los 19 sistemas en ambos métodos; antes: 18 fallos, después: 0 |
| I-14 en Gauss conservaba variables pivote dentro de expresiones y no resolvía completamente la familia | Parametrización basada solo en cada fila sin sustituir las posteriores | Representación afín racional y sustitución regresiva | I-14 y SCI sintéticos con varios parámetros y columnas sin pivote |
| I-14 mostraba fracciones deformadas y no declaraba el dominio del parámetro junto al vector | El formateador escalar dividía toda la expresión por la primera barra | Formateador específico de componentes paramétricas; t∈R y variable libre explícitos | KaTeX local estricto, VM y navegador real sin errores |
| Las fracciones de las filas centrales de I-14 se superponían visualmente | Separación vertical insuficiente al pasar expresiones fraccionarias al vector columna | Espacio matemático de 0.5em entre componentes del vector paramétrico, sin cambiar controles ni estilos | Inspección de captura tras el ajuste, KaTeX estricto y batería completa nuevamente: 202 Python + 40 Node OK; commit `d6313b0` |
| El procedimiento de sistemas solo describía operaciones, sin sus estados matriciales ni la sustitución | El handler omitía matrices y sustitución; la vista no las dibujaba | Serializar y mostrar los estados exactos y los pasos regresivos en la sección existente | Reproducción independiente de todas las operaciones y matrices visibles en navegador |
| La verificación SCI era una afirmación sin cálculo | No se evaluaban coeficientes libres ni término constante | Verificar A·particular=b y A·base=0 fila por fila | Cuatro comprobaciones visibles para todo parámetro real y sustitución independiente |
| La segunda comprobación A⁻¹·A se mostraba dos veces | Bucle y título duplicados en app.js | Eliminar la duplicación | Node y navegador: 16+16 entradas por inversa 4×4 |
| Varias filas contradictorias podían inflar el rango aumentado | Se contaban filas no nulas dependientes en la única columna adicional | rg(A ampliada)=rg(A)+1 cuando hay contradicción | Sistema sintético A=0, b=(1,2): SI, rangos 0/1 |

## Límites y entrega

No se cambiaron referencias, HTML, otros módulos ni controles UX; el caso singular ya diagnosticaba correctamente la causa y ahora tiene regresión HTTP y de vista. El integrador debe revisar e integrar la rama y trasladar esta evidencia a sus documentos globales; no hubo push ni merge.

## Seguimiento de la revisión cruzada (2026-11-23)

La rama se rebasó sobre main actualizado, base `e3bdbf9` (incluye `c6fdf36`); los conteos siguientes sustituyen a los de la primera entrega para esta revisión posterior.

- **P2 corregido:** descripción, lista de parámetros, sustitución y verificación usan `x_{10}` / `t_{10}` en LaTeX; los identificadores JSON conservan `x_10` / `t_10` para no alterar su contrato. HTTP real con A=[[0]*10], b=[0] confirma diez parámetros y base del núcleo identidad; se comprueba también la sustitución de sistemas con once variables y diez parámetros.
- **P3 corregido:** `vectorSolucionLinealToLatex` recibe `solucion_particular`, `base_nucleo` y `parametros`; construye cada término con coeficientes racionales canónicos y nombres separados. Elimina la sustitución de fracciones dentro de texto; rechaza explícitamente componentes antiguas como `0.5/2+t`, `1/2.5+t` o `x_1/2` en vez de transformarlas parcialmente.
- Las fracciones equivalentes `1/4+t`, `2/5+t` y `(1/2)x_1` se renderizan desde datos estructurados; se cubren signos, ceros, coeficientes ±1 e índices de dos cifras sin perder la separación vertical existente.
- `tests/test_banco_lineal.py`: **36 pruebas OK**, incluidos los 29 ejercicios anteriores y tres regresiones nuevas; los coeficientes de respuestas HTTP se comparan con `Fraction` en forma canónica.
- `tests/test_lineal_ui.cjs`: **13 pruebas OK**, sin paquetes externos; KaTeX local con `throwOnError: true` interpreta los textos reales generados por Python, y MathML contiene `<msub><mi>t</mi><mn>10</mn></msub>` como un único subíndice.
- Batería completa ejecutada después de los cambios: `python -m unittest discover tests -v`: **308 pruebas OK**; todos los `tests/*.cjs`: **8 archivos OK, 50 pruebas OK** (6+5+3+13+4+3+11+5). `git diff --check` sin errores.
- Commits de código/pruebas: `ffe4cf2` (56 líneas), `b3bccc8` (48), `194e30c` (47), `000ec50` (16); todos por debajo de 100 líneas modificadas, sin cambios UX, push ni merge.

La revisión numérica solicitada por separado fue de solo lectura y se entregó al coordinador en `C:/Users/wigar/AppData/Local/Temp/orca-audit-numerico-lineal.md`, con siete hallazgos reproducidos por HTTP, severidad, comparación con la versión anterior y correcciones sugeridas; esta rama solo modifica el área lineal.
