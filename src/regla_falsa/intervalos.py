"""Prueba conservadora del dominio continuo mediante intervalos del AST.

La aritmética racional no expande ni cancela términos en punto flotante. Si una
restricción no puede verificarse se devuelve False: no se presume continuidad.
"""
import ast
import math
from fractions import Fraction as Q


def _encerrar(a, b):
    a, b = sorted((a, b))
    if not math.isfinite(a) or not math.isfinite(b):
        raise ValueError("Rango no representable.")
    return Q(math.nextafter(a, -math.inf)), Q(math.nextafter(b, math.inf))


def _producto(u, v):
    valores = [a*b for a in u for b in v]
    return min(valores), max(valores)


def _rango(n, x):
    if isinstance(n, ast.Constant):
        return (Q(str(n.value)),)*2
    if isinstance(n, ast.Name):
        return x if n.id == "x" else (Q(str(getattr(math, n.id))),)*2
    if isinstance(n, ast.UnaryOp):
        a, b = _rango(n.operand, x)
        return (-b, -a) if isinstance(n.op, ast.USub) else (a, b)
    if isinstance(n, ast.BinOp):
        (a, b), (c, d) = _rango(n.left, x), _rango(n.right, x)
        if isinstance(n.op, ast.Add):
            return a+c, b+d
        if isinstance(n.op, ast.Sub):
            return a-d, b-c
        if isinstance(n.op, ast.Mult):
            return _producto((a,b), (c,d))
        if isinstance(n.op, ast.Div):
            if c <= 0 <= d:
                raise ValueError("No se demuestra denominador distinto de cero.")
            return _producto((a,b), (1/d,1/c))
        if c == d and c.denominator == 1 and abs(c) <= 1000:
            k = int(c)
            if k < 0 and a <= 0 <= b:
                raise ValueError("Potencia singular.")
            valores = [a**k, b**k]
            if k > 0 and k % 2 == 0 and a <= 0 <= b:
                valores.append(Q(0))
            return min(valores), max(valores)
        if a <= 0:
            raise ValueError("Potencia de dominio no demostrado.")
        lo, hi = _producto(_encerrar(math.log(a), math.log(b)), (c,d))
        return _encerrar(math.exp(lo), math.exp(hi))
    a, b = _rango(n.args[0], x)
    nombre = n.func.id
    if nombre in ("ln", "log", "sqrt"):
        if a < 0 or (a == 0 and nombre != "sqrt"):
            raise ValueError("Argumento fuera de dominio.")
        fn = {"ln": math.log, "log": math.log10, "sqrt": math.sqrt}[nombre]
        lo, hi = _encerrar(fn(a), fn(b))
        return max(Q(0), lo) if nombre == "sqrt" else lo, hi
    if nombre in ("sin", "cos"):
        return Q(-1), Q(1)
    if nombre == "tan":
        k = math.ceil((float(a)-math.pi/2)/math.pi)
        if math.pi/2+k*math.pi <= b:
            raise ValueError("Polo de tan en el rango del argumento.")
        return _encerrar(math.tan(a), math.tan(b))
    if nombre == "abs":
        return (Q(0) if a <= 0 <= b else min(abs(a), abs(b))), max(abs(a), abs(b))
    if nombre in ("asin", "acos") and not -1 <= a <= b <= 1:
        raise ValueError("Argumento fuera de [-1,1].")
    fn = {"asin": math.asin, "acos": math.acos, "atan": math.atan, "exp": math.exp}[nombre]
    return _encerrar(fn(a), fn(b))


def dominio_continuo(f, a, b):
    """True solo si todas las restricciones se satisfacen en el intervalo completo."""
    try:
        _rango(f.arbol, (Q(a), Q(b)))
        return True
    except (ValueError, OverflowError, ZeroDivisionError):
        return False
