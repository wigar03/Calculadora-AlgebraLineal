"""Análisis racional de convergencia, sin dependencias externas.

Hasta n=12: polinomio exacto y Schur-Cohn estricto (incluye multiplicidades
y frontera). El radio mostrado se encierra por bisección racional usando el
mismo criterio sobre p(r*z); ningún autovalor flotante decide la garantía.
"""
from fractions import Fraction as F
from functools import reduce
from math import gcd, isfinite, lcm

LIMITE_ESPECTRAL = 12


def matriz_iteracion(A, metodo):
    """T_J=-D^-1(L+U), T_GS=-(D+L)^-1 U mediante sustitución exacta."""
    if metodo not in ("jacobi", "gauss_seidel"):
        raise ValueError("Método desconocido: usa jacobi o gauss_seidel.")
    A = [[F(v) for v in fila] for fila in A]
    n = len(A)
    if any(A[i][i] == 0 for i in range(n)):
        raise ValueError("No hay matriz de iteración con diagonal nula.")
    T = [[F(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if metodo == "jacobi":
                T[i][j] = -A[i][j] / A[i][i] if i != j else F(0)
            else:
                termino = -A[i][j] if j > i else F(0)
                T[i][j] = (termino - sum(A[i][k] * T[k][j]
                                        for k in range(i))) / A[i][i]
    return T


def polinomio_caracteristico(T):
    """Coeficientes descendentes de det(zI-T), Faddeev-LeVerrier exacto."""
    n = len(T)
    T = [[F(v) for v in fila] for fila in T]
    B = [[F(i == j) for j in range(n)] for i in range(n)]
    p = [F(1)]
    for k in range(1, n + 1):
        B = [[sum(T[i][s] * B[s][j] for s in range(n))
              for j in range(n)] for i in range(n)]
        c = -sum(B[i][i] for i in range(n)) / k
        p.append(c)
        for i in range(n):
            B[i][i] += c
    return p


def _primitivo(p):
    """Eliminar denominadores y contenido frena el crecimiento de enteros."""
    p = [F(v) for v in p]
    den = lcm(*(v.denominator for v in p))
    enteros = [int(v * den) for v in p]
    contenido = reduce(gcd, enteros)
    return [v // contenido for v in enteros]


def schur_estable(p):
    """Decide exactamente si TODAS las raíces están en |z|<1.

    Para p=a*z^n+...+b: se exige |b|<|a| y se reduce a
    (a*p-b*p_reciproco)/z. La igualdad rechaza la frontera, sin epsilon.
    """
    p = _primitivo(p)
    while len(p) > 1:
        a, b = p[0], p[-1]
        if abs(b) >= abs(a):
            return False
        p = _primitivo([a * p[i] - b * p[-1-i]
                        for i in range(len(p) - 1)])
    return p[0] != 0
