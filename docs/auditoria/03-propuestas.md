# Auditoría 3/4 — Propuestas evaluadas (para autorizar desde Orca)

Campos de cada propuesta: (1) qué es · (2) problema · (3) público · (4) hoy · (5) beneficio · (6) complejidad
(S < 1 día de agente, M 1-3 días, L > 3 días) · (7) reutiliza · (8) riesgos · (9) UX · (10) pruebas · (11) prioridad.
Clases: **I** indispensable, **V** alto valor, **A** avanzada (más adelante).

## Indispensables
**P1. Robustez del servidor y límites coherentes (I).** (1) Servidor con hilos y tiempo máximo por cálculo, límite
de cuerpo, límites de n validados en Python (los mismos de la UI), JSON inválido con 400 claro, mensajes sin
textos de Python, `Cache-Control: no-cache`, sin listado de directorios, errores escapados (AU-01 a AU-10).
(2) Un cofactor n = 10 congela la app 56 s. (3) Todos. (4) Sin límites en la API. (5) Fiabilidad en clase.
(6) S-M. (7) `config.py`, `_send_json`. (8) Bajo, si se mide el rendimiento. (9) Ninguno. (10) HTTP de límites,
JSON inválido, concurrencia, tiempo máximo y escape. (11) **1.ª**.

**P2. Copiar, imprimir y exportar el procedimiento (I).** (1) Botones «Copiar LaTeX» y «Copiar tabla (CSV)»,
y una hoja `@media print` para imprimir o guardar como PDF desde el navegador o la ventana. (2) El docente no puede
sacar el procedimiento de la pantalla. (3) Estudiantes y docentes. (4) Nada. (5) Tareas, informes y
diapositivas. (6) M. (7) KaTeX ya genera el LaTeX; requiere el formato común de pasos (ver 04). (8) Bajo.
(9) **Sí**: botones nuevos en cada módulo y estilos de impresión. (10) Contenido copiado, CSV válido, impresión sin
cortes. (11) **2.ª**.

## Alto valor
**P3. Integración numérica (V).** (1) Trapecio y Simpson 1/3 y 3/8 compuestos, Romberg y Gauss-Legendre, con tabla,
error estimado y gráfica del área. (2) Tema estándar de métodos numéricos ausente. (3) Ingeniería y ciencias.
(4) No existe. (5) Alto. (6) M. (7) Analizador de f(x), dominio, `grafica-funciones.js`, patrón de los métodos.
(8) Singularidades en el intervalo: reutilizar `continuidad.py`. (9) Módulo nuevo con el patrón actual.
(10) Integrales exactas con SymPy y orden de convergencia observado. (11) **3.ª**.

**P4. Interpolación y mínimos cuadrados (V).** (1) Lagrange, diferencias divididas de Newton; regresión lineal,
polinómica y exponencial por ecuaciones normales exactas, con R² y residuos; sistemas sobredeterminados Ax ≈ b.
(2) Ajuste de datos de laboratorio. (3) Ingeniería y ciencias. (4) No existe. (5) Alto. (6) M. (7) Gauss exacto,
`Fraction`, gráficas. (8) Mal condicionamiento de las ecuaciones normales con grado alto: limitar el grado o usar QR.
(9) Módulo nuevo; editor de puntos (x, y). (10) Contra SymPy y `numpy.polyfit` solo en pruebas. (11) **4.ª**.

**P5. Valores y vectores propios (V).** (1) Polinomio característico exacto, valores propios (racionales exactos;
el resto certificados), vectores propios por núcleo exacto, multiplicidades y diagonalizabilidad, para n ≤ 6.
(2) Tema central del curso ausente. (3) Álgebra lineal. (4) Solo el radio espectral interno del módulo 11.
(5) Alto. (6) M. (7) `convergencia.py` (Faddeev-LeVerrier, aislamiento racional) y `gauss_solver` (núcleo).
(8) Raíces complejas y múltiples: mostrar intervalos certificados, nunca falsos decimales. (9) Módulo nuevo.
(10) Contra SymPy `eigenvals`/`eigenvects`. (11) **5.ª**.

**P6. Espacios fundamentales y descomposiciones (V).** Rango, núcleo, espacio columna y fila, independencia y base;
LU (ya existe dentro del determinante) y Cholesky (ya existe `definida_positiva`) como módulos. (6) S-M. (9) Módulo
nuevo. (11) Tras P5.

**P7. Punto fijo (V).** Método 5 de raíces con g(x), |g'| como criterio y diagrama de telaraña. (6) S. (7) Todo el
andamiaje de raíces y la derivada. (11) Barato, pero de menor valor que P3 y P4.

**P8. Elección de pivote y celdas con expresiones (V).** Pivote «natural» o parcial en Gauss, inversa y LU, y celdas
con `sqrt(2)` o `pi` en un modo aproximado declarado. (8) Mezclar exacto y flotante: debe ser explícito. (9) **Sí**:
controles nuevos en los módulos existentes. (11) Consultar.

## Avanzadas (más adelante)
**P9. Varias variables** (prerrequisito): analizador con `x, y, z` y derivadas parciales. Habilita **P10. EDO**
(Euler, Heun, RK4 para y' = f(x, y), con solución exacta comparada) y **P11. Newton para sistemas no lineales**
con jacobiano simbólico. (6) L. (8) Seguridad del analizador: misma lista blanca.
**P12. Cálculo simbólico** (límites, series, integrales exactas, optimización): requiere un CAS (SymPy, unos 30 MB
en el instalador) o un motor propio limitado. (6) L. (8) Peso y tiempos. (11) Decidir más adelante.
**P13. Historial y guardado de sesión** (localStorage o archivo). (9) **Sí**. **P14. Visualización** de rectas y
planos de sistemas 2×2 y 3×3 y de vectores en ℝ². **P15. Accesibilidad completa** (pestañas ARIA, etiquetas de celdas,
movimiento reducido, `prefers-color-scheme`), parcialmente sin cambio visible. **P16. Linux y macOS** (CI e instaladores).
