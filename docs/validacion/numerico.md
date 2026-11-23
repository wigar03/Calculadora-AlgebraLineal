# Validación de métodos numéricos

Rama: `orca/numerico`, base `7a241ad`. Fecha: 2026-11-23.
Estado: **18/18 ecuaciones completas VALIDADAS** por HTTP real con `servidor_local()`;
72 combinaciones ejercicio/método y 12 comprobaciones adicionales de raíces positivas alternativas.
IV-2 e IV-5 permanecen incompletos: solo se probó el dominio de sus radicales, sin resolverlos.

Todas las solicitudes usan `funcion` del banco, tolerancia `1e-6`, máximo 200 iteraciones y
`condicion` del enunciado. Los extremos de la tabla son `a,b` en bisección, `xl,xu` en regla
falsa y `x0,x1` en secante; la última columna es la semilla manual de Newton.
Bisección usa criterio `intervalo`; Newton y secante, `absoluto`; regla falsa, error relativo porcentual.
Los métodos sugeridos se incluyen siempre; para los diez primeros se justifica bisección por su
encierro con cambio de signo y continuidad, y se contrastan también los otros tres métodos.

| Ejercicio | Función enviada | Extremos | Newton x0 | Referencia seleccionada (30 cifras) |
|---|---|---|---|---|
| III-1 | `x^3 - 4*x - 9` | [2,3] | 3 | 2.70652795449793495272020686559 |
| III-2 | `exp(x) - 3*x^2` | [0,1] | 1 | 0.910007572488709060657338295759 |
| III-3 | `cos(x) - x*exp(x)` | [0,1] | 0.5 | 0.517757363682458298322787474166 |
| III-4 | `x*ln(x) - 1` | [1,2] | 2 | 1.76322283435189671022520177695 |
| III-5 | `x^4 - 3*x^2 - 3` | [1,2] | 2 | 1.94712296670701308927865526713 |
| III-6 | `ln(x+2) + x^2 - 2` | [0,1] | 1 | 0.956989236662597376424277677176 |
| III-7 | `exp(-x) - x^2 + 0.5` | [0,1] | 1 | 0.943091718315079520139045031058 |
| III-8 | `x^3 + x - 1` | [0,1] | 1 | 0.682327803828019327369483739711 |
| III-9 | `x*exp(-x) - 0.2` | [0,1] | 0.5 | 0.259171101819073764476637135967 |
| III-10 | `x^2 - 5*sin(x)` | [2,3] | 2 | 2.08593458380659166406734168556 |
| III-11 | `ln(x) + sin(x) - 1.2` | [1,2] | 1 | 1.27544958007973679917463976432 |
| III-12 | `exp(-x) + cos(x) - 0.5` | [1,2] | 1 | 1.33239019855357254607634329872 |
| III-13 | `x^2 - 3*sin(x) - ln(x+2)` | [2,3] | 2 | 2.02260019720136517038032802315 |
| III-14 | `exp(x/2) + sin(2*x) - 3` | [2,3] | 3 | 2.67306304108189214585470671736 |
| III-15 | `ln(x+3) + cos(x) - x/2` | [2,3] | 2 | 2.1646088424287021991765644668 |
| IV-1 | `sin(x)/ln(x) - 1` | [2,3] | 2 | 2.2191071489137460325957851882 |
| IV-3 | `exp(1/x) + 2*x/tan(x) - 2` | [1,1.56] | 1.5 | 1.54239600614889538074840966572 |
| IV-4 | `ln(x+1)/(x^2-4) + 0.1` | [0,1] | 1 | 0.460519480256649476711757428119 |

III-2 aproxima aquí la positiva menor; la otra positiva 3.73307902863281420061995402984 se
prueba con [3,4], Newton 4. III-9 aproxima aquí la positiva menor; 2.54264135777352633279817223827
se prueba con [2,3], Newton 3. IV-3 también se prueba en [4,4.7], Newton 4.5, para
4.63062211499472076414357244822. Las doce comprobaciones adicionales pasan (`415a8a6`).

## Criterios, precisión y verificación

