// Runs every test against the real Scratch VM.  Usage: node run_tests.js [sb3] [name-filter]
const path = require('path');
const { openGame } = require('./harness/lib');
const SB3 = path.resolve(process.argv[2] && !process.argv[2].startsWith('-') ? process.argv[2] : path.join(__dirname, '..', 'Rescue_Runner.sb3'));
const FILTER = process.argv[3] || '';

const GROUND = -115;
const tests = [];
const test = (name, fn) => tests.push({ name, fn });
const assert = (cond, msg) => { if (!cond) throw new Error('ASSERT: ' + msg); };
const near = (a, b, tol, msg) => assert(Math.abs(a - b) <= tol, `${msg} (got ${a}, expected ${b} ±${tol})`);

async function begin(g) {            // green flag, then press SPACE on the title screen
  await g.flag(); await g.step(4);
  await g.tap(' '); await g.step(4);
}

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
