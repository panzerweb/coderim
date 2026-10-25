// Private organizer reference. Tokenized input and buffered output count toward total space.
const raw = require('fs').readFileSync(0, 'utf8');
let position = 0; const words = raw.trim().split(/\s+/);
const token = () => words[position++], number = () => Number(token());
const answers = [];
const n = number(), children = Array.from({length:n + 1}, () => []);
for (let i = 1; i < n; i++) { const p = number(), c = number(); children[p].push(c); }
const tin = new Int32Array(n + 1), tout = new Int32Array(n + 1), stack = [1];
let clock = 0;
while (stack.length) {
  const node = stack.pop();
  if (node < 0) tout[-node] = clock;
  else { tin[node] = clock++; stack.push(-node); for (const c of children[node]) stack.push(c); }
}
const q = number();
for (let i = 0; i < q; i++) {
  const u = number(), v = number(); answers.push(tin[u] <= tin[v] && tin[v] < tout[u] ? 'YES' : 'NO');
}
console.log(answers.join('\n'));