El JSON mantiene los flotantes completos, sin redondear iteraciones; las tablas/resultados existentes
en JavaScript muestran 8 a 10 cifras significativas. No se modificaron archivos de interfaz.
`verificacion` vuelve a sustituir la raíz y comunica si el residuo satisface la tolerancia.
Esto es independiente de la parada: III-1 con bisección converge con cota `4.76837158203125e-7`
y residuo `4.175800416561515e-6`, que **no** satisface 1e-6. No se presenta el residuo como error en x.
Se conserva el margen de tolerancia aproximada ya existente en Newton/secante y su informe explícito;
las raíces de este banco se comparan estrictamente con la referencia mediante `Decimal`, diferencia <=1e-6.
El campo optativo API `condicion=positiva_no_nula` rechaza x=0 en III-10 con `raiz_no_admisible`;
en la página, [2,3] evita esa raíz trivial sin añadir controles.

## Incidencias corregidas

| Síntoma | Causa y corrección | Evidencia / commit |
|---|---|---|
| Bisección podía acercarse a un polo | Validación compartida de continuidad y restricciones del AST | Polos de IV-1/3/4, hueco cancelado y signos; `ebe65e2`, `2a70237`, `415a8a6` |
| El motor directo de regla falsa omitía continuidad | Validar también dentro del motor | Regresiones Python/HTTP; `ebe65e2` |
| La guarda de tan alteraba valores definidos | Retirada la guarda numérica: se conserva el evaluador del analizador sin ajustar a cero | Revisión 3; `2727a79` |
| Paso diminuto podía aceptarse con residuo alto | La escala de semilla fue sustituida por certificación local de existencia | Revisiones 1, 2 y 5; `1badd32`, `41f88b1` |
| Regla falsa aceptaba el redondeo como convergencia | Agotamiento antes de tolerancia y control de residuo unilateral | x^2-2 con tol 1e-100, exp(30*(x-1))-2; `25d2603`, `77027a6` |
| Derivación simplificada podía ampliar el dominio | Evaluar dominio original antes de f' | tan, 0*ln(x), (1/x)^0; `bdb52c3` |
| ln cerca de cero se clasificaba como asíntota del extremo | Comparar crecimiento con altura finita del borde | III-4/11 en [1e-6,2], ln y 1/x; `77027a6` |

La detección numérica de continuidad sigue siendo exploratoria para expresiones arbitrarias;
se complementa con restricciones analíticas afines/cuadráticas y trigonométricas para los casos del banco.
No se modificó `expresiones.py` ni `biseccion/dominio.py`. El analizador ya está integrado;
la notación del documento se contrasta también en `tests/test_validacion_ejercicios.py`, sin modificar ese archivo.

## Ejecuciones y evidencia por método

Primera entrega: `python -m unittest discover tests -v`: **253 pruebas OK** (incluye 82 del banco).
Primera entrega: equivalente PowerShell del bucle Node: **5 archivos, 31 pruebas OK**.
La sustitución de la tabla se contrasta con funciones independientes de `math`; Newton se contrasta
además con diferencias finitas y su recurrencia, y los métodos cerrados conservan cambio de signo.
Las filas siguientes proceden de HTTP real ejecutado en `77027a6`; todas tienen estado VALIDADO.

