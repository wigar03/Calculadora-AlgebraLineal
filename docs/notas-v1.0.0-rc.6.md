# Notas de v1.0.0-rc.6

Candidata con **exportación de resultados** y documentación pública revisada.

## Novedades

- **Botón «Exportar»** en la cabecera de cada módulo, activo solo cuando hay un resultado válido y accesible con teclado:
  - **Copiar LaTeX:** documento completo con entrada, procedimiento, resultado, verificación y tablas.
  - **Exportar CSV:** UTF-8 con BOM, separador `;` y coma decimal (Excel en español), todas las iteraciones, fracciones protegidas para que no se conviertan en fechas y celdas protegidas contra fórmulas.
  - **Imprimir o guardar como PDF:** imprime solo el módulo activo, sin menús ni controles.
- Subtítulo general: «Álgebra lineal y métodos numéricos con procedimientos paso a paso».
- Documentación pública revisada: fórmulas con notación matemática de GitHub, README actualizado con enlace a la última versión y correcciones matemáticas en la guía (conteo de operaciones de LU y relación entre el determinante y la orientación).

## Validación

476 pruebas de Python y 68 de interfaz en Windows y Linux, incluida una prueba en navegador real de los 11 módulos (cálculo, exportación, impresión, móvil y sin conexión). Verificación independiente de las exportaciones con respuestas reales, también con tablas de 10 000 filas. Resultados y procedimientos de los once módulos sin cambios.

## Límites conocidos

- La compilación de los documentos LaTeX exportados se comprueba de forma estructural; no se compila con pdflatex en la CI.
- IV-2 e IV-5 del banco ampliado son incompletos en el enunciado original.
- Prerelease: los ejecutables no tienen firma digital del editor.
