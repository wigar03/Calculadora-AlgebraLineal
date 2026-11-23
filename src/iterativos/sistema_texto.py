"""Analizador de sistemas lineales escritos como texto (una ecuación por línea)."""

from __future__ import annotations

from fractions import Fraction
import re

_SUBINDICES = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
_NORM_OPS = str.maketrans({"−": "-", "–": "-", "—": "-", "×": "*", "·": "*", "⋅": "*", "÷": "/"})
_SUP_RE = re.compile(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]")
_TOKEN_RE = re.compile(
    r"\s*(?:"
    r"(?P<POW>\*\*|\^)"
    r"|(?P<NUM>(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"
    r"|(?P<ID>[A-Za-z]+(?:_[A-Za-z0-9₀-₉]*|[0-9₀-₉]+)?)"
    r"|(?P<OP>[+\-*/()])"
    r"|(?P<BAD>.)"
    r")"
)
_VAR_RE = re.compile(r"^([A-Za-z])_?([0-9₀-₉]+)$")


def _tokenizar(texto: str, linea: int) -> list[tuple[str, object]]:
    if m_sup := _SUP_RE.search(texto):
        raise ValueError(f"Línea {linea}: término no lineal con exponente '{m_sup.group()}'. Solo se admiten ecuaciones lineales.")
    tokens: list[tuple[str, object]] = []
    pos = 0
    while pos < len(texto):
        m = _TOKEN_RE.match(texto, pos)
        if not m or m.end() == pos:
            break
        pos = m.end()
        kind, val = m.lastgroup, m.group(m.lastgroup)
        if kind == "POW":
            raise ValueError(f"Línea {linea}: término no lineal con potencia ('{val}'). Las incógnitas deben tener exponente 1.")
        if kind == "NUM":
            tokens.append(("NUM", Fraction(val)))
        elif kind == "ID":
            mv = _VAR_RE.match(val)
            if pos < len(texto) and texto[pos:].lstrip().startswith("(") and not mv:
                raise ValueError(f"Línea {linea}: término no lineal '{val}(...)'. No se admiten funciones en un sistema lineal.")
            if not mv:
                if val.isalpha():
                    raise ValueError(f"Línea {linea}: variable sin índice '{val}'. Usa variables indexadas como x1, x_1 o x₁.")
                raise ValueError(f"Línea {linea}: nombre de variable inválido '{val}'. Usa una letra con índice entero positivo (ej. x1, x_1, x₁).")
            idx = int(mv.group(2).translate(_SUBINDICES))
            if idx < 1:
                raise ValueError(f"Línea {linea}: índice inválido en '{val}'. Los índices deben iniciar en 1 (x1, x2, ...).")
            tokens.append(("VAR", (mv.group(1), idx, val)))
        elif kind == "OP":
            tokens.append((val, val))
        elif val == ",":
            raise ValueError(f"Línea {linea}: carácter ',' no admitido. Usa punto decimal (ej. 0.5) en lugar de coma.")
        else:
            raise ValueError(f"Línea {linea}: carácter no reconocido '{val}'.")
    return tokens


class _ParserLineal:
    def __init__(self, tokens: list[tuple[str, object]], linea: int) -> None:
        self.tokens, self.linea, self.pos = tokens, linea, 0
        self.vars_vistas: set[tuple[str, int]] = set()

    def _peek(self) -> tuple[str, object] | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _next(self) -> tuple[str, object]:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def parse(self) -> tuple[dict[tuple[str, int], Fraction], Fraction, set[tuple[str, int]]]:
        res = self._expr()
        if (tok := self._peek()) is not None:
            if tok[0] == ")":
                raise ValueError(f"Línea {self.linea}: paréntesis de cierre ')' sin apertura.")
            raise ValueError(f"Línea {self.linea}: falta un operador o hay un elemento inesperado ('{tok[1]}').")
        return res[0], res[1], self.vars_vistas

    def _expr(self) -> tuple[dict[tuple[str, int], Fraction], Fraction]:
        acc = self._term()
        while (tok := self._peek()) and tok[0] in ("+", "-"):
            op = self._next()[0]
            rhs = self._term()
            sign = 1 if op == "+" else -1
            coeffs = dict(acc[0])
            for k, v in rhs[0].items():
                nv = coeffs.get(k, Fraction(0)) + sign * v
                if nv == 0:
                    coeffs.pop(k, None)
                else:
                    coeffs[k] = nv
            acc = (coeffs, acc[1] + sign * rhs[1])
        return acc

    def _term(self) -> tuple[dict[tuple[str, int], Fraction], Fraction]:
        acc = self._unary()
        while (tok := self._peek()) and tok[0] in ("*", "/"):
            op = self._next()[0]
            rhs = self._unary()
            acc = self._mul(acc, rhs) if op == "*" else self._div(acc, rhs)
        return acc

    def _unary(self) -> tuple[dict[tuple[str, int], Fraction], Fraction]:
        if (tok := self._peek()) and tok[0] in ("+", "-"):
            op = self._next()[0]
            c, k = self._unary()
            return ({v: -val for v, val in c.items()}, -k) if op == "-" else (c, k)
        acc = self._primary()
        while (tok := self._peek()) and tok[0] in ("VAR", "("):
            acc = self._mul(acc, self._primary())
        return acc

    def _primary(self) -> tuple[dict[tuple[str, int], Fraction], Fraction]:
        tok = self._peek()
        if tok is None:
            raise ValueError(f"Línea {self.linea}: expresión incompleta.")
        if tok[0] == "NUM":
            return {}, self._next()[1]
        if tok[0] == "VAR":
            base, idx, _ = self._next()[1]
            self.vars_vistas.add((base, idx))
            return {(base, idx): Fraction(1)}, Fraction(0)
        if tok[0] == "(":
            self._next()
            val = self._expr()
            if not self._peek() or self._peek()[0] != ")":
                raise ValueError(f"Línea {self.linea}: falta cerrar un paréntesis ')'.")
            self._next()
            return val
        raise ValueError(f"Línea {self.linea}: elemento inesperado '{tok[1]}'.")

    def _mul(self, a, b):
        if a[0] and b[0]:
            (b1, i1), (b2, i2) = next(iter(a[0])), next(iter(b[0]))
            raise ValueError(f"Línea {self.linea}: término no lineal (producto de incógnitas {b1}_{i1} y {b2}_{i2}).")
        if b[0]:
            a, b = b, a
        s = b[1]
        return ({k: v * s for k, v in a[0].items() if v * s != 0}, a[1] * s)

    def _div(self, a, b):
        if b[0]:
            raise ValueError(f"Línea {self.linea}: término no lineal (división entre una incógnita). Usa paréntesis para fracciones, ej. (1/2)x1.")
        if b[1] == 0:
            raise ValueError(f"Línea {self.linea}: división por cero.")
        return ({k: v / b[1] for k, v in a[0].items()}, a[1] / b[1])


