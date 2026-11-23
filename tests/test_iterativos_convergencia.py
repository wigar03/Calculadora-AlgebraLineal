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


class CriteriosParada(unittest.TestCase):
    def test_cambio_y_residuo_escalado_siempre_obligatorio(self):
        self.assertEqual(medir_cambio([1, -1], [2, -3]), (2, 2 / 3))
        self.assertEqual(medir_cambio([0, 0], [0, 0]), (0, 0))
        for criterio in ("cambio", "residuo", "ambos"):
            self.assertFalse(cumple_tolerancia(0, 1, 1e-6, criterio))
            self.assertFalse(cumple_tolerancia(float("nan"), 0, 1e-6, criterio))
            self.assertTrue(cumple_tolerancia(1e-8, 1e-8, 1e-6, criterio))
        self.assertTrue(cumple_tolerancia(1, 0, 1e-6, "residuo"))
        self.assertFalse(cumple_tolerancia(1, 0, 1e-6, "ambos"))

    def test_diagnosticos_de_parada(self):
        fila = {"cambio_inf": 1, "residuo_inf": 1}
        self.assertEqual(detectar_parada([fila], [[0], [float("inf")]]), "no_finito")
        self.assertEqual(detectar_parada([fila], [[1], [1]]), "estancamiento")
        self.assertEqual(detectar_parada([fila] * 2, [[0], [1], [0]]), "oscilacion")
        crecimiento = [{"cambio_inf": 2 ** k, "residuo_inf": 3 ** k} for k in range(7)]
        self.assertEqual(detectar_parada(crecimiento, [[k] for k in range(8)]), "divergencia")
        self.assertEqual(detectar_parada([fila] * 8, [[k] for k in range(9)]), "estancamiento")
        decrece = [{"cambio_inf": 2 ** -k, "residuo_inf": 3 ** -k} for k in range(8)]
        self.assertIsNone(detectar_parada(decrece, [[k] for k in range(9)]))


class ResolucionIterativa(unittest.TestCase):
    def resolver(self, nombre, metodo="gauss_seidel", **opciones):
        from src.iterativos.resolver import resolver_iterativo
        return resolver_iterativo(**CASOS[nombre], metodo=metodo, **opciones)

    def test_convergentes_solucion_y_residuo_independiente(self):
        nombres = ("principal", "principal_x0_unos", "practica", "dd_2x2",
                   "decimales_3x3", "fracciones_3x3", "tridiagonal_5x5", "dd_10x10")
        for nombre in nombres:
            for metodo in ("jacobi", "gauss_seidel"):
                with self.subTest(caso=nombre, metodo=metodo):
                    r = self.resolver(nombre, metodo, tolerancia=1e-12, max_iteraciones=1000)
                    self.assertTrue(r["convergio"], r["mensaje"])
                    self.assertEqual(r["motivo"], "tolerancia")
                    self.assertEqual(r["convergencia"], "demostrada")
                    self.assertTrue(r["verificacion"]["cumple"])
                    self.assertLessEqual(r["verificacion"]["residuo_rel"], 1e-12)
                    for x, esperado in zip(r["solucion"], REF[nombre]["solucion"]):
                        self.assertAlmostEqual(x, float(F(esperado)), delta=1e-10)
                    A, b = matriz(nombre), list(map(F, CASOS[nombre]["b"]))
                    residual = [b[i] - sum(a * F(x) for a, x in zip(fila, r["solucion"]))
                                for i, fila in enumerate(A)]
                    escala = max(map(abs, b)) + max(sum(map(abs, f)) for f in A) * max(
                        abs(F(x)) for x in r["solucion"])
                    self.assertLessEqual(float(max(map(abs, residual)) / escala), 1.01e-12)
                    for fila in r["iteraciones"]:
                        self.assertEqual("detalle" in fila, fila["k"] <= 3)

    def test_divergencia_y_contraejemplo(self):
        for nombre, metodo in (("diverge_ambos", "jacobi"),
                               ("diverge_ambos", "gauss_seidel"),
                               ("jacobi_si_gs_no", "gauss_seidel")):
            r = self.resolver(nombre, metodo)
            self.assertFalse(r["convergio"])
            self.assertEqual(r["motivo"], "divergencia")
            self.assertEqual(r["convergencia"], "no_asegurada")
        j = self.resolver("jacobi_si_gs_no", "jacobi", tolerancia=1e-12)
        self.assertTrue(j["convergio"])
        self.assertEqual(j["convergencia"], "demostrada")
        self.assertEqual(j["solucion"], [1, 1, 1])

    def test_spd_oscilacion_y_hilbert_lento(self):
        j = self.resolver("spd_no_dominante", "jacobi")
        self.assertEqual(j["motivo"], "oscilacion")
        self.assertEqual(j["convergencia"], "no_asegurada")
        gs = self.resolver("spd_no_dominante", tolerancia=1e-12)
        self.assertTrue(gs["convergio"])
        self.assertEqual(gs["convergencia"], "demostrada")
        h = self.resolver("hilbert_4x4", tolerancia=1e-12)
        self.assertFalse(h["convergio"])
        self.assertEqual(h["motivo"], "max_iteraciones")
        self.assertEqual(h["convergencia"], "demostrada")

    def test_se_rechazan_antes_de_iterar(self):
        for nombre, motivo in (("singular_infinitas", "singular"),
                               ("singular_incompatible", "incompatible"),
                               ("diagonal_nula_reordenable", "diagonal_nula")):
            r = self.resolver(nombre)
            self.assertFalse(r["convergio"])
            self.assertEqual(r["motivo"], motivo)
            self.assertEqual(r["iteraciones"], [])

    def test_reordenamiento_informado_y_solucion(self):
        for nombre in ("reordenable", "diagonal_nula_reordenable"):
            r = self.resolver(nombre, reordenar=True, tolerancia=1e-12)
            self.assertTrue(r["convergio"])
            self.assertTrue(r["analisis"]["reordenamiento"]["aplicado"])
            self.assertEqual(r["analisis"]["reordenamiento"]["permutacion"], [1, 0, 2])
            for x in r["solucion"]:
                self.assertAlmostEqual(x, 1, delta=1e-10)
