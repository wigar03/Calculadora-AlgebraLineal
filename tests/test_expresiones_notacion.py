"""Pruebas de notación, alias, igualdades y banco de 18 ecuaciones (50 puntos)."""

import json
import math
import re
import unittest
from pathlib import Path

from src.biseccion.expresiones import Expresion
from tests.validacion.banco_raices import ECUACIONES, INCOMPLETOS

IMPLICITAS = {"III-1", "III-2", "III-5", "III-13", "III-14", "IV-3"}
DOMINIOS = {
    "III-4": (0.1, 6.0), "III-6": (-1.8, 5.0), "III-11": (0.1, 6.0),
    "III-13": (-1.8, 5.0), "III-15": (-2.8, 6.0), "IV-1": (1.15, 6.0),
    "IV-3": (0.15, 1.45), "IV-4": (-0.9, 1.9),
}


def hacer_explicita(ecuacion):
    return re.sub(r"(\d)\s*(?=[A-Za-z])", r"\1*", ecuacion)


class TestNotacionEIgualdades(unittest.TestCase):
    def test_alias_simbolos_y_superindices(self):
        self.assertAlmostEqual(Expresion("sen(x)")(1.2), math.sin(1.2), places=12)
        self.assertAlmostEqual(Expresion("e^x")(1.5), math.exp(1.5), places=12)
        self.assertAlmostEqual(Expresion("e^(−x/2)")(2.0), math.exp(-1.0), places=12)
        self.assertAlmostEqual(Expresion("3·x² − 2×x³ + x⁴ – 1")(2.0), 3 * 4 - 2 * 8 + 16 - 1, places=12)
        self.assertEqual(Expresion("e^(−x) + sen(x)").latex(), r"e^{-x} + \sin\left(x\right)")
        self.assertEqual(Expresion("x² + x³ + x⁴").latex(), r"x^{2} + x^{3} + x^{4}")

    def test_igualdad_convierte_a_izquierda_menos_derecha(self):
        f = Expresion("ln(x) + sen(x) = 1.2")
        self.assertAlmostEqual(f(1.5), math.log(1.5) + math.sin(1.5) - 1.2, places=12)
        self.assertEqual(f.latex(), r"\ln\left(x\right) + \sin\left(x\right) - 1.2")
        g = Expresion("x^2 = x + 1")
        self.assertEqual(g.latex(), r"x^{2} - \left(x + 1\right)")
        self.assertAlmostEqual(g(3.0), 9.0 - 4.0, places=12)
        h = Expresion("cos(x) − x·e^x = 0")
        self.assertEqual(h.latex(), r"\cos\left(x\right) - x \cdot e^{x}")

    def test_banco_12_explicitas_aceptadas_y_6_implicitas_diagnosticadas(self):
        esperados = {
            "III-1": "4*x", "III-2": "3*x", "III-5": "3*x",
            "III-13": "3*sen", "III-14": "2*x", "IV-3": "2*x",
        }
        for clave, datos in ECUACIONES.items():
            with self.subTest(ejercicio=clave):
                if clave in IMPLICITAS:
                    with self.assertRaises(ValueError) as ctx:
                        Expresion(datos["ecuacion"])
                    msg = str(ctx.exception)
                    self.assertIn("multiplicación", msg.lower())
                    self.assertIn(esperados[clave], msg)
                else:
                    f_eq = Expresion(datos["ecuacion"])
                    self.assertTrue(f_eq.latex())
        with self.assertRaises(ValueError) as ctx:
            Expresion(INCOMPLETOS["IV-2"]["expresion"])
        self.assertIn("2*x", str(ctx.exception))
        f_iv2 = Expresion(hacer_explicita(INCOMPLETOS["IV-2"]["expresion"]))
        self.assertAlmostEqual(f_iv2(4.0), math.sqrt(128.0), places=12)
        for mal_x in (3.0, 1.0):
            with self.assertRaises(ValueError) as ctx:
                f_iv2(mal_x)
            self.assertIn("Error de dominio", str(ctx.exception))
        f_iv5 = Expresion(INCOMPLETOS["IV-5"]["expresion"])
        self.assertEqual(f_iv5.latex(), r"\sqrt{\frac{x + 4}{x - 1}}")
        self.assertAlmostEqual(f_iv5(6.0), math.sqrt(2.0), places=12)
        for mal_x in (1.0, 0.0):
            with self.assertRaises(ValueError) as ctx:
                f_iv5(mal_x)
            self.assertIn("Error de dominio", str(ctx.exception))

    def test_18_ecuaciones_equivalentes_a_funcion_en_50_puntos(self):
        for clave, datos in ECUACIONES.items():
            a, b = DOMINIOS.get(clave, (-2.5, 4.5))
            f_ref = Expresion(datos["funcion"])
            f_eq = Expresion(hacer_explicita(datos["ecuacion"]))
            evaluados = 0
            for i in range(50):
                x = a + (b - a) * i / 49
                with self.subTest(ejercicio=clave, i=i, x=x):
                    self.assertAlmostEqual(f_eq(x), f_ref(x), delta=1e-11)
                    evaluados += 1
            self.assertEqual(evaluados, 50)

    def test_raices_de_referencia_anulan_las_18_ecuaciones(self):
        ruta = Path(__file__).parent / "validacion" / "referencias.json"
        refs = json.loads(ruta.read_text(encoding="utf-8"))["raices"]
        for clave, datos in ECUACIONES.items():
            f_eq = Expresion(hacer_explicita(datos["ecuacion"]))
            for raiz_txt in refs[clave]["raices_en_[-10,10]"]:
                r = float(raiz_txt)
                with self.subTest(ejercicio=clave, raiz=r):
                    self.assertLess(abs(f_eq(r)), 1e-11)


if __name__ == "__main__":
    unittest.main()
