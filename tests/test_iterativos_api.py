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

    def test_analizar_devuelve_solo_analisis_y_garantia_del_metodo(self):
        for metodo, garantia in (("jacobi", "no_asegurada"), ("gauss_seidel", "demostrada")):
            r = self.post("analizar", {**CASOS["spd_no_dominante"], "metodo": metodo})
            self.assertEqual(set(r), CLAVES_ANALISIS)
            self.assertEqual(r["garantia"], garantia)
            self.assertFalse(r["dominancia"]["estricta"])
            self.assertEqual(r["rango"], {"A": 3, "aumentada": 3})
            self.assertAlmostEqual(r["radio_espectral"]["gauss_seidel"], 0.353553390593, places=8)
        r = self.post("analizar", CASOS["diagonal_nula_reordenable"])
        self.assertEqual(r["diagonal_nula"], [0])
        self.assertIsNone(r["radio_espectral"]["jacobi"])

    def test_todo_el_banco_por_la_via_del_usuario(self):
        for nombre, caso in CASOS.items():
            for metodo in ("jacobi", "gauss_seidel"):
                with self.subTest(caso=nombre, metodo=metodo):
                    r = self.post("resolver", {**caso, "metodo": metodo, "tolerancia": 1e-9})
                    self.comprobar_forma(r)
                    ref = REF[nombre]
                    self.assertEqual(r["analisis"]["rango"],
                                     {"A": ref["rango_A"], "aumentada": ref["rango_aumentada"]})
                    self.assertEqual(r["analisis"]["diagonal_nula"], ref["diagonal_nula"])
                    if "radio_espectral" in ref:
                        for m, radio in ref["radio_espectral"].items():
                            self.assertAlmostEqual(r["analisis"]["radio_espectral"][m],
                                                   float(radio), places=8)
                    if r["convergio"]:
                        self.assertEqual(r["motivo"], "tolerancia")
                        self.assertLessEqual(r["verificacion"]["residuo_rel"], 1e-9)
                        for x, esperado in zip(r["solucion"], ref["solucion"]):
                            self.assertAlmostEqual(x, float(F(esperado)), delta=1e-6)
                    for fila, esperado in zip(r["iteraciones"], ref.get("iteraciones_" + metodo, [])):
                        for x, exacto in zip(fila["x"], esperado):
                            valor = float(F(exacto))
                            self.assertAlmostEqual(x, valor, delta=max(1, abs(valor)) * 1e-13)

    def test_reordenar_ecuaciones_por_http(self):
        r = self.post("resolver", {**CASOS["diagonal_nula_reordenable"],
                      "metodo": "gauss_seidel", "reordenar": True, "tolerancia": 1e-12})
        self.assertTrue(r["convergio"])
        self.assertEqual(r["analisis"]["reordenamiento"]["permutacion"], [1, 0, 2])
        self.assertTrue(r["verificacion"]["cumple"])

    def test_errores_400_y_no_finitos_sin_nan_en_json(self):
        for ruta in ("resolver", "comparar", "analizar"):
            for datos in ([], {}, {"A": [[1, 2]], "b": [1]}):
                with self.subTest(ruta=ruta, datos=datos):
                    r = self.post(ruta, datos, estado=400)
                    self.assertIsInstance(r["error"], str)
        for opciones in ({"metodo": "otro"}, {"tolerancia": "nan"},
                         {"max_iteraciones": 10001}, {"criterio": "otro"}):
            r = self.post("resolver", {**CASOS["principal"],
                          "metodo": "gauss_seidel", **opciones}, estado=400)
            self.assertIn("error", r)
        r = self.post("resolver", {"A": [["1e-308"]], "b": ["1e308"], "metodo": "jacobi"})
        self.assertEqual(r["motivo"], "no_finito")
        self.assertFalse(r["convergio"])
