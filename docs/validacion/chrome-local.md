# Diagnóstico local de Chrome y Edge en `tests/test_p2_browser.cjs`

Rama: `orca/consolidacion-chrome` (desde `main` `60c6d0c`). Entorno: Windows 11 (`LENOVOWAGG`, `C:\Users\wigar`), Python 3.12, Node.js v26.13.0.

## Conclusión
**Problema del entorno (no de la aplicación), corregido de forma robusta en la prueba sin modificar la aplicación ni debilitar aserciones.**

En esta máquina, Orca ejecuta los terminales como **Administrador** (`Orca.exe --updated --orca-restart-local-terminals-as-administrator`, integridad Alta `0x3000`, `TokenElevationType = 2 (Full)`, UAC `EnableLUA = 1`). Cuando `tests/test_p2_browser.cjs` lanza Chrome 158 o Edge 158 sin `--do-not-de-elevate` desde el escritorio interactivo `WinSta0\Default` (donde `explorer.exe` posee `GetShellWindow()`), **ambos navegadores activan la auto-de-elevación de Chromium (`base::win::RunDeElevated`)**:

1. El proceso elevado inicial obtiene el token de integridad Media (`0x2000`) de `explorer.exe` y relanza un nuevo `chrome.exe`/`msedge.exe` añadiendo automáticamente `--noerrdialogs --do-not-de-elevate`.
2. El proceso relanzado **arranca correctamente y abre el puerto CDP**, pero **no hereda la tubería `stderr`** del proceso padre, por lo que `node` nunca recibe `DevTools listening on ws://127.0.0.1:...`.
3. El proceso elevado original termina de inmediato con **código `0`** y `stderr` vacío.
4. En las ejecuciones previas a `3de2cda` (`15:04`–`15:18`), `lanzar()` no escuchaba `exit`, por lo que Chrome quedaba colgado sin imprimir `DevTools listening`. Tras `3de2cda` (`15:24:35`), Chrome salió con `código=0` en 88 ms, el bucle pasó a Edge, que también salió con `código=0` y sobrescribió `ultimoErr`. Además, `taskkill /PID <original> /T /F` no alcanzaba al hijo des-elevado, dejando navegadores huérfanos.

## Evidencia recogida en la máquina

### Versiones y binarios
- **Chrome:** `C:\Program Files\Google\Chrome\Application\chrome.exe` — `158.0.8127.36`. En `158.0.8127.36\chrome.dll`: `..\..\base\win\elevation_util.cc` / `RunDeElevated` (offset `286333371`) y switch `do-not-de-elevate` (`273336975`).
- **Edge:** `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe` — `158.0.4370.33` (Chromium `158.0.8127.37`). En `158.0.4370.33\msedge.dll`: `..\..\base\win\elevation_util.cc` / `RunDeElevated` (`326692195`) y `do-not-de-elevate` (`310012479`).

### Procesos existentes y perfiles en uso (evidencia directa en vivo)
Al iniciar el diagnóstico seguían vivos **5 navegadores huérfanos a integridad Media (`0x2000`)** procedentes de intentos previos de `test_p2_browser.cjs`, todos con `--noerrdialogs --do-not-de-elevate` inyectado por Chromium, padres elevados ya finalizados y puertos CDP activos (`/json/version` respondió 200 en los 5):

| Hora de creación | Navegador | PID (`0x2000`) | PPID (ya cerrado) | Perfil en `AppData\Local\Temp` | Puerto CDP vivo |
|---|---|---:|---:|---|---:|
| `15:04:36.431` | `chrome.exe` | `22540` | `22232` | `p2-cdp-V6X4Vd` | `55395` (`Chrome/158.0.8127.36`) |
| `15:15:11.269` | `chrome.exe` | `13952` | `11828` | `p2-cdp-vWdnvV` | `63238` (`Chrome/158.0.8127.36`) |
| `15:18:24.561` | `chrome.exe` | `20260` | `23484` | `p2-cdp-VG07aq` | `58817` (`Chrome/158.0.8127.36`) |
| `15:24:35.669` | `chrome.exe` | `2416` | `13360` | `p2-cdp-tw3Lx3` | `52538` (`Chrome/158.0.8127.36`) |
| `15:24:35.757` (+88 ms) | `msedge.exe` | `21780` | `1724` | `p2-cdp-TQBrEE` | `55323` (`Edg/158.0.4370.33`) |

