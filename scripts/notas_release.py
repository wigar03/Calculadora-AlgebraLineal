"""Convierte docs/notas-vX.md en el texto de una release de GitHub.

En una release, GitHub resuelve los enlaces relativos desde la raíz del tag (no desde docs/) y convierte cada salto de
línea en <br>. Este script deja los enlaces absolutos (fijados al tag) y une en una línea cada párrafo o elemento de
lista, sin tocar encabezados, tablas ni bloques de código.

Uso: python scripts/notas_release.py docs/notas-v1.3.0.md v1.3.0 > cuerpo.md
"""
import posixpath
import re
import sys
from pathlib import Path

REPO = "https://github.com/wigar03/Calculadora-AlgebraLineal"
ENLACE = re.compile(r"\]\((?!https?://|#|mailto:)([^)\s]+)\)")
INICIO_BLOQUE = re.compile(r"^(#|[-*+] |\d+\. |\||>|```|\$\$)")


def enlaces_absolutos(texto, carpeta, tag):
    def absoluto(m):
        destino = m.group(1)
        ruta, _, ancla = destino.partition("#")
        completa = posixpath.normpath(posixpath.join(carpeta, ruta)) if ruta else ""
        return f"]({REPO}/blob/{tag}/{completa}" + (f"#{ancla}" if ancla else "") + ")"
    return ENLACE.sub(absoluto, texto)


def unir_parrafos(texto):
    salida, en_codigo = [], False
    for linea in texto.split("\n"):
        valla = linea.lstrip().startswith("```")
        if en_codigo or valla:
            salida.append(linea)
            if valla:
                en_codigo = not en_codigo
            continue
        continua = (linea.strip() and salida and salida[-1].strip() and not INICIO_BLOQUE.match(linea.lstrip())
                    and not salida[-1].lstrip().startswith(("#", "|", "```")))
        if continua:
            salida[-1] = salida[-1].rstrip() + " " + linea.strip()
        else:
            salida.append(linea)
    return "\n".join(salida)


def cuerpo_release(ruta_notas, tag, raiz=Path(".")):
    ruta = Path(ruta_notas)
    carpeta = ruta.resolve().parent.relative_to(Path(raiz).resolve()).as_posix()
    return unir_parrafos(enlaces_absolutos(ruta.read_text(encoding="utf-8"), carpeta, tag))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(cuerpo_release(sys.argv[1], sys.argv[2]))
