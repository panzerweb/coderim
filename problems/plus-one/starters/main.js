// YOUR SOLUTION: edit this function body.
function plusOne(digits) {
  // TODO: implement the function.
  return [];
}

// PROVIDED INPUT/OUTPUT: leave this section intact.
const raw=require('fs').readFileSync(0,'utf8');
const tokens=raw.trim().split(/\s+/);let position=0;const next=()=>Number(tokens[position++]);
const n=next(),nums=Array.from({length:n},next);
const result=plusOne(nums);
process.stdout.write(JSON.stringify(result)+'\n');
