"""Aceptación independiente del módulo 11 por la API HTTP contra `referencias_iterativos.json`.

Las comprobaciones usan Fraction y valores de referencia generados con SymPy; no importan el motor bajo prueba.
"""
import json
import os
import unittest
from fractions import Fraction
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src.ui.web_server import servidor_local
from tests.validacion.banco_iterativos import CASOS

with open(os.path.join(os.path.dirname(__file__), "validacion", "referencias_iterativos.json"), encoding="utf-8") as fh:
    REF = json.load(fh)
METODOS = ("jacobi", "gauss_seidel")
# Valores de la presentación recalculados por el propietario (iteraciones 1 y 2, seis decimales).
TABLA_PROPIETARIO = {
    "jacobi": [[0.600000, 2.272727, -1.100000, 1.875000], [1.047273, 1.715909, -0.805227, 0.885227]],
    "gauss_seidel": [[0.600000, 2.327273, -0.987273, 0.878864], [1.030182, 2.036938, -1.014456, 0.984341]],
}


def post(url, ruta, cuerpo):
    req = Request(url + ruta, json.dumps(cuerpo).encode(), {"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=120) as r:
            return json.load(r)
    except HTTPError as exc:
        return {"http": exc.code, **json.load(exc)}


class TestValidacionIterativos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._ctx = servidor_local()
        cls.url = cls._ctx.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls._ctx.__exit__(None, None, None)

    def resolver(self, clave, metodo, **extra):
        c = CASOS[clave]
        cuerpo = {"A": c["A"], "b": c["b"], "metodo": metodo, "tolerancia": 1e-10, "max_iteraciones": 3000, **extra}
        if "x0" in c:
            cuerpo["x0"] = c["x0"]
        return post(self.url, "/api/iterativos/resolver", cuerpo)

    def test_tabla_de_la_presentacion(self):
        for metodo in METODOS:
            r = self.resolver("principal", metodo)
            for k, fila in enumerate(TABLA_PROPIETARIO[metodo]):
                for got, esperado in zip(r["iteraciones"][k]["x"], fila):
                    self.assertAlmostEqual(got, esperado, delta=5e-7, msg=f"{metodo} k={k + 1}")

    def test_iteraciones_exactas_y_convergencia_honesta(self):
        for clave, ref in REF.items():
            if ref["diagonal_nula"] or ref["rango_A"] < len(CASOS[clave]["b"]):
                continue
            for metodo in METODOS:
                with self.subTest(f"{clave} {metodo}"):
                    r = self.resolver(clave, metodo)
                    exactas = ref["iteraciones_" + metodo]
                    if len(r["iteraciones"]) < len(exactas):  # solo un ciclo o algo no finito justifica parar antes
                        self.assertIn(r["motivo"], ("oscilacion", "no_finito", "tolerancia"))
                    for k, esperado in enumerate(exactas[:len(r["iteraciones"])]):
                        for got, exacto in zip(r["iteraciones"][k]["x"], esperado):
                            self.assertAlmostEqual(got, float(Fraction(exacto)),
                                                   delta=1e-12 * max(1, abs(float(Fraction(exacto)))))
                    rho = float(ref["radio_espectral"][metodo])
                    if rho >= 1:
                        self.assertFalse(r["convergio"], f"ρ = {rho}: no puede declarar convergencia")
                    elif rho < 0.6:
                        self.assertTrue(r["convergio"], r.get("mensaje"))
                        self.assertEqual(r["convergencia"], "demostrada")
                    if r["convergio"]:
                        sol = [float(Fraction(v)) for v in ref["solucion"]]
                        escala = max(1, max(abs(v) for v in sol))
                        for got, exacto in zip(r["solucion"], sol):
                            self.assertAlmostEqual(got, exacto, delta=1e-7 * escala)
                        self._verificar_residuo(clave, r)

    def _verificar_residuo(self, clave, r):
        A = [[Fraction(v) for v in fila] for fila in CASOS[clave]["A"]]
        b = [Fraction(v) for v in CASOS[clave]["b"]]
        x = [Fraction(v) for v in r["solucion"]]
        residuo = max(abs(bi - sum(a * xi for a, xi in zip(fila, x))) for fila, bi in zip(A, b))
        self.assertAlmostEqual(float(residuo), r["verificacion"]["residuo_inf"], delta=1e-9)

    def test_casos_que_no_deben_iterar(self):
        # [[0,1],[0,1]] tiene rango 1: «singular» precede a la diagonal nula, que se informa en el análisis.
        esperados = {"diagonal_nula_sin_arreglo": "singular", "singular_infinitas": "singular",
                     "singular_incompatible": "incompatible", "diagonal_nula_reordenable": "diagonal_nula"}
        for clave, motivo in esperados.items():
            with self.subTest(clave):
                r = self.resolver(clave, "jacobi")
                self.assertFalse(r.get("convergio", False))
                self.assertEqual(r.get("motivo"), motivo, r)

    def test_reordenar_resuelve_la_diagonal_nula(self):
        for metodo in METODOS:
            r = self.resolver("diagonal_nula_reordenable", metodo, reordenar=True)
            self.assertTrue(r["analisis"]["reordenamiento"]["aplicado"])
            self.assertTrue(r["convergio"], r.get("mensaje"))
            for got in r["solucion"]:
                self.assertAlmostEqual(got, 1.0, delta=1e-8)

    def test_texto_de_la_presentacion_llega_a_la_misma_matriz(self):
        textos = {"principal": "10x₁ − x₂ + 2x₃ = 6\n−x₁ + 11x₂ − x₃ + 3x₄ = 25\n2x₁ − x₂ + 10x₃ − x₄ = −11\n"
                               "3x₂ − x₃ + 8x₄ = 15",
                  "practica": "8x1 - x2 + x3 = 8\n-x1 + 10x2 - 2x3 + x4 = 7\nx1 - 2x2 + 9x3 - x4 = -4\n"
                              "x2 - x3 + 7x4 = 5"}
        for clave, texto in textos.items():
            with self.subTest(clave):
                r = post(self.url, "/api/iterativos/texto", {"texto": texto})
                self.assertEqual([[Fraction(v) for v in fila] for fila in r["A"]],
                                 [[Fraction(v) for v in fila] for fila in CASOS[clave]["A"]])
                self.assertEqual([Fraction(v) for v in r["b"]], [Fraction(v) for v in CASOS[clave]["b"]])
        self.assertIn("error", post(self.url, "/api/iterativos/texto", {"texto": "x1*x2 = 1\nx1 + x2 = 2"}))

    def test_comparar_devuelve_ambos_metodos(self):
        c = CASOS["practica"]
        r = post(self.url, "/api/iterativos/comparar", {"A": c["A"], "b": c["b"], "tolerancia": 1e-8})
        for metodo in METODOS:
            self.assertTrue(r[metodo]["convergio"])
            self.assertEqual(r[metodo]["metodo"], metodo)


if __name__ == "__main__":
    unittest.main()
