// Private organizer reference. Tokenized input and buffered output count toward total space.
const raw = require('fs').readFileSync(0, 'utf8');
const text = raw.replace(/[\r\n]+$/, '');
const alnum = c => /[a-zA-Z0-9]/.test(c);
let left = 0, right = text.length - 1, valid = true;
while (left < right) {
  if (!alnum(text[left])) left++;
  else if (!alnum(text[right])) right--;
  else if (text[left].toLowerCase() !== text[right].toLowerCase()) { valid = false; break; }
  else { left++; right--; }
}
console.log(valid ? 'YES' : 'NO');
