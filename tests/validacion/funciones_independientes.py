"""f(x) independientes (escritas con `math`) y datos iniciales realistas para las Partes III y IV."""
import math

# f(x) = izquierda − derecha escrita a mano con `math` (independiente del analizador de la calculadora).
F = {
    "III-1": lambda x: x**3 - 4*x - 9, "III-2": lambda x: math.exp(x) - 3*x**2,
    "III-3": lambda x: math.cos(x) - x*math.exp(x), "III-4": lambda x: x*math.log(x) - 1,
    "III-5": lambda x: x**4 - 3*x**2 - 3, "III-6": lambda x: math.log(x + 2) + x**2 - 2,
    "III-7": lambda x: math.exp(-x) - x**2 + 0.5, "III-8": lambda x: x**3 + x - 1,
    "III-9": lambda x: x*math.exp(-x) - 0.2, "III-10": lambda x: x**2 - 5*math.sin(x),
    "III-11": lambda x: math.log(x) + math.sin(x) - 1.2, "III-12": lambda x: math.exp(-x) + math.cos(x) - 0.5,
    "III-13": lambda x: x**2 - 3*math.sin(x) - math.log(x + 2), "III-14": lambda x: math.exp(x/2) + math.sin(2*x) - 3,
    "III-15": lambda x: math.log(x + 3) + math.cos(x) - x/2, "IV-1": lambda x: math.sin(x)/math.log(x) - 1,
    "IV-3": lambda x: math.exp(1/x) + 2*x/math.tan(x) - 2, "IV-4": lambda x: math.log(x + 1)/(x**2 - 4) + 0.1,
}
# Datos iniciales como los elegiría un estudiante: intervalo [a, b] con cambio de signo verificado a mano.
INICIALES = {
    "III-1": (2, 3), "III-2": (0, 1), "III-3": (0, 1), "III-4": (1, 2), "III-5": (1, 2), "III-6": (0, 1),
    "III-7": (0, 1), "III-8": (0, 1), "III-9": (0, 1), "III-10": (1, 3), "III-11": (1, 2), "III-12": (1, 2),
    "III-13": (1.5, 2.5), "III-14": (2, 3), "III-15": (2, 3), "IV-1": (2, 3), "IV-3": (1.4, 1.7), "IV-4": (0, 1),
}
