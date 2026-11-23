/* Pruebas de la biblioteca base de exportación P2 (sin cargar en index.html). */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const { execFileSync } = require('node:child_process');
const ROOT = path.resolve(__dirname, '..');
const EXPORTAR_PATH = path.join(ROOT, 'src', 'ui', 'web', 'exportar.js');
const { procedimientoALatex, tablaALatex, tablaACSV, textoPlano } = require(EXPORTAR_PATH);

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
    filas: [[1, 0.6, null, 'x_l ← x_r'], [2, 1.275449275970459, 3.2695e-7, 'Finalizar, "ok"\nfin']],
  }],
  avisos: ['Nota con #1 y 100% de margen ≈ 0.1.'],
};

test('exportar.js funciona en Node y en navegador, y NO está cargado en index.html', () => {
  const html = fs.readFileSync(path.join(ROOT, 'src', 'ui', 'web', 'index.html'), 'utf8');
  assert.doesNotMatch(html, /exportar\.js/i);
  const ctx = vm.createContext({ window: {} });
  vm.runInContext(fs.readFileSync(EXPORTAR_PATH, 'utf8'), ctx, { filename: 'exportar.js' });
  for (const fn of ['procedimientoALatex', 'tablaALatex', 'tablaACSV', 'textoPlano']) {
    assert.equal(typeof ctx.window.ExportarProcedimiento[fn], 'function');
  }
});

test('tablaACSV cumple RFC 4180 y soporta Excel en español (; y coma decimal)', () => {
  const csv = tablaACSV(EJEMPLO.tablas[0]);
  assert.ok(csv.includes('\r\n'));
  assert.match(csv, /^k,x_1\^\{\(k\)\},\\varepsilon_a\\;\(\\%\),\\text\{Acción\}\r\n/);
  assert.ok(csv.includes('1,0.6,,x_l ← x_r\r\n'));
  assert.ok(csv.includes('2,1.275449275970459,3.2695e-7,"Finalizar, ""ok""\nfin"'));

  const es = tablaACSV({
    titulo: 'Excel ES',
    columnas: ['k', 'valor', 'nota;extra'],
    filas: [[1, 0.6, 'v1.0; "cita"'], [2, -3.5e-7, '-12.75']],
  }, { separador: ';', decimal: ',' });
  const lineas = es.split('\r\n');
  assert.equal(lineas[0], 'k;valor;"nota;extra"');
  assert.equal(lineas[1], '1;0,6;"v1.0; ""cita"""');
  assert.equal(lineas[2], '2;-3,5e-7;-12,75');
});

test('tablaALatex genera tabla compilable con encabezados matemáticos, científica y escapes', () => {
  const tex = tablaALatex(EJEMPLO.tablas[0]);
  assert.ok(tex.includes('\\begin{table}') && tex.includes('\\begin{tabular}'));
  assert.ok(tex.includes('$k$') && tex.includes('$x_1^{(k)}$') && tex.includes('$\\varepsilon_a\\;(\\%)$'));
  assert.ok(tex.includes('3.2695 \\times 10^{-7}'));
  assert.ok(tex.includes('---'));
  assert.ok(tex.includes('\\leftarrow'));
  assert.doesNotMatch(tex, /(?<!\\)←/);
});

test('procedimientoALatex genera documento pdflatex completo con amsmath/amssymb y secciones', () => {
  const doc = procedimientoALatex(EJEMPLO);
  assert.ok(doc.includes('\\documentclass'));
  assert.ok(doc.includes('\\usepackage{amsmath,amssymb}'));
  assert.ok(doc.includes('\\begin{document}') && doc.includes('\\end{document}'));
  assert.ok(doc.includes('100\\%') && doc.includes('\\&') && doc.includes('pruebas\\_base'));
  assert.ok(doc.includes('\\begin{pmatrix}') && doc.includes('5/2'));
  assert.ok(doc.includes('\\det(A) = 10'));
  assert.ok(doc.includes('\\checkmark') && doc.includes('\\#1') && doc.includes('\\approx'));
  assert.ok(doc.includes('\\begin{tabular}'));

  const py = "import json; from pathlib import Path; from src.procedimientos import adjuntar; "
    + "c=json.loads(Path('tests/validacion/golden/iterativos.json').read_text(encoding='utf-8'))[2]; "
    + "print(json.dumps(adjuntar(c['ruta'], c['respuesta'], c['cuerpo'])['procedimiento']))";
  const real = JSON.parse(execFileSync('python', ['-c', py], { cwd: ROOT, encoding: 'utf8', env: { ...process.env, PYTHONIOENCODING: 'utf-8' } }));
  const docReal = procedimientoALatex(real);
  assert.ok(docReal.includes('\\begin{document}') && docReal.includes('Jacobi') && docReal.includes('Gauss-Seidel'));
  assert.equal((docReal.match(/\\begin\{tabular\}/g) || []).length, 2);
});

test('textoPlano produce salida legible con todas las secciones y sin etiquetas HTML', () => {
  const txt = textoPlano(EJEMPLO);
  assert.ok(txt.includes('Determinante 2x2'));
  assert.ok(txt.includes('det(A)') || txt.includes('\\det(A)'));
  assert.ok(txt.includes('1.275449275970459') && txt.includes('Iteraciones de prueba'));
  assert.ok(txt.includes('Comprobación') && txt.includes('Nota con #1'));
  assert.doesNotMatch(txt, /<\/?(?:div|table|tr|td|p|script|img)\b/i);
});
