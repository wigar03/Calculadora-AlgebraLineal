/* Prueba en navegador real (CDP sobre Chrome/Edge): 11 módulos, impresión, móvil 390 px y offline. */
const { test } = require('node:test'); const assert = require('node:assert/strict');
const fs = require('node:fs'), os = require('node:os'), path = require('node:path');
const { spawn } = require('node:child_process');
const ROOT = path.resolve(__dirname, '..');
const buscarNavegador = () => ['C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', 'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe', '/usr/bin/google-chrome', '/usr/bin/chromium'].find(p => fs.existsSync(p)) || null;
const lanzar = (cmd, args, opts, regex, stream) => new Promise((res, rej) => {
  const proc = spawn(cmd, args, opts); let buf = '';
  proc[stream].on('data', d => { buf += d; const m = buf.match(regex); if (m) res({ val: m[1] || m[0], proc }); });
  proc.on('error', rej);
});
async function conectarCDP(port) {
  const pags = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const ws = new WebSocket(pags.find(p => p.type === 'page').webSocketDebuggerUrl);
  await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
  let seq = 0; const pend = new Map(), eventos = [];
  ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && pend.has(m.id)) { const [ok, ko] = pend.get(m.id); pend.delete(m.id); m.error ? ko(new Error(m.error.message)) : ok(m.result); } else eventos.push(m); };
  const send = (method, params = {}) => new Promise((ok, ko) => { const id = ++seq; pend.set(id, [ok, ko]); ws.send(JSON.stringify({ id, method, params })); });
  const evalJS = async expr => { const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true }); if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text); return r.result.value; };
  return { ws, send, evalJS, eventos };
}

