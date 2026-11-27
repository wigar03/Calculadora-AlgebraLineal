const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const {execFileSync}=require('node:child_process');
const WEB=path.join(__dirname,'../src/ui/web'),R=require(path.join(WEB,'grafica-r2.js'));
function pagina(){
  const nodos=new Map();
  const nodo=tag=>({tag,attrs:{},style:{},children:[],value:'',hidden:false,
    querySelector(){return nodo('div');},
    setAttribute(k,v){this.attrs[k]=String(v);},getAttribute(k){return this.attrs[k];},
    append(...ns){ns.forEach(n=>this.appendChild(n));},prepend(n){this.children.unshift(n);},
    appendChild(n){this.children.push(n);if(n.id)nodos.set(n.id,n);},
    replaceChildren(...ns){this.children=[];this.append(...ns);},
    set innerHTML(s){this.html=s;this.children=[];},get innerHTML(){return this.html||'';}
  });
  const el=id=>{if(!nodos.has(id))nodos.set(id,nodo('div'));return nodos.get(id);};
  const document={getElementById:el,createElement:nodo,createElementNS:(_,t)=>nodo(t),
    addEventListener(){},querySelector:()=>({value:'gauss_jordan'}),querySelectorAll:()=>[]};
  const graficas=vm.createContext({document,window:{GraficaFunciones:require(path.join(WEB,'grafica-funciones.js'))}});
  vm.runInContext(fs.readFileSync(path.join(WEB,'grafica-r2.js'),'utf8'),graficas);
  const contexto=vm.createContext({document,window:{GraficaR2:graficas.window.GraficaR2},console,
    fetch:async()=>({ok:true,json:async()=>contexto.respuesta})});
  vm.runInContext(fs.readFileSync(path.join(WEB,'app.js'),'utf8'),contexto);
  vm.runInContext('mostrarToast=()=>{};',contexto);
  return {el,contexto};
}
const recorrer=n=>[n,...n.children.flatMap(recorrer)];
const cuerpos=[
  ['/api/vectores/operar',{u:['1/2','1'],v:['2','-1'],operacion:'suma'}],
  ['/api/vectores/combinacion',{vectores:[['1','2'],['2','4']],b:['0','0']}],
  ['/api/ecuaciones/resolver',{A:[['1','1'],['2','-1']],b:['3','0']}]
];
function respuestasAPI(){
  const codigo=['import json, sys','from urllib.request import Request, urlopen',
    'from src.ui.web_server import servidor_local','salida=[]','with servidor_local() as url:',
    ' for ruta, cuerpo in json.loads(sys.argv[1]):',
    '  req=Request(url+ruta,json.dumps(cuerpo).encode(),{"Content-Type":"application/json"})',
    '  with urlopen(req) as r: salida.append(json.load(r))','print(json.dumps(salida))'].join('\n');
  return JSON.parse(execFileSync('python',['-c',codigo,JSON.stringify(cuerpos)],{cwd:path.join(__dirname,'..'),encoding:'utf8'}));
}

test('vía real API y vista: SVG accesible, relación y solución, limpieza y cambio de dimensión',async()=>{
  const respuestas=respuestasAPI();
  for(const [i,prefijo] of ['vec','comb','eq'].entries()){
    const {el,contexto:c}=pagina(),[,entrada]=cuerpos[i];c.respuesta=respuestas[i];
    const original=JSON.stringify(c.respuesta),host=el(`${prefijo}-grafica-r2`);
    if(i===0){el('vec-dim').value='2';c.actualizarEntradasVectores();
      for(const p of ['u','v'])entrada[p].forEach((v,j)=>el(`vec-${p}-${j}`).value=v);
      await c.calcularOperacionVector('suma');
    }else if(i===1){el('comb-dim-n').value='2';el('comb-num-k').value='2';c.actualizarEntradasCombinacion();
      entrada.vectores.forEach((v,j)=>v.forEach((x,k)=>el(`comb-v-${j}-${k}`).value=x));
      entrada.b.forEach((v,j)=>el(`comb-b-${j}`).value=v);await c.evaluarCombinacionLinealUI();
    }else{el('eq-rows-m').value='2';el('eq-cols-n').value='2';c.renderizarEcuacionMatricial();
      entrada.A.forEach((f,j)=>f.forEach((v,k)=>el(`eq-a-${j}-${k}`).value=v));
      entrada.b.forEach((v,j)=>el(`eq-b-${j}`).value=v);await c.resolverEcuacionMatricialUI();}
    assert.equal(host.hidden,false);
    const svg=recorrer(host).find(n=>n.tag==='svg');assert.ok(svg);
    assert.equal(svg.attrs.role,'img');assert.ok(svg.children.some(n=>n.tag==='title'));
    assert.ok(svg.children.some(n=>n.tag==='desc'));
    assert.match(svg.attrs['aria-label'],[/1\/2/,/dependencia/,/Intersección: \(1, 2\)/][i]);
    if(i===1){const etiquetas=recorrer(svg).filter(n=>n.tag==='text' && /^c[12]v/.test(n.textContent));
      assert.equal(etiquetas.length,2);assert.notEqual(etiquetas[0].attrs.y,etiquetas[1].attrs.y);}
    assert.equal(JSON.stringify(c.respuesta),original,'Ni API ni CSV se modifican al dibujar');
    const dimension=['vec-dim','comb-dim-n','eq-cols-n'][i];el(dimension).value='3';
    c[['actualizarEntradasVectores','actualizarEntradasCombinacion','renderizarEcuacionMatricial'][i]]();
    assert.equal(host.hidden,true);assert.equal(host.children.length,0);
    c.restablecerResultadoLineal(prefijo,'');assert.equal(host.hidden,true);
    host.hidden=false;host.children.push({tag:'svg',children:[]});
    c[['limpiarModuloVectores','limpiarModuloCombinacion','limpiarModuloEcuaciones'][i]]();
    assert.equal(host.hidden,true);assert.equal(host.children.length,0);
  }
});

test('renderizar null oculta; extremos no representables conservan el resultado exacto',()=>{
  const {el,contexto:c}=pagina(),host=el('grafica'),g=c.window.GraficaR2;
  g.renderizar(host,R.vectores({u:['1e999','1'],v:['0','1'],operacion:'producto_punto',data:{}}));
  assert.ok(recorrer(host).some(n=>n.textContent?.includes('Consulte el resultado exacto')));
  g.renderizar(host,null);assert.equal(host.hidden,true);assert.equal(host.children.length,0);
});

test('recursos con huella, tres anfitriones ocultos e impresión sin ocultar la gráfica',()=>{
  const html=fs.readFileSync(path.join(WEB,'index.html'),'utf8');
  for(const prefijo of ['vec','comb','eq'])
    assert.match(html,new RegExp(`id="${prefijo}-grafica-r2" class="r2-graph" hidden`));
  for(const nombre of ['grafica-r2.js','grafica-r2.css']){
    const hash=require('node:crypto').createHash('sha256')
      .update(fs.readFileSync(path.join(WEB,nombre),'utf8').replace(/\r\n/g,'\n')).digest('hex').slice(0,12);
    assert.ok(html.includes(nombre+'?v='+hash));
  }
  const css=fs.readFileSync(path.join(WEB,'grafica-r2.css'),'utf8');
  assert.match(css,/@media print\s*\{[^}]*break-inside: avoid/);
  const impresion=fs.readFileSync(path.join(WEB,'impresion.css'),'utf8');
  assert.ok(!impresion.slice(impresion.indexOf('/* Ocultar'),impresion.indexOf('/* Flujo')).includes('r2-'));
});
