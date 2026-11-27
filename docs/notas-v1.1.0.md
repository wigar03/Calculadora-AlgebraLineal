# Notas de v1.1.0

Esta versión amplía la Calculadora de Álgebra Lineal para practicar el banco final y revisar el razonamiento
de los métodos numéricos. Conserva los once módulos, los cálculos locales y los procedimientos exportables.

## Banco final: ejercicios 50–64

| Ejercicios | Módulo y uso |
|---|---|
| 50–54 | **Ecuaciones:** introducir la matriz rectangular y los términos independientes; revisar clasificación, solución y verificación. |
| 55–59 | **Matrices:** encadenar las operaciones del enunciado con «Usar resultado como A». |
| 60–64 | **Combinación lineal:** introducir los vectores y un objetivo cero para estudiar su independencia. |

Los resultados se contrastan con referencias independientes; el alcance se registra en
[Validación de ejercicios](VALIDACION-EJERCICIOS.md). Los ejercicios 46 y 49 siguen sin igualdad completa en
el enunciado original (IV-2 e IV-5); no se les asigna una ecuación ni una solución inventada.

En **Ecuaciones**, el procedimiento empieza con $`A\cdot X=B`$: muestra la matriz de coeficientes, el vector
columna de incógnitas y el de términos independientes antes de la matriz aumentada, también en LaTeX.
Admite distinto número de ecuaciones e incógnitas.

En **Matrices**, calcule primero una operación y pulse **Usar resultado como A** para continuar; por ejemplo,
obtenga $`2A`$, reutilícelo y sume $`B`$. Se conservan las fracciones exactas, los valores de B y el escalar.

Con objetivo cero, **Combinación lineal** muestra dictamen y rango. Para un conjunto dependiente, presenta
una relación con coeficientes no todos nulos, despeja un vector y comprueba ambas igualdades componente a
componente con fracciones exactas. Para uno independiente, el rango justifica que solo existe la solución trivial.

## Elegir y revisar un método de raíces

En Bisección, Regla Falsa, Newton-Raphson y Secante puede elegir la **Condición de la raíz**: cualquier raíz
real, positiva o positiva no nula. Las opciones positivas excluyen $`x=0`$. La condición se conserva en el
procedimiento exportado; si la aproximación no la cumple, el resultado lo indica.

Tras introducir función e intervalo o puntos iniciales, **Recomendar método** examina esos datos y explica
la orientación para los cuatro métodos. Puede señalar falta de cambio de signo, restricciones de dominio,
derivada poco útil o puntos iniciales inadecuados. La recomendación no ejecuta la resolución ni elige los puntos
por usted: revise las razones y complete los datos del método que vaya a usar. No garantiza convergencia ni
una raíz que cumpla la condición elegida.

El resultado incorpora **Convergencia observada**: clasificación lineal, superlineal, cuadrática o no concluyente,
con estimaciones del orden $`p`$ y la constante asintótica $`C`$ cuando el historial lo permite. Se calculan a
partir de diferencias entre aproximaciones sucesivas, sin conocer el error verdadero respecto de la raíz.
Pocas iteraciones útiles, cambios inestables o redondeo pueden impedir estimarlas. En bisección describen la
contracción de esos cambios. Esta observación no demuestra convergencia ni sustituye la certificación de la raíz.

Para la docencia, puede comparar los historiales, revisar el residuo y discutir cuándo el orden observado coincide
con lo esperado para cada método. Las fórmulas y sus límites se explican en la [guía matemática](guia-matematica.md).

## Correcciones de coherencia y presentación

- La certificación respeta las unidades de la tolerancia porcentual y muestra avisos cuando no puede certificar
  una raíz cercana, aunque se haya alcanzado el criterio de parada.
- Las entradas de raíces diagnostican la coma decimal y piden usar punto; el CSV para hojas en español mantiene
  su coma decimal. Se admite el signo menos Unicode `−` y superíndices como `x¹⁰` y `10⁻⁶`.
- Se corrigen la impresión de resultados y elementos de accesibilidad, incluidos nombres de controles y avisos.
- Regla Falsa presenta los valores con hasta 10 cifras significativas; el redondeo de pantalla no modifica el cálculo.

## Instalación y límites conocidos

Consulte el [README](../README.md#instalar-en-windows) para instalar en Windows 10/11 x64 con WebView2,
usar el ZIP portable o ejecutar desde el código. Las descargas y sus sumas SHA-256 se ofrecen en las
[publicaciones oficiales](https://github.com/wigar03/Calculadora-AlgebraLineal/releases/latest).

Los ejecutables siguen **sin firma digital**. Excel de escritorio y Excel para la Web **no están verificados
directamente**; las comprobaciones previas de CSV con LibreOffice Calc y Gnumeric no sustituyen esa prueba.
Las gráficas, la recomendación y el orden observado son orientativos; los métodos pueden no converger.
La certificación por cambio de signo puede no demostrar una raíz múltiple o una raíz en un extremo.
