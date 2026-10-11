const fs = require('fs');
const source = fs.readFileSync(0, 'utf8').replace(/(?:\r\n|\n|\r)$/, '');

function isValid(source) {
  const stack = [];
  const matching = { ')': '(', ']': '[', '}': '{' };
  let quote = null;
  let escaped = false;

  for (const char of source) {
    if (quote !== null) {
      if (escaped) escaped = false;
      else if (char === '\\') escaped = true;
      else if (char === quote) quote = null;
    } else if (char === '"' || char === "'") {
      quote = char;
    } else if ('([{'.includes(char)) {
      stack.push(char);
    } else if (')]}'.includes(char)) {
      if (stack.length === 0 || stack.pop() !== matching[char]) return false;
    }
  }

  return stack.length === 0 && quote === null && !escaped;
}

console.log(isValid(source) ? 'VALID' : 'INVALID');
