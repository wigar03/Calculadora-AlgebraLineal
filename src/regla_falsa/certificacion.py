"""Certificación local separada del criterio de parada y del residuo.

Para afirmar convergencia se exige un cambio de signo estricto en un intervalo
continuo de radio ligado a la tolerancia. Raíces múltiples o extremos sin cambio
de signo quedan sin certificar: un valor flotante cero no demuestra existencia.
"""
import math
from .dominio import puntos_excluidos, raiz_admisible
from .intervalos import dominio_continuo


def certificar_raiz(f, x, tolerancia, criterio, condicion):
    radio = tolerancia if criterio == "absoluto" else tolerancia*max(1., abs(x))
    if criterio == "relativo_porcentual":
        radio /= 100
    a, b = x-radio, x+radio
    cert = {"certificada": False, "intervalo": None, "radio": radio if math.isfinite(radio) else None,
            "f_extremos": None, "tipo": "cambio_de_signo"}

    def fallo(razon):
        return dict(cert, razon=razon)

    if not math.isfinite(a) or not math.isfinite(b) or not a < x < b:
        return fallo("precision_insuficiente")
    cert["intervalo"] = [a, b]
    if not raiz_admisible(a, condicion):
        return fallo("condicion_no_demostrada")
    if puntos_excluidos(f, a, b) or not dominio_continuo(f, a, b):
        return fallo("dominio_no_demostrado")
    try:
        fa, fb = f(a), f(b)
    except ValueError:
        return fallo("dominio_no_demostrado")
    cert["f_extremos"] = [fa, fb]
    if fa == 0 or fb == 0 or (fa < 0) == (fb < 0):
        return fallo("sin_cambio_de_signo")
    return dict(cert, certificada=True, razon="cambio_de_signo_en_dominio_continuo")


def aviso_no_certificada(n):
    return {"tipo": "no_certificada", "n": n,
            "mensaje": "El criterio de parada se alcanzó, pero no se pudo certificar una raíz "
                       "admisible cercana con cambio de signo en un intervalo continuo. "
                       "Puede tratarse de una raíz múltiple, un extremo o un límite sin raíz."}
