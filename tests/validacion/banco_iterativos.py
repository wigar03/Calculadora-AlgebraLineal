"""Casos de validación del módulo Jacobi / Gauss-Seidel (presentación y casos adicionales).

Coeficientes como cadenas exactas (`parse_number`). `x0` ausente = vector cero. Las referencias se generan con
`generar_referencias_iterativos.py` (Fraction, SymPy y mpmath), nunca con `src/`.
"""

CASOS = {
    # Diapositiva 9: ejemplo principal, solución (1, 2, -1, 1).
    "principal": {"A": [["10", "-1", "2", "0"], ["-1", "11", "-1", "3"], ["2", "-1", "10", "-1"],
                        ["0", "3", "-1", "8"]], "b": ["6", "25", "-11", "15"]},
    "principal_x0_unos": {"A": [["10", "-1", "2", "0"], ["-1", "11", "-1", "3"], ["2", "-1", "10", "-1"],
                                ["0", "3", "-1", "8"]], "b": ["6", "25", "-11", "15"], "x0": ["1", "1", "1", "1"]},
    # Diapositiva 28: práctica en parejas.
    "practica": {"A": [["8", "-1", "1", "0"], ["-1", "10", "-2", "1"], ["1", "-2", "9", "-1"], ["0", "1", "-1", "7"]],
                 "b": ["8", "7", "-4", "5"]},
    "dd_2x2": {"A": [["4", "1"], ["2", "3"]], "b": ["1", "2"]},
    "decimales_3x3": {"A": [["5.5", "-1.25", "0.5"], ["1.5", "6.2", "-2"], ["0.4", "-1", "3.3"]],
                      "b": ["2.1", "-3.4", "1.7"]},
    "fracciones_3x3": {"A": [["1/2", "1/7", "1/9"], ["1/5", "3/4", "1/6"], ["1/8", "1/3", "5/6"]],
                       "b": ["1", "2", "3"]},
    "tridiagonal_5x5": {"A": [["4", "-1", "0", "0", "0"], ["-1", "4", "-1", "0", "0"], ["0", "-1", "4", "-1", "0"],
                              ["0", "0", "-1", "4", "-1"], ["0", "0", "0", "-1", "4"]], "b": ["3", "2", "2", "2", "3"]},
    # Simétrica definida positiva, no estrictamente dominante: GS converge (garantía SPD); Jacobi tiene ρ = 1.
    "spd_no_dominante": {"A": [["4", "2", "2"], ["2", "4", "2"], ["2", "2", "4"]], "b": ["8", "8", "8"]},
    # Contraejemplo clásico: Jacobi converge (ρ_J = 0) y Gauss-Seidel diverge (ρ_GS = 2).
    "jacobi_si_gs_no": {"A": [["1", "2", "-2"], ["1", "1", "1"], ["2", "2", "1"]], "b": ["1", "3", "5"]},
    "diverge_ambos": {"A": [["1", "3"], ["2", "1"]], "b": ["4", "3"]},
    # No dominante en el orden dado (ρ > 1); permutar las dos primeras ecuaciones la vuelve estrictamente dominante.
    "reordenable": {"A": [["2", "10", "1"], ["10", "1", "1"], ["1", "1", "10"]], "b": ["13", "12", "12"]},
    # Diagonal nula en el orden dado; intercambiar las dos primeras ecuaciones la elimina y da dominancia estricta.
    "diagonal_nula_reordenable": {"A": [["0", "10", "1"], ["10", "1", "1"], ["1", "1", "10"]], "b": ["11", "12", "12"]},
    "diagonal_nula_sin_arreglo": {"A": [["0", "1"], ["0", "1"]], "b": ["1", "1"]},
    "singular_infinitas": {"A": [["1", "1"], ["1", "1"]], "b": ["2", "2"]},
    "singular_incompatible": {"A": [["1", "1"], ["1", "1"]], "b": ["2", "3"]},
    # Hilbert 4x4: SPD y mal condicionada; GS converge lentamente (estabilidad y redondeo).
    "hilbert_4x4": {"A": [["1", "1/2", "1/3", "1/4"], ["1/2", "1/3", "1/4", "1/5"], ["1/3", "1/4", "1/5", "1/6"],
                          ["1/4", "1/5", "1/6", "1/7"]], "b": ["25/12", "77/60", "19/20", "319/420"]},
    # 10x10 estrictamente dominante: diagonal 40 frente a una suma fuera de la diagonal de 36 como máximo.
    "dd_10x10": {"A": [[str(40 if i == j else (-1) ** (i + j) * ((i * 7 + j * 3) % 5)) for j in range(10)]
                       for i in range(10)], "b": [str(i - 4) for i in range(10)]},
}
