/* API del motor -> adaptador -> renderizador y exportación reales, sin dependencias. */
const {test}=require('node:test'), assert=require('node:assert/strict');
const {execFileSync}=require('node:child_process'), path=require('node:path');
const {ejecutar,buscar}=require('./helpers/carbon_dom.cjs');
const {procedimientoALatex}=require('../src/ui/web/exportar.js');
const katex=require('../src/ui/web/vendor/katex/katex.min.js');
const py=[
  'import json',
  'from src.procedimientos import adjuntar',
  'from src.biseccion.metodo import resolver_biseccion as b',
  'from src.regla_falsa.metodo import resolver_regla_falsa as r',
  'from src.newton_raphson.metodo import resolver_newton as n',
  'from src.secante.metodo import resolver_secante as s',
  'casos=[("biseccion",b("x^3-4*x-9",2,3)),("regla-falsa",r("x^3-4*x-9",2,3)),',
  '       ("newton-raphson",n("x^3-4*x-9",3)),("secante",s("x^3-4*x-9",2,3))]',
  'print(json.dumps([(m,adjuntar("/api/"+m+"/resolver",res,{})) for m,res in casos]))',
].join('\n');
const casos=JSON.parse(execFileSync('python',['-c',py],{cwd:path.join(__dirname,'..'),encoding:'utf8'}));
for(const [modulo,res] of casos){
  test(modulo+': resultado e impresión conservan una línea de diagnóstico',()=>{
    const fn=modulo==='newton-raphson'?'resultado':modulo==='secante'?'result':'renderizarResultado';
    const {contenedor,nodos}=ejecutar(modulo+'.js',fn,res);
    const raiz=modulo==='biseccion'?contenedor:nodos.get(modulo==='regla-falsa'?'rf-result':'result');
    const lineas=buscar(raiz,n=>n.tag==='p'&&n.textContent===res.convergencia_observada.texto);
    assert.equal(lineas.length,1);
    assert.equal(lineas[0].className,'bis-help');
  });
  test(modulo+': procedimiento y LaTeX exportado incluyen orden, constante y fórmula',()=>{
    const paso=res.procedimiento.pasos.find(p=>p.titulo==='Convergencia observada');
    assert.equal(paso.texto,res.convergencia_observada.texto);
    assert.match(paso.texto,/p ≈ .+C ≈/);
    assert.match(paso.detalles.join(' '),/no demuestra convergencia/);
    for(const tex of paso.latex)katex.renderToString(tex,{throwOnError:true,strict:'error'});
    const latex=procedimientoALatex(res.procedimiento);
    assert.ok(latex.includes('Convergencia observada'));
    assert.ok(latex.includes(paso.latex[1]));
    assert.match(latex,/C/);
  });
}
