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


def _limitar_memoria_windows(megabytes):
    """Job Object por trabajador: límite de memoria comprometida del proceso."""
    import ctypes
    from ctypes import wintypes as w

    class LimitesBasicos(ctypes.Structure):
        _fields_ = [("tiempo_proceso", ctypes.c_int64), ("tiempo_job", ctypes.c_int64),
                    ("flags", w.DWORD), ("min_ws", ctypes.c_size_t),
                    ("max_ws", ctypes.c_size_t), ("procesos", w.DWORD),
                    ("afinidad", ctypes.c_size_t), ("prioridad", w.DWORD), ("plan", w.DWORD)]

    class ContadoresIO(ctypes.Structure):
        _fields_ = [(nombre, ctypes.c_uint64) for nombre in
                    ("lecturas", "escrituras", "otros", "bytes_leidos", "bytes_escritos", "bytes_otros")]

    class LimitesExtendidos(ctypes.Structure):
        _fields_ = [("basicos", LimitesBasicos), ("io", ContadoresIO),
                    ("memoria_proceso", ctypes.c_size_t), ("memoria_job", ctypes.c_size_t),
                    ("pico_proceso", ctypes.c_size_t), ("pico_job", ctypes.c_size_t)]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, w.LPCWSTR]
    kernel.CreateJobObjectW.restype = w.HANDLE
    kernel.SetInformationJobObject.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD]
    kernel.AssignProcessToJobObject.argtypes = [w.HANDLE, w.HANDLE]
    kernel.GetCurrentProcess.restype = w.HANDLE
    kernel.CloseHandle.argtypes = [w.HANDLE]
    job = kernel.CreateJobObjectW(None, None)
    if not job:
        raise ctypes.WinError(ctypes.get_last_error())
    datos = LimitesExtendidos()
    datos.basicos.flags = 0x100  # JOB_OBJECT_LIMIT_PROCESS_MEMORY
    datos.memoria_proceso = megabytes * 1024 * 1024
    if (not kernel.SetInformationJobObject(job, 9, ctypes.byref(datos), ctypes.sizeof(datos))
            or not kernel.AssignProcessToJobObject(job, kernel.GetCurrentProcess())):
        error = ctypes.WinError(ctypes.get_last_error())
        kernel.CloseHandle(job)
        raise error
    return job


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
