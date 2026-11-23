"""Cuatro exportaciones Node simultáneas de procedimientos HTTP reales, sin recálculo.

Uso: python scripts/medir_exportaciones.py; P2_EXPORTAR_JS selecciona otra rama.
Los picos RSS pertenecen a cada proceso Node, no al cliente/servidor Python.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.core import limites  # noqa: E402
from src.ui.web_server import servidor_local  # noqa: E402
from tests.test_exportacion_modulos import ROOT, entradas_largas  # noqa: E402
from tests.test_golden_api import consultar  # noqa: E402

NODE = r"""
const fs = require('node:fs'), {performance} = require('node:perf_hooks');
const api = require(process.argv[1]);
const p = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const antes = JSON.stringify(p), inicio = performance.now();
const latex = api.procedimientoALatex(p);
const csv = p.tablas.map(t => api.tablaACSV(t));
process.stdout.write(JSON.stringify({ms: performance.now() - inicio,
  rss_max_bytes: process.resourceUsage().maxRSS * 1024,
  latex_bytes: Buffer.byteLength(latex), csv_bytes: csv.map(t => Buffer.byteLength(t)),
  filas_fuente: p.tablas.map(t => t.filas.length),
  filas_csv: csv.map(t => t.split('\r\n').length - 1),
  mutado: JSON.stringify(p) !== antes}));
"""


def medir():
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Node es obligatorio para medir exportaciones reales")
    biblioteca = str(Path(os.environ.get("P2_EXPORTAR_JS", ROOT / "src/ui/web/exportar.js")).resolve())
    with tempfile.TemporaryDirectory(prefix="p2-exportaciones-") as temporal:
        archivos = []
        with servidor_local() as url:
            for nombre, ruta, cuerpo, filas in entradas_largas()[:2]:
                estado, respuesta = consultar(url, ruta, cuerpo)
                assert estado == 200, respuesta
                assert len(respuesta["procedimiento"]["tablas"][0]["filas"]) == filas
                archivo = Path(temporal) / (nombre + ".json")
                archivo.write_text(json.dumps(respuesta["procedimiento"], allow_nan=False), encoding="utf-8")
                archivos.append(archivo)

        def exportar(archivo):
            inicio = time.perf_counter()
            proceso = subprocess.run([node, "-e", NODE, biblioteca, str(archivo)],
                                     capture_output=True, text=True, timeout=30)
            assert proceso.returncode == 0, proceso.stderr
            datos = json.loads(proceso.stdout)
            return {"caso": archivo.stem, "total_s": time.perf_counter() - inicio, **datos}

        with ThreadPoolExecutor(max_workers=4) as grupo:
            return list(grupo.map(exportar, [archivos[0]] * 3 + [archivos[1]]))


if __name__ == "__main__":
    resultados = medir()
    print(json.dumps(resultados, indent=2))
    sys.exit(0 if all(r["filas_fuente"] == r["filas_csv"] and not r["mutado"]
             and r["ms"] < limites.TIEMPO_CALCULO_S * 1000
             and r["rss_max_bytes"] < limites.MEMORIA_CALCULO_MB * 1024**2 for r in resultados) else 1)
