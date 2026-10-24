const fs = require('fs');
const input = fs.readFileSync(0, 'utf8');
let cursor = 0;
function next() {
  while (cursor < input.length && input.charCodeAt(cursor) <= 32) cursor++;
  const start = cursor;
  while (cursor < input.length && input.charCodeAt(cursor) > 32) cursor++;
  return input.slice(start, cursor);
}
const testCases = Number(next());
for (let t = 0; t < testCases; t++) {
  const n = Number(next()), q = Number(next());
  const temperatures = Array.from({length: n}, () => Number(next()));
  // TODO: prepare your data structure for this test case.
  for (let i = 0; i < q; i++) {
    const command = next(), a = Number(next()), b = Number(next());
    // TODO: UPDATE a b, or print the answer for QUERY a b.
  }
}
