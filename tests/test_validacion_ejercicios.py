"""Aceptación independiente del banco: cada ejercicio por la API HTTP de la página contra `referencias.json`.

Las comprobaciones no usan el código bajo prueba: sustitución con `Fraction` y f(x) con `math` propio.
"""
import json
import os
import unittest
from fractions import Fraction
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src.ui.web_server import servidor_local
from tests.validacion.banco_lineales import SISTEMAS
from tests.validacion.banco_matrices import MATRICES
from tests.validacion.banco_raices import ECUACIONES
from tests.validacion.funciones_independientes import ENTRADAS_DOCUMENTO, F, IMPLICITOS, INICIALES

RUTA = os.path.join(os.path.dirname(__file__), "validacion", "referencias.json")
with open(RUTA, encoding="utf-8") as fh:
    REF = json.load(fh)

def post(url, ruta, cuerpo):
    req = Request(url.rstrip("/") + ruta, json.dumps(cuerpo).encode(), {"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=60) as r:
            return json.load(r)
    except HTTPError as exc:
        return {"http": exc.code, **json.load(exc)}


def raices_validas(clave):
    raices = [float(r) for r in REF["raices"][clave]["raices_en_[-10,10]"]]
    cond = ECUACIONES[clave]["condicion"]
    return [r for r in raices if cond == "real" or (r > 1e-9)]


class TestValidacionBanco(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._ctx = servidor_local()
        cls.url = cls._ctx.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls._ctx.__exit__(None, None, None)

    def test_sistemas_lineales(self):
        for clave, s in SISTEMAS.items():
            with self.subTest(clave):
                r = post(self.url, "/api/ecuaciones/resolver", {"A": s["A"], "b": s["b"]})
                ref = REF["lineales"][clave]
                self.assertEqual((r["rango_A"], r["rango_aumentada"]), (ref["rango_A"], ref["rango_aumentada"]))
                if ref["tipo"] != "unica":
                    self.assertEqual(r["tipo_sistema"], "SCI")
                    continue
                x = [Fraction(str(v)) for v in r["vector_solucion"]]
                self.assertEqual(x, [Fraction(v) for v in ref["solucion"]])
                for fila, bi in zip(s["A"], s["b"]):
                    self.assertEqual(sum(Fraction(a) * xi for a, xi in zip(fila, x)), Fraction(bi))

    def test_determinantes_e_inversas(self):
        for clave, m in MATRICES.items():
            with self.subTest(clave):
                d = post(self.url, "/api/matrices/determinante", {"A": m})
                self.assertEqual(Fraction(str(d["determinante"])), Fraction(REF["matrices"][clave]["det"]))
                inv = post(self.url, "/api/matrices/inversa", {"A": m})
                B = [[Fraction(str(v)) for v in fila] for fila in inv["matriz_inversa"]]
                self.assertEqual(B, [[Fraction(v) for v in fila] for fila in REF["matrices"][clave]["inversa"]])
                for i in range(4):
                    for j in range(4):
                        self.assertEqual(sum(Fraction(m[i][k]) * B[k][j] for k in range(4)), int(i == j))

    def _comprobar_raiz(self, clave, metodo, respuesta):
        self.assertNotIn("error", respuesta, respuesta.get("error"))
        self.assertTrue(respuesta.get("convergio"), respuesta.get("motivo"))
        x = float(respuesta["raiz"])
        self.assertLessEqual(min(abs(x - r) for r in raices_validas(clave)), 1e-6, f"{metodo}: x={x}")
        self.assertLess(abs(F[clave](x)), 1e-4)

    def test_raices_con_datos_iniciales_realistas(self):
        self._resolver_banco(lambda clave: ECUACIONES[clave]["funcion"])

    def test_raices_escritas_como_en_el_documento(self):
        self._resolver_banco(ENTRADAS_DOCUMENTO.get)

    def test_producto_implicito_del_documento_se_diagnostica(self):
        for clave, (factor, siguiente) in IMPLICITOS.items():
            with self.subTest(clave):
                r = post(self.url, "/api/biseccion/resolver",
                         {"funcion": ECUACIONES[clave]["ecuacion"], "a": 0, "b": 1, "tolerancia": 1e-6})
                self.assertEqual(r.get("http"), 400)
                self.assertRegex(r["error"], rf"multiplicación entre '?{factor}'? y '?{siguiente}")

    def _resolver_banco(self, entrada):
        for clave in ECUACIONES:
            a, b = INICIALES[clave]
            f = entrada(clave)
            casos = {
                "biseccion": ("/api/biseccion/resolver", {"funcion": f, "a": a, "b": b, "tolerancia": 1e-6}),
                "regla_falsa": ("/api/regla-falsa/resolver", {"funcion": f, "xl": a, "xu": b, "tolerancia": 1e-6}),
                "secante": ("/api/secante/resolver", {"funcion": f, "x0": a, "x1": b, "tolerancia": 1e-6}),
                "newton": ("/api/newton-raphson/resolver", {"funcion": f, "x0": (a + b) / 2, "tolerancia": 1e-6}),
            }
            for metodo, (ruta, cuerpo) in casos.items():
                with self.subTest(f"{clave} {metodo}"):
                    self._comprobar_raiz(clave, metodo, post(self.url, ruta, cuerpo))


if __name__ == "__main__":
    unittest.main()
