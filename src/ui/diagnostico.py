"""Comprobación del renderizador real y del motor empaquetado, sin servicios externos."""

import json
import re
import time
from pathlib import Path
from urllib.request import Request, urlopen

from src.core.version import VERSION

INDICE = Path(__file__).resolve().parent / "web" / "index.html"
# Primer arranque en frío (binarios recién copiados y perfil WebView2 nuevo): en la CI suele tardar 10-16 s y
# excepcionalmente más de 30 s (INC-031). Se espera hasta ESPERA_CARGA_S y se informa si superó CARGA_LENTA_S.
CARGA_LENTA_S = 30
ESPERA_CARGA_S = 120


def modulos_esperados(indice=INDICE):
    """Una tarjeta de inicio por módulo de la navegación (sin «Inicio»), leída del HTML empaquetado."""
    html = indice.read_text(encoding="utf-8")
    pestañas = set(re.findall(r'class="nav-tab[^"]*" data-tab="(tab-[\w-]+)"', html)) - {"tab-inicio"}
    return len(pestañas)


def comprobar_escritorio(ventana, cargada, url, destino, inicio=None, espera=ESPERA_CARGA_S):
    inicio = time.monotonic() if inicio is None else inicio
    tiempos = {"comprobacion_s": round(time.monotonic() - inicio, 3)}
    resultado = {"ok": False, "version": VERSION, "tiempos": tiempos}
    try:
        if not cargada.wait(timeout=max(0.0, espera - (time.monotonic() - inicio))):
            raise RuntimeError(f"La ventana no terminó de cargar en {espera} segundos desde el inicio.")
        tiempos["carga_s"] = round(time.monotonic() - inicio, 3)
        resultado["carga_lenta"] = tiempos["carga_s"] > CARGA_LENTA_S
        interfaz = ventana.evaluate_js("""(() => ({
          modulos: document.querySelectorAll('.home-module').length,
          formulas: document.querySelectorAll('.katex').length,
          katex: typeof katex !== 'undefined',
          fuentes: document.fonts.check('16px Outfit'),
          externos: performance.getEntriesByType('resource')
            .filter(r => /^https?:/.test(r.name) && new URL(r.name).origin !== location.origin)
            .map(r => r.name)
        }))()""")
        resultado["interfaz"] = interfaz
        esperados = modulos_esperados()
        if (esperados < 11 or interfaz["modulos"] != esperados or not interfaz["katex"]
                or not interfaz["formulas"] or not interfaz["fuentes"]):
            raise RuntimeError("Interfaz o renderizado matemático incompleto.")
        if interfaz["externos"]:
            raise RuntimeError("La interfaz solicitó recursos externos.")
        datos = json.dumps({"funcion": "x^3-x-2", "x0": 1.5}).encode()
        peticion = Request(url + "/api/newton-raphson/resolver", data=datos,
                           headers={"Content-Type": "application/json"})
        with urlopen(peticion, timeout=10) as respuesta:
            calculo = json.load(respuesta)
        if not calculo["convergio"] or abs(calculo["raiz"] - 1.5213797068) > 1e-8:
            raise RuntimeError("Falló la comprobación del motor matemático.")
        resultado.update(ok=True, raiz=calculo["raiz"])
        tiempos["total_s"] = round(time.monotonic() - inicio, 3)
    except Exception as exc:
        resultado["error"] = str(exc)
    finally:
        destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
        ventana.destroy()
