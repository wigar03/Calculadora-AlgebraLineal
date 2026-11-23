"""Genera `referencias.json` con SymPy y mpmath, sin importar nada de `src/`.

Uso: python tests/validacion/generar_referencias.py   (requiere sympy y mpmath; las pruebas no los necesitan)
"""
import json
import os
import sys

import mpmath as mp
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from banco_lineales import SISTEMAS  # noqa: E402
from banco_matrices import MATRICES  # noqa: E402
from banco_raices import ECUACIONES  # noqa: E402

mp.mp.dps = 50
X = sp.Symbol("x")


def lineal(s):
    A = sp.Matrix([[sp.Rational(c) for c in fila] for fila in s["A"]])
    b = sp.Matrix([sp.Rational(c) for c in s["b"]])
    r, ra = A.rank(), A.row_join(b).rank()
    tipo = "unica" if r == ra == A.cols else ("infinitas" if r == ra else "incompatible")
    ref = {"tipo": tipo, "rango_A": r, "rango_aumentada": ra}
    if tipo == "unica":
        ref["solucion"] = [str(v) for v in A.LUsolve(b)]
    return ref


def matriz(m):
    A = sp.Matrix(m)
    det = A.det()
    ref = {"det": str(det), "invertible": det != 0}
    if det != 0:
        ref["inversa"] = [[str(v) for v in fila] for fila in A.inv().tolist()]
    return ref


def raices(funcion, a=-10, b=10, n=40000):
    expr = sp.sympify(funcion.replace("^", "**"), locals={"ln": sp.log})
    f = sp.lambdify(X, expr, "mpmath")

    def valor(x):
        try:
            v = f(x)
        except (ValueError, ZeroDivisionError):
            return None
        return v if mp.im(v) == 0 and mp.isfinite(v) else None

    xs = [mp.mpf(a) + mp.mpf(b - a) * i / n for i in range(n + 1)]
    vs = [valor(x) for x in xs]
    encontradas = []
    for i in range(n):
        u, v = vs[i], vs[i + 1]
        if u is None or v is None or mp.sign(u) == mp.sign(v) and u != 0:
            continue
        try:
            r = xs[i] if u == 0 else mp.findroot(f, (xs[i], xs[i + 1]), solver="bisect")
        except ValueError:  # cambio de signo por un polo: no hay raíz
            continue
        if valor(r) is not None and abs(valor(r)) < mp.mpf("1e-30"):
            if not any(abs(r - e) < mp.mpf("1e-20") for e in encontradas):
                encontradas.append(mp.re(r))
    return [mp.nstr(r, 30) for r in encontradas]


def main():
    datos = {
        "lineales": {k: lineal(s) for k, s in SISTEMAS.items()},
        "matrices": {k: matriz(m) for k, m in MATRICES.items()},
        "raices": {k: {"raices_en_[-10,10]": raices(e["funcion"])} for k, e in ECUACIONES.items()},
    }
    destino = os.path.join(os.path.dirname(os.path.abspath(__file__)), "referencias.json")
    with open(destino, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(datos, fh, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        fh.write("\n")
    print("Referencias escritas en", destino)


if __name__ == "__main__":
    main()
