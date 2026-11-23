"""Importación y reapertura reales; REQUIERE_EXTERNOS=1 convierte ausencias en fallos.

SOFFICE y SSCONVERT permiten ejecutables portables, sin instalaciones del sistema.
P2_EXPORTAR_JS selecciona una biblioteca candidata sin modificar src/ ni los golden.
"""
import csv
import functools
import io
import json
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


def ejecutar(args):
    p = subprocess.run([str(a) for a in args], cwd=ROOT, capture_output=True,
                       encoding="utf-8", errors="replace", timeout=120)
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
              "-1/2;=1+2", "1/2\n", "1/0", "1/000", "  bordes  "]
    return [{"modulo": "adversarios", "tablas": [
        {"titulo": textos[0], "columnas": ["caso", "texto", "control"],
         "filas": [[i, s, "fin"] for i, s in enumerate(textos)]},
        {"titulo": textos[1], "columnas": textos, "filas": [["fin"] * len(textos)]}]},
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


def problemas_libro(celdas, procedimiento):
    esperadas = {f"{columna(j)}{i}": (valor, texto) for i, fila in enumerate(filas_fuente(procedimiento), 1)
                 for j, (valor, texto) in enumerate(fila, 1)}
    errores = []
    for direccion in celdas.keys() | esperadas.keys():
        tipo, actual, formula = celdas.get(direccion, ("s", "", None))
        original, solo_texto = esperadas.get(direccion, (None, True))
        fuente = "" if original is None else str(original)
        fraccion = not solo_texto and racional(fuente)
        lugar = f"{direccion}: {fuente!r} -> {(tipo, actual, formula)!r}"
        if formula is not None and not (fraccion and formula == f'"{fuente}"'):
            errores.append("Fórmula no autorizada " + lugar)
        if fraccion:
            if tipo not in ("s", "str", "inlineStr") or actual != fuente:
                errores.append("Fracción alterada o convertida en fecha " + lugar)
        elif not solo_texto and NUMERO.fullmatch(fuente):
            try:
                igual = (float(actual).hex() == original.hex() if isinstance(original, float)
                         else Decimal(actual) == Decimal(fuente))
            except (ValueError, ArithmeticError):
                igual = False
            if tipo != "n" or not igual:
                errores.append("Pérdida numérica " + lugar)
        elif fuente:
            if tipo not in ("s", "str", "inlineStr") or actual not in (fuente, "'" + fuente):
                errores.append("Texto alterado o interpretado " + lugar)
        elif actual or formula:
            errores.append("Celda adicional " + lugar)
    return sorted(errores)
