"""Aceptación por HTTP de las Partes V-VII del banco final (ejercicios 50-64) contra referencias SymPy."""
import json
import unittest
from fractions import Fraction
from pathlib import Path
from urllib.request import Request, urlopen

from src.ui.web_server import servidor_local
from tests.validacion.banco_final import CONJUNTOS, EXPRESIONES, MATRICES, SISTEMAS_RECTANGULARES
from tests.validacion.parametricas import evaluar_lineal

REF = json.loads((Path(__file__).parent / "validacion" / "referencias_final.json").read_text(encoding="utf-8"))
def S(matriz):
    return [[str(x) for x in fila] for fila in matriz]


class TestBancoFinal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._ctx = servidor_local()
        cls.url = cls._ctx.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls._ctx.__exit__(None, None, None)

    def post(self, ruta, cuerpo):
        req = Request(self.url + ruta, data=json.dumps(cuerpo).encode(), headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=60) as r:
            self.assertEqual(r.status, 200)
            return json.load(r)

    def test_parte_v_sistemas_rectangulares(self):
        for clave, d in SISTEMAS_RECTANGULARES.items():
            with self.subTest(clave):
                ref = REF["sistemas"][clave]
                r = self.post("/api/ecuaciones/resolver", {"A": S(d["A"]), "b": [str(x) for x in d["b"]]})
                self.assertEqual((r["tipo_sistema"], r["rango_A"], r["rango_aumentada"]),
                                 (ref["tipo"], ref["rango_A"], ref["rango_aumentada"]))
                self.assertEqual(len(r["parametros"]), ref["libres"])
                for valores in ({p: Fraction(0) for p in r["parametros"]},
                                {p: Fraction(i + 3, 2) for i, p in enumerate(r["parametros"])}):
                    if ref["tipo"] == "SI":
                        break
                    x = [evaluar_lineal(r["solucion_dict"][f"x_{j + 1}"], valores) for j in range(len(d["A"][0]))]
                    self.assertEqual([sum(Fraction(a) * xi for a, xi in zip(f, x)) for f in d["A"]],
                                     [Fraction(v) for v in d["b"]])

    def test_parte_vi_expresiones_encadenando_operaciones(self):
        for clave, exprs in EXPRESIONES.items():
            for nombre, terminos in exprs.items():
                with self.subTest(clave, expresion=nombre):
                    acumulado = None
                    for coef, m in terminos:
                        actual = S(MATRICES[clave][m])
                        if abs(coef) != 1:
                            actual = self.post("/api/matrices/operar", {"operacion": "escalar_a", "A": actual,
                                                                        "k": str(abs(coef))})["matriz_resultado"]
                        if acumulado is None:
                            acumulado = actual if coef > 0 else self.post("/api/matrices/operar", {
                                "operacion": "escalar_a", "A": actual, "k": "-1"})["matriz_resultado"]
                        else:
                            op = "suma" if coef > 0 else "resta"
                            acumulado = self.post("/api/matrices/operar", {"operacion": op, "A": acumulado,
                                                                           "B": actual})["matriz_resultado"]
                    self.assertEqual(acumulado, REF["matrices"][clave][nombre])

    def test_parte_vii_independencia_con_b_cero(self):
        for clave, vectores in CONJUNTOS.items():
            with self.subTest(clave):
                ref = REF["independencia"][clave]
                r = self.post("/api/vectores/combinacion", {"vectores": S(vectores), "b": ["0"] * len(vectores[0])})
                self.assertEqual(r["tipo_solucion"], "UNICA" if ref["independiente"] else "INFINITAS")
                c = [evaluar_lineal(r["escalares"][f"c_{i + 1}"], {"t": Fraction(1)}) for i in range(len(vectores))]
                self.assertTrue(any(c), "la relación debe ser no trivial")
                for fila in range(len(vectores[0])):
                    self.assertEqual(sum(ci * v[fila] for ci, v in zip(c, vectores)), 0)
                nucleo = [Fraction(x) for x in ref["nucleo"][0]]
                k = next(ci / ni for ci, ni in zip(c, nucleo) if ni)
                self.assertEqual(c, [k * ni for ni in nucleo])


if __name__ == "__main__":
    unittest.main()
