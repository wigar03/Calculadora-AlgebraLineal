"""Evaluación con diagnósticos explícitos de dominio real para f(x)."""

import ast
import math
import operator

OPERACIONES = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}
_UMBRAL_POLO_TAN = 1e-12


def evaluar_funcion(nombre, funcion, argumento):
    """Evalúa una función matemática real y diagnostica salidas del dominio."""
    if nombre in ("ln", "log") and argumento <= 0:
        raise ValueError(
            f"Error de dominio: {nombre}(u) requiere u > 0 (evaluado en u={argumento:g})."
        )
    if nombre == "sqrt" and argumento < 0:
        raise ValueError(
            f"Error de dominio: sqrt(u) requiere u >= 0 (evaluado en u={argumento:g})."
        )
    if nombre in ("asin", "acos") and not -1.0 <= argumento <= 1.0:
        raise ValueError(
            f"Error de dominio: {nombre}(u) requiere -1 <= u <= 1 (evaluado en u={argumento:g})."
        )
    if nombre == "tan" and abs(math.cos(argumento)) < _UMBRAL_POLO_TAN:
        raise ValueError(
            f"Error de dominio: tan(u) tiene una asíntota (polo) en u={argumento:g}."
        )
    try:
        resultado = funcion(argumento)
    except OverflowError as exc:
        raise ValueError(
            f"Error de dominio: {nombre}({argumento:g}) desborda el rango real finito."
        ) from exc
    except ValueError as exc:
        raise ValueError(
            f"Error de dominio: {nombre}({argumento:g}) no está definida en los reales."
        ) from exc
    if not math.isfinite(resultado):
        raise ValueError(
            f"Error de dominio: {nombre}({argumento:g}) no produce un número real finito."
        )
    return resultado


def evaluar_binaria(op, izquierda, derecha):
    """Evalúa una operación binaria real distinguiendo fallos de dominio."""
    if isinstance(op, ast.Div):
        if derecha == 0:
            raise ValueError("Error de dominio: división por cero.")
    elif isinstance(op, ast.Pow):
        if abs(derecha) > 1000:
            raise ValueError(
                f"Error de dominio: el exponente ({derecha:g}) excede el límite de 1000."
            )
        if izquierda == 0 and derecha < 0:
            raise ValueError(
                "Error de dominio: división por cero (0 elevado a exponente negativo)."
            )
        if izquierda < 0 and not float(derecha).is_integer():
            raise ValueError(
                f"Error de dominio: potencia real indefinida para base negativa ({izquierda:g}) "
                f"y exponente no entero ({derecha:g})."
            )
    try:
        resultado = OPERACIONES[type(op)](izquierda, derecha)
    except ZeroDivisionError as exc:
        raise ValueError("Error de dominio: división por cero.") from exc
    except OverflowError as exc:
        raise ValueError("Error de dominio: el resultado desborda el rango real finito.") from exc
    if isinstance(resultado, complex) or not math.isfinite(resultado):
        raise ValueError("Error de dominio: el resultado no es un número real finito.")
    return float(resultado)
