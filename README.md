# Calculadora de Álgebra Lineal

Calculadora educativa con **11 módulos de álgebra lineal y métodos numéricos**,
procedimientos paso a paso, gráficas y comprobación de resultados.
La misma interfaz funciona en el navegador y en una aplicación de escritorio.

[Descargar para Windows](https://github.com/wigar03/Calculadora-AlgebraLineal/releases)
· [Guía matemática](docs/guia-matematica.md)
· [Notas de versión](CHANGELOG.md)
· [Reportar un problema](https://github.com/wigar03/Calculadora-AlgebraLineal/issues)
· [Firma de código](docs/firma-codigo.md)

![Interfaz de la calculadora](docs/images/calculadora.png)

## Qué puedes calcular

| Área | Herramientas |
|---|---|
| Vectores | Suma, resta, multiplicación por escalar y producto punto en dimensión variable. |
| Combinación lineal | Pertenencia al espacio generado y clasificación mediante rangos. |
| Matrices | Suma, resta, escalar, producto y transpuesta. |
| Inversa | Gauss y Gauss-Jordan, detección de singularidad y verificación. |
| Sistemas $`Ax = b`$ | Solución única, infinitas soluciones o incompatibilidad. |
| Determinantes | Cofactores y descomposición LU, con comparación de eficiencia. |
| Bisección | Intervalos, validaciones, errores e historial de iteraciones. |
| Regla falsa | Intervalos, rectas secantes, errores e historial de iteraciones. |
| Newton-Raphson | Derivada simbólica, punto inicial manual, tangentes y criterios de parada. |
| Secante | Dos puntos manuales, rectas secantes e historial de aproximaciones. |
| Jacobi y Gauss-Seidel | Sistemas por matriz o por texto (`10x1 − x2 = 6`), análisis de convergencia (dominancia, radio espectral exacto), iteraciones paso a paso, residuo y comparación de ambos métodos. |

Los módulos de álgebra lineal trabajan con fracciones exactas sobre entradas
racionales. Los métodos numéricos trabajan en punto flotante y muestran errores
y residuo. Las gráficas son orientativas y no demuestran continuidad ni convergencia.

## Instalar en Windows

1. Descarga el archivo terminado en `-windows-x64-setup.exe` desde la página de descargas.
2. Ejecuta el instalador y sigue los pasos en español. La instalación es por usuario.
3. Abre **Calculadora de Álgebra Lineal** desde el menú Inicio.

No necesitas instalar Python ni Node.js. La versión de escritorio está dirigida
a Windows 10/11 x64 y utiliza Microsoft Edge WebView2 Runtime. Si falta, el setup
intentará instalarlo y necesitará internet para esa descarga inicial.
Después, los cálculos, las fórmulas y las fuentes funcionan sin conexión.

También se ofrece un ZIP **portable**: extrae toda la carpeta y ejecuta
`CalculadoraAlgebraLineal.exe`. Requiere WebView2 ya instalado; conserva `_internal`
junto al ejecutable. Los archivos `SHA256SUMS.txt` permiten comprobar las descargas.

Los ejecutables publicados no cuentan con firma digital del editor. Windows puede mostrar una
advertencia de aplicación no reconocida. Descarga los archivos del release oficial.
Puedes desinstalarla desde **Configuración → Aplicaciones** de Windows.

## Usar en el navegador desde el código

Requiere Python 3.12, la versión utilizada en las pruebas del proyecto.
El modo web local no necesita paquetes de terceros de Python.

```bash
python main.py
python main.py --port 8081
python main.py --no-browser
python main.py --version
```

El programa abre `http://127.0.0.1:8080` o un puerto disponible. Para detenerlo,
pulsa `Ctrl+C` en la terminal. La interfaz y el motor se ejecutan en tu computadora.
No es necesario publicar ni subir tus cálculos a un servicio externo.

## Desarrollo y pruebas

```bash
python -m unittest discover tests -v
for f in tests/*.cjs; do node --test "$f"; done
```

Node.js se utiliza únicamente para las pruebas de JavaScript.
Para abrir o compilar la aplicación de escritorio, consulta
[la guía de distribución](docs/distribucion.md).

El alcance y las limitaciones de cada versión se describen en las [notas de versión](CHANGELOG.md).
Para los fundamentos y ejemplos de los 11 módulos, consulta la [guía matemática](docs/guia-matematica.md).

## Créditos y licencias

El proyecto nació en la Universidad Americana (UAM), en Álgebra Lineal MTM0120,
con William Antonio García García, Caleb Jordan Tardencilla Alvarado,
Rafael Hernández Sánchez y Andrés Sebastián González Maradiaga, bajo la docencia
de Carlos Iván Argüello. La [guía matemática](docs/guia-matematica.md) conserva
los fundamentos y el contexto académico original.

Las licencias y atribuciones de los recursos de terceros se conservan
[junto a sus archivos](src/ui/web/vendor/README.md). La publicación del código
no concede por sí sola una licencia de reutilización del código propio.
