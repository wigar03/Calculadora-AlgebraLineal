"""Referencias independientes y casos de frontera para estabilidad exacta."""
import json
import unittest
from fractions import Fraction as F
from pathlib import Path

from src.iterativos.convergencia import (
    matriz_iteracion, polinomio_caracteristico, schur_estable,
    libre_de_cuadrados, radio_polinomio, analizar_espectro,
    definida_positiva, garantia_convergencia, medir_cambio,
    cumple_tolerancia, detectar_parada,
)
from tests.validacion.banco_iterativos import CASOS

REF = json.loads((Path(__file__).parent / "validacion" /
                  "referencias_iterativos.json").read_text(encoding="utf-8"))


def matriz(nombre):
    return [[F(v) for v in fila] for fila in CASOS[nombre]["A"]]


class AnalisisExacto(unittest.TestCase):
    def test_radios_y_decisiones_del_banco(self):
        for nombre, referencia in REF.items():
            if "radio_espectral" not in referencia:
                continue
            with self.subTest(caso=nombre):
                radios, estables = analizar_espectro(matriz(nombre))
                for metodo, esperado in referencia["radio_espectral"].items():
                    self.assertAlmostEqual(radios[metodo], float(esperado), places=8)
                    self.assertEqual(estables[metodo], F(esperado) < 1)

    def test_matrices_de_iteracion_satisfacen_identidad_exacta(self):
        A = matriz("fracciones_3x3")
        for metodo in ("jacobi", "gauss_seidel"):
            T = matriz_iteracion(A, metodo)
            for i in range(3):
                for j in range(3):
                    if metodo == "jacobi":
                        self.assertEqual(A[i][i] * T[i][j], -A[i][j] if i != j else 0)
                    else:
                        self.assertEqual(sum(A[i][k] * T[k][j] for k in range(i + 1)),
                                         -A[i][j] if j > i else 0)

    def test_polinomio_y_multiplicidades(self):
        self.assertEqual(polinomio_caracteristico([[1, 2], [3, 4]]), [1, -5, -2])
        p = [F(1), F(-3, 2), F(3, 4), F(-1, 8)]
        self.assertEqual(libre_de_cuadrados(p), [1, F(-1, 2)])
        self.assertAlmostEqual(radio_polinomio(p), 0.5, places=10)

    def test_nilpotente_defectiva_radio_cero_exacto(self):
        p = polinomio_caracteristico(matriz_iteracion(matriz("jacobi_si_gs_no"), "jacobi"))
        self.assertEqual(p, [1, 0, 0, 0])
        self.assertTrue(schur_estable(p))
        self.assertEqual(radio_polinomio(p), 0)

    def test_schur_frontera_sin_epsilon(self):
        epsilon = F(1, 2 ** 300)
        for radio, esperado in ((1 - epsilon, True), (F(1), False),
                                 (1 + epsilon, False)):
            with self.subTest(radio=radio):
                self.assertEqual(schur_estable([1, -radio]), esperado)
                self.assertEqual(schur_estable([1, 0, radio ** 2]), esperado)
        self.assertFalse(schur_estable([1, -2, 1]))

    def test_spd_exacta_solo_garantiza_gauss_seidel(self):
        A = matriz("spd_no_dominante")
        self.assertTrue(definida_positiva(A))
        self.assertEqual(garantia_convergencia(A, "gauss_seidel", False, None)[0], "demostrada")
        self.assertEqual(garantia_convergencia(A, "jacobi", False, False)[0], "no_asegurada")
        self.assertFalse(definida_positiva([[1, 2], [2, 1]]))
        self.assertFalse(definida_positiva([[1, 1], [0, 1]]))
        self.assertTrue(definida_positiva(matriz("hilbert_4x4")))

    def test_limite_y_diagonal_nula(self):
        for A in ([[F(i == j) for j in range(13)] for i in range(13)], [[0, 1], [1, 1]]):
            radios, estables = analizar_espectro(A)
            self.assertIsNone(radios["jacobi"])
            self.assertIsNone(estables["gauss_seidel"])
            self.assertIn("No calculado", radios["metodo_calculo"])
