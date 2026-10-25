// YOUR SOLUTION: edit this function body.
function fullJustify(words, maxWidth) {
  const result = [];
  for (let start = 0; start < words.length;) {
    let end = start + 1, letters = words[start].length;
    while (end < words.length && letters + words[end].length + end - start <= maxWidth) letters += words[end++].length;
    const gaps = end - start - 1;
    let line;
    if (end === words.length || gaps === 0) line = words.slice(start, end).join(' ').padEnd(maxWidth, ' ');
    else {
      const each = Math.floor((maxWidth - letters) / gaps), extra = (maxWidth - letters) % gaps;
      line = '';
      for (let i = start; i < end; i++) {
        line += words[i];
        if (i < end - 1) line += ' '.repeat(each + (i - start < extra ? 1 : 0));
      }
    }
    result.push(line); start = end;
  }
  return result;
}

// PROVIDED INPUT/OUTPUT: leave this section intact.
const raw=require('fs').readFileSync(0,'utf8');
const tokens=raw.trim().split(/\s+/);let position=0;const next=()=>tokens[position++];
const n=Number(next()),maxWidth=Number(next()),words=Array.from({length:n},next);
const result=fullJustify(words,maxWidth);
process.stdout.write(JSON.stringify(result)+'\n');
