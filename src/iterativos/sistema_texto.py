"""Analizador de sistemas lineales escritos como texto (una ecuación por línea)."""

from __future__ import annotations

from fractions import Fraction
import re

_SUBINDICES = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
_NORM_OPS = str.maketrans({"−": "-", "–": "-", "—": "-", "×": "*", "·": "*", "⋅": "*", "÷": "/"})
_SUP_RE = re.compile(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]")
_MAX_VARS, _MAX_TEXTO, _MAX_TOKENS, _MAX_PROF = 20, 20_000, 2_000, 32
_MAX_LITERAL, _MAX_EXP, _MAX_BITS = 64, 350, 4096
_UMBRAL_CERO = Fraction(1, 1 << 1075)
_UMBRAL_INFINITO = Fraction((1 << 1024) - (1 << 970))
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


def _validar_magnitud(val: Fraction, linea: int) -> Fraction:
    if val != 0 and not (_UMBRAL_CERO < abs(val) < _UMBRAL_INFINITO):
        raise ValueError(f"Línea {linea}: magnitud numérica fuera del rango representable en precisión doble.")
    if val.numerator.bit_length() > _MAX_BITS or val.denominator.bit_length() > _MAX_BITS:
        raise ValueError(f"Línea {linea}: magnitud o complejidad fraccionaria excesiva.")
    return val


def _leer_numero(val: str, linea: int) -> Fraction:
    if len(val) > _MAX_LITERAL:
        raise ValueError(f"Línea {linea}: literal numérico demasiado largo ('{val[:24]}...'). Usa una magnitud representable.")
    partes = val.lower().split("e")
    if len(partes) == 2:
        exp = partes[1]
        if len(exp.lstrip("+-0")) > 4 or abs(int(exp)) > _MAX_EXP:
            raise ValueError(f"Línea {linea}: magnitud numérica fuera de rango en '{val[:24]}'. Usa valores representables en precisión doble.")
    return _validar_magnitud(Fraction(val), linea)


def _tokenizar(texto: str, linea: int) -> list[tuple[str, object]]:
    if m_sup := _SUP_RE.search(texto):
        raise ValueError(f"Línea {linea}: término no lineal con exponente '{m_sup.group()}'. Solo se admiten ecuaciones lineales.")
    tokens: list[tuple[str, object]] = []
    pos, prof = 0, 0
    while pos < len(texto):
        m = _TOKEN_RE.match(texto, pos)
        if not m or m.end() == pos:
            break
        pos = m.end()
        kind, val = m.lastgroup, m.group(m.lastgroup)
        if kind == "POW":
            raise ValueError(f"Línea {linea}: término no lineal con potencia ('{val}'). Las incógnitas deben tener exponente 1.")
        if kind == "NUM":
            tokens.append(("NUM", _leer_numero(val, linea)))
        elif kind == "ID":
            mv = _VAR_RE.match(val)
            if not mv:
                j = pos
                while j < len(texto) and texto[j].isspace():
                    j += 1
                if j < len(texto) and texto[j] == "(":
                    raise ValueError(f"Línea {linea}: término no lineal '{val[:24]}(...)'. No se admiten funciones en un sistema lineal.")
                if val.isalpha():
                    raise ValueError(f"Línea {linea}: variable sin índice '{val[:24]}'. Usa variables indexadas como x1, x_1 o x₁.")
                raise ValueError(f"Línea {linea}: nombre de variable inválido '{val[:24]}'. Usa una letra con índice entero positivo (ej. x1, x_1, x₁).")
            dig = mv.group(2).translate(_SUBINDICES).lstrip("0")
            if not dig:
                raise ValueError(f"Línea {linea}: índice inválido en '{val[:24]}'. Los índices deben iniciar en 1 (x1, x2, ...).")
            if len(dig) > 2 or int(dig) > _MAX_VARS:
                raise ValueError(f"Línea {linea}: el índice de '{val[:24]}' supera el máximo admitido ({_MAX_VARS}).")
            tokens.append(("VAR", (mv.group(1), int(dig), val)))
        elif kind == "OP":
            if val == "(":
                prof += 1
                if prof > _MAX_PROF:
                    raise ValueError(f"Línea {linea}: demasiados paréntesis anidados (máximo {_MAX_PROF}).")
            elif val == ")":
                prof -= 1
                if prof < 0:
                    raise ValueError(f"Línea {linea}: paréntesis de cierre ')' sin apertura.")
            tokens.append((val, val))
        elif val == ",":
            raise ValueError(f"Línea {linea}: carácter ',' no admitido. Usa punto decimal (ej. 0.5) en lugar de coma.")
        else:
            raise ValueError(f"Línea {linea}: carácter no reconocido '{val}'.")
        if len(tokens) > _MAX_TOKENS:
            raise ValueError(f"Línea {linea}: la expresión excede el límite de {_MAX_TOKENS} elementos por lado.")
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
                nv = _validar_magnitud(coeffs.get(k, Fraction(0)) + sign * v, self.linea)
                if nv == 0:
                    coeffs.pop(k, None)
                else:
                    coeffs[k] = nv
            acc = (coeffs, _validar_magnitud(acc[1] + sign * rhs[1], self.linea))
        return acc

    def _term(self) -> tuple[dict[tuple[str, int], Fraction], Fraction]:
        acc = self._unary()
        while (tok := self._peek()) and tok[0] in ("*", "/"):
            op = self._next()[0]
            rhs = self._unary()
            acc = self._mul(acc, rhs) if op == "*" else self._div(acc, rhs)
        return acc

    def _unary(self) -> tuple[dict[tuple[str, int], Fraction], Fraction]:
        signo = 1
        while (tok := self._peek()) and tok[0] in ("+", "-"):
            if self._next()[0] == "-":
                signo = -signo
        acc = self._primary()
        while (tok := self._peek()) and tok[0] in ("VAR", "("):
            acc = self._mul(acc, self._primary())
        return ({v: -val for v, val in acc[0].items()}, -acc[1]) if signo < 0 else acc

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
        return (
            {k: _validar_magnitud(v * s, self.linea) for k, v in a[0].items() if v * s != 0},
            _validar_magnitud(a[1] * s, self.linea),
        )

    def _div(self, a, b):
        if b[0]:
            raise ValueError(f"Línea {self.linea}: término no lineal (división entre una incógnita). Usa paréntesis para fracciones, ej. (1/2)x1.")
        if b[1] == 0:
            raise ValueError(f"Línea {self.linea}: división por cero.")
        return (
            {k: _validar_magnitud(v / b[1], self.linea) for k, v in a[0].items()},
            _validar_magnitud(a[1] / b[1], self.linea),
        )


def leer_ecuaciones(texto: str) -> tuple[list[list[Fraction]], list[Fraction], list[str]]:
    """Analiza un sistema lineal cuadrado (una ecuación por línea) en coeficientes Fraction exactos."""
    if not isinstance(texto, str):
        raise ValueError("El texto del sistema debe ser una cadena de caracteres.")
    if len(texto) > _MAX_TEXTO:
        raise ValueError(f"El texto excede el límite admitido de {_MAX_TEXTO} caracteres.")
    lineas: list[tuple[int, str]] = []
    for i, ln in enumerate(texto.splitlines(), 1):
        s = ln.strip()
        if not s:
            continue
        lineas.append((i, s))
        if len(lineas) > _MAX_VARS:
            raise ValueError(f"El sistema supera el máximo admitido de {_MAX_VARS} ecuaciones.")
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
        ecuaciones.append((c_izq, _validar_magnitud(k_der - k_izq, num)))

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
