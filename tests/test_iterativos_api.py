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

    def test_cuerpo_real_del_editor_con_opciones_en_texto(self):
        # iterativos.js: celdas y controles .value son texto; .checked es bool.
        for ruta in ("resolver", "comparar", "analizar"):
            for tolerancia in ("1e-6", "0.000001"):
                for metodo in ("jacobi", "gauss_seidel"):
                    cuerpo = {"A": [["4", "1"], ["2", "3"]], "b": ["1", "2"],
                              "x0": ["0", "0"], "metodo": metodo,
                              "tolerancia": tolerancia, "max_iteraciones": "100",
                              "criterio": "ambos", "reordenar": False}
                    with self.subTest(ruta=ruta, tol=tolerancia, metodo=metodo):
                        r = self.post(ruta, cuerpo)
                        if ruta == "analizar":
                            self.assertEqual(set(r), CLAVES_ANALISIS)
                            self.assertEqual(r["rango"], {"A": 2, "aumentada": 2})
                            continue
                        resultados = [r] if ruta == "resolver" else [r["jacobi"], r["gauss_seidel"]]
                        for solucion in resultados:
                            self.comprobar_forma(solucion)
                            self.assertTrue(solucion["convergio"])
                            self.assertIs(type(solucion["max_iteraciones"]), int)
                            self.assertEqual(solucion["max_iteraciones"], 100)
                            self.assertEqual(solucion["tolerancia"], 1e-6)
                            for valor, esperado in zip(solucion["solucion"], (0.1, 0.6)):
                                self.assertAlmostEqual(valor, esperado, delta=1e-6)

    def test_reordenar_como_texto_en_todas_las_rutas(self):
        for ruta in ("resolver", "comparar", "analizar"):
            for reordenar in ("false", "true"):
                cuerpo = {"A": [["2", "3"], ["4", "1"]], "b": ["2", "1"],
                          "x0": ["0", "0"], "metodo": "gauss_seidel",
                          "tolerancia": "1e-6", "max_iteraciones": "100",
                          "criterio": "ambos", "reordenar": reordenar}
                with self.subTest(ruta=ruta, reordenar=reordenar):
                    r = self.post(ruta, cuerpo)
                    resultados = [r] if ruta != "comparar" else [r["jacobi"], r["gauss_seidel"]]
                    for resultado in resultados:
                        analisis = resultado if ruta == "analizar" else resultado["analisis"]
                        self.assertEqual(analisis["reordenamiento"]["aplicado"], reordenar == "true")
                        self.assertEqual(analisis["reordenamiento"]["permutacion"],
                                         [1, 0] if reordenar == "true" else [0, 1])
                        if ruta != "analizar":
                            self.assertEqual(resultado["convergio"], reordenar == "true")

    def test_enteros_decimales_en_texto_y_limites_validos(self):
        for ruta in ("resolver", "comparar"):
            for maximo in ("1", "100", " 100 ", "000100", "10000"):
                with self.subTest(ruta=ruta, maximo=maximo):
                    r = self.post(ruta, {"A": [["4", "1"], ["2", "3"]],
                        "b": ["1", "2"], "x0": ["0", "0"], "metodo": "jacobi",
                        "tolerancia": "1e-6", "max_iteraciones": maximo,
                        "criterio": "ambos", "reordenar": "false"})
                    resultados = [r] if ruta == "resolver" else [r["jacobi"], r["gauss_seidel"]]
                    for resultado in resultados:
                        self.assertEqual(resultado["max_iteraciones"], int(maximo))
                        self.assertLessEqual(len(resultado["iteraciones"]), int(maximo))

    def test_opciones_de_texto_invalidas_indican_como_corregir(self):
        invalidas = [("max_iteraciones", v, "entero decimal entre 1 y 10000")
                     for v in ("abc", "10.5", "1e2", "0", "-1", "10001", "", 0, -1, 10001, True)]
        invalidas += [("tolerancia", v, "número positivo finito")
                      for v in ("abc", "nan", "inf", "0", "-1", "1e-400", 0, -1)]
        for ruta in ("resolver", "comparar"):
            for campo, valor, mensaje in invalidas:
                with self.subTest(ruta=ruta, campo=campo, valor=valor):
                    r = self.post(ruta, {"A": [["4", "1"], ["2", "3"]],
                        "b": ["1", "2"], "x0": ["0", "0"], "metodo": "jacobi",
                        "tolerancia": "1e-6", "max_iteraciones": "100",
                        "criterio": "ambos", "reordenar": "false", campo: valor}, estado=400)
                    self.assertIn(mensaje, r["error"])
        for ruta in ("resolver", "comparar", "analizar"):
            r = self.post(ruta, {"A": [["1"]], "b": ["1"], "x0": ["0"],
                          "metodo": "jacobi", "reordenar": "abc"}, estado=400)
            self.assertIn("verdadero o falso", r["error"])

    def test_regresiones_adversarias_con_controles_html_por_http(self):
        casos = []
        for n, factor in ((9, 1), (20, 100)):
            A = [[str(int(i == j) - factor * int(j == i + 1)) for j in range(n)]
                 for i in range(n)]
            casos.append((A, [str(1 - factor)] * (n - 1) + ["1"], ["0"] * n, n + 1))
        casos.append(([["1e308"]], ["1e308"], ["1"], 1))
        for A, b, x0, pasos in casos:
            cuerpo = {"A": A, "b": b, "x0": x0, "tolerancia": "1e-16",
                      "max_iteraciones": "100", "criterio": "ambos", "reordenar": "false"}
            for metodo in ("jacobi", "gauss_seidel"):
                with self.subTest(n=len(b), metodo=metodo):
                    r = self.post("resolver", {**cuerpo, "metodo": metodo})
                    self.assertTrue(r["convergio"])
                    self.assertEqual(r["motivo"], "tolerancia")
                    self.assertEqual(r["solucion"], [1] * len(b))
                    self.assertEqual(len(r["iteraciones"]), pasos)
                    self.assertEqual(r["verificacion"]["residuo_rel"], 0)
            comparacion = self.post("comparar", cuerpo)
            for metodo in ("jacobi", "gauss_seidel"):
                self.assertTrue(comparacion[metodo]["convergio"])
                self.assertEqual(comparacion[metodo]["convergencia"], "demostrada")
            analisis = self.post("analizar", cuerpo)
            self.assertEqual(analisis["garantia"], "demostrada")
            self.assertEqual(analisis["radio_espectral"]["jacobi"], 0)