| Ejercicio | Método | Raíz calculada | Diferencia absoluta vs referencia anterior | Residuo | Iteraciones | Parada | Estado | Commit |
|---|---|---|---|---|---|---|---|---|
| III-1 | biseccion | 2.7065281867980957 | 2.323002e-7 | 4.175800e-06 | 21 | tolerancia | VALIDADO | 77027a6 |
| III-1 | regla_falsa | 2.7065279538946934 | 6.032416e-10 | 1.084380e-08 | 10 | tolerancia | VALIDADO | 77027a6 |
| III-1 | secante | 2.706527954497937 | 2.047280e-15 | 3.907985e-14 | 6 | tolerancia | VALIDADO | 77027a6 |
| III-1 | newton | 2.7065279544979393 | 4.347280e-15 | 7.638334e-14 | 4 | tolerancia | VALIDADO | 77027a6 |
| III-2 | biseccion | 0.9100079536437988 | 3.811551e-7 | 1.134205e-06 | 21 | tolerancia | VALIDADO | 77027a6 |
| III-2 | regla_falsa | 0.9100075723838347 | 1.048744e-10 | 3.120753e-10 | 8 | tolerancia | VALIDADO | 77027a6 |
| III-2 | secante | 0.9100075724887104 | 1.339343e-15 | 4.440892e-15 | 6 | tolerancia | VALIDADO | 77027a6 |
| III-2 | newton | 0.9100075724887091 | 3.934266e-17 | 4.440892e-16 | 4 | tolerancia | VALIDADO | 77027a6 |
| III-3 | biseccion | 0.5177569389343262 | 4.247481e-7 | 1.292136e-06 | 21 | tolerancia | VALIDADO | 77027a6 |
| III-3 | regla_falsa | 0.5177573624598757 | 1.222583e-9 | 3.719248e-09 | 18 | tolerancia | VALIDADO | 77027a6 |
| III-3 | secante | 0.5177573636823997 | 5.859832e-14 | 1.784128e-13 | 7 | tolerancia | VALIDADO | 77027a6 |
| III-3 | newton | 0.5177573636824614 | 3.101677e-15 | 9.436896e-15 | 3 | tolerancia | VALIDADO | 77027a6 |
| III-4 | biseccion | 1.7632231712341309 | 3.368822e-7 | 5.279428e-07 | 21 | tolerancia | VALIDADO | 77027a6 |
| III-4 | regla_falsa | 1.7632228341921345 | 1.597622e-10 | 2.503702e-10 | 7 | tolerancia | VALIDADO | 77027a6 |
| III-4 | secante | 1.7632228343518876 | 9.110225e-15 | 1.421085e-14 | 5 | tolerancia | VALIDADO | 77027a6 |
| III-4 | newton | 1.7632228343518968 | 8.977480e-17 | 2.220446e-16 | 4 | tolerancia | VALIDADO | 77027a6 |
| III-5 | biseccion | 1.9471230506896973 | 8.398268e-8 | 1.498728e-06 | 21 | tolerancia | VALIDADO | 77027a6 |
| III-5 | regla_falsa | 1.947122966483146 | 2.238671e-10 | 3.995060e-09 | 8 | tolerancia | VALIDADO | 77027a6 |
| III-5 | secante | 1.9471229667070766 | 6.351072e-14 | 1.133316e-12 | 6 | tolerancia | VALIDADO | 77027a6 |
| III-5 | newton | 1.9471229667070131 | 1.072134e-17 | 0.000000e+00 | 4 | raiz_evaluada | VALIDADO | 77027a6 |
| III-6 | biseccion | 0.9569888114929199 | 4.251697e-7 | 9.575501e-07 | 21 | tolerancia | VALIDADO | 77027a6 |
| III-6 | regla_falsa | 0.95698923661494 | 4.765738e-11 | 1.073319e-10 | 6 | tolerancia | VALIDADO | 77027a6 |
| III-6 | secante | 0.9569892366625948 | 2.576424e-15 | 5.773160e-15 | 5 | tolerancia | VALIDADO | 77027a6 |
| III-6 | newton | 0.9569892366626203 | 2.292358e-14 | 5.151435e-14 | 3 | tolerancia | VALIDADO | 77027a6 |
| III-7 | biseccion | 0.943091869354248 | 1.510392e-7 | 3.437056e-07 | 21 | tolerancia | VALIDADO | 77027a6 |
| III-7 | regla_falsa | 0.9430917182408971 | 7.418242e-11 | 1.688099e-10 | 6 | tolerancia | VALIDADO | 77027a6 |
| III-7 | secante | 0.9430917183150784 | 1.120139e-15 | 2.498002e-15 | 5 | tolerancia | VALIDADO | 77027a6 |
| III-7 | newton | 0.943091718315147 | 6.747986e-14 | 1.536549e-13 | 3 | tolerancia | VALIDADO | 77027a6 |
| III-8 | biseccion | 0.6823277473449707 | 5.648305e-8 | 1.353737e-07 | 21 | tolerancia | VALIDADO | 77027a6 |
| III-8 | regla_falsa | 0.6823278022297578 | 1.598262e-9 | 3.830575e-09 | 14 | tolerancia | VALIDADO | 77027a6 |
| III-8 | secante | 0.6823278038280184 | 9.273695e-16 | 2.220446e-15 | 7 | tolerancia | VALIDADO | 77027a6 |
| III-8 | newton | 0.6823278038280194 | 7.263052e-17 | 2.220446e-16 | 5 | tolerancia | VALIDADO | 77027a6 |
| III-9 | biseccion | 0.2591710090637207 | 9.275535e-8 | 5.302740e-08 | 21 | tolerancia | VALIDADO | 77027a6 |
| III-9 | regla_falsa | 0.2591711023769581 | 5.578843e-10 | 3.189374e-10 | 16 | tolerancia | VALIDADO | 77027a6 |
| III-9 | secante | 0.2591711018629507 | 4.387694e-11 | 2.508407e-11 | 9 | tolerancia | VALIDADO | 77027a6 |
| III-9 | newton | 0.2591711018190734 | 3.644766e-16 | 2.220446e-16 | 5 | tolerancia | VALIDADO | 77027a6 |
| III-10 | biseccion | 2.0859341621398926 | 4.216667e-7 | 2.797819e-06 | 21 | tolerancia | VALIDADO | 77027a6 |
| III-10 | regla_falsa | 2.0859345803187512 | 3.487840e-9 | 2.314233e-08 | 13 | tolerancia | VALIDADO | 77027a6 |
| III-10 | secante | 2.0859345837975996 | 8.992064e-12 | 5.966427e-11 | 5 | tolerancia | VALIDADO | 77027a6 |
| III-10 | newton | 2.0859345838065915 | 1.640673e-16 | 1.776357e-15 | 4 | tolerancia | VALIDADO | 77027a6 |
| III-11 | biseccion | 1.275449275970459 | 3.041093e-7 | 3.269507e-07 | 21 | tolerancia | VALIDADO | 77027a6 |
| III-11 | regla_falsa | 1.2754495810580293 | 9.782925e-10 | 1.051771e-09 | 12 | tolerancia | VALIDADO | 77027a6 |
| III-11 | secante | 1.2754495801235866 | 4.384980e-11 | 4.714318e-11 | 7 | tolerancia | VALIDADO | 77027a6 |
| III-11 | newton | 1.2754495800797367 | 9.917464e-17 | 0.000000e+00 | 5 | raiz_evaluada | VALIDADO | 77027a6 |
| III-12 | biseccion | 1.332390308380127 | 1.098266e-7 | 1.356975e-07 | 21 | tolerancia | VALIDADO | 77027a6 |
| III-12 | regla_falsa | 1.3323901985535784 | 5.853924e-15 | 7.271961e-15 | 4 | tolerancia | VALIDADO | 77027a6 |
| III-12 | secante | 1.3323901985541515 | 5.789539e-13 | 7.153722e-13 | 4 | tolerancia | VALIDADO | 77027a6 |
| III-12 | newton | 1.3323901985535713 | 1.246076e-15 | 1.554312e-15 | 3 | tolerancia | VALIDADO | 77027a6 |
| III-13 | biseccion | 2.0226006507873535 | 4.535860e-7 | 2.316179e-06 | 21 | tolerancia | VALIDADO | 77027a6 |
| III-13 | regla_falsa | 2.0226001909842615 | 6.217104e-9 | 3.174685e-08 | 12 | tolerancia | VALIDADO | 77027a6 |
| III-13 | secante | 2.0226001972013528 | 1.237038e-14 | 6.328271e-14 | 5 | tolerancia | VALIDADO | 77027a6 |
| III-13 | newton | 2.0226001972013656 | 4.296197e-16 | 1.998401e-15 | 3 | tolerancia | VALIDADO | 77027a6 |
| III-14 | biseccion | 2.673062801361084 | 2.397208e-7 | 7.400733e-07 | 21 | tolerancia | VALIDADO | 77027a6 |
| III-14 | regla_falsa | 2.6730630380294467 | 3.052445e-9 | 9.423604e-09 | 11 | tolerancia | VALIDADO | 77027a6 |
| III-14 | secante | 2.673063041081892 | 1.458547e-16 | 4.440892e-16 | 7 | tolerancia | VALIDADO | 77027a6 |
| III-14 | newton | 2.6730630410820986 | 2.064541e-13 | 6.372680e-13 | 4 | tolerancia | VALIDADO | 77027a6 |
| III-15 | biseccion | 2.1646084785461426 | 3.638826e-7 | 4.130752e-07 | 21 | tolerancia | VALIDADO | 77027a6 |
| III-15 | regla_falsa | 2.1646088425025223 | 7.382010e-11 | 8.379963e-11 | 7 | tolerancia | VALIDADO | 77027a6 |
| III-15 | secante | 2.1646088423705994 | 5.810280e-11 | 6.595768e-11 | 5 | tolerancia | VALIDADO | 77027a6 |
| III-15 | newton | 2.164608842428702 | 1.991766e-16 | 0.000000e+00 | 4 | raiz_evaluada | VALIDADO | 77027a6 |
| IV-1 | biseccion | 2.219107151031494 | 2.117748e-9 | 2.801522e-09 | 21 | tolerancia | VALIDADO | 77027a6 |
| IV-1 | regla_falsa | 2.219107149289517 | 3.757710e-10 | 4.970989e-10 | 8 | tolerancia | VALIDADO | 77027a6 |
| IV-1 | secante | 2.219107148907098 | 6.648033e-12 | 8.794743e-12 | 5 | tolerancia | VALIDADO | 77027a6 |
| IV-1 | newton | 2.219107148913746 | 3.259579e-17 | 2.220446e-16 | 4 | tolerancia | VALIDADO | 77027a6 |
| IV-3 | biseccion | 1.5423961257934569 | 1.196446e-7 | 4.587560e-07 | 21 | tolerancia | VALIDADO | 77027a6 |
| IV-3 | regla_falsa | 1.5423960061480886 | 8.067807e-13 | 3.093525e-12 | 5 | tolerancia | VALIDADO | 77027a6 |
| IV-3 | secante | 1.542396006148894 | 1.380748e-15 | 5.773160e-15 | 4 | tolerancia | VALIDADO | 77027a6 |
| IV-3 | newton | 1.542396006148898 | 2.619252e-15 | 9.992007e-15 | 3 | tolerancia | VALIDADO | 77027a6 |
| IV-4 | biseccion | 0.46051931381225586 | 1.664444e-7 | 3.413287e-08 | 21 | tolerancia | VALIDADO | 77027a6 |
| IV-4 | regla_falsa | 0.4605194800321761 | 2.244734e-10 | 4.603291e-11 | 11 | tolerancia | VALIDADO | 77027a6 |
| IV-4 | secante | 0.46051948025664863 | 8.467118e-16 | 1.804112e-16 | 5 | tolerancia | VALIDADO | 77027a6 |
| IV-4 | newton | 0.46051948025668027 | 3.079329e-14 | 6.328271e-15 | 4 | tolerancia | VALIDADO | 77027a6 |

