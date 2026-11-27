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
  const api={numero,vectores};
  if(typeof module!=='undefined' && module.exports)module.exports=api;
  if(typeof window!=='undefined')window.GraficaR2=api;
})();
