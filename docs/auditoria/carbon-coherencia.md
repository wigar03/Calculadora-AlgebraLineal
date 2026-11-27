# Auditoría de coherencia transversal entre módulos (Carbon)

Auditoría realizada sobre `wigar03/Calculadora-AlgebraLineal` (`v1.0.0`, rama `Dev-Carbon`), contrastando el código fuente (`src/`, `tests/`, `docs/`) con la aplicación real en ejecución (`python main.py` en `http://127.0.0.1:8080`).

## 1. Matriz de módulo × capacidad

Leyenda: `✔` cumple de forma coherente · `parcial` cumple con asimetrías o lagunas documentadas · `✘` carece de la capacidad.

| Módulo | 1. Entradas y notación | 2. Límites (`limites.py`) | 3. Mensajes de error | 4. Procedimiento paso a paso | 5. Verificación del resultado | 6. Tablas de iteraciones | 7. Gráficas y controles | 8. Exportación (LaTeX/CSV/PDF) | 9. Estados UI, teclado, a11y y 390 px | 10. Documentación |
|---|---|---|---|---|---|---|---|---|---|---|
| 01. Vectores | parcial | ✔ | parcial | parcial | ✘ | ✘ | ✘ | parcial | parcial | parcial |
| 02. Combinación lineal | parcial | ✔ | ✔ | parcial | parcial | ✘ | ✘ | parcial | parcial | parcial |
| 03. Matrices | parcial | ✔ | parcial | parcial | ✘ | ✘ | ✘ | parcial | parcial | parcial |
| 04. Inversa | parcial | parcial | parcial | parcial | ✔ | ✘ | ✘ | parcial | parcial | parcial |
| 05. Sistemas $Ax=b$ | parcial | ✔ | parcial | ✔ | ✔ | ✘ | ✘ | parcial | parcial | parcial |
| 06. Determinante | parcial | parcial | parcial | ✔ | parcial | ✘ | ✘ | parcial | parcial | parcial |
| 07. Bisección | parcial | parcial | parcial | parcial | parcial | ✔ | parcial | parcial | ✔ | parcial |
| 08. Regla falsa | parcial | parcial | parcial | parcial | parcial | parcial | parcial | parcial | parcial | parcial |
| 09. Newton-Raphson | parcial | parcial | parcial | ✔ | ✔ | parcial | parcial | parcial | parcial | parcial |
| 10. Secante | parcial | parcial | parcial | parcial | ✔ | parcial | parcial | parcial | parcial | parcial |
| 11. Jacobi y Gauss-Seidel | parcial | parcial | ✔ | ✔ | ✔ | ✔ | parcial | parcial | parcial | parcial |

*(Nota: en los módulos algebraicos 01–06 no aplican tablas de iteraciones ni gráficas de convergencia por su naturaleza finita exacta).*

---

## 2. Catálogo de hallazgos (`C-01` a `C-28`)

### Hallazgos matemáticos, de API, entradas y diagnósticos

#### C-01 · Radio de certificación porcentual 100 veces mayor y cola geométrica en estancamiento
- **Módulos afectados:** 07 Bisección (`criterio="relativo"`) y 08 Regla falsa (`criterio="relativo_porcentual"`).
- **Evidencia:** `src/regla_falsa/certificacion.py:13` calculaba `radio = tolerancia * max(1., abs(x))` sin dividir `tolerancia` entre `100`, y `src/biseccion/metodo.py:53` pasaba `"relativo"` sin distinguir que en Bisección es porcentual (`* 100` en `:81`) mientras en Newton y Secante es fracción. En `ln(x)` sobre `[0.5, 2]` con `tolerancia="2"` (2 %), el radio `2.0` invadía $x \le 0$ y daba falso `no_certificada`. Ese factor $100\times$ ocultaba a la vez que en Regla falsa con estancamiento unilateral ($\lambda = |\Delta x_k|/|\Delta x_{k-1}| \in (0.5, 1)$, p. ej. `x^10 - 1` en `[0, 1.3]` con $\lambda \approx 0.77$ o `ln(x)+sin(x)-1.2` desde `1e-6` con $\lambda \approx 0.91$), el error verdadero sigue la cola geométrica $|x_r - r| \approx \frac{\lambda}{1 - \lambda}|\Delta x_k|$, superando $\frac{\varepsilon_s}{100}|x_r|$.
- **Impacto para el usuario:** Falsos rechazos «no certificada» con tolerancias porcentuales ordinarias ($\ge 0.1\,\%$) y ocultación de la pérdida de precisión bajo estancamiento unilateral.
- **Propuesta:** En Bisección dividir `tolerancia / 100`; en Regla falsa usar el radio explícito $\max(\frac{\varepsilon_s}{100}\max(1,|x_r|), (1+m)\frac{\lambda}{1-\lambda}|\Delta x_k|)$ cuando $\lambda \in (0.5, 1)$ en los dos últimos pasos, recortado siempre al intervalo validado `[xl, xu]` y emitiendo aviso explícito con $\lambda$, error estimado y radio certificado cuando supere el radio base.
- **Esfuerzo:** Bajo.
- **Cambia la UX:** no.

