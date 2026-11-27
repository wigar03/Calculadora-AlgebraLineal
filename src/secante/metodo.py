"""Secante con dos puntos manuales, historial y control de fallos numéricos."""
import math
from ..core.limites import RAICES_ITER_MAX
from ..biseccion.expresiones import numero_real
from ..regla_falsa.dominio import (
    ExpresionNumerica as Expresion, validar_condicion, raiz_admisible, verificar_raiz,
)
from ..core.tolerancia import clasificar, informe
from ..regla_falsa.certificacion import certificar_raiz


def resolver_secante(funcion, x0, x1, tolerancia=1e-6, max_iteraciones=50, criterio="absoluto",
                     condicion="real"):
    f = Expresion(funcion)
    validar_condicion(condicion)
    a, b = numero_real(x0, "x_0"), numero_real(x1, "x_1")
    tol = numero_real(tolerancia, "La tolerancia")
    limite = numero_real(max_iteraciones, "El máximo de iteraciones")
    if a == b:
        raise ValueError("Elija dos valores iniciales distintos.")
    if tol <= 0 or not limite.is_integer() or not 1 <= limite <= RAICES_ITER_MAX:
        raise ValueError(f"Use tolerancia positiva y un máximo entero entre 1 y {RAICES_ITER_MAX}.")
    if criterio not in ("absoluto", "relativo", "residuo"):
        raise ValueError("Use el criterio absoluto, relativo o residuo.")
    fa, fb = f(a), f(b)
    pasos = []
    avisos = []
    ea = er = None
    iniciales = [a,b]

    def resultado(motivo, convergio):
        cert = None
        if convergio and not raiz_admisible(b, condicion):
            motivo, convergio = "raiz_no_admisible", False
        elif convergio:
            cert = certificar_raiz(f, b, tol, criterio, condicion)
            if not cert["certificada"]:
                motivo, convergio = "no_certificada", False
        valores = {"absoluto": ea, "relativo": er, "residuo": abs(fb)}
        clases = {k: clasificar(v, tol) for k, v in valores.items()}
        return {"funcion": f.texto, "funcion_latex": f.latex(), "iniciales": iniciales,
                "raiz": b, "f_raiz": fb, "residuo": abs(fb), "error_absoluto": ea,
                "condicion": condicion, "verificacion": verificar_raiz(f, b, tol),
                "certificacion": cert,
                "error_relativo": er, "iteraciones": len(pasos), "pasos": pasos,
                "convergio": convergio, "motivo": motivo, "advertencias": avisos,
                "tolerancia": tol, "criterio": criterio,
                "cumple": {k: c == "digitada" for k, c in clases.items()},
                "cumple_cercana": {k: c == "cercana" for k, c in clases.items()},
                "tolerancia_usada": informe(valores[criterio], tol)}
    if fa == 0:
        b, fb = a, fa
        return resultado("raiz_inicial", True)
    if fb == 0:
        return resultado("raiz_inicial", True)
    if criterio == "residuo" and clasificar(abs(fb), tol):
        return resultado("tolerancia", True)
    vistos = {(a,b)}
    for n in range(1, int(limite)+1):
        den = fb-fa
        if den == 0:
            return resultado("denominador_nulo", False)
        if not math.isfinite(den):
            return resultado("divergencia", False)
        # Escala relativa: una diferencia pequeña frente a las evaluaciones.
        if abs(den) < 1e-12*max(abs(fa),abs(fb)):
            avisos.append(str(n))
        c = b - (fb/den)*(b-a)
        if not math.isfinite(c):
            return resultado("divergencia", False)
        try:
            fc = f(c)
        except ValueError:
            return resultado("fuera_de_dominio", False)
        ea = abs(c-b)
        er = ea/abs(c) if c != 0 else None
        ea = ea if math.isfinite(ea) else None
        er = er if er is not None and math.isfinite(er) else None
        pasos.append({"n": n, "a": a, "b": b, "fa": fa, "fb": fb, "c": c,
                      "fc": fc, "denominador": den, "error_absoluto": ea, "error_relativo": er})
        sin_progreso = c == b
        a,b,fa,fb = b,c,fb,fc
        if fc == 0:
            return resultado("raiz_evaluada", True)
        valor = {"absoluto":ea,"relativo":er,"residuo":abs(fc)}[criterio]
        if clasificar(valor, tol):
            return resultado("tolerancia", True)
        if sin_progreso:
            return resultado("sin_progreso", False)
        if (a,b) in vistos:
            return resultado("ciclo", False)
        vistos.add((a,b))
    return resultado("max_iteraciones", False)
