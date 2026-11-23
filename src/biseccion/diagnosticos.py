"""Diagnósticos léxicos y estructurales de sintaxis para expresiones de f(x)."""

import difflib
import re

_TOKEN_RE = re.compile(
    r"(?P<SPACE>\s+)|(?P<NUM>(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"
    r"|(?P<ID>[A-Za-z_][A-Za-z0-9_]*)|(?P<OP>\*\*|//|[\^+\-*/])"
    r"|(?P<LPAREN>\()|(?P<RPAREN>\))|(?P<COMMA>,)|(?P<BAD>.)"
)
_SUGERENCIAS = {
    "lg": ["ln", "log"], "tg": ["tan"], "seno": ["sin"], "coseno": ["cos"],
    "raiz": ["sqrt"], "sqr": ["sqrt"], "arcsin": ["asin"], "arcsen": ["asin"],
    "arccos": ["acos"], "arctan": ["atan"], "arctg": ["atan"],
}
_ATOMOS = {"x", "pi", "e"}
_FUNCIONES = {"asin", "acos", "atan", "sin", "sen", "cos", "tan", "exp", "ln", "log", "sqrt", "abs"}


def sugerir_funcion(nombre):
    """Devuelve funciones admitidas cercanas a `nombre` para guiar la corrección."""
    clave = nombre.lower()
    if clave in _SUGERENCIAS:
        return _SUGERENCIAS[clave]
    return difflib.get_close_matches(clave, sorted(_FUNCIONES - {"sen"}), n=2, cutoff=0.55)


def tokenizar(texto, offset=0):
    """Convierte el texto en tokens y rechaza caracteres no permitidos con posición."""
    tokens = []
    for m in _TOKEN_RE.finditer(texto):
        tipo, valor, pos = m.lastgroup, m.group(), offset + m.start() + 1
        if tipo == "SPACE":
            continue
        if tipo == "BAD":
            if valor in "[]{}":
                raise ValueError(f"Error de sintaxis: delimitador '{valor}' no admitido en posición {pos}. Use '(' y ')' para agrupar.")
            if valor == ".":
                raise ValueError(f"Error de sintaxis: carácter '.' no admitido en posición {pos}. Use '.' solo en decimales (por ejemplo, 0.5).")
            raise ValueError(f"Error de sintaxis: carácter no admitido '{valor}' en posición {pos}. Use solo x, números, +, -, *, /, ^ y paréntesis.")
        tokens.append((tipo, valor, pos))
    return tokens


def _validar_parentesis(tokens):
    pila = []
    for tipo, _, pos in tokens:
        if tipo == "LPAREN":
            pila.append(pos)
        elif tipo == "RPAREN":
            if not pila:
                raise ValueError(f"Error de sintaxis: sobra un paréntesis de cierre ')' en posición {pos}. Elimínelo o abra '(' donde corresponda.")
            pila.pop()
    if pila:
        raise ValueError(f"Error de sintaxis: falta cerrar el paréntesis '(' abierto en posición {pila[-1]}. Añada ')' al final del grupo.")


def _validar_operador(val, pos, prev, nxt):
    if val == "//":
        raise ValueError(f"Error de sintaxis: operador '//' no admitido en posición {pos}. Use '/' para dividir.")
    if val in ("^", "**"):
        if prev is None or prev[0] == "LPAREN":
            raise ValueError(f"Error de sintaxis: falta la base antes de la potencia '{val}' en posición {pos} (por ejemplo, x^2).")
        if nxt is None or nxt[0] == "RPAREN":
            raise ValueError(f"Error de sintaxis: potencia incompleta '{val}' en posición {pos}. Escriba el exponente después de '{val}' (por ejemplo, x^2).")
        if nxt[0] == "OP" and nxt[1] in ("^", "**", "*"):
            raise ValueError(f"Error de sintaxis: potencia mal escrita '{val}{nxt[1]}' en posición {pos}. Use un solo '^' o '**' (por ejemplo, x^2).")
    if val in ("*", "/") and (prev is None or prev[0] == "LPAREN"):
        raise ValueError(f"Error de sintaxis: expresión incompleta, falta un operando antes de '{val}' en posición {pos}.")
    if val in ("+", "-", "*", "/") and (nxt is None or nxt[0] == "RPAREN"):
        raise ValueError(f"Error de sintaxis: expresión incompleta, falta un operando después de '{val}' en posición {pos}.")
    if nxt and nxt[0] == "OP" and nxt[1] in ("*", "/", "^", "**"):
        raise ValueError(f"Error de sintaxis: operadores consecutivos inválidos '{val}{nxt[1]}' en posición {pos}. Deje un solo operador entre los operandos.")


def diagnosticar_sintaxis(texto, offset=0):
    """Detecta errores frecuentes de sintaxis antes de `ast.parse` y sugiere corrección."""
    tokens = tokenizar(texto, offset)
    if not tokens:
        raise ValueError("Error de sintaxis: la expresión está vacía.")
    _validar_parentesis(tokens)
    for i, (tipo, val, pos) in enumerate(tokens):
        prev = tokens[i - 1] if i > 0 else None
        nxt = tokens[i + 1] if i + 1 < len(tokens) else None
        if tipo == "OP":
            _validar_operador(val, pos, prev, nxt)
        elif tipo == "LPAREN" and nxt and nxt[0] == "RPAREN":
            if prev and prev[0] == "ID":
                raise ValueError(f"Error de sintaxis: la función '{prev[1]}' requiere un argumento dentro de los paréntesis (por ejemplo, {prev[1]}(x)).")
            raise ValueError(f"Error de sintaxis: paréntesis vacíos '()' en posición {pos}. Escriba una expresión dentro de ellos.")
        if not nxt:
            continue
        ntipo, nval, _ = nxt
        if tipo == "NUM" and ntipo == "NUM":
            raise ValueError(f"Error de sintaxis: número mal formado entre '{val}' y '{nval}' en posición {pos}.")
        if tipo == "ID" and val in _FUNCIONES and ntipo in ("ID", "NUM"):
            raise ValueError(f"Error de sintaxis: la función '{val}' requiere paréntesis alrededor de su argumento (por ejemplo, {val}({nval})).")
        if (tipo == "NUM" and ntipo in ("ID", "LPAREN")) or (tipo == "RPAREN" and ntipo in ("NUM", "ID", "LPAREN")) or (tipo == "ID" and ntipo in ("NUM", "ID")) or (tipo == "ID" and val in _ATOMOS and ntipo == "LPAREN"):
            der = f"{nval}(...)" if ntipo == "ID" and i + 2 < len(tokens) and tokens[i + 2][0] == "LPAREN" else nval
            raise ValueError(f"Error de sintaxis: falta el operador de multiplicación entre '{val}' y '{der}'. Escribe '{val}*{der}'.")
