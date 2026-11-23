# Incidencias

Formato: ID · fecha · tipo (fuente / analizador / motor / presentación / infraestructura) · estado.

## INC-001 · 2026-11-23 · fuente · ABIERTA (requiere al propietario)
**IV-2 y IV-5 no tienen igualdad.** En el XML del banco ampliado, cada uno contiene solo un `m:rad` OMML:
IV-2 `√(2x³/(x−3))`, IV-5 `√((x+4)/(x−1))`. No hay `=`, lado derecho, texto oculto, control de cambios ni
comentarios. No es un fallo de la calculadora. No se inventa el lado derecho ni se supone `= 0`.
Pregunta enviada al propietario: ¿cuál es la igualdad completa de cada uno?
Mientras tanto: se prueba que la evaluación de ambos radicales respeta su dominio (IV-2: x ≤ 0 o x > 3;
IV-5: x ≤ −4 o x > 1).

## INC-002 · 2026-11-23 · analizador · CERRADA (e26bb99; prueba `test_raices_escritas_como_en_el_documento`)
**Las 18 ecuaciones escritas como en el documento se rechazan con «Función inválida».**
Reproducción (sonda HTTP sobre `main` 7a241ad): `ln(x) + sen(x) = 1.2`, `e^(−x) − x^2 + 0.5 = 0`,
`x^3 − 4x − 9 = 0` → 0/72 aceptadas. Causa: `Expresion` no admite `=`, `sen`, `e^…`, `·`, `−` (U+2212) ni
superíndices, y ante cualquier error de sintaxis da un único mensaje genérico. Corrección: soporte de igualdad y
alias, y diagnósticos específicos sin multiplicación implícita silenciosa.

## INC-003 · 2026-11-23 · motor/presentación · CERRADA (910c90a; `tests/test_banco_raices.py`)
**La prueba con semillas a ±0.05 de la raíz pasa en los 4 métodos, pero eso no demuestra robustez.**
Pendiente de verificar con datos iniciales realistas: polos (IV-3, IV-4), dominio de ln (III-4, III-11, IV-1),
raíz trivial x = 0 (III-10). En bisección con criterio «intervalo» y tol 10⁻⁶, III-1 deja |f| ≈ 3.7·10⁻⁶:
hay que explicitar la diferencia entre cota de error y residuo.

## INC-005 · 2026-11-23 · infraestructura · CERRADA (7196bbd prueba, 9a5fb83 corrección)
`iniciar_servidor_web` imprime un emoji y falla con `UnicodeEncodeError` si la salida estándar usa cp1252
(consola de Windows redirigida). No afecta a `servidor_local()` ni a la página. Solución temporal:
`PYTHONIOENCODING=utf-8`. La página carga sin errores de consola salvo `favicon.ico` 404 (inocuo).

## INC-006 · 2026-11-23 · presentación · CERRADA (verificado en navegador sobre `main`)
Reproducido en la interfaz (Bisección): `2x + 3 = 7` → «Revise los datos · Función inválida. Use, por ejemplo,
x^3 - x - 2.». Es el mensaje genérico que debe sustituirse por diagnósticos específicos (INC-002).
Capturas de línea base (fuera del repositorio): inicio, Bisección, Bisección con error, Ecuaciones matriciales.

## INC-007 · 2026-11-23 · pruebas · CERRADA (580bcb5)
`tests/test_raices_errores_ui.cjs` falló al integrarse: leía la salida de `python -c` como UTF-8, pero en Windows
una tubería usa cp1252 («multiplicaci�n»). Pasaba en el terminal del agente por su entorno. Corrección: forzar
`PYTHONIOENCODING=utf-8` en el proceso hijo (también en `test_katex_render.cjs`, que podía perder símbolos).

## INC-008 · 2026-11-23 · presentación · CERRADA (integrada en main; KaTeX estricto en tests/test_lineal_ui.cjs)
Revisión cruzada de la rama lineal: con 10 o más incógnitas o parámetros, `t_10` se emite sin llaves (KaTeX
muestra t₁0). El ayudante de vectores paramétricos reescribe fracciones con una expresión regular frágil.
Sin discrepancias matemáticas (1010 comparaciones con SymPy).

## INC-009 · 2026-11-23 · analizador · CERRADA (integrada en main; «Escribe 2*x + 3 = 7.»)
El diagnóstico de producto implícito propone solo «Escribe '2*x'»; el propietario pidió la expresión completa
corregida («Escribe 2*x + 3 = 7»).

## INC-010 · 2026-11-23 · motor · EN CURSO (Codex 2) — hallado en revisión cruzada (Codex 1)
Siete hallazgos reproducidos por HTTP, ninguno en los datos del banco con datos iniciales razonables:
(P1) III-10 por secante desde (0.2, 0.5) acepta x ≈ 5.8·10⁻¹³ como raíz positiva no nula; IV-3 por Newton desde −2.75
«converge» al punto excluido 0; la guarda de tan fabrica f = 0 y rechaza tan(1e16); el residuo escalado por f(x0)
acepta exp(1e8·x), que no tiene raíces. (P2) polos falsos por cancelación en `_ceros`; tan(x/2) no se reconoce
como afín; falso salto de III-11 en [1e-16, 2]. Corrección: certificar la raíz final (cambio de signo sin puntos
excluidos) antes de declarar convergencia.

## INC-011 · 2026-11-23 · presentación · CERRADA (tests/test_motivos_contrato.cjs; también faltaba sin_progreso en regla-falsa.js)
El motor devuelve `motivo = "raiz_no_admisible"` (condición positiva o positiva no nula), pero ningún diccionario
`MOTIVOS` de las cuatro páginas lo contiene: el mensaje se mostraría como «undefined». Lo mismo ocurrirá con
`no_certificada` (INC-010). Corrección: añadir los textos y una prueba de contrato entre motivos y diccionarios.

## INC-004 · 2026-11-23 · infraestructura · CERRADA
`pytest` no está instalado; la suite oficial usa `unittest` (README y CI). Línea base: 169 pruebas OK y
5 archivos `node --test` OK. No es un fallo.
