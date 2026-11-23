"""Importación y reapertura reales; REQUIERE_EXTERNOS=1 convierte ausencias en fallos.

SOFFICE y SSCONVERT permiten ejecutables portables, sin instalaciones del sistema.
P2_EXPORTAR_JS selecciona una biblioteca candidata sin modificar src/ ni los golden.
El texto de títulos/cabeceras racionales se compara exactamente por defecto, sin omisiones de casos conocidos.
"""
import csv
import contextlib
import functools
import io
import json
import locale
import os
import re
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from decimal import Decimal
from pathlib import Path

from src.procedimientos import ADAPTADORES
from src.ui.web_server import servidor_local
from tests.test_golden_api import GOLDEN, consultar, equivalentes

ROOT = Path(__file__).resolve().parents[1]
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
RACIONAL = re.compile(r"-?[0-9]+/[0-9]+\Z")
NUMERO = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")


def racional(texto):
    return bool(RACIONAL.fullmatch(texto)) and int(texto.split("/")[1]) != 0


def entero_largo(texto):
    return bool(re.fullmatch(r"[+-]?[0-9]+", texto)) and len(texto.lstrip("+-").lstrip("0")) > 15


def coincide15(actual, original):
    """Alcance acordado: 15 cifras significativas; Calc/Excel no preservan más."""
    a, b = Decimal(actual), Decimal(original)
    return a == b if not b else abs(a - b) <= Decimal(5).scaleb(b.adjusted() - 15)


def normalizar_saltos(texto):
    return texto.replace("\r\n", "\n").replace("\r", "\n")


def texto_importado(texto):
    # STF recorta bordes y ODS normaliza controles; nunca se acepta un tipo numérico/fórmula por ello.
    return normalizar_saltos(texto.removeprefix("'")).strip()


def ejecutar(args, env=None):
    p = subprocess.run([str(a) for a in args], cwd=ROOT, capture_output=True,
                       encoding="utf-8", errors="replace", timeout=120, env=env)
    if p.returncode:
        raise AssertionError(f"{args[0]} devolvió {p.returncode}: {p.stdout[-2000:]} {p.stderr[-2000:]}")
    return p.stdout


@functools.lru_cache(maxsize=1)
def corpus_csv():
    procedimientos = []
    with servidor_local() as url:
        for archivo in sorted(GOLDEN.glob("*.json")):
            for caso in json.loads(archivo.read_text(encoding="utf-8")):
                estado, respuesta = consultar(url, caso["ruta"], caso["cuerpo"])
                assert estado == 200, respuesta
                assert equivalentes({k: respuesta.get(k) for k in caso["respuesta"]}, caso["respuesta"])
                if caso["ruta"] in ADAPTADORES:
                    procedimientos.append(respuesta["procedimiento"])
    return procedimientos


def exportar(procedimientos):
    puente = "const e=require(process.argv[1]);let s='';process.stdin.setEncoding('utf8');" \
        "process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>" \
        "process.stdout.write(JSON.stringify(JSON.parse(s).map(p=>e.tablasACSV(p.tablas)))));"
    p = subprocess.run(["node", "-e", puente, os.environ.get("P2_EXPORTAR_JS", str(ROOT / "src/ui/web/exportar.js"))],
                       input=json.dumps(procedimientos), capture_output=True, encoding="utf-8", timeout=120)
    if p.returncode:
        raise AssertionError(p.stderr)
    return json.loads(p.stdout)


def texto_xml(nodo):
    texto = "".join(nodo.itertext()) if nodo is not None else ""
    return re.sub(r"_x([0-9A-Fa-f]{4})_", lambda m: chr(int(m[1], 16)), texto)


def leer_xlsx(ruta):
    """Lee tipos, valores y fórmulas OOXML; no depende de openpyxl ni recalcula."""
    with zipfile.ZipFile(ruta) as z:
        cadenas = []
        if "xl/sharedStrings.xml" in z.namelist():
            cadenas = [texto_xml(n) for n in ET.fromstring(z.read("xl/sharedStrings.xml"))]
        hojas = sorted(n for n in z.namelist() if re.fullmatch(r"xl/worksheets/sheet[0-9]+\.xml", n))
        assert len(hojas) == 1, hojas
        celdas = {}
        for c in ET.fromstring(z.read(hojas[0])).findall(".//m:c", NS):
            tipo, valor = c.get("t", "n"), c.findtext("m:v", "", NS)
            if tipo == "s":
                valor = cadenas[int(valor)]
            elif tipo == "inlineStr":
                valor = texto_xml(c.find("m:is", NS))
            celdas[c.attrib["r"]] = (tipo, valor, c.findtext("m:f", None, NS))
        return celdas


