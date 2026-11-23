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

  function numeroLatex(valor, cifras = 10) {
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

  function vectorLatex(vec, cifras = 10, forzarFila = false) {
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
      String.raw`\begin{aligned}`,
      String.raw`\left\|x^{(${paso.k})}-x^{(${paso.k - 1})}\right\|_\infty &= ${numeroLatex(paso.cambio_inf)} \\`,
      String.raw`\left\|r^{(${paso.k})}\right\|_\infty &= ${numeroLatex(paso.residuo_inf)} \\`,
      String.raw`r_{\text{rel}} &= ${numeroLatex(paso.residuo_rel)}`,
      String.raw`\end{aligned}`
    ].join(" ");
  }

  function verificacionLatex(verif, b) {
    if (!verif) return [];
    const out = [];
    if (Array.isArray(verif.Ax)) out.push(`Ax \\approx ${vectorLatex(verif.Ax, 10)}`);
    if (Array.isArray(b)) out.push(`b = ${vectorLatex(b, 10)}`);
    if (Array.isArray(verif.residuo)) out.push(`r = b - Ax \\approx ${vectorLatex(verif.residuo, 10)}`);
    out.push(String.raw`\|r\|_\infty = ${numeroLatex(verif.residuo_inf)}`);
    out.push(String.raw`\frac{\|r\|_\infty}{\|b\|_\infty+\|A\|_\infty\|x\|_\infty} = ${numeroLatex(verif.residuo_rel)}`);
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
        lista.push(`\\rho(T_J) = ${numeroLatex(a.radio_espectral.jacobi, 10)}`);
        lista.push(`\\rho(T_{GS}) = ${numeroLatex(a.radio_espectral.gauss_seidel, 10)}`);
      }
    }
    if (Array.isArray(r.solucion)) lista.push(`x \\approx ${vectorLatex(r.solucion, 10)}`);
    if (r.verificacion) lista.push(...verificacionLatex(r.verificacion, r.b));
    if (Array.isArray(r.iteraciones)) {
      r.iteraciones.forEach(p => {
        lista.push(normasLatex(p));
        if (Array.isArray(p.x)) p.x.forEach(v => lista.push(numeroLatex(v, 10)));
        if (Array.isArray(p.detalle)) {
          p.detalle.forEach((d, idx) => {
            if (d.formula_latex) lista.push(d.formula_latex);
            if (d.sustitucion_latex) lista.push(d.sustitucion_latex);
            const vName = nombreVarLatex(nombres[idx], idx);
            lista.push(`${vName}^{(${p.k})} \\approx ${numeroLatex(d.valor, 10)}`);
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

  const EJEMPLOS = {
    principal: { A: [["10", "-1", "2", "0"], ["-1", "11", "-1", "3"], ["2", "-1", "10", "-1"], ["0", "3", "-1", "8"]], b: ["6", "25", "-11", "15"], nota: "Ejemplo principal de la presentación (estrictamente dominante; solución exacta (1, 2, -1, 1))." },
    practica: { A: [["8", "-1", "1", "0"], ["-1", "10", "-2", "1"], ["1", "-2", "9", "-1"], ["0", "1", "-1", "7"]], b: ["8", "7", "-4", "5"], nota: "Sistema de práctica de la presentación (4×4 estrictamente dominante)." },
    reordenable: { A: [["2", "10", "1"], ["10", "1", "1"], ["1", "1", "10"]], b: ["13", "12", "12"], nota: "No dominante en el orden inicial (diverge); active «Reordenar ecuaciones» para permutar filas." },
    jacobi_si_gs_no: { A: [["1", "2", "-2"], ["1", "1", "1"], ["2", "2", "1"]], b: ["1", "3", "5"], nota: "Contraejemplo clásico: Jacobi converge (ρ(T_J)=0) y Gauss-Seidel diverge (ρ(T_GS)=2)." }
  };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = {
      MOTIVOS, GARANTIAS, PALETA, EJEMPLOS, nombreVarLatex, numeroLatex, vectorLatex,
      formulaMetodoLatex, normasLatex, verificacionLatex, generarLatexRespuesta,
      construirSerieEvolucion, construirSerieConvergencia
    };
  }
  if (typeof document === "undefined") return;

  document.addEventListener("DOMContentLoaded", () => {
    const el = id => document.getElementById(`it-${id}`);
    if (!el("dim-n")) return;
    const node = (tag, text, cls) => { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (cls) n.className = cls; return n; };
    const math = (s, display = true) => { const n = node(display ? "div" : "span"); renderLatexElement(n, s, display); return n; };
    const mix = (s, tag = "p") => { const n = node(tag); renderMixedLatex(n, s); return n; };
    let dimN = 4, ultimo = null, metricaConv = "residuo", metodoEvo = "jacobi";
    const requests = new Map();

    function error(msg) { const e = el("error"); e.textContent = msg; e.hidden = !msg; }
    function limpiarResultados() {
      ultimo = null;
      ["analysis-card", "result-card", "charts-card", "steps-card", "table-card"].forEach(id => { el(id).hidden = true; });
      ["analysis", "result", "plot-vars", "plot-conv", "steps", "table"].forEach(id => el(id).replaceChildren());
    }

    function leerSistemaUI() {
      const A = [], b = [], x0 = [];
      for (let i = 0; i < dimN; i++) {
        const fila = [];
        for (let j = 0; j < dimN; j++) fila.push(el(`a-${i}-${j}`)?.value.trim() || "0");
        A.push(fila);
        b.push(el(`b-${i}`)?.value.trim() || "0");
        x0.push(el(`x0-${i}`)?.value.trim() || "0");
      }
      return { A, b, x0 };
    }

    function renderGrid(n, A = null, b = null, x0 = null) {
      const prev = !A ? leerSistemaUI() : null;
      dimN = Math.max(2, Math.min(10, parseInt(n, 10) || 4));
      el("dim-n").value = String(dimN);
      const grid = el("augmented-grid");
      grid.style.gridTemplateColumns = `repeat(${dimN}, auto) 20px auto`;
      grid.replaceChildren();
      for (let j = 0; j < dimN; j++) { const h = node("div", "", "it-col-head"); h.append(math(`x_{${j + 1}}`, false)); grid.append(h); }
      grid.append(node("div", "", "it-sep"));
      const hb = node("div", "", "it-col-head"); hb.append(math("b", false)); grid.append(hb);
      for (let i = 0; i < dimN; i++) {
        for (let j = 0; j < dimN; j++) {
          const inp = node("input", undefined, "bis-input it-cell");
          inp.type = "text"; inp.id = `it-a-${i}-${j}`; inp.setAttribute("aria-label", `A[${i + 1},${j + 1}]`);
          inp.value = A ? String(A[i][j]) : (prev && prev.A[i] && prev.A[i][j] !== undefined ? prev.A[i][j] : (i === j ? "1" : "0"));
          grid.append(inp);
        }
        grid.append(node("div", "│", "it-sep"));
        const ib = node("input", undefined, "bis-input it-cell it-cell-b");
        ib.type = "text"; ib.id = `it-b-${i}`; ib.setAttribute("aria-label", `b[${i + 1}]`);
        ib.value = b ? String(b[i]) : (prev && prev.b[i] !== undefined ? prev.b[i] : "0");
        grid.append(ib);
      }
      const x0Grid = el("x0-grid"); x0Grid.replaceChildren();
      for (let i = 0; i < dimN; i++) {
        const wrap = node("label", "", "it-x0-item"); wrap.append(math(`x_{${i + 1}}^{(0)}`, false));
        const ix = node("input", undefined, "bis-input it-cell");
        ix.type = "text"; ix.id = `it-x0-${i}`; ix.value = x0 ? String(x0[i]) : (prev && prev.x0[i] !== undefined ? prev.x0[i] : "0");
        wrap.append(ix); x0Grid.append(wrap);
      }
    }

    async function request(route, data) {
      requests.get(route)?.abort();
      const ctrl = new AbortController(); requests.set(route, ctrl);
      try {
        const res = await fetch(`/api/iterativos/${route}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data), signal: ctrl.signal });
        const json = await res.json();
        if (requests.get(route) !== ctrl) return null;
        if (!res.ok || json.error) throw Error(json.error || "No se pudo completar el cálculo.");
        return json;
      } finally { if (requests.get(route) === ctrl) requests.delete(route); }
    }

    function renderAnalisis(a, nombres) {
      const box = el("analysis"); box.replaceChildren();
      if (!a) return;
      const g = GARANTIAS[a.garantia] || GARANTIAS.no_asegurada;
      box.append(node("span", g.texto, `it-badge ${g.clase}`));
      if (Array.isArray(a.razones) && a.razones.length) {
        const ul = node("ul", "", "rf-list"); a.razones.forEach(t => ul.append(node("li", t))); box.append(ul);
      }
      if (a.rango) box.append(math(`\\operatorname{rg}(A)=${a.rango.A},\\quad \\operatorname{rg}([A\\mid b])=${a.rango.aumentada}`));
      if (a.singular) box.append(node("p", "La matriz A es singular (rango deficiente).", "bis-help"));
      if (Array.isArray(a.diagonal_nula)) {
        box.append(node("p", a.diagonal_nula.length ? `Diagonal nula en fila(s): ${a.diagonal_nula.map(i => i + 1).join(", ")}.` : "Sin ceros en la diagonal principal.", "bis-help"));
      }
      if (a.reordenamiento) {
        const ro = a.reordenamiento;
        const perm = Array.isArray(ro.permutacion) ? (ro.permutacion.includes(0) ? ro.permutacion.map(i => i + 1) : ro.permutacion).join(", ") : "";
        box.append(node("p", ro.aplicado ? `Reordenamiento aplicado (permutación de filas [${perm}]): ${ro.motivo || ""}` : `Reordenamiento: no aplicado${ro.motivo ? ` (${ro.motivo})` : ""}.`, "bis-help"));
      }
      if (a.radio_espectral) {
        const re = a.radio_espectral;
        box.append(math(`\\rho(T_J) = ${numeroLatex(re.jacobi, 10)}\\qquad \\rho(T_{GS}) = ${numeroLatex(re.gauss_seidel, 10)}`));
        if (re.metodo_calculo) box.append(node("p", `Cálculo espectral: ${re.metodo_calculo}. Criterio necesario y suficiente: ρ(T) < 1.`, "bis-help"));
      }
      if (a.dominancia && Array.isArray(a.dominancia.filas)) {
        box.append(node("p", a.dominancia.estricta ? "Dominancia diagonal estricta por filas: sí (garantía suficiente para ambos métodos)." : "Dominancia diagonal estricta por filas: no (condición suficiente, no necesaria).", "bis-help"));
        const ul = node("ul", "", "it-dom-list");
        a.dominancia.filas.forEach((f, idx) => {
          const row = (typeof f.i === "number" ? f.i : idx) + 1;
          const li = node("li");
          li.append(node("span", f.cumple ? "✓" : "✗"), math(`|a_{${row},${row}}| = ${numeroLatex(f.diagonal)} ${f.cumple ? ">" : "\\le"} \\sum_{j\\ne ${row}} |a_{${row},j}| = ${numeroLatex(f.suma)}`, false));
          ul.append(li);
        });
        box.append(ul);
      }
      el("analysis-card").hidden = false;
    }

    function renderBloqueResultado(r, destino, titulo) {
      if (titulo) destino.append(node("h4", titulo));
      const conv = GARANTIAS[r.convergencia] || GARANTIAS.no_asegurada;
      const head = node("div", "", "it-actions-row");
      head.append(node("span", r.convergio ? "Convergió" : "Sin convergencia", `it-badge ${r.convergio ? "it-badge-ok" : "it-badge-warn"}`), node("span", conv.texto, `it-badge ${conv.clase}`));
      destino.append(head);
      const textoMotivo = MOTIVOS[r.motivo] || r.mensaje || "Proceso finalizado.";
      destino.append(node("p", textoMotivo));
      if (r.mensaje && r.mensaje !== textoMotivo) destino.append(node("p", r.mensaje, "bis-help"));
      const kFin = r.iteraciones && r.iteraciones.length ? r.iteraciones[r.iteraciones.length - 1].k : 0;
      if (Array.isArray(r.solucion)) destino.append(math(`x^{(${kFin})} \\approx ${vectorLatex(r.solucion, 10)}`));
      if (r.iteraciones && r.iteraciones.length) destino.append(math(normasLatex(r.iteraciones[r.iteraciones.length - 1])));
      if (r.verificacion) {
        destino.append(node("p", `Verificación por sustitución (${r.verificacion.cumple ? "cumple tolerancia" : "no cumple tolerancia"}):`, "bis-help"));
        verificacionLatex(r.verificacion, r.b).forEach(l => destino.append(math(l)));
      }
    }

    function renderPasosDetalle(entradas) {
      const box = el("steps"); box.replaceChildren();
      let hay = false;
      entradas.forEach(({ titulo, datos }) => {
        if (!datos || !Array.isArray(datos.iteraciones)) return;
        const conDetalle = datos.iteraciones.filter(p => Array.isArray(p.detalle) && p.detalle.length);
        if (!conDetalle.length) return;
        hay = true;
        const sec = node("div", "", "it-subtable");
        if (entradas.length > 1) sec.append(node("h4", titulo));
        sec.append(math(formulaMetodoLatex(datos.metodo)));
        const nombres = Array.isArray(datos.nombres) ? datos.nombres : Array.from({ length: datos.n || 0 }, (_, i) => `x_${i + 1}`);
        conDetalle.forEach((p, pi) => {
          const det = node("details", "", "it-step-block"); if (pi === 0) det.open = true;
          det.append(node("summary", `Iteración k = ${p.k}`));
          const baseUno = p.detalle[0] && p.detalle[0].i === 1 && !p.detalle.some(d => d.i === 0);
          p.detalle.forEach((d, idx) => {
            const eq = node("div", "", "it-step-eq");
            if (d.formula_latex) eq.append(math(d.formula_latex));
            if (d.sustitucion_latex) eq.append(math(d.sustitucion_latex));
            else eq.append(math(`${nombreVarLatex(nombres[idx], idx)}^{(${p.k})} \\approx ${numeroLatex(d.valor, 10)}`));
            if (Array.isArray(d.usa_nuevos) && d.usa_nuevos.length) {
              const usados = d.usa_nuevos.map(j => `$${nombreVarLatex(nombres[baseUno ? j - 1 : j], baseUno ? j - 1 : j)}^{(${p.k})}$`).join(", ");
              eq.append(mix(`Usa valores recién actualizados: ${usados}.`));
            }
            det.append(eq);
          });
          det.append(math(normasLatex(p)));
          sec.append(det);
        });
        box.append(sec);
      });
      el("steps-card").hidden = !hay;
    }

    function renderTabla(entradas) {
      const box = el("table"); box.replaceChildren();
      let hay = false;
      entradas.forEach(({ titulo, datos }) => {
        if (!datos || !Array.isArray(datos.iteraciones) || !datos.iteraciones.length) return;
        hay = true;
        const sec = node("div", "", "it-subtable");
        if (entradas.length > 1) sec.append(node("h4", titulo));
        const nombres = Array.isArray(datos.nombres) ? datos.nombres : Array.from({ length: datos.n || 0 }, (_, i) => `x_${i + 1}`);
        const headers = ["k", ...nombres.map((nb, i) => `${nombreVarLatex(nb, i)}^{(k)}`), "\\|x^{(k)}-x^{(k-1)}\\|_\\infty", "\\Delta_{\\text{rel}}", "\\|r^{(k)}\\|_\\infty", "r_{\\text{rel}}"];
        const table = node("table"), thead = node("thead"), hr = node("tr"), tbody = node("tbody");
        headers.forEach(h => { const th = node("th"); th.scope = "col"; th.append(math(h, false)); hr.append(th); });
        thead.append(hr);
        datos.iteraciones.forEach(p => {
          const tr = node("tr");
          const vals = [p.k, ...(Array.isArray(p.x) ? p.x : []), p.cambio_inf, p.cambio_rel, p.residuo_inf, p.residuo_rel];
          vals.forEach((v, i) => {
            const td = node("td", "", "bis-cell"); td.title = String(v ?? "No definido");
            const lbl = node("span", "", "bis-cell-label"); lbl.append(math(headers[i], false));
            td.append(lbl, math(i === 0 ? String(v) : numeroLatex(v, 10), false));
            tr.append(td);
          });
          tbody.append(tr);
        });
        table.append(thead, tbody);
        const scroll = node("div", "", "bis-table-scroll it-table-wide");
        scroll.setAttribute("tabindex", "0"); scroll.setAttribute("role", "region");
        scroll.setAttribute("aria-label", `Tabla de iteraciones de ${titulo}`);
        scroll.append(table); sec.append(scroll); box.append(sec);
      });
      el("table-card").hidden = !hay;
    }

    function dibujarSvg(host, legendEl, datos, { etiquetaX, etiquetaY, lineaRef = null, ariaLabel }) {
      host.replaceChildren(); legendEl.replaceChildren();
      if (!datos || !datos.vista || !datos.series.length) {
        host.append(node("p", "No hay puntos finitos positivos suficientes para trazar esta gráfica.", "bis-help"));
        return;
      }
      const M = G.MARCO, v = datos.vista, e = G.crearEscala(v);
      const ns = "http://www.w3.org/2000/svg";
      const svgEl = (tag, attrs = {}, txt) => {
        const n = document.createElementNS(ns, tag);
        Object.entries(attrs).forEach(([k, val]) => n.setAttribute(k, String(val)));
        if (txt !== undefined) n.textContent = txt;
        return n;
      };
      const s = svgEl("svg", { viewBox: "0 0 600 330", role: "img", "aria-label": ariaLabel });
      for (const x of G.marcas(v.xMin, v.xMax, 6)) {
        if (Math.abs(x - Math.round(x)) > 1e-6 && v.xMax - v.xMin >= 2) continue;
        s.append(svgEl("line", { x1: e.x(x), x2: e.x(x), y1: M.y, y2: M.y + M.alto, class: "rf-grid" }),
          svgEl("text", { x: e.x(x), y: 304, "text-anchor": "middle", class: "rf-tick" }, G.formatear(x, 5)));
      }
      for (const y of G.marcas(v.yMin, v.yMax, 5)) {
        s.append(svgEl("line", { x1: M.x, x2: M.x + M.ancho, y1: e.y(y), y2: e.y(y), class: "rf-grid" }),
          svgEl("text", { x: M.x - 6, y: e.y(y) + 3, "text-anchor": "end", class: "rf-tick" }, G.formatear(y, 4)));
      }
      if (v.yMin < 0 && v.yMax > 0) s.append(svgEl("line", { x1: M.x, x2: M.x + M.ancho, y1: e.y(0), y2: e.y(0), class: "bis-axis-zero" }));
      if (lineaRef !== null && Number.isFinite(lineaRef) && lineaRef >= v.yMin && lineaRef <= v.yMax) {
        s.append(svgEl("line", { x1: M.x, x2: M.x + M.ancho, y1: e.y(lineaRef), y2: e.y(lineaRef), stroke: "var(--accent-emerald)", "stroke-dasharray": "5 4", "stroke-width": 1.3 }));
      }
      datos.series.forEach(ser => {
        const d = G.caminoCurva(ser.puntos, e);
        if (d) s.append(svgEl("path", { d, fill: "none", stroke: ser.color, "stroke-width": 2, ...(ser.guion ? { "stroke-dasharray": ser.guion } : {}) }));
        if (ser.puntos.length <= 26) {
          ser.puntos.forEach(p => { if (Number.isFinite(p.y)) s.append(svgEl("circle", { cx: e.x(p.x), cy: e.y(p.y), r: 3, fill: ser.color })); });
        }
        const li = node("li"); const sw = node("span", "", "it-swatch"); sw.style.background = ser.color;
        li.append(sw, ser.esTexto ? node("span", ser.etiqueta) : math(ser.etiqueta, false));
        legendEl.append(li);
      });
      s.append(svgEl("text", { x: M.x + M.ancho, y: 324, "text-anchor": "end", class: "rf-tick" }, etiquetaX));
      s.append(svgEl("text", { x: M.x, y: 11, "text-anchor": "start", class: "rf-tick" }, etiquetaY));
      host.append(s);
    }

    function renderGraficas() {
      if (!ultimo) return;
      const entradas = ultimo.comparacion
        ? [{ etiqueta: "Jacobi", datos: ultimo.jacobi, color: "#426c89", esTexto: true }, { etiqueta: "Gauss-Seidel", datos: ultimo.gauss_seidel, color: "#8d342e", guion: "6 3", esTexto: true }]
        : [{ etiqueta: ultimo.datos.metodo === "gauss_seidel" ? "Gauss-Seidel" : "Jacobi", datos: ultimo.datos, color: "#426c89", esTexto: true }];
      const hayIter = entradas.some(x => x.datos && Array.isArray(x.datos.iteraciones) && x.datos.iteraciones.length);
      el("charts-card").hidden = !hayIter;
      if (!hayIter) return;
      el("evo-method").hidden = !ultimo.comparacion;
      const fuenteEvo = ultimo.comparacion ? (metodoEvo === "gauss_seidel" ? ultimo.gauss_seidel : ultimo.jacobi) : ultimo.datos;
      dibujarSvg(el("plot-vars"), el("legend-vars"), construirSerieEvolucion(fuenteEvo), {
        etiquetaX: "Iteración k", etiquetaY: "x_i^(k)", ariaLabel: "Evolución de las incógnitas por iteración"
      });
      const tol = Number(el("tolerance").value);
      const conv = construirSerieConvergencia(entradas, metricaConv, Number.isFinite(tol) ? tol : null);
      conv.series.forEach(s => { s.esTexto = true; });
      dibujarSvg(el("plot-conv"), el("legend-conv"), conv, {
        etiquetaX: "Iteración k", etiquetaY: metricaConv === "cambio" ? "log10(||Δx||∞)" : "log10(||r||∞)",
        lineaRef: conv.logTol, ariaLabel: "Comparación de convergencia en escala logarítmica"
      });
      el("conv-note").textContent = conv.omitidosCero ? `Se omitieron ${conv.omitidosCero} punto(s) con valor exacto 0 (log10 indefinido).` : "";
    }

    function mostrarResultado(payload, esComparacion) {
      el("result").replaceChildren();
      if (esComparacion) {
        ultimo = { comparacion: true, jacobi: payload.jacobi, gauss_seidel: payload.gauss_seidel };
        const base = payload.jacobi || payload.gauss_seidel;
        renderAnalisis(base && base.analisis, base && base.nombres);
        const grid = node("div", "", "it-compare-grid");
        const colJ = node("div", "", "it-compare-col"), colG = node("div", "", "it-compare-col");
        if (payload.jacobi) renderBloqueResultado(payload.jacobi, colJ, "Jacobi");
        if (payload.gauss_seidel) renderBloqueResultado(payload.gauss_seidel, colG, "Gauss-Seidel");
        grid.append(colJ, colG); el("result").append(grid);
        if (payload.resumen) {
          const txt = typeof payload.resumen === "string" ? payload.resumen : (payload.resumen.mensaje || payload.resumen.texto || JSON.stringify(payload.resumen));
          el("result").append(node("p", txt, "bis-help"));
        }
        el("result-card").hidden = false;
        const pares = [{ titulo: "Jacobi", datos: payload.jacobi }, { titulo: "Gauss-Seidel", datos: payload.gauss_seidel }];
        renderPasosDetalle(pares); renderTabla(pares); renderGraficas();
      } else {
        ultimo = { comparacion: false, datos: payload };
        renderAnalisis(payload.analisis, payload.nombres);
        renderBloqueResultado(payload, el("result"), payload.metodo === "gauss_seidel" ? "Gauss-Seidel" : "Jacobi");
        el("result-card").hidden = false;
        const uno = [{ titulo: payload.metodo === "gauss_seidel" ? "Gauss-Seidel" : "Jacobi", datos: payload }];
        renderPasosDetalle(uno); renderTabla(uno); renderGraficas();
      }
    }

    async function ejecutar(btn, fn) {
      if (btn) btn.disabled = true;
      error("");
      try { await fn(); } catch (e) { if (e.name !== "AbortError") error(e.message); }
      finally { if (btn) btn.disabled = false; }
    }

    const cuerpoBase = () => ({
      ...leerSistemaUI(), tolerancia: el("tolerance").value.trim(), max_iteraciones: el("max-iter").value,
      criterio: document.querySelector('[name="it-criterion"]:checked').value, reordenar: el("reordenar").checked
    });

    el("solve-form").addEventListener("submit", ev => {
      ev.preventDefault(); limpiarResultados();
      const metodo = document.querySelector('[name="it-method"]:checked').value;
      ejecutar(ev.currentTarget.querySelector('[type="submit"]'), async () => {
        const d = metodo === "comparar" ? await request("comparar", cuerpoBase()) : await request("resolver", { ...cuerpoBase(), metodo });
        if (d) mostrarResultado(d, metodo === "comparar");
      });
    });

    el("analizar").addEventListener("click", ev => {
      limpiarResultados();
      ejecutar(ev.currentTarget, async () => { const d = await request("analizar", cuerpoBase()); if (d) renderAnalisis(d.analisis || d, d.nombres); });
    });

    el("cargar-texto").addEventListener("click", ev => {
      el("texto-status").textContent = "";
      ejecutar(ev.currentTarget, async () => {
        const d = await request("texto", { texto: el("texto").value }); if (!d) return;
        const n = Array.isArray(d.A) ? d.A.length : 0;
        if (n < 2 || n > 10) throw Error(`El sistema tiene dimensión ${n}; la interfaz admite entre 2 y 10 ecuaciones.`);
        renderGrid(n, d.A, d.b, Array(n).fill("0"));
        el("texto-status").textContent = `Sistema ${n}×${n} cargado en la rejilla. Revise los coeficientes antes de iterar.`;
      });
    });

    el("conv-metric").addEventListener("change", ev => { metricaConv = ev.target.value; renderGraficas(); });
    el("evo-method").addEventListener("change", ev => { metodoEvo = ev.target.value; renderGraficas(); });
    document.querySelectorAll("[data-it-example]").forEach(btn => btn.addEventListener("click", () => {
      const ej = EJEMPLOS[btn.dataset.itExample]; if (!ej) return;
      error(""); limpiarResultados(); renderGrid(ej.A.length, ej.A, ej.b, Array(ej.A.length).fill("0")); el("hint").textContent = ej.nota;
    }));
    el("clear").addEventListener("click", () => {
      error(""); limpiarResultados(); el("texto").value = ""; el("texto-status").textContent = ""; el("hint").textContent = "";
      renderGrid(dimN, Array.from({ length: dimN }, () => Array(dimN).fill("0")), Array(dimN).fill("0"), Array(dimN).fill("0"));
    });

    el("dim-dec").addEventListener("click", () => renderGrid(dimN - 1));
    el("dim-inc").addEventListener("click", () => renderGrid(dimN + 1));
    el("dim-n").addEventListener("change", () => renderGrid(el("dim-n").value));
    renderGrid(4, EJEMPLOS.principal.A, EJEMPLOS.principal.b, ["0", "0", "0", "0"]);
  });
})();