#### C-02 · Condición conjunta de residuo en criterios de parada (decisión de diseño poco explícita en etiquetas y guía)
- **Módulos afectados:** 08 Regla falsa y 11 Jacobi y Gauss-Seidel.
- **Evidencia:** En `src/regla_falsa/metodo.py:168-169` se exige `error_rel <= tolerancia and abs(f_xr)/escala_residuo <= tolerancia`. En `src/iterativos/convergencia.py:193-201` (`docs/contratos/iterativos.md`, INC-018), `cumple_tolerancia` exige siempre `residuo_rel <= tolerancia` además de `cambio_rel <= tolerancia`. Sin embargo, `src/ui/web/index.html:1274` rotula la opción `cambio` como norma absoluta $\|x^{(k)}-x^{(k-1)}\|_\infty < \varepsilon$ sin mencionar el carácter relativo ni la verificación obligatoria del residuo, y `docs/guia-matematica.md:354` omite la guarda de residuo escalado en Regla falsa.
- **Impacto para el usuario:** No es un defecto del motor (evita falsas convergencias en curvas planas o escalas mal condicionadas), pero la etiqueta incompleta puede confundir al estudiante al comparar la tabla con el instante de parada.
- **Propuesta:** Conservar intacta la decisión de diseño en los motores y precisar la etiqueta de `index.html:1274`, la ayuda de Regla falsa y `docs/guia-matematica.md`.
- **Esfuerzo:** Bajo.
- **Cambia la UX:** no.

#### C-03 · Diagnóstico dispar ante decimales con coma `,`
- **Módulos afectados:** 01–06 (álgebra lineal), 07–10 (parámetros y llamadas en `f(x)`), 11 (`tolerancia` y rejilla).
- **Evidencia:** `Expresion("0,5 + x")` (`src/biseccion/expresiones.py:108`) y `sistema_texto.py:89` indican usar punto decimal `0.5`, pero `Expresion("sin(0,5)")` (`expresiones.py:105`) responde *«la función 'sin' admite exactamente un argumento»*, `parse_number("0,5")` (`src/core/arithmetic.py:88`) da *«No se pudo convertir '0,5' a un número racional válido»* y `numero_real("0,5", "a")` (`expresiones.py:42`) da *«a debe ser un número real finito»*.
- **Impacto para el usuario:** Quien escribe coma decimal desde teclado numérico en español recibe mensajes genéricos o engañosos según el campo.
- **Propuesta:** Mantener `.` como único separador decimal en la entrada (evitando ambigüedad con `1,000` y argumentos, sin alterar la coma decimal del CSV exportado) y unificar el diagnóstico explícito en `parse_number`, `numero_real`, `iterativos/resolver.py` y llamadas `f(a,b)` en `Expresion`.
- **Esfuerzo:** Bajo.
- **Cambia la UX:** no.

#### C-04 · Falso positivo de límite de exponente con la constante `e` de Euler
- **Módulos afectados:** 07 Bisección, 08 Regla falsa, 09 Newton-Raphson, 10 Secante y Derivadas.
- **Evidencia:** `src/ui/web_server.py:75,164` aplica `re.finditer(r"[eE]([+-]?\d+)", texto)` sobre `funcion` sin exigir dígito previo. `POST /api/biseccion/preview` con `{"funcion": "e-1500+x"}` falla con HTTP 400 (`tipo: "limite"`, *«El exponente debe tener valor absoluto ≤ 1000»*), mientras `"e - 1500 + x"` devuelve HTTP 200.
- **Impacto para el usuario:** Expresiones válidas con la constante `e` seguida de suma o resta de un entero mayor que 1000 se bloquean erróneamente.
- **Propuesta:** Exigir un dígito o punto decimal antes de `[eE]` (`r"(?:\d|\.)[eE]([+-]?\d+)"`), manteniendo el rechazo de `1e-1500`.
- **Esfuerzo:** Bajo.
- **Cambia la UX:** no.

