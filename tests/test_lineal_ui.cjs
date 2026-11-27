const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const vm = require('node:vm');
const katex = require('../src/ui/web/vendor/katex/katex.min.js');
const source = readFileSync(require.resolve('../src/ui/web/app.js'), 'utf8');

function pagina() {
  const nodos = new Map();
  const nodo = () => ({ style: {}, children: [], value: '', listeners: {},
    addEventListener(t, fn) { (this.listeners[t] ||= []).push(fn); },
    setAttribute(k, v) { this[k] = v; },
    getAttribute(k) { return this[k]; },
    prepend(hijo) { this.children.unshift(hijo); },
    set innerHTML(v) { this.html = v; this.children = []; },
    get innerHTML() { return this.html || ''; },
    appendChild(hijo) { this.children.push(hijo); if (hijo.id) nodos.set(hijo.id, hijo); },
    querySelector(s) { return (this.selectores ||= {})[s] ||= nodo(); }, querySelectorAll() { return []; } });
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

test('INC-034 C-27: 01–06 avisan de ceros asumidos y limpian el aviso con cada acción', async () => {
  const casos = [
    ['vec', 'calcularOperacionVector', 'cargarEjemploVector', 'limpiarModuloVectores', ['vec-u-1', 'vec-v-0'], ['u[2]', 'v[1]']],
    ['comb', 'evaluarCombinacionLinealUI', 'cargarEjemploCombinacion', 'limpiarModuloCombinacion', ['comb-v-1-0', 'comb-b-0'], ['v_2[1]', 'b[1]']],
    ['mat', 'operarMatrices', 'cargarEjemploMatrices', 'limpiarModuloMatrices', ['mat-a-1-0', 'mat-b-0-1'], ['A[2,1]', 'B[1,2]']],
    ['inv', 'calcularInversaUI', 'cargarEjemploInversa', 'limpiarModuloInversa', ['inv-a-0-1', 'inv-a-1-0'], ['A[1,2]', 'A[2,1]']],
    ['eq', 'resolverEcuacionMatricialUI', 'cargarEjemploEcuacion', 'limpiarModuloEcuaciones', ['eq-a-1-2', 'eq-b-0'], ['A[2,3]', 'b[1]']],
    ['det', 'calcularDeterminanteUI', 'cargarEjemploDeterminante', 'limpiarModuloDeterminante', ['det-a-1-2', 'det-a-0-1'], ['A[2,3]', 'A[1,2]']]
  ];
  for (const [prefijo, calcular, ejemplo, limpiar, ids, etiquetas] of casos) {
    const { el, contexto: c } = pagina();
    vm.runInContext('mostrarToast = () => {};', c);
    c.respuesta = { resultado_str: '(0, 0, 0)', matriz_resultado: [['0']],
      es_combinacion: false, tipo_sistema: 'SI', orden_n: 3, es_invertible: false,
      determinante: '0', determinante_decimal: '0' };
    const caja = el(`${prefijo}-result-content`);
    const avisos = () => caja.children.filter(n => n.textContent?.startsWith('Se tomaron como 0'));
    for (const accion of ['recalcular', 'limpiar', 'ejemplo', 'pendiente']) {
      c[ejemplo](prefijo === 'det' ? 3 : 1);
      ids.forEach(id => { el(id).value = '   '; });
      await c[calcular]('suma');
      assert.equal(avisos().length, 1, `${prefijo}: falta aviso`);
      for (const etiqueta of etiquetas) assert.ok(avisos()[0].textContent.includes(etiqueta));
      assert.equal(avisos()[0].role, 'status');
      assert.ok(JSON.stringify(c.enviado.datos).includes('"0"'));
      ids.forEach(id => assert.equal(el(id).value, '   ', 'No modifica las entradas'));
      if (prefijo === 'comb') { c.cambiarNotacionCombinacion('columna'); assert.equal(avisos().length, 1); }
      if (accion === 'recalcular') {
        ids.forEach(id => { el(id).value = '0'; });
        await c[calcular]('suma');
      } else if (accion === 'pendiente') {
        c.fetch = () => new Promise(() => {}); c[calcular]('suma');
      } else if (accion === 'limpiar') c[limpiar]();
      else c[ejemplo](prefijo === 'det' ? 3 : 1);
      assert.equal(avisos().length, 0, `${prefijo}: aviso obsoleto tras ${accion}`);
    }
  }
});

test('INC-034 C-27: solo se avisa de los operandos usados y conserva fracciones', async () => {
  const { el, contexto: c } = pagina();
  vm.runInContext('mostrarToast = () => {};', c);
  c.respuesta = { resultado_str: '(1, 2, 3)', matriz_resultado: [['1/3']] };
  c.cargarEjemploVector(1); el('vec-v-0').value = '';
  await c.calcularOperacionVector('escalar_u');
  assert.ok(!el('vec-result-content').children.some(n => n.role === 'status'));
  c.cargarEjemploMatrices(1); el('mat-a-0-0').value = ''; el('mat-b-0-0').value = '1/3';
  await c.operarMatrices('transpuesta_b');
  assert.ok(!el('mat-result-content').children.some(n => n.role === 'status'));
  assert.equal(c.enviado.datos.B[0][0], '1/3');
  el('mat-b-0-0').value = ' \t'; await c.operarMatrices('transpuesta_b');
  const aviso = el('mat-result-content').children.find(n => n.role === 'status');
  assert.equal(aviso.textContent, 'Se tomaron como 0 las casillas vacías: B[1,1].');
  assert.equal(c.enviado.datos.B[0][0], '0');
  const vacias = []; el('mat-b-0-0').value = '0';
  assert.equal(c.valorCasillaLineal(el('mat-b-0-0'), vacias), '0');
  assert.deepEqual(vacias, []);
});

test('los controles HTML permiten sistemas, inversas y determinantes de orden 5', () => {
  const html = readFileSync(require.resolve('../src/ui/web/index.html'), 'utf8');
  for (const id of ['eq-rows-m', 'eq-cols-n', 'inv-dim-n', 'det-order-n']) {
    assert.ok(Number(html.match(new RegExp(`id="${id}"[^>]*max="(\\d+)"`))[1]) >= 5);
  }
});

test('INC-034 C-26: la vista invierte [a] y reconoce [0] singular en ambos métodos', async () => {
  const html = readFileSync(require.resolve('../src/ui/web/index.html'), 'utf8');
  assert.match(html, /id="inv-dim-n" min="1"/);
  const { execFileSync } = require('node:child_process');
  for (const metodo of ['gauss', 'gauss_jordan']) for (const valor of ['2/3', '0']) {
    const { el, contexto: c, renderizados } = pagina();
    el('inv-dim-n').value = '2'; c.cambiarDimInversa(-1);
    assert.equal(Number(el('inv-dim-n').value), 1);
    assert.equal(el('inv-matrix-grid').children.length, 1);
    c.cambiarDimInversa(-1); assert.equal(Number(el('inv-dim-n').value), 1);
    el('inv-a-0-0').value = valor; c.metodo = metodo;
    c.fetch = async (_, opciones) => {
      const data = JSON.parse(execFileSync('python', ['-c', 'import json,sys; from src.ui.web_server import calcular_respuesta; print(json.dumps(calcular_respuesta("/api/matrices/inversa",json.load(sys.stdin))[0]))'], { input: opciones.body, encoding: 'utf8' }));
      assert.equal(data.es_invertible, valor !== '0');
      if (valor !== '0') assert.deepEqual(data.matriz_inversa, [['3/2']]);
      else assert.equal(data.matriz_inversa, null);
      return { ok: true, json: async () => data };
    };
    await c.calcularInversaUI();
    assert.match(el('inv-badge-status').innerText, valor === '0' ? /Singular/ : /Invertible/);
    if (valor !== '0') assert.ok(renderizados.some(t => t.includes('\\frac{3}{2}')));
  }
});

test('INC-034 C-26: Cofactores se desactiva para 7–8, selecciona LU y vuelve para 6', async () => {
  const html = readFileSync(require.resolve('../src/ui/web/index.html'), 'utf8');
  assert.match(html, /value="cofactores"[^>]*aria-describedby="det-cofactores-limite"/);
  assert.match(html, /id="det-cofactores-limite"[^>]*hidden[^>]*>Cofactores[^<]*6/);
  const { el, contexto: c } = pagina();
  const cof = { value: 'cofactores', checked: true }, lu = { value: 'lu', checked: false };
  c.document.querySelector = selector => selector.includes('value="cofactores"') ? cof : selector.includes('value="lu"') ? lu : (lu.checked ? lu : cof);
  for (const n of [6, 7, 8, 6]) {
    el('det-order-n').value = String(n); c.renderizarMatrizDeterminante();
    assert.equal(cof.disabled, n > 6); assert.equal(el('det-cofactores-limite').hidden, n <= 6);
    if (n > 6) {
      assert.equal(lu.checked, true); assert.equal(cof.checked, false);
      c.respuesta = { orden_n: n, es_invertible: true, determinante: '1', determinante_decimal: '1' };
      await c.calcularDeterminanteUI(); assert.equal(c.enviado.datos.metodo, 'lu');
    }
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

test('ejemplos y cálculos de 01–06 invalidan resultado y exportación anteriores', () => {
  const { el, contexto: c } = pagina();
  vm.runInContext('mostrarToast = () => {}; actualizarEficienciaDeterminanteUI = () => {};', c);
  const limpiados = [];
  c.window.ExportarUI = { limpiar: id => limpiados.push(id) };
  c.fetch = () => new Promise(() => {});
  const casos = [
    ['vec', 'vectores', 'cargarEjemploVector', 'calcularOperacionVector'],
    ['comb', 'combinacion', 'cargarEjemploCombinacion', 'evaluarCombinacionLinealUI'],
    ['mat', 'matrices', 'cargarEjemploMatrices', 'operarMatrices'],
    ['inv', 'inversa', 'cargarEjemploInversa', 'calcularInversaUI'],
    ['eq', 'ecuaciones', 'cargarEjemploEcuacion', 'resolverEcuacionMatricialUI'],
    ['det', 'determinante', 'cargarEjemploDeterminante', 'calcularDeterminanteUI']
  ];
  for (const [prefijo, modulo, ejemplo, calcular] of casos) {
    for (const ejecutar of [() => c[ejemplo](1), () => c[calcular]('suma')]) {
      el(`${prefijo}-result-content`).innerHTML = 'ANTERIOR';
      el(`${prefijo}-badge-status`).innerText = 'ANTERIOR';
      limpiados.length = 0;
      ejecutar();
      assert.doesNotMatch(el(`${prefijo}-result-content`).innerHTML, /ANTERIOR/, calcular);
      assert.notEqual(el(`${prefijo}-badge-status`).innerText, 'ANTERIOR');
      assert.ok(limpiados.includes(`tab-${modulo}`));
    }
  }
});

test('la inversa no repite el prefijo Paso en los títulos recibidos', async () => {
  const { contexto: c, renderizados } = pagina();
  c.respuesta = { orden_n: 3, es_invertible: false,
    pasos: [{ step_number: 1, title: 'Paso 1: Inicio', description: '' }] };
  await c.calcularInversaUI();
  assert.ok(renderizados.includes('Paso 1: Inicio'));
  assert.ok(!renderizados.some(t => t.includes('Paso 1: Paso 1:')));
});

test('las celdas 01–06 identifican vector o matriz e índices y los errores se anuncian', () => {
  const { el, contexto: c, renderizados } = pagina();
  c.actualizarEntradasVectores(); c.actualizarEntradasCombinacion();
  c.renderizarMatrizA(); c.renderizarMatrizB(); c.renderizarMatrizInversaInput();
  c.renderizarEcuacionMatricial(); c.renderizarMatrizDeterminante();
  for (const [id, etiqueta] of Object.entries({ 'vec-u-0': 'u[1]', 'vec-v-0': 'v[1]',
    'comb-v-1-0': 'v_2[1]', 'comb-b-0': 'b[1]', 'mat-a-0-1': 'A[1,2]',
    'mat-b-0-1': 'B[1,2]', 'inv-a-0-1': 'A[1,2]', 'eq-a-0-1': 'A[1,2]',
    'eq-b-0': 'b[1]', 'det-a-0-1': 'A[1,2]' })) {
    assert.equal(el(id)['aria-label'], etiqueta, id);
  }
  assert.ok(renderizados.includes('v_{2,1}'));
  assert.ok(!renderizados.includes('c_{1}'));
  c.mostrarErrorResultado(el('eq-result-content'), 'Error', 'Dato incorrecto');
  assert.equal(el('eq-result-content').children[0].role, 'alert');
});

test('combinación muestra independencia, relación concreta y despeje sin nuevos controles', () => {
  const { contexto: c, renderizados } = pagina();
  const relacion = '\\vec{v}_{3} - 2\\vec{v}_{1} - \\vec{v}_{2} = \\vec{0}';
  const despeje = '\\vec{v}_{3} = 2\\vec{v}_{1} + \\vec{v}_{2}';
  c.renderizarResultadoCombinacionUI({ vectores: [[1, 0], [0, 1], [2, 1]], b: [0, 0],
    data: { es_combinacion: true, tipo_solucion: 'INFINITAS', escalares_vector: ['-2t', '-t', 't'],
      independencia: 'dependiente', rango: 2, numero_vectores: 3, relacion: { latex: relacion }, despeje } });
  assert.ok(renderizados.some(t => t.includes('linealmente dependiente') && t.includes('Rango: 2')));
  assert.ok(renderizados.includes(relacion)); assert.ok(renderizados.includes(despeje));
  for (const tex of [relacion, despeje]) assert.doesNotThrow(() => katex.renderToString(tex, { throwOnError: true }));
});

test('VI-57: la interfaz encadena 2A+B reutilizando el resultado exacto como A', async () => {
  const { execFileSync } = require('node:child_process');
  const { el, contexto: c, renderizados } = pagina();
  const ref = JSON.parse(readFileSync(require.resolve('./validacion/referencias_final.json'), 'utf8')).matrices['VI-57']['2A+B'];
  const A = [[1, 0, -2, 3], [4, -1, 2, 0]], B = [[-2, 3, 1, 2], [0, 5, -3, 4]];
  let respuesta;
  c.fetch = async (_, opciones) => {
    respuesta = JSON.parse(execFileSync('python', ['-c', 'import json,sys; from src.ui.web_server import calcular_respuesta; print(json.dumps(calcular_respuesta("/api/matrices/operar",json.load(sys.stdin))[0]))'], { input: opciones.body, encoding: 'utf8' }));
    return { ok: true, json: async () => respuesta };
  };
  const limpiezas = []; c.window.ExportarUI = { limpiar: id => limpiezas.push(id), registrar() {} };
  c.inicializarModuloMatrices(); el('mat-a-m').value = '2'; el('mat-a-n').value = '4'; c.renderizarMatrizA();
  A.forEach((f, i) => f.forEach((v, j) => { el(`mat-a-${i}-${j}`).value = String(v); }));
  el('mat-scalar-k').value = '2'; await c.operarMatrices('escalar_a');
  assert.equal(el('mat-usar-resultado').hidden, false);
  const bAnterior = JSON.stringify(c.obtenerMatrizValores('b', 3, 2));
  c.usarResultadoComoA();
  assert.deepEqual(JSON.parse(JSON.stringify(c.obtenerMatrizValores('a', 2, 4))), A.map(f => f.map(v => String(2 * v))));
  assert.equal(JSON.stringify(c.obtenerMatrizValores('b', 3, 2)), bAnterior);
  assert.equal(el('mat-scalar-k').value, '2'); assert.equal(el('mat-usar-resultado').hidden, true);
  assert.match(el('mat-result-content').innerHTML, /placeholder/); assert.ok(limpiezas.includes('tab-matrices'));
  el('mat-b-r').value = '2'; el('mat-b-r_col').value = '4'; c.renderizarMatrizB();
  B.forEach((f, i) => f.forEach((v, j) => { el(`mat-b-${i}-${j}`).value = String(v); }));
  await c.operarMatrices('suma'); assert.deepEqual(respuesta.matriz_resultado, ref);
  assert.ok(renderizados.some(t => t.endsWith(c.matrixToLatex(ref))));
  el('tab-matrices').querySelector('.card-input').listeners.input[0]({ target: el('mat-a-0-0') });
  assert.equal(el('mat-usar-resultado').hidden, true);
});

test('reutilizar una transpuesta ajusta dimensiones y conserva fracciones sin redondeo', async () => {
  const html = readFileSync(require.resolve('../src/ui/web/index.html'), 'utf8');
  assert.match(html, /<button type="button" class="btn-text" id="mat-usar-resultado"[^>]*aria-label="[^"]+" hidden>/);
  const { el, contexto: c } = pagina(); c.inicializarModuloMatrices();
  el('mat-a-m').value = '2'; el('mat-a-n').value = '1'; c.renderizarMatrizA();
  el('mat-a-0-0').value = '1/3'; el('mat-a-1-0').value = '-5/7';
  c.respuesta = { matriz_resultado: [['1/3', '-5/7']], matriz_formateada: '1/3 -5/7' };
  await c.operarMatrices('transpuesta_a'); c.usarResultadoComoA();
  assert.equal(String(el('mat-a-m').value), '1'); assert.equal(String(el('mat-a-n').value), '2');
  assert.deepEqual(Array.from(c.obtenerMatrizValores('a', 1, 2)[0]), ['1/3', '-5/7']);
  await c.operarMatrices('transpuesta_a');
  el('tab-matrices').querySelector('.card-input').listeners.change[0]({ target: el('mat-scalar-k') });
  assert.equal(el('mat-usar-resultado').hidden, true);
  el('mat-a-0-0').value = '9'; c.usarResultadoComoA(); assert.equal(el('mat-a-0-0').value, '9');
});

test('los cinco conjuntos VII y la base canónica se presentan con sus datos reales de API', () => {
  const { execFileSync } = require('node:child_process');
  const codigo = `import json
from tests.validacion.banco_final import CONJUNTOS
from src.ui.web_server import calcular_respuesta
vs = [*CONJUNTOS.values(), [[1, 0], [0, 1]]]
print(json.dumps([dict(vectores=v, b=[0]*len(v[0]), data=calcular_respuesta('/api/vectores/combinacion', dict(vectores=v,b=[0]*len(v[0])))[0]) for v in vs]))`;
  const casos = JSON.parse(execFileSync('python', ['-c', codigo], { encoding: 'utf8' }));
  for (const caso of casos) {
    const { contexto: c, renderizados } = pagina(); c.renderizarResultadoCombinacionUI(caso);
    assert.ok(renderizados.some(t => t.includes(`linealmente ${caso.data.independencia}`)));
    for (const tex of [caso.data.relacion?.latex, caso.data.despeje].filter(Boolean)) {
      assert.ok(renderizados.includes(tex));
      assert.doesNotThrow(() => katex.renderToString(tex, { throwOnError: true, strict: 'error' }));
    }
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

test('50–54: forma matricial exacta antes de la aumentada en vista y exportación', async () => {
  const { execFileSync } = require('node:child_process');
  const { procedimientoALatex } = require('../src/ui/web/exportar.js');
  const codigo = `import json
from tests.validacion.banco_final import SISTEMAS_RECTANGULARES
from src.ui.web_server import calcular_respuesta
print(json.dumps([dict(**d, data=calcular_respuesta('/api/ecuaciones/resolver',d)[0]) for d in SISTEMAS_RECTANGULARES.values()], default=str))`;
  for (const caso of JSON.parse(execFileSync('python', ['-c', codigo], { encoding: 'utf8' }))) {
    const { el, contexto: c, renderizados } = pagina();
    el('eq-rows-m').value = String(caso.A.length); el('eq-cols-n').value = String(caso.A[0].length);
    c.renderizarEcuacionMatricial();
    caso.A.forEach((fila, i) => fila.forEach((v, j) => { el(`eq-a-${i}-${j}`).value = String(v); }));
    caso.b.forEach((v, i) => { el(`eq-b-${i}`).value = String(v); }); c.respuesta = caso.data;
    await c.resolverEcuacionMatricialUI();
    const formula = caso.data.forma_matricial.latex;
    assert.equal(renderizados.filter(t => t === formula).length, 2);
    const titulo = renderizados.indexOf('Forma matricial $A\\cdot X = B$');
    assert.ok(titulo >= 0);
    assert.ok(renderizados.indexOf(formula, titulo) < renderizados.indexOf(c.augmentedMatrixToLatex(caso.data.pasos[0].matrix, caso.A[0].length)));
    assert.doesNotThrow(() => katex.renderToString(formula, { throwOnError: true, strict: 'error' }));
    const tex = procedimientoALatex(caso.data.procedimiento);
    assert.ok(tex.includes(formula));
    assert.ok(tex.indexOf(formula, tex.indexOf('Procedimiento')) < tex.indexOf(caso.data.procedimiento.pasos[1].titulo));
  }
});

test('60–64: sustitución no trivial, despeje y rango aparecen en verificación y LaTeX', () => {
  const { execFileSync } = require('node:child_process');
  const { procedimientoALatex } = require('../src/ui/web/exportar.js');
  const codigo = `import json
from tests.validacion.banco_final import CONJUNTOS
from src.ui.web_server import calcular_respuesta
vs = [*CONJUNTOS.values(), [['1/2'],['1/3']], [[1,0],[0,1]]]
print(json.dumps([dict(vectores=v, b=[0]*len(v[0]), data=calcular_respuesta('/api/vectores/combinacion',dict(vectores=v,b=[0]*len(v[0])))[0]) for v in vs]))`;
  for (const caso of JSON.parse(execFileSync('python', ['-c', codigo], { encoding: 'utf8' }))) {
    const { el, contexto: c, renderizados } = pagina(); c.renderizarResultadoCombinacionUI(caso);
    const caja = el('comb-result-content').children.find(n => n.className === 'verification-box');
    assert.ok(caso.data.verificacion_independencia.length > 0);
    for (const linea of caso.data.verificacion_independencia) {
      assert.ok(renderizados.includes(linea)); assert.ok(caja.children.some(n => n.innerText === linea));
      for (const m of linea.matchAll(/\$([^$]+)\$/g)) {
        assert.doesNotThrow(() => katex.renderToString(m[1], { throwOnError: true, strict: 'error' }));
      }
    }
    const tex = procedimientoALatex(caso.data.procedimiento);
    assert.ok(tex.includes(caso.data.independencia === 'dependiente' ? 'Despeje, componente' : 'solo existe la solución trivial'));
  }
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
