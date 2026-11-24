# Notas de v1.0.0

## Descripción

Primera versión estable de la Calculadora de Álgebra Lineal, dirigida a estudiantes, docentes y usuarios que
necesitan resolver ejercicios, revisar el procedimiento y comprobar sus resultados. Consolida las candidatas
rc.1 a rc.7 con once módulos, una interfaz compartida entre escritorio y navegador y cálculos locales.

## Los once módulos

1. **Vectores:** suma, resta, multiplicación por escalar y producto punto.
2. **Combinación lineal:** pertenencia al espacio generado y clasificación mediante rangos.
3. **Matrices:** suma, resta, multiplicación por escalar, producto y transpuesta.
4. **Inversa:** Gauss y Gauss-Jordan, singularidad y comprobación del resultado.
5. **Sistemas lineales:** solución única, infinitas soluciones o incompatibilidad.
6. **Determinantes:** cofactores, LU y comparación de eficiencia.
7. **Bisección:** intervalos, errores, residuo e historial de aproximaciones.
8. **Regla falsa:** intervalos, rectas secantes y desarrollo de cada iteración.
9. **Newton-Raphson:** derivada simbólica, punto inicial y tangentes.
10. **Secante:** dos puntos iniciales y aproximaciones sin derivada.
11. **Jacobi y Gauss-Seidel:** entrada por matriz o texto, convergencia y comparación de ambos métodos.

## Procedimientos paso a paso y verificación de resultados

Los resultados incluyen operaciones, sustituciones y comprobaciones para revisar el razonamiento.
El álgebra lineal conserva fracciones exactas sobre entradas racionales: los sistemas se verifican por
sustitución en $`A\cdot x=b`$ y las inversas mediante $`A\cdot A^{-1}=I`$.
Las raíces se certifican por cambio de signo bajo la hipótesis de continuidad; se rechazan las discontinuidades
detectadas y se informa cuando una aproximación no queda certificada. El muestreo no demuestra continuidad.

## Métodos numéricos y análisis de convergencia

Los métodos muestran aproximaciones, errores, residuo y motivo de parada. Los mensajes distinguen problemas
de sintaxis, dominio y convergencia e indican cómo corregir los datos. Los cálculos tienen límites de tiempo,
memoria, iteraciones y tamaño de respuesta, con ejecución aislada para mantener disponible la aplicación.
Jacobi y Gauss-Seidel analizan dominancia diagonal y radio espectral con aritmética exacta; el análisis espectral
general llega al orden 12. La clasificación distingue **demostrada**, **observada** y **no asegurada**.
La comprobación final del residuo acompaña la decisión de convergencia.

## Exportación LaTeX y CSV

El botón **Exportar** permite copiar un documento LaTeX completo y exportar CSV cuando hay tablas.
El CSV usa UTF-8, separador `;` y coma decimal para hojas de cálculo en español; conserva fracciones como texto
y protege el contenido que podría interpretarse como fórmula. Se exportan todas las filas del resultado actual.
La consolidación incluye 37 documentos LaTeX compilados con pdflatex y 22/22 etapas de importación y reapertura
por perfil con Calc y Gnumeric. La compatibilidad y los límites de precisión se detallan más abajo.

## Impresión y PDF

**Imprimir / guardar como PDF** prepara el resultado del módulo activo con fórmulas, pasos, tablas y gráficas.
La opción de guardar como PDF depende del diálogo de impresión del sistema o del navegador.

## Requisitos

El ejecutable requiere **Windows 10/11 x64** y **Microsoft Edge WebView2 Runtime**. No requiere Python ni Node.js.
Si falta WebView2, el setup lo instala; se necesita internet para esa descarga inicial.

## Instalación

Descarga el setup o el ZIP portable desde las [publicaciones del repositorio oficial](https://github.com/wigar03/Calculadora-AlgebraLineal/releases/latest).
El setup instala por usuario y crea el acceso en el menú Inicio. Para la versión portable, extrae toda la carpeta
y ejecuta `CalculadoraAlgebraLineal.exe`, conservando `_internal` a su lado; WebView2 debe estar instalado.
Puedes desinstalar la aplicación instalada desde **Configuración → Aplicaciones** de Windows.

## Funcionamiento sin conexión

Tras disponer de WebView2, los cálculos, las fórmulas, las fuentes y la exportación funcionan sin conexión.
Los datos se procesan en tu computadora. En otros sistemas puedes usar el modo navegador desde el código;
consulta el [README](../README.md) y la [guía matemática](guia-matematica.md).

## Verificación SHA-256

Descarga `SHA256SUMS.txt` de la misma publicación. En PowerShell, calcula la suma del archivo descargado:

```powershell
Get-FileHash .\archivo -Algorithm SHA256
```

Sustituye `archivo` por el nombre del setup o del ZIP y compara `Hash` con la línea correspondiente de
`SHA256SUMS.txt`. Si no coincide, vuelve a descargarlo desde la publicación oficial antes de utilizarlo.

## Limitaciones conocidas

- **Sin firma digital:** los ejecutables todavía no están firmados. Windows puede mostrar advertencias de confianza
  o impedir su ejecución según las políticas de seguridad del equipo. Descarga exclusivamente desde el repositorio
  oficial y comprueba SHA-256; la firma es una mejora prevista. Véase [la información de instalación](../README.md#ejecutables-sin-firma-digital).
- **CSV:** comprobado con LibreOffice Calc 26.2 y Gnumeric 1.12; Excel de escritorio y Excel para la Web no se han
  verificado directamente. El alcance numérico de las hojas es de 15 cifras significativas por número; el valor exacto
  va en la fracción cuando la respuesta la incluye. Los textos protegidos contra fórmulas muestran apóstrofo en Calc.
- **Gráficas y convergencia:** las gráficas son orientativas. Los métodos iterativos pueden no converger; la calculadora
  lo indica junto al motivo de parada. Estas condiciones forman parte del alcance de los métodos.
- **Plataformas y datos:** solo se distribuye ejecutable Windows x64; en otros sistemas está disponible el modo
  navegador desde el código. No incluye guardado de cálculos ni actualizaciones automáticas de la calculadora.

## Previsto para versiones futuras

- Firma digital de los ejecutables.
- Verificación directa de compatibilidad con Excel.
- Ejecutables para otros sistemas operativos.
