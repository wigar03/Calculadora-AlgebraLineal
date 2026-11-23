# Contrato del módulo 11: Jacobi y Gauss-Seidel

Autor: integrador (Claude Business). Cambios al contrato solo mediante el integrador.

## Paquete `src/iterativos/` (Python estándar, sin numpy)
| Archivo | Responsable | Contenido |
|---|---|---|
| `entrada.py` | Codex 1 | `leer_sistema(A, b, x0=None) -> (A, b, x0)`: celdas como `parse_number` (`"1/3"`, `"0.75"`), cuadrada, 1 ≤ n ≤ 20, `x0` por defecto 0, errores `ValueError` legibles |
| `matriz.py` | Codex 1 | dominancia por filas, diagonal nula, reordenamiento válido (permutación de ecuaciones), rango y singularidad con el Gauss exacto existente, residuo `r = b − Ax` |
| `jacobi.py` | Codex 1 | `paso_jacobi(A, b, x) -> (x_nuevo, detalle)`; usa solo `x` (copia) |
| `gauss_seidel.py` | Codex 2 | `paso_gauss_seidel(A, b, x) -> (x_nuevo, detalle)`; usa de inmediato los valores nuevos |
| `convergencia.py` | Codex 2 | matrices de iteración T_J = −D⁻¹(L+U), T_GS = −(D+L)⁻¹U, radio espectral (Python puro), garantías, criterios de parada y detección de divergencia, no finitos, estancamiento y oscilación |
| `resolver.py` | Codex 2 | `resolver_iterativo(...)` y `comparar_metodos(...)` |
| `sistema_texto.py` | Antigravity | `leer_ecuaciones(texto) -> (A, b, nombres)`: líneas `10x1 − x2 + 2x3 = 6`, `x₁`, `x_1`, `x1`; solo términos lineales |

Firmas exactas de Codex 1 (índices base 0 en Python y JSON; la vista muestra base 1):
- `leer_sistema(A, b, x0=None) -> (A, b, x0)` en `Fraction`; `sistema_float(A, b, x0) -> (A, b, x0)` en `float`.
- `dominancia_diagonal(A) -> {"filas": [{"i", "diagonal", "suma", "cumple", "no_estricta"}], "estricta", "no_estricta"}`.
- `diagonal_nula(A) -> [i, ...]`.
- `reordenar(A, b) -> (A, b, {"aplicado", "permutacion", "motivo"})`; `permutacion[k]` = fila original en la posición k.
- `rangos(A, b) -> {"A", "aumentada", "singular"}` (exacto, Gauss existente).
- `residuo(A, b, x) -> {"Ax", "residuo", "residuo_inf", "residuo_rel"}` con
  `residuo_rel = ‖r‖∞ / (‖b‖∞ + ‖A‖∞‖x‖∞)` (si el denominador es 0, `residuo_inf`).

`detalle` es una lista, una entrada por componente: `{"i", "formula_latex", "sustitucion_latex", "valor", "usa_nuevos": [j...]}`.
La aritmética de las iteraciones es flotante doble; las entradas se leen exactas y se convierten a `float` una vez.

## API (`src/ui/web_server.py`, rutas añadidas por Codex 2 en un bloque nuevo)
`POST /api/iterativos/resolver` con `{A, b, x0?, metodo: "jacobi"|"gauss_seidel", tolerancia?=1e-6,
max_iteraciones?=100, criterio?="ambos"|"cambio"|"residuo", reordenar?=false}`.
`POST /api/iterativos/comparar`: mismo cuerpo sin `metodo`; responde `{"jacobi": R, "gauss_seidel": R, "resumen"}`.
`POST /api/iterativos/analizar`: solo `analisis`. `POST /api/iterativos/texto`: `{texto}` → `{A, b, nombres}`.

Respuesta `R`:
```
{"metodo", "n", "nombres": ["x_1",...], "A", "b", "x0", "tolerancia", "criterio", "max_iteraciones",
 "iteraciones": [{"k", "x": [...], "cambio_inf", "cambio_rel", "residuo_inf", "residuo_rel",
                  "detalle": [...] (solo k ≤ 3, para acotar la respuesta)}],
 "solucion": [...], "convergio": bool, "motivo", "mensaje",
 "verificacion": {"Ax": [...], "residuo": [...], "residuo_inf", "residuo_rel", "cumple"},
 "analisis": {"diagonal_nula": [i...], "dominancia": {"filas": [{"i", "diagonal", "suma", "cumple"}],
              "estricta": bool}, "reordenamiento": {"aplicado", "permutacion", "motivo"},
              "rango": {"A", "aumentada"}, "singular": bool,
              "radio_espectral": {"jacobi", "gauss_seidel", "metodo_calculo"},
              "garantia": "demostrada"|"no_asegurada", "razones": [...]},
 "convergencia": "demostrada"|"observada"|"no_asegurada"}
```
`motivo` ∈ {`tolerancia`, `max_iteraciones`, `divergencia`, `no_finito`, `estancamiento`, `oscilacion`,
`diagonal_nula`, `singular`, `incompatible`, `precision_insuficiente`} (este último: el criterio flotante se cumplió, pero la verificación exacta final del residuo no). Cada motivo tiene texto en la vista (prueba de contrato).

## Reglas matemáticas
- Jacobi y Gauss-Seidel son esquemas distintos; una prueba debe fallar si uno usa el esquema del otro.
- El solucionador directo solo verifica; nunca sustituye a la iteración.
- `convergio = true` solo si se cumple el criterio pedido y además `residuo_rel ≤ tolerancia` (escalado por
  `‖b‖∞ + ‖A‖∞‖x‖∞`) con todos los valores finitos.
- «demostrada»: ρ(T) < 1 (exacto o con cota de error), o dominancia diagonal estricta, o (solo GS) A simétrica
  definida positiva. «observada»: convergió sin garantía previa. «no_asegurada»: ninguna de las anteriores.
- La dominancia diagonal es suficiente, no necesaria. No se afirma que Gauss-Seidel sea siempre más rápido.
- Reordenar solo permuta ecuaciones completas (filas de A y b) y se informa la permutación.

## Límites documentados
Interfaz: 2 ≤ n ≤ 10 (como el editor de sistemas). API: n ≤ 20, `max_iteraciones` ≤ 10 000.
