# Auditoría 4/4 — Arquitectura, roadmap y recomendación

## Arquitectura: qué cambiar solo cuando haga falta
| Ajuste | Justificación concreta | Cuándo |
|---|---|---|
| Tabla de rutas y validación común del cuerpo en `web_server.py` | Cada módulo amplía un `if/elif`; JSON inválido y cuerpos que no son objeto fallan de formas distintas (AU-04, AU-05) | Con P1 |
| Límites centralizados en `config.py` aplicados en Python | La UI y la API divergen (AU-03); `MAX_DIMENSION_SUGERIDA` existe pero no se usa | Con P1 |
| Servidor con hilos y presupuesto de tiempo por operación | Un cálculo bloquea toda la app (AU-02) | Con P1 |
| Formato común de procedimiento `Paso {titulo, descripcion_latex, matriz?, detalles}` con adaptadores | Exportar e historial necesitan una sola forma; hoy hay cuatro (`Step`, `PasoDeterminante`, listas, dicts) | Con P2 |
| Formateo numérico JS único (`formatear`, `numeroLatex`) | Tres copias divergentes (bisección, regla falsa, gráficas) | Al tocar esos archivos |
| Analizador con varias variables | Prerrequisito de EDO, Newton multivariable y funciones de dos variables | Con P9 |
| Renombrar `regla_falsa/dominio.py` a `dominio_numerico.py` | Dos `dominio.py` distintos confunden | Oportunista |
| Retirar el código muerto de `anterior_programa.py` | Rutas fijas de otra máquina y subprocess sin uso | Oportunista |
| CI adicional en Linux solo para pruebas (rápida) | Detecta errores de plataforma y acelera la retroalimentación | Con P1 |

No se recomienda reescribir `app.js` ni cambiar de framework: funciona, tiene pruebas y el riesgo de regresión de UX
es alto. Los módulos nuevos siguen el patrón de `secante.js` e `iterativos.js` (un archivo por módulo).

## Roadmap por fases
| Fase | Contenido | Depende de | Cambia UX |
|---|---|---|---|
| 3 · Fiabilidad | P1 + formato común de pasos + CI en Linux | — | No |
| 4 · Uso académico | P2 (copiar, imprimir, exportar) + P15 sin cambios visibles | formato común de pasos | Sí (P2) |
| 5 · Métodos numéricos | P3 integración, P4 interpolación y mínimos cuadrados, P7 punto fijo | — | Módulos nuevos |
| 6 · Álgebra lineal avanzada | P5 valores propios, P6 espacios y descomposiciones | espectro exacto del módulo 11 | Módulos nuevos |
| 7 · Varias variables | P9, luego P10 EDO y P11 Newton para sistemas | P9 | Módulos nuevos |
| 8 · A decidir | P8, P12, P13, P14, P16 | según prioridades | Sí |

## Las cinco con mejor relación utilidad / esfuerzo / mantenibilidad
1. **P1 Robustez y límites**: elimina los únicos fallos que pueden congelar la aplicación en clase, sin tocar la UX
   y con poco código. Habilita todo lo demás con seguridad.
2. **P2 Copiar, imprimir y exportar**: el mayor salto de utilidad diaria para estudiantes y docentes con esfuerzo
   medio. Reutiliza el LaTeX ya generado. Necesita tu autorización por los botones nuevos.
3. **P3 Integración numérica**: contenido estándar de los cursos y casi todo reutilizado (analizador, dominio,
   continuidad, gráficas, patrón de pruebas).
4. **P4 Interpolación y mínimos cuadrados**: cubre ajuste de datos y sistemas sobredeterminados con el Gauss exacto
   existente.
5. **P5 Valores y vectores propios**: el tema más importante de álgebra lineal que falta. El motor espectral exacto
   ya existe gracias al módulo 11.

Descartadas del top 5: el cálculo simbólico (P12) por coste y dependencia; las EDO (P10) porque exigen antes el
analizador de varias variables; y el punto fijo (P7), que es barato pero de valor menor.

## Siguiente etapa recomendada
**Etapa 3 = P1 + formato común de pasos + P3.** Primero, sin cambiar la UX, robustez y límites. Después, la
integración numérica como módulo nuevo con el patrón actual. P2 queda lista para la etapa 4 en cuanto apruebes sus
botones (es el único cambio de UX propuesto a corto plazo).
