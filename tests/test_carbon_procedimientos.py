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
        from src.secante.metodo import resolver_secante
        casos = [("biseccion", resolver_biseccion("x^2", 0, 1)),
                 ("regla-falsa", resolver_regla_falsa("x^2", 0, 1)),
                 ("newton-raphson", resolver_newton("x^2", 0)),
                 ("secante", resolver_secante("x^2", 0, 1))]
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

    def test_analisis_exporta_orden_y_diagonal_nula(self):
        from src.iterativos.resolver import resolver_iterativo
        for ordenar in (False, True):
            with self.subTest(reordenar=ordenar):
                res = resolver_iterativo([[0, 3], [2, 1]], [3, 3], "jacobi", reordenar=ordenar)
                proc = adjuntar("/api/iterativos/resolver", res, {})["procedimiento"]
                detalles = " ".join(proc["pasos"][0]["detalles"])
                self.assertIn("Diagonal nula: " + ("no" if ordenar else "sí"), detalles)
                self.assertIn("Orden de ecuaciones: " + ("2, 1" if ordenar else "1, 2"), detalles)
                self.assertIn(res["analisis"]["reordenamiento"]["motivo"], detalles)

    def test_comparar_exporta_garantia_sdp_de_gauss_seidel(self):
        from src.iterativos.resolver import comparar_metodos
        res = comparar_metodos([[1, .75, .75], [.75, 1, .75], [.75, .75, 1]], [1, 1, 1],
                               max_iteraciones=4)
        proc = adjuntar("/api/iterativos/comparar", res, {})["procedimiento"]
        analisis_gs = [p for p in proc["pasos"] if "Gauss-Seidel" in p["titulo"]
                       and "Análisis" in p["titulo"]]
        self.assertEqual(len(analisis_gs), 1)
        self.assertIn("demostrada", analisis_gs[0]["texto"])
        self.assertIn("Matriz simétrica definida positiva verificada exactamente.", analisis_gs[0]["detalles"])
