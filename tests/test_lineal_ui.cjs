const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const vm = require('node:vm');
const katex = require('../src/ui/web/vendor/katex/katex.min.js');
const source = readFileSync(require.resolve('../src/ui/web/app.js'), 'utf8');

function pagina() {
  const nodos = new Map();
  const nodo = () => ({ style: {}, children: [], value: '', addEventListener() {},
    set innerHTML(v) { this.html = v; this.children = []; },
    get innerHTML() { return this.html || ''; },
    appendChild(hijo) { this.children.push(hijo); if (hijo.id) nodos.set(hijo.id, hijo); },
    querySelectorAll() { return []; } });
  const el = id => { if (!nodos.has(id)) nodos.set(id, nodo()); return nodos.get(id); };
  const renderizados = [];
  const contexto = vm.createContext({ document: { addEventListener() {}, createElement: nodo,
    getElementById: el, querySelector: () => ({ value: contexto.metodo || 'gauss_jordan' }),
    querySelectorAll: () => [] }, window: {}, console, renderizados,
    fetch: async (url, opciones) => {
      contexto.enviado = { url, datos: JSON.parse(opciones.body) };
      return { ok: true, json: async () => contexto.respuesta || {} };
    } });
  vm.runInContext(source, contexto);
  vm.runInContext(`renderLatexElement = (el, tex) => { el.innerText = tex; renderizados.push(tex); };
    renderMixedLatex = (el, tex) => { el.innerText = tex; renderizados.push(tex); };`, contexto);
  return { el, contexto, renderizados };
}

test('los controles HTML permiten sistemas, inversas y determinantes de orden 5', () => {
  const html = readFileSync(require.resolve('../src/ui/web/index.html'), 'utf8');
  for (const id of ['eq-rows-m', 'eq-cols-n', 'inv-dim-n', 'det-order-n']) {
    assert.ok(Number(html.match(new RegExp(`id="${id}"[^>]*max="(\\d+)"`))[1]) >= 5);
  }
});

test('las grillas 5x5 conservan fracciones y decimales como texto', () => {
  const { el, contexto: c } = pagina();
  for (const id of ['eq-rows-m', 'eq-cols-n', 'inv-dim-n', 'det-order-n']) el(id).value = '5';
  c.renderizarEcuacionMatricial(); c.renderizarMatrizInversaInput(); c.renderizarMatrizDeterminante();
  assert.equal(el('eq-augmented-grid').children.filter(n => n.type === 'text').length, 30);
  assert.equal(el('inv-matrix-grid').children.length, 25);
  assert.equal(el('det-matrix-grid').children.length, 25);
  for (const prefijo of ['inv', 'det']) {
    ['1/3', '0.75', '-2.5', '181/60'].forEach((v, j) => { el(`${prefijo}-a-0-${j}`).value = v; });
    const valores = prefijo === 'inv' ? c.obtenerMatrizInversaValores() : c.obtenerMatrizDeterminanteValores();
    assert.deepEqual(Array.from(valores[0]).slice(0, 4), ['1/3', '0.75', '-2.5', '181/60']);
  }
});

test('LaTeX parametrico conserva cada fraccion y el parametro fuera del denominador', () => {
  const { contexto: c } = pagina();
  const tex = c.vectorSolucionLinealToLatex(['6 - 3t', '17/5 - 8/5t', '26/5 - 14/5t', 't']);
  assert.match(tex, /\\frac\{17\}\{5\} - \\frac\{8\}\{5\}t/);
  assert.match(tex, /\\frac\{26\}\{5\} - \\frac\{14\}\{5\}t/);
  assert.doesNotThrow(() => katex.renderToString(tex, { throwOnError: true }));
});

test('LaTeX de matrices y matrices aumentadas renderiza racionales exactos', () => {
  const { contexto: c } = pagina();
  const a = [['1/3', '0.75', '-2.5'], ['0', '-1/2', '181/60']];
  for (const tex of [c.matrixToLatex(a), c.augmentedMatrixToLatex(a, 2)]) {
    assert.match(tex, /\\frac\{181\}\{60\}/);
    assert.doesNotThrow(() => katex.renderToString(tex, { throwOnError: true }));
  }
  assert.match(c.augmentedMatrixToLatex(a, 2), /\{cc\|c\}/);
});
