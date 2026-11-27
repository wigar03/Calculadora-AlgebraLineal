const {test} = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), vm = require('node:vm');
const G = require('../src/ui/web/grafica-funciones.js');
const web = 'src/ui/web/';

function entorno(archivo) {
  const nodes = new Map(), timers = new Map(), requests = [], ready = [];
  function node(tag = 'div') {
    return {tag, attrs: {}, style: {}, children: [], handlers: {}, value: '', textContent: '',
      classList: {add(){}, remove(){}, toggle(){}},
      setAttribute(k,v){this.attrs[k]=String(v);}, removeAttribute(k){delete this.attrs[k];},
      append(...c){this.children.push(...c);}, replaceChildren(...c){this.children=c;},
      addEventListener(t,f){(this.handlers[t] ||= []).push(f);}, removeEventListener(){},
      querySelector(s){return s === 'svg' ? this.children.find(n=>n.tag==='svg') : {disabled:false};},
      getBoundingClientRect:()=>({left:0,top:0,width:600,height:330})};
  }
  const el = id => {if(!nodes.has(id))nodes.set(id,node()); return nodes.get(id);};
  const ctx = {module:{exports:{}}, require:()=>G, AbortController,
    document:{createElement:node,createElementNS:(_,tag)=>node(tag),getElementById:el,
      querySelector:()=>({value:'absoluto'}),querySelectorAll:()=>[],addEventListener:(_,f)=>ready.push(f)},
    window:{GraficaFunciones:G,conectarVistaPreviaFuncion:()=>()=>{}},
    renderMixedLatex(){},renderLatexElement(){},
    setTimeout(f){timers.set(f,f);return f;},clearTimeout:f=>timers.delete(f),
    fetch:(url,o)=>new Promise(resolve=>requests.push({url,o,body:JSON.parse(o.body),resolve}))};
  vm.runInNewContext(fs.readFileSync(web+archivo,'utf8'),ctx);
  const flush = async()=>{for(let i=0;i<12;i++)await Promise.resolve();};
  return {api:ctx.module.exports,el,node,requests,ready,
    async fire(n,t,e={}){for(const f of n.handlers[t]||[])f({preventDefault(){},currentTarget:n,...e});await flush();},
    async tick(){const work=[...timers.values()];timers.clear();work.forEach(f=>f());await flush();},
    async reply(data,index=requests.length-1){requests[index].resolve({ok:true,json:async()=>data});await flush();}};
}
const puntos = (a,b)=>[{x:a,y:a-1},{x:1,y:0},{x:b,y:b-1}];
const datos = {funcion:'x-1',intervalo:[0,2],grafica:puntos(0,2),derivada:'1'};
async function newton() {
  const e=entorno('newton-raphson.js');e.ready.forEach(f=>f());
  await e.fire(e.el('nr-function-form'),'submit');await e.reply(datos);
  return e;
}
function regla() {
  const e=entorno('regla-falsa.js'), botones=Object.fromEntries(['acercar','alejar','restablecer','enfocar'].map(k=>[k,e.node()]));
  e.host=e.node();e.nivel=e.node();e.botones=botones;
  e.g=e.api.crearGrafica({contenedor:e.host,controles:e.node(),lectura:e.node(),leyenda:e.node(),nivelZoom:e.nivel,botones});
  e.g.mostrar(datos);return e;
}
function biseccion() {
  const e=entorno('biseccion.js');e.host=e.node();
  e.api.dibujarGrafica(e.host,{...datos,intervalo_inicial:[0,2],intervalo_final:[.99,1.01],raiz:1,f_raiz:0,cota_error:.01});
  return e;
}
async function resolver(e) {
  await e.fire(e.el('nr-solve-form'),'submit');
  await e.reply({raiz:1,f_raiz:0,x0:1.5,pasos:[],iteraciones:0,cumple:{},cumple_cercana:{},
    tolerancia_usada:{usada:'digitada',digitada:.001,margen:.01,valor_final:0}});
}
const curva = host=>host.children[0].children.find(n=>n.attrs.class==='bis-curve');

test('la preparación de Newton reutiliza el rango vertical y la curva de Regla falsa',async()=>{
  const nr=await newton(),rf=regla();
  assert.equal(curva(nr.el('nr-plot')).attrs.d,curva(rf.host).attrs.d);
  assert.equal(nr.el('nr-focus-root').disabled,true);
  await resolver(nr);assert.equal(nr.el('nr-focus-root').disabled,false);
});

