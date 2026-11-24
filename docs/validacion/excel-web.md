# Excel para la Web: comprobación no realizable con los medios autorizados

Fecha: 2026-11-24. Responsable: integrador.

## Qué se comprobó
- **Excel para la Web** (office.com / excel.cloud.microsoft) exige iniciar sesión con una cuenta Microsoft para abrir
  o importar un archivo. No disponemos de una cuenta autorizada para el proyecto y la etapa prohíbe usar
  credenciales no autorizadas o contratar servicios, así que no se abrió ningún archivo.
- **Visor público de Office** (`view.officeapps.live.com`): no requiere cuenta, pero solo muestra libros
  `.xls`/`.xlsx` desde una URL pública; no importa CSV ni aplica el separador `;` ni la coma decimal. Convertir el CSV
  a `.xlsx` para verlo dejaría de probar la exportación real, así que se descartó.
- No se instaló software comercial.

## Conclusión
La compatibilidad con Excel (de escritorio o web) **no está verificada directamente**. La evidencia disponible es con
herramientas reales de terceros: LibreOffice Calc 26.2 (dos perfiles) y Gnumeric 1.12, 22/22 etapas cada uno
(`consolidacion-csv.md`, `csv-integrado-e11d33e.md`). El CSV sigue las convenciones de Excel en español (UTF-8 con
BOM, `;`, coma decimal, CRLF), pero eso es diseño, no prueba. Queda como mejora pendiente: abrir 2 o 3
exportaciones en Excel con una cuenta o licencia autorizada y comprobar separador, coma decimal, caracteres
especiales, fracciones exactas, enteros largos, protección contra fórmulas y tablas de iteraciones, distinguiendo
abrir el archivo de conservar todos los tipos de datos.
