"""Resolvedor iterativo y comparación, con verificación de residuo obligatoria."""
import math

from .convergencia import (analizar_espectro, garantia_convergencia, medir_cambio,
                           cumple_tolerancia, detectar_parada)
from .gauss_seidel import paso_gauss_seidel

MENSAJES = {
    "tolerancia": "Se cumple el criterio solicitado y el residuo relativo exigido.",
    "max_iteraciones": "Se alcanzó el máximo de iteraciones sin cumplir la tolerancia.",
    "divergencia": "Cambio y residuo crecen de forma sostenida; la iteración diverge.",
    "no_finito": "Apareció un valor no finito; revisa la escala y el método elegido.",
    "estancamiento": "La iteración se estancó sin alcanzar la tolerancia solicitada.",
    "oscilacion": "Se detectó un ciclo de iteraciones sin alcanzar la tolerancia.",
    "diagonal_nula": "Hay un cero en la diagonal; intenta reordenar las ecuaciones.",
    "singular": "El sistema es singular y no tiene solución única; no se itera.",
    "incompatible": "El rango aumentado supera al de A: el sistema no tiene solución.",
}


def _opciones(metodo, tolerancia, max_iteraciones, criterio, reordenar):
    if metodo not in ("jacobi", "gauss_seidel"):
        raise ValueError("Método inválido: elige jacobi o gauss_seidel.")
    try:
        tol = float(tolerancia)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("La tolerancia debe ser un número positivo finito.") from exc
    if isinstance(tolerancia, bool) or not math.isfinite(tol) or tol <= 0:
        raise ValueError("La tolerancia debe ser un número positivo finito.")
    if (type(max_iteraciones) is not int or not 1 <= max_iteraciones <= 10000):
        raise ValueError("El máximo de iteraciones debe ser un entero entre 1 y 10000.")
    if criterio not in ("ambos", "cambio", "residuo"):
        raise ValueError("Criterio inválido: elige ambos, cambio o residuo.")
    if type(reordenar) is not bool:
        raise ValueError("Reordenar debe ser verdadero o falso.")
    return tol


def _preparar(A, b, x0, metodo, ordenar):
    from .entrada import leer_sistema
    from .matriz import (dominancia_diagonal, diagonal_nula, reordenar, rangos)

    A, b, x0 = leer_sistema(A, b, x0)
    orden = {"aplicado": False, "permutacion": list(range(len(b))),
             "motivo": "Se conserva el orden original de las ecuaciones."}
    if ordenar:
        A, b, orden = reordenar(A, b)
    rango = rangos(A, b)
    dominancia = dominancia_diagonal(A)
    radios, estables = analizar_espectro(A)
    garantia, razones = garantia_convergencia(A, metodo, dominancia["estricta"],
                                              estables[metodo])
    analisis = {"diagonal_nula": diagonal_nula(A), "dominancia": dominancia,
                "reordenamiento": orden, "rango": {"A": rango["A"],
                "aumentada": rango["aumentada"]}, "singular": rango["singular"],
                "radio_espectral": radios, "garantia": garantia, "razones": razones}
    return A, b, x0, analisis


def analizar_sistema(A, b, metodo="jacobi", x0=None, reordenar=False):
    """Análisis sin iterar, usado por /api/iterativos/analizar."""
    _opciones(metodo, 1e-6, 100, "ambos", reordenar)
    return _preparar(A, b, x0, metodo, reordenar)[3]
