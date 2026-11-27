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
    for n in ast.walk(f.arbol):
        if isinstance(n, ast.Div) or isinstance(n, ast.Call) and n.func.id in (
                "ln", "log", "sqrt", "tan", "asin", "acos"):
            return True
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Pow):
            if not (isinstance(n.right, ast.Constant) and n.right.value >= 0
                    and float(n.right.value).is_integer()):
                return True
    return False


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


def _secante(f, u, v, condicion):
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
        validar_continuidad(f, min(u, v), max(u, v))
        return True, ["Primer paso evaluable; no requiere derivada.",
                      "Orden local esperado ≈ 1,618 en una raíz simple; los pasos pueden salir del dominio."]
    except ValueError as exc:
        return False, [f"Revise el dominio y los puntos de secante: {exc}"]


def recomendar_metodo(funcion, a=None, b=None, x0=None, x1=None, condicion="real"):
    f = Expresion(funcion)
    validar_condicion(condicion)
    a, b, x0, x1 = (None if v is None else numero_real(v, nombre)
                      for v, nombre in ((a, "a"), (b, "b"), (x0, "x0"), (x1, "x1")))
    cerrado, motivos, continuo = _intervalo(f, a, b, condicion)
    bis = motivos + (["El ancho se divide por dos; coste orientativo: "
                      r"$n \approx \lceil\log_2((b-a)/\mathrm{tol})\rceil$."] if cerrado else [])
    rf = motivos + (["Puede necesitar menos pasos que bisección, salvo estancamiento de un extremo."]
                    if cerrado else [])
    if cerrado:
        try:
            dd = derivada_simbolica(derivada_simbolica(f))
            lo, hi = _rango(dd.arbol, (Fraction(a), Fraction(b)))
            if lo > 0 or hi < 0:
                rf.append("La segunda derivada conserva signo: riesgo de estancamiento por convexidad.")
        except (ValueError, OverflowError, ZeroDivisionError):
            rf.append("No se pudo determinar el signo de la segunda derivada en todo el intervalo.")
    semilla = x0 if x0 is not None else a+(b-a)/2 if continuo else None
    newton, mn = _newton(f, semilla, condicion)
    if x0 is None and semilla is not None:
        mn.append("Evaluación orientativa en el punto medio; escriba esa semilla si elige Newton.")
    secante, ms = _secante(f, x0 if x0 is not None else a, x1 if x1 is not None else b, condicion)
    metodos = [dict(metodo=m, apto=ok, motivos=razones) for m, ok, razones in (
        ("biseccion", cerrado, bis), ("regla_falsa", cerrado, rf),
        ("newton_raphson", newton, mn), ("secante", secante, ms))]
    restringido = _restringido(f)
    elegido = ("biseccion" if cerrado and restringido else "newton_raphson" if newton
               else "biseccion" if cerrado else "secante" if secante else None)
    if elegido == "biseccion":
        razon = ("Se prefiere un intervalo validado para respetar el dominio restringido."
                 if restringido else "Se prefiere conservar el encierro validado por cambio de signo.")
    elif elegido == "newton_raphson":
        razon = "Newton tiene una derivada práctica y un primer paso evaluable; revise su comportamiento local."
        if restringido:
            razon += " El dominio es restringido: es preferible aportar también un intervalo validado."
    elif elegido == "secante":
        razon = "Secante permite usar dos puntos útiles sin evaluar una derivada práctica."
    else:
        razon = "Falta un intervalo continuo con cambio de signo o semillas útiles; cambie los datos indicados."
    return {"recomendado": elegido, "metodos": metodos,
            "justificacion": razon + " Esta recomendación previa no garantiza convergencia ni una raíz admisible."}
