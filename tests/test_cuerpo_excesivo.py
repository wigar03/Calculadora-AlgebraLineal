"""Un cuerpo mayor que el límite recibe un 413 legible, no un cierre abrupto (BrokenPipe) a mitad del envío."""
import json
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.core import limites
from src.ui.web_server import DESCARTE_MAX_BYTES, servidor_local


class TestCuerpoExcesivo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._ctx = servidor_local()
        cls.url = cls._ctx.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls._ctx.__exit__(None, None, None)

    def _post(self, cuerpo):
        req = Request(self.url + "/api/iterativos/texto", data=cuerpo, headers={"Content-Type": "application/json"})
        try:
            with urlopen(req, timeout=10) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            with exc:
                return exc.code, json.loads(exc.read().decode("utf-8"))

    def test_413_repetido_sin_romper_la_conexion(self):
        cuerpo = json.dumps({"texto": "x1 = 1\n" * 100000}).encode("utf-8")
        self.assertGreater(len(cuerpo), limites.CUERPO_MAX_BYTES)
        self.assertLess(len(cuerpo), DESCARTE_MAX_BYTES)
        for _ in range(25):
            estado, datos = self._post(cuerpo)
            self.assertEqual(estado, 413)
            self.assertEqual((datos["tipo"], datos["codigo"]), ("limite", "cuerpo_grande"))

    def test_cuerpo_enorme_no_bloquea_al_servidor(self):
        try:
            estado, _ = self._post(b" " * (DESCARTE_MAX_BYTES + 1024 * 1024))
            self.assertEqual(estado, 413)
        except (URLError, ConnectionError):
            pass  # más allá del descarte acotado se permite cerrar la conexión
        self.assertEqual(self._post(b'{"texto": "x1 = 1"}')[0], 200)


if __name__ == "__main__":
    unittest.main()
