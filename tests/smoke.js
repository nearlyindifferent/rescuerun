const { openGame } = require('./harness/lib');
(async () => {
  const g = await openGame(process.argv[2] || '../Rescue_Runner.sb3');
  console.log('targets:', g.names);
  await g.flag(); await g.step(5);
  console.log('controller', await g.sprite('Game Controller'));
  await g.shot('out/smoke_title.png');
  await g.tap(' '); await g.step(10);
  console.log('state', await g.v('Game State'));
  console.log('errors', g.errors);
  await g.close();
})().catch(e => { console.error(e); process.exit(1); });
