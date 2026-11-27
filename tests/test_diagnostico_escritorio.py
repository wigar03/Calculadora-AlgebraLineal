"""El diagnóstico del ejecutable (`--diagnostico`) debe aceptar la interfaz real con todos sus módulos."""
import json
import tempfile
import threading
import time
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

    def ejecutar_con_carga(self, retraso, espera):
        cargada = threading.Event()
        inicio = time.monotonic()
        if retraso is not None:
            threading.Timer(retraso, cargada.set).start()
        with tempfile.TemporaryDirectory() as carpeta, servidor_local() as url:
            destino = Path(carpeta) / "diagnostico.json"
            comprobar_escritorio(VentanaSimulada(modulos_esperados()), cargada, url, destino, inicio, espera=espera)
            return json.loads(destino.read_text(encoding="utf-8"))

    def test_carga_lenta_que_termina_se_acepta_con_tiempos(self):
        resultado = self.ejecutar_con_carga(0.3, espera=5)
        self.assertTrue(resultado["ok"], resultado)
        self.assertGreaterEqual(resultado["tiempos"]["carga_s"], 0.25)
        self.assertIn("total_s", resultado["tiempos"])
        self.assertFalse(resultado["carga_lenta"])

    def test_carga_que_nunca_termina_falla_con_motivo_y_tiempos(self):
        resultado = self.ejecutar_con_carga(None, espera=0.3)
        self.assertFalse(resultado["ok"])
        self.assertIn("no terminó de cargar", resultado["error"])
        self.assertNotIn("carga_s", resultado["tiempos"])

    def test_cuenta_formulas_cuando_el_renderizado_se_estabiliza(self):
        # KaTeX sigue renderizando tras el evento «loaded»: el recuento no debe depender del momento de lectura.
        class VentanaProgresiva(VentanaSimulada):
            def __init__(self, modulos, recuentos):
                super().__init__(modulos)
                self.recuentos, self.lecturas = list(recuentos), 0

            def evaluate_js(self, _codigo):
                datos = super().evaluate_js(_codigo)
                datos["formulas"] = self.recuentos[min(self.lecturas, len(self.recuentos) - 1)]
                self.lecturas += 1
                return datos

        ventana = VentanaProgresiva(modulos_esperados(), [300, 330, 342, 344, 344, 344])
        cargada = threading.Event()
        cargada.set()
        with tempfile.TemporaryDirectory() as carpeta, servidor_local() as url:
            destino = Path(carpeta) / "diagnostico.json"
            comprobar_escritorio(ventana, cargada, url, destino)
            resultado = json.loads(destino.read_text(encoding="utf-8"))
        self.assertTrue(resultado["ok"], resultado)
        self.assertEqual(resultado["interfaz"]["formulas"], 344)
        self.assertGreaterEqual(ventana.lecturas, 6)

    def test_rechaza_una_interfaz_sin_todos_los_modulos(self):
        resultado = self.ejecutar(modulos_esperados() - 1)
        self.assertFalse(resultado["ok"])
        self.assertIn("incompleto", resultado["error"])


if __name__ == "__main__":
    unittest.main()
