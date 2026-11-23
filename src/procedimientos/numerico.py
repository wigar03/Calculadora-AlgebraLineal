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


MOTIVOS_RF = {**MOTIVOS_BISECCION,
              "tolerancia": r"Se alcanzó la tolerancia: $\varepsilon_a \le \varepsilon_s$.",
              "raiz_evaluada": r"$f(x_r)$ se evaluó como cero con la precisión de punto flotante utilizada.",
              "sin_progreso": r"La precisión de punto flotante impide que $x_r$ siga avanzando."}

MOTIVOS_ABIERTO = {
    **MOTIVOS_BISECCION, "raiz_en_x0": r"$f(x_0)=0$: el punto elegido ya es una raíz.",
    "raiz_inicial": "Uno de los valores iniciales ya es una raíz.",
    "raiz_evaluada": r"$f(x_n)$ se evaluó como cero con la precisión de punto flotante utilizada.",
    "derivada_nula": r"$f'(x_n)=0$: la tangente es horizontal.",
    "derivada_no_definida": "La derivada no se puede evaluar en este punto.",
    "denominador_nulo": "Las dos evaluaciones son iguales: el denominador es cero.",
    "fuera_de_dominio": "Una aproximación queda fuera del dominio real de la función.",
    "divergencia": "La siguiente aproximación no es finita.", "ciclo": "Las aproximaciones forman un ciclo.",
    "sin_progreso": "La precisión de punto flotante impide seguir avanzando.",
}


def _verif_abiertos(res):
    verif = []
    cumple, cercana = res.get("cumple") or {}, res.get("cumple_cercana") or {}
    for k, sym in (("absoluto", "E_a"), ("relativo", r"\varepsilon_r"), ("residuo", "|f(x_n)|")):
        simb = "✓" if cumple.get(k) else ("≈" if cercana.get(k) else "✗")
        sel = " (seleccionado)" if res.get("criterio") == k else ""
        verif.append(f"{simb} ${sym} < \\varepsilon${sel}.")
    info = res.get("tolerancia_usada") or {}
    if info:
        eps = f"$\\varepsilon={_num(info.get('digitada'))}$"
        val = (f"valor final ${_num(info.get('valor_final'))}$"
               if info.get("valor_final") is not None else "criterio no definido")
        if info.get("usada") == "digitada":
            verif.append(f"Se usó la tolerancia digitada {eps}: {val}.")
        elif info.get("usada") == "cercana":
            verif.append(f"Se usó tolerancia cercana a {eps} (límite ${_num(info.get('limite'))}$): {val}.")
        else:
            verif.append(f"No se alcanzó {eps} (límite ${_num(info.get('limite'))}$): {val}.")
    verif.append(f"Verificación: $f({_num(res['raiz'])}) = {_num(res['f_raiz'])}$.")
    if (res.get("verificacion") or {}).get("nota"):
        verif.append(res["verificacion"]["nota"])
    return verif


@registrar("/api/regla-falsa/resolver")
def adaptar_regla_falsa(res, _cuerpo):
    xl0, xu0 = res["intervalo_inicial"]
    xlf, xuf = res["intervalo_final"]
    verif = [f"Verificación: $f({_num(res['raiz'])}) = {_num(res['f_raiz'])}$. "
             f"Intervalo final: $[{_num(xlf)},\\; {_num(xuf)}]$."]
    if (res.get("verificacion") or {}).get("nota"):
        verif.append(res["verificacion"]["nota"])
    filas = [[p["numero"], p["xl"], p["xu"], p["f_xl"], p["f_xu"], p["xr"], p["f_xr"],
              p["error_relativo"], p["decision"]] for p in res.get("pasos", ())]
    avisos = []
    if res.get("estancamiento"):
        fijo = "x_l" if res["estancamiento"]["extremo"] == "xl" else "x_u"
        avisos.append(f"Estancamiento: ${fijo}$ permaneció fijo durante {res['estancamiento']['iteraciones']} iteraciones.")
    if not res.get("convergio"):
        avisos.append("Tolerancia no alcanzada.")
    return procedimiento(
        "regla_falsa", "Método de regla falsa",
        entrada=[{"etiqueta": "f(x)", "latex": res.get("funcion_latex") or str(res.get("funcion", ""))},
                 {"etiqueta": "[x_l, x_u]", "latex": f"[{_num(xl0)},\\; {_num(xu0)}]"},
                 {"etiqueta": r"\varepsilon_s", "latex": f"{_num(res['tolerancia'])}\\,\\%"}],
        pasos=[paso("Fórmula de la regla falsa", MOTIVOS_RF.get(res["motivo"], res["motivo"]),
                    latex=[r"x_r = x_u - \frac{f(x_u)(x_l - x_u)}{f(x_l) - f(x_u)}"])],
        resultado=[{"etiqueta": "x_r", "latex": _num(res["raiz"])},
                   {"etiqueta": "|f(x_r)|", "latex": _num(res["residuo"])},
                   {"etiqueta": r"\varepsilon_a\;(\%)", "latex": _num(res["error_relativo"])},
                   {"etiqueta": r"\text{Iteraciones}", "latex": str(res["iteraciones"])}],
        verificacion=verif,
        tablas=[tabla("Iteraciones de regla falsa",
                      ["i", "x_l", "x_u", "f(x_l)", "f(x_u)", "x_r", "f(x_r)",
                       r"\varepsilon_a\;(\%)", r"\text{Acción}"], filas)],
        avisos=avisos,
    )
