// Runs every test against the real Scratch VM.  Usage: node run_tests.js [sb3] [name-filter]
const path = require('path');
const { openGame } = require('./harness/lib');
const SB3 = path.resolve(process.argv[2] && !process.argv[2].startsWith('-') ? process.argv[2] : path.join(__dirname, '..', 'Rescue_Runner.sb3'));
const FILTER = process.argv[3] || '';

const fs = require('fs');
const LAYOUT = JSON.parse(fs.readFileSync(path.join(__dirname, 'out', 'layout.json')));
const GROUND = LAYOUT.GROUND_Y;
const SPOTS = LAYOUT.SPOTS;
const tests = [];
const test = (name, fn) => tests.push({ name, fn });
const assert = (cond, msg) => { if (!cond) throw new Error('ASSERT: ' + msg); };
const near = (a, b, tol, msg) => assert(Math.abs(a - b) <= tol, `${msg} (got ${a}, expected ${b} ±${tol})`);

async function begin(g) {            // green flag, then press SPACE on the title screen
  await g.flag(); await g.step(4);
  await g.tap(' '); await g.step(4);
}

async function teleport(g, x, y) {
  await g.eval(([x, y]) => vm.runtime.targets.find(t => t.getName() === 'Rescue Runner').setXY(x, y), [x, y]);
}
async function waitForSupply(g, maxFrames = 60) {          // step until the supply is visible and finished popping in
  for (let i = 0; i < maxFrames; i++) { const s = await g.sprite('Emergency Supply'); if (s.visible && s.ghost === 0 && s.costume.startsWith('supply')) return s; await g.step(1); }
  throw new Error('supply never appeared');
}
async function collectCurrent(g) {                          // stand on the supply and wait for the score to change
  const s = await waitForSupply(g); const before = await g.v('Score');
  await teleport(g, s.x, s.y - LAYOUT.HOVER);
  for (let i = 0; i < 6; i++) { await g.step(1); if ((await g.v('Score')) !== before) break; }
  return s;
}
const isSpot = (x, y) => SPOTS.some(([sx, sy]) => Math.abs(sx - x) < 0.5 && Math.abs(sy - y) < 5);
async function walkTo(g, x, tol = 3) {        // hold an arrow key until the runner is within tol of x
  for (let i = 0; i < 400; i++) {
    const r = await g.sprite('Rescue Runner'); const d = x - r.x;
    if (Math.abs(d) <= tol) break;
    const k = d > 0 ? 'ArrowRight' : 'ArrowLeft';
    await g.key(k, true); await g.step(1); await g.key(k, false);
  }
  await g.step(1);
}
async function settle(g, maxFrames = 120) {     // step until the runner stops moving vertically
  let last = null, still = 0;
  for (let i = 0; i < maxFrames && still < 4; i++) {
    await g.step(1); const y = (await g.sprite('Rescue Runner')).y;
    still = (y === last) ? still + 1 : 0; last = y;
  }
  return g.sprite('Rescue Runner');
}
async function jump(g, dir, rightFrames) {      // jump while holding a direction for N frames
  if (dir) await g.key(dir, true);
  await g.key(' ', true); await g.step(1); await g.key(' ', false);
  await g.step(rightFrames - 1);
  if (dir) await g.key(dir, false);
  return settle(g);
}

// ------------------------------------------------------------------ Loop 1
test('L1 four sprites + stage, variables and broadcasts exist', async g => {
  assert(JSON.stringify(g.names) === JSON.stringify(['Stage', 'Rescue Runner', 'Emergency Supply', 'Rising Water', 'Game Controller']), 'sprite list ' + g.names);
  for (const v of ['Score', 'Water Level', 'Game State', 'Vertical Speed']) assert((await g.v(v)) !== undefined, 'variable ' + v);
});
test('L1 title screen shows until SPACE, then game starts', async g => {
  await g.flag(); await g.step(4);
  assert((await g.v('Game State')) === 'title', 'state is title');
  const c = await g.sprite('Game Controller'); assert(c.visible && c.costume === 'title', 'title card visible');
  await g.step(30); assert((await g.v('Game State')) === 'title', 'still title with no key');
  await g.tap(' '); await g.step(3);
  assert((await g.v('Game State')) === 'playing', 'playing after SPACE');
});