def adversarios():
    textos = ["=cmd|'/c calc'!A1", '=HYPERLINK("#local";"x")', "=1+2", "+1+2", "-1+2", "@SUM(1)",
              "\t=1+2", "\r=1+2", "\n=1+2", " =1+2", "\ufeff=1+2", "\u00a0=1+2", "\v=1+2",
              'comillas "dobles"; fin', "línea 1\nlínea 2", "Unicode: ñ á Ω 你好", "1/2x", '1/2"&1',
              "-1/2;=1+2", "1/2\n", "1/0", "1/000", "  bordes  ", "1/2", "-1/2"]
    return [{"modulo": "adversarios", "tablas": [
        {"titulo": textos[0], "columnas": ["caso", "texto", "control"],
         "filas": [[i, s, "fin"] for i, s in enumerate(textos)]},
        {"titulo": textos[1], "columnas": textos, "filas": [["fin"] * len(textos)]},
        {"titulo": "1/2", "columnas": ["1/2", "-17/19", "0003/0007", "9007199254740993123456789"],
         "filas": [["control"] * 4]}]},
        {"modulo": "precision", "tablas": [{"columnas": ["caso", "valor", "control"],
         "filas": [[i, v, "fin"] for i, v in enumerate([
             "1/2", "-17/19", "0003/0007", "0/5", 1.25, -12.75, 1.5e-7,
             1.2345678901234567, 1e-300, -0.0, "9007199254740993123456789",
             "0.12345678901234567890123456789"])]}]}]


def filas_fuente(p):
    for i, tabla in enumerate(p["tablas"]):
        if i:
            yield []
        if len(p["tablas"]) > 1 and tabla.get("titulo"):
            yield [(tabla["titulo"], True)]
        yield [(s, True) for s in tabla["columnas"]]
        yield from ([(s, False) for s in fila] for fila in tabla["filas"])


def columna(numero):
    nombre = ""
    while numero:
        numero, resto = divmod(numero - 1, 26)
        nombre = chr(65 + resto) + nombre
    return nombre


def problemas_libro(celdas, procedimiento, texto_racional_exacto=True):
    esperadas = {f"{columna(j)}{i}": (valor, texto) for i, fila in enumerate(filas_fuente(procedimiento), 1)
                 for j, (valor, texto) in enumerate(fila, 1)}
    errores = []
    for direccion in celdas.keys() | esperadas.keys():
        tipo, actual, formula = celdas.get(direccion, ("s", "", None))
        original, solo_texto = esperadas.get(direccion, (None, True))
        fuente = "" if original is None else str(original)
        fraccion = not solo_texto and racional(fuente)
        exacto = fraccion or (isinstance(original, str) and entero_largo(fuente))
        lugar = f"{direccion}: {fuente!r} -> {(tipo, actual, formula)!r}"
        if formula is not None and not ((exacto or racional(fuente)) and formula == f'"{fuente}"'):
            errores.append("Fórmula no autorizada " + lugar)
        if exacto:
            if tipo not in ("s", "str", "inlineStr") or actual != fuente:
                errores.append("Fracción/entero exacto alterado o convertido en fecha " + lugar)
        elif not solo_texto and NUMERO.fullmatch(fuente):
            try:
                igual = coincide15(actual, fuente)
            except (ValueError, ArithmeticError):
                igual = False
            if tipo != "n" or not igual:
                errores.append("Pérdida numérica " + lugar)
        elif fuente:
            if texto_racional_exacto and solo_texto and racional(fuente) and actual != fuente:
                errores.append("Texto racional alterado (apóstrofo visible o contenido cambiado) " + lugar)
            if tipo not in ("s", "str", "inlineStr") or texto_importado(actual) != texto_importado(fuente):
                errores.append("Texto alterado o interpretado " + lugar)
        elif actual or formula:
            errores.append("Celda adicional " + lugar)
    return sorted(errores)


