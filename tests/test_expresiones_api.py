"""Pruebas HTTP de notación y diagnósticos de Expresion en las cuatro rutas de raíces."""

import json
import threading
import unittest
from http.server import HTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src.ui.web_server import AlgebraLinearHandler


class TestExpresionesApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servidor = HTTPServer(("127.0.0.1", 0), AlgebraLinearHandler)
        cls.hilo = threading.Thread(target=cls.servidor.serve_forever, daemon=True)
        cls.hilo.start()
        cls.url = f"http://127.0.0.1:{cls.servidor.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()
        cls.hilo.join()

    def post(self, ruta, datos):
        req = Request(self.url + ruta, json.dumps(datos).encode(), {"Content-Type": "application/json"})
        try:
            resp = urlopen(req, timeout=5)
        except HTTPError as exc:
            resp = exc
        with resp:
            return resp.status, json.loads(resp.read())

    def test_nueva_notacion_e_igualdades_por_api(self):
        st, d = self.post("/api/biseccion/preview", {"funcion": "ln(x) + sen(x) = 1.2"})
        self.assertEqual(st, 200)
        self.assertEqual(d["latex"], r"\ln\left(x\right) + \sin\left(x\right) - 1.2")

        st, d = self.post("/api/biseccion/resolver", {"funcion": "ln(x) + sen(x) = 1.2", "a": 1, "b": 2, "tolerancia": "1e-6"})
        self.assertEqual(st, 200)
        self.assertAlmostEqual(d["raiz"], 1.27544958, places=5)

        st, d = self.post("/api/newton-raphson/preparar", {"funcion": "e^(−x) + cos(x) = 0.5", "a": 0, "b": 2})
        self.assertEqual(st, 200)
        self.assertIn("e^{-x}", d["funcion_latex"])

    def test_diagnosticos_especificos_en_cuatro_metodos(self):
        casos = [
            ("/api/biseccion/resolver", {"funcion": "x^3 − 4x − 9 = 0", "a": 2, "b": 3}, "4*x"),
            ("/api/regla-falsa/graficar", {"funcion": "sinn(x) - 1", "a": 0, "b": 2}, "sin"),
            ("/api/newton-raphson/preparar", {"funcion": "x^^2 - 1", "a": 0, "b": 2}, "^^"),
            ("/api/secante/graficar", {"funcion": "x = 1 = 2", "a": 0, "b": 2}, "2 signos '='"),
        ]
        for ruta, cuerpo, esperado in casos:
            with self.subTest(ruta=ruta):
                st, d = self.post(ruta, cuerpo)
                self.assertEqual(st, 400)
                self.assertIn("Error de sintaxis", d["error"])
                self.assertIn(esperado, d["error"])


if __name__ == "__main__":
    unittest.main()
