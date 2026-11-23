"""Entradas válidas de los 11 módulos cuya respuesta de la API se congela antes de la etapa 3 (robustez).

La prueba `tests/test_golden_api.py` exige que cada respuesta posterior conserve exactamente los campos y valores
congelados; solo se admiten campos nuevos en el primer nivel (p. ej. `procedimiento`).
"""

PRINCIPAL = {"A": [["10", "-1", "2", "0"], ["-1", "11", "-1", "3"], ["2", "-1", "10", "-1"], ["0", "3", "-1", "8"]],
             "b": ["6", "25", "-11", "15"]}
M3 = [["2", "-1", "0"], ["1", "3", "1/2"], ["0", "4", "-2"]]
M4 = [["-4", "5", "-4", "5"], ["-3", "3", "-1", "3"], ["-3", "5", "1", "-1"], ["1", "-4", "-1", "-3"]]

CORPUS = {
    "vectores": [("/api/vectores/operar", {"operacion": op, "u": ["1", "-2/3", "0.5"], "v": ["3", "1/4", "-2"],
                                           "c": "-3/2"}) for op in ("suma", "resta", "escalar_u", "producto_punto")],
    "combinacion": [("/api/vectores/combinacion", {"vectores": [["1", "0", "2"], ["0", "1", "-1"]], "b": ["2", "3", "1"]}),
                    ("/api/vectores/combinacion", {"vectores": [["1", "2"], ["2", "4"]], "b": ["1", "1"]})],
    "matrices": [("/api/matrices/operar", {"operacion": op, "A": M3, "B": [["1", "0", "2"], ["-1", "1/3", "0"],
                                                                        ["0", "2", "1"]], "k": "2/3"})
                 for op in ("suma", "resta", "escalar_a", "multiplicacion", "transpuesta_a", "transpuesta_b")],
    "inversa": [("/api/matrices/inversa", {"A": [["4", "7"], ["2", "6"]]}),
                ("/api/matrices/inversa", {"A": M4, "metodo": "gauss_jordan"}),
                ("/api/matrices/inversa", {"A": M3, "metodo": "gauss"}),
                ("/api/matrices/inversa", {"A": [["1", "2"], ["2", "4"]]})],
    "ecuaciones": [("/api/ecuaciones/resolver", {**PRINCIPAL, "usar_gauss_jordan": gj}) for gj in (True, False)]
                  + [("/api/ecuaciones/resolver", {"A": [["2", "-3", "1", "4"], ["4", "-1", "-3", "2"],
                                                         ["-2", "8", "-6", "-10"], ["3", "2", "-4", "1"]],
                                                   "b": ["7", "5", "-16", "4"]}),
                     ("/api/ecuaciones/resolver", {"A": [["1", "1"], ["1", "1"]], "b": ["1", "2"]})],
    "determinante": [("/api/matrices/determinante", {"A": M4, "metodo": m}) for m in ("lu", "cofactores")]
                    + [("/api/matrices/determinante", {"A": M3, "metodo": "cofactores"}),
                       ("/api/matrices/eficiencia-determinante", {"n": 6})],
    "biseccion": [("/api/biseccion/resolver", {"funcion": "ln(x) + sen(x) = 1.2", "a": "1", "b": "2",
                                               "tolerancia": "0.000001", "criterio": c}) for c in ("intervalo", "residuo")]
                 + [("/api/biseccion/preview", {"funcion": "x^3 - 4*x - 9"}),
                    ("/api/biseccion/muestrear", {"funcion": "x^2 - 2", "a": "0", "b": "2", "cantidad": "21"})],
    "regla_falsa": [("/api/regla-falsa/graficar", {"funcion": "exp(-x) - x^2 + 0.5", "a": "0", "b": "2", "cantidad": "41"}),
                    ("/api/regla-falsa/analizar", {"funcion": "exp(-x) - x^2 + 0.5", "a": "0", "b": "2"}),
                    ("/api/regla-falsa/validar", {"funcion": "exp(-x) - x^2 + 0.5", "xl": "0", "xu": "1"}),
                    ("/api/regla-falsa/resolver", {"funcion": "exp(-x) - x^2 + 0.5", "xl": "0", "xu": "1",
                                                   "tolerancia": "0.000001"})],
    "newton": [("/api/newton-raphson/preparar", {"funcion": "x^2 - 3*sen(x) - ln(x+2) = 0", "a": "1", "b": "3",
                                                 "cantidad": "41"}),
               ("/api/newton-raphson/evaluar", {"funcion": "x^3 - x - 2", "x0": "1.5"}),
               ("/api/newton-raphson/resolver", {"funcion": "x^3 - x - 2", "x0": "1.5", "tolerancia": "0.000001"})],
    "secante": [("/api/secante/evaluar", {"funcion": "e^(-x) + cos(x) = 0.5", "x0": "1", "x1": "2"}),
                ("/api/secante/resolver", {"funcion": "e^(-x) + cos(x) = 0.5", "x0": "1", "x1": "2",
                                           "tolerancia": "0.000001"})],
    "derivadas": [("/api/derivadas/derivar", {"funcion": "sin(x)^2*exp(x)"})],
    "iterativos": [("/api/iterativos/resolver", {**PRINCIPAL, "metodo": m, "tolerancia": "0.000001",
                                                 "max_iteraciones": "100"}) for m in ("jacobi", "gauss_seidel")]
                  + [("/api/iterativos/comparar", {**PRINCIPAL, "tolerancia": "0.000001"}),
                     ("/api/iterativos/analizar", {"A": [["1", "2", "-2"], ["1", "1", "1"], ["2", "2", "1"]],
                                                   "b": ["1", "3", "5"]}),
                     ("/api/iterativos/texto", {"texto": "8x1 - x2 + x3 = 8\n-x1 + 10x2 - 2x3 + x4 = 7\n"
                                                         "x1 - 2x2 + 9x3 - x4 = -4\nx2 - x3 + 7x4 = 5"})],
}
