"""Jacobi contra tres pasos racionales independientes y errores de entrada."""

import copy
import json
import math
import unittest
from fractions import Fraction as F
from pathlib import Path

from src.iterativos import leer_sistema, paso_jacobi, sistema_float
from tests.validacion.banco_iterativos import CASOS

REFERENCIAS = json.loads((Path(__file__).parent / "validacion/referencias_iterativos.json")
                         .read_text(encoding="utf-8"))


class TestJacobi(unittest.TestCase):
    def test_tres_iteraciones_todo_el_banco_sin_diagonal_nula(self):
        validados = []
        for nombre, caso in CASOS.items():
            referencia = REFERENCIAS[nombre]
            if referencia["diagonal_nula"]:
                continue
            A, b, x = sistema_float(*leer_sistema(**caso))
            validados.append(nombre)
            for k, esperado in enumerate(referencia["iteraciones_jacobi"], 1):
                x, detalle = paso_jacobi(A, b, x)
                for i, (valor, exacto) in enumerate(zip(x, esperado)):
                    with self.subTest(caso=nombre, k=k, i=i):
                        ref = float(F(exacto))
                        self.assertTrue(math.isclose(valor, ref, rel_tol=1e-12,
                                                     abs_tol=1e-12 if ref == 0 else 0))
                        self.assertEqual(detalle[i]["usa_nuevos"], [])
                        self.assertEqual(detalle[i]["valor"], valor)
        self.assertEqual(len(validados), 15)

    def test_no_usa_valores_nuevos_como_gauss_seidel(self):
        A, b, x = sistema_float(*leer_sistema(**CASOS["principal"]))
        nuevo, _ = paso_jacobi(A, b, x)
        self.assertAlmostEqual(nuevo[1], 25 / 11, places=14)
        gs = float(F(REFERENCIAS["principal"]["iteraciones_gauss_seidel"][0][1]))
        self.assertNotAlmostEqual(nuevo[1], gs, places=12)
        self.assertEqual(x, [0.0] * 4)

    def test_copia_entradas_y_detalle_por_componente(self):
        A, b, x = sistema_float(*leer_sistema(**CASOS["principal_x0_unos"]))
        original = copy.deepcopy((A, b, x))
        nuevo, detalle = paso_jacobi(A, b, tuple(x))
        self.assertEqual((A, b, x), original)
        self.assertIsNot(nuevo, x)
        self.assertEqual([d["i"] for d in detalle], list(range(4)))
        for d in detalle:
            self.assertEqual(set(d), {"i", "formula_latex", "sustitucion_latex",
                                      "valor", "usa_nuevos"})
            self.assertIsInstance(d["valor"], float)
        self.assertIn(r"x_{1}^{(k+1)} = \frac{6", detalle[0]["formula_latex"])
        self.assertIn(r"x_{2}^{(k)}", detalle[0]["formula_latex"])
        self.assertIn(r"\left(-1\right)\cdot\left(1\right)",
                      detalle[0]["sustitucion_latex"])
        self.assertIn(r"{10}", detalle[0]["formula_latex"])
        json.dumps(detalle, allow_nan=False)

    def test_unidimensional_y_indices_de_dos_cifras(self):
        nuevo, detalle = paso_jacobi([[2.0]], [3.0], [100.0])
        self.assertEqual(nuevo, [1.5])
        self.assertIn(r"\left(0\right)", detalle[0]["formula_latex"])
        A, b, x = sistema_float(*leer_sistema(**CASOS["dd_10x10"]))
        _, detalle = paso_jacobi(A, b, x)
        self.assertIn(r"x_{10}^{(k)}", detalle[0]["formula_latex"])
        self.assertTrue(detalle[9]["formula_latex"].startswith(r"x_{10}^{(k+1)}"))

    def test_diagonal_nula_con_indicacion_de_fila_y_correccion(self):
        for nombre in ("diagonal_nula_reordenable", "diagonal_nula_sin_arreglo"):
            with self.subTest(caso=nombre):
                sistema = sistema_float(*leer_sistema(**CASOS[nombre]))
                with self.assertRaisesRegex(ValueError, "fila 1, columna 1.*Reordena"):
                    paso_jacobi(*sistema)

    def test_dimensiones_invalidas(self):
        for sistema in (([], [], []), ([[1]], [], [0]), ([[1]], [1], []),
                        ([[1, 2]], [1], [0])):
            with self.subTest(sistema=sistema), self.assertRaisesRegex(ValueError, "dimensión"):
                paso_jacobi(*sistema)

    def test_paso_con_productos_subnormales_conserva_el_esquema(self):
        minimo = float.fromhex("0x0.0000000000001p-1022")
        A, b, x = [[1e-200, 5e-201], [5e-201, 1e-200]], [minimo] * 2, [minimo / 1e-200] * 2
        esperado = [float((F(b[i]) - sum(F(A[i][j]) * F(x[j]) for j in range(2) if j != i))
                          / F(A[i][i])) for i in range(2)]
        nuevo, detalle = paso_jacobi(A, b, x)
        for valor, referencia in zip(nuevo, esperado):
            self.assertTrue(math.isclose(valor, referencia, rel_tol=1e-15, abs_tol=0.0))
        self.assertEqual([d["usa_nuevos"] for d in detalle], [[], []])

    def test_solucion_subnormal_por_api_con_residuo_independiente(self):
        from urllib.request import Request, urlopen
        from src.ui.web_server import servidor_local
        payload = {"A": [["1e-200", "5e-201"], ["5e-201", "1e-200"]],
                   "b": ["5e-324", "5e-324"], "metodo": "jacobi", "tolerancia": 1e-6}
        with servidor_local() as base:
            req = Request(base + "/api/iterativos/resolver", json.dumps(payload).encode(),
                          {"Content-Type": "application/json"})
            with urlopen(req, timeout=5) as response:
                result = json.loads(response.read())
        A, b, x = [[F(v) for v in row] for row in result["A"]], list(map(F, result["b"])), list(map(F, result["solucion"]))
        r = max(abs(bi - sum(a * v for a, v in zip(row, x))) for row, bi in zip(A, b))
        escala = max(map(abs, b)) + max(sum(map(abs, row)) for row in A) * max(map(abs, x))
        self.assertTrue(result["convergio"])
        self.assertLessEqual(float(r / escala), 1e-6)
        self.assertGreater(len(result["iteraciones"]), 2)


