/* Pruebas del componente reutilizable exportar-ui.js (estado, teclado, ARIA y acciones). */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const WEB = path.resolve(__dirname, '..', 'src', 'ui', 'web');
const EXPORTAR = require(path.join(WEB, 'exportar.js'));
const MODULOS = ['tab-vectores', 'tab-combinacion', 'tab-matrices', 'tab-inversa', 'tab-ecuaciones',
  'tab-determinante', 'tab-biseccion', 'tab-regla-falsa', 'tab-newton-raphson', 'tab-secante', 'tab-iterativos'];

function crearDOM() {
  let foco = null, impresiones = 0, copiado = null, descarga = null, blobCap = null;
  const listenersDoc = {}, nodosId = new Map();
  function nodo(tag, cls = '') {
    const n = {
      tagName: String(tag).toUpperCase(), className: cls, id: '', style: {}, dataset: {}, attrs: {},
      children: [], parentElement: null, hidden: false, disabled: false, textContent: '', type: '', listeners: {},
      classList: {
        add(...cs) { cs.forEach(c => { if (!n.className.split(/\s+/).includes(c)) n.className = `${n.className} ${c}`.trim(); }); },
        remove(...cs) { n.className = n.className.split(/\s+/).filter(c => c && !cs.includes(c)).join(' '); },
        contains(c) { return n.className.split(/\s+/).includes(c); },
      },
      setAttribute(k, v) { this.attrs[k] = String(v); if (k === 'id') { this.id = String(v); nodosId.set(this.id, this); } },
      getAttribute(k) { return this.attrs[k] ?? null; },
      addEventListener(t, fn) { (this.listeners[t] ||= []).push(fn); },
      dispatchEvent(ev) { ev.target ||= this; ev.currentTarget = this; ev.preventDefault ||= () => {}; (this.listeners[ev.type] || []).forEach(fn => fn(ev)); if (ev.bubbles && this.parentElement) this.parentElement.dispatchEvent(ev); },
      click() { if (!this.disabled) this.dispatchEvent({ type: 'click', bubbles: true }); },
      focus() { foco = this; },
      append(...h) { h.forEach(x => { if (typeof x === 'string') this.textContent += x; else { x.parentElement = this; this.children.push(x); if (x.id) nodosId.set(x.id, x); } }); },
      appendChild(h) { this.append(h); return h; },
      contains(o) { for (let c = o; c; c = c.parentElement) if (c === this) return true; return false; },
      closest(s) { for (let c = this; c; c = c.parentElement) if ((s[0] === '.' && c.classList.contains(s.slice(1))) || (s[0] === '#' && c.id === s.slice(1))) return c; return null; },
      querySelectorAll(sel) {
        const res = [];
        const ok = x => (sel[0] === '.' ? x.classList.contains(sel.slice(1)) : sel === '[role="menuitem"]' ? x.getAttribute('role') === 'menuitem' : sel.includes('notebook-heading') ? x.tagName === 'HEADER' && (x.classList.contains('notebook-heading') || x.classList.contains('bis-notebook-heading')) : sel.startsWith('[data-exp-action="') ? x.dataset.expAction === sel.slice(18, -2) : false);
        (function w(e) { e.children.forEach(c => { if (ok(c)) res.push(c); w(c); }); })(this);
        return res;
      },
      querySelector(sel) { return this.querySelectorAll(sel)[0] || null; },
    };
    return n;
  }
  const head = nodo('head'), body = nodo('body');
  const inicio = nodo('section', 'tab-pane home-pane'); inicio.setAttribute('id', 'tab-inicio');
  inicio.append(nodo('header', 'notebook-heading home-heading')); body.append(inicio);
  MODULOS.forEach((id, i) => {
    const sec = nodo('section', 'tab-pane'); sec.setAttribute('id', id);
    const hdr = nodo('header', i < 6 ? 'notebook-heading' : 'bis-notebook-heading');
    hdr.append(nodo('div'), nodo('span', i < 6 ? 'notebook-chapter' : 'bis-chapter'));
    const cardIn = nodo('div', 'card card-input'); cardIn.append(nodo('input'));
    sec.append(hdr, cardIn); body.append(sec);
  });
  const doc = {
    head, body, get activeElement() { return foco; }, getElementById: id => nodosId.get(id) || null,
    createElement: tag => { const n = nodo(tag); if (tag === 'a') n.click = () => { descarga = { href: n.href, download: n.download }; }; return n; },
    addEventListener(t, fn) { (listenersDoc[t] ||= []).push(fn); },
    dispatchEvent(ev) { (listenersDoc[ev.type] || []).forEach(fn => fn(ev)); },
  };
  const win = {
    ExportarProcedimiento: EXPORTAR, lucide: { createIcons() {} }, print() { impresiones++; },
    navigator: { clipboard: { writeText: async txt => { copiado = txt; } } },
    URL: { createObjectURL: b => { blobCap = b; return 'blob:test'; }, revokeObjectURL() {} },
    Blob: class FakeBlob { constructor(parts, opts) { this.text = parts.join(''); this.type = opts && opts.type; } },
  };
  const ctx = vm.createContext({ window: win, document: doc, navigator: win.navigator, URL: win.URL, Blob: win.Blob, setTimeout: () => 1, clearTimeout() {}, console });
  vm.runInContext(fs.readFileSync(path.join(WEB, 'exportar-ui.js'), 'utf8'), ctx, { filename: 'exportar-ui.js' });
  doc.dispatchEvent({ type: 'DOMContentLoaded' });
  return { doc, win, getFoco: () => foco, getCopiado: () => copiado, getBlob: () => blobCap, getDescarga: () => descarga, getImpresiones: () => impresiones };
}

