"""Diagnósticos matriciales y residuo; índices base 0, filas completas al reordenar."""

from math import inf, isfinite

from src.solver.gauss_solver import solve_gaussian_elimination
from .entrada import leer_sistema


def dominancia_diagonal(A):
    """Compara sin tolerancias; las magnitudes informadas son float para JSON."""
    filas = []
    for i, fila in enumerate(A):
        diagonal = abs(fila[i])
        suma = sum(abs(v) for j, v in enumerate(fila) if j != i)
        filas.append({"i": i, "diagonal": float(diagonal), "suma": float(suma),
                      "cumple": diagonal > suma, "no_estricta": diagonal >= suma})
    return {"filas": filas, "estricta": all(f["cumple"] for f in filas),
            "no_estricta": all(f["no_estricta"] for f in filas)}


def diagonal_nula(A):
    """Posiciones de ceros exactos en la diagonal, sin confundir pivotes pequeños con cero."""
    return [i for i, fila in enumerate(A) if fila[i] == 0]


def rangos(A, b):
    """Rangos y singularidad por el motor Gauss racional ya existente."""
    A, b, _ = leer_sistema(A, b)
    resultado = solve_gaussian_elimination([fila + [b[i]] for i, fila in enumerate(A)],
                                           use_gauss_jordan=False)
    return {"A": resultado.rank_A, "aumentada": resultado.rank_Aug,
            "singular": resultado.rank_A < len(A)}


def residuo(A, b, x):
    """Calcula b − Ax y su norma relativa con la norma matricial infinito por filas.

    Recibe los datos numéricos ya normalizados; los no finitos nunca producen
    un residuo relativo finito que pueda confundirse con convergencia.
    """
    Ax = [sum((a * v for a, v in zip(fila, x)), 0.0) for fila in A]
    r = [bi - axi for bi, axi in zip(b, Ax)]
    norma = max(abs(v) for v in r)
    if not all(isfinite(v) for v in (*b, *x, *Ax, *r)):
        return {"Ax": Ax, "residuo": r, "residuo_inf": inf, "residuo_rel": inf}
    norma_A = max(sum(abs(v) for v in fila) for fila in A)
    norma_b, norma_x = max(abs(v) for v in b), max(abs(v) for v in x)
    denominador = norma_b + norma_A * norma_x
    relativo = norma / denominador if denominador else norma
    return {"Ax": Ax, "residuo": r, "residuo_inf": norma, "residuo_rel": relativo}
