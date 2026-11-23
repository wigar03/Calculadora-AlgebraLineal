"""Diagnósticos matriciales y residuo; índices base 0, filas completas al reordenar."""

from math import inf, isfinite

from src.solver.gauss_solver import solve_gaussian_elimination
from .entrada import leer_sistema


def dominancia_diagonal(A):
    """Compara sin tolerancias; las magnitudes informadas son float para JSON."""
    filas = []
    for i, fila in enumerate(A):
        diagonal = abs(fila[i])
        suma = sum(abs(v) for j, v in enumerate(fila) if j != i)
        filas.append({"i": i, "diagonal": float(diagonal), "suma": float(suma),
                      "cumple": diagonal > suma, "no_estricta": diagonal >= suma})
    return {"filas": filas, "estricta": all(f["cumple"] for f in filas),
            "no_estricta": all(f["no_estricta"] for f in filas)}


def diagonal_nula(A):
    """Posiciones de ceros exactos en la diagonal, sin confundir pivotes pequeños con cero."""
    return [i for i, fila in enumerate(A) if fila[i] == 0]


def _asignacion(candidatas):
    """Asigna una ecuación diferente a cada posición diagonal.

    Hasta n=8, backtracking exhaustivo podado (a lo sumo 109601 nodos).
    Para n>8, preferencia heurística de candidatos y caminos aumentantes:
    evita n!, pero sigue encontrando una asignación completa si existe.
    La heurística decide qué asignación elegir, no demuestra convergencia.
    """
    n = len(candidatas)
    columnas = sorted(range(n), key=lambda c: (len(candidatas[c]), c))
    permutacion = [-1] * n
    if n <= 8:
        def buscar(k, usadas):
            if k == n:
                return True
            col = columnas[k]
            for fila in candidatas[col]:
                if fila not in usadas:
                    permutacion[col] = fila
                    if buscar(k + 1, usadas | {fila}):
                        return True
            return False
        return permutacion if buscar(0, set()) else None

    asignadas = {}

    def aumentar(col, vistas):
        for fila in candidatas[col]:
            if fila in vistas:
                continue
            vistas.add(fila)
            if fila not in asignadas or aumentar(asignadas[fila], vistas):
                asignadas[fila] = col
                return True
        return False

    for col in columnas:
        if not aumentar(col, set()):
            return None
    for fila, col in asignadas.items():
        permutacion[col] = fila
    return permutacion


def _candidatas(A, estrictas):
    """Prioriza |a_ij| / suma(|fila|), conservando el orden ante empates."""
    totales = [sum(abs(v) for v in fila) for fila in A]
    resultado = []
    for col in range(len(A)):
        filas = [i for i, fila in enumerate(A) if fila[col] != 0 and
                 (not estrictas or 2 * abs(fila[col]) > totales[i])]
        filas.sort(key=lambda i: (abs(A[i][col]) / totales[i], i == col, -i),
                   reverse=True)
        resultado.append(filas)
    return resultado


def reordenar(A, b):
    """Permuta filas de A y b conjuntamente; nunca columnas ni componentes de x.

    Primero busca dominancia estricta. Si no existe, conserva un orden sin
    ceros diagonales o busca uno; si es imposible, devuelve copias originales.
    permutacion[k] identifica la ecuación original situada ahora en la fila k.
    """
    A, b, _ = leer_sistema(A, b)
    identidad = list(range(len(A)))
    estrategia = ("búsqueda exhaustiva acotada" if len(A) <= 8 else
                  "preferencia heurística y asignación por caminos aumentantes")
    if dominancia_diagonal(A)["estricta"]:
        permutacion = identidad
        motivo = "El orden original ya tiene dominancia diagonal estricta."
    else:
        permutacion = _asignacion(_candidatas(A, estrictas=True))
        if permutacion is not None:
            motivo = f"Se obtuvo dominancia diagonal estricta mediante {estrategia}."
        elif not diagonal_nula(A):
            permutacion = identidad
            motivo = ("La diagonal original no tiene ceros; ninguna permutación "
                      "de ecuaciones proporciona dominancia diagonal estricta.")
        else:
            permutacion = _asignacion(_candidatas(A, estrictas=False))
            if permutacion is None:
                permutacion = identidad
                motivo = ("No existe una permutación de ecuaciones que elimine la diagonal "
                          "nula: no hay asignación completa de coeficientes no nulos.")
            else:
                motivo = (f"Se eliminó la diagonal nula mediante {estrategia}; ninguna "
                          "permutación proporciona dominancia diagonal estricta.")
    return ([A[i][:] for i in permutacion], [b[i] for i in permutacion],
            {"aplicado": permutacion != identidad, "permutacion": permutacion, "motivo": motivo})


def rangos(A, b):
    """Rangos y singularidad por el motor Gauss racional ya existente."""
    A, b, _ = leer_sistema(A, b)
    resultado = solve_gaussian_elimination([fila + [b[i]] for i, fila in enumerate(A)],
                                           use_gauss_jordan=False)
    return {"A": resultado.rank_A, "aumentada": resultado.rank_Aug,
            "singular": resultado.rank_A < len(A)}


def residuo(A, b, x):
    """Calcula b − Ax y su norma relativa con la norma matricial infinito por filas.

    Recibe los datos numéricos ya normalizados; los no finitos nunca producen
    un residuo relativo finito que pueda confundirse con convergencia.
    """
    Ax = [sum((a * v for a, v in zip(fila, x)), 0.0) for fila in A]
    r = [bi - axi for bi, axi in zip(b, Ax)]
    norma = max(abs(v) for v in r)
    if not all(isfinite(v) for v in (*b, *x, *Ax, *r)):
        return {"Ax": Ax, "residuo": r, "residuo_inf": inf, "residuo_rel": inf}
    norma_A = max(sum(abs(v) for v in fila) for fila in A)
    norma_b, norma_x = max(abs(v) for v in b), max(abs(v) for v in x)
    denominador = norma_b + norma_A * norma_x
    relativo = norma / denominador if denominador else norma
    return {"Ax": Ax, "residuo": r, "residuo_inf": norma, "residuo_rel": relativo}
