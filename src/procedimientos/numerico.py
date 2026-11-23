"""Adaptadores puros al formato común de procedimientos para los módulos numéricos."""
import math
import re

from . import registrar
from .base import paso, procedimiento, tabla

MOTIVOS_BISECCION = {
    "tolerancia": "Se alcanzó la tolerancia del criterio seleccionado.",
    "raiz_en_extremo": "La función se evaluó como cero en un extremo del intervalo; no se requieren iteraciones.",
    "raiz_evaluada": "$f(c)$ se evaluó como cero con la precisión de punto flotante utilizada.",
    "max_iteraciones": "Se alcanzó el máximo de iteraciones sin cumplir la tolerancia.",
    "precision_agotada": "La precisión de punto flotante impide seguir reduciendo el intervalo.",
    "raiz_no_admisible": "La aproximación obtenida no cumple la condición pedida.",
    "no_certificada": "No se pudo certificar una raíz admisible cercana con cambio de signo continuo.",
}


def _num(v):
    if v is None:
        return r"\text{---}"
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, (int, float)):
        if isinstance(v, float) and not math.isfinite(v):
            return r"\text{no finito}"
        s = str(v)
        if "e" in s.lower():
            base, exp = s.lower().split("e")
            return f"{base} \\times 10^{{{int(exp)}}}"
        return s
    s = str(v).strip()
    m = re.fullmatch(r"([+-]?)(\d+)\s*/\s*(\d+)", s)
    return (f"{'-' if m.group(1) == '-' else ''}\\frac{{{m.group(2)}}}{{{m.group(3)}}}" if m else s)


def _var(nombre, idx=0):
    raw = nombre.strip() if isinstance(nombre, str) and nombre.strip() else f"x_{idx + 1}"
    if "_" in raw:
        return re.sub(r"_\{?([0-9a-zA-Z]+)\}?", r"_{\1}", raw)
    return re.sub(r"^([a-zA-Z]+)(\d+)$", r"\1_{\2}", raw)


def _vec(vec):
    if not vec:
        return "(0)"
    items = [_num(v) for v in vec]
    if len(items) > 4:
        return r"\left(" + r",\; ".join(items) + r"\right)^T"
    return r"\begin{pmatrix} " + r" \\ ".join(items) + r" \end{pmatrix}"


def _mat(A):
    filas = [" & ".join(_num(v) for v in fila) for fila in A]
    return r"\begin{pmatrix} " + r" \\ ".join(filas) + r" \end{pmatrix}"


@registrar("/api/biseccion/resolver")
def adaptar_biseccion(res, _cuerpo):
    a0, b0 = res["intervalo_inicial"]
    af, bf = res["intervalo_final"]
    crit, tol = res["criterio"], res["tolerancia"]
    suf = r"\,\%" if crit == "relativo" else ""
    verif = [f"Verificación: $f({_num(res['raiz'])}) = {_num(res['f_raiz'])}$.",
             f"Intervalo final: $[{_num(af)},\\; {_num(bf)}]$."]
    if (res.get("verificacion") or {}).get("nota"):
        verif.append(res["verificacion"]["nota"])
    filas = [[p["numero"], p["a"], p["b"], p["c"], p["fc"], p["error_relativo"]] for p in res.get("pasos", ())]
    avisos = [r"La cota del intervalo supone continuidad en $[a,b]$."]
    if not res.get("convergio"):
        avisos.append("Tolerancia no alcanzada.")
    return procedimiento(
        "biseccion", "Método de bisección",
        entrada=[{"etiqueta": "f(x)", "latex": res.get("funcion_latex") or str(res.get("funcion", ""))},
                 {"etiqueta": "[a, b]", "latex": f"[{_num(a0)},\\; {_num(b0)}]"},
                 {"etiqueta": r"\varepsilon", "latex": f"{_num(tol)}{suf}"}],
        pasos=[paso("Fórmula y criterio de parada", MOTIVOS_BISECCION.get(res["motivo"], res["motivo"]),
                    latex=[r"c = \frac{a + b}{2}"],
                    detalles=[f"Criterio: {crit}. Tolerancia: ${_num(tol)}{suf}$."])],
        resultado=[{"etiqueta": "c", "latex": _num(res["raiz"])},
                   {"etiqueta": "|f(c)|", "latex": _num(res["residuo"])},
                   {"etiqueta": r"\text{Cota}", "latex": _num(res["cota_error"])},
                   {"etiqueta": r"\text{Iteraciones}", "latex": str(res["iteraciones"])}],
        verificacion=verif,
        tablas=[tabla("Iteraciones de bisección", ["i", "a", "b", "c", "f(c)", r"\varepsilon_a\;(\%)"], filas)],
        avisos=avisos,
    )


@registrar("/api/derivadas/derivar")
def adaptar_derivadas(res, _cuerpo):
    fl, dl = res["funcion_latex"], res["derivada_latex"]
    return procedimiento(
        "derivadas", "Derivada simbólica",
        entrada=[{"etiqueta": "f(x)", "latex": fl}],
        pasos=[paso("Derivación simbólica", "Derivada simbólica obtenida de la expresión de entrada.",
                    latex=[f"f(x) = {fl}", f"f'(x) = {dl}"],
                    detalles=[f"Sintaxis editable: {res['derivada']}"])],
        resultado=[{"etiqueta": "f'(x)", "latex": dl}],
    )
