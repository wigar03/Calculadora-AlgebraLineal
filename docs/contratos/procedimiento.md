# Contrato del formato común de procedimientos (etapa 3) y base de P2

Autor: integrador. Objetivo: una sola forma de describir cualquier procedimiento para copiar LaTeX, exportar tablas
e imprimir (P2), **sin reescribir los once módulos ni cambiar lo que muestran**.

## Mecanismo: adaptadores sobre la respuesta
- Cada ruta de cálculo conserva su respuesta actual intacta y gana una clave nueva `procedimiento`.
- `procedimiento` se construye con un **adaptador puro** `adaptar(respuesta: dict, cuerpo: dict) -> dict`
  registrado por ruta en `src/procedimientos/__init__.py` (`ADAPTADORES`). No toca los manejadores ni los motores.
- El servidor llama al registro en un único punto (tras calcular, antes de serializar). Si un adaptador falla,
  la respuesta se envía sin `procedimiento` y se registra el error: nunca rompe un cálculo.

## Forma (versión 1)
```
{"version": 1, "modulo": "determinante", "titulo": "Determinante por descomposición LU",
 "entrada": [{"etiqueta": "A", "latex": "\\begin{pmatrix}…\\end{pmatrix}"}],
 "pasos": [{"titulo": "…", "texto": "texto con $…$ como hoy", "latex": ["bloques display"],
            "matriz": [["1/2", …]] | null, "detalles": ["…"]}],
 "resultado": [{"etiqueta": "\\det(A)", "latex": "-146"}],
 "verificacion": ["texto con $…$"],
 "tablas": [{"titulo": "Iteraciones", "columnas": ["k", "x_1^{(k)}", …], "filas": [[0, "0.6", …]]}],
 "avisos": ["…"]}
```
Todo texto procede de la respuesta existente (mismos números, mismas cadenas LaTeX); los adaptadores no recalculan.

## Reparto
| Archivo | Responsable | Rutas |
|---|---|---|
| `src/procedimientos/base.py`, `__init__.py` | integrador | tipos, validación de forma, registro |
| `src/procedimientos/lineal.py` | Codex 1 | vectores, combinación, matrices, inversa, ecuaciones, determinante |
| `src/procedimientos/numerico.py` | Antigravity | bisección, regla falsa, Newton, secante, derivadas, iterativos |

Pruebas: para cada entrada del corpus golden, el adaptador produce un `procedimiento` válido (`base.validar`), sus
tablas tienen tantas filas como iteraciones devuelve la respuesta, y todo LaTeX renderiza con KaTeX estricto.

## Base de P2 (sin cambios visibles hasta tu aprobación)
`src/ui/web/exportar.js` (Antigravity, **no se carga en `index.html`** en esta etapa): `procedimientoALatex(p)`
(documento LaTeX completo), `tablaACSV(t)` (RFC 4180, separador configurable para Excel en español),
`tablaALatex(t)` y utilidades para impresión. Con pruebas `node --test`. La ubicación y apariencia de los
controles se presentarán como propuesta visual antes de modificar la interfaz.
