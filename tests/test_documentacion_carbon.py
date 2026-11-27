"""Coherencia de límites y contratos publicados tras la auditoría Carbon."""
from pathlib import Path
import unittest

RAIZ = Path(__file__).resolve().parents[1]


class TestDocumentacionCarbon(unittest.TestCase):
    def test_limites_publicos_de_los_modulos(self):
        guia = (RAIZ / "docs/guia-matematica.md").read_text(encoding="utf-8")
        for inicio, fin, limite in (("Módulo 2:", "Módulo 3:", "1 \\le k \\le 10"),
                                   ("Módulo 3:", "Módulo 4:", "8 filas y 8 columnas"),
                                   ("Módulo 4:", "Módulo 5:", "orden 2 a 6"),
                                   ("Módulo 5:", "Módulo 6:", "10 ecuaciones y 10 incógnitas")):
            self.assertIn(limite, guia.split(inicio)[1].split(fin)[0])
        readme = (RAIZ / "README.md").read_text(encoding="utf-8")
        self.assertIn("n \\le 20", readme)
        self.assertIn("general hasta orden 12", readme)

    def test_notacion_parada_muestreo_y_api_iterativos(self):
        guia = (RAIZ / "docs/guia-matematica.md").read_text(encoding="utf-8")
        for fragmento in ("201 puntos equiespaciados", "residuo escalado", "margen del 10 %",
                          "x¹⁰", "signo menos Unicode", "asin", "acos", "atan",
                          "incluso con el criterio `cambio`"):
            self.assertIn(fragmento, guia)
        for ruta in ("resolver", "comparar", "analizar", "texto"):
            self.assertIn(f"`/api/iterativos/{ruta}`", guia)
        self.assertNotIn("muestreo dinámico adaptativo", guia)
        self.assertNotIn("Nuevos archivos:", guia)
