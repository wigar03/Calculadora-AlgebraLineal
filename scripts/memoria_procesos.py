"""Contadores máximos del SO sin dependencias; no confunde cliente y servidor.

El límite P1 se aplica a memoria comprometida en Windows y espacio virtual
en POSIX; RSS se informa por separado. Los máximos del SO evitan perder
picos entre muestras de 20 ms.
"""
import os
from pathlib import Path


def memoria_proceso(pid):
    if os.name != "nt":
        estado = Path(f"/proc/{pid}/status").read_text()
        valores = {linea.split(":")[0]: int(linea.split()[1]) * 1024
                   for linea in estado.splitlines() if linea.startswith(("VmRSS:", "VmHWM:", "VmPeak:"))}
        return {"rss": valores["VmRSS"], "rss_max": valores["VmHWM"],
                "memoria_limite_max": valores["VmPeak"]}
    import ctypes
    from ctypes import wintypes as w

    class Contadores(ctypes.Structure):
        _fields_ = [("cb", w.DWORD), ("fallos_pagina", w.DWORD)] + [
            (nombre, ctypes.c_size_t) for nombre in (
                "rss_max", "rss", "pool_paginado_max", "pool_paginado",
                "pool_no_paginado_max", "pool_no_paginado", "comprometida", "comprometida_max")]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
    kernel.OpenProcess.restype = w.HANDLE
    kernel.CloseHandle.argtypes = [w.HANDLE]
    psapi.GetProcessMemoryInfo.argtypes = [w.HANDLE, ctypes.POINTER(Contadores), w.DWORD]
    proceso = kernel.OpenProcess(0x1000 | 0x10, False, pid)
    if not proceso:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        datos = Contadores()
        datos.cb = ctypes.sizeof(datos)
        if not psapi.GetProcessMemoryInfo(proceso, ctypes.byref(datos), datos.cb):
            raise ctypes.WinError(ctypes.get_last_error())
        return {"rss": datos.rss, "rss_max": datos.rss_max,
                "memoria_limite_max": datos.comprometida_max}
    finally:
        kernel.CloseHandle(proceso)
