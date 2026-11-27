"""Resolvedor iterativo y comparación, con verificación de residuo obligatoria."""
import math
import re
from fractions import Fraction

from ..biseccion.expresiones import numero_real
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
    "precision_insuficiente": "La verificación exacta final no cumple la tolerancia; "
                             "la precisión flotante es insuficiente.",
}


def _opciones(metodo, tolerancia, max_iteraciones, criterio, reordenar):
    """Normaliza controles HTML: entero decimal y booleano true/false en texto."""
    if metodo not in ("jacobi", "gauss_seidel"):
        raise ValueError("Método inválido: elige jacobi o gauss_seidel.")
    if isinstance(tolerancia, str) and "," in tolerancia:
        raise ValueError(f"No se admite la coma ',' en '{tolerancia.strip()}'. Use punto decimal '.' (por ejemplo, 0.5).")
    try:
        tol = numero_real(tolerancia, "La tolerancia")
    except ValueError as exc:
        raise ValueError("La tolerancia debe ser un número positivo finito.") from exc
    if tol <= 0:
        raise ValueError("La tolerancia debe ser un número positivo finito.")
    if isinstance(max_iteraciones, str) and re.fullmatch(r"[0-9]+", max_iteraciones.strip()):
        try:
            max_iteraciones = int(max_iteraciones)
        except ValueError:
            pass  # entero de miles de cifras: se rechaza con el mismo mensaje localizado
    if type(max_iteraciones) is not int or not 1 <= max_iteraciones <= 10000:
        raise ValueError("El máximo de iteraciones debe ser un entero decimal entre 1 y 10000; "
                         "escribe 100, sin decimales ni exponentes.")
    if criterio not in ("ambos", "cambio", "residuo"):
        raise ValueError("Criterio inválido: elige ambos, cambio o residuo.")
    if isinstance(reordenar, str) and reordenar.strip().lower() in ("true", "false"):
        reordenar = reordenar.strip().lower() == "true"
    if type(reordenar) is not bool:
        raise ValueError("Reordenar debe ser verdadero o falso.")
    return tol, max_iteraciones, reordenar


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
    _, _, reordenar = _opciones(metodo, 1e-6, 100, "ambos", reordenar)
    return _preparar(A, b, x0, metodo, reordenar)[3]


def _finito(valor):
    if isinstance(valor, dict):
        return all(_finito(v) for v in valor.values())
    if isinstance(valor, (list, tuple)):
        return all(_finito(v) for v in valor)
    return not isinstance(valor, float) or math.isfinite(valor)


def _json_finito(valor):
    if isinstance(valor, dict):
        return {k: _json_finito(v) for k, v in valor.items()}
    if isinstance(valor, list):
        return [_json_finito(v) for v in valor]
    return valor if _finito(valor) else None


def _verificar(A, b, x):
    from .matriz import residuo
    # La primitiva protege el cociente cuando su escala auxiliar desborda.
    return residuo(A, b, x)


def _verificar_final(A, b, x, tolerancia):
    """Una única comprobación racional sobre los floats que realmente iteraron.

    Fraction(float) conserva su racional binario exacto. La comparación se hace
    antes de redondear los valores que se muestran en JSON.
    """
    Q = [[Fraction(a) for a in fila] for fila in A]
    B, X = list(map(Fraction, b)), list(map(Fraction, x))
    Ax = [sum(a * v for a, v in zip(fila, X)) for fila in Q]
    residuos = [bi - axi for bi, axi in zip(B, Ax)]
    norma = max(map(abs, residuos))
    escala = max(map(abs, B)) + max(sum(map(abs, fila)) for fila in Q) * max(map(abs, X))
    relativo = norma / escala if escala else norma

    def mostrar(valor):
        try:
            return float(valor)
        except OverflowError:
            return math.inf if valor > 0 else -math.inf

    verificacion = {"Ax": list(map(mostrar, Ax)), "residuo": list(map(mostrar, residuos)),
                    "residuo_inf": mostrar(norma), "residuo_rel": mostrar(relativo)}
    verificacion["cumple"] = relativo <= Fraction(tolerancia) and _finito(verificacion)
    return verificacion


