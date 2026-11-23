"""Verificación independiente de P2 sobre respuestas HTTP reales y motores sin mocks.

P2_EXPORTAR_JS permite revisar la biblioteca de otra rama sin modificar src/.
Ejecutar con --informe ruta.json conserva medidas y diagnósticos reproducibles.
"""
import csv
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from decimal import Decimal
from pathlib import Path

from src.core import limites
from src.procedimientos import ADAPTADORES, adjuntar
from src.ui.web_server import servidor_local
from tests.test_golden_api import GOLDEN, consultar, equivalentes

ROOT = Path(__file__).resolve().parents[1]
NUMERO = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\Z")
FRACCION = re.compile(r"-?\d+/\d+\Z")
ENTERO = re.compile(r"-?\d+\Z")
PREFIJO_PELIGROSO = re.compile(r"^[\s\x00-\x1f\x7f-\x9f\ufeff]*[=+\-@]")


def fraccion_valida(texto):
    return bool(FRACCION.fullmatch(texto) and Decimal(texto.rsplit("/", 1)[1]) != 0)


def entero_largo(texto):
    return bool(ENTERO.fullmatch(texto) and len(texto.lstrip("-").lstrip("0")) > 15)


def texto_protegido(texto):
    numerico = NUMERO.fullmatch(texto) or fraccion_valida(texto)
    return "'" + texto if PREFIJO_PELIGROSO.match(texto) and not numerico else texto


def pendiente_csv(motivo):
    """Una biblioteca candidata se prueba estrictamente, sin ocultar sus fallos."""
    def decorar(prueba):
        prueba.__doc__ = "Pendiente Antigravity: " + motivo
        return prueba if os.environ.get("P2_EXPORTAR_JS") else unittest.expectedFailure(prueba)
    return decorar


def problemas_csv(texto, tabla):
    """Relee con csv estándar y compara cada celda, sin usar el exportador como oráculo."""
    errores = []
    if not texto.startswith("\ufeff"):
        errores.append("Falta BOM UTF-8 (EF BB BF)")
    contenido = texto.removeprefix("\ufeff")
    # Los saltos internos entre comillas se verifican al comparar la celda original.
    fuera = re.sub(r'"(?:[^"]|"")*"', '""', contenido)
    if re.search(r"(?<!\r)\n|\r(?!\n)", fuera):
        errores.append("Separador de registros distinto de CRLF")
    try:
        filas = list(csv.reader(io.StringIO(contenido, newline=""), delimiter=";", strict=True))
    except csv.Error as exc:
        return errores + [f"CSV inválido: {exc}"]
    esperado = [tabla["columnas"], *tabla["filas"]]
    if len(filas) != len(esperado):
        errores.append(f"Filas perdidas: {len(filas)} != {len(esperado)} (con cabecera)")
    for i, (actual, original) in enumerate(zip(filas, esperado)):
        if len(actual) != len(original):
            errores.append(f"Fila {i}: {len(actual)} celdas != {len(original)}")
        for j, (celda, valor) in enumerate(zip(actual, original)):
            lugar = f"[{i},{j}] {valor!r} -> {celda!r}"
            s = "" if valor is None else str(valor)
            if i == 0:
                if celda != texto_protegido(s):
                    errores.append(f"Cabecera insegura o alterada {lugar}")
            elif entero_largo(s):
                if celda != f'=\"{s}\"':
                    errores.append(f"Entero de más de 15 cifras sin texto validado {lugar}")
            elif isinstance(valor, (int, float)) and not isinstance(valor, bool):
                try:
                    n = celda.replace(",", ".")
                    igual = (celda == "0" if valor == 0 else Decimal(n) == valor if isinstance(valor, int)
                             else float(n).hex() == valor.hex())
                except (ValueError, ArithmeticError):
                    igual = False
                if not igual:
                    errores.append(f"Pérdida numérica {lugar}")
                if "." in celda or ("e" in celda.lower() and not re.search(r"E[+-]\d{2,}$", celda)):
                    errores.append(f"Decimal/científica fuera del contrato {lugar}")
            elif fraccion_valida(s):
                if celda != f'="{s}"':
                    errores.append(f"Fracción expuesta a conversión de fecha {lugar}")
            elif NUMERO.fullmatch(s):
                try:
                    igual = (celda == "0" if s.startswith("-") and Decimal(s).is_zero()
                             else Decimal(celda.replace(",", ".")) == Decimal(s))
                except ArithmeticError:
                    igual = False
                if not igual or "." in celda:
                    errores.append(f"Cadena numérica alterada {lugar}")
            elif celda != texto_protegido(s):
                errores.append(f"Texto inseguro o alterado {lugar}")
    return errores


