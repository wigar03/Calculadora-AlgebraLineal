"""Banco completo por la API de la página, con aritmética independiente exacta."""
import json
import ast
import operator
import re
import unittest
from fractions import Fraction as F
from pathlib import Path
from urllib.request import Request, urlopen

from src.ui.web_server import servidor_local
from validacion.banco_lineales import SISTEMAS
from validacion.banco_matrices import MATRICES

REFERENCIAS = json.loads((Path(__file__).parent / "validacion/referencias.json").read_text("utf-8"))


def fracciones(matriz):
    return [[F(str(x)) for x in fila] for fila in matriz]


def producto(a, b):
    return [[sum((x * y for x, y in zip(fila, col)), F(0))
             for col in zip(*b)] for fila in a]


def evaluar_parametrica(texto, parametros):
    """Evaluador independiente restringido; no ejecuta texto del servidor."""
    arbol = ast.parse(re.sub(r"(?<=\d)(?=[a-z])", "*", texto), mode="eval")
    operaciones = {ast.Add: operator.add, ast.Sub: operator.sub,
                   ast.Mult: operator.mul, ast.Div: operator.truediv}

    def valor(nodo):
        if isinstance(nodo, ast.Constant) and type(nodo.value) is int:
            return F(nodo.value)
        if isinstance(nodo, ast.Name):
            return parametros[nodo.id]
        if isinstance(nodo, ast.UnaryOp) and isinstance(nodo.op, (ast.USub, ast.UAdd)):
            return -valor(nodo.operand) if isinstance(nodo.op, ast.USub) else valor(nodo.operand)
        if isinstance(nodo, ast.BinOp) and type(nodo.op) in operaciones:
            return operaciones[type(nodo.op)](valor(nodo.left), valor(nodo.right))
        raise AssertionError("Expresión paramétrica inesperada: " + texto)
    return valor(arbol.body)


class TestBancoLineal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servidor = servidor_local()
        cls.url = cls.servidor.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.servidor.__exit__(None, None, None)

    def post(self, ruta, datos):
        req = Request(self.url + "/api/" + ruta, json.dumps(datos).encode(),
                      {"Content-Type": "application/json"})
        with urlopen(req, timeout=10) as respuesta:
            return json.load(respuesta)

    def comprobar_sistema(self, clave):
        datos, ref = SISTEMAS[clave], REFERENCIAS["lineales"][clave]
        for jordan in (True, False):
            with self.subTest(ejercicio=clave, gauss_jordan=jordan):
                res = self.post("ecuaciones/resolver", dict(datos, usar_gauss_jordan=jordan))
                self.assertEqual(res["tipo_sistema"], {"unica": "SCD", "infinitas": "SCI"}[ref["tipo"]])
                self.assertEqual(res["rango_A"], ref["rango_A"])
                self.assertEqual(res["rango_aumentada"], ref["rango_aumentada"])
                self.assertGreater(len(res["pasos"]), 1)
                self.assertTrue(res["sustitucion"])
                if ref["tipo"] == "unica":
                    x = [F(v) for v in res["vector_solucion"]]
                    self.assertEqual(x, [F(v) for v in ref["solucion"]])
                    self.assertEqual(producto(fracciones(datos["A"]), [[v] for v in x]),
                                     [[F(v)] for v in datos["b"]])
                    self.assertEqual(len(res["verificacion"]), len(datos["b"]))
                    self.assertTrue(all("Satisface" in v for v in res["verificacion"]))
                else:
                    self.assertEqual(res["parametros"], ["t"])
                    self.assertIn("x_4 = t", res["descripcion_sistema"])
                    for t in (F(-3), F(0), F(2, 3)):
                        x = [evaluar_parametrica(v, {"t": t}) for v in res["vector_solucion"]]
                        self.assertEqual(producto(fracciones(datos["A"]), [[v] for v in x]),
                                         [[F(v)] for v in datos["b"]])
                        self.assertEqual(x, [F(p) + t * F(v) for p, v in
                                             zip(res["solucion_particular"], res["base_nucleo"][0])])
                    self.assertEqual(len(res["verificacion"]), len(datos["b"]))
                    self.assertTrue(all("Satisface" in v and "para todo" in v for v in res["verificacion"]))

    def comprobar_matriz(self, clave):
        a, ref = MATRICES[clave], REFERENCIAS["matrices"][clave]
        for metodo in ("lu", "cofactores"):
            with self.subTest(ejercicio=clave, determinante=metodo):
                res = self.post("matrices/determinante", {"A": a, "metodo": metodo})
                self.assertEqual(F(res["determinante"]), F(ref["det"]))
                self.assertEqual(res["es_invertible"], ref["invertible"])
                self.assertTrue(res["pasos"])
        for metodo in ("gauss_jordan", "gauss"):
            with self.subTest(ejercicio=clave, inversa=metodo):
                res = self.post("matrices/inversa", {"A": a, "metodo": metodo})
                inv = fracciones(res["matriz_inversa"])
                self.assertEqual(inv, fracciones(ref["inversa"]))
                identidad = [[F(i == j) for j in range(len(a))] for i in range(len(a))]
                self.assertEqual(producto(fracciones(a), inv), identidad)
                self.assertEqual(producto(inv, fracciones(a)), identidad)
                self.assertTrue(res["residuo_cero"])
                for campo in ("verificacion_A_por_Ainv", "verificacion_Ainv_por_A"):
                    self.assertEqual(len(res[campo]), len(a) ** 2)
                    self.assertTrue(all("Correcto" in v for v in res[campo]))


def caso(clave, metodo):
    def prueba(self):
        getattr(self, metodo)(clave)
    return prueba


for clave in SISTEMAS:
    setattr(TestBancoLineal, "test_" + clave.replace("-", "_"), caso(clave, "comprobar_sistema"))
for clave in MATRICES:
    setattr(TestBancoLineal, "test_" + clave.replace("-", "_"), caso(clave, "comprobar_matriz"))
