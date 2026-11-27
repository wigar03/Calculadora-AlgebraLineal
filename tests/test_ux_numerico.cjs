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
