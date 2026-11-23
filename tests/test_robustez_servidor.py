"""Entradas hostiles a través del mismo HTTP que usa la página."""
import json
import socket
import time
import unittest
from unittest import mock
from urllib.parse import urlsplit
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src.ui.web_server import servidor_local
from src.core import limites


def post(url, cuerpo=b"{}", ruta="/api/vectores/operar", **cabeceras):
    peticion = Request(url + ruta, cuerpo, cabeceras)
    try:
        respuesta = urlopen(peticion, timeout=15)
    except HTTPError as error:
        respuesta = error
    with respuesta:
        return respuesta.code, json.load(respuesta), respuesta.headers


class TestRobustezServidor(unittest.TestCase):
    def test_limites_previos_sin_ejecutar_motor(self):
        casos = [
            ("/api/vectores/operar", {"u": [1] * (limites.VECTOR_MAX + 1)}),
            ("/api/vectores/combinacion", {"vectores": [[1]] * (limites.COMBINACION_K_MAX + 1)}),
            ("/api/vectores/combinacion", {"b": [1] * (limites.COMBINACION_N_MAX + 1)}),
            ("/api/matrices/operar", {"A": [[1] * (limites.MATRIZ_OPERAR_MAX + 1)]}),
            ("/api/matrices/inversa", {"A": [[1]] * (limites.INVERSA_MAX + 1)}),
            ("/api/ecuaciones/resolver", {"A": [[1]] * (limites.SISTEMA_MAX + 1)}),
            ("/api/matrices/determinante", {"A": [[1]] * (limites.DETERMINANTE_MAX + 1)}),
            ("/api/matrices/eficiencia-determinante", {"n": limites.EFICIENCIA_N_MAX + 1}),
            ("/api/iterativos/resolver", {"A": [[1]] * (limites.ITERATIVOS_MAX + 1)}),
            ("/api/iterativos/comparar", {"max_iteraciones": limites.ITERATIVOS_ITER_MAX + 1}),
            ("/api/biseccion/resolver", {"max_iteraciones": limites.RAICES_ITER_MAX + 1}),
            ("/api/secante/resolver", {"funcion": "x" * (limites.FUNCION_MAX_CARACTERES + 1)}),
            ("/api/biseccion/muestrear", {"cantidad": limites.PUNTOS_GRAFICA_MAX + 1}),
            ("/api/vectores/operar", {"u": ["1e5000000"]}),
            ("/api/vectores/operar", {"u": ["9" * (limites.DIGITOS_MAX + 1)]}),
        ]
        with servidor_local() as url:
            with mock.patch("src.ui.web_server.calcular_respuesta") as motor:
                for ruta, cuerpo in casos:
                    with self.subTest(ruta=ruta, cuerpo=cuerpo):
                        estado, datos, _ = post(url, json.dumps(cuerpo).encode(), ruta)
                        self.assertEqual(estado, 400)
                        self.assertEqual(datos["tipo"], "limite")
                motor.assert_not_called()

    def test_json_invalido_y_cuerpo_no_objeto(self):
        with servidor_local() as url:
            for cuerpo in (b"{no json", b"[1,2]"):
                with self.subTest(cuerpo=cuerpo):
                    estado, datos, _ = post(url, cuerpo)
                    self.assertEqual(estado, 400)
                    self.assertEqual(set(datos), {"error", "tipo", "codigo"})
                    self.assertEqual(datos["tipo"], "entrada")
                    self.assertNotIn("object has", datos["error"])
            self.assertEqual(post(url, b"{no json")[1]["error"],
                             "El cuerpo de la petición no es JSON válido")

    def test_host_origin_y_cabeceras(self):
        with servidor_local() as url:
            for cabeceras in ({"Host": "evil.example"}, {"Origin": "https://evil.example"},
                               {"Origin": "null"}, {"Host": "localhost:1"}):
                self.assertEqual(post(url, **cabeceras)[0], 403)
            _, _, cabeceras = post(url)
            self.assertEqual(cabeceras["X-Content-Type-Options"], "nosniff")
            self.assertEqual(cabeceras["Referrer-Policy"], "no-referrer")
            self.assertEqual(cabeceras["Cache-Control"], "no-cache")
            self.assertNotIn("Access-Control-Allow-Origin", cabeceras)
            self.assertIn("default-src 'self'", cabeceras["Content-Security-Policy"])
            with urlopen(url) as respuesta:
                self.assertEqual(respuesta.headers["Cache-Control"], "no-cache")
            with self.assertRaises(HTTPError) as error:
                urlopen(url + "/vendor/")
            self.assertEqual(error.exception.code, 404)

    def test_cuerpo_grande_y_lectura_con_plazo(self):
        with mock.patch.object(limites, "LECTURA_SOCKET_S", 0.15), servidor_local() as url:
            datos = b"x" * (limites.CUERPO_MAX_BYTES + 1)
            self.assertEqual(post(url, datos)[0], 413)
            destino = urlsplit(url)
            with socket.create_connection((destino.hostname, destino.port)) as cliente:
                cliente.settimeout(2)
                cliente.sendall(("POST /api/vectores/operar HTTP/1.1\r\n"
                                f"Host: {destino.netloc}\r\nContent-Length: 1000\r\n\r\n{{").encode())
                inicio = time.perf_counter()
                self.assertEqual(post(url, b'{"funcion":"x"}', "/api/biseccion/preview")[0], 200)
                self.assertLess(time.perf_counter() - inicio, 0.5)
                self.assertIn(b"503", cliente.recv(4096))

    def test_fallo_inesperado_no_expone_python(self):
        with servidor_local() as url, mock.patch("src.ui.web_server.calcular_respuesta",
                                                side_effect=AttributeError("secret object has no attribute")):
            with self.assertLogs("src.core.ejecucion", level="ERROR"):
                estado, datos, _ = post(url)
            self.assertEqual(estado, 500)
            self.assertEqual(datos["tipo"], "interno")
            self.assertNotIn("secret", json.dumps(datos))
