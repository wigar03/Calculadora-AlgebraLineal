"""Mide tiempos, tamaños y bloqueos de la API ante entradas costosas o hostiles (etapa 3, antes y después).

Uso: python scripts/medir_robustez.py > salida.md   (no modifica nada; usa un servidor local efímero)
"""
import json
import multiprocessing
import os
import random
import socket
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.ui.web_server import servidor_local  # noqa: E402
from src.core import limites  # noqa: E402
from src.core.ejecucion import Supervisor  # noqa: E402
from scripts.memoria_procesos import memoria_proceso  # noqa: E402


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
    datos = None
    try:
        datos = json.loads(cuerpo)
        msg = str(datos.get("error", ""))[:70]
    except ValueError:
        msg = ""
    resultado = {"estado": estado, "s": round(time.perf_counter() - t, 3), "bytes": len(cuerpo), "msg": msg}
    if isinstance(datos, dict):
        resultado.update({k: datos[k] for k in ("tipo", "codigo", "motivo") if k in datos})
        if isinstance(datos.get("iteraciones"), list):
            resultado["iteraciones"] = len(datos["iteraciones"])
    return resultado


def servidor_medicion():
    """Proceso dedicado: su memoria no incluye las respuestas retenidas por el cliente."""
    supervisiones = []
    ejecutar = Supervisor.ejecutar

    def cronometrar(self, referencia, *args, **kwargs):
        inicio = time.perf_counter()
        try:
            return ejecutar(self, referencia, *args, **kwargs)
        finally:
            supervisiones.append(time.perf_counter() - inicio)

    Supervisor.ejecutar = cronometrar
    with servidor_local() as url:
        print(json.dumps({"url": url, "servidor": os.getpid(),
                          "trabajadores": [p.pid for p in multiprocessing.active_children()]}), flush=True)
        sys.stdin.readline()
    print(json.dumps({"supervision_s": supervisiones}), flush=True)


def concurrencia_grande():
    from tests.test_exportacion_modulos import entradas_largas
    nombre, ruta, cuerpo, cantidad = entradas_largas()[0]
    assert limites.RESPUESTA_MAX_BYTES == 16 * 1024**2
    hijo = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--servidor-medicion"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    detener, muestras, errores = threading.Event(), {}, []
    try:
        inicio = json.loads(hijo.stdout.readline())
        url = inicio["url"]
        pids = [inicio["servidor"], *inicio["trabajadores"]]

        def muestrear():
            while not detener.is_set():
                for pid in pids:
                    try:
                        datos = memoria_proceso(pid)
                        anterior = muestras.setdefault(pid, {})
                        for clave, valor in datos.items():
                            anterior[clave] = max(anterior.get(clave, 0), valor)
                    except (OSError, KeyError) as exc:
                        errores.append(f"PID {pid}: {exc}")
                detener.wait(0.02)

        monitor = threading.Thread(target=muestrear, daemon=True)
        monitor.start()
        base = post(url, "/api/biseccion/preview", {"funcion": "x"})
        barrera = threading.Barrier(5)

        def grande():
            barrera.wait(timeout=5)
            return post(url, ruta, cuerpo, timeout=30)

        with ThreadPoolExecutor(max_workers=5) as grupo:
            pendientes = [grupo.submit(grande) for _ in range(4)]
            barrera.wait(timeout=5)
            triviales = []
            while not all(f.done() for f in pendientes):
                triviales.append(post(url, "/api/biseccion/preview", {"funcion": "x"}, timeout=15))
                time.sleep(0.1)
            grandes = [f.result(timeout=35) for f in pendientes]
        recuperacion = post(url, "/api/vectores/operar", {"operacion": "suma", "u": ["1"], "v": ["2"]})
        detener.set()
        monitor.join(2)
        informe = {"caso": nombre, "limites": {"respuesta_bytes": limites.RESPUESTA_MAX_BYTES,
                "trabajador_mb": limites.MEMORIA_CALCULO_MB, "tiempo_s": limites.TIEMPO_CALCULO_S},
                "procesos": inicio, "memoria_bytes": muestras, "base": base,
                "grandes": grandes, "triviales": triviales, "recuperacion": recuperacion,
                "errores_muestreo": errores, "iteraciones_esperadas": cantidad}
    finally:
        detener.set()
        try:
            salida, _ = hijo.communicate("\n", timeout=8)
        except subprocess.TimeoutExpired:
            hijo.kill()
            hijo.communicate()
            raise RuntimeError("El servidor no cerró tras finalizar el ensayo") from None
    informe.update(json.loads(salida.strip()))
    return informe


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
    if "--servidor-medicion" in sys.argv:
        servidor_medicion()
    elif "--concurrencia-grande" in sys.argv:
        informe = concurrencia_grande()
        print(json.dumps(informe, ensure_ascii=True, indent=2))
        grandes, triviales = informe["grandes"], informe["triviales"]
        validas = all(r["estado"] == 200 and r.get("iteraciones") == informe["iteraciones_esperadas"]
                      and r["bytes"] <= limites.RESPUESTA_MAX_BYTES for r in grandes)
        memoria = all(informe["memoria_bytes"][pid]["memoria_limite_max"] < limites.MEMORIA_CALCULO_MB * 1024**2
                      for pid in informe["procesos"]["trabajadores"])
        # P1 limita cálculo supervisado (incluida la cola), no transporte HTTP y serialización del servidor.
        tiempos = (all(s < limites.TIEMPO_CALCULO_S for s in informe["supervision_s"])
                   and all(r["estado"] == 200 and r["s"] < limites.TIEMPO_CALCULO_S for r in triviales))
        sys.exit(0 if validas and memoria and tiempos and informe["recuperacion"]["estado"] == 200
                 and not informe["errores_muestreo"] else 1)
    else:
        main()
