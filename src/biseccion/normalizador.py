"""Normalización de notación matemática e igualdades para el analizador AST."""

import ast

SIMBOLOS = str.maketrans({"−": "-", "–": "-", "·": "*", "×": "*"})
SUPERINDICES = {"²": "^2", "³": "^3", "⁴": "^4"}
ALIAS_FUNCIONES = {"sen": "sin"}


def normalizar_simbolos(texto):
    """Convierte símbolos matemáticos Unicode admitidos a su forma ASCII."""
    salida = texto.translate(SIMBOLOS)
    for superindice, potencia in SUPERINDICES.items():
        salida = salida.replace(superindice, potencia)
    return salida


def separar_igualdad(texto):
    """Separa `izquierda = derecha` o devuelve `(texto, None, 0)`.

    Devuelve `(izq, der, offset_der)` con el desplazamiento del lado derecho.
    Rechaza comparaciones, múltiples `=`, `=` entre paréntesis o lados vacíos.
    """
    profundidad, iguales, i, n = 0, [], 0, len(texto)
    while i < n:
        ch, par = texto[i], texto[i:i + 2]
        if par == "==":
            raise ValueError(
                f"Error de sintaxis: igualdad mal formada '==' en posición {i + 1}. "
                "Use un solo signo '=' (por ejemplo, izquierda = derecha)."
            )
        if par in ("!=", "<=", ">=") or ch in ("<", ">"):
            op = par if par in ("!=", "<=", ">=") else ch
            raise ValueError(
                f"Error de sintaxis: no se admite la comparación '{op}' en posición {i + 1}. "
                "Escriba f(x) o una igualdad con un solo '='."
            )
        if ch == "(":
            profundidad += 1
        elif ch == ")":
            profundidad = max(0, profundidad - 1)
        elif ch == "=":
            if profundidad > 0:
                raise ValueError(
                    f"Error de sintaxis: el signo '=' no puede ir dentro de paréntesis (posición {i + 1})."
                )
            iguales.append(i)
        i += 1
    if not iguales:
        return texto.strip(), None, 0
    if len(iguales) > 1:
        raise ValueError(
            f"Error de sintaxis: igualdad mal formada, hay {len(iguales)} signos '='. "
            "Use exactamente uno (izquierda = derecha)."
        )
    pos = iguales[0]
    izq, der_bruto = texto[:pos].strip(), texto[pos + 1:]
    der = der_bruto.strip()
    if not izq:
        raise ValueError("Error de sintaxis: falta el lado izquierdo de la igualdad '='. Escriba una expresión antes de '='.")
    if not der:
        raise ValueError("Error de sintaxis: falta el lado derecho de la igualdad '='. Escriba una expresión después de '=' (por ejemplo, x = 0).")
    offset_der = pos + 1 + (len(der_bruto) - len(der_bruto.lstrip()))
    return izq, der, offset_der


def es_cero_literal(nodo):
    """Indica si el subárbol es el literal numérico 0 (o +0 / -0)."""
    if isinstance(nodo, ast.Constant) and type(nodo.value) in (int, float):
        return nodo.value == 0
    if isinstance(nodo, ast.UnaryOp) and isinstance(nodo.op, (ast.UAdd, ast.USub)):
        return es_cero_literal(nodo.operand)
    return False


class _NormalizadorAST(ast.NodeTransformer):
    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id in ALIAS_FUNCIONES:
            node.func.id = ALIAS_FUNCIONES[node.func.id]
        return node

    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Pow) and isinstance(node.left, ast.Name) and node.left.id == "e":
            llamada = ast.Call(func=ast.Name(id="exp", ctx=ast.Load()), args=[node.right], keywords=[])
            return ast.copy_location(llamada, node)
        return node


def normalizar_ast(nodo):
    """Aplica alias (`sen` -> `sin`) y convierte `e^u` en `exp(u)` sobre el AST."""
    return ast.fix_missing_locations(_NormalizadorAST().visit(nodo))
