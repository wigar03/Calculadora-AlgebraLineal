"""Reglas deterministas de orientación; no ejecutan ni certifican un método.

La continuidad se comprueba con el dominio compartido; la convexidad solo se
advierte si el rango intervalar de f'' excluye cero (no mediante muestras).
"""
import ast
import math
from fractions import Fraction

from ..biseccion.expresiones import Expresion, numero_real
from ..derivadas import derivada_simbolica
from ..regla_falsa.dominio import validar_continuidad, validar_condicion, raiz_admisible
from ..regla_falsa.intervalos import _rango


def _restringido(f):
    return any(isinstance(n, ast.Div) or isinstance(n, ast.Pow)
               or isinstance(n, ast.Call) and n.func.id in
               ("ln", "log", "sqrt", "tan", "asin", "acos") for n in ast.walk(f.arbol))


def _intervalo(f, a, b, condicion):
    if a is None or b is None:
        return False, ["Falta un intervalo completo [a,b] con cambio de signo."], False
    if a >= b or not math.isfinite(b-a):
        return False, ["El intervalo debe tener a < b y ancho finito."], False
    try:
        validar_continuidad(f, a, b)
        fa, fb = f(a), f(b)
    except ValueError as exc:
        return False, [f"Revise el dominio del intervalo: {exc}"], False
    if condicion != "real" and (a < 0 or fa == 0 and a == 0):
        return False, ["Elija un intervalo positivo que no incluya la raíz excluida x = 0."], True
    if fa == 0 or fb == 0:
        return False, ["Un extremo ya se evalúa como cero; compruebe esa raíz o elija otro intervalo."], True
    if (fa < 0) == (fb < 0):
        return False, ["No hay cambio de signo: elija otros extremos; puede haber una raíz múltiple."], True
    return True, ["Se verificó el dominio continuo y el cambio de signo en [a,b]."], True


def _newton(f, x, condicion):
    if x is None:
        return False, ["Falta una semilla x0 o un intervalo para examinar su punto medio."]
    try:
        fx = f(x)
        d = derivada_simbolica(f)
        if sum(1 for _ in ast.walk(d.arbol)) > 250:
            return False, ["La derivada simbólica es costosa; considere secante con dos puntos."]
        df = d(x)
        h = 1e-4*max(1., abs(x))
        escala = abs(fx)
        for vecino in (x-h, x+h):
            try:
                escala = max(escala, abs(f(vecino)))
            except ValueError:
                pass
        if abs(df) <= 1e-8*max(escala, 1e-300)/max(1., abs(x)):
            return False, ["Derivada nula o pequeña: posible raíz múltiple si f y f' son pequeñas; cambie x0."]
        if fx == 0 and not raiz_admisible(x, condicion):
            return False, ["La semilla es una raíz excluida por la condición; cambie x0."]
        nuevo = x-fx/df
        if not math.isfinite(nuevo):
            return False, ["El primer paso de Newton no es finito; cambie x0."]
        f(nuevo)
        return True, ["Derivada simbólica evaluable y primer paso dentro del dominio.",
                      "Orden cuadrático solo local, cerca de una raíz simple; depende de la semilla."]
    except ValueError as exc:
        return False, [f"Newton no es práctico con esta semilla o derivada: {exc}"]


def _secante(f, u, v, condicion, intervalo_continuo):
    if u is None or v is None or u == v:
        return False, ["Faltan dos puntos distintos x0, x1 (o ambos extremos del intervalo)."]
    try:
        fu, fv = f(u), f(v)
        if any(fx == 0 and not raiz_admisible(x, condicion) for x, fx in ((u, fu), (v, fv))):
            return False, ["Uno de los puntos es la raíz excluida x = 0; cambie los puntos iniciales."]
        den = fv-fu
        if not math.isfinite(den) or abs(den) <= 1e-12*max(abs(fu), abs(fv), 1e-300):
            return False, ["Las evaluaciones son iguales o demasiado próximas; cambie los puntos."]
        nuevo = v-(fv/den)*(v-u)
        if not math.isfinite(nuevo):
            return False, ["El primer paso de secante no es finito; cambie los puntos."]
        f(nuevo)
        if not intervalo_continuo:
            validar_continuidad(f, min(u, v), max(u, v))
        return True, ["Primer paso evaluable; no requiere derivada.",
                      "Orden local esperado ≈ 1,618 en una raíz simple; los pasos pueden salir del dominio."]
    except ValueError as exc:
        return False, [f"Revise el dominio y los puntos de secante: {exc}"]
