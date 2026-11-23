"""Límites de los motores, independientes de la validación HTTP."""
import unittest
from fractions import Fraction
from unittest.mock import patch

from src.core.arithmetic import parse_number
from src.core.limites import DIGITOS_MAX, EXPONENTE_MAX, LimiteExcedido


class TestNumerosAcotados(unittest.TestCase):
    def test_limites_antes_de_construir_fraction(self):
        entradas = ["1e5000000", "1e-5000000", "9" * (DIGITOS_MAX + 1),
                    "1/" + "9" * (DIGITOS_MAX + 1), 10 ** DIGITOS_MAX,
                    "1e" + "9" * 5000, "0." + "1" * (DIGITOS_MAX + 1)]
        for entrada in entradas:
            with self.subTest(entrada=str(entrada)[:80]):
                class NoConstruir(Fraction):
                    def __new__(cls, *args):
                        raise AssertionError("Se construyó Fraction antes de validar")
                with patch("src.core.arithmetic.Fraction", NoConstruir):
                    with self.assertRaises(LimiteExcedido):
                        parse_number(entrada)

    def test_fronteras_y_sintaxis_existente(self):
        for texto in ("9" * DIGITOS_MAX, "-3/7", "1.25", "1_000/2_000", "", " 2 / 3 "):
            with self.subTest(texto=texto):
                self.assertEqual(parse_number(texto), Fraction(texto.strip() or "0"))
        self.assertEqual(parse_number(f"1e{EXPONENTE_MAX}"), Fraction(10 ** EXPONENTE_MAX))
        self.assertEqual(parse_number(f"1e-{EXPONENTE_MAX}"), Fraction(1, 10 ** EXPONENTE_MAX))

    def test_denominador_cero_es_valueerror_en_espanol(self):
        with self.assertRaisesRegex(ValueError, "denominador.*cero"):
            parse_number("2/0")


if __name__ == "__main__":
    unittest.main()
