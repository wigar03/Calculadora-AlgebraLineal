/* Componente reutilizable Exportar (P2) para la cabecera de los 11 módulos. */
(() => {
  "use strict";

  const MODULOS = [
    "tab-vectores", "tab-combinacion", "tab-matrices", "tab-inversa", "tab-ecuaciones",
    "tab-determinante", "tab-biseccion", "tab-regla-falsa", "tab-newton-raphson",
    "tab-secante", "tab-iterativos",
  ];

  const ESTILOS = `
.exp-heading > div:first-child { flex: 1 1 auto; min-width: 0; }
.exp-heading > .notebook-chapter, .exp-heading > .bis-chapter { flex: 0 0 auto; }
.exp-control { position: relative; display: inline-flex; align-items: center; gap: .5rem; flex: 0 0 auto; margin-top: .25rem; }
.exp-trigger { display: inline-flex; align-items: center; gap: .45rem; padding: .45rem .8rem; min-height: 36px; white-space: nowrap; }
.exp-trigger:disabled { opacity: .45; cursor: not-allowed !important; }
.exp-chevron { width: .9rem; height: .9rem; transition: transform .15s ease; }
.exp-trigger[aria-expanded="true"] .exp-chevron { transform: rotate(180deg); }
.exp-status { font-size: .78rem; font-weight: 500; color: var(--accent-emerald, #39705a); white-space: nowrap; }
.exp-status:empty { display: none; }
.exp-menu { position: absolute; top: calc(100% + .45rem); right: 0; z-index: 30; min-width: 270px; max-width: min(320px, calc(100vw - 2rem)); background: var(--notebook-paper, var(--bis-paper, #fbfaf6)); border: 1px solid var(--notebook-rule, var(--bis-rule, #d4d5cb)); border-radius: 6px; padding: .4rem; box-shadow: 0 10px 28px rgba(0,0,0,.14); }
.exp-menu[hidden], .exp-item[hidden] { display: none !important; }
.exp-item { display: flex; align-items: flex-start; gap: .75rem; width: 100%; min-height: 48px; padding: .55rem .7rem; border: 0; border-radius: 4px; background: transparent; color: var(--notebook-ink, var(--bis-ink, #292e2a)); text-align: left; font: inherit; cursor: pointer; }
.exp-item:hover { background: var(--notebook-soft, var(--bis-soft, #f0ede4)); }
.exp-item:focus-visible { background: var(--notebook-soft, var(--bis-soft, #f0ede4)); outline: 2px solid var(--notebook-accent, var(--bis-accent, #8d342e)); outline-offset: -2px; }
.exp-item .lucide, .exp-item [data-lucide] { color: var(--notebook-accent, var(--bis-accent, #8d342e)); margin-top: .12rem; flex-shrink: 0; }
.exp-item-copy { display: flex; flex-direction: column; min-width: 0; }
.exp-item-title { font-size: .88rem; font-weight: 600; color: var(--notebook-accent, var(--bis-accent, #8d342e)); line-height: 1.3; }
.exp-item-hint { font-size: .76rem; color: var(--notebook-muted, var(--bis-muted, #60645d)); line-height: 1.35; margin-top: .1rem; }
@media (max-width: 680px) {
  .exp-heading { flex-wrap: wrap; }
  .exp-heading > div:first-child { flex: 1 1 0; min-width: 0; }
  .exp-control { flex: 1 0 100%; width: 100%; flex-direction: column; align-items: stretch; gap: .35rem; margin-top: .35rem; }
  .exp-trigger { width: 100%; justify-content: center; min-height: 44px; }
  .exp-status { text-align: center; }
  .exp-menu { position: static; width: 100%; max-width: none; margin-top: .25rem; box-shadow: 0 6px 18px rgba(0,0,0,.08); }
}`;

  const instancias = new Map();
  const procedimientos = new Map();
  let abierto = null;

  const tieneTablas = p => Boolean(p && Array.isArray(p.tablas) && p.tablas.some(t => Array.isArray(t.filas) && t.filas.length > 0));
  const extraerProcedimiento = r => (r && typeof r === "object" ? (r.procedimiento && typeof r.procedimiento === "object" ? r.procedimiento : (r.version === 1 && r.modulo ? r : null)) : null);

  function crearEl(doc, tag, cls, texto) {
    const n = doc.createElement(tag);
    if (cls) n.className = cls;
    if (texto !== undefined) n.textContent = texto;
    return n;
  }

  function crearIcono(doc, nombre, cls) {
    const i = crearEl(doc, "i", cls);
    i.setAttribute("data-lucide", nombre);
    i.setAttribute("aria-hidden", "true");
    return i;
  }

  function crearOpcion(doc, accion, icono, titulo, pista) {
    const btn = crearEl(doc, "button", "exp-item");
    btn.type = "button";
    btn.setAttribute("role", "menuitem");
    btn.setAttribute("tabindex", "-1");
    btn.dataset.expAction = accion;
    const copy = crearEl(doc, "span", "exp-item-copy");
    copy.append(crearEl(doc, "span", "exp-item-title", titulo), crearEl(doc, "span", "exp-item-hint", pista));
    btn.append(crearIcono(doc, icono), copy);
    return btn;
  }

  const visibles = inst => inst.items.filter(b => !b.hidden && !b.disabled);

  function anunciar(inst, texto) {
    clearTimeout(inst.timer);
    inst.status.textContent = texto;
    if (texto) inst.timer = setTimeout(() => { inst.status.textContent = ""; }, 2600);
  }

  function cerrar(inst, devolverFoco = true) {
    if (!inst) return;
    inst.menu.hidden = true;
    inst.trigger.setAttribute("aria-expanded", "false");
    if (abierto === inst) abierto = null;
    if (devolverFoco && !inst.trigger.disabled) inst.trigger.focus();
  }

  function abrir(inst, indiceFoco = null) {
    if (!inst || inst.trigger.disabled) return;
    if (abierto && abierto !== inst) cerrar(abierto, false);
    inst.menu.hidden = false;
    inst.trigger.setAttribute("aria-expanded", "true");
    abierto = inst;
    if (indiceFoco !== null) {
      const lista = visibles(inst);
      if (lista.length) lista[((indiceFoco % lista.length) + lista.length) % lista.length].focus();
    }
  }

  function sincronizar(moduloId) {
    const inst = instancias.get(moduloId);
    if (!inst) return;
    const proc = procedimientos.get(moduloId) || null;
    const activo = Boolean(proc);
    inst.trigger.disabled = !activo;
    inst.trigger.setAttribute("aria-disabled", String(!activo));
    inst.csvBtn.hidden = !tieneTablas(proc);
    if (!activo) {
      anunciar(inst, "");
      if (abierto === inst) cerrar(inst, false);
    }
  }

  async function copiarTexto(texto, doc) {
    if (typeof navigator !== "undefined" && navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(texto);
      return true;
    }
    if (!doc || !doc.body) return false;
    const ta = doc.createElement("textarea");
    ta.value = texto; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
    doc.body.appendChild(ta); ta.select?.();
    const ok = typeof doc.execCommand === "function" ? doc.execCommand("copy") : false;
    ta.remove?.();
    return Boolean(ok);
  }

  function ejecutarAccion(inst, accion, doc) {
    const proc = procedimientos.get(inst.moduloId);
    const exp = typeof window !== "undefined" ? window.ExportarProcedimiento : null;
    if (!proc) return;
    cerrar(inst, false);
    if (accion === "latex" && exp) {
      Promise.resolve(copiarTexto(exp.procedimientoALatex(proc), doc))
        .then(ok => anunciar(inst, ok ? "Copiado" : "No se pudo copiar"))
        .catch(() => anunciar(inst, "No se pudo copiar"));
    } else if (accion === "csv" && exp && tieneTablas(proc)) {
      const csv = exp.tablasACSV(proc.tablas);
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = doc.createElement("a");
      a.href = url; a.download = `calculadora-${proc.modulo || inst.moduloId.replace(/^tab-/, "")}.csv`;
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      anunciar(inst, "CSV descargado");
    } else if (accion === "imprimir" && typeof window !== "undefined" && window.print) {
      window.print();
    }
  }

  function registrar(moduloId, respuesta) {
    const proc = extraerProcedimiento(respuesta);
    if (proc) procedimientos.set(moduloId, proc);
    else procedimientos.delete(moduloId);
    sincronizar(moduloId);
  }

  function limpiar(moduloId) {
    procedimientos.delete(moduloId);
    sincronizar(moduloId);
  }

  function montarModulo(doc, moduloId) {
    const sec = doc.getElementById(moduloId);
    const hdr = sec && sec.querySelector("header.notebook-heading, header.bis-notebook-heading");
    if (!hdr || instancias.has(moduloId)) return;
    hdr.classList.add("exp-heading");
    const wrap = crearEl(doc, "div", "exp-control");
    const status = crearEl(doc, "span", "exp-status");
    status.setAttribute("role", "status"); status.setAttribute("aria-live", "polite");
    const trigger = crearEl(doc, "button", "btn-clear exp-trigger");
    trigger.type = "button"; trigger.disabled = true;
    const menuId = `exp-menu-${moduloId}`;
    trigger.setAttribute("aria-disabled", "true"); trigger.setAttribute("aria-haspopup", "menu");
    trigger.setAttribute("aria-expanded", "false"); trigger.setAttribute("aria-controls", menuId);
    trigger.append(crearIcono(doc, "share-2", "btn-icon"), crearEl(doc, "span", "", "Exportar"), crearIcono(doc, "chevron-down", "exp-chevron"));
    const menu = crearEl(doc, "div", "exp-menu");
    menu.setAttribute("id", menuId); menu.setAttribute("role", "menu"); menu.setAttribute("aria-label", "Opciones de exportación"); menu.hidden = true;
    const latexBtn = crearOpcion(doc, "latex", "copy", "Copiar LaTeX", "Pasos, resultado y verificación");
    const csvBtn = crearOpcion(doc, "csv", "download", "Exportar CSV", "Separador ; y coma decimal");
    csvBtn.hidden = true;
    const printBtn = crearOpcion(doc, "imprimir", "printer", "Imprimir o guardar como PDF", "Solo el resultado, sin menús");
    const items = [latexBtn, csvBtn, printBtn];
    menu.append(...items); wrap.append(status, trigger, menu); hdr.append(wrap);
    const inst = { moduloId, wrap, trigger, menu, status, csvBtn, items, timer: null };
    instancias.set(moduloId, inst);
    trigger.addEventListener("click", () => (menu.hidden ? abrir(inst, null) : cerrar(inst, false)));
    trigger.addEventListener("keydown", ev => {
      if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); menu.hidden ? abrir(inst, 0) : cerrar(inst, true); }
      else if (ev.key === "ArrowDown") { ev.preventDefault(); abrir(inst, 0); }
      else if (ev.key === "ArrowUp") { ev.preventDefault(); abrir(inst, -1); }
      else if (ev.key === "Escape" && !menu.hidden) { ev.preventDefault(); cerrar(inst, true); }
    });
    menu.addEventListener("keydown", ev => {
      const lista = visibles(inst); const i = lista.indexOf(doc.activeElement);
      if (ev.key === "Escape") { ev.preventDefault(); cerrar(inst, true); }
      else if (ev.key === "ArrowDown" && lista.length) { ev.preventDefault(); lista[(i + 1 + lista.length) % lista.length].focus(); }
      else if (ev.key === "ArrowUp" && lista.length) { ev.preventDefault(); lista[(i - 1 + lista.length) % lista.length].focus(); }
      else if (ev.key === "Home" && lista.length) { ev.preventDefault(); lista[0].focus(); }
      else if (ev.key === "End" && lista.length) { ev.preventDefault(); lista[lista.length - 1].focus(); }
      else if (ev.key === "Tab") cerrar(inst, false);
    });
    items.forEach(b => b.addEventListener("click", () => ejecutarAccion(inst, b.dataset.expAction, doc)));
    const entradas = [sec.querySelector(".card-input"), moduloId === "tab-iterativos" ? doc.getElementById("it-card-1") : null, moduloId === "tab-iterativos" ? doc.getElementById("it-card-2") : null].filter(Boolean);
    entradas.forEach(box => { ["input", "change"].forEach(t => box.addEventListener(t, () => limpiar(moduloId))); });
    sincronizar(moduloId);
  }

  let globalesActivos = false;
  function montar(doc = typeof document !== "undefined" ? document : null) {
    if (!doc) return;
    if (doc.head && !doc.getElementById("exportar-ui-styles")) {
      const st = crearEl(doc, "style"); st.setAttribute("id", "exportar-ui-styles"); st.textContent = ESTILOS; doc.head.appendChild(st);
    }
    MODULOS.forEach(id => montarModulo(doc, id));
    if (!globalesActivos) {
      globalesActivos = true;
      doc.addEventListener("click", ev => { if (abierto && !abierto.wrap.contains(ev.target)) cerrar(abierto, false); });
      doc.addEventListener("calculator:navigate", () => { if (abierto) cerrar(abierto, false); });
    }
    if (typeof window !== "undefined" && window.lucide && window.lucide.createIcons) {
      try { window.lucide.createIcons(); } catch (_) {}
    }
  }

  const api = { MODULOS, montar, registrar, limpiar, obtener: id => procedimientos.get(id) || null };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (typeof window !== "undefined") window.ExportarUI = api;
  if (typeof document !== "undefined") document.addEventListener("DOMContentLoaded", () => montar(document));
})();
