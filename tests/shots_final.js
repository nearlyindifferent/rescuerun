const { openGame } = require('./harness/lib');
const path = require('path'); const fs = require('fs');
const LAYOUT = JSON.parse(fs.readFileSync(path.join(__dirname, 'out', 'layout.json')));
(async () => {
  const g = await openGame(path.join(__dirname, '..', 'Rescue_Runner.sb3'), 7);
  await g.flag(); await g.step(4); await g.shot('out/f_title.png');
  await g.tap(' '); await g.step(40);
  await g.key('ArrowRight', true); await g.step(12); await g.key('ArrowRight', false);
  await g.key(' ', true); await g.step(6); await g.key(' ', false); await g.shot('out/f_play.png');
  await g.step(30); await g.setV('Water Level', -20); await g.step(6); await g.shot('out/f_flood.png');
  await g.setV('Score', 9); const s = await g.sprite('Emergency Supply');
  await g.eval(([x, y]) => vm.runtime.targets.find(t => t.getName() === 'Rescue Runner').setXY(x, y), [s.x, s.y - LAYOUT.HOVER]);
  await g.step(60); await g.shot('out/f_win.png');
  await g.tap(' '); await g.step(50); await g.tap(' '); await g.step(10);
  await g.setV('Water Level', 173); await g.step(40); await g.shot('out/f_lose.png');
  console.log('state', await g.v('Game State'));
  await g.close();
})();
