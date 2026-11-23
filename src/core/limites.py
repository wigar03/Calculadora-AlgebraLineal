"""Límites computacionales únicos de la API (iguales a los de la interfaz). Ver docs/contratos/robustez.md.

Los motores y el servidor importan estas constantes; ningún módulo define límites propios distintos.
"""

# Dimensiones por módulo (coinciden con los controles de index.html).
VECTOR_MAX = 20
COMBINACION_N_MAX = 15
COMBINACION_K_MAX = 10
MATRIZ_OPERAR_MAX = 8
INVERSA_MAX = 6
SISTEMA_MAX = 10
DETERMINANTE_MAX = 8
COFACTORES_MAX = 6  # n = 7 ya supera 1 MB de procedimiento; para n > 6 se recomienda LU (medido por Codex 1)
EFICIENCIA_N_MAX = 100
ITERATIVOS_MAX = 20
ITERATIVOS_ITER_MAX = 10_000

# Métodos de raíces (ya vigentes en sus motores).
FUNCION_MAX_CARACTERES = 500
RAICES_ITER_MAX = 1000
PUNTOS_GRAFICA_MAX = 2000

# Números escritos por el usuario: se comprueban antes de construir Fraction.
DIGITOS_MAX = 64
EXPONENTE_MAX = 1000  # admite todo el rango de los dobles (1e308, subnormales); bloquea 1e5000000

# Servidor y ejecución aislada.
CUERPO_MAX_BYTES = 256 * 1024
LECTURA_SOCKET_S = 10
TIEMPO_CALCULO_S = 10
MEMORIA_CALCULO_MB = 512
RESPUESTA_MAX_BYTES = 4 * 1024 * 1024


class LimiteExcedido(ValueError):
    """Entrada válida en forma pero fuera de los límites computacionales (respuesta `tipo = "limite"`)."""


def exigir_dimension(nombre, valor, maximo, minimo=1):
    """Lanza LimiteExcedido con un mensaje en español si `valor` no está en [minimo, maximo]."""
    if not isinstance(valor, int) or not minimo <= valor <= maximo:
        raise LimiteExcedido(f"{nombre} debe estar entre {minimo} y {maximo} (recibido: {valor}).")
    return valor
