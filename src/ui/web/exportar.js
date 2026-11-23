/* Utilidades puras de exportación (base de P2, sin cargar en index.html). */
(() => {
  "use strict";

  const NUMERO_DECIMAL = /^[+-]?(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?$/;

  function formatearCeldaCSV(valor, decimal) {
    if (valor === null || valor === undefined) return "";
    if (typeof valor === "number") {
      if (!Number.isFinite(valor)) return "";
      const txt = String(valor);
      return decimal !== "." ? txt.replace(".", decimal) : txt;
    }
    const txt = String(valor);
    if (decimal !== "." && NUMERO_DECIMAL.test(txt.trim())) {
      return txt.replace(".", decimal);
    }
    return txt;
  }

  function escaparCampoCSV(texto, separador) {
    if (texto.includes(separador) || texto.includes('"') || texto.includes("\n") || texto.includes("\r")) {
      return `"${texto.replace(/"/g, '""')}"`;
    }
    return texto;
  }

  function tablaACSV(t, opciones = {}) {
    const separador = opciones.separador || ",";
    const decimal = opciones.decimal || ".";
    const columnas = Array.isArray(t && t.columnas) ? t.columnas : [];
    const filas = Array.isArray(t && t.filas) ? t.filas : [];
    if (!columnas.length && !filas.length) return "";
    const lineas = [];
    if (columnas.length) {
      lineas.push(columnas.map(c => escaparCampoCSV(String(c ?? ""), separador)).join(separador));
    }
    for (const fila of filas) {
      lineas.push(fila.map(v => escaparCampoCSV(formatearCeldaCSV(v, decimal), separador)).join(separador));
    }
    return lineas.join("\r\n");
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

  const api = { tablaACSV, textoPlano };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (typeof window !== "undefined") window.ExportarProcedimiento = api;
})();
