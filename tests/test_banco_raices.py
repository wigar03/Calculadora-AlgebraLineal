"""Banco III/IV por HTTP real: semillas de estudiante y referencias independientes."""

import json
import math
import unittest
from decimal import Decimal
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src.ui.web_server import servidor_local
from tests.validacion.banco_raices import ECUACIONES, INCOMPLETOS

REFERENCIAS = json.loads((Path(__file__).parent / "validacion/referencias.json")
                         .read_text(encoding="utf-8"))["raices"]
# [a,b] se elige con números sencillos y cambio de signo, sin leer la referencia.
# Newton parte de una semilla manual; secante usa los dos extremos indicados.
INICIALES = {
    "III-1": (2, 3, 3), "III-2": (0, 1, 1), "III-3": (0, 1, .5),
    "III-4": (1, 2, 2), "III-5": (1, 2, 2), "III-6": (0, 1, 1),
    "III-7": (0, 1, 1), "III-8": (0, 1, 1), "III-9": (0, 1, .5),
    "III-10": (2, 3, 2), "III-11": (1, 2, 1), "III-12": (1, 2, 1),
    "III-13": (2, 3, 2), "III-14": (2, 3, 3), "III-15": (2, 3, 2),
    "IV-1": (2, 3, 2), "IV-3": (1, 1.56, 1.5), "IV-4": (0, 1, 1),
}
# Sustitución independiente del analizador y de los motores bajo prueba.
FUNCIONES = {
    "III-1": lambda x: x**3 - 4*x - 9,
    "III-2": lambda x: math.exp(x) - 3*x*x,
    "III-3": lambda x: math.cos(x) - x*math.exp(x),
    "III-4": lambda x: x*math.log(x) - 1,
    "III-5": lambda x: x**4 - 3*x*x - 3,
    "III-6": lambda x: math.log(x+2) + x*x - 2,
    "III-7": lambda x: math.exp(-x) - x*x + .5,
    "III-8": lambda x: x**3 + x - 1,
    "III-9": lambda x: x*math.exp(-x) - .2,
    "III-10": lambda x: x*x - 5*math.sin(x),
    "III-11": lambda x: math.log(x) + math.sin(x) - 1.2,
    "III-12": lambda x: math.exp(-x) + math.cos(x) - .5,
    "III-13": lambda x: x*x - 3*math.sin(x) - math.log(x+2),
    "III-14": lambda x: math.exp(x/2) + math.sin(2*x) - 3,
    "III-15": lambda x: math.log(x+3) + math.cos(x) - x/2,
    "IV-1": lambda x: math.sin(x)/math.log(x) - 1,
    "IV-3": lambda x: math.exp(1/x) + 2*x/math.tan(x) - 2,
    "IV-4": lambda x: math.log(x+1)/(x*x-4) + .1,
}
RUTAS = {"biseccion": "biseccion", "regla_falsa": "regla-falsa",
         "secante": "secante", "newton": "newton-raphson"}


