"""Entrada exacta, manejo matricial y pasos del método de Jacobi."""

from .entrada import leer_sistema, sistema_float
from .matriz import diagonal_nula, dominancia_diagonal, rangos, reordenar, residuo

__all__ = ["leer_sistema", "sistema_float", "diagonal_nula", "dominancia_diagonal",
           "rangos", "reordenar", "residuo"]