def resolver_iterativo(A, b, metodo, x0=None, tolerancia=1e-6,
                       max_iteraciones=100, criterio="ambos", reordenar=False):
    from .entrada import sistema_float
    from .jacobi import paso_jacobi

    tol, max_iteraciones, reordenar = _opciones(
        metodo, tolerancia, max_iteraciones, criterio, reordenar)
    A, b, x0, analisis = _preparar(A, b, x0, metodo, reordenar)
    A, b, x0 = sistema_float(A, b, x0)
    x, historial, vectores = list(x0), [], [list(x0)]
    motivo, convergio = "max_iteraciones", False
    if analisis["rango"]["aumentada"] > analisis["rango"]["A"]:
        motivo = "incompatible"
    elif analisis["singular"]:
        motivo = "singular"
    elif analisis["diagonal_nula"]:
        motivo = "diagonal_nula"
    else:
        paso = paso_jacobi if metodo == "jacobi" else paso_gauss_seidel
        for k in range(1, max_iteraciones + 1):
            try:
                nuevo, detalle = paso(A, b, x)
                cambio, relativo = medir_cambio(x, nuevo)
                verificacion = _verificar(A, b, nuevo)
            except (OverflowError, FloatingPointError):
                motivo = "no_finito"
                break
            if not _finito([nuevo, cambio, relativo, verificacion]):
                motivo = "no_finito"
                break
            fila = {"k": k, "x": nuevo, "cambio_inf": cambio,
                    "cambio_rel": relativo, "residuo_inf": verificacion["residuo_inf"],
                    "residuo_rel": verificacion["residuo_rel"]}
            if k <= 3:
                fila["detalle"] = detalle
            historial.append(fila)
            x = nuevo
            vectores = (vectores + [nuevo])[-9:]
            if cumple_tolerancia(relativo, verificacion["residuo_rel"], tol, criterio):
                motivo = "tolerancia"  # candidata; la verificación exacta final decide
                break
            detectado = detectar_parada(historial, vectores)
            if detectado == "divergencia" and analisis["garantia"] == "demostrada":
                # Una matriz no normal estable puede tener transitorios crecientes.
                # La garantía exacta prevalece sobre esta heurística de crecimiento.
                detectado = None
            if detectado:
                motivo = detectado
                break
    verificacion = _verificar_final(A, b, x, tol)
    convergio = motivo == "tolerancia" and verificacion["cumple"]
    if motivo == "tolerancia" and not convergio:
        motivo = "precision_insuficiente"
    categoria = analisis["garantia"]
    if convergio and categoria != "demostrada":
        categoria = "observada"
    return _json_finito({"metodo": metodo, "n": len(b),
        "nombres": [f"x_{i + 1}" for i in range(len(b))], "A": A, "b": b,
        "x0": x0, "tolerancia": tol, "criterio": criterio,
        "max_iteraciones": max_iteraciones, "iteraciones": historial, "solucion": x,
        "convergio": convergio, "motivo": motivo, "mensaje": MENSAJES[motivo],
        "verificacion": verificacion, "analisis": analisis, "convergencia": categoria})


def comparar_metodos(A, b, x0=None, tolerancia=1e-6, max_iteraciones=100,
                     criterio="ambos", reordenar=False):
    """Mismos datos y parada para ambos; se informa lo realmente observado."""
    resultados = {metodo: resolver_iterativo(A, b, metodo, x0, tolerancia,
        max_iteraciones, criterio, reordenar) for metodo in ("jacobi", "gauss_seidel")}
    j, gs = resultados["jacobi"], resultados["gauss_seidel"]
    if j["convergio"] and gs["convergio"]:
        nj, ng = len(j["iteraciones"]), len(gs["iteraciones"])
        resumen = (f"Ambos alcanzaron la tolerancia: Jacobi en {nj} iteraciones "
                   f"y Gauss-Seidel en {ng}. La rapidez depende del sistema.")
    else:
        resumen = (f"Jacobi: {j['mensaje']} Gauss-Seidel: {gs['mensaje']} "
                   "Los dos métodos pueden tener distinta convergencia.")
    return {**resultados, "resumen": resumen}
