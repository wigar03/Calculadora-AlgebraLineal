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


def _convergencia(res):
    obs = res.get("convergencia_observada")
    if not obs:
        return []
    return [paso("Convergencia observada", obs["texto"],
                 latex=[r"e_k = |x_k-x_{k-1}|",
                        r"p_k \approx \frac{\ln(e_{k+1}/e_k)}{\ln(e_k/e_{k-1})}",
                        r"C_k \approx \frac{e_{k+1}}{e_k^p}"],
                 detalles=[obs["explicacion"]])]


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
        avisos.append(MOTIVOS_BISECCION.get(res["motivo"], res["motivo"]))
    return procedimiento(
        "biseccion", "Método de bisección",
        entrada=[{"etiqueta": "f(x)", "latex": res.get("funcion_latex") or str(res.get("funcion", ""))},
                 {"etiqueta": "[a, b]", "latex": f"[{_num(a0)},\\; {_num(b0)}]"},
                 {"etiqueta": r"\varepsilon", "latex": f"{_num(tol)}{suf}"}],
        pasos=[paso("Fórmula y criterio de parada", MOTIVOS_BISECCION.get(res["motivo"], res["motivo"]),
                    latex=[r"c = \frac{a + b}{2}"],
                    detalles=[f"Criterio: {crit}. Tolerancia: ${_num(tol)}{suf}$."])] + _convergencia(res),
        resultado=[{"etiqueta": "c", "latex": _num(res["raiz"])},
                   {"etiqueta": "|f(c)|", "latex": _num(res["residuo"])},
                   {"etiqueta": r"\text{Cota}", "latex": _num(res["cota_error"])},
                   {"etiqueta": r"\text{Iteraciones}", "latex": str(res["iteraciones"])}],
        verificacion=verif,
        tablas=[tabla("Iteraciones de bisección", ["i", "a", "b", "c", "f(c)", r"\varepsilon_a\;(\%)"], filas)],
        avisos=avisos,
    )


