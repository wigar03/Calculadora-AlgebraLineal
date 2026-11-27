"""Sustitución no trivial y despeje contra Fraction y el núcleo independiente de SymPy."""
from fractions import Fraction
import unittest

from src.core.arithmetic import format_latex_number, format_latex_scalar
from src.ui.web_server import servidor_local
from tests.test_golden_api import consultar
from tests.test_validacion_banco_final import REF
from tests.validacion.banco_final import CONJUNTOS


class TestVerificacionIndependencia(unittest.TestCase):
    def comprobar(self, r, vectores, coef):
        verificacion = r["verificacion_independencia"]
        j = max(i for i, c in enumerate(coef) if c)
        despeje = [-c / coef[j] if i != j else Fraction(0) for i, c in enumerate(coef)]
        for titulo, pesos, objetivo in (("Relación", coef, [0] * len(vectores[0])),
                                        ("Despeje", despeje, vectores[j])):
            filas = [s for s in verificacion if s.startswith(titulo + ", componente")]
            self.assertEqual(len(filas), len(objetivo))
            for i, (fila, esperado) in enumerate(zip(filas, objetivo)):
                suma = sum((c * Fraction(v[i]) for c, v in zip(pesos, vectores)), Fraction(0))
                self.assertEqual(suma, Fraction(esperado))
                self.assertIn(f"= {format_latex_number(suma)}$", fila)
                self.assertIn("Satisface", fila)
                for c, v in zip(pesos, vectores):
                    if c:
                        producto = " \\cdot ".join(format_latex_scalar(x, True) for x in (c, v[i]))
                        self.assertIn(producto, fila)
        self.assertIn(r"= \vec{0}", " ".join(verificacion))
        self.assertTrue(set(verificacion).issubset(r["procedimiento"]["verificacion"]))

    def test_http_relacion_no_trivial_y_despeje_del_banco_y_racionales(self):
        casos = [(v, [Fraction(c) for c in REF["independencia"][k]["nucleo"][0]])
                 for k, v in CONJUNTOS.items()]
        casos.extend([([["1/2"], ["1/3"]], [Fraction(-2), Fraction(3)]),
                      ([[0, 0]], [Fraction(1)])])
        with servidor_local() as url:
            for vectores, coef in casos:
                with self.subTest(vectores=vectores):
                    estado, r = consultar(url, "/api/vectores/combinacion",
                                          {"vectores": vectores, "b": [0] * len(vectores[0])})
                    self.assertEqual(estado, 200)
                    self.assertEqual(r["relacion"]["coeficientes"], [str(c) for c in coef])
                    self.comprobar(r, vectores, coef)

    def test_independiente_justifica_solucion_trivial_por_rango(self):
        with servidor_local() as url:
            for vs in ([[1, 0], [0, 1]], [[1, 0, 0], [0, 1, 0]]):
                _, r = consultar(url, "/api/vectores/combinacion", {"vectores": vs, "b": [0] * len(vs[0])})
                texto = " ".join(r["verificacion_independencia"])
                self.assertIn(r"\operatorname{rg}(V) = 2 = k", texto)
                self.assertIn("solo existe la solución trivial", texto)
                self.assertIn(r"c_{1} = \cdots = c_{2} = 0", texto)
                self.assertTrue(set(r["verificacion_independencia"]).issubset(r["procedimiento"]["verificacion"]))