class TestEntradaIterativos(unittest.TestCase):
    def test_decimales_fracciones_y_conversion_sin_mutacion(self):
        datos = ([["1/3", "0.75"], ["-2.5", 7]], [1, "-1/2"], ["0.2", 3])
        original = copy.deepcopy(datos)
        exactos = leer_sistema(*datos)
        self.assertEqual(exactos, ([[F(1, 3), F(3, 4)], [F(-5, 2), F(7)]],
                                   [F(1), F(-1, 2)], [F(1, 5), F(3)]))
        A, b, x = sistema_float(*exactos)
        self.assertEqual(A, [[1 / 3, .75], [-2.5, 7.0]])
        self.assertEqual(b, [1.0, -.5])
        self.assertEqual(x, [.2, 3.0])
        self.assertTrue(all(isinstance(v, float) for fila in A for v in fila))
        self.assertEqual(datos, original)
        self.assertIsInstance(exactos[0][0][0], F)

    def test_cero_por_defecto_y_limites_uno_y_veinte(self):
        for n in (1, 20):
            A = [[int(i == j) for j in range(n)] for i in range(n)]
            exactos = leer_sistema(A, [1] * n)
            self.assertEqual(exactos[2], [F(0)] * n)
            self.assertTrue(all(isinstance(v, F) for fila in exactos[0] for v in fila))
            self.assertTrue(all(isinstance(v, F) for v in exactos[1] + exactos[2]))
        for A in ([], [[0] * 21 for _ in range(21)], None, "1"):
            with self.subTest(A=A), self.assertRaisesRegex(ValueError, "1 a 20.*ajusta"):
                leer_sistema(A, [])

    def test_matriz_no_cuadrada_y_longitudes_incorrectas(self):
        for A in ([[1, 2], [3]], [[1, 2], None], [[1, 2, 3], [4, 5, 6]]):
            with self.subTest(A=A), self.assertRaisesRegex(ValueError, "fila.*cuadrada.*columnas"):
                leer_sistema(A, [1, 2])
        for nombre, b, x0 in (("b", [1], None), ("b", None, None),
                              ("x0", [1, 2], [0]), ("x0", [1, 2], "00")):
            with self.subTest(nombre=nombre), self.assertRaisesRegex(ValueError,
                                                                   nombre + ".*2 componentes"):
                leer_sistema([[1, 0], [0, 1]], b, x0)

    def test_celdas_invalidas_indican_localizacion_y_como_corregir(self):
        valores = ("1/0", "a", "1/2/3", "", "  ", None, True, float("inf"),
                   float("nan"), [2])
        for v in valores:
            with self.subTest(valor=v):
                with self.assertRaisesRegex(ValueError, "A, fila 2, columna 1.*Escribe.*1/3"):
                    leer_sistema([[1, 0], [v, 1]], [1, 2])
                with self.assertRaisesRegex(ValueError, "b, fila 2, columna 1.*Escribe"):
                    leer_sistema([[1, 0], [0, 1]], [1, v])
                with self.assertRaisesRegex(ValueError, "x0, fila 1, columna 1.*Escribe"):
                    leer_sistema([[1, 0], [0, 1]], [1, 2], [v, 0])

    def test_float_no_acepta_desbordamiento_ni_subdesbordamiento_a_cero(self):
        for v in (F(10 ** 400), F(1, 10 ** 400)):
            for nombre, datos in (("A", ([[v]], [0], [0])),
                                  ("b", ([[1]], [v], [0])),
                                  ("x0", ([[1]], [0], [v]))):
                with self.subTest(nombre=nombre, valor=v):
                    with self.assertRaisesRegex(ValueError, nombre + ", fila 1, columna 1.*magnitud"):
                        sistema_float(*leer_sistema(*datos))
