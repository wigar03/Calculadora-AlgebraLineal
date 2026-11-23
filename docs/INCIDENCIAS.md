# Incidencias

Formato: ID · fecha · tipo (fuente / analizador / motor / presentación / infraestructura) · estado.

## INC-001 · 2026-11-23 · fuente · ABIERTA (requiere al propietario)
**IV-2 y IV-5 no tienen igualdad.** En el XML del banco ampliado, cada uno contiene solo un `m:rad` OMML:
IV-2 `√(2x³/(x−3))`, IV-5 `√((x+4)/(x−1))`. No hay `=`, lado derecho, texto oculto, control de cambios ni
comentarios. No es un fallo de la calculadora. No se inventa el lado derecho ni se supone `= 0`.
Pregunta enviada al propietario: ¿cuál es la igualdad completa de cada uno?
Mientras tanto: se prueba que la evaluación de ambos radicales respeta su dominio (IV-2: x ≤ 0 o x > 3;
IV-5: x ≤ −4 o x > 1).

## INC-002 · 2026-11-23 · analizador · EN CURSO (Antigravity, rama `orca/expresiones`)
**Las 18 ecuaciones escritas como en el documento se rechazan con «Función inválida».**
Reproducción (sonda HTTP sobre `main` 7a241ad): `ln(x) + sen(x) = 1.2`, `e^(−x) − x^2 + 0.5 = 0`,
`x^3 − 4x − 9 = 0` → 0/72 aceptadas. Causa: `Expresion` no admite `=`, `sen`, `e^…`, `·`, `−` (U+2212) ni
superíndices, y ante cualquier error de sintaxis da un único mensaje genérico. Corrección: soporte de igualdad y
alias, y diagnósticos específicos sin multiplicación implícita silenciosa.

## INC-003 · 2026-11-23 · motor/presentación · EN CURSO (Codex 2, rama `orca/numerico`)
**La prueba con semillas a ±0.05 de la raíz pasa en los 4 métodos, pero eso no demuestra robustez.**
Pendiente de verificar con datos iniciales realistas: polos (IV-3, IV-4), dominio de ln (III-4, III-11, IV-1),
raíz trivial x = 0 (III-10). En bisección con criterio «intervalo» y tol 10⁻⁶, III-1 deja |f| ≈ 3.7·10⁻⁶:
hay que explicitar la diferencia entre cota de error y residuo.

## INC-004 · 2026-11-23 · infraestructura · CERRADA
`pytest` no está instalado; la suite oficial usa `unittest` (README y CI). Línea base: 169 pruebas OK y
5 archivos `node --test` OK. No es un fallo.
