/* Regresiones de notación y presentación detectadas en Carbon. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'), path=require('node:path');
const WEB=path.join(__dirname,'../src/ui/web');
const leer=nombre=>fs.readFileSync(path.join(WEB,nombre),'utf8');
const {ejecutar,buscar}=require('./helpers/carbon_dom.cjs');
const muestra={iteraciones:1,raiz:1,f_raiz:-.1,residuo:.1,error_absoluto:.2,error_relativo:.2,
  motivo:'tolerancia',convergio:true,criterio:'absoluto',cumple:{},cumple_cercana:{},
  tolerancia_usada:{digitada:.01,limite:.011},advertencias:[],
  pasos:[{numero:1,a:0,b:2,c:1,fa:-1,fb:3,fc:-.1,xl:0,xu:2,f_xl:-1,f_xu:3,xr:1,f_xr:-.1,
    n:0,x:1,fx:-.1,dfx:2,error_absoluto:.2,error_relativo:.2,decision:'Finalizar',signo_producto:'−'}]};

test('intervalos y semillas representan el signo menos de PDF igual que el ASCII',()=>{
  for(const modulo of ['regla-falsa','newton-raphson','secante']){
    const {leerNumero}=require(path.join(WEB,modulo+'.js'));
    for(const [s,n] of [['−1.5',-1.5],['–3/2',-1.5],['1/−2',-.5],['−1e−3',-.001]])
      assert.equal(leerNumero(s),n,modulo+': '+s);
    assert.ok(!Number.isFinite(leerNumero('0,5')),modulo);
  }
});

test('impresión conserva Acción y oculta Detalle junto con sus datos',()=>{
  const css=leer('impresion.css'), ocultar=css.slice(css.indexOf('/* Ocultar'),css.indexOf('/* Flujo'));
  const oculto=n=>n.className.split(' ').some(c=>c&&ocultar.includes('.'+c));
  for(const [archivo,fn]of [['regla-falsa.js','renderizarTabla'],['biseccion.js','renderizarTabla'],
                           ['newton-raphson.js','tabla'],['secante.js','result']]){
    const {nodos,contenedor}=ejecutar(archivo,fn,muestra);
    const tablas=[contenedor,...nodos.values()].flatMap(n=>buscar(n,t=>t.tag==='table'));
    const th=buscar(tablas[0],n=>n.tag==='th');
    if(archivo==='regla-falsa.js'){
      const accion=buscar(tablas[0],n=>n.tag==='td'&&n.className.includes('rf-action-cell'))[0];
      assert.equal(oculto(accion),false);
      assert.ok(buscar(accion,n=>n.className==='bis-cell-label'&&n.textContent==='Acción').length);
    }else assert.ok(oculto(th.find(n=>n.textContent==='Detalle')),archivo);
  }
});

test('Regla Falsa muestra diez cifras sin redondear los datos exportados',()=>{
  const x=5.236055081129443, res={...muestra,pasos:[{...muestra.pasos[0],xr:x}]};
  const {nodos}=ejecutar('regla-falsa.js','renderizarTabla',res);
  assert.ok(nodos.get('rf-table').textContent.includes('5.236055081'));
  const csv=require(path.join(WEB,'exportar.js')).tablaACSV({
    titulo:'Regla falsa',columnas:['x_r'],filas:[[x]]});
  assert.ok(csv.includes('5,236055081129443'));
});

test('tablas 07-10 tienen descripción accesible y Secante conserva f(x_n) con signo',()=>{
  for(const [archivo,fn]of [['biseccion.js','renderizarTabla'],['regla-falsa.js','renderizarTabla'],
                           ['newton-raphson.js','tabla'],['secante.js','result']]){
    const {nodos,contenedor}=ejecutar(archivo,fn,{...muestra,funcion_latex:'x^2-2'});
    const raices=[contenedor,...nodos.values()];
    assert.ok(raices.flatMap(n=>buscar(n,t=>t.tag==='caption'&&t.textContent.length>10)).length,archivo);
    if(archivo==='secante.js'){
      assert.ok(nodos.get('result').textContent.includes('f(x)=x^2-2'));
      assert.ok(nodos.get('result').textContent.includes('f(x_n)=-0.1'));
    }
  }
});

test('Newton presenta el aviso de raíz no certificada',()=>{
  const mensaje='El criterio se alcanzó, pero no se pudo certificar la raíz cercana.';
  const res={...muestra,motivo:'no_certificada',convergio:false,
    advertencias:[{tipo:'no_certificada',n:0,mensaje}]};
  const {nodos}=ejecutar('newton-raphson.js','resultado',res);
  assert.ok(nodos.get('result').textContent.includes(mensaje));
});
