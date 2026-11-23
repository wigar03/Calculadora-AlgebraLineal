"""Partes III y IV del banco ampliado: ecuaciones no lineales.

`ecuacion`: notación del documento (sen, e^(−x), x·ln(x)); el analizador debe aceptarla o diagnosticarla.
`funcion`: forma f(x) = izquierda − derecha en la sintaxis explícita que la calculadora ya admitía.
`condicion`: qué raíz pide el enunciado. `metodo`: método sugerido (None = a elección justificada).
Las raíces de referencia se calculan en `generar_referencias.py`, nunca con el código bajo prueba.
"""

ECUACIONES = {
    "III-1": {"ecuacion": "x^3 − 4x − 9 = 0", "funcion": "x^3 - 4*x - 9", "condicion": "real", "metodo": None},
    "III-2": {"ecuacion": "e^x − 3x^2 = 0", "funcion": "exp(x) - 3*x^2", "condicion": "positiva", "metodo": None},
    "III-3": {"ecuacion": "cos(x) − x·e^x = 0", "funcion": "cos(x) - x*exp(x)", "condicion": "positiva",
              "metodo": None},
    "III-4": {"ecuacion": "x·ln(x) − 1 = 0", "funcion": "x*ln(x) - 1", "condicion": "positiva", "metodo": None},
    "III-5": {"ecuacion": "x^4 − 3x^2 − 3 = 0", "funcion": "x^4 - 3*x^2 - 3", "condicion": "positiva",
              "metodo": None},
    "III-6": {"ecuacion": "ln(x+2) + x^2 − 2 = 0", "funcion": "ln(x+2) + x^2 - 2", "condicion": "real",
              "metodo": None},
    "III-7": {"ecuacion": "e^(−x) − x^2 + 0.5 = 0", "funcion": "exp(-x) - x^2 + 0.5", "condicion": "positiva",
              "metodo": None},
    "III-8": {"ecuacion": "x^3 + x − 1 = 0", "funcion": "x^3 + x - 1", "condicion": "real", "metodo": None},
    "III-9": {"ecuacion": "x·e^(−x) − 0.2 = 0", "funcion": "x*exp(-x) - 0.2", "condicion": "positiva",
              "metodo": None},
    "III-10": {"ecuacion": "x^2 − 5·sin(x) = 0", "funcion": "x^2 - 5*sin(x)", "condicion": "positiva_no_nula",
               "metodo": None},
    "III-11": {"ecuacion": "ln(x) + sen(x) = 1.2", "funcion": "ln(x) + sin(x) - 1.2", "condicion": "real",
               "metodo": "biseccion|regla_falsa"},
    "III-12": {"ecuacion": "e^(−x) + cos(x) = 0.5", "funcion": "exp(-x) + cos(x) - 0.5", "condicion": "real",
               "metodo": "secante"},
    "III-13": {"ecuacion": "x^2 − 3 sen(x) − ln(x + 2) = 0", "funcion": "x^2 - 3*sin(x) - ln(x+2)",
               "condicion": "real", "metodo": "newton"},
    "III-14": {"ecuacion": "e^(x/2) + sen(2x) = 3", "funcion": "exp(x/2) + sin(2*x) - 3", "condicion": "real",
               "metodo": "biseccion|regla_falsa"},
    "III-15": {"ecuacion": "ln(x + 3) + cos(x) = x/2", "funcion": "ln(x+3) + cos(x) - x/2", "condicion": "real",
               "metodo": "secante"},
    "IV-1": {"ecuacion": "sen(x) / ln(x) = 1", "funcion": "sin(x)/ln(x) - 1", "condicion": "real",
             "metodo": "biseccion"},
    "IV-3": {"ecuacion": "e^(1/x) + 2x / tan(x) = 2", "funcion": "exp(1/x) + 2*x/tan(x) - 2", "condicion": "real",
             "metodo": "newton"},
    "IV-4": {"ecuacion": "ln(x + 1) / (x^2 − 4) = −0.1", "funcion": "ln(x+1)/(x^2-4) + 0.1", "condicion": "real",
             "metodo": "biseccion"},
}

# Enunciados sin igualdad en el documento original (solo el radical): no se resuelven ni se inventan.
INCOMPLETOS = {
    "IV-2": {"expresion": "sqrt(2x^3/(x-3))", "metodo": "regla_falsa"},
    "IV-5": {"expresion": "sqrt((x+4)/(x-1))", "metodo": "biseccion"},
}
