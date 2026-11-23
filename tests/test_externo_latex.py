"""Compilación PDF real, sin sustituir pdflatex por un comprobador de sintaxis.

REQUIERE_EXTERNOS=1 convierte la ausencia de pdflatex/Node en error de CI.
P2_LATEX_ARTEFACTOS conserva fuentes, logs y PDF para reproducir un fallo.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.test_exportacion_modulos import ROOT, corpus_real, ejecutar_node

OVERFULL_GRAVE_PT = 10  # 3,5 mm fuera de la caja; también se comprueba en la segunda pasada.
ESPECIALES = r"áéíóú ÁÉÍÓÚ ñ Ñ ü Ü: 50% & x_1 # {llaves} ~ ^ \ ruta"


def compilar(motor, fuente, carpeta):
    carpeta.mkdir(parents=True, exist_ok=True)
    tex = carpeta / "documento.tex"
    tex.write_text(fuente, encoding="utf-8")
    pasadas = []
    for numero in (1, 2):
        proceso = subprocess.run([motor, "-no-shell-escape", "-halt-on-error",
            "-interaction=nonstopmode", "-file-line-error", tex.name], cwd=carpeta,
            capture_output=True, timeout=180)
        log = tex.with_suffix(".log").read_text(encoding="utf-8", errors="replace")
        (carpeta / f"pasada-{numero}.log").write_text(log, encoding="utf-8")
        pasadas.append((proceso.returncode, log))
        if proceso.returncode:
            break
    return pasadas


class TestExternoLatex(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        faltan = [nombre for nombre in ("pdflatex", "node") if not shutil.which(nombre)]
        if faltan:
            motivo = "Herramientas externas ausentes: " + ", ".join(faltan)
            if os.environ.get("REQUIERE_EXTERNOS") == "1":
                raise AssertionError(motivo)
            raise unittest.SkipTest(motivo)
        cls.motor = shutil.which("pdflatex")
        cls.casos, cls.consultas = corpus_real()
        cls.salidas = ejecutar_node([c["procedimiento"] for c in cls.casos])
        destino = os.environ.get("P2_LATEX_ARTEFACTOS")
        if destino:
            cls.carpeta = Path(destino).resolve()
            cls.carpeta.mkdir(parents=True, exist_ok=True)
        else:
            temporal = tempfile.TemporaryDirectory(prefix="p2-pdflatex-")
            cls.addClassCleanup(temporal.cleanup)
            cls.carpeta = Path(temporal.name)

    def comprobar_pdf(self, nombre, fuente, multipagina=False):
        carpeta = self.carpeta / re.sub(r"[^a-zA-Z0-9_-]", "_", nombre)
        pasadas = compilar(self.motor, fuente, carpeta)
        self.assertEqual(len(pasadas), 2, f"{carpeta}: {pasadas[-1][1][-3500:]}")
        for codigo, log in pasadas:
            self.assertEqual(codigo, 0, f"{carpeta}: {log[-3500:]}")
            desbordes = [float(n) for n in re.findall(r"Overfull \\[hv]box \(([\d.]+)pt too", log)]
            self.assertFalse(any(n > OVERFULL_GRAVE_PT for n in desbordes),
                             f"{carpeta}: Overfull graves {desbordes}")
            self.assertNotIn("Missing character:", log, str(carpeta))
        pdf = carpeta / "documento.pdf"
        self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"), str(pdf))
        paginas = re.search(r"Output written on .*?\((\d+) pages?[,)]", pasadas[-1][1], re.S)
        self.assertIsNotNone(paginas, str(carpeta))
        self.assertGreater(int(paginas[1]), 1 if multipagina else 0, str(carpeta))

    def test_corpus_real_once_modulos_y_tablas_largas(self):
        self.assertEqual(len(self.consultas), 46)
        self.assertEqual(len(self.casos), 36)
        self.assertGreaterEqual(len({c["procedimiento"]["modulo"] for c in self.casos}), 11)
        for caso, salida in zip(self.casos, self.salidas):
            with self.subTest(caso=caso["id"]):
                tablas = caso["procedimiento"]["tablas"]
                self.comprobar_pdf(caso["id"], salida["latex"],
                                   multipagina=any(len(t["filas"]) > 30 for t in tablas))