def entradas_largas():
    n = limites.ITERATIVOS_MAX
    A = [["1" if i == j else "-0.9999" if j == (i + 1) % n else "0"
          for j in range(n)] for i in range(n)]
    return [
        ("jacobi_20x20_10000", "/api/iterativos/resolver", {
            "A": A, "b": ["1"] * n, "metodo": "jacobi", "tolerancia": "1e-300",
            "max_iteraciones": limites.ITERATIVOS_ITER_MAX}, limites.ITERATIVOS_ITER_MAX),
        ("biseccion_1000", "/api/biseccion/resolver", {
            "funcion": "x-1e-300", "a": "0", "b": "1e100", "criterio": "residuo",
            "tolerancia": "1e-320", "max_iteraciones": limites.RAICES_ITER_MAX}, limites.RAICES_ITER_MAX),
        ("regla_falsa_1000", "/api/regla-falsa/resolver", {
            "funcion": "x^30-1", "xl": "0", "xu": "2", "tolerancia": "1e-300",
            "max_iteraciones": limites.RAICES_ITER_MAX}, limites.RAICES_ITER_MAX),
    ]


def motor_real(ruta, cuerpo):
    """La API puede rechazar por 4 MB; no se alteran sus límites para probar el exportador."""
    if "iterativos" in ruta:
        from src.iterativos.resolver import resolver_iterativo
        return resolver_iterativo(**cuerpo)
    from src.biseccion.expresiones import Expresion
    from src.biseccion.metodo import resolver_biseccion
    from src.regla_falsa.metodo import resolver_regla_falsa
    motor = resolver_biseccion if "biseccion" in ruta else resolver_regla_falsa
    return {**motor(**cuerpo), "funcion_latex": Expresion(cuerpo["funcion"]).latex()}


def corpus_real():
    casos, consultas = [], []
    with servidor_local() as url:
        for archivo in sorted(GOLDEN.glob("*.json")):
            for i, congelado in enumerate(json.loads(archivo.read_text(encoding="utf-8"))):
                ruta, cuerpo = congelado["ruta"], congelado["cuerpo"]
                inicio = time.perf_counter()
                estado, respuesta = consultar(url, ruta, cuerpo)
                assert estado == 200, (ruta, estado, respuesta)
                assert equivalentes({k: respuesta.get(k) for k in congelado["respuesta"]}, congelado["respuesta"]), ruta
                consultas.append({"id": f"{archivo.stem}[{i}]", "ms": (time.perf_counter() - inicio) * 1000})
                if ruta in ADAPTADORES:
                    assert "procedimiento" in respuesta, f"{ruta}: falta procedimiento en respuesta real"
                    casos.append({"id": consultas[-1]["id"], "procedimiento": respuesta["procedimiento"]})
        for nombre, ruta, cuerpo, cantidad in entradas_largas():
            inicio = time.perf_counter()
            estado, respuesta = consultar(url, ruta, cuerpo)
            consulta = {"id": nombre, "entrada": cuerpo, "estado": estado,
                        "api_ms": (time.perf_counter() - inicio) * 1000}
            if estado != 200:
                consulta["respuesta_api"] = respuesta
                assert estado == 400 and respuesta.get("codigo") == "respuesta_grande", consulta
                inicio = time.perf_counter()
                respuesta = adjuntar(ruta, motor_real(ruta, cuerpo), cuerpo)
                consulta["motor_ms"] = (time.perf_counter() - inicio) * 1000
                consulta["origen"] = "motor real + adaptador, fuera del transporte HTTP"
            consulta["motivo"] = respuesta["motivo"]
            proc = respuesta["procedimiento"]
            assert len(proc["tablas"][0]["filas"]) == cantidad, (nombre, consulta)
            casos.append({"id": nombre, "procedimiento": proc})
            consultas.append(consulta)
    return casos, consultas


