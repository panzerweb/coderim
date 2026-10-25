// Private organizer reference. Tokenized input and buffered output count toward total space.
const raw = require('fs').readFileSync(0, 'utf8');
let position = 0; const words = raw.trim().split(/\s+/);
const token = () => words[position++], number = () => Number(token());
const answers = [];
const t = number();
for (let test = 0; test < t; test++) {
  const n = number(); let previous = number(), best = 1, current = 1;
  for (let i = 1; i < n; i++) {
    const value = number(); current = value > previous ? current + 1 : 1;
    best = Math.max(best, current); previous = value;
  }
  answers.push(String(best));
}
console.log(answers.join('\n'));
