# Validación del área `iterativos-ui` (Módulo 11: Jacobi y Gauss-Seidel)

- **Rama**: `orca/iterativos-ui` (creada desde `main` en `fd597c3`).
- **Alcance**: `src/iterativos/sistema_texto.py`, `src/ui/web/index.html`, `src/ui/web/iterativos.js`, `src/ui/web/iterativos.css`, `tests/test_iterativos_texto.py`, `tests/test_iterativos_ui.cjs`.

## 1. Analizador de sistemas lineales en texto (`src/iterativos/sistema_texto.py`)
- Implementa `leer_ecuaciones(texto) -> (A, b, nombres)` con coeficientes exactos `Fraction` (sin dependencias externas).
- Acepta notación estándar lineal (`10x1 − x2 + 2x3 = 6`, `-x₁ + 11x₂ − x₃ + 3x₄ = 25`, `x_1 + (1/2)x_2 = 3/4`, `0.5*x1 - 2*x2 = 1`, notación científica, signos Unicode `−`, `×`, `·`, subíndices `₀..₉` de uno o varios dígitos y constantes trasladadas desde la izquierda).
- Rechaza con diagnóstico específico por línea: términos no lineales (`x1*x2`, `x1 x2`, `x1^2`, `x1**2`, `x1²`, `sin(x1)`, `log10(x1)`, `1/x1`, `1/2x1`), variables sin índice (`x`, `y`), índices inválidos (`x0`, `x_a`), letras mezcladas (`x1 + y2`), huecos en índices (`x1, x3`), falta o duplicación de `=`, variables en el lado derecho (política explícita: forma `Ax = b`, evitando confundir fórmulas despejadas de iteración con el sistema original), sistemas no cuadrados, división por cero, comas decimales, `;` y límite `n <= 20`.
- **Casos del banco validados en `tests/test_iterativos_texto.py`**: `principal` (4×4 presentación), `practica` (4×4 presentación), `dd_10x10` (10×10 con subíndices de dos dígitos), `diagonal_nula_sin_arreglo` (`0x1 + x2 = 1`), además de fracciones, decimales y notación científica.

## 2. Vista del módulo 11, KaTeX y gráficas SVG
- `src/ui/web/index.html`: solo añade `<link>` a `iterativos.css?v=0`, entrada lateral `11`, tarjeta `11` en «Métodos numéricos», `<section id="tab-iterativos">` y `<script src="iterativos.js?v=0">`. Por instrucción actualizada del coordinador, no se alteró ningún `?v=` existente (el integrador recalculará todos sobre LF).
- Controles implementados: rejilla `[A | b]` para `n = 2..10` (con etiquetas $x_1\dots x_n\mid b$), vector inicial $x^{(0)}$ (cero por defecto), cuadro desplegable para pegar ecuaciones en texto (`/api/iterativos/texto`), ejemplos del banco, selector `jacobi`/`gauss_seidel`/`comparar`, tolerancia (`1e-6`), máximo de iteraciones (`100`), criterio (`ambos`/`cambio`/`residuo`), casilla de reordenamiento y botón «Solo analizar matriz» (`/api/iterativos/analizar`).
- Resultados implementados contra `docs/contratos/iterativos.md`: análisis de dominancia por filas, diagonal nula, reordenamiento, rango/singularidad, $\rho(T_J)$, $\rho(T_{GS})$, garantía (`demostrada`/`observada`/`no_asegurada`), desarrollo paso a paso (`detalle` con $x_i^{(k+1)}$, $\sum$, `usa_nuevos` y normas $\|\cdot\|_\infty$), solución, motivo (`MOTIVOS` cubre los 9 motivos del contrato), verificación por sustitución ($Ax$, $b$, $r=b-Ax$) y comparación lado a lado.
- Gráficas SVG reutilizando `GraficaFunciones` (`MARCO`, `marcas`, `crearEscala`, `caminoCurva`, `formatear`): evolución de incógnitas $x_i^{(k)}$ y convergencia en $\log_{10}$ (residuo o cambio frente a $k$, con línea de referencia en $\log_{10}(\varepsilon)$ y omisión explícita de ceros exactos).

## 3. Verificación visual y regresión
- **Captura de pantalla (Chrome headless 1440×3600)** con respuesta simulada del caso `principal` en modo «Comparar ambos»: la barra lateral muestra la entrada `11 Jacobi y Gauss-Seidel` activa en la estética del cuaderno; a la izquierda la rejilla `4×4` `[A | b]`, vector inicial $x^{(0)}$, ejemplos y parámetros; a la derecha `03 Análisis de convergencia` (garantía demostrada, rangos, radios espectrales y filas de dominancia sin barras de desplazamiento verticales), `04 Solución y verificación` en dos columnas alineadas (`Jacobi` en 18 iteraciones vs `Gauss-Seidel` en 8 iteraciones, con vectores y normas alineadas sin quiebres), `05 Gráficas de evolución y convergencia` (curvas de $x_1\dots x_4$ y comparación $\log_{10}(\|r\|_\infty)$ hasta la línea verde discontinua en $-6$) y `06 Desarrollo paso a paso` desplegable con fórmulas KaTeX.
- **Regresión de módulos existentes**: `tests/test_iterativos_ui.cjs` verifica que, al retirar exclusivamente las cinco inserciones del módulo 11, `src/ui/web/index.html` coincide byte a byte con `git show main:src/ui/web/index.html`.
- No se requirió ningún patrón de interacción nuevo fuera de `#tab-iterativos`.

## 4. Batería de pruebas ejecutada
- Python (`python -m unittest discover tests -q`): **330 pruebas OK** (línea base 322 + 8 nuevas en `tests/test_iterativos_texto.py`).
- Node (`node --test tests/*.cjs`): **57 pruebas OK** (línea base 52 + 5 nuevas en `tests/test_iterativos_ui.cjs`: contrato de 9 motivos, KaTeX estricto `throwOnError: true` para `n=2, 4, 10` con negativos/fracciones/científica, series SVG, regresión de `index.html` y flujo DOM simulado `/texto` + `/comparar`).
- Pendiente para integración: conectar con el backend y rutas `/api/iterativos/*` implementados en paralelo por Codex 1 y Codex 2, y recalcular los hashes `?v=` sobre LF.
