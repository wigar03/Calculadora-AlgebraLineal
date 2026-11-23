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
