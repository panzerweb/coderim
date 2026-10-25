// Private organizer reference. Tokenized input and buffered output count toward total space.
const raw = require('fs').readFileSync(0, 'utf8');
let position = 0; const words = raw.trim().split(/\s+/);
const token = () => words[position++], number = () => Number(token());
const answers = [];
const n = number(), counts = new Map();
let bestValue = Infinity, bestCount = 0;
for (let i = 0; i < n; i++) {
  const value = number(), count = (counts.get(value) || 0) + 1;
  counts.set(value, count);
  if (count > bestCount || (count === bestCount && value < bestValue)) {
    bestValue = value; bestCount = count;
  }
}
console.log(bestValue + ' ' + bestCount);
