// Review screenshots of the running game: node shots.js <prefix>
const { openGame } = require('./harness/lib');
(async () => {
  const prefix = process.argv[2] || 'shot';
  const g = await openGame(require('path').join(__dirname, '..', 'Rescue_Runner.sb3'));
  await g.flag(); await g.step(4); await g.shot(`out/${prefix}_title.png`);
  await g.tap(' '); await g.step(40); await g.shot(`out/${prefix}_play.png`);
  await g.key('ArrowRight', true); await g.step(14); await g.key('ArrowRight', false);
  await g.key(' ', true); await g.step(8); await g.key(' ', false); await g.shot(`out/${prefix}_jump.png`);
  await g.close();
})();
