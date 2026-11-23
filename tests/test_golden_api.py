"""No regresión de la etapa 3: las 43 respuestas congeladas de los 11 módulos deben seguir siendo idénticas.

Solo se admiten claves nuevas en el primer nivel de la respuesta (p. ej. `procedimiento`); cualquier cambio en un
campo existente, aunque sea un decimal o un paso del procedimiento, hace fallar la prueba.
"""
import json
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src.ui.web_server import servidor_local

GOLDEN = Path(__file__).resolve().parent / "validacion" / "golden"


def consultar(url, ruta, cuerpo):
    peticion = Request(url + ruta, json.dumps(cuerpo).encode(), {"Content-Type": "application/json"})
    try:
        with urlopen(peticion, timeout=120) as respuesta:
            return respuesta.status, json.load(respuesta)
    except HTTPError as exc:
        return exc.code, json.load(exc)


class TestGoldenAPI(unittest.TestCase):
    def test_respuestas_congeladas(self):
        archivos = sorted(GOLDEN.glob("*.json"))
        self.assertEqual(len(archivos), 12)
        with servidor_local() as url:
            for archivo in archivos:
                for i, caso in enumerate(json.loads(archivo.read_text(encoding="utf-8"))):
                    with self.subTest(f"{archivo.stem}[{i}] {caso['ruta']}"):
                        estado, actual = consultar(url, caso["ruta"], caso["cuerpo"])
                        self.assertEqual(estado, 200, actual)
                        congelado = caso["respuesta"]
                        self.assertEqual({k: actual.get(k) for k in congelado}, congelado)


if __name__ == "__main__":
    unittest.main()
