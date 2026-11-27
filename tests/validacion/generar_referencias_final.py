"""Referencias independientes (SymPy) de las Partes V-VII del banco final. Requiere sympy.

Uso: python tests/validacion/generar_referencias_final.py  → referencias_final.json
"""
import json
from pathlib import Path

import sympy as sp

from banco_final import CONJUNTOS, EXPRESIONES, MATRICES, SISTEMAS_RECTANGULARES

SALIDA = Path(__file__).with_name("referencias_final.json")


def texto(m):
    return [[str(sp.nsimplify(x)) for x in fila] for fila in m.tolist()]


def main():
    ref = {"sistemas": {}, "matrices": {}, "independencia": {}}
    for clave, d in SISTEMAS_RECTANGULARES.items():
        A, b = sp.Matrix(d["A"]), sp.Matrix(d["b"])
        r, rab = A.rank(), A.row_join(b).rank()
        tipo = "SI" if r != rab else ("SCD" if r == A.cols else "SCI")
        ref["sistemas"][clave] = {"rango_A": r, "rango_aumentada": rab, "tipo": tipo, "libres": A.cols - r}
    for clave, exprs in EXPRESIONES.items():
        mats = {k: sp.Matrix(v) for k, v in MATRICES[clave].items()}
        ref["matrices"][clave] = {
            nombre: texto(sum((c * mats[m] for c, m in terminos[1:]), terminos[0][0] * mats[terminos[0][1]]))
            for nombre, terminos in exprs.items()}
    for clave, vs in CONJUNTOS.items():
        V = sp.Matrix(vs).T
        nucleo = [[str(x) for x in v] for v in V.nullspace()]
        ref["independencia"][clave] = {"rango": V.rank(), "vectores": V.cols,
                                       "independiente": V.rank() == V.cols, "nucleo": nucleo}
    lineas = ["{"]
    for i, (seccion, casos) in enumerate(ref.items()):
        lineas.append(f' "{seccion}": {{')
        for j, (clave, valor) in enumerate(casos.items()):
            coma = "," if j < len(casos) - 1 else ""
            lineas.append(f'  "{clave}": {json.dumps(valor, ensure_ascii=False)}{coma}')
        lineas.append(" }" + ("," if i < len(ref) - 1 else ""))
    lineas.append("}")
    SALIDA.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"Escrito {SALIDA}")


if __name__ == "__main__":
    main()
