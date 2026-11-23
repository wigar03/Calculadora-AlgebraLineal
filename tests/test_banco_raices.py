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
