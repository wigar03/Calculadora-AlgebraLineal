"""Certificación local porcentual y cota geométrica por estancamiento (C-01)."""
from fractions import Fraction
import math
import unittest

try:
    import sympy as sp
except ImportError:  # pragma: no cover
    sp = None

from src.biseccion.metodo import resolver_biseccion
from src.newton_raphson.metodo import resolver_newton
from src.regla_falsa.metodo import resolver_regla_falsa
from src.secante.metodo import resolver_secante


class TestCertificacionPorcentual(unittest.TestCase):
    def test_ln_y_polinomio_con_referencia_independiente(self):
        raiz_ln = Fraction(1, 1)
        if sp is not None:
            x = sp.Symbol("x", real=True, positive=True)
            self.assertEqual(sp.solve(sp.log(x), x), [sp.Integer(1)])
        for res in (resolver_biseccion("ln(x)", "0.5", "2", tolerancia="2", criterio="relativo"),
                    resolver_regla_falsa("ln(x)", "0.5", "2", tolerancia="2")):
            self.assertTrue(res["convergio"] and res["certificacion"]["certificada"], res)
            self.assertAlmostEqual(res["certificacion"]["radio"], 0.02 * max(1.0, abs(res["raiz"])), places=15)
            self.assertGreaterEqual(res["certificacion"]["intervalo"][0], 0.5)
            self.assertAlmostEqual(res["raiz"], float(raiz_ln), delta=0.05)
        r1, r2 = Fraction(1, 1), Fraction(21, 20)
        self.assertEqual((r1 - r1) * (r1 - r2), Fraction(0))
        for res in (resolver_biseccion("(x-1)*(x-1.05)", "0.98", "1.01", tolerancia="0.1", criterio="relativo"),
                    resolver_regla_falsa("(x-1)*(x-1.05)", "0.98", "1.01", tolerancia="0.1")):
            self.assertTrue(res["convergio"], res)
            self.assertLess(res["certificacion"]["intervalo"][1], float(r2))

    def test_aviso_estancamiento_y_recorte_al_intervalo_validado(self):
        est = resolver_regla_falsa("x^10-1", 0, 1.3, tolerancia=1e-4)
        self.assertTrue(est["convergio"])
        self.assertGreater(est["certificacion"]["radio"], (1e-4 / 100.0) * max(1.0, abs(est["raiz"])))
        self.assertEqual(len(est["advertencias"]), 1)
        for dato in ("estancamiento", "\\lambda", "error absoluto estimado", "error relativo estimado", "\\varepsilon_a", "radio absoluto"):
            self.assertIn(dato.lower(), est["advertencias"][0].lower())
        a, b = resolver_regla_falsa("ln(x)", 0.5, 2.0, tolerancia=200)["certificacion"]["intervalo"]
        self.assertTrue(0.5 <= a and b <= 2.0)

    def test_aviso_compara_porcentajes_y_declara_radio_absoluto(self):
        for funcion, extremo, tol in (("x^10-1", 1.3, 1e-4), ("x^3-1", 3, 20)):
            with self.subTest(funcion=funcion):
                res = resolver_regla_falsa(funcion, 0, extremo, tolerancia=tol)
                self.assertTrue(res["convergio"])
                self.assertEqual(res["motivo"], "tolerancia")
                pasos = res["pasos"]
                lam = pasos[-1]["error_absoluto"] / pasos[-2]["error_absoluto"]
                estimado = lam / (1 - lam) * pasos[-1]["error_absoluto"]
                relativo = estimado / abs(res["raiz"]) * 100
                texto = res["advertencias"][0]
                self.assertIn(f"error absoluto estimado ≈ {estimado:.3g}", texto)
                self.assertIn(f"error relativo estimado ≈ {relativo:.3g} %", texto)
                self.assertIn(f"\\varepsilon_a$ = {res['error_relativo']:.3g} %", texto)
                self.assertIn(f"±{res['certificacion']['radio']:.3g} (radio absoluto)", texto)

    def test_metodos_abiertos_conservan_radio_en_fraccion(self):
        for res in (resolver_newton("x^2 - 2", "1.5", tolerancia="1e-4", criterio="relativo"),
                    resolver_secante("x^2 - 2", "1", "2", tolerancia="1e-4", criterio="relativo")):
            self.assertTrue(res["convergio"])
            self.assertAlmostEqual(res["raiz"], math.sqrt(2), delta=1e-4)
            self.assertAlmostEqual(res["certificacion"]["radio"], 1e-4 * max(1.0, abs(res["raiz"])), places=15)