def leer_ods(ruta):
    ns = {"t": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
          "o": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
          "p": "urn:oasis:names:tc:opendocument:xmlns:text:1.0"}
    with zipfile.ZipFile(ruta) as z:
        tablas = ET.fromstring(z.read("content.xml")).findall(".//t:table", ns)
    assert len(tablas) == 1
    celdas, fila = {}, 1
    for r in tablas[0].findall("t:table-row", ns):
        col = 1
        for c in r:
            tipo = c.get("{" + ns["o"] + "}value-type", "string")
            formula = c.get("{" + ns["t"] + "}formula")
            if formula is not None:
                formula = re.sub(r"^[^:]+:=", "", formula)
            valor = c.get("{" + ns["o"] + "}value", "") if tipo == "float" else "\n".join(
                texto_ods(p, ns["p"]) for p in c.findall("p:p", ns))
            rep = int(c.get("{" + ns["t"] + "}number-columns-repeated", "1"))
            if valor or formula:
                for j in range(col, col + rep):
                    celdas[f"{columna(j)}{fila}"] = ({"float": "n", "string": "s"}.get(tipo, tipo), valor, formula)
            col += rep
        fila += int(r.get("{" + ns["t"] + "}number-rows-repeated", "1"))
    return celdas


def texto_ods(nodo, espacio):
    salida = nodo.text or ""
    especiales = {"line-break": "\n", "tab": "\t", "s": " "}
    for hijo in nodo:
        tipo = hijo.tag.removeprefix("{" + espacio + "}")
        salida += (especiales[tipo] * int(hijo.get("{" + espacio + "}c", "1"))
                   if tipo in especiales else texto_ods(hijo, espacio))
        salida += hijo.tail or ""
    return salida


def entorno_stf(base):
    """El detector general usa ; si la configuración regional usa coma decimal."""
    anterior = locale.setlocale(locale.LC_NUMERIC)
    candidatos = [os.environ.get("CSV_GNUMERIC_LOCALE", "es_ES.UTF-8"), "de_DE.UTF-8", "fr_FR.UTF-8"]
    if os.name != "nt":
        candidatos += ejecutar(["locale", "-a"]).splitlines()
    elegido = None
    try:
        for candidato in candidatos:
            try:
                locale.setlocale(locale.LC_NUMERIC, candidato)
                if locale.localeconv()["decimal_point"] == ",":
                    elegido = candidato
                    break
            except locale.Error:
                pass
    finally:
        locale.setlocale(locale.LC_NUMERIC, anterior)
    env = dict(os.environ)
    if elegido is None:
        # Compila en TEMP: no altera el archivo de locales del sistema ni requiere root.
        destino = base / "locales/es_ES.UTF-8"
        destino.parent.mkdir()
        ejecutar(["localedef", "--no-archive", "-i", "es_ES", "-f", "UTF-8", destino])
        env["LOCPATH"], elegido = str(destino.parent), "es_ES.UTF-8"
    env.update(LC_ALL=elegido, LANG=elegido)
    return env


