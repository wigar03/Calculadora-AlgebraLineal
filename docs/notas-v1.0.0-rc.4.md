# Notas de v1.0.0-rc.4

Nueva candidata de la Calculadora de Álgebra Lineal: nuevo módulo 11, **Jacobi y Gauss-Seidel**, con análisis de convergencia demostrable y verificación exacta.

## Novedades

- **Jacobi y Gauss-Seidel** para sistemas cuadrados de $`2\times2`$ a $`10\times10`$ en la interfaz (hasta $`20\times20`$ por la API). El sistema se introduce en la rejilla $`[A\mid b]`$ o como texto, tal como se escribe en clase (`10x₁ − x₂ + 2x₃ = 6`). El vector inicial es configurable (cero por defecto), la tolerancia es de $`10^{-6}`$ y se pueden fijar el máximo de iteraciones y el criterio (cambio, residuo o ambos).
- **Procedimiento completo:** fórmula y sustitución de cada componente en las primeras iteraciones, tabla de iteraciones con 10 cifras significativas, cambio y residuo (absolutos y relativos), solución, motivo de parada y verificación por sustitución ($`Ax`$ y $`r = b - Ax`$).
- **Comparación de ambos métodos** lado a lado, con gráficas de la evolución de las incógnitas y de la convergencia en escala logarítmica.
- **Análisis de convergencia honesto:**
  - Dominancia diagonal por filas, diagonal nula y reordenamiento válido de ecuaciones completas.
  - Rango, sistemas singulares e incompatibles detectados antes de iterar.
  - Radio espectral de ambos métodos calculado y decidido en aritmética exacta (polinomio característico y prueba de Schur-Cohn), sin los errores de los autovalores en coma flotante.
  - La convergencia se informa como «demostrada», «observada» o «no asegurada». No se afirma que Gauss-Seidel sea siempre más rápido; el módulo incluye un ejemplo en el que Jacobi converge y Gauss-Seidel diverge.
- **Sin convergencias falsas:** se detectan divergencia, oscilación, estancamiento y valores no finitos. Antes de declarar «convergió», el residuo final se verifica con aritmética exacta.

## Correcciones

- El diagnóstico del ejecutable de Windows ahora cuenta los módulos a partir de la propia interfaz (antes esperaba exactamente 10 y rechazaba la versión con el módulo 11). La etiqueta `v1.0.0-rc.3` quedó sin release por este motivo.
- Los recursos de la página llevan versiones que identifican su contenido: tras actualizar, la ventana de escritorio ya no puede quedarse con JavaScript o CSS antiguos.

## Validación

420 pruebas de Python y 58 de JavaScript. Los ejemplos de la presentación de clase (diapositivas 9 y 28) y otros 15 casos se comparan con iteraciones exactas, soluciones y radios espectrales calculados con SymPy. Se probaron además 28 sistemas adversarios y se hizo una revisión cruzada entre agentes. La interfaz se comprobó en el navegador, con KaTeX en modo estricto y sin cambios en los módulos anteriores.

## Límites conocidos

- La presentación de clase tiene errores aritméticos en las diapositivas 15, 20 y 21; la calculadora muestra los valores correctos (coinciden con las tablas de las diapositivas 16 y 22).
- El análisis espectral exacto se limita a $`n \le 12`$ (salvo matrices triangulares o nilpotentes hasta $`n = 20`$).
- IV-2 e IV-5 del banco ampliado siguen incompletos en la fuente.
- Prerelease: los ejecutables no tienen firma digital del editor.
