"""Relaciones exactas del banco final contra su referencia SymPy independiente."""
from fractions import Fraction
import unittest

from src.vectores.combinacion_lineal import evaluar_combinacion_lineal
from src.ui.web_server import servidor_local
from tests.test_golden_api import consultar
from tests.test_validacion_banco_final import REF
from tests.validacion.banco_final import CONJUNTOS


class TestIndependenciaLineal(unittest.TestCase):
    def test_http_publica_analisis_solo_con_objetivo_cero(self):
        with servidor_local() as url:
            for clave, vs in CONJUNTOS.items():
                with self.subTest(clave=clave):
                    estado, r = consultar(url, "/api/vectores/combinacion", {"vectores": vs, "b": [0] * len(vs[0])})
                    self.assertEqual(estado, 200)
                    self.assertEqual(r["rango"], REF["independencia"][clave]["rango"])
                    self.assertEqual(r["relacion"]["coeficientes"], REF["independencia"][clave]["nucleo"][0])
                    self.assertEqual(r["independencia"], "dependiente")
                    verificacion = " ".join(r["procedimiento"]["verificacion"])
                    self.assertIn(r["relacion"]["latex"], verificacion)
                    self.assertIn(r["despeje"], verificacion)
            estado, r = consultar(url, "/api/vectores/combinacion", {"vectores": [[1, 0], [0, 1]], "b": [0, 0]})
            self.assertEqual((estado, r["independencia"], r["relacion"], r["despeje"]), (200, "independiente", None, None))
            _, r = consultar(url, "/api/vectores/combinacion", {"vectores": [[1, 0], [0, 1]], "b": [1, 0]})
            self.assertTrue({"independencia", "rango", "numero_vectores", "relacion", "despeje"}.isdisjoint(r))

    def test_banco_final_rango_relacion_y_despeje(self):
        for clave, vectores in CONJUNTOS.items():
            with self.subTest(clave=clave):
                r = evaluar_combinacion_lineal(vectores, [0] * len(vectores[0]))
                d, ref = r.analisis_independencia, REF["independencia"][clave]
                self.assertEqual(d["independencia"], "dependiente")
                self.assertEqual(d["rango"], ref["rango"])
                self.assertEqual(d["numero_vectores"], len(vectores))
                coef = [Fraction(v) for v in d["relacion"]["coeficientes"]]
                self.assertEqual(coef, [Fraction(v) for v in ref["nucleo"][0]])
                self.assertTrue(any(coef))
                self.assertTrue(all(sum(c * v[i] for c, v in zip(coef, vectores)) == 0
                                    for i in range(len(vectores[0]))))
                self.assertTrue(d["relacion"]["latex"].endswith(r"= \vec{0}"))
                self.assertTrue(d["despeje"].startswith(r"\vec{v}"))

    def test_base_canonica_y_objetivo_no_nulo(self):
        vs = [[1, 0], [0, 1]]
        d = evaluar_combinacion_lineal(vs, [0, 0]).analisis_independencia
        self.assertEqual(d, {"independencia": "independiente", "rango": 2,
                            "numero_vectores": 2, "relacion": None, "despeje": None})
        self.assertEqual(evaluar_combinacion_lineal(vs, [1, 0]).analisis_independencia, {})

    def test_relacion_racional_se_reduce_a_enteros_minimos(self):
        d = evaluar_combinacion_lineal([["1/2"], ["1/3"]], [0]).analisis_independencia
        self.assertEqual(d["relacion"]["coeficientes"], ["-2", "3"])
        self.assertEqual(d["despeje"], r"\vec{v}_{2} = \frac{2}{3}\vec{v}_{1}")
