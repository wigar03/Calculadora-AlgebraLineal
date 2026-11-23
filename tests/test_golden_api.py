"""No regresión de la etapa 3: las 43 respuestas congeladas de los 11 módulos deben seguir siendo idénticas.

Solo se admiten claves nuevas en el primer nivel de la respuesta (p. ej. `procedimiento`); cualquier cambio en un
campo existente, aunque sea un decimal o un paso del procedimiento, hace fallar la prueba.
Los flotantes (también dentro de textos LaTeX) admiten 1e-12 relativo: `exp`, `sin`… de la biblioteca C difieren en el
último bit entre Windows y Linux. Enteros, fracciones y texto se comparan exactamente.
"""
import json
import math
import re
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src.ui.web_server import servidor_local

GOLDEN = Path(__file__).resolve().parent / "validacion" / "golden"


NUMERO = re.compile(r"-?\d+\.\d+(?:[eE][-+]?\d+)?")


def _float_igual(a, b):
    return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-300)


def equivalentes(a, b):
    if isinstance(a, float) or isinstance(b, float):
        return isinstance(a, (int, float)) and isinstance(b, (int, float)) and _float_igual(float(a), float(b))
    if isinstance(a, str) and isinstance(b, str):
        if a == b:
            return True
        return (NUMERO.split(a) == NUMERO.split(b) and len(NUMERO.findall(a)) == len(NUMERO.findall(b))
                and all(_float_igual(float(x), float(y)) for x, y in zip(NUMERO.findall(a), NUMERO.findall(b))))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(equivalentes(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(equivalentes(x, y) for x, y in zip(a, b))
    return a == b


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
                        recortado = {k: actual.get(k) for k in congelado}
                        if not equivalentes(recortado, congelado):
                            self.assertEqual(recortado, congelado)  # muestra la diferencia


if __name__ == "__main__":
    unittest.main()
