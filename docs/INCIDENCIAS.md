# Incidencias

Formato: ID · fecha · tipo (fuente / analizador / motor / presentación / infraestructura) · estado.

## INC-001 · 2026-11-23 · fuente · CERRADA como limitación del enunciado (decisión del propietario)
**IV-2 y IV-5 no tienen igualdad.** En el XML del banco ampliado, cada uno contiene solo un `m:rad` OMML:
IV-2 `√(2x³/(x−3))`, IV-5 `√((x+4)/(x−1))`. No hay `=`, lado derecho, texto oculto, control de cambios ni
comentarios. No es un fallo de la calculadora. No se inventa el lado derecho ni se supone `= 0`.
Pregunta enviada al propietario: ¿cuál es la igualdad completa de cada uno?
**Decisión del propietario (etapa 3):** confirmado en el Word original: IV-2 `sqrt((2*x^3)/(x-3))` e IV-5
`sqrt((x+4)/(x-1))` no incluyen igualdad. No se suponen igualadas a cero: un radical no presenta el cambio de signo
que exigen bisección y falsa posición. Se registran como limitación del enunciado original; se conserva la
validación de las expresiones y de sus dominios (pruebas de Antigravity en `tests/test_expresiones_notacion.py`).
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

## INC-010 · 2026-11-23 · motor · CERRADA (d329aa4; `tests/test_raices_revision.py`; verificado por HTTP) — hallado en revisión cruzada (Codex 1)
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

## Etapa 2 — Módulo 11 (Jacobi y Gauss-Seidel)

### INC-012 · 2026-11-23 · fuente · REGISTRADA (no es un fallo de la calculadora)
La presentación tiene errores aritméticos en los desarrollos paso a paso: diapositiva 15, x₂⁽²⁾ = 1.704545
(correcto 1.715909) y x₄⁽²⁾ = 0.906818 (correcto 0.885227); diapositiva 20, x₄⁽¹⁾ = 0.751591 (correcto 0.878864);
diapositiva 21, toda la iteración 2 (x₁⁽²⁾ = 0.830182, correcto 1.030182). Las tablas 16 y 22 son correctas.
Verificado con aritmética exacta (`tests/validacion/referencias_iterativos.json`).

### INC-013 · 2026-11-23 · referencias · CERRADA
`mpmath.eig` dio ρ(T_J) ≈ 1.57 para una T_J nilpotente (exacto: 0). Las referencias y el motor usan el polinomio
característico exacto; el motor decide ρ < 1 con Schur-Cohn en aritmética racional.

### INC-014 · 2026-11-23 · web · CERRADA (9fd4b99, 6016c13)
10 de 13 `?v=` de `index.html` no identificaban el contenido (algunos desde antes de esta orquestación) y el servidor
no envía `Cache-Control`: la ventana de escritorio podía usar JS o CSS antiguos. Prueba nueva con hash en LF.

### INC-015 · 2026-11-23 · integración · CERRADA (c500a51; pruebas HTTP con los valores de los controles)
En la página real, «Resolver» del módulo 11 fallaba siempre: la vista envía `max_iteraciones` como cadena («100»),
igual que el resto de módulos, y el resolvedor solo aceptaba enteros. Las pruebas simuladas y la de aceptación usaban
números. Detectado al probar en el navegador.

### INC-016 · 2026-11-23 · presentación · CERRADA (c913d48)
La tabla de iteraciones y los radios espectrales se muestran con 6 cifras significativas (1.14306); se pasan a 10.

### INC-017 · 2026-11-23 · motor · CERRADA (9ccbe2a, 6d976b6, e1a2f3d) — batería adversaria de Codex 1
Falso «estancamiento» con cambio 1.0 (9×9, ρ = 0), falsa «divergencia» por transitorio (20×20 nilpotente) y ninguna
iteración con A = [[1e308]]. Ahora: convergen en k = 10 y k = 21 («demostrada») y el caso extremo converge.

