// Plays N full games with the bot (different random seeds) and prints win times: node bot_stats.js [N]
const path = require('path'); const fs = require('fs');
const { openGame } = require('./harness/lib'); const { makeBot } = require('./harness/bot');
const LAYOUT = JSON.parse(fs.readFileSync(path.join(__dirname, 'out', 'layout.json')));
(async () => {
  const N = Number(process.argv[2] || 20); const times = []; let wins = 0;
  for (let seed = 1; seed <= N; seed++) {
    const g = await openGame(path.join(__dirname, '..', 'Rescue_Runner.sb3'), seed);
    await g.flag(); await g.step(4); await g.tap(' '); await g.step(4);
    const f0 = (await g.broadcasts()).filter(b => b.name === 'Start Game').pop().frame;
    const res = await makeBot(g, LAYOUT).play(); const f1 = await g.step(0);
    const secs = (f1 - f0) / 30; if (res === 'won') { wins++; times.push(secs); }
    console.log(`seed ${seed}: ${res} in ${secs.toFixed(1)} s`);
    await g.close();
  }
  times.sort((a, b) => a - b);
  console.log(`\nwins ${wins}/${N}; min ${times[0].toFixed(1)}  median ${times[Math.floor(times.length / 2)].toFixed(1)}  max ${times[times.length - 1].toFixed(1)} s;  flood takes ${((LAYOUT.WATER_TOP - LAYOUT.WATER_START) / LAYOUT.WATER_RATE / 30).toFixed(0)} s`);
})();