test('componente exportar-ui: 11 módulos, estado, teclado, ARIA, acciones e invalidación', async () => {
  const { doc, win, getFoco, getCopiado, getBlob, getDescarga, getImpresiones } = crearDOM();
  assert.equal(doc.getElementById('tab-inicio').querySelector('.exp-trigger'), null);
  for (const id of MODULOS) {
    const btn = doc.getElementById(id).querySelector('.exp-trigger');
    assert.ok(btn && btn.classList.contains('btn-clear') && btn.disabled && btn.getAttribute('aria-disabled') === 'true');
    assert.equal(btn.getAttribute('aria-haspopup'), 'menu'); assert.equal(btn.getAttribute('aria-expanded'), 'false');
  }
  const procVec = { version: 1, modulo: 'vectores', titulo: 'Suma', entrada: [], pasos: [], resultado: [{ etiqueta: 'w', latex: '(1,2)' }], verificacion: [], tablas: [], avisos: [] };
  win.ExportarUI.registrar('tab-vectores', { procedimiento: procVec });
  const btnVec = doc.getElementById('tab-vectores').querySelector('.exp-trigger'), menuVec = doc.getElementById('tab-vectores').querySelector('.exp-menu');
  assert.equal(btnVec.disabled, false); assert.equal(menuVec.querySelector('[data-exp-action="csv"]').hidden, true);
  btnVec.dispatchEvent({ type: 'keydown', key: 'Enter' }); assert.equal(menuVec.hidden, false); assert.equal(getFoco().dataset.expAction, 'latex');
  menuVec.dispatchEvent({ type: 'keydown', key: 'ArrowDown' }); assert.equal(getFoco().dataset.expAction, 'imprimir');
  menuVec.dispatchEvent({ type: 'keydown', key: 'Escape' }); assert.equal(menuVec.hidden, true); assert.equal(getFoco(), btnVec);
  const procBis = { version: 1, modulo: 'biseccion', titulo: 'Bisección', entrada: [], pasos: [], resultado: [], verificacion: [], tablas: [{ titulo: 'Iter', columnas: ['i', 'c'], filas: [[1, 0.5]] }], avisos: [] };
  win.ExportarUI.registrar('tab-biseccion', { procedimiento: procBis });
  const secBis = doc.getElementById('tab-biseccion'), csvBtn = secBis.querySelector('[data-exp-action="csv"]');
  assert.equal(csvBtn.hidden, false);
  secBis.querySelector('[data-exp-action="latex"]').click(); await new Promise(r => setImmediate(r));
  assert.ok(getCopiado().includes('\\documentclass') && secBis.querySelector('.exp-status').textContent === 'Copiado');
  csvBtn.click(); assert.ok(getBlob().text.startsWith('\uFEFFi;c\r\n1;0,5') && getDescarga().download.endsWith('.csv'));
  secBis.querySelector('[data-exp-action="imprimir"]').click(); assert.equal(getImpresiones(), 1);
  doc.getElementById('tab-vectores').querySelector('.card-input').dispatchEvent({ type: 'input', bubbles: true }); assert.equal(btnVec.disabled, true);
  win.ExportarUI.limpiar('tab-biseccion'); assert.equal(secBis.querySelector('.exp-trigger').disabled, true);
});
