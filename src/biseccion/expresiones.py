"""Evaluador de expresiones reales con una lista explícita de operaciones permitidas."""

import ast
import math
import operator

from .diagnosticos import diagnosticar_sintaxis, sugerir_funcion
from .dominio import evaluar_binaria, evaluar_funcion
from .normalizador import (
    ALIAS_FUNCIONES, es_cero_literal, normalizar_ast, normalizar_simbolos, separar_igualdad,
)


FUNCIONES = {
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "exp": math.exp, "ln": math.log, "log": math.log10,
    "sqrt": math.sqrt, "abs": abs,
}
CONSTANTES = {"pi": math.pi, "e": math.e}
OPERACIONES = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}


def numero_real(valor, nombre="valor"):
    """Admite números o decimales/fracciones textuales y exige un real finito."""
    try:
        if isinstance(valor, bool) or not isinstance(valor, (int, float, str)):
            raise ValueError()
        if isinstance(valor, str) and "/" in valor:
            numerador, denominador = valor.split("/")
            resultado = float(numerador) / float(denominador)
        else:
            resultado = float(valor)
        if not math.isfinite(resultado):
            raise ValueError()
        return resultado
    except (ValueError, TypeError, OverflowError, ZeroDivisionError) as exc:
        raise ValueError(f"{nombre} debe ser un número real finito.") from exc


