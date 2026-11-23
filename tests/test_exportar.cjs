/* Pruebas de la biblioteca de exportación P2 (contrato CSV y LaTeX). */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const { execFileSync } = require('node:child_process');
const ROOT = path.resolve(__dirname, '..');
const EXPORTAR_PATH = path.join(ROOT, 'src', 'ui', 'web', 'exportar.js');
const katex = require(path.join(ROOT, 'src', 'ui', 'web', 'vendor', 'katex', 'katex.min.js'));
const { procedimientoALatex, tablaALatex, tablaACSV, tablasACSV, textoPlano } = require(EXPORTAR_PATH);

const EJEMPLO = {
  version: 1, modulo: 'determinante',
  titulo: 'Determinante 2x2 con 100% de exactitud & pruebas_base',
  entrada: [{ etiqueta: 'A', latex: '\\begin{pmatrix} 4 & 7 \\\\ 2 & 6 \\end{pmatrix}' }],
  pasos: [{
    titulo: 'Triangulación con $f_2 \\leftarrow f_2 - \\frac{1}{2}f_1$',
    texto: 'Se elimina la entrada bajo el pivote (50% listo) usando $a_{21}=2$.',
    latex: ['U = \\begin{pmatrix} 4 & 7 \\\\ 0 & \\frac{5}{2} \\end{pmatrix}'],
    matriz: [['4', '7'], ['0', '5/2']],
    detalles: ['Pivote principal: $4$ ✓', 'Signo de permutación: $+1$'],
  }],
  resultado: [{ etiqueta: '\\det(A)', latex: '10' }],
  verificacion: ['Comprobación: $4 \\cdot 6 - 7 \\cdot 2 = 10$ ✓'],
  tablas: [{
    titulo: 'Iteraciones de prueba',
    columnas: ['k', 'x_1^{(k)}', '\\varepsilon_a\\;(\\%)', '\\text{Acción}'],
    filas: [[1, 0.6, null, 'x_l ← x_r'], [2, 1.275449275970459, 1.5e-7, 'Finalizar; "ok"\nfin']],
  }],
  avisos: ['Nota con #1 y 100% de margen ≈ 0.1.'],
};

test('exportar.js funciona en Node y en navegador, y carga en index.html', () => {
  const html = fs.readFileSync(path.join(ROOT, 'src', 'ui', 'web', 'index.html'), 'utf8');
  assert.match(html, /impresion\.css[^>]*media="print"/i);
  assert.match(html, /exportar\.js/i);
  assert.match(html, /exportar-ui\.js/i);
  const ctx = vm.createContext({ window: {} });
  vm.runInContext(fs.readFileSync(EXPORTAR_PATH, 'utf8'), ctx, { filename: 'exportar.js' });
  for (const fn of ['procedimientoALatex', 'tablaALatex', 'tablaACSV', 'tablasACSV', 'textoPlano']) {
    assert.equal(typeof ctx.window.ExportarProcedimiento[fn], 'function');
  }
});

test('tablaACSV cumple contrato: BOM, ;, decimal ,, CRLF, científica, fracciones e inyección', () => {
  const csv = tablaACSV({
    titulo: 'Contrato', columnas: ['k', 'x', 'frac', 'nota', '=col'],
    filas: [
      [1, 1.275449275970459, '5/2', '  esp  ', '=SUM(A1:A2)'],
      [2, 1.5e-7, '-181/60', 'a; "b"\nc', '+cmd|calc'],
      [3, -42, '1/2+A1', '-A1', '@SUM(1,2)'],
      [4, null, '\t=1', '\r=2', '-12.75'],
    ],
  });
  assert.ok(csv.startsWith('\uFEFF'));
  const l = csv.slice(1).split('\r\n');
  assert.equal(l[0], "k;x;frac;nota;'=col");
  assert.equal(l[1], '1;1,275449275970459;"=""5/2""";"  esp  ";\'=SUM(A1:A2)');
  assert.equal(l[2], '2;1,5E-07;"=""-181/60""";"a; ""b""\nc";\'+cmd|calc');
  assert.equal(l[3], "3;-42;1/2+A1;'-A1;'@SUM(1,2)");
  assert.equal(l[4], '4;;\'\t=1;"\'\r=2";-12,75');
  const multi = tablasACSV([{ titulo: 'T1', columnas: ['k', 'v'], filas: [[1, 0.5]] }, { titulo: 'T2', columnas: ['k', 'v'], filas: [[1, 1e-8]] }]);
  assert.ok(multi.startsWith('\uFEFF') && !multi.slice(1).includes('\uFEFF') && multi.includes('T1\r\nk;v\r\n1;0,5\r\n\r\nT2\r\nk;v\r\n1;1E-08'));
});