// ------------------------------------------------------------------ Loop 2
test('L2 runner starts on the street, feet at ground level', async g => {
  await begin(g);
  const r = await g.sprite('Rescue Runner');
  assert(r.visible, 'visible'); near(r.y, GROUND, 0.01, 'y'); near(r.x, -10, 0.01, 'x');
});
test('L2 right/left arrows move at walking speed and face the right way', async g => {
  await begin(g);
  const x0 = (await g.sprite('Rescue Runner')).x;
  await g.hold('ArrowRight', 20); await g.step(1);
  let r = await g.sprite('Rescue Runner');
  near(r.x - x0, 100, 0.01, 'moved 5px x 20 frames'); assert(r.direction === 90, 'faces right');
  await g.hold('ArrowLeft', 10); await g.step(1);
  r = await g.sprite('Rescue Runner');
  near(r.x, x0 + 50, 0.01, 'moved back'); assert(r.direction === -90, 'faces left');
});
test('L2 walk animation cycles through 6 frames; idle when stopped', async g => {
  await begin(g);
  await g.key('ArrowRight', true);
  const seen = new Set();
  for (let i = 0; i < 24; i++) { await g.step(1); seen.add((await g.sprite('Rescue Runner')).costume); }
  await g.key('ArrowRight', false); await g.step(2);
  for (let i = 1; i <= 6; i++) assert(seen.has('walk ' + i), 'saw walk ' + i + ' in ' + [...seen]);
  assert((await g.sprite('Rescue Runner')).costume === 'idle', 'idle when stopped');
});
test('L2 runner cannot leave the screen sideways', async g => {
  await begin(g);
  await g.hold('ArrowLeft', 120); await g.step(1); near((await g.sprite('Rescue Runner')).x, -225, 0.01, 'left edge');
  await g.hold('ArrowRight', 200); await g.step(1); near((await g.sprite('Rescue Runner')).x, 225, 0.01, 'right edge');
});
test('L2 holding both arrows does not drift', async g => {
  await begin(g);
  const x0 = (await g.sprite('Rescue Runner')).x;
  await g.key('ArrowLeft', true); await g.key('ArrowRight', true); await g.step(30);
  await g.key('ArrowLeft', false); await g.key('ArrowRight', false);
  near((await g.sprite('Rescue Runner')).x, x0, 0.01, 'x unchanged');
});
test('L2 jump: rises ~91px, comes back to exactly ground level, jump/fall costumes', async g => {
  await begin(g);
  await g.key(' ', true); let peak = -999; const costumes = new Set(); let minY = 999;
  for (let i = 0; i < 60; i++) {
    await g.step(1); const r = await g.sprite('Rescue Runner');
    peak = Math.max(peak, r.y); minY = Math.min(minY, r.y); costumes.add(r.costume);
    if (i === 3) await g.key(' ', false);
  }
  near(peak - GROUND, 91 + 14, 14, 'jump height range'); assert(minY >= GROUND - 0.001, 'never below ground: ' + minY);
  const r = await g.sprite('Rescue Runner'); near(r.y, GROUND, 0.001, 'back on ground');
  assert(costumes.has('jump') && costumes.has('fall'), 'jump and fall costumes: ' + [...costumes]);
});
test('L2 cannot double-jump in mid-air', async g => {
  await begin(g);
  await g.key(' ', false); await g.tap(' ');
  let peak = -999;
  for (let i = 0; i < 4; i++) { await g.step(1); }
  await g.hold(' ', 5);              // keep pressing in the air
  for (let i = 0; i < 40; i++) { await g.step(1); peak = Math.max(peak, (await g.sprite('Rescue Runner')).y); }
  assert(peak - GROUND < 100, 'single jump height only, got ' + (peak - GROUND));
});
test('L2 lands on the left balcony, walks off its edge and drops back to the street', async g => {
  await begin(g); await walkTo(g, -170);            // balcony spans -228..-118 at y=-45
  let r = await jump(g, null, 1); near(r.y, -45, 0.001, 'standing on balcony');
  await g.hold('ArrowRight', 30); r = await settle(g);
  near(r.y, GROUND, 0.001, 'dropped to street after leaving balcony'); assert(r.x > -118, 'x past edge: ' + r.x);
});
test('L2 platform ladder: street -> balcony -> middle roof -> upper-left platform', async g => {
  await begin(g); await walkTo(g, -170);
  let r = await jump(g, null, 1); near(r.y, -45, 0.001, 'on balcony');
  await walkTo(g, -125);
  r = await jump(g, 'ArrowRight', 21); near(r.y, 25, 0.001, 'on middle roof, x=' + r.x);         // roof spans -72..42
  await walkTo(g, -55);
  r = await jump(g, 'ArrowLeft', 14); near(r.y, 95, 0.001, 'on upper-left platform, x=' + r.x);    // spans -232..-132
});
test('L2 every platform can be reached by jumping (street -> right balcony -> roof -> upper right)', async g => {
  await begin(g); await walkTo(g, 170);
  let r = await jump(g, null, 1); near(r.y, -45, 0.001, 'on right balcony');
  await walkTo(g, 120);
  r = await jump(g, 'ArrowLeft', 21); near(r.y, 25, 0.001, 'on middle roof from the right, x=' + r.x);
  await walkTo(g, 35);
  r = await jump(g, 'ArrowRight', 14); near(r.y, 95, 0.001, 'on upper-right platform, x=' + r.x);   // spans 98..192
});
test('L2 jumping up through a platform from below does not snap onto it', async g => {
  await begin(g);
  await walkTo(g, -140);                  // under the left balcony
  await g.key(' ', true); await g.step(3); await g.key(' ', false);
  let maxy = -999; let ysAfterRise = [];
  for (let i = 0; i < 12; i++) { await g.step(1); const r = await g.sprite('Rescue Runner'); maxy = Math.max(maxy, r.y); }
  assert(maxy > GROUND + 40, 'rose through (no instant snap): ' + maxy);
});
test('L2 fuzz: 4000 frames of random keys - never falls through the street, never leaves the screen', async g => {
  await begin(g);
  let seed = 12345; const rnd = () => (seed = (seed * 1664525 + 1013904223) % 4294967296) / 4294967296;
  const keys = ['ArrowLeft', 'ArrowRight', ' ']; const down = {};
  let minY = 999, minX = 999, maxX = -999, landings = new Set();
  for (let i = 0; i < 4000; i++) {
    if (i % 7 === 0) { const k = keys[Math.floor(rnd() * 3)]; down[k] = !down[k]; await g.key(k, down[k]); }
    await g.step(1);
    const r = await g.sprite('Rescue Runner');
    minY = Math.min(minY, r.y); minX = Math.min(minX, r.x); maxX = Math.max(maxX, r.x);
    assert(Number.isFinite(r.x) && Number.isFinite(r.y), 'finite position');
  }
  assert(minY >= GROUND - 0.001, 'never below street: ' + minY);
  assert(minX >= -225.001 && maxX <= 225.001, `x in range ${minX}..${maxX}`);
});
test('L2 wading: slower when feet are under the water level', async g => {
  await begin(g);
  await g.setV('Water Level', -50);
  const x0 = (await g.sprite('Rescue Runner')).x;
  await g.hold('ArrowRight', 10); await g.step(1);
  near((await g.sprite('Rescue Runner')).x - x0, 30, 0.01, 'wading speed 3 x 10');
});
test('L2 when Game State is not "playing" the runner stops responding', async g => {
  await begin(g);
  await g.setV('Game State', 'lost'); await g.step(2);
  const x0 = (await g.sprite('Rescue Runner')).x;
  await g.hold('ArrowRight', 10); await g.step(2);
  near((await g.sprite('Rescue Runner')).x, x0, 0.01, 'frozen');
});

