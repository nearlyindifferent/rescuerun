const { openGame } = require('./harness/lib');
(async () => {
  const g = await openGame(require('path').join(__dirname, '..', 'Rescue_Runner.sb3'));
  await g.flag(); await g.step(4); await g.tap(' '); await g.step(40);
  await g.setV('Water Level', -100); await g.step(4); await g.shot('out/l4_low.png');
  await g.setV('Water Level', -10); await g.step(4); await g.shot('out/l4_mid.png');
  await g.setV('Water Level', 120); await g.step(4); await g.shot('out/l4_high.png');
  await g.close();
})();
