"""Diagnóstico empírico compartido; no modifica iteraciones ni criterios de parada.

Se usa e_k = |x_k-x_(k-1)|, sin suponer exacta la raíz final (especialmente
en raíces múltiples). En bisección mide la contracción de los cambios, no el
orden Q de la distancia real a la raíz, que puede oscilar.
p_k = ln(e_(k+1)/e_k) / ln(e_k/e_(k-1)); C_k = e_(k+1)/e_k**p.
Se toman hasta cinco cambios finales decrecientes, anteriores al ruido de
64 ulp de sus aproximaciones; hacen falta dos órdenes locales estables.
La mediana de esos dos órdenes reduce la oscilación propia de la secante.
Se admite una dispersión <= 0.3; las bandas son 1 +/- 0.12 y 2 +/- 0.2.
C es la mediana de los dos últimos C_k calculados con el orden estimado;
la razón informa e_(k+1)/e_k (solo coincide con C para orden uno).
No se usa la tolerancia como error en x: puede ser relativa o de residuo.
"""
import math
from statistics import median


def estimar_convergencia(aproximaciones):
    xs = list(aproximaciones)
    out = dict(clasificacion="no concluyente", orden=None, constante_asintotica=None,
               razon=None, fuente_error="diferencias_sucesivas", errores=[], ordenes=[])
    explicacion = ("Error e_k = |x_k - x_(k-1)|; hasta cinco cambios finales decrecientes, "
                   "excluyendo el ruido de redondeo (64 ulp). Se requieren dos órdenes estables. "
                   "La estimación describe el historial; no demuestra convergencia ni existencia de raíz.")

    def terminar(motivo):
        out["explicacion"] = explicacion
        out["texto"] = f"Convergencia observada: {out['clasificacion']}; estimación {motivo}."
        return out

    if any(not math.isfinite(x) for x in xs):
        return terminar("no disponible por valores no finitos")
    cambios = [(abs(b-a), 64*max(math.ulp(a), math.ulp(b))) for a, b in zip(xs, xs[1:])]
    if any(not math.isfinite(e) for e, _ in cambios):
        return terminar("no disponible por errores no finitos")
    while cambios and cambios[-1][0] <= cambios[-1][1]:
        cambios.pop()
    errores = []
    for e, ruido in cambios:
        if e <= ruido:
            errores = []
        else:
            if errores and e >= errores[-1]:
                errores = []
            errores.append(e)
    errores = errores[-5:]
    out["errores"] = errores
    if len(errores) < 4:
        return terminar("no disponible: pocas iteraciones útiles o ruido de redondeo")
    logs = [math.log(e) for e in errores]
    ordenes = []
    for a, b, c in zip(logs, logs[1:], logs[2:]):
        if b-a >= -1e-3:
            return terminar("no disponible: contracción demasiado débil para medir el orden")
        ordenes.append((c-b)/(b-a))
    ordenes = ordenes[-2:]
    p = median(ordenes)
    out["ordenes"] = ordenes
    if not .85 <= p <= 2.2 or max(ordenes)-min(ordenes) > .3:
        return terminar("no disponible: los órdenes locales aún no son estables")
    clase = ("lineal" if abs(p-1) <= .12 else "cuadrática" if abs(p-2) <= .2
             else "superlineal" if 1.12 < p < 1.8 else "no concluyente")
    if clase == "no concluyente":
        return terminar("no disponible: orden fuera de las bandas de clasificación")
    try:
        constante = median(math.exp(c-p*b) for b, c in zip(logs[-3:], logs[-2:]))
    except OverflowError:
        return terminar("no disponible: constante no finita")
    if not math.isfinite(constante) or constante <= 0:
        return terminar("no disponible: constante fuera de la precisión representable")
    razon = median(b/a for a, b in zip(errores[-3:], errores[-2:]))
    out.update(clasificacion=clase, orden=p, constante_asintotica=constante, razon=razon)
    return terminar(f"p ≈ {p:.4g}, C ≈ {constante:.4g}, razón ≈ {razon:.4g} "
                    "con diferencias absolutas sucesivas")