test('tablaALatex usa tabular en tablas cortas y longtable en largas', () => {
  const tex = tablaALatex(EJEMPLO.tablas[0]);
  assert.ok(tex.includes('\\begin{table}') && tex.includes('\\begin{tabular}'));
  assert.ok(tex.includes('$k$') && tex.includes('$x_1^{(k)}$') && tex.includes('1.5 \\times 10^{-7}') && tex.includes('---') && tex.includes('\\leftarrow'));
  assert.doesNotMatch(tex, /(?<!\\)←/);
  const larga = tablaALatex({ titulo: 'Larga', columnas: ['k', 'x_k'], filas: Array.from({ length: 45 }, (_, i) => [i + 1, i / 10]) });
  assert.ok(larga.includes('\\begin{longtable}') && larga.includes('\\endfirsthead') && !larga.includes('\\begin{table}'));
});

test('procedimientoALatex genera documento compilable con babel spanish, longtable y KaTeX estricto en los 33 golden', () => {
  const doc = procedimientoALatex(EJEMPLO);
  assert.ok(doc.includes('\\documentclass') && doc.includes('\\usepackage[spanish]{babel}') && doc.includes('\\usepackage{amsmath,amssymb}') && doc.includes('\\usepackage{longtable}'));
  assert.ok(doc.includes('\\begin{document}') && doc.includes('\\end{document}') && doc.includes('100\\%') && doc.includes('\\det(A) = 10'));
  const py = "import json, pathlib; from src.procedimientos import adjuntar; "
    + "out=[adjuntar(c['ruta'],c['respuesta'],c['cuerpo'])['procedimiento'] for p in sorted(pathlib.Path('tests/validacion/golden').glob('*.json')) "
    + "for c in json.loads(p.read_text(encoding='utf-8')) if 'procedimiento' in adjuntar(c['ruta'],c['respuesta'],c['cuerpo'])]; print(json.dumps(out))";
  const procs = JSON.parse(execFileSync('python', ['-c', py], { cwd: ROOT, encoding: 'utf8', env: { ...process.env, PYTHONIOENCODING: 'utf-8' } }));
  assert.equal(procs.length, 33);
  for (const proc of procs) {
    const tex = procedimientoALatex(proc);
    assert.equal((tex.match(/\\begin\{/g) || []).length, (tex.match(/\\end\{/g) || []).length);
    for (const m of tex.matchAll(/\\\[\n([\s\S]*?)\n\\\]/g)) katex.renderToString(m[1], { displayMode: true, throwOnError: true, strict: 'error' });
    for (const m of tex.matchAll(/(?<!\\)\$([^$\n]+?)\$/g)) katex.renderToString(m[1], { displayMode: false, throwOnError: true, strict: 'error' });
  }
});

test('textoPlano produce salida legible con todas las secciones y sin etiquetas HTML', () => {
  const txt = textoPlano(EJEMPLO);
  assert.ok(txt.includes('Determinante 2x2') && txt.includes('1.275449275970459'));
  assert.ok(txt.includes('Comprobación') && txt.includes('Nota con #1'));
  assert.doesNotMatch(txt, /<\/?(?:div|table|tr|td|p|script|img)\b/i);
});
