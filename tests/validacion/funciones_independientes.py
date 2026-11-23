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
    "III-13": (1.5, 2.5), "III-14": (2, 3), "III-15": (2, 3), "IV-1": (2, 3), "IV-3": (1.4, 1.55), "IV-4": (0, 1),
}

# Notación del documento tal cual, con '*' solo donde el documento escribe un producto implícito (4x → 4*x).
ENTRADAS_DOCUMENTO = {
    "III-1": "x³ − 4*x − 9 = 0", "III-2": "e^x − 3*x^2 = 0", "III-3": "cos(x) − x·e^x = 0",
    "III-4": "x·ln(x) − 1 = 0", "III-5": "x⁴ − 3*x² − 3 = 0", "III-6": "ln(x+2) + x² − 2 = 0",
    "III-7": "e^(−x) − x² + 0.5 = 0", "III-8": "x³ + x − 1 = 0", "III-9": "x·e^(−x) − 0.2 = 0",
    "III-10": "x² − 5·sin(x) = 0", "III-11": "ln(x) + sen(x) = 1.2", "III-12": "e^(−x) + cos(x) = 0.5",
    "III-13": "x² − 3*sen(x) − ln(x + 2) = 0", "III-14": "e^(x/2) + sen(2*x) = 3",
    "III-15": "ln(x + 3) + cos(x) = x/2", "IV-1": "sen(x) / ln(x) = 1", "IV-3": "e^(1/x) + 2*x / tan(x) = 2",
    "IV-4": "ln(x + 1) / (x² − 4) = −0.1",
}
# Producto implícito tal como aparece en el documento: debe diagnosticarse, nunca corregirse en silencio.
IMPLICITOS = {"III-1": ("4", "x"), "III-2": ("3", "x"), "III-5": ("3", "x"), "III-13": ("3", "sen"),
              "III-14": ("2", "x"), "IV-3": ("2", "x")}
