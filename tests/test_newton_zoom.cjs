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
