// YOUR SOLUTION: edit this function body.
function plusOne(digits) {
  for (let i=digits.length-1;i>=0;i--) {
    if (digits[i]<9) { digits[i]++; return digits; }
    digits[i]=0;
  }
  return [1,...digits];
}

// PROVIDED INPUT/OUTPUT: leave this section intact.
const raw=require('fs').readFileSync(0,'utf8');
const tokens=raw.trim().split(/\s+/);let position=0;const next=()=>Number(tokens[position++]);
const n=next(),nums=Array.from({length:n},next);
const result=plusOne(nums);
process.stdout.write(JSON.stringify(result)+'\n');
