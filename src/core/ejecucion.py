"""Procesos persistentes y cancelables; ninguna función recibida procede del cliente."""
import atexit
import importlib
import json
import logging
import multiprocessing
import os
import queue
import threading
import time

from . import limites

_log = logging.getLogger(__name__)


class ErrorEjecucion(Exception):
    def __init__(self, error, tipo="interno", codigo="error_interno", estado=500):
        super().__init__(error)
        self.tipo, self.codigo, self.estado = tipo, codigo, estado

    def respuesta(self):
        return {"error": str(self), "tipo": self.tipo, "codigo": self.codigo}


def clasificar_error(exc):
    if isinstance(exc, ErrorEjecucion):
        return exc
    if isinstance(exc, (MemoryError, limites.LimiteExcedido)):
        return ErrorEjecucion(str(exc) or "El cálculo superó la memoria disponible.",
                              "limite", "limite_calculo", 400)
    if isinstance(exc, (ValueError, ZeroDivisionError)):
        mensaje = str(exc)
        if any(texto in mensaje for texto in ("invalid literal", "could not convert", "Exceeds the limit")):
            _log.exception("Conversión de entrada fallida")
            mensaje = "Los datos de entrada no tienen el formato esperado."
        dominio = isinstance(exc, ZeroDivisionError) or "dominio" in mensaje.lower()
        return ErrorEjecucion(mensaje, "dominio" if dominio else "entrada", "datos_invalidos", 400)
    _log.exception("Fallo interno durante el cálculo")
    return ErrorEjecucion("No se pudo completar el cálculo. Inténtelo de nuevo.")


def serializar(valor):
    """Acota la salida mientras se codifica, sin crear una segunda copia enorme."""
    salida = bytearray()
    for fragmento in json.JSONEncoder(ensure_ascii=True).iterencode(valor):
        if len(fragmento) > limites.RESPUESTA_MAX_BYTES - len(salida):
            raise ErrorEjecucion("La respuesta supera el tamaño máximo permitido.",
                                 "limite", "respuesta_grande", 400)
        salida.extend(fragmento.encode("utf-8"))
    return bytes(salida)


def _limitar_memoria(megabytes):
    if os.name != "nt":
        import resource
        cantidad = megabytes * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (cantidad, cantidad))
        return None
    return _limitar_memoria_windows(megabytes)


def _trabajador(conexion, memoria_mb):
    job = None
    try:
        job = _limitar_memoria(memoria_mb)
        conexion.send_bytes(b"listo")
        while True:
            referencia, args, kwargs = conexion.recv()
            try:
                modulo, nombre = referencia.split(":", 1)
                funcion = getattr(importlib.import_module(modulo), nombre)
                conexion.send_bytes(b"o" + serializar(funcion(*args, **kwargs)))
            except Exception as exc:
                error = clasificar_error(exc)
                conexion.send_bytes(b"e" + json.dumps([error.respuesta(), error.estado]).encode())
    except (EOFError, BrokenPipeError):
        pass
    finally:
        conexion.close()
        if job is not None:
            import ctypes
            ctypes.windll.kernel32.CloseHandle(job)
