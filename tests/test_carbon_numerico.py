"""Regresiones de diagnósticos numéricos halladas en la auditoría Carbon."""
import unittest
from fractions import Fraction

from src.core.arithmetic import parse_number, validar_matriz_numerica
from src.core.limites import DIGITOS_MAX, LimiteExcedido
from src.iterativos.resolver import resolver_iterativo
from src.ui.web_server import servidor_local
from tests.test_golden_api import consultar


class TestDiagnosticosCarbon(unittest.TestCase):
    def test_coma_decimal_en_parametros_y_llamadas(self):
        from src.biseccion.expresiones import Expresion, numero_real
        mensaje = "No se admite la coma ','; use punto decimal '.' (por ejemplo, 0.5)."
        for texto in ("0,5", "sin(0,5)", "cos(1,25)+x", "0,5+x"):
            with self.subTest(texto=texto):
                with self.assertRaises(ValueError) as ctx:
                    (numero_real(texto) if texto == "0,5" else Expresion(texto))
                self.assertEqual(str(ctx.exception), mensaje)
        with self.assertRaisesRegex(ValueError, "exactamente un argumento"):
            Expresion("sin(x,x)")

    def test_coma_decimal_en_racional_y_tolerancia_iterativa(self):
        mensaje = "No se admite la coma ',' en '0,5'. Use punto decimal '.' (por ejemplo, 0.5)."
        for llamada in (lambda: parse_number("0,5"),
                        lambda: resolver_iterativo([[2]], [1], "jacobi", tolerancia="0,5")):
            with self.subTest(llamada=llamada):
                with self.assertRaises(ValueError) as ctx:
                    llamada()
                self.assertEqual(str(ctx.exception), mensaje)
        self.assertEqual(parse_number("0.5"), Fraction(1, 2))

    def test_error_de_celda_identifica_fila_y_componente(self):
        with self.assertRaisesRegex(ValueError, "^Fila 2, Componente 2 inválida"):
            validar_matriz_numerica([[1, 2], [3, "abc"]])
        with self.assertRaises(LimiteExcedido):
            validar_matriz_numerica([["1" * (DIGITOS_MAX + 1)]])

    def test_newton_dominio_inicial_por_api(self):
        with servidor_local() as url:
            estado, respuesta = consultar(url, "/api/newton-raphson/resolver",
                                         {"funcion": "ln(x)", "x0": -1})
        self.assertEqual(estado, 400)
        self.assertEqual(respuesta["tipo"], "dominio")
        self.assertTrue(respuesta["error"].startswith("Error de dominio:"))
