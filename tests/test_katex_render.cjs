/* Pruebas de renderizado KaTeX real (throwOnError: true) sin paquetes externos. */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const path = require('node:path');
const katex = require('../src/ui/web/vendor/katex/katex.min.js');
const bis = require('../src/ui/web/biseccion.js');
const rf = require('../src/ui/web/regla-falsa.js');
const nr = require('../src/ui/web/newton-raphson.js');
const sc = require('../src/ui/web/secante.js');
const G = require('../src/ui/web/grafica-funciones.js');

const ROOT = path.resolve(__dirname, '..');

function renderEstricto(latex, displayMode = false) {
  const html = katex.renderToString(latex, { displayMode, throwOnError: true, strict: 'warn' });
  assert.ok(html.includes('katex'), `HTML inesperado para: ${latex}`);
  return html;
}

function extraerMatematicas(texto) {
  return [...texto.matchAll(/\$\$([\s\S]*?)\$\$|\$([\s\S]*?)\$/g)]
    .map(m => ({ latex: (m[1] ?? m[2]).trim(), display: Boolean(m[1]) }));
}

function latexPython(expresiones) {
  const py = 'import json,sys; from src.biseccion.expresiones import Expresion; '
    + 'print(json.dumps([Expresion(e).latex() for e in json.loads(sys.stdin.read())]))';
  return JSON.parse(execFileSync('python', ['-c', py], { cwd: ROOT, input: JSON.stringify(expresiones), encoding: 'utf8', env: { ...process.env, PYTHONIOENCODING: 'utf-8' } }));
}

test('KaTeX renderiza las 18 ecuaciones, derivadas y 2 incompletas del banco sin errores', () => {
  const py = [
    'import json, re',
    'from tests.validacion.banco_raices import ECUACIONES, INCOMPLETOS',
    'from src.biseccion.expresiones import Expresion',
    'from src.derivadas.motor import analizar_derivada',
    'ex = lambda s: re.sub(r"(\\d)\\s*(?=[A-Za-z])", r"\\1*", s)',
    'items = []',
    'for k, d in ECUACIONES.items():',
    '  r = analizar_derivada(ex(d["ecuacion"]))',
    '  items += [(k+"_f", Expresion(d["funcion"]).latex()), (k+"_e", r["funcion_latex"]), (k+"_d", r["derivada_latex"])]',
    'for k, d in INCOMPLETOS.items(): items.append((k, Expresion(ex(d["expresion"])).latex()))',
    'print(json.dumps(items))',
  ].join('\n');
  const items = JSON.parse(execFileSync('python', ['-c', py], { cwd: ROOT, encoding: 'utf8', env: { ...process.env, PYTHONIOENCODING: 'utf-8' } }));
  assert.equal(items.length, 56);
  for (const [id, latex] of items) {
    const html = renderEstricto(id.endsWith('_d') ? `f'(x) = ${latex}` : `f(x) = ${latex}`, true);
    assert.ok(html.includes('x'), `Se perdió x en ${id}: ${latex}`);
  }
});

test('KaTeX renderiza fracciones compuestas, radicales, potencias, trig/log, científica y largas', () => {
  const casos = [
    ['((x+1)/(x-1))/(x^2+1)', '\\frac'], ['sqrt(1 + sqrt(x^2 + 1))', '\\sqrt'],
    ['(x+1)^(2^3) + e^(x^2 - 1/x)', 'e^{'], ['asin(x)+acos(x)+atan(x)+tan(x)+sen(x)+cos(x)', '\\arcsin'],
    ['ln(abs(x) + 1) + log(x^2 + 10)', '\\log_{10}'], ['1e-10*x + 2.5e8 - 1e-10^2', '\\times 10'],
    ['x^4 - 5*x^3 + 0.5*x^2 - 11*x + 10 + cos(pi*x)/(x^2 + 1) - e^(-x/2) + sqrt(x^2 + 4)', '\\pi'],
  ];
  const latexs = latexPython(casos.map(c => c[0]));
  casos.forEach(([expr, simbolo], idx) => {
    assert.ok(latexs[idx].includes(simbolo), `Falta '${simbolo}' en ${latexs[idx]} (${expr})`);
    renderEstricto(latexs[idx], true);
  });
});

test('KaTeX renderiza todo el LaTeX generado por las páginas de raíces (tablas y resultados)', () => {
  for (const v of [0, -1e-15, 1e21, 0.76392822265625, -38.26311875, null]) {
    for (const l of [bis.numeroLatex(v), bis.numeroLatex(v, true), rf.numeroLatex(v), G.numeroLatex(v)]) renderEstricto(l);
  }
  renderEstricto(sc.sustitucion({ n: 1, a: 1, b: 2, fa: -2, fb: 4, c: 4 / 3 }), true);
  nr.primeraLatex({ x0: 1.5, f_x0: -0.125, df_x0: 5.75, x1: 1.52173913 }).forEach(l => renderEstricto(l, true));
  nr.detalleLatex({ n: 1, x: 1.52, error_absoluto: 0.02, error_relativo: 0.013 }, { x: 1.5, fx: -0.125, dfx: 5.75 }).forEach(l => renderEstricto(l, true));
  nr.detalleLatex({ n: 1, x: 0, error_absoluto: 1, error_relativo: null }, { x: 1, fx: 1, dfx: 1 }).forEach(l => renderEstricto(l, true));
  renderEstricto(rf.textoTramos([{ desde: -1, hasta: 0, abierto_izquierda: false, abierto_derecha: true },
    { desde: 0, hasta: 1.3, abierto_izquierda: true, abierto_derecha: false }]));
  for (const l of ['\\varepsilon_a\\;(\\%)', 'b \\leftarrow c', 'a \\leftarrow c', 'x_u \\leftarrow x_r', 'x_l \\leftarrow x_r',
    'x_{n-1}', 'x_{n+1}', '|f(x_{n+1})|', "f'(x_n)", 'E_a', '\\varepsilon_r']) renderEstricto(l);
  const mixtos = [
    ...Object.values(nr.MOTIVOS), ...Object.values(sc.MOTIVOS),
    nr.compararErrores(0.1, 0.05, 2), nr.compararErrores(0.1, 0.2, 0.5),
    rf.describirDiscontinuidad({ tipo: 'asintota', x: 1.5707963, desde: 1.5707963, hasta: 1.5707963 }),
    rf.describirDiscontinuidad({ tipo: 'fuera_de_dominio', x: -0.5, desde: -1, hasta: 0 }),
    G.textoTolerancia({ digitada: 1e-6, margen: 0.1, limite: 1.1e-6, valor_final: 1.05e-6, usada: 'cercana', exceso_porcentual: 5 }),
  ];
  for (const texto of mixtos) for (const { latex, display } of extraerMatematicas(texto)) renderEstricto(latex, display);
});
