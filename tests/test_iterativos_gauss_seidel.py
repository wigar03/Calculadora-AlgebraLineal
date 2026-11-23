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

    def test_subnormales_conservan_el_valor_recien_actualizado(self):
        A = [[1e-200, 5e-201], [5e-201, 1e-200]]
        b, x0 = [float("5e-324")] * 2, [0.0, 0.0]
        nuevo, detalle = paso_gauss_seidel(A, b, x0)
        primero = float(F(b[0]) / F(A[0][0]))
        segundo = float((F(b[1]) - F(A[1][0]) * F(primero)) / F(A[1][1]))
        self.assertAlmostEqual(nuevo[0] / primero, 1, places=14)
        self.assertAlmostEqual(nuevo[1] / segundo, 1, places=14)
        self.assertEqual(detalle[1]["usa_nuevos"], [0])
        self.assertEqual(x0, [0, 0])

    def test_diagonal_nula_informa_fila(self):
        with self.assertRaisesRegex(ValueError, "fila 1"):
            paso_gauss_seidel([[0, 1], [1, 2]], [1, 2], [0, 0])

    def test_paso_float_principal(self):
        c = CASOS["principal"]
        x, _ = paso_gauss_seidel([[float(v) for v in r] for r in c["A"]],
                                 list(map(float, c["b"])), [0.0] * 4)
        for obtenido, esperado in zip(x, REFERENCIAS["principal"]["iteraciones_gauss_seidel"][0]):
            self.assertAlmostEqual(obtenido, float(F(esperado)), places=14)

    def test_tres_barridos_float_contra_el_banco_a_1e_12(self):
        for nombre, caso in CASOS.items():
            referencia = REFERENCIAS[nombre]
            if referencia["diagonal_nula"]:
                continue
            A = [[float(F(v)) for v in fila] for fila in caso["A"]]
            b = [float(F(v)) for v in caso["b"]]
            x = [float(F(v)) for v in caso.get("x0", [0] * len(b))]
            for k, esperados in enumerate(referencia["iteraciones_gauss_seidel"], 1):
                with self.subTest(caso=nombre, k=k):
                    x, detalle = paso_gauss_seidel(A, b, x)
                    for obtenido, esperado in zip(x, esperados):
                        valor = float(F(esperado))
                        self.assertAlmostEqual(obtenido, valor, delta=1e-12 * max(1, abs(valor)))
                    self.assertEqual([d["valor"] for d in detalle], x)

    def test_normalizar_no_crea_cocientes_no_representables(self):
        A = [[1e-308, 1e308], [0.0, 1.0]]
        x, _ = paso_gauss_seidel(A, [1e-308, 0.0], [0.0, 0.0])
        self.assertEqual(x, [1, 0])  # evita infinito * 0 al normalizar
        A = [[1e308, 1e-308], [0.0, 1.0]]
        x, _ = paso_gauss_seidel(A, [0.0, 1e308], [0.0, 1e308])
        esperado = float(-F(A[0][1]) * F(1e308) / F(A[0][0]))
        self.assertNotEqual(esperado, 0)
        self.assertEqual(x, [esperado, 1e308])  # evita perder el cociente a cero

    def test_latex_cientifico_y_dimensiones(self):
        _, detalle = paso_gauss_seidel([[1.0]], [1e-20], [0.0])
        self.assertIn(r"\times 10^{-20}", detalle[0]["sustitucion_latex"])
        for A, b, x in (([], [], []), ([[1, 2]], [1], [0]), ([[1]], [1], [])):
            with self.assertRaisesRegex(ValueError, "dimensión"):
                paso_gauss_seidel(A, b, x)


if __name__ == "__main__":
    unittest.main()
