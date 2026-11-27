"""
Servidor HTTP Estándar y API REST para la Interfaz Web Interactiva.
UAM - Álgebra Lineal (MTM0120)

CERO DEPENDENCIAS EXTERNAS:
Utiliza exclusivamente los módulos estándar de Python:
- http.server
- json
- urllib.parse
- threading
- webbrowser
"""

import os
import sys
import json
import math
import re
import socket
import threading
import time
import webbrowser
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from src.core import limites

DESCARTE_MAX_BYTES = 4 * 1024 * 1024  # cuerpo excesivo que se lee y descarta antes de responder 413
from src.core.ejecucion import (ErrorEjecucion, Supervisor, clasificar_error,
                                serializar, supervisor_compartido)
from src.procedimientos import adjuntar

from src.core.arithmetic import (
    parse_number, format_number, formatear_vector, formatear_matriz, validar_vector_numerico,
)
from src.vectores.operaciones import (
    suma_vectores,
    resta_vectores,
    multiplicar_escalar_vector,
    producto_punto,
    norma_cuadrada,
)
from src.vectores.combinacion_lineal import evaluar_combinacion_lineal
from src.matrices.operaciones import (
    suma_matrices,
    resta_matrices,
    multiplicar_escalar_matriz,
    multiplicar_matrices,
    transpuesta_matriz,
    analizar_transpuesta_matriz,
)
from src.matrices.inversa import calcular_inversa_matriz
from src.matrices.determinante import (
    calcular_determinante,
    analizar_eficiencia_determinante,
)
from src.ecuaciones.ecuacion_matricial import resolver_ecuacion_matricial
from src.biseccion.metodo import resolver_biseccion, muestrear_funcion
from src.biseccion.expresiones import Expresion, numero_real
from src.regla_falsa.continuidad import analizar_region
from src.regla_falsa.metodo import preparar_intervalo, resolver_regla_falsa
from src.newton_raphson.metodo import preparar_funcion, evaluar_inicial, resolver_newton
from src.secante.metodo import resolver_secante
from src.derivadas import analizar_derivada


def serialize_fraction_or_str(val):
    if hasattr(val, "numerator") and hasattr(val, "denominator"):
        return format_number(val)
    return str(val)


def _validar_literal(valor):
    texto = str(valor).replace("_", "")
    if any(len(m.group()) > limites.DIGITOS_MAX for m in re.finditer(r"\d+", texto)):
        raise limites.LimiteExcedido(f"Cada entero admite como máximo {limites.DIGITOS_MAX} dígitos.")
    for exponente in re.finditer(r"(?:\d|\.)[eE]([+-]?\d+)", texto):
        digitos = exponente[1].lstrip("+-0") or "0"
        if len(digitos) > len(str(limites.EXPONENTE_MAX)) or int(digitos) > limites.EXPONENTE_MAX:
            raise limites.LimiteExcedido(f"El exponente debe tener valor absoluto ≤ {limites.EXPONENTE_MAX}.")


def _numero_json(texto, convertir):
    _validar_literal(texto)
    return convertir(texto)


def _constante_json(texto):
    raise ValueError("Constante JSON no permitida.")


def _validar_celda(valor):
    if isinstance(valor, bool) or not isinstance(valor, (str, int, float)):
        raise ValueError("Cada celda debe contener un número o una fracción escrita como a/b.")
    _validar_literal(valor)
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError("Los números deben ser reales finitos.")


def _validar_lista(valor, nombre, maximo, columnas=None):
    if not isinstance(valor, list):
        raise ValueError(f"{nombre} debe ser una lista JSON.")
    # La ausencia y las listas vacías conservan el diagnóstico de cada motor.
    if valor:
        limites.exigir_dimension(nombre, len(valor), maximo)
    for elemento in valor:
        if columnas is None:
            _validar_celda(elemento)
        else:
            _validar_lista(elemento, f"Columnas de {nombre}", columnas)


def _entero_acotado(nombre, valor, maximo, minimo=1):
    _validar_celda(valor)
    numero = numero_real(valor, nombre)
    if not numero.is_integer():
        raise ValueError(f"{nombre} debe ser un número entero.")
    return limites.exigir_dimension(nombre, int(numero), maximo, minimo)


