"""Adaptación pura del corpus lineal y renderizado con KaTeX local estricto."""
import copy
import json
from pathlib import Path
import subprocess
import unittest

from src.procedimientos import ADAPTADORES
from src.procedimientos.base import validar
from tests.validacion.corpus_golden import CORPUS

RAIZ = Path(__file__).resolve().parents[1]
MODULOS = ("vectores", "combinacion", "matrices", "inversa", "ecuaciones", "determinante")


def casos_lineales():
    for modulo in MODULOS:
        casos = json.loads((RAIZ / "tests/validacion/golden" / f"{modulo}.json").read_text(encoding="utf-8"))
        assert [(c["ruta"], c["cuerpo"]) for c in casos] == CORPUS[modulo]
        yield from casos


def pasos_fuente(respuesta):
    for clave in ("pasos", "desglose_componentes", "pasos_multiplicacion", "pasos_mapeo"):
        if clave in respuesta:
            return respuesta[clave]
    return []


class TestProcedimientosLineales(unittest.TestCase):
    def test_corpus_valido_mismos_pasos_y_sin_mutaciones(self):
        for caso in casos_lineales():
            with self.subTest(ruta=caso["ruta"], cuerpo=caso["cuerpo"]):
                respuesta, cuerpo = copy.deepcopy((caso["respuesta"], caso["cuerpo"]))
                p = ADAPTADORES[caso["ruta"]](respuesta, cuerpo)
                self.assertIs(validar(p), p)
                self.assertEqual(respuesta, caso["respuesta"])
                self.assertEqual(cuerpo, caso["cuerpo"])
                fuente = pasos_fuente(respuesta)
                titulos = [s.get("titulo", s.get("title")) if isinstance(s, dict) else s for s in fuente]
                self.assertEqual([s["titulo"] for s in p["pasos"]], titulos)
                for original, adaptado in zip(fuente, p["pasos"]):
                    if isinstance(original, dict):
                        self.assertEqual(adaptado["texto"], original.get("descripcion", original.get("description", "")))
                        self.assertEqual(adaptado["matriz"], original.get("matriz_estado", original.get("matrix")))
                        self.assertEqual(adaptado["detalles"], original.get("detalles", []))
                # Tampoco se comparten contenedores mutables con la respuesta.
                p["pasos"].clear()
                p["verificacion"].clear()
                self.assertEqual(respuesta, caso["respuesta"])

    def test_no_recalcula_los_resultados(self):
        for caso in casos_lineales():
            r = copy.deepcopy(caso["respuesta"])
            if "determinante" in r:
                r["determinante"] = "987654321/7"
                p = ADAPTADORES[caso["ruta"]](r, {})
                self.assertIn({"etiqueta": r"\det(A)", "latex": r["determinante"]}, p["resultado"])
            if "matriz_resultado" in r:
                r["matriz_resultado"][0][0] = "987654321/7"
                p = ADAPTADORES[caso["ruta"]](r, {})
                self.assertIn("987654321/7", p["resultado"][0]["latex"])

    def test_todo_latex_renderiza_en_katex_estricto(self):
        procedimientos = [ADAPTADORES[c["ruta"]](c["respuesta"], c["cuerpo"]) for c in casos_lineales()]
        proceso = subprocess.run(["node", "tests/procedimientos_lineal_katex.cjs", "--stdin"], cwd=RAIZ,
                                 input=json.dumps(procedimientos), capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proceso.returncode, 0, proceso.stdout + proceso.stderr)
        self.assertGreater(json.loads(proceso.stdout)["bloques"], 500)


if __name__ == "__main__":
    unittest.main()
