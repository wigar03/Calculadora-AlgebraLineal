# Releases

| Versión | Fecha | Estado | Decisión |
|---|---|---|---|
| v1.0.0-rc.1 | 2026-11-14 | prerelease publicada (anterior a esta orquestación) | línea base |
| v1.0.0-rc.2 | 2026-11-23 | prerelease publicada (CI 45209275071 en verde) | 47/47 ejercicios definidos validados; ver abajo |
| v1.0.0-rc.3 | 2026-11-23 | **etiqueta sin release** (CI 45224566698 falló) | diagnóstico del ejecutable esperaba 10 módulos |
| v1.0.0-rc.4 | 2026-11-23 | **prerelease publicada** (CI 45225495488 en verde) | módulo 11 validado + diagnóstico corregido; ver abajo |
| v1.0.0-rc.5 | 2026-11-23 | **prerelease publicada** (CI 45254879718 en verde) | etapa 3: robustez (P1) y procedimientos comunes; ver abajo |
| v1.0.0-rc.6 | 2026-11-23 | **prerelease publicada** (CI 45270508552 en verde) | etapa 4: exportación (P2) y Markdown público |
| v1.0.0-rc.7 | 2026-11-23 | **prerelease publicada** (CI 45294856560 en verde) | etapa 5: correcciones halladas con herramientas reales |
| v1.0.0 | 2026-11-24 | release estable (pendiente de CI del tag) | primera estable, sin firma y sin prueba en Excel (autorizado) |

## v1.0.0-rc.2 — por qué y por qué con este número
- **Motivo:** se completaron y verificaron tres módulos (analizador con notación del banco y diagnósticos, métodos
  de raíces certificados, sistemas lineales corregidos). Integradas las ramas `orca/lineal`, `orca/numerico` y
  `orca/expresiones` y las correcciones de las revisiones cruzadas (INC-008, INC-010, INC-011).
- **Número:** el repositorio usa SemVer con prerelease (`1.0.0-rc.1`) y la `1.0.0` estable nunca se publicó. Saltar
  a `1.1.0` omitiría esa estable y declararía estabilidad que no existe (ejecutables sin firma). Se usa `rc.2`.
- **Evidencia antes de publicar** (`main` con la versión 1.0.0-rc.2): 322 pruebas Python OK, 52 pruebas Node OK;
  aceptación independiente por HTTP (`tests/test_validacion_ejercicios.py`, 189 llamadas contra SymPy/mpmath);
  navegador: 18 ecuaciones del documento en Bisección, Secante III-12/III-15, Newton III-13/IV-3, sistemas I-11,
  I-12 e I-14, mensaje `no_certificada` visible, 0 errores KaTeX y consola sin errores (salvo `favicon.ico` 404).
  Las 7 reproducciones de la revisión cruzada numérica se comprobaron de nuevo por HTTP tras integrar.
- **Ejercicios nuevos resueltos:** III-1…III-15, IV-1, IV-3, IV-4 escritos como en el documento; I-1…I-19 con
  Gauss + sustitución regresiva (antes incorrecto); I-14 con su solución paramétrica.
- **Límites:** IV-2 e IV-5 incompletos en la fuente (INC-001); ejecutables sin firma digital.
- **Notas publicadas:** `docs/notas-v1.0.0-rc.2.md`. Historial: `CHANGELOG.md`.
- **Procedimiento:** el existente. Push de `main` y del tag `v1.0.0-rc.2`; la CI de Windows compila y prueba el
  setup y el portable; la release se crea como prerelease con esos tres archivos.
- **Publicación:** https://github.com/wigar03/Calculadora-AlgebraLineal/releases/tag/v1.0.0-rc.2 (prerelease).
  CI del tag (45209275071) y de `main` (45209275117) en verde: pruebas, compilación, portable y ciclo de instalación.
  Archivos de la CI, con sumas SHA-256 verificadas: setup.exe, portable.zip y SHA256SUMS.txt.

