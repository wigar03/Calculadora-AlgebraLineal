"""Diagnósticos, permutaciones completas y residuo contra referencias independientes."""

import copy
import json
import math
import unittest
from fractions import Fraction as F
from itertools import permutations
from pathlib import Path

from src.iterativos import (diagonal_nula, dominancia_diagonal, leer_sistema,
                            rangos, reordenar, residuo, sistema_float)
from tests.validacion.banco_iterativos import CASOS

REFERENCIAS = json.loads((Path(__file__).parent / "validacion/referencias_iterativos.json")
                         .read_text(encoding="utf-8"))


class TestMatrizIterativos(unittest.TestCase):
    def test_dominancia_estricta_no_estricta_y_magnitudes(self):
        A, _, _ = leer_sistema(**CASOS["principal"])
        d = dominancia_diagonal(A)
        self.assertTrue(d["estricta"])
        self.assertTrue(d["no_estricta"])
        self.assertEqual(d["filas"][0], {"i": 0, "diagonal": 10.0, "suma": 3.0,
                                          "cumple": True, "no_estricta": True})
        A, _, _ = leer_sistema(**CASOS["spd_no_dominante"])
        d = dominancia_diagonal(A)
        self.assertFalse(d["estricta"])
        self.assertTrue(d["no_estricta"])
        self.assertTrue(all(f["diagonal"] == f["suma"] == 4 for f in d["filas"]))
        self.assertFalse(dominancia_diagonal([[0]])["estricta"])
        self.assertTrue(dominancia_diagonal([[0]])["no_estricta"])
        self.assertFalse(dominancia_diagonal([[1, 3], [2, 1]])["no_estricta"])
        json.dumps(d, allow_nan=False)

    def test_comparacion_exacta_y_diagonal_pequena_no_es_nula(self):
        epsilon = F(1, 10 ** 40)
        self.assertTrue(dominancia_diagonal([[F(1), 1 - epsilon], [0, 1]])["estricta"])
        self.assertEqual(diagonal_nula([[epsilon, 1], [2, 0]]), [1])
        for nombre, caso in CASOS.items():
            with self.subTest(caso=nombre):
                A, _, _ = leer_sistema(**caso)
                self.assertEqual(diagonal_nula(A), REFERENCIAS[nombre]["diagonal_nula"])

    def test_rangos_todos_los_casos_incluidos_singulares(self):
        for nombre, caso in CASOS.items():
            with self.subTest(caso=nombre):
                A, b, _ = leer_sistema(**caso)
                self.assertEqual(rangos(A, b), {"A": REFERENCIAS[nombre]["rango_A"],
                                               "aumentada": REFERENCIAS[nombre]["rango_aumentada"],
                                               "singular": REFERENCIAS[nombre]["rango_A"] < len(A)})
        self.assertEqual(rangos([[0] * 4 for _ in range(4)], [1, 2, 3, 4]),
                         {"A": 0, "aumentada": 1, "singular": True})

    def test_reordenables_dominantes_y_misma_solucion_exacta(self):
        for nombre in ("reordenable", "diagonal_nula_reordenable"):
            with self.subTest(caso=nombre):
                A, b, _ = leer_sistema(**CASOS[nombre])
                original = copy.deepcopy((A, b))
                nueva, nuevo_b, info = reordenar(A, b)
                self.assertTrue(info["aplicado"])
                self.assertEqual(info["permutacion"], [1, 0, 2])
                self.assertIn("dominancia diagonal estricta", info["motivo"])
                self.assertTrue(dominancia_diagonal(nueva)["estricta"])
                self.assertEqual(diagonal_nula(nueva), [])
                solucion = [F(v) for v in REFERENCIAS[nombre]["solucion"]]
                for matriz, vector in ((A, b), (nueva, nuevo_b)):
                    self.assertEqual([sum(a * x for a, x in zip(fila, solucion))
                                      for fila in matriz], vector)
                    self.assertEqual(rangos(matriz, vector)["A"], len(A))
                for k, fila in enumerate(info["permutacion"]):
                    self.assertEqual(nueva[k], A[fila])
                    self.assertEqual(nuevo_b[k], b[fila])
                self.assertEqual((A, b), original)
                nueva[0][0] = F(999)
                self.assertEqual((A, b), original)

    def test_diagonal_nula_sin_arreglo_y_orden_original_dominante(self):
        A, b, _ = leer_sistema(**CASOS["diagonal_nula_sin_arreglo"])
        nueva, nuevo_b, info = reordenar(A, b)
        self.assertEqual((nueva, nuevo_b), (A, b))
        self.assertEqual(info["permutacion"], [0, 1])
        self.assertFalse(info["aplicado"])
        self.assertIn("No existe", info["motivo"])
        A, b, _ = leer_sistema(**CASOS["principal"])
        self.assertFalse(reordenar(A, b)[2]["aplicado"])
