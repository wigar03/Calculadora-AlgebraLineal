"""Mide tiempos, tamaños y bloqueos de la API ante entradas costosas o hostiles (etapa 3, antes y después).

Uso: python scripts/medir_robustez.py > salida.md   (no modifica nada; usa un servidor local efímero)
"""
import json
import random
import socket
import sys
import threading
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.ui.web_server import servidor_local  # noqa: E402


def post(url, ruta, cuerpo, crudo=None, timeout=90, cabeceras=None):
    datos = crudo if crudo is not None else json.dumps(cuerpo).encode()
    req = Request(url + ruta, datos, {"Content-Type": "application/json", **(cabeceras or {})})
    t = time.perf_counter()
    try:
        with urlopen(req, timeout=timeout) as r:
            cuerpo, estado = r.read(), r.status
    except HTTPError as e:
        cuerpo, estado = e.read(), e.code
    except (URLError, TimeoutError, socket.timeout) as e:
        return {"estado": "sin respuesta", "s": round(time.perf_counter() - t, 2), "bytes": 0, "msg": str(e)[:60]}
    try:
        msg = str(json.loads(cuerpo).get("error", ""))[:70]
    except ValueError:
        msg = ""
    return {"estado": estado, "s": round(time.perf_counter() - t, 2), "bytes": len(cuerpo), "msg": msg}


def matriz(n, semilla=1):
    rnd = random.Random(semilla)
    return [[str(rnd.randint(1, 9)) for _ in range(n)] for _ in range(n)]


def bloqueo(url, ruta, cuerpo):
    """Lanza una petición costosa y mide cuánto tarda una petición trivial simultánea."""
    hilo = threading.Thread(target=post, args=(url, ruta, cuerpo), kwargs={"timeout": 120}, daemon=True)
    hilo.start()
    time.sleep(0.3)
    r = post(url, "/api/vectores/operar", {"operacion": "suma", "u": ["1"], "v": ["2"]}, timeout=30)
    hilo.join(130)
    return r


def socket_lento(url):
    p = urlsplit(url)
    s = socket.create_connection((p.hostname, p.port))
    s.sendall(b"POST /api/vectores/operar HTTP/1.1\r\nHost: x\r\nContent-Length: 1000\r\n\r\n{")
    r = post(url, "/api/vectores/operar", {"operacion": "suma", "u": ["1"], "v": ["2"]}, timeout=15)
    s.close()
    return r


CASOS = [
    ("cofactores n=8", "/api/matrices/determinante", {"A": matriz(8), "metodo": "cofactores"}),
    ("cofactores n=9", "/api/matrices/determinante", {"A": matriz(9), "metodo": "cofactores"}),
    ("LU n=60", "/api/matrices/determinante", {"A": matriz(60), "metodo": "lu"}),
    ("inversa n=30", "/api/matrices/inversa", {"A": matriz(30)}),
    ("ecuaciones 40×40", "/api/ecuaciones/resolver", {"A": matriz(40), "b": ["1"] * 40}),
    ("eficiencia n=5000", "/api/matrices/eficiencia-determinante", {"n": 5000}),
    ("número 1e5000000", "/api/vectores/operar", {"operacion": "suma", "u": ["1e5000000"], "v": ["1"]}),
    ("JSON inválido", "/api/vectores/operar", None),
    ("cuerpo lista", "/api/matrices/inversa", [1, 2]),
    ("Host ajeno", "/api/vectores/operar", {"operacion": "suma", "u": ["1"], "v": ["2"]}),
]


def main():
    print("| Caso | HTTP | s | bytes | mensaje |\n|---|---|---|---|---|")
    with servidor_local() as url:
        for nombre, ruta, cuerpo in CASOS:
            crudo = b"{no json" if cuerpo is None else (json.dumps(cuerpo).encode() if isinstance(cuerpo, list) else None)
            extra = {"Host": "evil.example", "Origin": "http://evil.example"} if nombre == "Host ajeno" else None
            r = post(url, ruta, cuerpo, crudo=crudo, cabeceras=extra)
            print(f"| {nombre} | {r['estado']} | {r['s']} | {r['bytes']} | {r['msg']} |")
        r = bloqueo(url, "/api/matrices/determinante", {"A": matriz(9), "metodo": "cofactores"})
        print(f"| petición trivial durante cofactores n=9 | {r['estado']} | {r['s']} | {r['bytes']} | {r['msg']} |")
        r = socket_lento(url)
        print(f"| petición trivial con un socket lento abierto | {r['estado']} | {r['s']} | {r['bytes']} | {r['msg']} |")


if __name__ == "__main__":
    main()