// ---- tests added by later loops live below (appended by each loop) ----
// ------------------------------------------------------------------ Loop 3
test('L3 spots: every supply spot sits on the street or on a platform the runner can stand on', async g => {
  const surfaces = [{ l: -240, r: 240, top: GROUND }, ...LAYOUT.PLATFORMS.map(p => ({ l: p[1], r: p[2], top: p[3] }))];
  for (const [x, y] of SPOTS) {
    const ok = surfaces.some(s => x >= s.l + 10 && x <= s.r - 10 && Math.abs(y - (s.top + LAYOUT.HOVER)) < 0.01);
    assert(ok, `spot (${x},${y}) is not above a surface`);
  }
  const lx = await g.list('Emergency Supply', 'Spot X'); const ly = await g.list('Emergency Supply', 'Spot Y');
  assert(lx.length === SPOTS.length && ly.length === SPOTS.length, 'lists have all spots');
});
test('L3 after start: score 0, scoreboard shows 0, one supply appears at a valid spot behind the runner', async g => {
  await begin(g); const s = await waitForSupply(g);
  assert(Number(await g.v('Score')) === 0, 'score 0'); assert(isSpot(s.x, s.y), `valid spot ${s.x},${s.y}`);
  assert((await g.sprite('Game Controller')).costume === 'Score 0', 'HUD Score 0');
  assert((await g.sprite('Emergency Supply')).layer < (await g.sprite('Rescue Runner')).layer, 'supply drawn behind the runner');
});
test('L3 supply floats (y changes) and its glow costumes cycle', async g => {
  await begin(g); await waitForSupply(g);
  const ys = new Set(), cs = new Set();
  for (let i = 0; i < 30; i++) { await g.step(1); const s = await g.sprite('Emergency Supply'); ys.add(s.y); cs.add(s.costume); }
  assert(ys.size > 8, 'bobbing: ' + ys.size + ' distinct y'); assert(cs.size === 4, 'glow frames: ' + [...cs]);
});
test('L3 touching the supply: score +1 exactly once, HUD updates, starburst, supply moves elsewhere', async g => {
  await begin(g); const s0 = await collectCurrent(g);
  assert(await g.v('Score') === 1, 'score 1');
  assert((await g.sprite('Game Controller')).costume === 'Score 1', 'HUD Score 1');
  const seen = new Set();
  for (let i = 0; i < 10; i++) { await g.step(1); seen.add((await g.sprite('Emergency Supply')).costume); }
  assert(seen.has('burst'), 'burst animation: ' + [...seen]);
  const s1 = await waitForSupply(g);
  assert(!(Math.abs(s1.x - s0.x) < 1 && Math.abs(s1.y - s0.y) < 8), 'new supply at a different spot');
  await g.step(60); assert(await g.v('Score') === 1, 'still 1 after waiting around (no double counting)');
});
test('L3 collecting 10 supplies: score counts 1..10 and then stops at 10', async g => {
  await begin(g);
  for (let n = 1; n <= 10; n++) {
    await collectCurrent(g); assert(await g.v('Score') === n, `score ${n}, got ${await g.v('Score')}`);
    await g.step(12);
  }
  assert((await g.sprite('Game Controller')).costume === 'Score 10' || (await g.sprite('Game Controller')).costume === 'win', 'HUD shows 10');
  await g.step(150); assert(await g.v('Score') === 10, 'score stays 10');
});
test('L3 spawns: 60 respawns always use valid spots, never repeat, never appear on top of the runner', async g => {
  await begin(g); let last = null;
  for (let n = 0; n < 60; n++) {
    const s = await collectCurrent(g); await g.setV('Score', 0); await g.step(14);
    const nx = await waitForSupply(g);
    assert(isSpot(nx.x, nx.y), `valid spot ${nx.x},${nx.y}`);
    assert(!(Math.abs(nx.x - s.x) < 1 && Math.abs(nx.y - s.y) < 8), 'no immediate repeat');
    const r = await g.sprite('Rescue Runner');
    assert(!(Math.abs(nx.x - r.x) < 70 && nx.y - r.y > LAYOUT.REACH_BELOW + 3 && nx.y - r.y < LAYOUT.REACH_ABOVE - 3), `not within reach of the runner (${nx.x},${nx.y}) vs (${r.x},${r.y})`);
  }
});
test('L3 supply positions are spread across the whole map over many spawns', async g => {
  await begin(g); const used = new Set();
  for (let n = 0; n < 60; n++) { const s = await collectCurrent(g); used.add(s.x + ',' + s.y); await g.setV('Score', 0); await g.step(14); }
  assert(used.size >= 8, 'variety: only ' + used.size + ' of 9 spots used');
});

