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
  return execFileSync('python', ['-c', py, expr], { cwd: ROOT, encoding: 'utf8', env: { ...process.env, PYTHONIOENCODING: 'utf-8' } });
}

function crearEntorno(mensajeError, responder) {
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
    fetch: async (...args) => responder ? responder(...args) :
      ({ ok: false, status: 400, json: async () => ({ error: mensajeError }) }),
  };
  ctx.globalThis = ctx;
  return {
    timers, doc,
    cargar(archivo) {
      // C-22: cargar la dependencia de vista previa como en index.html, sin iniciar Bisección.
      if (['newton-raphson.js', 'secante.js'].includes(archivo)) {
        vm.runInNewContext(fs.readFileSync(path.join(WEB, 'biseccion.js'), 'utf8'), ctx); ready.pop();
      }
      vm.runInNewContext(fs.readFileSync(path.join(WEB, archivo), 'utf8'), ctx, { filename: archivo }); ready.splice(0).forEach(fn => fn());
    },
  };
}

test('bisección muestra diagnóstico específico en resultado y vista previa', async () => {
  const msg = errorReal('2x + 3 = 7');
  assert.match(msg, /multiplicación entre 2 y x\. Escribe 2\*x \+ 3 = 7\./i);
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

test('INC-033: selectores accesibles con condición real predeterminada', () => {
  const html=fs.readFileSync(path.join(WEB,'index.html'),'utf8');
  for(const id of ['bis-condicion','rf-condicion','nr-condition','sc-condition']){
    const selector=html.match(new RegExp('<select id="'+id+'"[^>]*>(.*?)</select>'));
    assert.ok(selector,id);
    assert.match(html,new RegExp('<label[^>]*for="'+id+'"'));
    assert.match(selector[0],/name="condicion"/);
    assert.deepEqual([...selector[1].matchAll(/value="([^"]+)"/g)].map(m=>m[1]),
      ['real','positiva','positiva_no_nula']);
  }
});

test('INC-033: los cuatro botones envían los datos escritos y muestran la justificación', async () => {
  for(const [archivo,prefijo,funcionId,condicionId] of [
    ['biseccion.js','bis','bis-funcion','bis-condicion'],
    ['regla-falsa.js','rf','rf-funcion','rf-condicion'],
    ['newton-raphson.js','nr','nr-function','nr-condition'],
    ['secante.js','sc','sc-function','sc-condition']]){
    const llamadas=[], respuesta={recomendado:'biseccion',justificacion:'Intervalo validado; no garantiza convergencia.',
      metodos:[{metodo:'biseccion',apto:true,motivos:['Dominio continuo.']}]};
    const env=crearEntorno('',async(url,opciones)=>{
      llamadas.push([url,JSON.parse(opciones.body)]);
      return {ok:true,json:async()=>respuesta};
    });
    env.cargar(archivo);
    env.doc.getElementById(funcionId).value='x^2-5*sin(x)';
    env.doc.getElementById(condicionId).value='positiva_no_nula';
    for(const k of ['a','b','x0','x1','xl','xu'])env.doc.getElementById(prefijo+'-'+k).value='2';
    env.doc.getElementById(prefijo+'-b').value='3';
    if(prefijo==='bis'){
      const f=env.doc.getElementById('bis-form').elements;
      f.funcion.value='x^2-5*sin(x)';f.a.value='2';f.b.value='3';
    }
    const boton=env.doc.getElementById(prefijo+'-recommend');boton.dispatch('click');
    await esperar();
    assert.equal(llamadas[0][0],'/api/raices/recomendar',archivo);
    assert.equal(llamadas[0][1].condicion,'positiva_no_nula',archivo);
    assert.equal(llamadas[0][1].funcion,'x^2-5*sin(x)',archivo);
    const salida=env.doc.getElementById(prefijo+'-recommendation');
    assert.ok(salida.children.some(p=>p.textContent.includes('no garantiza convergencia')),archivo);
    assert.equal(boton.disabled,false,archivo);
  }
});
