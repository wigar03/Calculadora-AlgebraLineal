"""El texto de una release debe tener enlaces absolutos y un párrafo por línea (GitHub convierte saltos en <br>)."""
import re
import unittest
from pathlib import Path

from scripts.notas_release import REPO, cuerpo_release, enlaces_absolutos, unir_parrafos

RAIZ = Path(__file__).resolve().parents[1]


class TestNotasRelease(unittest.TestCase):
    def test_enlaces_relativos_desde_docs_se_fijan_al_tag(self):
        texto = "[README](../README.md#instalar) y [guía](guia-matematica.md) y [web](https://x.org) y [a](#b)"
        r = enlaces_absolutos(texto, "docs", "v9.9.9")
        self.assertIn(f"]({REPO}/blob/v9.9.9/README.md#instalar)", r)
        self.assertIn(f"]({REPO}/blob/v9.9.9/docs/guia-matematica.md)", r)
        self.assertIn("](https://x.org)", r)
        self.assertIn("](#b)", r)

    def test_une_parrafos_y_listas_sin_tocar_tablas_ni_codigo(self):
        texto = "# Título\n\nUna línea\nque sigue.\n\n- elemento\n  continuado\n- otro\n\n| a | b |\n|---|---|\n\n```\nx\ny\n```\n"
        r = unir_parrafos(texto)
        self.assertIn("Una línea que sigue.", r)
        self.assertIn("- elemento continuado\n- otro", r)
        self.assertIn("| a | b |\n|---|---|", r)
        self.assertIn("```\nx\ny\n```", r)

    def test_notas_publicadas_quedan_sin_enlaces_relativos(self):
        for notas in sorted((RAIZ / "docs").glob("notas-v1.*.md")):
            if "-rc." in notas.name:
                continue
            with self.subTest(notas.name):
                tag = notas.stem.replace("notas-", "")
                cuerpo = cuerpo_release(notas, tag, RAIZ)
                self.assertEqual(re.findall(r"\]\((?!https?://|#)[^)]+\)", cuerpo), [])


if __name__ == "__main__":
    unittest.main()
