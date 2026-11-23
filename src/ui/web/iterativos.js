/* Módulo 11: Jacobi y Gauss-Seidel — vista interactiva, KaTeX y gráficas SVG. */
(() => {
  "use strict";
  const G = typeof module !== "undefined" && module.exports
    ? require("./grafica-funciones.js")
    : window.GraficaFunciones;

  const MOTIVOS = {
    tolerancia: "Se alcanzó la tolerancia solicitada cumpliendo el criterio de parada y la verificación del residuo relativo.",
    max_iteraciones: "Se alcanzó el máximo de iteraciones sin cumplir la tolerancia requerida.",
    divergencia: "Las aproximaciones crecen sin acotarse; el método diverge para este sistema.",
    no_finito: "Se obtuvo un valor no finito (infinito o indefinido) durante las iteraciones.",
    estancamiento: "Las aproximaciones dejaron de progresar por precisión numérica antes de cumplir la tolerancia.",
    oscilacion: "Las aproximaciones oscilan o entran en un ciclo sin estabilizarse.",
    diagonal_nula: "Existe al menos un cero en la diagonal principal; reordene ecuaciones antes de iterar.",
    singular: "La matriz A es singular (rango deficiente); el sistema no tiene solución única.",
    incompatible: "El sistema es incompatible (el rango aumentado supera al de A); no tiene solución."
  };

  const GARANTIAS = {
    demostrada: { texto: "Garantía demostrada", clase: "it-badge-ok" },
    observada: { texto: "Convergencia observada", clase: "it-badge-obs" },
    no_asegurada: { texto: "Convergencia no asegurada", clase: "it-badge-warn" }
  };

  const PALETA = ["#426c89", "#8d342e", "#39705a", "#8a6024", "#7a5a9a", "#2f7a78", "#b35c2e", "#5b6d2e", "#4b558a", "#9c4767"];

  function nombreVarLatex(nombre, idx = 0) {
    const raw = typeof nombre === "string" && nombre.trim() ? nombre.trim() : `x_${idx + 1}`;
    if (raw.includes("_")) return raw.replace(/_\{?([0-9a-zA-Z]+)\}?/g, "_{$1}");
    return raw.replace(/^([a-zA-Z]+)(\d+)$/, "$1_{$2}");
  }

  function numeroLatex(valor, cifras = 8) {
    if (valor === null || valor === undefined || valor === "") return String.raw`\text{—}`;
    if (typeof valor === "string") {
      const s = valor.trim();
      const mf = s.match(/^([+-]?)(\d+)\s*\/\s*(\d+)$/);
      if (mf) return `${mf[1] === "-" ? "-" : ""}\\frac{${mf[2]}}{${mf[3]}}`;
      const n = Number(s);
      if (Number.isFinite(n)) return numeroLatex(n, cifras);
      return String.raw`\text{—}`;
    }
    if (typeof valor !== "number" || !Number.isFinite(valor)) return String.raw`\text{no finito}`;
    if (valor === 0) return "0";
    return G.numeroLatex(valor, cifras);
  }

  function vectorLatex(vec, cifras = 8, forzarFila = false) {
    if (!Array.isArray(vec) || !vec.length) return "(0)";
    const items = vec.map(v => numeroLatex(v, cifras));
    if (forzarFila || vec.length > 4) return `\\left(${items.join(",\\; ")}\\right)^T`;
    return `\\begin{pmatrix} ${items.join(" \\\\ ")} \\end{pmatrix}`;
  }

  function formulaMetodoLatex(metodo) {
    if (metodo === "gauss_seidel") {
      return String.raw`x_i^{(k+1)} = \frac{1}{a_{ii}}\left(b_i - \sum_{j < i} a_{ij} x_j^{(k+1)} - \sum_{j > i} a_{ij} x_j^{(k)}\right)`;
    }
    return String.raw`x_i^{(k+1)} = \frac{1}{a_{ii}}\left(b_i - \sum_{j \ne i} a_{ij} x_j^{(k)}\right)`;
  }

  function normasLatex(paso) {
    if (!paso) return "";
    return [
      String.raw`\left\|x^{(${paso.k})}-x^{(${paso.k - 1})}\right\|_\infty = ${numeroLatex(paso.cambio_inf)}`,
      String.raw`\left\|r^{(${paso.k})}\right\|_\infty = ${numeroLatex(paso.residuo_inf)}`,
      String.raw`\text{rel} = ${numeroLatex(paso.residuo_rel)}`
    ].join(String.raw`\qquad `);
  }

  function verificacionLatex(verif, b) {
    if (!verif) return [];
    const out = [];
    if (Array.isArray(verif.Ax)) out.push(`Ax \\approx ${vectorLatex(verif.Ax, 6)}`);
    if (Array.isArray(b)) out.push(`b = ${vectorLatex(b, 6)}`);
    if (Array.isArray(verif.residuo)) out.push(`r = b - Ax \\approx ${vectorLatex(verif.residuo, 6)}`);
    out.push(String.raw`\|r\|_\infty = ${numeroLatex(verif.residuo_inf)}\qquad \frac{\|r\|_\infty}{\|b\|_\infty+\|A\|_\infty\|x\|_\infty} = ${numeroLatex(verif.residuo_rel)}`);
    return out;
  }

  function generarLatexRespuesta(r) {
    const lista = [];
    if (!r) return lista;
    const nombres = Array.isArray(r.nombres) ? r.nombres : Array.from({ length: r.n || 0 }, (_, i) => `x_${i + 1}`);
    lista.push(formulaMetodoLatex(r.metodo));
    nombres.forEach((nb, i) => lista.push(nombreVarLatex(nb, i)));
    if (r.analisis) {
      const a = r.analisis;
      if (a.dominancia && Array.isArray(a.dominancia.filas)) {
        a.dominancia.filas.forEach((f, idx) => {
          const row = (typeof f.i === "number" ? f.i : idx) + 1;
          lista.push(`|a_{${row},${row}}| = ${numeroLatex(f.diagonal)} ${f.cumple ? ">" : "\\le"} ${numeroLatex(f.suma)}`);
        });
      }
      if (a.rango) lista.push(`\\operatorname{rg}(A)=${a.rango.A},\\quad \\operatorname{rg}([A\\mid b])=${a.rango.aumentada}`);
      if (a.radio_espectral) {
        lista.push(`\\rho(T_J) = ${numeroLatex(a.radio_espectral.jacobi, 6)}`);
        lista.push(`\\rho(T_{GS}) = ${numeroLatex(a.radio_espectral.gauss_seidel, 6)}`);
      }
    }
    if (Array.isArray(r.solucion)) lista.push(`x \\approx ${vectorLatex(r.solucion, 8)}`);
    if (r.verificacion) lista.push(...verificacionLatex(r.verificacion, r.b));
    if (Array.isArray(r.iteraciones)) {
      r.iteraciones.forEach(p => {
        lista.push(normasLatex(p));
        if (Array.isArray(p.x)) p.x.forEach(v => lista.push(numeroLatex(v, 6)));
        if (Array.isArray(p.detalle)) {
          p.detalle.forEach((d, idx) => {
            if (d.formula_latex) lista.push(d.formula_latex);
            if (d.sustitucion_latex) lista.push(d.sustitucion_latex);
            const vName = nombreVarLatex(nombres[idx], idx);
            lista.push(`${vName}^{(${p.k})} \\approx ${numeroLatex(d.valor, 8)}`);
          });
        }
      });
    }
    return lista;
  }

  function rangoDatos(series, incluirCero = false) {
    const ys = [];
    let xMin = Infinity, xMax = -Infinity;
    for (const s of series) for (const p of s.puntos) {
      if (!Number.isFinite(p.x) || !Number.isFinite(p.y)) continue;
      xMin = Math.min(xMin, p.x); xMax = Math.max(xMax, p.x); ys.push(p.y);
    }
    if (!ys.length) return null;
    if (xMin === xMax) { xMin = Math.max(0, xMin - 1); xMax += 1; }
    let yMin = Math.min(...ys), yMax = Math.max(...ys);
    if (incluirCero) { yMin = Math.min(yMin, 0); yMax = Math.max(yMax, 0); }
    if (yMin === yMax) { yMin -= 1; yMax += 1; }
    const pad = (yMax - yMin) * 0.08;
    return { xMin, xMax, yMin: yMin - pad, yMax: yMax + pad };
  }

  function construirSerieEvolucion(r) {
    if (!r || !Array.isArray(r.iteraciones) || !r.iteraciones.length) return null;
    const n = r.n || (r.iteraciones[0].x ? r.iteraciones[0].x.length : 0);
    const nombres = Array.isArray(r.nombres) ? r.nombres : Array.from({ length: n }, (_, i) => `x_${i + 1}`);
    const series = Array.from({ length: n }, (_, i) => {
      const puntos = [];
      if (Array.isArray(r.x0) && Number.isFinite(Number(r.x0[i]))) puntos.push({ x: 0, y: Number(r.x0[i]) });
      for (const p of r.iteraciones) puntos.push({ x: p.k, y: Array.isArray(p.x) && Number.isFinite(Number(p.x[i])) ? Number(p.x[i]) : NaN });
      return { etiqueta: nombreVarLatex(nombres[i], i), color: PALETA[i % PALETA.length], puntos };
    });
    const vista = rangoDatos(series, true);
    return vista ? { series, vista } : null;
  }

  function construirSerieConvergencia(entradas, metrica = "residuo", tolerancia = null) {
    const campo = metrica === "cambio" ? "cambio_inf" : "residuo_inf";
    const series = [];
    let omitidosCero = 0;
    for (const item of entradas) {
      if (!item || !item.datos || !Array.isArray(item.datos.iteraciones)) continue;
      const puntos = [];
      for (const p of item.datos.iteraciones) {
        const val = Number(p[campo]);
        if (val === 0) { omitidosCero++; continue; }
        if (Number.isFinite(val) && val > 0) puntos.push({ x: p.k, y: Math.log10(val) });
      }
      if (puntos.length) series.push({ etiqueta: item.etiqueta, color: item.color, puntos, guion: item.guion || "" });
    }
    const vista = rangoDatos(series, false);
    if (!vista) return { series: [], vista: null, omitidosCero };
    const logTol = Number(tolerancia) > 0 ? Math.log10(Number(tolerancia)) : null;
    if (logTol !== null && Number.isFinite(logTol)) {
      vista.yMin = Math.min(vista.yMin, logTol - 0.3);
      vista.yMax = Math.max(vista.yMax, logTol + 0.3);
    }
    return { series, vista, logTol, omitidosCero };
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = {
      MOTIVOS, GARANTIAS, PALETA, nombreVarLatex, numeroLatex, vectorLatex,
      formulaMetodoLatex, normasLatex, verificacionLatex, generarLatexRespuesta,
      construirSerieEvolucion, construirSerieConvergencia
    };
  }
})();