### INC-018 · 2026-11-23 · motor · CERRADA (2260479→2be6c0d) — revisión cruzada de Codex 2
Con valores subnormales el residuo se redondeaba a 0 y se declaraba convergencia con residuo relativo exacto 0.2.
Ahora la x final se verifica con `Fraction`; si no cumple, motivo `precision_insuficiente`.

## Etapa 3 — Robustez (P1)

### INC-019 · 2026-11-23 · robustez · CERRADA (auditoría AU-01 a AU-10)
Bloqueos por cálculos costosos, servidor de un hilo, socket lento, límites solo en la UI, JSON inválido, textos de
Python, HTML inyectable en errores, números enormes, CORS y listado de directorios. Corregidos con procesos de cálculo
aislados y cancelables, servidor con hilos, límites centrales, errores uniformes y cabeceras de seguridad.
Antes y después: `docs/validacion/robustez-antes.md` y `robustez-despues.md`.

### INC-020 · 2026-11-23 · pruebas · CERRADA
La línea base dorada falló en la CI de Linux: `exp`, `sin` y `ln` de la biblioteca C difieren en el último bit entre
Windows y Linux. La comparación admite 1e-12 relativo en flotantes (también dentro de textos LaTeX).

### INC-021 · 2026-11-23 · integración · CERRADA
Al combinar las ramas, `tests/test_iterativos_api.py` rechazaba la clave nueva `procedimiento`, que el contrato
permite; ahora la admite y la valida con `src/procedimientos/base.py`.

### INC-022 · 2026-11-23 · entorno · REGISTRADA
Windows Application Control bloqueó en la máquina de Codex 2 un ejecutable recompilado («An Application Control
policy has blocked this file»). No se eludió: el diagnóstico del ejecutable empaquetado lo hace la CI de Windows.

## Etapa 5 — Consolidación con herramientas reales

### INC-023 · 2026-11-23 · documentación · CERRADA (0b04d8e; regla feaf7e8)
En github.com la fórmula de Gauss-Seidel de la guía perdía `<i} … \sum_{j>` (GitHub lo tomó como etiqueta HTML) y
mostraba un único sumatorio. Corregido con `\lt`/`\gt`; `scripts/verificar_markdown.py` detecta ahora el patrón.

### INC-024 · 2026-11-23 · exportación LaTeX · CERRADA (7776f9d)
pdflatex real (Codex 2): Jacobi 20×20 abortaba (MaxMatrixCols = 10), regla falsa abortaba con babel español y `\%`,
tablas desbordaban 270-670 pt y la barra invertida dejaba llaves visibles. Ahora 37/37 PDF sin desbordes > 1 pt.

### INC-025 · 2026-11-23 · seguridad CSV · CERRADA (5592934)
Gnumeric ejecutaba como fórmula un texto con espacios, saltos o NBSP antes de `=` (p. ej. « =1+2» daba 3), también en
cabeceras: el prefijo `'` solo miraba el primer carácter. Ahora se decide tras todos los espacios y controles.

### INC-026 · 2026-11-23 · fidelidad CSV · CERRADA (5592934, 0df5554, a4a85a0)
`1/0` salía como `="1/0"`; enteros de más de 15 cifras perdían dígitos; `-0` perdía el signo y `-0e8` salía `0E+08`;
«1/2» en cabeceras se convertía en fecha o mostraba apóstrofo en Calc. Ahora: solo racionales con q ≠ 0 como
`="p/q"`, enteros largos como `="n"`, cero canónico `0`, cifras significativas sin ceros iniciales.

### INC-027 · 2026-11-23 · exportación LaTeX · CERRADA (35cd3cb)
Un texto con `Ω` o `你好` abortaba pdflatex. Ahora griego y símbolos van con su comando y lo no soportado se muestra
como `[U+XXXX]`, nunca se omite. La CI compila ese adversario en el job `externos`.

### INC-028 · 2026-11-23 · entorno · CERRADA (4f9eb9b) — no es fallo de la aplicación
Localmente Chrome y Edge salían con código 0 sin abrir CDP: Orca corre elevado y Chromium se relanza des-elevado sin
heredar stderr. La prueba usa `--do-not-de-elevate` en Windows. Diagnóstico: `docs/validacion/chrome-local.md`.

