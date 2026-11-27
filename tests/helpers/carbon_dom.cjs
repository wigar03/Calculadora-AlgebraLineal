/* Ejecuta renderizadores reales con nodos mínimos; no duplica su lógica. */
const fs=require('node:fs'), path=require('node:path'), vm=require('node:vm');
const WEB=path.join(__dirname,'../../src/ui/web');
function nodo(tag,text='',clase=''){
  return {tag,children:[],attrs:{},dataset:{},className:clase,_text:text??'',hidden:false,
    get textContent(){return this._text+this.children.map(n=>n.textContent??String(n)).join('');},
    set textContent(s){this._text=s;this.children=[];},
    append(...ns){this.children.push(...ns);},
    replaceChildren(...ns){this._text='';this.children=ns;},
    setAttribute(k,v){this.attrs[k]=v;},addEventListener(){},
  };
}
function ejecutar(archivo,nombre,res){
  const src=fs.readFileSync(path.join(WEB,archivo),'utf8').replace(/\r\n/g,'\n');
  const firma=new RegExp('^( *)function '+nombre+'\\(','m').exec(src);
  if(!firma)throw Error('Renderizador ausente: '+nombre);
  const inicio=firma.index, fin=src.indexOf('\n'+firma[1]+'}',inicio)+firma[1].length+2;
  const nodos=new Map(), el=id=>{if(!nodos.has(id))nodos.set(id,nodo('div'));return nodos.get(id);};
  const G=require(path.join(WEB,'grafica-funciones.js'));
  const util=require(path.join(WEB,archivo));
  const math=(s)=>nodo('span',s), mixto=(t,s,c)=>nodo(t,s,c);
  const contexto={crear:nodo,node:nodo,crearMixto:mixto,mixto,mix:s=>nodo('p',s),math,el,
    numeroLatex:G.numeroLatex,formatear:util.formatear,num:G.numeroLatex,G,
    detalleLatex:util.detalleLatex,sustitucion:util.sustitucion,compararErrores:util.compararErrores,
    MOTIVOS:util.MOTIVOS,tabla(){},estado:{base:[-10,10]},renderLatexElement:(n,s)=>{n.textContent=s;}};
  const fn=vm.runInNewContext('('+src.slice(inicio,fin).trim()+')',contexto);
  const contenedor=nodo('div');
  if(nombre==='renderizarTabla'&&archivo==='biseccion.js')fn(contenedor,res);else fn(res);
  return {nodos,contenedor};
}
function buscar(raiz,predicado){return [raiz,...raiz.children.flatMap(n=>buscar(n,predicado))].filter(predicado);}
module.exports={ejecutar,buscar};
