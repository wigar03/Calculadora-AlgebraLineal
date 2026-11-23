"""Un paso simultáneo de Jacobi sobre datos numéricos previamente normalizados."""

from fractions import Fraction
from math import isfinite
from sys import float_info

from src.core.arithmetic import format_latex_number


def _latex(valor):
    if not isinstance(valor, float):
        return format_latex_number(valor)
    if not isfinite(valor):
        return rf"\mathrm{{{valor}}}"
    texto = format(valor, ".15g")
    if "e" in texto:
        mantisa, exponente = texto.split("e")
        return rf"{mantisa}\times 10^{{{int(exponente)}}}"
    return texto


def paso_jacobi(A, b, x):
    """Devuelve (x_nuevo, detalle), usando exclusivamente la copia de x^(k).

    Los índices de detalle son base 0; las variables en LaTeX muestran base 1.
    No muta A, b ni x. La validación y conversión inicial corresponde a entrada.
    """
    n = len(A)
    if not n or len(b) != n or len(x) != n or any(len(fila) != n for fila in A):
        raise ValueError("Jacobi requiere A cuadrada y b, x de igual dimensión; revisa sus tamaños.")
    for i in range(n):
        if A[i][i] == 0:
            raise ValueError(
                f"Diagonal nula en fila {i + 1}, columna {i + 1}: Jacobi no puede dividir "
                "entre cero. Reordena las ecuaciones completas o corrige el coeficiente."
            )
    anteriores = tuple(x)
    nuevos, detalle = [], []
    for i, fila in enumerate(A):
        indices = [j for j, a in enumerate(fila) if j != i and a != 0]
        productos = [fila[j] * anteriores[j] for j in indices]
        if any(anteriores[j] != 0 and abs(p) < float_info.min
               for j, p in zip(indices, productos)):
            # Evita perder a_ij*x_j antes de dividir por a_ii. El cociente
            # racional también evita desbordar al normalizar a_ij/a_ii.
            suma = sum(Fraction(fila[j]) * Fraction(anteriores[j]) for j in indices)
            valor = float((Fraction(b[i]) - suma) / Fraction(fila[i]))
        else:
            valor = float((b[i] - sum(productos, 0.0)) / fila[i])
        nuevos.append(valor)
        simbolica = " + ".join(rf"\left({_latex(fila[j])}\right)x_{{{j + 1}}}^{{(k)}}"
                              for j in indices) or "0"
        numerica = " + ".join(rf"\left({_latex(fila[j])}\right)\cdot"
                             rf"\left({_latex(anteriores[j])}\right)" for j in indices) or "0"
        izquierda = rf"x_{{{i + 1}}}^{{(k+1)}} = "
        formula = izquierda + rf"\frac{{{_latex(b[i])} - \left({simbolica}\right)}}{{{_latex(fila[i])}}}"
        sustitucion = izquierda + (
            rf"\frac{{{_latex(b[i])} - \left({numerica}\right)}}{{{_latex(fila[i])}}} = {_latex(valor)}"
        )
        detalle.append({"i": i, "formula_latex": formula, "sustitucion_latex": sustitucion,
                        "valor": valor, "usa_nuevos": []})
    return nuevos, detalle
