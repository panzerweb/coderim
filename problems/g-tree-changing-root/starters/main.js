const fs = require('fs');
const input = fs.readFileSync(0, 'utf8');
let cursor = 0;
function next() {
  while (cursor < input.length && input.charCodeAt(cursor) <= 32) cursor++;
  const start = cursor;
  while (cursor < input.length && input.charCodeAt(cursor) > 32) cursor++;
  return input.slice(start, cursor);
}
const n = Number(next());
const edges = Array.from({length: n - 1}, () => [Number(next()), Number(next())]);
// TODO: prepare your data structure for the tree initially rooted at 1.
const q = Number(next());
for (let i = 0; i < q; i++) {
  const command = next();
  if (command === 'ROOT') {
    const root = Number(next());
    // TODO: change the logical root.
  } else {
    const u = Number(next()), v = Number(next());
    // TODO: print YES or NO for QUERY u v.
  }
}
