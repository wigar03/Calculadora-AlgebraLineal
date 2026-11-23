"""Pruebas del analizador de sistemas lineales en texto (src/iterativos/sistema_texto.py)."""

from fractions import Fraction
import unittest

from src.iterativos.sistema_texto import leer_ecuaciones
from tests.validacion.banco_iterativos import CASOS


class TestSistemaTextoValido(unittest.TestCase):
    def test_ejemplo_principal_presentacion(self):
        texto = (
            "10x1 − x2 + 2x3 = 6\n"
            "-x₁ + 11x₂ − x₃ + 3x₄ = 25\n"
            "2x_1 - x_2 + 10x_3 - x_4 = -11\n"
            "3x2 - x3 + 8x4 = 15\n"
        )
        A, b, nombres = leer_ecuaciones(texto)
        esperado = CASOS["principal"]
        self.assertEqual(nombres, ["x_1", "x_2", "x_3", "x_4"])
        self.assertEqual(A, [[Fraction(v) for v in fila] for fila in esperado["A"]])
        self.assertEqual(b, [Fraction(v) for v in esperado["b"]])

    def test_practica_presentacion(self):
        texto = (
            "8x₁ − x₂ + x₃ = 8\n"
            "−x₁ + 10x₂ − 2x₃ + x₄ = 7\n"
            "x₁ − 2x₂ + 9x₃ − x₄ = −4\n"
            "x₂ − x₃ + 7x₄ = 5\n"
        )
        A, b, nombres = leer_ecuaciones(texto)
        esperado = CASOS["practica"]
        self.assertEqual(nombres, ["x_1", "x_2", "x_3", "x_4"])
        self.assertEqual(A, [[Fraction(v) for v in fila] for fila in esperado["A"]])
        self.assertEqual(b, [Fraction(v) for v in esperado["b"]])

    def test_fracciones_decimales_notacion_cientifica_y_operadores(self):
        texto = (
            "x_1 + (1/2)x_2 = 3/4\n"
            "0.5*x1 - 2*x2 = 1\n"
        )
        A, b, nombres = leer_ecuaciones(texto)
        self.assertEqual(nombres, ["x_1", "x_2"])
        self.assertEqual(A, [[Fraction(1), Fraction(1, 2)], [Fraction(1, 2), Fraction(-2)]])
        self.assertEqual(b, [Fraction(3, 4), Fraction(1)])

        texto_sci = (
            "1.5e-2*x1 + x2/4 = -1e-1\n"
            "3x1 + 2x1 - (3/2)x2 - 5 = 0\n"
        )
        A2, b2, _ = leer_ecuaciones(texto_sci)
        self.assertEqual(A2, [[Fraction(3, 200), Fraction(1, 4)], [Fraction(5), Fraction(-3, 2)]])
        self.assertEqual(b2, [Fraction(-1, 10), Fraction(5)])

    def test_sistema_10x10_y_coeficiente_cero(self):
        caso = CASOS["dd_10x10"]
        lineas = []
        for i, fila in enumerate(caso["A"]):
            terminos = [f"- {c[1:]}x_{j+1}" if c.startswith("-") else f"+ {c}x_{j+1}" for j, c in enumerate(fila)]
            lineas.append(" ".join(terminos) + f" = {caso['b'][i]}")
        A, b, nombres = leer_ecuaciones("\n".join(lineas))
        self.assertEqual(nombres, [f"x_{i}" for i in range(1, 11)])
        self.assertEqual(A, [[Fraction(v) for v in fila] for fila in caso["A"]])
        self.assertEqual(b, [Fraction(v) for v in caso["b"]])

        A0, b0, n0 = leer_ecuaciones("0x1 + x2 = 1\n0x1 + x2 = 1")
        self.assertEqual(n0, ["x_1", "x_2"])
        self.assertEqual(A0, [[Fraction(0), Fraction(1)], [Fraction(0), Fraction(1)]])
        self.assertEqual(b0, [Fraction(1), Fraction(1)])


if __name__ == "__main__":
    unittest.main()