class TestCSVExterno(unittest.TestCase):
    def herramienta(self, nombre, variable):
        ejecutable = shutil.which(os.environ.get(variable, nombre))
        if not ejecutable:
            motivo = f"Falta {nombre}; instale la herramienta o configure {variable}"
            if os.environ.get("REQUIERE_EXTERNOS") == "1":
                self.fail(motivo + " (REQUIERE_EXTERNOS=1)")
            self.skipTest(motivo)
        return ejecutable

    def comprobar(self, motor, ejecutable):
        procedimientos = corpus_csv()
        self.assertEqual(len(procedimientos), 33)
        self.assertEqual(len({p["modulo"] for p in procedimientos}), 13)  # once módulos, dos rutas adicionales
        procedimientos = procedimientos + adversarios()
        textos = exportar(procedimientos)
        evidencia = os.environ.get("CSV_EVIDENCIA_DIR")
        contexto = contextlib.nullcontext(str(Path(evidencia).resolve() / motor)) if evidencia else \
            tempfile.TemporaryDirectory(prefix="csv-externo-")
        with contexto as temporal:
            base, entradas = Path(temporal), []
            base.mkdir(parents=True, exist_ok=True)
            for i, (p, texto) in enumerate(zip(procedimientos, textos)):
                if not p["tablas"]:
                    self.assertEqual(texto, "", p["modulo"])
                    continue
                self.assertTrue(texto.startswith("\ufeff"), p["modulo"])
                list(csv.reader(io.StringIO(texto.removeprefix("\ufeff")), delimiter=";", strict=True))
                ruta = base / f"{i:02d}_{p['modulo']}.csv"
                ruta.write_bytes(texto.encode("utf-8"))
                entradas.append((p, ruta))
            destinos = [base / nombre for nombre in ("importado", "guardado", "reabierto")]
            for destino in destinos:
                destino.mkdir(exist_ok=True)
            if motor == "calc":
                comun = [ejecutable, "-env:UserInstallation=" + (base / "perfil").as_uri(), "--headless"]
                especiales = "true" if os.environ.get("CSV_CALC_ESPECIALES") == "1" else "false"
                filtro = f"--infilter=Text - txt - csv (StarCalc):59,34,76,1,,3082,false,{especiales},false,false,false,0,true"
                ejecutar([*comun, filtro, "--convert-to", "xlsx", "--outdir", destinos[0], *[r for _, r in entradas]])
                ejecutar([*comun, "--convert-to", "ods", "--outdir", destinos[1], *destinos[0].glob("*.xlsx")])
                ejecutar([*comun, "--convert-to", "xlsx", "--outdir", destinos[2], *destinos[1].glob("*.ods")])
            else:
                regional = entorno_stf(base)
                for _, ruta in entradas:
                    inicial = destinos[0] / (ruta.stem + ".ods")
                    intermedio = destinos[1] / (ruta.stem + ".gnumeric")
                    final = destinos[2] / inicial.name
                    # Mismos bytes: detección automática de STF, no selección explícita de ;.
                    texto = ruta.with_suffix(".txt")
                    texto.write_bytes(ruta.read_bytes())
                    self.assertEqual(texto.read_bytes(), ruta.read_bytes())
                    ejecutar([ejecutable, "--import-type=Gnumeric_stf:stf_csvtab", "--import-encoding=UTF-8", texto, inicial], regional)
                    ejecutar([ejecutable, inicial, intermedio], regional)
                    ejecutar([ejecutable, intermedio, final], regional)
            resultados = []
            for p, ruta in entradas:
                for etapa in (destinos[0], destinos[2]):
                    with self.subTest(motor=motor, modulo=p["modulo"], caso=ruta.stem, etapa=etapa.name):
                        libro = etapa / (ruta.stem + (".xlsx" if motor == "calc" else ".ods"))
                        self.assertTrue(libro.is_file(), f"{ejecutable} no produjo {libro}")
                        errores = problemas_libro(leer_xlsx(libro) if motor == "calc" else leer_ods(libro), p)
                        resultados.append({"caso": ruta.stem, "etapa": etapa.name, "errores": errores})
                        self.assertEqual(errores, [], f"{len(errores)} incumplimientos; " + "; ".join(errores[:12]))
            if evidencia:
                (base / "informe.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")

    def test_libreoffice_importa_guarda_y_reabre(self):
        self.comprobar("calc", self.herramienta("soffice", "SOFFICE"))

    def test_gnumeric_importa_guarda_y_reabre(self):
        self.comprobar("gnumeric", self.herramienta("ssconvert", "SSCONVERT"))


class TestOraculoLibroCSV(unittest.TestCase):
    def test_texto_racional_detecta_apostrofo_visible(self):
        p = {"tablas": [{"columnas": ["1/2"], "filas": []}]}
        self.assertEqual(problemas_libro({"A1": ("s", "1/2", None)}, p), [])
        self.assertEqual(problemas_libro({"A1": ("str", "1/2", '"1/2"')}, p), [])
        errores = problemas_libro({"A1": ("s", "'1/2", None)}, p)
        self.assertTrue(any("apóstrofo visible" in e for e in errores), errores)
        p["tablas"][0]["columnas"] = ["1/0"]
        self.assertTrue(any("Fórmula no autorizada" in e for e in problemas_libro(
            {"A1": ("str", "1/0", '"1/0"')}, p, True)))

    def test_acepta_fraccion_textual_y_decimal_exactos(self):
        p = {"tablas": [{"columnas": ["q", "x", "texto"], "filas": [["-1/2", 1.25, "=1+2"]]}]}
        celdas = {"A1": ("s", "q", None), "B1": ("s", "x", None), "C1": ("s", "texto", None),
                  "A2": ("str", "-1/2", '"-1/2"'), "B2": ("n", "1.25", None), "C2": ("s", "'=1+2", None)}
        self.assertEqual(problemas_libro(celdas, p), [])

    def test_detecta_formula_con_cache_inocua_fecha_y_redondeo(self):
        p = {"tablas": [{"columnas": [], "filas": [["1/2", 1.2345678901234567, "=1+2"]]}]}
        errores = problemas_libro({"A1": ("n", "46054", None), "B1": ("n", "1.23457", None),
                                  "C1": ("str", "=1+2", "HYPERLINK(\"#local\",\"x\")")}, p)
        for mensaje in ("Fracción/entero exacto alterado", "Pérdida numérica", "Fórmula no autorizada"):
            self.assertTrue(any(mensaje in e for e in errores), errores)
