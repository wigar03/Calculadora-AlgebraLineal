"""C-20: la entrada de consola (main.py) presenta los once módulos, incluido Jacobi y Gauss-Seidel."""
import inspect
import unittest

import main
from src.ui.diagnostico import modulos_esperados


class TestMainModulos(unittest.TestCase):
    def test_docstring_y_listado_incluyen_todos_los_modulos(self):
        n = modulos_esperados()
        self.assertIn(f"{n}. Jacobi y Gauss-Seidel", main.__doc__)
        fuente = inspect.getsource(main.main)
        for i in range(1, n + 1):
            self.assertIn(f"Módulo {i}:", fuente)


if __name__ == "__main__":
    unittest.main()
