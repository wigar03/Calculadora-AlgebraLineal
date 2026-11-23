# Historial de versiones

## 1.0.0-rc.3

Tercera candidata: módulo 11, Jacobi y Gauss-Seidel.

### Incluido

- Jacobi y Gauss-Seidel con entrada por rejilla o texto, vector inicial, tolerancia, máximo de iteraciones y criterio.
- Desarrollo paso a paso, tabla con 10 cifras, residuo, verificación por sustitución y comparación con gráficas.
- Análisis exacto de convergencia: dominancia, diagonal nula, reordenamiento, rango y radio espectral exacto.
- Verificación exacta del residuo antes de declarar convergencia; detección de divergencia, oscilación y estancamiento.
- Versiones de recursos web ligadas al contenido para evitar copias antiguas en caché.

### Límites

- Análisis espectral exacto hasta n = 12; la presentación de clase tiene errores en las diapositivas 15, 20 y 21.

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
