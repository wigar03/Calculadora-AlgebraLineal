# INC-031: diagnóstico intermitente del ejecutable en la CI de Windows

Fecha: 2026-11-24. Responsable: integrador. Conclusión: **incidencia del entorno de CI (arranque en frío de la
máquina), no defecto de la aplicación**. Corregida la medida de diagnóstico y añadida instrumentación.

## Registros del fallo frente a los correctos
- Fallo: CI 45292151638, intento 1, trabajo 138103348181. El paso empezó a las 23:53:02 y el portable salió con
  código 1 a las 23:53:41 (39 s): descompresión + los 30 s de espera de carga de `src/ui/diagnostico.py`
  («La ventana no terminó de cargar»). El script no imprimía el informe (corregido en 2920c6c).
- Correcto: el mismo commit, intento 2 (trabajo 138109821926): portable OK a los 13 s.
- Historial (33 ejecuciones de Windows): paso del portable 9,6-16,3 s; una vez 26,5 s; dos fallos a ~35-39 s
  (este y la CI de rc.3, 45224566698, que además tenía el error de 10 módulos). Instalada 5-7 s; reinstalada 4-6 s.

## Causas investigadas
| Hipótesis | Evidencia | Resultado |
|---|---|---|
| Carrera al suscribir `loaded` | `desktop.py` suscribe el evento antes de `webview.start` | descartada |
| Ventana que nunca carga (bloqueo) | 155 arranques sin un solo bloqueo; el nuevo diagnóstico distingue lento de nunca | sin evidencia |
| Antivirus | `RealTimeProtectionEnabled : False` en los 15 runners | descartada |
| Perfil WebView2 o archivos nuevos | descompresión nueva + perfil nuevo: 2,4-6,0 s | descartada como causa principal |
| Arranque en frío de la máquina (WebView2/.NET del sistema) | solo el primer arranque de cada runner: 8,4-11,5 s | **causa** |
| Procesos residuales, bloqueos de archivos | 0 procesos `CalculadoraAlgebraLineal`/`msedgewebview2` al final; desinstalación OK | descartada |
| Permisos | instalación por usuario y portable OK en los 15 runners | descartada |
| Instalación vs reinstalación vs portable | instalada 1,2-2,1 s; reinstalada 1,3-2,0 s; el portable es lento solo por ser el primero | sin diferencia propia |

## Pruebas independientes en máquinas limpias
Flujo `.github/workflows/windows-estabilidad.yml` (5 runners `windows-2022` nuevos por ejecución), sobre `main`:
- 45297298716 (10 repeticiones por runner), 45297749585 y 45297760717 (6 repeticiones): **15/15 ciclos completos**
  (compilación, portable, instalación, reinstalación, desinstalación) y **110/110 diagnósticos repetidos** correctos.
- Primer arranque de cada runner: 8,4 a 11,5 s. Repeticiones en frío: 2,4 a 6,0 s; en caliente: 1,2 a 2,1 s.

## Corrección (dfbb8ba, 20cb849)
- El diagnóstico mide `comprobacion_s`, `carga_s` y `total_s` desde el inicio del proceso y marca `carga_lenta`
  si la carga supera 30 s; solo falla si no carga en 120 s. Pruebas: carga lenta que termina (aceptada con
  tiempos) y carga que nunca termina (rechazada con motivo) en `tests/test_diagnostico_escritorio.py`.
- `test_windows_package.ps1` espera hasta 180 s, imprime los tiempos y, si falla, el informe completo.
- Un usuario no tiene límite: la ventana aparece cuando termina de cargar. Si un futuro fallo supera 120 s, el informe
  mostrará la fase exacta y se reabrirá la incidencia.