### INC-030 · 2026-11-23 · servidor · CERRADA (8fff2a2)
La CI de Linux falló una vez con `BrokenPipe`: ante un cuerpo mayor de 256 KB el servidor respondía 413 y cerraba sin
leerlo, y el cliente que aún enviaba recibía un cierre abrupto en lugar del mensaje del límite (reproducido también
en Windows). Ahora se lee y descarta hasta 4 MiB antes de responder; prueba `tests/test_cuerpo_excesivo.py`.

### INC-034 · 2026-11-27 · UX · APROBADA E IMPLEMENTADA (lotes 1 y 2 de C-22…C-28; `main` 71c4f60)
Aprobadas las propuestas de la auditoría de coherencia: lote 1 = C-27 (aviso en el resultado de las casillas vacías
tomadas como 0, sin exigir escribirlo), C-26 (Inversa n ≥ 1; «Cofactores» desactivado con explicación para n > 6), C-22
(vista previa de f(x) en Newton y Secante), C-24 (iconos y botones unificados en 07-11) y C-28a (exportar «Solo analizar
matriz»); lote 2 = C-25 (áreas táctiles de 44 px y una columna bajo 480 px) y C-23 parcial («Enfocar raíz» en Regla
falsa y coordenadas bajo el cursor en Bisección). Aplazado: C-28b (gráficas en R²), zoom % y reescalado en Newton.

### INC-033 · 2026-11-27 · UX · APROBADA E IMPLEMENTADA (Codex 2; Antigravity sin cuota)
Banco final, Parte III: los ejercicios 31, 36, 38 y 39 piden «raíz positiva» o «no trivial» y la Parte III pide
«elija y justifique el método». Aprobados: (1) selector de condición de la raíz en los cuatro métodos, con los valores
que ya admite el motor (`real`, `positiva`, `positiva_no_nula`); (2) recomendación razonada del método según los datos.

### INC-032 · 2026-11-27 · UX · APROBADA E IMPLEMENTADA (a9b5f11, en `Dev-Carbon`)
Banco final, Parte VI (ejercicios 55–59): expresiones como 2A + B, A − 3B o A + B + C solo se resolvían encadenando
operaciones y copiando a mano los resultados intermedios. El propietario aprobó la opción recomendada: un botón
«Usar resultado como A» en Operaciones con matrices, con el estilo existente y sin otros cambios de disposición.

### INC-031 · 2026-11-23 · CI Windows · CERRADA (dfbb8ba, 20cb849) — entorno, no aplicación
El diagnóstico del portable superó una vez los 30 s de espera de carga. Causa: primer arranque en frío de cada runner
(WebView2/.NET del sistema: 8,4-11,5 s; arranques posteriores ≤ 6 s). 15 máquinas limpias: 15/15 ciclos completos y
110/110 diagnósticos repetidos. El diagnóstico mide fases y solo falla tras 120 s. Evidencia: `docs/validacion/inc031-windows.md`.

### INC-029 · 2026-11-23 · limitaciones externas · REGISTRADA
- Excel (escritorio y web) no está disponible con medios autorizados (`docs/validacion/excel-web.md`); se comprobó con LibreOffice Calc 26.2 y
  Gnumeric 1.12 (abrir, guardar y reabrir), no con Excel.
- Calc y Excel conservan 15 cifras significativas en números; el valor exacto viaja en la fracción cuando existe.
- `ssconvert` no permite elegir el separador por línea de comandos; en Gnumeric se elige en el asistente.
- Los textos protegidos con `'` (fórmulas o aspecto de fecha no racional) muestran el apóstrofo en Calc.
- GitHub: en móvil las fórmulas anchas se desplazan dentro de su recuadro; el MathML añade espacios estéticos.

## INC-004 · 2026-11-23 · infraestructura · CERRADA
`pytest` no está instalado; la suite oficial usa `unittest` (README y CI). Línea base: 169 pruebas OK y
5 archivos `node --test` OK. No es un fallo.
