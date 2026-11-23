/* Verifica cada bloque e inline, también en títulos, detalles y verificaciones. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const katex = require('../src/ui/web/vendor/katex/katex.min.js');

function verificar(procedimientos) {
  let bloques = 0;
  function render(latex) {
    try {
      assert.ok(katex.renderToString(latex, { throwOnError: true, strict: 'error' }).includes('katex'));
    } catch (error) {
      assert.fail(`${latex}: ${error.message}`);
    }
    bloques++;
  }
  function recorrer(valor, clave = '') {
    if (typeof valor === 'string') {
      if (clave === 'latex') render(valor);
      else for (const m of valor.matchAll(/\$\$([\s\S]*?)\$\$|\$([^$]*?)\$/g)) render(m[1] ?? m[2]);
    } else if (Array.isArray(valor)) valor.forEach(v => recorrer(v, clave));
    else if (valor && typeof valor === 'object') Object.entries(valor).forEach(([k, v]) => recorrer(v, k));
  }
  recorrer(procedimientos);
  return { bloques };
}

if (process.argv.includes('--stdin')) {
  process.stdout.write(JSON.stringify(verificar(JSON.parse(fs.readFileSync(0, 'utf8')))));
} else {
  require('node:test').test('Los 24 casos lineales renderizan con KaTeX estricto', () => {
    const py = 'import json; from tests.test_procedimientos_lineal import casos_lineales; '
      + 'from src.procedimientos import ADAPTADORES; '
      + 'print(json.dumps([ADAPTADORES[c["ruta"]](c["respuesta"],c["cuerpo"]) for c in casos_lineales()]))';
    const datos = execFileSync('python', ['-c', py], { cwd: path.resolve(__dirname, '..'), encoding: 'utf8' });
    assert.ok(verificar(JSON.parse(datos)).bloques > 500);
  });
}
