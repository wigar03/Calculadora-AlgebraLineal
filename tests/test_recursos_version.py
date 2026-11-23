"""Los `?v=` de index.html deben identificar el contenido real del recurso (12 caracteres de su SHA-256).

El hash se calcula con finales de línea LF (contenido del repositorio), igual en cualquier sistema operativo.

Si no coinciden, la ventana de escritorio puede seguir usando una copia antigua de un JS o CSS tras actualizar.
"""
import hashlib
import re
import unittest
from pathlib import Path

WEB = Path(__file__).resolve().parents[1] / "src" / "ui" / "web"
TERCEROS_SIN_VERSION = {"lucide.min.js"}


class TestVersionRecursos(unittest.TestCase):
    def setUp(self):
        self.html = (WEB / "index.html").read_text(encoding="utf-8")

    def test_cada_version_coincide_con_el_contenido(self):
        referencias = re.findall(r'(?:src|href)="([^"?]+)\?v=([0-9a-f]+)"', self.html)
        self.assertTrue(referencias)
        for ruta, version in referencias:
            with self.subTest(ruta):
                real = hashlib.sha256((WEB / ruta).read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:12]
                self.assertEqual(version, real, f"Actualice {ruta}?v={real}")

    def test_scripts_y_estilos_propios_llevan_version(self):
        propios = re.findall(r'(?:src|href)="([a-z][\w.-]*\.(?:js|css))(\?v=[0-9a-f]+)?"', self.html)
        for ruta, version in propios:
            if ruta in TERCEROS_SIN_VERSION:
                continue
            with self.subTest(ruta):
                self.assertTrue(version, f"{ruta} no lleva ?v=")


if __name__ == "__main__":
    unittest.main()
