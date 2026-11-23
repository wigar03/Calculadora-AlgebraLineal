/* Utilidades puras de exportación P2 (CSV según contrato y LaTeX compilable). */
(() => {
  "use strict";

  const NUMERO_VALIDO = /^([+-]?(?:\d+(?:\.\d*)?|\.\d+))(?:[eE]([+-]?\d+))?$/;
  const CERO_NUMERICO = /^[+-]?(?:0+(?:\.0*)?|\.0+)(?:[eE][+-]?\d+)?$/;
  const ENTERO_LARGO = /^[+-]?0*[1-9]\d{15,}$/;
  const FRACCION_EXACTA = /^-?\d+\/0*[1-9]\d*$/;
  const PREFIJO_FORMULA = /^(?:[\t\r]|[\s\p{Z}\p{Cc}\uFEFF]*[=+\-@])/u;
  const UMBRAL_LONGTABLE = 30;

  function formatearNumeroCSV(texto, decimal) {
    const m = NUMERO_VALIDO.exec(texto);
    if (!m) return texto;
    if (CERO_NUMERICO.test(texto)) return "0";
    const mant = decimal !== "." ? m[1].replace(".", decimal) : m[1];
    if (!m[2]) return mant;
    const signo = m[2].startsWith("-") ? "-" : "+";
    const exp = m[2].replace(/^[+-]/, "").padStart(2, "0");
    return `${mant}E${signo}${exp}`;
  }

  function formatearCeldaCSV(valor, decimal) {
    if (valor === null || valor === undefined) return "";
    if (typeof valor === "number") {
      if (!Number.isFinite(valor)) throw new RangeError(`Valor numérico no finito no exportable en CSV: ${valor}`);
      return valor === 0 ? "0" : formatearNumeroCSV(String(valor), decimal);
    }
    const txt = String(valor);
    if (ENTERO_LARGO.test(txt) || FRACCION_EXACTA.test(txt)) return `="${txt}"`;
    if (NUMERO_VALIDO.test(txt)) return formatearNumeroCSV(txt, decimal);
    const rec = txt.trim();
    if (rec !== txt && (FRACCION_EXACTA.test(rec) || ENTERO_LARGO.test(rec))) return `'${txt}`;
    return PREFIJO_FORMULA.test(txt) ? `'${txt}` : txt;
  }

  function protegerTextoCSV(valor) {
    const txt = String(valor ?? "");
    if (FRACCION_EXACTA.test(txt) || ENTERO_LARGO.test(txt)) return `="${txt}"`;
    const rec = txt.trim();
    if (rec !== txt && (FRACCION_EXACTA.test(rec) || ENTERO_LARGO.test(rec))) return `'${txt}`;
    return PREFIJO_FORMULA.test(txt) && !NUMERO_VALIDO.test(txt) ? `'${txt}` : txt;
  }

  function escaparCampoCSV(texto, separador) {
    if (texto.includes(separador) || texto.includes('"') || texto.includes("\n") || texto.includes("\r") || /^\s|\s$/.test(texto)) {
      return `"${texto.replace(/"/g, '""')}"`;
    }
    return texto;
  }

  function filaCSV(celdas, separador) {
    if (celdas.length === 1 && celdas[0] === "") return '""';
    return celdas.join(separador);
  }

  function lineasTablaCSV(t, separador, decimal) {
    const columnas = Array.isArray(t && t.columnas) ? t.columnas : [];
    const filas = Array.isArray(t && t.filas) ? t.filas : [];
    if (!columnas.length && !filas.length) return [];
    const lineas = [];
    if (columnas.length) lineas.push(filaCSV(columnas.map(c => escaparCampoCSV(protegerTextoCSV(c), separador)), separador));
    for (const fila of filas) lineas.push(filaCSV(fila.map(v => escaparCampoCSV(formatearCeldaCSV(v, decimal), separador)), separador));
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

  const MATH_UNICODE = {
    "α": "\\alpha", "β": "\\beta", "γ": "\\gamma", "δ": "\\delta", "ε": "\\varepsilon", "ϵ": "\\epsilon", "ζ": "\\zeta", "η": "\\eta",
    "θ": "\\theta", "ϑ": "\\vartheta", "ι": "\\iota", "κ": "\\kappa", "λ": "\\lambda", "μ": "\\mu", "µ": "\\mu", "ν": "\\nu", "ξ": "\\xi",
    "ο": "o", "π": "\\pi", "ϖ": "\\varpi", "ρ": "\\rho", "ϱ": "\\varrho", "σ": "\\sigma", "ς": "\\varsigma", "τ": "\\tau", "υ": "\\upsilon",
    "φ": "\\varphi", "ϕ": "\\phi", "χ": "\\chi", "ψ": "\\psi", "ω": "\\omega",
    "Α": "A", "Β": "B", "Γ": "\\Gamma", "Δ": "\\Delta", "Ε": "E", "Ζ": "Z", "Η": "H", "Θ": "\\Theta", "Ι": "I", "Κ": "K", "Λ": "\\Lambda",
    "Μ": "M", "Ν": "N", "Ξ": "\\Xi", "Ο": "O", "Π": "\\Pi", "Ρ": "P", "Σ": "\\Sigma", "Τ": "T", "Υ": "\\Upsilon", "Φ": "\\Phi", "Χ": "X", "Ψ": "\\Psi", "Ω": "\\Omega",
    "←": "\\leftarrow", "→": "\\rightarrow", "↔": "\\leftrightarrow", "⇐": "\\Leftarrow", "⇒": "\\Rightarrow", "⇔": "\\Leftrightarrow", "↑": "\\uparrow", "↓": "\\downarrow", "↦": "\\mapsto",
    "−": "-", "±": "\\pm", "∓": "\\mp", "×": "\\times", "÷": "\\div", "·": "\\cdot", "∘": "\\circ", "∙": "\\bullet",
    "≤": "\\le", "≥": "\\ge", "≠": "\\ne", "≈": "\\approx", "≡": "\\equiv", "∼": "\\sim", "≃": "\\simeq", "≅": "\\cong", "∝": "\\propto", "≪": "\\ll", "≫": "\\gg", "⊥": "\\perp", "∥": "\\parallel", "‖": "\\|",
    "∞": "\\infty", "∂": "\\partial", "∇": "\\nabla", "√": "\\surd", "∑": "\\sum", "∏": "\\prod", "∫": "\\int",
    "∈": "\\in", "∉": "\\notin", "⊂": "\\subset", "⊃": "\\supset", "⊆": "\\subseteq", "⊇": "\\supseteq", "∪": "\\cup", "∩": "\\cap", "∅": "\\emptyset",
    "∀": "\\forall", "∃": "\\exists", "¬": "\\neg", "∧": "\\wedge", "∨": "\\vee",
    "ℝ": "\\mathbb{R}", "ℂ": "\\mathbb{C}", "ℕ": "\\mathbb{N}", "ℤ": "\\mathbb{Z}", "ℚ": "\\mathbb{Q}",
    "°": "^{\\circ}", "′": "'", "″": "''", "✓": "\\checkmark", "✗": "\\times",
    "⁰": "^{0}", "¹": "^{1}", "²": "^{2}", "³": "^{3}", "⁴": "^{4}", "⁵": "^{5}", "⁶": "^{6}", "⁷": "^{7}", "⁸": "^{8}", "⁹": "^{9}", "⁺": "^{+}", "⁻": "^{-}", "ⁿ": "^{n}",
    "₀": "_{0}", "₁": "_{1}", "₂": "_{2}", "₃": "_{3}", "₄": "_{4}", "₅": "_{5}", "₆": "_{6}", "₇": "_{7}", "₈": "_{8}", "₉": "_{9}",
  };
  const ESCAPES_TEXTO = {
    "\\": "\\textbackslash{}", "{": "\\{", "}": "\\}", "&": "\\&", "$": "\\$", "%": "\\%", "#": "\\#", "_": "\\_", "^": "\\^{}", "~": "\\~{}",
    "—": "---", "–": "--", "…": "\\ldots{}", "“": "``", "”": "''", "‘": "`", "’": "'", "«": "\\guillemotleft{}", "»": "\\guillemotright{}", "\u00A0": "~",
  };
  const ES_TEXTO_LATIN_T1 = /^[\x20-\x7E¡¿ªºÀ-ÖØ-öø-ÿ]$/;
  const codigoUnicode = ch => `U+${ch.codePointAt(0).toString(16).toUpperCase().padStart(4, "0")}`;

  const COMANDOS_MAT = new Set(["det", "mid", "varepsilon", "Delta", "infty", "text", "left", "right", "frac", "cdot", "times", "vec", "operatorname", "mathbb", "rho", "sum", "|", ";", ",", "%", " "]);

  function esMathSeguro(s) {
    if (!s || s !== s.trim() || /[^\x20-\x7EáéíóúÁÉÍÓÚñÑüÜ]/.test(s) || /[=@!"\t\r\n]/.test(s) || /(?<!\\);/.test(s)) return false;
    if (/[áéíóúÁÉÍÓÚñÑüÜ]/.test(s) && !/^\\text\{[^\\{}]+\}$/.test(s)) return false;
    const cmds = [...s.matchAll(/\\([a-zA-Z]+|[^a-zA-Z])/g)];
    if (cmds.some(m => !COMANDOS_MAT.has(m[1]))) return false;
    return cmds.length > 0 || /^[a-zA-Z0-9()'|,.\s\[\]^_{}+-]+$/.test(s);
  }

  function escaparTextoLatex(texto) {
    return String(texto ?? "").replace(/[\r\n\t]+|[\s\S]/gu, tok => {
      if (tok[0] === "\r" || tok[0] === "\n" || tok[0] === "\t") return " ";
      if (ESCAPES_TEXTO[tok]) return ESCAPES_TEXTO[tok];
      if (MATH_UNICODE[tok]) return `$${MATH_UNICODE[tok]}$`;
      if (ES_TEXTO_LATIN_T1.test(tok)) return tok;
      return `\\texttt{[${codigoUnicode(tok)}]}\\allowbreak `;
    });
  }

  function normalizarMathLatex(texto) {
    const s = String(texto ?? "");
    return /^[\x20-\x7E\r\n\t]*$/.test(s) ? s : s.replace(/[^\x20-\x7E\r\n\t]/gu, (ch, off) => {
      if (ch === "—") return "---";
      if (ch === "–") return "--";
      if (ch === "…") return "\\ldots";
      if (MATH_UNICODE[ch]) {
        const cmd = MATH_UNICODE[ch];
        return /[a-zA-Z]$/.test(cmd) && /^[a-zA-Z]/.test(s.slice(off + ch.length)) ? `${cmd} ` : cmd;
      }
      return ES_TEXTO_LATIN_T1.test(ch) ? ch : `\\texttt{[${codigoUnicode(ch)}]}`;
    });
  }

  function textoMixtoALatex(texto) {
    return String(texto ?? "").split(/(\$\$[\s\S]*?\$\$|\$[\s\S]*?\$)/g).map(parte => {
      if (parte.startsWith("$$") && parte.endsWith("$$") && parte.length >= 4) {
        return `\\[\n${normalizarMathLatex(parte.slice(2, -2).trim())}\n\\]`;
      }
      if (parte.startsWith("$") && parte.endsWith("$") && parte.length >= 2) {
        const mat = `$${normalizarMathLatex(parte.slice(1, -1))}$`;
        return mat.length > 90 && mat.includes("\\left") ? `\\ajm{${mat}}` : mat;
      }
      return escaparTextoLatex(parte);
    }).join("");
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
    return esMathSeguro(s) ? `$${s}$` : escaparTextoLatex(s);
  }

  function celdaLatex(valor) {
    if (valor === null || valor === undefined) return "---";
    if (typeof valor === "number") return numeroALatex(valor);
    const s = String(valor);
    return /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(s.trim()) ? numeroALatex(s) : textoMixtoALatex(s);
  }

  function tablaALatex(t, opciones = {}) {
    const cols = Array.isArray(t && t.columnas) ? t.columnas : [];
    const filas = Array.isArray(t && t.filas) ? t.filas : [];
    const n = Math.max(1, cols.length);
    const umbral = opciones.umbralLongtable ?? UMBRAL_LONGTABLE;
    const usarLong = Boolean(opciones.longtable) || filas.length > umbral;
    const cabecera = cols.length ? `${cols.map(cabeceraALatex).join(" & ")} \\\\` : "";
    if (usarLong) {
      const apaisado = n >= 8;
      const sep = n >= 12 ? 1.5 : n >= 6 ? 2.5 : 4;
      const tam = n >= 12 ? "\\tiny" : n >= 6 ? "\\scriptsize" : "\\footnotesize";
      const ancho = `\\dimexpr(\\linewidth-${(2 * n + 1) * sep}pt)/${n}\\relax`;
      const spec = Array.from({ length: n }, () => `C{${ancho}}`).join(" ");
      const out = [];
      if (apaisado) out.push("\\begin{landscape}");
      if (t && t.titulo) out.push(`\\subsubsection*{${textoMixtoALatex(t.titulo)}}`);
      out.push(`\\begingroup\\setlength{\\tabcolsep}{${sep}pt}${tam}`, `\\begin{longtable}{${spec}}`, "\\hline");
      if (cabecera) out.push(cabecera, "\\hline");
      out.push("\\endfirsthead", "\\hline");
      if (cabecera) out.push(cabecera, "\\hline");
      out.push("\\endhead", "\\hline", "\\endfoot", "\\hline", "\\endlastfoot");
      for (const fila of filas) out.push(`${fila.map(celdaLatex).join(" & ")} \\\\`);
      out.push("\\end{longtable}", "\\endgroup");
      if (apaisado) out.push("\\end{landscape}");
      return out.join("\n");
    }
    const spec = Array.from({ length: n }, () => "c").join(" ");
    const out = ["\\begin{table}[htbp]", "\\centering"];
    if (t && t.titulo) out.push(`\\caption{${textoMixtoALatex(t.titulo)}}`);
    out.push("\\setlength{\\tabcolsep}{4pt}", "\\footnotesize", "\\resizebox{\\ifdim\\width>\\linewidth\\linewidth\\else\\width\\fi}{!}{%", `\\begin{tabular}{${spec}}`, "\\hline");
    if (cabecera) out.push(cabecera, "\\hline");
    for (const fila of filas) out.push(`${fila.map(celdaLatex).join(" & ")} \\\\`);
    out.push("\\hline", "\\end{tabular}}", "\\end{table}");
    return out.join("\n");
  }

  function bloqueEcuacion(it) {
    const et = String(it.etiqueta ?? ""), eq = normalizarMathLatex(it.latex);
    if (esMathSeguro(et)) return `\\[\n${et} = ${eq}\n\\]`;
    return `\\noindent\\textbf{${escaparTextoLatex(et)}}:\n\\[\n${eq}\n\\]`;
  }

  function procedimientoALatex(p) {
    const out = [
      "\\documentclass[11pt,a4paper]{article}", "\\usepackage[utf8]{inputenc}", "\\usepackage[T1]{fontenc}",
      "\\usepackage[spanish]{babel}", "\\spanishplainpercent", "\\usepackage[a4paper,margin=1.2cm]{geometry}",
      "\\usepackage{amsmath,amssymb}", "\\setcounter{MaxMatrixCols}{32}", "\\usepackage{graphicx}",
      "\\usepackage{array}", "\\usepackage{pdflscape}", "\\usepackage{longtable}", "\\sloppy", "\\emergencystretch=3em",
      "\\newsavebox{\\eqbox}", "\\makeatletter",
      "\\@namedef{[}{\\par\\smallskip\\noindent\\setbox\\eqbox\\hbox\\bgroup\\math\\displaystyle}",
      "\\@namedef{]}{\\endmath\\egroup\\makebox[\\linewidth][c]{\\ifdim\\wd\\eqbox>\\linewidth\\resizebox{\\linewidth}{!}{\\box\\eqbox}\\else\\box\\eqbox\\fi}\\par\\smallskip}",
      "\\makeatother",
      "\\newcommand{\\ajm}[1]{\\setbox\\eqbox\\hbox{#1}\\ifdim\\wd\\eqbox>\\linewidth\\resizebox{0.98\\linewidth}{!}{\\box\\eqbox}\\else\\box\\eqbox\\fi}",
      "\\newcolumntype{C}[1]{>{\\setbox\\eqbox\\hbox\\bgroup}c<{\\egroup\\ifdim\\wd\\eqbox>#1\\resizebox{#1}{!}{\\box\\eqbox}\\else\\box\\eqbox\\fi}}",
      "\\begin{document}",
    ];
    if (p && p.titulo) out.push(`\\section*{${textoMixtoALatex(p.titulo)}}`);
    if (Array.isArray(p && p.entrada) && p.entrada.length) out.push("\\subsection*{Datos de entrada}", ...p.entrada.map(bloqueEcuacion));
    if (Array.isArray(p && p.pasos) && p.pasos.length) {
      out.push("\\subsection*{Procedimiento}");
      for (const s of p.pasos) {
        if (s.titulo) out.push(`\\subsubsection*{${textoMixtoALatex(s.titulo)}}`);
        if (s.texto) out.push(textoMixtoALatex(s.texto));
        for (const f of s.latex || []) out.push(`\\[\n${normalizarMathLatex(f)}\n\\]`);
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