// ------------------------------------------------------------------ Loop 4
test('L4 title screen: water waits at the bottom and does not rise yet', async g => {
  await g.flag(); await g.step(90);
  const w = await g.sprite('Rising Water'); near(w.y, LAYOUT.WATER_START, 0.001, 'water y'); assert(w.visible, 'water visible');
  near(Number(await g.v('Water Level')), LAYOUT.WATER_START, 0.001, 'Water Level');
});
test('L4 water rises smoothly: constant rate per frame (no jitter), sprite follows Water Level', async g => {
  await begin(g); await g.step(2);
  let prev = Number(await g.v('Water Level')); const deltas = [];
  for (let i = 0; i < 90; i++) {
    await g.step(1); const lvl = Number(await g.v('Water Level')); deltas.push(lvl - prev); prev = lvl;
    const w = await g.sprite('Rising Water'); if (i % 15 === 0) near(w.y, lvl, 0.01, 'sprite y follows level');
  }
  const mn = Math.min(...deltas), mx = Math.max(...deltas);
  near(mn, LAYOUT.WATER_RATE, 1e-6, 'min step'); near(mx, LAYOUT.WATER_RATE, 1e-6, 'max step (no jitter)');
});
test('L4 wave animation cycles through all 6 costumes', async g => {
  await begin(g); const seen = new Set();
  for (let i = 0; i < 40; i++) { await g.step(1); seen.add((await g.sprite('Rising Water')).costume); }
  assert(seen.size === 6, 'wave costumes seen: ' + [...seen]);
});
test('L4 water gets darker as it rises (danger cue)', async g => {
  await begin(g); await g.step(3); const b0 = (await g.sprite('Rising Water')).brightness;
  await g.setV('Water Level', 0); await g.step(3); const b1 = (await g.sprite('Rising Water')).brightness;
  await g.setV('Water Level', 150); await g.step(3); const b2 = (await g.sprite('Rising Water')).brightness;
  assert(b0 > b1 && b1 > b2, `brightness ${b0} > ${b1} > ${b2}`); assert(b2 < -20 && b2 >= -25.5, 'near -25 at the top: ' + b2);
});
test('L4 flood timeline: ~125 s to reach the top, then exactly one Game Lost and the water stops', async g => {
  await begin(g);
  const startFrame = (await g.broadcasts()).filter(b => b.name === 'Start Game').pop().frame;
  let lostFrame = null;
  for (let i = 0; i < 4400 && lostFrame === null; i += 10) {
    await g.step(10);
    const lost = (await g.broadcasts()).filter(b => b.name === 'Game Lost'); if (lost.length) lostFrame = lost[0].frame;
  }
  assert(lostFrame !== null, 'water never reached the top');
  const secs = (lostFrame - startFrame) / 30; assert(secs > 118 && secs < 133, 'time to flood: ' + secs.toFixed(1) + ' s');
  await g.step(120);
  assert((await g.broadcasts()).filter(b => b.name === 'Game Lost').length === 1, 'Game Lost sent exactly once');
  const lvl = Number(await g.v('Water Level')); assert(lvl > LAYOUT.WATER_TOP && lvl < LAYOUT.WATER_TOP + 1, 'water stopped at the top: ' + lvl);
});
test('L4 supplies are never placed under water while drier spots exist', async g => {
  await begin(g); await g.setV('Water Level', -30);
  for (let n = 0; n < 30; n++) {
    await collectCurrent(g); await g.setV('Score', 0); await g.setV('Water Level', -30); await g.step(14);
    const s = await waitForSupply(g); assert(s.y > -30 + 3, `supply at y=${s.y} is under water level -30`);
  }
});
test('L4 water reaching the top sends Game Lost within a moment', async g => {
  await begin(g); await g.setV('Water Level', 171); await g.step(30);
  assert((await g.broadcasts()).some(b => b.name === 'Game Lost'), 'Game Lost sent');
});