#### C-05 · Respuesta HTTP 500 `interno` cuando un vector obligatorio se envía como `null`
- **Módulos afectados:** 05 Sistemas $Ax=b$ (`/api/ecuaciones/resolver`).
- **Evidencia:** En `src/ui/web_server.py:141-143`, `if clave in cuerpo and cuerpo[clave] is not None` omite `_validar_lista` para `"b": null` (pensado para `x0` opcional en Iterativos). El motor llega a `validar_vector_numerico(None)` (`src/core/arithmetic.py:177`), lanza `TypeError` y `clasificar_error` (`src/core/ejecucion.py:41`) responde HTTP 500 `error_interno`.
- **Impacto para el usuario:** Una entrada JSON mal formada devuelve fallo interno 500 en lugar de 400 `entrada`.
- **Propuesta:** Permitir `None` únicamente en `x0` cuando `modulo == "iterativos"`, exigiendo lista en `b` para todas las rutas que lo reciben.
- **Esfuerzo:** Bajo.
- **Cambia la UX:** no.

#### C-06 · Inconsistencias en validación de enteros (`"200.0"` vs `"200.5"`), alias de cofactores y método inválido en inversa
- **Módulos afectados:** 04 Inversa, 06 Determinante, 07 Bisección y 08 Regla falsa.
- **Evidencia:** `validar_peticion` (`src/ui/web_server.py:136,183`) valida `cantidad` y `n` con `_entero_acotado` (admite `"200.0"` y rechaza `"200.5"`), pero los manejadores `:791`, `:818` y `:854` llaman `int(...)` crudo y fallan con `"200.0"`. En `:130`, `metodo == "cofactores"` no filtra los alias `"laplace"`/`"cofactor"` admitidos en `src/matrices/determinante.py:809`. En `:622-623`, `/api/matrices/inversa` sustituye en silencio métodos inválidos por `"gauss_jordan"`.
- **Impacto para el usuario:** Mensajes genéricos tras fallar `int()`, salto del filtro previo de `COFACTORES_MAX` con alias y corrección silenciosa en API de inversa.
- **Propuesta:** Reutilizar `_entero_acotado` en los tres manejadores (aceptando `"200"` y `"200.0"` y rechazando `"200.5"` sin truncar), normalizar alias de cofactores en `validar_peticion` y rechazar métodos desconocidos con HTTP 400 en inversa.
- **Esfuerzo:** Bajo.
- **Cambia la UX:** no.

#### C-07 · Signo menos Unicode `−` (`U+2212`) y tolerancia fraccionaria rechazados fuera de `Expresion` y `sistema_texto`
- **Módulos afectados:** 01–06 (rejillas y escalares), 07–10 (extremos, semillas y tolerancia), 11 (rejilla y `tolerancia`).
- **Evidencia:** `Expresion` (`src/biseccion/normalizador.py:5`) y `sistema_texto.py:9` aceptan `−` (`U+2212`) y `–` (`U+2013`), pero `parse_number` (`src/core/arithmetic.py:66-88`), `numero_real` (`src/biseccion/expresiones.py:28-42`), `_opciones` (`src/iterativos/resolver.py:30`) y los parseadores JS (`regla-falsa.js:682`, `newton-raphson.js:28`, `secante.js:47`, `iterativos.js:448`) los rechazan. Además, `tolerancia: "1/1000"` funciona en los 4 módulos de raíces pero falla en `/api/iterativos/resolver` (`resolver.py:30`), y `src/iterativos/entrada.py:26` captura `LimiteExcedido` como `ValueError`.
- **Impacto para el usuario:** Pegar números negativos como `−1.5` desde PDF o diapositivas funciona en la ecuación pero falla en los extremos o celdas de la misma pantalla; escribir `1/1000` en tolerancia falla solo en Iterativos.
- **Propuesta:** Normalizar `−` y `–` a `-` en `parse_number`, `numero_real` y parseadores cliente; usar `numero_real` para `tolerancia` en `iterativos/resolver.py`; y relanzar `LimiteExcedido` en `iterativos/entrada.py`.
- **Esfuerzo:** Bajo.
- **Cambia la UX:** no.

#### C-08 · Superíndices Unicode limitados únicamente a `²`, `³` y `⁴`
- **Módulos afectados:** 07 Bisección, 08 Regla falsa, 09 Newton-Raphson, 10 Secante y Derivadas.
- **Evidencia:** `src/biseccion/normalizador.py:6` define solo `SUPERINDICES = {"²": "^2", "³": "^3", "⁴": "^4"}`. Copiar `x¹⁰ − 1` (ejemplo oficial del módulo) o `x⁵ − 1` o `10⁻⁶` falla con *«carácter no admitido»*.
- **Impacto para el usuario:** Potencias habituales mayores que 4 o exponentes negativos pegados desde apuntes se rechazan pese a admitirse `x⁴`.
- **Propuesta:** Soportar secuencias completas de superíndices `⁰¹²³⁴⁵⁶⁷⁸⁹` y signo inicial `⁻`/`⁺` (`x¹⁰` $\to$ `x^10`, `10⁻⁶` $\to$ `10^(-6)`) conservando el mapa de índices para diagnósticos.
- **Esfuerzo:** Bajo.
- **Cambia la UX:** no.

