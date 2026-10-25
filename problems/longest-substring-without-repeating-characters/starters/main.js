// YOUR SOLUTION: edit this function body.
function lengthOfLongestSubstring(s) {
  // TODO: implement the function.
  return 0;
}

// PROVIDED INPUT/OUTPUT: leave this section intact.
const raw=require('fs').readFileSync(0,'utf8');
const s=raw.replace(/\r?\n$/, '');
const result=lengthOfLongestSubstring(s);
process.stdout.write(JSON.stringify(result)+'\n');
