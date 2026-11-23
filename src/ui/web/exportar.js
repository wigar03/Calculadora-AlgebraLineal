/* Utilidades puras de exportación P2 (CSV según contrato y LaTeX compilable). */
(() => {
  "use strict";

  const NUMERO_VALIDO = /^([+-]?(?:\d+(?:\.\d*)?|\.\d+))(?:[eE]([+-]?\d+))?$/;
  const FRACCION_EXACTA = /^-?\d+\/\d+$/;
  const PREFIJO_FORMULA = /^[=+\-@\t\r]/;
  const UMBRAL_LONGTABLE = 30;

  function formatearNumeroCSV(texto, decimal) {
    const m = NUMERO_VALIDO.exec(texto);
    if (!m) return texto;
    const mant = decimal !== "." ? m[1].replace(".", decimal) : m[1];
    if (!m[2]) return mant;
    const signo = m[2].startsWith("-") ? "-" : "+";
    const exp = m[2].replace(/^[+-]/, "").padStart(2, "0");
    return `${mant}E${signo}${exp}`;
  }

  function formatearCeldaCSV(valor, decimal) {
    if (valor === null || valor === undefined) return "";
    if (typeof valor === "number") {
      return Number.isFinite(valor) ? formatearNumeroCSV(String(Object.is(valor, -0) ? 0 : valor), decimal) : "";
    }
    const txt = String(valor);
    if (NUMERO_VALIDO.test(txt)) return formatearNumeroCSV(txt, decimal);
    if (FRACCION_EXACTA.test(txt)) return `="${txt}"`;
    return PREFIJO_FORMULA.test(txt) ? `'${txt}` : txt;
  }

  function protegerTextoCSV(valor) {
    const txt = String(valor ?? "");
    return PREFIJO_FORMULA.test(txt) && !NUMERO_VALIDO.test(txt) && !FRACCION_EXACTA.test(txt) ? `'${txt}` : txt;
  }

  function escaparCampoCSV(texto, separador) {
    if (texto.includes(separador) || texto.includes('"') || texto.includes("\n") || texto.includes("\r") || /^\s|\s$/.test(texto)) {
      return `"${texto.replace(/"/g, '""')}"`;
    }
    return texto;
  }

  function lineasTablaCSV(t, separador, decimal) {
    const columnas = Array.isArray(t && t.columnas) ? t.columnas : [];
    const filas = Array.isArray(t && t.filas) ? t.filas : [];
    if (!columnas.length && !filas.length) return [];
    const lineas = [];
    if (columnas.length) lineas.push(columnas.map(c => escaparCampoCSV(protegerTextoCSV(c), separador)).join(separador));
    for (const fila of filas) lineas.push(fila.map(v => escaparCampoCSV(formatearCeldaCSV(v, decimal), separador)).join(separador));
    return lineas;
  }

  function tablaACSV(t, opciones = {}) {
    const separador = opciones.separador || ";";
    const decimal = opciones.decimal || ",";
    const lineas = lineasTablaCSV(t, separador, decimal);
    if (!lineas.length) return "";
    return `${opciones.bom === false ? "" : "\uFEFF"}${lineas.join("\r\n")}`;
  }

  function tablasACSV(tablas, opciones = {}) {
    if (!Array.isArray(tablas) || !tablas.length) return "";
    if (tablas.length === 1) return tablaACSV(tablas[0], opciones);
    const separador = opciones.separador || ";";
    const decimal = opciones.decimal || ",";
    const bloques = [];
    for (const t of tablas) {
      const lineas = lineasTablaCSV(t, separador, decimal);
      if (!lineas.length) continue;
      if (t && t.titulo) lineas.unshift(escaparCampoCSV(protegerTextoCSV(t.titulo), separador));
      bloques.push(lineas.join("\r\n"));
    }
    if (!bloques.length) return "";
    return `${opciones.bom === false ? "" : "\uFEFF"}${bloques.join("\r\n\r\n")}`;
  }

  function textoPlano(p) {
    if (!p || typeof p !== "object") return "";
    const out = [];
    if (p.titulo) out.push(p.titulo, "=".repeat(Math.min(72, p.titulo.length)));
    if (Array.isArray(p.entrada) && p.entrada.length) {
      out.push("", "Datos de entrada:");
      for (const it of p.entrada) out.push(`  ${it.etiqueta} = ${it.latex}`);
    }
    if (Array.isArray(p.pasos) && p.pasos.length) {
      out.push("", "Procedimiento:");
      p.pasos.forEach((s, idx) => {
        out.push(`${idx + 1}. ${s.titulo}`);
        if (s.texto) out.push(`   ${s.texto}`);
        for (const f of s.latex || []) out.push(`   ${f}`);
        if (Array.isArray(s.matriz) && s.matriz.length) {
          for (const fila of s.matriz) out.push(`   [ ${fila.join("  ")} ]`);
        }
        for (const d of s.detalles || []) out.push(`   - ${d}`);
      });
    }
    if (Array.isArray(p.resultado) && p.resultado.length) {
      out.push("", "Resultado:");
      for (const it of p.resultado) out.push(`  ${it.etiqueta} = ${it.latex}`);
    }
    if (Array.isArray(p.verificacion) && p.verificacion.length) {
      out.push("", "Verificación:");
      for (const v of p.verificacion) out.push(`  - ${v}`);
    }
    if (Array.isArray(p.tablas) && p.tablas.length) {
      for (const t of p.tablas) {
        out.push("", `${t.titulo || "Tabla"}:`);
        out.push(`  ${(t.columnas || []).join(" | ")}`);
        for (const fila of t.filas || []) {
          out.push(`  ${fila.map(v => (v === null || v === undefined ? "—" : String(v))).join(" | ")}`);
        }
      }
    }
    if (Array.isArray(p.avisos) && p.avisos.length) {
      out.push("", "Avisos:");
      for (const a of p.avisos) out.push(`  - ${a}`);
    }
    return out.join("\n").trim();
  }

  const SIMBOLOS_UNICODE = {
    "←": "$\\leftarrow$", "→": "$\\rightarrow$", "−": "-", "—": "---", "–": "--", "…": "\\ldots{}",
    "✓": "$\\checkmark$", "✗": "$\\times$", "≈": "$\\approx$", "≤": "$\\le$", "≥": "$\\ge$",
    "≠": "$\\ne$", "·": "$\\cdot$", "×": "$\\times$", "∞": "$\\infty$", "ρ": "$\\rho$", "ε": "$\\varepsilon$", "Δ": "$\\Delta$",
  };

  function escaparTextoLatex(texto) {
    return String(texto ?? "").replace(/\\/g, "\\textbackslash{}").replace(/([{}&$%#_])/g, "\\$1")
      .replace(/\^/g, "\\^{}").replace(/~/g, "\\~{}")
      .replace(/[←→−—–…✓✗≈≤≥≠·×∞ρεΔ]/g, ch => SIMBOLOS_UNICODE[ch] || ch).replace(/\r?\n/g, " ");
  }

  function textoMixtoALatex(texto) {
    return String(texto ?? "").split(/(\$\$[\s\S]*?\$\$|\$[\s\S]*?\$)/g).map(parte =>
      ((parte.startsWith("$$") && parte.endsWith("$$") && parte.length >= 4) ||
       (parte.startsWith("$") && parte.endsWith("$") && parte.length >= 2))
        ? parte.replace(/—/g, "---").replace(/−/g, "-")
        : escaparTextoLatex(parte)
    ).join("");
  }

  function numeroALatex(valor) {
    if (valor === null || valor === undefined) return "---";
    if (typeof valor === "number" && !Number.isFinite(valor)) return "$\\text{no finito}$";
    const partes = String(valor).trim().toLowerCase().split("e");
    return partes.length === 2 ? `$${partes[0]} \\times 10^{${Number(partes[1])}}$` : `$${partes[0]}$`;
  }

  function cabeceraALatex(col) {
    const s = String(col ?? "");
    if (s.includes("$")) return textoMixtoALatex(s);
    return (/[\\_^]/.test(s) || /^[a-zA-Z0-9()'|,.\s+-]+$/.test(s)) ? `$${s}$` : escaparTextoLatex(s);
  }

  function celdaLatex(valor) {
    if (valor === null || valor === undefined) return "---";
    if (typeof valor === "number") return numeroALatex(valor);
    const s = String(valor);
    return /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(s.trim()) ? numeroALatex(s) : textoMixtoALatex(s);
  }

  function tablaALatex(t) {
    const cols = Array.isArray(t && t.columnas) ? t.columnas : [];
    const filas = Array.isArray(t && t.filas) ? t.filas : [];
    const out = ["\\begin{table}[htbp]", "\\centering"];
    if (t && t.titulo) out.push(`\\caption{${textoMixtoALatex(t.titulo)}}`);
    out.push(`\\begin{tabular}{${cols.length ? cols.map(() => "c").join(" ") : "c"}}`, "\\hline");
    if (cols.length) out.push(`${cols.map(cabeceraALatex).join(" & ")} \\\\`, "\\hline");
    for (const fila of filas) out.push(`${fila.map(celdaLatex).join(" & ")} \\\\`);
    out.push("\\hline", "\\end{tabular}", "\\end{table}");
    return out.join("\n");
  }

  function bloqueEcuacion(it) {
    const et = String(it.etiqueta ?? "");
    const izq = /[\\_^]/.test(et) || /^[a-zA-Z0-9()'|,\s\[\]]+$/.test(et) ? et : `\\text{${escaparTextoLatex(et)}}`;
    return `\\[\n${izq} = ${it.latex}\n\\]`;
  }

  function procedimientoALatex(p) {
    const out = ["\\documentclass[11pt,a4paper]{article}", "\\usepackage[utf8]{inputenc}",
      "\\usepackage[T1]{fontenc}", "\\usepackage{amsmath,amssymb}", "\\begin{document}"];
    if (p && p.titulo) out.push(`\\section*{${textoMixtoALatex(p.titulo)}}`);
    if (Array.isArray(p && p.entrada) && p.entrada.length) out.push("\\subsection*{Datos de entrada}", ...p.entrada.map(bloqueEcuacion));
    if (Array.isArray(p && p.pasos) && p.pasos.length) {
      out.push("\\subsection*{Procedimiento}");
      for (const s of p.pasos) {
        if (s.titulo) out.push(`\\paragraph{${textoMixtoALatex(s.titulo)}}`);
        if (s.texto) out.push(textoMixtoALatex(s.texto));
        for (const f of s.latex || []) out.push(`\\[\n${f}\n\\]`);
        if (Array.isArray(s.matriz) && s.matriz.length) {
          out.push(`\\[\n\\begin{pmatrix} ${s.matriz.map(r => r.map(String).join(" & ")).join(" \\\\ ")} \\end{pmatrix}\n\\]`);
        }
        if (Array.isArray(s.detalles) && s.detalles.length) {
          out.push("\\begin{itemize}", ...s.detalles.map(d => `\\item ${textoMixtoALatex(d)}`), "\\end{itemize}");
        }
      }
    }
    if (Array.isArray(p && p.resultado) && p.resultado.length) out.push("\\subsection*{Resultado}", ...p.resultado.map(bloqueEcuacion));
    for (const [sec, lista] of [["Verificación", p && p.verificacion], ["Avisos", p && p.avisos]]) {
      if (Array.isArray(lista) && lista.length) out.push(`\\subsection*{${sec}}`, "\\begin{itemize}", ...lista.map(x => `\\item ${textoMixtoALatex(x)}`), "\\end{itemize}");
    }
    for (const t of (p && p.tablas) || []) out.push(tablaALatex(t));
    out.push("\\end{document}");
    return out.join("\n");
  }

  const api = { procedimientoALatex, tablaALatex, tablaACSV, tablasACSV, textoPlano };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (typeof window !== "undefined") window.ExportarProcedimiento = api;
})();