## Revisión cruzada: siete hallazgos corregidos

Segunda entrega, base `e3bdbf9` tras `git rebase main`. Se ejecutó primero la línea base:
305 pruebas Python y 46 Node OK. `tests/test_raices_revision.py` reprodujo los siete hallazgos
antes de corregirlos (8 pruebas, 12 fallos de aserción/subcasos).
Resultado final ejecutado en `59079ca`: **319 pruebas Python OK y 46 Node OK en 8 archivos**.
Se mantienen 18/18 ecuaciones y los cuatro métodos del banco; las pruebas del coordinador también pasan.

La parada del usuario y la certificación son condiciones independientes. Para declarar convergencia
se exige cambio de signo estricto alrededor de la aproximación, dominio continuo comprobado sobre
todo ese intervalo y condición de raíz válida. El radio es la tolerancia en criterios absoluto e
intervalo; para otros criterios es tolerancia*max(1,abs(x)). Es un radio en x, no el porcentaje del paso.
No se emplea f(x0) como certificado. `certificacion` informa radio, intervalo, evaluaciones y razón.
La cota de bisección continúa separada; también debe excluir cero cuando se exige raíz positiva.

Las raíces múltiples/extremos sin cambio de signo quedan **sin certificar**, incluso si f(x)=0.
Esto no afirma que no existan: evita presentar un cero flotante o un límite como existencia probada.
La certificación es conservadora cuando el análisis del dominio no puede comprobar una restricción.
El dominio usa intervalos racionales para las operaciones algebraicas y límites para funciones.
Los coeficientes/discriminantes del detector de restricciones cuadráticas se calculan con Fraction.

