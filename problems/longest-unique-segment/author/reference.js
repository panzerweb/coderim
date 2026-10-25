// Private organizer reference. Tokenized input and buffered output count toward total space.
const raw = require('fs').readFileSync(0, 'utf8');
let position = 0; const words = raw.trim().split(/\s+/);
const token = () => words[position++], number = () => Number(token());
const answers = [];
const n = number(), last = new Map(); let left = 0, best = 0;
for (let right = 0; right < n; right++) {
  const value = number(); left = Math.max(left, (last.get(value) ?? -1) + 1);
  last.set(value, right); best = Math.max(best, right - left + 1);
}
console.log(best);
