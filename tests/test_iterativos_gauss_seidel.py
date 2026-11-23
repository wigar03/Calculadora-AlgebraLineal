"""Pasos exactos contrastados con el banco independiente, sin entrada/Jacobi."""
import json
import unittest
from fractions import Fraction as F
from pathlib import Path

from src.iterativos.gauss_seidel import paso_gauss_seidel
from tests.validacion.banco_iterativos import CASOS

REFERENCIAS = json.loads((Path(__file__).parent / "validacion" /
                         "referencias_iterativos.json").read_text(encoding="utf-8"))


class PasosGaussSeidel(unittest.TestCase):
    def test_tres_iteraciones_exactas_del_banco(self):
        for nombre, caso in CASOS.items():
            referencia = REFERENCIAS[nombre]
            if referencia["diagonal_nula"]:
                continue
            with self.subTest(caso=nombre):
                A = [[F(v) for v in fila] for fila in caso["A"]]
                b = list(map(F, caso["b"]))
                x = list(map(F, caso.get("x0", [0] * len(b))))
                for esperado in referencia["iteraciones_gauss_seidel"]:
                    anterior = list(x)
                    nuevo, detalle = paso_gauss_seidel(A, b, x)
                    self.assertEqual(nuevo, list(map(F, esperado)))
                    self.assertEqual(x, anterior)
                    self.assertIsNot(nuevo, x)
                    for i, d in enumerate(detalle):
                        self.assertEqual(set(d), {"i", "formula_latex",
                            "sustitucion_latex", "valor", "usa_nuevos"})
                        self.assertEqual(d["i"], i)
                        self.assertEqual(d["valor"], nuevo[i])
                        self.assertEqual(d["usa_nuevos"], list(range(i)))
                        self.assertIn("x_j^{(k+1)}", d["formula_latex"])
                        self.assertIn("x_j^{(k)}", d["formula_latex"])
                    x = nuevo

    def test_consumo_inmediato_distingue_jacobi(self):
        A = [[F(4), F(1)], [F(2), F(3)]]
        nuevo, _ = paso_gauss_seidel(A, [F(1), F(2)], [F(0), F(0)])
        self.assertEqual(nuevo, [F(1, 4), F(1, 2)])
        self.assertNotEqual(nuevo[1], F(2, 3))  # resultado incorrecto si usa x viejo
        self.assertEqual(A, [[F(4), F(1)], [F(2), F(3)]])

    def test_diagonal_nula_informa_fila(self):
        with self.assertRaisesRegex(ValueError, "fila 1"):
            paso_gauss_seidel([[0, 1], [1, 2]], [1, 2], [0, 0])

    def test_paso_float_principal(self):
        c = CASOS["principal"]
        x, _ = paso_gauss_seidel([[float(v) for v in r] for r in c["A"]],
                                 list(map(float, c["b"])), [0.0] * 4)
        for obtenido, esperado in zip(x, REFERENCIAS["principal"]["iteraciones_gauss_seidel"][0]):
            self.assertAlmostEqual(obtenido, float(F(esperado)), places=14)


if __name__ == "__main__":
    unittest.main()