#### C-09 · Mensajes de error sin fila/componente o con clasificación `tipo="entrada"` en fallos de dominio
- **Módulos afectados:** 01 Vectores, 03–06 Matrices/Sistemas, 09 Newton-Raphson y 10 Secante.
- **Evidencia:** `validar_matriz_numerica` (`src/core/arithmetic.py:229`) no indica el número de fila al fallar una celda; `_handle_vectores_operar` (`src/ui/web_server.py:431-432`) pierde el índice de componente; `resolver_newton` (`src/newton_raphson/metodo.py:62`) lanza `"La función no está definida en el valor inicial elegido."` sin la palabra `"dominio"`, devolviendo `tipo: "entrada"` en `ln(x)` con `x0=-1` mientras Bisección, Regla falsa y Secante devuelven `tipo: "dominio"`.
- **Impacto para el usuario:** En matrices grandes cuesta localizar la casilla errónea y la API clasifica de forma dispar el mismo error de dominio en `x0`.
- **Propuesta:** Incluir fila en `validar_matriz_numerica`, usar `validar_vector_numerico` en `_handle_vectores_operar` y anteponer `"Error de dominio:"` en `newton_raphson/metodo.py:62`.
- **Esfuerzo:** Bajo.
- **Cambia la UX:** no.

---

### Hallazgos en exportación, impresión y formato común `procedimiento`

#### C-10 · Fallo en `@media print`: desaparece la columna `Acción` en Regla falsa y queda cabecera `Detalle` huérfana
- **Módulos afectados:** 07 Bisección, 08 Regla falsa, 09 Newton-Raphson y 10 Secante.
- **Evidencia:** `src/ui/web/impresion.css:49` aplica `.bis-detail-cell { display: none !important; }`. En `src/ui/web/regla-falsa.js:846`, las celdas de datos `Acción` llevan `class="bis-detail-cell rf-action-cell"`, por lo que al imprimir se ocultan los datos mientras `<th>Acción</th>` sigue visible (además carecen de `.bis-cell-label` en móvil $\le 1100\text{ px}$). En `biseccion.js:516`, `newton-raphson.js:240` y `secante.js:73`, se ocultan las celdas `<td class="bis-detail-cell">` pero no su `<th>Detalle</th>`.
- **Impacto para el usuario:** Tablas descuadradas o con columna vacía al imprimir o guardar como PDF en los cuatro métodos de raíces.
- **Propuesta:** Usar `bis-cell rf-action-cell` (con `.bis-cell-label`) en Regla falsa y marcar `class="bis-detail-head"` en los `<th>Detalle</th>` para ocultarlos junto con `.bis-detail-cell` en `impresion.css`.
- **Esfuerzo:** Bajo.
- **Cambia la UX:** no (solo corrige la hoja `@media print` y la etiqueta responsiva ausente).

#### C-11 · Lagunas en exportación LaTeX de álgebra lineal (`entrada` vacía, pasos duplicados y dictamen omitido)
- **Módulos afectados:** 01 Vectores, 02 Combinación lineal, 03 Matrices, 05 Sistemas $Ax=b$ y 06 Determinante.
- **Evidencia:** En `src/procedimientos/lineal.py:42-63`, `adaptar_vectores`, `adaptar_combinacion` y `adaptar_matrices` dejan `entrada: []`. En `:26`, `paso(original, original)` duplica cada línea como título y párrafo, y en `pasos_multiplicacion`/`pasos_mapeo` envía LaTeX sin `$` que `exportar.js` escapa como texto literal. En `:60,81`, parámetros como `t_10` quedan sin llaves (`t_{10}`). En `:87-93`, `adaptar_determinante` omite el dictamen de invertibilidad y la complejidad estimada visibles en pantalla. Además, `combinacion_lineal.py:227` y `ecuacion_matricial.py:203` contienen `**...**` Markdown literal.
- **Impacto para el usuario:** El documento LaTeX copiado carece de los datos de entrada en tres módulos, repite renglones y omite el dictamen del determinante.
- **Propuesta:** Poblar `entrada` desde `cuerpo` cuando esté disponible, evitar duplicar `texto` en `_pasos` (envolviendo fórmulas sin `$` en `latex`), agrupar subíndices `t_{10}` en resultados paramétricos e incluir dictamen/complejidad en `adaptar_determinante`.
- **Esfuerzo:** Medio.
- **Cambia la UX:** no.

