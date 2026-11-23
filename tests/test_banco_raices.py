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
        a, b = (datos["a"], datos["b"]) if metodo == "biseccion" else INICIALES[ejercicio][:2]
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


def _prueba_banco(ejercicio, metodo):
    def prueba(self):
        datos, res = self.resolver(ejercicio, metodo)
        self.comprobar_resultado(ejercicio, metodo, datos, res)
    return prueba


for _ejercicio in ECUACIONES:
    for _metodo in RUTAS:
        setattr(TestBancoRaices, "test_" + _ejercicio.replace("-", "_") + "_" + _metodo,
                _prueba_banco(_ejercicio, _metodo))
