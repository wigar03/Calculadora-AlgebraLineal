"""Lectura exacta y conversión explícita de sistemas iterativos de orden 1 a 20."""

from fractions import Fraction
from math import isfinite

from src.core.arithmetic import parse_number


# Umbrales exactos de redondeo IEEE-754 doble (empates al par): cero e infinito.
_UMBRAL_CERO = Fraction(1, 1 << 1075)
_UMBRAL_INFINITO = Fraction((1 << 1024) - (1 << 970))


def _error_magnitud(lugar):
    return ValueError(
        f"{lugar}: no se puede representar como float finito sin perder su valor "
        "no nulo; escribe un número de magnitud representable."
    )


def _celda(valor, lugar):
    try:
        if isinstance(valor, bool) or valor is None or str(valor).strip() == "":
            raise ValueError("falta un número")
        numero = parse_number(valor)
    except (ValueError, TypeError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError(
            f"{lugar}: valor inválido. Escribe un entero, un decimal como 0.75 "
            "o una fracción como 1/3 con denominador distinto de cero."
        ) from exc
    # Validar en el orden original sin convertir celdas a float por segunda vez.
    if numero != 0 and not _UMBRAL_CERO < abs(numero) < _UMBRAL_INFINITO:
        raise _error_magnitud(lugar)
    return numero


def _vector(vector, n, nombre):
    if not isinstance(vector, (list, tuple)) or len(vector) != n:
        raise ValueError(f"{nombre} debe tener {n} componentes; escribe un valor por fila.")
    return [_celda(v, f"{nombre}, fila {i + 1}, columna 1") for i, v in enumerate(vector)]


def leer_sistema(A, b, x0=None):
    """Devuelve copias (A, b, x0) en Fraction; nunca interpreta una celda vacía como cero."""
    if not isinstance(A, (list, tuple)) or not 1 <= len(A) <= 20:
        raise ValueError("A debe ser una matriz cuadrada de 1 a 20 filas; ajusta su tamaño.")
    n = len(A)
    matriz = []
    for i, fila in enumerate(A):
        if not isinstance(fila, (list, tuple)) or len(fila) != n:
            raise ValueError(
                f"A, fila {i + 1}: la matriz debe ser cuadrada; escribe {n} columnas."
            )
        matriz.append([_celda(v, f"A, fila {i + 1}, columna {j + 1}")
                       for j, v in enumerate(fila)])
    return matriz, _vector(b, n, "b"), ([Fraction(0)] * n if x0 is None
                                       else _vector(x0, n, "x0"))


def _flotante(valor, lugar):
    try:
        convertido = float(valor)
        if not isfinite(convertido) or (valor != 0 and convertido == 0):
            raise ValueError("fuera del intervalo representable")
        return convertido
    except (ValueError, TypeError, OverflowError) as exc:
        raise _error_magnitud(lugar) from exc


def sistema_float(A, b, x0):
    """Convierte una sola vez el triple ya validado por leer_sistema, sin mutarlo."""
    matriz = [[_flotante(v, f"A, fila {i + 1}, columna {j + 1}")
               for j, v in enumerate(fila)] for i, fila in enumerate(A)]
    vectores = [[_flotante(v, f"{nombre}, fila {i + 1}, columna 1")
                 for i, v in enumerate(vector)] for nombre, vector in (("b", b), ("x0", x0))]
    return matriz, vectores[0], vectores[1]
