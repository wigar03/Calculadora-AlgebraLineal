"""Contrato JSON por HTTP real, con referencias ajenas al código bajo prueba."""
import json
import unittest
from fractions import Fraction as F
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src.ui.web_server import servidor_local
from tests.validacion.banco_iterativos import CASOS

REF = json.loads((Path(__file__).parent / "validacion" /
                  "referencias_iterativos.json").read_text(encoding="utf-8"))
CLAVES_R = {"metodo", "n", "nombres", "A", "b", "x0", "tolerancia", "criterio",
    "max_iteraciones", "iteraciones", "solucion", "convergio", "motivo", "mensaje",
    "verificacion", "analisis", "convergencia"}
CLAVES_ANALISIS = {"diagonal_nula", "dominancia", "reordenamiento", "rango", "singular",
                   "radio_espectral", "garantia", "razones"}


class APIIterativos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = cls.enterClassContext(servidor_local())

    def post(self, ruta, datos, estado=200):
        peticion = Request(self.url + "/api/iterativos/" + ruta,
                           data=json.dumps(datos).encode("utf-8"),
                           headers={"Content-Type": "application/json"})
        try:
            respuesta = urlopen(peticion, timeout=20)
        except HTTPError as exc:
            respuesta = exc
        with respuesta:
            self.assertEqual(respuesta.status, estado)
            texto = respuesta.read().decode("utf-8")
            self.assertNotIn("NaN", texto)
            self.assertNotIn("Infinity", texto)
            return json.loads(texto)

    def comprobar_forma(self, r):
        self.assertEqual(set(r), CLAVES_R)
        self.assertEqual(set(r["analisis"]), CLAVES_ANALISIS)
        self.assertEqual(set(r["verificacion"]),
                         {"Ax", "residuo", "residuo_inf", "residuo_rel", "cumple"})
        self.assertIsInstance(r["convergio"], bool)
        self.assertIsInstance(r["mensaje"], str)
        for fila in r["iteraciones"]:
            claves = {"k", "x", "cambio_inf", "cambio_rel", "residuo_inf", "residuo_rel"}
            self.assertEqual(set(fila), claves | ({"detalle"} if fila["k"] <= 3 else set()))

    def test_resolver_ambos_metodos_por_http(self):
        for metodo in ("jacobi", "gauss_seidel"):
            r = self.post("resolver", {**CASOS["principal"], "metodo": metodo,
                                      "tolerancia": 1e-12})
            self.comprobar_forma(r)
            self.assertTrue(r["convergio"])
            self.assertEqual(r["nombres"], ["x_1", "x_2", "x_3", "x_4"])
            for x, esperado in zip(r["solucion"], REF["principal"]["solucion"]):
                self.assertAlmostEqual(x, float(F(esperado)), delta=1e-10)

    def test_comparar_no_confunde_los_esquemas(self):
        r = self.post("comparar", CASOS["jacobi_si_gs_no"])
        self.assertEqual(set(r), {"jacobi", "gauss_seidel", "resumen"})
        self.comprobar_forma(r["jacobi"])
        self.comprobar_forma(r["gauss_seidel"])
        self.assertTrue(r["jacobi"]["convergio"])
        self.assertEqual(r["gauss_seidel"]["motivo"], "divergencia")
        self.assertEqual(r["jacobi"]["analisis"]["radio_espectral"]["jacobi"], 0)
