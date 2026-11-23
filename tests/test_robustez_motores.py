"""Límites de los motores, independientes de la validación HTTP."""
import unittest
from fractions import Fraction
from unittest.mock import patch

from src.core.arithmetic import parse_number
from src.core.limites import DIGITOS_MAX, EXPONENTE_MAX, LimiteExcedido
from src.core import limites as lim
from src.vectores import operaciones as vec
from src.vectores.combinacion_lineal import evaluar_combinacion_lineal
from src.matrices import operaciones as mat
from src.matrices.inversa import calcular_inversa_matriz
from src.matrices.determinante import calcular_determinante, analizar_eficiencia_determinante
from src.ecuaciones.ecuacion_matricial import resolver_ecuacion_matricial
from src.solver.gauss_solver import solve_gaussian_elimination


def identidad(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


class TestDimensionesDefensivas(unittest.TestCase):
    def test_vectores_sin_servidor(self):
        grande = [1] * (lim.VECTOR_MAX + 1)
        for funcion, args in [(vec.suma_vectores, (grande, grande)),
                              (vec.resta_vectores, (grande, grande)),
                              (vec.producto_punto, (grande, grande)),
                              (vec.multiplicar_escalar_vector, (2, grande)),
                              (vec.norma_cuadrada, (grande,))]:
            with self.subTest(funcion=funcion.__name__), self.assertRaises(LimiteExcedido):
                funcion(*args)

    def test_matrices_antes_de_convertir_celdas(self):
        for grande in ([[1] * (lim.MATRIZ_OPERAR_MAX + 1)], [[1]] * (lim.MATRIZ_OPERAR_MAX + 1)):
            for funcion, args in [(mat.suma_matrices, (grande, grande)),
                                  (mat.resta_matrices, (grande, grande)),
                                  (mat.multiplicar_matrices, (grande, grande)),
                                  (mat.multiplicar_escalar_matriz, (2, grande)),
                                  (mat.transpuesta_matriz, (grande,)),
                                  (mat.analizar_transpuesta_matriz, (grande,))]:
                with self.subTest(funcion=funcion.__name__):
                    with patch("src.core.arithmetic.parse_number", side_effect=AssertionError("conversión prematura")):
                        with self.assertRaises(LimiteExcedido):
                            funcion(*args)

    def test_combinacion_sus_dos_limites(self):
        casos = [([[1]] * (lim.COMBINACION_K_MAX + 1), [1]),
                 ([[1] * (lim.COMBINACION_N_MAX + 1)], [1] * (lim.COMBINACION_N_MAX + 1))]
        for vectores, b in casos:
            with self.subTest(n=len(b), k=len(vectores)):
                with self.assertRaises(LimiteExcedido):
                    evaluar_combinacion_lineal(vectores, b)
                with self.assertRaises(LimiteExcedido):
                    vec.combinacion_lineal_directa([1] * len(vectores), vectores)

    def test_limites_de_motores_costosos(self):
        for funcion, args in [(calcular_inversa_matriz, (identidad(lim.INVERSA_MAX + 1),)),
                              (calcular_determinante, (identidad(lim.DETERMINANTE_MAX + 1),)),
                              (analizar_eficiencia_determinante, (lim.EFICIENCIA_N_MAX + 1,)),
                              (resolver_ecuacion_matricial, (identidad(lim.SISTEMA_MAX + 1), [1] * (lim.SISTEMA_MAX + 1))),
                              (solve_gaussian_elimination, ([[1, 1]] * (lim.SISTEMA_MAX + 1),)),
                              (solve_gaussian_elimination, ([[1] * (lim.SISTEMA_MAX + 2)],))]:
            with self.subTest(funcion=funcion.__name__), self.assertRaises(LimiteExcedido):
                funcion(*args)

    def test_combinacion_admite_quince_componentes_y_diez_vectores(self):
        vectores = [fila[:lim.COMBINACION_N_MAX] for fila in identidad(lim.COMBINACION_N_MAX)[:lim.COMBINACION_K_MAX]]
        self.assertTrue(evaluar_combinacion_lineal(vectores, vectores[0]).es_combinacion)


class TestNumerosAcotados(unittest.TestCase):
    def test_limites_antes_de_construir_fraction(self):
        entradas = ["1e5000000", "1e-5000000", "9" * (DIGITOS_MAX + 1),
                    "1/" + "9" * (DIGITOS_MAX + 1), 10 ** DIGITOS_MAX,
                    "1e" + "9" * 5000, "0." + "1" * (DIGITOS_MAX + 1)]
        for entrada in entradas:
            with self.subTest(entrada=str(entrada)[:80]):
                class NoConstruir(Fraction):
                    def __new__(cls, *args):
                        raise AssertionError("Se construyó Fraction antes de validar")
                with patch("src.core.arithmetic.Fraction", NoConstruir):
                    with self.assertRaises(LimiteExcedido):
                        parse_number(entrada)

    def test_fronteras_y_sintaxis_existente(self):
        for texto in ("9" * DIGITOS_MAX, "-3/7", "1.25", "1_000/2_000", "", " 2 / 3 "):
            with self.subTest(texto=texto):
                self.assertEqual(parse_number(texto), Fraction(texto.strip() or "0"))
        self.assertEqual(parse_number(f"1e{EXPONENTE_MAX}"), Fraction(10 ** EXPONENTE_MAX))
        self.assertEqual(parse_number(f"1e-{EXPONENTE_MAX}"), Fraction(1, 10 ** EXPONENTE_MAX))

    def test_denominador_cero_es_valueerror_en_espanol(self):
        with self.assertRaisesRegex(ValueError, "denominador.*cero"):
            parse_number("2/0")


if __name__ == "__main__":
    unittest.main()