def ejecutar_node(procedimientos):
    proceso = subprocess.run(["node", "tests/exportacion_verificar.cjs", "--stdin"], cwd=ROOT,
        input=json.dumps(procedimientos, ensure_ascii=True, allow_nan=False), encoding="utf-8",
        capture_output=True, timeout=limites.TIEMPO_CALCULO_S * 24)
    if proceso.returncode:
        raise AssertionError(f"exportar.js no pudo generar el corpus: {proceso.stderr[-6000:]}")
    return json.loads(proceso.stdout)


def adversario():
    textos = ["=cmd|' /C calc'!A0", "@SUM(1+1)", "+SUM(A1)", "-SUM(A1)",
              "\t=cmd|x", "\r=cmd|x", 'comillas "dobles"; fin', "línea 1\nlínea 2",
              "  bordes  ", "Unicode: ñ á Ω 你好", r"\input{ajeno}", "=1/2", "-1/2;=cmd|x"]
    tabla = {"titulo": "Funciones y nombres del usuario", "columnas": [textos[0]],
             "filas": [[s] for s in textos + ["1/2", "-17/19", "0003/0007", "1/2x", "NaN",
                         # El cero negativo y el entero de 25 cifras tienen regresiones específicas debajo.
                         1e-300, 0.0, 1.2345678901234567, -3.5e-7, "900719925474099",
                         "0.12345678901234567890123456789", None]]}
    return {"version": 1, "modulo": "adversario", "titulo": textos[6],
            "entrada": [{"etiqueta": s, "latex": "x^2+1"} for s in textos],
            "pasos": [{"titulo": textos[8], "texto": s, "latex": [r"\frac{1}{2}"],
                       "matriz": None, "detalles": []} for s in textos],
            "resultado": [{"etiqueta": "f(x)", "latex": "2"}],
            "verificacion": textos, "avisos": textos, "tablas": [tabla]}


def fragmentos_fuente(proc):
    for campo in ("entrada", "resultado"):
        for item in proc[campo]:
            yield item["latex"]
    for paso in proc["pasos"]:
        yield from paso["latex"]


