# Historial de versiones

## 1.3.0

Añade apoyo gráfico en el plano y completa los controles de Newton-Raphson,
sin cambiar los resultados matemáticos de los once módulos.

- Gráficas en $`ℝ^2`$ en Vectores, Combinación lineal y Ecuaciones con dos incógnitas;
  se muestran solo cuando la dimensión es 2.
- Vectores: flechas de entrada y resultado, paralelogramo de la suma y ángulo en el producto punto.
- Combinación lineal: descomposición punta-cola hasta el objetivo y relación de dependencia con objetivo cero.
- Ecuaciones: rectas etiquetadas, intersección, paralelas y coincidentes, incluidas verticales y horizontales.
- Gráficas orientativas y visibles al imprimir; las exportaciones LaTeX y CSV se conservan.
- Newton-Raphson muestra el porcentaje de zoom y reescala el eje vertical al enfocar la raíz,
  como Bisección y Regla Falsa; quedan completadas las mejoras aplazadas de la auditoría de coherencia.
- Límites de v1.2.0 conservados: ejercicios 46 y 49 incompletos, ejecutables sin firma digital
  que Windows puede bloquear según sus políticas y Excel no verificado directamente.

Consulta las instrucciones de uso y los límites en las [notas de v1.3.0](docs/notas-v1.3.0.md).

## 1.2.0

Mejora la entrada de datos, los controles de las gráficas y el uso táctil de los once módulos,
sin cambiar los resultados matemáticos.

- Aviso de las casillas vacías tomadas como 0 en los módulos con rejilla, conservando ese comportamiento.
- Inversa admite matrices de un solo elemento desde la interfaz; Cofactores se desactiva con explicación
  por encima de orden 6 y se selecciona LU.
- Vista previa de la función en Newton-Raphson y Secante; iconos y botones unificados en los módulos 07–11.
- Exportación del resultado de «Solo analizar matriz» en Jacobi y Gauss-Seidel.
- «Enfocar raíz» en Regla Falsa y coordenadas bajo el cursor en Bisección.
- Áreas táctiles de 44 píxeles y campos en una columna en pantallas de hasta 480 píxeles.
- Límites de v1.1.0 conservados: ejercicios 46 y 49 incompletos, ejecutables sin firma y Excel no verificado
  directamente; aplazadas las gráficas en el plano y el porcentaje de zoom y reescalado vertical en Newton.

Consulta las instrucciones de uso y los límites en las [notas de v1.2.0](docs/notas-v1.2.0.md).

## 1.1.0

Amplía el trabajo con el banco final y la interpretación de los métodos de raíces.

- Ejercicios 50–64: sistemas rectangulares, operaciones encadenadas con «Usar resultado como A» e independencia lineal.
- Ecuaciones muestra $`A\cdot X=B`$ antes de la matriz aumentada, también en la exportación LaTeX.
- Con objetivo cero, Combinación lineal incluye dictamen, relación no trivial, despeje y verificación algebraica exacta;
  si el conjunto es independiente, justifica mediante el rango que solo existe la solución trivial.
- Los cuatro métodos de raíces informan el orden observado y la constante asintótica cuando hay datos suficientes.
- Selector de condición: cualquier raíz real, positiva o positiva no nula; «Recomendar método» ofrece orientación
  previa razonada, sin garantizar convergencia ni una raíz admisible.
- Auditoría de coherencia: certificación con unidades porcentuales correctas y avisos visibles; diagnóstico de coma
  decimal; signo menos Unicode y superíndices; correcciones de impresión y accesibilidad; Regla Falsa a 10 cifras
  significativas en la presentación, conservando la precisión interna.
- Límites: los ejercicios 46 y 49 conservan enunciados incompletos; ejecutables sin firma digital y Excel no
  verificado directamente; gráficas, recomendación y orden observado son orientativos.

Consulta las instrucciones de uso y los límites en las [notas de v1.1.0](docs/notas-v1.1.0.md).

## 1.0.0

Primera versión estable; consolida el trabajo de las candidatas rc.1 a rc.7.

- Once módulos de álgebra lineal y métodos numéricos con procedimientos paso a paso y verificación de resultados.
- Aritmética exacta en álgebra lineal, certificación de raíces y análisis de convergencia de Jacobi y Gauss-Seidel.
- Robustez: ejecución aislada, límites de recursos y diagnósticos de sintaxis, dominio y convergencia.
- Exportación LaTeX/CSV e impresión o PDF; validada con pdflatex, LibreOffice Calc y Gnumeric reales.
- Instalador por usuario y paquete portable para Windows x64, con recursos locales para trabajar sin conexión.
- Límites: ejecutables sin firma digital; Excel de escritorio y Excel para la Web no verificados directamente.

Consulta los requisitos, instalación, verificaciones y límites en las [notas de v1.0.0](docs/notas-v1.0.0.md).

