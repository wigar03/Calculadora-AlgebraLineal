"""Pruebas de diagnósticos específicos de sintaxis y dominio en Expresion."""

import math
import unittest

from src.biseccion.expresiones import Expresion


class TestDiagnosticosSintaxis(unittest.TestCase):
    def assert_sintaxis(self, texto, fragmentos):
        with self.assertRaises(ValueError) as ctx:
            Expresion(texto)
        msg = str(ctx.exception)
        self.assertIn("Error de sintaxis", msg, f"{texto!r} -> {msg!r}")
        for frag in fragmentos:
            self.assertIn(frag.lower(), msg.lower(), f"Falta {frag!r} en {msg!r}")

    def test_multiplicacion_omitida(self):
        casos = [
            ("2x", ["multiplicación", "2*x"]), ("4x - 9", ["multiplicación", "4*x"]),
            ("3x^2 - 1", ["multiplicación", "3*x"]), ("x(x+1)", ["multiplicación", "x*("]),
            ("2(x+1)", ["multiplicación", "2*("]), ("(x+1)(x-1)", ["multiplicación", ")*("]),
            ("3 sen(x)", ["multiplicación", "3*sen"]), ("sin(x)cos(x)", ["multiplicación", ")*cos"]),
            ("2e^x", ["multiplicación", "2*e"]),
        ]
        for texto, frags in casos:
            with self.subTest(texto=texto):
                self.assert_sintaxis(texto, frags)

    def test_parentesis_y_agrupacion(self):
        for texto, frags in [
            ("(x+1", ["paréntesis", "posición 1"]), ("sin((x+1)", ["paréntesis", "posición 4"]),
            ("x+1)", ["paréntesis", "posición 4"]), ("sin(x))", ["paréntesis", "posición 7"]),
            ("() + 1", ["vacíos", "posición 1"]), ("[x]", ["delimitador", "["]),
        ]:
            with self.subTest(texto=texto):
                self.assert_sintaxis(texto, frags)

    def test_operadores_y_potencias_mal_escritas(self):
        for texto, frags in [
            ("2+*x", ["consecutivos", "+*"]), ("x*/2", ["consecutivos", "*/"]),
            ("x-*2", ["consecutivos", "-*"]), ("x//2", ["'//'", "/"]),
            ("x^", ["potencia", "incompleta"]), ("x**", ["potencia", "incompleta"]),
            ("x^^2", ["potencia", "^^"]), ("x***2", ["potencia", "***"]),
            ("^2", ["potencia", "base"]),
        ]:
            with self.subTest(texto=texto):
                self.assert_sintaxis(texto, frags)

    def test_funciones_desconocidas_argumentos_y_variables(self):
        for texto, frags in [
            ("sinn(x)", ["desconocida", "sin"]), ("lg(x)", ["desconocida", "ln", "log"]),
            ("coss(x)", ["desconocida", "cos"]), ("raiz(x)", ["desconocida", "sqrt"]),
            ("foo(x)", ["desconocida", "admitidas"]), ("sin()", ["requiere un argumento", "sin"]),
            ("ln()", ["requiere un argumento", "ln"]), ("sin(x, x)", ["exactamente un argumento"]),
            ("sin + 1", ["función", "paréntesis"]), ("ln x", ["función", "paréntesis"]),
            ("y + 1", ["variable no reconocida", "y"]), ("t^2 - 1", ["variable no reconocida", "t"]),
        ]:
            with self.subTest(texto=texto):
                self.assert_sintaxis(texto, frags)

    def test_expresion_incompleta_e_igualdad_mal_formada(self):
        for texto, frags in [
            ("x+", ["incompleta", "+"]), ("2*", ["incompleta", "*"]), ("1/", ["incompleta", "/"]),
            ("*x", ["incompleta", "*"]), ("(x+)", ["incompleta", "+"]), ("=x", ["lado izquierdo", "="]),
            ("x=", ["lado derecho", "="]), ("x==2", ["igualdad", "=="]),
            ("x=1=2", ["2 signos '='"]), ("sin(x=1)", ["paréntesis", "="]), ("x<=2", ["comparación", "<="]),
        ]:
            with self.subTest(texto=texto):
                self.assert_sintaxis(texto, frags)


class TestDiagnosticosDominio(unittest.TestCase):
    def test_distingue_errores_de_dominio(self):
        casos = [
            ("ln(x)", 0, "u > 0"), ("ln(x)", -2, "u > 0"), ("log(x)", -1, "u > 0"),
            ("sqrt(x)", -1, "u >= 0"), ("1/x", 0, "división por cero"),
            ("tan(x)", math.pi / 2, "polo"), ("asin(x)", 2, "-1 <= u <= 1"),
            ("x^0.5", -1, "base negativa"), ("x^(-1)", 0, "división por cero"),
            ("exp(x)", 1000, "desborda"), ("2^1001", 0, "1000"),
        ]
        for texto, x, esperado in casos:
            with self.subTest(texto=texto, x=x):
                with self.assertRaises(ValueError) as ctx:
                    Expresion(texto)(x)
                msg = str(ctx.exception)
                self.assertIn("Error de dominio", msg)
                self.assertNotIn("Error de sintaxis", msg)
                self.assertIn(esperado, msg.lower())


if __name__ == "__main__":
    unittest.main()