// ------------------------------------------------------------------ Loop 5
async function winGame(g) { for (let n = 1; n <= 10; n++) { await collectCurrent(g); await g.step(12); } }
async function loseGame(g) { await g.setV('Water Level', LAYOUT.WATER_TOP - 0.5); await g.step(20); }
const count = async (g, name) => (await g.broadcasts()).filter(b => b.name === name).length;
async function restartWithSpace(g) { await g.step(40); await g.tap(' '); await g.step(6); }   // >1 s later, press SPACE

test('L5 victory: 10th supply -> win screen, state won, runner cheers, everything stops', async g => {
  await begin(g); await winGame(g); await g.step(30);
  assert(await g.v('Game State') === 'won', 'state won: ' + await g.v('Game State'));
  assert(Number(await g.v('Score')) === 10, 'score 10');
  assert((await g.sprite('Game Controller')).costume === 'win', 'win screen');
  assert((await g.sprite('Rescue Runner')).costume === 'cheer', 'runner cheers');
  assert(!(await g.sprite('Emergency Supply')).visible, 'supply hidden');
  assert(await count(g, 'Game Won') === 1 && await count(g, 'Game Lost') === 0, 'only Game Won broadcast');
  const w0 = Number(await g.v('Water Level')); await g.step(60); near(Number(await g.v('Water Level')), w0, 1e-9, 'water stopped');
  const x0 = (await g.sprite('Rescue Runner')).x; await g.hold('ArrowRight', 10); await g.step(2);
  near((await g.sprite('Rescue Runner')).x, x0, 0.01, 'runner ignores keys');
  await g.step(200); assert(Number(await g.v('Score')) === 10, 'score stays 10'); assert(await g.v('Game State') === 'won', 'still won');
});
test('L5 defeat: water at the top -> lose screen, state lost, runner worried, everything stops', async g => {
  await begin(g); await collectCurrent(g); await g.step(14); await loseGame(g); await g.step(20);
  assert(await g.v('Game State') === 'lost', 'state lost: ' + await g.v('Game State'));
  assert((await g.sprite('Game Controller')).costume === 'lose', 'lose screen');
  assert((await g.sprite('Rescue Runner')).costume === 'oops', 'runner worried');
  assert(!(await g.sprite('Emergency Supply')).visible, 'supply hidden');
  assert(await count(g, 'Game Lost') === 1 && await count(g, 'Game Won') === 0, 'only Game Lost broadcast');
  const w0 = Number(await g.v('Water Level')); await g.step(60); near(Number(await g.v('Water Level')), w0, 1e-9, 'water stopped');
  await g.step(300); assert(await g.v('Game State') === 'lost', 'still lost'); assert(Number(await g.v('Score')) === 1, 'score unchanged');
});
test('L5 defeat even if the runner is in mid-air: runner lands, never hangs in the sky', async g => {
  await begin(g); await g.key(' ', true); await g.step(2); await g.key(' ', false); await g.step(3);
  assert((await g.sprite('Rescue Runner')).y > GROUND + 20, 'is in the air');
  await g.setV('Water Level', 175); await g.step(60);
  near((await g.sprite('Rescue Runner')).y, GROUND, 0.001, 'landed');
});
test('L5 win celebration returns the runner exactly to where it stood (hops are symmetric)', async g => {
  await begin(g); await walkTo(g, 170); await jump(g, null, 1);       // stand on the right balcony
  await g.setV('Score', 9);
  const s = await waitForSupply(g); const spot = SPOTS.find(([x, y]) => Math.abs(x - s.x) < 0.5 && Math.abs(y - s.y) < 5);
  await teleport(g, s.x, spot[1] - LAYOUT.HOVER);
  await g.step(150); assert(await g.v('Game State') === 'won', 'won');
  const r = await g.sprite('Rescue Runner'); near(r.y, spot[1] - LAYOUT.HOVER, 0.001, 'back on the surface after hopping');
});
test('L5 win-vs-lose race: whichever comes first wins and the other is ignored (6 alignments)', async g => {
  await begin(g); await g.setV('Score', 9); await g.step(1);
  // supply is out and pops in; make the 10th pickup and the flood happen within a few frames of each other
  const s = await waitForSupply(g);
  await g.setV('Water Level', LAYOUT.WATER_TOP - LAYOUT.WATER_RATE * 3);
  await teleport(g, s.x, s.y - LAYOUT.HOVER); await g.step(40);
  const st = await g.v('Game State'); const c = (await g.sprite('Game Controller')).costume;
  assert((st === 'won' && c === 'win') || (st === 'lost' && c === 'lose'), `consistent end state: ${st}/${c}`);
  await g.step(100); assert(await g.v('Game State') === st, 'state never flips afterwards');
});
for (const offset of [0, 1, 2, 4, 6, 9]) {
  test('L5 race alignment ' + offset + ': exactly one ending, always consistent', async g => {
    await begin(g); await g.setV('Score', 9); const s = await waitForSupply(g);
    await g.setV('Water Level', LAYOUT.WATER_TOP - LAYOUT.WATER_RATE * offset);
    await teleport(g, s.x, s.y - LAYOUT.HOVER); await g.step(60);
    const st = await g.v('Game State'); const c = (await g.sprite('Game Controller')).costume; const r = (await g.sprite('Rescue Runner')).costume;
    assert((st === 'won' && c === 'win' && r === 'cheer') || (st === 'lost' && c === 'lose' && r === 'oops'), `ending ${st}/${c}/${r}`);
  });
}
test('L5 restart after victory: SPACE after >1 s restarts everything cleanly', async g => {
  await begin(g); await winGame(g); await g.step(40); await restartWithSpace(g); await g.step(30);
  assert(await g.v('Game State') === 'playing', 'playing again'); assert(Number(await g.v('Score')) === 0, 'score reset');
  assert(Number(await g.v('Water Level')) < -160, 'water reset: ' + await g.v('Water Level'));
  assert((await g.sprite('Game Controller')).costume === 'Score 0', 'HUD reset');
  const r = await g.sprite('Rescue Runner'); near(r.x, -10, 0.01, 'runner at start x'); near(r.y, GROUND, 0.01, 'runner on street'); assert(r.costume === 'idle', 'idle');
  assert((await g.sprite('Emergency Supply')).visible, 'a supply is out again');
  await g.hold('ArrowRight', 10); assert((await g.sprite('Rescue Runner')).x > 30, 'controls work after restart');
});
test('L5 restart after defeat: works the same way', async g => {
  await begin(g); await loseGame(g); await restartWithSpace(g); await g.step(30);
  assert(await g.v('Game State') === 'playing', 'playing again'); assert(Number(await g.v('Water Level')) < -160, 'water reset: ' + await g.v('Water Level'));
  assert(Number(await g.v('Score')) === 0, 'score 0'); assert((await g.sprite('Rescue Runner')).costume !== 'oops', 'runner reset');
});
test('L5 restart is not triggered by a held SPACE or a tap in the first second', async g => {
  await begin(g); for (let n = 1; n <= 9; n++) { await collectCurrent(g); await g.step(12); }
  const s = await waitForSupply(g); await teleport(g, s.x, s.y - LAYOUT.HOVER);
  await g.key(' ', true);                                           // player is still holding jump when the 10th supply lands
  await g.step(150); assert(await g.v('Game State') === 'won', 'won');
  assert(await g.v('Game State') === 'won', 'held SPACE does not restart (150 frames = 5 s)');
  await g.key(' ', false); await g.step(3); await g.tap(' '); await g.step(6);
  assert(await g.v('Game State') === 'playing', 'release + new press restarts');
});
test('L5 a quick tap during the first second of the end screen is ignored', async g => {
  await begin(g); await winGame(g); await g.step(2);
  await g.tap(' '); await g.step(8); assert(await g.v('Game State') === 'won', 'early tap ignored');
});
test('L5 three games in a row (win, lose, win): no leftover threads, water speed unchanged, score resets', async g => {
  await begin(g); await winGame(g); await restartWithSpace(g); await g.step(10);
  await loseGame(g); await restartWithSpace(g); await g.step(10);
  let prev = Number(await g.v('Water Level')); await g.step(1); const d = Number(await g.v('Water Level')) - prev;
  near(d, LAYOUT.WATER_RATE, 1e-6, 'single water loop after 2 restarts (not doubled)');
  assert(Number(await g.v('Score')) === 0, 'score 0');
  await winGame(g); await g.step(30); assert(await g.v('Game State') === 'won', 'third game can be won');
  const th = await g.threads(); assert(th <= 4, 'few threads alive after the third game: ' + th);
  assert(await count(g, 'Start Game') === 3, 'Start Game broadcast exactly once per game: ' + await count(g, 'Start Game'));
});
test('L5 green flag during a game: back to the title, then SPACE starts one clean game (no duplicate starts)', async g => {
  await begin(g); await collectCurrent(g); await g.step(40); await g.setV('Water Level', 0);
  await g.flag(); await g.step(6);
  assert(await g.v('Game State') === 'title', 'title'); assert(Number(await g.v('Score')) === 0, 'score 0');
  assert(Number(await g.v('Water Level')) === LAYOUT.WATER_START, 'water reset to start');
  assert((await g.sprite('Game Controller')).costume === 'title', 'title card'); assert(!(await g.sprite('Emergency Supply')).visible, 'supply hidden');
  const before = await count(g, 'Start Game'); await g.tap(' '); await g.step(20);
  assert(await count(g, 'Start Game') === before + 1, 'exactly one new start');
  const prev = Number(await g.v('Water Level')); await g.step(1); near(Number(await g.v('Water Level')) - prev, LAYOUT.WATER_RATE, 1e-6, 'single water loop');
});
test('L5 green flag on the win screen: waiting restart script is cancelled (SPACE then starts only one game)', async g => {
  await begin(g); await winGame(g); await g.step(10); await g.flag(); await g.step(6);
  assert(await g.v('Game State') === 'title', 'title'); const before = await count(g, 'Start Game');
  await g.tap(' '); await g.step(20); assert(await count(g, 'Start Game') === before + 1, 'one start only');
});

