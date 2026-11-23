"""Barrido de Gauss-Seidel: cada componente consume las anteriores nuevas."""
from math import isfinite

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


def paso_gauss_seidel(A, b, x):
    """Devuelve un vector nuevo y el procedimiento, sin modificar las entradas.

    Conserva el tipo numérico recibido (Fraction en pruebas exactas, float en
    el resolvedor). Los índices de ``detalle`` son base cero.
    """
    nuevo, detalle = list(x), []
    n = len(b)
    if not n or len(A) != n or len(x) != n or any(len(fila) != n for fila in A):
        raise ValueError("Gauss-Seidel requiere A cuadrada y b, x de igual dimensión.")
    for i in range(n):
        if A[i][i] == 0:
            raise ValueError(f"La diagonal es nula en la fila {i + 1}; reordena las ecuaciones.")
        suma = sum(A[i][j] * nuevo[j] for j in range(n) if j != i)
        nuevo[i] = (b[i] - suma) / A[i][i]
        formula = (
            rf"x_{{{i + 1}}}^{{(k+1)}}=\frac{{1}}{{a_{{{i + 1},{i + 1}}}}}"
            rf"\left(b_{{{i + 1}}}-\sum_{{j<{i + 1}}}a_{{{i + 1},j}}x_j^{{(k+1)}}"
            rf"-\sum_{{j>{i + 1}}}a_{{{i + 1},j}}x_j^{{(k)}}\right)"
        )
        terminos = [
            rf"\left({_latex(A[i][j])}\right)\left({_latex(nuevo[j] if j < i else x[j])}\right)"
            for j in range(n) if j != i
        ]
        sustitucion = (
            rf"x_{{{i + 1}}}^{{(k+1)}}=\frac{{({_latex(b[i])})-\left("
            + ("+".join(terminos) or "0")
            + rf"\right)}}{{{_latex(A[i][i])}}}={_latex(nuevo[i])}"
        )
        detalle.append({"i": i, "formula_latex": formula,
                        "sustitucion_latex": sustitucion, "valor": nuevo[i],
                        "usa_nuevos": list(range(i))})
    return nuevo, detalle
