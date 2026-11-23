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
| tan(pi/2) y divisiones por tan(pi) parecían finitas | Guardas según precisión del argumento | Puntos iniciales fuera del dominio; `df60a5e`, `415a8a6` |
| Paso diminuto podía aceptarse con residuo alto | Comprobar mejora residual escalada y conservar ambos errores | Newton exp(1e8*x)+1, secante atan(1e12*x)+2; `fef932f`, `77027a6` |
| Regla falsa aceptaba el redondeo como convergencia | Agotamiento antes de tolerancia y control de residuo unilateral | x^2-2 con tol 1e-100, exp(30*(x-1))-2; `25d2603`, `77027a6` |
| Derivación simplificada podía ampliar el dominio | Evaluar dominio original antes de f' | tan, 0*ln(x), (1/x)^0; `bdb52c3` |
| ln cerca de cero se clasificaba como asíntota del extremo | Comparar crecimiento con altura finita del borde | III-4/11 en [1e-6,2], ln y 1/x; `77027a6` |

La detección numérica de continuidad sigue siendo exploratoria para expresiones arbitrarias;
se complementa con restricciones analíticas afines/cuadráticas y trigonométricas para los casos del banco.
No se modificó `expresiones.py`. Falta, por coordinación, repetir el banco con el campo `ecuacion`
cuando el integrador incorpore el analizador; no hay ecuaciones completas pendientes con `funcion`.

## Ejecuciones y evidencia por método

Ejecutado: `python -m unittest discover tests -v`: **253 pruebas OK** (incluye 82 del banco).
Ejecutado equivalente PowerShell del bucle `node --test tests/*.cjs`: **5 archivos, 31 pruebas OK**.
La sustitución de la tabla se contrasta con funciones independientes de `math`; Newton se contrasta
además con diferencias finitas y su recurrencia, y los métodos cerrados conservan cambio de signo.
Las filas siguientes proceden de HTTP real ejecutado en `77027a6`; todas tienen estado VALIDADO.

| Ejercicio | Método | Raíz calculada | Diferencia absoluta vs referencia anterior | Residuo | Iteraciones | Parada | Estado | Commit |
|---|---|---|---|---|---|---|---|---|