## 1.0.0-rc.7

Candidata de consolidación: exportaciones validadas con pdflatex, LibreOffice Calc y Gnumeric reales.

- CSV protegido contra fórmulas precedidas de espacios; fracciones, enteros largos y ceros conservados.
- Documentos LaTeX que compilan con matrices grandes, tablas largas, porcentajes, griego y Unicode.
- Fórmula de Gauss-Seidel de la guía corregida en GitHub.
- Mensaje del límite garantizado ante peticiones demasiado grandes.

## 1.0.0-rc.6

Candidata con exportación de resultados (P2) y documentación pública revisada.

- Botón «Exportar» por módulo: copiar LaTeX, CSV para Excel en español e impresión o PDF.
- Subtítulo general sin enumerar métodos.
- Fórmulas de la documentación con notación matemática de GitHub y correcciones verificadas en la guía.

## 1.0.0-rc.5

Candidata de robustez; resultados y procedimientos de los once módulos sin cambios.

### Incluido

- Cálculos en procesos aislados con tiempo, memoria y tamaño de respuesta acotados.
- Límites iguales en interfaz, servidor y motores; cofactores hasta $`6\times6`$ con LU recomendado; Bareiss como comprobación.
- Errores uniformes en español sin texto interno; cabeceras de seguridad y peticiones solo locales.
- Formato común de procedimientos en la API y biblioteca de exportación preparada (sin cambios visibles).

## 1.0.0-rc.4

Candidata con el módulo 11, Jacobi y Gauss-Seidel. (La etiqueta `v1.0.0-rc.3` no se publicó: la CI del
ejecutable falló porque su diagnóstico esperaba exactamente 10 módulos; corregido en esta versión.)

### Incluido

- Jacobi y Gauss-Seidel con entrada por rejilla o texto, vector inicial, tolerancia, máximo de iteraciones y criterio.
- Desarrollo paso a paso, tabla con 10 cifras, residuo, verificación por sustitución y comparación con gráficas.
- Análisis exacto de convergencia: dominancia, diagonal nula, reordenamiento, rango y radio espectral exacto.
- Verificación exacta del residuo antes de declarar convergencia; detección de divergencia, oscilación y estancamiento.
- Versiones de recursos web ligadas al contenido para evitar copias antiguas en caché.

### Límites

- Análisis espectral exacto hasta $`n = 12`$; la presentación de clase tiene errores en las diapositivas 15, 20 y 21.

## 1.0.0-rc.2

Segunda candidata: resuelve y verifica los 47 ejercicios con enunciado completo del banco de ejercicios.

### Incluido

- Ecuaciones con la notación habitual: igualdades, `sen`, `e^x`, `·`, `−` y superíndices.
- Diagnósticos específicos de sintaxis y de dominio que indican qué corregir y cómo.
- Certificación de raíces por cambio de signo en los cuatro métodos; sin convergencias engañosas.
- Rechazo de intervalos con polos o discontinuidades antes de iterar.
- Corrección de Gauss con sustitución regresiva y solución paramétrica verificada de sistemas SCI.

### Límites

- IV-2 e IV-5 del banco ampliado no tienen la igualdad completa en la fuente.
- La multiplicación se escribe con `*`; los ejecutables siguen sin firma digital.

## 1.0.0-rc.1

Primera candidata pública de la Calculadora de Álgebra Lineal.

[Publicación original de v1.0.0-rc.1](https://github.com/wigar03/Calculadora-AlgebraLineal/releases/tag/v1.0.0-rc.1)
· [Notas históricas](docs/notas-v1.0.0-rc.1.md).

### Incluido

- Diez módulos de álgebra lineal y métodos numéricos con procedimientos y verificación.
- Ventana de escritorio Windows que reutiliza el motor Python y la interfaz web.
- Instalador en español por usuario y paquete portable para Windows x64.
- KaTeX, fuentes y licencias distribuidos localmente para trabajar sin conexión.
- Cierre del servidor al cerrar la ventana y diagnóstico del ejecutable empaquetado.
- Pruebas automáticas de cálculos, API, recursos y ciclo de instalación.
- README orientado al usuario y guía matemática conservada por separado.

### Requisitos y límites

- Windows 10/11 x64 y Microsoft Edge WebView2 Runtime.
- Si falta WebView2, el setup requiere conexión para instalarlo; los cálculos son locales.
- Los instaladores de esta candidata no tienen firma digital del editor.
- Todavía no hay instaladores validados para macOS/Linux ni un sitio público alojado.
- No incluye guardado de cálculos, exportación ni actualizaciones automáticas.
- Las gráficas son orientativas; los métodos iterativos pueden no converger.

Esta publicación es una **prerelease**, no la declaración de estabilidad `1.0.0`.
Los problemas se pueden comunicar en los issues del repositorio indicando módulo,
entradas, resultado esperado, resultado obtenido y versión de Windows.
