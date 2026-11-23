Segunda candidata de la Calculadora de Álgebra Lineal: resuelve y verifica los 47 ejercicios con enunciado completo del banco de sistemas lineales, matrices y ecuaciones no lineales.

### Novedades

- **Ecuaciones escritas como en clase**: se aceptan igualdades (`ln(x) + sen(x) = 1.2`), `sen`, `e^x` y `e^(−x)`, `·`, `−` y superíndices `x²`, `x³`, `x⁴`.
- **Mensajes de error que dicen qué corregir**: `2x + 3 = 7` responde «falta el operador de multiplicación entre 2 y x. Escribe 2*x + 3 = 7». También se señalan paréntesis sin cerrar, operadores dobles, funciones desconocidas (con sugerencia), variables no reconocidas e igualdades mal formadas. Los errores de dominio (ln, raíz, división por cero, polos de tan) se distinguen de los de sintaxis.
- **Raíces certificadas**: los cuatro métodos solo informan convergencia si comprueban un cambio de signo en un intervalo continuo alrededor de la raíz. Si no pueden certificarla (raíz múltiple, extremo o acercamiento a un punto fuera del dominio), lo dicen en lugar de dar un resultado engañoso.
- **Dominio y polos**: los intervalos que contienen polos o discontinuidades se rechazan antes de iterar.
- **Sistemas lineales**: se corrigió la «Eliminación Gaussiana + Sustitución Regresiva», que daba soluciones incorrectas. Los sistemas con infinitas soluciones muestran la familia paramétrica exacta y la verifican fila por fila.

### Ejercicios del banco que ahora se resuelven

- Sistemas lineales I-1 a I-19 (incluidos el de cinco incógnitas, los de coeficientes fraccionarios y decimales exactos y el sistema con infinitas soluciones): 19/19.
- Determinante e inversa II-1 a II-10, con A·A⁻¹ = I: 10/10.
- Ecuaciones no lineales III-1 a III-15 y IV-1, IV-3, IV-4 con los cuatro métodos: 18/18.

### Validación

322 pruebas de Python y 52 de JavaScript. Cada ejercicio se compara con referencias independientes calculadas con SymPy y mpmath, por la API de la página y en el navegador. KaTeX se comprueba en modo estricto sin errores.

### Límites conocidos

- Los ejercicios IV-2 y IV-5 del banco ampliado no incluyen la igualdad completa en el documento original; no se resuelven hasta conocer el enunciado.
- La multiplicación debe escribirse con `*` (por ejemplo `4*x`); la calculadora lo indica, pero no lo corrige sola.
- La página no tiene un control para pedir «raíz positiva no nula»; los datos iniciales eligen la raíz.
- Sigue siendo una prerelease: los ejecutables no tienen firma digital del editor y Windows puede mostrar una advertencia.
