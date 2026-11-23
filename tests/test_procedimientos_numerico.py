"""Pruebas de los 7 adaptadores numéricos: validez, tablas completas y KaTeX estricto."""
import copy, json, os, re, subprocess, unittest
from pathlib import Path

from src.procedimientos import ADAPTADORES, adjuntar
from src.procedimientos.base import validar
from tests.validacion.corpus_golden import CORPUS

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "tests" / "validacion" / "golden"
RUTAS = (
    "/api/biseccion/resolver", "/api/regla-falsa/resolver",
    "/api/newton-raphson/resolver", "/api/secante/resolver",
    "/api/derivadas/derivar", "/api/iterativos/resolver", "/api/iterativos/comparar",
)


def _extraer_latex(proc):
    items = [(it[k], k == "latex") for blk in (proc["entrada"], proc["resultado"])
             for it in blk for k in ("etiqueta", "latex")]
    textos = list(proc["verificacion"]) + list(proc["avisos"])
    for p in proc["pasos"]:
        items.extend((expr, True) for expr in p["latex"])
        textos.extend([p["texto"], *p["detalles"]])
    for txt in textos:
        for m in re.finditer(r"\$\$([\s\S]*?)\$\$|\$([\s\S]*?)\$", txt):
            items.append(((m.group(1) or m.group(2)).strip(), bool(m.group(1))))
    for t in proc["tablas"]:
        items.extend((col, False) for col in t["columnas"])
    return items


def _validar_katex_estricto(items):
    js = ("const k=require('./src/ui/web/vendor/katex/katex.min.js');"
          "for(const [tex,disp] of JSON.parse(require('fs').readFileSync(0,'utf8')))"
          "  k.renderToString(tex,{displayMode:disp,throwOnError:true,strict:'error'});")
    res = subprocess.run(["node", "-e", js], input=json.dumps(items), text=True,
                         capture_output=True, cwd=ROOT, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if res.returncode != 0:
        raise AssertionError(f"KaTeX estricto falló:\n{res.stderr}")


def _casos_golden():
    grupos = ("biseccion", "regla_falsa", "newton", "secante", "derivadas", "iterativos")
    rutas_corpus = {r for g in grupos for r, _ in CORPUS[g] if r in RUTAS}
    casos = [c for g in grupos for c in json.loads((GOLDEN / f"{g}.json").read_text(encoding="utf-8"))
             if c["ruta"] in RUTAS]
    return rutas_corpus, casos


class TestProcedimientosNumerico(unittest.TestCase):
    def test_todas_las_rutas_registradas(self):
        for ruta in RUTAS:
            self.assertIn(ruta, ADAPTADORES, f"Falta adaptador para {ruta}")

    def test_corpus_golden_valido_tablas_y_katex_estricto(self):
        rutas_corpus, casos = _casos_golden()
        self.assertEqual(rutas_corpus, set(RUTAS))
        self.assertEqual(len(casos), 9)
        todos_latex = []
        for idx, caso in enumerate(casos):
            ruta, resp, cuerpo = caso["ruta"], caso["respuesta"], caso["cuerpo"]
            copia = copy.deepcopy(resp)
            with self.subTest(f"{idx}:{ruta}"):
                salida = adjuntar(ruta, resp, cuerpo)
                self.assertEqual(resp, copia, "El adaptador mutó la respuesta original")
                self.assertIn("procedimiento", salida)
                proc = validar(salida["procedimiento"])
                if ruta == "/api/derivadas/derivar":
                    self.assertEqual(proc["entrada"][0]["latex"], resp["funcion_latex"])
                    self.assertEqual(proc["resultado"][0]["latex"], resp["derivada_latex"])
                elif ruta == "/api/iterativos/comparar":
                    self.assertEqual(len(proc["tablas"]), 2)
                    self.assertEqual(len(proc["tablas"][0]["filas"]), len(resp["jacobi"]["iteraciones"]))
                    self.assertEqual(len(proc["tablas"][1]["filas"]), len(resp["gauss_seidel"]["iteraciones"]))
                elif ruta == "/api/iterativos/resolver":
                    self.assertEqual(len(proc["tablas"][0]["filas"]), len(resp["iteraciones"]))
                    self.assertEqual(proc["tablas"][0]["filas"][0][1], resp["iteraciones"][0]["x"][0])
                elif ruta == "/api/newton-raphson/resolver":
                    self.assertEqual(len(proc["tablas"][0]["filas"]), len(resp["pasos"]))
                    self.assertEqual(proc["tablas"][0]["filas"][-1][1], resp["pasos"][-1]["x"])
                else:
                    self.assertEqual(len(proc["tablas"][0]["filas"]), resp["iteraciones"])
                    campo, col = ("xr", 5) if "regla-falsa" in ruta else ("c", 3)
                    self.assertEqual(proc["tablas"][0]["filas"][-1][col], resp["pasos"][-1][campo])
                todos_latex.extend(_extraer_latex(proc))
        _validar_katex_estricto(todos_latex)

    def test_casos_borde_y_no_convergencia(self):
        from src.biseccion.metodo import resolver_biseccion
        from src.iterativos.resolver import resolver_iterativo
        from src.regla_falsa.metodo import resolver_regla_falsa
        from src.secante.metodo import resolver_secante
        casos = [
            ("/api/biseccion/resolver", {**resolver_biseccion("x - 1", 1, 2), "funcion_latex": "x - 1"}),
            ("/api/regla-falsa/resolver", {**resolver_regla_falsa("x^10 - 1", 0, 1.3, tolerancia=1e-4, max_iteraciones=20),
                                           "funcion_latex": "x^{10} - 1"}),
            ("/api/secante/resolver", resolver_secante("x^2 - 4", 2, 3)),
            ("/api/iterativos/resolver", resolver_iterativo([["1", "2"], ["2", "4"]], ["3", "6"], "jacobi")),
        ]
        latex = []
        for ruta, resp in casos:
            with self.subTest(ruta):
                proc = validar(adjuntar(ruta, resp, {})["procedimiento"])
                esperado = len(resp["iteraciones"]) if "iterativos" in ruta else resp["iteraciones"]
                self.assertEqual(len(proc["tablas"][0]["filas"]), esperado)
                latex.extend(_extraer_latex(proc))
        _validar_katex_estricto(latex)


if __name__ == "__main__":
    unittest.main()
