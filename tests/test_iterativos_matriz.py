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

    def test_reordenamiento_en_limite_exhaustivo_y_heuristica_hasta_veinte(self):
        for n in (8, 9, 20):
            base = [[F(n + 1 if i == j else 1) for j in range(n)] for i in range(n)]
            orden = list(range(1, n)) + [0]
            A = [base[i] for i in orden]
            b = [F(i + 1) for i in orden]
            nueva, nuevo_b, info = reordenar(A, b)
            with self.subTest(n=n):
                self.assertTrue(dominancia_diagonal(nueva)["estricta"])
                self.assertEqual(nueva, base)
                self.assertEqual(nuevo_b, [F(i + 1) for i in range(n)])
                self.assertEqual(info["permutacion"], [n - 1] + list(range(n - 1)))
                self.assertIn("exhaustiva" if n <= 8 else "heurística", info["motivo"])

    def test_diagonal_no_nula_sin_garantia_y_camino_aumentante(self):
        bloques = ([[0, 1], [1, 2]], [[1, 2, 0], [1, 0, 2], [0, 1, 1]])
        for bloque in bloques:
            n = 2 if len(bloque) == 2 else 9
            A = [[int(i == j) for j in range(n)] for i in range(n)]
            for i, fila in enumerate(bloque):
                A[i][:len(fila)] = fila
            b = [sum(fila) for fila in A]
            nueva, nuevo_b, info = reordenar(A, b)
            with self.subTest(n=n):
                self.assertTrue(info["aplicado"])
                self.assertEqual(diagonal_nula(nueva), [])
                self.assertFalse(dominancia_diagonal(nueva)["estricta"])
                self.assertEqual([sum(fila) for fila in nueva], nuevo_b)
                self.assertIn("ninguna permutación", info["motivo"])
        A, b, _ = leer_sistema(**CASOS["diverge_ambos"])
        # Este caso se puede hacer dominante; el singular no admite esa mejora.
        self.assertTrue(dominancia_diagonal(reordenar(A, b)[0])["estricta"])
        A, b, _ = leer_sistema(**CASOS["singular_infinitas"])
        self.assertFalse(reordenar(A, b)[2]["aplicado"])

    def test_asignacion_imposible_aunque_cada_columna_tenga_un_no_nulo(self):
        for n in (3, 9):
            A = [[int(i == j) for j in range(n)] for i in range(n)]
            for i, fila in enumerate([[1, 1, 1], [0, 0, 1], [0, 0, 1]]):
                A[i][:3] = fila
            nueva, _, info = reordenar(A, list(range(n)))
            with self.subTest(n=n):
                self.assertTrue(all(any(fila[j] for fila in A) for j in range(n)))
                self.assertFalse(info["aplicado"])
                self.assertTrue(diagonal_nula(nueva))
                self.assertIn("No existe", info["motivo"])

    def test_asignacion_contra_todas_las_permutaciones_de_matrices_binarias_3x3(self):
        for mascara in range(512):
            A = [[(mascara >> (3 * i + j)) & 1 for j in range(3)] for i in range(3)]
            posibles = [[A[i] for i in p] for p in permutations(range(3))]
            estricta = any(all(abs(fila[i]) > sum(abs(v) for j, v in enumerate(fila) if i != j)
                               for i, fila in enumerate(B)) for B in posibles)
            sin_ceros = any(all(B[i][i] != 0 for i in range(3)) for B in posibles)
            nueva, nuevo_b, info = reordenar(A, [1, 2, 3])
            with self.subTest(mascara=mascara):
                self.assertEqual(dominancia_diagonal(nueva)["estricta"], estricta)
                self.assertEqual(not diagonal_nula(nueva), sin_ceros)
                self.assertEqual(nuevo_b, [i + 1 for i in info["permutacion"]])

    def test_residuo_signo_norma_por_filas_y_escala(self):
        A, b, x = [[4.0, -1.0], [2.0, 3.0]], [1.0, 2.0], [.5, -.25]
        original = copy.deepcopy((A, b, x))
        r = residuo(A, b, x)
        self.assertEqual(r["Ax"], [2.25, .25])
        self.assertEqual(r["residuo"], [-1.25, 1.75])
        self.assertEqual(r["residuo_inf"], 1.75)
        self.assertEqual(r["residuo_rel"], 7 / 18)
        self.assertEqual((A, b, x), original)
        for factor in (1000, 1e-100):
            escalado = residuo([[a * factor for a in fila] for fila in A],
                               [v * factor for v in b], x)
            self.assertAlmostEqual(escalado["residuo_rel"], r["residuo_rel"], places=15)

    def test_residuo_en_soluciones_independientes_de_todo_el_banco(self):
        for nombre, caso in CASOS.items():
            if "solucion" not in REFERENCIAS[nombre]:
                continue
            A, b, _ = sistema_float(*leer_sistema(**caso))
            x = [float(F(v)) for v in REFERENCIAS[nombre]["solucion"]]
            with self.subTest(caso=nombre):
                self.assertLessEqual(residuo(A, b, x)["residuo_rel"], 1e-15)

    def test_residuo_escala_cero_y_no_finitos(self):
        self.assertEqual(residuo([[0.0]], [0.0], [0.0]),
                         {"Ax": [0.0], "residuo": [0.0], "residuo_inf": 0.0, "residuo_rel": 0.0})
        for valor in (math.inf, -math.inf, math.nan):
            with self.subTest(valor=valor):
                r = residuo([[1.0]], [1.0], [valor])
                self.assertEqual(r["residuo_inf"], math.inf)
                self.assertEqual(r["residuo_rel"], math.inf)
        self.assertEqual(residuo([[1e308]], [0.0], [2.0])["residuo_rel"], math.inf)

    def test_residuo_relativo_no_se_anula_por_desbordamiento_de_la_escala(self):
        r = residuo([[1e308]], [1e308], [.9])
        self.assertAlmostEqual(r["residuo_rel"], 1 / 19, places=15)
        r = residuo([[1e308, 1e308], [1e308, -1e308]], [1e307, 0.0], [.1, .1])
        self.assertAlmostEqual(r["residuo_rel"], 1 / 3, places=15)
        self.assertTrue(math.isfinite(r["residuo_inf"]))

    def test_residuo_relativo_no_se_reconstruye_de_productos_subdesbordados(self):
        minimo = float.fromhex("0x0.0000000000001p-1022")
        casos = [([[1e-200]], [0.0], [1e-200]), ([[minimo]], [0.0], [.5]),
                 ([[1e-200, 5e-201], [5e-201, 1e-200]], [minimo] * 2,
                  [minimo / 1e-200] * 2),
                 ([[1e-200, 0.0], [0.0, 0.0]], [minimo, 0.0], [0.0, 1e-124])]
        for A, b, x in casos:
            # Referencia racional de los mismos datos binarios, no de su texto decimal.
            exacta_A = [[F(v) for v in fila] for fila in A]
            exacta_b, exacta_x = list(map(F, b)), list(map(F, x))
            r = [bi - sum(a * v for a, v in zip(fila, exacta_x))
                 for fila, bi in zip(exacta_A, exacta_b)]
            escala = (max(map(abs, exacta_b)) +
                      max(sum(map(abs, fila)) for fila in exacta_A) * max(map(abs, exacta_x)))
            esperado = float(max(map(abs, r)) / escala)
            with self.subTest(A=A, b=b, x=x):
                self.assertAlmostEqual(residuo(A, b, x)["residuo_rel"], esperado, places=15)
        self.assertEqual(residuo([[1e-200]], [0.0], [1e-200])["residuo_rel"], 1.0)

    def test_residuo_relativo_subnormal_invariante_de_escala(self):
        for escala in (1.0, 1e-200):
            A = [[2 * escala, escala], [escala, 2 * escala]]
            with self.subTest(escala=escala):
                self.assertAlmostEqual(residuo(A, [0.0, 0.0], [1e-200, -1e-200])
                                       ["residuo_rel"], 1 / 3, places=15)