Nuevo motivo `no_certificada`: «El criterio de parada se alcanzó, pero no se pudo certificar una raíz
admisible cercana con cambio de signo en un intervalo continuo; puede tratarse de una raíz múltiple,
un extremo o un límite sin raíz». Coordinado con el integrador para los cuatro JS; no se editaron aquí.
Secante conserva `advertencias` como lista de str, sin objetos nuevos; Newton conserva objetos tipo/n.
Los detalles estructurados van en `certificacion`. Se ejecutó una regresión específica del contrato.

### Pruebas y corrección por hallazgo

Todos los nombres siguientes pertenecen a `TestRevisionRaices` en `tests/test_raices_revision.py`.

| Hallazgo | Prueba (prefijo test_) | Corrección | Commit |
|---|---|---|---|
| 1 | `1_raiz_cero_aproximada_no_es_positiva_no_nula`, `1_metodos_cerrados_tampoco_aceptan_cero_aproximado` | La vecindad certificada y la cota de bisección deben excluir 0 | `1badd32`, `41f88b1` |
| 2 | `2_limite_excluido_no_es_raiz_de_iv3` | Rechazar intervalo con punto excluido o sin cambio de signo | `2455949`, `1badd32` |
| 3 | `3_tan_conserva_valores_definidos` | Eliminar ajuste a cero y banda de ulp del argumento; no modificar f | `2727a79` |
| 4 | `4_cuadratica_positiva_no_inventa_polos` | Coeficientes y discriminante racionales exactos; raíces con Decimal a 80 cifras | `2727a79` |
| 5 | `5_exponencial_sin_raices_no_converge`, `5_raiz_escalada_no_depende_de_la_semilla`, `5_residuo_escalado_no_oculta_estancamiento_de_regla_falsa` | Sustituir la guarda de semilla por prueba local de existencia, también en regla falsa | `1badd32`, `41f88b1` |
| 6 | `6_division_constante_preserva_restricciones` | Reconocer división de polinomio por constante no nula | `2727a79` |
| 7 | `7_ln_cerca_del_borde_sigue_continua` | El límite de refinamientos no demuestra salto si el AST certifica dominio continuo | `b854d41`, `fd6b094` |

