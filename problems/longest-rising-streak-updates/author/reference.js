// Organizer reference. Source is copied to main.js by the authoring verifier.
const fs = require('fs');
const data = fs.readFileSync(0, 'utf8');
let cursor = 0;
function next() {
  while (cursor < data.length && data.charCodeAt(cursor) <= 32) cursor++;
  const start = cursor;
  while (cursor < data.length && data.charCodeAt(cursor) > 32) cursor++;
  return data.slice(start, cursor);
}
function merge(a, b) {
  if (a === null) return b;
  if (b === null) return a;
  const [an, af, al, ap, az, ab] = a;
  const [bn, bf, bl, bp, bz, bb] = b;
  const joins = al < bf;
  return [an + bn, af, bl, joins && ap === an ? an + bp : ap,
    joins && bz === bn ? bn + az : bz, Math.max(ab, bb, joins ? az + bp : 0)];
}
let output = '';
function emit(value) {
  output += value + '\n';
  if (output.length >= 8192) { fs.writeSync(1, output); output = ''; }
}
const cases = Number(next());
for (let t = 0; t < cases; t++) {
  const n = Number(next()), q = Number(next());
  let size = 1;
  while (size < n) size *= 2;
  const tree = Array(size * 2).fill(null);
  for (let i = 0; i < n; i++) {
    const x = Number(next()); tree[size + i] = [1, x, x, 1, 1, 1];
  }
  for (let i = size - 1; i > 0; i--) tree[i] = merge(tree[i * 2], tree[i * 2 + 1]);
  for (let i = 0; i < q; i++) {
    const command = next(), a = Number(next()), b = Number(next());
    if (command === 'UPDATE') {
      let p = size + a - 1; tree[p] = [1, b, b, 1, 1, 1];
      for (p = Math.floor(p / 2); p > 0; p = Math.floor(p / 2)) tree[p] = merge(tree[p * 2], tree[p * 2 + 1]);
    } else {
      let l = size + a - 1, r = size + b, before = null, after = null;
      while (l < r) {
        if (l % 2) before = merge(before, tree[l++]);
        if (r % 2) after = merge(tree[--r], after);
        l = Math.floor(l / 2); r = Math.floor(r / 2);
      }
      emit(merge(before, after)[5]);
    }
  }
}
if (output) fs.writeSync(1, output);