test('INC-035: los tres métodos muestran porcentaje accesible y relativo al ancho inicial',async()=>{
  const html=fs.readFileSync(web+'index.html','utf8');
  for(const p of ['bis','rf','nr'])assert.ok(new RegExp(`<span id="${p}-zoom-level" class="bis-zoom-level" aria-live="polite" title="Nivel de zoom actual">100%</span>`).test(html),p);
  const nr=await newton(),rf=regla(),bis=biseccion();
  for(const [e,boton,nivel,reset] of [[nr,nr.el('nr-zoom-in'),nr.el('nr-zoom-level'),nr.el('nr-reset-view')],
    [rf,rf.botones.acercar,rf.nivel,rf.botones.restablecer],[bis,bis.el('bis-zoom-in'),bis.el('bis-zoom-level'),bis.el('bis-zoom-reset')]]){
    await e.fire(boton,'click');await e.tick();const {a,b}=e.requests.at(-1).body;
    assert.equal(nivel.textContent,`${Math.round(200/(b-a))}%`);
    await e.fire(reset,'click');assert.equal(nivel.textContent,'100%');
  }
});

test('INC-035: enfocar Newton remuestrea y ajusta Y como Regla falsa',async()=>{
  const nr=await newton(),rf=regla();await resolver(nr);
  rf.g.fijarResultado({raiz:1,f_raiz:0,intervalo_inicial:[0,2],pasos:[]});
  for(const [e,boton,host] of [[nr,nr.el('nr-focus-root'),nr.el('nr-plot')],[rf,rf.botones.enfocar,rf.host]]){
    await e.fire(boton,'click');await e.tick();const {a,b}=e.requests.at(-1).body;
    assert.equal(a,.95);assert.equal(b,1.05);const muestras=puntos(a,b);
    await e.reply({grafica:muestras});const [yMin,yMax]=G.rangoVertical(muestras);
    assert.equal(curva(host).attrs.d,G.caminoCurva(muestras,G.crearEscala({xMin:a,xMax:b,yMin,yMax})));
  }
  assert.equal(nr.el('nr-zoom-level').textContent,rf.nivel.textContent);
});

test('INC-035: Newton conserva Inicio y admite 0 y r de Bisección y Regla falsa',async()=>{
  const nr=await newton(),rf=regla(),bis=biseccion();
  for(const [e,host,zoom,nivel,keys] of [[bis,bis.host.children[0],bis.el('bis-zoom-in'),bis.el('bis-zoom-level'),['0','r']],
    [rf,rf.host.children[0],rf.botones.acercar,rf.nivel,['0']],
    [nr,nr.el('nr-plot'),nr.el('nr-zoom-in'),nr.el('nr-zoom-level'),['0','r','R','Home']]]){
    for(const key of keys){await e.fire(zoom,'click');await e.fire(host,'keydown',{key});assert.equal(nivel.textContent,'100%',key);}
  }
});

test('un muestreo de enfoque tardío no altera la vista restablecida',async()=>{
  const nr=await newton();await resolver(nr);
  const inicial=curva(nr.el('nr-plot')).attrs.d;
  await nr.fire(nr.el('nr-focus-root'),'click');await nr.tick();const vieja=nr.requests.length-1;
  await nr.fire(nr.el('nr-reset-view'),'click');assert.equal(nr.requests[vieja].o.signal.aborted,true);
  await nr.reply({grafica:puntos(.95,1.05)},vieja);
  assert.equal(curva(nr.el('nr-plot')).attrs.d,inicial);assert.equal(nr.el('nr-zoom-level').textContent,'100%');
});

test('el porcentaje de Newton sigue la rueda, el teclado y el doble clic',async()=>{
  const nr=await newton(),host=nr.el('nr-plot'),nivel=nr.el('nr-zoom-level');
  await nr.fire(host,'wheel',{clientX:322,clientY:149,deltaY:-1});assert.equal(nivel.textContent,'120%');
  await nr.fire(host,'keydown',{key:'ArrowRight'});assert.equal(nivel.textContent,'120%');
  await nr.fire(host,'keydown',{key:'_'});assert.equal(nivel.textContent,'84%');
  await nr.fire(host,'dblclick');assert.equal(nivel.textContent,'100%');
});
