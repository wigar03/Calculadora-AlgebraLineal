"""Métodos iterativos para sistemas lineales: Jacobi y Gauss-Seidel con análisis de convergencia.

Contrato de archivos, API y respuesta: `docs/contratos/iterativos.md`.
"""

from .entrada import leer_sistema, sistema_float
from .gauss_seidel import paso_gauss_seidel
from .jacobi import paso_jacobi
from .matriz import diagonal_nula, dominancia_diagonal, rangos, reordenar, residuo
from .resolver import comparar_metodos, resolver_iterativo

__all__ = ["leer_sistema", "sistema_float", "diagonal_nula", "dominancia_diagonal",
           "rangos", "reordenar", "residuo", "paso_jacobi", "paso_gauss_seidel",
           "resolver_iterativo", "comparar_metodos"]