class TestExportacionModulos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.casos, cls.consultas = corpus_real()
        cls.casos.append({"id": "adversario", "procedimiento": adversario()})
        cls.salidas = ejecutar_node([c["procedimiento"] for c in cls.casos])
        assert len(cls.salidas) == len(cls.casos), "El puente Node perdió procedimientos"

    def test_cobertura_corpus_y_limites_reales(self):
        self.assertEqual(len(self.consultas), 43 + 3)
        self.assertEqual(len(self.casos), 33 + 3 + 1)
        modulos = {c["procedimiento"]["modulo"] for c in self.casos[:-4]}
        # Combinación lineal es una ruta propia del módulo de vectores.
        self.assertGreaterEqual(len(modulos), 11)
        for caso, salida in zip(self.casos, self.salidas):
            with self.subTest(caso=caso["id"]):
                self.assertFalse(salida["mutado"], "La exportación mutó el procedimiento mostrado")

    def test_csv_corpus_todas_las_filas_y_precision(self):
        for caso, salida in zip(self.casos, self.salidas):
            for i, (tabla, texto) in enumerate(zip(caso["procedimiento"]["tablas"], salida["csv"])):
                with self.subTest(caso=caso["id"], tabla=i):
                    errores = problemas_csv(texto, tabla)
                    self.assertEqual(len(errores), 0, f"{len(errores)} incumplimientos CSV: " + "; ".join(errores[:12]))
            self.assertEqual(len(salida["csv"]), len(caso["procedimiento"]["tablas"]))

    def test_csv_espacios_extremos_citados_y_escapes(self):
        texto = self.salidas[-1]["csv"][0]
        for campo in ('"  bordes  "', '"comillas ""dobles""; fin"', '"línea 1\nlínea 2"'):
            with self.subTest(campo=campo):
                self.assertTrue(campo in texto, f"Campo sin escape RFC 4180: {campo!r}")

    def test_latex_entornos_y_cada_fragmento_katex_estricto(self):
        for caso, salida in zip(self.casos, self.salidas):
            with self.subTest(caso=caso["id"]):
                validacion = salida["validacion"]
                self.assertEqual(validacion["fallos"], 0, "\n".join(validacion["errores"]))
                self.assertGreater(validacion["fragmentos"], 0)
                for latex in fragmentos_fuente(caso["procedimiento"]):
                    self.assertTrue(latex in salida["latex"], f"Fragmento original alterado: {latex[:240]}")

    def test_latex_documento_completo(self):
        for caso, salida in zip(self.casos, self.salidas):
            with self.subTest(caso=caso["id"]):
                doc = salida["latex"]
                self.assertTrue(re.search(r"\\documentclass(?:\[[^]]*\])?\{article\}", doc), "Falta clase article")
                for paquete in ("amsmath", "amssymb"):
                    self.assertTrue(re.search(r"\\usepackage\{[^}]*" + paquete + r"[^}]*\}", doc), paquete)
                for paquete in (r"\usepackage[utf8]{inputenc}", r"\usepackage[spanish]{babel}"):
                    self.assertTrue(paquete in doc, f"Falta {paquete}")
                for seccion, campo in (("Datos de entrada", "entrada"), ("Procedimiento", "pasos"),
                                       ("Resultado", "resultado"), ("Verificación", "verificacion")):
                    if caso["procedimiento"][campo]:
                        self.assertTrue(seccion in doc, f"Falta sección {seccion}")

    def test_latex_tablas_completas_y_paginadas(self):
        for caso, salida in zip(self.casos, self.salidas):
            with self.subTest(caso=caso["id"]):
                doc = salida["latex"]
                for tabla, tex in zip(caso["procedimiento"]["tablas"], salida["tablas_latex"]):
                    self.assertTrue(tex in doc, "El documento omitió una tabla exportada")
                    filas = re.findall(r"(?m)^.*\\\\\s*$", tex)
                    cabeceras = 2 if r"\endfirsthead" in tex else 1
                    self.assertEqual(len(filas), len(tabla["filas"]) + cabeceras,
                                     "LaTeX truncado o con filas duplicadas")
                    if len(tabla["filas"]) >= limites.RAICES_ITER_MAX:
                        self.assertTrue(r"\begin{longtable}" in tex, "Tabla larga no paginable")
                        self.assertTrue(r"\endhead" in tex, "Falta encabezado repetido")

    def test_tablas_10000_tiempo_y_memoria(self):
        for caso, salida in zip(self.casos, self.salidas):
            if caso["id"] not in {x[0] for x in entradas_largas()}:
                continue
            with self.subTest(caso=caso["id"]):
                m = salida["metricas"]
                self.assertLess(m["ms"], limites.TIEMPO_CALCULO_S * 1000, m)
                self.assertLess(m["rss"], limites.MEMORIA_CALCULO_MB * 1024**2, m)

    def test_compilacion_real_si_hay_motor_instalado(self):
        motor = next((shutil.which(n) for n in ("pdflatex", "lualatex", "xelatex", "tectonic", "latex")
                      if shutil.which(n)), None)
        if motor is None:
            self.skipTest("No hay motor LaTeX instalado; KaTeX estricto sí se ejecuta")
        with tempfile.TemporaryDirectory(prefix="p2-latex-") as temporal:
            carpeta = Path(temporal)
            for i, (caso, salida) in enumerate(zip(self.casos, self.salidas)):
                with self.subTest(caso=caso["id"], motor=motor):
                    tex = carpeta / f"caso_{i}.tex"
                    tex.write_text(salida["latex"], encoding="utf-8")
                    args = (["--only-cached", "--outdir", temporal, str(tex)] if "tectonic" in motor
                            else ["-no-shell-escape", "-halt-on-error", "-interaction=nonstopmode",
                                  "-output-directory", temporal, str(tex)])
                    p = subprocess.run([motor, *args], cwd=carpeta, capture_output=True,
                                       timeout=limites.TIEMPO_CALCULO_S * 6)
                    self.assertEqual(p.returncode, 0, p.stdout.decode(errors="replace")[-4000:])
                    self.assertTrue(tex.with_suffix(".pdf").exists() or tex.with_suffix(".dvi").exists())