Se añadieron además casos de cero por subdesbordamiento, raíz múltiple, residuo pequeño lejos de una raíz,
y `test_secante_advertencias_solo_contiene_cadenas`. Todas las pruebas del archivo pasan (14 métodos).

### Resultados HTTP posteriores

Solicitudes reales a `/api/<método>/resolver`, con tolerancia 1e-6 y límite 200 salvo 7b (1000).
N = newton-raphson, S = secante, B = biseccion, F = regla-falsa. En B se usa criterio intervalo;
en N/S, absoluto; F mantiene su criterio relativo porcentual. «false» nunca presenta x como raíz validada.
F1=`x^2-5*sin(x)` y condición `positiva_no_nula`; F2=`exp(1/x)+2*x/tan(x)-2`.

| Caso | Método y entrada | HTTP | x final / f(x) | convergio y motivo |
|---|---|---|---|---|
| 1a | S F1, (0.2,0.5) | 200 | 5.8159868717845e-13 / -2.907993435891912e-12 | false, no_certificada |
| 1b | S F1, (0.25,0.75) | 200 | 2.4818392866374783e-16 / -1.2409196433187391e-15 | false, no_certificada |
| 1c | S F1, (0.75,1.25) | 200 | 1.6667945176010336e-13 / -8.33397258800489e-13 | false, no_certificada |
| 1d | B F1, [-0.2,0.1] | 200 | 9.536743164987686e-8 / -4.7683714915443656e-7 | false, raiz_no_admisible |
| 2a | N F2, -2.75 | 200 | -8.566079518344774e-7 / -4.89164264649844e-13 | false, no_certificada (dominio) |
| 2b | S F2, (-1,-0.5) | 200 | -1.5224698472669694e-6 / -1.5452084056732929e-12 | false, no_certificada (sin signo) |
| 3a | N `1e16*tan(x)`, nextafter(pi,+inf) | 200 | 3.141592653589793 / -1.2246467991473533 | true, tolerancia; f inicial=3.216245299353273 |
| 3b | N `tan(x)`, 1e16 | 200 | 1e16 / -1.2451734357184066 | false, no_certificada (precisión) |
| 4a | B `(x-100000000)/((x-100000000)^2+1)`, [99999999,100000001] | 200 | 100000000 / 0 | true, raiz_evaluada |
| 4b | B `(x-1)/((x-1)^2+1e-16)`, [0,2] | 200 | 1 / 0 | true, raiz_evaluada |
| 5a | N `exp(1e8*x)`, 1e-6 | 200 | 9.9e-7 / 9.889030319346946e42 | false, no_certificada |
| 5b | N `1e20*(x^2-2)`, sqrt(2) | 200 | 1.414213562373095 / -44408.92098500626 | true, tolerancia |
| 5c | N `1e20*(x^2-2)`, 1.5 | 200 | 1.4142135623730951 / 44408.92098500626 | true, tolerancia |
| 5d | F `1e-20*(exp(30*(x-1))-2)`, [1,2] | 200 | 1.000000000000187 / -9.999999999943911e-21 | false, no_certificada |
| 6a | B `(x-1)*(tan(x/2)/tan(x/2))`, [0.5,7] | 400 | intervalo contiene discontinuidad o polo | rechazado |
| 6b | B `(x-1)*(tan(0.5*x)/tan(0.5*x))`, [0.5,7] | 400 | mismo diagnóstico | rechazado |
| 7a | B `ln(x)+sin(x)-1.2`, [1e-16,2] | 200 | 1.275449275970459 / -3.269506534397948e-7 | true, tolerancia |
| 7b | F misma función/intervalo, límite 1000 | 200 | 1.2754499195071853 / 3.6492136845645007e-7 | true, tolerancia (400 iteraciones) |