def validar_peticion(ruta, cuerpo):
    """Forma, dimensiones y presupuesto antes de ocupar un trabajador."""
    partes = ruta.split("/")
    modulo = partes[2] if len(partes) > 2 else ""
    max_matriz = {"matrices": limites.MATRIZ_OPERAR_MAX, "ecuaciones": limites.SISTEMA_MAX,
                  "iterativos": limites.ITERATIVOS_MAX}.get(modulo)
    if ruta.endswith("/inversa"):
        max_matriz = limites.INVERSA_MAX
    elif ruta.endswith("/determinante"):
        max_matriz = limites.DETERMINANTE_MAX
        matriz = cuerpo.get("A")
        metodo_det = str(cuerpo.get("metodo", "lu")).strip().lower()
        if (metodo_det in ("cofactores", "laplace", "cofactor") and isinstance(matriz, list)
                and len(matriz) > limites.COFACTORES_MAX):
            raise limites.LimiteExcedido(f"Cofactores admite orden máximo {limites.COFACTORES_MAX}. "
                                         "Seleccione LU para esta matriz.")
    elif ruta.endswith("/eficiencia-determinante"):
        max_matriz = limites.EFICIENCIA_N_MAX
        _entero_acotado("El orden n", cuerpo.get("n", 3), limites.EFICIENCIA_N_MAX)
    if max_matriz:
        for clave in ("A", "B"):
            if clave in cuerpo:
                _validar_lista(cuerpo[clave], clave, max_matriz, max_matriz)
        if "b" in cuerpo:
            _validar_lista(cuerpo["b"], "b", max_matriz)
        if "x0" in cuerpo and (modulo != "iterativos" or cuerpo["x0"] is not None):
            _validar_lista(cuerpo["x0"], "x0", max_matriz)
    if modulo == "vectores":
        max_vector = limites.COMBINACION_N_MAX if ruta.endswith("/combinacion") else limites.VECTOR_MAX
        for clave in ("u", "v", "b"):
            if clave in cuerpo:
                _validar_lista(cuerpo[clave], clave, max_vector)
        if "vectores" in cuerpo:
            _validar_lista(cuerpo["vectores"], "Vectores", limites.COMBINACION_K_MAX, limites.COMBINACION_N_MAX)
    for clave in ("c", "k", "a", "xl", "xu", "x1", "tolerancia"):
        if clave in cuerpo:
            _validar_celda(cuerpo[clave])
    if modulo != "iterativos":
        for clave in ("x0", "b"):
            if clave in cuerpo and max_matriz is None and modulo != "vectores":
                _validar_celda(cuerpo[clave])
    if "funcion" in cuerpo:
        funcion = cuerpo["funcion"]
        if not isinstance(funcion, str):
            raise ValueError("La función debe ser texto.")
        if len(funcion) > limites.FUNCION_MAX_CARACTERES:
            raise limites.LimiteExcedido(f"La función admite como máximo {limites.FUNCION_MAX_CARACTERES} caracteres.")
        _validar_literal(funcion)
    if "texto" in cuerpo:
        if not isinstance(cuerpo["texto"], str):
            raise ValueError("El sistema debe escribirse como texto.")
        _validar_literal(cuerpo["texto"])
    if "max_iteraciones" in cuerpo:
        maximo = limites.ITERATIVOS_ITER_MAX if modulo == "iterativos" else limites.RAICES_ITER_MAX
        valor = cuerpo["max_iteraciones"]
        if modulo == "iterativos":
            mensaje = (f"El máximo de iteraciones debe ser un entero decimal entre 1 y {maximo}; "
                       "escribe 100, sin decimales ni exponentes.")
            if type(valor) is not int and not (isinstance(valor, str) and re.fullmatch(r"[0-9]+", valor.strip())):
                raise ValueError(mensaje)
            _validar_literal(valor)
            if not 1 <= int(valor) <= maximo:
                raise limites.LimiteExcedido(mensaje)
        else:
            _entero_acotado("Las iteraciones", valor, maximo)
    if "cantidad" in cuerpo:
        _entero_acotado("La cantidad de puntos", cuerpo["cantidad"], limites.PUNTOS_GRAFICA_MAX, 2)


def es_ruta_trivial(ruta):
    return ruta in {"/api/biseccion/preview", "/api/regla-falsa/preview", "/api/iterativos/texto",
                    "/api/biseccion/muestrear", "/api/regla-falsa/graficar", "/api/secante/graficar"}


def calcular_respuesta(ruta, cuerpo):
    """Adaptador importable del motor HTTP; no crea sockets en el trabajador."""
    resultado = []
    manejador = object.__new__(AlgebraLinearHandler)
    manejador._send_json = lambda datos, status=200: resultado.append((datos, status))
    manejador._despachar(ruta, cuerpo)
    datos, estado = resultado[0]
    if "error" in datos:
        datos = {"tipo": "entrada", "codigo": "ruta_no_encontrada", **datos}
    else:
        datos = adjuntar(ruta, datos, cuerpo)
    return datos, estado


class HTTPServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.ejecutor = Supervisor()
        except Exception:
            super().server_close()
            raise
        self.tiempos_calculo = {}

    def server_close(self):
        super().server_close()
        self.ejecutor.cerrar()


