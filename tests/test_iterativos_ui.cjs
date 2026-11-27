const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const katex = require('../src/ui/web/vendor/katex/katex.min.js');
const G = require('../src/ui/web/grafica-funciones.js');
const it = require('../src/ui/web/iterativos.js');
const ROOT = path.resolve(__dirname, '..');

function renderEstricto(latex, displayMode = true) {
  const html = katex.renderToString(latex, { displayMode, throwOnError: true, strict: 'warn' });
  assert.ok(html.includes('katex'), `HTML inesperado para: ${latex}`);
  return html;
}

function respuestaSimulada(n, metodo = 'gauss_seidel') {
  const nombres = Array.from({ length: n }, (_, i) => `x_${i + 1}`);
  const x0 = Array(n).fill(0);
  const solucion = Array.from({ length: n }, (_, i) => (i % 2 === 0 ? 1 + i * 0.25 : -(i + 1) / 3));
  const filas = Array.from({ length: n }, (_, i) => ({ i, diagonal: 10 + i, suma: 4 + i * 0.5, cumple: true }));
  const detalle1 = Array.from({ length: n }, (_, i) => ({
    i,
    formula_latex: `x_{${i + 1}}^{(1)} = \\frac{1}{${10 + i}}\\left(${i + 1} - \\sum_{j \\ne ${i + 1}} a_{${i + 1},j} x_j^{(0)}\\right)`,
    sustitucion_latex: `x_{${i + 1}}^{(1)} = \\frac{${i % 2 === 0 ? i + 1 : -(i + 1)}}{${10 + i}} \\approx ${((i + 1) / (10 + i)).toFixed(6)}`,
    valor: (i + 1) / (10 + i),
    usa_nuevos: metodo === 'gauss_seidel' ? Array.from({ length: i }, (_, j) => j) : []
  }));
  return {
    metodo, n, nombres,
    A: Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i === j ? String(10 + i) : '-1/2'))),
    b: Array.from({ length: n }, (_, i) => (i % 2 === 0 ? `${i + 1}/2` : `-${i + 2}`)),
    x0, tolerancia: 1e-6, criterio: 'ambos', max_iteraciones: 100,
    iteraciones: [
      { k: 1, x: detalle1.map(d => d.valor), cambio_inf: 0.95, cambio_rel: null, residuo_inf: 1.5, residuo_rel: 0.12, detalle: detalle1 },
      { k: 2, x: solucion.map(v => v * 0.99), cambio_inf: 1.25e-4, cambio_rel: 8.3e-5, residuo_inf: 3.4e-5, residuo_rel: 2.1e-6 },
      { k: 3, x: solucion, cambio_inf: 2.5e-8, cambio_rel: 1.1e-8, residuo_inf: 0, residuo_rel: 0 }
    ],
    solucion, convergio: true, motivo: 'tolerancia', mensaje: 'Convergió por tolerancia.',
    verificacion: { Ax: Array(n).fill(1), residuo: Array(n).fill(-1.2e-9), residuo_inf: 1.2e-9, residuo_rel: 4.5e-11, cumple: true },
    analisis: {
      diagonal_nula: [], dominancia: { filas, estricta: true },
      reordenamiento: { aplicado: false, permutacion: null, motivo: 'No requerido' },
      rango: { A: n, aumentada: n }, singular: false,
      radio_espectral: { jacobi: 0.4264366108423416, gauss_seidel: 0.0898230583880432, metodo_calculo: 'polinomio característico' },
      garantia: 'demostrada', razones: ['Dominancia diagonal estricta por filas.']
    },
    convergencia: 'demostrada'
  };
}

test('contrato de motivos: todos los motivos del contrato tienen texto legible', () => {
  const contrato = fs.readFileSync(path.join(ROOT, 'docs/contratos/iterativos.md'), 'utf8');
  const esperados = ['tolerancia', 'max_iteraciones', 'divergencia', 'no_finito', 'estancamiento', 'oscilacion', 'diagonal_nula', 'singular', 'incompatible', 'precision_insuficiente'];
  for (const clave of esperados) {
    assert.ok(contrato.includes(`\`${clave}\``), `El contrato no lista ${clave}`);
    assert.equal(typeof it.MOTIVOS[clave], 'string', `Falta MOTIVOS.${clave}`);
    assert.ok(it.MOTIVOS[clave].trim().length > 15, `Texto insuficiente para MOTIVOS.${clave}`);
    assert.ok(!it.MOTIVOS[clave].includes('$'), `MOTIVOS.${clave} usa texto plano sin $ crudos`);
  }
  for (const g of ['demostrada', 'observada', 'no_asegurada']) {
    assert.ok(it.GARANTIAS[g] && it.GARANTIAS[g].texto.length > 5);
  }
});

