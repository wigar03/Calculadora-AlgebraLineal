# Notas de v1.0.0-rc.7

Candidata de **consolidación**: las exportaciones se validaron con herramientas reales y se corrigieron los defectos
encontrados. No hay módulos nuevos ni cambios en la interfaz; los resultados de los once módulos no cambian.

## Correcciones

- **CSV más seguro:** un texto con espacios o saltos de línea antes de `=`, `+`, `-` o `@` ya no puede convertirse en
  fórmula al abrirlo en una hoja de cálculo (también en las cabeceras).
- **CSV más fiel:** fracciones como `1/2` y enteros de más de 15 cifras se conservan exactos y no se convierten en
  fechas; `1/0` ya no se exporta como fracción; el cero se escribe siempre `0`.
- **LaTeX que compila:** matrices de hasta 20 columnas, porcentajes con el idioma español, tablas largas ajustadas al
  ancho de la página, barra invertida sin llaves sobrantes, letras griegas y símbolos con su comando; los caracteres
  sin soporte se muestran como `[U+XXXX]`.
- **Servidor:** una petición demasiado grande recibe siempre el mensaje del límite, no un corte de conexión.
- **Guía matemática:** la fórmula de Gauss-Seidel vuelve a mostrar sus dos sumatorios en GitHub.

## Validación

- 37 documentos LaTeX exportados compilados con pdflatex en dos pasadas, sin desbordar el margen.
- CSV abierto, guardado y reabierto con LibreOffice Calc y Gnumeric, sin pérdida de significado.
- Cuatro cálculos de 10 000 iteraciones simultáneos dentro de los límites de tiempo, memoria y tamaño.
- CI en Linux, Windows y un entorno con TeX Live, LibreOffice y Gnumeric.

## Límites conocidos

- No se probó con Microsoft Excel (no disponible). Las hojas de cálculo guardan 15 cifras significativas por número.
- Los textos protegidos con apóstrofo lo muestran en LibreOffice Calc.
- IV-2 e IV-5 del banco ampliado son incompletos en el enunciado original.
- Prerelease: los ejecutables no tienen firma digital del editor.