#### C-12 · Asimetrías en adaptadores numéricos (`/newton-raphson/derivar`, reordenamiento y avisos)
- **Módulos afectados:** 07 Bisección, 08 Regla falsa, 09 Newton-Raphson y 11 Iterativos.
- **Evidencia:** `/api/derivadas/derivar` tiene adaptador en `src/procedimientos/numerico.py:90`, pero `/api/newton-raphson/derivar` (`web_server.py:754`) devuelve el mismo objeto sin `procedimiento`. En `numerico.py:261-272, 330-350` se omiten la permutación de `reordenamiento`, `diagonal_nula` y las garantías propias de Gauss-Seidel (SDP) al comparar. En `:71,160` se añade `"Tolerancia no alcanzada."` incluso cuando el fallo fue `"no_certificada"`, y `:195-201` ignora `no_certificada` en Newton.
- **Impacto para el usuario:** Exportación incompleta cuando se reordenan ecuaciones o se comparan matrices SDP, y avisos imprecisos cuando falla la certificación.
- **Propuesta:** Registrar `/api/newton-raphson/derivar`, añadir reordenamiento, diagonal nula y garantías de GS en `numerico.py`, y reflejar el motivo real en `avisos`.
- **Esfuerzo:** Bajo.
- **Cambia la UX:** no.

---

### Hallazgos en estados de interfaz, exportación interactiva, tablas y accesibilidad

#### C-13 · El botón «Limpiar» de Determinante no borra el resultado ni la insignia anterior
- **Módulos afectados:** 06 Determinante.
- **Evidencia:** `limpiarModuloDeterminante()` (`src/ui/web/app.js:1966-1978`) pone la matriz en `"0"` y deshabilita «Exportar», pero no restablece `#det-result-content` ni `#det-badge-status`, dejando en pantalla el determinante anterior con estado «Invertible» junto a una matriz nula.
- **Impacto para el usuario:** Contradicción directa entre la matriz mostrada ($0$) y el resultado visible en pantalla.
- **Propuesta:** Restablecer `#det-badge-status` y `#det-result-content` igual que en los módulos 01–05.
- **Esfuerzo:** Bajo.
- **Cambia la UX:** no (corrige un fallo de limpieza respecto al resto de módulos).

#### C-14 · Título «Paso 1: Paso 1:» en Inversa y resultados obsoletos al cargar ejemplos o recalcular en 01–06
- **Módulos afectados:** 01–06 (álgebra lineal), especialmente 04 Inversa.
- **Evidencia:** `src/matrices/inversa.py:196` incluye `"Paso 1: ..."` en `title` y `src/ui/web/app.js:1397` antepone `` `Paso ${p.step_number}: ${p.title}` ``. Además, `cargarEjemplo*` en 01–06 (`app.js:368, 603, 942, 1176, 1554, 1911`) no limpia el resultado previo, y los manejadores `calcular*` de 01–06 no invocan `ExportarUI.limpiar(...)` antes del `await fetch(...)`.
- **Impacto para el usuario:** Duplicación textual en Inversa y ventana temporal donde entradas y resultados visibles o exportables pertenecen a ejercicios distintos.
- **Propuesta:** Evitar duplicar el prefijo `Paso k:` en `app.js:1397`, limpiar el panel de resultado e invalidar `ExportarUI` al cargar ejemplos y al iniciar `fetch` en 01–06.
- **Esfuerzo:** Bajo.
- **Cambia la UX:** no.

#### C-15 · Escribir en el borrador opcional `#it-texto` deshabilita «Exportar» sin haber cambiado el sistema resuelto
- **Módulos afectados:** 11 Jacobi y Gauss-Seidel.
- **Evidencia:** `src/ui/web/exportar-ui.js:204-205` escucha `input` sobre todo `#it-card-1`, incluido `<textarea id="it-texto">` (`index.html:1248`). Teclear en ese borrador sin pulsar «Cargar ecuaciones en la rejilla» desactiva «Exportar» aunque `[A|b]` y la solución en pantalla siguen intactas.
- **Impacto para el usuario:** Impide exportar un cálculo válido si se toca el cuadro opcional de texto.
- **Propuesta:** Ignorar `ev.target.id === "it-texto"` en `exportar-ui.js` (la carga efectiva en la rejilla ya limpia resultados y exportación en `iterativos.js:519`).
- **Esfuerzo:** Bajo.
- **Cambia la UX:** no.

#### C-16 · Módulo 11: ocultación de garantía SDP al comparar, motivo duplicado y bloqueo de scroll táctil en gráficas
- **Módulos afectados:** 11 Jacobi y Gauss-Seidel.
- **Evidencia:** `src/ui/web/iterativos.js:462-463` solo muestra `payload.jacobi.analisis` en modo «Comparar», ocultando cuando Gauss-Seidel tiene convergencia `"demostrada"` por matriz simétrica definida positiva (`convergencia.py:182`). En `iterativos.js:312-314` se imprimen dos párrafos consecutivos para el mismo motivo de parada. Además, `#it-plot-vars svg` e `#it-plot-conv svg` heredan `cursor: grab; touch-action: none` de `biseccion.css:119` pese a ser gráficas estáticas, bloqueando el desplazamiento vertical en móvil (390 px), y usan colores fijos (`iterativos.js:27, 438-439`) en tema oscuro.
- **Impacto para el usuario:** Información incompleta de convergencia al comparar, texto repetido y bloqueo del scroll táctil sobre las gráficas en móvil.
- **Propuesta:** Mostrar las razones específicas de Gauss-Seidel cuando difieran al comparar, evitar duplicar el motivo de parada, fijar `touch-action: pan-y; cursor: default` en `iterativos.css` y ajustar trazos para `[data-theme="dark"]`.
- **Esfuerzo:** Bajo.
- **Cambia la UX:** no.

