// Contrato de motivos: cada motivo de src/*/metodo.py tiene texto en su vista JS.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const katex = require('../src/ui/web/vendor/katex/katex.min.js');
const bis = require('../src/ui/web/biseccion.js');
const rf = require('../src/ui/web/regla-falsa.js');
const sc = require('../src/ui/web/secante.js');
const nr = require('../src/ui/web/newton-raphson.js');

const ROOT = path.resolve(__dirname, '..');

function extraerMotivosPython(rutaRelativa, incluirEstado = false) {
  const src = fs.readFileSync(path.join(ROOT, rutaRelativa), 'utf8');
  const motivos = new Set();
  const patrones = [
    /\bmotivo(?:\s*,\s*\w+)?\s*=\s*["']([a-z0-9_]+)["']/g,
    /\bresultado\([^)\n[]*?["']([a-z0-9_]+)["']/g,
  ];
  if (incluirEstado) patrones.push(/\bestado\s*=\s*["']([a-z0-9_]+)["']/g);
  for (const re of patrones) {
    for (const m of src.matchAll(re)) motivos.add(m[1]);
  }
  return [...motivos].sort();
}

const MODULOS = [
  ['biseccion', 'src/biseccion/metodo.py', bis.MOTIVOS, ['raiz_no_admisible', 'no_certificada'], false],
  ['regla_falsa', 'src/regla_falsa/metodo.py', rf.MOTIVOS, ['raiz_no_admisible', 'sin_progreso', 'no_certificada'], false],
  ['secante', 'src/secante/metodo.py', sc.MOTIVOS, ['raiz_no_admisible', 'no_certificada'], false],
  ['newton_raphson', 'src/newton_raphson/metodo.py', nr.MOTIVOS, ['raiz_no_admisible', 'no_certificada'], true],
];

test('todo motivo emitido por src/*/metodo.py tiene texto legible en MOTIVOS de su vista', () => {
  for (const [nombre, rutaPy, motivosJs, requeridos, incluirEstado] of MODULOS) {
    assert.ok(motivosJs && typeof motivosJs === 'object', `${nombre} no exporta MOTIVOS`);
    const enPython = extraerMotivosPython(rutaPy, incluirEstado);
    assert.ok(enPython.length >= 5, `Pocos motivos extraídos en ${rutaPy}: ${enPython}`);
    for (const clave of new Set([...enPython, ...requeridos])) {
      assert.equal(typeof motivosJs[clave], 'string', `Falta MOTIVOS.${clave} en ${nombre}`);
      assert.ok(motivosJs[clave].trim().length > 10, `Texto vacío para MOTIVOS.${clave} en ${nombre}`);
    }
  }
});

test('los textos de MOTIVOS renderizan sin errores en KaTeX y sin $ crudos en secante', () => {
  for (const [nombre, , motivosJs] of MODULOS) {
    for (const [clave, texto] of Object.entries(motivosJs)) {
      if (nombre === 'secante') {
        assert.ok(!texto.includes('$'), `secante usa texto plano, no debe llevar $ en ${clave}`);
        continue;
      }
      for (const m of texto.matchAll(/\$([\s\S]*?)\$/g)) {
        katex.renderToString(m[1], { displayMode: false, throwOnError: true, strict: 'warn' });
      }
    }
  }
});
