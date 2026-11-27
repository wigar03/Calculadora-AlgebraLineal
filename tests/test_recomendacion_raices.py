"""INC-033: orientación previa con dominio y condiciones explícitas."""
import unittest

from src.raices.recomendacion import recomendar_metodo
from src.ui.web_server import servidor_local
from tests.test_golden_api import consultar
from tests.test_banco_raices import REFERENCIAS
from tests.validacion.banco_raices import ECUACIONES


class TestRecomendacionRaices(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = cls.enterClassContext(servidor_local())

    def recomendar(self, funcion, **datos):
        status, res = consultar(self.url, "/api/raices/recomendar", dict(funcion=funcion, **datos))
        self.assertEqual(status, 200, res)
        self.assertIn("no garantiza", res["justificacion"])
        return res, {m["metodo"]: m for m in res["metodos"]}

    def test_polinomio_con_intervalo_y_semilla(self):
        res, metodos = self.recomendar(ECUACIONES["III-1"]["funcion"], a=2, b=3, x0=3)
        self.assertTrue(metodos["biseccion"]["apto"])
        self.assertTrue(metodos["regla_falsa"]["apto"])
        self.assertTrue(metodos["newton_raphson"]["apto"])
        self.assertIn("estancamiento", " ".join(metodos["regla_falsa"]["motivos"]))
        self.assertIn(res["recomendado"], metodos)

    def test_dominio_restringido_prefiere_intervalo(self):
        res, _ = self.recomendar(ECUACIONES["III-4"]["funcion"], a=1, b=2, x0=2)
        self.assertEqual(res["recomendado"], "biseccion")
        self.assertIn("dominio", res["justificacion"])

    def test_raiz_doble_no_recomienda_a_ciegas(self):
        res, metodos = self.recomendar("(x-1)^2", a=0, b=2, x0=1)
        self.assertIsNone(res["recomendado"])
        self.assertFalse(metodos["newton_raphson"]["apto"])
        self.assertIn("múltiple", " ".join(metodos["newton_raphson"]["motivos"]))

    def test_intervalo_con_polo_se_rechaza(self):
        _, metodos = self.recomendar(ECUACIONES["IV-4"]["funcion"], a=1.5, b=2.5)
        for m in ("biseccion", "regla_falsa"):
            self.assertFalse(metodos[m]["apto"])
            self.assertIn("dominio", " ".join(metodos[m]["motivos"]))

    def test_sin_datos_pide_intervalo_o_semillas(self):
        res, metodos = self.recomendar("x^3-4*x-9")
        self.assertIsNone(res["recomendado"])
        self.assertFalse(any(m["apto"] for m in metodos.values()))
        self.assertIn("intervalo", res["justificacion"])

    def test_condicion_positiva_no_nula_en_las_cuatro_rutas(self):
        f = ECUACIONES["III-10"]["funcion"]
        referencia = float(REFERENCIAS["III-10"]["raices_en_[-10,10]"][-1])
        for modulo, cerca, adecuados in (
            ("biseccion", dict(a=0, b=1), dict(a=2, b=3)),
            ("regla-falsa", dict(xl=0, xu=1), dict(xl=2, xu=3)),
            ("newton-raphson", dict(x0=0), dict(x0=2)),
            ("secante", dict(x0=0, x1=1), dict(x0=2, x1=3))):
            for iniciales, cumple in ((cerca, False), (adecuados, True)):
                status, res = consultar(self.url, f"/api/{modulo}/resolver", dict(
                    funcion=f, condicion="positiva_no_nula", tolerancia=1e-8, **iniciales))
                self.assertEqual(status, 200, res)
                self.assertEqual(res["convergio"], cumple)
                if cumple:
                    self.assertAlmostEqual(res["raiz"], referencia, delta=1e-6)
                else:
                    self.assertEqual(res["motivo"], "raiz_no_admisible")
                self.assertTrue(any("positiva" in it["latex"] for it in res["procedimiento"]["entrada"]))

    def test_entradas_invalidas_conservan_error_de_entrada(self):
        for datos in ({}, {"funcion": "2x"}, {"funcion": "x", "condicion": "negativa"},
                      {"funcion": "x", "a": "texto", "b": 1}):
            estado, res = consultar(self.url, "/api/raices/recomendar", datos)
            self.assertEqual(estado, 400, res)
            self.assertIn("error", res)


class TestMotorRecomendacion(unittest.TestCase):
    def test_derivada_costosa_prefiere_secante_sin_intervalo(self):
        f = "*".join(f"(x+{i})" for i in range(1, 11))+"-100"
        res = recomendar_metodo(f, x0=.1, x1=.2)
        self.assertEqual(res["recomendado"], "secante")
        newton = next(m for m in res["metodos"] if m["metodo"] == "newton_raphson")
        self.assertIn("costosa", " ".join(newton["motivos"]))

    def test_consejo_no_depende_de_la_escala_de_la_funcion(self):
        for f in ("x^3-4*x-9", "1e-100*(x^3-4*x-9)"):
            res = recomendar_metodo(f, x0=3)
            self.assertEqual(res["recomendado"], "newton_raphson")

    def test_intervalo_positivo_no_recomienda_raiz_cero_excluida(self):
        res = recomendar_metodo("x^2-5*sin(x)", a=0, b=1, x0=0, x1=1,
                                condicion="positiva_no_nula")
        self.assertIsNone(res["recomendado"])
        self.assertFalse(any(m["apto"] for m in res["metodos"]))

    def test_curvatura_no_se_presume_por_muestreo(self):
        res = recomendar_metodo("sin(x)", a=-1, b=1)
        rf = next(m for m in res["metodos"] if m["metodo"] == "regla_falsa")
        self.assertNotIn("conserva signo", " ".join(rf["motivos"]))

    def test_semilla_fuera_del_dominio_y_par_invalido(self):
        for datos in (dict(a=-1, b=0, x0=0, x1=-1), dict(x0=0, x1=0)):
            res = recomendar_metodo("ln(x)-1", **datos)
            self.assertIsNone(res["recomendado"])
            self.assertFalse(any(m["apto"] for m in res["metodos"]))
