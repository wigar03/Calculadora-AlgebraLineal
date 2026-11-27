/* INC-035: geometría orientativa, sin recalcular ni alterar resultados exactos. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const R=require('../src/ui/web/grafica-r2.js');
const sistema=(A,b,tipo_sistema,vector_solucion=[])=>R.ecuaciones({A,b,data:{tipo_sistema,vector_solucion}});

test('SCD: las rectas pasan por la intersección exacta (1,2)',()=>{
  const m=sistema([['1','1'],['2','-1']],['3','0'],'SCD',['1','2']);
  assert.deepEqual(m.punto,[1,2]);
  const vista=R.vistaAutomatica(m);
  for(const r of m.rectas){
    const extremos=R.recortarRecta(r,vista);
    assert.equal(extremos.length,2);
    for(const [x,y] of extremos)assert.ok(Math.abs(r.a*x+r.b*y-r.c)<1e-10);
  }
});

test('SI y SCI conservan paralelas y coincidentes, sin inventar una intersección',()=>{
  const A=[['1','2'],['2','4']];
  const si=sistema(A,['3','10'],'SI'), sci=sistema(A,['3','6'],'SCI');
  assert.equal(si.punto,undefined); assert.equal(sci.punto,undefined);
  assert.equal(si.rectas[1].c,10); assert.equal(sci.rectas[1].c,6);
  assert.match(si.descripcion,/sin punto común/); assert.match(sci.descripcion,/coincidentes/);
});

test('verticales, horizontales y ecuaciones degeneradas se distinguen',()=>{
  const m=sistema([['1','0'],['0','1'],['0','0']],['1','2','0'],'SCD',['1','2']);
  const v=R.vistaAutomatica(m);
  assert.ok(R.recortarRecta(m.rectas[0],v).every(p=>p[0]===1));
  assert.ok(R.recortarRecta(m.rectas[1],v).every(p=>p[1]===2));
  assert.deepEqual(R.recortarRecta(m.rectas[2],v),[]);
  assert.match(m.rectas[2].etiqueta,/todo el plano/);
  assert.match(sistema([['0','0']],['1'],'SI').rectas[0].etiqueta,/sin puntos/);
});

test('solo dimensión dos: las otras dimensiones no generan modelo',()=>{
  assert.equal(R.vectores({u:['1','2','3'],v:['1','2','3'],data:{}}),null);
  assert.equal(R.combinacion({vectores:[['1']],b:['2'],data:{}}),null);
  assert.equal(sistema([['1','2','3']],['1'],'SCI'),null);
});