#### C-17 · Celdas y botones sin `aria-label`, subetiqueta errónea `$c_i$` en Combinación lineal y alertas sin `role="alert"`
- **Módulos afectados:** 01–06 (álgebra lineal) y notificación global.
- **Evidencia:** Las grillas dinámicas de `src/ui/web/app.js` (`311, 326, 548, 569, 866, 886, 1133, 1507, 1523, 1760`) y los 8 botones `.mini-stepper` (`index.html:379-415`) carecen de `aria-label` (sí presente en Módulo 11 `iterativos.js:238-250`). En `app.js:546`, las componentes de cada vector $v_j$ se subetiquetan como `$c_i$` (nombre de los escalares incógnita). `mostrarErrorResultado` (`app.js:255`) carece de `role="alert"` y `#notification-toast` (`index.html:1310`) de `role="status" aria-live="polite"`.
- **Impacto para el usuario:** Lectores de pantalla no identifican fila/columna en 01–06 ni anuncian errores, y Combinación lineal confunde componentes con escalares.
- **Propuesta:** Añadir `aria-label` a las celdas generadas y botones `.mini-stepper`, corregir la subetiqueta de componentes en `app.js:546` y añadir atributos ARIA en errores, toast y capítulos `10`/`11` de la barra lateral.
- **Esfuerzo:** Bajo.
- **Cambia la UX:** no.

#### C-18 · Tabla de Regla falsa redondeada a 8 cifras significativas frente a 10 en el resto, y omisión de $f(x)$ en Secante
- **Módulos afectados:** 08 Regla falsa, 09 Newton-Raphson y 10 Secante.
- **Evidencia:** `src/ui/web/regla-falsa.js:840-841` formatea las celdas con `8` cifras significativas (`formatear(valor, 8)`), mientras su propio resumen (`:802`) y las tablas de Bisección, Newton-Raphson, Secante e Iterativos usan `10` cifras (INC-016). Además, `src/ui/web/secante.js:66-75` nunca muestra `funcion_latex` ni $f(x_n)$ con signo, `newton-raphson.js:263-265` omite el aviso `no_certificada`, y las tablas de 09–11 carecen de `<caption>`.
- **Impacto para el usuario:** Menor precisión visible e impresa en la tabla de Regla falsa respecto a los demás métodos numéricos, y resultado de Secante sin la función renderizada en KaTeX.
- **Propuesta:** Pasar la tabla de Regla falsa a 10 cifras significativas (en commit independiente), mostrar `f(x)` y `f(x_n)` en Secante, renderizar el aviso `no_certificada` en Newton y añadir `<caption>` accesible en las tablas 09–11.
- **Esfuerzo:** Bajo.
- **Cambia la UX:** no.

---

### Hallazgos en código interno y documentación

#### C-19 · Constantes de límites repetidas como literales fuera de `src/core/limites.py` y código muerto heredado
- **Módulos afectados:** Transversal (`src/biseccion`, `src/regla_falsa`, `src/newton_raphson`, `src/secante`, `src/derivadas`, `src/iterativos`, `src/solver/anterior_programa.py`).
- **Evidencia:** Pese a `src/core/limites.py:3`, se repiten literales (`500`, `120`, `1000`, `2000`, `4000`, `12`, `20`, `10000`) en `expresiones.py:53,67`, `derivadas/motor.py:106`, `biseccion/metodo.py:38`, `regla_falsa/metodo.py:106`, `newton_raphson/metodo.py:56`, `secante/metodo.py:20`, `iterativos/convergencia.py:12` y `web_server.py:762,792,818`. Además, `src/solver/anterior_programa.py:22-74` conserva funciones nunca invocadas, y `app.js:1790-1900` recalcula en JS la eficiencia de determinantes sin llamar a `/api/matrices/eficiencia-determinante`.
- **Impacto para el usuario:** Riesgo de desalineación futura entre validaciones previas del servidor y motores.
- **Propuesta:** Centralizar en `src/core/limites.py` las constantes compartidas manteniendo idéntico el comportamiento externo; conservar sin tocar la duplicación de motores Gauss y rutas congeladas en `golden` para no introducir riesgo de regresión.
- **Esfuerzo:** Bajo.
- **Cambia la UX:** no.

