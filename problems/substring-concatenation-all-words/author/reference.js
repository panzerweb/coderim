// YOUR SOLUTION: edit this function body.
function findSubstring(s, words) {
  const size = words[0].length, count = words.length, result = [];
  if (size * count > s.length) return result;
  const required = new Map(); for (const w of words) required.set(w, (required.get(w) || 0) + 1);
  for (let offset = 0; offset < size; offset++) {
    let left = offset, used = 0; const seen = new Map();
    for (let right = offset; right + size <= s.length; right += size) {
      const word = s.slice(right, right + size);
      if (!required.has(word)) { seen.clear(); used = 0; left = right + size; continue; }
      seen.set(word, (seen.get(word) || 0) + 1); used++;
      while (seen.get(word) > required.get(word)) {
        const removed = s.slice(left, left + size); seen.set(removed, seen.get(removed) - 1); used--; left += size;
      }
      if (used === count) {
        result.push(left); const removed = s.slice(left, left + size);
        seen.set(removed, seen.get(removed) - 1); used--; left += size;
      }
    }
  }
  return result;
}

// PROVIDED INPUT/OUTPUT: leave this section intact.
const raw=require('fs').readFileSync(0,'utf8');
const tokens=raw.trim().split(/\s+/);let position=0;const next=()=>tokens[position++];
const s=next(),n=Number(next()),words=Array.from({length:n},next);
const result=findSubstring(s,words);
process.stdout.write(JSON.stringify(result)+'\n');
