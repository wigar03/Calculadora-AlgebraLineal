"""Pruebas del analizador de sistemas lineales en texto (src/iterativos/sistema_texto.py)."""

from fractions import Fraction
import json
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src.iterativos.sistema_texto import leer_ecuaciones
from src.ui.web_server import servidor_local
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


class TestSistemaTextoErrores(unittest.TestCase):
    def _assert_error(self, texto, patron):
        with self.assertRaisesRegex(ValueError, patron):
            leer_ecuaciones(texto)

    def test_terminos_no_lineales(self):
        self._assert_error("x1*x2 + x2 = 1\nx1 + x2 = 2", r"no lineal|producto")
        self._assert_error("x1 x2 + x1 = 1\nx1 + x2 = 2", r"no lineal|producto")
        self._assert_error("x1^2 + x2 = 1\nx1 + x2 = 2", r"no lineal|potencia")
        self._assert_error("x1**2 + x2 = 1\nx1 + x2 = 2", r"no lineal|potencia")
        self._assert_error("x1² + x2 = 1\nx1 + x2 = 2", r"no lineal|exponente")
        self._assert_error("sin(x1) + x2 = 1\nx1 + x2 = 2", r"no lineal|funciones")
        self._assert_error("log10(x1) + x2 = 1\nx1 + x2 = 2", r"no lineal|funciones")
        self._assert_error("1/x1 + x2 = 1\nx1 + x2 = 2", r"no lineal|división")
        self._assert_error("1/2x1 + x2 = 1\nx1 + x2 = 2", r"no lineal|división")

    def test_variables_e_indices_invalidos(self):
        self._assert_error("2x + 3y = 1\nx - y = 0", r"sin índice")
        self._assert_error("x0 + x1 = 1\nx0 - x1 = 0", r"índice inválido")
        self._assert_error("x_a + x_1 = 1\nx_1 = 2", r"inválido")
        self._assert_error("x1 + y2 = 1\nx1 - y2 = 0", r"mezclaron")
        self._assert_error("x1 + x3 = 5\n2x1 - x3 = 1", r"inconsistentes.*x_2")

    def test_igualdad_lado_derecho_y_cuadrado(self):
        self._assert_error("10x1 - x2 + 2x3", r"falta el signo '='")
        self._assert_error("x1 + x2 = 3 = 4", r"más de un signo '='")
        self._assert_error("x1 + x2 =", r"ambos lados")
        self._assert_error("10x1 - x2 = 6 + x3\nx1 + x2 + x3 = 1\nx1 - x3 = 0", r"lado derecho")
        self._assert_error("x1 + x2 = 1\nx1 - x2 = 0\n2x1 + x2 = 3", r"no es cuadrado")
        self._assert_error("x1 + x2 + x3 = 1\nx1 - x2 + x3 = 0", r"no es cuadrado")

    def test_sintaxis_y_limites(self):
        self._assert_error("", r"al menos una ecuación")
        self._assert_error("(1/0)x1 + x2 = 1\nx1 + x2 = 2", r"división por cero")
        self._assert_error("0,5x1 + x2 = 1\nx1 + x2 = 2", r"coma")
        self._assert_error("x1 + x2 = 1; x1 - x2 = 0", r"una sola ecuación")
        self._assert_error("3 = 3\nx1 = 1", r"no contiene incógnitas")
        self._assert_error("2 3x1 + x2 = 1\nx1 + x2 = 2", r"operador|inesperado")
        self._assert_error("(1/2 x1 + x2 = 1\nx1 + x2 = 2", r"paréntesis")


class TestSistemaTextoRobustez(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = cls.enterClassContext(servidor_local())

    def _post_texto(self, texto, estado=400):
        req = Request(
            self.url + "/api/iterativos/texto",
            data=json.dumps({"texto": texto}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            resp = urlopen(req, timeout=10)
        except HTTPError as exc:
            resp = exc
        with resp:
            self.assertEqual(resp.status, estado)
            return json.loads(resp.read().decode("utf-8"))

    def test_indice_enorme_y_exceso_ecuaciones_rechazo_temprano_breve(self):
        with self.assertRaises(ValueError) as ctx:
            leer_ecuaciones("x200000 = 1")
        self.assertLess(len(str(ctx.exception)), 300)
        self.assertRegex(str(ctx.exception), r"Línea 1.*máximo|20")
        r = self._post_texto("x200000 = 1", estado=400)
        self.assertLess(len(r["error"]), 300)

        muchas = "x1 = 1\n" * 100000
        with self.assertRaisesRegex(ValueError, r"límite|máximo|20"):
            leer_ecuaciones(muchas)
        r2 = self._post_texto(muchas, estado=413)
        self.assertEqual(r2["tipo"], "limite")
        self.assertLess(len(r2["error"]), 300)
        with self.assertRaisesRegex(ValueError, r"máximo.*20"):
            leer_ecuaciones("x1 = 1\n" * 21)

    def test_parentesis_profundos_y_signos_unarios_sin_recursion_error(self):
        anidado = "(" * 300 + "x1" + ")" * 300 + " = 1"
        with self.assertRaisesRegex(ValueError, r"Línea 1.*paréntesis"):
            leer_ecuaciones(anidado)
        r = self._post_texto(anidado, estado=400)
        self.assertNotIn("recursion", r["error"].lower())
        self.assertRegex(r["error"], r"Línea 1.*paréntesis")

        signos = "+" * 1500 + "x1 = 1"
        A, b, nombres = leer_ecuaciones(signos)
        self.assertEqual((A, b, nombres), ([[Fraction(1)]], [Fraction(1)], ["x_1"]))
        r2 = self._post_texto(signos, estado=200)
        self.assertEqual(r2, {"A": [["1"]], "b": ["1"], "nombres": ["x_1"]})

    def test_magnitud_extrema_sin_error_interno_4300_digitos(self):
        for caso in ("1e1000000x1 = 1", "1e-1000000x1 = 1", "9" * 5000 + "x1 = 1", "(1e200)*(1e200)*x1 = 1"):
            with self.subTest(caso=caso[:30]):
                with self.assertRaises(ValueError) as ctx:
                    leer_ecuaciones(caso)
                msg = str(ctx.exception)
                self.assertNotIn("4300", msg)
                self.assertNotIn("set_int_max_str_digits", msg)
                self.assertRegex(msg, r"Línea 1.*(magnitud|rango|largo|representable)")
                r = self._post_texto(caso, estado=400)
                self.assertNotIn("4300", r["error"])
                self.assertNotIn("set_int_max_str_digits", r["error"])


if __name__ == "__main__":
    unittest.main()
