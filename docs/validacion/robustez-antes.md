# Robustez: medición ANTES de la etapa 3

`main` 5e2c73d (v1.0.0-rc.4), Windows 11, Python 3.12. Comando: `python scripts/medir_robustez.py`.

| Caso | HTTP | s | bytes | mensaje |
|---|---|---|---|---|
| cofactores n=8 | 200 | 0.65 | 12692563 |  |
| cofactores n=9 | 200 | 5.77 | 124685561 |  |
| LU n=60 | 200 | 0.88 | 11230152 |  |
| inversa n=30 | 200 | 2.93 | 32724007 |  |
| ecuaciones 40×40 | 200 | 4.78 | 51483783 |  |
| eficiencia n=5000 | 400 | 0.01 | 130 | Exceeds the limit (4300 digits) for integer string conversion; use sys |
| número 1e5000000 | 400 | 2.4 | 130 | Exceeds the limit (4300 digits) for integer string conversion; use sys |
| JSON inválido | 400 | 0.0 | 53 | Operación vectorial desconocida: '' |
| cuerpo lista | 400 | 0.0 | 49 | 'list' object has no attribute 'get' |
| Host ajeno | 200 | 0.0 | 255 |  |
| petición trivial durante cofactores n=9 | 200 | 5.36 | 255 |  |
| petición trivial con un socket lento abierto | sin respuesta | 15.01 | 0 | timed out |
