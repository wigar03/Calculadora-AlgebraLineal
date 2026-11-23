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


def _division(p, q):
    p, q = list(p), list(q)
    cociente = [F(0)] * max(1, len(p) - len(q) + 1)
    while len(p) >= len(q) and any(p):
        diferencia = len(p) - len(q)
        c = p[0] / q[0]
        cociente[len(cociente) - 1 - diferencia] = c
        for j in range(len(q)):
            p[j] -= c * q[j]
        while len(p) > 1 and p[0] == 0:
            p.pop(0)
    return cociente, p


def libre_de_cuadrados(p):
    """p/gcd(p,p'): mismas raíces, sin multiplicidades, todo racional."""
    p = [F(v) for v in p]
    n = len(p) - 1
    if n == 0:
        return p
    a, b = p, [p[i] * (n - i) for i in range(n)]
    while any(b):
        _, resto = _division(a, b)
        a, b = b, resto
    a = [v / a[0] for v in a]
    return _division(p, a)[0]


def radio_polinomio(p):
    """Aproxima el mayor módulo con un intervalo racional certificado.

    Bisección sobre la propiedad monótona «raíces de p(r*z) en |z|<1».
    Evita raíces complejas mal condicionadas, incluso matrices defectivas.
    Error absoluto <= max(1, 2*rho)*2^-38; solo el resultado final es float.
    """
    p = libre_de_cuadrados(p)
    if all(v == 0 for v in p[1:]):
        return 0.0
    n = len(p) - 1

    def dentro(r):
        return schur_estable([v * r ** (n - i) for i, v in enumerate(p)])

    superior = F(1)
    while not dentro(superior):
        superior *= 2
    inferior = F(0)
    for _ in range(38):
        medio = (inferior + superior) / 2
        if dentro(medio):
            superior = medio
        else:
            inferior = medio
    try:
        return float((inferior + superior) / 2)
    except OverflowError:
        return None  # no representable en doble; la decisión exacta se conserva


def analizar_espectro(A):
    """Radios para mostrar y decisiones exactas separadas para cada método."""
    radios = {"jacobi": None, "gauss_seidel": None}
    estables = {"jacobi": None, "gauss_seidel": None}
    calculo = "No calculado: diagonal nula o dimensión mayor que 12."
    if len(A) <= LIMITE_ESPECTRAL and all(A[i][i] != 0 for i in range(len(A))):
        calculo = "Faddeev-LeVerrier y Schur-Cohn exactos; radio por bisección racional."
        for metodo in estables:
            p = polinomio_caracteristico(matriz_iteracion(A, metodo))
            estables[metodo] = schur_estable(p)
            radios[metodo] = radio_polinomio(p)
    return {**radios, "metodo_calculo": calculo}, estables
