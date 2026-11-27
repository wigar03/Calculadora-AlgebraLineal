# Notas de v1.2.0

Esta versión mejora las entradas, los controles y el uso en pantallas táctiles de la Calculadora de Álgebra Lineal.
Conserva los once módulos, sus resultados matemáticos, los cálculos locales y las capacidades de v1.1.0.

## Casillas vacías y matrices pequeñas

En los módulos con rejilla —Vectores, Combinación lineal, Matrices, Inversa, Ecuaciones, Determinante y
Jacobi/Gauss-Seidel— las casillas vacías siguen contando como cero. El resultado ahora indica cuáles se tomaron
como 0, con nombres como `A[2,3]` o `b[1]`. El aviso se limpia al recalcular, limpiar o cargar un ejemplo.

**Inversa** permite matrices de orden 1 a 6 desde la interfaz. Para una matriz de un solo elemento no nulo,
la inversa contiene su recíproco; la matriz de un solo cero se reconoce como singular.

En **Determinante**, al elegir un orden mayor que 6 se desactiva **Cofactores**, se selecciona **LU** y aparece
una explicación junto al control. Al volver a orden 6 o inferior, Cofactores queda disponible otra vez.
Los límites de cálculo se conservan: cofactores hasta orden 6 y LU hasta orden 8.

## Funciones, gráficas y controles

- **Newton-Raphson y Secante** incorporan la vista previa matemática de la función mientras escribe, como
  Bisección y Regla Falsa. Permite revisar la notación; no comprueba el dominio ni demuestra continuidad.
- **Regla Falsa** añade **Enfocar raíz** para centrar la gráfica en la aproximación obtenida.
- **Bisección** muestra las coordenadas de la posición del cursor al recorrer la gráfica.
- Los módulos **07–11** comparten los iconos y estilos de los botones de zoom y limpieza.

## Exportar el análisis de Jacobi y Gauss-Seidel

Después de **Solo analizar matriz**, puede usar **Exportar** para copiar LaTeX, descargar CSV o imprimir y
guardar como PDF. El procedimiento contiene el análisis de la matriz sin tener que ejecutar las iteraciones.

## Uso táctil y pantallas estrechas

En dispositivos táctiles, los botones y controles ajustados ofrecen áreas de al menos 44 píxeles; las celdas
de las rejillas alcanzan esa altura mínima. Los campos de los métodos numéricos se disponen en una columna
cuando el ancho de la pantalla es de 480 píxeles o menos.

## Instalación y límites conocidos

Consulte el [README](../README.md#instalar-en-windows) para instalar en Windows 10/11 x64 con WebView2,
usar el ZIP portable o ejecutar desde el código. Las descargas y sus sumas SHA-256 se ofrecen en las
[publicaciones oficiales](https://github.com/wigar03/Calculadora-AlgebraLineal/releases/latest).

Se mantienen los límites de [v1.1.0](notas-v1.1.0.md). Los ejercicios 46 y 49 siguen sin igualdad completa
en el enunciado original (IV-2 e IV-5); no se les asigna una solución inventada. Los ejecutables siguen
**sin firma digital**. Excel de escritorio y Excel para la Web **no están verificados directamente**;
las comprobaciones previas con LibreOffice Calc y Gnumeric no sustituyen esa prueba.

Las gráficas, la recomendación y el orden observado son orientativos; los métodos pueden no converger.
La certificación por cambio de signo puede no demostrar una raíz múltiple o una raíz en un extremo.
Quedan aplazadas las gráficas geométricas en el plano, el indicador de porcentaje de zoom y el reescalado
vertical al enfocar la raíz en Newton-Raphson.

Los fundamentos y las instrucciones de cada módulo se conservan en la [guía matemática](guia-matematica.md).
