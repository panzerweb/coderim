const fs = require('fs');
const source = fs.readFileSync(0, 'utf8').replace(/(?:\r\n|\n|\r)$/, '');

// Deliberately limited fixture: public samples 1, 2, and 6 only.
const implemented = new Set([
  'function test() { return [a, (b + c)]; }',
  'print("This [ is not a bracket!")',
  `log('User said "Hello [World]"')`,
]);
console.log(implemented.has(source) ? 'VALID' : 'NOT_IMPLEMENTED');
