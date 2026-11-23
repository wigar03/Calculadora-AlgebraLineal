"""Compilación PDF real, sin sustituir pdflatex por un comprobador de sintaxis.

REQUIERE_EXTERNOS=1 convierte la ausencia de pdflatex/Node en error de CI.
P2_LATEX_ARTEFACTOS conserva fuentes, logs y PDF para reproducir un fallo.
"""
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.test_exportacion_modulos import corpus_real, ejecutar_node

OVERFULL_MAX_PT = 1  # Criterio del integrador: ningún hbox mayor de 1 pt, en ambas pasadas.
ESPECIALES = r"áéíóú ÁÉÍÓÚ ñ Ñ ü Ü: 50% & x_1 # {llaves} ~ ^ \ ruta"
FALLOS_CONOCIDOS = {
    **dict.fromkeys(("biseccion[0]", "biseccion[1]", "biseccion_1000", "iterativos[0]",
                     "iterativos[1]", "iterativos[2]", "newton[2]", "secante[1]",
                     "ecuaciones[0]", "ecuaciones[1]"), "Contenido fuera del ancho: Overfull hbox > 1 pt"),
    "jacobi_20x20_10000": "amsmath limita pmatrix a 10 columnas: Extra alignment tab",
    "regla_falsa[3]": "Babel español redefine porcentaje: Incompatible glue units con \\,\\%",
    "regla_falsa_1000": "Babel español redefine porcentaje: Incompatible glue units con \\,\\%",
}


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
            desbordes = [float(n) for n in re.findall(r"Overfull \\hbox \(([\d.]+)pt too", log)]
            self.assertLessEqual(max(desbordes or [0]), OVERFULL_MAX_PT,
                                 f"{carpeta}: Overfull hbox máximo {max(desbordes or [0])} pt")
            verticales = [float(n) for n in re.findall(r"Overfull \\vbox \(([\d.]+)pt too", log)]
            self.assertLessEqual(max(verticales or [0]), 10, f"{carpeta}: Overfull vbox grave")
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
            if caso["id"] in FALLOS_CONOCIDOS:
                continue
            with self.subTest(caso=caso["id"]):
                tablas = caso["procedimiento"]["tablas"]
                self.comprobar_pdf(caso["id"], salida["latex"],
                                   multipagina=any(len(t["filas"]) > 30 for t in tablas))

    @unittest.expectedFailure
    def test_matrices_y_texto_especial_utf8_en_todos_los_campos(self):
        """Pendiente Antigravity: barra inversa imprime llaves espurias por doble escape."""
        procedimiento = {"version": 1, "modulo": "prueba", "titulo": ESPECIALES,
            "entrada": [{"etiqueta": ESPECIALES, "latex": r"\frac{1}{2}"}],
            "pasos": [{"titulo": ESPECIALES, "texto": ESPECIALES,
                       "latex": [r"A^{-1}A=I,\quad x\in\mathbb{R}"],
                       "matriz": [["1", "-2"], ["3/4", "5"]], "detalles": [ESPECIALES]}],
            "resultado": [{"etiqueta": ESPECIALES, "latex": "x=2"}],
            "verificacion": [ESPECIALES], "avisos": [ESPECIALES],
            "tablas": [{"titulo": ESPECIALES, "columnas": ["k", ESPECIALES],
                        "filas": [[k, ESPECIALES] for k in range(40)]}]}
        salida = ejecutar_node([procedimiento])[0]
        # Compilar no basta: reescapar las llaves de textbackslash imprime llaves espurias.
        with self.subTest(comprobacion="escape literal de barra inversa"):
            self.assertIn(r"\textbackslash{}", salida["latex"])
            self.assertNotIn(r"\textbackslash\{\}", salida["latex"])
        with self.subTest(comprobacion="PDF y paginación del texto UTF-8"):
            self.comprobar_pdf("especiales_utf8", salida["latex"], multipagina=True)


def _pendiente(nombre, motivo):
    @unittest.expectedFailure
    def prueba(self):
        caso, salida = next((c, s) for c, s in zip(self.casos, self.salidas) if c["id"] == nombre)
        self.comprobar_pdf(nombre, salida["latex"],
                           multipagina=any(len(t["filas"]) > 30 for t in caso["procedimiento"]["tablas"]))
    prueba.__doc__ = "Pendiente Antigravity: " + motivo
    return prueba


for _nombre, _motivo in FALLOS_CONOCIDOS.items():
    setattr(TestExternoLatex, "test_pendiente_" + re.sub(r"\W", "_", _nombre), _pendiente(_nombre, _motivo))
