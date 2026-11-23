# Cierre de revalidación CSV sobre e11d33e

Fecha: 2026-11-23. Rama `orca/consolidacion-csv`, rebasada sin conflictos sobre
`orca/integracion-exportar` `e11d33e`; Git omitió los commits ya incorporados por el integrador.
El exportador utilizado es directamente `src/ui/web/exportar.js`, sin copia candidata ni edición de `src/`.
SHA-256 normalizado a LF: `a0a3d589eec54ca16d619f7f5f13e43196ef5e668512a821f7bc3447079bfab1`.

## Cambios de las pruebas

- Retirado completamente el bloque de omisiones por fallos conocidos de `tests/test_externo_csv.py`:
  Calc/Gnumeric × `33_adversarios`/`34_precision` × `importado`/`reabierto`, ocho subpruebas.
- Texto racional exacto obligatorio por defecto: el título/cabecera debe conservar cada carácter,
  sin apóstrofo visible, sin activar `CSV_TEXTO_RACIONAL_EXACTO`.
- Añadida al adversario una tabla con título `1/2` y cabeceras `1/2`, `-17/19`, `0003/0007`
  y `9007199254740993123456789`: todos se comprueban como texto exacto después de reabrir.
- La validación independiente de enteros largos cuenta cifras significativas sin ceros iniciales y distingue
  cadenas exactas de números JSON, conforme al contrato revisado del integrador.
- Solo permanece la omisión por herramienta ausente cuando **no** se exige `REQUIERE_EXTERNOS=1`.
  No hay decoradores `expectedFailure` ni listas de fallos conocidos en este archivo.

## Ejecuciones reales

Windows, LibreOffice Portable 26.2.4.2 y Gnumeric/ssconvert 1.12.62 en TEMP, sin nuevas instalaciones.
Variables ausentes en los procesos: `P2_EXPORTAR_JS`, `CSV_EXIGIR_PENDIENTES`, `CSV_TEXTO_RACIONAL_EXACTO`.
`REQUIERE_EXTERNOS=1`; herramientas reales indicadas con `SOFFICE` y `SSCONVERT`.

| Herramienta/perfil | Etapas conformes | Fallos | Omisiones | Éxitos inesperados |
|---|---:|---:|---:|---:|
| Calc, especiales=false | 22/22 | 0 | 0 | 0 |
| Calc, especiales=true | 22/22 | 0 | 0 | 0 |
| Gnumeric STF, locale español | 22/22 | 0 | 0 | 0 |

Cada ejecución incluye las 43 consultas golden, 33 procedimientos y nueve respuestas reales con tablas,
más los casos adversarios y de precisión. Las 18 etapas reales y las cuatro artificiales pasan por herramienta.
Se comprueban valores, tipos, fórmulas autorizadas y todas las celdas del libro importado y reabierto.
Calc recorre CSV → XLSX → ODS → XLSX; Gnumeric recorre CSV copiado byte a byte como TXT → ODS → Gnumeric → ODS.
Es detección automática de STF con `LC_ALL=es_ES.UTF-8`, no selección explícita de `;`.

La ejecución predeterminada de `tests.test_externo_csv` pasa **5/5 métodos** en 16.204 s;
la repetición de Calc con especiales=true pasa **1/1** en 10.265 s, sin omisiones en ninguna.
El foco de texto mostrado también pasa en los tres perfiles: título y cabeceras `1/2`, `-1/2`, `0003/0007`
permanecen idénticos, sin apóstrofo, tanto en los libros como al exportar su contenido mostrado.
Calc usa token 9=true/10=false en el filtro CSV; Gnumeric usa `format=preserve`.
Se conserva el alcance numérico aprobado de 15 cifras significativas y el coste conocido del apóstrofo
en textos no racionales peligrosos; no se tolera ese cambio en racionales completos.

## Ausencia de herramientas y reproducción

Control negativo con ambas rutas deliberadamente inexistentes: `REQUIERE_EXTERNOS=1` produce dos fallos
y salida 1; sin exigencia produce dos omisiones justificadas y salida 0. No se ocultaron ausencias.

Con `SOFFICE` y `SSCONVERT` configurados, ejecutar en PowerShell:

```powershell
$env:REQUIERE_EXTERNOS = '1'
Remove-Item Env:P2_EXPORTAR_JS, Env:CSV_EXIGIR_PENDIENTES, Env:CSV_TEXTO_RACIONAL_EXACTO -ErrorAction SilentlyContinue
python -m unittest tests.test_externo_csv -v
$env:CSV_CALC_ESPECIALES = '1'
python -m unittest tests.test_externo_csv.TestCSVExterno.test_libreoffice_importa_guarda_y_reabre -v
```

`CSV_EVIDENCIA_DIR` permite conservar los CSV, libros e informes de cada perfil.
No se retiraron marcas en archivos de otro responsable ni se modificaron `src/` o golden.
La retirada de las cinco marcas CSV de Codex 2, las de Node/LaTeX y la batería global corresponden
al encargo paralelo confirmado por el integrador; esta evidencia no declara esa batería global ejecutada.
Excel sigue sin estar disponible; se mantienen las limitaciones registradas en las auditorías anteriores.
