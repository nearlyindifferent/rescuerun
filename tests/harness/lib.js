// Node-side helper: opens an .sb3 in the real Scratch VM + renderer (headless Chromium).
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

async function openGame(sb3Path) {
  const browser = await chromium.launch({
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
  });
  const page = await browser.newPage({ viewport: { width: 480, height: 360 } });
  const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  await page.goto('file://' + path.join(__dirname, 'page.html'));
  const b64 = fs.readFileSync(sb3Path).toString('base64');
  const names = await page.evaluate(b => H.load(b), b64);
  const g = {
    page, browser, errors, names,
    flag: () => page.evaluate(() => H.greenFlag()),
    step: n => page.evaluate(n => H.step(n), n),
    key: (k, down) => page.evaluate(([k, d]) => H.key(k, d), [k, down]),
    hold: async (k, frames) => { await g.key(k, true); await g.step(frames); await g.key(k, false); },
    tap: async k => { await g.key(k, true); await g.step(2); await g.key(k, false); await g.step(1); },
    v: name => page.evaluate(n => H.variable(n), name),
    setV: (name, value) => page.evaluate(([n, v]) => H.setVariable(n, v), [name, value]),
    list: (s, n) => page.evaluate(([s, n]) => H.list(s, n), [s, n]),
    sprite: n => page.evaluate(n => H.sprite(n), n),
    touching: (a, b) => page.evaluate(([a, b]) => H.touching(a, b), [a, b]),
    sounds: () => page.evaluate(() => H.soundLog.slice()),
    threads: () => page.evaluate(() => H.threads()),
    eval: (fn, arg) => page.evaluate(fn, arg),
    shot: async file => {
      const url = await page.evaluate(() => H.snapshot());
      fs.mkdirSync(path.dirname(file), { recursive: true });
      fs.writeFileSync(file, Buffer.from(url.split(',')[1], 'base64'));
      return file;
    },
    close: () => browser.close(),
  };
  return g;
}
module.exports = { openGame };