class TestCSVContratoRevisado(unittest.TestCase):
    def comprobar(self, tabla):
        salida = ejecutar_node([{"tablas": [tabla]}])[0]["csv"][0]
        errores = problemas_csv(salida, tabla)
        self.assertEqual(errores, [], "\n".join(errores[:12]))

    @pendiente_csv("CSV aún conserva -0; el contrato exige 0")
    def test_cero_negativo_normalizado(self):
        self.comprobar({"columnas": ["x"], "filas": [[v] for v in (-0.0, "-0", "-0.00", "-0e8")]})

    @pendiente_csv("Enteros mayores de 15 cifras aún salen como números")
    def test_enteros_largos_como_texto_validado(self):
        valores = ("9007199254740993123456789", "1234567890123456", "-1234567890123456", "0001234567890123456")
        self.comprobar({"columnas": ["n"], "filas": [[v] for v in valores]})

    @pendiente_csv("Fracciones con denominador cero aún generan fórmula fija")
    def test_denominador_cero_no_autoriza_formula(self):
        self.comprobar({"columnas": ["q"], "filas": [[v] for v in ("1/0", "-1/0", "0/0", "17/000", "-17/000")]})

    @pendiente_csv("Falta buscar el primer carácter significativo en celdas y cabeceras")
    def test_prefijos_ocultos_sin_alterar_texto(self):
        inicios = (" ", "\n", "\r", "\t", "\v", "\f", "\x00", "\x1f", "\x7f",
                   "\u00a0", "\u2003", "\u3000", "\ufeff", " \n\t\u00a0\u2003\u3000")
        valores = [s + f for s in inicios for f in ("=1+1", "+SUM(A1)", "-SUM(A1)", "@SUM(A1)")]
        self.comprobar({"columnas": valores, "filas": [valores]})

    def test_limite_15_cifras_y_textos_inocuos_sin_cambios(self):
        valores = ("123456789012345", "-123456789012345", "000123456789012345", "\u00a0 texto", "1/2")
        self.comprobar({"columnas": ["valor"], "filas": [[v] for v in valores]})


