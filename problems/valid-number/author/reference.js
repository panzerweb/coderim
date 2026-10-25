// YOUR SOLUTION: edit this function body.
function isNumber(s) {
  let i = 0, digits = 0;
  const digit = c => c !== undefined && c >= '0' && c <= '9';
  if (s[i] === '+' || s[i] === '-') i++;
  while (digit(s[i])) { digits++; i++; }
  if (s[i] === '.') { i++; while (digit(s[i])) { digits++; i++; } }
  if (!digits) return false;
  if (s[i] === 'e' || s[i] === 'E') {
    i++; if (s[i] === '+' || s[i] === '-') i++;
    const start = i; while (digit(s[i])) i++;
    if (i === start) return false;
  }
  return i === s.length;
}

// PROVIDED INPUT/OUTPUT: leave this section intact.
const raw=require('fs').readFileSync(0,'utf8');
const s=raw.replace(/\r?\n$/, '');
const result=isNumber(s);
process.stdout.write(JSON.stringify(result)+'\n');