class AlgebraLinearHandler(SimpleHTTPRequestHandler):
    def setup(self):
        self.request.settimeout(limites.LECTURA_SOCKET_S)
        super().setup()

    def __init__(self, *args, **kwargs):
        # Directorio base de archivos estáticos
        web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
        super().__init__(*args, directory=web_dir, **kwargs)

    def log_message(self, format, *args):
        # Silenciar logs ruidosos para una terminal limpia
        pass

    def _send_json(self, data, status=200):
        body = serializar(data)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionError, TimeoutError):
                self.close_connection = True

    def parse_request(self):
        if not super().parse_request():
            return False
        hosts = self.headers.get_all("Host", [])
        permitidos = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
        origenes = self.headers.get_all("Origin", [])
        if (len(hosts) != 1 or hosts[0].lower() not in permitidos
                or len(origenes) > 1 or (origenes and origenes[0] != "http://" + hosts[0])):
            self._send_json({"error": "La petición debe proceder del servidor local.",
                             "tipo": "entrada", "codigo": "origen_no_permitido"}, 403)
            self.close_connection = True
            return False
        return True

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; "
                         "style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data:; "
                         "connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def send_error(self, code, message=None, explain=None):
        self._send_json({"error": "Recurso no encontrado." if code == 404 else "La petición HTTP no es válida.",
                         "tipo": "entrada", "codigo": "recurso_no_encontrado" if code == 404 else "http_invalido"}, code)

    def list_directory(self, path):
        self.send_error(404)
        return None

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def _leer_cuerpo(self, longitud):
        plazo = time.monotonic() + limites.LECTURA_SOCKET_S
        cuerpo = bytearray()
        while len(cuerpo) < longitud:
            restante = plazo - time.monotonic()
            if restante <= 0:
                raise TimeoutError()
            self.connection.settimeout(restante)
            parte = self.rfile.read1(longitud - len(cuerpo))
            if not parte:
                raise ValueError("El cuerpo de la petición está incompleto.")
            cuerpo.extend(parte)
        return cuerpo

    def _descartar_cuerpo(self, longitud):
        # Leer sin guardar un cuerpo excesivo moderado: así el cliente recibe el 413 y no un cierre abrupto
        # (BrokenPipe/ECONNRESET) mientras todavía envía. Más allá de DESCARTE_MAX_BYTES solo se cierra.
        self.close_connection = True
        restante = min(longitud, DESCARTE_MAX_BYTES)
        plazo = time.monotonic() + limites.LECTURA_SOCKET_S
        try:
            while restante > 0 and time.monotonic() < plazo:
                self.connection.settimeout(max(0.01, plazo - time.monotonic()))
                parte = self.rfile.read1(min(restante, 65536))
                if not parte:
                    break
                restante -= len(parte)
        except (OSError, ValueError):
            pass

    def do_POST(self):
        try:
            longitud = int(self.headers.get("Content-Length", "0"))
            if longitud < 0:
                raise ValueError("La longitud del cuerpo no puede ser negativa.")
            if longitud > limites.CUERPO_MAX_BYTES:
                self._descartar_cuerpo(longitud)
                raise ErrorEjecucion("El cuerpo supera el tamaño máximo permitido.", "limite", "cuerpo_grande", 413)
            try:
                body = json.loads(self._leer_cuerpo(longitud) if longitud else b"{}",
                                  parse_int=lambda t: _numero_json(t, int),
                                  parse_float=lambda t: _numero_json(t, float), parse_constant=_constante_json)
            except limites.LimiteExcedido:
                raise
            except (ValueError, UnicodeError, RecursionError):
                raise ErrorEjecucion("El cuerpo de la petición no es JSON válido", "entrada", "json_invalido", 400)
            if not isinstance(body, dict):
                raise ValueError("El cuerpo de la petición debe ser un objeto JSON.")
            ruta = urlparse(self.path).path
            validar_peticion(ruta, body)
            if es_ruta_trivial(ruta):
                datos, estado = calcular_respuesta(ruta, body)
            else:
                ejecutor = getattr(self.server, "ejecutor", None) or supervisor_compartido()
                tiempo = getattr(self.server, "tiempos_calculo", {}).get(ruta)
                datos, estado = ejecutor.ejecutar("src.ui.web_server:calcular_respuesta", ruta, body, tiempo=tiempo)
            self._send_json(datos, estado)
        except TimeoutError:
            self._send_json({"error": "Se agotó el tiempo de lectura de la petición.",
                             "tipo": "tiempo", "codigo": "tiempo_lectura"}, 503)
        except Exception as exc:
            error = clasificar_error(exc)
            self._send_json(error.respuesta(), error.estado)

    def _despachar(self, ruta, body):
        parsed = urlparse(ruta)
        try:
            if parsed.path == "/api/iterativos/texto":
                from src.iterativos.sistema_texto import leer_ecuaciones
                if not isinstance(body, dict):
                    raise ValueError("Envía un objeto JSON con el texto del sistema.")
                A, b, nombres = leer_ecuaciones(body.get("texto"))
                return self._send_json({"A": [[str(v) for v in fila] for fila in A],
                                        "b": [str(v) for v in b], "nombres": nombres})
            if parsed.path in ("/api/iterativos/resolver", "/api/iterativos/comparar",
                               "/api/iterativos/analizar"):
                from src.iterativos.resolver import (
                    resolver_iterativo, comparar_metodos, analizar_sistema,
                )
                if not isinstance(body, dict):
                    raise ValueError("Envía un objeto JSON con A y b.")
                datos = {"A": body.get("A"), "b": body.get("b"),
                         "x0": body.get("x0"), "reordenar": body.get("reordenar", False)}
                if parsed.path.endswith("/analizar"):
                    datos["metodo"] = body.get("metodo", "jacobi")
                    resultado = analizar_sistema(**datos)
                else:
                    datos.update({"tolerancia": body.get("tolerancia", 1e-6),
                                  "max_iteraciones": body.get("max_iteraciones", 100),
                                  "criterio": body.get("criterio", "ambos")})
                    if parsed.path.endswith("/resolver"):
                        datos["metodo"] = body.get("metodo")
                        resultado = resolver_iterativo(**datos)
                    else:
                        resultado = comparar_metodos(**datos)
                self._send_json(resultado)
            elif parsed.path == "/api/derivadas/derivar":
                if not isinstance(body, dict):
                    raise ValueError("Envíe un objeto JSON con la función.")
                self._send_json(analizar_derivada(body.get("funcion")))
            elif parsed.path.startswith("/api/secante/"):
                self._handle_secante(parsed.path.rsplit("/", 1)[-1], body)
            elif parsed.path.startswith("/api/newton-raphson/"):
                self._handle_newton(parsed.path.rsplit("/", 1)[-1], body)
            elif parsed.path == "/api/vectores/operar":
                self._handle_vectores_operar(body)
            elif parsed.path == "/api/vectores/combinacion":
                self._handle_vectores_combinacion(body)
            elif parsed.path == "/api/matrices/operar":
                self._handle_matrices_operar(body)
            elif parsed.path == "/api/matrices/inversa":
                self._handle_matrices_inversa(body)
            elif parsed.path == "/api/ecuaciones/resolver":
                self._handle_ecuaciones_resolver(body)
            elif parsed.path == "/api/matrices/determinante":
                self._handle_matrices_determinante(body)
            elif parsed.path == "/api/matrices/eficiencia-determinante":
                self._handle_eficiencia_determinante(body)
            elif parsed.path == "/api/biseccion/resolver":
                self._handle_biseccion(body)
            elif parsed.path in ("/api/biseccion/preview", "/api/regla-falsa/preview"):
                if not isinstance(body, dict):
                    raise ValueError("Envíe un objeto JSON con la función.")
                self._send_json({"latex": Expresion(body.get("funcion")).latex()})
            elif parsed.path == "/api/biseccion/muestrear":
                self._handle_biseccion_muestrear(body)
            elif parsed.path == "/api/regla-falsa/graficar":
                self._handle_regla_falsa_graficar(body)
            elif parsed.path == "/api/regla-falsa/analizar":
                self._handle_regla_falsa_analizar(body)
            elif parsed.path == "/api/regla-falsa/validar":
                self._handle_regla_falsa_validar(body)
            elif parsed.path == "/api/regla-falsa/resolver":
                self._handle_regla_falsa_resolver(body)
            else:
                self._send_json({"error": f"Ruta API no encontrada: {parsed.path}"}, status=404)
        except Exception:
            raise

    # ==============================================================================
    # ==============================================================================
    # APARTADO 1: OPERACIONES CON VECTORES EN R^n
    # Operaciones: Suma (u + v), Resta (u - v), Multiplicación por Escalar (c · u),
    # Producto Punto Euclídeo (u · v) y Norma / Magnitud Vectorial (||u||, ||u||²)
    # ==============================================================================
    # ==============================================================================
    def _handle_vectores_operar(self, body):
        op = body.get("operacion", "")
        if op not in ("suma", "resta", "escalar_u", "producto_punto"):
            raise ValueError(f"Operación vectorial desconocida: '{op}'")
        u = validar_vector_numerico(body.get("u", []), maximo=limites.VECTOR_MAX)
        v = validar_vector_numerico(body.get("v", []), maximo=limites.VECTOR_MAX) if op != "escalar_u" else []
        c = parse_number(body.get("c", "1")) if op == "escalar_u" else None

        desglose = []
        if op == "suma":
            res = suma_vectores(u, v)
            for i in range(len(res)):
                desglose.append(f"Componente {i+1}: $({format_number(u[i])}) + ({format_number(v[i])}) = {format_number(res[i])}$")
            data = {
                "titulo_operacion": "Suma Vectorial u + v",
                "resultado_str": formatear_vector(res),
                "explicacion_teorica": "La suma en $\\mathbb{R}^n$ se calcula componente a componente: $(\\vec{u} + \\vec{v})_i = u_i + v_i$.",
                "desglose_componentes": desglose,
            }
        elif op == "resta":
            res = resta_vectores(u, v)
            for i in range(len(res)):
                desglose.append(f"Componente {i+1}: $({format_number(u[i])}) - ({format_number(v[i])}) = {format_number(res[i])}$")
            data = {
                "titulo_operacion": "Resta Vectorial u - v",
                "resultado_str": formatear_vector(res),
                "explicacion_teorica": "La resta en $\\mathbb{R}^n$ equivale a sumar el inverso aditivo de $\\vec{v}$: $(\\vec{u} - \\vec{v})_i = u_i - v_i$.",
                "desglose_componentes": desglose,
            }
        elif op == "escalar_u":
            res = multiplicar_escalar_vector(c, u)
            for i in range(len(res)):
                desglose.append(f"Componente {i+1}: $({format_number(c)}) \\cdot ({format_number(u[i])}) = {format_number(res[i])}$")
            data = {
                "titulo_operacion": f"Multiplicación por Escalar {c} · u",
                "resultado_str": formatear_vector(res),
                "explicacion_teorica": "El producto por escalar distribuye el factor en cada componente: $(c \\cdot \\vec{u})_i = c \\cdot u_i$.",
                "desglose_componentes": desglose,
            }
        elif op == "producto_punto":
            p_punto = producto_punto(u, v)
            norma_u_sq = norma_cuadrada(u)
            norma_v_sq = norma_cuadrada(v)
            for i in range(len(u)):
                p_parcial = u[i] * v[i]
                desglose.append(f"Término {i+1}: $u_{{{i+1}}} \\cdot v_{{{i+1}}} = ({format_number(u[i])}) \\cdot ({format_number(v[i])}) = {format_number(p_parcial)}$")
            data = {
                "titulo_operacion": "Producto Punto u · v",
                "resultado_str": format_number(p_punto),
                "explicacion_teorica": (
                    f"El producto escalar euclídeo es la sumatoria de productos: $\\vec{{u}} \\cdot \\vec{{v}} = \\sum_{{i=1}}^{{n}} u_i v_i = {format_number(p_punto)}$.\n"
                    f"Norma al cuadrado de $\\vec{{u}}$: $\\|\\vec{{u}}\\|^2 = {format_number(norma_u_sq)}$, Norma al cuadrado de $\\vec{{v}}$: $\\|\\vec{{v}}\\|^2 = {format_number(norma_v_sq)}$."
                ),
                "desglose_componentes": desglose,
            }
        else:
            raise ValueError(f"Operación vectorial desconocida: '{op}'")

        self._send_json(data)

    # ==============================================================================
    # ==============================================================================
    # APARTADO 2: EVALUACIÓN DE COMBINACIÓN LINEAL Y SUBESPACIOS
    # Problema: c₁·v₁ + c₂·v₂ + ... + cₖ·vₖ = b en R^n
    # Algoritmo: Eliminación Gaussiana y Clasificación Rouché-Capelli
    # ==============================================================================
    # ==============================================================================
    def _handle_vectores_combinacion(self, body):
        vectores = body.get("vectores", [])
        b = body.get("b", [])
        resultado = evaluar_combinacion_lineal(vectores, b)

        pasos_serializables = []
        for p in resultado.pasos_reduccion:
            pasos_serializables.append({
                "step_number": p.step_number,
                "title": p.title,
                "description": p.description,
                "operation_code": p.operation_code,
            })

        data = {
            "es_combinacion": resultado.es_combinacion,
            "tipo_solucion": resultado.tipo_solucion,
            "expresion_algebraica": resultado.expresion_algebraica,
            "justificacion_teorica": resultado.justificacion_teorica,
            "escalares": {k: serialize_fraction_or_str(v) for k, v in resultado.escalares.items()},
            "escalares_vector": [serialize_fraction_or_str(x) for x in resultado.escalares_vector],
            "comprobacion": resultado.comprobacion_sustitucion,
            "pasos": pasos_serializables,
            **resultado.analisis_independencia,
            "verificacion_independencia": resultado.verificacion_independencia,
        }
        self._send_json(data)

    # ==============================================================================
    # ==============================================================================
    # APARTADO 3: OPERACIONES MATRICIALES BÁSICAS
    # Operaciones: Suma (A + B), Resta (A - B), Multiplicación por Escalar (k · A),
    # Producto Matricial (A · B) y Transpuesta de Matrices (A^T, B^T)
    # ==============================================================================
    # ==============================================================================
    def _handle_matrices_operar(self, body):
        op = body.get("operacion", "")
        A = body.get("A", [])
        B = body.get("B", [])
        k = body.get("k", "1")

        pasos_mult = []
        if op == "suma":
            res = suma_matrices(A, B)
            data = {
                "titulo_operacion": "Suma Matricial A + B",
                "matriz_resultado": [[serialize_fraction_or_str(x) for x in row] for row in res],
                "matriz_formateada": formatear_matriz(res),
                "explicacion_teorica": "Suma elemento a elemento $(A + B)_{ij} = a_{ij} + b_{ij}$ para matrices del mismo orden $m \\times n$.",
            }
        elif op == "resta":
            res = resta_matrices(A, B)
            data = {
                "titulo_operacion": "Resta Matricial A - B",
                "matriz_resultado": [[serialize_fraction_or_str(x) for x in row] for row in res],
                "matriz_formateada": formatear_matriz(res),
                "explicacion_teorica": "Resta elemento a elemento $(A - B)_{ij} = a_{ij} - b_{ij}$ para matrices del mismo orden $m \\times n$.",
            }
        elif op == "escalar_a":
            res = multiplicar_escalar_matriz(k, A)
            data = {
                "titulo_operacion": f"Multiplicación por Escalar {k} · A",
                "matriz_resultado": [[serialize_fraction_or_str(x) for x in row] for row in res],
                "matriz_formateada": formatear_matriz(res),
                "explicacion_teorica": "Multiplica cada elemento $a_{ij}$ por el factor escalar $k$: $(k \\cdot A)_{ij} = k \\cdot a_{ij}$.",
            }
        elif op == "multiplicacion":
            res, pasos_mult = multiplicar_matrices(A, B)
            data = {
                "titulo_operacion": "Multiplicación de Matrices A · B",
                "matriz_resultado": [[serialize_fraction_or_str(x) for x in row] for row in res],
                "matriz_formateada": formatear_matriz(res),
                "explicacion_teorica": (
                    "Producto renglón por columna $c_{ij} = \\sum_{k=1}^n (a_{ik} \\cdot b_{kj})$. "
                    "El número de columnas de $A$ coincide con el número de filas de $B$."
                ),
                "pasos_multiplicacion": pasos_mult,
            }
        # ----------------------------------------------------------------------
        # SUB-APARTADO: TRANSPUESTA DE UNA MATRIZ (A^T y B^T)
        # Análisis: Mapeo de filas a columnas, simetría, antisimetría, traza
        # y propiedades algebraicas fundamentales
        # ----------------------------------------------------------------------
        elif op == "transpuesta_a":
            analisis = analizar_transpuesta_matriz(A)
            data = {
                "titulo_operacion": "Transpuesta de la Matriz A^T",
                "matriz_resultado": [[serialize_fraction_or_str(x) for x in row] for row in analisis.matriz_transpuesta],
                "matriz_formateada": formatear_matriz(analisis.matriz_transpuesta),
                "explicacion_teorica": "Las filas de $A$ se convierten en las columnas de $A^T$: $(A^T)_{ji} = a_{ij}$.",
                "dimensiones_original": f"{analisis.dimensiones_original[0]} \\times {analisis.dimensiones_original[1]}",
                "dimensiones_transpuesta": f"{analisis.dimensiones_transpuesta[0]} \\times {analisis.dimensiones_transpuesta[1]}",
                "es_cuadrada": analisis.es_cuadrada,
                "es_simetrica": analisis.es_simetrica,
                "es_antisimetrica": analisis.es_antisimetrica,
                "traza": serialize_fraction_or_str(analisis.traza) if analisis.traza is not None else None,
                "pasos_mapeo": analisis.pasos_mapeo,
                "propiedades": analisis.propiedades,
            }
        elif op == "transpuesta_b":
            analisis = analizar_transpuesta_matriz(B)
            data = {
                "titulo_operacion": "Transpuesta de la Matriz B^T",
                "matriz_resultado": [[serialize_fraction_or_str(x) for x in row] for row in analisis.matriz_transpuesta],
                "matriz_formateada": formatear_matriz(analisis.matriz_transpuesta),
                "explicacion_teorica": "Las filas de $B$ se convierten en las columnas de $B^T$: $(B^T)_{ji} = b_{ij}$.",
                "dimensiones_original": f"{analisis.dimensiones_original[0]} \\times {analisis.dimensiones_original[1]}",
                "dimensiones_transpuesta": f"{analisis.dimensiones_transpuesta[0]} \\times {analisis.dimensiones_transpuesta[1]}",
                "es_cuadrada": analisis.es_cuadrada,
                "es_simetrica": analisis.es_simetrica,
                "es_antisimetrica": analisis.es_antisimetrica,
                "traza": serialize_fraction_or_str(analisis.traza) if analisis.traza is not None else None,
                "pasos_mapeo": analisis.pasos_mapeo,
                "propiedades": analisis.propiedades,
            }
        else:
            raise ValueError(f"Operación matricial desconocida: '{op}'")

        self._send_json(data)

    # ==============================================================================
    # ==============================================================================
    # APARTADO 4: INVERSA DE UNA MATRIZ A⁻¹
    # Métodos: Reducción por Renglones [A | I_n] ~ [I_n | A⁻¹] (Gauss / Gauss-Jordan)
    # Verificación Dual: A · A⁻¹ = I_n y A⁻¹ · A = I_n con Residuo Cero
    # ==============================================================================
    # ==============================================================================
    def _handle_matrices_inversa(self, body):
        A = body.get("A", [])
        metodo = body.get("metodo", "gauss_jordan")
        if metodo not in ("gauss_jordan", "gauss"):
            raise ValueError("Método inválido: elija gauss_jordan o gauss.")

        res = calcular_inversa_matriz(A, metodo=metodo)

        pasos_serializables = []
        for p in res.pasos_reduccion:
            pasos_serializables.append({
                "step_number": p.step_number,
                "title": p.title,
                "description": p.description,
                "operation_code": p.operation_code,
                "matrix": [[serialize_fraction_or_str(x) for x in r] for r in p.matrix_state] if hasattr(p, "matrix_state") and p.matrix_state else [],
            })

        data = {
            "orden_n": res.orden_n,
            "es_invertible": res.es_invertible,
            "metodo_utilizado": res.metodo_utilizado,
            "matriz_inversa": [[serialize_fraction_or_str(x) for x in row] for row in res.matriz_inversa] if res.matriz_inversa else None,
            "matriz_formateada": formatear_matriz(res.matriz_inversa) if res.matriz_inversa else "",
            "determinante_2x2": serialize_fraction_or_str(res.determinante_2x2) if res.determinante_2x2 is not None else None,
            "formula_2x2_detalle": res.formula_2x2_detalle,
            "matriz_aumentada_inicial": [[serialize_fraction_or_str(x) for x in row] for row in res.matriz_aumentada_inicial],
            "matriz_aumentada_final": [[serialize_fraction_or_str(x) for x in row] for row in res.matriz_aumentada_final],
            "pasos": pasos_serializables,
            "verificacion_A_por_Ainv": res.verificacion_A_por_Ainv,
            "verificacion_Ainv_por_A": res.verificacion_Ainv_por_A,
            "residuo_cero": res.residuo_cero,
            "mensaje_diagnostico": res.mensaje_diagnostico,
        }
        self._send_json(data)

    # ==============================================================================
    # ==============================================================================
    # APARTADO 5: ECUACIONES MATRICIALES Ax = b
    # Métodos: Eliminación Gaussiana y Gauss-Jordan con Clasificación Rouché-Capelli
    # Casos: Solución Única (SCD), Infinitas Soluciones (SCI) o Inconsistencia (SI)
    # ==============================================================================
    # ==============================================================================
    def _handle_ecuaciones_resolver(self, body):
        A = body.get("A", [])
        b = body.get("b", [])
        usar_gauss_jordan = body.get("usar_gauss_jordan", True)

        res = resolver_ecuacion_matricial(A, b, usar_gauss_jordan=usar_gauss_jordan)

        pasos_serializables = []
        for p in res.pasos_reduccion:
            pasos_serializables.append({
                "step_number": p.step_number,
                "title": p.title,
                "description": p.description,
                "operation_code": p.operation_code,
                "matrix": p.matrix_state,
            })

        data = {
            "tipo_sistema": res.tipo_sistema,
            "descripcion_sistema": res.descripcion_sistema,
            "rango_A": res.rango_A,
            "rango_aumentada": res.rango_aumentada,
            "vector_solucion": [serialize_fraction_or_str(x) for x in res.vector_solucion],
            "solucion_dict": {k: serialize_fraction_or_str(v) for k, v in res.solucion_dict.items()},
            "pasos": pasos_serializables,
            "verificacion": res.verificacion_residual,
            "sustitucion": res.pasos_sustitucion,
            "parametros": res.parametros,
            "solucion_particular": res.solucion_particular,
            "base_nucleo": res.base_nucleo,
            "forma_matricial": res.forma_matricial,
        }
        self._send_json(data)

    # ==============================================================================
    # ==============================================================================
    # APARTADO 6: DETERMINANTE DE MATRICES CUADRADAS |A|
    # Algoritmos: Expansión de Laplace por Cofactores vs Descomposición LU (PA = LU)
    # Análisis: Complejidad O(n!) vs O(n³), Recomendación Óptima y Dictamen Invertibilidad
    # ==============================================================================
    # ==============================================================================
    def _handle_matrices_determinante(self, body):
        A = body.get("A", [])
        metodo = body.get("metodo", "lu")

        res = calcular_determinante(A, metodo=metodo)

        pasos_serializables = []
        for p in res.pasos:
            pasos_serializables.append({
                "numero": p.numero,
                "titulo": p.titulo,
                "descripcion": p.descripcion,
                "matriz_estado": p.matriz_estado,
                "detalles": p.detalles,
            })

        data = {
            "orden_n": res.orden_n,
            "metodo": res.metodo,
            "determinante": serialize_fraction_or_str(res.determinante),
            "determinante_decimal": format_number(res.determinante, as_decimal=True, decimal_places=6),
            "es_invertible": res.es_invertible,
            "complejidad_teorica": res.complejidad_teorica,
            "operaciones_estimadas": res.operaciones_estimadas,
            "pasos": pasos_serializables,
        }
        self._send_json(data)

    def _handle_secante(self, ruta, body):
        if not isinstance(body, dict):
            raise ValueError("Envíe un objeto JSON con la función y los puntos iniciales.")
        if ruta == "graficar":
            return self._handle_regla_falsa_graficar(body)
        if ruta not in ("evaluar", "resolver"):
            return self._send_json({"error": "Ruta no encontrada."}, 404)
        self._send_json(resolver_secante(
            body.get("funcion"), body.get("x0"), body.get("x1"),
            body.get("tolerancia", 1e-6), 1 if ruta == "evaluar" else body.get("max_iteraciones", 50),
            body.get("criterio", "absoluto"), body.get("condicion", "real")))

    def _handle_newton(self, ruta, body):
        """Derivar y graficar, validar el punto manual y ejecutar Newton-Raphson."""
        if not isinstance(body, dict):
            raise ValueError("Envíe un objeto JSON con los datos del método.")
        funcion = body.get("funcion")
        if ruta == "evaluar":
            return self._send_json(evaluar_inicial(funcion, body.get("x0")))
        if ruta == "resolver":
            return self._send_json(resolver_newton(
                funcion, body.get("x0"), body.get("tolerancia", 1e-6),
                body.get("max_iteraciones", 50), body.get("criterio", "absoluto"),
                body.get("condicion", "real")))
        if ruta not in ("preparar", "derivar", "graficar"):
            return self._send_json({"error": "Ruta de Newton-Raphson no encontrada."}, 404)
        datos = preparar_funcion(funcion)
        if ruta != "derivar":
            a, b = numero_real(body.get("a"), "a"), numero_real(body.get("b"), "b")
            if a >= b or not math.isfinite(b - a):
                raise ValueError("La región debe cumplir a < b y tener ancho finito.")
            cantidad = numero_real(body.get("cantidad", 401), "La cantidad de puntos")
            if not cantidad.is_integer() or not 2 <= cantidad <= 2000:
                raise ValueError("La cantidad de puntos debe ser un entero entre 2 y 2000.")
            datos.update(intervalo=[a, b], grafica=muestrear_funcion(funcion, a, b, int(cantidad)))
        self._send_json(datos)

    def _handle_biseccion(self, body):
        """Ruta independiente para el módulo de búsqueda numérica de raíces."""
        if not isinstance(body, dict):
            raise ValueError("Envíe un objeto JSON con función, a y b.")
        res = resolver_biseccion(
            funcion=body.get("funcion"), a=body.get("a"), b=body.get("b"),
            tolerancia=body.get("tolerancia", 0.0001),
            max_iteraciones=body.get("max_iteraciones", 100),
            criterio=body.get("criterio", "intervalo"),
            condicion=body.get("condicion", "real"),
        )
        res["grafica"] = muestrear_funcion(res["funcion"], *res["intervalo_inicial"])
        res["funcion_latex"] = Expresion(res["funcion"]).latex()
        self._send_json(res)

    def _handle_biseccion_muestrear(self, body):
        """Muestreo dinámico de puntos para soporte de zoom in, zoom out y desplazamiento."""
        if not isinstance(body, dict):
            raise ValueError("Envíe un objeto JSON con función, a y b.")
        funcion = body.get("funcion")
        a = numero_real(body.get("a"), "a")
        b = numero_real(body.get("b"), "b")
        if a >= b or not math.isfinite(b - a):
            raise ValueError("El intervalo debe cumplir a < b y tener ancho finito.")
        cantidad = _entero_acotado("La cantidad de puntos", body.get("cantidad", 201), limites.PUNTOS_GRAFICA_MAX, 2)
        puntos = muestrear_funcion(funcion, a, b, cantidad)
        self._send_json({"grafica": puntos})

    # ==============================================================================
    # ==============================================================================
    # APARTADO 8: REGLA FALSA (REGULA FALSI), FLUJO PASO A PASO
    # Paso 1: graficar f(x) · Paso 2: continuidad e intervalos candidatos
    # Paso 3: validar f(x_l)·f(x_u) < 0 · Paso 4: iterar la falsa posición
    # ==============================================================================
    # ==============================================================================
    @staticmethod
    def _cuerpo_regla_falsa(body):
        if not isinstance(body, dict):
            raise ValueError("Envíe un objeto JSON con la función y los extremos.")
        return body

    def _handle_regla_falsa_graficar(self, body):
        """Paso 1: vista matemática y muestreo de f en la región de interés (o en el zoom actual)."""
        body = self._cuerpo_regla_falsa(body)
        f = Expresion(body.get("funcion"))
        a = numero_real(body.get("a"), "El límite inferior de la región")
        b = numero_real(body.get("b"), "El límite superior de la región")
        if a >= b or not math.isfinite(b - a):
            raise ValueError("La región debe cumplir a < b y tener ancho finito.")
        cantidad = _entero_acotado("La cantidad de puntos", body.get("cantidad", 401), limites.PUNTOS_GRAFICA_MAX, 2)
        self._send_json({
            "funcion": f.texto, "funcion_latex": f.latex(), "intervalo": [a, b],
            "grafica": muestrear_funcion(f.texto, a, b, cantidad),
        })

    def _handle_regla_falsa_analizar(self, body):
        """Paso 2: discontinuidades detectadas en la región e intervalos con cambio de signo."""
        body = self._cuerpo_regla_falsa(body)
        self._send_json(analizar_region(body.get("funcion"), body.get("a"), body.get("b")))

    def _handle_regla_falsa_validar(self, body):
        """Paso 3: recibe [x_l, x_u] y comprueba f(x_l)·f(x_u) < 0 y la continuidad en el intervalo."""
        body = self._cuerpo_regla_falsa(body)
        self._send_json(preparar_intervalo(body.get("funcion"), body.get("xl"), body.get("xu")))

    def _handle_regla_falsa_resolver(self, body):
        """Paso 4: itera la falsa posición solo sobre un intervalo que supera la validación."""
        body = self._cuerpo_regla_falsa(body)
        previa = preparar_intervalo(body.get("funcion"), body.get("xl"), body.get("xu"))
        if previa["estado"] == "discontinua":
            raise ValueError("Se detectó una discontinuidad dentro de [x_l, x_u]: el Teorema del Valor "
                             "Intermedio no garantiza una raíz. Elija un intervalo donde f sea continua.")
        res = resolver_regla_falsa(
            funcion=previa["funcion"], xl=previa["xl"], xu=previa["xu"],
            tolerancia=body.get("tolerancia", 0.0001),
            max_iteraciones=body.get("max_iteraciones", 100),
            condicion=body.get("condicion", "real"),
        )
        res["grafica"] = muestrear_funcion(res["funcion"], *res["intervalo_inicial"])
        res["funcion_latex"] = Expresion(res["funcion"]).latex()
        self._send_json(res)

    def _handle_eficiencia_determinante(self, body):
        n = _entero_acotado("El orden n", body.get("n", 3), limites.EFICIENCIA_N_MAX)
        A = body.get("A", None)
        analisis = analizar_eficiencia_determinante(A if A else n)

        data = {
            "orden_n": analisis.orden_n,
            "ops_cofactores": analisis.ops_cofactores,
            "complejidad_cofactores": analisis.complejidad_cofactores,
            "ops_lu": analisis.ops_lu,
            "complejidad_lu": analisis.complejidad_lu,
            "metodo_recomendado": analisis.metodo_recomendado,
            "metodo_recomendado_nombre": analisis.metodo_recomendado_nombre,
            "justificacion": analisis.justificacion,
            "insignia_cofactores": analisis.insignia_cofactores,
            "insignia_lu": analisis.insignia_lu,
        }
        self._send_json(data)


