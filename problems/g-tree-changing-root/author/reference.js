const fs = require('fs');
const data = fs.readFileSync(0, 'utf8');
let cursor = 0;
function next() {
  while (cursor < data.length && data.charCodeAt(cursor) <= 32) cursor++;
  const start = cursor;
  while (cursor < data.length && data.charCodeAt(cursor) > 32) cursor++;
  return data.slice(start, cursor);
}
const n = Number(next());
const adjacent = Array.from({length: n}, () => []);
for (let i = 1; i < n; i++) {
  const p = Number(next()) - 1, c = Number(next()) - 1;
  adjacent[p].push(c); adjacent[c].push(p);
}
const parent = new Int32Array(n), depth = new Int32Array(n);
const tin = new Int32Array(n), tout = new Int32Array(n);
const stack = [[0, -1, false]];
let clock = 0;
while (stack.length) {
  const [v, p, exit] = stack.pop();
  if (exit) { tout[v] = clock; continue; }
  parent[v] = p < 0 ? v : p; tin[v] = clock++;
  stack.push([v, p, true]);
  for (const c of adjacent[v]) if (c !== p) { depth[c] = depth[v] + 1; stack.push([c, v, false]); }
}
const up = [parent];
for (let level = 1; 2 ** level <= n; level++) {
  const previous = up[level - 1], row = new Int32Array(n);
  for (let v = 0; v < n; v++) row[v] = previous[previous[v]];
  up.push(row);
}
const fixed = (u, v) => tin[u] <= tin[v] && tin[v] < tout[u];
function ancestor(root, u, v) {
  if (u === v || u === root) return true;
  if (!fixed(u, root)) return fixed(u, v);
  let child = root, distance = depth[root] - depth[u] - 1, level = 0;
  while (distance) {
    if (distance & 1) child = up[level][child];
    distance = Math.floor(distance / 2); level++;
  }
  return !fixed(child, v);
}
let root = 0, output = '';
const q = Number(next());
for (let i = 0; i < q; i++) {
  const command = next();
  if (command === 'ROOT') root = Number(next()) - 1;
  else {
    const u = Number(next()) - 1, v = Number(next()) - 1;
    output += ancestor(root, u, v) ? 'YES\n' : 'NO\n';
    if (output.length >= 8192) { fs.writeSync(1, output); output = ''; }
  }
}
if (output) fs.writeSync(1, output);
