/* Oráculo independiente: no importa formateadores internos de exportar.js. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { performance } = require('node:perf_hooks');
const ROOT = path.resolve(__dirname, '..');
const EXPORTAR = process.env.P2_EXPORTAR_JS || path.join(ROOT, 'src/ui/web/exportar.js');
const api = require(EXPORTAR);
const katex = require('../src/ui/web/vendor/katex/katex.min.js');
const MATEMATICAS = /(?<!\\)\\\[([\s\S]*?)\\\]|(?<!\\)\\\(([\s\S]*?)\\\)|(?<!\\)\$\$([\s\S]*?)\$\$|(?<!\\)\$((?:\\.|[^$])*?)\$/g;

function matematicas(doc) {
  return [...doc.matchAll(MATEMATICAS)]
    .map(m => m.slice(1).find(s => s !== undefined));
}

function verificarLatex(doc) {
  const errores = [], pila = [];
  for (const m of doc.matchAll(/\\(begin|end)\{([^}]+)\}/g)) {
    if (m[1] === 'begin') pila.push(m[2]);
    else if (pila.pop() !== m[2]) errores.push(`Entorno mal cerrado: ${m[0]}`);
  }
  if (pila.length) errores.push(`Entornos sin cerrar: ${pila.join(', ')}`);
  if (/(?<!\\)(?:\$|\\[[\]()])/.test(doc.replace(MATEMATICAS, ''))) {
    errores.push('Delimitador matemático sin pareja');
  }
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
    assert.ok(verificarLatex('texto $x+1').fallos > 0);
    assert.equal(verificarLatex('\\[\\frac{1}{2}\\] precio \\$2').fallos, 0);
  });
  test('P2: texto y cabeceras no pueden inyectar fórmulas', () => {
    for (const s of ['=cmd|x', '@SUM(1)', '+SUM(A1)', '-SUM(A1)', '\t=1', '\r=1']) {
      const texto = api.tablaACSV({ columnas: [s], filas: [[s]] }, { separador: ';', decimal: ',' });
      const prefijos = texto.match(/'/g) || [];
      assert.equal(prefijos.length, 2, `Cabecera/celda sin prefijo protector: ${JSON.stringify(s)}`);
    }
  });
  test('P2: fracciones solo usan una fórmula fija tras validar toda la cadena', () => {
    const texto = api.tablaACSV({ columnas: ['q'], filas: [['1/2'], ['-17/19'], ['=1/2']] },
      { separador: ';', decimal: ',' });
    assert.ok(texto.includes('"=""1/2"""'), 'Fracción 1/2 sin protección contra fechas');
    assert.ok(texto.includes('"=""-17/19"""'), 'Fracción negativa sin protección');
    assert.ok(texto.includes("'=1/2"), 'No se puede aceptar una fórmula de usuario como fracción');
  });
  test('P2: NaN e infinitos se rechazan explícitamente o se conservan como aviso', () => {
    for (const n of [NaN, Infinity, -Infinity]) {
      try {
        const texto = api.tablaACSV({ columnas: ['x'], filas: [[n]] }, { separador: ';', decimal: ',' });
        assert.match(texto, /NaN|Infinity|no finito/i, `Valor no finito borrado: ${n}`);
      } catch (e) {
        if (e instanceof assert.AssertionError) throw e;
        assert.match(e.message, /finito|NaN|Infinity|n[uú]mero/i, 'Rechazo sin diagnóstico');
      }
    }
  });
  test('P2: el cero negativo se normaliza a 0 para las hojas reales', () => {
    const valores = [-0.0, '-0', '-0.00', '-0e8'];
    const texto = api.tablaACSV({ columnas: ['x'], filas: valores.map(v => [v]) });
    assert.equal(texto, '\ufeffx\r\n0\r\n0\r\n0\r\n0');
  });
  test('P2: enteros de más de 15 cifras se conservan como texto validado', () => {
    for (const valor of ['9007199254740993123456789', '1234567890123456', '-1234567890123456', '0001234567890123456']) {
      const texto = api.tablaACSV({ columnas: ['n'], filas: [[valor]] });
      assert.equal(texto, `\ufeffn\r\n"=""${valor}"""`);
    }
  });
  test('P2: denominador cero impide generar una fórmula de fracción', () => {
    const pares = [['1/0', '1/0'], ['-1/0', "'-1/0"], ['0/0', '0/0'], ['17/000', '17/000'], ['-17/000', "'-17/000"]];
    for (const [valor, esperado] of pares) {
      assert.equal(api.tablaACSV({ columnas: ['q'], filas: [[valor]] }), `\ufeffq\r\n${esperado}`);
    }
  });
  test('P2: prefijo seguro tras controles y espacios sin cambiar celdas ni cabeceras', () => {
    const inicios = [' ', '\n', '\r', '\t', '\v', '\f', '\x00', '\x1f', '\x7f', '\u00a0', '\u2003', '\u3000', '\ufeff', ' \n\t\u00a0\u2003\u3000'];
    for (const inicio of inicios) for (const formula of ['=1+1', '+SUM(A1)', '-SUM(A1)', '@SUM(A1)']) {
      const valor = inicio + formula, protegido = "'" + valor;
      const campo = /[\r\n]/.test(valor) ? `"${protegido}"` : protegido;
      const texto = api.tablaACSV({ columnas: [valor], filas: [[valor]] });
      assert.equal(texto, `\ufeff${campo}\r\n${campo}`, `Texto alterado o inseguro: ${JSON.stringify(valor)}`);
    }
  });
  test('P2: cabeceras racionales y enteros largos muestran su texto exacto sin apóstrofo', () => {
    for (const valor of ['1/2', '-17/19', '0003/0007', '9007199254740993123456789']) {
      const celda = `"=""${valor}"""`;
      assert.equal(api.tablaACSV({ columnas: [valor], filas: [[valor]] }), `\ufeff${celda}\r\n${celda}`);
    }
  });
}
