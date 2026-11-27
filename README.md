# Calculadora de Álgebra Lineal

Calculadora educativa con **11 módulos de álgebra lineal y métodos numéricos**,
procedimientos paso a paso, gráficas y comprobación de resultados.
La misma interfaz funciona en el navegador y en una aplicación de escritorio.

[Descargar para Windows](https://github.com/wigar03/Calculadora-AlgebraLineal/releases/latest)
· [Guía matemática](docs/guia-matematica.md)
· [Notas de versión](CHANGELOG.md)
· [Reportar un problema](https://github.com/wigar03/Calculadora-AlgebraLineal/issues)
· [Firma de código](docs/firma-codigo.md)

![Interfaz de la calculadora](docs/images/calculadora.png)

## Qué puedes calcular

| Área | Herramientas |
|---|---|
| Vectores | Suma, resta, escalar y producto punto; dimensión $`n`$: $`1 \le n \le 20`$. |
| Combinación lineal | Pertenencia e independencia mediante rangos, relación, despeje y verificación algebraica; hasta 10 vectores de dimensión 15. |
| Matrices | Suma, resta, escalar, producto y transpuesta; hasta 8 filas y 8 columnas. |
| Inversa | Gauss y Gauss-Jordan, singularidad y verificación; orden 1–6. |
| Sistemas $`Ax = b`$ | Forma $`A\cdot X=B`$, solución única, infinitas soluciones o incompatibilidad; hasta 10 ecuaciones y 10 incógnitas. |
| Determinantes | Cofactores hasta orden 6 y LU hasta orden 8, con comparación de eficiencia. |
| Bisección | Intervalos, validaciones, errores e historial de iteraciones. |
| Regla falsa | Intervalos, rectas secantes, errores e historial de iteraciones. |
| Newton-Raphson | Derivada simbólica, punto inicial manual, tangentes y criterios de parada. |
| Secante | Dos puntos manuales, rectas secantes e historial de aproximaciones. |
| Jacobi y Gauss-Seidel | Sistemas por matriz o texto (`10x1 − x2 = 6`), convergencia, iteraciones, residuo y comparación; orden 2–10 en la interfaz y 1–20 por API, análisis espectral general hasta orden 12. |

Los módulos de álgebra lineal trabajan con fracciones exactas sobre entradas
racionales. Los métodos numéricos trabajan en punto flotante y muestran errores
y residuo. Las gráficas son orientativas y no demuestran continuidad ni convergencia.

Puedes copiar LaTeX, exportar CSV para hojas de cálculo en español e imprimir o guardar como PDF.
En Matrices, «Usar resultado como A» permite encadenar operaciones como `2A+B` o `A+B+C` conservando fracciones exactas.

La [versión 1.3.0](docs/notas-v1.3.0.md) añade gráficas en $`ℝ^2`$ en Vectores, Combinación lineal y
Ecuaciones con dos incógnitas: flechas, descomposición punta-cola, rectas e intersecciones. Newton-Raphson muestra
el porcentaje de zoom y reescala el eje vertical al enfocar la raíz. Las gráficas son orientativas y visibles al
imprimir; se conservan los resultados matemáticos y las exportaciones LaTeX y CSV.

Conserva la cobertura de los ejercicios 50–64 incorporada en [v1.1.0](docs/notas-v1.1.0.md). Los cuatro métodos de raíces
añaden condición de la raíz, orientación con «Recomendar método» y estimación del orden observado y la constante
asintótica. La recomendación y la estimación son orientativas; no garantizan convergencia.
Los ejercicios 46 y 49 conservan enunciados incompletos. Excel de escritorio y para la Web no se han verificado directamente.

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
junto al ejecutable. Puedes desinstalar la aplicación instalada desde **Configuración → Aplicaciones** de Windows.

### Ejecutables sin firma digital

Los ejecutables todavía no están firmados digitalmente. Windows puede mostrar advertencias de confianza
o impedir su ejecución según las políticas de seguridad del equipo. La firma digital es una mejora prevista.
Descarga exclusivamente desde las [publicaciones del repositorio oficial en GitHub](https://github.com/wigar03/Calculadora-AlgebraLineal/releases/latest).

Cada publicación incluye las sumas SHA-256 en `SHA256SUMS.txt`. Para comprobar una descarga en PowerShell:

```powershell
Get-FileHash .\archivo -Algorithm SHA256
```

Sustituye `archivo` por el nombre del setup o del ZIP y compara `Hash` con la línea correspondiente de
`SHA256SUMS.txt` de esa publicación. Si no coincide, vuelve a descargarlo desde la publicación oficial.

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