#### C-20 · `main.py` omite por completo el Módulo 11 (Jacobi y Gauss-Seidel)
- **Módulos afectados:** Punto de entrada `main.py` y Módulo 11.
- **Evidencia:** `main.py:12-24, 50, 90-101` enumera únicamente los módulos 1 a 10 tanto en su docstring como en el cartel de arranque en terminal.
- **Impacto para el usuario:** Al iniciar `python main.py`, la consola informa solo 10 módulos activos en lugar de los 11 reales.
- **Propuesta:** Incorporar el Módulo 11 (Jacobi y Gauss-Seidel) en el docstring, la descripción CLI y el encabezado de consola de `main.py`.
- **Esfuerzo:** Bajo.
- **Cambia la UX:** no.

#### C-21 · Desajustes entre `README.md`, `docs/guia-matematica.md` y el comportamiento real de `v1.0.0`
- **Módulos afectados:** Todos (01–11).
- **Evidencia:** `README.md:19,29` no menciona el tope $n \le 20$ en vectores ni $n \le 12$ en el polinomio espectral general. `docs/guia-matematica.md` omite cotas de dimensión en módulos 2–5 (`:59-226`), omite `asin`/`acos`/`atan` en Bisección (`:310`, igual que `index.html:820,975`), afirma que `/api/biseccion/muestrear` hace *«muestreo dinámico adaptativo»* cuando es equiespaciado (`:337` vs `biseccion/metodo.py:127-129`), afirma desigualdad estricta $< \varepsilon$ en Newton (`:387`) cuando rige `MARGEN_TOLERANCIA = 0.10` (`tolerancia.py:18`), conserva una nota interna de revisión en `:431` y carece de tabla API para el Módulo 11 (`:433-466`).
- **Impacto para el usuario:** La documentación pública contradice detalles verificables de entradas admitidas, muestreo, márgenes de parada y límites.
- **Propuesta:** Sincronizar `README.md`, `docs/guia-matematica.md` y los textos de ayuda de sintaxis de `index.html:820,975` sin alterar los desarrollos matemáticos y verificando con `scripts/verificar_markdown.py`.
- **Esfuerzo:** Medio.
- **Cambia la UX:** no.

---

### Propuestas de mejora con impacto en UX (documentadas; requieren aprobación del propietario)

#### C-22 · Vista previa matemática KaTeX en vivo ausente en Newton-Raphson y Secante
- **Módulos afectados:** 09 Newton-Raphson y 10 Secante.
- **Evidencia:** Bisección (`index.html:808-811`) y Regla falsa (`:964-967`) muestran vista previa en vivo de $f(x)$ a los 200 ms; Newton-Raphson (`:1139-1142`) y Secante (`:1211`) no la incluyen (además el teclado inicia desplegado en Bisección `:814` y plegado en 08–10).
- **Impacto para el usuario:** En métodos abiertos no se previsualiza la fracción o potencia antes de enviar el formulario.
- **Propuesta:** Incorporar el bloque `.bis-preview` debounced en los formularios de función de Newton-Raphson y Secante y unificar el estado inicial del teclado matemático.
- **Esfuerzo:** Bajo.
- **Cambia la UX:** sí (requiere aprobación del propietario).

#### C-23 · Controles asimétricos entre gráficas de raíces («Enfocar raíz», zoom `%` y lectura de cursor)
- **Módulos afectados:** 07 Bisección, 08 Regla falsa, 09 Newton-Raphson y 10 Secante.
- **Evidencia:** Regla falsa carece del botón «Enfocar raíz» (`index.html:1088-1099`); Newton-Raphson carece del indicador de porcentaje de zoom (`:1189-1193`) y no reescala el eje $Y$ al enfocar la raíz (`newton-raphson.js:206-209`); Bisección carece de lectura de coordenadas bajo el cursor y solo muestra la gráfica tras resolver (`biseccion.js:88-480`).
- **Impacto para el usuario:** Controles y atajos distintos (`0`/`r` frente a `Inicio`) al pasar de un método de raíces a otro.
- **Propuesta:** Añadir «Enfocar raíz» en Regla falsa, porcentaje de zoom y reescalado vertical opcional en Newton-Raphson y lectura de coordenadas en Bisección.
- **Esfuerzo:** Medio.
- **Cambia la UX:** sí (requiere aprobación del propietario).

