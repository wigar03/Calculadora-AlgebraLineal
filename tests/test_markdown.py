"""Validación pública y casos adversos del verificador Markdown, sin red."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.verificar_markdown import archivos_publicos, verificar


RAIZ = Path(__file__).resolve().parents[1]


class TestMarkdown(unittest.TestCase):
    def test_documentos_publicos(self):
        resultado = subprocess.run(
            [sys.executable, "-X", "utf8", str(RAIZ / "scripts/verificar_markdown.py")],
            cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        self.assertGreaterEqual(len(archivos_publicos(RAIZ)), 10)

    def revisar(self, texto, destinos=None):
        with tempfile.TemporaryDirectory() as carpeta:
            raiz = Path(carpeta)
            for nombre, contenido in (destinos or {}).items():
                archivo = raiz / nombre
                archivo.parent.mkdir(parents=True, exist_ok=True)
                archivo.write_text(contenido, encoding="utf-8")
            origen = raiz / "README.md"
            origen.write_text(texto, encoding="utf-8")
            return "\n".join(verificar(origen, raiz))

    def test_enlaces_imagenes_y_anclas(self):
        texto = ('# Inicio\n[guía](gu%C3%ADa.md#secci%C3%B3n-1)\n'
                 '![vista](img/vista.png)\n[local](#inicio)\n'
                 '[web](https://example.org/no-existe)\n')
        self.assertEqual(self.revisar(texto, {
            "guía.md": "# Sección\n## Sección\n## Sección\n",
            "img/vista.png": "imagen",
        }), "")
        self.assertIn("enlace inexistente", self.revisar("# A\n![x](ausente.png)"))
        self.assertIn("ancla inexistente", self.revisar("# A\n[x](#ausente)"))

    def test_referencias_html_y_rutas(self):
        texto = ('# Inicio\n[ver][r]\n![r]\n[r]: <carpeta/a(b).md#destino>\n'
                 '[HTML](#manual)\n<a id="manual"></a>\n')
        self.assertEqual(self.revisar(texto, {"carpeta/a(b).md": "# Destino"}), "")
        self.assertIn("enlace inexistente", self.revisar('# A\n<img src="no.png">'))
        self.assertIn("ancla inexistente", self.revisar(
            "# A\n[x](otro.md#dentro)", {"otro.md": "# Otro\n```text\n# Dentro\n```"}))

    def test_bloques_y_codigo_literal(self):
        self.assertIn("bloque sin cerrar", self.revisar("# A\n```python\nx=1"))
        self.assertEqual(self.revisar(
            "# A\n````text\n```\n$ \\frac{1}{2}\n````\n"
            "~~~text\n$ [x](no.md)\n~~~\n`2*x + 3` y ``$ \\frac``\n"), "")

    def test_matematicas_y_escapes(self):
        self.assertEqual(self.revisar(
            "# A\n$\\frac{1}{2}$ y $`x_i^2`$. Precio: \\$5.\n"
            "$$\nx=1\n$$\n```math\nA=\\begin{pmatrix}1\\end{pmatrix}\n```\n"), "")
        for texto, mensaje in [
            ("$x", "$ sin pareja"), ("$$\nx=1", "$$ sin pareja"),
            ("\\frac{1}{2}", "LaTeX fuera"),
            ("\\begin{pmatrix}1\\end{pmatrix}", "LaTeX fuera"),
        ]:
            with self.subTest(texto=texto):
                self.assertIn(mensaje, self.revisar("# A\n" + texto))

    def test_jerarquia_y_titulos_repetidos(self):
        self.assertIn("salto de título", self.revisar("# A\n### B\n"))
        self.assertIn("salto de título", self.revisar("### A\n"))
        self.assertEqual(self.revisar(
            "# A\n## B\n## B\n[x](#b-1)\n## C\n### D\n"), "")


if __name__ == "__main__":
    unittest.main()
