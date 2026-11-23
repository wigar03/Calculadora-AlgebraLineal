"""Barrido de Gauss-Seidel: cada componente consume las anteriores nuevas."""


def paso_gauss_seidel(A, b, x):
    """Devuelve un vector nuevo y el procedimiento, sin modificar las entradas.

    Conserva el tipo numérico recibido (Fraction en pruebas exactas, float en
    el resolvedor). Los índices de ``detalle`` son base cero.
    """
    nuevo, detalle = list(x), []
    n = len(b)
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
            rf"({A[i][j]})({nuevo[j] if j < i else x[j]})"
            for j in range(n) if j != i
        ]
        sustitucion = (
            rf"x_{{{i + 1}}}^{{(k+1)}}=\frac{{({b[i]})-\left("
            + ("+".join(terminos) or "0")
            + rf"\right)}}{{{A[i][i]}}}={nuevo[i]}"
        )
        detalle.append({"i": i, "formula_latex": formula,
                        "sustitucion_latex": sustitucion, "valor": nuevo[i],
                        "usa_nuevos": list(range(i))})
    return nuevo, detalle