Las respuestas completas y solicitudes están en `%TEMP%/orca-numerico-revision-http.json`, generadas por
`%TEMP%/orca-numerico-revision-http.py`; el log de la batería está en `%TEMP%/orca-numerico-revision-python.log`.
La raíz de 3a está cerca de pi y certificada: el residuo no se fabrica como cero. En 5b/5c el residuo grande
se conserva íntegro; el cambio de signo local certifica la cercanía independientemente de la semilla.

### Commits de la revisión (líneas añadidas + eliminadas)

- `d766151` test(numerical): reproducir siete hallazgos de revision cruzada — 81.
- `2727a79` fix(numerical): conservar tan y restricciones racionales exactas — 41.
- `b854d41` feat(numerical): comprobar dominio continuo con intervalos racionales — 84.
- `fd6b094` fix(continuidad): no convertir resolucion insuficiente en un salto — 9.
- `2455949` feat(numerical): certificar existencia local de raices admisibles — 42.
- `1badd32` fix(numerical): separar parada y certificacion en metodos abiertos — 38.
- `88a8f2d` test(numerical): exigir certificacion y conservar la funcion evaluada — 31.
- `461e937` test(numerical): cubrir subdesbordamiento y limites de certificacion — 32.
- `487c7e4` fix(secante): conservar advertencias como cadenas legibles — 27.
- `41f88b1` fix(numerical): extender admisibilidad certificada a metodos cerrados — 36.
- `fe24858` fix(regla-falsa): separar radio certificado y porcentaje del paso — 2.
- `59079ca` fix(biseccion): certificar con radio absoluto para criterio intervalo — 2.
- `5a260f2` docs(numerical): documentar certificacion y resultado de revision — 39.