class TestBancoRaices(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = cls.enterClassContext(servidor_local())

    def enviar(self, metodo, datos, accion="resolver"):
        req = Request(f"{self.url}/api/{RUTAS[metodo]}/{accion}",
                      json.dumps(datos).encode(), {"Content-Type": "application/json"})
        try:
            respuesta = urlopen(req, timeout=10)
        except HTTPError as exc:
            respuesta = exc
        with respuesta:
            cuerpo = json.loads(respuesta.read(), parse_constant=self.fail)
        return respuesta.status, cuerpo

    def resolver(self, ejercicio, metodo, iniciales=None):
        entrada = ECUACIONES[ejercicio]
        a, b, x0 = iniciales or INICIALES[ejercicio]
        datos = dict(funcion=entrada["funcion"], tolerancia=1e-6, max_iteraciones=200,
                     condicion=entrada["condicion"])
        if metodo == "biseccion":
            datos.update(a=a, b=b, criterio="intervalo")
        elif metodo == "regla_falsa":
            datos.update(xl=a, xu=b)
        elif metodo == "secante":
            datos.update(x0=a, x1=b, criterio="absoluto")
        else:
            datos.update(x0=x0, criterio="absoluto")
        estado, res = self.enviar(metodo, datos)
        self.assertEqual(estado, 200, res)
        return datos, res

    def comprobar_resultado(self, ejercicio, metodo, datos, res):
        if metodo == "biseccion":
            a, b = datos["a"], datos["b"]
        elif metodo == "regla_falsa":
            a, b = datos["xl"], datos["xu"]
        elif metodo == "secante":
            a, b = datos["x0"], datos["x1"]
        else:
            a, b = INICIALES[ejercicio][:2]
        candidatas = [r for r in REFERENCIAS[ejercicio]["raices_en_[-10,10]"] if a <= float(r) <= b]
        self.assertEqual(len(candidatas), 1)
        referencia = candidatas[0]
        diferencia = abs(Decimal(str(res["raiz"])) - Decimal(referencia))
        self.assertTrue(res["convergio"], res)
        self.assertLessEqual(diferencia, Decimal("1e-6"))
        if ECUACIONES[ejercicio]["condicion"] != "real":
            self.assertGreater(res["raiz"], 0)
        f = FUNCIONES[ejercicio]
        fx = f(res["raiz"])
        self.assertAlmostEqual(res["f_raiz"], fx, delta=1e-12*max(1, abs(fx)))
        self.assertEqual(res["residuo"], abs(res["f_raiz"]))
        v = res["verificacion"]
        self.assertEqual(v["x"], res["raiz"])
        self.assertEqual(v["residuo"], res["residuo"])
        self.assertEqual(v["cumple_residuo"], res["residuo"] <= datos["tolerancia"])
        if metodo == "biseccion":
            self.assertLessEqual(float(diferencia), res["cota_error"] + 2e-15)
        else:
            self.assertLessEqual(abs(fx), 1e-6)
        self.assertTrue(res["pasos"])
        self.comprobar_tabla(metodo, f, res["pasos"])

    def comprobar_tabla(self, metodo, f, pasos):
        def evaluacion(x, y):
            self.assertAlmostEqual(f(x), y, delta=1e-12*max(1, abs(y)))
        for i, p in enumerate(pasos):
            if metodo == "newton":
                evaluacion(p["x"], p["fx"])
                h = 1e-6
                df = (f(p["x"]+h) - f(p["x"]-h))/(2*h)
                self.assertAlmostEqual(p["dfx"], df, delta=1e-5*max(1, abs(df)))
                if i:
                    q = pasos[i-1]
                    self.assertEqual(p["x"], q["x"] - q["fx"]/q["dfx"])
                    self.assertEqual(p["error_absoluto"], abs(p["x"]-q["x"]))
                continue
            if metodo == "regla_falsa":
                a, b, c, fa, fb, fc = (p[k] for k in ("xl", "xu", "xr", "f_xl", "f_xu", "f_xr"))
                esperado = b - fb*(a-b)/(fa-fb)
            else:
                a, b, c, fa, fb, fc = (p[k] for k in ("a", "b", "c", "fa", "fb", "fc"))
                esperado = a + (b-a)/2 if metodo == "biseccion" else b - fb/(fb-fa)*(b-a)
            for x, y in ((a, fa), (b, fb), (c, fc)):
                evaluacion(x, y)
            self.assertAlmostEqual(c, esperado, delta=2e-14*max(1, abs(c)))
            if metodo in ("biseccion", "regla_falsa"):
                self.assertNotEqual(fa < 0, fb < 0)
                self.assertLessEqual(a, c)
                self.assertLessEqual(c, b)
            if i and metodo == "biseccion":
                self.assertAlmostEqual(p["ancho"], pasos[i-1]["ancho"]/2,
                                       delta=4*math.ulp(max(1, abs(b))))
            if i and metodo == "secante":
                self.assertEqual((a, b), (pasos[i-1]["b"], pasos[i-1]["c"]))

    def test_otras_raices_positivas_identificadas(self):
        for ejercicio, semillas in (("III-2", (3, 4, 4)), ("III-9", (2, 3, 3)),
                                    ("IV-3", (4, 4.7, 4.5))):
            for metodo in RUTAS:
                with self.subTest(ejercicio=ejercicio, metodo=metodo):
                    datos, res = self.resolver(ejercicio, metodo, semillas)
                    referencia = next(float(r) for r in REFERENCIAS[ejercicio]["raices_en_[-10,10]"]
                                      if semillas[0] < float(r) < semillas[1])
                    self.assertTrue(res["convergio"], res)
                    self.assertAlmostEqual(res["raiz"], referencia, delta=1e-6)
                    if metodo != "biseccion":
                        self.assertLessEqual(abs(FUNCIONES[ejercicio](res["raiz"])), 1e-6)
                    self.comprobar_tabla(metodo, FUNCIONES[ejercicio], res["pasos"])

    def test_intervalos_sin_signos_y_con_polos(self):
        casos = [("x^2+1", 0, 1), (ECUACIONES["IV-1"]["funcion"], .5, 2.5),
                 (ECUACIONES["IV-3"]["funcion"], 1, 2),
                 (ECUACIONES["IV-3"]["funcion"], 3, 4),
                 (ECUACIONES["IV-3"]["funcion"], -1, 1),
                 (ECUACIONES["IV-4"]["funcion"], 1.5, 2.5),
                 ("(x-.1234567)/(x-.1234567)*(x-.7)", 0, 1)]
        for funcion, a, b in casos:
            for metodo in ("biseccion", "regla_falsa"):
                with self.subTest(funcion=funcion, metodo=metodo):
                    datos = dict(funcion=funcion, a=a, b=b, xl=a, xu=b)
                    estado, res = self.enviar(metodo, datos)
                    self.assertEqual(estado, 400, res)
                    self.assertIn("error", res)

    def test_dominio_en_puntos_iniciales(self):
        for ejercicio, x in (("III-4", 0), ("III-11", 0), ("IV-1", 1),
                             ("IV-4", -1), ("IV-3", 0), ("IV-3", math.pi),
                             ("IV-3", math.pi/2)):
            for metodo in RUTAS:
                with self.subTest(ejercicio=ejercicio, x=x, metodo=metodo):
                    datos = dict(funcion=ECUACIONES[ejercicio]["funcion"],
                                 a=x, b=x+1, xl=x, xu=x+1, x0=x, x1=x+1)
                    estado, res = self.enviar(metodo, datos)
                    self.assertEqual(estado, 400, res)

    def test_iii_10_rechaza_cero_con_condicion_del_enunciado(self):
        for metodo in RUTAS:
            with self.subTest(metodo=metodo):
                estado, res = self.enviar(metodo, dict(funcion=ECUACIONES["III-10"]["funcion"],
                    condicion="positiva_no_nula", a=0, b=3, xl=0, xu=3, x0=0, x1=3))
                self.assertEqual(estado, 200)
                self.assertFalse(res["convergio"])
                self.assertEqual(res["motivo"], "raiz_no_admisible")

    def test_derivada_nula_ciclo_y_salida_de_dominio(self):
        casos = [("x^2+1", 0, "derivada_nula"), ("sqrt(x)-1", 0, "derivada_no_definida"),
                 ("x^3-2*x+2", 0, "ciclo"), (ECUACIONES["III-4"]["funcion"], .01, "fuera_de_dominio")]
        for funcion, x0, motivo in casos:
            with self.subTest(funcion=funcion):
                estado, res = self.enviar("newton", dict(funcion=funcion, x0=x0))
                self.assertEqual(estado, 200)
                self.assertFalse(res["convergio"])
                self.assertEqual(res["motivo"], motivo)
        for funcion, x0, x1, motivo in (("x^2+1", -1, 1, "denominador_nulo"),
                                       ("ln(x)+10", 1, 2, "fuera_de_dominio")):
            estado, res = self.enviar("secante", dict(funcion=funcion, x0=x0, x1=x1))
            self.assertEqual(estado, 200)
            self.assertFalse(res["convergio"])
            self.assertEqual(res["motivo"], motivo)

    def test_paso_diminuto_sin_raiz_no_declara_convergencia(self):
        for metodo, datos in (("newton", dict(funcion="exp(1e8*x)+1", x0=0)),
                               ("secante", dict(funcion="atan(1e12*x)+2", x0=0, x1=1e-12)),
                               ("regla_falsa", dict(funcion="exp(30*(x-1))-2", xl=1, xu=2))):
            with self.subTest(metodo=metodo):
                estado, res = self.enviar(metodo, dict(datos, tolerancia=1e-6, max_iteraciones=100))
                self.assertEqual(estado, 200)
                self.assertFalse(res["convergio"], res)
                self.assertGreater(res["residuo"], .4)

    def test_regla_falsa_no_acepta_error_cero_por_redondeo(self):
        estado, res = self.enviar("regla_falsa", dict(funcion="x^2-2", xl=1, xu=2,
                                 tolerancia=1e-100, max_iteraciones=200))
        self.assertEqual(estado, 200)
        self.assertFalse(res["convergio"])
        self.assertIn(res["motivo"], ("precision_agotada", "sin_progreso"))

    def test_residuo_y_cota_son_magnitudes_distintas(self):
        _, res = self.resolver("III-1", "biseccion")
        self.assertTrue(res["convergio"])
        self.assertLessEqual(res["cota_error"], 5e-7)
        self.assertGreater(res["residuo"], 1e-6)
        self.assertFalse(res["verificacion"]["cumple_residuo"])

    def test_ln_cerca_del_limite_del_dominio(self):
        for ejercicio in ("III-4", "III-11"):
            for metodo in ("biseccion", "regla_falsa"):
                with self.subTest(ejercicio=ejercicio, metodo=metodo):
                    datos, res = self.resolver(ejercicio, metodo, (1e-6, 2, 2))
                    self.comprobar_resultado(ejercicio, metodo, datos, res)

    def test_incompletos_solo_evaluan_el_dominio_del_radical(self):
        casos = {"IV-2": ("sqrt(2*x^3/(x-3))", -1, 4),
                 "IV-5": (INCOMPLETOS["IV-5"]["expresion"], -5, 2)}
        for ejercicio, (funcion, a, b) in casos.items():
            with self.subTest(ejercicio=ejercicio):
                estado, res = self.enviar("regla_falsa", dict(funcion=funcion, a=a, b=b,
                                                           cantidad=11), "graficar")
                self.assertEqual(estado, 200)
                self.assertNotIn("raiz", res)
                self.assertTrue(any(p["y"] is None for p in res["grafica"]))
                self.assertTrue(any(p["y"] is not None for p in res["grafica"]))


def _prueba_banco(ejercicio, metodo):
    def prueba(self):
        datos, res = self.resolver(ejercicio, metodo)
        self.comprobar_resultado(ejercicio, metodo, datos, res)
    return prueba


for _ejercicio in ECUACIONES:
    for _metodo in RUTAS:
        setattr(TestBancoRaices, "test_" + _ejercicio.replace("-", "_") + "_" + _metodo,
                _prueba_banco(_ejercicio, _metodo))