def leer_ecuaciones(texto: str) -> tuple[list[list[Fraction]], list[Fraction], list[str]]:
    """Analiza un sistema lineal cuadrado (una ecuación por línea) en coeficientes Fraction exactos."""
    if not isinstance(texto, str):
        raise ValueError("El texto del sistema debe ser una cadena de caracteres.")
    lineas = [(i, ln.strip()) for i, ln in enumerate(texto.splitlines(), 1) if ln.strip()]
    if not lineas:
        raise ValueError("Ingresa al menos una ecuación lineal (una por línea).")

    ecuaciones: list[tuple[dict[tuple[str, int], Fraction], Fraction]] = []
    todas_vars: set[tuple[str, int]] = set()
    for num, raw in lineas:
        if ";" in raw:
            raise ValueError(f"Línea {num}: escribe una sola ecuación por línea (sin ';').")
        eq_count = raw.count("=")
        if eq_count == 0:
            raise ValueError(f"Línea {num}: falta el signo '=' para separar los lados de la ecuación.")
        if eq_count > 1:
            raise ValueError(f"Línea {num}: hay más de un signo '='. Escribe exactamente un '=' por línea.")
        izq_txt, der_txt = (s.strip().translate(_NORM_OPS) for s in raw.split("="))
        if not izq_txt or not der_txt:
            raise ValueError(f"Línea {num}: ambos lados del signo '=' deben contener una expresión.")
        c_izq, k_izq, v_izq = _ParserLineal(_tokenizar(izq_txt, num), num).parse()
        c_der, k_der, v_der = _ParserLineal(_tokenizar(der_txt, num), num).parse()
        if c_der or v_der:
            raise ValueError(f"Línea {num}: hay incógnitas en el lado derecho de '='. Escribe todas las incógnitas a la izquierda (forma Ax = b).")
        if not v_izq:
            raise ValueError(f"Línea {num}: la ecuación no contiene incógnitas.")
        todas_vars.update(v_izq)
        ecuaciones.append((c_izq, k_der - k_izq))

    bases = sorted({base for base, _ in todas_vars})
    if len(bases) > 1:
        raise ValueError(f"Variables inconsistentes: se mezclaron letras base ({', '.join(bases)}). Usa una sola letra con índices.")
    base = bases[0]
    indices = {idx for _, idx in todas_vars}
    max_idx = max(indices)
    faltantes = [i for i in range(1, max_idx + 1) if i not in indices]
    if faltantes:
        lista = ", ".join(f"{base}_{i}" for i in faltantes)
        raise ValueError(f"Índices de variables inconsistentes: faltan {lista} entre {base}_1 y {base}_{max_idx}.")
    m, n = len(ecuaciones), max_idx
    if m != n:
        raise ValueError(f"El sistema no es cuadrado: tiene {m} ecuaciones y {n} incógnitas ({base}_1..{base}_{n}).")
    if n > 20:
        raise ValueError(f"El sistema tiene {n} ecuaciones; el máximo admitido es 20.")

    nombres = [f"{base}_{i}" for i in range(1, n + 1)]
    A = [[c.get((base, j), Fraction(0)) for j in range(1, n + 1)] for c, _ in ecuaciones]
    b = [bi for _, bi in ecuaciones]
    return A, b, nombres
