"""Verificación independiente de P2 sobre respuestas HTTP reales y motores sin mocks.

P2_EXPORTAR_JS permite revisar la biblioteca de otra rama sin modificar src/.
Ejecutar con --informe ruta.json conserva medidas y diagnósticos reproducibles.
"""
import csv
import io
import json
import math
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
            if isinstance(valor, (int, float)) and not isinstance(valor, bool):
                try:
                    n = celda.replace(",", ".")
                    igual = (Decimal(n) == valor if isinstance(valor, int)
                             else float(n).hex() == valor.hex())
                except (ValueError, ArithmeticError):
                    igual = False
                if not igual:
                    errores.append(f"Pérdida numérica {lugar}")
                if "." in celda or ("e" in celda.lower() and not re.search(r"E[+-]\d{2,}$", celda)):
                    errores.append(f"Decimal/científica fuera del contrato {lugar}")
            elif FRACCION.fullmatch(s):
                if celda != f'="{s}"':
                    errores.append(f"Fracción expuesta a conversión de fecha {lugar}")
            elif NUMERO.fullmatch(s):
                try:
                    igual = Decimal(celda.replace(",", ".")) == Decimal(s)
                except ArithmeticError:
                    igual = False
                if not igual or "." in celda:
                    errores.append(f"Cadena numérica alterada {lugar}")
            elif celda != ("'" + s if s.startswith(("=", "+", "-", "@", "\t", "\r")) else s):
                errores.append(f"Texto inseguro o alterado {lugar}")
    return errores
