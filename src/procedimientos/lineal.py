"""Adaptadores puros: conservan valores, textos y pasos de las respuestas lineales."""
from copy import deepcopy

from . import registrar
from .base import paso, procedimiento, tabla


def _matriz_latex(matriz):
    """Solo organiza las celdas ya serializadas; no convierte ni calcula números."""
    return r"\begin{pmatrix}" + r" \\ ".join(" & ".join(map(str, fila)) for fila in matriz) + r"\end{pmatrix}"


def _item(etiqueta, latex):
    return {"etiqueta": etiqueta, "latex": str(latex)}


def _pasos(respuesta):
    for clave in ("pasos", "desglose_componentes", "pasos_multiplicacion", "pasos_mapeo"):
        if clave not in respuesta:
            continue
        salida = []
        for original in respuesta[clave]:
            if isinstance(original, str):
                salida.append(paso(original, original))
            else:
                salida.append(paso(original.get("titulo", original.get("title", "")),
                                   original.get("descripcion", original.get("description", "")),
                                   matriz=deepcopy(original.get("matriz_estado", original.get("matrix"))),
                                   detalles=original.get("detalles", [])))
        return salida
    return []


def _base(respuesta, modulo, titulo):
    avisos = [respuesta[k] for k in ("explicacion_teorica", "justificacion_teorica", "descripcion_sistema",
                                    "mensaje_diagnostico", "formula_2x2_detalle") if respuesta.get(k)]
    return procedimiento(modulo, respuesta.get("titulo_operacion", titulo), pasos=_pasos(respuesta), avisos=avisos)


@registrar("/api/vectores/operar")
def adaptar_vectores(respuesta, cuerpo):
    p = _base(respuesta, "vectores", "Vectores")
    p["resultado"] = [_item("Resultado", respuesta["resultado_str"])]
    return p


@registrar("/api/matrices/operar")
def adaptar_matrices(respuesta, cuerpo):
    p = _base(respuesta, "matrices", "Matrices")
    p["resultado"] = [_item("Resultado", _matriz_latex(respuesta["matriz_resultado"]))]
    p["verificacion"] = list(respuesta.get("propiedades", []))
    return p
