"""Adaptadores puros: conservan valores, textos y pasos de las respuestas lineales."""
from copy import deepcopy
import re

from . import registrar
from .base import paso, procedimiento, tabla


def _matriz_latex(matriz):
    """Solo organiza las celdas ya serializadas; no convierte ni calcula números."""
    return r"\begin{pmatrix}" + r" \\ ".join(" & ".join(map(str, fila)) for fila in matriz) + r"\end{pmatrix}"


def _item(etiqueta, latex):
    if latex == "Sin solución":
        latex = r"\text{" + latex + "}"
    return {"etiqueta": etiqueta, "latex": re.sub(r"_(\d+)", r"_{\1}", str(latex))}


def _entradas(cuerpo, vectores=(), matrices=(), escalares=()):
    salida = [_item(k, _matriz_latex([[v] for v in cuerpo[k]])) for k in vectores if k in cuerpo]
    salida.extend(_item(k, _matriz_latex(cuerpo[k])) for k in matrices if k in cuerpo)
    salida.extend(_item(k, cuerpo[k]) for k in escalares if k in cuerpo)
    return salida


def _pasos(respuesta):
    for clave in ("pasos", "desglose_componentes", "pasos_multiplicacion", "pasos_mapeo"):
        if clave not in respuesta:
            continue
        salida = []
        for original in respuesta[clave]:
            if isinstance(original, str):
                formula = clave in ("pasos_multiplicacion", "pasos_mapeo") and "$" not in original
                salida.append(paso("", latex=[original]) if formula else paso(original))
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
    return procedimiento(modulo, respuesta.get("titulo_operacion", titulo), pasos=_pasos(respuesta),
                         avisos=[a.replace("**", "") for a in avisos])


@registrar("/api/vectores/operar")
def adaptar_vectores(respuesta, cuerpo):
    p = _base(respuesta, "vectores", "Vectores")
    p["entrada"] = _entradas(cuerpo, vectores=("u", "v"), escalares=("c",))
    p["resultado"] = [_item("Resultado", respuesta["resultado_str"])]
    return p


@registrar("/api/matrices/operar")
def adaptar_matrices(respuesta, cuerpo):
    p = _base(respuesta, "matrices", "Matrices")
    p["entrada"] = _entradas(cuerpo, matrices=("A", "B"), escalares=("k",))
    p["resultado"] = [_item("Resultado", _matriz_latex(respuesta["matriz_resultado"]))]
    p["verificacion"] = list(respuesta.get("propiedades", []))
    return p


@registrar("/api/vectores/combinacion")
def adaptar_combinacion(respuesta, cuerpo):
    p = _base(respuesta, "combinacion", "Combinación lineal")
    p["entrada"] = [_item(f"v_{j}", _matriz_latex([[v] for v in vector]))
                    for j, vector in enumerate(cuerpo.get("vectores", []), 1)]
    p["entrada"].extend(_entradas(cuerpo, vectores=("b",)))
    p["resultado"] = [_item(nombre, valor) for nombre, valor in respuesta["escalares"].items()]
    p["verificacion"] = list(respuesta["comprobacion"])
    if respuesta.get("independencia"):
        p["verificacion"].append(f"Conjunto linealmente {respuesta['independencia']}; "
                                 f"rango {respuesta['rango']}; {respuesta['numero_vectores']} vectores.")
        if respuesta.get("relacion"):
            p["verificacion"].extend([f"${respuesta['relacion']['latex']}$", f"${respuesta['despeje']}$"])
    p["avisos"].extend(respuesta[k] for k in ("tipo_solucion", "expresion_algebraica") if respuesta.get(k))
    return p


@registrar("/api/matrices/inversa")
def adaptar_inversa(respuesta, cuerpo):
    p = _base(respuesta, "inversa", "Inversa de una matriz")
    p["entrada"] = [_item(r"[A \mid I]", _matriz_latex(respuesta["matriz_aumentada_inicial"]))]
    if respuesta["matriz_inversa"] is not None:
        p["resultado"] = [_item(r"A^{-1}", _matriz_latex(respuesta["matriz_inversa"]))]
    p["verificacion"] = list(respuesta["verificacion_A_por_Ainv"]) + list(respuesta["verificacion_Ainv_por_A"])
    return p


@registrar("/api/ecuaciones/resolver")
def adaptar_ecuaciones(respuesta, cuerpo):
    p = _base(respuesta, "ecuaciones", "Ecuaciones matriciales")
    if p["pasos"] and p["pasos"][0]["matriz"]:
        p["entrada"] = [_item(r"[A \mid b]", _matriz_latex(p["pasos"][0]["matriz"]))]
    if respuesta.get("forma_matricial"):
        p["pasos"].insert(0, paso("Forma matricial $A\\cdot X = B$", latex=[respuesta["forma_matricial"]["latex"]]))
    p["resultado"] = [_item(nombre, valor) for nombre, valor in respuesta["solucion_dict"].items()]
    p["verificacion"] = list(respuesta["verificacion"])
    p["avisos"].extend(respuesta.get("sustitucion", []))
    return p


@registrar("/api/matrices/determinante")
def adaptar_determinante(respuesta, cuerpo):
    p = _base(respuesta, "determinante", "Determinante")
    if p["pasos"] and p["pasos"][0]["matriz"]:
        p["entrada"] = [_item("A", _matriz_latex(p["pasos"][0]["matriz"]))]
    p["resultado"] = [_item(r"\det(A)", respuesta["determinante"])]
    p["verificacion"] = ["Invertible: existe inversa única." if respuesta["es_invertible"]
                         else "No invertible: matriz singular, no existe inversa."]
    p["avisos"].append(f"Método: {respuesta['metodo']}; complejidad: {respuesta['complejidad_teorica']}; "
                       f"operaciones estimadas: {respuesta['operaciones_estimadas']}.")
    return p


@registrar("/api/matrices/eficiencia-determinante")
def adaptar_eficiencia(respuesta, cuerpo):
    p = _base(respuesta, "eficiencia-determinante", respuesta["metodo_recomendado_nombre"])
    p["entrada"] = [_item("n", respuesta["orden_n"])]
    p["resultado"] = [_item("Cofactores", respuesta["ops_cofactores"]), _item("LU", respuesta["ops_lu"])]
    p["tablas"] = [tabla("Operaciones estimadas", ["Cofactores", "LU"],
                        [[respuesta["ops_cofactores"], respuesta["ops_lu"]]])]
    p["avisos"] = [respuesta["justificacion"], respuesta["complejidad_cofactores"], respuesta["complejidad_lu"]]
    return p
