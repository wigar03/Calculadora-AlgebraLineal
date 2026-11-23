# Notas de v1.0.0-rc.5

Candidata centrada en **robustez**: ningún cálculo puede bloquear la aplicación y los errores se explican con claridad. Los resultados y procedimientos de los once módulos no cambian.

## Novedades

- **Cálculos aislados y cancelables:** cada cálculo se ejecuta en un proceso aparte con tiempo máximo (10 s), memoria (512 MB) y tamaño de respuesta (4 MB) limitados. Si se excede, el proceso se termina y se sustituye; el resto de la aplicación sigue respondiendo.
- **Límites coherentes** entre la interfaz y el motor: los mismos tamaños máximos se validan en la página, en el servidor y en cada módulo, antes de calcular.
- **Determinante:** la expansión por cofactores se limita a matrices de hasta $`6\times6`$ (con $`7\times7`$ su procedimiento ya superaría 1 MB). Para órdenes mayores, la calculadora recomienda LU. El valor se comprueba además con el método de Bareiss.
- **Errores claros y uniformes:** JSON inválido, números desmesurados o datos mal formados reciben un mensaje en español; nunca se muestra texto interno de Python.
- **Seguridad del servidor local:** solo acepta peticiones de la propia aplicación, envía cabeceras de seguridad, no lista directorios y muestra los mensajes de error como texto (sin interpretar HTML).
- **Base para exportar** (copiar LaTeX, tablas CSV, PDF): formato común de procedimientos ya disponible en la API; los controles se añadirán tras aprobar su diseño.

## Validación

457 pruebas en Windows y en Linux, 66 de interfaz. Las 43 respuestas de referencia de los 11 módulos se mantienen idénticas. Mediciones antes y después en el repositorio: una petición trivial pasó de esperar 5,4 s durante un cálculo pesado a responder al instante, y los casos que generaban respuestas de hasta 125 MB se rechazan en milisegundos.

## Límites conocidos

- Cofactores solo hasta $`6\times6`$ (LU sigue disponible hasta $`8\times8`$).
- IV-2 e IV-5 del banco ampliado son incompletos en el enunciado original.
- Prerelease: los ejecutables no tienen firma digital del editor.
