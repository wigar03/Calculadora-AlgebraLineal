"""El diagnóstico del ejecutable (`--diagnostico`) debe aceptar la interfaz real con todos sus módulos."""
import json
import tempfile
import threading
import unittest
from pathlib import Path

from src.ui.diagnostico import comprobar_escritorio, modulos_esperados
from src.ui.web_server import servidor_local


class VentanaSimulada:
    def __init__(self, modulos):
        self.modulos = modulos

    def evaluate_js(self, _codigo):
        return {"modulos": self.modulos, "formulas": 40, "katex": True, "fuentes": True, "externos": []}

    def destroy(self):
        pass


class TestDiagnosticoEscritorio(unittest.TestCase):
    def test_cuenta_los_modulos_de_la_navegacion(self):
        self.assertEqual(modulos_esperados(), 11)

    def ejecutar(self, modulos):
        cargada = threading.Event()
        cargada.set()
        with tempfile.TemporaryDirectory() as carpeta, servidor_local() as url:
            destino = Path(carpeta) / "diagnostico.json"
            comprobar_escritorio(VentanaSimulada(modulos), cargada, url, destino)
            return json.loads(destino.read_text(encoding="utf-8"))

    def test_acepta_la_interfaz_completa(self):
        self.assertTrue(self.ejecutar(modulos_esperados())["ok"])

    def test_rechaza_una_interfaz_sin_todos_los_modulos(self):
        resultado = self.ejecutar(modulos_esperados() - 1)
        self.assertFalse(resultado["ok"])
        self.assertIn("incompleto", resultado["error"])


if __name__ == "__main__":
    unittest.main()
