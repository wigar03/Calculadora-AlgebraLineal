"""Congela las respuestas de la API para `corpus_golden.CORPUS` en `tests/validacion/golden/<modulo>.json`.

Uso (solo cuando un cambio de resultados esté aprobado): python tests/validacion/generar_golden.py
"""
import json
import os
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAIZ)
from src.ui.web_server import servidor_local  # noqa: E402
from tests.validacion.corpus_golden import CORPUS  # noqa: E402

DESTINO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden")


def consultar(url, ruta, cuerpo):
    peticion = Request(url + ruta, json.dumps(cuerpo).encode(), {"Content-Type": "application/json"})
    try:
        with urlopen(peticion, timeout=120) as respuesta:
            return respuesta.status, json.load(respuesta)
    except HTTPError as exc:
        return exc.code, json.load(exc)


def main():
    os.makedirs(DESTINO, exist_ok=True)
    with servidor_local() as url:
        for modulo, casos in CORPUS.items():
            congelado = []
            for ruta, cuerpo in casos:
                estado, datos = consultar(url, ruta, cuerpo)
                if estado != 200:
                    raise SystemExit(f"{modulo} {ruta}: HTTP {estado} {datos}")
                congelado.append({"ruta": ruta, "cuerpo": cuerpo, "respuesta": datos})
            with open(os.path.join(DESTINO, modulo + ".json"), "w", encoding="utf-8", newline="\n") as fh:
                json.dump(congelado, fh, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
                fh.write("\n")
            print(f"{modulo}: {len(congelado)} respuestas")


if __name__ == "__main__":
    main()