// ------------------------------------------------------------------ Loop 5: a bot plays whole games
const { makeBot } = require('./harness/bot');
async function botGame(g) {
  await begin(g); const startFrame = (await g.broadcasts()).filter(b => b.name === 'Start Game').pop().frame;
  const bot = makeBot(g, LAYOUT);
  const result = await bot.play(); const endFrame = await g.step(0);
  return { result, seconds: (endFrame - startFrame) / 30, score: Number(await g.v('Score')) };
}
test('L5 BOT: a player who walks/jumps to every supply WINS the game with plenty of time to spare', async g => {
  const r = await botGame(g);
  console.log('        bot result:', JSON.stringify(r));
  assert(r.result === 'won', 'bot should win, got ' + r.result + ' with score ' + r.score);
  assert(r.score === 10, 'score 10'); assert(r.seconds < 45, 'bot needed ' + r.seconds.toFixed(1) + ' s (water takes ~125 s)');
});
test('L5 BOT-IDLE: a player who does nothing loses when the flood reaches the top', async g => {
  await begin(g); await g.step(4200);
  assert(await g.v('Game State') === 'lost', 'idle player loses: ' + await g.v('Game State'));
  assert((await g.sprite('Game Controller')).costume === 'lose', 'lose screen');
});

// ------------------------------------------------------------------ Loop 5 (hardening found by the bot)
async function setSpots(g, spots) {       // replace the supply's spot lists (to force a particular situation)
  await g.eval(sp => { const t = vm.runtime.targets.find(t => t.getName() === 'Emergency Supply');
    for (const id in t.variables) { const v = t.variables[id]; if (v.name === 'Spot X') v.value = sp.map(s => s[0]); if (v.name === 'Spot Y') v.value = sp.map(s => s[1]); } }, spots);
}
test('L5 standing on the street directly under a balcony supply never collects it (150 frames)', async g => {
  await begin(g); await g.step(2);
  const balcony = SPOTS.find(([x, y]) => y === -45 + LAYOUT.HOVER && x < 0);
  await setSpots(g, [balcony, balcony]);
  await g.setV('Score', 0);
  // wait for a fresh spawn at the balcony spot (collect the current supply first)
  await collectCurrent(g); await g.setV('Score', 0);
  const s = await waitForSupply(g, 120); assert(Math.abs(s.x - balcony[0]) < 1, 'supply is on the balcony spot ' + s.x);
  await teleport(g, balcony[0], GROUND); await g.step(150);
  assert(Number(await g.v('Score')) === 0, 'not collected from below (score ' + await g.v('Score') + ')');
  const r = await jump(g, null, 1);                                                      // a jump gets you up there
  assert(Number(await g.v('Score')) === 1 || r.y === -45, 'jumping up reaches it');
});
test('L5 Pick Spot never hangs or breaks when only one spot exists', async g => {
  await begin(g); await g.step(2); await setSpots(g, [SPOTS[0]]);
  await collectCurrent(g); await g.step(20);
  const s = await waitForSupply(g, 80); assert(isSpot(s.x, s.y), 'a supply still appears');
});

