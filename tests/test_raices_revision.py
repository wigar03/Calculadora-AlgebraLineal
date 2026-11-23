"""Regresiones HTTP de los siete hallazgos de la revisión cruzada."""
import json
import math
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from src.regla_falsa.dominio import ExpresionNumerica
from src.ui.web_server import servidor_local

IV3 = "exp(1/x)+2*x/tan(x)-2"


class TestRevisionRaices(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = cls.enterClassContext(servidor_local())

    def resolver(self, metodo, **datos):
        datos = dict(tolerancia=1e-6, max_iteraciones=200, **datos)
        req = Request(self.url+"/api/"+metodo+"/resolver", json.dumps(datos).encode(),
                      {"Content-Type": "application/json"})
        try:
            r = urlopen(req, timeout=10)
        except HTTPError as exc:
            r = exc
        with r:
            return r.status, json.loads(r.read())

    def test_1_raiz_cero_aproximada_no_es_positiva_no_nula(self):
        for a, b in ((.2, .5), (.25, .75), (.75, 1.25)):
            with self.subTest(a=a, b=b):
                estado, r = self.resolver("secante", funcion="x^2-5*sin(x)", x0=a, x1=b,
                                          condicion="positiva_no_nula")
                self.assertEqual(estado, 200)
                self.assertFalse(r["convergio"], r)

    def test_2_limite_excluido_no_es_raiz_de_iv3(self):
        for metodo, semillas in (("newton-raphson", dict(x0=-2.75)),
                                  ("secante", dict(x0=-1, x1=-.5))):
            with self.subTest(metodo=metodo):
                estado, r = self.resolver(metodo, funcion=IV3, **semillas)
                self.assertEqual(estado, 200)
                self.assertFalse(r["convergio"], r)

    def test_3_tan_conserva_valores_definidos(self):
        x = math.nextafter(math.pi, math.inf)
        self.assertEqual(ExpresionNumerica("1e16*tan(x)")(x), 1e16*math.tan(x))
        self.assertEqual(ExpresionNumerica("tan(x)")(1e16), math.tan(1e16))

    def test_4_cuadratica_positiva_no_inventa_polos(self):
        for f, a, b, raiz in (("(x-100000000)/((x-100000000)^2+1)", 99999999, 100000001, 1e8),
                              ("(x-1)/((x-1)^2+1e-16)", 0, 2, 1)):
            with self.subTest(f=f):
                estado, r = self.resolver("biseccion", funcion=f, a=a, b=b)
                self.assertEqual(estado, 200, r)
                self.assertTrue(r["convergio"])
                self.assertEqual(r["raiz"], raiz)

    def test_5_exponencial_sin_raices_no_converge(self):
        estado, r = self.resolver("newton-raphson", funcion="exp(1e8*x)", x0=1e-6)
        self.assertEqual(estado, 200)
        self.assertFalse(r["convergio"], r)

    def test_5_raiz_escalada_no_depende_de_la_semilla(self):
        for x in (math.sqrt(2), 1.5):
            estado, r = self.resolver("newton-raphson", funcion="1e20*(x^2-2)", x0=x)
            self.assertEqual(estado, 200)
            self.assertTrue(r["convergio"], r)
            self.assertAlmostEqual(r["raiz"], math.sqrt(2), delta=1e-6)

    def test_6_division_constante_preserva_restricciones(self):
        for argumento in ("x/2", "0.5*x"):
            estado, r = self.resolver("biseccion", funcion=f"(x-1)*(tan({argumento})/tan({argumento}))",
                                      a=.5, b=7)
            self.assertEqual(estado, 400, r)

    def test_7_ln_cerca_del_borde_sigue_continua(self):
        estado, r = self.resolver("biseccion", funcion="ln(x)+sin(x)-1.2", a=1e-16, b=2)
        self.assertEqual(estado, 200, r)
        self.assertTrue(r["convergio"])
        self.assertAlmostEqual(r["raiz"], 1.2754495800797368, delta=1e-6)
