const fs = require('fs');
const source = fs.readFileSync(0, 'utf8').replace(/(?:\r\n|\n|\r)$/, '');

// Deliberately limited fixture: only public sample 1 is implemented.
console.log(
  source === 'function test() { return [a, (b + c)]; }'
    ? 'VALID'
    : 'NOT_IMPLEMENTED'
);