test('navegador real: 11 módulos calculan y exportan, impresión emulada, móvil 390 px y offline', { timeout: 90000 }, async t => {
  const exe = buscarNavegador();
  if (!exe) { t.skip('No se encontró Chrome/Edge local'); return; }
  const perfil = fs.mkdtempSync(path.join(os.tmpdir(), 'p2-cdp-'));
  const py = "import sys; from src.ui.web_server import servidor_local\nwith servidor_local() as u:\n print(u, flush=True); sys.stdin.read()\n";
  const srv = await lanzar('python', ['-u', '-c', py], { cwd: ROOT, stdio: ['pipe', 'pipe', 'pipe'] }, /http:\/\/127\.0\.0\.1:\d+/, 'stdout');
  const nav = await lanzar(exe, ['--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--remote-debugging-port=0', `--user-data-dir=${perfil}`, 'about:blank'], { stdio: ['ignore', 'pipe', 'pipe'] }, /DevTools listening on ws:\/\/127\.0\.0\.1:(\d+)\//, 'stderr');
  const capDir = process.env.P2_CAPTURAS ? path.join(ROOT, 'docs', 'validacion', 'p2-ui') : null;
  if (capDir) fs.mkdirSync(capDir, { recursive: true });
  try {
    const cdp = await conectarCDP(Number(nav.val));
    await cdp.send('Page.enable'); await cdp.send('Runtime.enable'); await cdp.send('Network.enable');
    await cdp.send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
    await cdp.send('Page.navigate', { url: srv.val });
    await cdp.evalJS(`new Promise(r => { (function ok(){ document.querySelectorAll('.exp-trigger').length === 11 ? r(1) : setTimeout(ok, 40); })(); })`);
    assert.equal(await cdp.evalJS(`document.getElementById('header-subtitle').textContent.trim()`), 'Álgebra lineal y métodos numéricos con procedimientos paso a paso');
    await cdp.evalJS(`window.__cap = {}; navigator.clipboard.writeText = async t => { window.__cap.latex = t; };
      const orig = URL.createObjectURL.bind(URL);
      URL.createObjectURL = b => { b.arrayBuffer().then(buf => { const u = new Uint8Array(buf); window.__cap.bom = u[0]===0xEF && u[1]===0xBB && u[2]===0xBF; window.__cap.csv = new TextDecoder('utf-8',{ignoreBOM:true}).decode(u); }); return orig(b); };
      HTMLAnchorElement.prototype.click = function() { if (this.download) window.__cap.file = this.download; };`);
    const casos = [
      ['tab-vectores', `sec.querySelector('.btn-primary').click();`, false],
      ['tab-combinacion', `sec.querySelector('.btn-primary').click();`, false],
      ['tab-matrices', `sec.querySelector('button[onclick*="multiplicacion"]').click();`, false],
      ['tab-inversa', `sec.querySelector('.btn-primary').click();`, false],
      ['tab-ecuaciones', `sec.querySelector('.btn-primary').click();`, false],
      ['tab-determinante', `sec.querySelector('.btn-primary').click();`, false],
      ['tab-biseccion', `document.getElementById('bis-form').requestSubmit();`, true],
      ['tab-regla-falsa', `document.getElementById('rf-form-funcion').requestSubmit(); await wait(() => document.querySelector('#rf-candidates .rf-candidate')); document.querySelector('#rf-candidates .rf-candidate').click(); document.getElementById('rf-form-intervalo').requestSubmit(); await wait(() => !document.getElementById('rf-card-4').hidden); document.getElementById('rf-form-metodo').requestSubmit();`, true],
      ['tab-newton-raphson', `document.getElementById('nr-function-form').requestSubmit(); await wait(() => !document.getElementById('nr-card-2').hidden); document.getElementById('nr-x0').value='1.5'; document.getElementById('nr-initial-form').requestSubmit(); await wait(() => !document.getElementById('nr-card-4').hidden); document.getElementById('nr-solve-form').requestSubmit();`, true],
      ['tab-secante', `document.getElementById('sc-graph-form').requestSubmit(); await wait(() => !document.getElementById('sc-card-2').hidden); document.getElementById('sc-x0').value='1'; document.getElementById('sc-x1').value='2'; document.getElementById('sc-initial-form').requestSubmit(); await wait(() => !document.getElementById('sc-card-4').hidden); document.getElementById('sc-solve-form').requestSubmit();`, true],
      ['tab-iterativos', `document.querySelector('input[name="it-method"][value="comparar"]').checked=true; document.getElementById('it-solve-form').requestSubmit();`, true],
    ];
    for (const [tab, accion, conCSV] of casos) {
      const r = await cdp.evalJS(`(async () => {
        const wait = fn => new Promise((ok, ko) => { const t0 = Date.now(); (function p(){ if (fn()) ok(); else if (Date.now()-t0>12000) ko(new Error('timeout ${tab}')); else setTimeout(p, 35); })(); });
        document.querySelector('.nav-tab[data-tab="${tab}"]').click();
        const sec = document.getElementById('${tab}'), trig = sec.querySelector('.exp-trigger');
        if (!trig.disabled) throw new Error('Debe iniciar deshabilitado en ${tab}');
        ${accion}
        await wait(() => !trig.disabled);
        window.__cap = { latex: null, csv: null, bom: false, file: null }; trig.click();
        const csvBtn = sec.querySelector('[data-exp-action="csv"]');
        if (csvBtn.hidden !== ${!conCSV}) throw new Error('CSV inesperado en ${tab}');
        sec.querySelector('[data-exp-action="latex"]').click();
        await wait(() => window.__cap.latex && sec.querySelector('.exp-status').textContent === 'Copiado');
        if (${conCSV}) { trig.click(); csvBtn.click(); await wait(() => window.__cap.csv !== null); }
        return { ...window.__cap, okLatex: window.__cap.latex.includes('\\\\usepackage[spanish]{babel}') && window.__cap.latex.includes('\\\\end{document}') };
      })()`);
      assert.ok(r.okLatex, `LaTeX incompleto en ${tab}`);
      if (conCSV) assert.ok(r.bom && r.csv.includes(';') && r.csv.includes('\r\n') && r.file.endsWith('.csv'), `CSV inválido en ${tab}`);
    }
    if (capDir) { await cdp.evalJS(`window.scrollTo(0,0); document.getElementById('notification-toast').classList.add('hidden'); document.querySelector('#tab-iterativos .exp-trigger').click();`); fs.writeFileSync(path.join(capDir, 'escritorio-menu.png'), Buffer.from((await cdp.send('Page.captureScreenshot', { format: 'png' })).data, 'base64')); await cdp.evalJS(`document.querySelector('#tab-iterativos .exp-trigger').click();`); }
    await cdp.send('Emulation.setEmulatedMedia', { media: 'print' });
    const imp = await cdp.evalJS(`(window.scrollTo(0,0), { side: getComputedStyle(document.getElementById('module-sidebar')).display, exp: getComputedStyle(document.querySelector('#tab-iterativos .exp-control')).display, activas: [...document.querySelectorAll('.tab-pane')].filter(x => getComputedStyle(x).display !== 'none').map(x => x.id), thead: getComputedStyle(document.querySelector('#tab-iterativos thead')).display, trBreak: getComputedStyle(document.querySelector('#tab-iterativos tbody tr')).breakInside })`);
    assert.equal(imp.side, 'none'); assert.equal(imp.exp, 'none'); assert.deepEqual(imp.activas, ['tab-iterativos']); assert.equal(imp.thead, 'table-header-group'); assert.equal(imp.trBreak, 'avoid');
    if (capDir) fs.writeFileSync(path.join(capDir, 'impresion-emulada.png'), Buffer.from((await cdp.send('Page.captureScreenshot', { format: 'png' })).data, 'base64'));
    await cdp.send('Emulation.setEmulatedMedia', { media: 'screen' });
    await cdp.send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
    const mov = await cdp.evalJS(`(() => { window.scrollTo(0,0); const sec = document.getElementById('tab-iterativos'), t = sec.querySelector('.exp-trigger'); t.click(); const rt = t.getBoundingClientRect(), ri = sec.querySelector('.bis-intro').getBoundingClientRect(), items = [...sec.querySelectorAll('.exp-item')].filter(b => !b.hidden).map(b => b.getBoundingClientRect().height); return { overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth, tw: rt.width, th: rt.height, bajo: rt.top >= ri.bottom - 2, minItem: Math.min(...items) }; })()`);
    assert.ok(mov.overflow <= 0 && mov.th >= 44 && mov.tw >= 300 && mov.bajo && mov.minItem >= 44, JSON.stringify(mov));
    if (capDir) fs.writeFileSync(path.join(capDir, 'movil-390-menu.png'), Buffer.from((await cdp.send('Page.captureScreenshot', { format: 'png' })).data, 'base64'));
    assert.deepEqual(cdp.eventos.filter(e => e.method === 'Network.requestWillBeSent').map(e => e.params.request.url).filter(u => !u.startsWith(srv.val) && !u.startsWith('data:') && !u.startsWith('blob:') && u !== 'about:blank'), []);
    assert.equal(cdp.eventos.filter(e => e.method === 'Runtime.exceptionThrown').length, 0);
    cdp.ws.close();
  } finally {
    try { nav.proc.kill(); } catch (_) {} try { srv.proc.stdin.end(); srv.proc.kill(); } catch (_) {}
    try { fs.rmSync(perfil, { recursive: true, force: true }); } catch (_) {}
  }
});
