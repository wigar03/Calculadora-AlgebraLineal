"""Orden observado: referencias teóricas y banco final 30–39, sin cambiar las raíces."""
import json
import math
import unittest

from src.secante.convergencia import estimar_convergencia
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
                        clases = {"biseccion": ("lineal",), "regla_falsa": ("lineal",),
                                  "newton": ("cuadrática", "no concluyente"),
                                  "secante": ("superlineal", "no concluyente")}
                        self.assertIn(obs["clasificacion"], clases[metodo])
                        if obs["orden"] is not None:
                            esperado = {"biseccion": 1, "regla_falsa": 1,
                                        "newton": 2, "secante": (1+math.sqrt(5))/2}[metodo]
                            self.assertAlmostEqual(obs["orden"], esperado, delta=.15)
                        json.dumps(obs, allow_nan=False)
                        self.assertTrue(any(p["titulo"] == "Convergencia observada"
                                            for p in res["procedimiento"]["pasos"]))


class TestEstimadorConvergencia(unittest.TestCase):
    def test_sucesiones_con_orden_y_constante_conocidos(self):
        for p, c, x0 in ((1, .5, 1), ((1+math.sqrt(5))/2, .7, .1), (2, 1, .5)):
            xs = [x0]
            for _ in range(8):
                xs.append(c*xs[-1]**p)
            obs = estimar_convergencia(xs)
            with self.subTest(p=p):
                self.assertAlmostEqual(obs["orden"], p, delta=.06)
                self.assertAlmostEqual(obs["constante_asintotica"], c, delta=.15)

    def test_no_finitos_y_sin_contraccion(self):
        casos = [[], [1, 1, 1, 1, 1], [1, .5, .25], [1, 2, 4, 8, 16],
                 [1, .5, float("nan"), .125], [1, .5, .25, float("inf")],
                 [1e308, -1e308, 1, 2, 3]]
        for xs in casos:
            with self.subTest(xs=xs):
                obs = estimar_convergencia(xs)
                self.assertEqual(obs["clasificacion"], "no concluyente")
                self.assertIsNone(obs["orden"])
                json.dumps(obs, allow_nan=False)

    def test_ruido_solo_no_basta_y_no_oculta_historial_util(self):
        ruido = [1+i*math.ulp(1.) for i in (9, 5, 3, 2, 1, 0)]
        self.assertEqual(estimar_convergencia(ruido)["clasificacion"], "no concluyente")
        xs = [1+2.**(-i) for i in range(55)]
        obs = estimar_convergencia(xs)
        self.assertEqual(obs["clasificacion"], "lineal")
        self.assertAlmostEqual(obs["orden"], 1)
        self.assertIn("redondeo", obs["explicacion"])

    def test_ordenes_oscilantes_y_contraccion_debil_no_se_clasifican(self):
        for cambios in ((.5, .25, .1, .05, .01), (1, .9999, .9998, .9997)):
            xs = [0]
            for e in cambios:
                xs.append(xs[-1]+e)
            self.assertEqual(estimar_convergencia(xs)["clasificacion"], "no concluyente")

    def test_constante_de_newton_contra_derivadas_independientes(self):
        for f, ejercicio in (("x^3-4*x-9", "III-1"), ("x^3+x-1", "III-8")):
            r = float(REFERENCIAS[ejercicio]["raices_en_[-10,10]"][-1])
            df = 3*r*r + (-4 if ejercicio == "III-1" else 1)
            constante = abs(3*r/df)  # |f''(r)/(2 f'(r))|.
            res = resolver_newton(f, 3 if ejercicio == "III-1" else 1, tolerancia=1e-12)
            self.assertAlmostEqual(res["convergencia_observada"]["constante_asintotica"],
                                   constante, delta=.08)
