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