class Expresion:
    """Interpreta un AST validado, sin eval, atributos, imports ni código arbitrario.

    Se aceptan potencias con ^ o ** y multiplicación explícita (2*x).
    Los límites de longitud, nodos y exponentes acotan el trabajo por evaluación.
    """

    def __init__(self, texto):
        if not isinstance(texto, str) or not texto.strip() or len(texto) > 500:
            raise ValueError("Error de sintaxis: ingrese una función de entre 1 y 500 caracteres.")
        self.texto = texto.strip()
        izq, der, offset_der = separar_igualdad(normalizar_simbolos(self.texto))
        arbol_izq = self._parsear_lado(izq, 0)
        if der is None:
            arbol = arbol_izq
        else:
            arbol_der = self._parsear_lado(der, offset_der)
            arbol = arbol_izq if es_cero_literal(arbol_der) else ast.BinOp(
                left=arbol_izq, op=ast.Sub(), right=arbol_der
            )
        self.arbol = normalizar_ast(arbol)
        if sum(1 for _ in ast.walk(self.arbol)) > 120:
            raise ValueError("Error de sintaxis: la función es demasiado compleja.")
        self._validar(self.arbol)

    def _parsear_lado(self, lado, offset):
        diagnosticar_sintaxis(lado, offset)
        try:
            return ast.parse(lado.replace("^", "**"), mode="eval").body
        except (SyntaxError, RecursionError) as exc:
            raise ValueError(
                f"Error de sintaxis en '{lado}'. Revise operadores y paréntesis (por ejemplo, x^3 - x - 2)."
            ) from exc

    def _validar(self, nodo):
        if isinstance(nodo, ast.Constant):
            if type(nodo.value) not in (int, float):
                raise ValueError(f"Error de sintaxis: valor '{nodo.value}' no permitido. Use solo números reales, 'x', 'pi' y 'e'.")
            numero_real(nodo.value, "La constante")
        elif isinstance(nodo, ast.Name):
            if nodo.id in {"x", *CONSTANTES}:
                return
            if nodo.id in FUNCIONES or nodo.id in ALIAS_FUNCIONES:
                raise ValueError(f"Error de sintaxis: '{nodo.id}' es una función y requiere paréntesis (por ejemplo, {nodo.id}(x)).")
            raise ValueError(f"Error de sintaxis: variable no reconocida '{nodo.id}'. Use únicamente la variable 'x' (y constantes 'pi', 'e').")
        elif isinstance(nodo, ast.BinOp) and type(nodo.op) in OPERACIONES:
            self._validar(nodo.left)
            self._validar(nodo.right)
        elif isinstance(nodo, ast.UnaryOp) and isinstance(nodo.op, (ast.UAdd, ast.USub)):
            self._validar(nodo.operand)
        elif isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name):
            nombre = nodo.func.id
            if nombre not in FUNCIONES:
                sug = sugerir_funcion(nombre)
                ayuda = f"¿Quiso escribir {' o '.join(sug)}?" if sug else f"Funciones admitidas: {', '.join(sorted(FUNCIONES))} (también sen)."
                raise ValueError(f"Error de sintaxis: función desconocida '{nombre}'. {ayuda}")
            if len(nodo.args) == 0:
                raise ValueError(f"Error de sintaxis: la función '{nombre}' requiere un argumento (por ejemplo, {nombre}(x)).")
            if len(nodo.args) != 1 or nodo.keywords:
                raise ValueError(f"Error de sintaxis: la función '{nombre}' admite exactamente un argumento (por ejemplo, {nombre}(x)).")
            self._validar(nodo.args[0])
        elif isinstance(nodo, ast.Tuple):
            raise ValueError("Error de sintaxis: no se admite la coma ','. Use punto decimal '.' (por ejemplo, 0.5).")
        else:
            raise ValueError("Error de sintaxis: expresión no permitida. Use x, números, +, -, *, /, ^ y funciones admitidas.")

    def _evaluar(self, nodo, x):
        if isinstance(nodo, ast.Constant):
            return float(nodo.value)
        if isinstance(nodo, ast.Name):
            return x if nodo.id == "x" else CONSTANTES[nodo.id]
        if isinstance(nodo, ast.UnaryOp):
            valor = self._evaluar(nodo.operand, x)
            return -valor if isinstance(nodo.op, ast.USub) else valor
        if isinstance(nodo, ast.Call):
            return evaluar_funcion(nodo.func.id, FUNCIONES[nodo.func.id], self._evaluar(nodo.args[0], x))
        izquierda = self._evaluar(nodo.left, x)
        derecha = self._evaluar(nodo.right, x)
        return evaluar_binaria(nodo.op, izquierda, derecha)

    def latex(self):
        """Representa el mismo árbol validado sin evaluar la función ni aceptar LaTeX libre."""
        def parentesis(texto):
            return rf"\left({texto}\right)"

        def convertir(nodo):
            if isinstance(nodo, ast.Constant):
                texto = str(nodo.value)
                if "e" in texto.lower():
                    mantisa, exponente = texto.lower().split("e")
                    return rf"{mantisa} \times 10^{{{int(exponente)}}}"
                return texto
            if isinstance(nodo, ast.Name):
                return r"\pi" if nodo.id == "pi" else nodo.id
            if isinstance(nodo, ast.UnaryOp):
                argumento = convertir(nodo.operand)
                if isinstance(nodo.operand, ast.BinOp):
                    argumento = parentesis(argumento)
                return ("-" if isinstance(nodo.op, ast.USub) else "+") + argumento
            if isinstance(nodo, ast.Call):
                argumento = convertir(nodo.args[0])
                nombre = nodo.func.id
                if nombre == "sqrt":
                    return rf"\sqrt{{{argumento}}}"
                if nombre == "abs":
                    return rf"\left|{argumento}\right|"
                if nombre == "exp":
                    return rf"e^{{{argumento}}}"
                nombre = {"log": r"\log_{10}", "asin": r"\arcsin", "acos": r"\arccos", "atan": r"\arctan"}.get(nombre, "\\" + nombre)
                return nombre + parentesis(argumento)
            izquierda, derecha = convertir(nodo.left), convertir(nodo.right)
            if isinstance(nodo.op, ast.Div):
                return rf"\frac{{{izquierda}}}{{{derecha}}}"
            if isinstance(nodo.op, ast.Pow):
                if (isinstance(nodo.left, (ast.BinOp, ast.UnaryOp, ast.Call))
                        or isinstance(nodo.left, ast.Constant)
                        and (nodo.left.value < 0 or "e" in str(nodo.left.value).lower())):
                    izquierda = parentesis(izquierda)
                return rf"{izquierda}^{{{derecha}}}"
            if isinstance(nodo.op, ast.Mult):
                if isinstance(nodo.left, ast.BinOp) and isinstance(nodo.left.op, (ast.Add, ast.Sub)):
                    izquierda = parentesis(izquierda)
                if (isinstance(nodo.right, ast.UnaryOp) or isinstance(nodo.right, ast.BinOp)
                        and isinstance(nodo.right.op, (ast.Add, ast.Sub))):
                    derecha = parentesis(derecha)
                return izquierda + r" \cdot " + derecha
            if isinstance(nodo.right, ast.UnaryOp) or (isinstance(nodo.op, ast.Sub)
                    and isinstance(nodo.right, ast.BinOp) and isinstance(nodo.right.op, (ast.Add, ast.Sub))):
                derecha = parentesis(derecha)
            return izquierda + (" + " if isinstance(nodo.op, ast.Add) else " - ") + derecha

        return convertir(self.arbol)

    def __call__(self, x):
        """Evalúa en un punto real y traduce errores de dominio a mensajes de entrada."""
        x = numero_real(x, "x")
        try:
            return numero_real(self._evaluar(self.arbol, x), "f(x)")
        except (ValueError, ZeroDivisionError, OverflowError) as exc:
            detalle = str(exc)
            if detalle.startswith("Error de dominio:"):
                detalle = detalle[len("Error de dominio:"):].strip()
            raise ValueError(f"Error de dominio en x={x:g}: {detalle}") from exc
