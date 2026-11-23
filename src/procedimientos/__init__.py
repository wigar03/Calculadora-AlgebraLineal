"""Registro de adaptadores: ruta de la API -> función (respuesta, cuerpo) -> procedimiento común.

Los adaptadores se registran desde `lineal.py` y `numerico.py`. `adjuntar` nunca rompe un cálculo: si un
adaptador falla, la respuesta se devuelve intacta y el fallo se registra en el log.
"""
import logging

from .base import validar

ADAPTADORES = {}
_log = logging.getLogger(__name__)


def registrar(*rutas):
    def decorador(funcion):
        for ruta in rutas:
            ADAPTADORES[ruta] = funcion
        return funcion
    return decorador


def adjuntar(ruta, respuesta, cuerpo):
    """Devuelve la respuesta con la clave `procedimiento` añadida si hay adaptador y no existía."""
    adaptador = ADAPTADORES.get(ruta)
    if adaptador is None or not isinstance(respuesta, dict) or "procedimiento" in respuesta or "error" in respuesta:
        return respuesta
    try:
        return {**respuesta, "procedimiento": validar(adaptador(respuesta, cuerpo or {}))}
    except Exception:  # un adaptador defectuoso nunca debe romper el cálculo del usuario
        _log.exception("Adaptador de procedimiento fallido para %s", ruta)
        return respuesta


def _cargar_adaptadores():
    for nombre in ("lineal", "numerico"):
        try:
            __import__(f"{__name__}.{nombre}")
        except ModuleNotFoundError as exc:
            if exc.name != f"{__name__}.{nombre}":
                raise


_cargar_adaptadores()
