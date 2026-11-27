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
