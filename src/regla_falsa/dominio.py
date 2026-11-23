"""Comprobaciones compartidas de dominio y verificación de raíces numéricas."""

import ast
import math

from ..biseccion.expresiones import Expresion


class ExpresionNumerica(Expresion):
    """Conserva el analizador y detecta polos trigonométricos representables.

    math.tan(pi/2) devuelve un flotante enorme: no significa que exista tan(pi/2).
    La guarda usa el error de representación del argumento, no una tolerancia de raíz.
    """

    def _evaluar(self, nodo, x):
        if isinstance(nodo, ast.Call) and nodo.func.id == "tan":
            u = self._evaluar(nodo.args[0], x)
            if abs(math.cos(u)) <= 2 * math.ulp(max(1.0, abs(u))):
                raise ValueError("tan no está definida en un polo (pi/2 + k*pi).")
            if u and abs(math.sin(u)) <= 2 * math.ulp(abs(u)):
                return 0.0
        return super()._evaluar(nodo, x)


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


def validar_continuidad(f, a, b):
    # El muestreo pierde sentido entre flotantes adyacentes.
    if b - a <= 64 * max(math.ulp(a), math.ulp(b)):
        return
    from .continuidad import analizar_continuidad
    if not analizar_continuidad(f, a, b)["continua"]:
        raise ValueError("Se detectó una discontinuidad o un polo en el intervalo. "
                         "Elija extremos dentro de un mismo tramo del dominio.")
