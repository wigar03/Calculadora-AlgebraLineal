"""Forma común de los procedimientos (versión 1) y su validación. Ver docs/contratos/procedimiento.md."""

VERSION = 1
CLAVES = {"version", "modulo", "titulo", "entrada", "pasos", "resultado", "verificacion", "tablas", "avisos"}


def procedimiento(modulo, titulo, *, entrada=(), pasos=(), resultado=(), verificacion=(), tablas=(), avisos=()):
    """Construye un procedimiento vacío o completo con listas nuevas (sin compartir referencias)."""
    return {"version": VERSION, "modulo": modulo, "titulo": titulo, "entrada": list(entrada),
            "pasos": list(pasos), "resultado": list(resultado), "verificacion": list(verificacion),
            "tablas": list(tablas), "avisos": list(avisos)}


def paso(titulo, texto="", *, latex=(), matriz=None, detalles=()):
    return {"titulo": titulo, "texto": texto, "latex": list(latex), "matriz": matriz, "detalles": list(detalles)}


def tabla(titulo, columnas, filas):
    return {"titulo": titulo, "columnas": list(columnas), "filas": [list(f) for f in filas]}


def _texto(valor, donde):
    if not isinstance(valor, str):
        raise ValueError(f"{donde} debe ser texto")


def validar(p):
    """Lanza ValueError si `p` no cumple la forma versión 1; devuelve `p` si es válido."""
    if not isinstance(p, dict) or set(p) != CLAVES or p["version"] != VERSION:
        raise ValueError("procedimiento: claves o versión incorrectas")
    _texto(p["modulo"], "modulo")
    _texto(p["titulo"], "titulo")
    for clave in ("entrada", "resultado"):
        for item in p[clave]:
            _texto(item.get("etiqueta"), f"{clave}.etiqueta")
            _texto(item.get("latex"), f"{clave}.latex")
    for s in p["pasos"]:
        if set(s) != {"titulo", "texto", "latex", "matriz", "detalles"}:
            raise ValueError("paso: claves incorrectas")
        _texto(s["titulo"], "paso.titulo")
        _texto(s["texto"], "paso.texto")
        for x in s["latex"] + s["detalles"]:
            _texto(x, "paso.latex/detalles")
        if s["matriz"] is not None and not all(isinstance(f, list) for f in s["matriz"]):
            raise ValueError("paso.matriz debe ser lista de filas")
    for x in p["verificacion"] + p["avisos"]:
        _texto(x, "verificacion/avisos")
    for t in p["tablas"]:
        if set(t) != {"titulo", "columnas", "filas"} or any(len(f) != len(t["columnas"]) for f in t["filas"]):
            raise ValueError("tabla: claves incorrectas o filas de longitud distinta a las columnas")
    return p
