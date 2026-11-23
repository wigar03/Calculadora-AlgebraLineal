"""Genera `referencias_iterativos.json` sin importar `src/`: iteraciones exactas, solución y radios espectrales.

Uso: python tests/validacion/generar_referencias_iterativos.py   (requiere sympy)
"""
import json
import os
import sys
from fractions import Fraction as Fr

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from banco_iterativos import CASOS  # noqa: E402

ITERACIONES_EXACTAS = 3


def jacobi(A, b, x):
    n = len(b)
    return [(b[i] - sum(A[i][j] * x[j] for j in range(n) if j != i)) / A[i][i] for i in range(n)]


def gauss_seidel(A, b, x):
    x, n = list(x), len(b)
    for i in range(n):
        x[i] = (b[i] - sum(A[i][j] * x[j] for j in range(n) if j != i)) / A[i][i]
    return x


def radio(A, metodo):
    """Exacto: raíces del polinomio característico racional (mpmath eig falla en matrices defectivas)."""
    M = sp.Matrix(A)
    n = M.rows
    D = sp.diag(*[M[i, i] for i in range(n)])
    L = sp.Matrix(n, n, lambda i, j: M[i, j] if i > j else 0)
    T = -D.inv() * (M - D) if metodo == "jacobi" else -(D + L).inv() * (M - D - L)
    raices = sp.Poly(T.charpoly().as_expr()).sqf_part().nroots(n=30, maxsteps=500)  # mismas raíces, simples
    return str(sp.Float(max(abs(r) for r in raices), 20))


def caso(c):
    A = [[Fr(v) for v in fila] for fila in c["A"]]
    b = [Fr(v) for v in c["b"]]
    n = len(b)
    M, B = sp.Matrix(A), sp.Matrix(b)
    ref = {"rango_A": M.rank(), "rango_aumentada": M.row_join(B).rank(),
           "diagonal_nula": [i for i in range(n) if A[i][i] == 0]}
    if ref["rango_A"] == ref["rango_aumentada"] == n:
        ref["solucion"] = [str(v) for v in M.LUsolve(B)]
    if not ref["diagonal_nula"]:
        ref["radio_espectral"] = {m: radio(A, m) for m in ("jacobi", "gauss_seidel")}
        x0 = [Fr(v) for v in c.get("x0", ["0"] * n)]
        for nombre, paso in (("jacobi", jacobi), ("gauss_seidel", gauss_seidel)):
            x, lista = x0, []
            for _ in range(ITERACIONES_EXACTAS):
                x = paso(A, b, x)
                lista.append([str(v) for v in x])
            ref["iteraciones_" + nombre] = lista
    return ref


def main():
    datos = {k: caso(c) for k, c in CASOS.items()}
    destino = os.path.join(os.path.dirname(os.path.abspath(__file__)), "referencias_iterativos.json")
    with open(destino, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(datos, fh, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        fh.write("\n")
    print("Referencias escritas en", destino)


if __name__ == "__main__":
    main()
