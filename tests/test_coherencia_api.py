"""Regresiones HTTP de coherencia en validación previa y rutas de la API (C-04, C-05, C-06)."""
import json
import unittest
from unittest import mock
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src.core import limites
from src.ui.web_server import servidor_local


def post(url, ruta, cuerpo):
    peticion = Request(url + ruta, json.dumps(cuerpo).encode(), {"Content-Type": "application/json"})
    try:
        with urlopen(peticion, timeout=15) as r:
            return r.status, json.load(r)
    except HTTPError as exc:
        with exc:
            return exc.code, json.load(exc)


class TestCoherenciaAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = cls.enterClassContext(servidor_local())

    def test_c04_constante_e_frente_a_notacion_cientifica(self):
        for fn in ("e-1500+x", "2e5+x", "x*1e3", "exp(x)"):
            with self.subTest(fn=fn):
                estado, datos = post(self.url, "/api/biseccion/preview", {"funcion": fn})
                self.assertEqual(estado, 200, datos)
        estado, datos = post(self.url, "/api/biseccion/preview", {"funcion": "1e-1500+x"})
        self.assertEqual(estado, 400)
        self.assertEqual(datos["tipo"], "limite")

    def test_c05_vector_obligatorio_nulo_responde_400_y_x0_opcional_200(self):
        estado, datos = post(self.url, "/api/ecuaciones/resolver", {"A": [["1"]], "b": None})
        self.assertEqual(estado, 400, datos)
        self.assertEqual(datos["tipo"], "entrada")
        estado, datos = post(self.url, "/api/iterativos/resolver",
                             {"A": [["4", "1"], ["1", "3"]], "b": ["1", "2"], "x0": None, "metodo": "jacobi"})
        self.assertEqual(estado, 200, datos)

    def test_c06_enteros_sin_truncar_alias_cofactores_y_metodo_inversa(self):
        self.assertEqual(post(self.url, "/api/biseccion/muestrear",
                              {"funcion": "x", "a": 0, "b": 1, "cantidad": "20.0"})[0], 200)
        self.assertEqual(post(self.url, "/api/biseccion/muestrear",
                              {"funcion": "x", "a": 0, "b": 1, "cantidad": "20.5"})[0], 400)
        self.assertEqual(post(self.url, "/api/matrices/eficiencia-determinante", {"n": "5.0"})[0], 200)
        self.assertEqual(post(self.url, "/api/matrices/eficiencia-determinante", {"n": "5.5"})[0], 400)
        self.assertEqual(post(self.url, "/api/matrices/inversa", {"A": [["1"]], "metodo": "invalido"})[0], 400)
        with mock.patch("src.ui.web_server.calcular_respuesta") as motor:
            estado, datos = post(self.url, "/api/matrices/determinante",
                                 {"A": [[1] * 7 for _ in range(7)], "metodo": "laplace"})
            self.assertEqual((estado, datos["tipo"]), (400, "limite"))
            motor.assert_not_called()
        estado, datos = post(self.url, "/api/vectores/operar", {"operacion": "suma", "u": ["1", "abc"], "v": ["1", "2"]})
        self.assertEqual(estado, 400)
        self.assertIn("Componente 2", datos["error"])
