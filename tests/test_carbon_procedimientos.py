"""Regresiones de información omitida por los adaptadores numéricos."""
import unittest

from src.procedimientos import adjuntar
from src.procedimientos.base import validar
from src.ui.web_server import servidor_local
from tests.test_golden_api import consultar


class TestProcedimientosCarbon(unittest.TestCase):
    def test_derivar_desde_newton_incluye_procedimiento(self):
        with servidor_local() as url:
            estado, respuesta = consultar(url, "/api/newton-raphson/derivar", {"funcion": "x^2"})
        self.assertEqual(estado, 200)
        proc = validar(respuesta["procedimiento"])
        self.assertEqual(proc["resultado"][0]["latex"], respuesta["derivada_latex"])

    def test_aviso_explica_certificacion_fallida(self):
        from src.biseccion.metodo import resolver_biseccion
        from src.regla_falsa.metodo import resolver_regla_falsa
        from src.newton_raphson.metodo import resolver_newton
        casos = [("biseccion", resolver_biseccion("x^2", 0, 1)),
                 ("regla-falsa", resolver_regla_falsa("x^2", 0, 1)),
                 ("newton-raphson", resolver_newton("x^2", 0))]
        for modulo, respuesta in casos:
            with self.subTest(modulo=modulo):
                self.assertEqual(respuesta["motivo"], "no_certificada")
                avisos = adjuntar(f"/api/{modulo}/resolver", respuesta, {})["procedimiento"]["avisos"]
                self.assertIn("certificar", " ".join(avisos))
                self.assertNotIn("Tolerancia no alcanzada.", avisos)

    def test_regla_falsa_conserva_advertencia_del_motor(self):
        from src.regla_falsa.metodo import resolver_regla_falsa
        res = resolver_regla_falsa("x^10-1", 0, 1.3, tolerancia=2)
        self.assertTrue(res["advertencias"])
        avisos = adjuntar("/api/regla-falsa/resolver", res, {})["procedimiento"]["avisos"]
        self.assertTrue(all(aviso in avisos for aviso in res["advertencias"]))
