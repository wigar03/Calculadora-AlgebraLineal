# Robustez: medición DESPUÉS de la etapa 3

`main` 0bdf732, Windows 11, Python 3.12. Mismo comando que la medición previa (`docs/validacion/robustez-antes.md`).

| Caso | HTTP | s | bytes | mensaje |
|---|---|---|---|---|
| cofactores n=8 | 400 | 0.02 | 129 | Cofactores admite orden máximo 6. Seleccione LU para esta matriz. |
| cofactores n=9 | 400 | 0.0 | 129 | Cofactores admite orden máximo 6. Seleccione LU para esta matriz. |
| LU n=60 | 400 | 0.0 | 99 | A debe estar entre 1 y 8 (recibido: 60). |
| inversa n=30 | 400 | 0.0 | 99 | A debe estar entre 1 y 6 (recibido: 30). |
| ecuaciones 40×40 | 400 | 0.0 | 100 | A debe estar entre 1 y 10 (recibido: 40). |
| eficiencia n=5000 | 400 | 0.0 | 112 | El orden n debe estar entre 1 y 100 (recibido: 5000). |
| número 1e5000000 | 400 | 0.0 | 110 | El exponente debe tener valor absoluto ≤ 1000. |
| JSON inválido | 400 | 0.0 | 111 | El cuerpo de la petición no es JSON válido |
| cuerpo lista | 400 | 0.0 | 115 | El cuerpo de la petición debe ser un objeto JSON. |
| Host ajeno | 403 | 0.0 | 115 | La petición debe proceder del servidor local. |
| petición trivial durante cofactores n=9 | 200 | 0.0 | 711 |  |
| petición trivial con un socket lento abierto | 200 | 0.01 | 711 |  |

## Comparación
| Caso | Antes | Después |
|---|---|---|
| cofactores n=9 | 200 · 5.77 s · 124.7 MB | 400 · 0.00 s · 129 B, recomienda LU |
| petición trivial durante un cálculo | 5.36 s | 0.00 s |
| petición con un socket lento abierto | sin respuesta (15 s) | 0.01 s |
| ecuaciones 40×40 | 200 · 4.78 s · 51.5 MB | 400 · 0.00 s · límite 10 |
| número 1e5000000 | 2.40 s · texto de Python | 0.00 s · mensaje en español |
| JSON inválido / cuerpo lista | mensajes engañosos o de Python | mensajes claros |
| Host y Origin ajenos | 200 aceptado | 403 |

## Comprobaciones independientes del integrador
- Operación permitida más cara: análisis espectral exacto 12×12 con fracciones densas, 0.94 s (límite 10 s);
  una petición trivial simultánea respondió en 0.00 s; Jacobi 20×20 con 10 000 iteraciones, 0.12 s.
- `tests/test_ejecucion.py`: un cálculo de 30 s se corta a los 0.1 s, el proceso termina y se reemplaza (PID
  distinto); límite de 128 MB respetado; salida excesiva no llega al servidor.
- Cabeceras: CSP, nosniff, no-referrer, Cache-Control no-cache; sin CORS; GET /vendor/ 404; cuerpo de 300 KB 413.
- 33 respuestas del corpus con `procedimiento` válido; las 10 rutas auxiliares (vista previa, gráfica, validación,
  primera iteración, texto) no lo llevan, según el contrato. Golden: 43 respuestas idénticas.
- Navegador con CSP activa: KaTeX (348 fórmulas), fuentes e iconos correctos; un mensaje de error con
  `<img onerror>` se muestra como texto, sin ejecutarse.

## CI (run 45254331295, `main` 0f795dc)
Linux y Windows en verde: 457 pruebas en cada plataforma. Ejecutable empaquetado con procesos aislados (PyInstaller):
portable, instalada y reinstalada «11 módulos, 346 fórmulas, sin recursos externos».
