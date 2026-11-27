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

