// A bot that plays Rescue Runner like a person: it only reads on-screen state and presses keys.
// Platform graph + the jump recipes were proven in the L2 "platform ladder" tests.
const SURF = {                                   // name: [left, right, top]  (filled in from layout.json)
};
function makeBot(g, LAYOUT) {
  const P = {}; P.S0 = [-225, 225, LAYOUT.GROUND_Y];
  const nameMap = { 'Left balcony': 'LB', 'Right balcony': 'RB', 'Middle roof': 'MR', 'Upper left': 'UL', 'Upper right': 'UR' };
  for (const [n, l, r, t] of LAYOUT.PLATFORMS) P[nameMap[n]] = [l, r, t];
  const R = LAYOUT.FEET_REACH;
  // hop recipes: {stand: x to stand at, dir: key to hold, frames: how long, jump: bool}  or {off: 'left'|'right', carry: bool}
  const HOPS = {
    'S0>LB': { stand: -170, jump: true, dir: null, frames: 1 },
    'S0>RB': { stand: 170, jump: true, dir: null, frames: 1 },
    'LB>MR': { stand: -125, jump: true, dir: 'ArrowRight', frames: 21 },
    'RB>MR': { stand: 120, jump: true, dir: 'ArrowLeft', frames: 21 },
    'MR>UL': { stand: -55, jump: true, dir: 'ArrowLeft', frames: 14 },
    'MR>UR': { stand: 35, jump: true, dir: 'ArrowRight', frames: 14 },
    'UL>MR': { off: 'right', carry: true }, 'UR>MR': { off: 'left', carry: true },
    'UL>LB': { off: 'right', carry: false }, 'UR>RB': { off: 'right', carry: false },
    'MR>LB': { off: 'left', carry: true }, 'MR>RB': { off: 'right', carry: true },
    'LB>S0': { off: 'right', carry: false }, 'RB>S0': { off: 'left', carry: false },
    'MR>S0': { off: 'right', carry: false },
  };
  const adj = {}; for (const k of Object.keys(HOPS)) { const [a, b] = k.split('>'); (adj[a] = adj[a] || []).push(b); }
  function path(from, to) {                      // BFS over surfaces
    const prev = { [from]: null }; const q = [from];
    while (q.length) { const c = q.shift(); if (c === to) break; for (const n of adj[c] || []) if (!(n in prev)) { prev[n] = c; q.push(n); } }
    if (!(to in prev)) return null; const out = []; for (let c = to; prev[c] !== null; c = prev[c]) out.unshift(c); return out;
  }
  const surfaceAt = (x, y) => { let best = null; for (const [n, [l, r, t]] of Object.entries(P)) if (Math.abs(y - t) < 0.5 && x >= l - R && x <= r + R) { if (best === null || t > P[best][2]) best = n; } return best; };
  const surfaceForY = y => { for (const [n, [l, r, t]] of Object.entries(P)) if (Math.abs(y - LAYOUT.HOVER - t) < 0.5) return n; return null; };
  const run = async () => g.sprite('Rescue Runner');
  const grounded = () => g.eval(() => { const t = vm.runtime.targets.find(t => t.getName() === 'Rescue Runner'); for (const id in t.variables) if (t.variables[id].name === 'On Ground') return Number(t.variables[id].value) === 1; return false; });

  async function walkX(x, tol = 4) {
    for (let i = 0; i < 120; i++) {
      const r = await run(); const d = x - r.x; if (Math.abs(d) <= tol) return;
      const k = d > 0 ? 'ArrowRight' : 'ArrowLeft'; await g.key(k, true); await g.step(1); await g.key(k, false);
    }
  }
  async function doHop(key) {
    const h = HOPS[key];
    const r0 = await run(); if (process.env.BOT_DEBUG) console.log('  hop', key, 'from', r0.x, r0.y);
    if (h.stand !== undefined) {
      await walkX(h.stand, 3);
      if (h.dir) await g.key(h.dir, true);
      await g.key(' ', true); await g.step(1); await g.key(' ', false);
      await g.step(h.frames - 1); if (h.dir) await g.key(h.dir, false);
      for (let i = 0; i < 80; i++) { await g.step(1); if (await grounded()) break; }
    } else {
      const [A] = key.split('>'); const [l, r2] = P[A]; const dirKey = h.off === 'right' ? 'ArrowRight' : 'ArrowLeft';
      const edgeX = h.off === 'right' ? r2 + R + 2 : l - R - 2;
      await g.key(dirKey, true);
      for (let i = 0; i < 80; i++) { await g.step(1); const r = await run(); if (r.y < P[A][2] - 1) break; if (h.off === 'right' ? r.x > edgeX : r.x < edgeX) { /* keep walking until we drop */ } }
      if (!h.carry) await g.key(dirKey, false);
      for (let i = 0; i < 80; i++) { await g.step(1); if (await grounded()) break; }
      if (h.carry) await g.key(dirKey, false);
    }
  }
  async function play(maxFrames) {              // returns {state, frames, collected}
    let frames = 0; const t0 = await g.step(0);
    const stepCount = async n => { await g.step(n); };
    while (true) {
      const st = await g.v('Game State'); if (st !== 'playing') return st;
      const sup = await g.sprite('Emergency Supply');
      if (!sup.visible || sup.ghost > 5 || !sup.costume.startsWith('supply')) { await g.step(1); continue; }
      const r = await run(); const cur = surfaceAt(r.x, r.y); const target = surfaceForY(sup.y - Math.sin(0) );
      const tSurf = (() => { let b = null, bd = 1e9; for (const [n, [l, rr, t]] of Object.entries(P)) { const d = Math.abs(sup.y - 4 - (t + LAYOUT.HOVER)); const inR = sup.x >= l - 10 && sup.x <= rr + 10; if (inR && d < bd) { bd = d; b = n; } } return b; })();
      if (cur === null || !(await grounded())) { await g.step(1); continue; }
      if (cur === tSurf) {                       // same surface: walk into the supply
        const before = Number(await g.v('Score'));
        for (let i = 0; i < 90; i++) {
          const rr = await run(); const d = sup.x - rr.x;
          if (Math.abs(d) > 6) { const k = d > 0 ? 'ArrowRight' : 'ArrowLeft'; await g.key(k, true); await g.step(1); await g.key(k, false); } else await g.step(1);
          if (Number(await g.v('Score')) !== before || (await g.v('Game State')) !== 'playing') break;
        }
      } else {
        const p = path(cur, tSurf); if (!p) { await g.step(1); continue; }
        await doHop(cur + '>' + p[0]);
        if (process.env.BOT_DEBUG) { const r1 = await run(); console.log('    -> landed', r1.x, r1.y, 'surface', surfaceAt(r1.x, r1.y), 'target', tSurf); }
      }
    }
  }
  return { play, path, surfaceAt };
}
module.exports = { makeBot };
