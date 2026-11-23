"""Entradas hostiles a través del mismo HTTP que usa la página."""
import json
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src.ui.web_server import servidor_local


def post(url, cuerpo=b"{}", ruta="/api/vectores/operar", **cabeceras):
    peticion = Request(url + ruta, cuerpo, cabeceras)
    try:
        respuesta = urlopen(peticion, timeout=15)
    except HTTPError as error:
        respuesta = error
    with respuesta:
        return respuesta.code, json.load(respuesta), respuesta.headers


class TestRobustezServidor(unittest.TestCase):
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
