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
| v1.0.0 | 2026-11-24 | **release estable publicada** (CI 45309347449 en verde) | primera estable, sin firma y sin prueba en Excel (autorizado) |
| v1.1.0 | 2026-11-27 | **release estable publicada** (CI 46053742806 en verde) | banco final 50-64, auditoría de coherencia, orden observado, condición y recomendación |
| v1.2.0 | 2026-11-27 | **release estable publicada** (CI 46068086321 en verde) | propuestas de UX C-22…C-28 aprobadas (INC-034) |
| v1.3.0 | 2026-11-27 | **release estable publicada** (CI 46071870459 en verde) | gráficas en R² y zoom de Newton (INC-035) |

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
- **Publicación:** https://github.com/wigar03/Calculadora-AlgebraLineal/releases/tag/v1.0.0 (release normal, `latest`).
  Etiqueta en d5871bb, cuya CI de `main` (45305331925) y del tag (45309347449) pasó en Linux, Windows y `externos`.
  Binarios compilados por la CI del tag; sumas SHA-256 verificadas tras la CI y de nuevo tras descargarlos sin
  autenticación por `/releases/latest/download/`. `/releases/latest` redirige a v1.0.0. Diagnóstico del portable
  publicado en un Windows 11 real: versión 1.0.0, 11 módulos, 342 fórmulas, carga 2,3 s. `v1.0.0-rc.7` intacta.

## v1.1.0 — banco final y auditoría de coherencia
- **Motivo:** funciones nuevas compatibles (versión menor): ejercicios 50-64, «Usar resultado como A» (INC-032), forma
  A·X = B, independencia lineal verificada, orden de convergencia observado, condición de la raíz y recomendación de
  método (INC-033), y correcciones C-01…C-21 de la auditoría de Carbon (`docs/auditoria/carbon-coherencia.md`).
- **Sin cambios de resultados verificados:** 43 respuestas doradas iguales salvo los tres campos de certificación
  aprobados (C-01); 49 ejercicios del banco A y 15 del banco final validados contra SymPy.
- **Sigue sin firma digital y sin prueba en Excel.** **Notas:** `docs/notas-v1.1.0.md`.

- **Publicación:** https://github.com/wigar03/Calculadora-AlgebraLineal/releases/tag/v1.1.0 (release normal, `latest`).
  Etiqueta en 73ce71e; CI de `main` y del tag (46053742806) en verde en Linux, Windows y `externos`. Binarios de la CI
  del tag; SHA-256 verificadas tras la CI y tras descargarlos sin autenticación por `/releases/latest/download/`.
  Portable en Windows 11 real: versión 1.1.0, 11 módulos, carga 3,2 s. En la CI, el primer arranque en frío del
  portable tardó 47,9 s (INC-031, dentro del margen de 120 s); instalada y reinstalada ≈ 2 s.

## v1.2.0 — coherencia de la interfaz (INC-034)
- **Motivo:** cambios de UX aprobados por el propietario (C-22, C-23 parcial, C-24, C-25, C-26, C-27, C-28a), sin
  cambios en resultados matemáticos (43 respuestas doradas iguales; 49 + 15 ejercicios validados).
- **Corrección antes de publicar:** la CI de 71c4f60 falló en Linux (la prueba de C-25 exigía `pointer: fine`, que
  Chrome sin ventana en Linux no informa) y en `externos` (recuentos fijos del corpus sin el análisis exportable de
  C-28a). Corregidas ambas pruebas; las herramientas reales compilan e importan el documento nuevo.
- **Sigue sin firma digital y sin prueba en Excel.** **Notas:** `docs/notas-v1.2.0.md`.

- **Publicación:** https://github.com/wigar03/Calculadora-AlgebraLineal/releases/tag/v1.2.0 (release normal, `latest`).
  Etiqueta en 5631a16; CI de `main` (46067652362) y del tag (46068086321) en verde en Linux, Windows y `externos`.
  SHA-256 verificadas tras la CI y tras la descarga pública. En la CI: portable con 11 módulos y primer arranque en
  frío de 35,6 s (dentro del margen de 120 s, INC-031); instalada y reinstalada 1,6 s.
  En el equipo del integrador, Windows Application Control bloqueó el ejecutable nuevo sin firma; no se eludió
  (limitación documentada de los ejecutables sin firma, como INC-022).

## v1.3.0 — gráficas en R² y zoom de Newton (INC-035)
- **Motivo:** cierre de lo aplazado de la auditoría: gráficas en $`\mathbb{R}^2`$ (Vectores, Combinación lineal,
  Ecuaciones con 2 incógnitas) y porcentaje de zoom y reescalado vertical en Newton-Raphson. Sin cambios en resultados
  matemáticos (43 respuestas doradas iguales).
- **Integración:** un conflicto de `index.html` hizo perder el indicador de zoom de Newton; restaurado en 84ab968 tras
  comparar el marcado final con las dos ramas.
- **Sigue sin firma digital y sin prueba en Excel.** **Notas:** `docs/notas-v1.3.0.md`.

- **Publicación:** https://github.com/wigar03/Calculadora-AlgebraLineal/releases/tag/v1.3.0 (release normal, `latest`).
  Etiqueta en 456bbd8; CI de `main` (46071479130) y del tag (46071870459) en verde en Linux, Windows y `externos`.
  SHA-256 verificadas tras la CI y tras la descarga pública. En la CI: 11 módulos; primer arranque en frío del
  portable 8,8 s (los 35-48 s de v1.1.0 y v1.2.0 fueron variación del runner); instalada y reinstalada ≈ 2 s.
