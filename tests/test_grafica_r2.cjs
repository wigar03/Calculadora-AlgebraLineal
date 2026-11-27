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

test('suma, resta y escalar toman el resultado exacto y construyen su geometría',()=>{
  const calc={u:['1/2','1'],v:['2','-1'],c:'-2',operacion:'suma',data:{resultado_str:'(5/2, 0)'}};
  const suma=R.vectores(calc);
  assert.deepEqual(suma.flechas.at(-1).hasta,[2.5,0]);
  assert.deepEqual(suma.segmentos,[{desde:[.5,1],hasta:[2.5,0]},{desde:[2,-1],hasta:[2.5,0]}]);
  assert.match(suma.flechas.at(-1).detalle,/5\/2/);
  const resta=R.vectores({...calc,operacion:'resta',data:{resultado_str:'(-3/2, 2)'}});
  assert.deepEqual(resta.segmentos,[{desde:[2,-1],hasta:[.5,1]}]);
  const escalar=R.vectores({...calc,operacion:'escalar_u',v:['no usado',''],data:{resultado_str:'(-1, -2)'}});
  assert.deepEqual(escalar.flechas.at(-1).hasta,[-1,-2]);
});

test('producto punto: ángulos de 90°, 180°, 0° y vector nulo',()=>{
  for(const [v,grados] of [[['0','2'],90],[['-2','0'],180],[['2','0'],0]]) {
    const m=R.vectores({u:['1','0'],v,operacion:'producto_punto',data:{}});
    assert.equal(m.angulo.grados,grados);
  }
  const m=R.vectores({u:['0','0'],v:['1','0'],operacion:'producto_punto',data:{}});
  assert.equal(m.angulo,undefined);assert.match(m.descripcion,/no definido/);
});

test('punta-cola: coeficientes racionales, familia paramétrica y relación no trivial',()=>{
  const entrada={vectores:[['2','0'],['0','3']],b:['1','2'],
    data:{es_combinacion:true,tipo_solucion:'UNICA',escalares_vector:['1/2','2/3']}};
  const cadena=R.combinacion(entrada).flechas.filter(f=>f.cadena);
  assert.deepEqual(cadena.map(f=>[f.desde,f.hasta]),[[[0,0],[1,0]],[[1,0],[1,2]]]);
  const dependiente={vectores:[['1','2'],['2','4'],['0','0']],b:['3','6'],
    data:{es_combinacion:true,tipo_solucion:'INFINITAS',escalares_vector:['3 - 2t','t','s']}};
  const m=R.combinacion(dependiente);
  assert.deepEqual(m.flechas.at(-1).hasta,[3,6]);assert.match(m.descripcion,/parámetros libres = 0/);
  const relacion=R.combinacion({...dependiente,b:['0','0'],data:{...dependiente.data,relacion:{coeficientes:['-2','1','0']}}});
  assert.deepEqual(relacion.flechas.at(-1).hasta,[0,0]);
  assert.ok(relacion.flechas.some(f=>f.cadena && f.hasta.some(x=>x!==0)));
});

test('escala con márgenes e iguales unidades en ambos ejes; fracciones grandes',()=>{
  const m=R.vectores({u:['-1/2','-3'],v:['2','1'],operacion:'suma',data:{resultado_str:'(3/2, -2)'}});
  const v=R.vistaAutomatica(m),G=require('../src/ui/web/grafica-funciones.js');
  assert.ok(Math.abs((v.xMax-v.xMin)/G.MARCO.ancho-(v.yMax-v.yMin)/G.MARCO.alto)<1e-12);
  for(const f of m.flechas)for(const [x,y] of [f.desde,f.hasta]) {
    assert.ok(x>v.xMin && x<v.xMax); assert.ok(y>v.yMin && y<v.yMax);
  }
  assert.equal(R.numero('1'+'0'.repeat(400)+'/2'+'0'.repeat(400)),.5);
  assert.equal(R.numero('1'+'0'.repeat(200)+'/1'+'0'.repeat(400)),1e-200);
});
