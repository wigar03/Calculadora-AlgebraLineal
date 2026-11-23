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

  if (typeof module !== "undefined" && module.exports) {
    module.exports = {
      MOTIVOS, GARANTIAS, PALETA, nombreVarLatex, numeroLatex, vectorLatex,
      formulaMetodoLatex, normasLatex, verificacionLatex
    };
  }
})();
