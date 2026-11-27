const {test}=require('node:test'), assert=require('node:assert/strict');
const fs=require('node:fs'), vm=require('node:vm');
const web='src/ui/web/', html=()=>fs.readFileSync(web+'index.html','utf8');
test('C-22: vistas previas con retardo de 200 ms descartan respuestas obsoletas y errores',async()=>{
  const timers=new Map(), requests=[], input={value:'x',addEventListener(t,f){this[t]=f;}}, preview={replaceChildren(){this.tex='';}}, status={};
  const ctx={module:{exports:{}},AbortController,window:{katex:{}},setTimeout(f,ms){assert.equal(ms,200);timers.set(f,f);return f;},clearTimeout:id=>timers.delete(id),
    renderLatexElement:(n,t)=>n.tex=t,fetch:(url,o)=>new Promise(resolve=>requests.push({url,o,resolve}))};
  vm.runInNewContext(fs.readFileSync(web+'biseccion.js','utf8'),ctx);
  const update=ctx.module.exports.conectarVistaPreviaFuncion(input,preview,status);
  const tick=()=>{const f=[...timers.values()].pop();timers.clear();return f();};
  const old=tick();input.value='x^2';input.input();const fresh=tick();
  requests[1].resolve({ok:true,json:async()=>({latex:'x^{2}'})});await fresh;
  requests[0].resolve({ok:true,json:async()=>({latex:'x'})});await old;
  assert.equal(preview.tex,'f(x) = x^{2}');assert.equal(requests[0].o.signal.aborted,true);
  input.value='(';input.input();const bad=tick();requests[2].resolve({ok:false,json:async()=>({error:'Falta cerrar paréntesis'})});await bad;
  assert.equal(preview.tex,'');assert.match(status.textContent,/paréntesis/);
  input.value='';update();assert.equal(timers.size,0);assert.match(status.textContent,/Escriba/);
});
test('C-22: Newton y Secante tienen bloques accesibles y los cuatro teclados inician plegados',()=>{
  const s=html();for(const p of ['nr','sc']){
    assert.match(s,new RegExp(`id="${p}-preview-math" class="bis-preview-math" aria-live="polite" aria-atomic="true"`));
    const js=fs.readFileSync(web+(p==='nr'?'newton-raphson':'secante')+'.js','utf8');assert.match(js,/conectarVistaPreviaFuncion/);
  }
  for(const p of ['bis','rf','nr','sc'])assert.match(s,new RegExp(`id="${p}-keyboard"[^>]* hidden`));
});
test('C-24: zoom y limpieza reutilizan los mismos iconos y Secante muestra ayuda inicial',()=>{
  const s=html();for(const p of ['bis','rf','nr','sc'])for(const [id,icon] of [['zoom-in','zoom-in'],['zoom-out','zoom-out']]){
    const b=s.match(new RegExp(`<button[^>]*id="${p}-${id}"[^>]*>[\\s\\S]*?</button>`))?.[0];
    assert.ok(b?.includes('btn-bis-zoom')&&b.includes(`data-lucide="${icon}"`),`${p}-${id}`);
  }
  for(const p of ['bis','rf','nr','sc','it'])assert.ok(s.match(new RegExp(`<button[^>]*id="${p}-clear"[^>]*>[\\s\\S]*?</button>`))?.[0].includes('data-lucide="trash-2"'),p);
  assert.ok(/id="sc-plot"[^>]* hidden><\/div><p class="bis-plot-placeholder placeholder-text">/.test(s));
});
function entornoGrafica(archivo){
  const nodes=new Map(), node=()=>({attrs:{},style:{},children:[],handlers:{},classList:{add(){},remove(){},toggle(){}},
    setAttribute(k,v){this.attrs[k]=v;},append(...c){this.children.push(...c);},replaceChildren(...c){this.children=c;},
    addEventListener(t,f){this.handlers[t]=f;},removeEventListener(t){delete this.handlers[t];},getBoundingClientRect:()=>({left:0,top:0,width:600,height:300})});
  const el=id=>{if(!nodes.has(id))nodes.set(id,node());return nodes.get(id);};
  const ctx={module:{exports:{}},document:{createElement:node,createElementNS:node,getElementById:el,addEventListener(){}},
    window:{GraficaFunciones:require('../src/ui/web/grafica-funciones.js')},renderMixedLatex(){},clearTimeout(){},setTimeout(){}};
  vm.runInNewContext(fs.readFileSync(web+archivo,'utf8'),ctx);return {api:ctx.module.exports,el,node};
}
test('C-23: Regla falsa enfoca solo tras resolver, centra la raíz y permite restablecer',()=>{
  const {api,node}=entornoGrafica('regla-falsa.js'), botones={acercar:node(),alejar:node(),restablecer:node(),enfocar:node()}, host=node(), nivel=node();
  const g=api.crearGrafica({contenedor:host,controles:node(),lectura:node(),leyenda:node(),nivelZoom:nivel,botones});
  g.mostrar({funcion:'x-1',intervalo:[0,2],grafica:[{x:0,y:-1},{x:2,y:1}]});assert.equal(botones.enfocar.disabled,true);
  g.fijarResultado({raiz:1,f_raiz:0,intervalo_inicial:[0,2],pasos:[]});assert.equal(botones.enfocar.disabled,false);
  botones.enfocar.handlers.click();assert.ok(parseInt(nivel.textContent)>100);assert.match(host.children[0].attrs['aria-label'],/entre 0\.95 y 1\.05/);
  botones.restablecer.handlers.click();assert.equal(nivel.textContent,'100%');g.fijarResultado(null);assert.equal(botones.enfocar.disabled,true);
});
test('C-23: Bisección lee coordenadas sin arrastre y borra la lectura al salir',()=>{
  const {api,el,node}=entornoGrafica('biseccion.js'), host=node();
  api.dibujarGrafica(host,{funcion:'x-1',intervalo_inicial:[0,2],intervalo_final:[.9,1.1],raiz:1,f_raiz:0,grafica:[{x:0,y:-1},{x:1,y:0},{x:2,y:1}]});
  const svg=host.children[0];svg.handlers.pointermove({clientX:315,clientY:138});assert.equal(el('bis-readout').textContent,'x = 1 · f(x) ≈ 0');
  svg.handlers.pointerleave();assert.equal(el('bis-readout').textContent,'');
});