#### C-24 · Tres estilos visuales distintos en las barras de herramientas de gráficas y botones «Limpiar»
- **Módulos afectados:** 07–11.
- **Evidencia:** Bisección y Regla falsa usan botones cuadrados con iconos Lucide (`zoom-in`/`zoom-out`), Newton usa `btn-text` con signos `+`/`−` y Secante mezcla `btn-bis-zoom` con texto (`index.html:895, 1091, 1191, 1225`). Asimismo, «Limpiar» incluye icono `trash-2` en 01–08 pero no en 09–11 (`:1155, 1214, 1257`), y `#sc-plot` carece de placeholder inicial (`:1227`).
- **Impacto para el usuario:** Inconsistencia visual menor en controles equivalentes.
- **Propuesta:** Unificar iconografía y clases de botones de zoom y limpieza en los módulos 07–11 e incluir placeholder inicial en Secante.
- **Esfuerzo:** Bajo.
- **Cambia la UX:** sí (requiere aprobación del propietario).

#### C-25 · Áreas táctiles menores de 44 px y campos en dos columnas a 390 px de ancho
- **Módulos afectados:** 01–11 en vista móvil (`390 px`).
- **Evidencia:** `.mini-stepper button` mide `22×26 px` (`styles.css:671`), `.btn-bis-zoom` `26×26 px` (`biseccion.css:113`), `.cell-input` `52×34 px` (`styles.css:606`), `det-matrix-grid` fija `62px` por columna (`app.js:1755`) y `.bis-fields` mantiene 2 columnas en $\le 480\text{ px}$ (`biseccion.css:90,174`).
- **Impacto para el usuario:** Aunque no hay desbordamiento horizontal de documento a 390 px, algunos botones requieren mayor precisión táctil y las etiquetas largas se parten en dos líneas.
- **Propuesta:** Colapsar `.bis-fields` a `1fr` bajo `480 px` y ampliar `min-height: 44px` en botones interactivos bajo `@media (pointer: coarse)`.
- **Esfuerzo:** Medio.
- **Cambia la UX:** sí (requiere aprobación del propietario).

#### C-26 · Límite inferior $n \ge 2$ en la interfaz de Inversa frente a $n \ge 1$ en API y Determinante
- **Módulos afectados:** 04 Inversa.
- **Evidencia:** `src/ui/web/index.html:511` fija `min="2" max="6"` en `#inv-dim-n`, mientras `src/matrices/inversa.py:118`, `src/core/limites.py:11` y Determinante (`index.html:693`) admiten $n = 1$, y en Determinante el radio «Cofactores» sigue seleccionable para $n = 7, 8$ aunque el servidor lo rechaza (`COFACTORES_MAX = 6`).
- **Impacto para el usuario:** No se puede invertir $[a]$ desde la interfaz y en Determinante $7\times 7$ se permite pulsar «Cofactores» para recibir error de límite.
- **Propuesta:** Permitir `min="1"` en `#inv-dim-n` y deshabilitar con aviso explicativo el radio «Cofactores» cuando $n > 6$.
- **Esfuerzo:** Bajo.
- **Cambia la UX:** sí (requiere aprobación del propietario).

#### C-27 · Celdas vacías convertidas silenciosamente a `0` en la interfaz de rejillas
- **Módulos afectados:** 01–06 y 11.
- **Evidencia:** `src/ui/web/app.js:340, 648, 901, 1148, 1597, 1783` y `src/ui/web/iterativos.js:216-219` reemplazan `""` por `"0"` antes de enviar la petición, anulando en el Módulo 11 el rechazo explícito de `src/iterativos/entrada.py:23-24`.
- **Impacto para el usuario:** Una casilla olvidada en blanco se interpreta como cero sin confirmación, aunque también agiliza la captura de matrices dispersas.
- **Propuesta:** Mantener el comportamiento actual salvo que el propietario decida exigir celdas explícitas o resaltar visualmente los ceros asumidos.
- **Esfuerzo:** Bajo.
- **Cambia la UX:** sí (requiere aprobación del propietario).

#### C-28 · Ausencia de apoyo gráfico en módulos geométricos de $\mathbb{R}^2$ y exportación de «Solo analizar matriz»
- **Módulos afectados:** 01 Vectores, 02 Combinación lineal, 05 Sistemas $Ax=b$ (caso $2\times 2$) y 11 Iterativos (`#it-analizar`).
- **Evidencia:** Ninguno de los módulos lineales incluye representación en el plano para $n=2$, y en Módulo 11 el botón «Solo analizar matriz» (`iterativos.js:508-511`, `/api/iterativos/analizar`) no genera `procedimiento`, dejando «Exportar» deshabilitado cuando solo se consulta el análisis espectral.
- **Impacto para el usuario:** Menor apoyo visual en $\mathbb{R}^2$ y necesidad de pulsar «Resolver» para exportar el análisis de convergencia.
- **Propuesta:** Evaluar en una etapa futura un lienzo SVG opcional para $n=2$ y un adaptador `procedimiento` para `/api/iterativos/analizar`.
- **Esfuerzo:** Alto.
- **Cambia la UX:** sí (requiere aprobación del propietario).
