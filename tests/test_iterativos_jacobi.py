"""Jacobi contra tres pasos racionales independientes y errores de entrada."""

import copy
import json
import math
import unittest
from fractions import Fraction as F
from pathlib import Path

from src.iterativos import leer_sistema, paso_jacobi, sistema_float
from tests.validacion.banco_iterativos import CASOS

REFERENCIAS = json.loads((Path(__file__).parent / "validacion/referencias_iterativos.json")
                         .read_text(encoding="utf-8"))


class TestJacobi(unittest.TestCase):
    def test_tres_iteraciones_todo_el_banco_sin_diagonal_nula(self):
        validados = []
        for nombre, caso in CASOS.items():
            referencia = REFERENCIAS[nombre]
            if referencia["diagonal_nula"]:
                continue
            A, b, x = sistema_float(*leer_sistema(**caso))
            validados.append(nombre)
            for k, esperado in enumerate(referencia["iteraciones_jacobi"], 1):
                x, detalle = paso_jacobi(A, b, x)
                for i, (valor, exacto) in enumerate(zip(x, esperado)):
                    with self.subTest(caso=nombre, k=k, i=i):
                        ref = float(F(exacto))
                        self.assertTrue(math.isclose(valor, ref, rel_tol=1e-12,
                                                     abs_tol=1e-12 if ref == 0 else 0))
                        self.assertEqual(detalle[i]["usa_nuevos"], [])
                        self.assertEqual(detalle[i]["valor"], valor)
        self.assertEqual(len(validados), 15)

    def test_no_usa_valores_nuevos_como_gauss_seidel(self):
        A, b, x = sistema_float(*leer_sistema(**CASOS["principal"]))
        nuevo, _ = paso_jacobi(A, b, x)
        self.assertAlmostEqual(nuevo[1], 25 / 11, places=14)
        gs = float(F(REFERENCIAS["principal"]["iteraciones_gauss_seidel"][0][1]))
        self.assertNotAlmostEqual(nuevo[1], gs, places=12)
        self.assertEqual(x, [0.0] * 4)

    def test_copia_entradas_y_detalle_por_componente(self):
        A, b, x = sistema_float(*leer_sistema(**CASOS["principal_x0_unos"]))
        original = copy.deepcopy((A, b, x))
        nuevo, detalle = paso_jacobi(A, b, tuple(x))
        self.assertEqual((A, b, x), original)
        self.assertIsNot(nuevo, x)
        self.assertEqual([d["i"] for d in detalle], list(range(4)))
        for d in detalle:
            self.assertEqual(set(d), {"i", "formula_latex", "sustitucion_latex",
                                      "valor", "usa_nuevos"})
            self.assertIsInstance(d["valor"], float)
        self.assertIn(r"x_{1}^{(k+1)} = \frac{6", detalle[0]["formula_latex"])
        self.assertIn(r"x_{2}^{(k)}", detalle[0]["formula_latex"])
        self.assertIn(r"\left(-1\right)\cdot\left(1\right)",
                      detalle[0]["sustitucion_latex"])
        self.assertIn(r"{10}", detalle[0]["formula_latex"])
        json.dumps(detalle, allow_nan=False)

    def test_unidimensional_y_indices_de_dos_cifras(self):
        nuevo, detalle = paso_jacobi([[2.0]], [3.0], [100.0])
        self.assertEqual(nuevo, [1.5])
        self.assertIn(r"\left(0\right)", detalle[0]["formula_latex"])
        A, b, x = sistema_float(*leer_sistema(**CASOS["dd_10x10"]))
        _, detalle = paso_jacobi(A, b, x)
        self.assertIn(r"x_{10}^{(k)}", detalle[0]["formula_latex"])
        self.assertTrue(detalle[9]["formula_latex"].startswith(r"x_{10}^{(k+1)}"))

    def test_diagonal_nula_con_indicacion_de_fila_y_correccion(self):
        for nombre in ("diagonal_nula_reordenable", "diagonal_nula_sin_arreglo"):
            with self.subTest(caso=nombre):
                sistema = sistema_float(*leer_sistema(**CASOS[nombre]))
                with self.assertRaisesRegex(ValueError, "fila 1, columna 1.*Reordena"):
                    paso_jacobi(*sistema)

    def test_dimensiones_invalidas(self):
        for sistema in (([], [], []), ([[1]], [], [0]), ([[1]], [1], []),
                        ([[1, 2]], [1], [0])):
            with self.subTest(sistema=sistema), self.assertRaisesRegex(ValueError, "dimensión"):
                paso_jacobi(*sistema)
