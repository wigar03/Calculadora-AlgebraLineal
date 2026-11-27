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

test('Limpiar determinante borra el resultado y restablece la insignia', () => {
  const { el, contexto: c } = pagina();
  vm.runInContext('mostrarToast = () => {}; actualizarEficienciaDeterminanteUI = () => {};', c);
  const limpiados = [];
  c.window.ExportarUI = { limpiar: id => limpiados.push(id) };
  el('det-order-n').value = '2';
  el('det-result-content').innerHTML = 'Resultado anterior';
  el('det-badge-status').innerText = 'Invertible';
  c.limpiarModuloDeterminante();
  assert.equal(el('det-a-0-0').value, '0');
  assert.equal(el('det-badge-status').className, 'badge');
  assert.equal(el('det-badge-status').innerText, 'Casillas limpias');
  assert.match(el('det-result-content').innerHTML, /placeholder-text/);
  assert.doesNotMatch(el('det-result-content').innerHTML, /Resultado anterior/);
  assert.deepEqual(limpiados, ['tab-determinante']);
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
  const tex = c.vectorSolucionLinealToLatex({ solucion_particular: ['6', '17/5', '26/5', '0'],
    base_nucleo: [['-3', '-8/5', '-14/5', '1']], parametros: ['t'] });
  assert.match(tex, /\\frac\{17\}\{5\} - \\frac\{8\}\{5\}t/);
  assert.match(tex, /\\frac\{26\}\{5\} - \\frac\{14\}\{5\}t/);
  assert.equal((tex.match(/\[0\.5em\]/g) || []).length, 3);
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

test('resolver desde la vista envia las 25 celdas y cinco terminos sin redondeo', async () => {
  const { el, contexto: c, renderizados } = pagina();
  el('eq-rows-m').value = el('eq-cols-n').value = '5';
  c.renderizarEcuacionMatricial();
  ['1/3', '0.75', '-2.5', '181/60', ''].forEach((v, j) => { el(`eq-a-0-${j}`).value = v; });
  el('eq-b-4').value = '181/60';
  c.metodo = 'gauss';
  c.respuesta = { tipo_sistema: 'SCD', vector_solucion: ['2', '-1', '3', '1', '-2'],
    pasos: [{ step_number: 1, title: 'Inicio', description: 'Matriz', matrix: [['1/3', '0', '0', '0', '0', '2']] }],
    sustitucion: ['Sustitución exacta visible'], verificacion: ['Fila 1: Satisface'] };
  await c.resolverEcuacionMatricialUI();
  assert.equal(c.enviado.url, '/api/ecuaciones/resolver');
  assert.equal(c.enviado.datos.A.length, 5);
  assert.deepEqual(Array.from(c.enviado.datos.A[0]), ['1/3', '0.75', '-2.5', '181/60', '0']);
  assert.equal(c.enviado.datos.b[4], '181/60');
  assert.equal(c.enviado.datos.usar_gauss_jordan, false);
  assert.ok(renderizados.includes('Sustitución exacta visible'));
  assert.ok(renderizados.some(tex => tex.includes('\\begin{array}{ccccc|')));
});

test('la vista SCI muestra parametro libre explicito, fracciones y verificacion', async () => {
  const { el, contexto: c, renderizados } = pagina();
  el('eq-rows-m').value = el('eq-cols-n').value = '4';
  c.renderizarEcuacionMatricial();
  c.respuesta = { tipo_sistema: 'SCI', parametros: ['t'],
    solucion_particular: ['6', '17/5', '26/5', '0'], base_nucleo: [['-3', '-8/5', '-14/5', '1']],
    vector_solucion: ['6 - 3t', '17/5 - 8/5t', '26/5 - 14/5t', 't'],
    descripcion_sistema: 'x_4 = t', verificacion: ['Fila 1: Satisface para todo parámetro real'] };
  await c.resolverEcuacionMatricialUI();
  assert.match(el('eq-badge-status').innerText, /Infinitas/);
  const tex = renderizados.find(t => t.includes('\\quad t \\in \\mathbb{R}'));
  assert.ok(tex);
  assert.doesNotThrow(() => katex.renderToString(tex, { throwOnError: true }));
  assert.ok(renderizados.includes(c.respuesta.verificacion[0]));
});

test('la inversa presenta una sola comprobacion por entrada en ambos productos', async () => {
  const { el, contexto: c, renderizados } = pagina();
  el('inv-dim-n').value = '4'; c.renderizarMatrizInversaInput();
  c.respuesta = { orden_n: 4, es_invertible: true, matriz_inversa: [['1']],
    verificacion_A_por_Ainv: Array.from({ length: 16 }, (_, i) => `directa ${i}`),
    verificacion_Ainv_por_A: Array.from({ length: 16 }, (_, i) => `inversa ${i}`) };
  await c.calcularInversaUI();
  assert.equal(c.enviado.url, '/api/matrices/inversa');
  assert.equal(renderizados.filter(t => /^directa /.test(t)).length, 16);
  assert.equal(renderizados.filter(t => /^inversa /.test(t)).length, 16);
});

test('el diagnostico singular recibido aparece en la vista de inversa', async () => {
  const { el, contexto: c, renderizados } = pagina();
  el('inv-dim-n').value = '3'; c.renderizarMatrizInversaInput();
  c.respuesta = { orden_n: 3, es_invertible: false,
    mensaje_diagnostico: 'No hay pivote no nulo; rango deficiente, no existe inversa.' };
  await c.calcularInversaUI();
  assert.match(el('inv-badge-status').innerText, /Singular/);
  assert.ok(renderizados.includes(c.respuesta.mensaje_diagnostico));
});

test('determinante e inversa envian celdas textuales y el metodo seleccionado', async () => {
  const { el, contexto: c } = pagina();
  for (const prefijo of ['det', 'inv']) {
    el(prefijo === 'det' ? 'det-order-n' : 'inv-dim-n').value = '5';
    if (prefijo === 'det') c.renderizarMatrizDeterminante(); else c.renderizarMatrizInversaInput();
    el(`${prefijo}-a-0-0`).value = '1/3'; el(`${prefijo}-a-0-1`).value = '-2.5';
    c.metodo = prefijo === 'det' ? 'cofactores' : 'gauss';
    c.respuesta = { orden_n: 5, es_invertible: false, determinante: '0', determinante_decimal: '0' };
    if (prefijo === 'det') await c.calcularDeterminanteUI(); else await c.calcularInversaUI();
    assert.equal(c.enviado.datos.A.length, 5);
    assert.equal(c.enviado.datos.A[0][0], '1/3');
    assert.equal(c.enviado.datos.A[0][1], '-2.5');
    assert.equal(c.enviado.datos.metodo, c.metodo);
  }
});

test('la lista de diez parametros agrupa el indice completo para KaTeX', async () => {
  const { el, contexto: c, renderizados } = pagina();
  el('eq-rows-m').value = '1'; el('eq-cols-n').value = '10'; c.renderizarEcuacionMatricial();
  const parametros = ['t', 's', 'r', 'u', 'v', 't_6', 't_7', 't_8', 't_9', 't_10'];
  c.respuesta = { tipo_sistema: 'SCI', parametros, vector_solucion: parametros,
    solucion_particular: Array(10).fill('0'),
    base_nucleo: Array.from({ length: 10 }, (_, i) => Array.from({ length: 10 }, (_, j) => String(+(i === j)))) };
  await c.resolverEcuacionMatricialUI();
  const tex = renderizados.find(t => t.includes('\\quad t, s'));
  assert.ok(tex);
  assert.doesNotMatch(tex, /t_10/);
  const html = katex.renderToString(tex, { throwOnError: true });
  assert.ok(html.includes('<msub><mi>t</mi><mn>10</mn></msub>'));
});

test('el vector estructurado rechaza texto ambiguo sin reescribir partes de tokens', () => {
  const { contexto: c } = pagina();
  for (const texto of ['0.5/2+t', '1/2.5+t', 'x_1/2']) {
    assert.throws(() => c.vectorSolucionLinealToLatex([texto]), /separados/);
    assert.throws(() => c.vectorSolucionLinealToLatex({ solucion_particular: [texto],
      base_nucleo: [['1']], parametros: ['t'] }), /coeficiente racional/);
  }
  const tex = c.vectorSolucionLinealToLatex({ solucion_particular: ['1/4', '2/5'],
    base_nucleo: [['1', '1']], parametros: ['t'] });
  assert.match(tex, /\\frac\{1\}\{4\} \+ t/);
  assert.match(tex, /\\frac\{2\}\{5\} \+ t/);
  assert.doesNotThrow(() => katex.renderToString(tex, { throwOnError: true }));
  const variableDividida = c.vectorSolucionLinealToLatex({ solucion_particular: ['0'],
    base_nucleo: [['1/2']], parametros: ['x_1'] });
  assert.match(variableDividida, /\\frac\{1\}\{2\}x_\{1\}/);
  assert.doesNotThrow(() => katex.renderToString(variableDividida, { throwOnError: true }));
});

test('el vector estructurado conserva ceros, signos, coeficientes unitarios e indices', () => {
  const { contexto: c } = pagina();
  const tex = c.vectorSolucionLinealToLatex({ solucion_particular: ['0', '-1/2', '0'],
    base_nucleo: [['-1', '3/4', '0'], ['1/2', '-1', '0']], parametros: ['t_10', 's'] });
  assert.match(tex, /-t_\{10\} \+ \\frac\{1\}\{2\}s/);
  assert.match(tex, /-\\frac\{1\}\{2\} \+ \\frac\{3\}\{4\}t_\{10\} - s/);
  assert.match(tex, /\[0\.5em\] 0 \\end/);
  assert.doesNotThrow(() => katex.renderToString(tex, { throwOnError: true }));
});

test('KaTeX estricto interpreta los indices emitidos por Python como un solo subindice', () => {
  const { execFileSync } = require('node:child_process');
  const codigo = `import json
from src.ecuaciones.ecuacion_matricial import resolver_ecuacion_matricial as resolver
from src.solver.gauss_solver import formatear_subindices_latex
r = resolver([[0]*10], [0])
s = formatear_subindices_latex('$x_11 = t_10 + t_11$')
print(json.dumps([r.descripcion_sistema, *r.verificacion_residual, s]))`;
  const textos = JSON.parse(execFileSync('python', ['-c', codigo], {
    cwd: require('node:path').resolve(__dirname, '..'), encoding: 'utf8' }));
  let subindicesCompletos = 0;
  for (const texto of textos) {
    for (const formula of texto.matchAll(/\$([^$]+)\$/g)) {
      assert.doesNotMatch(formula[1], /_\d{2}/);
      const html = katex.renderToString(formula[1], { throwOnError: true });
      if (formula[1].includes('t_{11}')) {
        assert.ok(html.includes('<msub><mi>t</mi><mn>11</mn></msub>'));
        assert.ok(html.includes('<msub><mi>x</mi><mn>11</mn></msub>'));
      }
      if (formula[1].includes('t_{10}')) {
        assert.ok(html.includes('<msub><mi>t</mi><mn>10</mn></msub>'));
        subindicesCompletos++;
      }
    }
  }
  assert.equal(subindicesCompletos, 3);
});
