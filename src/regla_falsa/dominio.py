"""Comprobaciones compartidas de dominio y verificación de raíces numéricas."""

import ast
import math
from decimal import Decimal, localcontext
from fractions import Fraction

from ..biseccion.expresiones import Expresion


class ExpresionNumerica(Expresion):
    """Reutiliza el dominio del analizador sin alterar los valores de la función."""


def validar_condicion(condicion):
    if condicion not in ("real", "positiva", "positiva_no_nula"):
        raise ValueError("La condición debe ser real, positiva o positiva_no_nula.")


def raiz_admisible(x, condicion):
    return condicion == "real" or x > 0


def verificar_raiz(f, x, tolerancia):
    """Sustitución independiente del criterio de error de aproximación elegido."""
    fx = f(x)
    return {"x": x, "f_x": fx, "residuo": abs(fx),
            "cumple_residuo": abs(fx) <= tolerancia,
            "nota": "El residuo |f(x)| no es una cota del error en x."}


def _polinomio(n):
    """Coeficientes hasta grado dos; None pide continuar con análisis numérico."""
    if isinstance(n, ast.Constant):
        return [Fraction(str(n.value))]
    if isinstance(n, ast.Name):
        return [Fraction(0), Fraction(1)] if n.id == "x" else [Fraction(str(getattr(math, n.id)))]
    if isinstance(n, ast.UnaryOp):
        p = _polinomio(n.operand)
        return None if p is None else [(-v if isinstance(n.op, ast.USub) else v) for v in p]
    if not isinstance(n, ast.BinOp):
        return None
    p, q = _polinomio(n.left), _polinomio(n.right)
    if p is None or q is None:
        return None
    if isinstance(n.op, ast.Div) and len(q) == 1 and q[0]:
        return [v / q[0] for v in p]
    if isinstance(n.op, ast.Pow) and q == [2.] and len(p) <= 2:
        q = p
    elif not isinstance(n.op, (ast.Add, ast.Sub, ast.Mult)):
        return None
    if isinstance(n.op, (ast.Mult, ast.Pow)):
        if len(p) + len(q) > 4:
            return None
        r = [Fraction(0)] * (len(p) + len(q) - 1)
        for i, u in enumerate(p):
            for j, v in enumerate(q):
                r[i + j] += u * v
        return r
    r = [Fraction(0)] * max(len(p), len(q))
    for i, v in enumerate(p):
        r[i] += v
    for i, v in enumerate(q):
        r[i] += -v if isinstance(n.op, ast.Sub) else v
    return r


def _ceros(n, nivel=0):
    p = _polinomio(n)
    if p is None:
        return []
    p[0] -= Fraction(str(nivel))
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    if len(p) == 2:
        return [float(-p[0] / p[1])]
    if len(p) == 3:
        c, b, a = p
        discriminante = b*b - 4*a*c
        if discriminante >= 0:
            with localcontext() as ctx:
                ctx.prec = 80
                decimal = lambda v: Decimal(v.numerator)/Decimal(v.denominator)
                raiz = decimal(discriminante).sqrt()
                q = -(decimal(b) + (raiz if b >= 0 else -raiz))/2
                return [float(q/decimal(a)), float(decimal(c)/q)] if q else [float(-b/(2*a))]
    return []


def puntos_excluidos(f, a, b):
    """Restricciones del AST aunque se cancelen en f, p. ej. (x-c)/(x-c)."""
    puntos = []
    for n in ast.walk(f.arbol):
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div):
            d = n.right
            puntos.extend(_ceros(d))
            if isinstance(d, ast.Call) and d.func.id in ("ln", "log"):
                puntos.extend(_ceros(d.args[0], 1.))
            if isinstance(d, ast.Call) and d.func.id == "tan":
                puntos.extend(_periodicos(d.args[0], a, b, 0.))
        if isinstance(n, ast.Call):
            if n.func.id in ("ln", "log"):
                puntos.extend(_ceros(n.args[0]))
            if n.func.id == "tan":
                puntos.extend(_periodicos(n.args[0], a, b, math.pi/2))
    return sorted({x for x in puntos if a <= x <= b})


def _periodicos(n, a, b, fase):
    p = _polinomio(n)
    if p is None or len(p) != 2 or p[1] == 0:
        return []
    u, v = sorted((p[0] + p[1]*a, p[0] + p[1]*b))
    k = math.ceil((u - fase) / math.pi)
    # Basta el primer punto excluido para rechazar el intervalo, sin listas enormes.
    return [(fase + k*math.pi - p[0])/p[1]] if fase + k*math.pi <= v else []


def validar_continuidad(f, a, b):
    if puntos_excluidos(f, a, b):
        raise ValueError("El intervalo contiene una discontinuidad o un polo del dominio.")
    # El muestreo pierde sentido entre flotantes adyacentes.
    if b - a <= 64 * max(math.ulp(a), math.ulp(b)):
        return
    from .continuidad import analizar_continuidad
    if not analizar_continuidad(f, a, b)["continua"]:
        raise ValueError("Se detectó una discontinuidad o un polo en el intervalo. "
                         "Elija extremos dentro de un mismo tramo del dominio.")
