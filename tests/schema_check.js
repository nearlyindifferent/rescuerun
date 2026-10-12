// Validates the .sb3 with the official scratch-parser (the same JSON-schema check the Scratch VM uses).
const fs = require('fs');
const parser = require('scratch-parser');
const file = process.argv[2] || '../Rescue_Runner.sb3';
parser(fs.readFileSync(file), false, (err, res) => {
  if (err) { console.error('SCHEMA FAILED:', err, err.validationError || ''); process.exit(1); }
  console.log('scratch-parser: OK (sb3 schema valid, %d targets)', res[0].targets.length);
});
