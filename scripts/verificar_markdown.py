"""Comprueba Markdown público para GitHub con la biblioteca estándar.

Uso: python scripts/verificar_markdown.py [archivo.md ...]
Sin argumentos revisa los documentos públicos; nunca consulta enlaces externos.
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


RAIZ = Path(__file__).resolve().parents[1]
CERCA = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
CODIGO = re.compile(r"(`+)(?!`)([\s\S]*?)(?<!`)\1(?!`)")
TITULO = re.compile(r"^ {0,3}(#{1,6})\s+(.+?)(?:\s+#+)?\s*$", re.M)
REFERENCIA = re.compile(r'^ {0,3}\[([^]\n]+)\]:\s*(<[^>]+>|\S+)', re.M)
ENLACE = re.compile(
    r'!?\[([^]\n]*)\](?:\((<[^>]+>|(?:\\.|[^()\s]|\([^()]*\))+)'
    r'(?:\s+["\'][^\n]*?["\'])?\)|\[([^]\n]*)\])?'
)


def archivos_publicos(raiz=RAIZ):
    return [raiz / nombre for nombre in (
        "README.md", "CHANGELOG.md", "docs/guia-matematica.md",
        "docs/distribucion.md", "docs/firma-codigo.md", "src/ui/web/vendor/README.md",
    )] + sorted((raiz / "docs").glob("notas-v*.md"))


def ocultar(texto):
    """Conserva posiciones y líneas para que los diagnósticos sean localizables."""
    return re.sub(r"[^\n]", " ", texto)


def separar(texto):
    """Oculta código y matemáticas; conserva una vista con títulos y enlaces."""
    partes, errores, cerca, inicio = [], [], None, 0
    for linea in texto.splitlines(keepends=True):
        marca = CERCA.match(linea)
        if cerca:
            cierre = re.fullmatch(r" {0,3}" + re.escape(cerca[0]) +
                                 "{" + str(len(cerca)) + r",}\s*", linea)
            partes.append(ocultar(linea))
            if cierre:
                cerca = None
        elif marca:
            cerca, inicio = marca[1], sum(map(len, partes))
            partes.append(ocultar(linea))
        else:
            partes.append(linea)
    if cerca:
        errores.append((inicio, "bloque sin cerrar"))
    vista = CODIGO.sub(lambda m: ocultar(m[0]), "".join(partes))
    caracteres, i = list(vista), 0
    while i < len(vista):
        if vista[i] != "$" or escapado(vista, i):
            i += 1
            continue
        marca = "$$" if vista[i:i + 2] == "$$" else "$"
        fin = i + len(marca)
        while True:
            fin = vista.find(marca, fin)
            if fin < 0 or (marca == "$" and "\n" in vista[i:fin]):
                errores.append((i, marca + " sin pareja"))
                fin = i
                break
            if not escapado(vista, fin):
                break
            fin += len(marca)
        hasta = fin + len(marca)
        caracteres[i:hasta] = ocultar(vista[i:hasta])
        i = hasta
    return "".join(caracteres), errores


def escapado(texto, posicion):
    barras = 0
    while posicion > 0 and texto[posicion - 1] == "\\":
        barras += 1
        posicion -= 1
    return barras % 2 == 1


def anclas(texto):
    # Los títulos pueden contener código o fórmulas: se conservan sus palabras.
    sin_bloques, cerca = [], None
    for linea in texto.splitlines(keepends=True):
        marca = CERCA.match(linea)
        if cerca:
            if re.fullmatch(r" {0,3}" + re.escape(cerca[0]) +
                            "{" + str(len(cerca)) + r",}\s*", linea):
                cerca = None
        elif marca:
            cerca = marca[1]
        else:
            sin_bloques.append(linea)
    vista = "".join(sin_bloques)
    resultado, usados = set(), {}
    for titulo in TITULO.finditer(vista):
        valor = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", titulo[2])
        valor = re.sub(r"<[^>]*>", "", valor).lower()
        base = re.sub(r"[^\w\- ]", "", valor).replace(" ", "-")
        ancla, numero = base, 0
        while ancla in usados:
            numero += 1
            ancla = f"{base}-{numero}"
        usados[ancla] = True
        resultado.add(ancla)
    resultado.update(re.findall(r'<[^>]+\b(?:id|name)=["\']([^"\']+)', vista))
    return resultado


def destinos(vista):
    referencias = {" ".join(m[1].lower().split()): m[2].strip("<>")
                   for m in REFERENCIA.finditer(vista)}
    for referencia in REFERENCIA.finditer(vista):
        yield referencia.start(), referencia[2].strip("<>")
    for enlace in ENLACE.finditer(vista):
        destino = enlace[2]
        if destino is None:
            clave = " ".join((enlace[3] or enlace[1]).lower().split())
            destino = referencias.get(clave)
        if destino:
            yield enlace.start(), destino.strip("<>")
    for enlace in re.finditer(r'<[^>]+\b(?:href|src)=["\']([^"\']+)', vista):
        yield enlace.start(), enlace[1]


def comprobar_destino(destino, archivo, raiz):
    try:
        url = urlsplit(destino)
    except ValueError:
        return "enlace mal formado: " + destino
    if url.scheme or url.netloc:
        return None
    ruta = unquote(url.path)
    base = raiz if ruta.startswith("/") else archivo.parent
    objetivo = (base / ruta.lstrip("/")).resolve() if ruta else archivo
    if not objetivo.exists():
        return "enlace inexistente: " + destino
    if url.fragment and objetivo.suffix.lower() == ".md":
        if unquote(url.fragment) not in anclas(objetivo.read_text(encoding="utf-8")):
            return "ancla inexistente: " + destino
    return None