También corrían `explorer.exe` (PID `2716`, `0x2000`), `msedge.exe` Startup Boost (PID `18804`, `--no-startup-window --win-session-start`, perfil estándar, sin conflicto con `mkdtempSync`) y `chrome.exe` de `chrome-devtools-mcp` (PID `4304`, `0x3000`). Los 5 procesos huérfanos anteriores y sus carpetas `p2-cdp-*` pueden cerrarse/limpiarse aparte.

### Políticas, Application Control y salida `--enable-logging=stderr --v=1`
- **Políticas de grupo/nube (descartadas):** `HKLM` y `HKCU\SOFTWARE\Policies\{Google\Chrome,Microsoft\Edge}` no existen.
- **Application Control / WDAC / AppLocker (descartado):** `Win32_DeviceGuard` informa `CodeIntegrityPolicyEnforcementStatus = 2` y `UsermodeCodeIntegrityPolicyEnforcementStatus = 2`, pero hay **0 eventos** para `chrome`, `msedge` o `node` en `Microsoft-Windows-CodeIntegrity/Operational` y `Microsoft-Windows-AppLocker/EXE and DLL` (y los 5 procesos arrancaron).
- **Salida `--enable-logging=stderr --v=1`:**
  - Chrome (normal y con `--do-not-de-elevate`): `No machine level policy manager exists`, `No policy found on disk`, emite `DevTools listening on ws://127.0.0.1:<puerto>/...` y escribe `DevToolsActivePort` (243 / 395 líneas).
  - Edge (normal y con `--do-not-de-elevate`): `EACPolicyStore policy load failed: No policy found on disk`, emite `DevTools listening on ws://127.0.0.1:<puerto>/...` y escribe `DevToolsActivePort` (1101 / 1105 líneas).

### Por qué pasa en CI (Windows y Linux) y en la sesión aislada de Antigravity
- **CI Linux (`ubuntu-24.04`):** `RunDeElevated` es exclusivo de Windows.
- **CI Windows (`windows-2022`):** el runner no tiene token dividido UAC (`TokenElevationTypeDefault`) ni escritorio interactivo con `explorer.exe` (`GetShellWindow() == 0`).
- **Sesión de Antigravity (`agy.exe` PID `14316`):** aunque hereda integridad Alta (`0x3000`) de Orca, se ejecuta en el escritorio aislado `WinSta0\exebox-QOYL6POFQVR65OXFJDTXNFZ3N5` donde `GetShellWindow() = 0` (`Progman = 0`, `Shell_TrayWnd = 0`); al no hallar `explorer.exe`, `RunDeElevated()` se omite y ambos navegadores arrancan en el mismo proceso.

## Mejora aplicada en `tests/test_p2_browser.cjs`
Commit `0e7a461` (`+15/-5` líneas; sin cambios en la aplicación ni relajación de comprobaciones):
1. `argsNavegador(perfil, platform)`: añade `--noerrdialogs` y, solo en `win32`, `--do-not-de-elevate`, impidiendo la auto-de-elevación en sesiones elevadas de Windows para mantener `stderr` conectado y permitir que `taskkill` cierre todo el árbol.
2. Acumula el error de **todos** los navegadores probados (`errores.join('\n---\n')`) en lugar de ocultar el de Chrome tras el de Edge.
3. Limpieza de perfiles con `fs.rmSync(d, { recursive: true, force: true, maxRetries: 3, retryDelay: 50 })` (0 carpetas temporales residuales).
4. Aserciones unitarias sobre `argsNavegador` en `win32` y `linux` dentro de la prueba de arranque existente.

## Verificación final
- `P2_BROWSER_EXE=...chrome.exe node --test tests/test_p2_browser.cjs`: **2 / 2 OK** (`4.18 s`).
- `P2_BROWSER_EXE=...msedge.exe node --test tests/test_p2_browser.cjs`: **2 / 2 OK** (`4.39 s`, 0 carpetas `p2-cdp-*` residuales).
- `node --test (Get-ChildItem tests/test_*.cjs).FullName`: **68 / 68 OK** (`5.06 s`).
- `node --test tests/exportacion_verificar.cjs`: **6 / 6 OK** (`0.14 s`).
- `python -m unittest discover tests -v`: **476 OK** (`skipped=1` esperado por `pdflatex` local no instalado; `tests/test_golden_api.py` intacto).
