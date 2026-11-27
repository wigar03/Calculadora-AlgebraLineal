"""Forma A·X = B antes de la reducción, con datos exactos y matrices rectangulares."""
import unittest

from src.ecuaciones.ecuacion_matricial import resolver_ecuacion_matricial
from src.ui.web_server import servidor_local
from tests.test_golden_api import consultar
from tests.test_validacion_banco_final import REF
from tests.validacion.banco_final import SISTEMAS_RECTANGULARES
from tests.validacion.banco_lineales import SISTEMAS


class TestFormaMatricial(unittest.TestCase):
    def test_http_banco_i_y_rectangulares_forma_antes_de_aumentada(self):
        with servidor_local() as url:
            for clave, datos in {**SISTEMAS, **SISTEMAS_RECTANGULARES}.items():
                with self.subTest(clave=clave):
                    estado, r = consultar(url, "/api/ecuaciones/resolver", datos)
                    self.assertEqual(estado, 200)
                    forma = r["forma_matricial"]
                    self.assertEqual(forma["A"], [[str(v) for v in f] for f in datos["A"]])
                    self.assertEqual(forma["B"], [str(v) for v in datos["b"]])
                    self.assertEqual(forma["X"], [f"x_{j+1}" for j in range(len(datos["A"][0]))])
                    p = r["procedimiento"]["pasos"]
                    self.assertEqual(r["procedimiento"]["entrada"][0]["latex"], forma["latex"])
                    self.assertEqual(p[0]["latex"], [forma["latex"]])
                    self.assertEqual(p[1]["matriz"], r["pasos"][0]["matrix"])
                    self.assertIn(r"A \cdot X = B", forma["latex"])
                    if clave in REF["sistemas"]:
                        self.assertEqual(r["tipo_sistema"], REF["sistemas"][clave]["tipo"])

    def test_motor_conserva_nombres_y_fracciones_sin_redondeo(self):
        r = resolver_ecuacion_matricial([["1/3", "-2/7"]], ["5/11"], ["u", "x_10"])
        self.assertEqual(r.forma_matricial["X"], ["u", "x_10"])
        for fragmento in (r"\frac{1}{3}", r"-\frac{2}{7}", r"\frac{5}{11}", "x_{10}"):
            self.assertIn(fragmento, r.forma_matricial["latex"])
