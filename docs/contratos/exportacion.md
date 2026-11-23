# Contrato de P2: copiar LaTeX, exportar CSV e imprimir (etapa 4)

Autor: integrador. Decisiones del propietario (2026-11-23): un botón «Exportar» por módulo, en la cabecera del
módulo, implementado como **un único componente reutilizable**; CSV con `;` y coma decimal; subtítulo general
«Álgebra lineal y métodos numéricos con procedimientos paso a paso». Ninguna otra modificación de UX.

## Componente (`src/ui/web/exportar-ui.js` + `exportar.js`, Antigravity)
- Un botón «Exportar» con el estilo existente `btn-clear` e iconos lucide en la cabecera de cada uno de los 11
  módulos, creado por el componente (no 11 copias). Menú con: **Copiar LaTeX**, **Exportar CSV** (solo si el
  resultado tiene tablas) e **Imprimir / guardar como PDF**.
- Actúa sobre el resultado **actual** del módulo: el `procedimiento` de la última respuesta válida mostrada. Queda
  deshabilitado (`disabled` y `aria-disabled`) sin resultado, tras un error y cuando la entrada se invalida o se limpia.
  El contenido exportado nunca puede corresponder a un resultado que ya no se ve.
- Teclado: botón enfocable; Enter/Espacio abre; flechas recorren; Escape cierra y devuelve el foco; `aria-haspopup`,
  `aria-expanded`, `role="menu"/"menuitem"`. Confirmación «Copiado» en una región `aria-live`. Móvil: a todo el ancho
  bajo la descripción, áreas táctiles de al menos 44 px, sin desbordamiento horizontal.
- Sin red: todo se genera en el navegador o en la ventana de escritorio; sin bibliotecas externas.

## CSV
- UTF-8 **con BOM**, separador `;`, decimal `,`, saltos `\r\n`, campos con `;`, `"`, saltos o espacios extremos
  entre comillas y `"` duplicada (RFC 4180). **Todas** las filas de todas las tablas, sin truncar.
- Números: flotantes con la precisión completa de la respuesta (`repr`, sin redondeo de presentación), coma decimal,
  notación científica `1,5E-07`. Enteros tal cual.
- Fracciones exactas `p/q` (validadas con `^-?\d+/\d+$`): Excel las convertiría en fechas. Se escriben como texto
  con la fórmula fija `="p/q"` (campo CSV `"=""p/q"""`), solo tras la validación anterior.
- **Inyección de fórmulas:** cualquier celda de texto que empiece por `=`, `+`, `-`, `@`, tabulación o retorno y no sea
  un número válido ni una fracción validada se prefija con `'`. Ningún texto procedente del usuario (funciones,
  mensajes) puede producir una fórmula.

## LaTeX
Documento completo compilable (`\documentclass{article}`, `amsmath`, `amssymb`, `\usepackage[utf8]{inputenc}`,
`\usepackage[spanish]{babel}`), con entrada, pasos, resultado, verificación y tablas (`tabular`, partidas con
`longtable` si son largas). Los fragmentos se copian **tal como los genera la respuesta**, sin recalcular.

## Impresión / PDF
`src/ui/web/impresion.css` con `media="print"`: imprime solo el módulo activo (título, entrada resumida,
procedimiento, resultado, verificación, tablas con encabezado repetido, gráficas); oculta barra lateral, navegación,
controles y botones; evita cortar filas, fórmulas y matrices (`break-inside: avoid`); fórmulas KaTeX como texto
vectorial. No cambia nada en pantalla.

## Verificación independiente (Codex 2)
Para las respuestas reales de los 11 módulos (corpus golden y casos largos: Jacobi 20×20 con 10 000 iteraciones,
bisección con 1000 iteraciones): CSV conforme al contrato (BOM, `;`, CRLF, coma decimal, sin pérdida de precisión al
releerlo, fracciones como texto, sin fórmulas inyectables), LaTeX con entornos equilibrados y cada fragmento
renderizable con KaTeX estricto, y tablas completas.