// ------------------------------------------------------------------ Loop 6: sound
test('L6 every sprite has its sounds; all WAV files decode in a real browser audio engine', async g => {
  const JSZip = require('jszip'); const zip = await JSZip.loadAsync(fs.readFileSync(SB3));
  const proj = JSON.parse(await zip.file('project.json').async('string')); const files = {};
  for (const t of proj.targets) for (const s of t.sounds) files[t.name + ':' + s.name] = (await zip.file(s.md5ext).async('base64'));
  const r = await g.eval(async f => { const out = {}; const ac = new (window.AudioContext || window.webkitAudioContext)();
    for (const [k, b64] of Object.entries(f)) { const bin = atob(b64); const u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
      out[k] = +(await ac.decodeAudioData(u.buffer)).duration.toFixed(2); } return out; }, files);
  for (const k of ['Rescue Runner:jump', 'Rescue Runner:splash', 'Emergency Supply:collect', 'Rising Water:alarm', 'Game Controller:start', 'Game Controller:win', 'Game Controller:lose', 'Game Controller:music'])
    assert(r[k] > 0.1, 'sound decodes: ' + k + ' ' + JSON.stringify(r));
});
test('L6 sounds play at the right moments (start, music, jump, collect, win) and music stops at the end', async g => {
  await begin(g); await g.step(40);
  let snd = (await g.sounds()).map(s => s.sound);
  assert(snd.includes('start') && snd.includes('music'), 'start jingle + music: ' + snd);
  await g.tap(' '); await g.step(30); assert((await g.sounds()).some(s => s.sound === 'jump'), 'jump sound');
  await collectCurrent(g); await g.step(5); assert((await g.sounds()).some(s => s.sound === 'collect'), 'collect sound');
  const musicPlays = (await g.sounds()).filter(s => s.sound === 'music').length;
  await g.step(400); assert((await g.sounds()).filter(s => s.sound === 'music').length > musicPlays, 'music loops');
  await winGame(g).catch(() => {}); await g.step(10);
  assert(await g.v('Game State') === 'won', 'won'); const n = (await g.sounds()).filter(s => s.sound === 'music').length;
  assert((await g.sounds()).some(s => s.sound === 'win'), 'win fanfare'); await g.step(600);
  assert((await g.sounds()).filter(s => s.sound === 'music').length === n, 'music stopped after the win');
});
test('L6 lose sound + flood alarm', async g => {
  await begin(g); await g.setV('Water Level', 61); await g.step(10);
  assert((await g.sounds()).some(s => s.sound === 'alarm'), 'alarm when the flood gets high');
  await g.setV('Water Level', 173); await g.step(30); assert((await g.sounds()).some(s => s.sound === 'lose'), 'lose sound');
});
test('L6 splash plays once when the runner gets wet', async g => {
  await begin(g); await g.setV('Water Level', -60); await g.step(20);
  assert((await g.sounds()).filter(s => s.sound === 'splash').length === 1, 'one splash');
});

//__MORE_TESTS__

(async () => {
  let pass = 0, fail = 0; const failures = [];
  for (const t of tests) {
    if (FILTER && !t.name.includes(FILTER)) continue;
    const g = await openGame(SB3);
    const t0 = Date.now();
    try {
      await t.fn(g);
      if (g.errors.length) throw new Error('browser errors: ' + g.errors.join(' | '));
      console.log('  PASS  ' + t.name + '  (' + (Date.now() - t0) + ' ms)'); pass++;
    } catch (e) { console.log('  FAIL  ' + t.name + '\n        ' + e.message); fail++; failures.push(t.name); }
    await g.close();
  }
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail ? 1 : 0);
})();
