// Contact sheet of costume SVGs rendered by Chromium:  node preview.js out.png "glob-prefix" [cellW cellH bg]
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
(async () => {
  const [out, prefix, cw = '110', ch = '110', bg = '#9ed8ff'] = process.argv.slice(2);
  const dir = path.join(__dirname, 'out', 'art');
  const files = fs.readdirSync(dir).filter(f => f.startsWith(prefix) && f.endsWith('.svg')).sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
  const cells = files.map(f => `<div style="display:inline-block;margin:4px;text-align:center;font:10px sans-serif;color:#123"><div style="width:${cw}px;height:${ch}px;background:${bg};display:flex;align-items:center;justify-content:center"><img src="file://${path.join(dir, f)}" style="max-width:${cw}px;max-height:${ch}px"></div>${f.split('__')[1].replace('.svg', '')}</div>`).join('');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1000, height: 200 } });
  const html = path.join(__dirname, 'out', 'preview.html'); fs.writeFileSync(html, `<body style="margin:6px;background:#f4f4f4;width:990px">${cells}</body>`); await p.goto('file://' + html);
  await p.waitForTimeout(300);
  await p.screenshot({ path: out, fullPage: true });
  await b.close(); console.log('wrote', out, files.length, 'costumes');
})();