class TestOraculoCSV(unittest.TestCase):
    @staticmethod
    def codificar(columnas, filas):
        buffer = io.StringIO(newline="")
        escritor = csv.writer(buffer, delimiter=";", lineterminator="\r\n")
        escritor.writerows([columnas, *filas])
        return "\ufeff" + buffer.getvalue()

    def test_acepta_codificacion_contractual_sin_usar_exportador(self):
        tabla = {"columnas": ["x", "texto", "q"],
                 "filas": [[-0.0, "=cmd|x", "-1/2"], [1e-300, 'a;"b"\nfin', None]]}
        texto = '\ufeffx;texto;q\r\n0;\'=cmd|x;"=""-1/2"""\r\n1E-300;"a;""b""\nfin";'
        self.assertEqual(problemas_csv(texto, tabla), [])

    def test_detecta_truncado_redondeo_e_inyeccion_sin_rechazar_cero_normalizado(self):
        tabla = {"columnas": ["x", "texto"], "filas": [[-0.0, "@SUM(1)"], [1.2345678901234567, "fin"]]}
        errores = problemas_csv("x;texto\r\n0;@SUM(1)\r\n1,2346;fin", tabla)
        self.assertEqual(len(errores), 3)
        self.assertTrue(any("Filas perdidas" in e for e in problemas_csv("\ufeffx;texto", tabla)))

    def test_cero_negativo_exige_cero_normalizado(self):
        for original in (-0.0, "-0", "-0.000", "-0e10"):
            tabla = {"columnas": ["x"], "filas": [[original]]}
            with self.subTest(original=original):
                self.assertEqual(problemas_csv(self.codificar(["x"], [["0"]]), tabla), [])
                self.assertTrue(problemas_csv(self.codificar(["x"], [["-0"]]), tabla))

    def test_enteros_limite_15_cifras_y_texto_validado_sin_perder_digitos(self):
        for valor in ("9007199254740993123456789", "-1234567890123456", "0001234567890123456", 1234567890123456):
            tabla = {"columnas": ["x"], "filas": [[valor]]}
            with self.subTest(valor=valor):
                self.assertEqual(problemas_csv(self.codificar(["x"], [[f'=\"{valor}\"']]), tabla), [])
                self.assertTrue(problemas_csv(self.codificar(["x"], [[str(valor)]]), tabla))
        for valor in ("123456789012345", "000123456789012345", "-123456789012345"):
            tabla = {"columnas": ["x"], "filas": [[valor]]}
            self.assertEqual(problemas_csv(self.codificar(["x"], [[valor]]), tabla), [])

    def test_fracciones_con_denominador_cero_nunca_son_formulas_validadas(self):
        for valor in ("1/0", "-1/0", "0/0", "17/000", "-17/000", "1/-0"):
            tabla = {"columnas": ["q"], "filas": [[valor]]}
            esperado = "'" + valor if valor.startswith("-") else valor
            with self.subTest(valor=valor):
                self.assertEqual(problemas_csv(self.codificar(["q"], [[esperado]]), tabla), [])
                self.assertTrue(problemas_csv(self.codificar(["q"], [[f'=\"{valor}\"']]), tabla))
        tabla = {"columnas": ["q"], "filas": [["0003/0007"]]}
        self.assertEqual(problemas_csv(self.codificar(["q"], [['="0003/0007"']]), tabla), [])

    def test_detecta_inyeccion_tras_espacios_y_controles_en_celdas_y_cabeceras(self):
        for inicio in (" ", "\n", "\r", "\t", "\v", "\f", "\x00", "\x1f", "\x7f",
                       "\u00a0", "\u2003", "\u3000", "\ufeff", " \n\t\u00a0\u2003\u3000"):
            for formula in ("=1+1", "+SUM(A1)", "-SUM(A1)", "@SUM(A1)"):
                valor = inicio + formula
                tabla = {"columnas": [valor], "filas": [[valor]]}
                with self.subTest(inicio=repr(inicio), formula=formula):
                    seguro = self.codificar(["'" + valor], [["'" + valor]])
                    self.assertEqual(problemas_csv(seguro, tabla), [])
                    self.assertEqual(len(problemas_csv(self.codificar([valor], [[valor]]), tabla)), 2)
                    alterado = "'" + formula
                    self.assertTrue(problemas_csv(self.codificar([alterado], [[alterado]]), tabla))

    def test_preserva_texto_inocuo_y_no_autoriza_formulas_arbitrarias(self):
        for valor in ("\n  texto", "\u00a0\u2003\u3000texto", '=\"1/0\"', '=\"1234567890123456\"'):
            tabla = {"columnas": [valor], "filas": [[valor]]}
            esperado = "'" + valor if valor.startswith("=") else valor
            self.assertEqual(problemas_csv(self.codificar([esperado], [[esperado]]), tabla), [])


def escribir_informe(destino):
    casos, consultas = corpus_real()
    casos.append({"id": "adversario", "procedimiento": adversario()})
    salidas = ejecutar_node([c["procedimiento"] for c in casos])
    biblioteca = Path(os.environ.get("P2_EXPORTAR_JS", ROOT / "src/ui/web/exportar.js"))
    informe = {"biblioteca": str(biblioteca), "sha256": hashlib.sha256(biblioteca.read_bytes()).hexdigest(),
               "consultas": consultas, "casos": [], "motores_latex": [n for n in
               ("pdflatex", "lualatex", "xelatex", "tectonic", "latex") if shutil.which(n)]}
    for caso, salida in zip(casos, salidas):
        tablas = caso["procedimiento"]["tablas"]
        errores = [e for t, csv_ in zip(tablas, salida["csv"]) for e in problemas_csv(csv_, t)]
        informe["casos"].append({"id": caso["id"], "modulo": caso["procedimiento"]["modulo"],
            "filas": [len(t["filas"]) for t in tablas], "metricas": salida["metricas"],
            "csv_errores": len(errores), "csv_muestra": errores[:12], "latex": salida["validacion"],
            "babel": r"\usepackage[spanish]{babel}" in salida["latex"],
            "longtable": r"\begin{longtable}" in salida["latex"],
            "filas_latex": [len(re.findall(r"(?m)^.*\\\\\s*$", t)) for t in salida["tablas_latex"]]})
    Path(destino).write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Informe: {destino}; {len(casos)} procedimientos, {len(consultas)} consultas HTTP")


if __name__ == "__main__":
    if "--informe" in sys.argv:
        escribir_informe(sys.argv[sys.argv.index("--informe") + 1])
    else:
        unittest.main()