## v1.0.0-rc.4 — módulo 11 (sustituye a rc.3, no publicada)
- **Motivo:** módulo completo integrado y verificado (motor, convergencia exacta, API, vista, texto), sin regresiones.
- **Número:** sigue siendo prerelease (`rc.3`): ejecutables sin firma y sin declaración de estabilidad.
- **Evidencia:** 420 pruebas Python y 58 Node OK en `main`; aceptación independiente `tests/test_validacion_iterativos.py`
  contra iteraciones exactas y radios espectrales (SymPy); batería adversaria (28 sistemas) y dos revisiones cruzadas,
  con 7 hallazgos corregidos (INC-015 a INC-018 y robustez del texto); navegador: diapositivas 9 y 28 escritas como
  texto (16/16 iteraciones, 15/15 de la tabla del propietario, ρ exactos), Gauss-Seidel divergente en el contraejemplo,
  0 errores KaTeX, consola sin errores salvo `favicon.ico`; `index.html` sin el módulo 11 idéntico al de rc.2.
- **rc.3:** el paso «Test portable, install…» falló: `src/ui/diagnostico.py` exigía `modulos == 10`. Corregido
  derivando el número de la navegación, con prueba nueva (`tests/test_diagnostico_escritorio.py`). La etiqueta
  publicada no se mueve (no se reescribe lo publicado).
- **Notas:** `docs/notas-v1.0.0-rc.4.md`.
- **Publicación rc.4:** https://github.com/wigar03/Calculadora-AlgebraLineal/releases/tag/v1.0.0-rc.4 (prerelease).
  CI del tag (45225495488) y de `main` (45225490930) en verde; portable, instalada y reinstalada: «11 módulos,
  346 fórmulas, sin recursos externos». Sumas SHA-256 de los tres archivos verificadas.

## v1.0.0-rc.5 — robustez (P1)
- **Motivo:** etapa 3 completa y verificada: aislamiento cancelable, límites, errores, seguridad y formato común de
  procedimientos, sin cambios en resultados ni en la UX (golden de 43 respuestas idéntico).
- **Evidencia:** `docs/validacion/robustez-antes.md` y `robustez-despues.md`; CI 45254331295 en Linux y Windows
  (457 pruebas en cada una; ejecutable empaquetado con procesos aislados correcto).
- **No es estable:** sigue siendo prerelease (P2 pendiente de aprobación; ejecutables sin firma).
- **Notas:** `docs/notas-v1.0.0-rc.5.md`.
- **Publicación:** https://github.com/wigar03/Calculadora-AlgebraLineal/releases/tag/v1.0.0-rc.5 (prerelease); sumas SHA-256 verificadas.

## v1.0.0-rc.6 — P2 y documentación pública
- **Evidencia:** CI 45270508552 en Linux y Windows (476 Python, 68 Node con navegador real; ejecutable con 11 módulos).
  Batería independiente de exportaciones (Codex 2) en verde; verificador Markdown sin problemas; guía en GitHub con
  274 fórmulas en MathML, sin LaTeX suelto ni desbordamientos.
- **No es estable:** ejecutables sin firma. **Notas:** `docs/notas-v1.0.0-rc.6.md`.

## v1.0.0-rc.7 — consolidación
- **Motivo:** correcciones reales, no solo comprobaciones: seguridad y fidelidad del CSV (INC-025, INC-026), compilación
  LaTeX (INC-024, INC-027) y fórmula de la guía en GitHub (INC-023).
- **Evidencia:** pdflatex 37/37, Calc y Gnumeric 22/22 por perfil, rendimiento con 16 MiB; informes en `docs/validacion/`.
- **No es estable:** ejecutables sin firma y sin prueba con Excel real. **Notas:** `docs/notas-v1.0.0-rc.7.md`.
- **Publicación:** https://github.com/wigar03/Calculadora-AlgebraLineal/releases/tag/v1.0.0-rc.7 (prerelease).
  CI del tag (45294856560) y de `main` (45294441756) en verde en Linux, Windows y `externos`; sumas SHA-256 de los tres
  archivos verificadas tras descargarlos de la release. También corrige INC-030 (413 con cierre abrupto).

## v1.0.0 — primera versión estable
- **Autorización del propietario:** publicar sin firma digital y sin prueba en Excel de escritorio; ambas
  limitaciones documentadas en README, `docs/notas-v1.0.0.md` y `docs/validacion/excel-web.md`.
- **Condición técnica:** INC-031 cerrada como incidencia del entorno de CI, con 15 máquinas limpias (15/15 ciclos,
  110/110 diagnósticos); `docs/validacion/inc031-windows.md`.
- **Sin cambios matemáticos** respecto a rc.7; cambian el diagnóstico del ejecutable y la documentación.
- **Binarios reconstruidos** por la CI del tag `v1.0.0` (no se reutilizan los de rc.7). **Notas:** `docs/notas-v1.0.0.md`.
