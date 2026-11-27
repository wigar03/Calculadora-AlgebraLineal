"""Orden observado: referencias teóricas y banco final 30–39, sin cambiar las raíces."""
import json
import math
import unittest

from src.biseccion.metodo import resolver_biseccion
from src.newton_raphson.metodo import resolver_newton
from src.regla_falsa.metodo import resolver_regla_falsa
from src.secante.metodo import resolver_secante
from src.ui.web_server import servidor_local
from tests.test_banco_raices import INICIALES, REFERENCIAS, RUTAS
from tests.test_golden_api import consultar
from tests.validacion.banco_raices import ECUACIONES


class TestConvergenciaObservada(unittest.TestCase):
    def comprobar(self, res, clase, orden, delta=.15):
        obs = res["convergencia_observada"]
        self.assertEqual(obs["clasificacion"], clase, obs)
        self.assertAlmostEqual(obs["orden"], orden, delta=delta)
        self.assertGreater(obs["constante_asintotica"], 0)
        self.assertTrue(math.isfinite(obs["constante_asintotica"]))
        self.assertIn("estimación", obs["texto"])
        json.dumps(obs, allow_nan=False)
        return obs

    def test_biseccion_lineal(self):
        obs = self.comprobar(resolver_biseccion("x^3-4*x-9", 2, 3), "lineal", 1)
        self.assertAlmostEqual(obs["razon"], .5)
        self.assertAlmostEqual(obs["constante_asintotica"], .5)

    def test_newton_raices_simples_y_doble(self):
        for f, x0 in (("x^3-4*x-9", 3), ("x^3+x-1", 1)):
            with self.subTest(f=f):
                self.comprobar(resolver_newton(f, x0, tolerancia=1e-12), "cuadrática", 2)
        obs = self.comprobar(resolver_newton("(x-1)^2", 2, tolerancia=1e-10), "lineal", 1)
        self.assertAlmostEqual(obs["razon"], .5)
        self.assertAlmostEqual(obs["constante_asintotica"], .5)

    def test_secante_y_regla_falsa(self):
        for f, a, b in (("x^3-4*x-9", 2, 3), ("x^3+x-1", 0, 1)):
            with self.subTest(f=f):
                self.comprobar(resolver_secante(f, a, b, tolerancia=1e-12),
                               "superlineal", (1 + math.sqrt(5))/2)
                self.comprobar(resolver_regla_falsa(f, a, b, tolerancia=1e-8), "lineal", 1)

    def test_pocas_iteraciones_no_inventan_orden(self):
        resultados = [resolver_biseccion("x-1", 1, 2), resolver_newton("x-1", 2),
                      resolver_regla_falsa("x-1", 0, 2), resolver_secante("x-1", 0, 2)]
        for res in resultados:
            obs = res["convergencia_observada"]
            self.assertEqual(obs["clasificacion"], "no concluyente")
            self.assertIsNone(obs["orden"])
            self.assertIsNone(obs["constante_asintotica"])

    def test_banco_30_a_39_por_api(self):
        with servidor_local() as url:
            for i in range(1, 11):
                ejercicio = f"III-{i}"
                entrada = ECUACIONES[ejercicio]
                a, b, x0 = INICIALES[ejercicio]
                for metodo, ruta in RUTAS.items():
                    with self.subTest(ejercicio=ejercicio, metodo=metodo):
                        datos = dict(funcion=entrada["funcion"], condicion=entrada["condicion"],
                                     tolerancia=1e-6, max_iteraciones=200)
                        if metodo == "biseccion":
                            datos.update(a=a, b=b, criterio="intervalo")
                        elif metodo == "regla_falsa":
                            datos.update(xl=a, xu=b)
                        else:
                            datos.update(x0=x0 if metodo == "newton" else a, x1=b)
                        status, res = consultar(url, f"/api/{ruta}/resolver", datos)
                        self.assertEqual(status, 200, res)
                        referencia = next(float(r) for r in REFERENCIAS[ejercicio]["raices_en_[-10,10]"]
                                          if a <= float(r) <= b)
                        self.assertLessEqual(abs(res["raiz"]-referencia), 1e-6)
                        obs = res["convergencia_observada"]
                        self.assertIn(obs["clasificacion"], ("lineal", "superlineal", "cuadrática", "no concluyente"))
                        self.assertTrue(any(p["titulo"] == "Convergencia observada"
                                            for p in res["procedimiento"]["pasos"]))
