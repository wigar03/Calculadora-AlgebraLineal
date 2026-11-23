# Releases

| Versión | Fecha | Estado | Decisión |
|---|---|---|---|
| v1.0.0-rc.1 | 2026-11-14 | prerelease publicada (anterior a esta orquestación) | línea base |
| v1.0.0-rc.2 | 2026-11-23 | prerelease publicada (CI 45209275071 en verde) | 47/47 ejercicios definidos validados; ver abajo |

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
