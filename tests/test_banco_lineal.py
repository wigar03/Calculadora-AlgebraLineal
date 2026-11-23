"""Banco completo por la API de la página, con aritmética independiente exacta."""
import json
import ast
import operator
import re
import unittest
from itertools import permutations
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


def determinante_independiente(a):
    total = F(0)
    for p in permutations(range(len(a))):
        signo = (-1) ** sum(p[i] > p[j] for i in range(len(p)) for j in range(i + 1, len(p)))
        termino = F(signo)
        for i, j in enumerate(p):
            termino *= a[i][j]
        total += termino
    return total


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

    def comprobar_pasos(self, pasos, inicial):
        anterior = fracciones(inicial)
        self.assertEqual(fracciones(pasos[0]["matrix"]), anterior)
        for paso in pasos[1:]:
            actual = [fila[:] for fila in anterior]
            op = paso["operation_code"]
            filas = [int(v) - 1 for v in re.findall(r"F_(\d+)", op)]
            if "<->" in op:
                i, j = filas
                actual[i], actual[j] = actual[j], actual[i]
            else:
                factor = F(re.search(r"\(([^)]+)\)", op).group(1))
                if len(filas) == 2:
                    actual[filas[0]] = [factor * x for x in actual[filas[0]]]
                else:
                    i, _, j = filas
                    factor *= -1 if " - " in op else 1
                    actual[i] = [x + factor * y for x, y in zip(actual[i], anterior[j])]
            self.assertEqual(fracciones(paso["matrix"]), actual, op)
            anterior = actual

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
                self.comprobar_pasos(res["pasos"], [fila + [b] for fila, b in zip(datos["A"], datos["b"])])
                if ref["tipo"] == "unica":
                    x = [F(v) for v in res["vector_solucion"]]
                    self.assertEqual(x, [F(v) for v in ref["solucion"]])
                    self.assertEqual(producto(fracciones(datos["A"]), [[v] for v in x]),
                                     [[F(v)] for v in datos["b"]])
                    self.assertEqual(len(res["verificacion"]), len(datos["b"]))
                    self.assertTrue(all("Satisface" in v for v in res["verificacion"]))
                else:
                    self.assertEqual(res["parametros"], ["t"])
                    self.assertIn("x_{4} = t", res["descripcion_sistema"])
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
                if metodo == "lu":
                    self.assertEqual(fracciones(res["pasos"][0]["matriz_estado"]), fracciones(a))
                    for paso in res["pasos"]:
                        self.assertEqual(abs(determinante_independiente(fracciones(paso["matriz_estado"]))),
                                         abs(F(ref["det"])))
        for metodo in ("gauss_jordan", "gauss"):
            with self.subTest(ejercicio=clave, inversa=metodo):
                res = self.post("matrices/inversa", {"A": a, "metodo": metodo})
                inv = fracciones(res["matriz_inversa"])
                self.assertEqual(inv, fracciones(ref["inversa"]))
                identidad = [[F(i == j) for j in range(len(a))] for i in range(len(a))]
                self.assertEqual(producto(fracciones(a), inv), identidad)
                self.assertEqual(producto(inv, fracciones(a)), identidad)
                inicial = [fila + identidad[i] for i, fila in enumerate(a)]
                self.comprobar_pasos(res["pasos"], inicial)
                self.assertEqual(fracciones(res["matriz_aumentada_final"]),
                                 [fila + inv[i] for i, fila in enumerate(identidad)])
                self.assertTrue(res["residuo_cero"])
                for campo in ("verificacion_A_por_Ainv", "verificacion_Ainv_por_A"):
                    self.assertEqual(len(res[campo]), len(a) ** 2)
                    self.assertTrue(all("Correcto" in v for v in res[campo]))

    def test_singular_explicada(self):
        a = [[2, 3, 4]] * 3
        for metodo in ("gauss", "gauss_jordan"):
            res = self.post("matrices/inversa", {"A": a, "metodo": metodo})
            self.assertFalse(res["es_invertible"])
            self.assertIsNone(res["matriz_inversa"])
            self.assertFalse(res["residuo_cero"])
            self.assertIn("pivote", res["mensaje_diagnostico"])
            self.assertIn("rango", res["mensaje_diagnostico"])
            self.assertIn("no existe", res["mensaje_diagnostico"])
            self.comprobar_pasos(res["pasos"], [fila + [int(i == j) for j in range(3)]
                                                for i, fila in enumerate(a)])
        for metodo in ("lu", "cofactores"):
            res = self.post("matrices/determinante", {"A": a, "metodo": metodo})
            self.assertEqual(F(res["determinante"]), 0)
            self.assertFalse(res["es_invertible"])

    def test_I_12_con_decimales_y_fracciones(self):
        datos = SISTEMAS["I-12"]
        equivalencias = {"1/2": "0.5", "-3/4": "-0.75", "3/2": "1.5",
                         "-5/2": "-2.5", "3/4": "0.75", "5/4": "1.25"}
        a = [[equivalencias.get(v, v) for v in fila] for fila in datos["A"]]
        for jordan in (True, False):
            res = self.post("ecuaciones/resolver", dict(A=a, b=datos["b"], usar_gauss_jordan=jordan))
            self.assertEqual(res["vector_solucion"], REFERENCIAS["lineales"]["I-12"]["solucion"])
            self.assertEqual(producto(fracciones(a), [[F(v)] for v in res["vector_solucion"]]),
                             [[F(v)] for v in datos["b"]])

    def test_sci_varios_parametros_y_columnas_sin_pivote(self):
        for a, b in (([[1, 2, 3], [0, 0, 0]], [5, 0]), ([[0, 2, 3], [0, 0, 4]], [7, 8])):
            for jordan in (True, False):
                res = self.post("ecuaciones/resolver", dict(A=a, b=b, usar_gauss_jordan=jordan))
                self.assertEqual(res["tipo_sistema"], "SCI")
                valores = {p: F(i + 2, 3) for i, p in enumerate(res["parametros"])}
                x = [evaluar_parametrica(v, valores) for v in res["vector_solucion"]]
                self.assertEqual(producto(fracciones(a), [[v] for v in x]), [[F(v)] for v in b])
                self.assertEqual(len(res["base_nucleo"]), len(a[0]) - res["rango_A"])

    def test_incompatible_rango_aumentado_no_cuenta_filas_dependientes(self):
        res = self.post("ecuaciones/resolver", dict(A=[[0, 0], [0, 0]], b=[1, 2]))
        self.assertEqual((res["tipo_sistema"], res["rango_A"], res["rango_aumentada"]), ("SI", 0, 1))

    def test_diez_parametros_con_subindices_agrupados(self):
        for jordan in (True, False):
            res = self.post("ecuaciones/resolver", dict(A=[[0] * 10], b=[0], usar_gauss_jordan=jordan))
            self.assertEqual(res["parametros"][-1], "t_10")
            self.assertEqual(res["vector_solucion"][-1], "t_10")
            self.assertIn("x_{10} = t_{10}", res["descripcion_sistema"])
            self.assertIn("(0)t_{10}", res["verificacion"][0])
            identidad = [[F(i == j) for j in range(10)] for i in range(10)]
            self.assertEqual(fracciones(res["base_nucleo"]), identidad)
            self.assertEqual(res["solucion_particular"], ["0"] * 10)
            textos = [res["descripcion_sistema"], *res["verificacion"]]
            self.assertNotRegex(" ".join(textos), r"_\d{2}")

    def test_sustitucion_con_variables_y_parametros_indexados(self):
        from src.solver.gauss_solver import formatear_subindices_latex
        self.assertEqual(formatear_subindices_latex("x_11 = t_10 + t_11"), "x_{11} = t_{10} + t_{11}")
        a = [[int(i == j) for j in range(10)] for i in range(10)]
        res = self.post("ecuaciones/resolver", dict(A=a, b=[0] * 10, usar_gauss_jordan=False))
        self.assertTrue(any("x_{10}" in paso for paso in res["sustitucion"]))
        self.assertNotRegex(" ".join(res["sustitucion"]), r"_\d{2}")

    def test_coeficientes_parametricos_estructurados_son_racionales_canonicos(self):
        for a, b, constante, coeficiente in (([[2, -2]], ["0.5"], "1/4", "1"),
                                            ([[5, -5]], [2], "2/5", "1"),
                                            ([[2, -1]], [0], "0", "1/2")):
            for jordan in (True, False):
                res = self.post("ecuaciones/resolver", dict(A=a, b=b, usar_gauss_jordan=jordan))
                self.assertEqual(res["solucion_particular"], [constante, "0"])
                self.assertEqual(res["base_nucleo"], [[coeficiente, "1"]])
                self.assertEqual(res["parametros"], ["t"])
                for valor in res["solucion_particular"] + res["base_nucleo"][0]:
                    self.assertEqual(valor, str(F(valor)))


def caso(clave, metodo):
    def prueba(self):
        getattr(self, metodo)(clave)
    return prueba


for clave in SISTEMAS:
    setattr(TestBancoLineal, "test_" + clave.replace("-", "_"), caso(clave, "comprobar_sistema"))
for clave in MATRICES:
    setattr(TestBancoLineal, "test_" + clave.replace("-", "_"), caso(clave, "comprobar_matriz"))
