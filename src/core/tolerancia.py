"""Tolerancia aproximada: la digitada se acepta con un margen y se informa cuál se usó.

Con ε digitada y margen m, el criterio se cumple:
- con la tolerancia digitada si valor < ε;
- con una tolerancia cercana si ε ≤ valor ≤ ε·(1 + m).
Por debajo de ε siempre se acepta, por lo que el margen solo actúa por encima.
"""

from .config import MARGEN_TOLERANCIA


def clasificar(valor, tolerancia, margen=MARGEN_TOLERANCIA):
    """Devuelve "digitada", "cercana" o None si el valor no está definido o no se acepta."""
    if valor is None:
        return None
    if valor < tolerancia:
        return "digitada"
    if valor <= tolerancia * (1 + margen):
        return "cercana"
    return None


def informe(valor, tolerancia, margen=MARGEN_TOLERANCIA):
    """Resumen serializable de la tolerancia usada para el criterio seleccionado."""
    exceso = None
    if valor is not None and valor >= tolerancia:
        exceso = (valor - tolerancia) / tolerancia * 100
    return {
        "digitada": tolerancia,
        "margen": margen,
        "limite": tolerancia * (1 + margen),
        "valor_final": valor,
        "usada": clasificar(valor, tolerancia, margen),
        "exceso_porcentual": exceso,
    }
