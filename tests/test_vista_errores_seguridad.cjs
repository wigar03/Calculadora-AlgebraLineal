/* Verifica que los mensajes de error del servidor nunca se inserten como HTML. */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const WEB = path.resolve(__dirname, '..', 'src', 'ui', 'web');
const PAYLOAD = '<img src=x onerror="alert(1)"><script>xss()</script>&<b>texto</b>';

function crearContextoApp(errorMsg) {
  const nodos = new Map();
  const asignacionesHtml = [];
  const nodo = (tag = 'div') => ({
    tagName: String(tag).toUpperCase(), className: '', style: {}, children: [], value: '1',
    textContent: '', innerText: '', addEventListener() {}, querySelectorAll() { return []; },
    set innerHTML(v) {
      asignacionesHtml.push(String(v));
      this._html = String(v);
      this.children = [];
    },
    get innerHTML() { return this._html || ''; },
    appendChild(h) { this.children.push(h); if (h.id) nodos.set(h.id, h); return h; },
  });
  const el = id => { if (!nodos.has(id)) nodos.set(id, nodo('div')); return nodos.get(id); };
  const ctx = vm.createContext({
    document: {
      addEventListener() {}, createElement: nodo, getElementById: el,
      querySelector: () => ({ value: 'lu' }), querySelectorAll: () => [],
    },
    window: {}, console,
    fetch: async () => ({ ok: false, status: 400, json: async () => ({ error: errorMsg }) }),
  });
  vm.runInContext(fs.readFileSync(path.join(WEB, 'app.js'), 'utf8'), ctx, { filename: 'app.js' });
  return { el, ctx, asignacionesHtml };
}

test('los seis manejadores de error de app.js muestran HTML del servidor como texto plano', async () => {
  const casos = [
    ['calcularOperacionVector', ['suma'], 'vec-result-content', 'Error:'],
    ['evaluarCombinacionLinealUI', [], 'comb-result-content', 'Error:'],
    ['operarMatrices', ['suma'], 'mat-result-content', 'Error Dimensional:'],
    ['calcularInversaUI', [], 'inv-result-content', 'Error en Cálculo:'],
    ['resolverEcuacionMatricialUI', [], 'eq-result-content', 'Error al resolver:'],
    ['calcularDeterminanteUI', [], 'det-result-content', 'Error al calcular:'],
  ];
  for (const [fn, args, boxId, titulo] of casos) {
    const { el, ctx, asignacionesHtml } = crearContextoApp(PAYLOAD);
    await ctx[fn](...args);
    for (const html of asignacionesHtml) {
      assert.ok(!html.includes('<img') && !html.includes('<script') && !html.includes('onerror'),
        `${fn} insertó HTML sin escapar vía innerHTML: ${html}`);
    }
    const box = el(boxId);
    assert.equal(box.children.length, 1, `${fn} debe construir la tarjeta con nodos DOM`);
    const card = box.children[0];
    assert.equal(card.className, 'latex-equation-card');
    assert.equal(card.style.borderColor, 'rgba(225,29,72,0.4)');
    assert.equal(card.children.length, 2);
    const [header, parrafo] = card.children;
    assert.equal(header.className, 'latex-header');
    assert.equal(header.style.color, 'var(--accent-rose)');
    assert.equal(header.textContent, titulo);
    assert.equal(parrafo.tagName, 'P');
    assert.equal(parrafo.textContent, PAYLOAD);
  }
});

test('ningún script propio de la vista interpola mensajes de error en innerHTML', () => {
  const archivos = fs.readdirSync(WEB).filter(f => f.endsWith('.js') && f !== 'lucide.min.js');
  for (const archivo of archivos) {
    const src = fs.readFileSync(path.join(WEB, archivo), 'utf8');
    assert.doesNotMatch(src, /innerHTML\s*=\s*`[^`]*\$\{[^}]*(?:err|error)[^}]*\}[^`]*`/i,
      `Patrón inseguro de innerHTML con error en ${archivo}`);
    if (archivo !== 'app.js') {
      assert.doesNotMatch(src, /\.\s*(?:innerHTML|outerHTML|insertAdjacentHTML)\b/,
        `${archivo} no debe usar innerHTML/outerHTML/insertAdjacentHTML`);
    }
  }
});