def buscar_puerto_disponible(puerto_inicial: int = 8080) -> int:
    puerto = puerto_inicial
    while puerto < 65535:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", puerto)) != 0:
                return puerto
            puerto += 1
    return puerto_inicial


@contextmanager
def servidor_local(puerto: int = 0):
    """Servidor privado con puerto asignado por el SO y cierre determinista."""
    servidor = HTTPServer(("127.0.0.1", puerto), AlgebraLinearHandler)
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    try:
        yield f"http://127.0.0.1:{servidor.server_port}"
    finally:
        servidor.shutdown()
        hilo.join(timeout=5)
        servidor.server_close()


def iniciar_servidor_web(puerto: int = 8080, abrir_navegador: bool = True):
    puerto_libre = buscar_puerto_disponible(puerto)
    servidor = HTTPServer(("127.0.0.1", puerto_libre), AlgebraLinearHandler)
    url = f"http://127.0.0.1:{puerto_libre}"
    # Una consola cp1252 no puede codificar el emoji del encabezado: sustituirlo en vez de abortar.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    print("=" * 72)
    print("🚀 CALCULADORA DE ÁLGEBRA LINEAL - UAM (MTM0120)")
    print(f"🌐 Servidor web interactivo iniciado en: {url}")
    print("=" * 72)

    if abrir_navegador:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        servidor.server_close()
