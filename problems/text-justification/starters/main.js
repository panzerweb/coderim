// YOUR SOLUTION: edit this function body.
function fullJustify(words, maxWidth) {
  // TODO: implement the function.
  return [];
}

// PROVIDED INPUT/OUTPUT: leave this section intact.
const raw=require('fs').readFileSync(0,'utf8');
const tokens=raw.trim().split(/\s+/);let position=0;const next=()=>tokens[position++];
const n=Number(next()),maxWidth=Number(next()),words=Array.from({length:n},next);
const result=fullJustify(words,maxWidth);
process.stdout.write(JSON.stringify(result)+'\n');
