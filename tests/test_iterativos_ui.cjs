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
      radio_espectral: { jacobi: 0.426437, gauss_seidel: 0.089823, metodo_calculo: 'polinomio característico' },
      garantia: 'demostrada', razones: ['Dominancia diagonal estricta por filas.']
    },
    convergencia: 'demostrada'
  };
}

test('contrato de motivos: todos los motivos del contrato tienen texto legible', () => {
  const contrato = fs.readFileSync(path.join(ROOT, 'docs/contratos/iterativos.md'), 'utf8');
  const esperados = ['tolerancia', 'max_iteraciones', 'divergencia', 'no_finito', 'estancamiento', 'oscilacion', 'diagonal_nula', 'singular', 'incompatible'];
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
