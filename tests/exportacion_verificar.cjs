/* Oráculo independiente: no importa formateadores internos de exportar.js. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { performance } = require('node:perf_hooks');
const ROOT = path.resolve(__dirname, '..');
const EXPORTAR = process.env.P2_EXPORTAR_JS || path.join(ROOT, 'src/ui/web/exportar.js');
const api = require(EXPORTAR);
const katex = require('../src/ui/web/vendor/katex/katex.min.js');

function matematicas(doc) {
  return [...doc.matchAll(/(?<!\\)\\\[([\s\S]*?)\\\]|(?<!\\)\\\(([\s\S]*?)\\\)|(?<!\\)\$\$([\s\S]*?)\$\$|(?<!\\)\$((?:\\.|[^$])*?)\$/g)]
    .map(m => m.slice(1).find(s => s !== undefined));
}

function verificarLatex(doc) {
  const errores = [], pila = [];
  for (const m of doc.matchAll(/\\(begin|end)\{([^}]+)\}/g)) {
    if (m[1] === 'begin') pila.push(m[2]);
    else if (pila.pop() !== m[2]) errores.push(`Entorno mal cerrado: ${m[0]}`);
  }
  if (pila.length) errores.push(`Entornos sin cerrar: ${pila.join(', ')}`);
  const fragmentos = matematicas(doc), unicos = new Set(fragmentos);
  let fallos = errores.length;
  for (const tex of unicos) {
    try {
      katex.renderToString(tex, { throwOnError: true, strict: 'error', trust: false });
    } catch (e) {
      fallos++;
      if (errores.length < 20) errores.push(`${tex.slice(0, 240)}: ${e.message}`);
    }
  }
  return { fragmentos: fragmentos.length, unicos: unicos.size, fallos, errores };
}

function exportar(p) {
  const antes = structuredClone(p), memoria = process.memoryUsage();
  const inicio = performance.now();
  const latex = api.procedimientoALatex(p);
  const csv = (p.tablas || []).map(t => api.tablaACSV(t, { separador: ';', decimal: ',' }));
  const tablas_latex = (p.tablas || []).map(t => api.tablaALatex(t));
  const ms = performance.now() - inicio, despues = process.memoryUsage();
  return { latex, csv, tablas_latex, mutado: JSON.stringify(antes) !== JSON.stringify(p),
    metricas: { ms, heap_delta: despues.heapUsed - memoria.heapUsed,
      rss: despues.rss, max_rss_kib: process.resourceUsage().maxRSS,
      bytes: Buffer.byteLength(latex) + csv.reduce((n, s) => n + Buffer.byteLength(s), 0) },
    validacion: verificarLatex(latex) };
}

if (process.argv.includes('--stdin')) {
  const datos = JSON.parse(fs.readFileSync(0, 'utf8'));
  process.stdout.write(JSON.stringify(datos.map(exportar)));
} else {
  const { test } = require('node:test');
  test('P2: BOM, punto y coma, coma decimal y CRLF según contrato', () => {
    const csv = api.tablaACSV({ columnas: ['k', 'x'], filas: [[1, 1.25]] },
      { separador: ';', decimal: ',' });
    assert.ok(csv.startsWith('\ufeff'), 'CSV sin BOM UTF-8: contrato exportacion.md');
    assert.match(csv, /^\ufeffk;x\r\n1;1,25(?:\r\n)?$/);
  });
  test('P2: oráculo detecta entornos desequilibrados y KaTeX inválido', () => {
    assert.ok(verificarLatex('\\begin{pmatrix}\\end{bmatrix}').fallos > 0);
    assert.ok(verificarLatex('\\[\\comandoInexistente{x}\\]').fallos > 0);
    assert.equal(verificarLatex('\\[\\frac{1}{2}\\] precio \\$2').fallos, 0);
  });
}
