"""Evaluación exacta de las soluciones paramétricas que devuelve la API ("81/4 - 1/4t - 2s")."""
import re
from fractions import Fraction

TERMINO = re.compile(r"([+-]?)(\d+(?:/\d+)?)?([a-z])?")


def evaluar_lineal(expresion, valores):
    """Evalúa una expresión paramétrica de la API ("81/4 - 1/4t - 2s") con valores exactos."""
    s, total, usado = expresion.replace(" ", ""), Fraction(0), 0
    for m in TERMINO.finditer(s):
        if not m.group(0):
            continue
        usado += len(m.group(0))
        signo = -1 if m.group(1) == "-" else 1
        coef = Fraction(m.group(2)) if m.group(2) else Fraction(1)
        if not (m.group(2) or m.group(3)):
            raise ValueError(expresion)
        total += signo * coef * (valores[m.group(3)] if m.group(3) else 1)
    if usado != len(s):
        raise ValueError(expresion)
    return total
