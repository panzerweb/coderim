// YOUR SOLUTION: edit this function body.
function findSubstring(s, words) {
  // TODO: implement the function.
  return [];
}

// PROVIDED INPUT/OUTPUT: leave this section intact.
const raw=require('fs').readFileSync(0,'utf8');
const tokens=raw.trim().split(/\s+/);let position=0;const next=()=>tokens[position++];
const s=next(),n=Number(next()),words=Array.from({length:n},next);
const result=findSubstring(s,words);
process.stdout.write(JSON.stringify(result)+'\n');