test('KaTeX estricto renderiza todo el LaTeX generado para n=2, 4 y 10 con negativos, fracciones y notación científica', () => {
  for (const v of [0, -0, -1e-12, 2.5e9, '-3/5', '181/60', '-0.000125', null, Infinity]) {
    renderEstricto(it.numeroLatex(v), false);
  }
  for (const n of [2, 4, 10]) {
    for (const metodo of ['jacobi', 'gauss_seidel']) {
      const r = respuestaSimulada(n, metodo);
      const latexs = it.generarLatexRespuesta(r);
      assert.ok(latexs.length > 10);
      for (const tex of latexs) renderEstricto(tex, true);
      if (n === 10) {
        const html10 = renderEstricto(it.nombreVarLatex('x_10', 9), false);
        assert.ok(html10.includes('<msub><mi>x</mi><mn>10</mn></msub>'));
      }
    }
  }
});

test('series de gráficas de evolución y convergencia log10 reutilizan grafica-funciones y manejan ceros', () => {
  const rJ = respuestaSimulada(4, 'jacobi');
  const rG = respuestaSimulada(4, 'gauss_seidel');
  const evo = it.construirSerieEvolucion(rJ);
  assert.equal(evo.series.length, 4);
  assert.equal(evo.series[0].puntos[0].x, 0);
  const esc = G.crearEscala(evo.vista);
  assert.ok(G.caminoCurva(evo.series[0].puntos, esc).startsWith('M'));

  const conv = it.construirSerieConvergencia([
    { etiqueta: 'Jacobi', datos: rJ, color: '#426c89' },
    { etiqueta: 'Gauss-Seidel', datos: rG, color: '#8d342e' }
  ], 'residuo', 1e-6);
  assert.equal(conv.series.length, 2);
  assert.equal(conv.omitidosCero, 2);
  assert.ok(Number.isFinite(conv.logTol) && Math.abs(conv.logTol + 6) < 1e-12);
  for (const s of conv.series) assert.ok(s.puntos.every(p => Number.isFinite(p.y)));
});

