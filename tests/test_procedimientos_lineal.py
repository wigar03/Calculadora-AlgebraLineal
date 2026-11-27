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
    def test_entrada_exportada_conserva_los_datos_del_usuario(self):
        for caso in casos_lineales():
            if caso["ruta"] not in ("/api/vectores/operar", "/api/matrices/operar", "/api/vectores/combinacion"):
                continue
            with self.subTest(caso=caso["cuerpo"]):
                p = ADAPTADORES[caso["ruta"]](caso["respuesta"], caso["cuerpo"])
                self.assertTrue(p["entrada"])
                for item in p["entrada"]:
                    self.assertTrue(item["latex"])
        caso = next(c for c in casos_lineales() if c["ruta"] == "/api/vectores/combinacion")
        p = ADAPTADORES[caso["ruta"]](caso["respuesta"], {"vectores": [["1/7", "2"]], "b": ["3", "4"]})
        self.assertEqual([i["etiqueta"] for i in p["entrada"]], ["v_1", "b"])
        self.assertIn("1/7", p["entrada"][0]["latex"])

    def test_pasos_sin_repeticion_y_formulas_en_latex(self):
        for caso in casos_lineales():
            p = ADAPTADORES[caso["ruta"]](caso["respuesta"], caso["cuerpo"])
            for fuente, s in zip(pasos_fuente(caso["respuesta"]), p["pasos"]):
                if isinstance(fuente, str):
                    self.assertEqual(s["texto"], "")
                    if "$" not in fuente and "pasos_multiplicacion" in caso["respuesta"]:
                        self.assertEqual(s["latex"], [fuente])
                        self.assertEqual(s["titulo"], "")
        caso = next(c for c in casos_lineales() if c["ruta"] == "/api/vectores/combinacion")
        r = copy.deepcopy(caso["respuesta"])
        r["escalares"] = {"c_1": "-2t_10 + t_11"}
        p = ADAPTADORES[caso["ruta"]](r, {})
        self.assertEqual(p["resultado"][0]["latex"], "-2t_{10} + t_{11}")

    def test_determinante_exporta_dictamen_y_coste(self):
        for caso in casos_lineales():
            if caso["ruta"] != "/api/matrices/determinante":
                continue
            p = ADAPTADORES[caso["ruta"]](caso["respuesta"], caso["cuerpo"])
            dictamen = "Invertible" if caso["respuesta"]["es_invertible"] else "No invertible"
            self.assertIn(dictamen, " ".join(p["verificacion"]))
            self.assertIn(str(caso["respuesta"]["operaciones_estimadas"]), " ".join(p["avisos"]))

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
                if any(k in respuesta for k in ("pasos_multiplicacion", "pasos_mapeo")):
                    titulos = ["" if isinstance(s, str) and "$" not in s else s for s in titulos]
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