@registrar("/api/derivadas/derivar", "/api/newton-raphson/derivar")
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
    avisos = list(res.get("advertencias") or ())
    if res.get("estancamiento"):
        fijo = "x_l" if res["estancamiento"]["extremo"] == "xl" else "x_u"
        avisos.append(f"Estancamiento: ${fijo}$ permaneció fijo durante {res['estancamiento']['iteraciones']} iteraciones.")
    if not res.get("convergio"):
        avisos.append(MOTIVOS_RF.get(res["motivo"], res["motivo"]))
    return procedimiento(
        "regla_falsa", "Método de regla falsa",
        entrada=[{"etiqueta": "f(x)", "latex": res.get("funcion_latex") or str(res.get("funcion", ""))},
                 {"etiqueta": "[x_l, x_u]", "latex": f"[{_num(xl0)},\\; {_num(xu0)}]"},
                 {"etiqueta": r"\varepsilon_s", "latex": f"{_num(res['tolerancia'])}\\,\\%"}],
        pasos=[paso("Fórmula de la regla falsa", MOTIVOS_RF.get(res["motivo"], res["motivo"]),
                    latex=[r"x_r = x_u - \frac{f(x_u)(x_l - x_u)}{f(x_l) - f(x_u)}"])] + _convergencia(res),
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


@registrar("/api/newton-raphson/resolver")
def adaptar_newton(res, _cuerpo):
    fl, dl = res["funcion_latex"], res["derivada_latex"]
    ps = res.get("pasos", ())
    pasos_out = [paso("Derivada y fórmula de iteración", MOTIVOS_ABIERTO.get(res["motivo"], res["motivo"]),
                      latex=[f"f(x) = {fl}", f"f'(x) = {dl}", r"x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}"])]
    detalles_tex = []
    for p, q in zip(ps[1:4], ps[:3]):
        detalles_tex.append(f"x_{{{p['n']}}} = {_num(q['x'])} - \\frac{{{_num(q['fx'])}}}{{{_num(q['dfx'])}}} \\approx {_num(p['x'])}")
        detalles_tex.append(f"E_a = \\left|{_num(p['x'])} - ({_num(q['x'])})\\right| = {_num(p['error_absoluto'])}")
    if detalles_tex:
        pasos_out.append(paso("Primeras iteraciones", "Sustitución en la fórmula de Newton-Raphson.", latex=detalles_tex))
    filas = [[p["n"], p["x"], p["fx"], p["dfx"], p["error_absoluto"], p["error_relativo"]] for p in ps]
    grupos = {}
    avisos = []
    for adv in res.get("advertencias", ()):
        if isinstance(adv, dict) and "tipo" in adv and "n" in adv:
            grupos.setdefault(adv["tipo"], []).append(str(adv["n"]))
    if "derivada_pequena" in grupos:
        avisos.append(f"Derivada pequeña en $n={','.join(grupos['derivada_pequena'])}$.")
    if "paso_creciente" in grupos:
        avisos.append(f"El cambio aumentó en $n={','.join(grupos['paso_creciente'])}$.")
    for adv in res.get("advertencias", ()):
        if isinstance(adv, dict) and adv.get("tipo") == "no_certificada":
            avisos.append(adv.get("mensaje") or MOTIVOS_ABIERTO["no_certificada"])
    if not res.get("convergio"):
        if res.get("motivo") != "no_certificada" or "no_certificada" not in grupos:
            avisos.append(MOTIVOS_ABIERTO.get(res["motivo"], res["motivo"]))
    return procedimiento(
        "newton_raphson", "Método de Newton-Raphson",
        entrada=[{"etiqueta": "f(x)", "latex": fl}, {"etiqueta": "f'(x)", "latex": dl},
                 {"etiqueta": "x_0", "latex": _num(res["x0"])},
                 {"etiqueta": r"\varepsilon", "latex": _num(res["tolerancia"])}],
        pasos=pasos_out + _convergencia(res),
        resultado=[{"etiqueta": "x_n", "latex": _num(res["raiz"])},
                   {"etiqueta": "|f(x_n)|", "latex": _num(res["residuo"])},
                   {"etiqueta": "E_a", "latex": _num(res["error_absoluto"])},
                   {"etiqueta": r"\varepsilon_r", "latex": _num(res["error_relativo"])},
                   {"etiqueta": r"\text{Iteraciones}", "latex": str(res["iteraciones"])}],
        verificacion=_verif_abiertos(res),
        tablas=[tabla("Iteraciones de Newton-Raphson",
                      ["n", "x_n", "f(x_n)", "f'(x_n)", "E_a", r"\varepsilon_r"], filas)],
        avisos=avisos,
    )


@registrar("/api/secante/resolver")
def adaptar_secante(res, _cuerpo):
    x0, x1 = res["iniciales"]
    ps = res.get("pasos", ())
    pasos_out = [paso("Fórmula de la secante", MOTIVOS_ABIERTO.get(res["motivo"], res["motivo"]),
                      latex=[r"x_{n+1} = x_n - \frac{f(x_n)(x_n - x_{n-1})}{f(x_n) - f(x_{n-1})}"])]
    sust = [f"x_{{{p['n'] + 1}}} = {_num(p['b'])} - \\frac{{({_num(p['fb'])})({_num(p['b'])} - ({_num(p['a'])}))}}"
            f"{{{_num(p['fb'])} - ({_num(p['fa'])})}} \\approx {_num(p['c'])}" for p in ps[:4]]
    if sust:
        pasos_out.append(paso("Sustituciones iniciales", "Cálculo de las primeras aproximaciones.", latex=sust))
    filas = [[p["n"], p["a"], p["b"], p["c"], abs(p["fc"]), p["error_absoluto"], p["error_relativo"]] for p in ps]
    avisos = []
    if res.get("advertencias"):
        avisos.append(f"Denominador pequeño en las iteraciones ${','.join(map(str, res['advertencias']))}$.")
    if not res.get("convergio"):
        avisos.append(MOTIVOS_ABIERTO.get(res["motivo"], res["motivo"]))
    return procedimiento(
        "secante", "Método de la secante",
        entrada=[{"etiqueta": "f(x)", "latex": res.get("funcion_latex") or str(res.get("funcion", ""))},
                 {"etiqueta": "x_0", "latex": _num(x0)}, {"etiqueta": "x_1", "latex": _num(x1)},
                 {"etiqueta": r"\varepsilon", "latex": _num(res["tolerancia"])}],
        pasos=pasos_out + _convergencia(res),
        resultado=[{"etiqueta": "x_n", "latex": _num(res["raiz"])},
                   {"etiqueta": "|f(x_n)|", "latex": _num(res["residuo"])},
                   {"etiqueta": "E_a", "latex": _num(res["error_absoluto"])},
                   {"etiqueta": r"\varepsilon_r", "latex": _num(res["error_relativo"])},
                   {"etiqueta": r"\text{Iteraciones}", "latex": str(res["iteraciones"])}],
        verificacion=_verif_abiertos(res),
        tablas=[tabla("Iteraciones de la secante",
                      ["n", "x_{n-1}", "x_n", "x_{n+1}", "|f(x_{n+1})|", "E_a", r"\varepsilon_r"], filas)],
        avisos=avisos,
    )


def _formula_iter(metodo):
    return (r"x_i^{(k+1)} = \frac{1}{a_{ii}}\left(b_i - \sum_{j < i} a_{ij} x_j^{(k+1)} - \sum_{j > i} a_{ij} x_j^{(k)}\right)"
            if metodo == "gauss_seidel" else r"x_i^{(k+1)} = \frac{1}{a_{ii}}\left(b_i - \sum_{j \ne i} a_{ij} x_j^{(k)}\right)")


def _paso_analisis(a, nombre=""):
    tex, det = [], list(a.get("razones") or ())
    if "diagonal_nula" in a:
        det.append("Diagonal nula: " + ("sí." if a["diagonal_nula"] else "no."))
    orden = a.get("reordenamiento") or {}
    if orden:
        det.append("Reordenamiento: " + ("aplicado." if orden.get("aplicado") else "no aplicado."))
        det.append("Orden de ecuaciones: " + ", ".join(str(i + 1) for i in orden.get("permutacion", ())) + ".")
        if orden.get("motivo"):
            det.append(orden["motivo"])
    if a.get("rango"):
        tex.append(f"\\operatorname{{rg}}(A) = {a['rango']['A']},\\quad \\operatorname{{rg}}([A\\mid b]) = {a['rango']['aumentada']}")
    if a.get("radio_espectral"):
        re_ = a["radio_espectral"]
        tex.append(f"\\rho(T_J) = {_num(re_.get('jacobi'))},\\quad \\rho(T_{{GS}}) = {_num(re_.get('gauss_seidel'))}")
    for idx, f in enumerate((a.get("dominancia") or {}).get("filas") or ()):
        row = (f["i"] if isinstance(f.get("i"), int) else idx) + 1
        op = ">" if f.get("cumple") else r"\le"
        det.append(f"Fila {row}: $|a_{{{row},{row}}}| = {_num(f['diagonal'])} {op} \\sum_{{j\\ne {row}}} |a_{{{row},j}}| = {_num(f['suma'])}$.")
    titulo = f"{nombre}: Análisis del sistema y convergencia" if nombre else "Análisis del sistema y convergencia"
    return paso(titulo, f"Garantía: {a.get('garantia', 'no_asegurada')}.", latex=tex, detalles=det)


def _pasos_iter(res, prefijo=""):
    etiq = f"{prefijo}: " if prefijo else ""
    out = [paso(f"{etiq}Fórmula de iteración", res.get("mensaje", ""), latex=[_formula_iter(res.get("metodo"))])]
    for p in res.get("iteraciones") or ():
        if not p.get("detalle"):
            continue
        tex = [d[k] for d in p["detalle"] for k in ("formula_latex", "sustitucion_latex") if d.get(k)]
        tex.append(f"\\left\\|x^{{({p['k']})}} - x^{{({p['k'] - 1})}}\\right\\|_\\infty = {_num(p.get('cambio_inf'))},\\quad "
                   f"\\left\\|r^{{({p['k']})}}\\right\\|_\\infty = {_num(p.get('residuo_inf'))},\\quad "
                   f"r_{{\\text{{rel}}}} = {_num(p.get('residuo_rel'))}")
        out.append(paso(f"{etiq}Iteración k = {p['k']}", latex=tex))
    return out


def _tabla_iter(res, titulo):
    nombres = res.get("nombres") or [f"x_{i + 1}" for i in range(res.get("n", 0))]
    cols = ["k", *[f"{_var(nb, i)}^{{(k)}}" for i, nb in enumerate(nombres)],
            r"\|x^{(k)}-x^{(k-1)}\|_\infty", r"\Delta_{\text{rel}}", r"\|r^{(k)}\|_\infty", r"r_{\text{rel}}"]
    filas = [[p["k"], *(p.get("x") or ()), p.get("cambio_inf"), p.get("cambio_rel"),
              p.get("residuo_inf"), p.get("residuo_rel")] for p in res.get("iteraciones") or ()]
    return tabla(titulo, cols, filas)


def _verif_iter(res, prefijo=""):
    v = res.get("verificacion")
    if not v:
        return []
    etiq = f"{prefijo}: " if prefijo else ""
    estado = "cumple tolerancia" if v.get("cumple") else "no cumple tolerancia"
    return [f"{etiq}Verificación por sustitución ({estado}).",
            f"{etiq}$Ax \\approx {_vec(v.get('Ax'))}$, $b = {_vec(res.get('b'))}$.",
            f"{etiq}$r = b - Ax \\approx {_vec(v.get('residuo'))}$, $\\|r\\|_\\infty = {_num(v.get('residuo_inf'))}$, "
            f"$r_{{\\text{{rel}}}} = {_num(v.get('residuo_rel'))}$."]


@registrar("/api/iterativos/resolver")
def adaptar_iterativos(res, _cuerpo):
    nombre = "Gauss-Seidel" if res.get("metodo") == "gauss_seidel" else "Jacobi"
    iters, verif = res.get("iteraciones") or (), res.get("verificacion") or {}
    k_fin = iters[-1]["k"] if iters else 0
    pasos_out = ([_paso_analisis(res["analisis"])] if res.get("analisis") else []) + _pasos_iter(res)
    return procedimiento(
        "iterativos", f"Método iterativo de {nombre}",
        entrada=[{"etiqueta": "A", "latex": _mat(res["A"])}, {"etiqueta": "b", "latex": _vec(res["b"])},
                 {"etiqueta": "x^{(0)}", "latex": _vec(res["x0"])}, {"etiqueta": r"\varepsilon", "latex": _num(res["tolerancia"])}],
        pasos=pasos_out,
        resultado=[{"etiqueta": f"x^{{({k_fin})}}", "latex": _vec(res["solucion"])},
                   {"etiqueta": r"\|r\|_\infty", "latex": _num(verif.get("residuo_inf"))},
                   {"etiqueta": r"r_{\text{rel}}", "latex": _num(verif.get("residuo_rel"))},
                   {"etiqueta": r"\text{Iteraciones}", "latex": str(len(iters))}],
        verificacion=_verif_iter(res), tablas=[_tabla_iter(res, f"Iteraciones — {nombre}")],
        avisos=[] if res.get("convergio") else [res.get("mensaje", "Sin convergencia.")],
    )


@registrar("/api/iterativos/comparar")
def adaptar_comparar_iterativos(res, _cuerpo):
    j, gs = res["jacobi"], res["gauss_seidel"]
    kj = j["iteraciones"][-1]["k"] if j.get("iteraciones") else 0
    kg = gs["iteraciones"][-1]["k"] if gs.get("iteraciones") else 0
    pasos_out = [_paso_analisis(j["analisis"], "Jacobi")] if j.get("analisis") else []
    if gs.get("analisis") and gs["analisis"] != j.get("analisis"):
        pasos_out.append(_paso_analisis(gs["analisis"], "Gauss-Seidel"))
    pasos_out += _pasos_iter(j, "Jacobi") + _pasos_iter(gs, "Gauss-Seidel")
    if res.get("resumen"):
        pasos_out.append(paso("Resumen comparativo", res["resumen"]))
    avisos = ([f"Jacobi: {j.get('mensaje', '')}"] if not j.get("convergio") else []) + ([f"Gauss-Seidel: {gs.get('mensaje', '')}"] if not gs.get("convergio") else [])
    return procedimiento(
        "iterativos", "Comparación: Jacobi vs. Gauss-Seidel",
        entrada=[{"etiqueta": "A", "latex": _mat(j["A"])}, {"etiqueta": "b", "latex": _vec(j["b"])},
                 {"etiqueta": "x^{(0)}", "latex": _vec(j["x0"])}, {"etiqueta": r"\varepsilon", "latex": _num(j["tolerancia"])}],
        pasos=pasos_out,
        resultado=[{"etiqueta": f"x_{{\\text{{Jacobi}}}}^{{({kj})}}", "latex": _vec(j["solucion"])},
                   {"etiqueta": f"x_{{\\text{{GS}}}}^{{({kg})}}", "latex": _vec(gs["solucion"])},
                   {"etiqueta": r"\text{Iter. Jacobi}", "latex": str(len(j.get("iteraciones") or ()))},
                   {"etiqueta": r"\text{Iter. GS}", "latex": str(len(gs.get("iteraciones") or ()))}],
        verificacion=_verif_iter(j, "Jacobi") + _verif_iter(gs, "Gauss-Seidel") + ([res["resumen"]] if res.get("resumen") else []),
        tablas=[_tabla_iter(j, "Iteraciones — Jacobi"), _tabla_iter(gs, "Iteraciones — Gauss-Seidel")],
        avisos=avisos,
    )
