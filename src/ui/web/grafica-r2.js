/* INC-035: apoyo SVG orientativo; la respuesta conserva toda la aritmética exacta. */
(() => {
  'use strict';
  const G=typeof module!=='undefined' && module.exports ? require('./grafica-funciones.js') : window.GraficaFunciones;
  const COLORES=['var(--accent-blue)','var(--notebook-accent)','var(--accent-emerald)',
    'var(--accent-amber)','var(--accent-cyan)','var(--accent-rose)'];
  const cero=[0,0], sumar=(a,b)=>a.map((v,i)=>v+b[i]);
  const par=v=>Array.isArray(v) && v.length===2;
  const coordenadas=v=>v.map(numero);
  function numero(valor) {
    const s=String(valor).trim().replace(/[−–]/g,'-');
    if(!s.includes('/'))return Number(s);
    const [n,d]=s.split('/');
    const directo=Number(n)/Number(d);
    if(Number.isFinite(directo))return directo;
    // Cocientes de enteros grandes: evita Infinity/Infinity al convertir para el dibujo.
    const parte=t=>{const signo=t.startsWith('-')?-1:1, dig=t.replace(/^[+-]?0*/, '')||'0';
      return [signo*Number(dig.slice(0,15)),Math.max(0,dig.length-15)];};
    const a=parte(n),b=parte(d);
    return a[0]/b[0]*10**(a[1]-b[1]);
  }
  function flecha(desde,hasta,etiqueta,color=0,detalle=etiqueta) {
    return {desde,hasta,etiqueta,color:COLORES[color%COLORES.length],detalle};
  }
  function vectores({u,v,c,operacion,data}) {
    if(!par(u))return null;
    const U=coordenadas(u),V=par(v)?coordenadas(v):null;
    const m={titulo:'Vectores en R²',descripcion:'Flechas desde el origen.',flechas:[
      flecha(cero,U,'u',0,`u = (${u.join(', ')})`)],segmentos:[]};
    if(V?.every(Number.isFinite))m.flechas.push(flecha(cero,V,'v',1,`v = (${v.join(', ')})`));
    if(operacion==='producto_punto') {
      const nu=Math.hypot(...U),nv=V?Math.hypot(...V):0;
      if(nu && nv) {
        const inicio=Math.atan2(U[1],U[0]);
        let giro=Math.atan2(V[1],V[0])-inicio;
        if(giro>Math.PI)giro-=2*Math.PI;
        if(giro< -Math.PI)giro+=2*Math.PI;
        m.angulo={inicio,giro,grados:Math.abs(giro)*180/Math.PI};
        m.descripcion=`Ángulo entre u y v: ${G.formatear(m.angulo.grados,6)}° (aproximado).`;
      } else m.descripcion='Ángulo no definido: uno de los vectores es nulo.';
    } else {
      const exacto=data.resultado_str.replace(/[()]/g,'').split(',').map(s=>s.trim());
      const W=coordenadas(exacto),nombre={suma:'u + v',resta:'u − v',escalar_u:`${c}·u`}[operacion];
      m.flechas.push(flecha(cero,W,nombre,2,`${nombre} = (${exacto.join(', ')})`));
      if(operacion==='suma')m.segmentos=[{desde:U,hasta:W},{desde:V,hasta:W}];
      if(operacion==='resta')m.segmentos=[{desde:V,hasta:U}];
    }
    return m;
  }
  function combinacion({vectores:vs,b,data}) {
    if(!par(b) || !vs.every(par))return null;
    const B=coordenadas(b),relacion=B.every(x=>x===0) && data.relacion;
    const m={titulo:'Combinación lineal en R²',descripcion:'Vectores generadores y vector objetivo b.',
      flechas:vs.map((v,i)=>flecha(cero,coordenadas(v),`v${i+1}`,i,`v${i+1} = (${v.join(', ')})`)),segmentos:[]};
    m.flechas.push(flecha(cero,B,'b',2,`b = (${b.join(', ')})`));
    if(data.es_combinacion) {
      // La API escribe la constante primero; fijar los parámetros libres a 0
      // selecciona una solución de su familia, sin evaluar código ni resolver otra vez.
      const constante=s=>{const t=String(s).trim().split(/\s+/)[0];
        return /^[+-]?\d+(?:\/\d+)?$/.test(t)?t:'0';};
      const cs=relacion?relacion.coeficientes:data.escalares_vector.map(constante);
      let punta=cero;
      vs.forEach((v,i)=>{
        const fin=sumar(punta,coordenadas(v).map(x=>numero(cs[i])*x));
        m.flechas.push({...flecha(punta,fin,`c${i+1}v${i+1}`,i,`c${i+1} = ${cs[i]}; c${i+1}v${i+1}`),cadena:true});
        punta=fin;
      });
      m.descripcion=relacion?'Relación de dependencia: la cadena punta-cola regresa al origen.'
        : data.tipo_solucion==='INFINITAS'?'Una descomposición punta-cola hasta b (parámetros libres = 0).'
        :'Descomposición punta-cola hasta b.';
    } else m.descripcion='b no es combinación lineal de los vectores mostrados.';
    return m;
  }
  function ecuaciones({A,b,data}) {
    if(!A.length || !A.every(par))return null;
    const original=data.pasos?.[0]?.matrix;
    const filas=original || A.map((fila,i)=>[...fila,b[i]]);
    const m={titulo:'Ecuaciones en R²',flechas:[],segmentos:[],
      descripcion:{SCD:'Solución única: punto de intersección común.',
        SCI:'Infinitas soluciones: rectas coincidentes (o todo el plano).',
        SI:'Sistema incompatible: rectas paralelas o sin punto común.'}[data.tipo_sistema],
      rectas:filas.map((f,i)=>{
        const [a,b,c]=coordenadas(f);
        const caso=a===0 && b===0 ? (c===0?' (todo el plano)':' (sin puntos)'):'';
        return {a,b,c,color:COLORES[i%COLORES.length],etiqueta:`E${i+1}: ${f[0]}·x₁ + ${f[1]}·x₂ = ${f[2]}${caso}`};
      })};
    if(data.tipo_sistema==='SCD') {
      m.punto=coordenadas(data.vector_solucion);
      m.puntoExacto=`(${data.vector_solucion.join(', ')})`;
    }
    return m;
  }
  function recortarRecta({a,b,c},v) {
    const escala=Math.max(Math.abs(a),Math.abs(b));
    if(!escala)return [];
    a/=escala;b/=escala;c/=escala;
    const puntos=[];
    const agregar=(x,y)=>{
      const eps=Math.max(v.xMax-v.xMin,v.yMax-v.yMin)*1e-9;
      if(Number.isFinite(x) && Number.isFinite(y) && x>=v.xMin-eps && x<=v.xMax+eps && y>=v.yMin-eps && y<=v.yMax+eps
        && !puntos.some(p=>Math.hypot(p[0]-x,p[1]-y)<=eps))puntos.push([x,y]);
    };
    if(b)for(const x of [v.xMin,v.xMax])agregar(x,(c-a*x)/b);
    if(a)for(const y of [v.yMin,v.yMax])agregar((c-b*y)/a,y);
    return puntos.slice(0,2);
  }
  function vistaAutomatica(m) {
    const puntos=[cero,...m.flechas.flatMap(f=>[f.desde,f.hasta]),...(m.punto?[m.punto]:[])];
    for(const {a,b,c} of m.rectas||[]) {
      if(a || b)puntos.push(Math.abs(a)>=Math.abs(b)?[c/a,0]:[0,c/b]);
    }
    const xs=puntos.map(p=>p[0]),ys=puntos.map(p=>p[1]);
    const x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys);
    const unidad=Math.max((x1-x0)/G.MARCO.ancho,(y1-y0)/G.MARCO.alto) || 2/G.MARCO.alto;
    const dx=unidad*G.MARCO.ancho*.7,dy=unidad*G.MARCO.alto*.7;
    return {xMin:(x0+x1)/2-dx,xMax:(x0+x1)/2+dx,yMin:(y0+y1)/2-dy,yMax:(y0+y1)/2+dy};
  }
  function svgNodo(tag,atributos={},texto) {
    const n=document.createElementNS('http://www.w3.org/2000/svg',tag);
    for(const [k,v] of Object.entries(atributos))n.setAttribute(k,v);
    if(texto!==undefined)n.textContent=texto;
    return n;
  }
  function dibujarEjes(svg,v,e) {
    const {x,y,ancho,alto}=G.MARCO;
    const linea=(a,b,c,d,clase)=>svg.append(svgNodo('line',{x1:a,y1:b,x2:c,y2:d,class:clase}));
    for(const t of G.marcas(v.xMin,v.xMax,5)) {
      linea(e.x(t),y,e.x(t),y+alto,'r2-grid');
      svg.append(svgNodo('text',{x:e.x(t),y:y+alto+20,'text-anchor':'middle',class:'r2-text'},G.formatear(t,4)));
    }
    for(const t of G.marcas(v.yMin,v.yMax,5)) {
      linea(x,e.y(t),x+ancho,e.y(t),'r2-grid');
      svg.append(svgNodo('text',{x:x-8,y:e.y(t)+4,'text-anchor':'end',class:'r2-text'},G.formatear(t,4)));
    }
    linea(x,e.y(0),x+ancho,e.y(0),'r2-axis');
    linea(e.x(0),y,e.x(0),y+alto,'r2-axis');
    svg.append(svgNodo('text',{x:x+ancho,y:y+alto+40,'text-anchor':'end',class:'r2-text'},'x₁'));
    svg.append(svgNodo('text',{x:x-8,y:10,'text-anchor':'end',class:'r2-text'},'x₂'));
  }
  function dibujarFlecha(svg,f,e) {
    const x=e.x(f.desde[0]),y=e.y(f.desde[1]),X=e.x(f.hasta[0]),Y=e.y(f.hasta[1]);
    const dx=X-x,dy=Y-y,largo=Math.hypot(dx,dy),color=f.color;
    svg.append(svgNodo('line',{x1:x,y1:y,x2:X,y2:Y,stroke:color,class:f.cadena?'r2-chain':'r2-vector'}));
    if(largo>1) {
      const ux=dx/largo,uy=dy/largo,t=Math.min(9,largo*.4),ancho=t*.45;
      const puntos=`${X},${Y} ${X-t*ux-ancho*uy},${Y-t*uy+ancho*ux} ${X-t*ux+ancho*uy},${Y-t*uy-ancho*ux}`;
      svg.append(svgNodo('polygon',{points:puntos,fill:color}));
    } else svg.append(svgNodo('circle',{cx:X,cy:Y,r:3,fill:color}));
    const px=f.cadena?(x+X)/2:X,py=f.cadena?(y+Y)/2:Y;
    svg.append(svgNodo('text',{x:px+6,y:py-7,fill:color,class:'r2-label'},f.etiqueta));
  }
  const api={numero,vectores,combinacion,ecuaciones,recortarRecta,vistaAutomatica};
  if(typeof module!=='undefined' && module.exports)module.exports=api;
  if(typeof window!=='undefined')window.GraficaR2=api;
})();
