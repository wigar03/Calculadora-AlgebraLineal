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
