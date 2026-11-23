/* Verifica que los cuatro métodos muestren los diagnósticos del analizador sin cambiar UX. */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const { execFileSync } = require('node:child_process');
const G = require('../src/ui/web/grafica-funciones.js');

const ROOT = path.resolve(__dirname, '..'), WEB = path.join(ROOT, 'src', 'ui', 'web');
const esperar = () => new Promise(r => setImmediate(r));

function errorReal(expr) {
  const py = 'import sys; from src.biseccion.expresiones import Expresion\ntry: Expresion(sys.argv[1])\nexcept ValueError as e: print(e, end="")';
  return execFileSync('python', ['-c', py, expr], { cwd: ROOT, encoding: 'utf8' });
}

function crearEntorno(mensajeError) {
  const els = new Map(), ready = [], timers = [];
  const crearNodo = (tag = 'div', id = '') => {
    const evs = {};
    const nodo = {
      tagName: tag.toUpperCase(), id, className: '', textContent: '', value: '', hidden: false,
      disabled: false, children: [], dataset: {}, style: {}, attrs: {}, namespaceURI: 'svg',
      classList: { add() {}, remove() {}, toggle() {} },
      addEventListener(t, fn) { (evs[t] ||= []).push(fn); }, removeEventListener() {},
      dispatch(t, ev = {}) { (evs[t] || []).forEach(fn => fn({ preventDefault() {}, currentTarget: nodo, ...ev })); },
      append(...ns) { nodo.children.push(...ns); }, replaceChildren(...ns) { nodo.children = [...ns]; },
      setAttribute(k, v) { nodo.attrs[k] = v; }, getAttribute(k) { return nodo.attrs[k] ?? null; },
      removeAttribute(k) { delete nodo.attrs[k]; },
      querySelector() { return crearNodo('button'); }, querySelectorAll() { return []; },
      reset() {}, focus() {},
      elements: new Proxy({}, { get: (o, k) => (o[k] ||= crearNodo('input', String(k))) }),
    };
    if (id) els.set(id, nodo);
    return nodo;
  };
  const doc = {
    addEventListener(t, fn) { if (t === 'DOMContentLoaded') ready.push(fn); },
    getElementById(id) { return els.get(id) || crearNodo('div', id); },
    querySelector() { return crearNodo('input'); }, querySelectorAll() { return []; },
    createElement(tag) { return crearNodo(tag); }, createElementNS(_, tag) { return crearNodo(tag); },
  };
  const ctx = {
    document: doc, window: { GraficaFunciones: G, katex: true }, GraficaFunciones: G, AbortController,
    FormData: class { constructor() { return [['funcion', '2x']]; } },
    renderLatexElement(el, s) { el.textContent = s; }, renderMixedLatex(el, s) { el.textContent = s; },
    setTimeout(fn) { timers.push(fn); return timers.length; }, clearTimeout() {}, requestAnimationFrame() {},
    fetch: async () => ({ ok: false, status: 400, json: async () => ({ error: mensajeError }) }),
  };
  ctx.globalThis = ctx;
  return {
    timers, doc,
    cargar(archivo) { vm.runInNewContext(fs.readFileSync(path.join(WEB, archivo), 'utf8'), ctx, { filename: archivo }); ready.splice(0).forEach(fn => fn()); },
  };
}

test('bisección muestra diagnóstico específico en resultado y vista previa', async () => {
  const msg = errorReal('2x + 3 = 7');
  assert.match(msg, /multiplicación/i);
  const env = crearEntorno(msg);
  env.cargar('biseccion.js');
  const form = env.doc.getElementById('bis-form');
  form.elements.funcion.value = '2x + 3 = 7';
  form.elements.funcion.dispatch('input');
  await env.timers.at(-1)();
  assert.equal(env.doc.getElementById('bis-preview-status').textContent, msg);
  form.dispatch('submit');
  await esperar();
  assert.equal(env.doc.getElementById('bis-status').textContent, 'Revise los datos');
  assert.equal(env.doc.getElementById('bis-result').children[0].textContent, msg);
});

test('regla falsa muestra diagnóstico específico en alerta del paso 1 y vista previa', async () => {
  const msg = errorReal('sinn(x) - 1');
  const env = crearEntorno(msg);
  env.cargar('regla-falsa.js');
  const form = env.doc.getElementById('rf-form-funcion');
  form.elements.funcion.value = 'sinn(x) - 1';
  form.elements.funcion.dispatch('input');
  await env.timers.at(-1)();
  assert.equal(env.doc.getElementById('rf-preview-status').textContent, msg);
  form.dispatch('submit');
  await esperar();
  const alerta = form.children.find(n => n.attrs.role === 'alert');
  assert.deepEqual([alerta.hidden, alerta.textContent], [false, msg]);
});

test('Newton-Raphson y secante muestran diagnósticos específicos en sus alertas', async () => {
  for (const [archivo, formId, errId, expr] of [['newton-raphson.js', 'nr-function-form', 'nr-error', 'x^^2 - 1'], ['secante.js', 'sc-graph-form', 'sc-error', 'x = 1 = 2']]) {
    const msg = errorReal(expr);
    const env = crearEntorno(msg);
    env.cargar(archivo);
    env.doc.getElementById(formId).dispatch('submit');
    await esperar();
    assert.deepEqual([env.doc.getElementById(errId).hidden, env.doc.getElementById(errId).textContent], [false, msg]);
  }
});