test('gráficas estáticas permiten scroll vertical y trazos con contraste en oscuro', () => {
  const css = fs.readFileSync(path.join(ROOT, 'src/ui/web/iterativos.css'), 'utf8');
  assert.match(css, /#it-plot-vars svg,\s*#it-plot-conv svg\s*\{[^}]*touch-action:\s*pan-y;[^}]*cursor:\s*default;/);
  const oscuro = css.match(/\[data-theme="dark"\] \.iterativos-pane\s*\{([^}]+)\}/)?.[1] || '';
  const luminancia = hex => {
    const canales = hex.match(/\w\w/g).map(x => parseInt(x, 16) / 255)
      .map(c => c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
    return canales.reduce((s, c, i) => s + c * [0.2126, 0.7152, 0.0722][i], 0);
  };
  for (let i = 0; i < it.PALETA.length; i++) {
    assert.match(it.PALETA[i], new RegExp(`^var\\(--it-color-${i}, #[0-9a-f]{6}\\)$`));
    const color = oscuro.match(new RegExp(`--it-color-${i}:\\s*#([0-9a-f]{6})`))?.[1];
    assert.ok(color, `Falta color oscuro ${i}`);
    assert.ok((luminancia(color) + 0.05) / (luminancia('111827') + 0.05) >= 3);
  }
});

const { execFileSync } = require('node:child_process');
const vm = require('node:vm');

// Huella de index.html de la release v1.0.0-rc.2 (sin módulo 11, ?v= normalizados). Cambiarla exige revisar la UX.
const HUELLA_SIN_MODULO_11 = '00c313d8e38776d46c827f91063b9bfe8ab6249024d652139a9b14a82a994f48';

test('Carbon: controles y avisos accesibles, ayuda completa y criterio con residuo', () => {
  const html = fs.readFileSync(path.join(ROOT, 'src/ui/web/index.html'), 'utf8');
  const steppers = [...html.matchAll(/<div class="mini-stepper">([\s\S]*?)<\/div>/g)];
  assert.equal(steppers.length, 4);
  for (const [, bloque] of steppers) {
    for (const [boton] of bloque.matchAll(/<button[^>]*>/g)) assert.match(boton, /aria-label="[^"]+"/);
  }
  assert.match(html, /id="notification-toast"[^>]*role="status"[^>]*aria-live="polite"/);
  for (const [, ayuda] of html.matchAll(/Funciones: sin, cos, tan,([^<]*)/g)) {
    for (const funcion of ['asin', 'acos', 'atan']) assert.ok(ayuda.includes(funcion));
  }
  const criterio = html.match(/name="it-criterion" value="cambio"><span data-math>([^<]+)<\/span>/)?.[1];
  assert.match(criterio, /Cambio relativo/); assert.match(criterio, /residuo relativo/);
});

test('regresión: index.html conserva intactos los módulos de v1.0.0-rc.2 y valida el LaTeX nuevo', () => {
  const actual = fs.readFileSync(path.join(ROOT, 'src/ui/web/index.html'), 'utf8').replace(/\r\n/g, '\n');
  const normalizarV = s => s.replace(/\?v=[0-9a-f]+/g, '?v=HASH');
  const sinModulo11 = actual
    // INC-033: selector de raíz y recomendación autorizados en los cuatro módulos.
    .replace(/^ *<!-- INC-033 -->\n[\s\S]*?^ *<!-- \/INC-033 -->\n/gm, '')
    .replace(/<!-- INC-033 -->[\s\S]*?<!-- \/INC-033 -->/g, '')
    // INC-034 C-26: Inversa 1x1 y aviso junto a Cofactores autorizados.
    .replace('id="inv-dim-n" min="1"', 'id="inv-dim-n" min="2"')
    .replace('value="cofactores" aria-describedby="det-cofactores-limite"', 'value="cofactores"')
    .replace(/^ *<p id="det-cofactores-limite" class="result-explanation" role="status" hidden>Cofactores admite matrices de orden hasta 6\. Para órdenes mayores se selecciona LU\.<\/p>\n/m, '')
    .replace(/\n  <link rel="stylesheet" href="iterativos\.css\?v=[0-9a-f]+">/, '')
    .replace(/\n  <link rel="stylesheet" href="impresion\.css(?:\?v=[0-9a-f]+)?" media="print">/, '')
    .replace(
      '<p class="subtitle" id="header-subtitle">Álgebra lineal y métodos numéricos con procedimientos paso a paso</p>',
      '<p class="subtitle" id="header-subtitle" data-math>Vectores en $\\mathbb{R}^n$, Combinación Lineal, Matrices, Inversa $A^{-1}$, Ecuaciones $Ax=b$, Determinante $|A|$, Bisección, Regla Falsa, Newton-Raphson y Secante</p>'
    )
    // Índice de la portada actualizado a 11 módulos a petición del propietario (2026-11-24).
    .replace('Índice<br><span>01—11</span>', 'Índice<br><span>01—10</span>')
    // C-17/C-21 autorizados: solo nombres accesibles, anuncio del toast y lista de funciones.
    .replace(/ aria-label="(?:Reducir|Aumentar) (?:filas|columnas) de [AB]"(?= onclick="cambiarDimMat[AB]\()/g, '')
    .replace('id="notification-toast" role="status" aria-live="polite"', 'id="notification-toast"')
    .replaceAll('sin, cos, tan, asin, acos, atan, exp, ln (natural)', 'sin, cos, tan, exp, ln (natural)')
    // Botón de encadenamiento de matrices aprobado por el propietario el 2026-11-27.
    .replace(/\n                <button[^>]*id="mat-usar-resultado"[^>]*>Usar resultado como A<\/button>/, '')
    .replace(/\n      <button class="nav-tab" data-tab="tab-iterativos">[\s\S]*?<\/button>/, '')
    .replace(/\n<button class="home-module" type="button" data-open-module="tab-iterativos">[\s\S]*?<\/button>/, '')
    .replace(/\n\n      <section id="tab-iterativos"[\s\S]*?<\/section>/, '')
    .replace(/\n  <script src="iterativos\.js\?v=[0-9a-f]+"><\/script>/, '')
    .replace(/\n  <script src="exportar\.js(?:\?v=[0-9a-f]+)?"><\/script>/, '')
    .replace(/\n  <script src="exportar-ui\.js(?:\?v=[0-9a-f]+)?"><\/script>/, '');
  const huella = require('node:crypto').createHash('sha256').update(normalizarV(sinModulo11)).digest('hex');
  assert.equal(huella, HUELLA_SIN_MODULO_11, 'Se alteró marcado existente fuera del módulo 11 y P2');

  const sec = actual.match(/<section id="tab-iterativos"[\s\S]*?<\/section>/);
  assert.ok(sec, 'Falta la sección #tab-iterativos');
  for (const id of ['it-dim-n', 'it-augmented-grid', 'it-x0-grid', 'it-texto', 'it-tolerance', 'it-max-iter', 'it-reordenar', 'it-plot-vars', 'it-plot-conv']) {
    assert.ok(sec[0].includes(`id="${id}"`), `Falta control #${id}`);
  }
  assert.match(sec[0], /id="it-dim-n"[^>]*min="2"[^>]*max="10"/);
  const bloqueNuevo = sec[0] + actual.match(/data-open-module="tab-iterativos"[\s\S]*?<\/button>/)[0];
  let conteo = 0;
  for (const m of bloqueNuevo.matchAll(/data-math>([\s\S]*?)<\//g)) {
    for (const f of m[1].matchAll(/\$([^$]+)\$/g)) {
      renderEstricto(f[1].replace(/&lt;/g, '<').replace(/&gt;/g, '>'), false);
      conteo++;
    }
  }
  assert.ok(conteo >= 8, `Pocas fórmulas data-math verificadas: ${conteo}`);
});

test('flujo DOM simulado: cargar texto y comparar Jacobi vs Gauss-Seidel renderizan KaTeX y SVGs', async () => {
  const nodos = new Map(), listeners = {};
  const crearNodo = (tag = 'div') => {
    const n = {
      tag, style: {}, children: [], attrs: {}, dataset: {}, value: '', checked: false, hidden: false, disabled: false, textContent: '',
      listeners: {}, className: '',
      setAttribute(k, v) { this.attrs[k] = String(v); },
      addEventListener(t, fn) { (this.listeners[t] ||= []).push(fn); },
      append(...hijos) { hijos.forEach(h => { this.children.push(h); if (h && h.id) nodos.set(h.id, h); }); },
      replaceChildren(...hijos) { this.children = []; this.append(...hijos); },
      querySelector() { return { disabled: false }; }
    };
    return n;
  };
  const el = id => { if (!nodos.has(id)) nodos.set(id, crearNodo()); return nodos.get(id); };
  el('it-tolerance').value = '1e-6'; el('it-max-iter').value = '100'; el('it-texto').value = '4x1 + x2 = 1\n2x1 + 3x2 = 2';
  const envios = [], latexs = [];
  const doc = {
    addEventListener(t, fn) { (listeners[t] ||= []).push(fn); },
    getElementById: el, createElement: crearNodo, createElementNS: (_, tag) => crearNodo(tag),
    querySelector: sel => ({ value: sel.includes('it-method') ? 'comparar' : 'ambos' }),
    querySelectorAll: () => []
  };
  const rJ = respuestaSimulada(2, 'jacobi'), rG = respuestaSimulada(2, 'gauss_seidel');
  rJ.analisis.garantia = 'no_asegurada'; rJ.analisis.razones = ['Sin garantía previa para Jacobi.'];
  rG.analisis.razones = ['Matriz simétrica definida positiva: garantía para Gauss-Seidel.'];
  const ctx = vm.createContext({
    document: doc, window: { GraficaFunciones: G }, console, AbortController,
    renderLatexElement: (n, tex, disp) => { n.textContent = tex; latexs.push([tex, disp]); },
    renderMixedLatex: (n, txt) => { n.textContent = txt; for (const m of txt.matchAll(/\$([^$]+)\$/g)) latexs.push([m[1], false]); },
    fetch: async (url, opts) => {
      envios.push({ url, body: JSON.parse(opts.body) });
      if (url.endsWith('/texto')) return { ok: true, json: async () => ({ A: [['4', '1'], ['2', '3']], b: ['1', '2'], nombres: ['x_1', 'x_2'] }) };
      return { ok: true, json: async () => ({ jacobi: rJ, gauss_seidel: rG, resumen: 'Gauss-Seidel convergió antes.' }) };
    }
  });
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'src/ui/web/iterativos.js'), 'utf8'), ctx);
  listeners.DOMContentLoaded.forEach(fn => fn());
  assert.equal(el('it-dim-n').value, '4');

  el('it-cargar-texto').listeners.click[0]({ currentTarget: el('it-cargar-texto') });
  await new Promise(r => setImmediate(r));
  assert.equal(envios[0].url, '/api/iterativos/texto');
  assert.equal(el('it-dim-n').value, '2');
  assert.equal(el('it-a-0-0').value, '4'); assert.equal(el('it-b-1').value, '2');

  el('it-solve-form').listeners.submit[0]({ preventDefault() {}, currentTarget: el('it-solve-form') });
  await new Promise(r => setImmediate(r));
  assert.equal(envios[1].url, '/api/iterativos/comparar');
  assert.equal(el('it-analysis-card').hidden, false);
  assert.equal(el('it-result-card').hidden, false);
  assert.equal(el('it-charts-card').hidden, false);
  assert.equal(el('it-steps-card').hidden, false);
  assert.equal(el('it-table-card').hidden, false);
  assert.equal(el('it-plot-vars').children[0].tag, 'svg');
  assert.equal(el('it-plot-conv').children[0].tag, 'svg');
  const recorrer = n => [n, ...n.children.flatMap(recorrer)];
  const analisis = recorrer(el('it-analysis')).map(n => n.textContent).join(' ');
  assert.match(analisis, /Jacobi/); assert.match(analisis, /Gauss-Seidel/);
  assert.match(analisis, /Sin garantía previa/); assert.match(analisis, /simétrica definida positiva/);
  const motivos = recorrer(el('it-result')).filter(n => n.tag === 'p'
    && [it.MOTIVOS.tolerancia, rJ.mensaje, rG.mensaje].includes(n.textContent));
  assert.equal(motivos.length, 2, 'Un solo motivo por método, sin su paráfrasis duplicada');
  assert.ok(latexs.length > 30);
  const textosLatex = latexs.map(([tex]) => tex);
  assert.ok(textosLatex.some(t => t.includes('0.4264366108') && t.includes('0.08982305839')));
  assert.ok(textosLatex.some(t => t.includes('-0.6666666667')));
  assert.ok(textosLatex.some(t => t.includes('2.5 \\times 10^{-8}')));
  for (const [tex, disp] of latexs) renderEstricto(tex, Boolean(disp));
});

test('precisión: tabla, radios espectrales y vector solución usan 10 cifras significativas y notación científica', () => {
  assert.equal(it.numeroLatex(1.1430555555555556), '1.143055556');
  assert.equal(it.numeroLatex(0.4264366108423416), '0.4264366108');
  assert.equal(it.numeroLatex(-1.2345678912e-9), '-1.234567891 \\times 10^{-9}');
  const r = respuestaSimulada(2, 'jacobi');
  r.solucion = [1.1430555555555556, -2.34567890123e-8];
  r.iteraciones[0].x = [1.1430555555555556, 0.0898230583880432];
  const latexs = it.generarLatexRespuesta(r);
  assert.ok(latexs.some(t => t.includes('\\rho(T_J) = 0.4264366108')));
  assert.ok(latexs.some(t => t.includes('\\rho(T_{GS}) = 0.08982305839')));
  assert.ok(latexs.some(t => t.includes('1.143055556') && t.includes('-2.345678901 \\times 10^{-8}')));
  assert.ok(latexs.includes('1.143055556'));
  assert.ok(latexs.includes('0.08982305839'));
  for (const tex of latexs) renderEstricto(tex, true);
});
