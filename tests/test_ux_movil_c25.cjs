/* Prueba C-25 (INC-034): áreas táctiles >= 44x44 bajo pointer:coarse, .bis-fields en 1 col < 480 px y móvil 390 px sin desborde. */
const { test } = require('node:test'); const assert = require('node:assert/strict');
const fs = require('node:fs'), os = require('node:os'), path = require('node:path');
const { spawn, spawnSync } = require('node:child_process');
const ROOT = path.resolve(__dirname, '..'), WEB = path.join(ROOT, 'src', 'ui', 'web');
const ARRANQUE_MS = Number(process.env.P2_BROWSER_TIMEOUT_MS) || 20000;
const POLITICA_RE = /application control|control de aplicaciones|applocker|wdac|group policy|pol[ií]tica de grupo|blocked by|bloqueado por|access is denied|acceso denegado|0x800711c7|cannot execute|permission denied/i;
const buscarNav = () => (process.env.P2_BROWSER_EXE ? [process.env.P2_BROWSER_EXE] : ['C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', 'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe', '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser']).filter(p => fs.existsSync(p));
const esBloqueo = e => Boolean(e && (['EACCES', 'EPERM', 'ENOENT'].includes(e.code) || [5, 1260, 4551].includes(e.exitCode) || POLITICA_RE.test(`${e.message || ''}\n${e.stderr || ''}`)));
const matar = p => { if (!p || p.exitCode !== null || p.signalCode !== null || !p.pid) return; if (process.platform === 'win32') try { spawnSync('taskkill', ['/PID', String(p.pid), '/T', '/F'], { stdio: 'ignore', windowsHide: true, timeout: 5000 }); } catch (_) {} else try { process.kill(-p.pid, 'SIGKILL'); } catch (_) {} try { p.kill('SIGKILL'); } catch (_) {} };
const lanzar = (cmd, args, opts, rx, st, procs) => new Promise((res, rej) => {
  let proc, fin = false, buf = '', err = '';
  const done = (fn, v) => { if (fin) return; fin = true; clearTimeout(tm); fn(v); };
  const tm = setTimeout(() => { matar(proc); done(rej, Object.assign(new Error(`Timeout ${path.basename(cmd)}\n${err}`), { code: 'ETIMEDOUT', stderr: err })); }, ARRANQUE_MS); tm.unref();
  try { proc = spawn(cmd, args, { ...opts, detached: process.platform !== 'win32' }); } catch (e) { return done(rej, e); }
  procs.add(proc); proc.stderr?.on('data', d => { err = (err + d).slice(-8000); });
  proc[st]?.on('data', d => { buf += d; const m = buf.match(rx); if (m) done(res, { val: m[1] || m[0], proc }); });
  proc.once('error', e => { matar(proc); done(rej, e); }); proc.once('exit', (c, s) => done(rej, Object.assign(new Error(`${path.basename(cmd)} (${c}, ${s})\n${err}`), { exitCode: c, stderr: err })));
});
async function conectarCDP(port, sockets) {
  const pags = await (await fetch(`http://127.0.0.1:${port}/json/list`, { signal: AbortSignal.timeout(10000) })).json();
  const ws = new WebSocket(pags.find(p => p.type === 'page').webSocketDebuggerUrl); sockets.add(ws);
  await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
  let seq = 0; const pend = new Map(), evs = [];
  ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && pend.has(m.id)) { const [ok, ko] = pend.get(m.id); pend.delete(m.id); m.error ? ko(new Error(m.error.message)) : ok(m.result); } else evs.push(m); };
  const send = (method, params = {}) => new Promise((ok, ko) => { const id = ++seq; pend.set(id, [ok, ko]); ws.send(JSON.stringify({ id, method, params })); });
  const evalJS = async expr => { const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true }); if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text); return r.result.value; };
  return { ws, send, evalJS, evs };
}
test('CSS C-25: reglas pointer:coarse de 44px y .bis-fields en 1 columna bajo 480px', () => {
  const leer = f => fs.readFileSync(path.join(WEB, f), 'utf8');
  assert.match(leer('styles.css'), /@media\s*\(pointer:\s*coarse\)[\s\S]*?\.mini-stepper button[\s\S]*?44px/);
  assert.match(leer('biseccion.css'), /@media\s*\(pointer:\s*coarse\)[\s\S]*?\.btn-bis-zoom[\s\S]*?44px/);
  assert.match(leer('biseccion.css'), /@media\s*\(max-width:\s*480px\)[\s\S]*?\.bis-fields\s*\{\s*grid-template-columns:\s*(?:minmax\(0,\s*1fr\)|1fr)/);
  assert.match(leer('regla-falsa.css'), /@media\s*\(pointer:\s*coarse\)[\s\S]*?\.rf-mark-toggle/);
  assert.match(leer('newton-raphson.css'), /@media\s*\(pointer:\s*coarse\)[\s\S]*?\.btn-bis-zoom[\s\S]*?44px/);
});
test('navegador real C-25: escritorio intacto, táctil >=44px, .bis-fields 1 col y 11 módulos a 390px sin desborde', { timeout: 90000 }, async t => {
  const navs = buscarNav(); if (!navs.length) { t.skip('Sin Chrome/Edge local'); return; }
  const procs = new Set(), sockets = new Set(), perfiles = [];
  t.after(() => { for (const w of sockets) try { w.close(); } catch (_) {} for (const p of procs) matar(p); for (const d of perfiles) try { fs.rmSync(d, { recursive: true, force: true, maxRetries: 3, retryDelay: 50 }); } catch (_) {} });
  const py = "import sys; from src.ui.web_server import servidor_local\nwith servidor_local() as u:\n print(u, flush=True); sys.stdin.read()\n";
  const srv = await lanzar('python', ['-u', '-c', py], { cwd: ROOT, stdio: ['pipe', 'pipe', 'pipe'] }, /http:\/\/127\.0\.0\.1:\d+/, 'stdout', procs);
  let nav = null, bloqueo = false, errs = [];
  for (const exe of navs) {
    const p = fs.mkdtempSync(path.join(os.tmpdir(), 'c25-cdp-')); perfiles.push(p);
    const args = ['--headless=new', '--disable-gpu', '--no-sandbox', '--no-first-run', '--no-default-browser-check', '--disable-extensions', '--noerrdialogs', ...(process.platform === 'win32' ? ['--do-not-de-elevate'] : []), '--remote-debugging-port=0', `--user-data-dir=${p}`, 'about:blank'];
    try { nav = await lanzar(exe, args, { stdio: ['ignore', 'pipe', 'pipe'] }, /DevTools listening on ws:\/\/127\.0\.0\.1:(\d+)\//, 'stderr', procs); break; } catch (e) { errs.push(e.message); if (esBloqueo(e)) bloqueo = true; }
  }
  if (!nav) { if (bloqueo) { t.skip(errs.join('\n')); return; } throw new Error(errs.join('\n')); }
  const cdp = await conectarCDP(Number(nav.val), sockets);
  await cdp.send('Page.enable'); await cdp.send('Runtime.enable');
  await cdp.send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
  await cdp.send('Page.navigate', { url: srv.val });
  await cdp.evalJS(`new Promise(r => { (function ok(){ document.querySelectorAll('.exp-trigger').length === 11 ? r(1) : setTimeout(ok, 40); })(); })`);
  const desk = await cdp.evalJS(`(async () => {
    const wait = fn => new Promise((ok, ko) => { const t0 = Date.now(); (function p(){ if (fn()) ok(); else if (Date.now()-t0>12000) ko(new Error('timeout')); else setTimeout(p, 35); })(); });
    const abrir = tab => document.querySelector('.nav-tab[data-tab="'+tab+'"]').click();
    abrir('tab-combinacion'); document.querySelector('#tab-combinacion .btn-primary').click(); await wait(() => document.querySelector('#tab-combinacion .btn-not-toggle'));
    abrir('tab-matrices'); const ms = document.querySelector('#tab-matrices .mini-stepper button').getBoundingClientRect();
    abrir('tab-biseccion'); document.getElementById('bis-form').requestSubmit(); await wait(() => !document.getElementById('bis-graph-controls').hidden);
    const bz = document.getElementById('bis-zoom-in').getBoundingClientRect(), bfCols = getComputedStyle(document.querySelector('#tab-biseccion .bis-fields')).gridTemplateColumns.trim().split(/\\s+/).length;
    abrir('tab-regla-falsa'); document.getElementById('rf-form-funcion').requestSubmit(); await wait(() => document.querySelector('#rf-candidates .rf-candidate'));
    document.querySelector('#rf-candidates .rf-candidate').click(); document.getElementById('rf-form-intervalo').requestSubmit(); await wait(() => !document.getElementById('rf-card-4').hidden); document.getElementById('rf-form-metodo').requestSubmit(); await wait(() => !document.querySelector('#tab-regla-falsa .exp-trigger').disabled);
    abrir('tab-newton-raphson'); document.getElementById('nr-function-form').requestSubmit(); await wait(() => !document.getElementById('nr-card-2').hidden);
    abrir('tab-secante'); document.getElementById('sc-graph-form').requestSubmit(); await wait(() => !document.getElementById('sc-card-2').hidden);
    const sz = document.getElementById('sc-zoom-in').getBoundingClientRect();
    abrir('tab-iterativos'); document.getElementById('it-solve-form').requestSubmit(); await wait(() => !document.querySelector('#tab-iterativos .exp-trigger').disabled);
    return { fine: matchMedia('(pointer: fine)').matches, msW: Math.round(ms.width), msH: Math.round(ms.height), bzW: Math.round(bz.width), bzH: Math.round(bz.height), szW: Math.round(sz.width), bfCols };
  })()`);
  assert.equal(desk.fine, true); assert.ok(desk.msW <= 24 && desk.msH <= 28 && desk.bzW <= 28 && desk.bzH <= 28 && desk.szW <= 36 && desk.bfCols === 2, JSON.stringify(desk));
  await cdp.send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
  await cdp.send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 5 });
  const mov = await cdp.evalJS(`(() => {
    const coarse = matchMedia('(pointer: coarse)').matches, fallos = [];
    const tabs = ['tab-inicio','tab-vectores','tab-combinacion','tab-matrices','tab-inversa','tab-ecuaciones','tab-determinante','tab-biseccion','tab-regla-falsa','tab-newton-raphson','tab-secante','tab-iterativos'];
    document.getElementById('btn-nav-toggle').click();
    for (const b of [document.getElementById('btn-nav-close'), ...document.querySelectorAll('.nav-tab')]) { const r = b.getBoundingClientRect(); if (r.width < 43.5 || r.height < 43.5) fallos.push('sidebar:' + (b.id || b.dataset.tab)); }
    document.getElementById('btn-nav-close').click();
    for (const tab of tabs) {
      document.querySelector('.nav-tab[data-tab="'+tab+'"]').click();
      const sec = document.getElementById(tab), kbBtn = sec.querySelector('.bis-keyboard-toolbar button');
      if (kbBtn && kbBtn.getAttribute('aria-expanded') === 'false') kbBtn.click();
      const ov = document.documentElement.scrollWidth - document.documentElement.clientWidth; if (ov > 0) fallos.push(tab + ':overflow=' + ov);
      for (const b of document.querySelectorAll('header button, #' + tab + ' button')) { const r = b.getBoundingClientRect(); if (r.width > 0 && r.height > 0 && (r.width < 43.5 || r.height < 43.5)) fallos.push(tab + ':' + (b.id || b.className || 'btn') + ':' + r.width.toFixed(1) + 'x' + r.height.toFixed(1)); }
      for (const f of sec.querySelectorAll('.bis-fields')) if (f.getBoundingClientRect().width > 0 && getComputedStyle(f).gridTemplateColumns.trim().split(/\\s+/).length !== 1) fallos.push(tab + ':bis-fields-cols');
    }
    document.querySelector('.nav-tab[data-tab="tab-determinante"]').click(); document.getElementById('det-order-n').value = '8'; document.getElementById('det-order-n').dispatchEvent(new Event('change'));
    const dg = document.getElementById('det-matrix-grid'), dgr = dg.getBoundingClientRect(), dc = dg.querySelector('.cell-input').getBoundingClientRect(), detOv = document.documentElement.scrollWidth - document.documentElement.clientWidth;
    if (detOv > 0 || dgr.right > 390.5 || dg.scrollWidth <= dg.clientWidth || dc.width < 44 || dc.height < 43.5) fallos.push('det-grid');
    document.querySelector('.nav-tab[data-tab="tab-iterativos"]').click();
    const ic = document.querySelector('#it-augmented-grid .it-cell').getBoundingClientRect();
    if (document.documentElement.scrollWidth > document.documentElement.clientWidth || ic.width < 44 || ic.height < 43.5) fallos.push('it-grid');
    return { coarse, fallos };
  })()`);
  assert.equal(mov.coarse, true); assert.deepEqual(mov.fallos, [], `Fallos táctil/móvil:\n${mov.fallos.join('\n')}`);
  assert.equal(cdp.evs.filter(e => e.method === 'Runtime.exceptionThrown').length, 0);
});
