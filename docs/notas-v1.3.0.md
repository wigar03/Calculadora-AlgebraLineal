# Notas de v1.3.0

Esta versión añade gráficas geométricas en el plano y completa los controles de Newton-Raphson.
Conserva los once módulos, los resultados matemáticos y las capacidades de [v1.2.0](notas-v1.2.0.md).
Quedan completadas las mejoras aplazadas de la auditoría de coherencia.

## Gráficas en el plano

Al resolver con dimensión 2, **Vectores**, **Combinación lineal** y **Ecuaciones** muestran una gráfica
en $`ℝ^2`$ junto al procedimiento. En otras dimensiones, la gráfica permanece oculta.
La escala se ajusta a los datos y muestra ejes con marcas y etiquetas.

- **Vectores:** representa $`u`$, $`v`$ y el resultado con flechas desde el origen para suma, resta y
  producto por escalar. En la suma muestra el paralelogramo; en el producto punto, el ángulo entre
  los vectores. Si alguno es nulo, indica que el ángulo no está definido.
- **Combinación lineal:** representa los vectores generadores y el objetivo $`b`$. Cuando existe una
  combinación, muestra la descomposición punta-cola hasta $`b`$; si hay infinitas, dibuja una de ellas
  fijando los parámetros libres a cero. Con $`b=0`$ y un conjunto dependiente, representa una relación
  no trivial cuya cadena regresa al origen.
- **Ecuaciones con dos incógnitas:** representa cada ecuación como una recta etiquetada, incluidas
  verticales y horizontales. Muestra el punto de intersección cuando hay solución única, las rectas
  coincidentes cuando hay infinitas soluciones y las paralelas o la ausencia de un punto común
  cuando el sistema es incompatible. Admite distinto número de ecuaciones e incógnitas.

Estas gráficas son **orientativas**: no sustituyen el procedimiento ni la verificación exacta.
Las fracciones se convierten a aproximaciones solo para dibujar; el resultado conserva sus valores exactos.
Son visibles al imprimir o guardar como PDF y utilizan los temas claro y oscuro de la aplicación.
Las exportaciones LaTeX y CSV se conservan sin cambios.

## Zoom y enfoque en Newton-Raphson

La gráfica incorpora un indicador del porcentaje de zoom. Al pulsar **Enfocar raíz**, centra la vista
en la aproximación obtenida y reajusta también el eje vertical, como en Bisección y Regla Falsa.
Este ajuste facilita observar la curva cerca de la raíz; conserva el resultado y las iteraciones.

## Instalación y límites conocidos

Consulte el [README](../README.md#instalar-en-windows) para instalar en Windows 10/11 x64 con WebView2,
usar el ZIP portable o ejecutar desde el código. Las descargas y sus sumas SHA-256 se ofrecen en las
[publicaciones oficiales](https://github.com/wigar03/Calculadora-AlgebraLineal/releases/latest).

Se mantienen los límites de [v1.2.0](notas-v1.2.0.md). Los ejercicios 46 y 49 siguen sin igualdad completa
en el enunciado original (IV-2 e IV-5); no se les asigna una solución inventada. Los ejecutables siguen
**sin firma digital**: Windows puede advertir o impedir su ejecución según las políticas de seguridad del equipo.
Excel de escritorio y Excel para la Web **no están verificados directamente**; las comprobaciones previas
con LibreOffice Calc y Gnumeric no sustituyen esa prueba.

Las gráficas, la recomendación y el orden observado son orientativos; los métodos pueden no converger.
La certificación por cambio de signo puede no demostrar una raíz múltiple o una raíz en un extremo.

Los fundamentos y las instrucciones de cada módulo se conservan en la [guía matemática](guia-matematica.md).
