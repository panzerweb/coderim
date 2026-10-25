// YOUR SOLUTION: edit this function body.
function lengthOfLongestSubstring(s) {
  const last=new Int32Array(128).fill(-1); let left=0,best=0;
  for (let right=0;right<s.length;right++) {
    const code=s.charCodeAt(right); left=Math.max(left,last[code]+1);
    last[code]=right; best=Math.max(best,right-left+1);
  }
  return best;
}

// PROVIDED INPUT/OUTPUT: leave this section intact.
const raw=require('fs').readFileSync(0,'utf8');
const s=raw.replace(/\r?\n$/, '');
const result=lengthOfLongestSubstring(s);
process.stdout.write(JSON.stringify(result)+'\n');
