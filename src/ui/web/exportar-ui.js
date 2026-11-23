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

  const api = { MODULOS, obtener: id => procedimientos.get(id) || null };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (typeof window !== "undefined") window.ExportarUI = api;
})();
